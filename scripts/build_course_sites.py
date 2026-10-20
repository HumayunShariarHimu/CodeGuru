#!/usr/bin/env python3
"""Build one navigable static course site from each repository's real Markdown source."""
from __future__ import annotations
import argparse
import html
import json
import posixpath
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown

OWNER = "HumayunShariarHimu"
SKIP_DIRS = {".git", ".github", "node_modules", "vendor", "_site", "_book", ".bundle"}
COPY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".css", ".scss", ".js", ".mjs", ".pdf", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".webm", ".mp3", ".wav", ".ipynb", ".csv", ".json", ".txt", ".zip", ".html", ".htm", ".py", ".c", ".cpp", ".h", ".java", ".go", ".rb", ".php", ".sql", ".sh", ".swift", ".m", ".scala", ".clj", ".ino", ".r"}
FRONT_MATTER = re.compile(r"\A---\s*\r?\n.*?\r?\n---\s*\r?\n", re.S)
SUMMARY_LINK = re.compile(r"^\s*[-*+]\s+\[([^\]]+)\]\(([^)]+)\)")
CATALOG = {
    "arduino": ("Arduino খুঁটিনাটি", "হার্ডওয়্যার ও মাইক্রোকন্ট্রোলার"),
    "blog": ("বাংলা টেক ব্লগ", "প্রোগ্রামিং ও সফটওয়্যার ডেভেলপমেন্ট নিয়ে লেখা"),
    "bangla-programming-resources": ("বাংলা প্রোগ্রামিং রিসোর্স", "বাংলা টিউটোরিয়াল ও শেখার উপকরণ"),
    "clojure": ("Clojure ও ফাংশনাল প্রোগ্রামিং", "Clojure, Lisp এবং concurrency"),
    "django": ("Django ওয়েব ফ্রেমওয়ার্ক", "Python-এ ওয়েব অ্যাপ্লিকেশন তৈরি"),
    "c": ("সি প্রোগ্রামিং", "সি ভাষার ভিত্তি থেকে প্রোগ্রামিং"),
    "deep-learning": ("ডিপ লার্নিং", "Neural networks, CNN ও TensorFlow"),
    "data-science": ("ডেটা সায়েন্সের ভিত্তি", "পরিসংখ্যান ও ডেটা মাইনিং"),
    "go": ("Go (Golang)", "Go ভাষার ভিত্তি ও প্রোগ্রামিং"),
    "ios": ("iOS ডেভেলপমেন্ট", "Objective-C, Swift ও iOS অ্যাপ"),
    "javascript": ("জাভাস্ক্রিপ্ট", "JavaScript syntax, functions ও আধুনিক ধারণা"),
    "minima": ("Minima Jekyll থিম", "Jekyll theme-এর ডকুমেন্টেশন ও রিসোর্স"),
    "php": ("পিএইচপি", "PHP basics, OOP ও design patterns"),
    "laravel": ("Laravel ফ্রেমওয়ার্ক", "Laravel দিয়ে PHP ওয়েব ডেভেলপমেন্ট"),
    "sql": ("SQL ও MySQL", "SQL query, database design ও MySQL"),
    "shell": ("শেল ও শেল স্ক্রিপ্টিং", "Linux shell ও command line"),
    "scala": ("Scala প্রোগ্রামিং", "Scala, JVM ও functional programming"),
    "ruby": ("Ruby প্রোগ্রামিং", "Ruby ভাষার প্রাথমিক পাঠ"),
    "qt": ("Qt ফ্রেমওয়ার্ক", "Qt ও C++ দিয়ে GUI application"),
    "python-programming": ("বাংলায় পাইথন", "Python fundamentals থেকে object-oriented programming"),
    "machine-learning": ("মেশিন লার্নিং", "ডেটা প্রস্তুতি ও predictive modeling"),
    "java": ("বাংলায় জাভা", "Java fundamentals ও object-oriented programming"),
    "git": ("Git ভার্সন কন্ট্রোল", "Git, branching ও collaboration"),
}
ALIASES = {
    "python.howtocode.dev":"python-programming", "java.howtocode.dev":"java", "c.howtocode.dev":"c",
    "php.howtocode.dev":"php", "sh.howtocode.dev":"shell", "ml.howtocode.dev":"machine-learning",
    "ios.howtocode.dev":"ios", "dl.howtocode.dev":"deep-learning", "arduino.howtocode.dev":"arduino",
    "ds.howtocode.dev":"data-science", "qt.howtocode.dev":"qt", "sql.howtocode.dev":"sql",
    "golang.howtocode.dev":"go", "clojure.howtocode.dev":"clojure", "js.howtocode.dev":"javascript",
    "laravel.howtocode.dev":"laravel", "django.howtocode.dev":"django", "git.howtocode.dev":"git",
    "scala.howtocode.dev":"scala", "ruby.howtocode.dev":"ruby",
}


