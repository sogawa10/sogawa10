"""成果物カード・GitHub Stats・言語比率のカードを作る。

    GITHUB_TOKEN=... python tools/cards.py sogawa10     # GitHub から取得して生成（Actions で毎日実行）
    python tools/cards.py --sample                     # 手元の仮データで見た目だけ確認

出力（それぞれ -day / -night の 2 枚）:
    assets/project-<repo>-*.svg   成果物カード（スター数・主言語・更新日は自動で最新になる）
    assets/stats-*.svg            リポジトリ数・スター・コミット数など
    assets/langs-*.svg            公開リポジトリの言語比率（コード量ベース）
    assets/activity-*.svg         最近のコミットと PR（コミットメッセージは見る人の PC のフォントで表示）

成果物を増やす・文言を変えるときは PROJECTS を書き換えるだけ。README にも 1 枚追加する。
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
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

# ------------------------------------------------------------------ 載せる内容
PROJECTS = [
    # 全カード同じ形式: 一言説明 / 特徴 3 つ / 技術構成（層, 中身）。site があればカードの下にボタンが付く
    {
        "repo": "hackathon", "title": "VegeTASK",
        "desc": "勉強を「野菜を育てること」に見立てたタスク管理アプリ。",
        "points": ["タスクを毎日の小タスクに自動で分割",
                   "こなすと野菜が育ち、収穫してかごに溜まる",
                   "サボると予備日が減り、使い切ると枯れる"],
        "layers": [("FRONTEND", "React · TypeScript · Vite"),
                   ("BACKEND", "Go · Gin · JWT"),
                   ("DATABASE", "PostgreSQL"),
                   ("INFRA", "Docker Compose · Nginx · さくらのVPS"),
                   ("CI / CD", "GitHub Actions")],
        "site": "https://www.vegetask.net/",
    },
    {
        "repo": "shogi_ai", "title": "shogi_ai",
        "desc": "既存の将棋エンジンを使わず、ゼロから実装した将棋AI。",
        "points": ["ルール処理・状態管理からαβ探索まで自前で実装",
                   "二歩・打ち歩詰め・千日手・入玉宣言法に対応",
                   "コマンドラインでの対局と、対局用のAPIを提供"],
        "layers": [("LANGUAGE", "Python"),
                   ("AI", "αβ探索（自前実装）"),
                   ("API", "FastAPI · Pydantic · Uvicorn"),
                   ("DATABASE", "PostgreSQL"),
                   ("AUTH", "bcrypt · JWT")],
    },
    {
        "repo": "shogi_frontend", "title": "shogi_frontend",
        "desc": "shogi_ai と対局できる将棋AI対局Webサイト。",
        "points": ["ユーザー登録・ログイン（認証付きページ）",
                   "外部の将棋AIをAPIとして登録できる",
                   "人対AI・AI対AIの対局ができる"],
        "layers": [("FRONTEND", "React · TypeScript"),
                   ("ROUTING", "React Router"),
                   ("BUILD", "Vite · ESLint"),
                   ("API", "shogi_ai（FastAPI）")],
    },
]

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        name stargazerCount pushedAt
        primaryLanguage { name color }
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
    }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST]) { totalCount }
  }
}"""

# Recent Activity: 自分のコミットとして数える名前（GitHub のログイン名 / git の author 名）
MY_NAMES = {"sogawa10", "sogawa", "Soki-1010"}

