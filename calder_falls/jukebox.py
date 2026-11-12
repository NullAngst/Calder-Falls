"""Calder Falls jukebox: every music cue, played live through the real engine.

This is the step 1 listening tool. The controls are the ones the story will
drive with Ink tags, so what you hear here is what the game can do to a cue.

    python3 -m calder_falls.jukebox
    python3 -m calder_falls.jukebox --selftest     # headless check, exits
"""

import argparse
import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QProgressBar, QPushButton,
    QSlider, QVBoxLayout, QWidget,
)

from . import __version__, paths
from .audio import cues as cue_table
from .audio.engine import AudioEngine

MIDNIGHT = """
QWidget { background: #0B0F1A; color: #C8CDD8; font-size: 13px; }
QGroupBox { border: 1px solid #1E2638; border-radius: 4px; margin-top: 14px; padding: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #8A93A8; }
QListWidget { background: #080B13; border: 1px solid #1E2638; outline: none; }
QListWidget::item { padding: 6px 8px; border-bottom: 1px solid #121826; }
QListWidget::item:selected { background: #18233A; color: #E4E8F0; }
QPushButton { background: #141B2B; border: 1px solid #2A3550; padding: 6px 16px; border-radius: 3px; }
QPushButton:hover { border-color: #4A6FA5; }
QPushButton:pressed { background: #1C2740; }
QPushButton:disabled { color: #4A5163; border-color: #1E2638; }
QSlider::groove:horizontal { height: 4px; background: #1E2638; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #4A6FA5; border-radius: 2px; }
QSlider::handle:horizontal { background: #C8CDD8; width: 12px; margin: -5px 0; border-radius: 6px; }
QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #2A3550; background: #080B13; }
QCheckBox::indicator:checked { background: #4A6FA5; }
QCheckBox:disabled { color: #4A5163; }
QProgressBar { border: 1px solid #1E2638; background: #080B13; height: 8px; text-align: center; }
QProgressBar::chunk { background: #4A6FA5; }
QLabel#dim { color: #8A93A8; }
QLabel#title { font-size: 18px; color: #E4E8F0; }
"""


def pick_font():
    families = set(QFontDatabase.families())
    for name in ("Courier Prime", "Courier New", "Liberation Mono", "DejaVu Sans Mono"):
        if name in families:
            return QFont(name, 11)
    f = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    f.setPointSize(11)
    return f


def icon_path():
    for p in (os.path.join(paths.data_dir(), "assets", "icon", "calder-falls-256.png"),
              os.path.join(paths.data_dir(), "assets", "icon", "calder-falls.svg")):
        if os.path.isfile(p):
            return p
    return None


def tempo_text(cue):
    return "free time" if cue.tempo == "none" else cue.tempo


class Knob(QWidget):
    """A labelled slider with its current value beside it."""

    def __init__(self, label, lo, hi, value, fmt, on_change):
        super().__init__()
        self.fmt = fmt
        self.default = value
        self.on_change = on_change
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        name = QLabel(label)
        name.setMinimumWidth(110)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(lo, hi)
        self.slider.setValue(value)
        self.value = QLabel(fmt(value))
        self.value.setMinimumWidth(80)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(name)
        row.addWidget(self.slider, 1)
        row.addWidget(self.value)
        self.slider.valueChanged.connect(self._changed)

    def _changed(self, v):
        self.value.setText(self.fmt(v))
        self.on_change(v)

    def reset(self):
        self.slider.setValue(self.default)


