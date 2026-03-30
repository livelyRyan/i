#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render resume.md into static HTML for GitHub Pages (local path or CI `_site/`)."""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_PHOTO_RELPATH = "resume-profile.jpg"


def _embedded_styles() -> str:
    p = _SCRIPT_DIR / "resume_embedded.css"
    if not p.is_file():
        raise FileNotFoundError(
            f"Missing {p}; copy CSS from repo-root index.html into this file."
        )
    return p.read_text(encoding="utf-8").rstrip() + "\n"


def html_head_open() -> str:
    css = _embedded_styles()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Resume</title>
  <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&f[]=jet-brains-mono@400,600&display=swap" />
  <style>
{css}
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


@dataclass
class Profile:
    name: str
    age: str
    location: str
    phone: str
    email: str
    website_url: str
    website_display: str
    intent_roles: List[str]
    intent_city: str


def parse_profile(md: str) -> Profile:
    lines = strip_html_comments(md).splitlines()
    name = ""
    meta_line = ""
    intent_roles: List[str] = []
    intent_city = ""
    for line in lines:
        if line.startswith("## "):
            break
        if line.startswith("# "):
            name = line[2:].strip()
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith("意向岗位"):
            parts = re.split(r"[：:]", s, maxsplit=1)
            if len(parts) > 1:
                intent_roles = [
                    x.strip()
                    for x in re.split(r"[；;]", parts[1])
                    if x.strip()
                ]
        elif s.startswith("意向城市"):
            parts = re.split(r"[：:]", s, maxsplit=1)
            if len(parts) > 1:
                intent_city = parts[1].strip()
        elif not meta_line and not s.startswith("意向"):
            meta_line = s

    parts = [p.strip() for p in meta_line.split("|")]
    age = parts[0] if len(parts) > 0 else ""
    loc_raw = parts[1] if len(parts) > 1 else ""
    phone = parts[2] if len(parts) > 2 else ""
    email = parts[3] if len(parts) > 3 else ""
    site_part = parts[4] if len(parts) > 4 else ""

    website_url = ""
    website_display = ""
    m = re.search(r"\[([^\]]*)\]\(([^)]+)\)", site_part)
    if m:
        website_url = m.group(2).strip()
    else:
        m2 = re.search(r"(https?://[^\s|]+)", site_part)
        if m2:
            website_url = m2.group(1).rstrip(").,]")
    if website_url:
        tail = website_url.rstrip("/").split("//", 1)[-1]
        website_display = tail + "/"
    else:
        website_display = ""

    location = loc_raw

    return Profile(
        name=name,
        age=age,
        location=location,
        phone=phone,
        email=email,
        website_url=website_url,
        website_display=website_display or website_url,
        intent_roles=intent_roles,
        intent_city=intent_city,
    )


