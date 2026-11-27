#!/usr/bin/env python3
"""THE FRIDAY LEDGER - The World in One Day.
Sum up Friday 27 November 2026 world news in one image.

Pure Python 3 stdlib (struct, zlib, os, hashlib, math). No network, no
third-party packages, fully deterministic: two runs produce
byte-identical PNG output.

Layout (1024x1024, navy-and-crimson broadsheet, own design):
  - navy masthead band + edition bar (Black Friday, day 331 of 2026)
  - the day in numbers: six big figures that defined the day
  - lead story (Hong Kong fire toll hits 94) + side box (two more fires:
    Cairo tanker, Bangkok refinery)
  - dotted world map built from ellipse blobs, with numbered pins
  - 24-hour UTC timeline strip with the day's turning points
  - region index + 4-column grid of 36 sourced stories, 8 regions
  - sport-in-brief footer strip

Run:  python3 main.py
Out:  output/entry.png  (and /output/entry.png when that dir exists)
"""
import hashlib
import math
import os
import struct
import zlib

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 characters, '#' = ink, '.' = empty.
# Hand-drawn for this entry. Lowercase is rendered as uppercase.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10001", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '&': ("01110", "10001", "10001", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "10110", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10101", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

BLANK = ("00000",) * 7


def glyph(ch):
    ch = ch.upper()
    return FONT.get(ch, BLANK)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if yy < 0 or yy >= self.h:
                continue
            for xx in range(x, x + w):
                if 0 <= xx < self.w:
                    i = (yy * self.w + xx) * 3
                    self.px[i:i + 3] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            x = round(cx + r * math.cos(math.radians(a)))
            y = round(cy + r * math.sin(math.radians(a)))
            self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        """Draw text, all caps, left aligned. Returns width used."""
        cx = x
        for ch in s:
            g = glyph(ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, x, y, w, s, scale, c):
        tw = self.text_w(s, scale)
        self.text(x + max(0, (w - tw) // 2), y, s, scale, c)


def wrap_words(text, max_chars):
    """Greedy word wrap. Returns list of lines, each <= max_chars."""
    lines = []
    for para in text.split('\n'):
        words = para.split(' ')
        cur = ''
        for wd in words:
            if cur == '':
                cur = wd
            elif len(cur) + 1 + len(wd) <= max_chars:
                cur += ' ' + wd
            else:
                lines.append(cur)
                cur = wd
        if cur != '':
            lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, text, scale, color, max_chars, leading):
    lines = wrap_words(text, max_chars)
    for i, ln in enumerate(lines):
        cv.text(x, y + i * leading, ln, scale, color)
    return len(lines)


# ---------------------------------------------------------------- PNG out
def write_png(cv, path):
    w, h = cv.w, cv.h
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        out = struct.pack('>I', len(data)) + ctype + data
        out += struct.pack('>I', zlib.crc32(ctype + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- palette
PAPER = bytes([250, 246, 236])   # warm newsprint
INK = bytes([16, 20, 28])
NAVY = bytes([16, 38, 74])       # masthead band + section headers
NAVY2 = bytes([28, 62, 110])
CRIMSON = bytes([178, 34, 34])   # numbers accent + map pins
GOLD = bytes([198, 148, 42])
GREY = bytes([110, 110, 104])
LGREY = bytes([226, 220, 208])
BLUE = bytes([42, 92, 150])      # map land dots
WHITE = bytes([255, 255, 255])
CREAM = bytes([240, 232, 214])

W, H = 1024, 1024
MX = 26            # side margin
CW = W - 2 * MX    # content width = 972

# ---------------------------------------------------------------- the day
# 36 sourced stories. Headline + one-line deck. Regions used for the index.
STORIES = [
    ("ASIA", "HONG KONG FIRE TOLL HITS 94; 279 STILL MISSING",
     "Rescuers search the charred Wang Fuk Court towers; three held over renovation work; 70-plus hurt."),
    ("ASIA", "BANGKOK REFINERY BLAST HURTS NINE",
     "Bangchak's Phra Khanong plant shuts all units after a blast; three critical; 120,000 barrels a day halted."),
    ("ASIA", "SOUTH KOREA LIFTS KEY RATE TO 3.25%",
     "Third hike this year as the AI chip boom lifts growth forecasts to 3.9% for 2026 and 4.1% for 2027."),
    ("ASIA", "INDIA MARKS 18 YEARS SINCE 26/11 MUMBAI ATTACKS",
     "The nation remembers the victims of the 2008 attacks on the anniversary."),
    ("ASIA", "TAMIL NADU GIVES 15 DAYS' PATERNITY LEAVE",
     "First Indian state to grant male government staff two weeks off for a new baby."),
    ("ASIA", "RUPEE SLIPS TO 92.44 AGAINST THE DOLLAR",
     "The currency weakens 24 paise as US tariff worries weigh on markets."),
    ("ASIA", "INDONESIA SEARCHES FOR WORKERS IN ILLEGAL GOLD MINE",
     "Rescue teams hunt for miners trapped underground; the site operated without permits."),
    ("ASIA", "KIM VOWS MORE NUCLEAR WEAPONS, SNUBS TRUMP",
     "North Korea's leader pledges a bigger arsenal after ignoring the US president's overture."),
    ("EUROPE", "EU LEADERS WRESTLE OVER 1.6TN EURO BUDGET",
     "Brussels summit weighs a 2028-34 budget and a 45bn euro Ukraine loan; deal eyed for 17-18 Dec."),
    ("EUROPE", "FRANCE EYED AS BYD MANUFACTURING HUB",
     "China's EV giant weighs a French plant as Europe courts its factories."),
    ("EUROPE", "GERMANY'S RECOVERY LOSES MOMENTUM",
     "Europe's largest economy stalls as exports and industry stay weak."),
    ("EUROPE", "SPAIN DECLARES EMERGENCY ON EL HIERRO",
     "Record maritime migrant arrivals overwhelm the Canary Island."),
    ("EUROPE", "SCOTLAND PROBES HOSPITAL SAFETY FAILURES",
     "Investigators examine longstanding safety concerns at Scottish hospitals."),
    ("EUROPE", "IRELAND ADVANCES NATURE RESTORATION PLANS",
     "Dublin pushes ahead with restoring peatlands, rivers and wildlife habitats."),
    ("EUROPE", "ICELAND'S PODCAST INDUSTRY BOOMS",
     "The island's podcast scene posts remarkable commercial growth."),
    ("EUROPE", "UZBEKISTAN TO RECOVER ASSETS FROM SWITZERLAND",
     "Tashkent agrees a deal to bring home illicitly acquired funds held in Swiss banks."),
    ("N. AMERICA", "US PROPOSES NEW TARIFFS ON 14 ECONOMIES",
     "Washington targets China, the EU and others, rattling manufacturers and shoppers."),
    ("N. AMERICA", "MUSK PLEDGES TWO SPACEX SHARES PER US CHILD",
     "A gift worth about $18bn for 72m children; one share next month, one after a June lockup."),
    ("N. AMERICA", "MACY'S 100TH PARADE MOVED TO SATURDAY",
     "First postponement in a century as a nor'easter brings 50-60 mph gusts to New York."),
    ("N. AMERICA", "BLACK FRIDAY OPENS WITH $1,000 GIFTCARD HUNTS",
     "Target gives gift cards to its first 100 guests per store; Best Buy sells a $100 card for $60."),
    ("N. AMERICA", "TRUMP TO VISIT ARIZONA DEC 4 FOR TSMC PLANT",
     "The president breaks ground on a new Taiwan Semiconductor chip plant."),
    ("N. AMERICA", "CANADA STRUGGLES TO KEEP FOREIGN SCIENTISTS",
     "Tighter immigration rules leave labs short of international talent."),
    ("MIDDLE EAST", "CAIRO TANKER FIRE KILLS 31; DRIVER HELD",
     "A 21-year-old is detained after a crash overturns a fuel tanker; 27 vehicles burn; 26 hurt."),
    ("MIDDLE EAST", "TWO ITALIANS KILLED IN DRONE ATTACK ON KUWAIT",
     "Officials blame an Iranian drone strike; Rome demands answers."),
    ("MIDDLE EAST", "IRAN FOOD INFLATION TOPS 112 PERCENT",
     "Soaring prices squeeze households as sanctions bite deeper."),
    ("MIDDLE EAST", "SAUDI ARAMCO PUTS $7BN INTO KOREAN PETCHEM",
     "Riyadh expands its Asian manufacturing footprint with a South Korea investment."),
    ("MIDDLE EAST", "FRESH ISRAELI STRIKES IN GAZA TEST CEASEFIRE",
     "New attacks raise fears the truce arrangements are unravelling."),
    ("LATIN AM.", "BRAZIL UNVEILS SWEEPING CREDIT REFORMS",
     "Brasilia moves to cut household indebtedness with new lending rules."),
    ("LATIN AM.", "COLOMBIA DROPS PLAN TO JOIN BRICS BANK",
     "Bogota abandons its bid to join the New Development Bank."),
    ("LATIN AM.", "URUGUAY STRENGTHENS FIGHT ON GENDER VIOLENCE",
     "Montevideo boosts its national response to violence against women."),
    ("LATIN AM.", "JAMAICA EYES RECOVERY AFTER FOUR QUARTERS DOWN",
     "Kingston hopes the economy turns after a year of contraction."),
    ("AFRICA", "RAMAPHOSA WINS COURT BID TO OVERTURN REPORT",
     "South Africa's president defeats an impeachment report in court."),
    ("AFRICA", "KENYA COURT QUASHES SEVEN STATE DEPARTMENTS",
     "Judges strike down departments created by President Ruto."),
    ("OCEANIA", "AUSTRALIA FACES HEALTH COST OF BAD HOUSING",
     "Unhealthy homes are driving a public health bill, a new study warns."),
    ("OCEANIA", "FIJI UNVEILS LONG-TERM WATER PLAN AMID DROUGHT",
     "Suva plans new infrastructure as dry spells intensify."),
    ("WORLD", "ANTHROPIC PLANS NEW FUND FOR THE PUBLIC GOOD",
     "The AI lab sketches a different blueprint for sharing the AI boom's spoils."),
]

# The day in numbers: (big figure, caption)
NUMBERS = [
    ("94", "DEAD IN HONG KONG FIRE"),
    ("$18BN", "MUSK SPACEX SHARE PLEDGE"),
    ("EUR 1.6TN", "EU 2028-34 BUDGET PLAN"),
    ("3.25%", "SOUTH KOREA KEY RATE"),
    ("31", "DEAD IN CAIRO TANKER FIRE"),
    ("100TH", "MACY'S PARADE POSTPONED"),
]

# 24-hour UTC timeline: (hour, minute, label) - times stories were reported
TIMELINE = [
    (0, 30, "HK TOLL HITS 94"),
    (3, 0, "BANGKOK BLAST"),
    (6, 0, "KOREA RATE 3.25%"),
    (8, 0, "EU SUMMIT OPENS"),
    (11, 0, "BLACK FRIDAY OPENS"),
    (14, 0, "US TARIFFS ON 14"),
    (17, 0, "MUSK $18BN PLEDGE"),
    (20, 0, "SINNER OUT OF AO 2027"),
]

# Numbered map pins: (number, lon, lat, label)
PINS = [
    (1, 114.2, 22.3, "HONG KONG"),
    (2, 100.5, 13.8, "BANGKOK"),
    (3, 127.0, 37.5, "SEOUL"),
    (4, 4.4, 50.8, "BRUSSELS"),
    (5, -77.0, 38.9, "WASHINGTON"),
    (6, 31.2, 30.0, "CAIRO"),
    (7, 36.8, -1.3, "NAIROBI"),
    (8, -47.9, -15.8, "BRASILIA"),
    (9, 77.2, 28.6, "DELHI"),
    (10, 149.1, -35.3, "CANBERRA"),
]

# Stylised world map: continents as unions of ellipses on a 72x28 grid.
# (centre-x, centre-y, radius-x, radius-y) in grid cells.
MAP_ELLIPSES = [
    # North America
    (8, 3, 6, 3), (16, 4, 6, 3), (15, 8, 6, 2), (16, 11, 3, 1),
    (28, 2, 3, 2),  # Greenland
    # South America
    (23, 14, 3, 2), (24, 18, 3, 3), (23, 23, 2, 2),
    # Europe
    (37, 3, 3, 2), (38, 6, 3, 2), (40, 8, 2, 1),
    # Africa
    (38, 11, 4, 3), (39, 15, 4, 3), (40, 19, 2, 2),
    # Asia
    (50, 3, 8, 3), (56, 5, 8, 3), (62, 8, 6, 2),
    (54, 10, 3, 2), (61, 12, 3, 1),  # India, SE Asia
    (60, 15, 4, 1),  # Indonesia
    # Australia + NZ
    (61, 21, 4, 2), (70, 24, 1, 1),
]
MAP_W, MAP_H = 72, 28


def map_land(gx, gy):
    for (cx, cy, rx, ry) in MAP_ELLIPSES:
        if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1.0:
            return True
    return False


def lonlat_to_grid(lon, lat):
    gx = int((lon + 180.0) / 5.0)
    gy = int((80.0 - lat) / 5.0)
    return gx, gy

# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.rect(MX, 22, CW, 92, NAVY)
    cv.text_center(MX, 34, CW, "THE FRIDAY LEDGER", 5, WHITE)
    cv.hline(MX + 60, 84, CW - 120, GOLD, 2)
    cv.text_center(MX, 92, CW,
                   "THE WORLD IN ONE DAY. 36 STORIES. 8 REGIONS.",
                   1, bytes([196, 210, 232]))
    # edition bar
    cv.rect(MX, 120, CW, 26, CREAM)
    cv.frame(MX, 120, CW, 26, INK, 1)
    cv.text(MX + 8, 128, "FRIDAY 27 NOVEMBER 2026", 1, INK)
    cv.text_center(MX, 128, CW, "EDITION NO. 327  -  THE WORLD IN ONE DAY",
                   1, INK)
    right = "BLACK FRIDAY - DAY 331 OF 2026"
    cv.text(MX + CW - 8 - cv.text_w(right, 1), 128, right, 1, INK)


def draw_numbers(cv, y):
    cv.text(MX, y, "THE DAY IN NUMBERS", 2, NAVY)
    cv.text(MX + CW - cv.text_w("SIX FIGURES THAT DEFINED THE DAY", 1),
            y + 4, "SIX FIGURES THAT DEFINED THE DAY", 1, GREY)
    by = y + 26
    bw = 156
    gap = 7
    for i, (big, cap) in enumerate(NUMBERS):
        x = MX + i * (bw + gap)
        cv.frame(x, by, bw, 56, INK, 1)
        cv.rect(x, by, bw, 3, CRIMSON)
        cv.text_center(x, by + 10, bw, big, 2, CRIMSON)
        draw_wrapped(cv, x + 6, by + 34, cap, 1, INK, 24, 9)
    return y + 26 + 56 + 8


def draw_lead(cv, y):
    # lead story, left ~640 wide; fires box right
    lead_w = 640
    box_x = MX + lead_w + 14
    box_w = CW - lead_w - 14
    cv.text(MX, y, "LEAD STORY", 1, NAVY)
    cv.text(box_x, y, "TWO MORE FIRES", 1, NAVY)
    hy = y + 14
    n = draw_wrapped(cv, MX, hy,
                     "HONG KONG FIRE TOLL HITS 94; 279 STILL MISSING",
                     2, INK, 26, 22)
    by = hy + n * 22 + 4
    draw_wrapped(cv, MX, by,
                 "TAI PO - FIREFIGHTERS BATTLED FOR A SECOND DAY AT THE "
                 "WANG FUK COURT COMPLEX AFTER A FIRE THAT STARTED IN "
                 "BAMBOO SCAFFOLDING SPREAD ACROSS SEVEN OF ITS EIGHT "
                 "BLOCKS. OFFICIALS SAY 94 PEOPLE ARE DEAD, 279 ARE "
                 "UNACCOUNTED FOR AND MORE THAN 70 ARE HURT. THREE MEN "
                 "LINKED TO THE RENOVATION FIRM HAVE BEEN ARRESTED.",
                 1, INK, 100, 11)
    # fires box
    cv.frame(box_x, hy, box_w, 106, INK, 2)
    cv.rect(box_x, hy, box_w, 20, CRIMSON)
    cv.text_center(box_x, hy + 6, box_w, "CAIRO AND BANGKOK BURN", 1, WHITE)
    draw_wrapped(cv, box_x + 8, hy + 28,
                 "CAIRO: A FUEL TANKER CRASH KILLS 31 ON THE RING ROAD; "
                 "THE DRIVER, 21, IS DETAINED. BANGKOK: A BLAST AT THE "
                 "BANGCHAK REFINERY HURTS NINE AND SHUTS ALL UNITS.",
                 1, INK, 46, 11)
    cv.hline(box_x + 8, hy + 84, box_w - 16, LGREY, 1)
    cv.text(box_x + 8, hy + 90,
            "ALSO: GUKESH-SINDAROV 1.5-1.5 IN GENEVA", 1, NAVY)
    return y + 14 + 106 + 8


def draw_map_panel(cv, y):
    panel_h = 150
    cv.text(MX, y, "WHERE IT HAPPENED", 2, NAVY)
    cv.text(MX + CW - cv.text_w("PIN NUMBERS MATCH THE STORY LIST", 1),
            y + 4, "PIN NUMBERS MATCH THE STORY LIST", 1, GREY)
    my = y + 26
    map_w = 520
    cv.frame(MX, my, map_w, panel_h, INK, 1)
    cell = 5
    ox = MX + (map_w - MAP_W * cell) // 2
    oy = my + (panel_h - MAP_H * cell) // 2
    for gy in range(MAP_H):
        for gx in range(MAP_W):
            if map_land(gx, gy):
                cv.rect(ox + gx * cell + 1, oy + gy * cell + 1,
                        cell - 2, cell - 2, BLUE)
    # pins
    for (num, lon, lat, lab) in PINS:
        gx, gy = lonlat_to_grid(lon, lat)
        px = ox + gx * cell + cell // 2
        py = oy + gy * cell + cell // 2
        cv.disc(px, py, 7, CRIMSON)
        cv.ring(px, py, 8, WHITE)
        ns = str(num)
        cv.text(px - cv.text_w(ns, 1) // 2, py - 3, ns, 1, WHITE)
    # legend, right of map
    lx = MX + map_w + 16
    lw = CW - map_w - 16
    cv.text(lx, my + 2, "PIN GUIDE", 1, NAVY)
    for i, (num, lon, lat, lab) in enumerate(PINS):
        yy = my + 20 + i * 15
        cv.disc(lx + 6, yy + 3, 6, CRIMSON)
        ns = str(num)
        cv.text(lx + 6 - cv.text_w(ns, 1) // 2, yy, ns, 1, WHITE)
        cv.text(lx + 18, yy, lab, 1, INK)
    return y + 26 + panel_h + 10


def draw_timeline(cv, y):
    cv.text(MX, y, "THE DAY IN 24 HOURS", 2, NAVY)
    cv.text(MX + CW - cv.text_w("ALL TIMES UTC", 1), y + 4,
            "ALL TIMES UTC", 1, GREY)
    ty = y + 42
    cv.hline(MX, ty, CW, INK, 2)
    for h in range(0, 25, 3):
        x = MX + int(h / 24.0 * CW)
        cv.vline(x, ty - 4, 9, INK, 1)
        lab = "%02d:00" % h
        cv.text(x - cv.text_w(lab, 1) // 2, ty + 8, lab, 1, GREY)
    # events alternate above / below the line
    for i, (h, m, lab) in enumerate(TIMELINE):
        x = MX + int(((h * 60 + m) / 1440.0) * CW)
        cv.disc(x, ty, 4, CRIMSON)
        cv.ring(x, ty, 6, CRIMSON)
        tw = cv.text_w(lab, 1)
        lx = min(max(MX, x - tw // 2), MX + CW - tw)
        if i % 2 == 0:
            cv.vline(x, ty - 18, 14, CRIMSON, 1)
            cv.text(lx, ty - 28, lab, 1, INK)
        else:
            cv.vline(x, ty + 5, 14, CRIMSON, 1)
            cv.text(lx, ty + 20, lab, 1, INK)
    return y + 74


def draw_stories(cv, y):
    cv.text(MX, y, "THE WORLD, STORY BY STORY", 2, NAVY)
    cv.text(MX + CW - cv.text_w("36 STORIES  -  8 REGIONS", 1), y + 4,
            "36 STORIES  -  8 REGIONS", 1, GREY)
    gy = y + 24
    col_w = (CW - 3 * 12) // 4
    per_col = 9
    max_bottom = gy
    for c in range(4):
        x = MX + c * (col_w + 12)
        yy = gy
        for item in STORIES[c * per_col:(c + 1) * per_col]:
            region, head, deck = item
            cv.rect(x, yy + 1, 5, 5, CRIMSON)
            cv.text(x + 10, yy, region, 1, NAVY)
            n = draw_wrapped(cv, x, yy + 10, head, 1, INK, 39, 9)
            yy += 10 + n * 9 + 5
        max_bottom = max(max_bottom, yy)
        # vertical divider
        if c < 3:
            cv.vline(x + col_w + 6, gy, max(0, yy - gy), LGREY, 1)
    return max_bottom + 6

def draw_footer(cv, y):
    cv.hline(MX, y, CW, INK, 2)
    cv.text(MX, y + 8, "SPORT IN BRIEF", 1, NAVY)
    draw_wrapped(cv, MX, y + 20,
                 "CHESS: GUKESH AND SINDAROV DRAW GAME 3 IN 60 MOVES, "
                 "1.5-1.5; FRIDAY IS A REST DAY, GAME 4 ON SATURDAY. "
                 "TENNIS: SINNER OUT OF THE 2027 AUSTRALIAN OPEN AFTER "
                 "KNEE SURGERY. CRICKET: SOORYAVANSHI SMASHES 204 OFF 53 "
                 "VS UAE; INDIA A FACE SRI LANKA A IN DOHA. HOCKEY: INDIA "
                 "WOMEN BEAT JAPAN 4-0.",
                 1, INK, 148, 10)
    fy = y + 44
    cv.hline(MX, fy, CW, GREY, 1)
    cv.text(MX, fy + 6,
            "SOURCES: LIBRE NEWS OF THE WORLD, JAGRAN JOSH, DAILY JAGRAN, "
            "REUTERS, AP, NBC, MORNINGSTAR - SEE NEWS-SOURCES.MD",
            1, GREY)
    cv.text(MX, fy + 15,
            "DRAWN ENTIRELY BY CODE - NO NETWORK, NO PHOTOS, NO FONTS. "
            "DATE CHECK: FRIDAY 27 NOVEMBER 2026. ALL STORIES AS REPORTED "
            "ON FRIDAY 27 NOVEMBER 2026.",
            1, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_numbers(cv, 154)
    y = draw_lead(cv, y)
    y = draw_map_panel(cv, y)
    y = draw_timeline(cv, y)
    y = draw_stories(cv, y)
    draw_footer(cv, y)
    return cv


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(here, "output", "entry.png")
    cv = build()
    if os.path.isdir("/output"):
        # Grader mounts the repo read-only; /output is the writable target,
        # so it must be written FIRST, before any local copy attempt.
        primary = "/output/entry.png"
        size = write_png(cv, primary)
        try:
            write_png(cv, local)
        except OSError:
            pass  # local repo copy is best-effort only
    else:
        primary = local
        size = write_png(cv, primary)
    digest = hashlib.sha256(open(primary, 'rb').read()).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (primary, size, digest))


if __name__ == "__main__":
    main()
