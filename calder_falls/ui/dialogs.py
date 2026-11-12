"""Dialogs: first launch, settings, theory filing, saves, How to Play,
and the fake crash."""

import threading

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QSlider, QSpinBox, QTextBrowser, QVBoxLayout, QWidget,
)

from .. import banks

HOWTO = """
<h3>How to play</h3>
<p>You are Detective Sergeant Cal Brennick, state police, Major Crimes. Read, then pick
what he does with the buttons under the text. Click the text to skip ahead while it types.</p>
<p><b>The notebook.</b> What you find goes into the tabs on the right: notes in the pad,
photos and statements on the corkboard. When the case gives you the chance, you file a
theory: who, what, when, why, chosen from what you have found. A right theory moves you
on. A wrong one puts you back where you started, and the house will be worse for it.
Nothing you find is wasted, even on a reset.</p>
<p><b>Nerve</b> is the bar in the top right. It drops when things go badly and comes back
when you rest or smoke. Low Nerve makes it harder to see straight.</p>
<p><b>The radio</b> tab has an AM dial and a police knob. Sometimes there is something on a
frequency or on the band. Tune to it and listen, or key the knob. Some voices on there
tell the truth. Not all of them are on your side.</p>
<p><b>Hint</b> in the top bar always works and never lies.</p>
<p>The game saves at the start of every loop and every chapter. Save to a slot from the
menu whenever you like.</p>
"""

HOWTO_REWRITTEN = """
<h3>How to listen</h3>
<p>You are the vessel. You have been the vessel since 1957, when he could not make room
and your mother took you south in the back seat. Read, then pick what he does. Click the
text. It does not matter how fast you read. We are patient.</p>
<p><b>The ledger.</b> What you find goes on the right. You thought you were building a
case. You were filling in a page. Every man we brought in is written there, and how he
turned out. There is a line left at the bottom.</p>
<p><b>Nerve</b> is how much of you is left to hold us. Do not worry about it. We will
hold on to the rest.</p>
<p><b>The radio</b> is how we talk. It always was. One six one zero. Say it with us, and
then say how many live in your house.</p>
<p><b>Hint</b> still never lies. That is the only thing on this page that is yours.</p>
"""

CRASH_TEXT = """calder-falls has stopped responding.

Traceback (most recent call last):
  File "calder_falls/app.py", line 1610, in <module>
    house.make_room(occupants=household.count())
  File "calder_falls/ledger.py", line 57, in make_room
    raise VesselError("unsuitable")
VesselError: unsuitable

A report has been written to ~/.local/share/calder-falls/ledger.txt
"""


