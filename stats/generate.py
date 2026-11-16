#!/usr/bin/env python3
"""
Genera dos tarjetas SVG con tus estadísticas de GitHub:
  - stats-card.svg      → tarjeta moderna en blanco y negro
  - stats-terminal.svg  → consola retro estilo neofetch

Uso:
  STATS_TOKEN=xxx GH_USER=JoansebHM python stats/generate.py
  python stats/generate.py --demo     (datos de ejemplo, sin token)

Sin dependencias: solo la librería estándar de Python.
"""
import datetime as dt
import html
import json
import os
import random
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

# ======================= CONFIGURACIÓN =======================
LANG = "en"                 # "en" o "es"
INITIALS = "JSHM"           # se muestra en la pantalla del ASCII art (máx. 6)
EXCLUDE_LANGS = []          # p. ej. ["HTML", "CSS", "Jupyter Notebook"]
EXCLUDE_REPOS = []          # repos que no quieres contar
MAX_LANGS = 6
OUT_DIR = Path(__file__).resolve().parent.parent / "assets"   # carpeta de imágenes
# =============================================================

HERE = Path(__file__).resolve().parent
FONTS = {k: (HERE / "fonts" / f"{k}.b64").read_text().strip()
         for k in ["vt323", "inter-400", "inter-600", "inter-700", "jbmono-700"]}

T = {
    "en": dict(title="GitHub stats", since="on GitHub since", contrib_year="contributions in the last year",
               commits="Commits", commits_sub="{} all-time", stars="Stars", stars_sub="{} forks",
               prs="Pull requests", issues="Issues", repos="Repositories", repos_sub="{} public",
               followers="Followers", followers_sub="{} following", cur_streak="Current streak",
               best_streak="Longest streak", days="days", day="day", this_year="this year", last12="last 12 months",
               contributions="Contributions", langs="Top languages", less="Less", more="More",
               u_user="User", u_uptime="Uptime", u_repos="Repos", u_stars="Stars", u_commits="Commits",
               u_prs="PRs", u_contrib="Contribs", u_streak="Streak", u_followers="Followers",
               u_langs="Languages", public="public", forks="Forks", issues_s="Issues",
               total="total", last_year="last year", best="best", following="Following",
               year="year", years="years", month="month", months="months", updated="updated"),
    "es": dict(title="Estadísticas de GitHub", since="en GitHub desde", contrib_year="contribuciones en el último año",
               commits="Commits", commits_sub="{} en total", stars="Estrellas", stars_sub="{} forks",
               prs="Pull requests", issues="Issues", repos="Repositorios", repos_sub="{} públicos",
               followers="Seguidores", followers_sub="{} siguiendo", cur_streak="Racha actual",
               best_streak="Mejor racha", days="días", day="día", this_year="este año", last12="últimos 12 meses",
               contributions="Contribuciones", langs="Lenguajes principales", less="Menos", more="Más",
               u_user="Usuario", u_uptime="Uptime", u_repos="Repos", u_stars="Estrellas", u_commits="Commits",
               u_prs="PRs", u_contrib="Contribs", u_streak="Racha", u_followers="Seguidores",
               u_langs="Lenguajes", public="públicos", forks="Forks", issues_s="Issues",
               total="en total", last_year="último año", best="mejor", following="Siguiendo",
               year="año", years="años", month="mes", months="meses", updated="actualizado"),
}[LANG]

esc = html.escape
fmt = lambda n: f"{n:,}"


# --------------------------------------------------------------------------- #
#  Datos
# --------------------------------------------------------------------------- #
def gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if res.get("errors"):
        raise SystemExit(f"GitHub API error: {res['errors']}")
    return res["data"]


Q_USER = """
query($login:String!){ user(login:$login){
  name login createdAt
  followers{totalCount} following{totalCount}
  pullRequests{totalCount} issues{totalCount}
  contributionsCollection{
    contributionYears totalCommitContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
  }
}}"""

Q_REPOS = """
query($login:String!,$after:String){ user(login:$login){
  repositories(first:100, after:$after, ownerAffiliations:OWNER, isFork:false){
    pageInfo{hasNextPage endCursor}
    nodes{ name isPrivate stargazerCount forkCount
      languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{name} } } }
  }
}}"""

Q_YEAR = """
query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
  contributionsCollection(from:$from, to:$to){
    totalCommitContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
  }
}}"""


