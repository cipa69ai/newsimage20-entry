#!/usr/bin/env python3
"""News poster for Friday 20 November 2026.

Draws a 1024x1024 newspaper front page summing up the day's world news
with pure Python stdlib (hand-written PNG encoder + 5x7 bitmap font).
Deterministic: no clock, no randomness, no network. Running it twice
writes byte-identical output.
"""

import binascii
import hashlib
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (22, 22, 22)
RED = (163, 22, 33)
NAVY = (30, 58, 95)
BLUE = (43, 93, 138)
GREEN = (63, 122, 74)
GOLD = (217, 164, 65)
LIGHT = (216, 230, 242)
WHITE = (255, 255, 255)
GREY = (110, 105, 95)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, '#' = on, '.' = off.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '*': ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
    '<': ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    '>': ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self):
        self.buf = bytearray(PAPER * (W * H))

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def circle(self, cx, cy, r, c):
        # outline, one pixel
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.px(cx + sx, cy + sy, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def text(self, s, x, y, scale, c, align="left"):
        s = s.upper()  # the 5x7 font only carries capitals
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def para(self, s, x, y, max_w, scale, c, lh=None):
        lines = wrap(s, max_w, scale)
        step = lh or int(9 * scale)
        for i, ln in enumerate(lines):
            self.text(ln, x, y + i * step, scale, c)
        return y + len(lines) * step


def draw_flag(c, x, y, w, h, kind):
    """Small flag chips, w x h, drawn from stripes/blocks."""
    if kind == "usa":
        for i in range(7):
            c.fill_rect(x, y + i * h // 7, w, h // 7 + 1,
                        RED if i % 2 == 0 else WHITE)
        c.fill_rect(x, y, w * 2 // 5, h * 4 // 7, NAVY)
        for sx in range(3):
            for sy in range(2):
                c.px(x + 4 + sx * 9, y + 4 + sy * 8, WHITE)
    elif kind == "china":
        c.fill_rect(x, y, w, h, RED)
        c.fill_circle(x + 12, y + 10, 4, GOLD)
        for sx, sy in ((26, 5), (32, 9), (32, 16), (26, 20)):
            c.fill_circle(x + sx, y + sy, 2, GOLD)
    elif kind == "russia":
        c.fill_rect(x, y, w, h // 3, WHITE)
        c.fill_rect(x, y + h // 3, w, h // 3, BLUE)
        c.fill_rect(x, y + 2 * h // 3, w, h // 3, RED)


def draw_globe(c, cx, cy, r):
    c.fill_circle(cx, cy, r, BLUE)
    # graticule, clipped to the disc
    for dx in (-90, -45, 0, 45, 90):
        for yy in range(cy - r, cy + r + 1):
            xx = cx + dx
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                c.px(xx, yy, LIGHT)
    for dy in (-64, 0, 64):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (dy) ** 2 <= r * r:
                c.px(xx, cy + dy, LIGHT)
    # land blobs, stamped as filled discs clipped to the globe
    for bx, by, br in ((cx - 52, cy - 42, 30), (cx - 30, cy - 30, 22),
                       (cx + 48, cy - 18, 26), (cx + 62, cy + 38, 24),
                       (cx - 58, cy + 48, 22), (cx + 8, cy + 62, 20)):
        for yy in range(by - br, by + br + 1):
            for xx in range(bx - br, bx + br + 1):
                if (xx - bx) ** 2 + (yy - by) ** 2 <= br * br and \
                        (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    c.px(xx, yy, GREEN)
    c.circle(cx, cy, r, INK)
    c.circle(cx, cy, r - 1, INK)


def draw_scales(c, x, y, s):
    # simple scales of justice, s = overall size
    c.vline(x + s // 2, y, s, INK, 3)
    c.hline(x, y + 6, s, INK, 3)
    for side in (0, s):
        c.line(x + side, y + 6, x + side - 10, y + s - 14, INK)
        c.line(x + side, y + 6, x + side + 10, y + s - 14, INK)
        c.fill_rect(x + side - 12, y + s - 14, 24, 4, INK)


def draw_probe(c, x, y, s):
    # Voyager-style probe: star + dish + trail
    cx, cy = x + s // 2, y + s // 2
    c.line(cx - 16, cy, cx + 16, cy, GOLD)
    c.line(cx, cy - 16, cx, cy + 16, GOLD)
    c.line(cx - 11, cy - 11, cx + 11, cy + 11, GOLD)
    c.line(cx - 11, cy + 11, cx + 11, cy - 11, GOLD)
    c.fill_rect(cx - 4, cy - 4, 8, 8, INK)
    for i, (dx, dy) in enumerate(((24, -20), (30, -26), (36, -32))):
        c.fill_circle(cx + dx, cy + dy, 3 - i // 2, GREY)


def draw_controller(c, x, y, s):
    # game controller silhouette
    c.fill_rect(x + 6, y + 14, s - 12, s - 28, INK)
    c.fill_circle(x + 14, y + s - 14, 12, INK)
    c.fill_circle(x + s - 14, y + s - 14, 12, INK)
    c.fill_rect(x + 16, y + 24, 8, 8, PAPER)
    c.fill_rect(x + s - 24, y + 24, 8, 8, RED)
    c.fill_rect(x + s - 24, y + 36, 8, 8, GOLD)


def build():
    c = Canvas()
    # ---- masthead
    c.fill_rect(0, 0, W, 8, INK)
    c.text("THE WORLD TODAY", 512, 24, 6, INK, align="center")
    c.hline(24, 78, W - 48, INK, 2)
    c.text("FRIDAY, 20 NOVEMBER 2026", 512, 88, 3, RED, align="center")
    c.hline(24, 118, W - 48, INK, 2)

    # ---- hero: text left, globe right
    c.text("HISTORIC SUMMIT - FIRST EVER", 24, 140, 2, RED)
    c.text("TRUMP, XI &", 24, 172, 5, INK)
    c.text("PUTIN MEET", 24, 217, 5, INK)
    c.text("IN SHENZHEN", 24, 262, 5, INK)
    c.para("The three leaders sign a 'peace declaration' "
           "in Shenzhen - nuclear arms control and trade "
           "on the table.", 24, 330, 520, 2, INK, lh=20)
    c.para("Trump says the Iran decision can wait until "
           "2027: 'We'll see what happens after Jan 1.'",
           24, 420, 520, 2, GREY, lh=20)

    draw_globe(c, 790, 300, 128)
    # flag chips under the globe
    fx = 640
    for kind, label in (("usa", "USA"), ("china", "CHINA"), ("russia", "RUSSIA")):
        draw_flag(c, fx, 448, 72, 44, kind)
        c.text(label, fx + 36, 500, 2, INK, align="center")
        fx += 108

    c.hline(24, 548, W - 48, INK, 2)

    # ---- supporting row: three columns
    cols = [
        (24, 344, draw_scales, "WORLD COURT:",
         ["MYANMAR", "GUILTY OF", "GENOCIDE"],
         "ICJ rules the 2017 Rohingya crackdown was genocide."),
        (352, 672, draw_probe, "VOYAGER 1:",
         ["ONE", "LIGHT-DAY", "FROM EARTH"],
         "NASA confirms the farthest human object passes the milestone."),
        (680, 1000, draw_controller, "GAME BUSINESS",
         ["GTA 6 SALES", "PASS $1.8", "BILLION"],
         "Launch-week sales top The Odyssey's global box-office run."),
    ]
    for x0, x1, icon, kicker, heads, summary in cols:
        icon(c, x0 + 8, 568, 64)
        c.text(kicker, x0 + 84, 576, 2, RED)
        for i, ln in enumerate(heads):
            c.text(ln, x0 + 84, 600 + i * 24, 3, INK)
        c.para(summary, x0 + 8, 678, x1 - x0 - 16, 2, INK, lh=18)
        c.vline(x1, 568, 160, GREY, 1) if x1 < 1000 else None

    c.hline(24, 748, W - 48, INK, 2)

    # ---- strip: two half-width items
    c.fill_rect(24, 768, 6, 64, RED)
    c.text("CYCLONE AKVAN", 44, 770, 3, INK)
    c.text("300,000 EVACUATED IN ODISHA.", 44, 800, 2, INK)
    c.fill_rect(524, 768, 6, 64, RED)
    c.text("ANTHROPIC'S $81.3BN IPO", 544, 770, 3, INK)
    c.text("Largest IPO on record.", 544, 800, 2, INK)

    # ---- ticker
    c.fill_rect(0, 856, W, 96, INK)
    c.text("HOUTHIS HIT RIYADH TOWER  *  VAN GOGH SELLS FOR $190.4M",
           512, 872, 2, WHITE, align="center")
    c.text("HAYABUSA2 ENGINE TROUBLE ENDS ASTEROID LANDING  *  TAIWAN STEADIES STOCKS",
           512, 900, 2, WHITE, align="center")
    c.text("S. KOREA EXPORTS TOP $1 TRILLION  *  GENOA AIRPORT HALTED BY DRONES",
           512, 928, 2, WHITE, align="center")

    # ---- footer
    c.text("FRIDAY 20 NOVEMBER 2026 - THE WORLD IN ONE IMAGE",
           512, 976, 2, GREY, align="center")
    c.fill_rect(0, 1016, W, 8, INK)

    return c.buf


def png_bytes(rgb, w, h):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build(), W, H)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes sha256=%s" % (
        path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
