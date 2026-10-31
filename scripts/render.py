#!/usr/bin/env python3
"""Turns data/stats.json and the active season into the SVG art and README.md.

Standard library only. Reads aggregates, never the GitHub API, so it can run
without any token and on any season:  python3 scripts/render.py [--season dark]
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, datetime, timezone
import hashlib
from html import escape
import json
import math
from pathlib import Path

from glyphs import Art, measure, wrap

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets' / 'art'
PLATES = ROOT / 'assets' / 'plates'
ICONS = json.loads((ROOT / 'data' / 'icons.json').read_text(encoding='utf-8'))
COLORS = json.loads((ROOT / 'data' / 'lang_colors.json').read_text(encoding='utf-8'))

DISPLAY, HEAD, FIGURE, TEXT, STRONG = 'bd', 'bm', 'bt', 'j4', 'j5'
DESKTOP, PHONE = 1280, 720  # PHONE is the narrow art: GitHub's sidebar shrinks the column below about 1100 px
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
SCOPES = {
    'global': ('Everything', 'Every repository: public and private, together.'),
    'public': ('Public', 'Only what anyone can open.'),
    'private': ('Private', 'Scrambled traffic: language totals, nothing else.'),
    'contributions': ('Contributions', "Lines changed in other people's public repositories."),
}


def active_season(config: dict, today: date, forced: str | None = None) -> str:
    chosen = forced or config['season']
    if chosen != 'auto':
        return chosen
    stamp = today.strftime('%m-%d')
    for name, season in config['seasons'].items():
        if 'from' not in season:
            continue
        start, end = season['from'], season['to']
        # a season may cross New Year: from 12-20 to 01-05
        if start <= stamp <= end or (start > end and (stamp >= start or stamp <= end)):
            return name
    return 'dark'


def plate(name: str) -> str:
    return 'data:image/jpeg;base64,' + base64.b64encode((PLATES / name).read_bytes()).decode()


def day_text(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


def luminance(color: str) -> float:
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return .2126 * r + .7152 * g + .0722 * b


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + .05) / (low + .05)


def legible(color: str, ground: str, target: float = 4.5) -> str:
    """Linguist colours stay identifiable but are lifted until they read on the ground."""
    channels = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    current = color
    for step in range(1, 21):
        if contrast(current, ground) >= target:
            break
        current = '#' + ''.join(f'{round(c + (255 - c) * step / 20):02x}' for c in channels)
    return current


# --- The message: a real one-time pad over a straddling checkerboard ---------

BOARD_TOP = 'ATONESIR'  # sit in single digits 0-7
BOARD_8 = 'BCDFGHJKLM'
BOARD_9 = 'PQUVWXYZ./'


def encode_text(text: str) -> str:
    out = []
    for ch in text.replace(' ', '/'):
        if ch in BOARD_TOP:
            out.append(str(BOARD_TOP.index(ch)))
        elif ch in BOARD_8:
            out.append('8' + str(BOARD_8.index(ch)))
        else:
            out.append('9' + str(BOARD_9.index(ch)))
    return ''.join(out)


def decode_digits(digits: str) -> str:
    out, i = [], 0
    while i < len(digits):
        d = digits[i]
        if d in '89':
            if i + 1 >= len(digits):
                break
            out.append((BOARD_8 if d == '8' else BOARD_9)[int(digits[i + 1])])
            i += 2
        else:
            out.append(BOARD_TOP[int(d)])
            i += 1
    return ''.join(out).replace('/', ' ')


def groups(digits: str) -> str:
    return ' '.join(digits[i:i + 5] for i in range(0, len(digits), 5))


WORDS = 'ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE'.split()


def message(season: dict, heard: int, stamp: str) -> dict:
    text = f"{season['message']} HEARD {' '.join(WORDS[int(d)] for d in str(heard))} THIS WEEK"
    plain = encode_text(text)
    plain += '4' * (-len(plain) % 5)  # padded with E so groups stay complete
    pad, seed = '', f'{stamp}:{text}'
    while len(pad) < len(plain):
        seed = hashlib.sha256(seed.encode()).hexdigest()
        pad += ''.join(c for c in seed if c.isdigit())
    pad = pad[:len(plain)]
    cipher = ''.join(str((int(p) + int(k)) % 10) for p, k in zip(plain, pad))
    return {'text': text, 'cipher': cipher, 'pad': pad}


def decrypt(cipher: str, pad: str) -> str:
    return decode_digits(''.join(str((int(c) - int(k)) % 10) for c, k in zip(cipher, pad)))


# --- Shared calendar reading --------------------------------------------------

def weeks_of(days: list) -> list[list]:
    """Rows of up to 7 [date, count], split on Sunday as GitHub's calendar does."""
    weeks, week = [], []
    for iso, count in days:
        if date.fromisoformat(iso).isoweekday() == 7 and week:
            weeks.append(week)
            week = []
        week.append([iso, count])
    return weeks + [week] if week else weeks