def tel_href(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        return "+86" + digits
    if phone.strip().startswith("+"):
        return phone.strip()
    return ("+86" + digits) if digits else phone.strip()


def render_profile_hero(p: Profile, photo_rel: str = DEFAULT_PHOTO_RELPATH) -> str:
    tel = tel_href(p.phone)
    esc = html.escape
    site_link = ""
    if p.website_url:
        site_link = (
            f'<a href="{esc(p.website_url, quote=True)}" rel="noopener noreferrer">'
            f"{esc(p.website_display)}</a>"
        )
    roles_pills = "\n                  ".join(
        f'<span class="intent-pill intent-pill-accent">{esc(t)}</span>'
        for t in p.intent_roles
    )
    lines = [
        '    <header class="hero">',
        '      <div class="hero-content">',
        '        <div class="hero-main">',
        '          <div class="block-title">',
        '            <h2>Profile</h2>',
        "          </div>",
        '          <div class="hero-intro">',
        f"            <h1>{esc(p.name)}</h1>",
        "          </div>",
        '          <ul class="hero-facts" aria-label="联系方式与基本信息">',
        '            <li class="hero-fact">',
        '              <span class="hero-fact-label">年龄</span>',
        f'              <span class="hero-fact-value">{esc(p.age)}</span>',
        "            </li>",
        '            <li class="hero-fact">',
        '              <span class="hero-fact-label">现居</span>',
        f'              <span class="hero-fact-value">{esc(p.location)}</span>',
        "            </li>",
        '            <li class="hero-fact">',
        '              <span class="hero-fact-label">电话</span>',
        f'              <span class="hero-fact-value"><a href="{esc("tel:" + tel, quote=True)}">'
        f"{esc(p.phone)}</a></span>",
        "            </li>",
        '            <li class="hero-fact">',
        '              <span class="hero-fact-label">邮箱</span>',
        f'              <span class="hero-fact-value"><a href="mailto:{esc(p.email)}">'
        f"{esc(p.email)}</a></span>",
        "            </li>",
    ]
    if p.website_url:
        lines += [
            '            <li class="hero-fact">',
            '              <span class="hero-fact-label">网站</span>',
            f'              <span class="hero-fact-value">{site_link}</span>',
            "            </li>",
        ]
    lines += [
        "          </ul>",
        '          <ul class="hero-facts" aria-label="求职意向">',
        '            <li class="hero-fact hero-fact-wide">',
        '              <span class="hero-fact-label">意向岗位</span>',
        '              <span class="hero-fact-value hero-fact-value--pills">',
        '                <span class="hero-intent-pills">',
        f"                  {roles_pills}",
        "                </span>",
        "              </span>",
        "            </li>",
    ]
    if p.intent_city:
        lines += [
            '            <li class="hero-fact hero-fact-wide">',
            '              <span class="hero-fact-label">意向城市</span>',
            '              <span class="hero-fact-value hero-fact-value--pills">',
            '                <span class="hero-intent-pills">',
            f'                  <span class="intent-pill intent-pill-accent">'
            f"{esc(p.intent_city)}</span>",
            "                </span>",
            "              </span>",
            "            </li>",
        ]
    lines += [
        "          </ul>",
        "        </div>",
        '        <figure class="hero-photo-slot" aria-label="个人照片">',
        f'          <img class="hero-photo-img" src="{esc(photo_rel)}" alt="{esc(p.name)}" '
        f'width="560" height="747" decoding="async" />',
        '          <span class="hero-photo-placeholder" aria-hidden="true">个人照片<br />'
        f"使用 <code>{esc(photo_rel)}</code>（与本页同级）</span>",
        "        </figure>",
        "      </div>",
        "    </header>",
    ]
    return "\n".join(lines)


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
        r"(?<![（(])(?<![A-Za-z./])(?<!\d)\d+\+(?!\d)(?!\s*人)|"
        r"\d+(?:\.\d+)?\s*PD\b|"
        r"\d+\s*PD\b|"
        r"\d+\s*min\b|"
        r"\d+\s*个\b|"
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


def render_skills_groups(block: str) -> str:
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith("- ")]
    parts: List[str] = ['        <div class="skills-groups">']
    esc = html.escape
    for ln in lines:
        body = ln[2:].strip()
        m = re.match(r"^([^:]+):\s*(.+)$", body)
        if not m:
            continue
        title, rest = m.group(1).strip(), m.group(2).strip()
        tags = [
            t.strip()
            for t in re.split(r"[,，;；、]\s*", rest)
            if t.strip()
        ]
        parts.append('          <div class="skill-block">')
        parts.append(f'            <h3 class="skill-subtitle">{esc(title)}</h3>')
        parts.append('            <div class="tag-list skill-tags">')
        for t in tags:
            parts.append(f'              <span class="tag">{esc(t)}</span>')
        parts.append("            </div>")
        parts.append("          </div>")
    parts.append("        </div>")
    return "\n".join(parts)


EXPERIENCE_RE = re.compile(r"^\*\*(.+?)\*\*,\s*(.+?)\s+\((.+)\)\s*$")


