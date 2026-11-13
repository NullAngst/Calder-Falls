#!/usr/bin/env node
/* Headless story checks for the Android front end. Exit code 0 means every
   check passed.

       node android/test/storytest.js [path/to/ink.js]

   The same checks as calder_falls/storytest.py, run against android/www/js/story.js
   and inkjs instead of story.py and bink:

   1. Scripted routes reach all five endings.
   2. On every route, each theory's right answers were findable in time.
   3. Wandering walks that file wrong theories still reach an ending.
   4. A save loaded into a fresh session has the same choices and variables.
   5. Every music tag the routes hit is one the web player understands.

   inkjs comes from android/web-out/assets/www/js/ink.js after build-web.sh runs,
   or from the path given, or from require("inkjs"). */

"use strict";

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const CFStory = require(path.join(root, "android", "www", "js", "story.js"));
const MusicTags = require(path.join(root, "android", "www", "js", "musictags.js"));

function loadInk() {
  const candidates = [process.argv[2], path.join(root, "android", "web-out", "assets", "www", "js", "ink.js")];
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return require(path.resolve(c));
  }
  return require("inkjs");
}

const ink = loadInk();
const storyJson = fs.readFileSync(path.join(root, "story", "build", "main.json"), "utf8");
const FAILS = [];

function check(ok, what) {
  console.log((ok ? "  ok   " : "  FAIL ") + what);
  if (!ok) FAILS.push(what);
}

