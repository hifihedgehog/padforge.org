# -*- coding: utf-8 -*-
"""Stage the app's 3D controller previews as product photography.

The colorway screenshots are full app windows: sidebar, tab strips, an
appearance picker, and motor buttons. This lifts the controller out and
places it on a clean stage.

The mistake this replaced: cropping tight to the controller's bounding
box. A bounding box by definition touches the product at its widest
points, so the grips and shoulders ran straight off the frame edge and
read as amputated. A product shot needs MARGIN, so the subject is
measured, then composited onto a canvas sized as a multiple of the
subject, and the leftover is filled with the backdrop. The product never
touches an edge.
"""
import io, os, glob, os.path
from PIL import Image, ImageDraw, ImageFilter

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(_ROOT, "assets")
OUT = os.path.join(_ROOT, "assets", "render")
os.makedirs(OUT, exist_ok=True)

# The render viewport inside the app window: right of the sidebar, below
# the appearance picker (measured: bright UI ends at 0.178 of source
# height, the controller's shoulders begin at 0.180), above the motor row.
VIEW = (0.21, 0.179, 0.995, 0.88)

# Margin around the subject, as a fraction of subject size. Generous on
# purpose: negative space is what makes a product read as staged rather
# than cropped.
PAD_X, PAD_TOP, PAD_BOTTOM = 0.17, 0.16, 0.26

OUT_H = 1000

# The site's canvas colour (--bg). The staged render must resolve to this
# at its edges or the image reads as a pasted rectangle.
PAGE_BG = (6, 8, 12)


def subject_box(view, bg, thresh=14):
    """Extent of the controller by content density, not by first pixel.

    A raw bounding box catches stray antialiasing and the backdrop's own
    gradient; a density profile finds where the product actually is.
    """
    g = view.convert("L")
    w, h = g.size
    px = g.load()
    cols = [(x, sum(1 for y in range(0, h, 3) if abs(px[x, y] - bg) > thresh))
            for x in range(0, w, 2)]
    rows = [(y, sum(1 for x in range(0, w, 3) if abs(px[x, y] - bg) > thresh))
            for y in range(0, h, 2)]
    cmax = max(n for _, n in cols) or 1
    rmax = max(n for _, n in rows) or 1
    xs = [x for x, n in cols if n > cmax * 0.05]
    ys = [y for y, n in rows if n > rmax * 0.05]
    if not xs or not ys:
        return None
    return xs[0], ys[0], xs[-1], ys[-1]


def stage(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    view = im.crop((int(w * VIEW[0]), int(h * VIEW[1]),
                    int(w * VIEW[2]), int(h * VIEW[3])))
    bg_rgb = view.getpixel((view.width // 2, 3))
    bg_lum = int(0.2126 * bg_rgb[0] + 0.7152 * bg_rgb[1] + 0.0722 * bg_rgb[2])

    box = subject_box(view, bg_lum)
    if box is None:
        return None
    sx0, sy0, sx1, sy1 = box
    sw, sh = sx1 - sx0, sy1 - sy0

    # Canvas sized from the SUBJECT, so every finish gets the same
    # proportional breathing room regardless of controller shape.
    cw = int(sw * (1 + PAD_X * 2))
    ch = int(sh * (1 + PAD_TOP + PAD_BOTTOM))

    # Widest source crop available, so the app's own lighting and contact
    # shadow come along with the product.
    px0 = max(0, sx0 - int(sw * PAD_X))
    py0 = max(0, sy0 - int(sh * PAD_TOP))
    px1 = min(view.width, sx1 + int(sw * PAD_X))
    py1 = min(view.height, sy1 + int(sh * PAD_BOTTOM))
    piece = view.crop((px0, py0, px1, py1))

    # The backdrop is EXTENDED FROM THE SOURCE, not filled flat. A flat
    # fill leaves a visible rectangular seam wherever the app's own
    # gradient meets it; a heavily blurred cover-scale of the same pixels
    # continues that gradient with nothing to see.
    cover = piece.resize(
        (max(cw, int(piece.width * ch / piece.height)),
         max(ch, int(piece.height * cw / piece.width))), Image.LANCZOS)
    left = (cover.width - cw) // 2
    top = (cover.height - ch) // 2
    canvas = cover.crop((left, top, left + cw, top + ch))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=max(cw, ch) // 14))
    canvas = Image.blend(canvas, Image.new("RGB", (cw, ch), bg_rgb), 0.55)

    # Fade the canvas to the PAGE's own background colour along ALL FOUR
    # edges, so the image's border pixels ARE the page. An elliptical
    # vignette cannot do this: an ellipse touches the mid-left and
    # mid-right edges, which is exactly where the frame stayed visible.
    # A uniform inset band fades every edge equally.
    band = int(min(cw, ch) * 0.17)
    edge = Image.new("L", (cw, ch), 255)
    ImageDraw.Draw(edge).rectangle([band, band, cw - band, ch - band], fill=0)
    edge = edge.filter(ImageFilter.GaussianBlur(radius=band * 0.62))
    canvas = Image.composite(Image.new("RGB", (cw, ch), PAGE_BG), canvas, edge)

    ox = int((cw - piece.width) / 2)
    oy = max(0, int(sh * PAD_TOP - (sy0 - py0)))

    # Feather the paste so even the blurred backdrop cannot show a hard
    # boundary at the piece's edge.
    mask = Image.new("L", (piece.width, piece.height), 0)
    f = max(6, min(piece.width, piece.height) // 22)
    ImageDraw.Draw(mask).rectangle([f, f, piece.width - f, piece.height - f], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=f))
    canvas.paste(piece, (ox, oy), mask)

    tw = int(cw * (OUT_H / ch))
    return canvas.resize((tw, OUT_H), Image.LANCZOS)


made = []
for path in sorted(glob.glob(os.path.join(SRC, "screenshot-colorway-*.jpg"))):
    name = os.path.basename(path)[len("screenshot-colorway-"):-len(".jpg")]
    img = stage(path)
    if img is None:
        print("skip", name); continue
    dst = os.path.join(OUT, "pad-%s.jpg" % name)
    img.save(dst, quality=90, optimize=True)
    made.append((name, img.size, os.path.getsize(dst) // 1024))

for n, s, kb in made:
    print("%-28s %sx%s  %dKB" % (n, s[0], s[1], kb))
print("total:", len(made))
