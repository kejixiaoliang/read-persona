# Read Persona

**Read Persona** 是一个基于微信读书数据生成「阅读人格画像」的 Codex Skill。它会调用微信读书相关 Skill 获取书架、阅读统计、笔记和推荐数据，然后输出一份具有阅读质感的单页 HTML 报告。

它不是简单的数据看板，而是把你的阅读行为转化为更具解释力的画像：你为什么读、常读什么、何时读、如何做笔记、在哪些主题上反复停留，以及下一步适合读什么。

## 功能特性

- 生成精致的单页 HTML 阅读人格报告
- 分析微信读书书架结构与分类偏好
- 汇总累计阅读时长、有效阅读天数、读过/读完数量
- 识别阅读节律，例如夜间阅读、阶段性爆发、长期沉寂等
- 分析笔记密度与标注风格
- 归纳阅读人格标签，例如「技术建造者」「系统观察者」「夜间学者」
- 根据阅读偏好生成下一步阅读路径
- 输出可直接在浏览器打开的本地 HTML 文件

## 适用场景

当你想回答这些问题时，可以使用本 Skill：

- 分析我的阅读人格
- 给我做一份微信读书阅读画像
- 我是怎样的读者？
- 分析我的阅读习惯和偏好
- 基于微信读书数据生成一份好看的 HTML 报告
- 总结我的阅读风格、笔记风格和推荐下一本书

## 前置条件

Read Persona 是一个上层分析 Skill，它本身不直接维护微信读书 API 的完整接口说明。使用前需要满足以下条件：

1. 已安装并可用 `weread-skills`

   `weread-skills` 负责提供微信读书接口的调用规范，包括书架、阅读统计、笔记、划线、推荐等能力。

   官方配置页面：

   ```text
   https://weread.qq.com/r/weread-skills
   ```

   官方安装指令：

   ```bash
   npx skills add Tencent/WeChatReading -g
   ```

2. 已配置有效的微信读书 API Key

   环境变量名称：

   ```powershell
   WEREAD_API_KEY
   ```

   Windows 示例：

   ```powershell
   [Environment]::SetEnvironmentVariable('WEREAD_API_KEY', 'wrk-你的apikey', 'User')
   ```

   设置后建议重新打开 Codex 会话或终端，让环境变量生效。

   API Key 获取方式：

   1. 打开微信读书 Skill 官方配置页：

      ```text
      https://weread.qq.com/r/weread-skills
      ```

   2. 登录微信读书账号。
   3. 页面会提供用于连接个人微信读书账号的 API Key。
   4. 将 API Key 配置为本机环境变量 `WEREAD_API_KEY`。

   该 API Key 用于读取你的个人微信读书信息，数据仅对你可见。请勿提交到 Git 仓库或公开分享。

## 工作原理

Read Persona 会按需读取微信读书数据，并将其综合成阅读人格报告。

主要数据来源：

- `/shelf/sync`：书架总量、电子书、有声书、文章收藏、公开/私密、分类分布
- `/readdata/detail`：累计阅读时长、阅读天数、年度/月度/周度趋势、偏好分类、偏好时间段
- `/user/notebooks`：有笔记的书、笔记数量、划线数量、想法数量
- `/book/bookmarklist`：单本书划线内容，按需使用
- `/review/list/mine`：单本书个人想法与点评，按需使用
- `/book/recommend`、`/book/similar`：个性化推荐和相似书推荐

Read Persona 会特别遵守微信读书数据口径：

- 阅读时长字段按「秒」处理，并转换为「X小时Y分钟」
- `readDays` 表示有效阅读天数
- `dayAverageReadTime` 是自然日平均，不等于阅读日平均
- 书架总数按 `books.length + albums.length + mp入口` 计算
- 笔记总数按 `reviewCount + noteCount + bookmarkCount` 计算

## 输出内容

默认生成一个完整的 HTML 文件，例如：

```text
exports/read-persona-report.html
```

报告通常包含以下部分：

1. 阅读人格标题与一句话画像
2. 关键指标：书架数量、阅读时长、阅读天数、读过/读完、笔记数
3. 阅读人格标签
4. 阅读 DNA：分类偏好、作者偏好、主题偏好
5. 时间节律：年度趋势、当前阅读季节、偏好时段
6. 注释心智：笔记密度、标注方式、思考模式
7. 代表性书目
8. 下一条阅读路径
9. 数据说明与限制

