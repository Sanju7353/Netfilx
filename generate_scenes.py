"""
🎨 generate_scenes.py — builds cinematic themed SVG backdrops.

These are hand-crafted vector "worlds" (beach, mountains, galaxy, horror,
action, aurora, ...). The web app composites your girlfriend's photo INTO each
scene, so she stars in every genre even if her photos are all one theme.

Run once (auto-runs on server start too):
    python generate_scenes.py

Output: static/scenes/*.svg
"""

from __future__ import annotations
import math
import random
from pathlib import Path

W, H = 1200, 1500
OUT = Path(__file__).resolve().parent / "static" / "scenes"

HEART = ("M12 21 C 4 15, 1 10, 4.5 6.5 C 6.8 4.2, 10 5, 12 8 "
         "C 14 5, 17.2 4.2, 19.5 6.5 C 23 10, 20 15, 12 21 Z")


def f(n): return f"{n:.1f}"


# --------------------------------------------------------------------------- #
#  Element builders
# --------------------------------------------------------------------------- #
def sky(c1, c2, c3=None):
    stops = f'<stop offset="0" stop-color="{c1}"/>'
    if c3:
        stops += f'<stop offset="0.55" stop-color="{c2}"/><stop offset="1" stop-color="{c3}"/>'
    else:
        stops += f'<stop offset="1" stop-color="{c2}"/>'
    return (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')


def glow(x, y, r, color, op=0.9):
    return (f'<radialGradient id="g{int(x)}{int(y)}" cx="0.5" cy="0.5" r="0.5">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#g{int(x)}{int(y)})"/>')


def disc(x, y, r, color, halo=None):
    s = ""
    if halo:
        s += glow(x, y, r * 3.2, halo, 0.65)
    s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{color}"/>'
    return s


def moon(x, y, r, color="#f4f6ff"):
    s = glow(x, y, r * 3, color, 0.5)
    s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{color}"/>'
    # craters
    rng = random.Random(7)
    for _ in range(5):
        cx = x + rng.uniform(-r * .6, r * .6)
        cy = y + rng.uniform(-r * .6, r * .6)
        cr = rng.uniform(r * .08, r * .2)
        s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(cr)}" fill="#d7dcf0" opacity="0.6"/>'
    return s


def rays(x, y, color, n=14, length=1600):
    g = f'<g opacity="0.16">'
    for i in range(n):
        a = (2 * math.pi * i) / n
        x2 = x + math.cos(a) * length
        y2 = y + math.sin(a) * length
        a2 = a + 0.12
        x3 = x + math.cos(a2) * length
        y3 = y + math.sin(a2) * length
        g += f'<path d="M{f(x)},{f(y)} L{f(x2)},{f(y2)} L{f(x3)},{f(y3)} Z" fill="{color}"/>'
    return g + "</g>"


def peaks(seed, base_y, min_h, max_h, count, color, opacity=1.0, snow=False):
    rng = random.Random(seed)
    d = f"M -40,{H} L -40,{f(base_y)} L 0,{f(base_y)} "
    step = W / count
    tops = []
    for i in range(count):
        px = (i + 0.5) * step
        py = base_y - rng.uniform(min_h, max_h)
        tops.append((px, py))
        d += f"L {f(px)},{f(py)} "
        vx = (i + 1) * step
        vy = base_y - rng.uniform(0, min_h * .35)
        d += f"L {f(vx)},{f(vy)} "
    d += f"L {W + 40},{f(base_y)} L {W + 40},{H} Z"
    s = f'<path d="{d}" fill="{color}" opacity="{opacity}"/>'
    if snow:
        for (px, py) in tops:
            cap = (f"M{f(px - 34)},{f(py + 40)} L{f(px)},{f(py)} L{f(px + 34)},{f(py + 40)} "
                   f"L{f(px + 18)},{f(py + 30)} L{f(px)},{f(py + 42)} L{f(px - 18)},{f(py + 30)} Z")
            s += f'<path d="{cap}" fill="#ffffff" opacity="0.9"/>'
    return s


