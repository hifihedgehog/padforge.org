"""Writes each image's own width and height onto its <img> tag.

A lazy image with no size takes no room until it arrives, so the page grew by
thousands of pixels while a visitor scrolled it. With the two attributes the
browser keeps the image's shape free from the start. The stylesheet's
`img { height: auto }` lets the width still follow the layout.

usage: python tools/stamp_image_sizes.py [--check] page.html [page.html ...]

Run it after the screenshots change. --check changes nothing and exits 1 when
a tag lacks its size or carries a stale one.
"""
import io
import os
import re
import sys

from PIL import Image

IMG = re.compile(rb"<img\b[^>]*>")
SRC = re.compile(rb'\bsrc="([^"]*)"')
SIZE = re.compile(rb'\s+(?:width|height)="[^"]*"')


def stamped(tag, page_dir):
    """The tag with its file's size, or the tag unchanged when it names no local raster file."""
    m = SRC.search(tag)
    if not m:
        return tag
    src = m.group(1).decode("utf-8")
    if not src or "://" in src or src.startswith("data:") or src.lower().endswith(".svg"):
        return tag
    path = os.path.normpath(os.path.join(page_dir, src.split("?")[0]))
    if not os.path.isfile(path):
        raise SystemExit("no such image: %s" % path)
    with Image.open(path) as im:
        width, height = im.size
    stated = {name: int(value) for name, value in re.findall(rb'\b(width|height)="(\d+)"', tag)}
    if stated == {b"width": width, b"height": height}:
        return tag
    bare = SIZE.sub(b"", tag)
    at = SRC.search(bare).end()
    return bare[:at] + (' width="%d" height="%d"' % (width, height)).encode("ascii") + bare[at:]


def main():
    args = sys.argv[1:]
    check = "--check" in args
    pages = [a for a in args if a != "--check"]
    if not pages:
        raise SystemExit(__doc__)
    stale = 0
    for page in pages:
        raw = io.open(page, "rb").read()
        page_dir = os.path.dirname(os.path.abspath(page))
        changed = 0

        def swap(m):
            nonlocal changed
            # An icon shown at a fixed size keeps the size its tag states.
            if b"icon.png" in m.group(0) and SIZE.search(m.group(0)):
                return m.group(0)
            new = stamped(m.group(0), page_dir)
            if new != m.group(0):
                changed += 1
            return new

        out = IMG.sub(swap, raw)
        print("%s: %d of %d tags %s" % (page, changed, len(IMG.findall(raw)), "stale" if check else "stamped"))
        stale += changed
        if not check and out != raw:
            io.open(page, "wb").write(out)
    if check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
