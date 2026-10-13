"""Build a self-contained preview of a draft post for publishing as a claude.ai Artifact.

Usage: python _preview/build.py [post-html-under-_site]
Run after `jekyll build --drafts` (or while `jekyll serve --drafts` is running).
Writes _preview/out/index.html plus the CSS, fonts and images it uses.
"""

import json
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


def annotate(body, notes):
    """Mark AI-written prose for rewriting and drop a facts-to-keep note under each heading."""
    note = lambda key, cls="rw-note": f'<aside class="{cls}">{notes[key]}</aside>' if key in notes else ""
    body = re.sub(r'<p><img ([^>]*src="assets/img/(?:argus-latency|coodie-sequential)[^>]*)>',
                  r'<p class="keep"><img \1>', body)  # charts from real data: keep
    body = body.replace("<p><img ", '<p class="ai-img"><img ')  # generated illustrations
    body = re.sub(r"<(p|li|h2)(?=[ >])(?![^>]*class=)", r'<\1 class="rw"', body)
    body = body.replace("<blockquote>", '<blockquote class="rw">')
    body = re.sub(r'(<h2 class="rw" id="([^"]+)">.*?</h2>)', lambda m: m.group(1) + note(m.group(2)), body)
    first = body.find('<p class="ai-img">')
    body = body[:first] + note("_top", "rw-note rw-top") + note("_images", "rw-note rw-img") + body[first:]
    intro = body.find('<p class="rw">')
    return body[:intro] + note("_intro") + body[intro:]


notes_file = REPO / "_preview" / "notes" / (Path(POST).stem + ".json")
annotated = bool(os.environ.get("ANNOTATE")) and notes_file.exists()
if annotated:  # only the post itself, not the site menu and footer
    start = body.index('<div class="bd">'); end = body.index('<div class="meta">', start)
    body = body[:start] + annotate(body[start:end], json.loads(notes_file.read_text())) + body[end:]

banner = (
    '<p class="draft-banner">Draft preview, not published yet. '
    + ("Yellow: rewrite in your own words. Green: real data, keep." if annotated else "Numbers and quotes may still change.")
    + "</p>"
)
page = f"""<title>{title}</title>
<link rel="stylesheet" href="{THEME}/css/style.css">
<style>
  :root {{ color-scheme: light; }}
  body {{ background: #999999; }}
  .draft-banner {{ margin: 0; padding: 8px 16px; background: #fdf3c8; color: #3a3220;
    font: 14px/1.4 "Ubuntu Mono", monospace; text-align: center; }}
  pre, .highlight {{ overflow-x: auto; }}
  .rw {{ background: #fff6d6; box-shadow: -6px 0 0 #e0a800; }}
  .ai-img img {{ outline: 4px dashed #e0a800; }}
  .keep {{ box-shadow: -6px 0 0 #2f9e8f; }}
  .rw-note {{ display: block; margin: 0.6em 0 1.2em; padding: 10px 14px; border: 1px solid #e0a800;
    border-radius: 6px; background: #fffdf3; color: #3a3220; font-size: 0.85em; line-height: 1.5; }}
  .rw-note::before {{ content: "Rewrite note: "; font-weight: bold; }}
  .rw-top::before {{ content: "How to read the marks: "; }}
  .rw-img::before {{ content: "Images: "; }}
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