def hills(seed, base_y, amp, color, opacity=1.0):
    rng = random.Random(seed)
    d = f"M -40,{H} L -40,{f(base_y)} "
    n = 6
    step = W / n
    x = 0
    prev = base_y
    d += f"L 0,{f(base_y)} "
    for i in range(1, n + 1):
        cx = (i - .5) * step
        cy = base_y - rng.uniform(0, amp)
        ex = i * step
        ey = base_y - rng.uniform(-amp * .3, amp * .3)
        d += f"Q {f(cx)},{f(cy)} {f(ex)},{f(ey)} "
    d += f"L {W + 40},{H} Z"
    return f'<path d="{d}" fill="{color}" opacity="{opacity}"/>'


def water(y, c1, c2):
    return (f'<linearGradient id="wtr" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
            f'<rect x="0" y="{f(y)}" width="{W}" height="{H - y:.0f}" fill="url(#wtr)"/>')


def reflection(x, top_y, water_y, r, color):
    g = f'<g opacity="0.35">'
    yy = water_y + 20
    while yy < H:
        g += (f'<rect x="{f(x - r)}" y="{f(yy)}" width="{f(2 * r)}" height="6" '
              f'rx="3" fill="{color}"/>')
        r *= .92
        yy += 26
    return g + "</g>"


def castle(color="#160a1e"):
    cx = W / 2
    s = f'<g fill="{color}">'
    # main keep
    s += f'<rect x="{f(cx-160)}" y="900" width="320" height="600"/>'
    # towers
    for tx in (cx - 250, cx - 160, cx + 60, cx + 190):
        s += f'<rect x="{f(tx)}" y="820" width="90" height="680"/>'
        s += f'<path d="M{f(tx-14)},820 L{f(tx+45)},700 L{f(tx+104)},820 Z"/>'
        # flag
        s += f'<line x1="{f(tx+45)}" y1="700" x2="{f(tx+45)}" y2="660" stroke="{color}" stroke-width="4"/>'
        s += f'<path d="M{f(tx+45)},662 L{f(tx+90)},672 L{f(tx+45)},684 Z" fill="#E50914"/>'
    # gate
    s += f'<path d="M{f(cx-40)},1500 L{f(cx-40)},1180 Q{f(cx)},1120 {f(cx+40)},1180 L{f(cx+40)},1500 Z" fill="#050208"/>'
    s += "</g>"
    # lit windows
    win = '<g fill="#ffd27a" opacity="0.9">'
    rng = random.Random(11)
    for _ in range(10):
        wx = cx - 140 + rng.uniform(0, 280)
        wy = 980 + rng.uniform(0, 380)
        win += f'<rect x="{f(wx)}" y="{f(wy)}" width="10" height="16" rx="2"/>'
    return s + win + "</g>"


def city(color="#0a0f1e", lit="#ffd27a", seed=3):
    rng = random.Random(seed)
    s = f'<g fill="{color}">'
    windows = f'<g fill="{lit}">'
    x = -20
    while x < W + 20:
        bw = rng.uniform(60, 130)
        bh = rng.uniform(260, 620)
        by = H - bh
        s += f'<rect x="{f(x)}" y="{f(by)}" width="{f(bw)}" height="{f(bh)}"/>'
        # windows grid
        for gy in range(int(by) + 24, H - 20, 34):
            for gx in range(int(x) + 12, int(x + bw) - 12, 26):
                if rng.random() < 0.5:
                    op = rng.uniform(.4, 1)
                    windows += f'<rect x="{gx}" y="{gy}" width="9" height="12" opacity="{op:.2f}"/>'
        x += bw + rng.uniform(4, 16)
    return s + "</g>" + windows + "</g>"


