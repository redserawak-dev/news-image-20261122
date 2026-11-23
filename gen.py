#!/usr/bin/env python3
"""Draws entry.png: one image summing up the world news of Sunday 22 November 2026.

Rendered at 2x and downsampled so every stroke and glyph is antialiased.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

W = 1024
S = 3
PAPER = (243, 238, 228)
LAND = (228, 219, 203)
INK = (23, 25, 29)
MUTED = (94, 96, 102)
FAINT = (150, 145, 136)
RULE = (204, 196, 181)
RED = (177, 45, 38)
CREAM = (250, 246, 238)

F = "/usr/share/fonts/opentype/inter/"


def font(name, px):
    return ImageFont.truetype(F + name, int(round(px * S)))


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, W * S), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def line(self, a, b, fill=INK, w=1.0):
        self.d.line([(a[0] * S, a[1] * S), (b[0] * S, b[1] * S)], fill=fill, width=max(1, int(w * S)))

    def path(self, pts, fill=None, outline=None, w=1.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, int(w * S)), joint="curve")

    def rect(self, box, fill=None, outline=None, w=1.0, r=0):
        x0, y0, x1, y1 = [v * S for v in box]
        if r:
            self.d.rounded_rectangle([x0, y0, x1, y1], radius=r * S, fill=fill, outline=outline, width=max(1, int(w * S)))
        else:
            self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=max(1, int(w * S)))

    def poly(self, pts, fill=None, outline=None, w=1.0):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline, width=max(1, int(w * S)))

    def ellipse(self, box, fill=None, outline=None, w=1.0):
        x0, y0, x1, y1 = [v * S for v in box]
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=max(1, int(w * S)))

    def chord(self, box, a0, a1, fill=None, outline=None, w=1.0):
        x0, y0, x1, y1 = [v * S for v in box]
        self.d.chord([x0, y0, x1, y1], a0, a1, fill=fill, outline=outline, width=max(1, int(w * S)))

    def arc(self, box, a0, a1, fill=INK, w=1.0):
        x0, y0, x1, y1 = [v * S for v in box]
        self.d.arc([x0, y0, x1, y1], a0, a1, fill=fill, width=max(1, int(w * S)))

    def text(self, xy, s, f, fill=INK, anchor="la", track=0.0):
        if not track:
            self.d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill, anchor=anchor)
            return
        # tracked text is drawn left to right, so resolve the anchor first
        width = self.tw(s, f, track)
        x, y = xy
        if anchor[0] == "r":
            x -= width
        elif anchor[0] == "m":
            x -= width / 2
        for ch in s:
            self.d.text((x * S, y * S), ch, font=f, fill=fill, anchor="l" + anchor[1])
            x += self.d.textlength(ch, font=f) / S + track

    def tw(self, s, f, track=0.0):
        n = self.d.textlength(s, font=f) / S
        return n + track * max(0, len(s) - 1)

    def wrap(self, s, f, width):
        out, cur = [], ""
        for word in s.split():
            t = (cur + " " + word).strip()
            if self.tw(t, f) <= width or not cur:
                cur = t
            else:
                out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out

    def save(self, path):
        self.img.resize((W, W), Image.LANCZOS).save(path, "PNG", optimize=True)


# ------------------------------------------------------------------ icons
# Line art in a 0..1 box, drawn at (x, y) with side s.

def icon_atom(c, x, y, s):
    """An atom: the nuclear file, and the deal over it."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    cx, cy = 0.50, 0.50
    for ang in (0, 60, 120):
        # an ellipse is drawn axis-aligned, so a thin rotated one is approximated
        # by sampling the rotated curve directly
        pts = []
        for k in range(97):
            t = 2 * math.pi * k / 96
            ex, ey = 0.44 * math.cos(t), 0.17 * math.sin(t)
            a = math.radians(ang)
            pts.append((cx + ex * math.cos(a) - ey * math.sin(a),
                        cy + ex * math.sin(a) + ey * math.cos(a)))
        c.path([P(px, py) for px, py in pts], fill=INK, w=1.9)
    c.ellipse((x + (cx - 0.075) * s, y + (cy - 0.075) * s, x + (cx + 0.075) * s, y + (cy + 0.075) * s), fill=RED)