def md_files(root: Path) -> list[Path]:
    return sorted((p.resolve() for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".markdown"} and not p.is_symlink() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)), key=lambda p: p.relative_to(root).as_posix().casefold())


def output_map(root: Path, sources: list[Path]) -> dict[Path, Path]:
    result = {}
    has_readme = any(p.relative_to(root).as_posix().lower() == "readme.md" for p in sources)
    for src in sources:
        rel = src.relative_to(root)
        low = rel.as_posix().lower()
        if low in {"readme.md", "summary.md"}:
            dest = Path("index.html")
        elif low == "index.md":
            dest = Path("index-page.html") if has_readme else Path("index.html")
        else:
            dest = rel.with_suffix(".html")
        result[src] = dest
    return result


def title_from(text: str, fallback: str) -> str:
    text = FRONT_MATTER.sub("", text)
    for line in text.splitlines():
        m = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", line)
        if m:
            return re.sub(r"[`*_]", "", m.group(1)).strip()[:120]
    return fallback


def chapter_list(root: Path, sources: list[Path], mapping: dict[Path, Path], slug: str) -> list[tuple[int, str, Path]]:
    result: list[tuple[int, str, Path]] = []
    seen: set[Path] = set()
    summary = root / "SUMMARY.md"
    if summary.is_file():
        for line in summary.read_text(encoding="utf-8", errors="replace").splitlines():
            match = SUMMARY_LINK.match(line)
            if not match:
                continue
            label, target = match.group(1).strip(), match.group(2).strip()
            rel = target.split("#", 1)[0].split("?", 1)[0]
            src = (summary.parent / unquote(rel)).resolve()
            if src not in mapping or src.suffix.lower() not in {".md", ".markdown"}:
                continue
            dest = mapping[src]
            if dest in seen or src.name.lower() == "summary.md":
                continue
            depth = min(5, (len(line) - len(line.lstrip(" "))) // 2)
            result.append((depth, label, dest)); seen.add(dest)
    if not result:
        for src in sources:
            rel = src.relative_to(root)
            if src.name.lower() in {"readme.md", "summary.md"}:
                continue
            dest = mapping[src]
            if dest not in seen:
                label = title_from(src.read_text(encoding="utf-8", errors="replace"), rel.stem.replace("-", " ").replace("_", " ").title())
                result.append((min(5, max(0, len(rel.parts)-1)), label, dest)); seen.add(dest)
    intro = next((p for p in sources if p.relative_to(root).as_posix().lower() == "readme.md"), None)
    if intro is None:
        intro = next((p for p in sources if p.relative_to(root).as_posix().lower() == "index.md"), None)
    if intro:
        dest = mapping[intro]
        if dest not in seen:
            result.insert(0, (0, "পরিচিতি", dest)); seen.add(dest)
    for src in sources:
        dest = mapping[src]
        if dest in seen or src.name.lower() in {"readme.md", "summary.md"}:
            continue
        rel = src.relative_to(root)
        label = title_from(src.read_text(encoding="utf-8", errors="replace"), rel.stem.replace("-", " ").replace("_", " ").title())
        result.append((min(5, max(0, len(rel.parts)-1)), label, dest)); seen.add(dest)
    return result


class HtmlLinks(HTMLParser):
    def __init__(self, content: str, rewrite):
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.rewrite = rewrite
        self.feed(content); self.close()
    def handle_starttag(self, tag, attrs):
        self.out.append("<" + tag)
        for key, value in attrs:
            if value is not None and key.lower() in {"href", "src"}:
                value = self.rewrite(value)
                if value is None:
                    continue
            if value is None: self.out.append(" " + key)
            else: self.out.append(" " + key + '="' + html.escape(value, quote=True) + '"')
        self.out.append(">")
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs); self.out[-1] = "/>"
    def handle_endtag(self, tag): self.out.append("</" + tag + ">")
    def handle_data(self, data): self.out.append(data)
    def handle_entityref(self, name): self.out.append("&" + name + ";")
    def handle_charref(self, name): self.out.append("&#" + name + ";")
    def handle_comment(self, data): self.out.append("<!--" + data + "-->")


def page_for_directory(candidate: Path, mapping: dict[Path, Path]) -> Path | None:
    """Resolve a directory URL to its authored landing page when one exists."""
    for name in ("README.md", "index.md", "SUMMARY.md"):
        source_page = (candidate / name).resolve()
        if source_page in mapping:
            return mapping[source_page]
    return None


