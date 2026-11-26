"""コントリビューションのグラフ（assets/contrib-day.svg / contrib-night.svg）を作る。

    GITHUB_TOKEN=... python tools/contrib.py sogawa10     # GitHub から取得して生成
    python tools/contrib.py --sample data.json            # 手元のデータで試す

上段: 合計・最長連続・現在の連続・最多の日 / 中段: 週ごとの推移 / 下段: いつもの草（ヒートマップ）
標準ライブラリだけで動く（GitHub Actions で毎日実行）。
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

from glyphs import Glyphs
from theme import THEMES, card

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 440
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount contributionLevel weekday } }
      }
    }
  }
}"""


# ------------------------------------------------------------------ データ
def fetch(login: str, token: str) -> list[dict]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    weeks = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [
        {"date": d["date"], "count": d["contributionCount"],
         "level": LEVEL.get(d["contributionLevel"], 0), "weekday": d["weekday"]}
        for w in weeks for d in w["contributionDays"]
    ]


def fill_levels(days: list[dict]) -> None:
    """level / weekday が無いデータ（--sample）用。GitHub と同じく四分位で段階を付ける。"""
    nz = sorted(d["count"] for d in days if d["count"] > 0)
    q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)] if nz else [0, 0, 0]
    for d in days:
        d.setdefault("weekday", (dt.date.fromisoformat(d["date"]).weekday() + 1) % 7)
        if "level" not in d:
            c = d["count"]
            d["level"] = 0 if c == 0 else 1 + sum(c > x for x in q)


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    seq = days[:-1] if days and days[-1]["count"] == 0 else days  # 今日がまだ 0 なら昨日から
    current = 0
    for d in reversed(seq):
        if d["count"] == 0:
            break
        current += 1
    best = max(days, key=lambda d: d["count"])
    return {"total": total, "longest": longest, "current": current, "best": best}


def smooth(pts: list[tuple[float, float]]) -> str:
    """点列をなめらかな曲線（Catmull-Rom → ベジェ）にする。"""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


