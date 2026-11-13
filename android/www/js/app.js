/* The Android front end's controller: title screen, game screen, dialogs,
   settings and saves. A port of calder_falls/app.py, ui/title.py,
   ui/dialogs.py and settings.py. The rules for what happens when live in
   the same order as app.py, so a change there has an obvious home here. */

(function () {
  "use strict";

  const APP_TITLE = "Calder Falls";
  const LOW_NERVE = 3;
  const COUNT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven"];
  const SLOTS = ["auto", "1", "2", "3"];
  const $ = (id) => document.getElementById(id);

  // ------------------------------------------------------------ storage
  // Everything the desktop keeps in ~/.local/share/calder-falls lives in
  // the WebView's own storage, which Android keeps with the app's data.
  const store = {
    get(k) {
      try {
        return localStorage.getItem("cf:" + k);
      } catch (e) {
        return null;
      }
    },
    set(k, v) {
      try {
        localStorage.setItem("cf:" + k, v);
      } catch (e) {
        /* full or blocked: the game keeps going without saving */
      }
    },
  };

  const SETTINGS = {
    flicker: "gentle", // off, gentle, full
    honest_controls: false,
    flashlight_cone: true,
    text_size: 15,
    reveal_speed: 55, // characters per second, 0 = instant
    timed_choices: false,
    fourth_wall: true,
    font: "Courier Prime", // or Source Serif 4
    music_volume: 80,
    first_launch_done: false,
  };
  const PROFILE = { launches: 0, playthroughs: 0, endings_seen: [] };

  function load(name, defaults) {
    const out = JSON.parse(JSON.stringify(defaults));
    try {
      const data = JSON.parse(store.get(name) || "{}");
      for (const k of Object.keys(out)) if (k in data) out[k] = data[k];
    } catch (e) {
      /* broken file means defaults, never a crash */
    }
    return out;
  }
  const save = (name, obj) => store.set(name, JSON.stringify(obj));

  // ------------------------------------------------------------ text
  const HOWTO = `
<h3>How to play</h3>
<p>You are Detective Sergeant Cal Brennick, state police, Major Crimes. Read, then pick
what he does with the buttons under the text. Tap the text to skip ahead while it types.</p>
<p><b>The notebook.</b> What you find goes into the tabs: notes in the pad, photos and
statements on the corkboard. When the case gives you the chance, you file a theory: who,
what, when, why, chosen from what you have found. A right theory moves you on. A wrong one
puts you back where you started, and the house will be worse for it. Nothing you find is
wasted, even on a reset.</p>
<p><b>Nerve</b> is the bar at the top. It drops when things go badly and comes back
when you rest or smoke. Low Nerve makes it harder to see straight.</p>
<p><b>The radio</b> tab has an AM dial and a police knob. Sometimes there is something on a
frequency or on the band. Tune to it and listen, or key the knob. Some voices on there
tell the truth. Not all of them are on your side.</p>
<p><b>Hint</b> in the top bar always works and never lies.</p>
<p>The game saves at the start of every loop and every chapter. Save to a slot from the
menu whenever you like. The back button opens the menu too.</p>`;

  const HOWTO_REWRITTEN = `
<h3>How to listen</h3>
<p>You are the vessel. You have been the vessel since 1957, when he could not make room
and your mother took you south in the back seat. Read, then pick what he does. Touch the
text. It does not matter how fast you read. We are patient.</p>
<p><b>The ledger.</b> What you find goes in the tabs. You thought you were building a
case. You were filling in a page. Every man we brought in is written there, and how he
turned out. There is a line left at the bottom.</p>
<p><b>Nerve</b> is how much of you is left to hold us. Do not worry about it. We will
hold on to the rest.</p>
<p><b>The radio</b> is how we talk. It always was. One six one zero. Say it with us, and
then say how many live in your house.</p>
<p><b>Hint</b> still never lies. That is the only thing on this page that is yours.</p>`;

  const CRASH_TEXT = `calder-falls has stopped responding.

Traceback (most recent call last):
  File "calder_falls/app.py", line 1610, in <module>
    house.make_room(occupants=household.count())
  File "calder_falls/ledger.py", line 57, in make_room
    raise VesselError("unsuitable")
VesselError: unsuitable

A report has been written to /data/data/io.github.nullangst.calderfalls/ledger.txt
`;

  function subtitleFor(profile, fourthWall) {
    if (!fourthWall) return "Ostrander County, October 1986";
    const seen = new Set(profile.endings_seen);
    const n = profile.launches;
    if (seen.has("quiet_house") && n % 2 === 0) return "Somewhere, someone clips it.";
    if (seen.has("dawn") && n % 3 === 0) return "The line stays open.";
    if (seen.has("broadcast")) return "Now on every station.";
    if (n <= 1) return "Ostrander County, October 1986";
    if (n <= 3) return "You came back.";
    if (n <= 6) return "one six one zero, one";
    return "We have kept your place.";
  }

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  // ------------------------------------------------------------ dialogs
  const dialogs = [];

  function dialog(build) {
    return new Promise((resolve) => {
      const back = document.createElement("div");
      back.className = "dialog-back";
      const box = document.createElement("div");
      box.className = "dialog";
      back.appendChild(box);
      const close = (value) => {
        back.remove();
        const i = dialogs.indexOf(entry);
        if (i >= 0) dialogs.splice(i, 1);
        resolve(value);
      };
      const entry = { close, cancel: () => close(null) };
      dialogs.push(entry);
      build(box, close);
      $("dialogs").appendChild(back);
    });
  }

  function button(label, onClick, cls) {
    const b = document.createElement("button");
    b.textContent = label;
    if (cls) b.className = cls;
    b.addEventListener("click", onClick);
    return b;
  }

  function row(...buttons) {
    const r = document.createElement("div");
    r.className = "row";
    r.append(...buttons);
    return r;
  }

  function message(title, text) {
    return dialog((box, close) => {
      box.innerHTML = `<h3>${esc(title)}</h3><p>${esc(text)}</p>`;
      box.appendChild(row(button("OK", () => close(true), "flat")));
    });
  }

  function firstLaunchDialog() {
    return dialog((box, close) => {
      box.innerHTML = `<p>Calder Falls uses flickering light, flashing, and scanline effects.
        If flashing images bother you or could trigger a seizure, turn them off.
        You can change this any time in Settings.</p>`;
      for (const [key, label] of [
        ["off", "No flicker: a still picture, nothing flashes or moves on its own"],
        ["gentle", "Gentle (default): softened flicker"],
        ["full", "Full: everything the game does"],
      ]) {
        const l = document.createElement("label");
        l.className = "check";
        l.innerHTML = `<input type="radio" name="flick" value="${key}" ${key === "gentle" ? "checked" : ""}><span>${label}</span>`;
        box.appendChild(l);
      }
      box.appendChild(row(button("Continue", () => close(box.querySelector("input:checked").value), "flat")));
    });
  }

  function settingsDialog(s) {
    return dialog((box, close) => {
      box.innerHTML = `<h3>Settings</h3>
        <div class="field"><span>Flicker and flashes</span>
          <select id="s-flicker"><option value="off">No flicker</option><option value="gentle">Gentle</option><option value="full">Full</option></select>
          <span class="small">No flicker: no flashes, no scanlines, grain and fog frozen, the flashlight steady, the title screen light always on.</span></div>
        <label class="check"><input type="checkbox" id="s-honest"><span>Honest controls (a tap always does what the button says)</span></label>
        <label class="check"><input type="checkbox" id="s-cone"><span>Flashlight cone in dark scenes (off dims the text evenly)</span></label>
        <label class="check"><input type="checkbox" id="s-timed"><span>Timed choices</span></label>
        <label class="check"><input type="checkbox" id="s-fourth"><span>Fourth-wall effects (fake crash, fake corrupted save, changing title screen)</span></label>
        <div class="field"><span>Text size <b id="s-size-l"></b></span><input type="range" id="s-size" min="11" max="26"></div>
        <div class="field"><span>Story font</span><select id="s-font"><option>Courier Prime</option><option>Source Serif 4</option></select></div>
        <div class="field"><span>Reveal speed <b id="s-speed-l"></b></span><input type="range" id="s-speed" min="0" max="200"></div>
        <div class="field"><span>Music volume <b id="s-vol-l"></b></span><input type="range" id="s-vol" min="0" max="100"></div>`;
      const q = (id) => box.querySelector("#" + id);
      q("s-flicker").value = s.flicker;
      q("s-honest").checked = s.honest_controls;
      q("s-cone").checked = s.flashlight_cone;
      q("s-timed").checked = s.timed_choices;
      q("s-fourth").checked = s.fourth_wall;
      q("s-size").value = s.text_size;
      q("s-font").value = s.font;
      q("s-speed").value = s.reveal_speed;
      q("s-vol").value = s.music_volume;
      const labels = () => {
        q("s-size-l").textContent = q("s-size").value;
        const v = +q("s-speed").value;
        q("s-speed-l").textContent = v === 0 ? "instant" : `${v} chars/s`;
        q("s-vol-l").textContent = q("s-vol").value;
      };
      box.addEventListener("input", labels);
      labels();
      box.appendChild(row(
        button("Cancel", () => close(null), "flat"),
        button("Save", () => close(Object.assign({}, s, {
          flicker: q("s-flicker").value,
          honest_controls: q("s-honest").checked,
          flashlight_cone: q("s-cone").checked,
          timed_choices: q("s-timed").checked,
          fourth_wall: q("s-fourth").checked,
          text_size: +q("s-size").value,
          font: q("s-font").value,
          reveal_speed: +q("s-speed").value,
          music_volume: +q("s-vol").value,
        })), "flat"),
      ));
    });
  }

  function theoryDialog(theory, collected) {
    return dialog((box, close) => {
      const t = document.createElement("div");
      t.className = "theory-title";
      t.textContent = theory.title;
      box.appendChild(t);
      const boxes = {};
      for (const [name, opts] of CFStory.Theory.available(theory, collected)) {
        const f = document.createElement("div");
        f.className = "field";
        const sel = document.createElement("select");
        for (const [text] of opts) {
          const o = document.createElement("option");
          o.textContent = text;
          sel.appendChild(o);
        }
        f.append(name.charAt(0).toUpperCase() + name.slice(1), sel);
        box.appendChild(f);
        boxes[name] = sel;
      }
      const note = document.createElement("div");
      note.className = "small";
      note.textContent = "Options only show up once you have found something that supports them.";
      box.appendChild(note);
      box.appendChild(row(
        button("Keep looking", () => close(null), "flat"),
        button("File it", () => {
          const out = {};
          for (const [k, sel] of Object.entries(boxes)) out[k] = sel.value;
          close(out);
        }, "flat"),
      ));
    });
  }

  function saveDialog(session, mode, corrupt) {
    return dialog((box, close) => {
      box.innerHTML = `<h3>${mode === "save" ? "Save" : "Load"}</h3>`;
      const list = document.createElement("div");
      list.className = "slots";
      for (const slot of SLOTS) {
        if (mode === "save" && slot === "auto") continue;
        const info = session ? session.slotInfo(slot) : null;
        const name = slot === "auto" ? "Autosave" : `Slot ${slot}`;
        let b;
        if (corrupt && slot === "2") {
          b = button(`${name}   ▒▒▓ save data unreadable ▓▒▒   one six one zero, one`, () => {});
          b.disabled = true;
        } else {
          const desc = info ? `${info.chapter_no}. ${info.chapter_title}   ${info.saved}` : "empty";
          b = button(`${name}   ${desc}`, () => close(slot));
          b.disabled = !(mode === "save" || info);
        }
        list.appendChild(b);
      }
      box.appendChild(list);
      box.appendChild(row(button("Cancel", () => close(null), "flat")));
    });
  }

  function howtoDialog(rewritten) {
    return dialog((box, close) => {
      const d = document.createElement("div");
      d.className = "howto";
      d.innerHTML = rewritten ? HOWTO_REWRITTEN : HOWTO;
      box.appendChild(d);
      box.appendChild(row(button("Close", () => close(true), "flat")));
    });
  }

  function menuDialog(items) {
    return dialog((box, close) => {
      box.classList.add("menu-list");
      for (const [label, fn] of items) box.appendChild(button(label, () => close(fn)));
      box.appendChild(button("Back to the story", () => close(null)));
    }).then((fn) => fn && fn());
  }

  // ------------------------------------------------------------ the game
  class Game {
    constructor(storyJson) {
      this.storyJson = storyJson;
      this.settings = load("settings", SETTINGS);
      this.profile = load("profile", PROFILE);
      this.music = new CFMusic("music/");
      this.session = null;
      this.pendingTimed = null;
      this.pendingCrash = false;
      this.corruptOnce = false;
      this.ended = false;
      this.inGame = false;
      this.stageName = "midnight";
      this.stageNow = CFThemes.STAGES.midnight;
      this.stageFrom = this.stageNow;
      this.stageTo = this.stageNow;
      this.stageT = 1;
      this.timer = null;

      this.overlay = new CFOverlay($("overlay"));
      this.view = new CFStoryView($("story"), $("story-inner"), $("dark"), () => this._revealed());
      this.watch = new CFWidgets.Watch($("watch"));
      this.nerve = new CFWidgets.Nerve($("nerve"));
      this.notebook = new CFWidgets.Notebook($("notebook-page"));
      this.dial = new CFWidgets.Dial($("dial"), () => this._radioRefresh());
      this.offers = [];
      this.radioDrift = false;
      this.evidence = {};
      this.evOrder = [];
      this.marks = [];
      this.tab = "story";

      this._wire();
      setInterval(() => this._animateStage(), 50);
      setInterval(() => this._driftStep(), 120);
      this.towerOn = true;
      setInterval(() => this._blink(), 900);
      new ResizeObserver(() => this._repaintSide()).observe($("side"));
    }

    async start() {
      this.profile.launches += 1;
      save("profile", this.profile);
      if (!this.settings.first_launch_done) {
        this.settings.flicker = await firstLaunchDialog();
        this.settings.first_launch_done = true;
        save("settings", this.settings);
      }
      await this.music.init();
      this.applySettings();
      this.showTitle();
    }

    // ------------------------------------------------------------ wiring
    _wire() {
      document.querySelectorAll("#title [data-act]").forEach((b) =>
        b.addEventListener("click", () => {
          const act = b.dataset.act;
          if (act === "new") this.newGame();
          else if (act === "continue") this.continueGame();
          else if (act === "load") this.loadDialog();
          else if (act === "settings") this.settingsDialog();
          else if (act === "howto") this.howto();
        }));
      $("hint-btn").addEventListener("click", () => this.session && message("Hint", this.session.state.hint));
      $("menu-btn").addEventListener("click", () => this.menu());
      document.querySelectorAll("#tabs button").forEach((b) => b.addEventListener("click", () => this.showTab(b.dataset.tab)));
      $("nb-prev").addEventListener("click", () => this._flip(-1));
      $("nb-next").addEventListener("click", () => this._flip(1));
      $("am-btn").addEventListener("click", () => {
        const c = this._amOffer();
        if (c) this.onChoice(c);
      });
      $("knob").addEventListener("click", () => {
        const c = this.offers.find((o) => o.kind === "police");
        if (c) this.onChoice(c);
      });
      $("crash-restart").addEventListener("click", () => {
        $("crash").classList.add("hidden");
        setTimeout(() => this._showChoices(), 1200);
      });
      document.addEventListener("pointerdown", () => this.music.resume(), { capture: true });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") window.CF.back();
      });
      document.addEventListener("visibilitychange", () => {
        if (document.hidden) this.music.suspend();
        else this.music.resume();
      });
    }

    // Phones show one pane at a time; a wide screen shows the story beside the tabs
    showTab(tab) {
      const wide = window.matchMedia("(min-width: 900px)").matches;
      if (wide && tab === "story") tab = this.tab === "story" ? "notebook" : this.tab;
      this.tab = tab;
      document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
      document.querySelectorAll("#side .pane").forEach((p) => p.classList.toggle("active", p.dataset.pane === tab));
      $("left").classList.toggle("active", tab === "story");
      $("side").classList.toggle("open", tab !== "story");
      this._repaintSide();
    }

    _sideVisible(tab) {
      const pane = document.querySelector(`#side .pane[data-pane="${tab}"]`);
      return pane && pane.offsetParent !== null;
    }

    // ------------------------------------------------------------ theme
    _effectiveStageName() {
      let name = this.stageName;
      if (this.session && this.inGame && this.session.nerve <= LOW_NERVE) name = CFThemes.push(name);
      return name;
    }

    setStage(name, instant = false) {
      this.stageName = name;
      const target = CFThemes.STAGES[this._effectiveStageName()];
      if (target === this.stageTo && !instant) return;
      this.stageFrom = this.stageNow;
      this.stageTo = target;
      this.stageT = instant ? 1 : 0;
      if (instant) this._pushStage(target);
    }

    _animateStage() {
      if (this.stageT < 1) {
        this.stageT = Math.min(1, this.stageT + 0.025);
        // With no flicker, recolor once at the end of the fade
        if (this.settings.flicker !== "off" || this.stageT >= 1) {
          this._pushStage(CFThemes.interpolate(this.stageFrom, this.stageTo, this.stageT));
        }
      }
    }

    _pushStage(st) {
      this.stageNow = st;
      const calm = CFThemes.calm(st, this.settings.flicker);
      this.overlay.setStage(calm);
      this.view.setStage(calm);
      this.nerve.set(this.nerve.value, st.accent);
      const root = document.documentElement.style;
      for (const [k, v] of Object.entries(CFThemes.cssVars(st))) root.setProperty(k, v);
    }

    // ------------------------------------------------------------ settings
    applySettings() {
      const s = this.settings;
      const root = document.documentElement.style;
      root.setProperty("--px", `${s.text_size}px`);
      root.setProperty("--small", `${Math.max(11, s.text_size - 3)}px`);
      root.setProperty("--story-px", `${s.text_size + 2}px`);
      root.setProperty("--story-font", s.font === "Source Serif 4" ? '"Source Serif 4", serif' : '"Courier Prime", monospace');
      this.view.speed = +s.reveal_speed;
      this.view.flashlightCone = s.flashlight_cone;
      this.view.flickerMode = s.flicker;
      this.overlay.setMode(s.flicker);
      this.music.setVolume((s.music_volume / 100) * 0.95);
      this._pushStage(this.stageNow);
      if (this.session && this.inGame) this._showChoices();
    }

    async settingsDialog() {
      const s = await settingsDialog(this.settings);
      if (s) {
        this.settings = s;
        save("settings", s);
        this.applySettings();
      }
    }

    // ------------------------------------------------------------ title
    _newSession() {
      this.session = new CFStory.Session({ ink: window.inkjs, storyJson: this.storyJson, store, audio: this.music });
      return true;
    }

    _anySave() {
      const probe = this.session || new CFStory.Session({ ink: window.inkjs, storyJson: this.storyJson, store });
      let latest = null;
      for (const slot of SLOTS) {
        const info = probe.slotInfo(slot);
        if (info && (!latest || info.saved > latest[1])) latest = [slot, info.saved];
      }
      return latest ? latest[0] : null;
    }

    _blink() {
      const blinks = this.settings.flicker !== "off";
      this.towerOn = blinks ? !this.towerOn : true;
      $("tower-light").classList.toggle("off", !this.towerOn);
    }

    showTitle() {
      this.inGame = false;
      this._stopTimer();
      $("game").classList.add("hidden");
      $("title").classList.remove("hidden");
      $("subtitle").textContent = subtitleFor(this.profile, this.settings.fourth_wall);
      const can = this._anySave() !== null;
      document.querySelector('[data-act="continue"]').disabled = !can;
      document.querySelector('[data-act="load"]').disabled = !can;
      document.title = APP_TITLE;
      this.setStage("midnight", true);
      $("game").classList.remove("needle");
      this.music.title();
    }

    newGame() {
      this._newSession();
      this.profile.playthroughs += 1;
      save("profile", this.profile);
      this.session.newGame(this.profile.endings_seen.length > 0);
      this.ended = false;
      this._enterGame();
      this.view.clear();
      this.step();
    }

    continueGame() {
      const slot = this._anySave();
      if (slot) this._load(slot);
    }

    async loadDialog() {
      if (!this.session) this._newSession();
      const corrupt = this.corruptOnce && this.settings.fourth_wall;
      this.corruptOnce = false;
      const slot = await saveDialog(this.session, "load", corrupt);
      if (slot) this._load(slot);
    }

    _load(slot) {
      if (!this.session) this._newSession();
      try {
        this.session.load(slot);
      } catch (e) {
        message(APP_TITLE, `Could not load that save: ${e.message}`);
        return;
      }
      this.ended = false;
      this._enterGame();
      const st = this.session.state;
      this.view.loadTranscript(st.transcript);
      this._refreshAll();
      this.setStage(st.theme, true);
      this._showChoices();
    }

    async saveDialog() {
      if (!this.session) return;
      const slot = await saveDialog(this.session, "save", false);
      if (slot) this.session.save(slot);
    }

    howto() {
      const rewritten = !!(this.session && this.session.state.howto_rewritten && this.settings.fourth_wall);
      howtoDialog(rewritten);
    }

    _enterGame() {
      this.inGame = true;
      $("title").classList.add("hidden");
      $("game").classList.remove("hidden");
      this.showTab("story");
    }

    menu() {
      menuDialog([
        ["Save", () => this.saveDialog()],
        ["Load", () => this.loadDialog()],
        ["Settings", () => this.settingsDialog()],
        ["How to Play", () => this.howto()],
        ["Title screen", () => this.showTitle()],
      ]);
    }

    // ------------------------------------------------------------ playing
    step() {
      this._clearChoices();
      this._setOffers([]);
      const events = this.session.step();
      this.applyEvents(events);
      this.nerve.set(this.session.nerve);
      this.setStage(this.session.state.theme);
      if (!this.view.isRevealing()) this._revealed();
    }

    applyEvents(events) {
      for (const ev of events) {
        const kind = ev[0];
        if (kind === "text") {
          const style = ["1610", "radio", "police"].includes(ev[2]) ? "radio" : "story";
          this.view.add(ev[1], style);
        } else if (kind === "clear") this.view.clear();
        else if (kind === "time") this.watch.set(ev[1]);
        else if (kind === "pause") this.view.addPause(ev[1]);
        else if (kind === "timed") this.pendingTimed = [ev[1], ev[2]];
        else if (kind === "dark") this.view.setDark(ev[1]);
        else if (kind === "battery") this.view.batteryLow = ev[1];
        else if (kind === "shadow") this.view.shadow = ev[1];
        else if (kind === "warp" && ev[1] === "scrollback") this.view.scrollback(ev[2][0], ev[2][1]);
        else if (kind === "fourth") {
          if (!this.settings.fourth_wall) continue;
          if (ev[1] === "crash") this.pendingCrash = true;
          else if (ev[1] === "corrupt_save") this.corruptOnce = true;
        } else if (kind === "ending") {
          if (!this.profile.endings_seen.includes(ev[1])) this.profile.endings_seen.push(ev[1]);
          save("profile", this.profile);
        } else if (kind === "end") this.ended = true;
      }
      this._refreshAll();
    }

    _refreshAll() {
      const st = this.session.state;
      $("chapter").textContent = st.chapter_title ? `${st.chapter_no}.  ${st.chapter_title}` : "";
      this.watch.set(st.time);
      const rounds = this.session.getVar("rounds", 0);
      $("items").textContent = st.items.map((i) => (i === "pistol" ? `pistol (${rounds})` : i)).join("   ");
      this.notebook.setLines(st.notes);
      this.notebook.ledger = st.tabs_renamed;
      this.evidence = st.evidence;
      this.evOrder = st.evidence_order.slice();
      this.marks = st.map_marks.slice();
      document.querySelector('#tabs [data-tab="notebook"]').textContent = st.tabs_renamed ? "Ledger" : "Notebook";
      document.querySelector('#tabs [data-tab="evidence"]').textContent = st.tabs_renamed ? "Family" : "Evidence";
      this.radioDrift = st.radio_drift;
      if (st.title_count) {
        let words = st.title_count;
        if (/^\d+$/.test(words) && +words < COUNT_WORDS.length) words = COUNT_WORDS[+words];
        // The desktop puts this in the window title. A phone has none, so it
        // sits under the chapter instead.
        document.title = `${APP_TITLE}   one six one zero, ${words}`;
        $("items").textContent = `one six one zero, ${words}`;
      } else document.title = APP_TITLE;
      $("game").classList.toggle("needle", st.cursor_needle || st.theme === "bleed");
      this.view.dark = st.dark;
      this.view.setDark(st.dark);
      this.view.batteryLow = st.battery_low;
      this._repaintSide();
    }

    _repaintSide() {
      if (this._sideVisible("notebook")) this._paintNotebook();
      if (this._sideVisible("evidence")) this._paintEvidence();
      if (this._sideVisible("map")) CFWidgets.paintMap($("map"), this.marks);
      if (this._sideVisible("radio")) {
        this.dial.paint();
        this._radioRefresh();
      }
    }

    _paintNotebook() {
      this.notebook.paint();
      const n = this.notebook.pages();
      $("nb-label").textContent = `page ${this.notebook.page + 1} of ${n}`;
      $("nb-prev").disabled = this.notebook.page <= 0;
      $("nb-next").disabled = this.notebook.page >= n - 1;
    }

    _flip(d) {
      this.notebook.flip(d);
      this._paintNotebook();
    }

    _paintEvidence() {
      const cork = $("cork");
      const key = this.evOrder.join("|");
      if (cork.dataset.key !== key) {
        cork.textContent = "";
        for (const eid of this.evOrder) {
          const c = document.createElement("canvas");
          c.title = this.evidence[eid].title || "";
          c.addEventListener("click", () => {
            const info = this.evidence[eid] || {};
            $("ev-detail").innerHTML = `<b>${esc(info.title || "")}</b><br>${esc(info.caption || "")}<br><i>${esc(info.kind || "")}</i>`;
          });
          cork.appendChild(c);
        }
        cork.dataset.key = key;
      }
      [...cork.children].forEach((c, i) => CFWidgets.paintPolaroid(c, this.evOrder[i], this.evidence[this.evOrder[i]]));
    }

    // ------------------------------------------------------------ radio
    _setOffers(offers) {
      this.offers = offers.slice();
      this._radioRefresh();
    }

    _amOffer() {
      return this.offers.find((c) => c.kind === "radio" && Math.abs(c.freq - this.dial.freq) <= 20) || null;
    }

    _radioRefresh() {
      const am = this._amOffer();
      $("freq").textContent = `${this.dial.freq} kHz` + (am ? "   something is on this frequency" : "");
      $("am-btn").disabled = !am;
      $("am-btn").textContent = am ? `Listen: ${am.text}` : "Listen";
      const pol = this.offers.find((c) => c.kind === "police");
      $("police-label").textContent = pol ? pol.text : "Nothing on the band.";
      if (this._sideVisible("radio")) CFWidgets.paintKnob($("knob"), !!pol);
    }

    _driftStep() {
      // The dial creeps toward 1610 while nobody is looking at it
      if (!this.radioDrift || this._sideVisible("radio")) return;
      const f = this.dial.freq;
      if (f !== 1610) this.dial.setFreq(f + (f < 1610 ? 10 : -10));
    }

    // ------------------------------------------------------------ choices
    _clearChoices() {
      this._stopTimer();
      $("choice-grid").textContent = "";
    }

    _revealed() {
      if (!this.session || !this.inGame) return;
      if (this.pendingCrash) {
        this.pendingCrash = false;
        $("crash-text").textContent = CRASH_TEXT;
        $("crash").classList.remove("hidden");
        return;
      }
      if (this.ended) {
        this._showEnd();
        return;
      }
      this._showChoices();
    }

    _showChoices() {
      if (this.view.isRevealing() || !this.session || this.ended || !this.inGame) return;
      if (!$("crash").classList.contains("hidden")) return;
      const flinch = this.session.nerve <= LOW_NERVE || this.session.state.flinch;
      const honest = this.settings.honest_controls;
      const choices = this.session.visibleChoices();
      const grid = $("choice-grid");
      this._clearChoices();
      // many choices go in two columns so the story keeps its room
      grid.classList.toggle("two", choices.length > 5);
      for (const c of choices) {
        const b = button(honest ? c.truth : c.text, () => this._pick(c));
        // Says one thing. Under a finger or the mouse it may say what it
        // really does, and that is what the tap picks.
        const turn = (on) => {
          if (c.hover && !honest) b.textContent = on ? c.hover : c.text;
        };
        const shy = () => {
          if (flinch && !honest) {
            const dx = (Math.random() < 0.5 ? -1 : 1) * (4 + Math.floor(Math.random() * 6));
            b.style.transform = `translateX(${dx}px)`;
          }
        };
        b.addEventListener("pointerenter", () => {
          turn(true);
          shy();
        });
        b.addEventListener("pointerdown", () => {
          turn(true);
          shy();
        });
        b.addEventListener("pointerleave", () => turn(false));
        b.addEventListener("pointercancel", () => turn(false));
        grid.appendChild(b);
      }
      this._setOffers(this.session.radioOffers());
      if (this.pendingTimed && this.settings.timed_choices && choices.length) {
        const [secs, idx] = this.pendingTimed;
        this._startTimer(secs, choices[Math.max(0, Math.min(choices.length - 1, idx))]);
      }
      this.pendingTimed = null;
      if (this.view.follow) requestAnimationFrame(() => this.view._followNow());
    }

    _startTimer(seconds, dflt) {
      const dur = Math.max(0.5, seconds);
      const deadline = performance.now() + dur * 1000;
      $("timerbar").classList.remove("hidden");
      const fill = $("timerbar").firstElementChild;
      this.timer = setInterval(() => {
        const left = deadline - performance.now();
        if (left <= 0) {
          this._pick(dflt);
          return;
        }
        fill.style.width = `${(100 * left) / (dur * 1000)}%`;
      }, 50);
    }

    _stopTimer() {
      if (this.timer) clearInterval(this.timer);
      this.timer = null;
      $("timerbar").classList.add("hidden");
    }

    _pick(c) {
      this._stopTimer();
      this.onChoice(c);
    }

    async onChoice(choice) {
      if (!this.session || this.ended) return;
      let answers = null;
      if (choice.kind === "file") {
        const theory = this.session.pendingTheory();
        if (theory) {
          answers = await theoryDialog(theory, new Set(Object.keys(this.session.state.evidence)));
          if (!answers) return;
        }
      }
      if (choice.kind === "radio" || choice.kind === "police") this.showTab("story");
      this.view.add(choice.truth, "echo");
      this.session.choose(choice, answers);
      this.step();
    }

    _showEnd() {
      this._clearChoices();
      $("choice-grid").appendChild(button("The end. Back to the title screen.", () => this.showTitle()));
    }

    // Android's back button: close a dialog, then the menu, then leave
    back() {
      if (dialogs.length) {
        dialogs[dialogs.length - 1].cancel();
        return "handled";
      }
      if (!$("crash").classList.contains("hidden")) return "handled";
      if (this.inGame) {
        if (this.tab !== "story" && !window.matchMedia("(min-width: 900px)").matches) this.showTab("story");
        else this.menu();
        return "handled";
      }
      return "exit";
    }
  }

  // ------------------------------------------------------------ boot
  async function boot() {
    $("loading").textContent = "Loading...";
    let json;
    try {
      json = await (await fetch("story/main.json")).text();
    } catch (e) {
      $("loading").textContent = "story/main.json is missing from this build.";
      return;
    }
    if (!window.inkjs) {
      $("loading").textContent = "The Ink runtime (js/ink.js) is missing from this build.";
      return;
    }
    if (document.fonts && document.fonts.load) {
      await Promise.all(["Courier Prime", "Caveat", "Cedarville Cursive", "Source Serif 4"].map((f) => document.fonts.load(`16px "${f}"`).catch(() => {})));
    }
    $("loading").textContent = "";
    const game = new Game(json);
    window.CF = { game, back: () => game.back() };
    await game.start();
  }

  window.CF = { back: () => "exit" };
  boot();
})();
