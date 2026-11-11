"""Render assets/icon/calder-falls.svg to PNGs at the sizes the AppImage and
.desktop file want. Uses Qt's own SVG renderer, so nothing extra to install.

    QT_QPA_PLATFORM=offscreen python3 build/render-icons.py
"""

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

SIZES = (16, 32, 48, 64, 128, 256, 512)


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_dir = os.path.join(here, "assets", "icon")
    svg = os.path.join(icon_dir, "calder-falls.svg")
    _app = QGuiApplication(sys.argv)
    renderer = QSvgRenderer(svg)
    if not renderer.isValid():
        print(f"could not read {svg}", file=sys.stderr)
        return 1
    for size in SIZES:
        img = QImage(size, size, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(p)
        p.end()
        out = os.path.join(icon_dir, f"calder-falls-{size}.png")
        img.save(out)
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