class Jukebox(QMainWindow):
    def __init__(self, output=True):
        super().__init__()
        self.setWindowTitle(f"Calder Falls Jukebox {__version__}")
        ip = icon_path()
        if ip:
            self.setWindowIcon(QIcon(ip))
        self.engine = AudioEngine(output=output)
        self.current = None

        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)

        # cue list
        left = QVBoxLayout()
        self.list = QListWidget()
        for cue in cue_table.CUES:
            item = QListWidgetItem(f"{cue.title}\n{tempo_text(cue)}  ·  {cue.where}")
            item.setData(Qt.ItemDataRole.UserRole, cue.name)
            self.list.addItem(item)
        self.list.setMinimumWidth(360)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.list.currentItemChanged.connect(self._select)
        self.list.itemDoubleClicked.connect(lambda _i: self.play())
        left.addWidget(self.list, 1)
        outer.addLayout(left)

        # right side
        right = QVBoxLayout()
        self.title = QLabel("")
        self.title.setObjectName("title")
        self.feel = QLabel("")
        self.feel.setObjectName("dim")
        self.feel.setWordWrap(True)
        right.addWidget(self.title)
        right.addWidget(self.feel)

        transport = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.play_btn.clicked.connect(self.play)
        self.stop_btn.clicked.connect(self.stop)
        self.pos = QProgressBar()
        self.pos.setRange(0, 1000)
        self.pos.setTextVisible(False)
        self.time = QLabel("0:00 / 0:00")
        self.time.setMinimumWidth(110)
        transport.addWidget(self.play_btn)
        transport.addWidget(self.stop_btn)
        transport.addWidget(self.pos, 1)
        transport.addWidget(self.time)
        right.addLayout(transport)

        knobs = QGroupBox("Controls the story can use")
        kl = QVBoxLayout(knobs)
        self.tempo = Knob("Tempo", 50, 150, 100, lambda v: f"{v}%  ",
                          lambda v: self.engine.set_tempo(v / 100.0))
        self.detune = Knob("Detune", -100, 100, 0, lambda v: f"{v:+d} cents",
                           lambda v: self.engine.set_detune(v))
        self.static = Knob("Static bleed", 0, 100, 0, lambda v: f"{v}%  ",
                           lambda v: self.engine.set_static(v / 100.0))
        self.volume = Knob("Volume", 0, 100, 90, lambda v: f"{v}%  ",
                           lambda v: self.engine.set_volume(v / 100.0))
        for k in (self.tempo, self.detune, self.static, self.volume):
            kl.addWidget(k)
        row = QHBoxLayout()
        self.ps2 = QCheckBox("PS2 filter")
        self.ps2.setChecked(True)
        self.ps2.toggled.connect(self.engine.set_ps2)
        reset = QPushButton("Reset controls")
        reset.clicked.connect(self.reset_controls)
        row.addWidget(self.ps2)
        row.addStretch(1)
        row.addWidget(reset)
        kl.addLayout(row)
        right.addWidget(knobs)

        layers = QGroupBox("Layers")
        ll = QGridLayout(layers)
        self.layer_boxes = {}
        for i, name in enumerate(cue_table.LAYER_ORDER):
            box = QCheckBox(name)
            box.setChecked(True)
            box.toggled.connect(lambda on, n=name: self.engine.set_layer(n, on))
            ll.addWidget(box, 0, i)
            self.layer_boxes[name] = box
        right.addWidget(layers)

        tip = QLabel("If a cue sounds wrong, say which cue and what is wrong in plain words "
                     "(\"too busy\", \"too happy\", \"the drums are too loud\"). "
                     "Greyed-out layers are not used by that cue.")
        tip.setObjectName("dim")
        tip.setWordWrap(True)
        right.addWidget(tip)
        right.addStretch(1)

        self.status = QLabel("")
        self.status.setObjectName("dim")
        self.status.setWordWrap(True)
        right.addWidget(self.status)
        outer.addLayout(right, 1)

        bank = os.path.basename(self.engine.base_bank)
        msg = f"Base bank: {bank}   Calder bank: {os.path.basename(self.engine.calder_bank)}"
        if self.engine.output_error:
            msg += f"\nNo audio output: {self.engine.output_error}"
            self.play_btn.setEnabled(False)
        self.status.setText(msg)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(100)
        self.list.setCurrentRow(0)
        self.resize(1040, 620)

    def _select(self, item, _prev=None):
        if item is None:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        cue = cue_table.get(name)
        data = self.engine.load(name)
        self.current = name
        self.title.setText(cue.title)
        loop = "loops" if cue.loop else "plays once"
        self.feel.setText(f"{cue.where}. {cue.feel}. {tempo_text(cue).capitalize()}, {loop}, "
                          f"{int(data.length // 60)}:{int(data.length % 60):02d}.")
        for layer, box in self.layer_boxes.items():
            box.setEnabled(layer in data.layers)

    def play(self):
        if self.current:
            self.engine.play(self.current)

    def stop(self):
        self.engine.stop()

    def reset_controls(self):
        for k in (self.tempo, self.detune, self.static, self.volume):
            k.reset()
        self.ps2.setChecked(True)
        for box in self.layer_boxes.values():
            box.setChecked(True)

    def _tick(self):
        e = self.engine
        if e.data is not None and e.playing:
            frac = e.position / e.data.length
            self.pos.setValue(int(frac * 1000))
            p, length = e.position, e.data.length
            self.time.setText(f"{int(p // 60)}:{int(p % 60):02d} / {int(length // 60)}:{int(length % 60):02d}")
        elif not e.playing:
            self.pos.setValue(0)
        if e.error:
            self.status.setText(f"Audio error: {e.error}")

    def closeEvent(self, event):
        self.timer.stop()
        self.engine.close()
        super().closeEvent(event)


def selftest(app, win):
    """Walk every cue and every control, render through the engine, quit."""
    import numpy as np
    failures = []
    eng = win.engine
    from ._libs import check_portaudio
    ok, msg = check_portaudio()
    print(f"jukebox: {msg}", flush=True)
    if not ok:  # the AppImage must be able to load PortAudio
        failures.append("portaudio")
    for row in range(win.list.count()):
        win.list.setCurrentRow(row)
        app.processEvents()
        win.play()
        for k in (win.tempo, win.detune, win.static, win.volume):
            k.slider.setValue(k.slider.minimum())
            k.slider.setValue(k.slider.maximum())
            k.reset()
        win.ps2.setChecked(False)
        win.ps2.setChecked(True)
        for box in win.layer_boxes.values():
            if box.isEnabled():
                box.setChecked(False)
                box.setChecked(True)
        app.processEvents()
        if eng.stream is None:
            block = eng.render(1.0)
            if not np.isfinite(block).all():
                failures.append(win.current)
        print(f"jukebox: {win.current} ok", flush=True)
    win.close()
    if failures:
        print(f"jukebox selftest failed for: {failures}", flush=True)
        return 1
    print("jukebox selftest passed", flush=True)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Calder Falls music jukebox")
    ap.add_argument("--selftest", action="store_true", help="headless check, then exit")
    args, qt_args = ap.parse_known_args(argv)
    app = QApplication([sys.argv[0]] + qt_args)
    app.setApplicationName("Calder Falls Jukebox")
    app.setDesktopFileName("calder-falls-jukebox")
    app.setStyleSheet(MIDNIGHT)
    app.setFont(pick_font())
    try:
        win = Jukebox(output=not args.selftest)
    except RuntimeError as exc:
        print(f"calder-falls-jukebox: {exc}", file=sys.stderr)
        return 1
    if args.selftest:
        return selftest(app, win)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
