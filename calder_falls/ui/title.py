"""The title screen: the mill's water tower in fog, its red light blinking.
With fourth-wall effects on, the line under the title changes between
launches."""

import os

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .. import paths


def subtitle_for(profile, fourth_wall):
    if not fourth_wall:
        return "Ostrander County, October 1986"
    seen = set(profile.endings_seen)
    n = profile.launches
    if "quiet_house" in seen and n % 2 == 0:
        return "Somewhere, someone clips it."
    if "dawn" in seen and n % 3 == 0:
        return "The line stays open."
    if "broadcast" in seen:
        return "Now on every station."
    if n <= 1:
        return "Ostrander County, October 1986"
    if n <= 3:
        return "You came back."
    if n <= 6:
        return "one six one zero, one"
    return "We have kept your place."


class Tower(QWidget):
    def __init__(self):
        super().__init__()
        svg = os.path.join(paths.data_dir(), "assets", "icon", "calder-falls.svg")
        self.renderer = QSvgRenderer(svg)
        self.on = True
        self.blinks = True      # off with the no-flicker setting: the light stays lit
        self.setMinimumSize(300, 300)
        t = QTimer(self)
        t.timeout.connect(self._blink)
        t.start(900)

    def _blink(self):
        if not self.blinks:
            if not self.on:
                self.on = True
                self.update()
            return
        self.on = not self.on
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        r = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        if self.renderer.isValid():
            self.renderer.render(p, r)
        if not self.on:
            # cover the light: the icon's light sits at (256, 70) of 512
            c = QPointF(r.left() + side * 256 / 512, r.top() + side * 70 / 512)
            g = QRadialGradient(c, side * 70 / 512)
            g.setColorAt(0, QColor("#1A1C1F"))
            g.setColorAt(0.5, QColor(26, 28, 31, 230))
            g.setColorAt(1, QColor(26, 28, 31, 0))
            p.setBrush(g)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(c, side * 70 / 512, side * 70 / 512)
        p.end()


class TitleScreen(QWidget):
    new_game = pyqtSignal()
    continue_game = pyqtSignal()
    load_game = pyqtSignal()
    settings = pyqtSignal()
    howto = pyqtSignal()
    quit = pyqtSignal()

    def __init__(self):
        super().__init__()
        h = QHBoxLayout(self)
        h.setContentsMargins(60, 40, 60, 40)
        self.tower = Tower()
        h.addWidget(self.tower, 3)
        col = QVBoxLayout()
        col.addStretch(1)
        title = QLabel("CALDER FALLS")
        title.setObjectName("bigtitle")
        self.sub = QLabel("")
        self.sub.setObjectName("subtitle")
        col.addWidget(title)
        col.addWidget(self.sub)
        col.addSpacing(30)
        self.buttons = {}
        for key, label, sig in (("new", "New game", self.new_game),
                                ("continue", "Continue", self.continue_game),
                                ("load", "Load", self.load_game),
                                ("settings", "Settings", self.settings),
                                ("howto", "How to Play", self.howto),
                                ("quit", "Quit", self.quit)):
            b = QPushButton(label)
            b.setObjectName("menu")
            b.setMinimumWidth(240)
            b.clicked.connect(sig.emit)
            col.addWidget(b)
            self.buttons[key] = b
        col.addStretch(2)
        h.addLayout(col, 2)

    def refresh(self, profile, fourth_wall, can_continue, flicker="gentle"):
        self.tower.blinks = flicker != "off"
        self.sub.setText(subtitle_for(profile, fourth_wall))
        self.buttons["continue"].setEnabled(can_continue)
        self.buttons["load"].setEnabled(can_continue)
