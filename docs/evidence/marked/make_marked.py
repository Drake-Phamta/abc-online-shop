"""Copies of diagrams A10 and D1 with numbered red marks for the essay (the notes under the figure explain each
number); the diagrams in vp/png stay unmarked. A mark is a red frame around one or more class boxes, found in the
image itself: a point inside a class gives the box of light blue around it.
Run: python docs/evidence/marked/make_marked.py
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RED = (31, 95, 168)   # the blue of the change bars of the essay
NUM = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)


def class_box(mask, x, y, step=3):
    """Bounding box of the light blue region (a class box) that contains (x, y), searched on every step-th pixel."""
    h, w = mask.shape
    sx, sy = x // step, y // step
    small = mask[::step, ::step]
    if not small[sy, sx]:   # the point fell on text: take the nearest blue pixel within 15 samples
        near = [(abs(dy) + abs(dx), sy + dy, sx + dx) for dy in range(-15, 16) for dx in range(-15, 16)
                if 0 <= sy + dy < small.shape[0] and 0 <= sx + dx < small.shape[1] and small[sy + dy, sx + dx]]
        if not near:
            raise SystemExit(f"no class at {x},{y}")
        _, sy, sx = min(near)
    seen = np.zeros_like(small, dtype=bool)
    q = deque([(sy, sx)])
    seen[sy, sx] = True
    y0 = y1 = sy
    x0 = x1 = sx
    while q:
        cy, cx = q.popleft()
        y0, y1, x0, x1 = min(y0, cy), max(y1, cy), min(x0, cx), max(x1, cx)
        for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
            if 0 <= ny < small.shape[0] and 0 <= nx < small.shape[1] and small[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return x0 * step, y0 * step, x1 * step + step, y1 * step + step


def whole_class(mask, x, y):
    """The compartments of a class (name, attributes, operations) are separated by black lines: join the blue
    regions just above and below until the whole class box is covered."""
    b = class_box(mask, x, y)
    while True:
        grown = b
        for py in (b[1] - 8, b[3] + 8):
            for cx in (b[0] + 8, (b[0] + b[2]) // 2, b[2] - 8):   # several probes: one may fall on the class name
                if 0 <= py < mask.shape[0] and mask[py, cx]:
                    o = class_box(mask, cx, py)
                    if abs(o[0] - b[0]) < 12 and abs(o[2] - b[2]) < 12:   # same column of the same class
                        grown = (min(grown[0], o[0]), min(grown[1], o[1]), max(grown[2], o[2]), max(grown[3], o[3]))
                        break
        if grown == b:
            return b
        b = grown


def mark(src, out, marks, pad=12):
    """marks: [(n, [points inside classes], extra (dx0, dy0, dx1, dy1) or None)]"""
    img = Image.open(ROOT / src).convert("RGB")
    a = np.asarray(img).astype(int)
    mask = (a[:, :, 2] > 200) & (a[:, :, 1] > 170) & (a[:, :, 0] < 160)   # the light blue fill of the classes
    d = ImageDraw.Draw(img)
    for n, points, extra, *where in marks:
        boxes = [whole_class(mask, x, y) for x, y in points]
        x0 = min(b[0] for b in boxes) - pad
        y0 = min(b[1] for b in boxes) - pad
        x1 = max(b[2] for b in boxes) + pad
        y1 = max(b[3] for b in boxes) + pad
        if extra:
            x0, y0, x1, y1 = x0 + extra[0], y0 + extra[1], x1 + extra[2], y1 + extra[3]
        x0, y0 = max(x0, 3), max(y0, 3)
        x1, y1 = min(x1, img.width - 4), min(y1, img.height - 4)
        d.rectangle([x0, y0, x1, y1], outline=RED, width=7)
        r = 26
        cx = x0 + r + 4 if where == ["left"] else x1 - r - 4                     # number in a corner, inside the frame
        cy = y1 - r - 4 if where == ["bottom"] else y0 + r + 4
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        w = d.textlength(str(n), font=NUM)
        d.text((cx - w / 2, cy - 20), str(n), font=NUM, fill=(255, 255, 255))
    img.save(OUT / out)
    print(out, img.size)


# points are inside the class boxes (coordinates of the PNG files)
mark("vp/png/A10.png", "A10_marked.png", [
    (1, [(250, 150), (1000, 150), (1750, 180), (2500, 120)], None),   # BookDetail, LaptopDetail, PhoneDetail, ApparelDetail
    (2, [(1000, 650)], None, "bottom"),                               # Product
    (3, [(250, 540)], (0, 0, 0, 130)),                                # Category with its tree loop below
    (4, [(3250, 100)], None),                                         # CustomerNew
    (4, [(4000, 560)], None),                                         # CustomerVIP
    (5, [(1750, 1580), (2400, 1560), (1750, 1850)], None),            # Payment, PayCredit, PayCash
])
mark("vp/png/D1.png", "D1_marked.png", [
    (1, [(1000, 640)], None, "bottom"),                               # Product: types and the identifier
    (2, [(250, 150), (1000, 160), (1750, 180), (2550, 120)], None),   # the four subclasses (Table per subclass)
    (3, [(3350, 680)], (0, 0, 55, 108), "left"),                      # Customer with the ends of places and has
    (4, [(1800, 1200)], None),                                        # Order
])