def pines(seed, base_y, color, count=10, scale=1.0):
    rng = random.Random(seed)
    s = f'<g fill="{color}">'
    for i in range(count):
        x = (i + .5) * (W / count) + rng.uniform(-30, 30)
        hgt = rng.uniform(120, 220) * scale
        w = hgt * .5
        y = base_y
        s += (f'<path d="M{f(x)},{f(y)} L{f(x-w/2)},{f(y)} L{f(x)},{f(y-hgt*.55)} '
              f'L{f(x-w*.35)},{f(y-hgt*.5)} L{f(x)},{f(y-hgt)} '
              f'L{f(x+w*.35)},{f(y-hgt*.5)} L{f(x+w/2)},{f(y)} Z"/>')
    return s + "</g>"


def dead_trees(seed, base_y, color="#05070c", count=4):
    rng = random.Random(seed)
    s = f'<g stroke="{color}" fill="none" stroke-linecap="round">'
    for i in range(count):
        x = (i + .5) * (W / count) + rng.uniform(-40, 40)
        hgt = rng.uniform(260, 420)
        s += f'<path d="M{f(x)},{H} L{f(x)},{f(base_y-hgt)}" stroke-width="{rng.uniform(8,14):.0f}"/>'
        # branches
        for _ in range(int(rng.uniform(4, 7))):
            by = base_y - rng.uniform(hgt * .3, hgt)
            bl = rng.uniform(40, 110)
            dirn = rng.choice([-1, 1])
            s += (f'<path d="M{f(x)},{f(by)} q {f(dirn*bl*.5)},{f(-bl*.4)} '
                  f'{f(dirn*bl)},{f(-bl*.2)}" stroke-width="{rng.uniform(3,6):.0f}"/>')
    return s + "</g>"


def graves(seed, base_y, color="#0b0d14", count=7):
    rng = random.Random(seed)
    s = f'<g fill="{color}">'
    for i in range(count):
        x = (i + .5) * (W / count) + rng.uniform(-30, 30)
        w = rng.uniform(50, 80)
        h = rng.uniform(70, 120)
        tilt = rng.uniform(-4, 4)
        s += (f'<g transform="rotate({tilt:.1f} {f(x)} {f(base_y)})">'
              f'<path d="M{f(x-w/2)},{f(base_y)} L{f(x-w/2)},{f(base_y-h+w/2)} '
              f'A {f(w/2)},{f(w/2)} 0 0 1 {f(x+w/2)},{f(base_y-h+w/2)} '
              f'L{f(x+w/2)},{f(base_y)} Z"/>'
              f'<rect x="{f(x-6)}" y="{f(base_y-h+w/2)}" width="12" height="34" fill="{color}"/>'
              f'<rect x="{f(x-20)}" y="{f(base_y-h+w/2+8)}" width="40" height="10" fill="{color}"/></g>')
    return s + "</g>"


def flowers_field(seed, base_y, count=26):
    rng = random.Random(seed)
    palette = ["#ff5e7e", "#ffd54a", "#ff9ad5", "#ffffff", "#ff7eb3", "#ffb347"]
    s = f'<rect x="0" y="{f(base_y)}" width="{W}" height="{H-base_y:.0f}" fill="#2b6b3a"/>'
    for _ in range(count):
        x = rng.uniform(0, W)
        y = rng.uniform(base_y + 30, H - 20)
        sc = rng.uniform(.6, 1.4) * (0.6 + (y - base_y) / (H - base_y))
        col = rng.choice(palette)
        s += f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x)}" y2="{f(y+26*sc)}" stroke="#2e8b57" stroke-width="{2*sc:.1f}"/>'
        for k in range(6):
            a = k * math.pi / 3
            px = x + math.cos(a) * 9 * sc
            py = y + math.sin(a) * 9 * sc
            s += f'<circle cx="{f(px)}" cy="{f(py)}" r="{6*sc:.1f}" fill="{col}"/>'
        s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{5*sc:.1f}" fill="#ffde59"/>'
    return s


