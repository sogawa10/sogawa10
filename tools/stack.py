"""Tech Stack のアイコン行を「光るSVG」として作る。

skill-icons (https://github.com/tandpfun/skill-icons) のアイコンを取ってきて SVG に埋め込み、
  - アイコンの後ろでブランド色がふわっと明滅するグロー
  - 縁取りのネオン線
  - 左から右へ流れる光沢（キラッと光る）
を付けて、カテゴリごとに assets/stack-<key>-night.svg / -day.svg を書き出す。

GitHub の README は CSS が使えないが、<img> で読み込んだ SVG の中の
<style> / filter / アニメーションは動くので、エフェクトは全部 SVG 側に持たせている。

技術を増やすとき: 下の STACK の該当カテゴリに (ファイル名, 光の色) を1件足して
  python tools/stack.py
を実行し、README の alt にも名前を足す。

ファイル名は skill-icons の icons/ フォルダのもの（-Dark/-Light は付けない。自動で選ぶ）。
  一覧: https://github.com/tandpfun/skill-icons/tree/main/icons
光の色は "#RRGGBB" 1つ、または (ダーク用, ライト用) のタプル。
skill-icons に無いもの（Slack）は "local:<パス>" で assets/icons/ の SVG を使う。
"""

from __future__ import annotations

import base64
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
RAW = "https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/{}.svg"

# ■ 並びは README の Tech Stack と同じ（フロント → バック → AI・その他）
STACK: dict[str, list[tuple[str, str | tuple[str, str]]]] = {
    "languages": [
        ("HTML", "#E34F26"),
        ("CSS", "#2D8CF0"),
        ("JavaScript", "#F7DF1E"),
        ("TypeScript", "#3178C6"),
        ("GoLang", "#00ADD8"),
        ("Python", "#4B8BBE"),
        ("C", "#7986CB"),
        ("Java", "#F89820"),
        ("Matlab", "#E16737"),
    ],
    "frameworks": [
        ("React", "#61DAFB"),
        ("VueJS", "#41B883"),
        ("FastAPI", "#05998B"),
        ("PyTorch", "#EE4C2C"),
        ("OpenCV", "#7C5CFF"),
    ],
    "platforms": [
        ("NodeJS", "#8CC84B"),
        ("Github", ("#FFFFFF", "#24292F")),
    ],
    "tools": [
        ("Npm", "#CB3837"),
        ("Vite", "#BD34FE"),
        ("Anaconda", "#44A833"),
        ("Git", "#F05033"),
        ("GithubActions", "#2088FF"),
    ],
    "softwares": [
        ("Windows", "#00A4EF"),
        ("Linux", "#FCC624"),
        ("Ubuntu", "#E95420"),
        ("Debian", "#D70A53"),
        ("Docker", "#2496ED"),
        ("Nginx", "#009639"),
        ("PostgreSQL", "#4F8CC9"),
    ],
    "apps": [
        ("VSCode", "#23A8F2"),
        ("Notion", ("#FFFFFF", "#000000")),
        ("Discord", "#5865F2"),
        ("local:assets/icons/slack-{theme}.svg", "#E01E5A"),
    ],
}

# ■ 見た目の調整
ICON = 48          # アイコン1個の大きさ(px)。skillicons の既定と同じ
GAP = 14           # アイコン同士の間隔
PAD = 17           # 外側の余白（グローが切れないための場所）
RADIUS = ICON * 60 / 256   # skill-icons の角丸に合わせる

THEMES = {
    # icon: skill-icons のテーマ / base,peak: グローの明るさ(最小,最大) / blur: ぼかし / spread: 光の広がり / dy: 下へのずれ / rim: 縁取り
    "night": dict(icon="Dark", base=0.45, peak=1.0, blur=7, spread=3, dy=0, rim=0.7),
    "day": dict(icon="Light", base=0.25, peak=0.6, blur=5, spread=1, dy=3, rim=0.0),
}

PULSE_SEC = 3.2    # グローが1往復する時間
SWEEP_SEC = 6.0    # 光沢が流れる周期
STAGGER = 0.12     # 隣のアイコンとのずれ（波のように光る）

_cache: dict[str, bytes] = {}


def fetch(url: str) -> bytes:
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "sogawa10-profile"})
        with urllib.request.urlopen(req, timeout=30) as r:
            _cache[url] = r.read()
    return _cache[url]


def skill_icon(name: str, theme: str) -> bytes:
    """themed なアイコンは -Dark/-Light を、無ければ素のファイルを使う。"""
    for stem in (f"{name}-{theme}", name):
        try:
            return fetch(RAW.format(stem))
        except Exception:
            continue
    raise SystemExit(f"skill-icons に {name} が見つかりません")


