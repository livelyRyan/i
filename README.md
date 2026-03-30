# Resume Workflow

This repo keeps `resume.md` as the single source of truth for the resume.

## Source of truth

- `resume.md`: primary resume content
- `index.html`: 由 `scripts/render_resume.py` 从 `resume.md` **生成**；提交到仓库后，在 Pages 使用 **Deploy from a branch**（`master` / `/ (root)`）时可直接访问。推送 `master` 时 **Actions** 也会构建 `_site` 并尝试通过 **GitHub Actions** 源部署（见 `.github/workflows/render-resume-pages.yml`）。
- `代表作/`: 项目展示 HTML 与静态资源（仅此一份；发布站点中与首页同级，相对路径 `代表作/...`）

## 如何更新网站（GitHub Pages）

打开 **Settings → Pages → Build and deployment**：

- **GitHub Actions**（推荐）：Source 选 **GitHub Actions**，保存后每次推 `master` 会跑「Render Resume Pages」：**build** 上传产物，**deploy** 发布。若长期 404，到 **Actions** 打开最近一次运行，确认 `deploy` 成功且无 Environment 审批阻塞。
- **Deploy from a branch**（备用）：Source 改为 **Deploy from a branch**，Branch **master**，Folder **`/ (root)`**。仓库根目录必须有已提交的 **`index.html`**（否则 `/i/` 会 404）。

两种源**不要混用**：选 Actions 时以运行产物为准；选 branch 时以仓库里 `index.html` 为准。可选在改完 `resume.md` 后本地执行渲染并一并提交 `index.html`，与线上 branch 源一致：

```bash
python3 scripts/render_resume.py --in resume.md --out index.html
git add resume.md index.html 代表作/
git commit -m "docs: AI update resume and portfolio"
git push origin master
```

推送后，Actions 工作流会重新渲染并部署（若已启用 Actions 源）。
