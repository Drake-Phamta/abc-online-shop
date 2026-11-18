"""Figures of Chapter 6 that put the code next to the screen it produces, with numbered red marks.

The code is read from the real source files (the line numbers are those of the file; a line is found by a pattern,
so the figure follows the code), and the screens are the screenshots of tests/e2e (run_e2e.mjs and
shot_product_kinds.mjs). Each mark joins a part of the screen to the line of code that produces it.
Run: python docs/evidence/code_screen/make_code_screens.py   (writes the PNG files next to this script)
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
JAVA = ROOT / "app" / "src" / "main" / "java" / "vn" / "ptit" / "ecom"
E2E = ROOT / "docs" / "evidence" / "e2e"
FONTS = Path("C:/Windows/Fonts")
MONO = ImageFont.truetype(str(FONTS / "consola.ttf"), 21)
MONO_B = ImageFont.truetype(str(FONTS / "consolab.ttf"), 21)
SANS_B = ImageFont.truetype(str(FONTS / "arialbd.ttf"), 24)
NUM = ImageFont.truetype(str(FONTS / "arialbd.ttf"), 22)
RED = (31, 95, 168)   # the blue of the change bars of the essay
LH = 29          # line height of the code
PAD = 14
KEYWORDS = set("""public private protected static final class extends implements return if else new throw void
long int double boolean record for this super null true false""".split())


def find(path, pattern, start=1):
    """Number of the first line at or after start that matches the pattern."""
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if i >= start and re.search(pattern, line):
            return i
    raise SystemExit(f"{path.name}: no line matches {pattern!r}")


def code_image(path, ranges, marks, width=860):
    """ranges: [(first, last)] line numbers; marks: {(first, last): n} boxes in the code."""
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []                      # (line number or None for a gap, text)
    for k, (a, b) in enumerate(ranges):
        if k:
            rows.append((None, "    ..."))
        rows += [(n, lines[n - 1]) for n in range(a, b + 1)]
    indent = min(len(t) - len(t.lstrip()) for n, t in rows if n and t.strip())
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_x = width - 52               # room for the number boxes on the right
    # lay out the tokens first: a long line continues on the next row with a hanging indent
    visual = []                      # (line number on the first row of a line, [(x, token, color, font)])
    first_row, last_row = {}, {}
    for n, text in rows:
        text = text[indent:] if n else text
        lead = len(text) - len(text.lstrip())
        x, cur = 62, []
        first_row[n] = len(visual)
        for tok in re.findall(r'"[^"]*"|//.*|/\*\*.*|\w+|\s+|.', text):
            if tok.startswith(("//", "/**", "*")) or not n:
                color, font = (120, 120, 120), MONO
            elif tok.startswith('"'):
                color, font = (20, 120, 50), MONO
            elif tok in KEYWORDS:
                color, font = (20, 60, 160), MONO_B
            else:
                color, font = (30, 30, 30), MONO
            w = probe.textlength(tok, font=font)
            if x + w > max_x and cur and not tok.isspace():
                visual.append((n if len(visual) == first_row[n] else None, cur))
                x, cur = 62 + probe.textlength(" " * (lead + 8), font=MONO), []
            if tok.isspace() and not cur and len(visual) > first_row[n]:
                continue
            cur.append((x, tok, color, font))
            x += w
        visual.append((n if len(visual) == first_row[n] else None, cur))
        last_row[n] = len(visual) - 1
    img = Image.new("RGB", (width, PAD * 2 + LH * len(visual)), (250, 250, 247))
    d = ImageDraw.Draw(img)
    for i, (n, toks) in enumerate(visual):
        y = PAD + i * LH
        if n:
            d.text((10, y), f"{n:>3}", font=MONO, fill=(150, 150, 150))
        for x, tok, color, font in toks:
            d.text((x, y), tok, font=font, fill=color)
    for (a, b), n in marks.items():
        y0, y1 = PAD + first_row[a] * LH - 3, PAD + last_row[b] * LH + LH - 4
        d.rectangle([56, y0, width - 46, y1], outline=RED, width=3)
        badge(d, width - 40, y0 + 1, n, square=True)
    return img


def badge(d, x, y, n, square=False):
    s = 30
    if square:
        d.rectangle([x, y, x + s, y + s], fill=RED)
    else:
        d.ellipse([x, y, x + s, y + s], fill=RED, outline=(255, 255, 255), width=2)
    w = d.textlength(str(n), font=NUM)
    d.text((x + (s - w) / 2, y + 3), str(n), font=NUM, fill=(255, 255, 255))


def screen_image(name, crop, marks, scale=1.0):
    """marks: [(x0, y0, x1, y1, n)] in the coordinates of the full screenshot."""
    img = Image.open(E2E / name).convert("RGB").crop(crop)
    if scale != 1.0:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1, n in marks:
        box = [round((x0 - crop[0]) * scale), round((y0 - crop[1]) * scale),
               round((x1 - crop[0]) * scale), round((y1 - crop[1]) * scale)]
        d.rectangle(box, outline=RED, width=4)
        badge(d, max(box[0] - 36, 2), max(box[1] - 4, 2), n)
    return img


def titled(title, img):
    out = Image.new("RGB", (img.width, img.height + 40), (255, 255, 255))
    ImageDraw.Draw(out).text((4, 6), title, font=SANS_B, fill=(40, 40, 40))
    out.paste(img, (0, 40))
    frame = ImageDraw.Draw(out)
    frame.rectangle([0, 40, img.width - 1, img.height + 39], outline=(190, 190, 190), width=1)
    return out


def row(parts, gap=36):
    h = max(p.height for p in parts)
    out = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), h), (255, 255, 255))
    x = 0
    for p in parts:
        out.paste(p, (x, 0))
        x += p.width + gap
    return out


def col(parts, gap=26):
    w = max(p.width for p in parts)
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), (255, 255, 255))
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.height + gap
    return out


def save(img, name):
    img.save(OUT / name)
    print(name, img.size)


# 1. Product kinds: BookDetail and LaptopDetail are Products and override kind() and specs()
book = JAVA / "model" / "product" / "BookDetail.java"
laptop = JAVA / "model" / "product" / "LaptopDetail.java"
b_cls, b_kind, b_specs = find(book, r"class BookDetail extends Product"), find(book, r"DetailKind kind\(\)"), find(book, r"List<Spec> specs\(\)")
l_cls, l_kind, l_specs = find(laptop, r"class LaptopDetail extends Product"), find(laptop, r"DetailKind kind\(\)"), find(laptop, r"List<Spec> specs\(\)")
left = col([
    titled("Code: model, BookDetail.java", code_image(book, [(b_cls, b_cls), (b_kind - 1, b_specs + 3)],
                                                       {(b_cls, b_cls): 1, (b_kind, b_kind): 2, (b_specs, b_specs + 3): 3}, width=820)),
    titled("Screen: product page of a book", screen_image("kind_book.png", (684, 136, 1224, 820),
                                                           [(692, 140, 1000, 302, 1), (692, 512, 850, 546, 2), (692, 552, 1218, 727, 3)], 1.0)),
])
right = col([
    titled("Code: model, LaptopDetail.java", code_image(laptop, [(l_cls, l_cls), (l_kind - 1, l_specs + 3)],
                                                         {(l_cls, l_cls): 1, (l_kind, l_kind): 2, (l_specs, l_specs + 3): 3}, width=820)),
    titled("Screen: product page of a laptop", screen_image("kind_laptop.png", (684, 136, 1224, 860),
                                                             [(692, 140, 1180, 342, 1), (692, 555, 900, 588, 2), (692, 594, 1218, 816, 3)], 1.0)),
])
save(row([left, right]), "cs_product_kinds.png")

# 2. Checkout: the totals of BR04 come from Order.Totals.of
order = JAVA / "model" / "order" / "Order.java"
t_rec = find(order, r"public record Totals")
t_disc, t_fee, t_tot = find(order, r"long discount = ", t_rec), find(order, r"long fee = ", t_rec), find(order, r"return new Totals", t_rec)
p_tot, p_first = find(order, r"Totals t = Totals.of"), find(order, r"OrderStatus first = ")
code = code_image(order, [(t_rec, t_tot + 2), (p_tot, p_first)],
                  {(p_tot, p_tot): 1, (t_disc, t_disc): 2, (t_fee, t_fee): 3, (t_tot, t_tot): 4, (p_first, p_first): 5}, width=1220)
scr = screen_image("08_checkout.png", (930, 205, 1302, 596),
                   [(952, 278, 1280, 307, 1), (952, 315, 1280, 344, 2), (952, 353, 1280, 382, 3), (952, 400, 1280, 442, 4), (955, 456, 1277, 506, 5)], 1.0)
save(row([titled("Code: model, Order.java", code), titled("Screen: checkout", scr)]), "cs_checkout.png")

# 3. Card payment: only an approved payment makes the order PAID; a declined one only adds an event
p_rec = find(order, r"public void recordCardPayment")
p_guard, p_last4 = find(order, r"paymentMethod != PaymentMethod.CARD", p_rec), find(order, r"String card = ", p_rec)
p_ok, p_else = find(order, r"getStatus\(\) == Payment.Status.APPROVED", p_rec), find(order, r"^\s*else\s*$", p_rec)
code = code_image(order, [(p_rec, p_else + 1)],
                  {(p_guard, p_guard + 1): 1, (p_else, p_else + 1): 2, (p_last4, p_last4): 3, (p_ok, p_ok + 1): 4}, width=1560)
scr = screen_image("10_payment_declined.png", (144, 136, 1300, 740),
                   [(164, 198, 530, 246, 1), (164, 255, 876, 341, 2), (955, 386, 1278, 450, 3)], 1.0)
save(col([titled("Code: model, Order.java", code), titled("Screen: card payment after a declined card", scr)]), "cs_payment.png")

# 4. Order board: the buttons are the transitions that OrderStatus allows for the sales staff
st = JAVA / "model" / "order" / "OrderStatus.java"
s_enum, s_static = find(st, r"PENDING_PAYMENT, PLACED, PAID"), find(st, r"static \{")
s_paid1, s_paid2 = find(st, r"allow\(PAID, PROCESSING"), find(st, r"allow\(PAID, CANCELLED")
s_deliv, s_next = find(st, r"allow\(SHIPPED, DELIVERED"), find(st, r"public Set<OrderStatus> next")
code = code_image(st, [(s_enum, s_enum), (s_static, s_static + 10), (s_next, s_next + 4)],
                  {(s_enum, s_enum): 1, (s_paid1, s_paid2): 2, (s_deliv, s_deliv): 3, (s_next, s_next): 4}, width=1560)
scr = screen_image("13_order_board.png", (144, 244, 1300, 690),
                   [(146, 250, 1294, 284, 1), (166, 430, 386, 470, 2), (750, 430, 880, 470, 3), (166, 633, 386, 673, 4)], 1.0)
save(col([titled("Code: model, OrderStatus.java", code), titled("Screen: order board of the sales staff", scr)]), "cs_order_board.png")

# 5. Inventory: a negative stock is refused by Product.updateStock (BR12)
prod = JAVA / "model" / "product" / "Product.java"
u = find(prod, r"public void updateStock")
code = code_image(prod, [(u - 1, u + 3)], {(u, u): 1, (u + 1, u + 1): 2}, width=1560)
scr = screen_image("19_stock_refused.png", (144, 770, 1300, 900), [(1072, 862, 1168, 900, 1), (576, 822, 864, 875, 2)], 1.0)
save(col([titled("Code: model, Product.java", code), titled("Screen: inventory of the warehouse staff", scr)]), "cs_stock.png")
