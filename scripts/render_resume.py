#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render resume.md into docs/index.html for GitHub Pages (static HTML)."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import List, Optional, Tuple

# --- HTML shell: styles copied from docs/index.html (visual parity) ---

HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Resume</title>
  <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&f[]=jet-brains-mono@400,600&display=swap" />
  <style>
    :root {
      --bg-0: #070911;
      --bg-1: #0b1020;
      --glass: rgba(255, 255, 255, 0.06);
      --glass-2: rgba(255, 255, 255, 0.03);
      --line: rgba(255, 255, 255, 0.12);
      --text-0: rgba(255, 255, 255, 0.92);
      --text-1: rgba(255, 255, 255, 0.70);
      --accent: #3dffcf;
      --accent-2: #7c5cff;
      --accent-3: #ff4fd8;

      --font-body: "Satoshi", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
      --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;

      --page-pad: clamp(0.9rem, 2.4vw, 2.2rem);
      --card-pad: clamp(0.8rem, 1.9vw, 1.4rem);
      --gap: clamp(0.7rem, 1.6vw, 1.1rem);
      --radius: 16px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-body);
      background: radial-gradient(1100px 900px at 15% 10%, rgba(124, 92, 255, 0.18), transparent 60%),
                  radial-gradient(900px 700px at 80% 20%, rgba(61, 255, 207, 0.12), transparent 55%),
                  radial-gradient(900px 700px at 65% 88%, rgba(255, 79, 216, 0.10), transparent 55%),
                  linear-gradient(180deg, var(--bg-0), var(--bg-1));
      color: var(--text-0);
      min-height: 100vh;
    }

    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }

    .page {
      max-width: 1200px;
      margin: 0 auto;
      padding: var(--page-pad) var(--page-pad) 1.2rem;
      display: grid;
      gap: calc(var(--gap) * 0.9);
    }

    .hero {
      display: grid;
      gap: 0.45rem;
      background: linear-gradient(180deg, var(--glass), var(--glass-2));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: var(--card-pad);
      box-shadow: 0 30px 120px rgba(0, 0, 0, 0.45);
      position: relative;
      overflow: hidden;
    }

    .hero h1 {
      font-size: clamp(1.5rem, 3.2vw, 2.4rem);
      letter-spacing: 0.4px;
    }

    .hero .meta {
      color: var(--text-1);
      font-size: clamp(0.8rem, 1.25vw, 0.98rem);
    }

    .hero .roles {
      font-size: clamp(0.86rem, 1.4vw, 1.02rem);
      color: var(--text-0);
      font-weight: 500;
    }

    .hero::after {
      content: "";
      position: absolute;
      right: -90px;
      top: -90px;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(61, 255, 207, 0.35), transparent 65%);
      opacity: 0.5;
      pointer-events: none;
    }

    .columns {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--gap);
      align-items: start;
    }

    .card {
      background: linear-gradient(180deg, var(--glass), var(--glass-2));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: var(--card-pad);
      box-shadow: 0 28px 100px rgba(0, 0, 0, 0.38);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }

    h2 {
      font-size: clamp(1rem, 1.8vw, 1.3rem);
      margin-bottom: 0.5rem;
      color: var(--accent);
      letter-spacing: 0.3px;
    }

    .block-title {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .chip {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      padding: 0.16rem 0.5rem;
      border-radius: 999px;
      border: 1px solid rgba(61, 255, 207, 0.5);
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .section p {
      color: var(--text-1);
      font-size: clamp(0.82rem, 1.3vw, 0.96rem);
      line-height: 1.55;
    }

    ul {
      list-style: none;
      display: grid;
      gap: 0.35rem;
      color: var(--text-1);
      font-size: clamp(0.82rem, 1.3vw, 0.96rem);
      line-height: 1.55;
    }

    ul > li::before {
      content: "•";
      color: var(--accent-3);
      margin-right: 0.5rem;
    }

    ul ul {
      margin-left: 1.05rem;
      margin-top: 0.3rem;
      gap: 0.3rem;
    }

    ul ul > li::before {
      content: "◦";
      color: var(--accent-2);
    }

    .item-title {
      color: var(--text-0);
      font-weight: 600;
      font-size: clamp(0.9rem, 1.5vw, 1.02rem);
      margin-bottom: 0.35rem;
    }

    .metric {
      color: var(--accent);
      font-weight: 600;
      text-shadow: 0 0 18px rgba(61, 255, 207, 0.25);
    }

    .prefix {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-family: var(--font-mono);
      font-size: 0.7rem;
      padding: 0.08rem 0.45rem;
      border-radius: 999px;
      background: rgba(124, 92, 255, 0.12);
      border: 1px solid rgba(124, 92, 255, 0.4);
      color: var(--accent-2);
      letter-spacing: 0.5px;
    }

    .link-pill {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      padding: 0.18rem 0.55rem;
      border-radius: 999px;
      border: 1px solid rgba(61, 255, 207, 0.4);
      color: var(--accent);
    }

    .project-card + .project-card {
      margin-top: 0.7rem;
      padding-top: 0.7rem;
      border-top: 1px dashed rgba(255, 255, 255, 0.12);
    }

    .span-2 {
      grid-column: span 2;
    }

    .timeline {
      position: relative;
      margin-top: 0.4rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .timeline-item {
      display: grid;
      grid-template-columns: minmax(7.5rem, 9.5rem) 1fr;
      gap: 0.85rem 1.1rem;
      align-items: start;
      position: relative;
    }

    .timeline-date {
      position: relative;
      text-align: right;
      padding-right: 1rem;
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--accent);
      line-height: 1.4;
      letter-spacing: 0.02em;
    }

    .timeline-date::before {
      content: "";
      position: absolute;
      right: -5px;
      top: 0.4rem;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 14px rgba(61, 255, 207, 0.5);
      z-index: 1;
    }

    .timeline-date::after {
      content: "";
      position: absolute;
      right: 0;
      top: 0.85rem;
      bottom: -1.05rem;
      width: 2px;
      background: linear-gradient(180deg, rgba(61, 255, 207, 0.55), rgba(124, 92, 255, 0.3));
      border-radius: 999px;
    }

    .timeline-item:last-child .timeline-date::after {
      bottom: 0;
    }

    .timeline-body {
      min-width: 0;
    }

    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      align-items: center;
      color: var(--text-1);
      font-size: 0.82rem;
      margin-bottom: 0.35rem;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-top: 0.35rem;
    }

    .tag {
      font-family: var(--font-mono);
      font-size: 0.65rem;
      padding: 0.12rem 0.5rem;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.16);
      color: var(--text-0);
      background: rgba(255, 255, 255, 0.06);
    }

    .tag.accent { border-color: rgba(61, 255, 207, 0.45); color: var(--accent); }
    .tag.purple { border-color: rgba(124, 92, 255, 0.45); color: var(--accent-2); }
    .tag.pink { border-color: rgba(255, 79, 216, 0.45); color: var(--accent-3); }

    .project-keywords {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.35rem 0.5rem;
    }

    .project-keywords .tag-list {
      display: inline-flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0;
    }

    .awards-prefix {
      max-width: 100%;
      white-space: normal;
      text-align: left;
      line-height: 1.35;
      font-size: 0.65rem;
      letter-spacing: 0.2px;
    }

    @media (max-width: 980px) {
      .columns { grid-template-columns: 1fr; }
      .span-2 { grid-column: span 1; }
      .timeline-item {
        grid-template-columns: 1fr;
        gap: 0.45rem;
      }
      .timeline-date {
        text-align: left;
        padding-right: 0;
        padding-left: 1.15rem;
        border-left: 2px solid rgba(61, 255, 207, 0.35);
      }
      .timeline-date::before { left: -6px; right: auto; }
      .timeline-date::after { display: none; }
    }
  </style>
