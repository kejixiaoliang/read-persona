---
name: read-persona
description: 根据微信读书数据生成精致的 HTML 阅读人格报告。当用户要求分析阅读人格、阅读画像、阅读习惯、阅读偏好、微信读书身份、书架气质，或说“分析我的阅读人格”时使用；本 Skill 应调用 weread-skills 获取书架、阅读统计、笔记和推荐数据，并综合生成单页 HTML 报告。
---

# Read Persona

## 概览

把用户的微信读书数据转化为一份精致、有阅读感的 HTML 阅读人格报告。`weread-skills` 负责底层数据连接，本 Skill 负责分析、归纳和视觉呈现。

## 数据流程

优先使用脚本完成稳定的数据采集和报告生成；只有脚本无法满足用户要求时，才手动调用接口并临场生成 HTML。

1. 调用 API 前，先按任务读取 `weread-skills` 的对应文档：
   - `shelf.md`：书架数量、公开/私密、分类、读完数。
   - `readdata.md`：阅读时长、阅读天数、笔记数、分类偏好、时间偏好。
   - `notes.md`：需要分析笔记密度、反复主题或单本书思考时读取。
   - `discover.md`：需要推荐下一本书或阅读路径时读取。
2. 按 `weread-skills` 文档里的网关方式调用微信读书 API：
   - `/shelf/sync`：书架构成与分类分布。
   - `/readdata/detail`：使用 `overall`、`annually`、`monthly`、`weekly` 分析习惯和趋势。
   - `/user/notebooks`：需要笔记概览或笔记密度时调用；分页只能使用顶层 `count` 和 `lastSort`。
   - `/book/bookmarklist` 与 `/review/list/mine`：只有用户要求单本书思考、代表性笔记或划线回顾时调用。
   - `/book/recommend` 与 `/book/similar`：需要生成“下一条阅读路径”时调用。
3. 严格遵守 `weread-skills` 的数据口径：
   - 所有阅读时长字段都按“秒”处理，并展示为 `X小时Y分钟`。
   - `readDays` 是有效阅读天数。
   - `dayAverageReadTime` 是自然日平均，不是阅读日平均。
   - 可见书架总数为 `books.length + albums.length + (mp 非空 ? 1 : 0)`。
   - 笔记总数为 `reviewCount + noteCount + bookmarkCount`。

## 脚本工作流

默认两步生成报告：

```bash
python scripts/fetch_persona_data.py --output exports/persona-data.json
python scripts/generate_report.py exports/persona-data.json --output exports/read-persona-report.html --theme classic
```