def month_marks(weeks: list[list]) -> list[tuple[int, str]]:
    marks, seen = [], None
    for i, week in enumerate(weeks):
        month = week[0][0][:7]
        if month != seen:
            if seen is not None and i < len(weeks) - 2:
                marks.append((i, MONTHS[int(month[5:]) - 1]))
            seen = month
    return marks


def last_seven(days: list) -> int:
    return sum(count for _, count in days[-7:])


def figure_colour(count: int, season: dict) -> str:
    if count == 0:
        return season['zero']
    return season['accent'] if count >= 9 else season['ink'] if count >= 4 else season['ink2']


# --- Art ---------------------------------------------------------------------

def qsl_card(art: Art, x: float, y: float, w: float, h: float, season: dict, stats: dict, phone: bool) -> None:
    """The reception card, after the form real QSL cards used."""
    paper, ink = season['card'], season['card_ink']
    k = w / 400
    margin = 18 * k
    art.rect(x, y, w, h, paper)
    art.add(f'<path d="M{x + margin:.1f} {y + margin:.1f}h{w - 2 * margin:.1f}v{h - 2 * margin:.1f}h-{w - 2 * margin:.1f}z" '
            f'fill="none" stroke="{ink}" stroke-width="{1.6 * k:.2f}"/>')
    art.run(STRONG, 'Confirming reception', 21 * k, x + w / 2, y + 48 * k, ink, 'middle')
    art.run(HEAD, 'RX3CARD', 66 * k, x + w / 2, y + 122 * k, ink, 'middle')
    top = stats['languages']['global'][0]['name']
    rows = (('Date', day_text(stats['calendar']['days'][-1][0])),
            ('Heard', f"{stats['calendar']['total']:,} in 12 months"),
            ('Strongest', top))
    for i, (label, value) in enumerate(rows):
        yy = y + (156 + i * 26) * k
        art.run(TEXT, label, 21 * k, x + 36 * k, yy, ink)
        art.run(STRONG, value, 21 * k, x + w - 36 * k, yy, ink, 'end')