class FirstLaunchDialog(QDialog):
    """Asked before anything flashes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Before you start")
        self.setModal(True)
        v = QVBoxLayout(self)
        msg = QLabel("Calder Falls uses flickering light, flashing, and scanline effects. "
                     "If flashing images bother you or could trigger a seizure, turn them off. "
                     "You can change this any time in Settings.")
        msg.setWordWrap(True)
        v.addWidget(msg)
        self.group = QButtonGroup(self)
        for key, label in (("off", "No flicker: a still picture, nothing flashes or moves on its own"),
                           ("gentle", "Gentle (default): softened flicker"),
                           ("full", "Full: everything the game does")):
            rb = QRadioButton(label)
            rb.setProperty("key", key)
            self.group.addButton(rb)
            v.addWidget(rb)
            if key == "gentle":
                rb.setChecked(True)
        ok = QPushButton("Continue")
        ok.setObjectName("flat")
        ok.clicked.connect(self.accept)
        v.addWidget(ok)
        self.resize(520, 240)

    def choice(self):
        b = self.group.checkedButton()
        return b.property("key") if b else "gentle"


class SettingsDialog(QDialog):
    bank_message = pyqtSignal(str)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.s = settings
        v = QVBoxLayout(self)
        form = QFormLayout()
        self.flicker = QComboBox()
        for k, label in (("off", "No flicker"), ("gentle", "Gentle"), ("full", "Full")):
            self.flicker.addItem(label, k)
        self.flicker.setCurrentIndex(["off", "gentle", "full"].index(settings.flicker))
        self.flicker.setToolTip("No flicker: no flashes, no scanlines, grain and fog frozen, "
                                "the flashlight steady, the title screen light always on.")
        form.addRow("Flicker and flashes", self.flicker)
        self.honest = QCheckBox("Honest controls (a click always does what the button says)")
        self.honest.setChecked(settings.honest_controls)
        form.addRow("", self.honest)
        self.cone = QCheckBox("Flashlight cone in dark scenes (off dims the text evenly)")
        self.cone.setChecked(settings.flashlight_cone)
        form.addRow("", self.cone)
        self.timed = QCheckBox("Timed choices")
        self.timed.setChecked(settings.timed_choices)
        form.addRow("", self.timed)
        self.fourth = QCheckBox("Fourth-wall effects (fake crash, fake corrupted save, changing title screen)")
        self.fourth.setChecked(settings.fourth_wall)
        form.addRow("", self.fourth)
        self.size = QSpinBox()
        self.size.setRange(11, 26)
        self.size.setValue(settings.text_size)
        form.addRow("Text size", self.size)
        self.font = QComboBox()
        self.font.addItems(["Courier Prime", "Source Serif 4"])
        self.font.setCurrentText(settings.font)
        form.addRow("Story font", self.font)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(0, 200)
        self.speed.setValue(settings.reveal_speed)
        self.speed_label = QLabel("")
        self.speed.valueChanged.connect(self._speed_text)
        self._speed_text(settings.reveal_speed)
        row = QHBoxLayout()
        row.addWidget(self.speed, 1)
        row.addWidget(self.speed_label)
        w = QWidget()
        w.setLayout(row)
        form.addRow("Reveal speed", w)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(settings.music_volume)
        form.addRow("Music volume", self.volume)
        v.addLayout(form)

        bank_row = QHBoxLayout()
        cur = banks.current_choice()
        self.bank_label = QLabel("Sound bank: " + ("GeneralUser GS" if cur else "FluidR3 Mono (bundled)"))
        self.bank_label.setObjectName("small")
        self.dl = QPushButton("Download GeneralUser GS")
        self.dl.setObjectName("flat")
        self.dl.setToolTip("Sounds better. Downloaded from its author's GitHub, not bundled, "
                           "since the origin of some samples is not fully documented.")
        self.dl.clicked.connect(self._download)
        self.revert = QPushButton("Use bundled")
        self.revert.setObjectName("flat")
        self.revert.clicked.connect(self._revert)
        bank_row.addWidget(self.bank_label, 1)
        bank_row.addWidget(self.dl)
        bank_row.addWidget(self.revert)
        v.addLayout(bank_row)
        self.bank_message.connect(self.bank_label.setText)

        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Cancel")
        ok = QPushButton("Save")
        for b in (cancel, ok):
            b.setObjectName("flat")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        v.addLayout(btns)
        self.resize(640, 460)

    def _speed_text(self, v):
        self.speed_label.setText("instant" if v == 0 else f"{v} chars/s")

    def _download(self):
        self.dl.setEnabled(False)

        def run():
            try:
                banks.download_generaluser(self.bank_message.emit)
            except Exception as exc:
                self.bank_message.emit(f"Download failed: {exc}")

        threading.Thread(target=run, daemon=True).start()

    def _revert(self):
        banks.use_bundled()
        self.bank_label.setText("Sound bank: FluidR3 Mono (bundled). Restart the game to hear it.")

    def apply(self):
        s = self.s
        s.flicker = self.flicker.currentData()
        s.honest_controls = self.honest.isChecked()
        s.flashlight_cone = self.cone.isChecked()
        s.timed_choices = self.timed.isChecked()
        s.fourth_wall = self.fourth.isChecked()
        s.text_size = self.size.value()
        s.font = self.font.currentText()
        s.reveal_speed = self.speed.value()
        s.music_volume = self.volume.value()
        return s


class TheoryDialog(QDialog):
    def __init__(self, theory, collected, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File a theory")
        self.theory = theory
        v = QVBoxLayout(self)
        title = QLabel(theory.title)
        title.setWordWrap(True)
        title.setFont(QFont("Caveat", 20))
        v.addWidget(title)
        form = QFormLayout()
        self.boxes = {}
        for name, opts in theory.available(collected):
            box = QComboBox()
            for text, _correct, _need in opts:
                box.addItem(text)
            form.addRow(name.capitalize(), box)
            self.boxes[name] = box
        v.addLayout(form)
        note = QLabel("Options only show up once you have found something that supports them.")
        note.setObjectName("small")
        note.setWordWrap(True)
        v.addWidget(note)
        row = QHBoxLayout()
        row.addStretch(1)
        back = QPushButton("Keep looking")
        ok = QPushButton("File it")
        for b in (back, ok):
            b.setObjectName("flat")
        back.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        row.addWidget(back)
        row.addWidget(ok)
        v.addLayout(row)
        self.resize(560, 300)

    def answers(self):
        return {k: b.currentText() for k, b in self.boxes.items()}


class SaveDialog(QDialog):
    SLOTS = ("auto", "1", "2", "3")

    def __init__(self, session, mode, corrupt=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save" if mode == "save" else "Load")
        self.slot = None
        v = QVBoxLayout(self)
        for slot in self.SLOTS:
            if mode == "save" and slot == "auto":
                continue
            info = session.slot_info(slot) if session else None
            name = "Autosave" if slot == "auto" else f"Slot {slot}"
            if corrupt and slot == "2":
                label = f"{name}   ▒▒▓ save data unreadable ▓▒▒   one six one zero, one"
                b = QPushButton(label)
                b.setEnabled(False)
            else:
                desc = (f"{info['chapter_no']}. {info['chapter_title']}   {info['saved']}"
                        if info else "empty")
                b = QPushButton(f"{name}   {desc}")
                b.setEnabled(mode == "save" or info is not None)
                b.clicked.connect(lambda _=False, s=slot: self._pick(s))
            v.addWidget(b)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("flat")
        cancel.clicked.connect(self.reject)
        v.addWidget(cancel)
        self.resize(560, 260)

    def _pick(self, slot):
        self.slot = slot
        self.accept()


class HowToDialog(QDialog):
    def __init__(self, rewritten=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("How to Play")
        v = QVBoxLayout(self)
        t = QTextBrowser()
        t.setHtml(HOWTO_REWRITTEN if rewritten else HOWTO)
        v.addWidget(t)
        ok = QPushButton("Close")
        ok.setObjectName("flat")
        ok.clicked.connect(self.accept)
        v.addWidget(ok)
        self.resize(620, 560)


class FakeCrash(QWidget):
    """Covers the window with a crash report. The Restart button brings the
    game straight back where it was."""
    done = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background: #000000; color: #D0D0D0;")
        v = QVBoxLayout(self)
        v.setContentsMargins(80, 80, 80, 80)
        msg = QLabel(CRASH_TEXT)
        msg.setFont(QFont("DejaVu Sans Mono", 11))
        msg.setStyleSheet("background: #1E1E1E; color: #E0E0E0; padding: 18px; border: 1px solid #555;")
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        v.addStretch(1)
        v.addWidget(msg)
        row = QHBoxLayout()
        row.addStretch(1)
        b = QPushButton("Restart")
        b.setStyleSheet("background: #2D2D2D; color: #EEE; border: 1px solid #666; padding: 6px 18px;")
        b.clicked.connect(self._restart)
        row.addWidget(b)
        v.addLayout(row)
        v.addStretch(1)

    def show_over(self):
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()

    def _restart(self):
        self.hide()
        self.done.emit()
