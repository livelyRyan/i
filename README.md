# Resume Workflow

This repo keeps `resume.md` as the single source of truth for the resume.

## Source of truth

- `resume.md`: primary resume content
- `docs/index.html`: GitHub Pages 展示页，由 `scripts/render_resume.py` 从 `resume.md` 生成（勿手改 HTML）
- `代表作/`: 项目展示 HTML 与静态资源；同步副本在 `docs/代表作/`（供 Pages 访问 `代表作/...` 链接）

## 如何更新网站（GitHub Pages）

站点从仓库 **`/docs` 目录** 发布，因此首页与项目页都必须出现在 `docs/` 下。

1. 编辑 **`resume.md`**（改文案、链接等）。
2. 若新增或修改了 **`代表作/`** 下的页面或图片，保持根目录 `代表作/` 为真源。
3. 本地生成并同步（与 CI 行为一致）：

   ```bash
   python3 scripts/render_resume.py --in resume.md --out docs/index.html
   touch docs/.nojekyll
   bash scripts/sync_portfolio_to_docs.sh
   ```

4. 提交并推送到 **`master`**：

   ```bash
   git add resume.md docs/
   git commit -m "docs: AI update resume and portfolio"
   git push origin master
   ```

推送后，工作流会再次渲染并同步 `docs/`，若产生额外提交属正常。仅改 `resume.md` 也可只 push，由 CI 生成 `docs/index.html` 并同步 `代表作`；为减少往返，建议在本地执行第 3 步再 push。