def aurora(seed):
    rng = random.Random(seed)
    cols = ["#43e97b", "#38f9d7", "#7afcff", "#b388ff"]
    s = '<g filter="url(#soft)" opacity="0.55">'
    for i in range(4):
        col = cols[i % len(cols)]
        base = 180 + i * 60
        d = f"M -50,{base} "
        x = 0
        while x <= W + 50:
            d += f"L {x},{base + math.sin(x/160 + i)*70 + rng.uniform(-20,20):.0f} "
            x += 90
        s += (f'<linearGradient id="au{i}" x1="0" y1="0" x2="0" y2="1">'
              f'<stop offset="0" stop-color="{col}" stop-opacity="0.9"/>'
              f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient>')
        s += f'<path d="{d} L {W+50},600 L -50,600 Z" fill="url(#au{i})"/>'
    return s + "</g>"


def clouds(seed, count=6, y_range=(120, 620), color="#ffffff", op=0.85):
    rng = random.Random(seed)
    s = f'<g fill="{color}" opacity="{op}" filter="url(#soft)">'
    for _ in range(count):
        cx = rng.uniform(80, W - 80)
        cy = rng.uniform(*y_range)
        sc = rng.uniform(.7, 1.5)
        for dx, dy, r in [(-70, 10, 46), (-20, -14, 60), (40, -6, 54), (95, 12, 44), (10, 22, 70)]:
            s += f'<ellipse cx="{f(cx+dx*sc)}" cy="{f(cy+dy*sc)}" rx="{f(r*sc)}" ry="{f(r*sc*.7)}"/>'
    return s + "</g>"


def particles(kind, seed, count, color="#ffffff"):
    rng = random.Random(seed)
    s = "<g>"
    for _ in range(count):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        if kind == "stars":
            r = rng.uniform(.6, 2.4)
            s += f'<circle cx="{f(x)}" cy="{f(y*0.7)}" r="{f(r)}" fill="{color}" opacity="{rng.uniform(.3,1):.2f}"/>'
        elif kind == "snow":
            r = rng.uniform(2, 6)
            s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#ffffff" opacity="{rng.uniform(.4,.9):.2f}"/>'
        elif kind == "rain":
            ln = rng.uniform(18, 40)
            s += (f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x-8)}" y2="{f(y+ln)}" '
                  f'stroke="#bcd4ff" stroke-width="1.6" opacity="{rng.uniform(.2,.5):.2f}"/>')
        elif kind == "petals":
            sc = rng.uniform(.6, 1.4)
            rot = rng.uniform(0, 360)
            col = rng.choice(["#ff9ad5", "#ff7eb3", "#ffd1e8", "#ff5e7e"])
            s += (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{7*sc:.1f}" ry="{3.4*sc:.1f}" '
                  f'fill="{col}" opacity="{rng.uniform(.5,.9):.2f}" transform="rotate({rot:.0f} {f(x)} {f(y)})"/>')
        elif kind == "hearts":
            sc = rng.uniform(.5, 1.6)
            rot = rng.uniform(-25, 25)
            col = rng.choice(["#E50914", "#ff5e7e", "#ff9ad5"])
            s += (f'<path d="{HEART}" fill="{col}" opacity="{rng.uniform(.35,.8):.2f}" '
                  f'transform="translate({f(x)},{f(y)}) scale({sc:.2f}) rotate({rot:.0f})"/>')
        elif kind == "sparkles":
            sc = rng.uniform(.5, 1.8)
            col = rng.choice([color, "#fff6c8", "#ffd54a"])
            s += (f'<path d="M0,-12 L3,-3 L12,0 L3,3 L0,12 L-3,3 L-12,0 L-3,-3 Z" '
                  f'fill="{col}" opacity="{rng.uniform(.4,.95):.2f}" '
                  f'transform="translate({f(x)},{f(y*0.8)}) scale({sc:.2f})"/>')
        elif kind == "fireflies":
            yy = rng.uniform(H * .45, H)
            r = rng.uniform(2, 4)
            s += glow(x, yy, r * 6, "#c6ff8a", 0.5)
            s += f'<circle cx="{f(x)}" cy="{f(yy)}" r="{f(r)}" fill="#eaffb0"/>'
    return s + "</g>"