ACTIVITY_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 8, ownerAffiliations: OWNER, privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        defaultBranchRef { target { ... on Commit {
          history(first: 15) { nodes { messageHeadline committedDate url author { name user { login } } } }
        } } }
      }
    }
    pullRequests(last: 10) {
      nodes { title createdAt mergedAt state url repository { name owner { login } } }
    }
  }
}"""

SAMPLE_ACTIVITY = [  # --sample 用（見た目確認のためだけ）
    ("PR MERGED", "ヘッダーにユーザー歓迎メッセージを追加", "hackathon", "2026-10-23T23:11:29+09:00"),
    ("COMMIT", "Go を 1.26.10 に、vite を 8.3.4 に上げて脆弱性検査の失敗を解消する", "hackathon", "2026-10-21T13:47:08+09:00"),
    ("COMMIT", "畑の周りの画像を高解像度版に差し替える", "hackathon", "2026-10-21T13:34:57+09:00"),
    ("PR MERGED", "収穫を HARVESTS に記録し、野菜の名前とサイズを VEGETABLES テーブルだけから引く", "hackathon", "2026-10-20T11:47:43+09:00"),
    ("COMMIT", "cssを適用", "shogi_frontend", "2026-08-30T00:48:20+09:00"),
    ("COMMIT", "テスト仕様の追加", "shogi_frontend", "2026-05-11T19:04:17+09:00"),
]

SAMPLE = {  # --sample 用の仮データ（見た目確認のためだけ）
    "createdAt": "2023-04-01T00:00:00Z",
    "repositories": {"totalCount": 12, "nodes": [
        {"name": "hackathon", "stargazerCount": 3, "pushedAt": "2026-11-20T00:00:00Z",
         "primaryLanguage": {"name": "TypeScript", "color": "#3178c6"},
         "languages": {"edges": [{"size": 380, "node": {"name": "TypeScript", "color": "#3178c6"}},
                                 {"size": 70, "node": {"name": "Go", "color": "#00ADD8"}},
                                 {"size": 40, "node": {"name": "CSS", "color": "#663399"}}]}},
        {"name": "shogi_ai", "stargazerCount": 1, "pushedAt": "2026-10-02T00:00:00Z",
         "primaryLanguage": {"name": "Python", "color": "#3572A5"},
         "languages": {"edges": [{"size": 270, "node": {"name": "Python", "color": "#3572A5"}}]}},
        {"name": "shogi_frontend", "stargazerCount": 1, "pushedAt": "2026-10-15T00:00:00Z",
         "primaryLanguage": {"name": "TypeScript", "color": "#3178c6"},
         "languages": {"edges": [{"size": 120, "node": {"name": "TypeScript", "color": "#3178c6"}},
                                 {"size": 30, "node": {"name": "CSS", "color": "#663399"}}]}},
        {"name": "vue-app", "stargazerCount": 0, "pushedAt": "2026-06-01T00:00:00Z",
         "primaryLanguage": {"name": "Vue", "color": "#41b883"},
         "languages": {"edges": [{"size": 120, "node": {"name": "Vue", "color": "#41b883"}},
                                 {"size": 90, "node": {"name": "JavaScript", "color": "#f1e05a"}},
                                 {"size": 30, "node": {"name": "HTML", "color": "#e34c26"}}]}},
    ]},
    "contributionsCollection": {"totalCommitContributions": 342, "totalPullRequestContributions": 24,
                                "totalIssueContributions": 11},
    "repositoriesContributedTo": {"totalCount": 3},
}


# ------------------------------------------------------------------ データ
def fetch(login: str, token: str, query: str = QUERY) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def activity_items(data: dict, login: str, n: int = 6) -> list[tuple[str, str, str, str]]:
    """(種類, 内容, リポジトリ, 日時) を新しい順に n 件。マージコミットは PR 側で拾うので除く。"""
    items = []
    for r in data["repositories"]["nodes"]:
        ref = r.get("defaultBranchRef") or {}
        for c in ((ref.get("target") or {}).get("history") or {}).get("nodes", []):
            a = c.get("author") or {}
            who = {(a.get("user") or {}).get("login"), a.get("name")}
            if not who & MY_NAMES or c["messageHeadline"].startswith("Merge "):
                continue
            items.append(("COMMIT", c["messageHeadline"], r["name"], c["committedDate"]))
    for pr in data["pullRequests"]["nodes"]:
        repo = pr["repository"]
        name = repo["name"] if repo["owner"]["login"] == login else f"{repo['owner']['login']}/{repo['name']}"
        if pr.get("mergedAt"):
            items.append(("PR MERGED", pr["title"], name, pr["mergedAt"]))
        elif pr["state"] == "OPEN":
            items.append(("PR OPEN", pr["title"], name, pr["createdAt"]))
    items.sort(key=lambda x: dt.datetime.fromisoformat(x[3].replace("Z", "+00:00")), reverse=True)
    return items[:n]


def ago(iso: str, now: dt.datetime) -> str:
    d = (now - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds()
    for unit, sec in (("year", 31536000), ("month", 2592000), ("week", 604800), ("day", 86400), ("hour", 3600)):
        if d >= sec:
            k = int(d // sec)
            return f"{k} {unit}{'s' if k > 1 else ''} ago"
    return "just now"


# ------------------------------------------------------------------ 部品
def clip(g: Glyphs, text: str, font: str, size: float, maxw: float) -> str:
    if g.width(text, font, size) <= maxw:
        return text
    while text and g.width(text + "…", font, size) > maxw:
        text = text[:-1]
    return text + "…"



def wrap(g: Glyphs, text: str, font: str, size: float, maxw: float) -> list[str]:
    """日本語向けの折り返し（句読点の直後で折りやすくする）。"""
    lines, cur = [], ""
    for ch in text:
        if g.width(cur + ch, font, size) > maxw and cur:
            # 行頭に句読点が来ないように、句読点は前の行にぶら下げる
            if ch in "、。，．」）":
                cur += ch
                lines.append(cur)
                cur = ""
                continue
            lines.append(cur)
            cur = ""
        cur += ch
    if cur:
        lines.append(cur)
    return lines


def chips(g: Glyphs, t: dict, tags: list[str], x: float, y: float, maxx: float) -> str:
    out = []
    for tag in tags:
        w = g.width(tag, "sans", 13) + 24
        if x + w > maxx:
            break
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="28" rx="14" fill="{t["chip"]}" '
                   f'stroke="{t["chipBorder"]}"/>')
        out.append(g.text(tag, x + 12, y + 18.5, 13, "sans", t["chipText"]))
        x += w + 8
    return "".join(out)


def footer(g: Glyphs, t: dict, repo: dict | None, x: float, y: float) -> str:
    if not repo:
        return ""
    out = []
    lang = repo.get("primaryLanguage") or {}
    if lang:
        out.append(f'<circle cx="{x + 6}" cy="{y - 5}" r="6" fill="{lang.get("color") or "#888"}"/>')
        out.append(g.text(lang["name"], x + 18, y, 14, "text", t["sub"]))
        x += 18 + g.width(lang["name"], "text", 14) + 22
    # スター
    star = ("M0 -7.5 L2.2 -2.6 L7.4 -2.3 L3.4 1.1 L4.6 6.2 L0 3.4 L-4.6 6.2 L-3.4 1.1 L-7.4 -2.3 L-2.2 -2.6Z")
    out.append(f'<path d="{star}" transform="translate({x + 7} {y - 5})" fill="none" stroke="{t["sub"]}" '
               f'stroke-width="1.4" stroke-linejoin="round"/>')
    out.append(g.text(str(repo.get("stargazerCount", 0)), x + 19, y, 14, "text", t["sub"]))
    x += 19 + g.width(str(repo.get("stargazerCount", 0)), "text", 14) + 22
    if repo.get("pushedAt"):
        d = dt.date.fromisoformat(repo["pushedAt"][:10])
        out.append(g.text(f"Updated {MONTHS[d.month - 1]} {d.year}", x, y, 14, "text", t["faint"]))
    return "".join(out)


# ------------------------------------------------------------------ カード
def project_card(p: dict, repo: dict | None, theme: str) -> str:
    t = THEMES[theme]
    g = Glyphs()
    w, h = 1200, 300
    b = [g.text(p["title"], 48, 82, 42, "display", t["fg"], spacing=-0.8),
         g.text(f"sogawa10/{p['repo']}", 48 + g.width(p["title"], "display", 42, -0.8) + 16, 80,
                15, "mono", t["faint"]),
         g.text(p["desc"], 48, 126, 19, "jp", t["sub"])]
    for i, pt in enumerate(p.get("points", [])):
        yy = 172 + i * 31
        b.append(f'<circle cx="56" cy="{yy - 6}" r="8" fill="{t["accent"]}" fill-opacity=".16"/>')
        b.append(f'<path d="M52 {yy - 6} l3 3 l5 -6" fill="none" stroke="{t["accent"]}" stroke-width="1.8" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(g.text(pt, 74, yy, 16.5, "jp", t["fg"]))
    b.append(footer(g, t, repo, 48, 272))

    # 右: 技術構成パネル（行数が違っても縦に均等に並べる）
    px, py, pw, ph = 742, 30, 412, 240
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="{t["chip"]}" stroke="{t["chipBorder"]}"/>')
    cols = [t["accent"], t["cyan"], t["green"], t["gold"], t["violet"]]
    layers = p.get("layers", [])
    gap = (ph - 24) / max(len(layers), 1)
    for i, (label, val) in enumerate(layers):
        c = cols[i % len(cols)]
        yy = py + 12 + i * gap + (gap - 34) / 2
        b.append(f'<rect x="{px + 22}" y="{yy:.1f}" width="3" height="34" rx="1.5" fill="{c}"/>')
        b.append(g.text(label, px + 38, yy + 11, 10.5, "sans", c, spacing=1.6))
        b.append(g.text(val, px + 38, yy + 30, 15.5, "jpm", t["fg"]))
    body = f'<g class="in">{"".join(b)}</g>'
    style = ".in{animation:in .6s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(6px)}}"
    return card(w, h, t, body, g.defs(), style, p["title"])


def site_button(url: str, theme: str) -> str:
    """公開サイトへのリンクボタン（README でカードの下に置く）。"""
    t = THEMES[theme]
    g = Glyphs()
    host = url.split("//")[-1].strip("/").removeprefix("www.")
    label = f"Visit {host}"
    w, h = int(g.width(label, "sans", 15) + 92), 46
    globe = (f'<g transform="translate(26 23)" fill="none" stroke="{t["accent"]}" stroke-width="1.6">'
             f'<circle r="8"/><ellipse rx="3.6" ry="8"/><path d="M-8 0H8"/></g>')
    arrow = (f'<path d="M{w - 30} 28 L{w - 21} 19 M{w - 28} 19 L{w - 21} 19 L{w - 21} 26" fill="none" '
             f'stroke="{t["sub"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6366f1"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{h / 2 - 1}" fill="{t['bg1']}" stroke="url(#bd)" stroke-width="1.5"/>
{globe}{g.text(label, 46, 28.5, 15, "sans", t["fg"])}{arrow}
<defs>{g.defs()}</defs>
</svg>
"""


