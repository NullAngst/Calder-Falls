"""The story text: typed out at a readable pace, and allowed to lie.

Everything the window does to the text happens here: typewriter reveal and
its stutter, words that swap for a moment, color split on the letter edges,
letters drifting off their line, earlier paragraphs that change while you
are not looking, and the flashlight cone in dark scenes.

Layout is deterministic. The same text at the same width lays out the same,
down to the line breaks, which is what the Act I loops rely on.
"""

import math
import random
import time

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QFontMetricsF, QPainter, QRadialGradient,
    QTextLayout, QTextOption,
)
from PyQt6.QtWidgets import QScrollArea, QSizePolicy, QWidget

UNEASY = {
    "door": "mouth", "house": "throat", "hallway": "hallway", "light": "eye",
    "radio": "choir", "June": "you", "children": "count", "wall": "skin",
    "window": "mouth", "quiet": "counted", "home": "here", "father": "vessel",
    "kitchen": "listening room", "phone": "open line", "you": "we",
}

MAX_TEXT_WIDTH = 760
MARGIN_X = 40
MARGIN_Y = 28
PARA_GAP = 0.85   # in line heights


class Para:
    __slots__ = ("text", "kind", "shown", "layout", "lay_key", "top", "height", "pause")

    def __init__(self, text, kind="story", pause=0.0):
        self.text = text
        self.kind = kind          # story, echo, radio, system, pause
        self.shown = 0            # characters revealed
        self.layout = None
        self.lay_key = None
        self.top = 0.0
        self.height = 0.0
        self.pause = pause