def bats(seed, count=5):
    rng = random.Random(seed)
    s = '<g fill="#05060a">'
    bat = ("M-14,0 C-9,-7 -4,-6 0,0 C4,-6 9,-7 14,0 "
           "C9,-3 4,-2 0,2 C-4,-2 -9,-3 -14,0 Z")
    for _ in range(count):
        x = rng.uniform(80, W - 80)
        y = rng.uniform(120, 460)
        sc = rng.uniform(.7, 1.8)
        s += f'<path d="{bat}" transform="translate({f(x)},{f(y)}) scale({sc:.2f})"/>'
    return s + "</g>"


def fog(color="#0d0f18"):
    return (f'<g filter="url(#fog)" opacity="0.6">'
            f'<ellipse cx="{W*.3:.0f}" cy="{H-120}" rx="500" ry="120" fill="{color}"/>'
            f'<ellipse cx="{W*.7:.0f}" cy="{H-60}" rx="600" ry="140" fill="{color}"/></g>')


def vignette(strength=0.65):
    return (f'<radialGradient id="vig" cx="0.5" cy="0.42" r="0.75">'
            f'<stop offset="0.55" stop-color="#000000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000000" stop-opacity="{strength}"/></radialGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<linearGradient id="btm" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0.65" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0.5"/></linearGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#btm)"/>')


DEFS = ('<defs>'
        '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="14"/></filter>'
        '<filter id="fog" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="40"/></filter>'
        '</defs>')


def wrap(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'preserveAspectRatio="xMidYMid slice">{DEFS}{body}</svg>')


# --------------------------------------------------------------------------- #
#  Scene definitions
# --------------------------------------------------------------------------- #
def scene_beach():
    b = sky("#7fd8e8", "#bfeaf0", "#ffe4b5")
    b += disc(900, 300, 90, "#fff6d5", "#ffe9a8")
    b += clouds(2, 4, (120, 320))
    b += hills(5, 980, 90, "#3aa6a0", .9)
    b += water(1000, "#1f8f9e", "#0f6b7a")
    b += reflection(900, 300, 1000, 60, "#ffe9a8")
    b += f'<path d="M0,1180 Q600,1120 {W},1200 L{W},{H} L0,{H} Z" fill="#f2d7a0"/>'
    b += f'<path d="M0,1200 Q600,1150 {W},1220 L{W},1260 Q600,1200 0,1250 Z" fill="#fff3d6" opacity="0.7"/>'
    b += vignette(.5)
    return b


def scene_ocean():
    b = sky("#2b3a67", "#3f6fa3", "#f6a35c")
    b += disc(600, 360, 110, "#ffd38a", "#ff9e5c")
    b += clouds(9, 4, (140, 340), "#ffd9b0", .5)
    b += water(760, "#2a5f86", "#0a2740")
    b += reflection(600, 360, 760, 90, "#ffcf87")
    b += particles("sparkles", 4, 20, "#ffe9c7")
    b += vignette(.55)
    return b


def scene_mountains():
    b = sky("#8fbfe0", "#cfe6f2", "#eef6fb")
    b += disc(880, 320, 70, "#fffdf5", "#fff3c4")
    b += clouds(3, 3, (180, 380), "#ffffff", .8)
    b += peaks(21, 1120, 380, 640, 5, "#5b7a96", .5)
    b += peaks(22, 1180, 300, 560, 6, "#3d5a75", .8, snow=True)
    b += peaks(23, 1240, 200, 380, 7, "#26384a", snow=True)
    b += pines(24, 1420, "#152430", 12)
    b += vignette(.5)
    return b


def scene_snow():
    b = sky("#c3d4e6", "#dfe9f3", "#f4f8fc")
    b += moon(300, 300, 66)
    b += peaks(31, 1160, 340, 560, 5, "#9fb3c9", .6, snow=True)
    b += peaks(32, 1240, 220, 420, 7, "#7d94ad", snow=True)
    b += pines(33, 1440, "#4a5c72", 11)
    b += f'<rect x="0" y="1360" width="{W}" height="140" fill="#eef4fb"/>'
    b += particles("snow", 34, 130)
    b += vignette(.4)
    return b


