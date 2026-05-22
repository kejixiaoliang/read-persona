---
name: read-persona
description: Generate a polished HTML reading-persona report from WeRead data. Use when the user asks to analyze their reading personality, reading persona, reading profile, reading temperament, reading habits, WeRead identity, bookish self, or says "分析我的阅读人格"; this skill should call the WeRead skill/API for shelf, reading statistics, notes, and recommendations, then synthesize an elegant single-page HTML report.
---

# Read Persona

## Overview

Create a refined, bookish HTML report that turns a user's WeRead data into a reading-persona portrait. Use `weread-skills` as the data source; this skill is the analysis and presentation layer.

## Data Workflow

1. Load the relevant `weread-skills` docs before calling APIs:
   - `shelf.md` for shelf size, public/private counts, categories, finished books.
   - `readdata.md` for reading time, read days, note counts, category/time preferences.
   - `notes.md` when analyzing note density, recurring themes, or book-level thinking.
   - `discover.md` when recommending next books.
2. Call WeRead APIs through the same gateway pattern documented in `weread-skills`:
   - `/shelf/sync` for shelf composition and category distribution.
   - `/readdata/detail` with `mode=overall`, `annually`, `monthly`, and `weekly` for habit and trend analysis.
   - `/user/notebooks` when note overview or note density is needed; paginate with top-level `count` and `lastSort`.
   - `/book/bookmarklist` and `/review/list/mine` only when the user asks for book-level thinking or representative note themes.
   - `/book/recommend` and `/book/similar` for the "next reading path" section when useful.
3. Respect all source semantics from `weread-skills`:
   - Treat reading time fields as seconds and display as `X小时Y分钟`.
   - Treat `readDays` as effective reading days.
   - Treat `dayAverageReadTime` as natural-day average, not reading-day average.
   - Shelf visible total is `books.length + albums.length + (mp non-empty ? 1 : 0)`.
   - Notebook total is `reviewCount + noteCount + bookmarkCount`.

## Persona Dimensions

Score and describe the user across these dimensions. Use 0-100 scores when there is enough evidence; otherwise use qualitative labels.

- **Reading Engine**: what drives the user to read, such as technical mastery, story immersion, self-understanding, historical curiosity, or practical problem solving.
- **Knowledge Shape**: whether the library is tool-oriented, system-oriented, literary, exploratory, emotional, or archival.
- **Depth Pattern**: infer from total time, reading days, finished books, read-longest list, and note density.
- **Temporal Rhythm**: infer from `preferTime`, `preferTimeWord`, weekly/monthly activity, and yearly trend.
- **Annotation Style**: infer from notebook counts and sample notes. Common labels: glossary collector, systems observer, emotion marker, quote keeper, question asker, synthesis writer.
- **Genre Gravity**: use shelf categories and `preferCategory` from reading stats.
- **Current Season**: compare current year/month/week with historical peaks.
- **Next Best Path**: recommend a short reading route that fits the persona.

## HTML Output Rules

Always produce a complete standalone `.html` file unless the user explicitly requests inline HTML only.

Use a refined reading feel:

- Single-page editorial report, not a dashboard app.
- Warm paper-like background with high-contrast ink text.
- Use serif display headings and readable body text.
- Include subtle sections: hero, metrics, persona cards, category map, rhythm, annotations, next reading path.
- Avoid garish gradients, decorative blobs, and generic marketing hero sections.
- Keep layout responsive for desktop and mobile.
- Use inline CSS; avoid external network assets.
- Use semantic HTML and accessible contrast.
- Add a small "Data Notes" section naming API modes used and any limitations.

Suggested file location:

```text
exports/read-persona-report.html
```

If a report already exists, create a timestamped or clearly named file rather than overwriting unless the user asks.

## Report Structure

Use this structure by default:

1. **Hero**: title, date, one-line persona summary.
2. **At A Glance**: shelf size, total reading time, read days, books read, finished books, notes.
3. **Persona Archetype**: 3-5 archetype chips, each grounded in data.
4. **Reading DNA**: category and author preferences; explain what they imply.
5. **Rhythm**: preferred hours, yearly trend, active/inactive seasons.
6. **Annotation Mind**: note density, common note behaviors, recurring thought patterns.
7. **Representative Books**: books with longest reading time or strongest preference signal.
8. **Next Reading Path**: 3-6 recommended books or reading missions.
9. **Data Notes**: exact modes and important caveats.

## Analysis Style

Write with literary warmth and analytic precision. Ground claims in numbers, but avoid sounding like a spreadsheet. Prefer formulations like:

- "Your library has a technical spine, but its lungs are literary."
- "You do not read every day; you return in seasons."
- "Your notes show a systems reader: you mark not only what happens, but how power, process, and cost move through a scene."

Do not overclaim. If the data is sparse for the current week or year, say so plainly and shift attention to long-term patterns.

## Validation

Before finalizing:

1. Confirm all major numbers are internally consistent.
2. Confirm time units were converted from seconds.
3. Confirm the HTML opens as a standalone file.
4. If possible, run a local syntax/sanity check by reading the file and verifying it contains `<html`, `<style`, and the key section headings.
5. In the final response, link to the generated HTML file and summarize the persona in 2-4 sentences.