Windows/PowerShell 环境优先使用：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fetch_persona_data.ps1 -Output exports/persona-data.json
py scripts/generate_report.py exports/persona-data.json --output exports/read-persona-report.html --theme classic
```

脚本说明：

- `scripts/fetch_persona_data.py`：读取 `WEREAD_API_KEY`，拉取书架、总计/年度/月度/周度阅读统计、笔记本概览和个性化推荐，输出 JSON。脚本不会打印 API Key。
- `scripts/fetch_persona_data.ps1`：PowerShell 版数据采集脚本，适合 Windows 环境；功能与 Python 版一致。
- `scripts/generate_report.py`：读取上一步 JSON，使用 `assets/report-template.html` 生成独立 HTML 报告。

采集脚本常用参数：

- `--timeout 20`：单次请求超时秒数，默认 20。
- `--max-notebook-pages 3`：最多拉取多少页笔记本概览，默认 3，避免长时间分页。
- `--skip-recommendations`：网络不稳定或只需要画像时跳过推荐接口。

PowerShell 版对应参数为 `-TimeoutSec`、`-MaxNotebookPages`、`-SkipRecommendations`。

主题参数：

- 用户未指定主题：使用 `--theme classic`。
- 用户说“经典、书卷、纸页、阅读感”：使用 `classic`。
- 用户说“现代、极简、干净、适合分享”：使用 `modern`。

如果当前环境的命令是 PowerShell，优先用 `py` 或可用的 Python 运行脚本。

## 阅读人格维度

在数据足够时给出 0-100 分或清晰的强弱判断；数据不足时只做定性描述。

- **阅读引擎**：用户为什么读书，例如技术掌握、故事沉浸、自我理解、历史好奇、实际问题求解。
- **知识形状**：书架更偏工具型、系统型、文学型、探索型、情感型，还是资料库型。
- **深读模式**：结合总时长、阅读天数、读完数、读得最久的书和笔记密度判断。
- **时间节律**：结合 `preferTime`、`preferTimeWord`、周/月/年度活跃度判断。
- **标注风格**：结合笔记本概览和样本笔记判断。常见标签包括：查词考据者、系统观察者、情绪标记者、摘句收藏者、问题追问者、综合型笔记者。
- **类型重力**：结合书架分类和 `preferCategory` 判断。
- **当前阅读季节**：用当前年/月/周和历史高峰对比。
- **下一条阅读路径**：给出适合该阅读人格的短路线。

## HTML 输出规则

除非用户明确要求只输出内联 HTML，否则始终生成完整独立的 `.html` 文件。

优先使用 `assets/report-template.html` 作为基础模板，不要每次临场重新发明布局。替换以下占位符：

- `{{REPORT_TITLE}}`
- `{{THEME_CLASS}}`
- `{{EYEBROW}}`
- `{{TITLE}}`
- `{{LEDE}}`
- `{{META}}`
- `{{REPORT_BODY}}`

内置主题：

- `classic`：默认主题。将 `{{THEME_CLASS}}` 设为 `theme-classic`，呈现温暖纸页、藏书票、阅读室质感。
- `modern`：当用户要求极简、现代、干净、适合分享时使用。将 `{{THEME_CLASS}}` 设为 `theme-modern`。

视觉要求：

- 做成单页编辑式报告，不做冷冰冰的数据仪表盘。
- 使用温暖纸页背景和高对比墨色文字。
- 标题有书卷感，正文易读。
- 包含：开场、关键指标、人格卡片、分类地图、阅读节律、笔记心智、下一条阅读路径。
- 避免刺眼渐变、装饰性光球、无意义背景图。
- 桌面和移动端都要可读。
- 使用内联 CSS，不依赖外部网络资源。
- 使用语义化 HTML，并保证对比度。
- 增加“数据说明”小节，说明用到的 API 模式和限制。

建议输出位置：

```text
exports/read-persona-report.html
```

如果报告已存在，除非用户要求覆盖，否则创建带时间戳或清晰名称的新文件。

## 默认报告结构

默认按以下结构生成：

1. **开场**：标题、日期、一句话阅读人格画像。
2. **一眼看见你**：书架数量、总阅读时长、阅读天数、读过、读完、笔记数。
3. **阅读人格标签**：3-5 个标签，每个都要有数据依据。
4. **阅读 DNA**：分类、作者、出版社或主题偏好，并解释含义。
5. **时间节律**：偏好时段、年度趋势、活跃期与沉寂期。
6. **注释心智**：笔记密度、笔记行为、反复出现的思考模式。
7. **代表性书目**：读得最久或信号最强的书。
8. **下一条阅读路径**：3-6 本推荐书或阅读任务。
9. **数据说明**：具体 API 模式、统计口径和限制。

## 分析风格

语言要有文学温度，也要有分析精度。结论必须落在数字上，但不要写成表格解说。

推荐表达：

- “你的书架有一条技术脊梁，但肺叶里呼吸着文学。”
- “你不是每天匀速前进的打卡型读者，而是阶段性回到书里深挖。”
- “你的笔记显示出系统观察者气质：你标记的不只是发生了什么，还有权力、流程和代价如何移动。”

不要过度推断。如果本周或今年数据很少，要直接说明，并把重点转向长期模式。

## 故障处理

如果没有安装 `weread-skills`，或找不到它的文件：

1. 告诉用户 Read Persona 需要微信读书官方 Skill 作为数据连接器。
2. 提供安装命令：

```bash
npx skills add Tencent/WeChatReading -g
```

3. 提供官方配置页：

```text
https://weread.qq.com/r/weread-skills
```

4. 不要编造阅读数据。提示用户安装完成后再继续。

如果缺少 `WEREAD_API_KEY`：

1. 告诉用户必须配置该环境变量。
2. 引导用户到官方配置页登录并获取 Key：

```text
https://weread.qq.com/r/weread-skills
```

3. 提供 Windows 配置命令：

```powershell
[Environment]::SetEnvironmentVariable('WEREAD_API_KEY', 'wrk-你的apikey', 'User')
```

4. 提醒用户设置后重新打开 Codex 会话或终端。

如果 API 返回 `401`、`用户不存在` 或空响应：

- 说明 Key 可能无效、过期、未绑定，或当前进程不可见。
- 可以检查 `WEREAD_API_KEY` 是否存在，但不要打印 Key 内容。
- 请用户从官方配置页重新生成或重新配置 Key。

如果脚本运行失败：

- 先阅读错误消息。`fetch_persona_data.py` 的错误通常是 Key、网络或 WeRead API 返回错误。
- `generate_report.py` 的错误通常是输入 JSON 路径、模板路径或主题参数错误。
- 不要绕过脚本重新发明一份风格完全不同的报告；优先修复脚本输入或参数。

## 校验

交付前检查：

1. 主要数字内部一致。
2. 所有时长都已从秒转换。
3. 除非用户明确要求自定义 HTML，否则已使用 `assets/report-template.html`。
4. 主题是 `classic` 或 `modern`。
5. HTML 是可独立打开的完整文件。
6. 尽量做本地 sanity check：文件中应包含 `<html`、`<style` 和关键章节标题。
7. 最终回复里给出 HTML 文件链接，并用 2-4 句话总结阅读人格。
