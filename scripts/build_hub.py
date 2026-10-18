#!/usr/bin/env python3
"""Render CodeGuru's searchable repository cards into static, crawler-visible HTML."""
from __future__ import annotations
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "projects.json"
START = "<!-- PROJECT_CARDS_START -->"
END = "<!-- PROJECT_CARDS_END -->"
OWNER = "HumayunShariarHimu"
PAGES_HOST = "humayunshariarhimu.github.io"


def safe_https_url(value: str, allowed_hosts: set[str]) -> str:
    parts = urlsplit(value)
    if parts.scheme != "https" or parts.hostname not in allowed_hosts or parts.username or parts.password:
        raise ValueError(f"Unexpected URL in project catalog: {value!r}")
    return value


def render_card(project: dict) -> str:
    title = html.escape(project["title"])
    slug = project["repo"]
    repo = html.escape(slug)
    description = html.escape(project["description"])
    mark = html.escape(project.get("mark", slug[:2].upper()))
    status = project.get("status", "published")
    if status not in {"published", "pending"}:
        raise ValueError(f"Unsupported publication status for {slug}: {status}")
    pages_url = safe_https_url(project["pages_url"], {PAGES_HOST})
    repo_url = safe_https_url(project["repo_url"], {"github.com"})
    expected_repo = f"https://github.com/{OWNER}/{slug}"
    expected_page = f"https://{PAGES_HOST}/{slug}/"
    if repo_url.rstrip("/") != expected_repo:
        raise ValueError(f"Repository URL does not match the owner and slug: {repo_url}")
    if pages_url.rstrip("/") != expected_page.rstrip("/"):
        raise ValueError(f"Pages URL does not match the expected project path: {pages_url}")
    topics = [str(t) for t in project.get("topics", [])[:10]]
    searchable = " ".join([project["title"], slug, project["description"], *topics, pages_url]).lower()
    chips = "".join(f"<li>{html.escape(topic)}</li>" for topic in topics[:3])
    search_attr = html.escape(searchable, quote=True)
    if status == "published":
        card_class = "project-card"
        label = "Published guide"
        title_markup = f'<a href="{html.escape(pages_url, quote=True)}" target="_blank" rel="noopener noreferrer">{title}</a>'
        actions = f'<a class="read-link" href="{html.escape(pages_url, quote=True)}" target="_blank" rel="noopener noreferrer">Read the guide <span aria-hidden="true">↗</span></a><a class="source-link" href="{html.escape(repo_url, quote=True)}" target="_blank" rel="noopener noreferrer">GitHub source <span aria-hidden="true">↗</span></a>'
    else:
        card_class = "project-card is-pending"
        label = "Awaiting publication"
        title_markup = title
        actions = f'<span class="pending-note">Repository not published yet</span><code class="expected-path">/{repo}/</code>'
    return f'''<article class="{card_class}" data-project data-status="{status}" data-search="{search_attr}">
  <div class="card-topline"><span class="project-mark" aria-hidden="true">{mark}</span><span class="repo-label">{label} · {repo}</span></div>
  <h3>{title_markup}</h3>
  <p>{description}</p>
  <ul class="topic-list" aria-label="Topics">{chips}</ul>
  <div class="card-actions">{actions}</div>
</article>'''


def replace_marker(source: str, name: str, value: str) -> str:
    pattern = re.compile(rf"<!-- {name}_START -->.*?<!-- {name}_END -->", re.S)
    replacement = f"<!-- {name}_START -->{value}<!-- {name}_END -->"
    updated, count = pattern.subn(lambda _: replacement, source)
    if count == 0:
        raise ValueError(f"Missing marker pair for {name}")
    return updated


def main() -> None:
    projects = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(projects, list) or not projects:
        raise ValueError("projects.json must contain at least one project")
    repos = [p.get("repo") for p in projects]
    if len(repos) != len(set(repos)):
        raise ValueError("Duplicate repository slugs in projects.json")
    published = [p for p in projects if p.get("status") == "published"]
    pending = [p for p in projects if p.get("status") == "pending"]
    cards = "\n".join(render_card(p) for p in projects)
    source = INDEX.read_text(encoding="utf-8")
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("index.html must contain exactly one project-card marker pair")
    start = source.index(START) + len(START)
    end = source.index(END)
    if end < start:
        raise ValueError("Project-card markers are out of order")
    source = source[:start] + "\n" + cards + "\n        " + source[end:]
    canonical = "https://humayunshariarhimu.github.io/CodeGuru/"
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "CodeGuru: Bangla Programming & Developer Guides",
        "description": "A searchable directory of Bangla-first programming books and developer guides.",
        "url": canonical,
        "mainEntity": {
            "@type": "ItemList",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(published),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "item": {
                        "@type": "LearningResource",
                        "name": project["title"],
                        "description": project["description"],
                        "url": project["pages_url"],
                        "learningResourceType": "Online book or guide",
                        "inLanguage": "bn",
                        "provider": {"@type": "Organization", "name": "CodeGuru"},
                    },
                }
                for i, project in enumerate(published, 1)
            ],
        },
    }
    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    source = replace_marker(source, "PROJECT_COUNT", str(len(published)))
    source = replace_marker(source, "TOTAL_REPOSITORIES", str(len(projects) + 1))
    source = replace_marker(source, "PENDING_COUNT", str(len(pending)))
    source = replace_marker(source, "PROJECT_SCHEMA", schema_json)
    INDEX.write_text(source, encoding="utf-8")
    print(f"Rendered {len(projects)} CodeGuru projects: {len(published)} published and {len(pending)} pending.")


if __name__ == "__main__":
    main()
