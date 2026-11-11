"""The painted layer over the whole window: grain, fog, light flicker,
scanlines, and the dark CRT edges. Mouse events pass straight through it.
Color split, word swaps and the flashlight live in the text renderer,
since they need to know where the letters are."""

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget


def _noise_tile(seed, size=192):
    rng = random.Random(seed)
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    for y in range(size):
        for x in range(size):
            v = rng.random()
            if v > 0.55:
                g = rng.randint(120, 255)
                a = int((v - 0.55) * 255 / 0.45 * 0.6)
                img.setPixelColor(x, y, QColor(g, g, g, a))
    return img


def _scan_tile():
    img = QImage(8, 3, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    for x in range(8):
        img.setPixelColor(x, 2, QColor(0, 0, 0, 255))
    return img


class Overlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.stage = None
        self.tiles = [_noise_tile(i) for i in range(3)]
        self.scan = _scan_tile()
        self.frame = 0
        self.flash = 0.0
        self.fog_seed = [random.random() * 100 for _ in range(3)]
        self.rng = random.Random(1986)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(70)

    def set_stage(self, stage):
        self.stage = stage
        self.update()

    def _tick(self):
        self.frame += 1
        s = self.stage
        if s is None:
            return
        if self.flash > 0:
            self.flash = max(0.0, self.flash - 0.12)
        elif s.flicker > 0 and self.rng.random() < s.flicker * 0.05:
            self.flash = 0.15 + 0.25 * s.flicker * self.rng.random()
        self.update()

    def resizeEvent(self, _e):
        self.update()

    def paintEvent(self, _e):
        s = self.stage
        if s is None:
            return
        p = QPainter(self)
        r = self.rect()
        w, h = r.width(), r.height()

        if s.haze > 0:
            t = self.frame * 0.004
            for i, seed in enumerate(self.fog_seed):
                cx = w * (0.5 + 0.45 * math.sin(t * (0.6 + i * 0.2) + seed))
                cy = h * (0.5 + 0.35 * math.cos(t * (0.4 + i * 0.15) + seed))
                rad = max(w, h) * (0.45 + 0.1 * i)
                g = QRadialGradient(QPointF(cx, cy), rad)
                c = QColor(150, 152, 156, int(70 * s.haze))
                g.setColorAt(0, c)
                g.setColorAt(1, QColor(150, 152, 156, 0))
                p.fillRect(r, QBrush(g))

        if s.grain > 0:
            p.setOpacity(min(1.0, s.grain * 1.6))
            tile = self.tiles[self.frame % len(self.tiles)]
            ox = self.rng.randint(0, tile.width() - 1)
            oy = self.rng.randint(0, tile.height() - 1)
            brush = QBrush(tile)
            p.setBrushOrigin(-ox, -oy)
            p.fillRect(r, brush)
            p.setOpacity(1.0)

        if s.scanlines > 0:
            p.setOpacity(s.scanlines * 0.35)
            p.fillRect(r, QBrush(self.scan))
            p.setOpacity(1.0)

        # CRT edges: darker at the borders than the middle
        g = QRadialGradient(QPointF(w / 2, h / 2), max(w, h) * 0.75)
        g.setColorAt(0.55, QColor(0, 0, 0, 0))
        g.setColorAt(1.0, QColor(0, 0, 0, 120))
        p.fillRect(QRectF(r), QBrush(g))

        if self.flash > 0:
            p.fillRect(r, QColor(0, 0, 0, int(255 * self.flash)))
        p.end()
