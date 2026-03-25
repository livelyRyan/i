# Resume Workflow

This repo keeps `resume.md` as the single source of truth and renders multiple deliverable resumes from it.

## Prerequisites

- `python3` (3.10+)

## Render variants

Outputs are written to `dist/` (gitignored).

- Agent resume:
  - `python3 scripts/render_resume.py --in resume.md --variant agent --out dist/resume.agent.md`
- Platform resume:
  - `python3 scripts/render_resume.py --in resume.md --variant platform --out dist/resume.platform.md`
- Full/all (for website or master view):
  - `python3 scripts/render_resume.py --in resume.md --variant all --out dist/resume.all.md`

## Variant markers (in `resume.md`)

Wrap variant-only content with comment blocks:

- Agent only:
  - `<!-- VARIANT: agent -->`
  - `...`
  - `<!-- /VARIANT -->`
- Platform only:
  - `<!-- VARIANT: platform -->`
  - `...`
  - `<!-- /VARIANT -->`
- Shared by multiple variants:
  - `<!-- VARIANT: agent, platform -->`

Unmarked lines are treated as common content and appear in all deliverable resumes.