</head>
<body>
  <main class="page">
"""


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--[\s\S]*?-->", "", text)


def extract_sections(md: str) -> dict[str, str]:
    md = strip_html_comments(md)
    lines = md.splitlines()
    sections: dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in lines:
        m = re.match(r"^##\s+(.+)\s*$", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def parse_hero(md: str) -> Tuple[str, str, str]:
    lines = strip_html_comments(md).splitlines()
    name = ""
    meta = ""
    roles = ""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            name = line[2:].strip()
        elif name and not meta and line.strip() and not line.startswith("#"):
            meta = line.strip()
        elif meta and not roles and line.strip() and not line.startswith("#") and "意向" in line:
            roles = line.strip()
            break
    return name, meta, roles


def linkify_meta_line(line: str) -> str:
    """Escape and turn bare URLs into links."""
    parts: List[str] = []
    pos = 0
    for m in re.finditer(r"https?://[^\s·]+", line):
        parts.append(html.escape(line[pos : m.start()]))
        raw = m.group(0)
        url = raw.rstrip(".,;)")
        parts.append(f'<a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>')
        pos = m.end()
    parts.append(html.escape(line[pos:]))
    return "".join(parts)


def apply_metrics(s: str) -> str:
    """Wrap numeric highlights after escaping (conservative — avoid mid-word digits)."""
    protected: List[str] = []

    def shield(mm: re.Match[str]) -> str:
        protected.append(mm.group(0))
        return f"\x00{len(protected) - 1}\x00"

    # CET-4, LangChain4j, Base64-style tokens: do not metric-wrap inner digits.
    s = re.sub(r"CET-\d+|[A-Za-z]{2,}\d{1,4}[a-z]{0,12}\b", shield, s)

    pat = re.compile(
        r"Top\s*\d+%|"
        r"\d+(?:\.\d+)?%|"
        r"\d+(?:\.\d+)?W\+?|"  # 4.4W, 2500W+
        r"\b20[0-9]{2}\b|"
        r"(?<![A-Za-z./])\d+\+(?!\d)|"
        r"\d+\s*PD\b|"
        r"\d+\s*min\b|"
        r"\d+\s*步\b|"
        r"\d+\s*个\b|"
        r"\d+\s*年\b|"
        r"\d+\s*名\b|"
        r"\d+\s*次\b|"
        r"(?<![A-Za-z.])\d+(?:\.\d+)?(?=\s*W\b)"
    )
    out: List[str] = []
    last = 0
    for m in pat.finditer(s):
        st, ed = m.start(), m.end()
        if st > 0 and s[st - 1].isalpha() and ed < len(s) and s[ed].isalpha():
            continue
        out.append(s[last:st])
        out.append(f'<span class="metric">{m.group(0)}</span>')
        last = ed
    out.append(s[last:])
    text = "".join(out)
    for i, p in enumerate(protected):
        text = text.replace(f"\x00{i}\x00", p)
    return text


def rich_line(s: str) -> str:
    return apply_metrics(html.escape(s))


def bullet_list_lines(lines: List[str]) -> str:
    items = []
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("- "):
            items.append(f"<li>{rich_line(ln[2:].strip())}</li>")
    if not items:
        return ""
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def bullet_list_from_block(block: str) -> str:
    lines = [ln for ln in block.splitlines() if ln.strip().startswith("- ")]
    return bullet_list_lines([ln.strip() for ln in lines])


EXPERIENCE_RE = re.compile(
    r"^\*\*(.+?)\*\*,\s*(.+?)\s+—\s*(.+?)\s+\((.+)\)\s*$"
)


def parse_experience(block: str) -> str:
    """Experience entries are consecutive; jobs start with **...,** not separated by blank lines."""
    lines = [ln.strip() for ln in block.splitlines()]
    jobs: List[dict] = []
    current: Optional[dict] = None
    for line in lines:
        if not line:
            continue
        m = EXPERIENCE_RE.match(line)
        if m:
            title, company, city, dates = (x.strip() for x in m.groups())
            current = {
                "title": title,
                "company": company,
                "city": city,
                "dates": dates,
                "bullets": [],
            }
            jobs.append(current)
        elif line.startswith("- ") and current:
            current["bullets"].append(line[2:].strip())
    parts: List[str] = ['<div class="timeline">']
    for job in jobs:
        parts.append('<div class="timeline-item">')
        parts.append(f'<div class="timeline-date">{html.escape(job["dates"])}</div>')
        parts.append('<div class="timeline-body">')
        parts.append(f'<div class="item-title">{html.escape(job["title"])}</div>')
        parts.append(
            f'<div class="meta-row"><span class="prefix">{html.escape(job["company"])}</span>'
            f'<span>{html.escape(job["city"])}</span></div>'
        )
        if job["bullets"]:
            parts.append("<ul>")
            for b in job["bullets"]:
                parts.append(f"<li>{rich_line(b)}</li>")
            parts.append("</ul>")
        parts.append("</div></div>")
    parts.append("</div>")
    return "\n".join(parts)


def group_bullets(
    entries: List[Tuple[int, str]], min_level: Optional[int] = None
) -> List[Tuple[str, List]]:
    if not entries:
        return []
    if min_level is None:
        min_level = entries[0][0]
    i = 0
    n = len(entries)
    result: List[Tuple[str, List]] = []
    while i < n:
        lvl, txt = entries[i]
        if lvl != min_level:
            break
        j = i + 1
        while j < n and entries[j][0] > min_level:
            j += 1
        sub = entries[i + 1 : j]
        children = group_bullets(sub, min_level + 1) if sub else []
        result.append((txt, children))
        i = j
    return result


def collect_bullet_entries(lines: List[str]) -> List[Tuple[int, str]]:
    entries: List[Tuple[int, str]] = []
    for line in lines:
        if not line.strip():
            continue
        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if not m:
            continue
        spaces, rest = m.group(1), m.group(2)
        level = len(spaces.replace("\t", "  ")) // 2
        entries.append((level, rest.strip()))
    return entries


def render_bullet_tree(nodes: List[Tuple[str, List]], awards_prefix: bool = False) -> str:
    parts = ["<ul>"]
    for text, children in nodes:
        inner = format_project_line(text, awards_prefix=awards_prefix)
        li_cls = ' class="project-keywords"' if text.startswith("关键词：") else ""
        if children:
            parts.append(f"<li{li_cls}>{inner}{render_bullet_tree(children, awards_prefix)}</li>")
        else:
            parts.append(f"<li{li_cls}>{inner}</li>")
    parts.append("</ul>")
    return "".join(parts)


def format_project_line(text: str, awards_prefix: bool = False) -> str:
    if text.startswith("关键词："):
        body = text[len("关键词：") :].strip()
        tags = re.split(r"[、,，]", body)
        tags = [t.strip() for t in tags if t.strip()]
        spans = []
        for idx, t in enumerate(tags):
            cls = "tag accent" if idx == 0 else "tag"
            spans.append(f'<span class="{cls}">{html.escape(t)}</span>')
        return (
            '<span class="prefix">关键词</span><span class="tag-list">' + "".join(spans) + "</span>"
        )
    m = re.match(r"^([^：]{1,32})：(.*)$", text)
    if m and m.group(1) in (
        "目标",
        "结果",
        "提效",
        "覆盖",
        "稳定性",
        "创新",
        "先进性",
        "吞吐",
        "安全",
        "效果",
    ):
        label, body = m.group(1), m.group(2)
        return f'<span class="prefix">{html.escape(label)}</span> {rich_line(body)}'
    if m and awards_prefix:
        label, body = m.group(1), m.group(2)
        return f'<span class="prefix awards-prefix">{html.escape(label)}</span> {rich_line(body)}'
    if m:
        label, body = m.group(1), m.group(2)
        return f'<span class="prefix">{html.escape(label)}</span> {rich_line(body)}'
    return rich_line(text)


def parse_project_header(line: str) -> Tuple[str, Optional[str]]:
    """Return display title line and optional href."""
    href: Optional[str] = None
    for lm in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", line):
        href = lm.group(2).strip()
    display = line
    display = re.sub(r"\[([^\]]*)\]\([^)]+\)", "", display)
    display = re.sub(r"\*\*([^*]+)\*\*", r"\1", display)
    display = re.sub(r"\s+\|\s*$", "", display).strip()
    display = re.sub(r"^\s+|\s+$", "", display)
    return display, href


def split_projects(block: str) -> List[Tuple[str, List[str]]]:
    """Split into (header_line, body_lines)."""
    lines = block.splitlines()
    projects: List[Tuple[str, List[str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("**") and "|" in line:
            header = lines[i].rstrip()
            i += 1
            body: List[str] = []
            while i < len(lines):
                nxt = lines[i]
                stripped = nxt.strip()
                if stripped.startswith("## "):
                    break
                if stripped.startswith("**") and "|" in stripped and i > 0:
                    break
                body.append(nxt)
                i += 1
            projects.append((header, body))
        else:
            i += 1
    return projects


def render_projects(block: str) -> str:
    out: List[str] = []
    for header, body in split_projects(block):
        title, href = parse_project_header(header)
        out.append('<div class="project-card">')
        out.append(f'<div class="item-title">{html.escape(title)}</div>')
        if href:
            out.append(
                f'<a class="link-pill" href="{html.escape(href, quote=True)}">项目链接</a>'
            )
        entries = collect_bullet_entries(body)
        tree = group_bullets(entries)
        if tree:
            out.append(render_bullet_tree(tree))
        out.append("</div>")
    return "\n".join(out)


def render_awards(block: str) -> str:
    lines = [ln for ln in block.splitlines() if ln.strip().startswith("- ")]
    body_lines = [ln[2:].strip() for ln in lines]
    # Awards are flat single-level with "label：body"
    parts = ["<ul>"]
    for ln in body_lines:
        m = re.match(r"^(.+?)：(.+)$", ln)
        if m:
            label, rest = m.group(1), m.group(2)
            parts.append(
                "<li>"
                f'<span class="prefix awards-prefix">{html.escape(label)}</span> '
                f"{rich_line(rest)}"
                "</li>"
            )
        else:
            parts.append(f"<li>{rich_line(ln)}</li>")
    parts.append("</ul>")
    return "\n".join(parts)


def build_html(md_text: str) -> str:
    sections = extract_sections(md_text)
    name, meta, roles = parse_hero(md_text)

    summary = sections.get("Summary", "")
    skills = sections.get("Skills", "")
    exp = sections.get("Experience", "")
    projects = sections.get("Projects", "")
    education = sections.get("Education", "")
    certs = sections.get("Certifications", "")
    awards = sections.get("Awards", "")

    sb: List[str] = []
    sb.append(HTML_HEAD)
    sb.append('    <header class="hero">')
    sb.append(f"      <h1>{html.escape(name)}</h1>")
    sb.append(f'      <div class="meta">{linkify_meta_line(meta)}</div>')
    sb.append(f'      <div class="roles">{html.escape(roles)}</div>')
    sb.append("    </header>")

    sb.append('    <div class="columns">')
    sb.append('      <section class="card section">')
    sb.append('        <div class="block-title"><h2>Summary</h2><span class="chip">overview</span></div>')
    sb.append(bullet_list_from_block(summary))
    sb.append("      </section>")

    sb.append('      <section class="card section">')
    sb.append('        <div class="block-title"><h2>Skills</h2><span class="chip">stack</span></div>')
    sb.append(bullet_list_from_block(skills))
    sb.append("      </section>")

    sb.append('      <section class="card section">')
    sb.append('        <div class="block-title"><h2>Education</h2><span class="chip">base</span></div>')
    sb.append(f"        <p>{rich_line(education.strip())}</p>")
    sb.append('        <div class="block-title" style="margin-top:0.7rem;">')
    sb.append('          <h2>Certifications</h2><span class="chip">certs</span>')
    sb.append("        </div>")
    sb.append(bullet_list_from_block(certs))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Experience</h2><span class="chip">impact</span></div>')
    sb.append(parse_experience(exp))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Projects</h2><span class="chip">selected</span></div>')
    sb.append(render_projects(projects))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Awards</h2><span class="chip">honors</span></div>')
    sb.append(render_awards(awards))
    sb.append("      </section>")

    sb.append("    </div>")
    sb.append("  </main>")
    sb.append("</body>")
    sb.append("</html>")
    return "\n".join(sb)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render resume.md to static docs/index.html")
    ap.add_argument("--in", dest="in_path", default="resume.md", help="Input Markdown path")
    ap.add_argument("--out", dest="out_path", default="docs/index.html", help="Output HTML path")
    ap.add_argument(
        "--variant",
        default="all",
        help="Ignored; kept for compatibility with existing CI invocations",
    )
    args = ap.parse_args()
    src = Path(args.in_path).read_text(encoding="utf-8")
    out = build_html(src)
    outp = Path(args.out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(out, encoding="utf-8")
    print(f"Wrote {outp}")


if __name__ == "__main__":
    main()

