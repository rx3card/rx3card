"""Sets text as vector outlines so the art never depends on a visitor's fonts."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = json.loads((ROOT / 'data' / 'glyphs.json').read_text(encoding='utf-8'))


def measure(font: str, text: str, size: float, track: float = 0) -> float:
    f = FONTS[font]
    total, prev = 0.0, ''
    for ch in text:
        g = f['g'].get(ch) or f['g'][' ']
        total += g['a'] + f['k'].get(prev + ch, 0) + track * f['u']
        prev = ch
    return total * size / f['u']


def wrap(font: str, text: str, size: float, width: float) -> list[str]:
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if line and measure(font, trial, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line else lines


class Art:
    """One SVG image. Glyphs are defined once and reused."""

    def __init__(self, w: int, h: int, title: str, ground: str | None = None):
        self.w, self.h, self.title = w, h, title
        self.css: list[str] = []
        self.defs: dict[str, str] = {}
        self.body: list[str] = []
        if ground:
            self.rect(0, 0, w, h, ground)

    def add(self, markup: str) -> 'Art':
        self.body.append(markup)
        return self

    def rect(self, x, y, w, h, fill, extra: str = '') -> 'Art':
        return self.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>')

    def run(self, font: str, text: str, size: float, x: float, y: float, fill: str,
            anchor: str = 'start', track: float = 0, extra: str = '') -> float:
        """Draws one line and returns its width."""
        f = FONTS[font]
        width = measure(font, text, size, track)
        x0 = x - width if anchor == 'end' else x - width / 2 if anchor == 'middle' else x
        scale = size / f['u']
        pen, prev, uses = 0.0, '', []
        for ch in text:
            g = f['g'].get(ch) or f['g'][' ']
            pen += f['k'].get(prev + ch, 0)
            if g['d']:
                gid = f'{font}{ord(ch):x}'
                self.defs[gid] = g['d']
                uses.append(f'<use href="#{gid}" x="{pen:.0f}"/>')
            pen += g['a'] + track * f['u']
            prev = ch
        self.add(f'<g fill="{fill}" transform="translate({x0:.1f} {y:.1f}) scale({scale:.4f} {-scale:.4f})" {extra}>'
                 + ''.join(uses) + '</g>')
        return width

    def lines(self, font: str, text: str, size: float, x: float, y: float, width: float,
              fill: str, leading: float = 1.32, anchor: str = 'start') -> float:
        """Wraps text and returns the baseline after the last line."""
        for i, line in enumerate(wrap(font, text, size, width)):
            self.run(font, line, size, x, y + i * size * leading, fill, anchor)
            last = y + i * size * leading
        return last + size * leading

    def svg(self) -> str:
        defs = ''.join(f'<path id="{k}" d="{v}"/>' for k, v in self.defs.items())
        motion = '@media (prefers-reduced-motion:reduce){*{animation:none!important}}' if self.css else ''
        style = f'<style>{"".join(self.css)}{motion}</style>' if self.css else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-label="{escape(self.title, quote=True)}"><title>{escape(self.title)}</title>'
                f'{style}<defs>{defs}</defs>{"".join(self.body)}</svg>')
