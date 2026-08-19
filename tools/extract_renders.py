# -*- coding: utf-8 -*-
"""Stage the app's 3D controller previews as product photography.

The colorway screenshots are full app windows: sidebar, tab strips, an
appearance picker, and motor buttons. This lifts the controller out and
places it on a clean stage.

Three failures this script exists to avoid, each one shipped once:

1. **Cropping to the subject's bounding box.** A bounding box touches the
   product at its widest points, so grips and shoulders ran off the frame
   and the controller read as amputated. The canvas is sized independently
   and the product never touches an edge.

2. **A flat backdrop fill, then an elliptical vignette.** A flat fill
   meets the app's own gradient at a visible rectangular seam. An ellipse
   fails to hide it, because an ellipse touches the mid-left and mid-right
   edges, which is exactly where the frame stayed visible. The backdrop is
   extended from the source pixels and every edge fades to the page colour
   through a uniform inset band.

3. **Measuring each finish separately.** Per-image measurement is polluted
   by each finish's own contact shadow and brightness: across one family
   the measured top varied by 224px and the bottom by 252px, so the
   controller jumped vertically as the finishes crossfaded. The app's 3D
   camera is FIXED, so every finish in a family occupies the same region.
   Pass one measures the family, pass two stages every member inside that
   single shared frame. Framing is then identical by construction.
"""
import os, glob, os.path, re
from PIL import Image, ImageDraw, ImageFilter

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(_ROOT, "assets")
OUT = os.path.join(_ROOT, "assets", "render")
os.makedirs(OUT, exist_ok=True)

# The render viewport inside the app window: right of the sidebar, below
# the appearance picker (measured: bright UI ends at 0.178 of source
# height, the controller's shoulders begin at 0.180), above the motor row.
VIEW = (0.21, 0.179, 0.995, 0.88)

# One fixed canvas for every finish, subject normalised and centred.
OUT_W, OUT_H = 1500, 1000
SUBJECT_W = 0.70      # subject width as a fraction of canvas width
SUBJECT_CY = 0.50     # subject centre as a fraction of canvas height


def viewport(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.crop((int(w * VIEW[0]), int(h * VIEW[1]),
                    int(w * VIEW[2]), int(h * VIEW[3])))


def measure(view, thresh=40):
    """Extent of the controller by content density within one viewport.

    The threshold is deliberately high. At 12 the backdrop's own gradient
    clears it and the measured frame becomes the entire viewport, which is
    no measurement at all. At 40 only the solid product registers.
    """
    g = view.convert("L")
    w, h = g.size
    px = g.load()
    bg = px[3, h // 2]
    cols = [(x, sum(1 for y in range(0, h, 3) if abs(px[x, y] - bg) > thresh))
            for x in range(0, w, 2)]
    rows = [(y, sum(1 for x in range(0, w, 3) if abs(px[x, y] - bg) > thresh))
            for y in range(0, h, 2)]
    cmax = max(n for _, n in cols) or 1
    rmax = max(n for _, n in rows) or 1
    xs = [x for x, n in cols if n > cmax * 0.06]
    ys = [y for y, n in rows if n > rmax * 0.06]
    if not xs or not ys:
        return None
    return xs[0], ys[0], xs[-1], ys[-1]


def family_of(name):
    return re.split(r"[-_]", name, maxsplit=1)[0]


paths = sorted(glob.glob(os.path.join(SRC, "screenshot-colorway-*.jpg")))
names = [os.path.basename(p)[len("screenshot-colorway-"):-len(".jpg")] for p in paths]

# ── Pass 1: one frame per family, the union of what any finish reaches ──
frames = {}
for path, name in zip(paths, names):
    box = measure(viewport(path))
    if box is None:
        continue
    fam = family_of(name)
    if fam in frames:
        a = frames[fam]
        frames[fam] = (min(a[0], box[0]), min(a[1], box[1]),
                       max(a[2], box[2]), max(a[3], box[3]))
    else:
        frames[fam] = box
for fam, b in sorted(frames.items()):
    print("frame %-11s x %4d..%4d  y %4d..%4d  (%d x %d)"
          % (fam, b[0], b[2], b[1], b[3], b[2] - b[0], b[3] - b[1]))


# ── Pass 2: stage every finish inside its family's shared frame ─────────
def stage(path, name):
    view = viewport(path)
    fam = family_of(name)
    if fam not in frames:
        return None
    sx0, sy0, sx1, sy1 = frames[fam]
    sw, sh = sx1 - sx0, sy1 - sy0
    if sw <= 0 or sh <= 0:
        return None

    bg_rgb = view.getpixel((view.width // 2, 3))

    # Widest crop the source allows around the shared frame, so the app's
    # own lighting and contact shadow travel with the product.
    px0 = max(0, sx0 - int(sw * 0.5))
    py0 = max(0, sy0 - int(sh * 0.5))
    px1 = min(view.width, sx1 + int(sw * 0.5))
    py1 = min(view.height, sy1 + int(sh * 0.5))
    piece = view.crop((px0, py0, px1, py1))

    scale = (OUT_W * SUBJECT_W) / sw
    piece = piece.resize((max(1, int(piece.width * scale)),
                          max(1, int(piece.height * scale))), Image.LANCZOS)
    sub_cx = (sx0 - px0 + sw / 2) * scale
    sub_cy = (sy0 - py0 + sh / 2) * scale

    cover = piece.resize(
        (max(OUT_W, int(piece.width * OUT_H / piece.height)),
         max(OUT_H, int(piece.height * OUT_W / piece.width))), Image.LANCZOS)
    cl = (cover.width - OUT_W) // 2
    ct = (cover.height - OUT_H) // 2
    canvas = cover.crop((cl, ct, cl + OUT_W, ct + OUT_H))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=max(OUT_W, OUT_H) // 14))
    canvas = Image.blend(canvas, Image.new("RGB", (OUT_W, OUT_H), bg_rgb), 0.55)

    ox = int(OUT_W / 2 - sub_cx)
    oy = int(OUT_H * SUBJECT_CY - sub_cy)

    mask = Image.new("L", (piece.width, piece.height), 0)
    f = max(6, min(piece.width, piece.height) // 18)
    ImageDraw.Draw(mask).rectangle([f, f, piece.width - f, piece.height - f], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=f))
    canvas.paste(piece, (ox, oy), mask)

    # The edge fade is done in CSS, to TRANSPARENT, not baked here to a
    # page colour. These renders appear on two different section
    # backgrounds, and a baked colour can only ever match one of them.
    return canvas


made = 0
for path, name in zip(paths, names):
    img = stage(path, name)
    if img is None:
        print("skip", name)
        continue
    img.save(os.path.join(OUT, "pad-%s.jpg" % name), quality=90, optimize=True)
    made += 1
print("staged:", made)
