#!/usr/bin/env python3
"""Regenerate SideLode.ico and SideLode.icns from logo.svg.

    pip install pillow
    python3 branding/genicons.py

It draws the <polygon> elements of logo.svg itself, so it needs no Inkscape or ImageMagick. That
means logo.svg may only contain filled polygons (optionally inside plain <g> groups); anything
else (paths, gradients, text) is not drawn and the script stops with an error instead.

The logo is scaled to fit a transparent square, so a logo that is not square is padded, not
stretched.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SVG = HERE / "logo.svg"
NAME = "SideLode"
FILL = 0.86  # the logo's longer side as a share of the square icon
SUPERSAMPLE = 4  # draw at 4x and scale down, for smooth edges
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
ICNS_MASTER = 1024  # Pillow writes the smaller .icns sizes from this one


def load_logo():
    root = ET.parse(SVG).getroot()
    if not root.tag.endswith("svg"):
        sys.exit("logo.svg: not an SVG")
    view = root.get("viewBox")
    if not view:
        sys.exit("logo.svg: needs a viewBox")
    _, _, width, height = (float(v) for v in view.replace(",", " ").split())

    polygons = []
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag in ("svg", "g", "title", "desc"):
            continue
        if tag != "polygon":
            sys.exit("logo.svg: <%s> is not supported, only <polygon> (see the top of this file)" % tag)
        numbers = [float(v) for v in element.get("points").replace(",", " ").split()]
        points = list(zip(numbers[0::2], numbers[1::2]))
        polygons.append((points, element.get("fill", "#000000")))
    if not polygons:
        sys.exit("logo.svg: no polygons found")
    return width, height, polygons


def render(size, logo):
    width, height, polygons = logo
    big = size * SUPERSAMPLE
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = big * FILL / max(width, height)
    left = (big - width * scale) / 2
    top = (big - height * scale) / 2
    for points, colour in polygons:
        draw.polygon([(left + x * scale, top + y * scale) for x, y in points], fill=colour)
    return image.resize((size, size), Image.LANCZOS)


def main():
    logo = load_logo()
    master = render(ICNS_MASTER, logo)
    master.save(HERE / (NAME + ".ico"), sizes=[(s, s) for s in ICO_SIZES])
    master.save(HERE / (NAME + ".icns"))
    print("wrote %s.ico and %s.icns" % (NAME, NAME))


if __name__ == "__main__":
    main()
