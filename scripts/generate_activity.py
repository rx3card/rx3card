#!/usr/bin/env python3
"""
Generates assets/activity.svg - a contribution heatmap built from the
GitHub GraphQL API. No third-party widgets: the data is fetched and the
SVG is drawn here.

Local run:
    export GITHUB_TOKEN=ghp_your_token   # needs no scopes for public data
    python scripts/generate_activity.py

In CI the workflow passes GITHUB_TOKEN automatically.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "rx3card"

# GitHub's own scale, tuned to sit on a #0D1117 card
EMPTY = "#161B22"
LEVELS = ["#0E4429", "#006D32", "#26A641", "#39D353"]

CELL, GAP = 11, 3
PAD_L, PAD_T = 34, 46
TEXT = "#7D8590"

QUERY = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch(token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USER}-profile-readme",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)

    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(count: int, peak: int) -> str:
    """Bucket a day's count into one of the four greens."""
    if count == 0:
        return EMPTY
    if peak <= 1:
        return LEVELS[3]
    # thresholds relative to this user's own busiest day
    for i, cut in enumerate((0.25, 0.5, 0.75)):
        if count <= max(1, round(peak * cut)):
            return LEVELS[i]
    return LEVELS[3]


def build(cal: dict) -> str:
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    peak = max(
        (d["contributionCount"] for w in weeks for d in w["contributionDays"]),
        default=0,
    )

    width = PAD_L + len(weeks) * (CELL + GAP) + 22
    height = PAD_T + 7 * (CELL + GAP) + 40

    cells, months, seen = [], [], set()

    for x, week in enumerate(weeks):
        for day in week["contributionDays"]:
            wd = day["weekday"]
            cx = PAD_L + x * (CELL + GAP)
            cy = PAD_T + wd * (CELL + GAP)
            n = day["contributionCount"]
            cells.append(
                f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{level(n, peak)}"><title>{day["date"]}: '
                f'{n} contribution{"" if n == 1 else "s"}</title></rect>'
            )

        first = week["contributionDays"][0]["date"]
        d = datetime.strptime(first, "%Y-%m-%d")
        if d.day <= 7 and d.strftime("%b") not in seen:
            seen.add(d.strftime("%b"))
            months.append(
                f'<text class="ax" x="{PAD_L + x * (CELL + GAP)}" y="{PAD_T - 8}">'
                f'{d.strftime("%b")}</text>'
            )

    days = "".join(
        f'<text class="ax" x="{PAD_L - 8}" y="{PAD_T + i * (CELL + GAP) + 9}" '
        f'text-anchor="end">{lbl}</text>'
        for i, lbl in ((1, "M"), (3, "W"), (5, "F"))
    )

    legend_x = width - 22 - 5 * (CELL + GAP) - 30
    legend_y = height - 22
    legend = (
        f'<text class="ax" x="{legend_x - 8}" y="{legend_y + 9}" '
        f'text-anchor="end">less</text>'
        + "".join(
            f'<rect x="{legend_x + i * (CELL + GAP)}" y="{legend_y}" '
            f'width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
            for i, c in enumerate([EMPTY] + LEVELS)
        )
        + f'<text class="ax" x="{legend_x + 5 * (CELL + GAP) + 4}" '
        f'y="{legend_y + 9}">more</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-label="{total} contributions in the last year">\n'
        "<style>"
        'text{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace}'
        f".ax{{font-size:10px;fill:{TEXT}}}"
        ".hd{font-size:13px;fill:#E6EDF3;font-weight:600}"
        f".sub{{font-size:11px;fill:{TEXT}}}"
        "</style>\n"
        f'<rect width="{width}" height="{height}" rx="9" fill="#0D1117" '
        'stroke="#21262D"/>\n'
        f'<text class="hd" x="{PAD_L - 8}" y="24">{total} contributions</text>\n'
        f'<text class="sub" x="{width - 22}" y="24" text-anchor="end">'
        "last 12 months</text>\n"
        + "".join(months) + days + "".join(cells) + legend + "\n</svg>\n"
    )


if __name__ == "__main__":
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        sys.exit("GITHUB_TOKEN is not set")

    out = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    cal = fetch(tok)
    out.write_text(build(cal), encoding="utf-8")
    print(f"wrote {out}  ({cal['totalContributions']} contributions)")