def scene_sunset():
    b = sky("#3a1a4a", "#c94b6a", "#ff9e5c")
    b += rays(600, 720, "#ffd27a")
    b += disc(600, 740, 150, "#ffe08a", "#ff7e5f")
    b += water(880, "#a83a5b", "#3a1030")
    b += reflection(600, 740, 880, 120, "#ffcf87")
    b += hills(41, 900, 60, "#2a0d24", 1)
    b += particles("sparkles", 42, 14, "#ffe9c7")
    b += vignette(.55)
    return b


def scene_galaxy():
    b = sky("#0a0620", "#1a1147", "#3a1c71")
    b += glow(820, 460, 620, "#7b3fe4", .55)
    b += glow(360, 320, 460, "#e94fd0", .35)
    b += particles("stars", 51, 240, "#ffffff")
    b += particles("sparkles", 52, 22, "#cfe3ff")
    b += disc(300, 380, 8, "#fff", "#bcd4ff")
    b += vignette(.7)
    return b


def scene_starrynight():
    b = sky("#0b1030", "#141e46", "#24325f")
    b += moon(920, 300, 80)
    b += particles("stars", 61, 200, "#ffffff")
    b += hills(62, 1150, 120, "#0a0f24", 1)
    b += pines(63, 1420, "#060a18", 10)
    b += particles("fireflies", 64, 12)
    b += vignette(.6)
    return b


def scene_castle():
    b = sky("#3a1a5e", "#7b3f8f", "#f7a8c4")
    b += moon(300, 320, 70, "#fff2fb")
    b += particles("stars", 71, 90, "#ffe9ff")
    b += clouds(72, 3, (260, 460), "#f7c9e0", .4)
    b += castle("#241033")
    b += particles("sparkles", 73, 20, "#ffe9ff")
    b += vignette(.55)
    return b


def scene_royal():
    b = sky("#2a0a12", "#7a0b1e", "#c9a227")
    b += rays(600, 500, "#ffe08a", 18)
    b += glow(600, 520, 520, "#ffd700", .4)
    b += f'<g opacity="0.25" stroke="#ffd700" fill="none" stroke-width="3">'
    for i in range(5):
        y = 1080 + i * 70
        b += f'<path d="M0,{y} Q{W/2},{y-40} {W},{y}"/>'
    b += "</g>"
    b += particles("sparkles", 81, 26, "#ffe9a8")
    b += vignette(.6)
    return b


def scene_neon():
    b = sky("#08061e", "#1a0b3e", "#3a0b5e")
    b += glow(300, 420, 420, "#00e5ff", .4)
    b += glow(900, 380, 420, "#ff2bd6", .4)
    b += city("#0a0820", "#00e5ff", seed=82)
    b += f'<rect x="0" y="1360" width="{W}" height="4" fill="#ff2bd6" opacity="0.8"/>'
    b += particles("sparkles", 83, 18, "#00e5ff")
    b += vignette(.6)
    return b


def scene_city():
    b = sky("#0c1330", "#1c2b52", "#3a4d7a")
    b += moon(950, 260, 60)
    b += particles("stars", 91, 90, "#dfe9ff")
    b += city("#0a1226", "#ffd27a", seed=92)
    b += vignette(.55)
    return b


def scene_action():
    b = sky("#1a0806", "#5e1508", "#ff6a2b")
    b += glow(600, 640, 560, "#ffb347", .55)
    b += glow(600, 640, 300, "#fff2c4", .7)
    b += city("#0a0604", "#ff9e5c", seed=101)
    b += rays(600, 640, "#ffcf87", 16, 900)
    b += particles("sparkles", 102, 26, "#ffd27a")
    b += vignette(.6)
    return b


