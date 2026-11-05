#!/usr/bin/env python3
"""Capture screenshots of the site with headless Chromium (Playwright).

Normally run through Docker so nothing needs installing on the host:
    docker compose --profile tools run --rm screenshots

Against the live GitHub Pages URL:
    BASE_URL=https://USER.github.io/devsandbox-pages/ SHOT_PREFIX=live \
        docker compose --profile tools run --rm screenshots
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://localhost:8080/")
BASE = BASE if BASE.endswith("/") else BASE + "/"
PREFIX = os.environ.get("SHOT_PREFIX", "local")
OUT = Path(os.environ.get("OUT_DIR", "screenshots"))
OUT.mkdir(parents=True, exist_ok=True)


def shot(page, name: str, **kw) -> None:
    path = OUT / f"{PREFIX}-{name}.png"
    page.screenshot(path=str(path), **kw)
    print(f"saved {path}")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()

        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(BASE, wait_until="networkidle")
        page.wait_for_selector("#run-status.passed", timeout=15000)
        shot(page, "01-home-pipeline-run")
        shot(page, "02-home-full-page", full_page=True)

        page.locator("#architecture").scroll_into_view_if_needed()
        shot(page, "03-architecture")

        page.goto(urljoin(BASE, "no-such-page"), wait_until="networkidle")
        shot(page, "04-custom-404")
        ctx.close()

        mobile = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        mp = mobile.new_page()
        mp.goto(BASE, wait_until="networkidle")
        mp.wait_for_selector("#run-status.passed", timeout=15000)
        shot(mp, "05-mobile", full_page=True)
        mobile.close()
        browser.close()


if __name__ == "__main__":
    main()
