# Read Persona Report Template

Use this reference when generating the HTML report.

## Visual Direction

- Background: warm paper (`#f7f0e6`, `#fbf7ef`) with ink text (`#211a16`).
- Accent palette: oxblood, muted moss, brass, deep indigo.
- Typography: system serif for headings, system sans for labels and metrics.
- Motifs: margins, rules, chapter labels, bookplate-like cards.
- Avoid remote fonts, external images, and decorative blobs.

## Suggested Archetypes

Choose 2-4 based on data:

- Systems Reader: marks process, power, cause/effect, institutions, execution chains.
- Technical Builder: reads programming, engineering, tooling, and implementation books.
- Night Scholar: preference time clusters in late evening or after midnight.
- Seasonal Sprinter: high reading years/months interrupted by quiet periods.
- Annotation Forager: high note density, many glossary/context notes.
- Historical Operator: reads history through institutions, logistics, and decision costs.
- Reflective Romantic: recurring psychology, intimacy, and relationship reading.
- Cosmic Engineer: blends science fiction with technical and scientific curiosity.

## HTML Skeleton

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>阅读人格报告</title>
  <style>
    :root {
      --paper: #f7f0e6;
      --paper-2: #fffaf1;
      --ink: #211a16;
      --muted: #6f6258;
      --rule: #d8c7b0;
      --accent: #8b3f2f;
      --moss: #556b4e;
      --brass: #a9783a;
      --indigo: #26364f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: "Noto Serif SC", "Songti SC", "SimSun", Georgia, serif;
      line-height: 1.72;
    }
    .page { max-width: 1120px; margin: 0 auto; padding: 48px 24px 72px; }
    .hero { border-bottom: 1px solid var(--rule); padding-bottom: 28px; }
    .eyebrow { font: 700 12px/1.2 system-ui, sans-serif; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); }
    h1 { margin: 14px 0; font-size: clamp(36px, 7vw, 84px); line-height: 1.02; letter-spacing: 0; }
    h2 { margin: 48px 0 18px; font-size: clamp(24px, 3vw, 38px); line-height: 1.15; }
    .lede { max-width: 760px; font-size: 20px; color: var(--muted); }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
    .metric, .card {
      background: color-mix(in srgb, var(--paper-2) 88%, white);
      border: 1px solid var(--rule);
      border-radius: 8px;
      padding: 18px;
    }
    .metric { grid-column: span 3; }
    .metric strong { display:block; font-size: 30px; line-height: 1.1; }
    .metric span, .label { font: 700 12px/1.3 system-ui, sans-serif; color: var(--muted); }
    .card { grid-column: span 4; }
    .wide { grid-column: span 8; }
    .full { grid-column: 1 / -1; }
    .chip { display:inline-block; margin: 0 8px 8px 0; padding: 6px 10px; border:1px solid var(--rule); border-radius:999px; font: 700 13px system-ui, sans-serif; color: var(--indigo); }
    @media (max-width: 760px) { .metric, .card, .wide { grid-column: 1 / -1; } .page { padding: 28px 16px 48px; } }
  </style>
</head>
<body>
  <main class="page">
    <!-- Fill with report content. -->
  </main>
</body>
</html>
```