def activity_card(items: list, theme: str, now: dt.datetime) -> str:
    t = THEMES[theme]
    g = Glyphs()
    row_h, top = 46, 116
    h = top + (len(items) - 1) * row_h + 44
    kinds = {"COMMIT": t["accent"], "PR MERGED": t["violet"], "PR OPEN": t["green"]}
    b = [g.text("Recent Activity", 48, 62, 24, "display", t["fg"], spacing=-0.3),
         g.text("latest commits & pull requests", 48, 86, 13, "text", t["sub"])]
    for i, (kind, msg, repo, when) in enumerate(items):
        y = top + i * row_h
        c = kinds.get(kind, t["accent"])
        if i:
            b.append(f'<line x1="48" y1="{y - 23}" x2="1152" y2="{y - 23}" stroke="{t["faint"]}" stroke-opacity=".18"/>')
        pw = 104
        row = [f'<rect x="48" y="{y - 13}" width="{pw}" height="24" rx="12" fill="{c}" fill-opacity=".14"/>',
               g.text(kind, 48 + pw / 2, y + 3.5, 10.5, "sans", c, "middle", spacing=1.2),
               g.text(clip(g, msg, "jp", 16, 640), 172, y + 5, 16, "jp", t["fg"]),
               g.text(repo, 870, y + 4, 13.5, "mono", t["sub"]),
               g.text(ago(when, now), 1152, y + 4, 13.5, "text", t["faint"], "end")]
        b.append(f'<g class="r" style="animation-delay:{0.1 + i * 0.08:.2f}s">' + "".join(row) + "</g>")
    style = ".r{animation:in .5s ease-out backwards}@keyframes in{from{opacity:0;transform:translateX(-8px)}}"
    return card(1200, h, t, "".join(b), g.defs(), style, "Recent Activity", halo=False)


