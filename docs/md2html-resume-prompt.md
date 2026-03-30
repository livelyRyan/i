# Prompt：`resume.md` → `docs/index.html` 同步规范

将本文件作为 **系统/用户提示** 交给 AI，用于把仓库根目录的 `resume.md` 转换为（或更新）`docs/index.html`。目标是：**版式沿用现有 HTML 模板与样式，正文以 `resume.md` 为唯一事实来源**。

---

## 1. 角色与输入输出

- **输入**：`/resume.md`（主源）
- **输出**：`/docs/index.html`（在**保留既有 `<head>` 内联样式与整体 DOM 结构**的前提下，替换 `<main class="page">` 内的可编辑内容）
- **禁止**：在 HTML 中保留 `resume.md` 已删除的句子、条目或字段；禁止「为了好看」补回源文件中不存在的公司地点、额外 bullet、旧版项目等。

---

## 2. 核心原则：增删一致

- **仅追加**：若 `resume.md` 新增段落或列表项，在 HTML 对应区块按相同结构追加。
- **同步删除**：若用户在 `resume.md` 中删除了某段文字、某条经历、某个项目或某字段（例如经历行里不再写城市），则 **HTML 中对应节点必须删除**，不得保留历史残留。
- **对照方式**：生成前按章节（Summary / Experience / Skills / Projects / Education / Certifications / Awards）逐项对比；任何只存在于 HTML、不存在于 `resume.md` 的可见正文，一律移除或改到与 md 一致。

**示例（Experience）**：若 md 中经历标题为「职位**,** 公司名 (日期)」且**没有**「城市 / 地点」，则 HTML 的 `exp-org` 内 **不得** 再输出 `exp-sep` + 城市；若 md 中显式写了「北京」等，再按下文规则映射。

---

## 3. 页面骨架（须保持）

- 外层：`<main class="page">` → `<header class="hero">`（姓名、联系方式一行、意向岗位一行）
- 双列网格：`<div class="columns">`
  - **第一列**：`<div class="column-stack">` 内依次为 **Summary** → **Education**（Education 卡片内包含 **Certifications** 子块，与当前 `index.html` 一致）
  - **第二列（与 column-stack 同级）**：**Skills** 单独一节（避免把 Skills 塞进 column-stack 导致左侧大块空白）
  - **整宽**：`Experience`、`Projects`、`Awards` 使用 `section.card.section.span-2`

---

## 4. 各章节映射规则

### 4.1 Hero

- `# 马阳阳` → `<h1>`
- 元信息行、意向岗位行：与 md 纯文本一致；邮箱/个人站点保留 `<a href="...">`。

### 4.2 Summary

- 使用 `<!-- LLM:BEGIN summary -->` … `<!-- LLM:END summary -->` 之间的列表（若用户删掉注释标记，则以 `## Summary` 下第一个列表为准）。
- 列表项与 md 逐字一致；**不要**为 md 中未加粗的数字擅自套 `<span class="metric">`（业绩高亮规则见 §6）。

### 4.3 Experience

- 每条经历对应一个 `.timeline-item`：
  - `.timeline-date`：括号内日期区间，与 md 一致。
  - `.timeline-body` 内第一行：`.exp-first-line`
    - `.item-title`：加粗职位标题（保留 md 中的 `｜` / `|` 等标点）
    - `.exp-org`：**仅当 `resume.md` 在同一条经历中显式包含「地点」时**，再使用  
      `<span class="prefix">公司名</span><span class="exp-sep">·</span><span>地点</span>`  
      若 md 只有「公司名」无地点，则只用  
      `<span class="exp-org"><span class="prefix">公司名</span></span>`  
      **不要**从旧版 HTML 或常识补「北京」等城市。
  - 其下 `<ul>`：与 md 中该经历下的 bullet 一一对应；无 bullet 的经历（仅一行标题）则不要生成 `<ul>`。

### 4.4 Skills

- 解析 `<!-- LLM:BEGIN skills -->` … `<!-- LLM:END skills -->` 内各行（`Languages:`、`LLM:` 等）。
- 映射为多个 `.skill-block`：`h3.skill-subtitle` + `.tag-list.skill-tags` 内若干 `span.tag`。
- 逗号/分号分隔的技能拆成多个 tag；`...` 等与 md 一致保留。

### 4.5 Projects

- 每个项目：`.project-card`
  - `.project-headline`：标题行与 md 一致；若存在 `[项目链接](路径)`，生成 `<a class="link-pill" href="路径">项目链接</a>`（路径与 md 相对路径一致）。
  - 结构：`目标` / `结果`（含嵌套列表）/ `关键词` → 使用 `<span class="prefix">` 标记标签式前缀；`关键词` 一行拆为多个 `span.tag`（样式统一为 `class="tag"`，不要给首词单独 `accent`）。
- md 中删除整个项目 → HTML 删除整个 `.project-card`。

### 4.6 Education & Certifications

- Education：单段 `<p>` 与 md 一致。
- Certifications：列表与 md `## Certifications` 下内容一致。

### 4.7 Awards

- 每条 `<li>`：`<span class="prefix awards-prefix">标签</span>` + 正文；标签与正文分隔方式与当前 `index.html` 一致。
- md 使用 `<` 处（如「全司均值 < 50%」）在 HTML 中写成 `&lt;`。

---

## 5. `metric` 高亮（可选、保守）

- **可**用 `<span class="metric">...</span>` 强调业绩向数字（比例、PD、覆盖率、排名等）。
- **不要**高亮：纯年份表述、「0 到 1」中的 0/1、步骤数（如「1 步」）、非业绩口径数字；与既有 `index.html` 中已约定的风格保持一致。

---

## 6. 交付前自检清单

- [ ] `resume.md` 里不存在的段落，HTML 里没有。
- [ ] Experience 地点：md 无则 HTML 无 `exp-sep` 与城市。
- [ ] 项目数量、标题、链接与 md 一致。
- [ ] Awards / Summary 等区块与 md 列表条数一致。
- [ ] 合法 HTML：`<`、`>`、`&` 在需要时已转义。

---

## 7. 参考文件

- 规范与样式以当前仓库 **`docs/index.html`** 为准；改内容时尽量**小范围替换**正文节点，避免重写整文件导致样式回归。
