"""SVG 用の文字アウトライン（フォントに依存せず、どの環境でも同じ見た目になる）。

- 実行時（header.py / contrib.py）は tools/glyphs.json だけを読む。標準ライブラリのみで動く。
- 文字を増やしたいときだけ、フォントと fontTools がある環境で
      python tools/glyphs.py build "追加したい文字"
  を実行して glyphs.json を作り直す（既存の文字は保持される）。

フォント（すべて SIL Open Font License）:
  display : Inter Display Bold      … 名前・大きい数字
  sans    : Inter Medium            … 見出し・ラベル
  text    : Inter Regular           … 本文
  mono    : JetBrains Mono Regular  … コード
  jp / jpm: Noto Sans CJK JP Regular / Medium … 日本語
glyphs.json に無い文字が来たら、自動で普通の <text>（見る人の PC のフォント）で描く。
（build するときは FONT_FILES のパスを手元のフォントの場所に書き換える）
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "glyphs.json")

FONT_FILES = {
    "display": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
    "sans": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "text": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "mono": "/home/claude/fonts/JetBrainsMono-Regular.ttf",
    "jp": ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "JP"),
    "jpm": ("/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc", "JP"),
}
SHORT = {"display": "d", "sans": "s", "text": "t", "mono": "m", "jp": "j", "jpm": "k"}
FALLBACK = {  # glyphs.json に無い文字のときの <text> 用
    "display": ("Inter, 'Segoe UI', sans-serif", 700), "sans": ("Inter, 'Segoe UI', sans-serif", 500),
    "text": ("Inter, 'Segoe UI', sans-serif", 400), "mono": ("'JetBrains Mono', Consolas, monospace", 400),
    "jp": ("'Hiragino Sans', 'Yu Gothic UI', 'Noto Sans JP', 'Noto Sans CJK JP', sans-serif", 400),
    "jpm": ("'Hiragino Sans', 'Yu Gothic UI', 'Noto Sans JP', 'Noto Sans CJK JP', sans-serif", 500),
}

BASE_CHARS = "".join(chr(c) for c in range(0x20, 0x7F)) + "·—→…•"


# ---------------------------------------------------------------- 実行時
class Glyphs:
    """glyphs.json を読み、テキストを <use> の列に変換する。"""

    def __init__(self, path: str = JSON_PATH):
        with open(path, encoding="utf-8") as f:
            self.data = json.load(f)
        self.used: dict[str, str] = {}

    def _id(self, font: str, ch: str) -> str:
        return f"g-{SHORT[font]}-{ord(ch):x}"

    def width(self, text: str, font: str, size: float, spacing: float = 0) -> float:
        g = self.data[font]
        w = sum(g[ch][0] if ch in g else (1000 if ord(ch) > 0x2E80 else 560) for ch in text)
        return w * size / 1000 + spacing * max(len(text) - 1, 0)

    def text(self, text: str, x: float, y: float, size: float, font: str = "mincho",
             fill: str = "currentColor", anchor: str = "start", spacing: float = 0,
             extra: str = "") -> str:
        """(x, y) はベースライン位置。anchor は start / middle / end。"""
        g = self.data[font]
        w = self.width(text, font, size, spacing)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        if any(ch not in g for ch in text):
            fam, wt = FALLBACK[font]
            esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            ls = f' letter-spacing="{spacing}"' if spacing else ""
            return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-weight="{wt}" '
                    f'font-size="{size}" fill="{fill}"{ls}{extra}>{esc}</text>')
        s = size / 1000
        out = []
        cx = 0.0
        for ch in text:
            adv, d = g[ch]
            if d:
                gid = self._id(font, ch)
                self.used[gid] = d
                out.append(f'<use href="#{gid}" x="{cx / s:.0f}"/>')
            cx += adv * s + spacing
        return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" fill="{fill}"{extra}>'
                + "".join(out) + "</g>")

    def defs(self) -> str:
        return "".join(f'<path id="{k}" d="{v}"/>' for k, v in sorted(self.used.items()))


# ---------------------------------------------------------------- 作り直し用
def _outline(font, ch: str):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen

    upm = font["head"].unitsPerEm
    k = 1000 / upm
    cmap = font.getBestCmap()
    if ord(ch) not in cmap:
        return None
    name = cmap[ord(ch)]
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{round(v)}")
    gs[name].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))  # y を下向きに
    return [round(gs[name].width * k), pen.getCommands()]


def build(extra: str = "") -> None:
    from fontTools.ttLib import TTCollection, TTFont

    data = {}
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    chars = sorted(set(BASE_CHARS + extra))
    for key, path in FONT_FILES.items():
        if isinstance(path, tuple):
            path, lang = path
            font = next(f for f in TTCollection(path).fonts if lang in f["name"].getDebugName(4))
        else:
            font = TTFont(path)
        table = data.setdefault(key, {})
        for ch in chars:
            o = _outline(font, ch)
            if o is not None:
                table[ch] = o
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {JSON_PATH} ({os.path.getsize(JSON_PATH) // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build(sys.argv[2] if len(sys.argv) > 2 else "")
    else:
        print(__doc__)
