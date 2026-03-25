#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_name(raw: str, max_len: int = 80) -> str:
    raw = raw.strip()
    raw = re.sub(r"\s+", " ", raw)
    raw = raw.replace(" ", "_")
    raw = (
        raw.replace("：", "_")
        .replace("？", "_")
        .replace("?", "_")
        .replace("“", "")
        .replace("”", "")
        .replace("‘", "")
        .replace("’", "")
    )
    raw = re.sub(r'[\\\\/:*?"<>|]+', "_", raw)
    raw = raw.replace("\u200b", "")
    raw = re.sub(r"_+", "_", raw).strip("_")
    if len(raw) > max_len:
        raw = raw[: max_len - 1].rstrip() + "…"
    return raw or "untitled"


def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def url_filename_hint(url: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if name and "." in name:
        return name

    qs = parse_qs(parsed.query)
    if "wx_fmt" in qs and qs["wx_fmt"]:
        return f"asset.{qs['wx_fmt'][0]}"

    return "asset.bin"


def http_get_bytes(url: str, *, headers: dict[str, str] | None = None, timeout_s: int = 30) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": DEFAULT_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            **(headers or {}),
        },
        method="GET",
    )
    with urlopen(req, timeout=timeout_s) as resp:
        return resp.read()


class ImgUrlExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.img_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr_map = {k.lower(): v for k, v in attrs}
        for key in ("data-src", "data-original", "src"):
            v = attr_map.get(key)
            if v and v.startswith("http"):
                self.img_urls.append(v)
                break


@dataclass(frozen=True)
class AssetItem:
    url: str
    file: str
    bytes: int
    sha256: str


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_assets(urls: Iterable[str], assets_dir: Path) -> list[AssetItem]:
    ensure_dir(assets_dir)
    seen: set[str] = set()
    items: list[AssetItem] = []

    for url in urls:
        if url in seen:
            continue
        seen.add(url)

        hint = url_filename_hint(url)
        ext = "".join(Path(hint).suffixes) or ".bin"
        fname = f"{sha1_hex(url)}{ext}"
        out_path = assets_dir / fname

        if not out_path.exists():
            data = http_get_bytes(url, headers={"Referer": "https://mp.weixin.qq.com/"})
            out_path.write_bytes(data)

        items.append(
            AssetItem(
                url=url,
                file=str(Path("assets") / fname),
                bytes=out_path.stat().st_size,
                sha256=sha256_file(out_path),
            )
        )

    return items


def rewrite_html_assets(raw_html: str, assets: list[AssetItem]) -> str:
    out = raw_html
    for item in assets:
        out = out.replace(item.url, item.file)
    return out


def archive_wechat(url: str, out_root: Path) -> dict[str, object]:
    html_bytes = http_get_bytes(url, headers={"Referer": "https://mp.weixin.qq.com/"})
    html = html_bytes.decode("utf-8", errors="replace")

    title = "wechat_article"
    og_match = re.search(
        r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']\s*/?>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if og_match:
        title = og_match.group(1).strip()
    else:
        msg_match = re.search(r"var\s+msg_title\s*=\s*'(.*?)'\.html\(", html, flags=re.DOTALL)
        if msg_match:
            title = msg_match.group(1).strip()
        else:
            title_match = re.search(r"<title>\s*(.*?)\s*</title>", html, flags=re.IGNORECASE | re.DOTALL)
            if title_match and title_match.group(1).strip():
                title = title_match.group(1).strip()

    title = safe_name(html_lib.unescape(re.sub(r"\s+", " ", title)).strip())

    article_id = url.rstrip("/").split("/")[-1]
    dir_name = safe_name(f"微信_{title}_{article_id[-8:]}")
    out_dir = out_root / dir_name

    ensure_dir(out_dir)
    (out_dir / "source_url.txt").write_text(url + "\n", encoding="utf-8")
    (out_dir / "fetched_at.txt").write_text(utc_now_iso() + "\n", encoding="utf-8")
    (out_dir / "index.html").write_bytes(html_bytes)

    parser = ImgUrlExtractor()
    parser.feed(html)
    assets = download_assets(parser.img_urls, out_dir / "assets")
    write_json(out_dir / "assets_manifest.json", [asdict(a) for a in assets])

    local_html = rewrite_html_assets(html, assets)
    (out_dir / "index.local.html").write_text(local_html, encoding="utf-8")

    meta = {
        "type": "wechat",
        "title": title,
        "source_url": url,
        "out_dir": str(out_dir),
        "fetched_at_utc": utc_now_iso(),
        "assets": len(assets),
    }
    write_json(out_dir / "metadata.json", meta)
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- Source: {url}",
                "- Files:",
                "  - index.html (raw)",
                "  - index.local.html (rewritten local assets)",
                "  - assets/ (downloaded images)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return meta


def run_yt_dlp(url: str, out_dir: Path) -> None:
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--write-info-json",
        "--write-description",
        "--write-thumbnail",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "all",
        "--write-comments",
        "--output",
        str(out_dir / "media" / "%(title).200B [%(id)s].%(ext)s"),
        url,
    ]
    subprocess.run(cmd, check=True)


