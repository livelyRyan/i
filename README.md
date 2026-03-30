# Resume Workflow

This repo keeps `resume.md` as the single source of truth for the resume.

## Source of truth

- `resume.md`: primary resume content
- `index.html`: **不纳入 Git**。由 `scripts/render_resume.py` 生成；推送 `master` 后由 GitHub Actions 构建并发布（见 `.github/workflows/render-resume-pages.yml`）。
- `代表作/`: 项目展示 HTML 与静态资源（仅此一份；发布站点中与首页同级，相对路径 `代表作/...`）

## 如何更新网站（GitHub Pages）

站点通过 **GitHub Actions** 发布（勿再使用 “Deploy from a branch”）。请在仓库 **Settings → Pages → Build and deployment** 将 **Source** 设为 **GitHub Actions**。若仍指向 `master` 根目录，而在仓库中已删除 `index.html`，首页会 404，直到改为 Actions 并成功跑通工作流。

1. 编辑 **`resume.md`**（改文案、链接等）。
2. 若新增或修改 **`代表作/`** 下的页面或图片，直接改根目录 `代表作/` 并随仓库提交。
3. （可选）本地预览首页，生成到被忽略的 `index.html`：

   ```bash
   python3 scripts/render_resume.py --in resume.md --out index.html
   ```

4. 提交并推送到 **`master`**（无需 `git add index.html`）：

   ```bash
   git add resume.md 代表作/
   git commit -m "docs: AI update resume and portfolio"
   git push origin master
   ```

推送后，工作流会渲染简历、复制 `resume-profile.jpg` 与 **`代表作/`** 到发布产物并部署。

`docs/` 仅保留与站点无关的说明文档（例如 `md2html-resume-prompt.md`），不参与 Pages 发布根目录。
