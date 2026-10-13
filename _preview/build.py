"""Build a self-contained preview of a draft post for publishing as a claude.ai Artifact.

Usage: python _preview/build.py [post-html-under-_site]
Run after `jekyll build --drafts` (or while `jekyll serve --drafts` is running).
Writes _preview/out/index.html plus the CSS, fonts and images it uses.
"""

import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "_site"
OUT = Path(os.environ.get("PREVIEW_OUT", REPO / "_preview" / "out"))
POST = sys.argv[1] if len(sys.argv) > 1 else "python/2026/10/11/coodie-goes-to-production.html"
THEME = "assets/themes/the-program"

html = (SITE / POST).read_text()
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
body = re.search(r"<body>(.*)</body>", html, re.S).group(1)

# Drop everything that needs a third-party host: share buttons, comments, scripts.
body = re.sub(r"<!-- AddThis Button BEGIN -->.*?<!-- AddThis Button END -->", "", body, flags=re.S)
body = re.sub(r'<div class="addthis_toolbox.*?</div>', "", body, flags=re.S)
body = re.sub(r'<div class="comment">.*?</div>\s*</div><!-- misc-content -->', "</div><!-- misc-content -->", body, flags=re.S)
body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
body = re.sub(r"<noscript>.*?</noscript>", "", body, flags=re.S)
body = re.sub(r'<nav class="pagination">.*?</nav>', "", body, flags=re.S)
# Site-absolute links: assets become relative files, other pages point at the live blog.
body = body.replace('src="/assets/', 'src="assets/')
body = re.sub(r'href="/(?!/)', 'href="https://fruch.github.io/', body)

banner = (
    '<p class="draft-banner">Draft preview, not published yet. '
    "Numbers and quotes may still change.</p>"
)
page = f"""<title>{title}</title>
<link rel="stylesheet" href="{THEME}/css/style.css">
<style>
  :root {{ color-scheme: light; }}
  body {{ background: #999999; }}
  .draft-banner {{ margin: 0; padding: 8px 16px; background: #fdf3c8; color: #3a3220;
    font: 14px/1.4 "Ubuntu Mono", monospace; text-align: center; }}
  pre, .highlight {{ overflow-x: auto; }}
</style>
{banner}
{body}
"""

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / THEME / "css").mkdir(parents=True)
(OUT / "index.html").write_text(page)

css = (SITE / THEME / "css/style.css").read_text().replace(f"url('/{THEME}/", "url('../")
(OUT / THEME / "css/style.css").write_text(css)
for sub in ("font", "skin"):
    shutil.copytree(SITE / THEME / sub, OUT / THEME / sub, ignore=shutil.ignore_patterns("*.eot", "*.svg"))
for src in sorted(set(re.findall(r'src="(assets/img/[^"]+)"', body))):
    (OUT / src).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SITE / src, OUT / src)
    if src.endswith(".svg"):  # the Artifact host rejects SVGs with a DOCTYPE (matplotlib adds one)
        svg = (OUT / src).read_text()
        (OUT / src).write_text(re.sub(r"<!DOCTYPE[^>]*>", "", svg, flags=re.S))

print("\n".join(str(p.relative_to(OUT)) for p in sorted(OUT.rglob("*")) if p.is_file()))
