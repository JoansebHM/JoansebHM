#!/usr/bin/env python3
"""Genera assets/banner.svg (escritorio) y assets/banner-mobile.svg (celular).

Terminal retro en blanco y negro con efecto de máquina de escribir.
Uso: python stats/banner.py
"""
import html
from pathlib import Path

# ======================= CONFIGURACIÓN =======================
PROMPT = "JoansebHM@github:~$ "
COMMAND = "whoami"
LINES_DESKTOP = ["Hi there, I'm Sebastian"]
LINES_MOBILE = ["Hi there,", "I'm Sebastian"]
FG, DIM, BG = "#f2f2f2", "#8a8a8a", "#0a0a0a"
DUR = 10.0  # duración del ciclo (s)
# =============================================================

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets"
FONT = (HERE / "fonts" / "vt323.b64").read_text().strip()
CW_EM = 0.4  # ancho de carácter de VT323
esc = html.escape


def build(W, H, fs1, fs2, y1, ys, lines, x0=48):
    cw1, cw2 = fs1 * CW_EM, fs2 * CW_EM
    f = lambda t: f"{t / DUR:.4f}"
    t_reset = DUR - 0.6

    # línea del comando
    pw = len(PROMPT) * cw1
    t = 0.6
    l1 = [(0.0, 0.0), (0.3, pw)]
    for i in range(1, len(COMMAND) + 1):
        l1.append((t + (i - 1) * 0.11, pw + i * cw1))
    t = l1[-1][0] + 0.6

    # líneas del nombre
    name_steps = []
    for line in lines:
        steps = [(0.0, 0.0)]
        for i in range(1, len(line) + 1):
            steps.append((t + (i - 1) * 0.13, i * cw2))
        name_steps.append(steps)
        t = steps[-1][0] + 0.45

    def anim_width(steps):
        times, vals = ["0"], [f"{steps[0][1]:.1f}"]
        for tt, w in steps[1:]:
            times.append(f(tt)); vals.append(f"{w:.1f}")
        times.append(f(t_reset)); vals.append("0")
        return (f'<animate attributeName="width" dur="{DUR}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{";".join(times)}" values="{";".join(vals)}"/>')

    # cursor
    c1 = lambda w: (x0 + w, y1 - fs1 * 0.8, cw1, fs1 * 0.92)
    cur = [(0.0, c1(0))] + [(tt, c1(w)) for tt, w in l1[1:]]
    for li, steps in enumerate(name_steps):
        c2 = lambda w, y=ys[li]: (x0 + w, y - fs2 * 0.75, cw2, fs2 * 0.8)
        start = steps[1][0] - 0.3 if len(steps) > 1 else t
        cur.append((start, c2(0)))
        cur += [(tt, c2(w)) for tt, w in steps[1:]]
    cur.append((t_reset, c1(0)))

    def anim_cursor(attr, idx):
        times = ["0"] + [f(tt) for tt, _ in cur[1:]]
        vals = [f"{c[idx]:.1f}" for _, c in cur]
        return (f'<animate attributeName="{attr}" dur="{DUR}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{";".join(times)}" values="{";".join(vals)}"/>')

    clips = [f'<clipPath id="l1"><rect x="{x0}" y="{y1 - fs1}" height="{fs1 * 1.4:.0f}" width="0">'
             f'{anim_width(l1)}</rect></clipPath>']
    texts = [f'<g clip-path="url(#l1)"><text x="{x0}" y="{y1}" class="t" font-size="{fs1}">'
             f'<tspan class="dim">{esc(PROMPT)}</tspan>{esc(COMMAND)}</text></g>']
    for i, (line, steps) in enumerate(zip(lines, name_steps)):
        clips.append(f'<clipPath id="n{i}"><rect x="{x0}" y="{ys[i] - fs2}" height="{fs2 * 1.3:.0f}" '
                     f'width="0">{anim_width(steps)}</rect></clipPath>')
        texts.append(f'<g clip-path="url(#n{i})"><text x="{x0}" y="{ys[i]}" class="t" font-size="{fs2}" '
                     f'xml:space="preserve">{esc(line)}</text></g>')

    title = " ".join(lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<defs><style>
@font-face{{font-family:"VT323";src:url(data:font/woff2;base64,{FONT}) format("woff2");}}
.t{{font-family:"VT323","Courier New",monospace;fill:{FG}}}
.dim{{fill:{DIM}}}
.crt{{animation:flicker 4s infinite}}
@keyframes flicker{{0%,100%{{opacity:1}}47%{{opacity:1}}48%{{opacity:.86}}49%{{opacity:1}}82%{{opacity:.94}}83%{{opacity:1}}}}
</style>
<filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
<radialGradient id="vig" cx="50%" cy="55%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".75"/></radialGradient>
<clipPath id="screen"><rect width="{W}" height="{H}" rx="14"/></clipPath>
{"".join(clips)}
</defs>
<g clip-path="url(#screen)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="36" fill="#161616"/>
<circle cx="24" cy="18" r="6" fill="#5a5a5a"/><circle cx="44" cy="18" r="6" fill="#5a5a5a"/><circle cx="64" cy="18" r="6" fill="#5a5a5a"/>
<text x="{W / 2}" y="24" text-anchor="middle" class="t" font-size="20" style="fill:#777">{esc(PROMPT.strip().rstrip("$").strip())} — bash</text>
<g class="crt" filter="url(#glow)">
{"".join(texts)}
<rect fill="{FG}" x="{x0}" y="{y1 - fs1 * 0.8:.1f}" width="{cw1:.1f}" height="{fs1 * 0.92:.1f}">
{anim_cursor("x", 0)}{anim_cursor("y", 1)}{anim_cursor("width", 2)}{anim_cursor("height", 3)}
<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/>
</rect>
</g>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</g>
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(
        build(1000, 260, 28, 72, 100, [196], LINES_DESKTOP), encoding="utf-8")
    (OUT / "banner-mobile.svg").write_text(
        build(600, 320, 26, 66, 92, [184, 258], LINES_MOBILE, x0=36), encoding="utf-8")
    print("✓ banner.svg y banner-mobile.svg generados")