def square_crop(svg: bytes) -> bytes:
    """左に余白を入れた横長SVG（Slack用）を、右端の正方形だけに切り抜く。"""
    text = svg.decode("utf-8")
    m = re.search(r"<svg\b[^>]*>", text)
    if not m:
        return svg
    tag = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', tag)
    if vb:
        x, y, w, h = (float(v) for v in vb.group(1).replace(",", " ").split())
    else:
        w = float(re.search(r'width="([\d.]+)', tag).group(1))
        h = float(re.search(r'height="([\d.]+)', tag).group(1))
        x = y = 0.0
    if w <= h * 1.02:
        return svg
    new = re.sub(r'\s(viewBox|width|height)="[^"]*"', "", tag)
    new = new.replace("<svg", f'<svg viewBox="{x + w - h:g} {y:g} {h:g} {h:g}" width="{h:g}" height="{h:g}"', 1)
    return text.replace(tag, new, 1).encode("utf-8")


def local_icon(spec: str, theme: str) -> bytes | None:
    path = ROOT / spec.removeprefix("local:").format(theme=theme.lower())
    if not path.exists():
        print(f"  ! {path.relative_to(ROOT)} が無いのでスキップ", file=sys.stderr)
        return None
    return square_crop(path.read_bytes())


def build(key: str, theme_name: str) -> str:
    t = THEMES[theme_name]
    is_night = theme_name == "night"
    icons = []
    for spec, color in STACK[key]:
        data = local_icon(spec, t["icon"]) if spec.startswith("local:") else skill_icon(spec, t["icon"])
        if data is None:
            continue
        c = color if isinstance(color, str) else color[0 if is_night else 1]
        icons.append((base64.b64encode(data).decode(), c))

    n = len(icons)
    width = PAD * 2 + n * ICON + (n - 1) * GAP
    height = PAD * 2 + ICON

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        f".g{{opacity:{t['base']};animation:pulse {PULSE_SEC}s ease-in-out infinite}}",
        f"@keyframes pulse{{0%,100%{{opacity:{t['base']}}}50%{{opacity:{t['peak']}}}}}",
        f".r{{opacity:{t['rim'] * 0.4:.2f};animation:rim {PULSE_SEC}s ease-in-out infinite}}",
        f"@keyframes rim{{0%,100%{{opacity:{t['rim'] * 0.4:.2f}}}50%{{opacity:{t['rim']}}}}}",
        f".s{{transform:translateX(-{ICON * 1.3:g}px);animation:sweep {SWEEP_SEC}s ease-in-out infinite}}",
        f"@keyframes sweep{{0%{{transform:translateX(-{ICON * 1.3:g}px)}}"
        f"16%,100%{{transform:translateX({ICON * 1.3:g}px)}}}}",
        "@media (prefers-reduced-motion:reduce){.g,.r,.s{animation:none}}",
        "</style>",
        "<defs>",
        f'<filter id="blur" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur stdDeviation="{t["blur"]}"/></filter>',
        '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0.35" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="#fff" stop-opacity="{0.38 if is_night else 0.55}"/>'
        '<stop offset="0.65" stop-color="#fff" stop-opacity="0"/>'
        "</linearGradient>",
        f'<clipPath id="clip"><rect width="{ICON}" height="{ICON}" rx="{RADIUS:.2f}"/></clipPath>',
        "</defs>",
    ]

    for i, (b64, c) in enumerate(icons):
        x = PAD + i * (ICON + GAP)
        pulse_delay = f"animation-delay:-{(n - i) * STAGGER * 2:.2f}s"
        sweep_delay = f"animation-delay:{i * STAGGER:.2f}s"
        parts += [
            f'<g transform="translate({x},{PAD})">',
            # 1. 後ろで明滅するグロー
            f'<rect class="g" style="{pulse_delay}" x="{-t["spread"]}" y="{t["dy"] - t["spread"]}" '
            f'width="{ICON + 2 * t["spread"]}" height="{ICON + 2 * t["spread"]}" '
            f'rx="{RADIUS + t["spread"]:.2f}" fill="{c}" filter="url(#blur)"/>',
            # 2. アイコン本体
            f'<image width="{ICON}" height="{ICON}" href="data:image/svg+xml;base64,{b64}"/>',
            # 3. 光沢（角丸の中だけ）
            f'<g clip-path="url(#clip)"><rect class="s" style="{sweep_delay}" width="{ICON}" height="{ICON}" '
            f'fill="url(#shine)"/></g>',
        ]
        # 4. ネオンの縁取り（ダークのみ）
        if t["rim"]:
            parts.append(
                f'<rect class="r" style="{pulse_delay}" x="0.5" y="0.5" width="{ICON - 1}" height="{ICON - 1}" '
                f'rx="{RADIUS:.2f}" fill="none" stroke="{c}" stroke-width="1"/>'
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for key in STACK:
        for theme in THEMES:
            out = ASSETS / f"stack-{key}-{theme}.svg"
            out.write_text(build(key, theme), encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
