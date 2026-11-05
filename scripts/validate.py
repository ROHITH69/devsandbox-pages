#!/usr/bin/env python3
"""Static checks for the site. Standard library only, so it runs anywhere.

Checks:
  * required files exist
  * every HTML file has a doctype, <html lang>, <title> and a viewport meta tag
  * tags are balanced
  * every local href/src points at a file that exists
  * every #fragment link on a page points at an id that exists on that page

Exit code 0 = pass, 1 = failures. Use --strict to also fail on warnings.
"""
from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
REQUIRED = ["index.html", "404.html", "assets/css/style.css", "assets/js/main.js", "assets/favicon.svg", ".nojekyll"]
PLACEHOLDER = "YOUR_GITHUB_USERNAME"


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []  # (attr, value)
        self.has_doctype = False
        self.lang = False
        self.title = ""
        self.viewport = False
        self._in_title = False

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and a.get("lang"):
            self.lang = True
        if tag == "meta" and a.get("name") == "viewport":
            self.viewport = True
        if tag == "title":
            self._in_title = True
        if "id" in a and a["id"]:
            self.ids.add(a["id"])
        for attr in ("href", "src"):
            if a.get(attr):
                self.refs.append((attr, a[attr]))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # self-closing syntax such as <path/>: record attrs, do not push
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-1] if self.stack else 'none'})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def check_page(path: Path, root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    p = Page()
    p.feed(text)
    p.close()
    rel = path.relative_to(root)

    if not p.has_doctype:
        errors.append(f"{rel}: missing <!DOCTYPE html>")
    if not p.lang:
        errors.append(f"{rel}: <html> has no lang attribute")
    if not p.title.strip():
        errors.append(f"{rel}: missing or empty <title>")
    if not p.viewport:
        errors.append(f"{rel}: missing viewport meta tag")
    errors += [f"{rel}: {e}" for e in p.errors]
    if p.stack:
        errors.append(f"{rel}: unclosed tags: {', '.join(p.stack)}")

    for attr, value in p.refs:
        u = urlparse(value)
        if u.scheme in ("http", "https", "mailto", "tel", "data"):
            continue
        if value.startswith("#"):
            if value[1:] and value[1:] not in p.ids:
                errors.append(f"{rel}: {attr}={value!r} has no matching id")
            continue
        target = (path.parent / u.path).resolve() if u.path else path
        if u.path.endswith("/") or u.path in ("", "."):
            target = (path.parent / u.path / "index.html").resolve()
        if not target.exists():
            errors.append(f"{rel}: {attr}={value!r} does not exist")

    if PLACEHOLDER in text:
        warnings.append(f"{rel}: contains {PLACEHOLDER} (run scripts/configure.py before publishing)")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="site", help="site directory (default: site)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for name in REQUIRED:
        if not (root / name).exists():
            errors.append(f"missing required file: {name}")

    pages = sorted(root.rglob("*.html"))
    if not pages:
        errors.append("no HTML files found")
    for page in pages:
        e, w = check_page(page, root)
        errors += e
        warnings += w

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    failed = bool(errors) or (args.strict and bool(warnings))
    print(f"\nChecked {len(pages)} HTML file(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    print("RESULT: FAIL" if failed else "RESULT: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
