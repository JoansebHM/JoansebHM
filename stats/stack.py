#!/usr/bin/env python3
"""Genera assets/stack-card.svg: tu stack de tecnologías con el mismo estilo de la tarjeta de stats.

Edita STACK y ejecuta:  python stats/stack.py
Los íconos se descargan de Simple Icons al generar la tarjeta.
"""
import base64
import os
import re
import urllib.request
import html
from pathlib import Path

# ======================= CONFIGURACIÓN =======================
TITLE = "Tech stack"
SUBTITLE = "languages, frameworks & tools"
# Íconos de Simple Icons (https://simpleicons.org): usa el "slug" de cada tecnología
STACK = {
    "Languages": ["python", "typescript", "javascript"],
    "Frontend": ["react", "vite", "tailwindcss", "html5", "css", "figma"],
    "Backend": ["nodedotjs", "nestjs", "fastapi", "supabase"],
    "Databases": ["postgresql", "mysql"],
    "DevOps & CI/CD": ["docker", "githubactions", "gitlab", "git", "github", "vercel"],
    "OS": ["linux", "apple"],
}
ICON_CDN = "https://cdn.jsdelivr.net/npm/simple-icons@16/icons/{}.svg"
# =============================================================

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets"
FONTS = {k: (HERE / "fonts" / f"{k}.b64").read_text().strip()
         for k in ["inter-600", "inter-700", "jbmono-700"]}
esc = html.escape


def icon_path(slug):
    """Descarga el ícono oficial desde Simple Icons y devuelve su path (viewBox 24x24)."""
    local = os.environ.get("SI_DIR")
    if local:
        svg = Path(local, f"{slug}.svg").read_text()
    else:
        req = urllib.request.Request(ICON_CDN.format(slug), headers={"User-Agent": "profile-stats"})
        with urllib.request.urlopen(req, timeout=30) as r:
            svg = r.read().decode()
    title = re.search(r"<title>(.*?)</title>", svg)
    return re.search(r' d="([^"]+)"', svg).group(1), (title.group(1) if title else slug)


def face(name, key, weight=400):
    return (f'@font-face{{font-family:"{name}";font-weight:{weight};'
            f'src:url(data:font/woff2;base64,{FONTS[key]}) format("woff2");}}')


def build():
    W, P, GAP, COLS = 900, 32, 12, 2
    bw = (W - 2 * P - GAP) / COLS
    T, TG, IC = 48, 10, 24          # tile, separación, tamaño del ícono
    per_row = int((bw - 32 + TG) // (T + TG))

    icons = {slug: icon_path(slug) for items in STACK.values() for slug in items}
    o = []
    add = o.append
    delay = [0.0]

    def nxt(step=0.05):
        delay[0] += step
        return f'style="animation-delay:{delay[0]:.2f}s"'

    add(f'<g class="f" {nxt()}>')
    add(f'<text x="{P}" y="62" class="h1">{esc(TITLE)}</text>')
    add(f'<text x="{P}" y="88" class="mono muted" font-size="14">{esc(SUBTITLE)}</text>')
    add(f'<text x="{W-P}" y="62" class="mono big" text-anchor="end">{len(icons)}</text>')
    add(f'<text x="{W-P}" y="86" class="lbl2 muted" text-anchor="end">technologies</text>')
    add('</g>')
    add(f'<line x1="{P}" x2="{W-P}" y1="112" y2="112" stroke="#242424"/>')

    cats = list(STACK.items())
    y = 132
    for r in range(0, len(cats), COLS):
        pair = cats[r:r + COLS]
        nrows = max((len(items) + per_row - 1) // per_row for _, items in pair)
        bh = 44 + nrows * (T + TG) + 6
        for c, (cat, items) in enumerate(pair):
            bx = P + c * (bw + GAP)
            add(f'<g class="f" {nxt()}>')
            add(f'<rect x="{bx:.1f}" y="{y}" width="{bw:.1f}" height="{bh}" rx="10" fill="#131313" stroke="#232323"/>')
            add(f'<text x="{bx+16:.1f}" y="{y+27}" class="lbl muted">{esc(cat.upper())}</text>')
            for k, slug in enumerate(items):
                d, name = icons[slug]
                tx = bx + 16 + (k % per_row) * (T + TG)
                ty = y + 40 + (k // per_row) * (T + TG)
                add(f'<g><title>{esc(name)}</title>'
                    f'<rect x="{tx:.1f}" y="{ty}" width="{T}" height="{T}" rx="10" fill="#1c1c1c" stroke="#2f2f2f"/>'
                    f'<path transform="translate({tx + (T-IC)/2:.1f} {ty + (T-IC)/2:.1f}) scale({IC/24})" '
                    f'fill="#e6e6e6" d="{d}"/></g>')
            add('</g>')
        y += bh + GAP
    H = int(y - GAP + P)

    style = (face("Inter", "inter-600", 600) + face("Inter", "inter-700", 700)
             + face("JB", "jbmono-700", 700) + """
      text{font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;fill:#f5f5f5}
      .mono{font-family:JB,ui-monospace,Menlo,Consolas,monospace;font-weight:700}
      .h1{font-size:28px;font-weight:700;letter-spacing:-.5px}
      .big{font-size:34px}
      .lbl{font-size:11px;font-weight:600;letter-spacing:1.2px}
      .lbl2{font-size:12px}
      .muted{fill:#8f8f8f}.dim{fill:#5f5f5f}
      .f{opacity:0;animation:in .5s ease-out forwards}
      @keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
      @media (prefers-reduced-motion:reduce){.f{animation:none;opacity:1}}
    """)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="{esc(TITLE)}"><title>{esc(TITLE)}</title><style>{style}</style>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="#0b0b0b" stroke="#262626"/>'
            + "".join(o) + "</svg>")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "stack-card.svg").write_text(build(), encoding="utf-8")
    print("✓ stack-card.svg generado")
