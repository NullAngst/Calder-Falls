"""The right sidebar. Every tab is a period object Brennick carries:
a spiral pad, Polaroids on a corkboard, a gas-station county map, and an
AM radio with the police band on its own knob."""

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

HAND = "Caveat"
LEDGER_HAND = "Cedarville Cursive"


# ---------------------------------------------------------------- notebook

class NotebookPage(QWidget):
    """A spiral pad page: ruled lines, red margin, his handwriting."""

    LINES_PER_PAGE = 16

    def __init__(self):
        super().__init__()
        self.lines = []
        self.page = 0
        self.ledger = False
        self.setMinimumHeight(420)

    def pages(self):
        return max(1, math.ceil(len(self.wrapped()) / self.LINES_PER_PAGE))

    def wrapped(self):
        out = []
        width = 30
        for entry in self.lines:
            words = entry.split()
            cur = ""
            for w in words:
                if cur and len(cur) + len(w) + 1 > width:
                    out.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                out.append(cur)
            out.append("")
        return out

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(8, 18, -8, -8)
        paper = QColor("#E9E2CF") if not self.ledger else QColor("#D8CFB4")
        p.fillRect(r, paper)
        # spiral
        p.setPen(QPen(QColor("#6B6B6B"), 2))
        for x in range(int(r.left()) + 14, int(r.right()) - 8, 18):
            p.drawEllipse(QRectF(x, r.top() - 10, 8, 18))
        lh = (r.height() - 30) / self.LINES_PER_PAGE
        p.setPen(QPen(QColor(110, 140, 180, 90), 1))
        for i in range(self.LINES_PER_PAGE + 1):
            y = r.top() + 26 + i * lh
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
        p.setPen(QPen(QColor(190, 70, 70, 120), 1))
        p.drawLine(QPointF(r.left() + 34, r.top()), QPointF(r.left() + 34, r.bottom()))
        font = QFont(LEDGER_HAND if self.ledger else HAND, 15 if self.ledger else 17)
        p.setFont(font)
        p.setPen(QColor("#1F2A44") if not self.ledger else QColor("#3A1F14"))
        lines = self.wrapped()
        chunk = lines[self.page * self.LINES_PER_PAGE:(self.page + 1) * self.LINES_PER_PAGE]
        for i, text in enumerate(chunk):
            y = r.top() + 26 + (i + 1) * lh - 5
            p.drawText(QPointF(r.left() + 42, y), text)
        if not self.lines:
            p.setPen(QColor(31, 42, 68, 120))
            p.drawText(QPointF(r.left() + 42, r.top() + 26 + lh - 5), "Nothing yet.")
        p.end()


class NotebookTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        self.page = NotebookPage()
        v.addWidget(self.page, 1)
        row = QHBoxLayout()
        self.prev = QPushButton("Back")
        self.next = QPushButton("Next")
        self.prev.setObjectName("flat")
        self.next.setObjectName("flat")
        self.label = QLabel("")
        self.label.setObjectName("small")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev.clicked.connect(lambda: self.flip(-1))
        self.next.clicked.connect(lambda: self.flip(1))
        row.addWidget(self.prev)
        row.addWidget(self.label, 1)
        row.addWidget(self.next)
        v.addLayout(row)
        self.refresh()

    def set_lines(self, lines, to_last=True):
        self.page.lines = list(lines)
        if to_last:
            self.page.page = self.page.pages() - 1
        self.refresh()

    def set_ledger(self, on):
        self.page.ledger = on
        self.page.update()

    def flip(self, d):
        self.page.page = max(0, min(self.page.pages() - 1, self.page.page + d))
        self.refresh()

    def refresh(self):
        n = self.page.pages()
        self.label.setText(f"page {self.page.page + 1} of {n}")
        self.prev.setEnabled(self.page.page > 0)
        self.next.setEnabled(self.page.page < n - 1)
        self.page.update()


# ---------------------------------------------------------------- evidence

