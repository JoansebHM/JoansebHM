"""Genera botones retro en blanco y negro: btn-linkedin.svg, btn-gmail.svg, btn-portfolio.svg"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = (HERE / "fonts" / "vt323.b64").read_text().strip()

# Íconos pixel-art propios de 9x9 (1 = píxel encendido)
ICONS = {
    "user": [  # persona (perfil profesional)
        "...###...",
        "..#####..",
        "..#####..",
        "...###...",
        ".........",
        ".#######.",
        "#########",
        "#########",
        "#########",
    ],
    "mail": [  # sobre
        ".........",
        "#########",
        "##.....##",
        "#.#...#.#",
        "#..#.#..#",
        "#...#...#",
        "#.......#",
        "#########",
        ".........",
    ],
    "code": [  # </>
        "...........",
        "......#....",
        "..#...#.#..",
        ".#...#...#.",
        "#....#....#",
        ".#...#...#.",
        "..#.#...#..",
        "....#......",
        "...........",
    ],
    "globe": [  # monitor con ventana (portafolio)
        "#########",
        "#.......#",
        "#.##.##.#",
        "#.##.##.#",
        "#.......#",
        "#########",
        "....#....",
        "..#####..",
        ".........",
    ],
}

BUTTONS = [
    ("btn-linkedin.svg", "linkedin", "user"),
    ("btn-gmail.svg", "gmail", "mail"),
    ("btn-portfolio.svg", "portfolio", "globe"),
    ("btn-hackerrank.svg", "hackerrank", "code"),
]

FS = 26
CW = FS * 0.4
H = 48
PX = 2  # tamaño de cada píxel del ícono


def button(label, icon):
    text = f"> {label}"
    pad, icon_w, gap = 16, len(ICONS[icon][0]) * PX, 12
    tx = pad + icon_w + gap
    W = round(tx + len(text) * CW + pad)
    iy = (H - 9 * PX) / 2
    pixels = "".join(
        f'<rect x="{pad + c*PX}" y="{iy + r*PX:.0f}" width="{PX}" height="{PX}"/>'
        for r, row in enumerate(ICONS[icon]) for c, ch in enumerate(row) if ch == "#")
    cx = tx + len(text) * CW + 4
    b = 7  # largo de las esquinas
    corners = (f"M1 {1+b}V1H{1+b} M{W-1-b} 1H{W-1}V{1+b} "
               f"M{W-1} {H-1-b}V{H-1}H{W-1-b} M{1+b} {H-1}H1V{H-1-b}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
<title>{label}</title>
<defs><style>
@font-face{{font-family:"VT323";src:url(data:font/woff2;base64,{FONT}) format("woff2");}}
.t{{font-family:VT323,"Courier New",monospace;font-size:{FS}px;fill:#f2f2f2}}
.d{{fill:#8a8a8a}}
</style>
<filter id="g" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="1.8" result="x"/><feMerge><feMergeNode in="x"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="s" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1.5" fill="#000" opacity=".35"/></pattern>
</defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="4" fill="#0a0a0a" stroke="#3a3a3a"/>
<path d="{corners}" fill="none" stroke="#f2f2f2" stroke-width="2"/>
<g filter="url(#g)">
<g fill="#f2f2f2">{pixels}</g>
<text x="{tx}" y="{H/2 + 8}" class="t" xml:space="preserve"><tspan class="d">&gt;</tspan> {label}</text>
</g>
<rect width="{W}" height="{H}" fill="url(#s)"/>
</svg>'''


for fname, label, icon in BUTTONS:
    (OUT / fname).write_text(button(label, icon), encoding="utf-8")
    print("✓", fname)
