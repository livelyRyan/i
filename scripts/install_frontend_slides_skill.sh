#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${SOURCE_DIR:-$HOME/.openclaw/workspace/skills/frontend-slides}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source skill not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$CODEX_SKILLS_DIR/frontend-slides" "$CLAUDE_SKILLS_DIR/frontend-slides"

rsync -a --delete "$SOURCE_DIR/" "$CODEX_SKILLS_DIR/frontend-slides/"
rsync -a --delete "$SOURCE_DIR/" "$CLAUDE_SKILLS_DIR/frontend-slides/"

echo "Installed frontend-slides skill to:"
echo "  - $CODEX_SKILLS_DIR/frontend-slides"
echo "  - $CLAUDE_SKILLS_DIR/frontend-slides"
