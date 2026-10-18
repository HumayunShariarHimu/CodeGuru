#!/usr/bin/env python3
"""Import the explicitly listed public repositories as source snapshots."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import json
import shutil
import subprocess

OWNER = "HumayunShariarHimu"
REPOS = ["arduino", "blog", "bangla-programming-resources", "clojure", "django", "c", "deep-learning", "data-science", "go", "ios", "javascript", "minima", "php", "laravel", "sql", "shell", "scala", "ruby", "qt", "python-programming", "machine-learning", "java", "git"]
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "content"


def snapshot(repo: str, refresh: bool) -> tuple[str, bool, str]:
    target = DEST / repo
    if target.is_dir() and not refresh and not (target / ".git").exists():
        return repo, True, "existing snapshot kept"
    temp = DEST / f".{repo}.importing"
    shutil.rmtree(temp, ignore_errors=True)
    if refresh:
        shutil.rmtree(target, ignore_errors=True)
    clone = subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{OWNER}/{repo}.git", str(temp)], text=True, capture_output=True)
    if clone.returncode:
        shutil.rmtree(temp, ignore_errors=True)
        return repo, False, clone.stderr.strip() or "clone failed"
    revision = subprocess.run(["git", "-C", str(temp), "rev-parse", "HEAD"], text=True, capture_output=True).stdout.strip()
    shutil.rmtree(temp / ".git", ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(target, ignore_errors=True)
    temp.rename(target)
    (target / ".source-revision").write_text(revision + "\n", encoding="utf-8")
    return repo, True, f"source revision {revision[:12]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Replace stored source snapshots with current repository contents")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    failed = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(snapshot, repo, args.refresh) for repo in REPOS]
        for future in as_completed(futures):
            repo, ok, detail = future.result()
            print(f"{'OK' if ok else 'FAIL'} {repo}: {detail}", flush=True)
            if not ok:
                failed.append(repo)
    revisions = {}
    for repo in REPOS:
        marker = DEST / repo / ".source-revision"
        if marker.is_file():
            revisions[repo] = marker.read_text(encoding="utf-8").strip()
    (DEST / "SOURCES.json").write_text(json.dumps({"owner": OWNER, "repositories": revisions}, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(REPOS) - len(failed)}/{len(REPOS)} source repositories")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