def mapped_url(destination: Path, output: Path, parts) -> str:
    rel = posixpath.relpath(destination.as_posix(), output.parent.as_posix() or ".")
    if not rel.startswith(".") and "/" not in rel:
        rel = "./" + rel
    return urlunsplit(("", "", quote(rel, safe="/._-"), parts.query, parts.fragment))


def rewrite_link(value: str, source: Path, course_root: Path, output: Path, mapping: dict[Path, Path], base_path: str) -> str:
    parts = urlsplit(value)
    if not parts.scheme and not parts.netloc and parts.path.startswith("www."):
        return "https://" + value
    if parts.scheme in {"http", "https"}:
        slug = ALIASES.get((parts.hostname or "").lower())
        if slug:
            return f"{base_path}/courses/{slug}/index.html"
        return value
    if parts.scheme or parts.netloc:
        return value
    path = unquote(parts.path)
    if course_root.name == "laravel" and path.startswith("/docs/{{version}}/"):
        return "https://laravel.com/docs/" + quote(path.split("/", 3)[-1], safe="/._-{}")
    if path.startswith("/"):
        candidate = (course_root / path.lstrip("/")).resolve()
        try: candidate.relative_to(course_root.resolve())
        except ValueError: return value
        if candidate in mapping:
            destination = mapping[candidate]
        elif candidate.is_dir():
            destination = page_for_directory(candidate, mapping)
            if not destination:
                return value
        elif candidate.is_file():
            destination = Path(candidate.relative_to(course_root).as_posix())
        else:
            return value
        return mapped_url(destination, output, parts)
    if path:
        candidate = (source.parent / path).resolve()
        try:
            candidate.relative_to(course_root.resolve())
        except ValueError:
            return value
        if candidate.is_dir():
            destination = page_for_directory(candidate, mapping)
            if destination:
                return mapped_url(destination, output, parts)
    if not path.lower().endswith((".md", ".markdown")):
        if course_root.name == "minima" and path.lower().endswith((".html", ".htm")):
            return None
        if course_root.name == "python-programming" and path.lower().endswith(".html"):
            source_target = (source.parent / path).resolve()
            if not source_target.is_file():
                return urlunsplit(("https", "docs.python.org", "/3/library/" + quote(path.lstrip("./"), safe="/._-"), parts.query, parts.fragment))
        if path.lower().endswith((".html", ".htm")) and not (source.parent / path).is_file():
            return None
        return value
    candidate = (source.parent / path).resolve()
    try: candidate.relative_to(course_root.resolve())
    except ValueError: return value
    destination = mapping.get(candidate)
    if not destination:
        if course_root.name == "python-programming" and path.lower().endswith(".html"):
            return urlunsplit(("https", "docs.python.org", "/3/library/" + quote(path.lstrip("./"), safe="/._-"), parts.query, parts.fragment))
        if candidate.is_file():
            return None
        return None
    return mapped_url(destination, output, parts)


def course_page(slug: str, book_title: str, description: str, source: Path, out_rel: Path, entries: list[tuple[int, str, Path]], prev: Path | None, nxt: Path | None, body: str, base_path: str, site_url: str) -> str:
    base = f"{base_path}/courses/{slug}"
    title = book_title if out_rel == Path("index.html") else title_from(source.read_text(encoding="utf-8", errors="replace"), book_title)
    nav_items=[]
    for depth,label,dest in entries:
        href=f"{base}/{quote(dest.as_posix(), safe='/._-')}"
        active=' class="active" aria-current="page"' if dest == out_rel else ""
        nav_items.append(f'<li class="depth-{depth}"><a href="{html.escape(href, quote=True)}"{active}>{html.escape(label)}</a></li>')
    def pager(dest: Path | None, label: str, cls: str) -> str:
        if not dest: return "<span></span>"
        return f'<a class="pager {cls}" href="{base}/{quote(dest.as_posix(), safe="/._-")}">{label}</a>'
    canonical = site_url.rstrip("/") + f"/courses/{slug}/{quote(out_rel.as_posix(), safe='/._-')}"
    return f'''<!doctype html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — {html.escape(book_title)} | CodeGuru</title><meta name="description" content="{html.escape(description, quote=True)}"><meta name="theme-color" content="#263b4d"><link rel="canonical" href="{html.escape(canonical, quote=True)}"><link rel="stylesheet" href="{base}/assets/book.css"></head><body><header class="topbar"><button id="menu-toggle" aria-label="সূচিপত্র খুলুন" aria-expanded="false">☰</button><a class="book-brand" href="{base}/index.html">{html.escape(book_title)}</a><div class="top-actions"><a href="{base_path}/">সব কোর্স</a><a href="https://github.com/{OWNER}/{slug}" target="_blank" rel="noopener">GitHub-এ সোর্স ↗</a></div></header><div class="book-shell"><aside id="sidebar" class="sidebar"><div class="sidebar-heading"><a href="{base}/index.html">{html.escape(book_title)}</a><span>{html.escape(description)}</span></div><nav aria-label="অধ্যায় সূচি"><ul>{''.join(nav_items)}</ul></nav></aside><main class="reading"><div class="breadcrumbs"><a href="{base_path}/">CodeGuru</a><span> / </span><a href="{base}/index.html">{html.escape(book_title)}</a></div><article class="markdown-body">{body}</article><div class="chapter-pager">{pager(prev,'← আগের অধ্যায়','prev')}{pager(nxt,'পরের অধ্যায় →','next')}</div><footer class="book-footer"><a href="{base}/index.html">সূচিতে ফিরে যান</a> · <a href="https://github.com/{OWNER}/{slug}" target="_blank" rel="noopener">মূল রিপোজিটরি</a> · <a href="{base_path}/">CodeGuru</a></footer></main></div><script>(function(){{var b=document.getElementById('menu-toggle'),s=document.getElementById('sidebar');b.addEventListener('click',function(){{var o=s.classList.toggle('open');b.setAttribute('aria-expanded',String(o));}});}})();</script></body></html>'''


