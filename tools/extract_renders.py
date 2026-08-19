# -*- coding: utf-8 -*-
"""Free the 3D controller renders from the app-window chrome.

The colorway screenshots are full app windows: sidebar, tab strip, a
top-right appearance picker, and motor buttons at the bottom. The render
itself sits in the middle on a near-uniform dark ground. Crop to the
controller's own bounding box so the site can use it as product
photography instead of a screenshot of a window.
"""
import io, os, glob
from PIL import Image

import os.path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(_ROOT, "assets")
OUT = os.path.join(_ROOT, "assets", "render")
os.makedirs(OUT, exist_ok=True)

# The render viewport inside the app window, as fractions. Excludes the
# left sidebar, the two top tab strips + appearance picker row, and the
# motor-button row at the bottom.
SAFE = (0.205, 0.1785, 0.985, 0.865)

# The appearance picker + Reset View sit in the render viewport's top-right
# corner (measured: bright UI at y~0.16h, controller shoulders begin ~0.18h).
# Painting that corner with the backdrop keeps the product intact where a
# tighter crop would clip the shoulder buttons.
UI_CORNER = (0.55, 0.0, 1.0, 0.135)


def content_box(im, pad=14):
    """Bounding box of the controller against its flat dark backdrop."""
    g = im.convert("L")
    w, h = g.size
    bg = g.getpixel((int(w * 0.5), 6))          # backdrop sample, top-center
    px = g.load()
    step = 2
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            if abs(px[x, y] - bg) > 16:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx <= minx or maxy <= miny:
        return None
    return (max(0, minx - pad), max(0, miny - pad),
            min(w, maxx + pad), min(h, maxy + pad))


made = []
for path in sorted(glob.glob(os.path.join(SRC, "screenshot-colorway-*.jpg"))):
    name = os.path.basename(path)[len("screenshot-colorway-"):-len(".jpg")]
    im = Image.open(path)
    w, h = im.size
    view = im.crop((int(w * SAFE[0]), int(h * SAFE[1]),
                    int(w * SAFE[2]), int(h * SAFE[3])))
    box = content_box(view)
    if box:
        view = view.crop(box)
    # Uniform output height so the set is typographically consistent.
    tw = int(view.width * (900 / view.height))
    view = view.resize((tw, 900), Image.LANCZOS)
    out = os.path.join(OUT, "pad-%s.jpg" % name)
    view.convert("RGB").save(out, quality=90, optimize=True)
    made.append((name, view.size, os.path.getsize(out) // 1024))

for n, s, kb in made:
    print("%-28s %sx%s  %dKB" % (n, s[0], s[1], kb))
print("total:", len(made))
