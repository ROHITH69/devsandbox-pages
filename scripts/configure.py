#!/usr/bin/env python3
"""Replace the YOUR_GITHUB_USERNAME placeholder with your real GitHub username.

Usage:
    python scripts/configure.py --user octocat
    python scripts/configure.py --repo octocat/devsandbox-pages     # used by CI
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PLACEHOLDER = "YOUR_GITHUB_USERNAME"
EXTENSIONS = {".html", ".md", ".yml", ".yaml", ".txt"}
SKIP_DIRS = {".git", "node_modules"}


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--user", help="GitHub username")
    g.add_argument("--repo", help="owner/name (for example $GITHUB_REPOSITORY)")
    ap.add_argument("--path", default=".", help="folder to process (default: repo root)")
    ap.add_argument("--no-docs", action="store_true", help="only touch site/ (used in CI)")
    args = ap.parse_args()

    user = args.user or args.repo.split("/")[0]
    if not user or "/" in user or " " in user:
        print("invalid username", file=sys.stderr)
        return 2

    root = Path(args.path)
    changed = 0
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix not in EXTENSIONS or SKIP_DIRS & set(f.parts):
            continue
        if args.no_docs and "site" not in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        if PLACEHOLDER in text:
            f.write_text(text.replace(PLACEHOLDER, user), encoding="utf-8")
            print(f"updated {f}")
            changed += 1
    print(f"Done: {changed} file(s) updated for user '{user}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
