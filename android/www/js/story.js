/* The Ink story and everything the game remembers around it.

   A port of calder_falls/story.py for the Android front end. Same tags, same
   choice prefixes, same state, same save layout. The runtime here is inkjs,
   reading the same story/build/main.json the desktop game reads.

   When story.py changes, this file changes with it. android/test/storytest.js
   plays the same scripted routes as calder_falls/storytest.py, so a mismatch
   shows up there.

   Runs in the WebView (window.CFStory) and in Node for the tests
   (module.exports). */

(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CFStory = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const THEME_STAGES = ["midnight", "fog", "bleed", "static", "dead_signal"];
  const ITEMS = ["flashlight", "notebook", "camera", "pistol", "radio", "keys"];
  const ENDINGS = ["dawn", "dead_air", "broadcast", "quiet_house", "test_pattern"];
  const TAGS = new Set([
    "chapter", "autosave", "clear", "time", "hint", "evidence", "note",
    "theory", "slot", "map", "item", "item_lose", "ending", "pause", "timed",
    "dark", "battery", "shadow", "theme", "warp", "fourth", "music",
    "music_layer", "music_detune", "music_tempo", "music_static", "music_ps2",
    "speaker",
  ]);
  const WARPS = new Set([
    "scrollback", "tabs_rename", "tabs_normal", "radio_drift", "radio_still",
    "title_count", "title_normal", "cursor_needle", "cursor_normal", "swap",
    "swap_clear", "flinch", "flinch_off",
  ]);
  const FOURTH = new Set(["crash", "corrupt_save", "howto"]);
  const TRANSCRIPT_KEEP = 80;

  class StoryError extends Error {}

  // Python's str.partition: always three parts
  function partition(s, sep) {
    const i = s.indexOf(sep);
    return i < 0 ? [s, "", ""] : [s.slice(0, i), sep, s.slice(i + sep.length)];
  }

  // ------------------------------------------------------------ parsing

  function parseTag(raw) {
    raw = raw.trim().replace(/^#+/, "").trim();
    const [name, , arg] = partition(raw, ":");
    return [name.trim(), arg.trim(), raw];
  }

  function parseChoice(index, raw) {
    let text = raw.trim();
    let kind = "normal";
    let freq = 0;
    if (text.startsWith("RADIO:")) {
      const [num, , rest] = partition(text.slice(6), ":");
      kind = "radio";
      freq = parseInt(num.trim(), 10);
      text = rest;
    } else if (text.startsWith("POLICE:")) {
      kind = "police";
      text = text.slice(7);
    } else if (text.startsWith("FILE:")) {
      kind = "file";
      text = text.slice(5);
    }
    text = text.trim();
    let hover = "";
    if (text.includes("@@")) {
      const [a, , b] = partition(text, "@@");
      text = a.trim();
      hover = b.trim();
    }
    return { index, text, hover, kind, freq, truth: hover || text };
  }

  function parseSlot(arg) {
    const parts = arg.split(";").map((p) => p.trim());
    const name = parts[0];
    const options = [];
    for (let o of parts.slice(1)) {
      let need = "";
      if (o.includes("@")) {
        const [a, , b] = partition(o, "@");
        o = a.trim();
        need = b.trim();
      }
      const correct = o.endsWith("*");
      options.push([o.replace(/\*+$/, "").trim(), correct, need]);
    }
    if (!options.some((o) => o[1])) throw new StoryError(`theory slot '${name}' has no correct option`);
    return { name, options };
  }

  // A theory is plain data: { id, title, slots: [{ name, options: [[text, correct, need]] }] }
  const Theory = {
    available(t, collected) {
      return t.slots.map((s) => [s.name, s.options.filter((o) => !o[2] || collected.has(o[2]))]);
    },
    score(t, answers) {
      let total = 0;
      for (const s of t.slots) {
        const pick = answers[s.name];
        for (const [text, correct] of s.options) if (text === pick && correct) total += 1;
      }
      return total;
    },
    correctAnswers(t) {
      const out = {};
      for (const s of t.slots) out[s.name] = s.options.find((o) => o[1])[0];
      return out;
    },
  };

  function newState(secondRun) {
    return {
      chapter_no: 0,
      chapter_title: "",
      theme: "midnight",
      evidence: {},
      evidence_order: [],
      notes: [],
      map_marks: [],
      items: [],
      hint: "Read everything. Then look again.",
      time: "--:--",
      tabs_renamed: false,
      radio_drift: false,
      title_count: "",
      cursor_needle: false,
      flinch: false,
      swaps: {},
      dark: false,
      battery_low: false,
      transcript: [],
      theory: {},
      howto_rewritten: false,
      ending: "",
      second_run: !!secondRun,
      speaker: "",
    };
  }

  function stamp() {
    const d = new Date();
    const p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }

  // ------------------------------------------------------------ session

  class Session {
    /* ink: the inkjs module. storyJson: main.json as text.
       store: { get(key) -> string|null, set(key, string) } for saves.
       audio: anything with applyTag(tag), or null. */
    constructor({ ink, storyJson, store, audio = null, strict = false }) {
      this.inkModule = ink;
      this.storyJson = storyJson.replace(/^﻿/, "");
      this.store = store;
      this.audio = audio;
      this.strict = strict;
      this.ink = null;
      this.state = newState(false);
      this.choices = [];
      this.ended = false;
      this.autosavePending = false;
      this.tagsSeen = new Set();
      this.unknownTags = [];
    }

    newGame(secondRun = false) {
      this.ink = new this.inkModule.Story(this.storyJson);
      this.state = newState(secondRun);
      this.setVar("second_run", !!secondRun);
      this.ended = false;
      this.choices = [];
    }

    // -------------------------------------------------- variables
    getVar(name, dflt = null) {
      try {
        if (this.ink.variablesState.GetVariableWithName(name) == null) return dflt;
        const v = this.ink.variablesState[name];
        return v == null ? dflt : v;
      } catch (e) {
        return dflt;
      }
    }

    setVar(name, value) {
      try {
        if (this.ink.variablesState.GetVariableWithName(name) == null) return false;
        this.ink.variablesState[name] = value;
      } catch (e) {
        return false;
      }
      return true;
    }

    get nerve() {
      return this.getVar("nerve", 10);
    }

    // -------------------------------------------------- running
    step() {
      const events = [];
      let guard = 0;
      while (this.ink.canContinue) {
        guard += 1;
        if (guard > 5000) throw new StoryError("story ran 5000 lines without a choice; probably a loop with no choice");
        const line = this.ink.Continue();
        for (const t of this.ink.currentTags || []) events.push(...this._tag(t));
        let text = line.trim();
        if (text) {
          text = this._applySwaps(text);
          this.state.transcript.push(text);
          if (this.state.transcript.length > TRANSCRIPT_KEEP) {
            this.state.transcript.splice(0, this.state.transcript.length - TRANSCRIPT_KEEP);
          }
          events.push(["text", text, this.state.speaker]);
          this.state.speaker = ""; // a speaker tag styles one line only
        }
      }
      this.choices = this.ink.currentChoices.map((c, i) => parseChoice(i, c.text));
      if (!this.choices.length) {
        this.ended = true;
        events.push(["end"]);
      } else if (this.autosavePending) {
        this.autosavePending = false;
        this.save("auto");
        events.push(["autosaved"]);
      }
      return events;
    }

    _applySwaps(text) {
      for (const [a, b] of Object.entries(this.state.swaps)) text = text.split(a).join(b);
      return text;
    }

    visibleChoices() {
      return this.choices.filter((c) => c.kind === "normal" || c.kind === "file");
    }

    radioOffers() {
      return this.choices.filter((c) => c.kind === "radio" || c.kind === "police");
    }

    pendingTheory() {
      const t = this.state.theory;
      return t && t.id !== undefined ? t : null;
    }

    choose(choice, answers = null) {
      if (choice.kind === "file") {
        const t = this.pendingTheory();
        const score = t ? Theory.score(t, answers || {}) : 0;
        this.setVar("theory_score", score);
        this.state.theory = {};
      }
      this.state.transcript.push("> " + choice.truth);
      this.ink.ChooseChoiceIndex(choice.index);
      this.choices = [];
    }

    // -------------------------------------------------- tags
    _tag(raw) {
      const [name, arg, full] = parseTag(raw);
      this.tagsSeen.add(name === "warp" || name === "fourth" ? `${name}:${arg.split(":")[0]}` : name);
      const st = this.state;
      const ev = [];
      if (!TAGS.has(name)) {
        this.unknownTags.push(full);
        if (this.strict) throw new StoryError(`unknown tag: # ${full}`);
        return ev;
      }
      if (name.startsWith("music")) {
        if (this.audio) {
          try {
            this.audio.applyTag(full);
          } catch (e) {
            if (this.strict) throw new StoryError(String(e.message || e));
          }
        }
        ev.push(["music", full]);
      } else if (name === "chapter") {
        const [num, , title] = partition(arg, ":");
        st.chapter_no = parseInt(num, 10);
        st.chapter_title = title.trim();
        this.autosavePending = true;
        ev.push(["chapter", st.chapter_no, st.chapter_title]);
      } else if (name === "autosave") {
        this.autosavePending = true;
      } else if (name === "clear") {
        st.transcript.length = 0;
        ev.push(["clear"]);
      } else if (name === "time") {
        st.time = arg;
        ev.push(["time", arg]);
      } else if (name === "hint") {
        st.hint = arg;
        ev.push(["hint", arg]);
      } else if (name === "speaker") {
        st.speaker = arg;
      } else if (name === "evidence") {
        const parts = arg.split(";").map((p) => p.trim());
        if (parts.length < 3) throw new StoryError(`evidence tag needs id;kind;title[;caption]: ${full}`);
        const [eid, kind, title] = parts;
        const caption = parts.length > 3 ? parts[3] : "";
        if (!(eid in st.evidence)) {
          st.evidence[eid] = { kind, title, caption };
          st.evidence_order.push(eid);
          ev.push(["evidence", eid]);
        }
      } else if (name === "note") {
        st.notes.push(arg);
        ev.push(["note", arg]);
      } else if (name === "theory") {
        const [tid, , title] = partition(arg, ";");
        st.theory = { id: tid.trim(), title: title.trim(), slots: [] };
      } else if (name === "slot") {
        if (!st.theory || st.theory.id === undefined) throw new StoryError(`# slot with no # theory before it: ${full}`);
        st.theory.slots.push(parseSlot(arg));
      } else if (name === "map") {
        if (!st.map_marks.includes(arg)) st.map_marks.push(arg);
        ev.push(["map", arg]);
      } else if (name === "item") {
        if (!ITEMS.includes(arg)) throw new StoryError(`unknown item: ${arg}`);
        if (!st.items.includes(arg)) st.items.push(arg);
        ev.push(["items"]);
      } else if (name === "item_lose") {
        const i = st.items.indexOf(arg);
        if (i >= 0) st.items.splice(i, 1);
        ev.push(["items"]);
      } else if (name === "ending") {
        if (!ENDINGS.includes(arg)) throw new StoryError(`unknown ending: ${arg}`);
        st.ending = arg;
        ev.push(["ending", arg]);
      } else if (name === "pause") {
        ev.push(["pause", parseFloat(arg || "1")]);
      } else if (name === "timed") {
        const [secs, , idx] = partition(arg, ":");
        ev.push(["timed", parseFloat(secs), parseInt(idx || "0", 10)]);
      } else if (name === "dark") {
        st.dark = arg === "on";
        ev.push(["dark", st.dark]);
      } else if (name === "battery") {
        st.battery_low = arg === "low";
        ev.push(["battery", st.battery_low]);
      } else if (name === "shadow") {
        ev.push(["shadow", arg]);
      } else if (name === "theme") {
        if (!THEME_STAGES.includes(arg)) throw new StoryError(`unknown theme stage: ${arg}`);
        st.theme = arg;
        ev.push(["theme", arg]);
      } else if (name === "warp") {
        const [kind, , rest] = partition(arg, ":");
        if (!WARPS.has(kind)) throw new StoryError(`unknown warp: ${kind}`);
        if (kind === "tabs_rename") st.tabs_renamed = true;
        else if (kind === "tabs_normal") st.tabs_renamed = false;
        else if (kind === "radio_drift") st.radio_drift = true;
        else if (kind === "radio_still") st.radio_drift = false;
        else if (kind === "title_count") st.title_count = rest;
        else if (kind === "title_normal") st.title_count = "";
        else if (kind === "cursor_needle") st.cursor_needle = true;
        else if (kind === "cursor_normal") st.cursor_needle = false;
        else if (kind === "flinch") st.flinch = true;
        else if (kind === "flinch_off") st.flinch = false;
        else if (kind === "swap") {
          const [a, , b] = partition(rest, "=>");
          st.swaps[a.trim()] = b.trim();
        } else if (kind === "swap_clear") st.swaps = {};
        else if (kind === "scrollback") {
          let [a, , b] = partition(rest, "=>");
          a = a.trim();
          b = b.trim();
          for (let i = st.transcript.length - 1; i >= 0; i--) {
            if (st.transcript[i].includes(a)) {
              st.transcript[i] = st.transcript[i].split(a).join(b);
              break;
            }
          }
          ev.push(["warp", "scrollback", [a, b]]);
          return ev;
        }
        ev.push(["warp", kind, rest]);
      } else if (name === "fourth") {
        if (!FOURTH.has(arg)) throw new StoryError(`unknown fourth-wall effect: ${arg}`);
        if (arg === "howto") st.howto_rewritten = true;
        ev.push(["fourth", arg]);
      }
      return ev;
    }

    // -------------------------------------------------- saves
    // Same two pieces as the desktop: Ink's own state JSON, and a small JSON
    // of everything around it. Kept in the WebView's storage, not files.
    save(slot) {
      this.store.set(`slot-${slot}.ink`, this.ink.state.toJson());
      const meta = {
        saved: stamp(),
        chapter_no: this.state.chapter_no,
        chapter_title: this.state.chapter_title,
        state: JSON.parse(JSON.stringify(this.state)),
      };
      this.store.set(`slot-${slot}`, JSON.stringify(meta));
    }

    slotInfo(slot) {
      const raw = this.store.get(`slot-${slot}`);
      if (!raw) return null;
      try {
        return JSON.parse(raw);
      } catch (e) {
        return null;
      }
    }

    load(slot) {
      const meta = this.slotInfo(slot);
      const saved = this.store.get(`slot-${slot}.ink`);
      if (meta == null || !saved) throw new StoryError(`save slot ${slot} is empty or damaged`);
      this.ink = new this.inkModule.Story(this.storyJson);
      this.ink.state.LoadJson(saved);
      const st = newState(false);
      for (const [k, v] of Object.entries(meta.state || {})) if (k in st) st[k] = v;
      this.state = st;
      this.ended = false;
      this.choices = this.ink.currentChoices.map((c, i) => parseChoice(i, c.text));
      return meta;
    }
  }

  return {
    Session, StoryError, Theory, parseTag, parseChoice, parseSlot,
    THEME_STAGES, ITEMS, ENDINGS, TAGS, WARPS, FOURTH,
  };
});
