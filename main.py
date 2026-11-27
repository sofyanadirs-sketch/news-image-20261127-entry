#!/usr/bin/env python3
"""The Friday Ledger -- front page of Friday 27 November 2026 in one image.

Renders a 1024x1024 newspaper front page with nothing but the Python
standard library: every letter comes from a small 5x7 bitmap font drawn
here, every shape is built from rectangles, lines and polygons, and the
PNG bytes are assembled by hand (zlib + struct). No network, no external
files, no timestamps inside the output, so two runs are byte-identical.
"""

import hashlib
import math
import os
import struct
import zlib

W = 1024
H = 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN  # 976

# ---------------------------------------------------------------- palette
PAPER = (250, 247, 238)
INK = (28, 28, 28)
NAVY = (18, 38, 74)
CRIMSON = (178, 34, 34)
GOLD = (184, 134, 11)
OCEAN = (196, 221, 235)
LAND = (224, 211, 176)
GRIDLINE = (200, 195, 182)
SOFT = (118, 116, 108)
WHITE = (255, 255, 255)
TEAL = (14, 110, 110)
FOREST = (46, 110, 52)
PLUM = (110, 58, 110)
RUST = (150, 74, 20)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is seven rows of five cells; '#' is ink, '.' is empty.
# Designed for this page only: capitals, digits and common punctuation.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "*": (".....", "#...#", ".#.#.", "#####", ".#.#.", "#...#", "....."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "#": ("#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"),
}

GLYPH_W = 5
GLYPH_H = 7
GLYPH_ADV = 6  # glyph width + one column of tracking