def icon_city(c, x, y, s):
    """A strike on a city: a skyline under a burst."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    ground = 0.86
    towers = ((0.06, 0.24, 0.34), (0.28, 0.44, 0.24), (0.48, 0.70, 0.42), (0.74, 0.94, 0.30))
    for a, b, h in towers:
        c.rect((x + a * s, y + (ground - h) * s, x + b * s, y + ground * s), fill=LAND, outline=INK, w=1.6)
        rows = max(2, int(h * 3.2))
        for r in range(rows):
            wy = ground - h + 0.05 + r * (h - 0.09) / rows
            if wy + 0.045 > ground - 0.02:
                continue
            c.rect((x + (a + 0.035) * s, y + wy * s, x + (a + 0.075) * s, y + (wy + 0.042) * s), fill=INK)
            c.rect((x + (b - 0.075) * s, y + wy * s, x + (b - 0.035) * s, y + (wy + 0.042) * s), fill=INK)
    c.line(P(-0.02, ground), P(1.02, ground), fill=INK, w=2.0)
    # burst
    cx, cy, R = 0.28, 0.17, 0.135
    pts = []
    for i in range(18):
        ang = math.pi * 2 * i / 18 - math.pi / 2
        rr = R if i % 2 == 0 else R * 0.46
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    c.poly([P(px, py) for px, py in pts], fill=RED)


def icon_ship(c, x, y, s):
    """A cargo ship burning at sea."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    for ny in (0.88, 0.96):
        c.line(P(0.00, ny), P(1.00, ny), fill=INK, w=1.4)
    c.poly([P(0.06, 0.62), P(0.94, 0.62), P(0.84, 0.80), P(0.16, 0.80)], fill=LAND, outline=INK, w=1.8)
    c.rect((x + 0.22 * s, y + 0.46 * s, x + 0.44 * s, y + 0.62 * s), fill=LAND, outline=INK, w=1.6)
    c.rect((x + 0.46 * s, y + 0.38 * s, x + 0.62 * s, y + 0.62 * s), fill=LAND, outline=INK, w=1.6)
    c.rect((x + 0.66 * s, y + 0.30 * s, x + 0.84 * s, y + 0.62 * s), fill=LAND, outline=INK, w=1.6)
    for fx, h, wid in ((0.29, 0.26, 0.085), (0.39, 0.17, 0.055), (0.52, 0.30, 0.09), (0.72, 0.13, 0.05)):
        c.poly([P(fx - wid, 0.50), P(fx, 0.50 - h), P(fx + wid, 0.50)], fill=RED)
    for sx, sy, r in ((0.34, 0.13, 0.042), (0.47, 0.08, 0.05), (0.60, 0.12, 0.036)):
        c.ellipse((x + (sx - r) * s, y + (sy - r) * s, x + (sx + r) * s, y + (sy + r) * s), outline=INK, w=1.2)


def icon_bars(c, x, y, s):
    """A figure behind bars: an arrest."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    # the figure, solid, so it reads at 300 px
    c.ellipse((x + 0.39 * s, y + 0.17 * s, x + 0.61 * s, y + 0.39 * s), fill=INK)
    c.poly([P(0.24, 0.92), P(0.31, 0.52), P(0.50, 0.44), P(0.69, 0.52), P(0.76, 0.92)], fill=INK)
    # the bars, over it
    c.rect((x + 0.02 * s, y + 0.90 * s, x + 0.98 * s, y + 0.96 * s), fill=INK)
    for nx in (0.14, 0.36, 0.64, 0.86):
        c.rect((x + (nx - 0.032) * s, y + 0.02 * s, x + (nx + 0.032) * s, y + 0.96 * s), fill=INK)
    c.rect((x - 0.02 * s, y + 0.02 * s, x + 1.02 * s, y + 0.075 * s), fill=INK)


def icon_boat(c, x, y, s):
    """A boat going down: the hull tipped under the waterline, heads beside it."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    # hull in planks, tilted bow up
    hull = [P(0.14, 0.42), P(0.66, 0.56), P(0.60, 0.74), P(0.20, 0.62)]
    c.poly(hull, fill=LAND)
    c.poly(hull, outline=INK, w=2.2)
    c.path([P(0.17, 0.50), P(0.63, 0.64)], fill=INK, w=1.3)
    # gunwale rim at the bow
    c.path([P(0.14, 0.42), P(0.66, 0.56)], fill=INK, w=2.4)
    # water, drawn over the submerged end
    c.rect((x - 0.02 * s, y + 0.62 * s, x + 1.02 * s, y + 0.74 * s), fill=PAPER)
    for i, ny in enumerate((0.66, 0.80, 0.90)):
        pts = []
        for k in range(49):
            nx = k / 48
            pts.append((nx, ny + 0.024 * math.sin(nx * math.pi * 3 + i * 1.2)))
        c.path([P(px, py) for px, py in pts], fill=INK, w=1.6)
    # heads still above the water, to the right of the hull
    for hx, hy in ((0.76, 0.53), (0.87, 0.56)):
        c.ellipse((x + (hx - 0.032) * s, y + (hy - 0.032) * s, x + (hx + 0.032) * s, y + (hy + 0.032) * s), fill=INK)


def icon_db(c, x, y, s):
    """A database with a crack through it: a breach."""
    P = lambda nx, ny: (x + nx * s, y + ny * s)
    L, R, T, B, ry = 0.20, 0.74, 0.14, 0.86, 0.072
    c.rect((x + L * s, y + T * s, x + R * s, y + B * s), fill=LAND)
    c.line(P(L, T), P(L, B), fill=INK, w=2.0)
    c.line(P(R, T), P(R, B), fill=INK, w=2.0)
    c.ellipse((x + L * s, y + (T - ry) * s, x + R * s, y + (T + ry) * s), fill=LAND, outline=INK, w=2.0)
    for by in (0.44, 0.62):
        c.arc((x + L * s, y + (by - ry) * s, x + R * s, y + (by + ry) * s), 0, 180, fill=INK, w=1.8)
    c.arc((x + L * s, y + (B - ry) * s, x + R * s, y + (B + ry) * s), 0, 180, fill=INK, w=2.0)
    # crack
    pts = [(0.44, 0.07), (0.52, 0.30), (0.42, 0.46), (0.54, 0.64), (0.44, 0.93)]
    c.path([P(px, py) for px, py in pts], fill=RED, w=2.8)