def scene_horror():
    b = sky("#04060e", "#0a0f1e", "#16203a")
    b += moon(880, 300, 96, "#e8ecff")
    b += glow(880, 300, 340, "#4a5a8a", .35)
    b += bats(111, 6)
    b += particles("stars", 112, 70, "#aab6d8")
    b += hills(113, 1200, 90, "#050810", 1)
    b += dead_trees(114, 1500, "#04060c", 4)
    b += fog("#0a0f1e")
    b += vignette(.75)
    return b


def scene_graveyard():
    b = sky("#060810", "#101828", "#2a2140")
    b += moon(320, 320, 84, "#e0e6ff")
    b += glow(320, 320, 300, "#5a4a8a", .3)
    b += bats(121, 5)
    b += particles("stars", 122, 60, "#9fb0d8")
    b += hills(123, 1240, 60, "#070a14", 1)
    b += graves(124, 1440, "#0b0e18", 7)
    b += dead_trees(125, 1500, "#05070e", 3)
    b += fog("#0c1020")
    b += vignette(.75)
    return b


def scene_aurora():
    b = sky("#04081e", "#0a1236", "#122048")
    b += particles("stars", 131, 160, "#ffffff")
    b += aurora(132)
    b += peaks(133, 1200, 260, 460, 6, "#0a1428", 1, snow=True)
    b += f'<rect x="0" y="1380" width="{W}" height="120" fill="#0e1a30"/>'
    b += reflection(600, 300, 1380, 120, "#43e97b")
    b += vignette(.6)
    return b


def scene_desert():
    b = sky("#f7b267", "#f4845f", "#7a3b6a")
    b += disc(600, 560, 130, "#fff0c4", "#ff9e5c")
    b += f'<path d="M-20,1000 Q300,900 700,1000 T{W+20},1020 L{W+20},{H} L-20,{H} Z" fill="#d98c4a"/>'
    b += f'<path d="M-20,1160 Q400,1060 900,1160 T{W+20},1180 L{W+20},{H} L-20,{H} Z" fill="#b5673a"/>'
    b += f'<path d="M-20,1320 Q500,1240 {W+20},1320 L{W+20},{H} L-20,{H} Z" fill="#8a472b"/>'
    # cacti
    b += '<g fill="#1f3a2a">'
    for cx in (180, 1000):
        b += (f'<path d="M{cx},1420 L{cx},1240 Q{cx},1200 {cx+30},1200 Q{cx+50},1200 {cx+50},1250 '
              f'L{cx+50},1290 M{cx},1300 Q{cx-40},1300 {cx-40},1260 L{cx-40},1230" '
              f'stroke="#1f3a2a" stroke-width="26" fill="none" stroke-linecap="round"/>')
    b += "</g>"
    b += vignette(.5)
    return b


def scene_jungle():
    b = sky("#123a2a", "#1f6b4a", "#8fd66f")
    b += glow(700, 300, 460, "#eaffa8", .4)
    b += pines(141, 900, "#2e7d4a", 8, 1.6)
    b += pines(142, 1120, "#1f5c37", 10, 1.8)
    b += f'<rect x="0" y="1200" width="{W}" height="300" fill="#0f3d26"/>'
    # hanging leaves top
    b += '<g fill="#1f6b3a" opacity="0.9">'
    rng = random.Random(143)
    for x in range(0, W + 1, 90):
        h = rng.uniform(120, 260)
        b += f'<path d="M{x},0 Q{x+20},{h*.5:.0f} {x},{h:.0f} Q{x-20},{h*.5:.0f} {x},0 Z"/>'
    b += "</g>"
    b += particles("fireflies", 144, 14)
    b += vignette(.55)
    return b


def scene_fairy():
    b = sky("#2a1a4a", "#6a4b8f", "#b388ff")
    b += moon(880, 320, 60, "#fff2fb")
    b += particles("stars", 151, 80, "#ffe9ff")
    b += pines(152, 1160, "#241a3a", 9)
    b += flowers_field(153, 1220, 20)
    b += particles("fireflies", 154, 18)
    b += particles("sparkles", 155, 16, "#ffd6ff")
    b += vignette(.55)
    return b


