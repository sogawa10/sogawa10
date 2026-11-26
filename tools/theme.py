"""カード類（contrib.py / cards.py）で共有する配色と枠。ヘッダーと同じトーン。"""

THEMES = {
    "night": {
        "bg1": "#0b0e16", "bg2": "#0d1117", "border": "#222a38",
        "fg": "#f1f5f9", "sub": "#8b95a7", "faint": "#4b5565",
        "chip": "#151b28", "chipBorder": "#273044", "chipText": "#b6c0d0",
        "cells": ["#161b26", "#312e81", "#4f46e5", "#818cf8", "#67e8f9"],
        "glow": "#6366f1", "glowOp": 0.22, "areaOp": 0.35, "today": "#ffffff",
        "accent": "#a5b4fc", "gold": "#fbbf24", "green": "#34d399", "cyan": "#22d3ee", "violet": "#c084fc", "track": "#1a2030",
    },
    "day": {
        "bg1": "#ffffff", "bg2": "#f7f8fc", "border": "#e4e7ef",
        "fg": "#0f172a", "sub": "#64748b", "faint": "#a3abb9",
        "chip": "#f3f5fa", "chipBorder": "#e3e7f0", "chipText": "#475569",
        "cells": ["#eef0f5", "#c7d2fe", "#818cf8", "#4f46e5", "#0891b2"],
        "glow": "#a5b4fc", "glowOp": 0.25, "areaOp": 0.22, "today": "#0f172a",
        "accent": "#4f46e5", "gold": "#b45309", "green": "#059669", "cyan": "#0891b2", "violet": "#9333ea", "track": "#eef0f5",
    },
}

EDGE = """<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6366f1" stop-opacity="0"/><stop offset=".5" stop-color="#8b5cf6" stop-opacity=".9"/>
  <stop offset="1" stop-color="#22d3ee" stop-opacity="0"/>
</linearGradient>"""


def card(w: int, h: int, t: dict, body: str, defs: str = "", style: str = "", label: str = "",
         halo: bool = True) -> str:
    """角丸のカード（背景グラデーション・上辺の光るライン・枠線）で body を包む。"""
    halo_el = f'<rect width="{w}" height="{h * 0.9:.0f}" fill="url(#halo)"/>' if halo else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<style>{style}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg1']}"/><stop offset="1" stop-color="{t['bg2']}"/></linearGradient>
<radialGradient id="halo" cx=".5" cy="0" r=".8"><stop offset="0" stop-color="{t['glow']}" stop-opacity="{t['glowOp']}"/><stop offset="1" stop-color="{t['glow']}" stop-opacity="0"/></radialGradient>
{EDGE}
<clipPath id="card"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18"/></clipPath>
{defs}
</defs>
<g clip-path="url(#card)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
{halo_el}
{body}
<rect x="0" y="0" width="{w}" height="2" fill="url(#edge)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="none" stroke="{t['border']}" stroke-width="1.5"/>
</svg>
"""