def opening(stats: dict, season: dict, phone: bool) -> Art:
    days = stats['calendar']['days']
    alt = (f"rx3card {season['claim']}. {season['sentence']} A radio dish at dusk with one small figure on a lift. "
           f"A reception card confirms {stats['calendar']['total']:,} heard in 12 months up to {day_text(days[-1][0])}, "
           f"strongest in {stats['languages']['global'][0]['name']}.")
    w = PHONE if phone else DESKTOP
    h = 1268 if phone else 700
    art = Art(w, h, alt, season['ground'])
    art.css.append('.dusk{animation:dusk 48s ease-in-out infinite}@keyframes dusk{0%,100%{opacity:0}50%{opacity:.5}}'
                   '.lamp{animation:lamp 5s ease-in-out infinite}@keyframes lamp{0%,62%,100%{opacity:.18}70%,78%{opacity:1}}')
    name = f"dish-{season['plate']}{'-phone' if phone else ''}.jpg"
    art.add(f'<image href="{plate(name)}" width="{w}" height="{930 if phone else h}" preserveAspectRatio="xMidYMin slice"/>')
    art.add(f'<rect class="dusk" width="{w}" height="{930 if phone else h}" fill="{season["ground"]}" opacity="0"/>')
    if phone:
        art.add(f'<circle class="lamp" cx="411" cy="280" r="5" fill="{season["accent"]}"/>')
        art.run(HEAD, 'rx3card', 118, 36, 660, season['ink'])
        art.run(HEAD, season['claim'], 70, 36, 746, season['ink'])
        art.run(TEXT, season['sentence'], 34, 36, 812, season['ink'])
        qsl_card(art, 36, 856, 648, 376, season, stats, phone)
    else:
        art.add(f'<circle class="lamp" cx="897" cy="343" r="4" fill="{season["accent"]}"/>')
        art.run(HEAD, 'rx3card', 124, 56, 226, season['ink'])
        art.run(HEAD, season['claim'], 64, 56, 306, season['ink'])
        art.run(TEXT, season['sentence'], 30, 56, 366, season['ink'])
        qsl_card(art, 56, 432, 420, 244, season, stats, phone)
    return art