class Polaroid(QWidget):
    clicked = pyqtSignal(str)
    SIZE = (118, 142)

    def __init__(self, eid, info):
        super().__init__()
        self.eid = eid
        self.info = info
        self.setFixedSize(*self.SIZE)
        self.tilt = random.Random(eid).uniform(-4, 4)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(info.get("title", ""))

    def mousePressEvent(self, _e):
        self.clicked.emit(self.eid)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self.width() / 2, self.height() / 2)
        p.rotate(self.tilt)
        w, h = self.SIZE[0] - 18, self.SIZE[1] - 18
        frame = QRectF(-w / 2, -h / 2, w, h)
        p.fillRect(frame.translated(2, 3), QColor(0, 0, 0, 90))
        kind = self.info.get("kind", "photo")
        paper = {"photo": "#EEEBE2", "statement": "#F2EED8", "object": "#E4DCC8", "time": "#E8E4D4"}.get(kind, "#EEEBE2")
        p.fillRect(frame, QColor(paper))
        img = QRectF(frame.left() + 7, frame.top() + 7, w - 14, h - 46)
        rng = random.Random(self.eid)
        if kind == "photo":
            g = QLinearGradient(img.topLeft(), img.bottomRight())
            base = rng.choice(["#3B3A33", "#2E3439", "#40352B", "#2B2F2A"])
            g.setColorAt(0, QColor(base).lighter(140))
            g.setColorAt(1, QColor(base).darker(160))
            p.fillRect(img, QBrush(g))
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(5):
                c = QColor(rng.randint(60, 160), rng.randint(50, 140), rng.randint(40, 120), 120)
                p.setBrush(c)
                x = img.left() + rng.random() * img.width()
                y = img.top() + rng.random() * img.height()
                p.drawEllipse(QPointF(x, y), rng.uniform(6, 22), rng.uniform(6, 22))
            p.setBrush(QColor(255, 255, 240, 60))
            p.drawEllipse(QPointF(img.left() + img.width() * 0.7, img.top() + img.height() * 0.3), 10, 10)
        else:
            p.fillRect(img, QColor(paper).darker(108))
            p.setPen(QPen(QColor(60, 60, 80, 100), 1))
            for i in range(6):
                y = img.top() + 10 + i * 11
                p.drawLine(QPointF(img.left() + 6, y), QPointF(img.right() - rng.uniform(6, 30), y))
            p.setFont(QFont("Courier Prime", 8))
            p.setPen(QColor(40, 40, 40))
            p.drawText(img.adjusted(4, 2, -4, -2), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, kind.upper())
        cap = QRectF(frame.left() + 4, img.bottom() + 1, w - 8, 38)
        p.setFont(QFont(HAND, 12))
        p.setPen(QColor("#1D1D24"))
        p.drawText(cap, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.info.get("title", ""))
        # pin
        p.setBrush(QColor("#9C2B1F"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(0, frame.top() + 2), 4, 4)
        p.end()


class Corkboard(QWidget):
    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#6E5136"))
        rng = random.Random(3)
        for _ in range(int(self.width() * self.height() / 90)):
            p.setPen(QColor(90, 65, 40, rng.randint(40, 110)))
            p.drawPoint(rng.randint(0, self.width()), rng.randint(0, self.height()))
        p.end()


class EvidenceTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.board = Corkboard()
        self.grid = None
        self.scroll.setWidget(self.board)
        v.addWidget(self.scroll, 1)
        self.detail = QLabel("Click a photo or a statement to read it.")
        self.detail.setObjectName("small")
        self.detail.setWordWrap(True)
        self.detail.setMinimumHeight(70)
        self.detail.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail.setContentsMargins(8, 6, 8, 6)
        v.addWidget(self.detail)
        self.items = {}
        self.order = []

    def set_evidence(self, evidence, order):
        self.items = dict(evidence)
        self.order = list(order)
        self._rebuild()

    def _rebuild(self):
        for child in self.board.findChildren(Polaroid):
            child.setParent(None)
            child.deleteLater()
        cols = max(1, (self.scroll.viewport().width() - 20) // (Polaroid.SIZE[0] + 6))
        for i, eid in enumerate(self.order):
            pol = Polaroid(eid, self.items[eid])
            pol.setParent(self.board)
            pol.move(8 + (i % cols) * (Polaroid.SIZE[0] + 6), 8 + (i // cols) * (Polaroid.SIZE[1] + 4))
            pol.clicked.connect(self._show)
            pol.show()
        rows = max(1, math.ceil(len(self.order) / cols))
        self.board.setMinimumHeight(16 + rows * (Polaroid.SIZE[1] + 4))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._rebuild()

    def _show(self, eid):
        info = self.items.get(eid, {})
        cap = info.get("caption", "")
        self.detail.setText(f"<b>{info.get('title', '')}</b><br>{cap}<br><i>{info.get('kind', '')}</i>")


# ---------------------------------------------------------------- map

# Places on the Ostrander County map, in 0..1 coordinates
PLACES = {
    "cobb_road": (0.22, 0.30, "22 Cobb Rd"),
    "substation": (0.55, 0.47, "County substation"),
    "hospital": (0.70, 0.38, "Ostrander Co. Hospital"),
    "pruitt": (0.35, 0.62, "Pruitt house"),
    "dorsey": (0.62, 0.70, "Dorsey house"),
    "mill_street": (0.48, 0.58, "9 Mill St"),
    "st_adalberts": (0.52, 0.36, "St. Adalbert's"),
    "spindle": (0.44, 0.50, "The Spindle"),
    "library": (0.60, 0.28, "Public library"),
    "mill": (0.40, 0.75, "Ostrander Paper"),
    "water_tower": (0.33, 0.80, "Water tower"),
    "rest_stop": (0.88, 0.12, "Rest stop, Rt 9"),
}


class MapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.marks = []
        self.setMinimumHeight(380)

    def set_marks(self, marks):
        self.marks = list(marks)
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(6, 6, -6, -6)
        p.fillRect(r, QColor("#E6DFC8"))
        # fold lines
        p.setPen(QPen(QColor(0, 0, 0, 30), 1))
        for i in (1, 2):
            x = r.left() + r.width() * i / 3
            p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
        p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))

        def pt(x, y):
            return QPointF(r.left() + x * r.width(), r.top() + y * r.height())

        # river
        river = QPainterPath(pt(0.0, 0.85))
        river.cubicTo(pt(0.3, 0.72), pt(0.45, 0.9), pt(0.6, 0.78))
        river.cubicTo(pt(0.75, 0.66), pt(0.9, 0.74), pt(1.0, 0.62))
        p.setPen(QPen(QColor("#7FA0B8"), 5))
        p.drawPath(river)
        # roads
        p.setPen(QPen(QColor("#B5523B"), 3))
        p.drawLine(pt(0.05, 0.5), pt(0.95, 0.45))
        p.drawLine(pt(0.5, 0.05), pt(0.5, 0.95))
        p.setPen(QPen(QColor("#C9A54A"), 2))
        p.drawLine(pt(0.2, 0.25), pt(0.5, 0.48))
        p.drawLine(pt(0.5, 0.48), pt(0.9, 0.1))
        p.drawLine(pt(0.3, 0.65), pt(0.65, 0.72))
        # town grid
        p.setPen(QPen(QColor(0, 0, 0, 60), 1))
        for i in range(5):
            p.drawLine(pt(0.42, 0.40 + i * 0.05), pt(0.62, 0.40 + i * 0.05))
            p.drawLine(pt(0.42 + i * 0.05, 0.40), pt(0.42 + i * 0.05, 0.60))
        p.setFont(QFont("Courier Prime", 9, QFont.Weight.Bold))
        p.setPen(QColor("#333"))
        p.drawText(QRectF(r.left() + 6, r.top() + 4, r.width(), 20), "OSTRANDER COUNTY  ·  ROAD MAP")
        p.setFont(QFont("Courier Prime", 8))
        p.drawText(pt(0.44, 0.39), "CALDER FALLS")
        p.drawText(pt(0.05, 0.48), "RT 9")
        # pen marks
        for key in self.marks:
            if key not in PLACES:
                continue
            x, y, label = PLACES[key]
            c = pt(x, y)
            p.setPen(QPen(QColor(20, 30, 90, 200), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(c, 9, 7)
            p.setFont(QFont(HAND, 13))
            p.drawText(QPointF(c.x() + 11, c.y() + 4), label)
        p.end()


# ---------------------------------------------------------------- radio

class Dial(QWidget):
    """An AM dial, 530 to 1700 kHz, with a needle you drag."""
    tuned = pyqtSignal(int)
    LO, HI = 530, 1700

    def __init__(self):
        super().__init__()
        self.freq = 880
        self.glow = 1.0
        self.setMinimumHeight(110)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

    def _x_for(self, f, r):
        return r.left() + (f - self.LO) / (self.HI - self.LO) * r.width()

    def _face(self):
        return QRectF(self.rect()).adjusted(14, 16, -14, -16)

    def set_freq(self, f, emit=True):
        self.freq = int(max(self.LO, min(self.HI, f)))
        self.update()
        if emit:
            self.tuned.emit(self.freq)

    def _set_from_x(self, x):
        r = self._face()
        f = self.LO + (x - r.left()) / r.width() * (self.HI - self.LO)
        self.set_freq(round(f / 10) * 10)

    def mousePressEvent(self, e):
        self._set_from_x(e.position().x())

    def mouseMoveEvent(self, e):
        if e.buttons():
            self._set_from_x(e.position().x())

    def wheelEvent(self, e):
        self.set_freq(self.freq + (10 if e.angleDelta().y() > 0 else -10))

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        outer = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        p.setBrush(QColor("#2A1E14"))
        p.setPen(QPen(QColor("#120C08"), 2))
        p.drawRoundedRect(outer, 8, 8)
        r = self._face()
        g = QLinearGradient(r.topLeft(), r.bottomLeft())
        g.setColorAt(0, QColor(232, 190, 110, int(200 * self.glow)))
        g.setColorAt(1, QColor(180, 120, 50, int(200 * self.glow)))
        p.fillRect(r, QBrush(g))
        p.setPen(QColor(40, 25, 10))
        p.setFont(QFont("Courier Prime", 8))
        for f in (540, 600, 700, 800, 1000, 1200, 1400, 1600):
            x = self._x_for(f, r)
            p.drawLine(QPointF(x, r.bottom() - 14), QPointF(x, r.bottom() - 4))
            p.drawText(QPointF(x - 10, r.bottom() - 18), str(f // 10))
        p.drawText(QPointF(r.left() + 4, r.top() + 12), "AM  kHz x10")
        x = self._x_for(self.freq, r)
        p.setPen(QPen(QColor("#B23A22"), 2))
        p.drawLine(QPointF(x, r.top() + 2), QPointF(x, r.bottom() - 2))
        p.end()


class PoliceKnob(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(70, 70)
        self.active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Police band")

    def mousePressEvent(self, _e):
        self.clicked.emit()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QPointF(35, 35)
        p.setBrush(QColor("#1C1C1C"))
        p.setPen(QPen(QColor("#444"), 2))
        p.drawEllipse(c, 28, 28)
        p.setPen(QPen(QColor("#B8B8B8"), 3))
        ang = math.radians(-60 if not self.active else 40)
        p.drawLine(c, QPointF(c.x() + math.cos(ang) * 22, c.y() + math.sin(ang) * 22))
        p.setBrush(QColor("#B23A22") if self.active else QColor("#3A1A14"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(60, 8), 4, 4)
        p.end()


class RadioTab(QWidget):
    listen = pyqtSignal(object)      # a Choice
    TOL = 20                         # kHz either side that still counts as tuned

    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        self.dial = Dial()
        v.addWidget(self.dial)
        self.freq_label = QLabel("")
        self.freq_label.setObjectName("small")
        v.addWidget(self.freq_label)
        self.am_btn = QPushButton("Listen")
        self.am_btn.setObjectName("flat")
        self.am_btn.clicked.connect(self._listen_am)
        v.addWidget(self.am_btn)
        v.addSpacing(18)
        row = QHBoxLayout()
        self.knob = PoliceKnob()
        self.knob.clicked.connect(self._police)
        col = QVBoxLayout()
        title = QLabel("Police band")
        self.police_label = QLabel("Nothing on the band.")
        self.police_label.setObjectName("small")
        self.police_label.setWordWrap(True)
        col.addWidget(title)
        col.addWidget(self.police_label)
        row.addWidget(self.knob)
        row.addLayout(col, 1)
        v.addLayout(row)
        v.addStretch(1)
        note = QLabel("Drag the needle or use the mouse wheel. Click the knob to key the police band.")
        note.setObjectName("small")
        note.setWordWrap(True)
        v.addWidget(note)
        self.offers = []
        self.drift = False
        self.drift_timer = QTimer(self)
        self.drift_timer.timeout.connect(self._drift_step)
        self.drift_timer.start(120)
        self.dial.tuned.connect(lambda _f: self.refresh())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.refresh()

    def set_offers(self, offers):
        self.offers = list(offers)
        self.refresh()

    def _am_offer(self):
        for c in self.offers:
            if c.kind == "radio" and abs(c.freq - self.dial.freq) <= self.TOL:
                return c
        return None

    def _police_offer(self):
        return next((c for c in self.offers if c.kind == "police"), None)

    def refresh(self):
        f = self.dial.freq
        am = self._am_offer()
        self.freq_label.setText(f"{f} kHz" + ("   something is on this frequency" if am else ""))
        self.am_btn.setEnabled(am is not None)
        self.am_btn.setText(f"Listen: {am.text}" if am else "Listen")
        pol = self._police_offer()
        self.knob.active = pol is not None
        self.police_label.setText(pol.text if pol else "Nothing on the band.")
        self.knob.update()

    def _listen_am(self):
        c = self._am_offer()
        if c:
            self.listen.emit(c)

    def _police(self):
        c = self._police_offer()
        if c:
            self.listen.emit(c)

    def _drift_step(self):
        if not self.drift or self.isVisible():
            return
        target = 1610
        f = self.dial.freq
        if f != target:
            self.dial.set_freq(f + (10 if target > f else -10))