def fetch(login, token):
    u = gql(Q_USER, {"login": login}, token)["user"]
    cc = u["contributionsCollection"]

    repos, after = [], None
    while True:
        r = gql(Q_REPOS, {"login": login, "after": after}, token)["user"]["repositories"]
        repos += [n for n in r["nodes"] if n["name"] not in EXCLUDE_REPOS]
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]

    langs = defaultdict(int)
    for repo in repos:
        for e in repo["languages"]["edges"]:
            if e["node"]["name"] not in EXCLUDE_LANGS:
                langs[e["node"]["name"]] += e["size"]

    # historial completo, año por año (para totales y mejor racha)
    days, commits_total, contrib_total = {}, 0, 0
    now = dt.datetime.now(dt.timezone.utc)
    for y in sorted(cc["contributionYears"]):
        frm = f"{y}-01-01T00:00:00Z"
        to = min(dt.datetime(y, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc), now)
        c = gql(Q_YEAR, {"login": login, "from": frm, "to": to.strftime("%Y-%m-%dT%H:%M:%SZ")},
                token)["user"]["contributionsCollection"]
        commits_total += c["totalCommitContributions"]
        contrib_total += c["contributionCalendar"]["totalContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]]
             for w in cc["contributionCalendar"]["weeks"]]
    for w in weeks:
        for d, c in w:
            days[d] = c

    return dict(
        name=u["name"] or u["login"], login=u["login"],
        created=dt.date.fromisoformat(u["createdAt"][:10]),
        followers=u["followers"]["totalCount"], following=u["following"]["totalCount"],
        prs=u["pullRequests"]["totalCount"], issues=u["issues"]["totalCount"],
        repos_total=len(repos), repos_public=sum(not r["isPrivate"] for r in repos),
        stars=sum(r["stargazerCount"] for r in repos), forks=sum(r["forkCount"] for r in repos),
        commits_year=cc["totalCommitContributions"], commits_total=commits_total,
        contrib_year=cc["contributionCalendar"]["totalContributions"], contrib_total=contrib_total,
        weeks=weeks, days=sorted(days.items()),
        langs=sorted(langs.items(), key=lambda x: -x[1]),
    )


def demo():
    rnd = random.Random(7)
    today = dt.date.today()
    start = dt.date(2022, 3, 10)
    days, d = [], start
    while d <= today:
        base = 0.55 if d.weekday() < 5 else 0.25
        busy = 1.6 if (d.month in (3, 4, 9, 10, 11)) else 1.0
        c = 0 if rnd.random() > base * busy * 0.9 else int(rnd.expovariate(0.28)) + 1
        days.append((d.isoformat(), c)); d += dt.timedelta(days=1)
    # últimas 53 semanas empezando en domingo
    first = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    lookup = dict(days)
    weeks, d = [], first
    while d <= today:
        weeks.append([((d + dt.timedelta(i)).isoformat(), lookup.get((d + dt.timedelta(i)).isoformat(), 0))
                      for i in range(7) if d + dt.timedelta(i) <= today])
        d += dt.timedelta(7)
    year = sum(c for w in weeks for _, c in w)
    return dict(name="Joan Sebastián", login="JoansebHM", created=start,
                followers=18, following=23, prs=41, issues=17, repos_total=27, repos_public=21,
                stars=64, forks=12, commits_year=round(year * 0.82), commits_total=2347,
                contrib_year=year, contrib_total=3120, weeks=weeks, days=days,
                langs=[("TypeScript", 520000), ("JavaScript", 310000), ("Python", 240000),
                       ("CSS", 110000), ("Java", 90000), ("HTML", 60000), ("Shell", 9000)])


# --------------------------------------------------------------------------- #
#  Cálculos
# --------------------------------------------------------------------------- #
def streaks(days):
    best = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        best = max(best, run)
    cur, items = 0, list(days)
    if items and items[-1][1] == 0:   # hoy aún sin contribuciones: no rompe la racha
        items = items[:-1]
    for _, c in reversed(items):
        if not c:
            break
        cur += 1
    return cur, best


def uptime(created):
    today = dt.date.today()
    months = (today.year - created.year) * 12 + today.month - created.month - (today.day < created.day)
    y, m = divmod(max(months, 0), 12)
    parts = []
    if y: parts.append(f"{y} {T['year'] if y == 1 else T['years']}")
    if m or not y: parts.append(f"{m} {T['month'] if m == 1 else T['months']}")
    return ", ".join(parts)


