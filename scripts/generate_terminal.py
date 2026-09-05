#!/usr/bin/env python3
"""
Generates assets/terminal.svg - a fake zsh session that types itself out.

Pure CSS + SMIL, no JavaScript: GitHub serves images through camo, which
strips scripts but keeps keyframes.

Edit LINES below, then run:  python scripts/generate_terminal.py
"""

from pathlib import Path

USER, HOST = "rx3card", "dev"

# kind: cmd | out | dim | hl | ok | warn | gap
LINES = [
    ("cmd",  "whoami"),
    ("out",  "Oscar Rojas"),
    ("dim",  "Full-Stack Developer · Ibagué, Tolima, Colombia"),
    ("gap",  ""),

    ("cmd",  "cat about.txt"),
    ("out",  "My goal is always to build complete systems that solve real problems."),
    ("gap",  ""),

    ("cmd",  "ls interests/"),
    ("hl",   "infrastructure    automation        databases"),
    ("hl",   "computer science  machine-learning  physics"),
    ("hl",   "philosophy        mathematics"),
    ("gap",  ""),

    ("cmd",  "systemctl status rx3card"),
    ("ok",   "● active (open to work) · remote, hybrid or on-site"),
    ("gap",  ""),

    ("cmd",  ""),   # trailing prompt + cursor
]

CHAR_W, LINE_H = 8.6, 23
PAD_X, TOP     = 24, 76
TYPE, PAUSE    = 0.042, 0.32

C = {
    "bg": "#0D1117", "chrome": "#161B22", "border": "#30363D",
    "user": "#3FB950", "path": "#58A6FF", "sign": "#8B949E",
    "cmd": "#E6EDF3", "out": "#ADBAC7", "dim": "#6E7681",
    "hl": "#79C0FF", "ok": "#3FB950", "warn": "#D29922", "title": "#6E7681",
}

PROMPT = f"{USER}@{HOST}"
PROMPT_W = (len(PROMPT) + len(":~$") + 1.6) * CHAR_W  # +1.6 = breathing room


def build() -> str:
    W = 880
    H = TOP + LINE_H * len(LINES) + 24
    css, body = [], []
    t = 0.5

    for i, (kind, text) in enumerate(LINES):
        y = TOP + i * LINE_H
        if kind == "gap":
            t += PAUSE * 0.5
            continue

        if kind == "cmd":
            body.append(
                f'<g class="s{i}" opacity="0">'
                f'<text x="{PAD_X}" y="{y}">'
                f'<tspan fill="{C["user"]}" font-weight="700">{PROMPT}</tspan>'
                f'<tspan fill="{C["sign"]}">:</tspan>'
                f'<tspan fill="{C["path"]}">~</tspan>'
                f'<tspan fill="{C["sign"]}">$</tspan>'
                f"</text></g>"
            )
            css.append(f".s{i}{{animation:show .01s linear {t:.2f}s forwards}}")
            x = PAD_X + PROMPT_W
        else:
            x = PAD_X + CHAR_W * 2

        if text:
            n = len(text)
            dur = n * TYPE
            body.append(
                f'<clipPath id="c{i}"><rect class="r{i}" x="{x:.0f}" y="{y-14}" '
                f'width="0" height="19"/></clipPath>'
                f'<text class="{kind}" x="{x:.0f}" y="{y}" clip-path="url(#c{i})">'
                f"{text}</text>"
            )
            css.append(
                f".r{i}{{animation:t{i} {dur:.2f}s steps({n}) {t:.2f}s both}}"
                f"@keyframes t{i}{{from{{width:0}}to{{width:{n*CHAR_W:.0f}px}}}}"
            )
            t += dur + (PAUSE if kind == "cmd" else PAUSE * 0.45)
        else:
            css.append(
                f".cursor{{animation:show .01s linear {t:.2f}s forwards,"
                f"blink 1.05s steps(1) {t:.2f}s infinite}}"
            )
            body.append(
                f'<rect class="cursor" x="{x:.0f}" y="{y-13}" width="9" '
                f'height="17" fill="{C["user"]}" opacity="0"/>'
            )

    style = (
        'text{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;'
        "font-size:14.5px}"
        f'.cmd{{fill:{C["cmd"]}}}.out{{fill:{C["out"]}}}.dim{{fill:{C["dim"]}}}'
        f'.hl{{fill:{C["hl"]}}}.ok{{fill:{C["ok"]}}}.warn{{fill:{C["warn"]}}}'
        f'.tt{{fill:{C["title"]};font-size:12.5px}}'
        "@keyframes show{to{opacity:1}}"
        "@keyframes blink{0%,50%{opacity:1}50.01%,100%{opacity:0}}"
        + "".join(css)
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="terminal session">\n'
        f"<style>{style}</style>\n"
        f'<rect width="{W}" height="{H}" rx="9" fill="{C["bg"]}" '
        f'stroke="{C["border"]}"/>\n'
        f'<path d="M0 9a9 9 0 0 1 9-9h{W-18}a9 9 0 0 1 9 9v35H0z" '
        f'fill="{C["chrome"]}"/>\n'
        f'<line x1="0" y1="44" x2="{W}" y2="44" stroke="{C["border"]}"/>\n'
        '<circle cx="22" cy="22" r="6" fill="#FF5F57"/>'
        '<circle cx="43" cy="22" r="6" fill="#FEBC2E"/>'
        '<circle cx="64" cy="22" r="6" fill="#28C840"/>\n'
        f'<text class="tt" x="{W//2}" y="27" text-anchor="middle">'
        f"{USER}@{HOST} \u2014 zsh</text>\n" + "\n".join(body) + "\n</svg>\n"
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}  ({len(LINES)} lines)")
