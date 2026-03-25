#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


START_RE = re.compile(r"^\s*<!--\s*VARIANT\s*:\s*(.*?)\s*-->\s*$", re.IGNORECASE)
END_RE = re.compile(r"^\s*<!--\s*/VARIANT\s*-->\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class VariantBlock:
    variants: set[str]


def parse_variant_list(raw: str) -> set[str]:
    parts = [p.strip().lower() for p in re.split(r"[,\s]+", raw) if p.strip()]
    return set(parts)


def render_lines(lines: list[str], variant: str) -> list[str]:
    if variant != "all":
        variant = variant.strip().lower()

    active: VariantBlock | None = None
    out: list[str] = []

    for idx, line in enumerate(lines, start=1):
        start_match = START_RE.match(line)
        if start_match:
            if active is not None:
                raise ValueError(f"Nested VARIANT blocks are not supported (line {idx}).")
            active = VariantBlock(variants=parse_variant_list(start_match.group(1)))
            if not active.variants:
                raise ValueError(f"Empty VARIANT list (line {idx}).")
            continue

        if END_RE.match(line):
            if active is None:
                raise ValueError(f"Unmatched /VARIANT (line {idx}).")
            active = None
            continue

        if variant == "all":
            out.append(line)
            continue

        if active is None or variant in active.variants:
            out.append(line)

    if active is not None:
        raise ValueError("Unclosed VARIANT block at end of file.")

    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render a resume variant from a single Markdown source.\n\n"
            "Use blocks like:\n"
            "  <!-- VARIANT: agent -->\n"
            "  - This line only appears in agent resume\n"
            "  <!-- /VARIANT -->\n"
            "Or multi-target:\n"
            "  <!-- VARIANT: agent, platform -->"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--in", dest="inp", required=True, help="Input Markdown file (source of truth).")
    parser.add_argument("--out", dest="out", required=False, help="Output Markdown file.")
    parser.add_argument(
        "--variant",
        required=True,
        choices=["agent", "platform", "all"],
        help="Which variant to render. Use 'all' for website/full version.",
    )
    parser.add_argument("--check", action="store_true", help="Validate variant markers only; do not write output.")
    args = parser.parse_args(argv)

    inp_path = Path(args.inp)
    raw = inp_path.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)

    try:
        rendered = render_lines(lines, args.variant)
    except ValueError as e:
        print(f"[render_resume] {e}", file=sys.stderr)
        return 2

    if args.check:
        return 0

    if not args.out:
        print("[render_resume] --out is required unless --check is used.", file=sys.stderr)
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(rendered), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

