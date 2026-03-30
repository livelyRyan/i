#!/usr/bin/env bash
# Sync 代表作/ into docs/代表作/ so GitHub Pages (publishing from /docs) can serve project links.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/代表作"
DST="${ROOT}/docs/代表作"
if [[ ! -d "$SRC" ]]; then
  echo "Missing source: $SRC" >&2
  exit 1
fi
mkdir -p "$DST"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SRC/" "$DST/"
else
  rm -rf "$DST"
  mkdir -p "$DST"
  cp -a "$SRC/." "$DST/"
fi
echo "Synced $SRC -> $DST"