# ------------------------------------------------------------------ 描画
def build(days: list[dict], theme: str) -> str:
    t = THEMES[theme]
    g = Glyphs()
    st = stats(days)
    p = []

    cols: list[list[dict]] = []
    for d in days:
        if not cols or d["weekday"] == 0:
            cols.append([])
        cols[-1].append(d)
    n = len(cols)
    gx, gx2 = 84, W - 48
    step = (gx2 - gx) / n
    cell = step - 4

    # ---- 見出しと数字
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])
    p.append(g.text("Contributions", 48, 70, 26, "display", t["fg"], spacing=-0.4))
    rng = f"{MONTHS[first.month - 1]} {first.day}, {first.year}  —  {MONTHS[last.month - 1]} {last.day}, {last.year}"
    p.append(g.text(rng, 48, 96, 14, "text", t["sub"]))

    best = st["best"]
    bd = dt.date.fromisoformat(best["date"])
    items = [
        ("TOTAL", f"{st['total']:,}", ""),
        ("LONGEST STREAK", str(st["longest"]), "days"),
        ("CURRENT STREAK", str(st["current"]), "days"),
        ("BEST DAY", str(best["count"]), f"{MONTHS[bd.month - 1]} {bd.day}"),
    ]
    x = W - 48
    for label, val, unit in reversed(items):
        vw = g.width(val, "display", 30, -0.5)
        uw = g.width(unit, "text", 13) + 6 if unit else 0
        lw = g.width(label, "sans", 11, 1.6)
        wdt = max(vw + uw, lw)
        left = x - wdt
        p.append(g.text(label, left, 58, 11, "sans", t["sub"], spacing=1.6))
        p.append(g.text(val, left, 94, 30, "display", t["fg"], spacing=-0.5))
        if unit:
            p.append(g.text(unit, left + vw + 6, 94, 13, "text", t["sub"]))
        x = left - 46

    # ---- 週ごとの推移（エリアチャート）
    cy0, cy1 = 128, 206                      # チャートの上端・下端
    weekly = [sum(d["count"] for d in c) for c in cols]
    mx = max(weekly) or 1
    pts = [(gx + i * step + step / 2, cy1 - (v / mx) * (cy1 - cy0)) for i, v in enumerate(weekly)]
    line = smooth(pts)
    area = line + f" L{pts[-1][0]:.1f} {cy1} L{pts[0][0]:.1f} {cy1} Z"
    for k in range(1, 3):
        yy = cy1 - (cy1 - cy0) * k / 2
        p.append(f'<line x1="{gx}" y1="{yy}" x2="{gx2}" y2="{yy}" stroke="{t["faint"]}" stroke-opacity=".25" stroke-dasharray="2 5"/>')
    p.append(f'<line x1="{gx}" y1="{cy1}" x2="{gx2}" y2="{cy1}" stroke="{t["faint"]}" stroke-opacity=".4"/>')
    p.append(f'<path d="{area}" fill="url(#areaGrad)" class="area"/>')
    p.append(f'<path d="{line}" fill="none" stroke="url(#lineGrad)" stroke-width="5" opacity=".35" filter="url(#glow)" pathLength="1" class="draw"/>')
    p.append(f'<path d="{line}" fill="none" stroke="url(#lineGrad)" stroke-width="2.2" stroke-linecap="round" pathLength="1" class="draw"/>')
    wi = max(range(n), key=lambda i: weekly[i])
    p.append(f'<circle cx="{pts[wi][0]:.1f}" cy="{pts[wi][1]:.1f}" r="4" fill="{t["cells"][4]}" class="area"/>')
    p.append(g.text(f"{weekly[wi]} / week", pts[wi][0] + 9, pts[wi][1] + 4, 11.5, "sans", t["sub"], extra=' class="area"'))
    p.append(g.text("weekly", gx - 10, cy1 - 2, 11, "text", t["faint"], "end"))

    # ---- ヒートマップ
    hy = 248
    prev = None
    for i, c in enumerate(cols):
        mo = dt.date.fromisoformat(c[0]["date"]).month
        if mo != prev and i < n - 2 and (i > 0 or c[0]["date"][8:] <= "07"):
            p.append(g.text(MONTHS[mo - 1], gx + i * step, hy - 10, 11.5, "text", t["sub"]))
        prev = mo
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(g.text(name, gx - 10, hy + row * step + cell / 2 + 4, 11, "text", t["faint"], "end"))
    for i, c in enumerate(cols):
        cells = []
        for d in c:
            lv = d["level"]
            x0, y0 = gx + i * step, hy + d["weekday"] * step
            glow = ' filter="url(#cellGlow)"' if lv == 4 and theme == "night" else ""
            cells.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="3.5" fill="{t["cells"][lv]}"{glow}/>')
        p.append(f'<g class="col" style="animation-delay:{0.1 + i * 0.022:.2f}s">' + "".join(cells) + "</g>")
    # 今日
    li, ld = n - 1, cols[-1][-1]
    p.append(f'<rect x="{gx + li * step - 1.5:.1f}" y="{hy + ld["weekday"] * step - 1.5:.1f}" width="{cell + 3:.1f}" '
             f'height="{cell + 3:.1f}" rx="4.5" fill="none" stroke="{t["today"]}" stroke-width="1.3" opacity=".8"/>')

    # 凡例
    ly = hy + 7 * step + 16
    lx = gx2
    for lv in range(4, -1, -1):
        lx -= 15
        p.append(f'<rect x="{lx:.1f}" y="{ly}" width="11" height="11" rx="2.5" fill="{t["cells"][lv]}"/>')
    p.append(g.text("More", lx + 5 * 15 + 6, ly + 10, 11, "text", t["faint"]))
    p.append(g.text("Less", lx - 8, ly + 10, 11, "text", t["faint"], "end"))

    style = """
.col{animation:pop .45s ease-out backwards}
.draw{stroke-dasharray:1;animation:draw 1.8s cubic-bezier(.4,0,.2,1) .2s backwards}
.area{animation:fade .8s ease-out 1.4s backwards}
@keyframes pop{from{opacity:0;transform:translateY(4px)}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes fade{from{opacity:0}}
"""
    defs = f"""
<linearGradient id="lineGrad" x1="{gx}" y1="0" x2="{gx2}" y2="0" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#6366f1"/><stop offset=".55" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/>
</linearGradient>
<linearGradient id="areaGrad" x1="0" y1="{cy0}" x2="0" y2="{cy1}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#818cf8" stop-opacity="{t['areaOp']}"/><stop offset="1" stop-color="#818cf8" stop-opacity="0"/>
</linearGradient>
<filter id="glow" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="cellGlow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
{g.defs()}"""
    return card(W, H, t, "".join(p), defs, style, f"{st['total']} contributions in the last year")


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--sample"]:
        with open(args[1], encoding="utf-8") as f:
            days = json.load(f)
    else:
        login = args[0] if args else os.environ.get("USERNAME", "sogawa10")
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN が必要です")
        days = fetch(login, token)
    fill_levels(days)
    for theme in ("day", "night"):
        path = os.path.join(ROOT, "assets", f"contrib-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(days, theme))
        print("wrote", path)


if __name__ == "__main__":
    main()