class StoryView(QWidget):
    revealed = pyqtSignal()      # everything queued has been typed out

    def __init__(self, scroll):
        super().__init__()
        self.scroll = scroll
        self.paras = []
        self.stage = None
        self.font_ = QFont("Courier Prime", 15)
        self.speed = 60.0            # characters per second, 0 = instant
        self.flashlight_cone = True
        self.dark = False
        self.battery_low = False
        self.shadow = ""
        self.mouse = QPointF(-1000, -1000)
        self.rng = random.Random(7)
        self.temp_swap = None        # (para index, start, end, replacement, until)
        self.pending_scrollback = []  # (find, replace)
        self.drift_seed = 0
        self.last_tick = time.monotonic()
        self.carry = 0.0
        self.pause_until = 0.0
        self.follow = True
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)
        self.fx_timer = QTimer(self)
        self.fx_timer.timeout.connect(self._fx)
        self.fx_timer.start(90)
        scroll.verticalScrollBar().valueChanged.connect(self._scrolled)

    # ------------------------------------------------------------ content
    def clear(self):
        self.paras = []
        self.temp_swap = None
        self._relayout()

    def add(self, text, kind="story"):
        self.paras.append(Para(text, kind))
        self._relayout()

    def add_pause(self, seconds):
        self.paras.append(Para("", "pause", pause=seconds))

    def load_transcript(self, lines):
        self.paras = []
        for line in lines:
            if line.startswith("> "):
                p = Para(line[2:], "echo")
            else:
                p = Para(line)
            p.shown = len(p.text)
            self.paras.append(p)
        self._relayout()
        self._to_bottom()

    def skip(self):
        for p in self.paras:
            p.shown = len(p.text)
            p.pause = 0.0
        self.pause_until = 0.0
        self.update()
        self.revealed.emit()

    def is_revealing(self):
        return any(p.shown < len(p.text) or p.pause > 0 for p in self.paras)

    def scrollback(self, find, replace):
        self.pending_scrollback.append((find, replace))
        self._scrolled()

    # ------------------------------------------------------------ settings
    def set_font(self, family, size):
        self.font_ = QFont(family, size)
        self.font_.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        for p in self.paras:
            p.lay_key = None
        self._relayout()

    def set_stage(self, stage):
        self.stage = stage
        self.update()

    def set_dark(self, on):
        self.dark = on
        self.update()

    # ------------------------------------------------------------ layout
    def _text_rect_width(self):
        return min(MAX_TEXT_WIDTH, max(200, self.width() - 2 * MARGIN_X))

    def _left(self):
        return max(MARGIN_X, (self.width() - self._text_rect_width()) / 2)

    def _font_for(self, kind):
        f = QFont(self.font_)
        if kind in ("echo", "radio"):
            f.setItalic(True)
        if kind == "system":
            f.setPointSizeF(max(8.0, f.pointSizeF() - 3))
        return f

    def _layout_para(self, p, text, width):
        key = (text, width, p.kind, self.font_.family(), self.font_.pointSizeF())
        if p.lay_key == key and p.layout is not None:
            return p.layout
        lay = QTextLayout(text, self._font_for(p.kind))
        opt = QTextOption()
        opt.setWrapMode(QTextOption.WrapMode.WordWrap)
        lay.setTextOption(opt)
        fm = QFontMetricsF(self._font_for(p.kind))
        lh = fm.height() * 1.42
        y = 0.0
        lay.beginLayout()
        while True:
            line = lay.createLine()
            if not line.isValid():
                break
            line.setLineWidth(width)
            line.setPosition(QPointF(0, y))
            y += lh
        lay.endLayout()
        p.layout = lay
        p.lay_key = key
        p.height = y
        return lay

    def _relayout(self):
        width = self._text_rect_width()
        fm = QFontMetricsF(self.font_)
        gap = fm.height() * 1.42 * PARA_GAP
        y = MARGIN_Y
        for p in self.paras:
            if p.kind == "pause":
                p.top = y
                p.height = 0
                continue
            self._layout_para(p, p.text, width)
            p.top = y
            y += p.height + gap
        self.setMinimumHeight(int(y + MARGIN_Y * 2))
        self.update()

    def resizeEvent(self, _e):
        for p in self.paras:
            p.lay_key = None
        self._relayout()

    # ------------------------------------------------------------ reveal
    def _tick(self):
        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now
        if now < self.pause_until:
            return
        target = next((p for p in self.paras if p.shown < len(p.text) or p.pause > 0), None)
        if target is None:
            return
        if target.kind == "pause":
            self.pause_until = now + target.pause
            target.pause = 0.0
            return
        if self.speed <= 0:
            target.shown = len(target.text)
        else:
            self.carry += dt * self.speed
            n = int(self.carry)
            if n <= 0:
                return
            self.carry -= n
            if self.stage and self.stage.stutter and self.rng.random() < self.stage.stutter:
                self.pause_until = now + self.rng.uniform(0.08, 0.35)
                n = 1
            target.shown = min(len(target.text), target.shown + n)
            # a little breath at the end of a sentence
            if target.shown < len(target.text) and target.text[target.shown - 1] in ".?!":
                self.pause_until = now + 0.12
        self.update()
        if self.follow:
            self._to_bottom()
        if not self.is_revealing():
            self.revealed.emit()

    def _to_bottom(self):
        sb = self.scroll.verticalScrollBar()
        QTimer.singleShot(0, lambda: sb.setValue(sb.maximum()))

    def _scrolled(self, *_):
        sb = self.scroll.verticalScrollBar()
        self.follow = sb.value() >= sb.maximum() - 4
        if not self.pending_scrollback:
            return
        top = sb.value()
        bottom = top + self.scroll.viewport().height()
        keep = []
        for find, rep in self.pending_scrollback:
            done = False
            for p in reversed(self.paras):
                if find in p.text:
                    if p.top + p.height < top or p.top > bottom:
                        p.text = p.text.replace(find, rep)
                        p.shown = len(p.text)
                        p.lay_key = None
                        done = True
                    break
            else:
                done = True   # nothing to change any more
            if not done:
                keep.append((find, rep))
        self.pending_scrollback = keep
        self._relayout()

    # ------------------------------------------------------------ effects
    def _fx(self):
        s = self.stage
        changed = False
        now = time.monotonic()
        if self.temp_swap and now > self.temp_swap[4]:
            self.temp_swap = None
            changed = True
        if s and s.swap > 0 and self.temp_swap is None and self.paras and self.rng.random() < s.swap * 0.09:
            visible = [i for i, p in enumerate(self.paras) if p.kind == "story" and p.shown == len(p.text)]
            if visible:
                i = self.rng.choice(visible[-6:])
                text = self.paras[i].text
                hits = [(w, text.find(w)) for w in UNEASY if text.find(w) >= 0]
                if hits:
                    w, at = self.rng.choice(hits)
                    self.temp_swap = (i, at, at + len(w), UNEASY[w], now + 0.22)
                    changed = True
        if s and s.drift > 0:
            self.drift_seed = int(now * 1.3)
            changed = True
        if self.dark or (s and s.split):
            changed = True
        if changed:
            self.update()

    def mouseMoveEvent(self, e):
        self.mouse = e.position()
        if self.dark:
            self.update()

    def leaveEvent(self, _e):
        self.mouse = QPointF(-1000, -1000)
        if self.dark:
            self.update()

    def mousePressEvent(self, _e):
        if self.is_revealing():
            self.skip()

    # ------------------------------------------------------------ painting
    def _colors(self):
        s = self.stage
        if s is None:
            return QColor("#C8CDD8"), QColor("#4A6FA5"), QColor("#0B0F1A")
        return QColor(s.text), QColor(s.accent), QColor(s.bg)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        text_c, accent_c, bg_c = self._colors()
        p.fillRect(self.rect(), bg_c)
        left = self._left()
        width = self._text_rect_width()
        clip = QRectF(e.rect())
        split = self.stage.split if self.stage else 0.0
        drift = self.stage.drift if self.stage else 0.0
        for idx, para in enumerate(self.paras):
            if para.kind == "pause" or para.shown <= 0:
                continue
            if para.top > clip.bottom() or para.top + para.height < clip.top():
                continue
            text = para.text
            if self.temp_swap and self.temp_swap[0] == idx:
                _i, a, b, rep, _u = self.temp_swap
                text = text[:a] + rep + text[b:]
            lay = self._layout_para(para, text, width) if text != para.text else para.layout
            shown = para.shown if text == para.text else len(text)
            color = QColor(text_c)
            if para.kind == "echo":
                color = QColor(text_c)
                color.setAlphaF(0.55)
            elif para.kind == "radio":
                color = QColor(accent_c).lighter(150)
            elif para.kind == "system":
                color.setAlphaF(0.45)
            origin = QPointF(left, para.top)
            self._draw_layout(p, lay, origin, shown, color, split, accent_c)
            if drift and idx >= len(self.paras) - 3:
                self._draw_drift(p, lay, origin, text, shown, color, bg_c, drift, idx)
        if self.dark:
            self._draw_flashlight(p, bg_c, text_c)
        p.end()

    def _draw_layout(self, p, lay, origin, shown, color, split, accent):
        for li in range(lay.lineCount()):
            line = lay.lineAt(li)
            start = line.textStart()
            if start >= shown:
                break
            end = start + line.textLength()
            pos = QPointF(origin.x() + line.position().x(), origin.y() + line.position().y())
            if end > shown:
                # partially revealed line: clip to the revealed width
                x = line.cursorToX(shown)[0]
                p.save()
                p.setClipRect(QRectF(pos.x(), pos.y(), x, line.height() + 2), Qt.ClipOperation.IntersectClip)
            if split:
                red = QColor(accent).lighter(170)
                red.setAlphaF(0.35)
                cyan = QColor(90, 200, 210, 70)
                p.setPen(red)
                line.draw(p, QPointF(origin.x() - split, origin.y()))
                p.setPen(cyan)
                line.draw(p, QPointF(origin.x() + split, origin.y()))
            p.setPen(color)
            line.draw(p, origin)
            if end > shown:
                p.restore()

    def _draw_drift(self, p, lay, origin, text, shown, color, bg, drift, idx):
        rng = random.Random(self.drift_seed * 131 + idx)
        count = int(len(text) * 0.02 * drift) + 1
        fm = QFontMetricsF(self._font_for("story"))
        for _ in range(count):
            i = rng.randrange(0, max(1, shown))
            ch = text[i] if i < len(text) else " "
            if ch.isspace():
                continue
            line = lay.lineForTextPosition(i)
            if not line.isValid():
                continue
            x = origin.x() + line.cursorToX(i)[0]
            y = origin.y() + line.position().y()
            wch = fm.horizontalAdvance(ch)
            p.fillRect(QRectF(x, y + 2, wch, line.height() - 2), bg)
            dy = rng.choice((-1, 1)) * rng.uniform(3, 9) * drift * 2
            p.setPen(color)
            p.setFont(self._font_for("story"))
            p.drawText(QPointF(x, y + fm.ascent() + dy), ch)

    def _draw_flashlight(self, p, bg, text_c):
        r = self.rect()
        if not self.flashlight_cone:
            dim = QColor(bg)
            dim.setAlphaF(0.55)
            p.fillRect(r, dim)
            return
        radius = 150.0
        if self.battery_low:
            radius *= 0.75 + 0.25 * self.rng.random()
            if self.rng.random() < 0.04:
                radius = 0
        g = QRadialGradient(self.mouse, max(radius, 1.0))
        hole = QColor(bg)
        hole.setAlpha(0)
        solid = QColor(0, 0, 0, 255)
        g.setColorAt(0.0, hole)
        g.setColorAt(0.55, QColor(0, 0, 0, 40))
        g.setColorAt(1.0, solid)
        p.fillRect(r, QBrush(g))
        if self.shadow and radius > 0 and self.mouse.x() > -500:
            ang = (time.monotonic() * 0.3) % 6.283
            sx = self.mouse.x() + math.cos(ang) * radius * 1.05
            sy = self.mouse.y() + math.sin(ang) * radius * 1.05
            c = QColor(text_c)
            c.setAlphaF(0.22)
            p.setPen(c)
            p.setFont(self._font_for("story"))
            p.drawText(QPointF(sx, sy), self.shadow)


def make_story_pane(parent=None):
    scroll = QScrollArea(parent)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view = StoryView(scroll)
    scroll.setWidget(view)
    return scroll, view
