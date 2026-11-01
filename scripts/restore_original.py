#!/usr/bin/env python3
"""Download the deployed static site and all its same-host assets."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import re

SITE = "https://valgkort-usa-2026-michel.danske-a-kas-7580.chatgpt.site/"
ROOT = Path(".")
seen = set()
queue = ["index.html"]
MIME_SKIP = {".php", ".cgi"}

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("link", "script", "img", "source"):
            self.urls.extend([v for k,v in a.items() if k in ("href", "src") and v])

def normalize(raw):
    if not raw or raw.startswith(("#","data:","blob:","mailto:","javascript:")): return None
    url = urljoin(SITE, raw)
    parsed = urlsplit(url)
    if parsed.netloc != urlsplit(SITE).netloc: return None
    rel = unquote(parsed.path.lstrip("/"))
    if not rel: return "index.html"
    if ".." in Path(rel).parts or rel.startswith("."): return None
    return rel

def enqueue(value):
    path = normalize(value)
    if path and path not in seen and path not in queue:
        queue.append(path)

def extract_refs(path, content):
    text = content.decode("utf-8", "replace")
    if path.endswith(".html"):
        p = Elements(); p.feed(text)
        for ref in p.urls: enqueue(ref)
    if path.endswith(".css"):
        for s in re.findall(r'url\(\s*[\x27\x22]?([^\x27\x22)]+)', text):
            enqueue(s)
        for s in re.findall(r'@import\s+[\x27\x22]([^\x27\x22]+)', text):
            enqueue(s)
    if path.endswith((".js", ".html", ".css")):
        for ref in re.findall(r'(?:(?:[\x27\x22\x60])|(?:url\())((?:\./|/)?(?:assets|data|fonts|images|img|maps)/[a-zA-Z0-9_./-]+\.(?:json|geojson|topojson|js|css|svg|png|jpg|jpeg|webp|woff2?|ttf|csv))(?:[\x27\x22\x60\x29])', text):
            enqueue(ref)

while queue:
    rel = queue.pop(0)
    if rel in seen: continue
    seen.add(rel)
    if len(seen) > 250: raise RuntimeError("Too many assets")
    url = SITE if rel == "index.html" else urljoin(SITE, rel)
    try:
        req = Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urlopen(req, timeout=35) as response:
            if response.status != 200: raise RuntimeError("HTTP " + str(response.status))
            body = response.read()
    except HTTPError as exc:
        print("MISSING:", rel, str(exc))
        continue
    if len(body) > 25_000_000:
        raise RuntimeError("File too large: " + rel)
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    print("DOWNLOADED:", rel, len(body), "bytes")
    extract_refs(rel, body)

index = (ROOT / "index.html").read_text(encoding="utf-8")
expected = ["assets/style.css", "assets/data.js", "assets/app.js", "assets/math.js"]
missing = [s for s in expected if not (ROOT / s).is_file()]
if missing: raise RuntimeError("Required original files missing: " + repr(missing))
if "Median husstandsindkomst" not in index and "Median husstandsindkomst" not in (ROOT/"assets/app.js").read_text(encoding="utf-8",errors="replace"):
    raise RuntimeError("Cannot verify Census fields in original source")
print("VERIFIED: Original site HTML and mandatory script/style assets downloaded")