# ------------------------------------------------------------------ page
CARDS = [
    ("MIDDLE EAST", "US vows a ‘permanent’ deal with Iran",
     "Trump says the pact must outlast him. Tehran keeps the Strait of Hormuz shut.", icon_atom),
    ("UKRAINE", "Strike hits Zelenskyy’s hometown",
     "A Russian attack on Kryvyi Rih killed two people and wounded 60.", icon_city),
    ("BALTIC SEA", "Drones set a Russian cargo ship ablaze",
     "The ship burned in the Gulf of Finland; Helsinki warns the war is spreading.", icon_ship),
    ("MEXICO", "‘El Chapo Isidro’ seized in Sinaloa",
     "The FBI-wanted cartel boss was taken in a raid that left 11 dead.", icon_bars),
    ("NIGERIA", "At least 24 dead as a boat capsizes",
     "The vessel went down with its passengers aboard, officials said.", icon_boat),
    ("UNITED STATES", "FBI probes a breach of its database",
     "Reported after outages struck banking and air traffic control.", icon_db),
]


def main(out):
    c = Canvas()
    M = 54
    KICK = font("Inter-SemiBold.otf", 15)
    c.text((M, 38), "ONE DAY  \u00b7  WORLD NEWS", KICK, MUTED, track=2.2)
    c.text((W - M, 38), "SIX STORIES", KICK, MUTED, anchor="ra", track=2.2)

    DATE = font("InterDisplay-Black.otf", 78)
    c.text((M - 5, 62), "22 NOVEMBER", DATE, INK)
    c.text((M - 5, 138), "2026", DATE, INK)

    CHIP = font("Inter-SemiBold.otf", 18)
    chip = "SUNDAY"
    cw, chh = c.tw(chip, CHIP, 2.0) + 30, 34
    cy = 152
    c.rect((W - M - cw, cy, W - M, cy + chh), fill=RED)
    c.text((W - M - cw / 2, cy + chh / 2), chip, CHIP, CREAM, anchor="mm", track=2.0)

    DECK = font("Inter-Regular.otf", 20)
    deck = ("The day in six stories: the Gulf, Ukraine’s front line, the Baltic, "
            "Sinaloa, Nigeria and Washington.")
    dy = 244
    for ln in c.wrap(deck, DECK, W - 2 * M):
        c.text((M, dy), ln, DECK, MUTED)
        dy += 26
    c.line((M, 226), (W - M, 226), fill=INK, w=1.4)
    c.line((M, dy + 8), (W - M, dy + 8), fill=INK, w=1.4)

    top = dy + 28
    gap = 30
    colw = (W - 2 * M - 2 * gap) / 3
    rowh = 292
    REGION = font("Inter-SemiBold.otf", 13)
    HEAD = font("InterDisplay-Bold.otf", 25)
    BODY = font("Inter-Regular.otf", 16)

    for i, (region, head, body, icon) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x0 = M + col * (colw + gap)
        y0 = top + row * rowh
        if col > 0:
            c.line((x0 - gap / 2, y0 + 4), (x0 - gap / 2, y0 + rowh - 46), fill=RULE, w=1.0)
        icon(c, x0 + 2, y0, 98)
        c.text((x0 + 1, y0 + 118), region, REGION, RED, track=1.4)
        yy = y0 + 140
        for ln in c.wrap(head, HEAD, colw - 6)[:2]:
            c.text((x0 - 1, yy), ln, HEAD, INK)
            yy += 28
        yy += 5
        for ln in c.wrap(body, BODY, colw - 8)[:3]:
            c.text((x0, yy), ln, BODY, MUTED)
            yy += 21

    fy = top + 2 * rowh - 14
    c.line((M, fy), (W - M, fy), fill=INK, w=1.4)
    ALSO = font("Inter-SemiBold.otf", 13)
    c.text((M, fy + 14), "ALSO ON THE DAY", ALSO, RED, track=1.4)
    TICK = font("Inter-Regular.otf", 16)
    tick = ("Iraq: a fire at the Hartha power station kills four  \u00b7  Germany: the AfD urges the "
            "deportation of 2.6m  \u00b7  Chess: Gukesh and Sindarov open the world final  \u00b7  "
            "London: a march for tighter AI rules")
    lines = c.wrap(tick, TICK, W - 2 * M)
    ty = fy + 40
    for ln in lines[:2]:
        c.text((M, ty), ln, TICK, MUTED)
        ty += 22
    SRC = font("Inter-Regular.otf", 12.5)
    c.text((M, 992), "Compiled from newswire reports of Sunday, 22 November 2026.", SRC, FAINT)
    c.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")