def scene_flowers():
    b = sky("#ffd1e8", "#ffe4b5", "#cfeecf")
    b += disc(880, 300, 80, "#fff6d5", "#ffe9a8")
    b += clouds(161, 3, (140, 300), "#ffffff", .7)
    b += hills(162, 1080, 70, "#7cc47c", .9)
    b += flowers_field(163, 1120, 30)
    b += particles("petals", 164, 26)
    b += vignette(.4)
    return b


def scene_clouds():
    b = sky("#8ec5ff", "#bcdcff", "#eaf4ff")
    b += disc(900, 280, 84, "#fff8e0", "#fff0b8")
    b += clouds(171, 7, (160, 900), "#ffffff", .95)
    b += particles("sparkles", 172, 12, "#ffffff")
    b += vignette(.35)
    return b


def scene_rain():
    b = sky("#2b333f", "#3f4a58", "#59677a")
    b += moon(920, 260, 50, "#c8d2e0")
    b += clouds(181, 6, (120, 420), "#39424f", .9)
    b += city("#1a222e", "#ffcf87", seed=182)
    b += particles("rain", 183, 220)
    b += f'<rect x="0" y="1420" width="{W}" height="80" fill="#2a333f" opacity="0.6"/>'
    b += vignette(.55)
    return b


def scene_hearts():
    b = sky("#3a0812", "#8a0f24", "#ff5e7e")
    b += glow(600, 620, 560, "#ff3b6b", .45)
    b += particles("hearts", 191, 40)
    b += particles("sparkles", 192, 16, "#ffd6de")
    b += vignette(.55)
    return b


def scene_golden():
    b = sky("#5e3a0a", "#c98a1e", "#ffe08a")
    b += rays(600, 520, "#fff3c4", 20)
    b += disc(600, 540, 160, "#fff6d5", "#ffd700")
    b += hills(201, 1120, 60, "#7a5210", .8)
    b += particles("sparkles", 202, 30, "#fff2c4")
    b += vignette(.5)
    return b


def scene_pinksky():
    b = sky("#ff9a9e", "#ffb7c5", "#ffe0c4")
    b += disc(860, 320, 90, "#fff6ea", "#ffd0b8")
    b += clouds(211, 5, (160, 520), "#ffd9e4", .8)
    b += hills(212, 1120, 80, "#e08aa0", .7)
    b += particles("petals", 213, 22)
    b += vignette(.4)
    return b


def scene_sparkles():
    b = sky("#2a0b4a", "#5a1e8f", "#8a2be2")
    b += glow(600, 500, 560, "#b388ff", .45)
    b += particles("stars", 221, 120, "#ffffff")
    b += particles("sparkles", 222, 40, "#ffd54a")
    b += vignette(.6)
    return b


SCENES = {
    "beach": scene_beach, "ocean": scene_ocean, "mountains": scene_mountains,
    "snow": scene_snow, "sunset": scene_sunset, "galaxy": scene_galaxy,
    "starrynight": scene_starrynight, "castle": scene_castle, "royal": scene_royal,
    "neon": scene_neon, "city": scene_city, "action": scene_action,
    "horror": scene_horror, "graveyard": scene_graveyard, "aurora": scene_aurora,
    "desert": scene_desert, "jungle": scene_jungle, "fairy": scene_fairy,
    "flowers": scene_flowers, "clouds": scene_clouds, "rain": scene_rain,
    "hearts": scene_hearts, "golden": scene_golden, "pinksky": scene_pinksky,
    "sparkles": scene_sparkles,
}


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in SCENES.items():
        (OUT / f"{name}.svg").write_text(wrap(fn()), encoding="utf-8")
    return list(SCENES.keys())


if __name__ == "__main__":
    names = generate()
    print(f"Generated {len(names)} cinematic scenes into static/scenes/:")
    print("  " + ", ".join(names))