def archive_bilibili(url: str, out_root: Path) -> dict[str, object]:
    parsed = urlparse(url)
    bvid_match = re.search(r"/video/(BV[0-9A-Za-z]+)", parsed.path)
    bvid = bvid_match.group(1) if bvid_match else sha1_hex(url)[:12]
    out_dir = out_root / safe_name(f"B站_{bvid}")

    ensure_dir(out_dir)
    ensure_dir(out_dir / "media")
    (out_dir / "source_url.txt").write_text(url + "\n", encoding="utf-8")
    (out_dir / "fetched_at.txt").write_text(utc_now_iso() + "\n", encoding="utf-8")

    try:
        page = http_get_bytes(
            url,
            headers={
                "User-Agent": DEFAULT_UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )
        (out_dir / "page.html").write_bytes(page)
    except Exception as e:  # noqa: BLE001 - best-effort snapshot
        (out_dir / "page_fetch_error.txt").write_text(str(e) + "\n", encoding="utf-8")

    run_yt_dlp(url, out_dir)

    info_json = next((p for p in (out_dir / "media").glob("*.info.json")), None)
    title = None
    if info_json and info_json.exists():
        try:
            info = json.loads(info_json.read_text(encoding="utf-8"))
            title = info.get("title")
        except Exception:
            title = None

    meta = {
        "type": "bilibili",
        "title": title,
        "bvid": bvid,
        "source_url": url,
        "out_dir": str(out_dir),
        "fetched_at_utc": utc_now_iso(),
    }
    write_json(out_dir / "metadata.json", meta)
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                f"# {title or bvid}",
                "",
                f"- Source: {url}",
                "- Files:",
                "  - page.html (best-effort snapshot)",
                "  - media/* (yt-dlp outputs: video/audio, info.json, description, thumbnail, subs/comments)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return meta


def classify(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.endswith("mp.weixin.qq.com"):
        return "wechat"
    if host.endswith("bilibili.com"):
        return "bilibili"
    return "unknown"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Archive external share URLs into 对外分享/")
    parser.add_argument("--out-dir", default="对外分享", help="Output directory (default: 对外分享)")
    parser.add_argument("urls", nargs="*", help="URLs to archive")
    args = parser.parse_args(argv)

    urls = [u.strip() for u in args.urls if u.strip()]
    if not urls:
        print("[archive] No URLs provided.", file=sys.stderr)
        return 2

    out_root = Path(args.out_dir)
    ensure_dir(out_root)

    manifest_path = out_root / "_manifest.json"
    manifest: dict[str, object] = {
        "generated_at_utc": utc_now_iso(),
        "items": [],
    }

    for url in urls:
        kind = classify(url)
        print(f"[archive] {kind}: {url}", flush=True)
        try:
            if kind == "wechat":
                meta = archive_wechat(url, out_root)
            elif kind == "bilibili":
                meta = archive_bilibili(url, out_root)
            else:
                out_dir = out_root / safe_name(f"未知来源_{sha1_hex(url)[:12]}")
                ensure_dir(out_dir)
                (out_dir / "source_url.txt").write_text(url + "\n", encoding="utf-8")
                (out_dir / "fetched_at.txt").write_text(utc_now_iso() + "\n", encoding="utf-8")
                meta = {"type": "unknown", "source_url": url, "out_dir": str(out_dir)}
                write_json(out_dir / "metadata.json", meta)

            manifest["items"].append(meta)
        except subprocess.CalledProcessError as e:
            print(f"[archive] FAILED (yt-dlp): {url}\n  {e}", file=sys.stderr)
            manifest["items"].append({"type": kind, "source_url": url, "error": f"yt-dlp failed: {e}"})
        except Exception as e:  # noqa: BLE001 - best-effort archiving
            print(f"[archive] FAILED: {url}\n  {e}", file=sys.stderr)
            manifest["items"].append({"type": kind, "source_url": url, "error": str(e)})

        time.sleep(1)

    write_json(manifest_path, manifest)
    print(f"[archive] Done. Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
