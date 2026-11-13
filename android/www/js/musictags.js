/* Music tags as plain state, the same rules as AudioEngine.apply_tag in
   calder_falls/audio/engine.py. The web player (music.js) acts on what
   changed; the Node story test runs every tag through here to prove the
   player understands it. */

(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CFMusicTags = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const LAYERS = ["drums", "bass", "lead", "pad", "noise"];
  const CUES = [
    "calder_falls", "cobb_road", "june", "the_hush", "substation", "listening_room",
    "fellowship", "the_spindle", "precentor", "water_tower", "mill_floor", "dawn",
  ];

  function initialState() {
    return { cue: null, off: [], tempo: 1.0, detune: 0.0, static: 0.0, ps2: true };
  }

  // What the title screen does: everything on, straight tempo, no static
  function titleState(state) {
    state.off = [];
    state.tempo = 1.0;
    state.detune = 0.0;
    state.static = 0.0;
    return state;
  }

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  function num(value, tag) {
    const v = parseFloat(value);
    if (!isFinite(v) || String(value).trim() === "") throw new Error(`bad music tag '# ${tag}'`);
    return v;
  }

  /* Returns what changed: "play", "stop", "mix" (layers, tempo, detune)
     or "static". Throws on a malformed tag, like the desktop engine. */
  function apply(state, tag) {
    tag = tag.trim().replace(/^#+/, "").trim();
    const i = tag.indexOf(":");
    const key = (i < 0 ? tag : tag.slice(0, i)).trim();
    const value = (i < 0 ? "" : tag.slice(i + 1)).trim();
    if (key === "music") {
      if (value === "stop") {
        state.cue = null;
        return "stop";
      }
      if (!CUES.includes(value)) throw new Error(`unknown music cue: ${value}`);
      state.cue = value;
      return "play";
    }
    if (key === "music_layer") {
      const parts = value.split(/\s+/);
      if (parts.length !== 2 || !LAYERS.includes(parts[0]) || !["on", "off"].includes(parts[1])) {
        throw new Error(`bad music tag '# ${tag}'`);
      }
      const off = new Set(state.off);
      if (parts[1] === "on") off.delete(parts[0]);
      else off.add(parts[0]);
      state.off = LAYERS.filter((l) => off.has(l));
      return "mix";
    }
    if (key === "music_tempo") {
      state.tempo = clamp(num(value, tag), 0.25, 2.0);
      return "mix";
    }
    if (key === "music_detune") {
      state.detune = clamp(num(value, tag), -200, 200);
      return "mix";
    }
    if (key === "music_static") {
      state.static = clamp(num(value, tag), 0, 1);
      return "static";
    }
    if (key === "music_ps2") {
      if (!["on", "off"].includes(value)) throw new Error(`bad music tag '# ${tag}'`);
      // The renders have the PS2 filter baked in, as the desktop default.
      // The story never turns it off, so the web player ignores this one.
      state.ps2 = value === "on";
      return "none";
    }
    throw new Error(`bad music tag '# ${tag}'`);
  }

  return { LAYERS, CUES, initialState, titleState, apply };
});
