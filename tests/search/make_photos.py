# -*- coding: utf-8 -*-
"""Customer-like photos for the photo search evaluation (docs/SPEC.md 6.2), made from the catalogue images.

Three photos per product, written to tests/search/photos/<SKU>_<variant>.jpg:
  crop        the middle 80 % of the picture, turned by 8 degrees (a photo taken a little askew)
  dark        30 % darker, lower contrast, slightly blurred (a shop corner, a phone camera)
  background  the product at 70 % size on a textured beige background (not the catalogue's plain one)
They measure robustness to framing, light and background, not recognition of a different photo of the same model.
Deterministic: the same catalogue gives the same photos. Usage: python tests/search/make_photos.py
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "app" / "src" / "main" / "resources" / "static" / "img" / "products"
OUT = Path(__file__).resolve().parent / "photos"


def crop(im):
    w, h = im.size
    c = im.crop((int(w * 0.1), int(h * 0.1), int(w * 0.9), int(h * 0.9)))
    return c.rotate(8, resample=Image.BICUBIC, expand=False, fillcolor=c.getpixel((2, 2)))


def dark(im):
    im = ImageEnhance.Brightness(im).enhance(0.7)
    im = ImageEnhance.Contrast(im).enhance(0.85)
    return im.filter(ImageFilter.GaussianBlur(1.2))


def background(im, seed):
    rnd = random.Random(seed)
    w, h = im.size
    bg = Image.new("RGB", (w, h), (214, 196, 168))
    px = bg.load()
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-14, 14) + (8 if (y // 6) % 2 else 0)
            px[x, y] = (214 + n, 196 + n, 168 + n)
    small = im.resize((int(w * 0.7), int(h * 0.7)), Image.LANCZOS)
    # cut the product out of its plain catalogue background (pixels far from the border colour), soft edge
    sw, sh = small.size
    border = [small.getpixel((x, y)) for x in range(sw) for y in (0, 1, sh - 2, sh - 1)] + \
             [small.getpixel((x, y)) for y in range(sh) for x in (0, 1, sw - 2, sw - 1)]
    br, bgc, bb = (sum(c[k] for c in border) / len(border) for k in range(3))
    mask = Image.new("L", small.size, 0)
    mp, sp = mask.load(), small.load()
    for y in range(sh):
        for x in range(sw):
            r, g, b = sp[x, y]
            if ((r - br) ** 2 + (g - bgc) ** 2 + (b - bb) ** 2) ** 0.5 > 40:
                mp[x, y] = 255
    mask = mask.filter(ImageFilter.GaussianBlur(1.5))
    bg.paste(small, ((w - sw) // 2, (h - sh) // 2), mask)
    return bg


def main():
    OUT.mkdir(exist_ok=True)
    products = json.loads((ROOT / "db" / "seed" / "products.json").read_text(encoding="utf-8"))
    n = 0
    for i, p in enumerate(products):
        src = IMAGES / p["image_file"]
        im = Image.open(src).convert("RGB")
        im.thumbnail((640, 640))
        for name, photo in (("crop", crop(im)), ("dark", dark(im)), ("background", background(im, i))):
            photo.save(OUT / f"{p['sku']}_{name}.jpg", quality=88)
            n += 1
    print(f"{n} photos in {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