def transmission(stats: dict, season: dict, phone: bool) -> Art:
    days = stats['calendar']['days']
    weeks = weeks_of(days)
    total = stats['calendar']['total']
    alt = (f"A year of real GitHub contributions set as figures, one per day, {total:,} in all, "
           f"ending {day_text(days[-1][0])}. The figures arrive week by week.")
    per_week, period = .12, 18
    css = f'.w{{animation:rx {period}s linear infinite}}@keyframes rx{{0%{{opacity:.14}}1.4%{{opacity:1}}100%{{opacity:1}}}}'
    if phone:
        per_row, group_w, row_h = 4, 164, 46
        rows = math.ceil(len(weeks) / per_row)
        h = 262 + rows * row_h + 96
        art = Art(PHONE, h, alt, season['field'])
        art.css.append(css)
        art.run(HEAD, 'Twelve months,', 62, 36, 92, season['ink'])
        art.run(HEAD, 'as received', 62, 36, 160, season['ink'])
        art.lines(TEXT, 'One figure, one day. Each group is a week. Nine means nine or more.', 28, 36, 214, 640, season['ink2'])
        for i, week in enumerate(weeks):
            gx, gy = 36 + (i % per_row) * group_w, 316 + (i // per_row) * row_h
            art.add(f'<g class="w" style="animation-delay:{i * per_week:.2f}s">')
            for d, (_, count) in enumerate(week):
                art.run(FIGURE, str(min(count, 9)), 27, gx + d * 19, gy, figure_colour(count, season))
            art.add('</g>')
        art.run(TEXT, f'{total:,} heard. Last figure {day_text(days[-1][0])}.', 28, 36, h - 40, season['ink'])
        return art
    art = Art(DESKTOP, 512, alt, season['field'])
    x0, cell, row, y0 = 56, (DESKTOP - 112) / len(weeks), 36, 216
    art.css.append(css + f'.scan{{animation:sc {period}s steps({len(weeks)}) infinite}}@keyframes sc{{0%{{opacity:.28;transform:translateX(0)}}{100 * per_week * len(weeks) / period:.1f}%'
                         f'{{opacity:.28;transform:translateX({cell * len(weeks):.0f}px)}}{100 * per_week * len(weeks) / period + .1:.1f}%,100%{{opacity:0}}}}')
    art.run(HEAD, 'Twelve months, as received', 50, 538, 100, season['ink'])
    art.lines(TEXT, 'One figure, one day. Each column is a week. Nine means nine or more.', 25, 56, 76, 420, season['ink2'])
    for i, label in month_marks(weeks):
        art.run(TEXT, label, 23, x0 + i * cell + 3, y0 - 34, season['ink2'])
    art.add(f'<rect class="scan" x="{x0}" y="{y0 - 22}" width="{cell:.1f}" height="{7 * row + 8}" fill="{season["accent"]}" opacity="0"/>')
    for i, week in enumerate(weeks):
        art.add(f'<g class="w" style="animation-delay:{i * per_week:.2f}s">')
        offset = date.fromisoformat(week[0][0]).isoweekday() % 7
        for d, (_, count) in enumerate(week):
            art.run(FIGURE, str(min(count, 9)), 29, x0 + i * cell + cell / 2, y0 + (d + offset) * row,
                    figure_colour(count, season), 'middle')
        art.add('</g>')
    art.run(TEXT, f'{total:,} heard in the last twelve months', 25, 56, 486, season['ink'])
    art.run(TEXT, f'Last figure {day_text(days[-1][0])}', 25, 1224, 486, season['ink'], 'end')
    return art


def array(stats: dict, season: dict, phone: bool) -> Art:
    """The calendar as a field of masts in perspective; height is the square root of the count."""
    days = stats['calendar']['days']
    weeks = weeks_of(days)
    peak_date, peak = max(days, key=lambda d: d[1])
    alt = (f'A three-dimensional field of masts, one for each day of the last year. '
           f'The tallest stands for {peak} contributions on {day_text(peak_date)}.')
    w = PHONE if phone else DESKTOP
    h = 900 if phone else 690
    art = Art(w, h, alt, season['ground'])
    art.css.append('.peak{animation:lamp 5s ease-in-out infinite}@keyframes lamp{0%,62%,100%{opacity:.25}70%,78%{opacity:1}}')
    horizon = 540 if phone else 434
    plate_h = w * 376 / 1280
    art.add(f'<image href="{plate("array-" + season["plate"] + ".jpg")}" y="{horizon - plate_h + 8:.0f}" width="{w}" height="{plate_h:.0f}" opacity=".72"/>')
    if phone:
        art.run(HEAD, 'One mast for', 62, 36, 92, season['ink'])
        art.run(HEAD, 'every day', 62, 36, 160, season['ink'])
        art.run(TEXT, f'Tallest: {peak} on {day_text(peak_date)}', 30, 36, 214, season['accent'])
        art.run(TEXT, 'Height is the square root of the count.', 26, 36, 256, season['ink2'])
    else:
        art.run(HEAD, 'One mast for every day', 50, 538, 92, season['ink'])
        art.run(TEXT, f'Tallest: {peak} on {day_text(peak_date)}', 25, 56, 76, season['accent'])
        art.run(TEXT, 'Height is the square root of the count.', 25, 56, 110, season['ink2'])
    near, far = h - 30, horizon + 10
    margin_near, margin_far = (10, 150) if phone else (24, 300)
    scale_far = (w - 2 * margin_far) / (w - 2 * margin_near)
    tallest = (300 if phone else 270) / math.sqrt(max(peak, 1))
    tip = None
    span = len(weeks)
    colours = (season['ink2'], season['ink'], season['accent'])
    # far rows first, so nearer masts paint over them
    for row in range(6, -1, -1):
        depth = (1 - row / 6) ** 2.1  # 0 far, 1 near; rows crowd toward the horizon
        s = scale_far + (1 - scale_far) * depth
        ground = far + (near - far) * depth
        stroke = 1 + 2.6 * s ** 2
        arm = 3 + 10 * s ** 2
        art.add(f'<path d="M{w / 2 - (w - 2 * margin_near) * s / 2:.1f} {ground:.1f}h{(w - 2 * margin_near) * s:.1f}" '
                f'stroke="{season["dim"]}" stroke-width="{.6 + s:.1f}" fill="none"/>')
        paths = ([], [], [])
        for i, week in enumerate(weeks):
            offset = date.fromisoformat(week[0][0]).isoweekday() % 7
            if row < offset or row - offset >= len(week):
                continue
            iso, count = week[row - offset]
            if count == 0:
                continue
            x = w / 2 + (i - span / 2) / span * (w - 2 * margin_near) * s
            top = ground - tallest * math.sqrt(count) * s
            band = 2 if count >= 15 else 1 if count >= 4 else 0
            paths[band].append(f'M{x:.1f} {ground:.1f}V{top:.1f}M{x - arm / 2:.1f} {top:.1f}h{arm:.1f}')
            if iso == peak_date:
                tip = (x, top)
        for segments, colour in zip(paths, colours):
            art.add(f'<path d="{"".join(segments)}" stroke="{colour}" stroke-width="{stroke:.1f}" fill="none"/>')
    if tip:
        art.add(f'<circle class="peak" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="7" fill="{season["accent"]}"/>')
    return art


def icon(art: Art, name: str, x: float, y: float, size: float, colour: str, ground: str) -> None:
    if name in ICONS:
        art.add(f'<path d="{ICONS[name]}" transform="translate({x:.1f} {y:.1f}) scale({size / 24:.3f})" fill="{colour}"/>')
    else:  # no icon exists for this language: its initials, in the same tile
        art.rect(x, y, size, size, colour)
        art.run(STRONG, name[:2], size * .56, x + size / 2, y + size * .72, ground, 'middle')


def bands(stats: dict, season: dict, scope: str, phone: bool) -> Art:
    rows = stats['languages'][scope]
    title, note = SCOPES[scope]
    listing = ', '.join(f"{r['rank']}. {r['name']} {r['pct']}%" for r in rows) or 'nothing measured yet'
    alt = f'Language ranking, {title}. {note} {listing}.'
    ground = season['field'] if scope == 'global' else season['ground']
    w = PHONE if phone else DESKTOP
    margin = 36 if phone else 56
    columns = 1 if phone else 2
    row_h = 66 if phone else 54
    per_col = len(rows) if phone else math.ceil(len(rows) / 2)
    has_bar = len(rows) > 1  # one language would fill the bar and say nothing
    head = (300 if phone else 214) if has_bar else (220 if phone else 150)
    h = head + max(per_col, 1) * row_h + (96 if phone else 74)
    art = Art(w, h, alt, ground)
    if scope == 'global':
        if phone:
            art.run(HEAD, 'Where the', 62, margin, 92, season['ink'])
            art.run(HEAD, 'traffic sits', 62, margin, 160, season['ink'])
        else:
            art.run(HEAD, 'Where the traffic sits', 50, 538, 92, season['ink'])
            art.lines(TEXT, note, 25, 56, 76, 420, season['ink2'])
    else:
        art.run(HEAD, title, 62 if phone else 50, margin if phone else 538, 92, season['ink'])
        if not phone:
            art.lines(TEXT, note, 25, 56, 76, 420, season['ink2'])
    if phone:
        art.lines(TEXT, note, 26, margin, 150 if scope != 'global' else 206, w - 2 * margin, season['ink2'])
    bar_y = head - 66
    x = margin
    full = w - 2 * margin
    for r in rows if has_bar else []:
        seg = full * r['pct'] / 100
        art.rect(x, bar_y, max(seg - 1.5, 1), 26, legible(COLORS.get(r['name'], season['ink2']), ground, 3))
        x += seg
    top = rows[0]['pct'] if rows else 1
    col_w = (w - 2 * margin - (48 if columns == 2 else 0)) / columns
    for i, r in enumerate(rows):
        col, line = (0, i) if phone else (i // per_col, i % per_col)
        x0 = margin + col * (col_w + 48)
        y = head + line * row_h + 22
        colour = legible(COLORS.get(r['name'], season['ink2']), ground)
        art.run(FIGURE, str(r['rank']), 28 if phone else 26, x0 + 30, y + 10, season['ink2'], 'end')
        icon(art, r['name'], x0 + 44, y - 16, 30 if phone else 28, colour, ground)
        art.run(STRONG, r['name'], 30 if phone else 26, x0 + 90, y + 10, season['ink'])
        pct = '<0.1%' if r['pct'] < .1 else f"{r['pct']}%"
        art.run(FIGURE, pct, 30 if phone else 27, x0 + col_w, y + 10, season['ink'], 'end')
        bar_x = x0 + (300 if phone else 262)
        bar_w = (col_w - (300 if phone else 262) - 124) * r['pct'] / top
        art.rect(bar_x, y - 2, max(bar_w, 2), 8, colour)
    footer = {'global': 'Bytes detected by GitHub Linguist. Not time spent, not skill.',
              'public': 'Bytes detected by GitHub Linguist in public repositories.',
              'private': 'Aggregate percentages only. No names, no links, no counts.'}.get(scope)
    if scope == 'contributions':
        cov = stats.get('contributions_coverage')
        footer = (f"{cov['lines']} lines from {cov['merged_prs']} merged PR, "
                  f"{cov['direct_commits']} direct commits, {cov['repositories']} repositories."
                  if cov else 'Could not be measured on the last run. Nothing is guessed.')
    art.lines(TEXT, footer, 25, margin, h - (58 if phone and len(footer) > 44 else 30), full, season['ink2'], 1.3)
    return art


def project_mark(art: Art, item: dict, x: float, y: float, w: float, h: float, season: dict, phone: bool) -> None:
    """Each project is shown by its own material, never by a shared card."""
    if 'minimap' in item:  # the real shape of a real source file, with one line found
        lines, lit = item['minimap']['lines'], item['minimap']['lit']
        step, scale = w / len(lines), h / max(max(lines), 1)
        for i, length in enumerate(lines):
            colour = season['accent'] if i == lit else season['dim']
            art.rect(x + i * step, y + h - length * scale, max(step - 1.2, 1), max(length * scale, 2), colour)
    elif 'race' in item:  # the timings its README reports, drawn to scale
        slowest = max(ms for _, ms in item['race'])
        for i, (name, ms) in enumerate(item['race']):
            top = y + 8 + i * h / 2
            colour = season['accent'] if i == 0 else season['dim']
            art.run(TEXT, f'{name}, {ms} ms', 26, x, top + 24, season['ink'])
            art.rect(x, top + 38, max(w * ms / slowest, 4), 14, colour)
    elif 'manifest' in item:
        for i, name in enumerate(item['manifest']):
            art.run(TEXT, name, 28 if phone else 27, x + (i % 2) * w / 2, y + 34 + (i // 2) * 46,
                    season['accent'] if i == 0 else season['ink'])
    elif 'token' in item:
        token, per = item['token'], 40 if phone else 70
        for i in range(0, math.ceil(len(token) / per)):
            art.run(TEXT, token[i * per:(i + 1) * per], 26, x, y + 28 + i * 40, season['ink2'])


def follow(art: Art, info: str, size: float, x: float, y: float, season: dict) -> None:
    """The metadata line, closed by the arrow that says the whole panel is a link."""
    end = x + art.run(TEXT, info, size, x, y, season['ink2']) + 16
    art.add(f'<path d="M{end:.1f} {y - 8:.1f}h24m-8 -7l8 7l-8 7" fill="none" stroke="{season["accent"]}" stroke-width="2.4"/>')


def project(item: dict, stats: dict, season: dict, phone: bool) -> Art:
    meta = stats['projects'].get(item['repo'], {})
    alt = f"{item['name']}: {item['line']} Public repository, opens on GitHub."
    info = ' · '.join(x for x in (meta.get('language'), f"last touched {day_text(meta['pushed'])}" if meta.get('pushed') else None) if x)
    if phone:
        margin, width = 36, PHONE - 72
        size = {'token': 180, 'manifest': 150}.get(next((k for k in ('token', 'manifest') if k in item), ''), 130)
        used = len(wrap(TEXT, item['line'], 30, width)) * 40
        top = 150 + used + 40
        h = top + 30 + size + 40
        art = Art(PHONE, h, alt, season['ground'])
        art.run(HEAD, item['name'], 54, margin, 92, season['ink'])
        art.lines(TEXT, item['line'], 30, margin, 150, width, season['ink'], 1.33)
        follow(art, info, 25, margin, top, season)
        project_mark(art, item, margin, top + 30, width, size, season, True)
        return art
    margin, axis, right = 56, 538, DESKTOP - 56
    if 'minimap' in item or 'token' in item:  # the material first, full width, words under it
        mark_h = 112 if 'minimap' in item else 84
        art = Art(DESKTOP, mark_h + 180, alt, season['ground'])
        project_mark(art, item, margin, 28, right - margin, mark_h, season, False)
        base = mark_h + 28 + 92
        art.run(HEAD, item['name'], 44, margin, base, season['ink'])
        art.run(TEXT, item['line'], 27, axis, base - 26, season['ink'])
        follow(art, info, 23, axis, base + 12, season)
        return art
    art = Art(DESKTOP, 228, alt, season['ground'])
    text_x = axis if 'race' in item else margin
    art.run(HEAD, item['name'], 44, text_x, 92, season['ink'])
    art.run(TEXT, item['line'], 27, text_x, 140, season['ink'])
    follow(art, info, 23, text_x, 180, season)
    if 'race' in item:
        project_mark(art, item, margin, 26, 454, 176, season, False)
    else:
        project_mark(art, item, axis + 122, 42, right - axis - 122, 150, season, False)
    return art


def message_art(msg: dict, season: dict, phone: bool) -> Art:
    cipher, pad = [groups(msg[k]).split() for k in ('cipher', 'pad')]
    alt = (f"A coded message. Figures: {' '.join(cipher)}. Pad: {' '.join(pad)}. Subtract each pad figure from the one "
           f"above it, without borrowing, then read the result on the board printed here.")
    w = PHONE if phone else DESKTOP
    margin, per = (36, 5) if phone else (56, 9)
    cell = (w - 2 * margin) / per
    rows = math.ceil(len(cipher) / per)
    top = 262 if phone else 172
    board_y = top + rows * 96 + 44
    step = 58 if phone else 46
    art = Art(w, board_y + step * 3 + (150 if phone else 100), alt, season['field'])
    note = 'Subtract each lower figure from the one above it, without borrowing.'
    if phone:
        art.run(HEAD, "Tonight's message", 56, margin, 92, season['ink'])
        art.lines(TEXT, note, 28, margin, 152, w - 2 * margin, season['ink2'])
    else:
        art.run(HEAD, "Tonight's message", 50, 538, 92, season['ink'])
        art.lines(TEXT, note, 25, margin, 76, 420, season['ink2'])
    for i, (c, k) in enumerate(zip(cipher, pad)):
        x, y = margin + (i % per) * cell, top + (i // per) * 96
        art.run(FIGURE, c, 34, x, y, season['ink'], track=.06)
        art.run(FIGURE, k, 34, x, y + 42, season['ink2'], track=.06)
    width = (w - 2 * margin) / 11
    for i in range(10):
        art.run(FIGURE, str(i), 28, margin + width * (i + 1.5), board_y, season['ink2'], 'middle')
    for r, (label, letters) in enumerate((('', BOARD_TOP), ('8', BOARD_8), ('9', BOARD_9))):
        y = board_y + step * (r + 1)
        art.run(FIGURE, label, 28, margin + width / 2, y, season['ink2'], 'middle')
        for i, ch in enumerate(letters):
            shown = 'sp' if ch == '/' else ch
            art.run(STRONG, shown, 28, margin + width * (i + 1.5), y, season['ink'] if r else season['accent'], 'middle')
    art.lines(TEXT, 'Then read it here: orange letters stand alone, 8 and 9 take the next figure with them.', 25, margin,
              board_y + step * 3 + 62, w - 2 * margin, season['ink2'])
    return art


def closing(stats: dict, season: dict, phone: bool) -> Art:
    days = stats['calendar']['days']
    alt = f"rx3card. {season['close']} 73. Last reception {day_text(days[-1][0])}."
    w = PHONE if phone else DESKTOP
    h = 520 if phone else 470
    art = Art(w, h, alt, season['card'])
    ink = season['card_ink']
    margin = 36 if phone else 56
    bottom = art.lines(STRONG, season['close'], 34, margin, 72, w - 2 * margin - 160, ink)
    art.run(TEXT, f'Last reception {day_text(days[-1][0])}', 28 if phone else 26, margin, bottom + 4, ink)
    art.run(HEAD, '73', 84 if phone else 72, w - margin, 100, ink, 'end')
    size = (w - 2 * margin) / measure(DISPLAY, 'rx3card', 1)
    art.run(DISPLAY, 'rx3card', size, margin, h - 18, ink)
    return art


def write_art(name: str, desktop: Art, phone: Art, out: Path) -> tuple[str, str]:
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{name}.svg').write_text(desktop.svg(), encoding='utf-8')
    (out / f'{name}-phone.svg').write_text(phone.svg(), encoding='utf-8')
    return name, desktop.title


def picture(name: str, alt: str, base: str) -> str:
    return (f'<picture><source media="(max-width: 1100px)" srcset="{base}/{name}-phone.svg">'
            f'<img src="{base}/{name}.svg" width="100%" alt="{escape(alt, quote=True)}"></picture>')


def readme(stats: dict, season: dict, config: dict, shown: dict, base: str) -> str:
    def details(scope: str) -> str:
        rows = stats['languages'][scope]
        title = SCOPES[scope][0]
        lead = f"{rows[0]['name']} leads, {len(rows)} in all" if len(rows) > 1 else (rows[0]['name'] if rows else 'nothing measured')
        return (f'<details>\n<summary><b>{title}</b> · {escape(lead)}</summary>\n<br>\n\n'
                f'{picture("bands-" + scope, shown["bands-" + scope], base)}\n\n</details>\n')

    projects = '\n\n'.join(
        f'<a href="https://github.com/rx3card/{p["repo"]}">{picture("project-" + p["repo"].lower(), shown["project-" + p["repo"].lower()], base)}</a>'
        for p in config['projects'])
    return f'''<!-- Generated by scripts/render.py. Edit profile.config.json or scripts, not this file. -->
{picture('opening', shown['opening'], base)}

{picture('transmission', shown['transmission'], base)}

<details>
<summary><b>Tonight's message</b> · it can be read by hand</summary>
<br>

{picture('message', shown['message'], base)}

</details>

{picture('array', shown['array'], base)}

{picture('bands-global', shown['bands-global'], base)}

{details('public')}
{details('private')}
{details('contributions')}

{projects}

{picture('closing', shown['closing'], base)}

<sub>Dish: Gar Lunney, 1960, public domain. Duga array: Ingmar Runge, CC BY 3.0, recoloured. Type: Bodoni Moda and Jost, SIL OFL. <a href="./ASSET_SOURCES.md">Sources</a> · <a href="./DATA_METHODOLOGY.md">How the figures are made</a></sub>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--season')
    parser.add_argument('--out', default=str(ART))
    parser.add_argument('--readme', default=str(ROOT / 'README.md'))
    parser.add_argument('--base', default='./assets/art')
    args = parser.parse_args()
    config = json.loads((ROOT / 'profile.config.json').read_text(encoding='utf-8'))
    stats = json.loads((ROOT / 'data' / 'stats.json').read_text(encoding='utf-8'))
    today = datetime.now(timezone.utc).date()
    season = config['seasons'][active_season(config, today, args.season)]
    out = Path(args.out)
    shown = {}
    for name, build in (('opening', opening), ('transmission', transmission), ('array', array), ('closing', closing)):
        key, alt = write_art(name, build(stats, season, False), build(stats, season, True), out)
        shown[key] = alt
    for scope in SCOPES:
        key, alt = write_art(f'bands-{scope}', bands(stats, season, scope, False), bands(stats, season, scope, True), out)
        shown[key] = alt
    for item in config['projects']:
        key, alt = write_art(f"project-{item['repo'].lower()}", project(item, stats, season, False), project(item, stats, season, True), out)
        shown[key] = alt
    msg = message(season, last_seven(stats['calendar']['days']), stats['calendar']['days'][-1][0])
    key, alt = write_art('message', message_art(msg, season, False), message_art(msg, season, True), out)
    shown[key] = alt
    Path(args.readme).write_text(readme(stats, season, config, shown, args.base), encoding='utf-8')
    print(f'Rendered {len(shown)} images.')


if __name__ == '__main__':
    main()
