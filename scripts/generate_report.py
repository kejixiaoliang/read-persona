#!/usr/bin/env python3
"""Generate a read-persona HTML report from fetched WeRead JSON data."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "report-template.html"


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def fmt_seconds(value: Any) -> str:
    try:
        seconds = int(value or 0)
    except (TypeError, ValueError):
        seconds = 0
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}小时{minutes}分钟"


def get_books(data: dict[str, Any]) -> list[dict[str, Any]]:
    shelf = data.get("shelf") or {}
    return list(shelf.get("books") or [])


def visible_shelf_total(data: dict[str, Any]) -> int:
    shelf = data.get("shelf") or {}
    books = shelf.get("books") or []
    albums = shelf.get("albums") or []
    mp_count = 1 if shelf.get("mp") else 0
    return len(books) + len(albums) + mp_count


def category_counts(books: list[dict[str, Any]], top_n: int = 8) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for book in books:
        category = book.get("category") or "未分类/导入/公众号"
        parent = category.split("-", 1)[0]
        counts[parent] = counts.get(parent, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top_n]


def reading_stat(overall: dict[str, Any], name: str, fallback: str = "0") -> str:
    for item in overall.get("readStat") or []:
        if item.get("stat") == name:
            return str(item.get("counts") or fallback)
    return fallback


def notebook_total(data: dict[str, Any]) -> int:
    notebooks = data.get("notebooks") or {}
    total = notebooks.get("totalNoteCount")
    if total is not None:
        return int(total)
    total_from_books = 0
    for item in notebooks.get("books") or []:
        total_from_books += int(item.get("reviewCount") or 0)
        total_from_books += int(item.get("noteCount") or 0)
        total_from_books += int(item.get("bookmarkCount") or 0)
    return total_from_books


def public_secret_counts(data: dict[str, Any]) -> tuple[int, int]:
    shelf = data.get("shelf") or {}
    public = 0
    secret = 0
    for book in shelf.get("books") or []:
        if int(book.get("secret") or 0) == 1:
            secret += 1
        else:
            public += 1
    for album in shelf.get("albums") or []:
        extra = album.get("albumInfoExtra") or {}
        if int(extra.get("secret") or 0) == 1:
            secret += 1
        else:
            public += 1
    if shelf.get("mp"):
        secret += 1
    return public, secret


def year_times(overall: dict[str, Any]) -> list[tuple[str, int, str]]:
    props = overall.get("readTimes") or {}
    rows: list[tuple[str, int, str]] = []
    for key, value in props.items():
        # API returns bucket timestamps. For year buckets, UTC/local shifts do not
        # matter for the displayed year in this report enough to justify deps.
        try:
            import datetime as _dt

            year = str(_dt.datetime.fromtimestamp(int(key)).year)
        except Exception:
            year = str(key)
        seconds = int(value or 0)
        rows.append((year, seconds, fmt_seconds(seconds)))
    return rows


def extract_title(entry: dict[str, Any]) -> str:
    if "book" in entry and isinstance(entry["book"], dict):
        return entry["book"].get("title") or ""
    book_info = (((entry.get("book") or {}).get("bookInfo")) or {})
    return book_info.get("title") or entry.get("title") or ""


def extract_author(entry: dict[str, Any]) -> str:
    if "book" in entry and isinstance(entry["book"], dict):
        return entry["book"].get("author") or ""
    book_info = (((entry.get("book") or {}).get("bookInfo")) or {})
    return book_info.get("author") or entry.get("author") or ""


def render_metrics(data: dict[str, Any]) -> str:
    shelf = data.get("shelf") or {}
    reading = data.get("reading") or {}
    overall = reading.get("overall") or {}
    books = shelf.get("books") or []
    albums = shelf.get("albums") or []
    public, secret = public_secret_counts(data)
    metrics = [
        (str(visible_shelf_total(data)), "可见书架条目"),
        (fmt_seconds(overall.get("totalReadTime")), "累计阅读时长"),
        (str(overall.get("readDays") or 0), "有效阅读天数"),
        (str(notebook_total(data)), "笔记与标注"),
        (reading_stat(overall, "读过"), "读过"),
        (reading_stat(overall, "读完", str(sum(1 for b in books if b.get("finishReading") == 1))), "读完"),
        (f"{public} / {secret}", "公开 / 私密"),
        (f"{len(books)} / {len(albums)}", "电子书 / 有声书"),
    ]
    return "\n".join(
        f'<div class="metric"><strong>{esc(value)}</strong><span>{esc(label)}</span></div>'
        for value, label in metrics
    )


def render_category_section(data: dict[str, Any]) -> str:
    books = get_books(data)
    counts = category_counts(books, 8)
    max_count = max((count for _, count in counts), default=1)
    bars = []
    bar_classes = ["", "indigo", "brass", "moss"]
    for idx, (name, count) in enumerate(counts):
        width = round(count / max_count * 100)
        cls = bar_classes[idx % len(bar_classes)]
        bars.append(
            '<div class="score">'
            f"<span>{esc(name)}</span>"
            f'<div class="bar {cls}"><i style="width:{width}%"></i></div>'
            f"<b>{count}</b>"
            "</div>"
        )

    overall = (data.get("reading") or {}).get("overall") or {}
    pref_rows = []
    for item in (overall.get("preferCategory") or [])[:8]:
        pref_rows.append(
            "<tr>"
            f"<td>{esc(item.get('categoryTitle'))}</td>"
            f"<td>{esc(item.get('readingCount'))}</td>"
            f"<td>{esc(fmt_seconds(item.get('readingTime')))}</td>"
            "</tr>"
        )

    return f"""
      <section>
        <h2>阅读 DNA</h2>
        <div class="grid">
          <div class="card half">
            <h3>藏书重力</h3>
            {''.join(bars)}
          </div>
          <div class="card half">
            <h3>实际阅读偏好</h3>
            <table class="table">
              <thead><tr><th>分类</th><th>本数</th><th>时长</th></tr></thead>
              <tbody>{''.join(pref_rows)}</tbody>
            </table>
          </div>
          <div class="card full">
            <h3>结构判断</h3>
            <p>你的阅读结构不是单一工具型。技术书提供工具和实现能力，文学、历史、科幻与心理书则提供叙事、尺度、制度感和自我理解。</p>
          </div>
        </div>
      </section>
    """


def render_years(data: dict[str, Any]) -> str:
    overall = (data.get("reading") or {}).get("overall") or {}
    years = [row for row in year_times(overall) if int(row[1]) > 0]
    years = years[-6:] or year_times(overall)[-6:]
    max_seconds = max((seconds for _, seconds, _ in years), default=1)
    blocks = []
    for year, seconds, text in years:
        height = max(2, round(seconds / max_seconds * 100)) if max_seconds else 2
        blocks.append(
            '<div class="year">'
            f'<div class="col" style="height:{height}%"></div>'
            f"<b>{esc(year)}</b><small>{esc(text)}</small>"
            "</div>"
        )
    return "".join(blocks)


def render_longest_books(data: dict[str, Any]) -> str:
    overall = (data.get("reading") or {}).get("overall") or {}
    cards = []
    for item in (overall.get("readLongest") or [])[:6]:
        title = extract_title(item)
        author = extract_author(item)
        read_time = fmt_seconds(item.get("readTime"))
        cards.append(
            '<div class="card">'
            f"<h3>《{esc(title)}》</h3>"
            f"<p>{esc(author)} · {esc(read_time)}。这本书是你阅读画像里的强信号之一。</p>"
            "</div>"
        )
    return "".join(cards)


def render_recommendations(data: dict[str, Any]) -> str:
    rec = data.get("recommendations") or {}
    books = rec.get("books") if isinstance(rec, dict) else rec
    cards = []
    for book in (books or [])[:4]:
        category = book.get("category") or ""
        # Filter obviously weak matches less aggressively; leave final judgment to report text.
        cards.append(
            '<div class="card">'
            f"<h3>{esc(book.get('title'))}</h3>"
            f"<p>{esc(book.get('author'))} · {esc(category)}。可作为下一阶段阅读候选。</p>"
            "</div>"
        )
    if not cards:
        cards.append(
            '<div class="card full"><h3>下一本书</h3><p>推荐数据不足。可优先从你书架中的技术、历史制度、科幻和心理类书继续推进。</p></div>'
        )
    return "".join(cards)


def render_body(data: dict[str, Any]) -> str:
    reading = data.get("reading") or {}
    overall = reading.get("overall") or {}
    annual = reading.get("annually") or {}
    monthly = reading.get("monthly") or {}
    weekly = reading.get("weekly") or {}
    read_days = int(overall.get("readDays") or 0)
    total_seconds = int(overall.get("totalReadTime") or 0)
    note_count = notebook_total(data)
    notes_per_hour = round(note_count / (total_seconds / 3600), 1) if total_seconds else 0

    return f"""
      <section>
        <h2>一眼看见你</h2>
        <div class="grid">{render_metrics(data)}</div>
      </section>

      <section>
        <h2>你的阅读人格</h2>
        <div class="grid">
          <div class="card">
            <h3>技术建造者</h3>
            <p>你的书架和累计偏好都显示出明显的计算机与工程取向。你读书时常在寻找可以落地的工具、方法和结构。</p>
            <span class="chip">计算机偏好</span><span class="chip">工具型知识</span>
          </div>
          <div class="card">
            <h3>系统观察者</h3>
            <p>你会被流程、权力、成本、因果和执行链条吸引。对你来说，书里真正有意思的地方常常是“事情如何发生”。</p>
            <span class="chip">流程</span><span class="chip">制度</span>
          </div>
          <div class="card">
            <h3>夜间学者</h3>
            <p>{esc(overall.get('preferTimeWord') or '你的阅读时段偏好需要更多数据确认。')}。你更像在安静时段回到书里处理问题。</p>
            <span class="chip">时间节律</span><span class="chip">深读窗口</span>
          </div>
          <div class="card">
            <h3>注释采集者</h3>
            <p>你留下 {note_count} 条笔记与标注，约 {notes_per_hour} 条/小时。你的笔记不是装饰，而是理解支架。</p>
            <span class="chip">高标注密度</span><span class="chip">主动加工</span>
          </div>
          <div class="card wide">
            <h3>一句话画像</h3>
            <blockquote class="quote">你是一个工程理性驱动、系统感强、在阶段性深读中用笔记建立理解结构的读者。</blockquote>
          </div>
        </div>
      </section>

      {render_category_section(data)}

      <section>
        <h2>时间节律</h2>
        <div class="grid">
          <div class="card wide">
            <h3>年度阅读曲线</h3>
            <div class="timeline" aria-label="年度阅读时长">{render_years(data)}</div>
          </div>
          <div class="card">
            <h3>当前季节</h3>
            <p>今年：{esc(fmt_seconds(annual.get('totalReadTime')))}；本月：{esc(fmt_seconds(monthly.get('totalReadTime')))}；本周：{esc(fmt_seconds(weekly.get('totalReadTime')))}。如果当前数据很少，应把判断重点放在长期模式上。</p>
          </div>
          <div class="card full">
            <h3>节律判断</h3>
            <p>你并不一定适合每日匀速打卡。更自然的方式是主题式阅读：围绕一个问题连续推进两周，再沉淀一份笔记。</p>
          </div>
        </div>
      </section>

      <section>
        <h2>注释里的心智</h2>
        <div class="grid">
          <div class="card half">
            <h3>笔记行为</h3>
            <ul class="list">
              <li>有笔记的书：{esc((data.get('notebooks') or {}).get('totalBookCount') or 0)} 本。</li>
              <li>笔记总数：{note_count} 条。</li>
              <li>阅读日均强度：约 {esc(fmt_seconds(total_seconds // read_days if read_days else 0))} / 有效阅读日。</li>
            </ul>
          </div>
          <div class="card half">
            <h3>思考方式</h3>
            <ul class="list">
              <li>遇到技术内容时，你倾向于把它转化为可执行能力。</li>
              <li>遇到历史叙事时，你会追问制度、权力和底层成本。</li>
              <li>遇到心理与关系主题时，你在寻找自我解释和相处方法。</li>
            </ul>
          </div>
        </div>
      </section>

      <section>
        <h2>代表性书目</h2>
        <div class="grid">{render_longest_books(data)}</div>
      </section>

      <section>
        <h2>下一条阅读路径</h2>
        <div class="grid">
          {render_recommendations(data)}
          <div class="card full">
            <h3>阅读任务建议</h3>
            <p>选择一个主题，不要选择十本书。比如“嵌入式补骨架”“历史里的执行系统”或“科幻里的工程问题”，每天推进 20-40 分钟，两周后做一次复盘。</p>
          </div>
        </div>
      </section>

      <section>
        <h2>数据说明</h2>
        <p class="footer-note">本报告使用微信读书书架、阅读统计、笔记本概览和推荐数据生成。阅读时长按秒转换；书架总量按电子书、有声书/专辑和文章收藏入口计算；当前周/月/年数据稀疏时，报告优先采用长期模式。</p>
      </section>
    """


def generate(data: dict[str, Any], template: str, theme: str) -> str:
    overall = (data.get("reading") or {}).get("overall") or {}
    theme_class = "theme-modern" if theme == "modern" else "theme-classic"
    title = "阅读人格报告"
    lede = (
        "你的书架有清晰的知识重力，也保留着文学、历史、科幻和心理的侧翼。"
        "这份报告把微信读书数据转化为一张可阅读的个人画像。"
    )
    meta = (
        f"累计阅读 {fmt_seconds(overall.get('totalReadTime'))}，"
        f"有效阅读 {overall.get('readDays') or 0} 天，"
        f"笔记 {notebook_total(data)} 条。"
    )
    replacements = {
        "{{REPORT_TITLE}}": "阅读人格报告｜微信读书画像",
        "{{THEME_CLASS}}": theme_class,
        "{{EYEBROW}}": f"WeRead Persona · {esc(data.get('generatedAt') or '')}",
        "{{TITLE}}": title,
        "{{LEDE}}": lede,
        "{{META}}": meta,
        "{{REPORT_BODY}}": render_body(data),
    }
    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate read-persona HTML.")
    parser.add_argument("input", help="JSON generated by fetch_persona_data.py")
    parser.add_argument("--output", "-o", required=True, help="Output HTML path")
    parser.add_argument("--theme", choices=["classic", "modern"], default="classic")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    template = Path(args.template).read_text(encoding="utf-8")
    html_text = generate(data, template, args.theme)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
