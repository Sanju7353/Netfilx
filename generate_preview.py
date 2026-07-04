"""
Builds the social link-preview banner + home-screen icons.

- static/preview.png   (1200x630)  -> the card shown when you share the link
- static/icon-512.png / icon-192.png -> "Add to Home Screen" icon

Run once (outputs are committed, so the server never needs Pillow):
    pip install Pillow
    python generate_preview.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "static"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"

RED = (229, 9, 20)
PINK = (255, 138, 160)
WHITE = (245, 245, 245)
MUTED = (170, 170, 170)


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def vgrad(w, h, top, bottom):
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return base


def radial_glow(w, h, cx, cy, radius, color, strength=0.55):
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    steps = 60
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(strength * 255 * (1 - i / steps) ** 1.6)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    return glow


def heart(draw, cx, cy, w, color):
    """Filled heart centered at (cx, cy), total width w."""
    r = w / 4
    draw.ellipse([cx - 2 * r, cy - 2 * r, cx, cy], fill=color)
    draw.ellipse([cx, cy - 2 * r, cx + 2 * r, cy], fill=color)
    draw.polygon([(cx - 2 * r + 2, cy - r), (cx + 2 * r - 2, cy - r),
                  (cx, cy + 2.05 * r)], fill=color)


def center_text(draw, cx, y, text, font, fill, tracking=0):
    if tracking:
        widths = [draw.textlength(ch, font=font) + tracking for ch in text]
        total = sum(widths) - tracking
        x = cx - total / 2
        for ch, wch in zip(text, widths):
            draw.text((x, y), ch, font=font, fill=fill)
            x += wch
        return
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, y), text, font=font, fill=fill)


# --------------------------------------------------------------------------- #
def build_banner():
    W, H = 1200, 630
    img = vgrad(W, H, (26, 6, 9), (9, 9, 11)).convert("RGBA")
    img.alpha_composite(radial_glow(W, H, W // 2, 250, 620, RED, 0.5))
    d = ImageDraw.Draw(img)

    # faint watermark hearts
    for (hx, hy, hw, a) in [(150, 500, 90, 26), (1050, 150, 120, 22), (980, 520, 70, 24)]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        heart(ld, hx, hy, hw, RED + (a,))
        img.alpha_composite(layer)

    cx = W // 2
    center_text(d, cx, 150, "MY FAVORITE PERSON", _font(FONT_BOLD, 40), PINK, tracking=8)

    # "Musku" + heart, centered as a group
    name_font = _font(FONT_BOLD, 150)
    name = "Musku"
    nw = d.textlength(name, font=name_font)
    gap, hw = 34, 96
    group = nw + gap + hw
    nx = cx - group / 2
    d.text((nx, 235), name, font=name_font, fill=WHITE)
    heart(d, nx + nw + gap + hw / 2, 322, hw, RED)

    # red accent underline
    d.rounded_rectangle([cx - 70, 445, cx + 70, 453], radius=4, fill=RED)

    center_text(d, cx, 486, "A private love story — made just for you",
                _font(FONT_REG, 34), MUTED)
    center_text(d, cx, 556, "Tap to open  •  our secret code inside",
                _font(FONT_REG, 26), (120, 120, 120))

    img.convert("RGB").save(OUT / "preview.png", "PNG")
    print("  ✓ static/preview.png (1200x630)")


def build_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * 0.06)
    d.rounded_rectangle([pad, pad, size - pad, size - pad],
                        radius=int(size * 0.22), fill=(15, 15, 17, 255))
    img.alpha_composite(radial_glow(size, size, size // 2, int(size * 0.42),
                                    int(size * 0.55), RED, 0.5))
    d = ImageDraw.Draw(img)
    heart(d, size // 2, int(size * 0.46), int(size * 0.52), RED)
    img.save(OUT / f"icon-{size}.png", "PNG")
    print(f"  ✓ static/icon-{size}.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_banner()
    build_icon(512)
    build_icon(192)
    print("Done.")
