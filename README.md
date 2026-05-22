# Read Persona

**Read Persona** 是一个基于微信读书数据生成「阅读人格画像」的 Codex Skill。它会调用微信读书官方 Skill 获取书架、阅读统计、笔记和推荐数据，然后输出一份具有阅读质感的单页 HTML 报告。

它不是简单的数据看板，而是把阅读行为转化为更具解释力的画像：你为什么读、常读什么、何时读、如何做笔记、在哪些主题上反复停留，以及下一步适合读什么。

## 功能特性

- 生成精致的单页 HTML 阅读人格报告
- 分析微信读书书架结构与分类偏好
- 汇总累计阅读时长、有效阅读天数、读过/读完数量
- 识别阅读节律，例如夜间阅读、阶段性爆发、长期沉寂
- 分析笔记密度与标注风格
- 归纳阅读人格标签，例如「技术建造者」「系统观察者」「夜间学者」
- 根据阅读偏好生成下一步阅读路径
- 支持 `classic` 与 `modern` 两种 HTML 主题
- 提供数据采集脚本和报告生成脚本，便于复用与排错

## 前置条件

1. 安装微信读书官方 Skill：

```bash
npx skills add Tencent/WeChatReading -g
```

官方配置页：

```text
https://weread.qq.com/r/weread-skills
```

2. 配置有效的微信读书 API Key：

```powershell
[Environment]::SetEnvironmentVariable('WEREAD_API_KEY', 'wrk-你的apikey', 'User')
```

设置后重新打开 Codex 会话或终端，让环境变量生效。

## 安装

将 `read-persona` 文件夹放入 Codex Skills 目录：

```text
~/.codex/skills/read-persona
```

Windows 常见路径：

```text
C:\Users\<你的用户名>\.codex\skills\read-persona
```

目录结构：

```text
read-persona/
├─ README.md
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ assets/
│  └─ report-template.html
├─ references/
│  └─ report-template.md
└─ scripts/
   ├─ fetch_persona_data.ps1
   ├─ fetch_persona_data.py
   └─ generate_report.py
```

## 使用方式

在 Codex 中输入：

```text
分析我的阅读人格
```

或显式调用：

```text
使用 $read-persona 分析我的微信读书阅读人格，并生成一份精致的 HTML 报告。
```

## 脚本工作流

你也可以手动运行脚本：

```bash
python scripts/fetch_persona_data.py --output exports/persona-data.json
python scripts/generate_report.py exports/persona-data.json --output exports/read-persona-report.html --theme classic
```

Windows/PowerShell 推荐：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fetch_persona_data.ps1 -Output exports/persona-data.json
py scripts/generate_report.py exports/persona-data.json --output exports/read-persona-report.html --theme classic
```

采集脚本常用参数：

```bash
python scripts/fetch_persona_data.py --output exports/persona-data.json --timeout 20 --max-notebook-pages 3
```

PowerShell 版：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fetch_persona_data.ps1 -Output exports/persona-data.json -TimeoutSec 20 -MaxNotebookPages 3
```

如果推荐接口不稳定，或只需要阅读画像：

```bash
python scripts/fetch_persona_data.py --output exports/persona-data.json --skip-recommendations
```

主题参数：

- `classic`：纸页、书卷、阅读室质感，默认主题
- `modern`：极简、干净、适合分享

## 数据来源

- `/shelf/sync`：书架总量、电子书、有声书、文章收藏、公开/私密、分类分布
- `/readdata/detail`：累计阅读时长、阅读天数、年度/月度/周度趋势、偏好分类、偏好时间段
- `/user/notebooks`：有笔记的书、笔记数量、划线数量、想法数量
- `/book/recommend`：个性化推荐

## 隐私与安全

- 不要将 `WEREAD_API_KEY` 提交到 Git 仓库
- 不要公开包含真实私密书籍或笔记的报告
- 开源时建议只发布 Skill 文件，不发布个人生成的 HTML 报告
- 如果 API Key 曾经泄露，建议重新生成或更换

## 故障排查

如果没有安装微信读书 Skill：

```bash
npx skills add Tencent/WeChatReading -g
```

如果缺少 API Key：

```text
https://weread.qq.com/r/weread-skills
```

如果接口返回 `401`、`用户不存在` 或空响应，通常表示 Key 无效、过期、未绑定，或当前进程读不到环境变量。

## 校验

```powershell
$env:PYTHONUTF8='1'
py C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<你的用户名>\.codex\skills\read-persona
```

期望输出：

```text
Skill is valid!
```

## 许可证

建议使用 MIT License 或 Apache-2.0。正式开源前请补充 `LICENSE` 文件。