## 示例输出风格

报告不是冷冰冰的表格，而是偏书页感、杂志感的阅读画像。

示例表述：

> 你的书架有一条坚硬的技术脊梁，但肺叶里呼吸着文学、科幻、历史与心理。

> 你不是每天匀速前进的打卡型读者，而是带着问题回到书里，在某些阶段突然深挖、标注、追问。

> 你是一个工程理性驱动、历史制度敏感、夜间深挖、以笔记建立理解支架的读者。

## 安装方式

### 1. 安装微信读书 Skill

Read Persona 依赖微信读书官方 Skill 提供数据连接能力。先安装 `weread-skills`：

```bash
npx skills add Tencent/WeChatReading -g
```

安装与 API Key 获取入口：

```text
https://weread.qq.com/r/weread-skills
```

### 2. 配置微信读书 API Key

在官方页面登录微信读书后获取 API Key，然后配置环境变量。

Windows 示例：

```powershell
[Environment]::SetEnvironmentVariable('WEREAD_API_KEY', 'wrk-你的apikey', 'User')
```

配置完成后，重新打开 Codex 会话或终端，让新环境变量生效。

### 3. 安装 Read Persona

将 `read-persona` 文件夹放入 Codex Skills 目录：

```text
~/.codex/skills/read-persona
```

Windows 常见路径：

```text
C:\Users\<你的用户名>\.codex\skills\read-persona
```

目录结构示例：

```text
read-persona/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
└─ references/
   └─ report-template.md
```

安装完成后，在 Codex 中使用类似提示词即可触发：

```text
分析我的阅读人格
```

或显式调用：

```text
Use $read-persona to analyze my WeRead reading persona and generate a polished HTML report.
```

## 配置项

当前 Skill 主要依赖环境变量：

| 名称 | 必需 | 说明 |
| --- | --- | --- |
| `WEREAD_API_KEY` | 是 | 微信读书 Agent API Key |

如果没有配置，或 Key 无效，Skill 将无法读取个人书架、阅读统计和笔记。

## 隐私与安全

Read Persona 会读取你的个人微信读书数据，包括：

- 书架内容
- 阅读统计
- 笔记数量
- 个人划线与想法，按需读取
- 个性化推荐结果

建议：

- 不要将 `WEREAD_API_KEY` 提交到 Git 仓库
- 不要在公开报告中保留过于私密的书籍或笔记
- 开源本 Skill 时只发布 Skill 文件，不发布个人生成的 HTML 报告
- 如果要公开示例报告，请使用脱敏或模拟数据
- 如果曾把 API Key 发到公开渠道，建议重新生成或更换

## 设计理念

Read Persona 的核心目标不是「统计你读了多少」，而是「解释你如何阅读」。

它关注：

- 你的阅读动力是什么
- 你的知识结构长成什么样
- 你在什么时间最容易读进去
- 你如何通过笔记处理信息
- 哪些主题反复吸引你
- 你的下一本书应该服务于什么问题

换句话说，它希望把微信读书从一个阅读记录工具，变成一面能照见个人心智结构的镜子。

## 已知限制

- 依赖 `weread-skills` 和有效的 `WEREAD_API_KEY`
- 微信读书接口返回字段可能随版本变化
- 推荐结果可能混入与用户长期偏好不完全一致的内容，需要报告生成时做人工式筛选
- 当前默认输出为静态 HTML，不包含交互式筛选
- 单本书划线原文涉及版权，应避免在公开报告中大段复制

## 开发与校验

创建或修改 Skill 后，可使用 Skill Creator 的校验脚本：

```powershell
$env:PYTHONUTF8='1'
py C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<你的用户名>\.codex\skills\read-persona
```

期望输出：

```text
Skill is valid!
```

## 许可证

你可以按自己的开源计划选择许可证。

推荐：

- MIT License：适合宽松开源与二次创作
- Apache-2.0：适合希望保留更明确专利授权条款的项目

请在正式发布前补充 `LICENSE` 文件。

## 致谢

本 Skill 建立在微信读书数据能力与 `weread-skills` 的接口说明之上。`read-persona` 只负责将这些数据进一步组织为阅读人格分析与 HTML 报告。

微信读书 Skill 官方配置页：

```text
https://weread.qq.com/r/weread-skills
```