def stats_card(user: dict, theme: str) -> str:
    t = THEMES[theme]
    g = Glyphs()
    cc = user["contributionsCollection"]
    repos = user["repositories"]
    items = [
        (f"{repos['totalCount']}", "Public repos"),
        (f"{sum(r['stargazerCount'] for r in repos['nodes'])}", "Stars earned"),
        (f"{cc['totalCommitContributions']:,}", "Commits (1 yr)"),
        (f"{cc['totalPullRequestContributions']}", "Pull requests (1 yr)"),
        (f"{cc['totalIssueContributions']}", "Issues (1 yr)"),
        (f"{user['repositoriesContributedTo']['totalCount']}", "Contributed to"),
    ]
    since = user["createdAt"][:4]
    b = [g.text("GitHub Stats", 40, 62, 24, "display", t["fg"], spacing=-0.3),
         g.text(f"on GitHub since {since}", 40, 86, 13, "text", t["sub"])]
    for i, (val, label) in enumerate(items):
        c, r = i % 3, i // 3
        x, y = 40 + c * 180, 160 + r * 92
        b.append(f'<g class="n" style="animation-delay:{0.1 + i * 0.07:.2f}s">'
                 + g.text(val, x, y, 36, "display", t["fg"], spacing=-0.8)
                 + g.text(label, x, y + 24, 13, "text", t["sub"]) + "</g>")
    style = ".n{animation:in .5s ease-out backwards}@keyframes in{from{opacity:0;transform:translateY(6px)}}"
    return card(590, 300, t, "".join(b), g.defs(), style, "GitHub Stats")


