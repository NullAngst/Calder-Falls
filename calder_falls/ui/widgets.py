"""Small pieces of the main window: Brennick's LCD wristwatch, the Nerve
meter, and the choice buttons (which can turn and flinch)."""

import random
import time

from PyQt6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QGridLayout, QProgressBar, QPushButton, QVBoxLayout, QWidget

# seven-segment layout: a b c d e f g
SEGMENTS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
    "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": "",
}


class LCDWatch(QWidget):
    """A cheap 1980s digital watch face."""

    def __init__(self):
        super().__init__()
        self.text = "--:--"
        self.blink = True
        self.setFixedSize(118, 38)
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(1000)

    def set_time(self, text):
        self.text = text if len(text) == 5 else "--:--"
        self.update()

    def _tick(self):
        self.blink = not self.blink
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setBrush(QColor("#1A1A1A"))
        p.setPen(QPen(QColor("#3A3A3A"), 2))
        p.drawRoundedRect(r, 6, 6)
        face = r.adjusted(6, 5, -6, -5)
        p.fillRect(face, QColor("#7C8A6A"))
        on = QColor("#1E2418")
        off = QColor(30, 36, 24, 28)
        dw, dh = 16, 22
        x = face.left() + 8
        y = face.top() + 3
        for ch in self.text:
            if ch == ":":
                if self.blink:
                    p.setBrush(on)
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawRect(QRectF(x + 1, y + 6, 3, 3))
                    p.drawRect(QRectF(x + 1, y + 14, 3, 3))
                x += 8
                continue
            segs = SEGMENTS.get(ch, "")
            for s in "abcdefg":
                p.setPen(QPen(on if s in segs else off, 3, cap=Qt.PenCapStyle.FlatCap))
                pts = {
                    "a": ((2, 0), (dw - 2, 0)), "b": ((dw, 2), (dw, dh / 2 - 1)),
                    "c": ((dw, dh / 2 + 1), (dw, dh - 2)), "d": ((2, dh), (dw - 2, dh)),
                    "e": ((0, dh / 2 + 1), (0, dh - 2)), "f": ((0, 2), (0, dh / 2 - 1)),
                    "g": ((2, dh / 2), (dw - 2, dh / 2)),
                }[s]
                p.drawLine(QPointF(x + pts[0][0] * 0.8, y + pts[0][1]), QPointF(x + pts[1][0] * 0.8, y + pts[1][1]))
            x += dw * 0.8 + 6
        p.end()


class NerveMeter(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 10
        self.accent = QColor("#4A6FA5")
        self.setFixedSize(140, 30)
        self.setToolTip("Nerve. It drops in bad moments and comes back when you rest or smoke.")

    def set_value(self, v, accent=None):
        self.value = max(0, min(10, int(v)))
        if accent:
            self.accent = QColor(accent)
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor(200, 200, 200, 150))
        p.drawText(QRectF(0, 0, 48, 30), Qt.AlignmentFlag.AlignVCenter, "NERVE")
        for i in range(10):
            r = QRectF(50 + i * 9, 8, 6, 14)
            c = QColor(self.accent) if i < self.value else QColor(255, 255, 255, 25)
            if self.value <= 3 and i < self.value:
                c = QColor("#A33A2A")
            p.fillRect(r, c)
        p.end()


class ChoiceButton(QPushButton):
    """Says one thing. On hover it may say what it really does, and that is
    what a click picks. At low Nerve it slides a little away from the mouse."""

    def __init__(self, choice, honest, flinch):
        shown = choice.truth if honest else choice.text
        super().__init__(shown)
        self.choice = choice
        self.honest = honest
        self.flinch = flinch and not honest
        self.setObjectName("choice")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.anim = None
        self.rng = random.Random(choice.index + int(time.time()))

    def enterEvent(self, e):
        if self.choice.hover and not self.honest:
            self.setText(self.choice.hover)
        if self.flinch:
            dx = self.rng.choice((-1, 1)) * self.rng.randint(4, 9)
            self.anim = QPropertyAnimation(self, b"pos", self)
            self.anim.setDuration(120)
            self.anim.setStartValue(self.pos())
            self.anim.setEndValue(self.pos() + QPointF(dx, 0).toPoint())
            self.anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self.choice.hover and not self.honest:
            self.setText(self.choice.text)
        super().leaveEvent(e)


class ChoicePanel(QWidget):
    chosen = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(40, 6, 40, 14)
        self.lay.setSpacing(6)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        self.bar.hide()
        self.buttons = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._count)
        self.deadline = 0.0
        self.duration = 0.0
        self.default = None

    def clear(self):
        self.timer.stop()
        self.bar.hide()
        for b in self.buttons:
            b.setParent(None)
            b.deleteLater()
        self.buttons = []
        while self.lay.count():
            item = self.lay.takeAt(0)
            w = item.widget()
            if w is not None and w is not self.bar:
                w.setParent(None)

    def show_choices(self, choices, honest=False, flinch=False):
        self.clear()
        self.lay.addWidget(self.bar)
        # many choices go in two columns so the story keeps its room
        cols = 2 if len(choices) > 5 else 1
        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(5)
        for i, c in enumerate(choices):
            b = ChoiceButton(c, honest, flinch)
            b.clicked.connect(lambda _=False, ch=c: self._pick(ch))
            grid.addWidget(b, i // cols if cols == 2 else i, i % cols)
            self.buttons.append(b)
        self.lay.addWidget(holder)

    def start_timer(self, seconds, default_index):
        if not self.buttons:
            return
        self.duration = max(0.5, seconds)
        self.deadline = time.monotonic() + self.duration
        idx = max(0, min(len(self.buttons) - 1, default_index))
        self.default = self.buttons[idx].choice
        self.bar.setValue(1000)
        self.bar.show()
        self.timer.start(50)

    def _count(self):
        left = self.deadline - time.monotonic()
        if left <= 0:
            self.timer.stop()
            self._pick(self.default)
            return
        self.bar.setValue(int(1000 * left / self.duration))

    def _pick(self, choice):
        self.timer.stop()
        self.chosen.emit(choice)