def parse_experience(block: str) -> str:
    """Experience: ``**title**, company (dates)`` then bullet lines."""
    lines = [ln.strip() for ln in block.splitlines()]
    jobs: List[dict] = []
    current: Optional[dict] = None
    for line in lines:
        if not line:
            continue
        m = EXPERIENCE_RE.match(line)
        if m:
            title, company, dates = (x.strip() for x in m.groups())
            current = {
                "title": title,
                "company": company,
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
        parts.append(
            '<div class="exp-first-line">'
            f'<span class="item-title">{html.escape(job["title"])}</span>'
            f'<span class="exp-org"><span class="prefix">{html.escape(job["company"])}</span></span>'
            "</div>"
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


def render_bullet_tree(nodes: List[Tuple[str, List]]) -> str:
    parts = ["<ul>"]
    for text, children in nodes:
        inner = format_project_line(text)
        li_cls = ' class="project-keywords"' if text.startswith("关键词：") else ""
        if children:
            parts.append(f"<li{li_cls}>{inner}{render_bullet_tree(children)}</li>")
        else:
            parts.append(f"<li{li_cls}>{inner}</li>")
    parts.append("</ul>")
    return "".join(parts)


def format_project_line(text: str) -> str:
    if text.startswith("关键词："):
        body = text[len("关键词：") :].strip()
        tags = re.split(r"[、,，]", body)
        tags = [t.strip() for t in tags if t.strip()]
        spans = []
        for t in tags:
            spans.append(f'<span class="tag">{html.escape(t)}</span>')
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


def normalize_project_body_lines(lines: List[str]) -> List[str]:
    """将「- 结果：正文在同一行」拆成「- 结果：」+ 子 bullet，与手写嵌套 md 渲染一致。"""
    out: List[str] = []
    for line in lines:
        m = re.match(r"^(\s*)-\s+结果：\s*(.+)$", line)
        if m and m.group(2).strip():
            indent, rest = m.group(1), m.group(2).strip()
            out.append(f"{indent}- 结果：")
            out.append(f"{indent}  - {rest}")
        else:
            out.append(line)
    return out


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
        head = (
            '<div class="project-headline"><span class="item-title">'
            + html.escape(title)
            + "</span>"
        )
        if href:
            head += (
                ' <a class="link-pill" href="'
                + html.escape(href, quote=True)
                + '">项目链接</a>'
            )
        head += "</div>"
        out.append(head)
        entries = collect_bullet_entries(normalize_project_body_lines(body))
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
        m = re.match(r"^(.+?)[：:](.+)$", ln)
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
    profile = parse_profile(md_text)

    summary = sections.get("Summary", "")
    skills = sections.get("Skills", "")
    exp = sections.get("Experience", "")
    projects = sections.get("Projects", "")
    education = sections.get("Education", "")
    certs = sections.get("Certifications", "")
    awards = sections.get("Awards", "")

    sb: List[str] = []
    sb.append(html_head_open())
    sb.append(render_profile_hero(profile))

    sb.append('    <div class="columns">')
    sb.append('      <div class="column-stack">')
    sb.append('      <section class="card section section-summary">')
    sb.append('        <div class="block-title"><h2>Summary</h2></div>')
    sb.append(bullet_list_from_block(summary))
    sb.append("      </section>")

    sb.append('      <section class="card section">')
    sb.append('        <div class="block-title"><h2>Education</h2></div>')
    sb.append(f"        <p>{rich_line(education.strip())}</p>")
    sb.append('        <div class="block-title" style="margin-top:0.7rem;">')
    sb.append("          <h2>Certifications</h2>")
    sb.append("        </div>")
    sb.append(bullet_list_from_block(certs))
    sb.append("      </section>")
    sb.append("      </div>")

    sb.append('      <section class="card section">')
    sb.append('        <div class="block-title"><h2>Skills</h2></div>')
    sb.append(render_skills_groups(skills))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Experience</h2></div>')
    sb.append(parse_experience(exp))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Projects</h2></div>')
    sb.append(render_projects(projects))
    sb.append("      </section>")

    sb.append('      <section class="card section span-2">')
    sb.append('        <div class="block-title"><h2>Awards</h2></div>')
    sb.append(render_awards(awards))
    sb.append("      </section>")

    sb.append("    </div>")
    sb.append("  </main>")
    sb.append("</body>")
    sb.append("</html>")
    return "\n".join(sb)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render resume.md to static index.html")
    ap.add_argument("--in", dest="in_path", default="resume.md", help="Input Markdown path")
    ap.add_argument("--out", dest="out_path", default="index.html", help="Output HTML path")
    args = ap.parse_args()
    src = Path(args.in_path).read_text(encoding="utf-8")
    out = build_html(src)
    outp = Path(args.out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(out, encoding="utf-8")
    print(f"Wrote {outp}")


if __name__ == "__main__":
    main()