def top_langs(langs):
    total = sum(s for _, s in langs) or 1
    top = [(n, s / total * 100) for n, s in langs[:MAX_LANGS]]
    rest = 100 - sum(p for _, p in top)
    if len(langs) > MAX_LANGS and rest >= 0.5:
        top[-1] = ("Other", top[-1][1] + rest) if False else top[-1]
    return top


def daylabel(n):
    return f"{n} {T['day'] if n == 1 else T['days']}"


def font_face(name, key, weight=400):
    return (f'@font-face{{font-family:"{name}";font-weight:{weight};'
            f'src:url(data:font/woff2;base64,{FONTS[key]}) format("woff2");}}')


# --------------------------------------------------------------------------- #
#  Tarjeta moderna
# --------------------------------------------------------------------------- #
SHADES = ["#f5f5f5", "#bdbdbd", "#8c8c8c", "#636363", "#454545", "#2e2e2e"]
HEAT = ["#1b1b1b", "#3a3a3a", "#6e6e6e", "#a9a9a9", "#f2f2f2"]


def card(d):
    W, P = 900, 32
    IW = W - 2 * P
    cur, best = streaks(d["days"])
    o = []
    add = o.append
    delay = [0.0]

    def nxt(step=0.06):
        delay[0] += step
        return f'style="animation-delay:{delay[0]:.2f}s"'

    # ---- cabecera
    add(f'<g class="f" {nxt()}>')
    add(f'<text x="{P}" y="62" class="h1">{T["title"]}</text>')
    add(f'<text x="{P}" y="88" class="mono muted" font-size="14">{T["since"]} {d["created"].year}  ·  '
        f'{T["updated"]} {dt.date.today().strftime("%Y-%m-%d")}</text>')
    add(f'<text x="{W-P}" y="62" class="mono big" text-anchor="end">{fmt(d["contrib_year"])}</text>')
    add(f'<text x="{W-P}" y="86" class="lbl2 muted" text-anchor="end">{T["contrib_year"]}</text>')
    add('</g>')
    add(f'<line x1="{P}" x2="{W-P}" y1="112" y2="112" stroke="#242424"/>')

    # ---- tiles
    tiles = [
        (T["commits"], fmt(d["commits_year"]), T["commits_sub"].format(fmt(d["commits_total"]))),
        (T["stars"], fmt(d["stars"]), T["stars_sub"].format(fmt(d["forks"]))),
        (T["prs"], fmt(d["prs"]), ""),
        (T["issues"], fmt(d["issues"]), ""),
        (T["repos"], fmt(d["repos_total"]), T["repos_sub"].format(d["repos_public"])),
        (T["followers"], fmt(d["followers"]), T["followers_sub"].format(d["following"])),
        (T["cur_streak"], str(cur), T["days"]),
        (T["best_streak"], str(best), T["days"]),
    ]
    gap, tw, th = 12, (IW - 36) / 4, 76
    for i, (label, value, sub) in enumerate(tiles):
        x, y = P + (i % 4) * (tw + gap), 132 + (i // 4) * (th + gap)
        add(f'<g class="f" {nxt()}>')
        add(f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="10" fill="#131313" stroke="#232323"/>')
        add(f'<text x="{x+16:.1f}" y="{y+27}" class="lbl muted">{esc(label.upper())}</text>')
        add(f'<text x="{x+16:.1f}" y="{y+60}" class="mono val">{esc(value)}</text>')
        if sub:
            add(f'<text x="{x+tw-16:.1f}" y="{y+60}" class="lbl2 dim" text-anchor="end">{esc(sub)}</text>')
        add('</g>')

    # ---- heatmap
    hy = 334
    add(f'<text x="{P}" y="{hy}" class="lbl muted f" {nxt()}>{T["contributions"].upper()} · '
        f'{T["last12"].upper()}</text>')
    weeks = d["weeks"][-53:]
    nz = sorted(c for w in weeks for _, c in w if c)
    q = [nz[int(len(nz) * p)] if nz else 1 for p in (0.25, 0.5, 0.75)]
    level = lambda c: 0 if c == 0 else 1 + sum(c > t for t in q)
    cs, cg = 12, 3
    gy = hy + 34
    last_m, last_col = None, -9
    for wi, week in enumerate(weeks):
        m = dt.date.fromisoformat(week[0][0]).month
        if m != last_m and wi - last_col >= 3 and wi < len(weeks) - 1:
            name = dt.date(2000, m, 1).strftime("%b")
            if LANG == "es":
                name = "Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic".split()[m - 1]
            add(f'<text x="{P + wi*(cs+cg)}" y="{gy-9}" class="lbl2 dim f" {nxt(0)}>{name}</text>')
            last_col = wi
        last_m = m
    for wi, week in enumerate(weeks):
        add(f'<g class="pop" style="animation-delay:{0.9 + wi*0.012:.3f}s">')
        for date, c in week:
            di = (dt.date.fromisoformat(date).weekday() + 1) % 7  # domingo = 0
            add(f'<rect x="{P + wi*(cs+cg)}" y="{gy + di*(cs+cg)}" width="{cs}" height="{cs}" rx="2.5" '
                f'fill="{HEAT[level(c)]}"><title>{date}: {c}</title></rect>')
        add('</g>')
    ly = gy + 7 * (cs + cg) + 14
    lx = W - P - 5 * (cs - 2 + 4) - 34
    add(f'<g class="f" style="animation-delay:1.5s">')
    add(f'<text x="{lx-8}" y="{ly+9}" class="lbl2 dim" text-anchor="end">{T["less"]}</text>')
    for i, c in enumerate(HEAT):
        add(f'<rect x="{lx + i*14}" y="{ly}" width="10" height="10" rx="2" fill="{c}"/>')
    add(f'<text x="{lx + 5*14 + 4}" y="{ly+9}" class="lbl2 dim">{T["more"]}</text>')
    add('</g>')

    # ---- lenguajes
    langs = top_langs(d["langs"])
    by = ly + 52
    delay[0] = 1.5
    add(f'<text x="{P}" y="{by}" class="lbl muted f" {nxt()}>{T["langs"].upper()}</text>')
    bar_y = by + 16
    add(f'<clipPath id="bar"><rect x="{P}" y="{bar_y}" width="{IW}" height="10" rx="5"/></clipPath>')
    add(f'<rect x="{P}" y="{bar_y}" width="{IW}" height="10" rx="5" fill="#1b1b1b"/>')
    add(f'<g clip-path="url(#bar)"><g class="grow" style="animation-delay:1.65s">')
    x, tot = P, sum(p for _, p in langs) or 1
    for i, (n, p) in enumerate(langs):
        w = IW * p / tot
        add(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w-2, 1):.1f}" height="10" fill="{SHADES[i]}"/>')
        x += w
    add('</g></g>')
    col_w = IW / 3
    for i, (n, p) in enumerate(langs):
        cx, cy = P + (i % 3) * col_w, bar_y + 42 + (i // 3) * 26
        add(f'<g class="f" {nxt()}>')
        add(f'<circle cx="{cx+5:.1f}" cy="{cy-4}" r="5" fill="{SHADES[i]}" stroke="#3a3a3a"/>')
        add(f'<text x="{cx+18:.1f}" y="{cy}" class="lang">{esc(n)}</text>')
        add(f'<text x="{cx+col_w-24:.1f}" y="{cy}" class="mono muted" font-size="13" text-anchor="end">{p:.1f}%</text>')
        add('</g>')
    H = int(bar_y + 42 + ((len(langs) + 2) // 3) * 26 + 10)

    style = (font_face("Inter", "inter-400", 400) + font_face("Inter", "inter-600", 600)
             + font_face("Inter", "inter-700", 700) + font_face("JB", "jbmono-700", 700) + """
      text{font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;fill:#f5f5f5}
      .mono{font-family:JB,ui-monospace,Menlo,Consolas,monospace;font-weight:700}
      .h1{font-size:28px;font-weight:700;letter-spacing:-.5px}
      .big{font-size:34px}
      .val{font-size:26px}
      .lbl{font-size:11px;font-weight:600;letter-spacing:1.2px}
      .lbl2{font-size:12px;font-weight:400}
      .lang{font-size:13.5px;font-weight:600}
      .muted{fill:#8f8f8f}.dim{fill:#5f5f5f}
      .f{opacity:0;animation:in .55s ease-out forwards}
      .pop{opacity:0;animation:fade .35s ease-out forwards}
      .grow{transform-box:fill-box;transform-origin:left;transform:scaleX(0);
            animation:grow 1.1s cubic-bezier(.2,.8,.2,1) forwards}
      @keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
      @keyframes fade{to{opacity:1}}
      @keyframes grow{to{transform:scaleX(1)}}
      @media (prefers-reduced-motion:reduce){.f,.pop,.grow{animation:none;opacity:1;transform:none}}
    """)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="GitHub stats for {esc(d["login"])}">'
            f'<title>GitHub stats · {esc(d["login"])}</title><style>{style}</style>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="#0b0b0b" stroke="#262626"/>'
            + "".join(o) + "</svg>")


# --------------------------------------------------------------------------- #
#  Tarjeta moderna · versión celular (una columna, letra más grande)
# --------------------------------------------------------------------------- #
def card_mobile(d):
    W, P = 440, 22
    IW = W - 2 * P
    cur, best = streaks(d["days"])
    o = []
    add = o.append
    delay = [0.0]

    def nxt(step=0.06):
        delay[0] += step
        return f'style="animation-delay:{delay[0]:.2f}s"'

    add(f'<g class="f" {nxt()}>')
    add(f'<text x="{P}" y="50" class="h1">{T["title"]}</text>')
    add(f'<text x="{P}" y="74" class="mono muted" font-size="13">{T["since"]} {d["created"].year}  ·  '
        f'{dt.date.today().strftime("%Y-%m-%d")}</text>')
    add('</g>')
    add(f'<g class="f" {nxt()}>')
    add(f'<rect x="{P}" y="94" width="{IW}" height="74" rx="10" fill="#131313" stroke="#232323"/>')
    add(f'<text x="{P+16}" y="142" class="mono big">{fmt(d["contrib_year"])}</text>')
    add(f'<text x="{W-P-16}" y="128" class="lbl2 muted" text-anchor="end">{T["contrib_year"].rsplit(" ", 3)[0]}</text>')
    add(f'<text x="{W-P-16}" y="148" class="lbl2 muted" text-anchor="end">{" ".join(T["contrib_year"].rsplit(" ", 3)[1:])}</text>')
    add('</g>')

    tiles = [
        (T["commits"], fmt(d["commits_year"]), T["commits_sub"].format(fmt(d["commits_total"]))),
        (T["stars"], fmt(d["stars"]), T["stars_sub"].format(fmt(d["forks"]))),
        (T["prs"], fmt(d["prs"]), ""),
        (T["issues"], fmt(d["issues"]), ""),
        (T["repos"], fmt(d["repos_total"]), T["repos_sub"].format(d["repos_public"])),
        (T["followers"], fmt(d["followers"]), T["followers_sub"].format(d["following"])),
        (T["cur_streak"], str(cur), T["days"]),
        (T["best_streak"], str(best), T["days"]),
    ]
    gap, th = 12, 90
    tw = (IW - gap) / 2
    ty0 = 180
    for i, (label, value, sub) in enumerate(tiles):
        x, y = P + (i % 2) * (tw + gap), ty0 + (i // 2) * (th + gap)
        add(f'<g class="f" {nxt()}>')
        add(f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="10" fill="#131313" stroke="#232323"/>')
        add(f'<text x="{x+14:.1f}" y="{y+26}" class="lbl muted">{esc(label.upper())}</text>')
        add(f'<text x="{x+14:.1f}" y="{y+60}" class="mono val">{esc(value)}</text>')
        if sub:
            add(f'<text x="{x+14:.1f}" y="{y+79}" class="lbl3 dim">{esc(sub)}</text>')
        add('</g>')

    # mapa de contribuciones: últimas 26 semanas
    hy = ty0 + 4 * (th + gap) + 22
    add(f'<text x="{P}" y="{hy}" class="lbl muted f" {nxt()}>{T["contributions"].upper()}</text>')
    weeks = d["weeks"][-26:]
    nz = sorted(c for w in weeks for _, c in w if c)
    q = [nz[int(len(nz) * p)] if nz else 1 for p in (0.25, 0.5, 0.75)]
    level = lambda c: 0 if c == 0 else 1 + sum(c > t for t in q)
    cg = 3
    cs = (IW - 25 * cg) / 26
    gy = hy + 34
    last_m, last_col = None, -9
    for wi, week in enumerate(weeks):
        m = dt.date.fromisoformat(week[0][0]).month
        if m != last_m and wi - last_col >= 3 and wi < len(weeks) - 1:
            name = dt.date(2000, m, 1).strftime("%b")
            if LANG == "es":
                name = "Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic".split()[m - 1]
            add(f'<text x="{P + wi*(cs+cg):.1f}" y="{gy-9}" class="lbl3 dim">{name}</text>')
            last_col = wi
        last_m = m
    for wi, week in enumerate(weeks):
        add(f'<g class="pop" style="animation-delay:{0.7 + wi*0.02:.2f}s">')
        for date, c in week:
            di = (dt.date.fromisoformat(date).weekday() + 1) % 7
            add(f'<rect x="{P + wi*(cs+cg):.1f}" y="{gy + di*(cs+cg):.1f}" width="{cs:.1f}" height="{cs:.1f}" '
                f'rx="2.5" fill="{HEAT[level(c)]}"/>')
        add('</g>')

    # lenguajes
    langs = top_langs(d["langs"])
    by = gy + 7 * (cs + cg) + 34
    delay[0] = 1.3
    add(f'<text x="{P}" y="{by}" class="lbl muted f" {nxt()}>{T["langs"].upper()}</text>')
    bar_y = by + 16
    add(f'<clipPath id="bar"><rect x="{P}" y="{bar_y}" width="{IW}" height="10" rx="5"/></clipPath>')
    add(f'<rect x="{P}" y="{bar_y}" width="{IW}" height="10" rx="5" fill="#1b1b1b"/>')
    add(f'<g clip-path="url(#bar)"><g class="grow" style="animation-delay:1.4s">')
    x, tot = P, sum(p for _, p in langs) or 1
    for i, (n, p) in enumerate(langs):
        w = IW * p / tot
        add(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w-2, 1):.1f}" height="10" fill="{SHADES[i]}"/>')
        x += w
    add('</g></g>')
    col_w = (IW - 20) / 2
    for i, (n, p) in enumerate(langs):
        cx, cy = P + (i % 2) * (col_w + 20), bar_y + 42 + (i // 2) * 28
        add(f'<g class="f" {nxt()}>')
        add(f'<circle cx="{cx+5:.1f}" cy="{cy-5}" r="5" fill="{SHADES[i]}" stroke="#3a3a3a"/>')
        add(f'<text x="{cx+18:.1f}" y="{cy}" class="lang">{esc(n)}</text>')
        add(f'<text x="{cx+col_w:.1f}" y="{cy}" class="mono muted" font-size="14" text-anchor="end">{p:.1f}%</text>')
        add('</g>')
    H = int(bar_y + 42 + ((len(langs) + 1) // 2) * 28 + 6)

    style = (font_face("Inter", "inter-400", 400) + font_face("Inter", "inter-600", 600)
             + font_face("Inter", "inter-700", 700) + font_face("JB", "jbmono-700", 700) + """
      text{font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;fill:#f5f5f5}
      .mono{font-family:JB,ui-monospace,Menlo,Consolas,monospace;font-weight:700}
      .h1{font-size:28px;font-weight:700;letter-spacing:-.5px}
      .big{font-size:38px}
      .val{font-size:30px}
      .lbl{font-size:12.5px;font-weight:600;letter-spacing:1px}
      .lbl2{font-size:14px}
      .lbl3{font-size:12px}
      .lang{font-size:15px;font-weight:600}
      .muted{fill:#8f8f8f}.dim{fill:#5f5f5f}
      .f{opacity:0;animation:in .55s ease-out forwards}
      .pop{opacity:0;animation:fade .35s ease-out forwards}
      .grow{transform-box:fill-box;transform-origin:left;transform:scaleX(0);
            animation:grow 1.1s cubic-bezier(.2,.8,.2,1) forwards}
      @keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
      @keyframes fade{to{opacity:1}}
      @keyframes grow{to{transform:scaleX(1)}}
      @media (prefers-reduced-motion:reduce){.f,.pop,.grow{animation:none;opacity:1;transform:none}}
    """)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="GitHub stats for {esc(d["login"])}">'
            f'<title>GitHub stats · {esc(d["login"])}</title><style>{style}</style>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="#0b0b0b" stroke="#262626"/>'
            + "".join(o) + "</svg>")


# --------------------------------------------------------------------------- #
#  Tarjeta terminal (neofetch)
# --------------------------------------------------------------------------- #
def terminal(d):
    W = 1000
    FS, LH, CW = 22, 25, 22 * 0.4
    X0, PY = 40, 84
    cur, best = streaks(d["days"])
    login = d["login"]
    prompt = f"{login}@github:~$ "
    cmd = "neofetch"

    ini = INITIALS[:6].center(10)
    art = [
        " .----------------------. ",
        " | .------------------. | ",
        " | | >_               | | ",
        " | |                  | | ",
        f" | |    {ini}    | | ",
        " | |                  | | ",
        " | |      ______      | | ",
        " | '------------------' | ",
        " |  [__]     o  o  o    | ",
        " '----------------------' ",
        "     ___|________|___     ",
        "    /________________\\    ",
    ]

    langs = top_langs(d["langs"])[:4]
    lang_str = ", ".join(f"{n} {p:.0f}%" for n, p in langs)
    head = f"{login}@github"
    info = [
        ("", head, "title"),
        ("", "-" * len(head), "dim"),
        (T["u_user"], d["name"], ""),
        (T["u_uptime"], uptime(d["created"]), ""),
        (T["u_repos"], f'{d["repos_total"]} ({d["repos_public"]} {T["public"]})', ""),
        (T["u_stars"], f'{fmt(d["stars"])}   {T["forks"]}: {fmt(d["forks"])}', ""),
        (T["u_commits"], f'{fmt(d["commits_year"])} {T["last_year"]} · {fmt(d["commits_total"])} {T["total"]}', ""),
        (T["u_prs"], f'{fmt(d["prs"])}   {T["issues_s"]}: {fmt(d["issues"])}', ""),
        (T["u_contrib"], f'{fmt(d["contrib_year"])} {T["last_year"]}', ""),
        (T["u_streak"], f'{daylabel(cur)} ({T["best"]}: {best})', ""),
        (T["u_followers"], f'{fmt(d["followers"])}   {T["following"]}: {fmt(d["following"])}', ""),
        (T["u_langs"], lang_str, ""),
    ]
    lab_w = max(len(l) for l, _, _ in info) + 2
    IX = X0 + 30 * CW
    max_chars = int((W - IX - 30) / CW)

    t_type0, t_per = 0.5, 0.09
    t_out = t_type0 + len(cmd) * t_per + 0.45
    line_step = 0.09
    o = []
    add = o.append
    y0 = PY + 50  # primera línea de salida

    # prompt + comando tecleado
    pw = len(prompt) * CW
    add(f'<text x="{X0}" y="{PY}" class="t" font-size="{FS}" xml:space="preserve">'
        f'<tspan class="dim">{esc(prompt)}</tspan></text>')
    keyt = ["0"] + [f"{(t_type0 + i*t_per):.3f}" for i in range(1, len(cmd) + 1)]
    vals = ";".join(f"{i*CW:.1f}" for i in range(len(cmd) + 1))
    begin_offsets = ";".join(f"{float(k)/ (t_type0 + len(cmd)*t_per + .001):.4f}" for k in keyt)
    dur = t_type0 + len(cmd) * t_per + 0.001
    add(f'<clipPath id="cmd"><rect x="{X0+pw:.1f}" y="{PY-24}" height="32" width="0">'
        f'<animate attributeName="width" dur="{dur:.3f}s" fill="freeze" calcMode="discrete" '
        f'keyTimes="{begin_offsets}" values="{vals}"/></rect></clipPath>')
    add(f'<text x="{X0+pw:.1f}" y="{PY}" class="t" font-size="{FS}" clip-path="url(#cmd)">{cmd}</text>')
    # cursor de tecleo
    xs = ";".join(f"{X0+pw+i*CW:.1f}" for i in range(len(cmd) + 1))
    add(f'<rect y="{PY-18}" width="{CW:.1f}" height="21" fill="#f2f2f2" x="{X0+pw:.1f}">'
        f'<animate attributeName="x" dur="{dur:.3f}s" fill="freeze" calcMode="discrete" '
        f'keyTimes="{begin_offsets}" values="{xs}"/>'
        f'<set attributeName="opacity" to="0" begin="{t_out-0.2:.2f}s" fill="freeze"/></rect>')

    # ASCII art
    for i, line in enumerate(art):
        add(f'<text x="{X0}" y="{y0 + i*LH}" class="t art o" font-size="{FS}" xml:space="preserve" '
            f'style="animation-delay:{t_out + i*0.04:.2f}s">{esc(line)}</text>')

    # info
    for i, (lab, val, kind) in enumerate(info):
        y = y0 + i * LH
        dl = f'style="animation-delay:{t_out + 0.2 + i*line_step:.2f}s"'
        if kind == "title":
            add(f'<text x="{IX:.1f}" y="{y}" class="t o" font-size="{FS}" {dl}>{esc(val)}</text>')
        elif kind == "dim":
            add(f'<text x="{IX:.1f}" y="{y}" class="t dim o" font-size="{FS}" {dl}>{esc(val)}</text>')
        else:
            v = val if len(val) <= max_chars - lab_w else val[:max_chars - lab_w - 1] + "…"
            add(f'<text x="{IX:.1f}" y="{y}" class="t o" font-size="{FS}" xml:space="preserve" {dl}>'
                f'<tspan class="dim">{esc((lab + ":").ljust(lab_w))}</tspan>{esc(v)}</text>')

    # paleta en escala de grises (como los bloques de color de neofetch)
    py_ = y0 + len(info) * LH - 6
    dl = f'style="animation-delay:{t_out + 0.25 + len(info)*line_step:.2f}s"'
    add(f'<g class="o" {dl}>')
    for i, c in enumerate(["#0b0b0b", "#2a2a2a", "#4a4a4a", "#6e6e6e", "#939393", "#b8b8b8", "#dcdcdc", "#ffffff"]):
        add(f'<rect x="{IX + i*3*CW:.1f}" y="{py_}" width="{3*CW:.1f}" height="18" fill="{c}" stroke="#3a3a3a" stroke-width=".5"/>')
    add('</g>')

    # prompt final con cursor parpadeando
    fy = max(y0 + len(art) * LH, py_ + 18) + 46
    t_end = t_out + 0.35 + len(info) * line_step
    add(f'<g class="o" style="animation-delay:{t_end:.2f}s">'
        f'<text x="{X0}" y="{fy}" class="t dim" font-size="{FS}" xml:space="preserve">{esc(prompt)}</text></g>')
    add(f'<rect x="{X0+pw:.1f}" y="{fy-18}" width="{CW:.1f}" height="21" fill="#f2f2f2" class="blink" '
        f'style="animation-delay:{t_end:.2f}s"/>')
    H = fy + 34

    style = font_face("VT323", "vt323") + """
      .t{font-family:VT323,"Courier New",monospace;fill:#f2f2f2}
      .dim{fill:#8a8a8a}
      .art{fill:#cfcfcf}
      .o{opacity:0;animation:show .12s linear forwards}
      .blink{opacity:0;animation:blink 1s steps(1) infinite}
      @keyframes show{from{opacity:0}to{opacity:1}}
      @keyframes blink{0%{opacity:1}50%{opacity:0}}
      .crt{animation:flicker 5s infinite}
      @keyframes flicker{0%,100%{opacity:1}48%{opacity:1}49%{opacity:.88}50%{opacity:1}}
      @media (prefers-reduced-motion:reduce){.o{animation:none;opacity:1}}
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="neofetch · {esc(login)}">
<title>neofetch · {esc(login)}</title>
<defs><style>{style}</style>
<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".7"/></radialGradient>
<clipPath id="screen"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#screen)">
<rect width="{W}" height="{H}" fill="#0a0a0a"/>
<rect width="{W}" height="36" fill="#161616"/>
<circle cx="24" cy="18" r="6" fill="#5a5a5a"/><circle cx="44" cy="18" r="6" fill="#5a5a5a"/><circle cx="64" cy="18" r="6" fill="#5a5a5a"/>
<text x="{W/2}" y="24" text-anchor="middle" class="t" font-size="20" style="fill:#777">{esc(login)}@github: ~ — bash</text>
<g class="crt" filter="url(#glow)">{"".join(o)}</g>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</g></svg>'''


# --------------------------------------------------------------------------- #
def main():
    if "--demo" in sys.argv:
        data = demo()
    else:
        token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
        login = os.environ.get("GH_USER")
        if not token or not login:
            raise SystemExit("Faltan STATS_TOKEN y/o GH_USER")
        data = fetch(login, token)
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "stats-card.svg").write_text(card(data), encoding="utf-8")
    (OUT_DIR / "stats-card-mobile.svg").write_text(card_mobile(data), encoding="utf-8")
    print("✓ stats-card.svg y stats-card-mobile.svg generados")


if __name__ == "__main__":
    main()