// Seeded random, so a failing walk can be replayed
function rng(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function memoryStore() {
  const m = new Map();
  return { get: (k) => (m.has(k) ? m.get(k) : null), set: (k, v) => m.set(k, v) };
}

// Collects music tags and checks the web player can parse each one
class TagAudio {
  constructor() {
    this.bad = [];
    this.state = MusicTags.initialState();
  }
  applyTag(tag) {
    try {
      MusicTags.apply(this.state, tag);
    } catch (e) {
      this.bad.push(`${tag}: ${e.message}`);
    }
  }
}

class Player {
  constructor(seed, { presets = {}, final = null, wrong = 0, second_run = false, take_radio = 0.5, store = null } = {}) {
    this.rand = rng(seed);
    this.presets = presets;
    this.final = final;
    this.wrong = wrong;
    this.secondRun = second_run;
    this.takeRadio = take_radio;
    this.audio = new TagAudio();
    this.s = new CFStory.Session({ ink, storyJson, store: store || memoryStore(), audio: this.audio, strict: true });
    this.used = new Map();
    this.unfindable = [];
    this.stalled = 0;
  }

  start() {
    this.s.newGame(this.secondRun);
    for (const [k, v] of Object.entries(this.presets)) {
      if (!this.s.setVar(k, v)) throw new CFStory.StoryError(`route preset names an unknown variable: ${k}`);
    }
  }

  pick() {
    const ch = this.s.choices;
    if (this.final) {
      const c = ch.find((c) => c.truth.includes(this.final));
      if (c) return c;
    }
    if (this.secondRun) {
      const c = ch.find((c) => c.truth.includes("Stay on 1610"));
      if (c) return c;
    }
    const t = this.s.pendingTheory();
    let missing = [];
    if (t) {
      const have = new Set(Object.keys(this.s.state.evidence));
      for (const sl of t.slots) for (const [, ok, need] of sl.options) if (ok && need && !have.has(need)) missing.push(need);
    }
    if (missing.length) {
      this.stalled += 1;
      if (this.stalled > 400) {
        this.unfindable.push(`${t.id}: never found ${[...new Set(missing)].sort().join(", ")}`);
        this.stalled = 0;
        missing = [];
      }
    } else {
      this.stalled = 0;
    }
    const key = (c) => {
      let w = this.used.get(c.truth) || 0;
      if (missing.length && c.kind === "file") w += 1000;
      if (missing.length && (c.truth.startsWith("Leave the house") || c.truth.startsWith("Go round again"))) w -= 0.5;
      if ((c.kind === "radio" || c.kind === "police") && this.rand() > this.takeRadio) w += 3;
      if (["Walk to the kitchen", "Go back out", "Go round again"].some((p) => c.truth.startsWith(p))) w += 0.6;
      if (["Keep looking", "Not yet"].some((p) => c.truth.startsWith(p))) w += 4;
      if (c.kind === "file") w -= 0.2;
      return [w, this.rand()];
    };
    let best = null;
    let bestKey = null;
    for (const c of ch) {
      const k = key(c);
      if (!best || k[0] < bestKey[0] || (k[0] === bestKey[0] && k[1] < bestKey[1])) {
        best = c;
        bestKey = k;
      }
    }
    return best;
  }

  answers() {
    const t = this.s.pendingTheory();
    if (!t) return null;
    if (this.rand() < this.wrong) {
      const out = {};
      for (const s of t.slots) out[s.name] = s.options[s.options.length - 1][0];
      return out;
    }
    return CFStory.Theory.correctAnswers(t);
  }

  play(limit = 6000, saveAt = null, onSave = null) {
    this.start();
    let steps = 0;
    for (;;) {
      this.s.step();
      if (this.s.ended) return steps;
      steps += 1;
      if (steps > limit) throw new CFStory.StoryError(`no ending after ${limit} choices (chapter ${this.s.state.chapter_no})`);
      if (saveAt !== null && steps === saveAt && onSave) onSave(this);
      const c = this.pick();
      this.used.set(c.truth, (this.used.get(c.truth) || 0) + 1);
      if (c.kind === "file" || ["Walk to the kitchen", "Go back out", "Drive"].some((p) => c.truth.startsWith(p))) {
        for (const k of [...this.used.keys()]) if (!k.startsWith("Smoke") && !k.startsWith("Sit")) this.used.delete(k);
      }
      this.s.choose(c, c.kind === "file" ? this.answers() : null);
    }
  }
}

const ROUTES = [
  ["dawn", { presets: { resolve: 40, mercy: 40, attunement: -40 }, final: "Hold on to the people" }],
  ["dead_air", { presets: { resolve: 20, attunement: -200 }, final: "Refuse them" }],
  ["broadcast", { presets: { attunement: 200, resolve: 5, mercy: -100 }, final: "Let them in" }],
  ["quiet_house", { presets: { resolve: -300 }, final: "Try to hold on" }],
  ["test_pattern", { second_run: true }],
];

function routes() {
  console.log("routes to every ending");
  const seen = new Set();
  for (const [want, kw] of ROUTES) {
    const p = new Player([...want].reduce((a, c) => a + c.charCodeAt(0), 0), kw);
    try {
      const steps = p.play();
      const got = p.s.state.ending;
      check(got === want, `route '${want}' reaches the ${got || "no"} ending in ${steps} choices`);
      check(!p.s.unknownTags.length, `route '${want}': no unknown tags`);
      const uniq = [...new Set(p.unfindable)].sort();
      for (const u of uniq) console.log("    " + u);
      check(!uniq.length, `route '${want}': every right theory answer can be found before filing`);
      for (const b of p.audio.bad) console.log("    " + b);
      check(!p.audio.bad.length, `route '${want}': the web player understands every music tag`);
      for (const t of p.s.tagsSeen) seen.add(t);
    } catch (e) {
      check(false, `route '${want}': ${e.message}`);
    }
  }
  console.log(`    tags exercised: ${seen.size}`);
  return seen;
}

function wander(seeds = 6) {
  console.log("wandering walks");
  for (let seed = 0; seed < seeds; seed++) {
    const p = new Player(1000 + seed, { wrong: 0.35, take_radio: 0.8 });
    try {
      const steps = p.play(9000);
      check(!!p.s.state.ending, `walk ${seed} ends (${p.s.state.ending}) after ${steps} choices`);
    } catch (e) {
      check(false, `walk ${seed}: ${e.message}`);
    }
  }
}

function saveLoad() {
  console.log("save and load");
  const store = memoryStore();
  const result = {};
  const snap = (player) => {
    player.s.save("smoke");
    const fresh = new CFStory.Session({ ink, storyJson, store, strict: true });
    fresh.load("smoke");
    const keys = ["nerve", "resolve", "attunement", "mercy", "evidence", "loop"];
    const vars = (s) => JSON.stringify(keys.map((k) => s.getVar(k)));
    result.choices = [fresh.choices.map((c) => c.text).join("|"), player.s.choices.map((c) => c.text).join("|")];
    result.vars = [vars(fresh), vars(player.s)];
    result.state = [fresh.state.chapter_title, player.s.state.chapter_title];
  };
  const p = new Player(7, { presets: { resolve: 40, mercy: 40 }, final: "Hold on to the people", store });
  p.play(6000, 120, snap);
  const same = (pair) => !!pair && pair[0] === pair[1];
  check(same(result.choices), "loaded save has the same choices");
  check(same(result.vars), "loaded save has the same variables");
  check(same(result.state), "loaded save is in the same chapter");
}

function main() {
  const seen = routes();
  wander();
  saveLoad();
  const warps = [...seen].filter((t) => t.startsWith("warp:"));
  check(warps.length >= 6, `routes exercise the window tricks (${warps.length} warp kinds)`);
  console.log();
  if (FAILS.length) {
    console.log(`${FAILS.length} check(s) failed:`);
    for (const f of FAILS) console.log(`  ${f}`);
    process.exit(1);
  }
  console.log("all Android story checks passed");
}

main();
