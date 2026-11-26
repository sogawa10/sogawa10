"""ツーリングのドット絵（assets/touring-*.svg）を、ほかのカードと同じ枠に収めたフッターにする。

    python tools/footer.py      → assets/footer-day.svg / footer-night.svg

ドット絵を作り直したら（tools/touring.py）、これも実行し直す。
- 角丸・枠線・上辺の光るラインをほかのカードとそろえる
- 空の上の方をカードの背景色へなじませ、夜はオーロラ色をうっすら重ねる
"""
import os
import re

from theme import EDGE, THEMES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 300   # ドット絵（200×50）のちょうど 6 倍


def build(theme: str) -> str:
    t = THEMES[theme]
    src = open(os.path.join(ROOT, "assets", f"touring-{theme}.svg"), encoding="utf-8").read()
    # id がこのファイルの id とぶつからないように接頭辞を付ける
    ids = set(re.findall(r'\bid="([^"]+)"', src))
    for i in sorted(ids, key=len, reverse=True):
        src = re.sub(rf'\bid="{re.escape(i)}"', f'id="tr-{i}"', src)
        src = re.sub(rf'url\(#{re.escape(i)}\)', f'url(#tr-{i})', src)
        src = re.sub(rf'href="#{re.escape(i)}"', f'href="#tr-{i}"', src)
    # 一番外側の <svg> をカード内いっぱいに置く入れ子の <svg> にする
    src = re.sub(r"<svg\b[^>]*>", lambda m: re.sub(r'\b(width|height)="[^"]*"', "", m.group(0))
                 .replace("<svg", f'<svg x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"'),
                 src, count=1)
    tint = ("" if theme == "day" else
            f'<rect width="{W}" height="{H}" fill="url(#tint)" style="mix-blend-mode:screen"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="バイクでツーリング中のドット絵">
<defs>
{EDGE}
<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t['bg1']}" stop-opacity=".92"/><stop offset=".42" stop-color="{t['bg1']}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="tint" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6366f1" stop-opacity=".18"/><stop offset=".55" stop-color="#a855f7" stop-opacity=".08"/>
  <stop offset="1" stop-color="#22d3ee" stop-opacity=".16"/>
</linearGradient>
</defs>
<g clip-path="url(#card)">
{src}
{tint}
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect x="0" y="0" width="{W}" height="2" fill="url(#edge)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{t['border']}" stroke-width="1.5"/>
</svg>
"""


if __name__ == "__main__":
    for theme in ("day", "night"):
        path = os.path.join(ROOT, "assets", f"footer-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", path)
