# -*- coding: utf-8 -*-
"""Trim the dead black margin the capture harness bakes around each window.

The app screenshots arrive 2582x1550 with an 11px pure-black margin on the
left, right and top, and none at the bottom. That margin is invisible on a
dark page right up until the screen is staged as an object: the rig rounds
its own box and draws a rim light on it, and with the margin present that
rim traces the edge of the BLACK BORDER instead of the edge of the window.
The result is a rounded frame with a square window floating inside it, off
by 11px on three sides, which is exactly what "the windows have corners and
you aren't following their edges" describes.

Cropping the margin makes the image edge and the window edge the same line,
so the rig's radius and rim light land on the window itself.

Idempotent by construction: it measures each file and crops only what is
actually black, so re-running after a fresh capture is safe and re-running
on already-trimmed files is a no-op.
"""
import glob, os, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
THRESH = 10          # below this luminance the pixel is outside the window


def margin(im):
    """Black margin on each side, as (left, right, top, bottom)."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    midy, midx = h // 2, w // 2

    def walk(rng, horiz, fixed):
        for i in rng:
            if (px[i, fixed] if horiz else px[fixed, i]) > THRESH:
                return i
        return 0

    left = walk(range(0, 160), True, midy)
    right = w - 1 - walk(range(w - 1, w - 160, -1), True, midy)
    top = walk(range(0, 160), False, midx)
    bottom = h - 1 - walk(range(h - 1, h - 160, -1), False, midx)
    return left, right, top, bottom


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "assets", "screenshot-*.jpg")))
    trimmed = clean = 0
    for path in files:
        im = Image.open(path)
        l, r, t, b = margin(im)
        if not (l or r or t or b):
            clean += 1
            continue
        w, h = im.size
        im.crop((l, t, w - r, h - b)).save(path, quality=92, optimize=True)
        trimmed += 1
        print("trimmed %-52s l%d r%d t%d b%d  ->  %dx%d"
              % (os.path.basename(path), l, r, t, b, w - l - r, h - t - b))
    print("\n%d trimmed, %d already clean, %d total" % (trimmed, clean, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
