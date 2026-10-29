"""Bake a Forma preview watermark into an image.

    python3 tools/watermark.py in.jpg out.jpg [--dark]

Tiles a diagonal FORMA · PREVIEW mark across the whole image and adds a corner
badge, so a screenshot of a preview page can't be used as finished marketing.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def watermark(src, dst, dark=False, max_w=2000):
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    W, H = im.size
    ink = (14, 14, 14) if dark else (255, 255, 255)

    # diagonal tiled mark
    size = max(24, W // 46)
    f = ImageFont.truetype(FONT_BOLD, size)
    text = "FORMA  ·  PREVIEW  ·  NOT FOR MARKETING"
    tw = int(f.getlength(text)) + size * 3
    th = size * 4
    diag = int(math.hypot(W, H)) + tw
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    alpha = 34 if dark else 58
    for row, y in enumerate(range(0, diag, th)):
        off = (row % 2) * (tw // 2)
        for x in range(-tw, diag, tw):
            d.text((x + off, y), text, font=f, fill=ink + (alpha,))
    layer = layer.rotate(28, resample=Image.BICUBIC)
    lx, ly = (layer.width - W) // 2, (layer.height - H) // 2
    layer = layer.crop((lx, ly, lx + W, ly + H))
    out = Image.alpha_composite(im.convert("RGBA"), layer)

    # corner badge
    d = ImageDraw.Draw(out)
    bs = max(14, W // 90)
    bf = ImageFont.truetype(FONT_MED, bs)
    label = "PRELIMINARY PREVIEW · FORMADESIGNS.IO"
    pad = bs // 1.2
    bw, bh = bf.getlength(label) + pad * 2, bs + pad * 2
    x0, y0 = W - bw - bs, H - bh - bs
    d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(14, 14, 14, 215))
    d.text((x0 + pad, y0 + pad - bs * 0.12), label, font=bf, fill=(220, 187, 122, 255))
    out.convert("RGB").save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    return dst


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    watermark(a[0], a[1], dark="--dark" in sys.argv)
