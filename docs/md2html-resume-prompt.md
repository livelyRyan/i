# Prompt：将 `resume.md` 同步为仓库根目录 `index.html`

把本文件作为 **系统/任务说明** 交给 AI，用于根据最新的 `resume.md` 更新或生成仓库根目录下的 `index.html`。**`resume.md` 是唯一事实来源**；HTML 仅负责版式与既有样式类名，不得保留源文件中已删除的内容。

---

## 1. 角色与目标

- **输入**：仓库根目录下的 `resume.md`。
- **输出**：仓库根目录 `index.html`（在**保留现有 `<head>` 内联样式与整体 DOM 结构**的前提下，替换正文区块中的文案与结构）。
- **原则**：这是一次 **全量对齐**，不是「在旧 HTML 上追加新段落」。若 `resume.md` 删掉了某段、某词、某列表项，HTML 中对应内容 **必须一并删除**，禁止沿用历史版本残留。

---

## 2. 核心规则：删除与增量等价重要

- **禁止陈旧内容**：例如 Experience 里若 `resume.md` 仅写「公司名」而不再写「城市/地点」，则 HTML 的 Experience 第一行 **不得** 再出现 `·` + 城市等；若删了一条经历，整条 `timeline-item` 应从 HTML 移除。
- **段落级一致**：各章节（Summary、Experience、Skills、Projects、Education、Certifications、Awards）的条目数量、顺序、措辞应与 `resume.md` 一致。
- **标点与分隔符**：以 `resume.md` 为准（全角 `｜`、半角 `|`、顿号等）；不要随意「优化」改写。

---

## 3. `resume.md` 结构解析约定

### 3.1 头部（无 `##`）

- 第 1 行：`# 姓名` → `<h1>`。
- 第 3 行：一行联系方式 → `.hero .meta`；其中 URL 需转为 `<a href="...">...</a>`。
- 第 5 行：意向岗位 → `.hero .roles`。

### 3.2 `## Summary`

- 使用 `<!-- LLM:BEGIN summary -->` … `<!-- LLM:END summary -->` 之间的列表（若存在）；否则用该节下普通列表。
- 每条 `<li>` 对应一行 bullet，文字与 Markdown 一致。

### 3.3 `## Experience`

每段经历通常形如：

```text
**职位标题**, 公司名 (起止时间)
- 要点
```

- **时间**：左侧 `.timeline-date`，格式与 MD 括号内一致（如 `2024-01 — 至今`）。
- **第一行**（`.exp-first-line`）：
  - `<span class="item-title">` 内为 **加粗部分**（去掉 `**`，保留原文中的 `｜` 或 `|`）。
  - `<span class="exp-org"><span class="prefix">公司名</span></span>`：**仅当 `resume.md` 在「公司名」后仍明确写出地点时**，才在 `prefix` 后追加 `<span class="exp-sep">·</span><span>地点</span>`；若 MD 无地点，**不要**添加 `exp-sep` 与地点（避免与旧版 HTML 不一致）。
- **要点**：每条 `- ` → `<ul><li>...</li></ul>`；若无子 bullet，不要生成空列表。

### 3.4 `## Skills`

- 解析 `<!-- LLM:BEGIN skills -->` … 之间内容（若存在）。
- 每一类 `- Label: a, b, c` → 一个 `.skill-block`：`h3.skill-subtitle` 为 `Label`，`span.tag` 为拆分的技能词（与现有页面一致：逗号、分号处可拆成多个 tag；`...` 保留为字面量如 `Golang, ...`）。

### 3.5 `## Projects`

每个项目：

- 标题行：`**名称** | 角色 | 时间 | [项目链接](相对路径)`  
  → `.project-headline` 内 `.item-title` + 若有链接则 `<a class="link-pill" href="相对路径">项目链接</a>`（`href` 与 MD 一致）。
- `- 目标：` → `<span class="prefix">目标</span>` + 正文；业绩向数字可包 `<span class="metric">...</span>`（规则见第 4 节）。
- `- 结果：` → 嵌套 `<ul>`，子项用 `.prefix` 标记「提效」「覆盖」等小标题（与现有 HTML 一致）。
- `- 关键词：` → `li.project-keywords` + `.tag-list` 内多个 `<span class="tag">...</span>`，**所有关键词样式统一为 `tag`，不要给首词单独加 `accent` 等变体**。

### 3.6 `## Education` / `## Certifications`

- Education：一段 `<p>`。
- Certifications：与 Summary 类似用 `<ul><li>`；尊重 `<!-- LLM:BEGIN certs -->` 范围。

### 3.7 `## Awards`

- 每条一行；`前缀：正文` 形式 → `<span class="prefix awards-prefix">前缀</span>` + 正文。
- Markdown 中的 `<`（如「全司均值 < 50%」）在 HTML 中必须写作 **`&lt;`**，避免被解析为标签。

---

## 4. 数字高亮 `.metric`（与简历可读性）

仅对 **业绩/结果向** 数字使用 `<span class="metric">...</span>`，例如：提效比例、金额/PD、覆盖率、排名对比等。

**通常不加 `metric` 的情况**（与 `resume.md` 纯文本一致即可）：

- 「0 到 1」类表述中的 **0 / 1**；
- **年份/年数** 作时间尺度时（如「8 年经验」「4 年 3 次」中的「4 年」若希望与 Summary 一致可不加）；
- **步骤数**（如「7 步降到 1 步」中的「1 步」）等非业绩口径数字。

具体以产品侧约定为准；**宁可少标 metric，不要把整段年份刷亮。**

---

## 5. 页面布局（须保持）

- 外层 `<main class="page">`。
- **第一行区块**：`<header class="hero">`。
- **`.columns`** 网格：
  - **`.column-stack`**（左列）：**仅**包含 `Summary` 卡片 + `Education`（含其下的 `Certifications` 小节），避免与右侧 Skills 等高时在左侧留下大块空白。
  - 与 `column-stack` **同级**：`Skills` 卡片（右列第一行与左列对齐）。
  - **`Experience`、`Projects`、`Awards`**：使用 **`section.card.section.span-2`** 占满两列。

---

## 6. 完成后自检清单

- [ ] 任意段落对比 `resume.md`：无多字、无少字、无旧版残留（尤其 Experience 地点、已删项目/奖项）。
- [ ] Awards 与文中比较符号已转义为 `&lt;`。
- [ ] 项目链接 `href` 与 MD 相对路径一致。
- [ ] `span-2`、`.column-stack` 结构未被破坏；样式类名与现有根目录 `index.html` 保持一致。

---

## 7. 建议交给 AI 的一句话任务描述

> 请阅读仓库根目录 `resume.md`，按 `docs/md2html-resume-prompt.md` 的规则，将内容 **完整同步** 到仓库根目录 `index.html`：以 MD 为唯一事实来源，删除 HTML 中所有 MD 已不存在的文字与节点；保留现有 CSS 与布局结构。

---

## 8. 默认不要改动的部分（除非用户明确要求）

- **`<head>`**：`<meta>`、`<title>`、字体 `<link>`、整段 **内联 `<style>`** 一般保持不变；本次任务只更新 `<body>` 内 `<main class="page">` 下的结构与正文。
- **不要**根据「常识」补全 `resume.md` 未写的内容（例如擅自加城市、补一条经历或项目）。
- **结构样板**：具体 DOM 层级、class 命名以当前仓库根目录 `index.html` 为参考实现；新章节仍须遵守第 5 节布局约定。
