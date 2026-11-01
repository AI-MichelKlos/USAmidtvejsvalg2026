#!/usr/bin/env python3
"""Capture a real browser screenshot of the public map for LinkedIn (1200 x 630).
The temporary screenshot-only CSS does NOT change the published website.
"""
import os
import re
import shutil
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

repo = os.environ.get("GITHUB_REPOSITORY", "")
slug = repo.rsplit("/", 1)[-1]
assert slug in ("USAmidtvejsvalg", "USAmidtvejsvalg2026"), repo
base = f"https://ai-michelklos.github.io/{slug}/"
image_name = "social-preview-site.png"
image_path = Path("assets") / image_name

# Screenshot-only layout: show the real headline, real state map and state details
# together in the aspect ratio used by LinkedIn without editing the website.
compact = """
html,body {overflow-x:hidden!important}
.header-inner {padding:10px 28px!important;gap:15px!important;max-width:1200px!important}
.brand-credit {display:none!important}
.nav {gap:14px!important}
.nav-link {font-size:13px!important}
.share-button {display:none!important}
.page {padding:0 30px!important;max-width:1200px!important}
.hero {padding:17px 0 11px!important;gap:10px!important}
.hero h1 {font-size:49px!important;letter-spacing:-1.6px!important}
.hero-copy {margin-top:7px!important;font-size:14px!important}
.election-date {display:none!important}
.snapshot-line {display:none!important}
.balance {display:none!important}
.map-layout {margin-top:10px!important;gap:13px!important;
             grid-template-columns:minmax(0,1.75fr) minmax(0,.9fr)!important}
.map-panel {padding:11px 14px!important}
.state-detail {padding:13px!important;max-height:455px!important;overflow:hidden!important}
.map-top {margin-bottom:3px!important}
.map-top h2 {font-size:21px!important}
.map-top .eyebrow {font-size:10px!important}
.map-description,.map-legend,.map-bottom,.map-note,.explainer-row,
#election-explainers,.chicago-shortcut {display:none!important}
.map-stage {margin:3px 0!important}
#us-map {max-height:420px!important}
.map-stage svg {overflow:visible!important}
"""

with sync_playwright() as p:
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    browser = p.chromium.launch(
        headless=True,
        executable_path=chrome if chrome else None,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width":1200,"height":630},
                            device_scale_factor=1, reduced_motion="reduce")
    page.goto(base + "?view=senate&state=IL&preview=1",
              wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#us-map path.state-shape", timeout=45000)
    page.add_style_tag(content=compact)
    page.wait_for_timeout(1500)
    page.wait_for_function("document.querySelectorAll('#us-map path.state-shape').length >= 50",
                           timeout=20000)
    title = page.locator("#page-title").inner_text()
    count = page.locator("#us-map path.state-shape").count()
    bounds = page.locator("#us-map").bounding_box()
    print(f"Page: {page.url}")
    print(f"Title: {title}; rendered state paths: {count}; map bounds: {bounds}")
    if "Senatet" not in title or count < 50 or not bounds:
        raise RuntimeError("Homepage failed screenshot content checks")
    if bounds["y"] > 400 or bounds["height"] < 100:
        raise RuntimeError("Map is not sufficiently visible in screenshot viewport")
    page.screenshot(path=str(image_path), full_page=False, animations="disabled")
    browser.close()

im = Image.open(image_path).convert("RGB")
if im.size != (1200,630):
    raise RuntimeError(f"Incorrect screenshot dimensions: {im.size}")
if len(set(im.resize((100,53)).getdata())) < 80:
    raise RuntimeError("Screenshot seems nearly blank")

print(f"Actual website screenshot saved at {image_path}: "
      f"{image_path.stat().st_size} bytes, {im.size[0]}x{im.size[1]}")

# Switch LinkedIn metadata only AFTER the real screenshot is present & verified.
old = "assets/social-preview.png?v=20261101"
new = f"assets/{image_name}?v=20261101-realmap"
for name in ("index.html", "saadan-fungerer-valget.html"):
    path = Path(name)
    html = path.read_text(encoding="utf-8")
    if old not in html and new in html:
        print("Already updated",name)
        continue
    if html.count(old) < 3:
        raise RuntimeError(f"Expected previous image metadata missing from {name}")
    html = html.replace(old, new)
    html = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(">)',
                  r'\1Skærmbillede af valgkortet Midtvejsvalg i USA 2026, med Senatet og USA-kortet.\2',
                  html)
    path.write_text(html, encoding="utf-8")
    print(f"Updated image metadata in {name}")
