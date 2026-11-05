#!/usr/bin/env python3
"""HTTP smoke test against a running copy of the site (container or live URL).

Usage:
    python scripts/smoke_test.py                       # http://localhost:8080
    python scripts/smoke_test.py https://user.github.io/devsandbox-pages/ --live

--live skips checks that only apply to the local nginx container
(/healthz endpoint and custom security headers).
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "smoke-test/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode("utf-8", "replace")


def wait_until_up(base: str, seconds: int) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            if fetch(base)[0] < 500:
                return True
        except OSError:
            pass
        time.sleep(1)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", nargs="?", default="http://localhost:8080/")
    ap.add_argument("--live", action="store_true", help="target is GitHub Pages, not the local container")
    ap.add_argument("--wait", type=int, default=30, help="seconds to wait for the server")
    args = ap.parse_args()
    base = args.base if args.base.endswith("/") else args.base + "/"

    if not wait_until_up(base, args.wait):
        print(f"FAIL  {base} did not come up within {args.wait}s")
        return 1

    results: list[tuple[bool, str]] = []

    def check(ok: bool, label: str) -> None:
        results.append((ok, label))
        print(("PASS  " if ok else "FAIL  ") + label)

    code, hdr, body = fetch(base)
    check(code == 200, f"GET / returns 200 (got {code})")
    check("text/html" in hdr.get("Content-Type", ""), "GET / is served as text/html")
    check("<title>DevSandbox" in body, "home page has the expected <title>")
    check('id="pipeline"' in body, "home page contains the pipeline section")

    for path, ctype in (("assets/css/style.css", "text/css"),
                        ("assets/js/main.js", "javascript"),
                        ("assets/favicon.svg", "svg"),
                        ("robots.txt", "text/plain")):
        c, h, _ = fetch(urljoin(base, path))
        check(c == 200 and ctype in h.get("Content-Type", ""), f"GET /{path} returns 200 with {ctype}")

    c, _, b = fetch(urljoin(base, "this-page-does-not-exist"))
    check(c == 404, f"unknown path returns 404 (got {c})")
    check("does not exist" in b, "404 page uses the custom 404.html")

    if not args.live:
        c, _, b = fetch(urljoin(base, "healthz"))
        check(c == 200 and b.strip() == "ok", "GET /healthz returns ok")
        check(hdr.get("X-Content-Type-Options") == "nosniff", "header X-Content-Type-Options: nosniff")
        check(hdr.get("X-Frame-Options") == "DENY", "header X-Frame-Options: DENY")
        check("default-src 'self'" in hdr.get("Content-Security-Policy", ""), "Content-Security-Policy header is set")
        check("nginx/" not in hdr.get("Server", ""), "server version is not disclosed")

    failed = [label for ok, label in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
