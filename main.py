#!/usr/bin/env python3
"""VELMARA - a travel poster for a place that isn't there.
Pure standard library. Run: python3 main.py -> writes /output/entry.png."""

import math, os, struct, zlib

W, H = 768, 1024
buf = bytearray(W * H * 3)

def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else v

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]

def pxa(x, y, c, a):
    if 0 <= x < W and 0 <= y < H and a > 0:
        i = (y * W + x) * 3
        buf[i] = clamp(int(buf[i] * (1 - a) + c[0] * a))
        buf[i + 1] = clamp(int(buf[i + 1] * (1 - a) + c[1] * a))
        buf[i + 2] = clamp(int(buf[i + 2] * (1 - a) + c[2] * a))

def mix(a, b, t):
    return (clamp(int(a[0] + (b[0] - a[0]) * t)),
            clamp(int(a[1] + (b[1] - a[1]) * t)),
            clamp(int(a[2] + (b[2] - a[2]) * t)))

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def vgrad(y0, y1, stops):
    for y in range(max(0, y0), min(H, y1)):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        c = stops[-1][1]
        for k in range(len(stops) - 1):
            p0, c0 = stops[k]; p1, c1 = stops[k + 1]
            if p0 <= t <= p1:
                c = mix(c0, c1, (t - p0) / max(1e-9, p1 - p0))
                break
        row = y * W * 3
        brow = BAYER[y & 3]
        for x in range(W):
            d = (brow[x & 3] - 8) // 2
            buf[row + x * 3] = clamp(c[0] + d)
            buf[row + x * 3 + 1] = clamp(c[1] + d)
            buf[row + x * 3 + 2] = clamp(c[2] + d)

def fill_rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            px(x, y, c)

def disc(cx, cy, r, c, alpha=1.0):
    for dy in range(-r, r + 1):
        dx = math.isqrt(max(0, r * r - dy * dy))
        for x in range(cx - dx, cx + dx + 1):
            if alpha >= 1.0:
                px(x, cy + dy, c)
            else:
                pxa(x, cy + dy, c, alpha)

def ellipse(cx, cy, rx, ry, c, alpha=1.0):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy / float(ry)) ** 2
        if t < 0:
            continue
        dx = int(rx * math.sqrt(t))
        for x in range(cx - dx, cx + dx + 1):
            if alpha >= 1.0:
                px(x, cy + dy, c)
            else:
                pxa(x, cy + dy, c, alpha)

def poly(pts, c, alpha=1.0):
    ys = [p[1] for p in pts]
    ylo, yhi = max(0, min(ys)), min(H - 1, max(ys))
    n = len(pts)
    for y in range(ylo, yhi + 1):
        xs = []
        for i in range(n):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[i])), int(xs[i + 1]) + 1):
                if alpha >= 1.0:
                    px(x, y, c)
                else:
                    pxa(x, y, c, alpha)