def build_one(repo: Path, output_root: Path, slug: str, base_path: str, site_url: str, book_css: Path) -> dict:
    sources=md_files(repo)
    if not sources:
        raise RuntimeError(f"No Markdown source files in {slug}")
    mapping=output_map(repo,sources)
    entries=chapter_list(repo,sources,mapping,slug)
    title,description=CATALOG[slug]
    destination=output_root/slug
    if destination.exists(): shutil.rmtree(destination)
    destination.mkdir(parents=True)
    # Preserve images and attachment paths so relative links from the original Markdown keep working.
    for path in repo.rglob("*"):
        if not path.is_file() or path.is_symlink(): continue
        rel=path.relative_to(repo)
        if any(part in SKIP_DIRS or part == ".git" for part in rel.parts): continue
        if path.suffix.lower() in {".md",".markdown"} or path.name in {"pages-metadata.json","requirements-pages.txt","SUMMARY.md","package.json","book.json","Gemfile","Gemfile.lock"}: continue
        if path.suffix.lower() not in COPY_EXTS or (slug == "minima" and path.suffix.lower() in {".html", ".htm"}): continue
        target=destination/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
    assetdir=destination/"assets"; assetdir.mkdir(exist_ok=True); shutil.copy2(book_css,assetdir/"book.css")
    order=[]
    for _,_,dest in entries:
        if dest not in order: order.append(dest)
    neighbors={dest:(order[i-1] if i else None,order[i+1] if i+1<len(order) else None) for i,dest in enumerate(order)}
    for source in sources:
        dest=mapping[source]
        if source.name.lower()=="summary.md": continue
        text=FRONT_MATTER.sub("",source.read_text(encoding="utf-8",errors="replace"))
        converter=markdown.Markdown(extensions=["extra","toc","fenced_code","sane_lists","tables"])
        body=converter.convert(text)
        body=HtmlLinks(body,lambda link:rewrite_link(link,source,repo,dest,mapping,base_path)).out
        target=destination/dest; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(course_page(slug,title,description,source,dest,entries,*neighbors.get(dest,(None,None)),"".join(body),base_path,site_url),encoding="utf-8")
    return {"repo":slug,"title":title,"markdown_pages":len(sources)-sum(1 for p in sources if p.name.lower()=="summary.md"),"navigation_entries":len(entries)}


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--content",default="content")
    parser.add_argument("--output",default="_site/courses")
    args=parser.parse_args()
    root=Path.cwd().resolve(); content=(root/args.content).resolve(); output=(root/args.output).resolve()
    meta=json.loads((root/"pages-metadata.json").read_text(encoding="utf-8"))
    base_path=meta.get("base_path","/CodeGuru").rstrip("/"); site_url=meta["site_url"]
    if output.exists(): shutil.rmtree(output)
    output.mkdir(parents=True)
    book_css=Path(__file__).with_name("book.css")
    results=[]
    for slug in CATALOG:
        result=build_one(content/slug,output,slug,base_path,site_url,book_css)
        results.append(result)
        print(f"Built {slug}: {result['markdown_pages']} pages; {result['navigation_entries']} navigation links",flush=True)
    manifest={"site_count":len(results),"markdown_page_count":sum(r["markdown_pages"] for r in results),"sites":results}
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Built {manifest['site_count']} resource sites and {manifest['markdown_page_count']} Markdown pages")

if __name__=="__main__":
    main()
