"""The main window: title screen and game, and the controller between the
Ink session and everything on screen."""

import os
import time

from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QColor, QCursor, QIcon, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QPushButton, QSplitter,
    QStackedWidget, QTabWidget, QVBoxLayout, QWidget,
)

from . import paths, story, themes
from .settings import load_profile, load_settings, save_profile, save_settings
from .themes.overlay import Overlay
from .ui.dialogs import FakeCrash, HowToDialog, SaveDialog, SettingsDialog, TheoryDialog
from .ui.sidebar import EvidenceTab, MapTab, NotebookTab, RadioTab
from .ui.storyview import make_story_pane
from .ui.title import TitleScreen
from .ui.widgets import ChoicePanel, LCDWatch, NerveMeter

APP_TITLE = "Calder Falls"
LOW_NERVE = 3
COUNT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven"]


def needle_cursor():
    pm = QPixmap(24, 24)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setPen(QPen(QColor("#B23A22"), 2))
    p.drawLine(QPointF(4, 2), QPointF(4, 22))
    p.setPen(QPen(QColor(178, 58, 34, 90), 6))
    p.drawLine(QPointF(4, 6), QPointF(4, 18))
    p.end()
    return QCursor(pm, 4, 2)


class GameWindow(QMainWindow):
    def __init__(self, audio=None, headless=False):
        super().__init__()
        self.headless = headless
        self.audio = audio
        self.settings = load_settings()
        self.profile = load_profile()
        self.session = None
        self.pending_timed = None
        self.pending_crash = False
        self.corrupt_once = False
        self.ended = False
        self.stage_name = "midnight"
        self.stage_now = themes.STAGES["midnight"]
        self.stage_from = self.stage_now
        self.stage_to = self.stage_now
        self.stage_t = 1.0
        self.last_restyle = 0.0
        self.setWindowTitle(APP_TITLE)
        icon = os.path.join(paths.data_dir(), "assets", "icon", "calder-falls-256.png")
        if os.path.isfile(icon):
            self.setWindowIcon(QIcon(icon))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.title = TitleScreen()
        self.stack.addWidget(self.title)
        self.game = self._build_game()
        self.stack.addWidget(self.game)
        self.overlay = Overlay(self.stack)
        self.crash = FakeCrash(self.stack)
        self.crash.hide()
        self.crash.done.connect(self._after_crash)

        t = self.title
        t.new_game.connect(self.new_game)
        t.continue_game.connect(self.continue_game)
        t.load_game.connect(self.load_dialog)
        t.settings.connect(self.settings_dialog)
        t.howto.connect(self.howto)
        t.quit.connect(self.close)
        QShortcut(QKeySequence("Escape"), self, activated=self._menu_at_cursor)

        self.anim = QTimer(self)
        self.anim.timeout.connect(self._animate_stage)
        self.anim.start(50)
        self.apply_settings()
        self.show_title()
        self.resize(1320, 820)

    # ------------------------------------------------------------ layout
    def _build_game(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        top = QFrame()
        top.setObjectName("topstrip")
        th = QHBoxLayout(top)
        th.setContentsMargins(14, 6, 14, 6)
        self.chapter = QLabel("")
        self.chapter.setObjectName("chapter")
        self.items = QLabel("")
        self.items.setObjectName("small")
        self.watch = LCDWatch()
        self.nerve = NerveMeter()
        self.hint_btn = QPushButton("Hint")
        self.menu_btn = QPushButton("Menu")
        for b in (self.hint_btn, self.menu_btn):
            b.setObjectName("menu")
        self.hint_btn.clicked.connect(self.show_hint)
        self.menu_btn.clicked.connect(lambda: self._menu(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft())))
        th.addWidget(self.chapter)
        th.addSpacing(16)
        th.addWidget(self.items, 1)
        th.addWidget(self.watch)
        th.addSpacing(10)
        th.addWidget(self.nerve)
        th.addSpacing(10)
        th.addWidget(self.hint_btn)
        th.addWidget(self.menu_btn)
        v.addWidget(top)

        split = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(0)
        self.scroll, self.view = make_story_pane()
        lv.addWidget(self.scroll, 1)
        self.choices = ChoicePanel()
        lv.addWidget(self.choices)
        split.addWidget(left)

        self.tabs = QTabWidget()
        self.notebook = NotebookTab()
        self.evidence = EvidenceTab()
        self.map = MapTab()
        self.radio = RadioTab()
        self.tabs.addTab(self.notebook, "Notebook")
        self.tabs.addTab(self.evidence, "Evidence")
        self.tabs.addTab(self.map, "Map")
        self.tabs.addTab(self.radio, "Radio")
        self.tabs.setMinimumWidth(330)
        split.addWidget(self.tabs)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 1)
        split.setSizes([920, 380])
        v.addWidget(split, 1)

        self.view.revealed.connect(self._revealed)
        self.choices.chosen.connect(self.on_choice)
        self.radio.listen.connect(self.on_choice)
        return page

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.overlay.setGeometry(self.stack.rect())
        self.overlay.raise_()
        if self.crash.isVisible():
            self.crash.setGeometry(self.stack.rect())

    # ------------------------------------------------------------ theme
    def _effective_stage_name(self):
        name = self.stage_name
        if self.session and self.stack.currentWidget() is self.game and self.session.nerve <= LOW_NERVE:
            name = themes.push(name)
        return name

    def set_stage(self, name, instant=False):
        self.stage_name = name
        target = themes.STAGES[self._effective_stage_name()]
        if target == self.stage_to and not instant:
            return
        self.stage_from = self.stage_now
        self.stage_to = target
        self.stage_t = 1.0 if instant else 0.0
        if instant:
            self._push_stage(target, restyle=True)

    def _animate_stage(self):
        if self.stage_t < 1.0:
            self.stage_t = min(1.0, self.stage_t + 0.025)
            st = themes.interpolate(self.stage_from, self.stage_to, self.stage_t)
            now = time.monotonic()
            # Restyling repaints the whole window. With no flicker, do it once
            # at the end of the fade instead of four times a second.
            step = 0.25 if self.settings.flicker != "off" else 999.0
            restyle = self.stage_t >= 1.0 or now - self.last_restyle > step
            self._push_stage(st, restyle)

    def _push_stage(self, st, restyle):
        self.stage_now = st
        calm = themes.calm(st, self.settings.flicker)
        self.overlay.set_stage(calm)
        self.view.set_stage(calm)
        self.nerve.set_value(self.nerve.value, st.accent)
        if restyle:
            self.last_restyle = time.monotonic()
            self.setStyleSheet(themes.stylesheet(st, self.settings.text_size))

    # ------------------------------------------------------------ settings
    def apply_settings(self):
        s = self.settings
        self.view.set_font(s.font, s.text_size)
        self.view.speed = float(s.reveal_speed)
        self.view.flashlight_cone = s.flashlight_cone
        self.view.flicker_mode = s.flicker
        self.overlay.set_mode(s.flicker)
        self.title.tower.blinks = s.flicker != "off"
        if self.audio:
            self.audio.set_volume(s.music_volume / 100.0 * 0.95)
        self._push_stage(self.stage_now, restyle=True)
        if self.session:
            self._show_choices()

    def settings_dialog(self):
        d = SettingsDialog(self.settings, self)
        if d.exec():
            self.settings = d.apply()
            save_settings(self.settings)
            self.apply_settings()

    # ------------------------------------------------------------ title
    def _any_save(self):
        probe = story.Session.__new__(story.Session)
        probe.save_dir = os.path.join(paths.user_dir(), "saves")
        latest = None
        for slot in SaveDialog.SLOTS:
            info = story.Session.slot_info(probe, slot)
            if info and (latest is None or info["saved"] > latest[1]):
                latest = (slot, info["saved"])
        return latest[0] if latest else None

    def show_title(self):
        self.stack.setCurrentWidget(self.title)
        self.title.refresh(self.profile, self.settings.fourth_wall, self._any_save() is not None,
                           self.settings.flicker)
        self.setWindowTitle(APP_TITLE)
        self.set_stage("midnight", instant=True)
        self.unsetCursor()
        if self.audio:
            for layer in ("drums", "bass", "lead", "pad", "noise"):
                self.audio.set_layer(layer, True)
            self.audio.set_detune(0)
            self.audio.set_tempo(1.0)
            self.audio.set_static(0)
            self.audio.play("calder_falls")

    def _new_session(self):
        try:
            self.session = story.Session(audio=self.audio, strict=False)
        except story.StoryError as exc:
            QMessageBox.critical(self, APP_TITLE, str(exc))
            self.session = None
            return False
        return True

    def new_game(self):
        if not self._new_session():
            return
        self.profile.playthroughs += 1
        save_profile(self.profile)
        self.session.new_game(second_run=bool(self.profile.endings_seen))
        self.ended = False
        self._enter_game()
        self.view.clear()
        self.step()

    def continue_game(self):
        slot = self._any_save()
        if slot:
            self._load(slot)

    def load_dialog(self):
        if self.session is None and not self._new_session():
            return
        d = SaveDialog(self.session, "load", corrupt=self.corrupt_once and self.settings.fourth_wall, parent=self)
        self.corrupt_once = False
        if d.exec() and d.slot:
            self._load(d.slot)

    def _load(self, slot):
        if self.session is None and not self._new_session():
            return
        try:
            self.session.load(slot)
        except Exception as exc:
            QMessageBox.warning(self, APP_TITLE, f"Could not load that save: {exc}")
            return
        self.ended = False
        self._enter_game()
        st = self.session.state
        self.view.load_transcript(st.transcript)
        self._refresh_all()
        self.set_stage(st.theme, instant=True)
        self._show_choices()

    def save_dialog(self):
        if not self.session:
            return
        d = SaveDialog(self.session, "save", parent=self)
        if d.exec() and d.slot:
            self.session.save(d.slot)

    def howto(self):
        rewritten = bool(self.session and self.session.state.howto_rewritten and self.settings.fourth_wall)
        HowToDialog(rewritten, self).exec()

    def _enter_game(self):
        self.stack.setCurrentWidget(self.game)
        self.overlay.raise_()

    def _menu_at_cursor(self):
        if self.stack.currentWidget() is self.game:
            self._menu(QCursor.pos())

    def _menu(self, where):
        m = QMenu(self)
        m.addAction("Save", self.save_dialog)
        m.addAction("Load", self.load_dialog)
        m.addAction("Settings", self.settings_dialog)
        m.addAction("How to Play", self.howto)
        m.addSeparator()
        m.addAction("Title screen", self.show_title)
        m.exec(where)

    def show_hint(self):
        if self.session:
            QMessageBox.information(self, "Hint", self.session.state.hint)

    # ------------------------------------------------------------ playing
    def step(self):
        self.choices.clear()
        self.radio.set_offers([])
        events = self.session.step()
        self.apply_events(events)
        self.nerve.set_value(self.session.nerve)
        self.set_stage(self.session.state.theme)
        if not self.view.is_revealing():
            self._revealed()

    def apply_events(self, events):
        for ev in events:
            kind = ev[0]
            if kind == "text":
                style = "radio" if ev[2] in ("1610", "radio", "police") else "story"
                self.view.add(ev[1], style)
            elif kind == "clear":
                self.view.clear()
            elif kind == "chapter":
                self.chapter.setText(f"{ev[1]}.  {ev[2]}")
            elif kind == "time":
                self.watch.set_time(ev[1])
            elif kind == "pause":
                self.view.add_pause(ev[1])
            elif kind == "timed":
                self.pending_timed = (ev[1], ev[2])
            elif kind == "dark":
                self.view.set_dark(ev[1])
            elif kind == "battery":
                self.view.battery_low = ev[1]
            elif kind == "shadow":
                self.view.shadow = ev[1]
            elif kind == "warp" and ev[1] == "scrollback":
                self.view.scrollback(*ev[2])
            elif kind == "fourth":
                if not self.settings.fourth_wall:
                    continue
                if ev[1] == "crash":
                    self.pending_crash = True
                elif ev[1] == "corrupt_save":
                    self.corrupt_once = True
            elif kind == "ending":
                if ev[1] not in self.profile.endings_seen:
                    self.profile.endings_seen.append(ev[1])
                save_profile(self.profile)
            elif kind == "end":
                self.ended = True
        self._refresh_all()

    def _refresh_all(self):
        st = self.session.state
        self.chapter.setText(f"{st.chapter_no}.  {st.chapter_title}" if st.chapter_title else "")
        self.watch.set_time(st.time)
        rounds = self.session.get_var("rounds", 0)
        names = [f"pistol ({rounds})" if i == "pistol" else i for i in st.items]
        self.items.setText("   ".join(names))
        self.notebook.set_lines(st.notes)
        self.evidence.set_evidence(st.evidence, st.evidence_order)
        self.map.set_marks(st.map_marks)
        self.notebook.set_ledger(st.tabs_renamed)
        self.tabs.setTabText(0, "Ledger" if st.tabs_renamed else "Notebook")
        self.tabs.setTabText(1, "Family" if st.tabs_renamed else "Evidence")
        self.radio.drift = st.radio_drift
        if st.title_count:
            words = st.title_count
            if words.isdigit() and int(words) < len(COUNT_WORDS):
                words = COUNT_WORDS[int(words)]
            self.setWindowTitle(f"{APP_TITLE}   one six one zero, {words}")
        else:
            self.setWindowTitle(APP_TITLE)
        if st.cursor_needle or st.theme == "bleed":
            self.game.setCursor(needle_cursor())
        else:
            self.game.unsetCursor()
        self.view.dark = st.dark
        self.view.battery_low = st.battery_low

    def _revealed(self):
        if self.session is None or self.stack.currentWidget() is not self.game:
            return
        if self.pending_crash:
            self.pending_crash = False
            self.crash.show_over()
            return
        if self.ended:
            self._show_end()
            return
        self._show_choices()

    def _show_choices(self):
        if self.view.is_revealing() or self.session is None or self.ended:
            return
        flinch = (self.session.nerve <= LOW_NERVE or self.session.state.flinch)
        self.choices.show_choices(self.session.visible_choices(), self.settings.honest_controls, flinch)
        self.radio.set_offers(self.session.radio_offers())
        if self.pending_timed and self.settings.timed_choices:
            secs, idx = self.pending_timed
            self.choices.start_timer(secs, idx)
        self.pending_timed = None

    def _after_crash(self):
        self.view.update()
        QTimer.singleShot(1200, self._show_choices)

    def on_choice(self, choice):
        if self.session is None or self.ended:
            return
        answers = None
        if choice.kind == "file":
            theory = self.session.pending_theory()
            if theory is not None:
                if self.headless:
                    answers = theory.correct_answers()
                else:
                    d = TheoryDialog(theory, set(self.session.state.evidence), self)
                    if not d.exec():
                        return
                    answers = d.answers()
        self.view.add(choice.truth, "echo")
        self.session.choose(choice, answers)
        self.step()

    def _show_end(self):
        self.choices.clear()
        b = QPushButton("The end. Back to the title screen.")
        b.setObjectName("choice")
        b.clicked.connect(self.show_title)
        self.choices.lay.addWidget(b)
        self.choices.buttons.append(b)

    def closeEvent(self, e):
        if self.audio:
            self.audio.close()
        super().closeEvent(e)