def line(x0, y0, x1, y1, c, w=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        t = s / float(steps)
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        if w <= 1:
            px(x, y, c)
        else:
            disc(x, y, w // 2, c)

def glow(cx, cy, r, c, steps=5):
    for k in range(steps, 0, -1):
        disc(cx, cy, int(r * k / steps), c, alpha=0.05)

def lcg(seed):
    s = seed
    while True:
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        yield s

FONT = {
 'A': ["01110","10001","10001","11111","10001","10001","10001"],
 'B': ["11110","10001","10001","11110","10001","10001","11110"],
 'C': ["01110","10001","10000","10000","10000","10001","01110"],
 'D': ["11110","10001","10001","10001","10001","10001","11110"],
 'E': ["11111","10000","10000","11110","10000","10000","11111"],
 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'G': ["01110","10001","10000","10111","10001","10001","01111"],
 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"],
 'J': ["00111","00010","00010","00010","00010","10010","01100"],
 'K': ["10001","10010","10100","11000","10100","10010","10001"],
 'L': ["10000","10000","10000","10000","10000","10000","11111"],
 'M': ["10001","11011","10101","10101","10001","10001","10001"],
 'N': ["10001","11001","10101","10011","10001","10001","10001"],
 'O': ["01110","10001","10001","10001","10001","10001","01110"],
 'P': ["11110","10001","10001","11110","10000","10000","10000"],
 'Q': ["01110","10001","10001","10001","10101","10010","01101"],
 'R': ["11110","10001","10001","11110","10100","10010","10001"],
 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'T': ["11111","00100","00100","00100","00100","00100","00100"],
 'U': ["10001","10001","10001","10001","10001","10001","01110"],
 'V': ["10001","10001","10001","10001","10001","01010","00100"],
 'W': ["10001","10001","10001","10101","10101","11011","10001"],
 'X': ["10001","10001","01010","00100","01010","10001","10001"],
 'Y': ["10001","10001","01010","00100","00100","00100","00100"],
 'Z': ["11111","00001","00010","00100","01000","10000","11111"],
 ' ': ["00000","00000","00000","00000","00000","00000","00000"],
 '-': ["00000","00000","00000","01110","00000","00000","00000"],
 '.': ["00000","00000","00000","00000","00000","01100","01100"],
}

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(s, x, y, scale, c):
    for k, ch in enumerate(s):
        g = FONT.get(ch, FONT[' '])
        ox = x + k * 6 * scale
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px(ox + col * scale + dx, y + r * scale + dy, c)

def draw_text_c(s, cx, y, scale, c, shadow=None):
    x = cx - text_w(s, scale) // 2
    if shadow is not None:
        draw_text(s, x + 3, y + 4, scale, shadow)
    draw_text(s, x, y, scale, c)

def border(c, inset=18, w=3):
    for t in range(w):
        for x in range(inset + t, W - inset - t):
            px(x, inset + t, c); px(x, H - 1 - inset - t, c)
        for y in range(inset + t, H - inset - t):
            px(inset + t, y, c); px(W - 1 - inset - t, y, c)

def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out

def save_png(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)

def tree(x, y, s, c):
    poly([(x, y - 3 * s), (x - s, y), (x + s, y)], c)
    poly([(x, y - 5 * s), (x - int(0.7 * s), y - 2 * s), (x + int(0.7 * s), y - 2 * s)], c)
    fill_rect(x - 1, y, x + 2, y + s, c)

def house(x, y, w, h, wall, roof, lit):
    fill_rect(x, y, x + w, y + h, wall)
    poly([(x - 3, y), (x + w // 2, y - h // 2), (x + w + 3, y)], roof)
    fill_rect(x + w // 2 - 3, y + h // 2 - 2, x + w // 2 + 3, y + h // 2 + 4, lit)
    fill_rect(x + 3, y + 3, x + 9, y + 9, lit)

def bird(x, y, s, c):
    line(x - s, y, x, y + s // 2, c, 2)
    line(x, y + s // 2, x + s, y, c, 2)

def draw():
    # Golden-hour sky over a sea of clouds.
    vgrad(0, 720, [(0.0, (43, 27, 78)), (0.35, (120, 58, 110)),
                   (0.62, (214, 96, 110)), (0.85, (242, 166, 90)),
                   (1.0, (250, 208, 138))])
    fill_rect(0, 720, W, H, (246, 196, 158))
    # Low sun setting just behind the island's rim.
    glow(384, 430, 170, (255, 190, 110), 6)
    disc(384, 430, 58, (255, 214, 140))
    disc(384, 430, 42, (255, 232, 180))
    # Wispy high clouds.
    ellipse(150, 260, 150, 16, (255, 205, 190), 0.35)
    ellipse(620, 210, 170, 14, (255, 205, 190), 0.30)
    ellipse(420, 320, 120, 12, (255, 220, 205), 0.28)
    # Distant floating islets.
    poly([(110, 470), (210, 470), (185, 520), (160, 545), (135, 520)], (74, 44, 94))
    poly([(560, 440), (680, 440), (650, 500), (620, 530), (590, 495)], (74, 44, 94))
    fill_rect(152, 545, 157, 590, (210, 225, 235))
    fill_rect(612, 530, 617, 575, (210, 225, 235))
    tree(160, 468, 7, (52, 70, 60))
    tree(620, 438, 7, (52, 70, 60))
    # Main floating island.
    poly([(150, 470), (620, 470), (560, 560), (470, 660), (384, 735),
          (300, 660), (210, 560)], (58, 34, 80))
    poly([(150, 470), (620, 470), (600, 492), (170, 492)], (146, 152, 82))
    # Faint rock strata on the island's underside.
    line(220, 560, 550, 560, (74, 44, 94), 2)
    line(275, 620, 495, 620, (74, 44, 94), 2)
    # Village on the island top.
    house(210, 440, 34, 28, (250, 230, 200), (150, 60, 60), (255, 220, 120))
    house(270, 432, 30, 26, (245, 220, 185), (140, 55, 55), (255, 220, 120))
    house(330, 444, 36, 24, (250, 232, 205), (150, 60, 60), (255, 220, 120))
    house(420, 436, 32, 28, (245, 222, 188), (140, 55, 55), (255, 220, 120))
    house(480, 442, 34, 26, (250, 230, 200), (150, 60, 60), (255, 220, 120))
    tree(255, 440, 9, (44, 66, 52))
    tree(395, 438, 8, (44, 66, 52))
    tree(540, 442, 9, (44, 66, 52))
    tree(180, 446, 8, (44, 66, 52))
    # Waterfalls spilling off the island.
    fill_rect(300, 660, 307, 745, (205, 228, 238))
    fill_rect(462, 660, 469, 745, (205, 228, 238))
    fill_rect(303, 660, 305, 745, (235, 245, 248))
    fill_rect(465, 660, 467, 745, (235, 245, 248))
    ellipse(303, 752, 26, 8, (235, 240, 245), 0.7)
    ellipse(465, 752, 26, 8, (235, 240, 245), 0.7)
    # Birds.
    bird(120, 350, 10, (52, 32, 70))
    bird(180, 320, 8, (52, 32, 70))
    bird(640, 330, 9, (52, 32, 70))
    bird(580, 380, 7, (52, 32, 70))
    # Sea of clouds below.
    ellipse(120, 880, 260, 60, (250, 220, 190), 0.85)
    ellipse(420, 930, 300, 70, (244, 200, 175), 0.9)
    ellipse(680, 880, 240, 55, (250, 222, 192), 0.85)
    ellipse(250, 990, 320, 60, (238, 190, 168), 0.9)
    ellipse(560, 1000, 300, 55, (242, 196, 172), 0.9)
    # Title block.
    draw_text_c("VELMARA", 384, 62, 10, (255, 244, 214), shadow=(46, 24, 66))
    line(118, 160, 168, 160, (255, 244, 214), 2)
    line(600, 160, 650, 160, (255, 244, 214), 2)
    draw_text_c("ISLES ABOVE THE CLOUDS", 384, 150, 3, (255, 236, 205))
    border((255, 244, 214))

if __name__ == "__main__":
    draw()
    save_png("/output/entry.png")