def langs_card(user: dict, theme: str, skip: tuple[str, ...] = ()) -> str:
    t = THEMES[theme]
    g = Glyphs()
    total: dict[str, list] = {}
    for r in user["repositories"]["nodes"]:
        if r["name"] in skip:
            continue
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            total.setdefault(n, [0, e["node"].get("color") or "#8b95a7"])[0] += e["size"]
    s = sum(v[0] for v in total.values()) or 1
    langs = sorted(total.items(), key=lambda kv: -kv[1][0])
    top = langs[:7]
    rest = sum(v[0] for _, v in langs[7:])
    rows = [(n, v[0] / s, v[1]) for n, v in top] + ([("Other", rest / s, "#8b95a7")] if rest else [])

    b = [g.text("Languages", 40, 62, 24, "display", t["fg"], spacing=-0.3),
         g.text("public repos · by code size", 40, 86, 13, "text", t["sub"])]
    bx, by, bw, bh = 40, 112, 510, 12
    b.append(f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6"/></clipPath>')
    seg, x = [], bx
    for n, frac, col in rows:
        w = bw * frac
        seg.append(f'<rect x="{x:.1f}" y="{by}" width="{w + 0.5:.1f}" height="{bh}" fill="{col}"/>')
        x += w
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{t["track"]}"/>')
    b.append(f'<g clip-path="url(#bar)"><g class="grow">{"".join(seg)}</g></g>')
    for i, (n, frac, col) in enumerate(rows):
        c, r = i // 4, i % 4
        x, y = 40 + c * 270, 166 + r * 34
        b.append(f'<circle cx="{x + 6}" cy="{y - 5}" r="6" fill="{col}"/>')
        b.append(g.text(n, x + 20, y, 15, "sans", t["fg"]))
        b.append(g.text(f"{frac * 100:.1f}%", x + 240, y, 15, "text", t["sub"], "end"))
    style = (".grow{transform-origin:40px 0;animation:grow 1.1s cubic-bezier(.4,0,.2,1) .2s backwards}"
             "@keyframes grow{from{transform:scaleX(0)}}")
    return card(590, 300, t, "".join(b), g.defs(), style, "Languages")


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--sample"]:
        user, login = SAMPLE, "sogawa10"
        items, now = SAMPLE_ACTIVITY, dt.datetime(2026, 11, 27, tzinfo=dt.timezone.utc)
    else:
        login = args[0] if args else os.environ.get("USERNAME", "sogawa10")
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN が必要です")
        user = fetch(login, token)
        items = activity_items(fetch(login, token, ACTIVITY_QUERY), login)
        now = dt.datetime.now(dt.timezone.utc)
    by_name = {r["name"]: r for r in user["repositories"]["nodes"]}
    out = os.path.join(ROOT, "assets")
    for theme in ("day", "night"):
        for p in PROJECTS:
            with open(os.path.join(out, f"project-{p['repo']}-{theme}.svg"), "w", encoding="utf-8") as f:
                f.write(project_card(p, by_name.get(p["repo"]), theme))
            if p.get("site"):
                with open(os.path.join(out, f"site-{p['repo']}-{theme}.svg"), "w", encoding="utf-8") as f:
                    f.write(site_button(p["site"], theme))
        with open(os.path.join(out, f"activity-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(activity_card(items, theme, now))
        with open(os.path.join(out, f"stats-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(stats_card(user, theme))
        with open(os.path.join(out, f"langs-{theme}.svg"), "w", encoding="utf-8") as f:
            # プロフィール用のこのリポジトリ自体は言語比率から外す
            f.write(langs_card(user, theme, skip=(login,)))
    print("wrote cards to", out)


if __name__ == "__main__":
    main()
