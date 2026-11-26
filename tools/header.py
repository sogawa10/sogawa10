"""プロフィールのヘッダー（assets/header-day.svg / header-night.svg）を作る。

    python tools/header.py

文言は下の NAME / GREETING / TAGLINE / CODE を書き換えるだけ。
"""
import os

from glyphs import Glyphs

NAME = "sogawa10"
GREETING = "Hi, I'm"
TAGLINE = "Webアプリを作るのが好きな、情報系の大学院生です。"
FILENAME = "sogawa10.ts"

# 右のコードウィンドウ。各行は (文字, 種類) の並び。種類: kw / prop / str / pun / txt
CODE = [
    [("const ", "kw"), ("me", "txt"), (" = {", "pun")],
    [("  stack", "prop"), (": [", "pun"), ('"TypeScript"', "str"), (", ", "pun"), ('"Go"', "str"),
     (", ", "pun"), ('"Python"', "str"), ("],", "pun")],
    [("  building", "prop"), (": ", "pun"), ('"VegeTASK"', "str"), (",", "pun")],
    [("  offline", "prop"), (": [", "pun"), ('"touring"', "str"), (", ", "pun"), ('"games"', "str"), ("],", "pun")],
    [("};", "pun")],
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 300

THEMES = {
    "night": {
        "bg1": "#0b0e16", "bg2": "#0d1117", "border": "#222a38",
        "fg1": "#ffffff", "fg2": "#a5b4fc", "sub": "#94a3b8", "role": "#a5b4fc",
        "dots": "#ffffff", "dotsOp": 0.07,
        "blobs": [("#6366f1", 0.45), ("#22d3ee", 0.30), ("#d946ef", 0.30)],
        "win": "#0f1422", "winBorder": "#2a3346", "shadowOp": 0.6,
    },
    "day": {
        "bg1": "#ffffff", "bg2": "#f7f8fc", "border": "#e4e7ef",
        "fg1": "#0f172a", "fg2": "#4338ca", "sub": "#64748b", "role": "#4f46e5",
        "dots": "#0f172a", "dotsOp": 0.07,
        "blobs": [("#818cf8", 0.35), ("#67e8f9", 0.35), ("#f0abfc", 0.30)],
        "win": "#0f1422", "winBorder": "#1e2536", "shadowOp": 0.22,
    },
}
SYNTAX = {"kw": "#c792ea", "prop": "#82aaff", "str": "#c3e88d", "pun": "#89ddff", "txt": "#e2e8f0"}


def build(theme: str) -> str:
    t = THEMES[theme]
    g = Glyphs()
    p = []

    # ---- 背景: オーロラ + ドットグリッド
    blobs = [(330, 40, 300, 150), (980, 260, 320, 150), (700, -30, 260, 120)]
    for i, ((cx, cy, rx, ry), (col, op)) in enumerate(zip(blobs, t["blobs"])):
        p.append(f'<ellipse class="b b{i}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}" filter="url(#blur)"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotFade)"/>')

    # ---- 左: 肩書き・名前・タグライン
    x0 = 76
    p.append(g.text(GREETING, x0, 92, 22, "text", t["sub"]))
    name = g.text(NAME, x0 - 4, 182, 100, "display", "#fff", spacing=-3)
    p.append(f'<mask id="nameMask">{name}</mask>')
    p.append(f'<rect x="0" y="80" width="700" height="130" fill="url(#nameGrad)" mask="url(#nameMask)"/>')
    p.append(g.text(TAGLINE, x0, 232, 19, "jp", t["sub"]))

    # ---- 右: コードウィンドウ
    wx, wy, ww, wh = 706, 52, 420, 196
    p.append(f'<rect x="{wx}" y="{wy + 14}" width="{ww}" height="{wh}" rx="14" fill="#000" '
             f'opacity="{t["shadowOp"]}" filter="url(#shadow)"/>')
    p.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{t["win"]}" '
             f'stroke="{t["winBorder"]}" stroke-width="1"/>')
    p.append(f'<line x1="{wx}" y1="{wy + 36}" x2="{wx + ww}" y2="{wy + 36}" stroke="{t["winBorder"]}"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        p.append(f'<circle cx="{wx + 20 + i * 18}" cy="{wy + 18}" r="5.5" fill="{c}"/>')
    p.append(g.text(FILENAME, wx + ww / 2, wy + 23, 12.5, "mono", "#64748b", "middle"))

    lx, ly, lh, fs = wx + 22, wy + 68, 25, 14.5
    for n, line in enumerate(CODE):
        y = ly + n * lh
        row = []
        x = lx
        for txt, kind in line:
            row.append(g.text(txt, x, y, fs, "mono", SYNTAX[kind]))
            x += g.width(txt, "mono", fs)
        p.append(f'<g class="ln" style="animation-delay:{0.25 + n * 0.12:.2f}s">' + "".join(row) + "</g>")
        last_x, last_y = x, y
    p.append(f'<rect class="cur" x="{last_x + 3:.1f}" y="{last_y - 13}" width="8" height="17" rx="1" fill="#a5b4fc"/>')

    style = """
.b{animation:drift 16s ease-in-out infinite alternate}
.b1{animation-duration:19s;animation-direction:alternate-reverse}
.b2{animation-duration:13s}
.ln{animation:in .5s ease-out backwards}
.cur{animation:blink 1.1s steps(1) infinite}
@keyframes drift{0%{transform:translate(0,0)}50%{transform:translate(60px,18px)}100%{transform:translate(-40px,-12px)}}
@keyframes in{from{opacity:0;transform:translateX(-6px)}}
@keyframes blink{50%{opacity:0}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{NAME}">
<style>{style}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg1']}"/><stop offset="1" stop-color="{t['bg2']}"/></linearGradient>
<linearGradient id="nameGrad" x1="72" y1="0" x2="520" y2="0" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{t['fg1']}"/><stop offset="1" stop-color="{t['fg2']}"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6366f1" stop-opacity="0"/><stop offset=".5" stop-color="#8b5cf6" stop-opacity=".9"/>
  <stop offset="1" stop-color="#22d3ee" stop-opacity="0"/>
</linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
  <circle cx="11" cy="11" r="1.1" fill="{t['dots']}" opacity="{t['dotsOp']}"/>
</pattern>
<radialGradient id="fade" cx=".3" cy=".5" r=".75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="dotFade"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20"/></clipPath>
<filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>
{g.defs()}
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{''.join(p)}
<rect x="0" y="0" width="{W}" height="2" fill="url(#edge)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="{t['border']}" stroke-width="1.5"/>
</svg>
"""


if __name__ == "__main__":
    for theme in ("day", "night"):
        path = os.path.join(ROOT, "assets", f"banner-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", path)
