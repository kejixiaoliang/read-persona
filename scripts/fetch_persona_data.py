#!/usr/bin/env python3
"""Fetch WeRead data for the read-persona skill.

This script intentionally uses only the Python standard library so it can run in
minimal Codex environments. It never prints the API key.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


GATEWAY_URL = "https://i.weread.qq.com/api/agent/gateway"
DEFAULT_SKILL_VERSION = "1.0.3"


def call_api(
    api_key: str,
    payload: dict[str, Any],
    skill_version: str,
    timeout: int,
) -> Any:
    body = dict(payload)
    body["skill_version"] = skill_version
    data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        GATEWAY_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WeRead API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"WeRead API network error: {exc.reason}") from exc

    if not text.strip():
        raise RuntimeError("WeRead API returned an empty response.")

    parsed = json.loads(text)
    if isinstance(parsed, dict) and parsed.get("errcode"):
        raise RuntimeError(
            f"WeRead API error {parsed.get('errcode')}: "
            f"{parsed.get('errmsg') or parsed.get('errlog') or parsed}"
        )
    return parsed


def fetch_notebooks(
    api_key: str,
    skill_version: str,
    page_size: int,
    max_pages: int,
    timeout: int,
) -> dict[str, Any]:
    all_books: list[Any] = []
    last_sort = None
    total_book_count = None
    total_note_count = None
    has_more = 1

    pages = 0
    while has_more and pages < max_pages:
        payload: dict[str, Any] = {"api_name": "/user/notebooks", "count": page_size}
        if last_sort is not None:
            payload["lastSort"] = last_sort
        page = call_api(api_key, payload, skill_version, timeout)
        pages += 1
        page_books = page.get("books") or []
        all_books.extend(page_books)
        total_book_count = page.get("totalBookCount", total_book_count)
        total_note_count = page.get("totalNoteCount", total_note_count)
        has_more = int(page.get("hasMore") or 0)
        if not page_books:
            break
        last_sort = page_books[-1].get("sort")
        if last_sort is None:
            break

    return {
        "totalBookCount": total_book_count,
        "totalNoteCount": total_note_count,
        "books": all_books,
        "fetchedPages": pages,
        "truncated": bool(has_more and pages >= max_pages),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get("WEREAD_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "WEREAD_API_KEY is missing. Get a key at "
            "https://weread.qq.com/r/weread-skills and set it as an environment variable."
        )

    reading_modes = ["overall", "annually", "monthly", "weekly"]
    reading = {
        mode: call_api(
            api_key,
            {"api_name": "/readdata/detail", "mode": mode},
            args.skill_version,
            args.timeout,
        )
        for mode in reading_modes
    }

    recommendations: Any
    if args.skip_recommendations:
        recommendations = {"books": [], "skipped": True}
    else:
        recommendations = call_api(
            api_key,
            {
                "api_name": "/book/recommend",
                "count": args.recommend_count,
                "maxIdx": 0,
            },
            args.skill_version,
            args.timeout,
        )

    result: dict[str, Any] = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": {
            "gateway": GATEWAY_URL,
            "skillVersion": args.skill_version,
            "modes": reading_modes,
        },
        "shelf": call_api(api_key, {"api_name": "/shelf/sync"}, args.skill_version, args.timeout),
        "reading": reading,
        "notebooks": fetch_notebooks(
            api_key,
            args.skill_version,
            args.notebook_page_size,
            args.max_notebook_pages,
            args.timeout,
        ),
        "recommendations": recommendations,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch WeRead data for read-persona.")
    parser.add_argument("--output", "-o", help="Write JSON to this file. Defaults to stdout.")
    parser.add_argument("--skill-version", default=DEFAULT_SKILL_VERSION)
    parser.add_argument("--recommend-count", type=int, default=12)
    parser.add_argument("--notebook-page-size", type=int, default=100)
    parser.add_argument("--max-notebook-pages", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=20, help="Per-request timeout in seconds.")
    parser.add_argument("--skip-recommendations", action="store_true")
    args = parser.parse_args()

    try:
        payload = build_payload(args)
    except Exception as exc:  # noqa: BLE001 - CLI should convert all failures to messages.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
