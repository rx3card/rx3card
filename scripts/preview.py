#!/usr/bin/env python3
"""Builds previews/index.html from HTML rendered by GitHub's own Markdown API.

usage: gh api markdown -f mode=gfm -f context=rx3card/rx3card -F text=@README.md > /tmp/out.html
       python3 scripts/preview.py /tmp/out.html
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PENDING = 'Nothing pending: every picture here is final. Generated images in ASSETS_TO_GENERATE.md are optional.'


def main(source: str) -> None:
    body = Path(source).read_text(encoding='utf-8')
    body = re.sub(r'(src|srcset|href)="(?:\./|https://raw\.githubusercontent\.com/rx3card/rx3card/[^/]+/|/rx3card/rx3card/(?:raw|blob)/[^/]+/)(assets/[^"]+)"',
                  r'\1="../\2"', body)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>rx3card preview</title>
<style>:root{{color-scheme:dark}}body{{margin:0;background:#0d1117;color:#e6edf3;font:16px/1.5 -apple-system,"Segoe UI",sans-serif}}
main{{max-width:830px;margin:0 auto;padding:24px 16px}}img{{max-width:100%}}p{{margin:0 0 16px}}pre{{background:#151b23;padding:16px;overflow:auto}}
table{{border-collapse:collapse;margin-bottom:16px}}td,th{{border:1px solid #3d444d;padding:6px 13px}}details{{margin-bottom:16px}}a{{color:#4493f8}}
small{{color:#9198a1}}</style></head><body><main>
<h1 hidden>rx3card preview</h1>
{body}
<p><small>Local preview, rendered from GitHub's own Markdown API. {PENDING}</small></p>
</main></body></html>'''
    (ROOT / 'previews').mkdir(exist_ok=True)
    (ROOT / 'previews' / 'index.html').write_text(page, encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1])
