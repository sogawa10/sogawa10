<!--
  ===== sogawa10 Profile README =====
  編集のしかた:
  - 各セクションは「■」で始まるコメントで区切ってあります。
  - プロジェクトを増やすときは tools/cards.py の PROJECTS に1件足して、下の Projects にカードを1枚追加する。
  - 技術を増やすときは、該当カテゴリの skillicons の URL の i= にカンマ区切りで追加（dark と light の両方）。
    使えるID一覧: https://github.com/tandpfun/skill-icons#icons-list
    skillicons に無い Slack は assets/icons/ の SVG を、直前の picture の閉じタグの直後に
    （改行やスペースを挟まず）続けて並べている。左に余白入りなので、必ず行の最後に置く。
  - <picture> の中は、上が「ダークモード用」、下の img が「ライトモード用」。
  - srcset の中では URL のカンマを %2C と書く（カンマは区切り文字扱いになるため）。
  - ヘッダーは tools/header.py、成果物カード・Stats・言語比率は tools/cards.py、
    コントリビューションのグラフは tools/contrib.py で作っている。
    cards.py と contrib.py は .github/workflows/profile-art.yml が毎日自動で実行する。
-->

<!-- ■ ヘッダー（ダーク: 夜 / ライト: 昼） -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-night.svg">
    <img src="./assets/banner-day.svg" alt="sogawa10" width="100%">
  </picture>
</p>

<!-- ■ プロジェクト（カードは tools/cards.py の PROJECTS から作る。スター数などは毎日自動更新） -->
<a id="projects"></a>
## Projects

<p align="center">
  <a href="https://github.com/sogawa10/hackathon"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/project-hackathon-night.svg"><img src="./assets/project-hackathon-day.svg" alt="VegeTASK" width="100%"></picture></a>
  <a href="https://www.vegetask.net/"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/site-hackathon-night.svg"><img src="./assets/site-hackathon-day.svg" alt="Visit vegetask.net"></picture></a>
</p>
<p align="center">
  <a href="https://github.com/sogawa10/shogi_ai"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/project-shogi_ai-night.svg"><img src="./assets/project-shogi_ai-day.svg" alt="shogi_ai" width="100%"></picture></a>
</p>
<p align="center">
  <a href="https://github.com/sogawa10/shogi_frontend"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/project-shogi_frontend-night.svg"><img src="./assets/project-shogi_frontend-day.svg" alt="shogi_frontend" width="100%"></picture></a>
</p>

<!-- ■ 技術スタック（ダーク/ライトでアイコンの色が切り替わる）
  並べ方のルール: どの行も「フロントエンド → バックエンド → AI・その他」の順（Webアプリの手前から奥へ）。
  Softwares は「開発するPC → サーバーのOS → その上で動くもの（Docker → Nginx → DB）」の順。 -->
<a id="stack"></a>
## Tech Stack

#### 💻 Programming Languages

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=html%2Ccss%2Cjs%2Cts%2Cgo%2Cpython%2Cc%2Cjava%2Cmatlab&theme=dark">
    <img src="https://skillicons.dev/icons?i=html,css,js,ts,go,python,c,java,matlab&theme=light" alt="HTML, CSS, JavaScript, TypeScript, Go, Python, C, Java, MATLAB">
  </picture>
</p>

#### 📚 Library & Framework

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=react%2Cvue%2Cfastapi%2Cpytorch%2Copencv&theme=dark">
    <img src="https://skillicons.dev/icons?i=react,vue,fastapi,pytorch,opencv&theme=light" alt="React, Vue, FastAPI, PyTorch, OpenCV">
  </picture>
</p>

#### 🌐 Platforms

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=nodejs%2Cgithub&theme=dark">
    <img src="https://skillicons.dev/icons?i=nodejs,github&theme=light" alt="Node.js, GitHub">
  </picture>
</p>

#### 🛠 Tools

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=npm%2Cvite%2Canaconda%2Cgit%2Cgithubactions&theme=dark">
    <img src="https://skillicons.dev/icons?i=npm,vite,anaconda,git,githubactions&theme=light" alt="npm, Vite, Anaconda, Git, GitHub Actions">
  </picture>
</p>

#### 💾 Softwares

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=windows%2Clinux%2Cubuntu%2Cdebian%2Cdocker%2Cnginx%2Cpostgres&theme=dark">
    <img src="https://skillicons.dev/icons?i=windows,linux,ubuntu,debian,docker,nginx,postgres&theme=light" alt="Windows, Linux, Ubuntu, Debian, Docker, Nginx, PostgreSQL">
  </picture>
</p>

#### 🖥 Applications

<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=vscode%2Cnotion%2Cdiscord&theme=dark">
    <img src="https://skillicons.dev/icons?i=vscode,notion,discord&theme=light" alt="VS Code, Notion, Discord">
  </picture><picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/icons/slack-dark.svg">
    <img src="./assets/icons/slack-light.svg" alt="Slack">
  </picture>
</p>

<!-- ■ GitHub の数字・言語比率・コントリビューション・最近の活動（tools/cards.py と tools/contrib.py が毎日自動で作り直す） -->
<a id="activity"></a>
## Activity

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/stats-night.svg"><img src="./assets/stats-day.svg" alt="GitHub Stats" width="49%"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/langs-night.svg"><img src="./assets/langs-day.svg" alt="Languages" width="49%"></picture>
</p>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/contrib-night.svg"><img src="./assets/contrib-day.svg" alt="Contributions" width="100%"></picture>
</p>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/activity-night.svg"><img src="./assets/activity-day.svg" alt="Recent Activity" width="100%"></picture>
</p>

<!-- ■ フッター: ツーリングのドット絵をカードの枠に収めたもの（tools/footer.py。元の絵は tools/touring.py） -->
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/footer-night.svg"><img src="./assets/footer-day.svg" alt="バイクでツーリング中のドット絵" width="100%"></picture>
</p>
