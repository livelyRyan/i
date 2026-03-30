# Resume Workflow

This repo keeps `resume.md` as the single source of truth for the resume.

## Source of truth

- `resume.md`: primary resume content
- `index.html`: GitHub Pages 首页，由 `scripts/render_resume.py` 从 `resume.md` 生成（勿手改 HTML）
- `代表作/`: 项目展示 HTML 与静态资源（仅此一份；与首页同级，相对路径 `代表作/...`）

## 如何更新网站（GitHub Pages）

站点从仓库 **根目录** 发布（请在仓库 Settings → Pages 中选择 **Branch: `master` / Folder: `/ (root)`**）。

1. 编辑 **`resume.md`**（改文案、链接等）。
2. 若新增或修改 **`代表作/`** 下的页面或图片，直接改根目录 `代表作/` 并随仓库提交即可。
3. 本地生成首页（与 CI 行为一致）：

   ```bash
   python3 scripts/render_resume.py --in resume.md --out index.html
   touch .nojekyll
   ```

4. 提交并推送到 **`master`**：

   ```bash
   git add resume.md index.html .nojekyll 代表作/
   git commit -m "docs: AI update resume and portfolio"
   git push origin master
   ```

推送后，工作流会再次渲染 `index.html`；若产生额外提交属正常。仅改 `resume.md` 也可只 push，由 CI 生成首页；为减少往返，建议在本地执行第 3 步再 push。

`docs/` 仅保留与站点无关的说明文档（例如 `md2html-resume-prompt.md`），不参与 Pages 发布根目录。
