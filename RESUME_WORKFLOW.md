# 简历与个人网站（Markdown 真源）工作流规范

> 目的：把“投递简历”和“个人网站”都建立在同一套 Markdown 内容体系上，让 LLM 修改稳定、可控、可复用，并能一键产出 PDF / Word / 网站页面。

## 0. 核心原则

1. **`resume.md` 是唯一真源（Single Source of Truth）**：所有信息只在这里维护一次；不再区分投递版。
2. **投递版必须克制**：优先保证 ATS/筛选友好（单栏、纯文本、可复制）。
3. **网站允许更丰富，但不复制简历段落**：网站增加的内容拆到独立文章/项目页；不要在网站里再写一份“经历要点”，避免分叉不同步。
4. **LLM 修改必须有边界**：通过固定结构 + 标记区块，要求 LLM 只改允许编辑的范围。

## 1. 仓库结构（约定）

后续实现时按下面组织（本文件是规范，不强制立刻建齐所有目录）：

- `resume.md`：投递简历真源（建议 1 页为默认目标）
- `resume.en.md`：英文版（如果需要双语）
- `content/`：网站扩展内容（不与 `resume.md` 重复）
  - `content/projects/*.md`：每个项目一篇（可长）
  - `content/writing/*.md`：文章/复盘/随笔
  - `content/talks/*.md`：分享/演讲
  - `content/about.md`：更完整自我介绍（可引用简历摘要，但不要重写经历要点）
- `site/`：静态网站工程（推荐 Astro）
- `scripts/`：构建脚本（md → pdf/docx，md → site 数据）
- `dist/`：构建产物（gitignore）

## 2. `resume.md` 必须满足的格式约束（给 LLM 的硬规则）

### 2.1 允许的 Markdown 语法
- 仅使用：标题（`#`/`##`）、段落、`-` 无序列表、行内链接。
- **禁止**：表格、HTML、图片、双栏布局技巧（ATS 与格式转换不稳定）。

### 2.2 固定章节顺序（不得改动标题层级与顺序）
1. `# <Name>`（第一行必须是姓名）
2. `## Summary`
3. `## Skills`
4. `## Experience`
5. `## Projects`（可选）
6. `## Education`（可选）
7. `## Certifications` / `## Awards` / `## Publications`（可选，按需）

### 2.3 统一日期格式
- 统一使用：`YYYY-MM — YYYY-MM`（仍在职用 `YYYY-MM — Present`）
- 所有经历、项目、教育都必须一致。

### 2.4 Experience 条目模板（强约束）
每段经历使用以下模板（LLM 不得增删字段行）：

- 第一行（职位与时间）：
  - `**<Title>**, <Company> — <City/Remote>  (<YYYY-MM — YYYY-MM/Present>)`
- 后面 3–5 条要点（每条一行，尽量不换行）：
  - `- <Action verb> <what> ...; <impact metric>; <how/tech>`

要点写作要求：
- 每条聚焦一个结果；优先数字化（性能、成本、转化、效率、规模、稳定性）。
- 避免“负责/参与/协助”等弱动词开头；优先“Designed / Built / Led / Reduced / Improved …”

### 2.5 Skills 写法（结构固定）
按分组列出，分组名使用英文且保持稳定，便于英文版复用；允许在不破坏整体结构的前提下扩展分组（例如补充 AI/LLM 与 AI Coding）：

- `- Languages: ...`
- `- AI/LLM: ...`（如需要，推荐包含 LLM/Agent/Workflow/Prompt/ReAct/MCP 等）
- `- Frameworks: ...`
- `- Infrastructure: ...`
- `- AI Coding: ...`（如需要，推荐包含 Claude Code/Codex/Cursor 等）
- `- Data/ML: ...`（如需要）

### 2.6 单一投递简历
只维护一份 `resume.md`，不区分 Agent / Platform 版本；需要突出岗位时在同一份简历中合并表达即可。

## 3. LLM 修改协议（每次改简历都要遵守）

为了让修改可控，`resume.md` 使用“可编辑区块标记”。LLM 必须：

1. **只修改 `<!-- LLM:BEGIN ... -->` 与 `<!-- LLM:END ... -->` 之间的内容**。
2. 不得改动任何标题行、条目顺序、公司/时间等“事实字段”，除非用户明确提供新事实。
3. 不得引入表格/HTML/图片/多栏。
4. 输出必须是 **整文件**（便于直接替换），或输出 **补丁**（更推荐）。

推荐的区块粒度：
- `Summary` 整块
- 每段 `Experience` 的 bullets 作为一块
- `Projects` 中每个项目的 bullets 作为一块

## 4. 网站信息架构（“更丰富但不重复”）

网站的目标不是“再写一份简历”，而是承接筛选后的深挖：

- 简历页：展示 `resume.md`（或其渲染结果），保持与投递版一致。
- 项目页：每个项目单独展开（背景、目标、约束、方案、取舍、结果、复盘）。
- 文章页：展示思考与方法论（可提升可信度与可聊话题）。

### 4.1 去重规则（强制）
- 网站的 Experience 区域不再维护第二份 bullets；**直接渲染 `resume.md`** 或引用其片段。
- 网站新增的细节必须进入 `content/` 的独立页面，并在简历的项目要点里只放一句“结果+链接”。

## 5. 构建产物（约定）

后续会维护以下产物（产物不手改，只由构建生成）：

- `dist/resume.pdf`
- `dist/resume.docx`
- `dist/site/`（静态站点输出）

## 6. 后续实现（推荐技术选型）

由于需要“网站直接渲染 `resume.md` + 扩展内容”，推荐：

- 静态站点：**Astro**
  - 优点：原生支持 Markdown 内容与布局组合；对 LLM 维护友好；生成纯静态产物便于部署。
- 导出工具：**Pandoc**
  - `resume.md` → `resume.pdf` / `resume.docx`
  - 版式用单栏、简洁 CSS（避免多栏/表格）

> 说明：本规范只定义设计与约束。落地时会补齐 `resume.md` 模板、Astro 工程与一键脚本。