def text_width(text, scale):
    """Pixel width of text at the given scale (trailing gap excluded)."""
    if not text:
        return 0
    return (len(text) * GLYPH_ADV - 1) * scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_w:
            current = trial
            continue
        if current:
            lines.append(current)
        # A single word wider than the box gets hard-split by characters.
        while text_width(word, scale) > max_w:
            cut = max_w // (GLYPH_ADV * scale)
            lines.append(word[:cut])
            word = word[cut:]
        current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def outline_rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line, inclusive of both ends."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)

    def fill_polygon(self, points, color):
        """Scanline fill for a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[k])), y,
                               int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1,
                               1, color)

    def draw_glyph(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT[" "])
        for row in range(GLYPH_H):
            bits = glyph[row]
            for col in range(GLYPH_W):
                if bits[col] == "#":
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            self.draw_glyph(cx, y, ch, scale, color)
            cx += GLYPH_ADV * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def text_right(self, x_right, y, s, scale, color):
        self.text(x_right - text_width(s, scale), y, s, scale, color)


# ------------------------------------------------------------------- PNG
def _chunk(kind, data):
    block = struct.pack(">I", len(data)) + kind + data
    block += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return block


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------- masthead
def draw_masthead(cv):
    # Navy band with the paper name, a gold rule, and a crimson date strip.
    cv.fill_rect(MARGIN, 14, CONTENT_W, 88, NAVY)
    cv.text_center(W // 2, 26, "THE FRIDAY LEDGER", 6, PAPER)
    cv.text_center(W // 2, 76, "THE WORLD IN ONE DAY", 2, GOLD)
    cv.hline(MARGIN, 104, CONTENT_W, GOLD, 2)
    cv.fill_rect(MARGIN, 108, CONTENT_W, 20, CRIMSON)
    cv.text(MARGIN + 10, 114, "VOL. I - NO. 331", 1, WHITE)
    cv.text_center(W // 2, 112, "FRIDAY 27 NOVEMBER 2026", 2, WHITE)
    cv.text_right(W - MARGIN - 10, 114, "ONE DAY - ONE PAGE", 1, WHITE)


# ------------------------------------------------------- numbers strip
NUMBERS = [
    ("94", "DEAD IN HONG KONG FIRE"),
    ("$18BN", "SPACEX SHARES FOR US KIDS"),
    ("1.6TN", "EU BUDGET IN EUR 2028-34"),
    ("3.25%", "BANK OF KOREA RATE"),
    ("31", "DEAD IN CAIRO TANKER FIRE"),
    ("100TH", "MACY'S PARADE POSTPONED"),
]


def draw_numbers(cv):
    cv.text(MARGIN, 134, "THE DAY IN NUMBERS", 1, NAVY)
    cv.text_right(W - MARGIN, 134, "SIX FIGURES THAT SET THE DAY", 1, SOFT)
    cv.hline(MARGIN, 144, CONTENT_W, NAVY, 2)
    box_w, gap = 158, 5
    total = 6 * box_w + 5 * gap
    x = MARGIN + (CONTENT_W - total) // 2
    y = 150
    for big, label in NUMBERS:
        cv.outline_rect(x, y, box_w, 52, NAVY, 1)
        cv.text_center(x + box_w // 2, y + 5, big, 3, CRIMSON)
        for i, line in enumerate(wrap_text(label, 1, box_w - 12)):
            cv.text_center(x + box_w // 2, y + 30 + i * 9, line, 1, INK)
        x += box_w + gap


# ------------------------------------------------------------ lead story
LEAD_BODY = (
    "A fire that began in bamboo scaffolding raced through seven of "
    "eight tower blocks at Wang Fuk Court in Tai Po, killing 94 people. "
    "Another 279 are unaccounted for, and 70 more were hurt."
)


def draw_lead(cv):
    lx = MARGIN
    lw = 616
    cv.text(lx, 210, "LEAD STORY - HONG KONG", 1, CRIMSON)
    cv.text(lx, 224, "FIRE SWEEPS HONG KONG", 4, NAVY)
    cv.text(lx, 256, "TOWERS: 94 DEAD", 4, NAVY)
    cv.hline(lx, 290, lw, GOLD, 2)
    for i, line in enumerate(wrap_text(LEAD_BODY, 2, lw)):
        cv.text(lx, 298 + i * 15, line, 2, INK)
    cv.text(lx, 368, "94 DEAD - 279 MISSING - 70+ HURT", 2, CRIMSON)

    # Right-hand box: the day's two other fires.
    bx, bw = 656, 344
    cv.fill_rect(bx, 208, bw, 24, CRIMSON)
    cv.text_center(bx + bw // 2, 214, "TWO MORE FIRES", 2, WHITE)
    cv.outline_rect(bx, 208, bw, 170, NAVY, 1)
    cv.text(bx + 10, 240, "CAIRO TANKER FIRE", 2, NAVY)
    cairo = ("A fuel tanker overturned on the Cairo ring road and burst "
             "into flames. 31 people were killed, 26 hurt and 27 "
             "vehicles were destroyed. The driver was detained.")
    for i, line in enumerate(wrap_text(cairo, 1, bw - 20)):
        cv.text(bx + 10, 258 + i * 9, line, 1, INK)
    cv.hline(bx + 10, 294, bw - 20, GRIDLINE, 1)
    cv.text(bx + 10, 302, "BANGKOK REFINERY BLAST", 2, NAVY)
    bangkok = ("An explosion at the Bangchak Phra Khanong refinery "
               "injured 9 workers, 3 of them critically. All units were "
               "shut at the 120,000-barrel-a-day plant.")
    for i, line in enumerate(wrap_text(bangkok, 1, bw - 20)):
        cv.text(bx + 10, 320 + i * 9, line, 1, INK)
    cv.hline(bx + 10, 356, bw - 20, GRIDLINE, 1)
    cv.text(bx + 10, 362, "BOTH BLAZES ARE UNDER INVESTIGATION.", 1, SOFT)


# ------------------------------------------------------------------- map
# Rough continent outlines in (longitude, latitude), drawn from memory.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-81, 25), (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-110, 24),
     (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-78, 8), (-60, 9), (-52, 5), (-44, -3), (-35, -8), (-40, -20),
     (-48, -27), (-57, -35), (-65, -41), (-70, -54), (-73, -45),
     (-71, -30), (-70, -18), (-77, -12), (-81, -5), (-80, 2)],
    [(-17, 15), (-11, 27), (-5, 35), (10, 37), (20, 32), (32, 31),
     (34, 28), (38, 22), (43, 12), (51, 11), (48, 2), (40, -5),
     (40, -15), (36, -22), (32, -28), (27, -33), (19, -35), (15, -27),
     (12, -17), (9, -1), (9, 4), (-8, 5), (-13, 8), (-16, 12)],
    [(-10, 37), (-9, 43), (-2, 48), (2, 51), (5, 53), (8, 57), (12, 58),
     (18, 56), (21, 55), (25, 59), (30, 60), (28, 65), (24, 68),
     (18, 70), (14, 71), (30, 70), (45, 68), (60, 69), (75, 72),
     (90, 75), (105, 77), (120, 73), (135, 72), (150, 70), (162, 66),
     (178, 65), (170, 60), (158, 56), (150, 59), (142, 55), (140, 40),
     (130, 38), (127, 35), (122, 30), (120, 25), (114, 22), (108, 18),
     (105, 10), (103, 2), (100, 8), (97, 15), (92, 21), (88, 22),
     (85, 19), (80, 13), (77, 8), (73, 18), (68, 23), (62, 25),
     (57, 26), (52, 27), (48, 30), (44, 36), (36, 36), (30, 36),
     (28, 38), (23, 40), (19, 42), (15, 44), (12, 44), (8, 44),
     (3, 42), (0, 39), (-2, 37), (-6, 36), (-10, 37)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (137, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    [(95, 5), (98, 3), (101, -1), (104, -3), (107, -6), (110, -7),
     (114, -8), (118, -9), (121, -10), (124, -9), (127, -8), (130, -4),
     (132, -2), (135, -3), (138, -5), (141, -8), (140, -8), (136, -6),
     (132, -1), (128, 0), (124, 1), (120, 0), (116, -1), (112, -3),
     (108, -5), (104, -4), (100, 0), (96, 4)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (142, 44), (144, 44), (142, 42), (141, 39), (139, 35),
     (136, 33), (133, 32)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51)],
]

# (name, longitude, latitude, label dx, label dy) relative to the pin.
PINS = [
    ("HONG KONG", 114.16, 22.32, 8, -4),
    ("BANGKOK", 100.50, 13.76, -52, 6),
    ("SEOUL", 126.98, 37.57, 8, -4),
    ("BRUSSELS", 4.35, 50.85, 8, -4),
    ("WASHINGTON", -77.04, 38.91, -66, -4),
    ("CAIRO", 31.24, 30.06, 8, -4),
    ("NAIROBI", 36.82, -1.29, 8, -4),
    ("BRASILIA", -47.88, -15.79, -56, -4),
    ("DELHI", 77.21, 28.61, -40, -12),
    ("CANBERRA", 149.13, -35.28, -64, -4),
]

MAP_X, MAP_Y, MAP_W, MAP_H = MARGIN, 400, CONTENT_W, 152


def project(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (80.0 - lat) / 140.0 * MAP_H
    return int(x), int(y)


def draw_map(cv):
    cv.text(MARGIN, 384, "THE WORLD, AT A GLANCE", 1, NAVY)
    cv.text_right(W - MARGIN, 384, "10 PINS - 10 STORIES", 1, SOFT)
    cv.hline(MARGIN, 394, CONTENT_W, NAVY, 2)
    cv.fill_rect(MAP_X, MAP_Y, MAP_W, MAP_H, OCEAN)
    for lon in range(-150, 151, 30):
        x, _ = project(lon, 0)
        cv.vline(x, MAP_Y, MAP_H, (214, 228, 236), 1)
    for lat in (60, 30, 0, -30):
        _, y = project(0, lat)
        cv.hline(MAP_X, y, MAP_W, (214, 228, 236), 1)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        cv.fill_polygon(pts, LAND)
    cv.outline_rect(MAP_X, MAP_Y, MAP_W, MAP_H, NAVY, 1)
    for name, lon, lat, dx, dy in PINS:
        px, py = project(lon, lat)
        cv.fill_circle(px, py, 5, WHITE)
        cv.fill_circle(px, py, 3, CRIMSON)
        lx, ly = px + dx, py + dy
        tw = text_width(name, 1)
        cv.fill_rect(lx - 2, ly - 1, tw + 4, 9, WHITE)
        cv.text(lx, ly, name, 1, INK)


# -------------------------------------------------------------- timeline
# (hour in UTC, label, label above the line?)
TIMELINE = [
    (0.0, "HONG KONG TOLL 55", True),
    (1.0, "KOREA RATE 3.25%", False),
    (5.0, "HONG KONG TOLL 83", True),
    (8.0, "BANGKOK BLAST", False),
    (11.0, "HONG KONG TOLL 94", True),
    (13.0, "MUSK PLEDGES $18BN", False),
    (18.0, "MACY'S PARADE MOVED", True),
    (21.0, "GUKESH DRAW, GAME 3", False),
]


def draw_timeline(cv):
    cv.text(MARGIN, 562, "THE DAY IN UTC", 1, NAVY)
    cv.text_right(W - MARGIN, 562, "FROM MIDNIGHT TO MIDNIGHT", 1, SOFT)
    cv.hline(MARGIN, 572, CONTENT_W, NAVY, 2)
    x0, x1, yline = 40, 984, 600
    cv.hline(x0, yline, x1 - x0, INK, 2)
    for h in range(0, 25, 4):
        x = x0 + int(h / 24.0 * (x1 - x0))
        cv.vline(x, yline - 3, 7, INK, 1)
        cv.text_center(x, 622, "%02d" % h, 1, SOFT)
    for hour, label, above in TIMELINE:
        x = x0 + int(hour / 24.0 * (x1 - x0))
        cv.fill_circle(x, yline, 4, CRIMSON)
        tw = text_width(label, 1)
        lx = min(max(x - tw // 2, MARGIN), W - MARGIN - tw)
        if above:
            cv.vline(x, 588, 10, CRIMSON, 1)
            cv.text(lx, 578, label, 1, INK)
        else:
            cv.vline(x, 602, 8, CRIMSON, 1)
            cv.text(lx, 610, label, 1, INK)


# -------------------------------------------------------------- news grid
REGION_COLORS = {
    "ASIA": CRIMSON,
    "EUROPE": NAVY,
    "AMERICAS": TEAL,
    "MIDEAST": RUST,
    "AFRICA": FOREST,
    "OCEANIA": PLUM,
    "MARKETS": GOLD,
    "SPORT": (140, 30, 90),
}

STORIES = [
    ("ASIA", "KOREA LIFTS KEY RATE TO 3.25% AS AI BOOM FUELS GROWTH"),
    ("EUROPE", "EU LEADERS WRESTLE OVER EUR 1.6TN BUDGET TO 2034"),
    ("AMERICAS", "US TARIFFS HIT 14 ECONOMIES IN A NEW ROUND"),
    ("MIDEAST", "FRESH ISRAELI STRIKES HIT GAZA"),
    ("AFRICA", "RAMAPHOSA WINS COURT CASE IN SOUTH AFRICA"),
    ("OCEANIA", "AUSTRALIA FACES UNHEALTHY HOUSING CRISIS"),
    ("MARKETS", "SENSEX AND NIFTY EDGE UP IN FRIDAY TRADE"),
    ("SPORT", "INDIA A FACE SRI LANKA A IN DOHA SEMI-FINAL"),
    ("ASIA", "CHINA WARNS OVER NEW US TARIFFS ON 14 ECONOMIES"),
    ("EUROPE", "FRANCE PITCHED AS THE NEXT BYD HUB IN EUROPE"),
    ("AMERICAS", "TRUMP TO VISIT ARIZONA ON DEC 4 FOR TSMC EVENT"),
    ("MIDEAST", "IRAN FOOD INFLATION TOPS 112 PERCENT"),
    ("AFRICA", "ALGERIA MOVES TO CUT METHANE LEAKS"),
    ("OCEANIA", "FIJI ROLLS OUT A NATIONAL WATER STRATEGY"),
    ("MARKETS", "RUPEE AT 92.44 AS TARIFF WORRIES WEIGH"),
    ("SPORT", "PANKAJ ADVANI LIFTS THE CRUCIBLE CUP"),
    ("ASIA", "INDIA MARKS CONSTITUTION DAY AND 18 YEARS SINCE 26/11"),
    ("EUROPE", "GERMANY'S RECOVERY STALLS AS ORDERS FADE"),
    ("AMERICAS", "BRAZIL PUSHES CREDIT REFORMS TO CUT BORROWING COSTS"),
    ("MIDEAST", "SAUDI ARAMCO PUTS $7BN INTO A KOREA PLANT"),
    ("EUROPE", "UKRAINE AND HUNGARY TALK COOPERATION"),
    ("OCEANIA", "ICELAND'S PODCASTS FIND A NEW AUDIENCE"),
    ("MARKETS", "FLIPKART CHIEF TO STEP DOWN, REPORT SAYS"),
    ("ASIA", "TAMIL NADU GIVES DADS 15 DAYS OF PATERNITY LEAVE"),
    ("EUROPE", "SPAIN DECLARES EMERGENCY ON EL HIERRO ISLAND"),
    ("AMERICAS", "COLOMBIA DROPS ITS BID TO JOIN BRICS"),
    ("MIDEAST", "YEMEN AID CRISIS DEEPENS, AGENCIES WARN"),
    ("EUROPE", "RUSSIA SETS ITS 2027 BUDGET AMID WAR COSTS"),
    ("ASIA", "INDONESIA SEARCHES FOR MINERS IN ILLEGAL GOLD PIT"),
    ("AMERICAS", "URUGUAY FACES A GENDER VIOLENCE CRISIS"),
    ("MIDEAST", "TURKIYE SPEEDS UP ITS DECARBONISATION PLAN"),
    ("EUROPE", "BRITAIN SETS UP PANEL FOR NUCLEAR VETERANS"),
    ("ASIA", "JAPAN'S COMMUNITY CAFETERIAS FEED THE NEIGHBOURHOOD"),
    ("AMERICAS", "JAMAICA'S RECOVERY CONTINUES AFTER THE STORM"),
    ("EUROPE", "SCOTLAND FACES QUESTIONS OVER HOSPITAL SAFETY"),
    ("ASIA", "PAKISTANI ASTRONAUT JOINS THE CREW OF TIANGONG"),
]


def draw_grid(cv):
    cv.text(MARGIN, 638, "AROUND THE WORLD", 2, NAVY)
    cv.text_right(W - MARGIN, 640, "36 STORIES - 8 REGIONS", 1, SOFT)
    cv.hline(MARGIN, 658, CONTENT_W, NAVY, 2)
    col_w, col_gap = 235, 12
    row_h, y0 = 30, 664
    for i, (region, headline) in enumerate(STORIES):
        col, row = i % 4, i // 4
        x = MARGIN + col * (col_w + col_gap)
        y = y0 + row * row_h
        cv.text(x, y, region, 1, REGION_COLORS[region])
        lines = wrap_text(headline, 1, col_w)[:2]
        for j, line in enumerate(lines):
            cv.text(x, y + 9 + j * 9, line, 1, INK)


# ---------------------------------------------------------------- footer
def draw_footer(cv):
    cv.hline(MARGIN, 940, CONTENT_W, GOLD, 2)
    cv.fill_rect(MARGIN, 944, CONTENT_W, 66, NAVY)
    cv.text(MARGIN + 10, 952, "SPORT", 2, GOLD)
    cv.text(110, 950,
            "GUKESH-SINDAROV GAME 3 DRAW AFTER 60 MOVES, 1.5-1.5  |  "
            "SINNER OUT OF AUSTRALIAN OPEN 2027", 1, WHITE)
    cv.text(110, 964,
            "SOORYAVANSHI 204 OFF 53 BALLS  |  "
            "INDIA BEAT JAPAN 4-0 IN HOCKEY", 1, WHITE)
    cv.text(MARGIN + 10, 988,
            "SOURCES: AP - REUTERS - CHESS.COM - NBC SPORTS - "
            "FULL LIST IN NEWS-SOURCES.MD", 1, (200, 200, 195))
    cv.text_right(W - MARGIN - 10, 988, "FRIDAY 27 NOVEMBER 2026", 1, GOLD)


def main():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_numbers(cv)
    draw_lead(cv)
    draw_map(cv)
    draw_timeline(cv)
    draw_grid(cv)
    draw_footer(cv)

    here = os.path.dirname(os.path.abspath(__file__))
    # The grader mounts the repository read-only at /bot and gives us a
    # writable directory through MAKEFUN_OUTPUT_DIR (/output): writing
    # next to main.py fails there with PermissionError (exit 1). Locally
    # the variable is unset, so the render still lands in output/.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = encode_png(cv)
    with open(path, "wb") as fh:
        fh.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (path, len(data), digest))


if __name__ == "__main__":
    main()
