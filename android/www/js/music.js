/* The Android music player.

   The desktop sequences MIDI live through FluidSynth. Here every reachable
   combination of cue, layers, tempo and detune was rendered ahead of time
   by calder_falls/audio/variants.py, and this player switches between those
   files the way the desktop engine changes a cue in place:

   - a new cue fades the old one out over 0.8 s, holds 0.6 s of silence,
     then starts from the top, like AudioEngine._drain
   - a layer, tempo or detune change crossfades to the matching file at the
     same point in the cue over 0.15 s, like the engine's layer ramp
   - static bleed runs live, in static-worklet.js

   A state no walk reached falls back to the closest file for that cue, with
   playbackRate and detune making up the tempo and pitch difference. */

(function (root) {
  "use strict";

  const FADE_OUT = 0.8;
  const HOLD = 0.6;
  const XFADE = 0.15;

  class MusicPlayer {
    constructor(base) {
      this.base = base; // "music/"
      this.ctx = null;
      this.manifest = null;
      this.state = CFMusicTags.initialState();
      this.volume = 0.8;
      this.cache = new Map(); // file -> Promise<AudioBuffer>
      this.cacheOrder = [];
      this.voice = null; // { variant, src, gain, startedAt, offset, rate }
      this.bus = null;
      this.master = null;
      this.staticNode = null;
      this.token = 0; // bumps on every cue change so late loads drop out
      this.failed = "";
    }

    // ------------------------------------------------------------ setup
    async init() {
      if (this.ctx) return;
      try {
        const r = await fetch(this.base + "manifest.json");
        this.manifest = await r.json();
      } catch (e) {
        this.failed = "no music: manifest.json missing";
        return;
      }
      const Ctx = window.AudioContext || window.webkitAudioContext;
      try {
        this.ctx = new Ctx({ sampleRate: this.manifest.rate, latencyHint: "playback" });
      } catch (e) {
        this.ctx = new Ctx({ latencyHint: "playback" });
      }
      this.master = this.ctx.createGain();
      this.master.gain.value = this.volume;
      this.bus = this.ctx.createGain();
      let tail = this.bus;
      try {
        await this.ctx.audioWorklet.addModule("js/static-worklet.js");
        const rates = Object.keys(this.manifest.static).map(Number);
        const near = rates.reduce((a, b) => (Math.abs(b - this.ctx.sampleRate) < Math.abs(a - this.ctx.sampleRate) ? b : a));
        this.staticNode = new AudioWorkletNode(this.ctx, "static-bleed", {
          numberOfInputs: 1,
          numberOfOutputs: 1,
          outputChannelCount: [2],
          processorOptions: { filters: this.manifest.static[String(near)] },
        });
        this.bus.connect(this.staticNode);
        tail = this.staticNode;
      } catch (e) {
        // No worklet: music plays clean, static bleed is the only loss
        this.staticNode = null;
      }
      tail.connect(this.master);
      this.master.connect(this.ctx.destination);
    }

    resume() {
      if (this.ctx && this.ctx.state !== "running") this.ctx.resume().catch(() => {});
    }

    setVolume(v) {
      this.volume = Math.max(0, Math.min(1, v));
      if (this.master) this.master.gain.setTargetAtTime(this.volume, this.ctx.currentTime, 0.05);
    }

    // Pause everything while the app is in the background
    suspend() {
      if (this.ctx && this.ctx.state === "running") this.ctx.suspend().catch(() => {});
    }

    // ------------------------------------------------------------ tags
    applyTag(tag) {
      const what = CFMusicTags.apply(this.state, tag);
      if (!this.ctx) return;
      if (what === "play") this._changeCue();
      else if (what === "stop") this._stop(FADE_OUT);
      else if (what === "mix") this._remix();
      else if (what === "static") this._static();
    }

    // What the title screen does before it plays the theme
    title() {
      CFMusicTags.titleState(this.state);
      this._static();
      this.applyTag("music:calder_falls");
    }

    // ------------------------------------------------------------ files
    _variantFor(state) {
      const all = this.manifest.variants.filter((v) => v.cue === state.cue);
      if (!all.length) return null;
      const want = new Set(state.off);
      let best = null;
      let bestScore = Infinity;
      for (const v of all) {
        const have = new Set(v.off);
        let miss = 0;
        for (const l of CFMusicTags.LAYERS) if (want.has(l) !== have.has(l)) miss += 1;
        const score = miss * 10 + Math.abs(v.tempo - state.tempo) * 20 + Math.abs(v.detune - state.detune) / 10;
        if (score < bestScore) {
          best = v;
          bestScore = score;
        }
      }
      return best;
    }

    _buffer(file) {
      if (!this.cache.has(file)) {
        const p = fetch(this.base + file)
          .then((r) => r.arrayBuffer())
          .then((data) => this.ctx.decodeAudioData(data));
        this.cache.set(file, p);
        this.cacheOrder.push(file);
        // Decoded audio is big; keep the last few only
        while (this.cacheOrder.length > 4) this.cache.delete(this.cacheOrder.shift());
        p.catch(() => this.cache.delete(file));
      }
      return this.cache.get(file);
    }

    // ------------------------------------------------------------ voices
    _position() {
      // Where the current voice is, in seconds of the cue at its own tempo
      const v = this.voice;
      if (!v) return 0;
      let t = v.offset + (this.ctx.currentTime - v.startedAt) * v.rate;
      if (v.variant.loop) t %= v.variant.seconds;
      return t * v.variant.tempo;
    }

    _start(variant, buffer, cuePos, fadeIn) {
      const ctx = this.ctx;
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.loop = variant.loop;
      const rate = this.state.tempo / variant.tempo;
      src.playbackRate.value = rate;
      src.detune.value = this.state.detune - variant.detune;
      const g = ctx.createGain();
      src.connect(g);
      g.connect(this.bus);
      const now = ctx.currentTime;
      g.gain.setValueAtTime(fadeIn ? 0 : 1, now);
      if (fadeIn) g.gain.linearRampToValueAtTime(1, now + fadeIn);
      const offset = Math.min(Math.max(0, cuePos / variant.tempo), Math.max(0, buffer.duration - 0.01));
      src.start(now, offset);
      const voice = { variant, src, gain: g, startedAt: now, offset, rate };
      src.onended = () => {
        if (this.voice === voice) this.voice = null;
      };
      return voice;
    }

    _kill(voice, seconds) {
      if (!voice) return;
      const now = this.ctx.currentTime;
      voice.gain.gain.cancelScheduledValues(now);
      voice.gain.gain.setValueAtTime(voice.gain.gain.value, now);
      voice.gain.gain.linearRampToValueAtTime(0, now + seconds);
      try {
        voice.src.stop(now + seconds + 0.02);
      } catch (e) {
        /* already stopped */
      }
    }

    _stop(fade) {
      this.token += 1;
      this._kill(this.voice, fade);
      this.voice = null;
    }

    async _changeCue() {
      const token = ++this.token;
      const wait = this.voice ? FADE_OUT + HOLD : 0;
      this._kill(this.voice, FADE_OUT);
      this.voice = null;
      const variant = this._variantFor(this.state);
      if (!variant) return;
      const started = this.ctx.currentTime;
      let buffer;
      try {
        buffer = await this._buffer(variant.file);
      } catch (e) {
        return;
      }
      const left = wait - (this.ctx.currentTime - started);
      if (left > 0) await new Promise((r) => setTimeout(r, left * 1000));
      if (token !== this.token) return;
      // The state may have moved on while the file loaded
      const now = this._variantFor(this.state);
      if (now && now.file !== variant.file) {
        try {
          buffer = await this._buffer(now.file);
        } catch (e) {
          return;
        }
        if (token !== this.token) return;
        this.voice = this._start(now, buffer, 0, 0.01);
      } else {
        this.voice = this._start(variant, buffer, 0, 0.01);
      }
    }

    async _remix() {
      if (!this.state.cue) return;
      const old = this.voice;
      const variant = this._variantFor(this.state);
      if (!variant) return;
      if (old && old.variant.file === variant.file) {
        // Same file: only the tempo or pitch make-up changes
        const pos = this._position();
        const rate = this.state.tempo / variant.tempo;
        const now = this.ctx.currentTime;
        old.offset = pos / variant.tempo;
        old.startedAt = now;
        old.rate = rate;
        old.src.playbackRate.setTargetAtTime(rate, now, 0.05);
        old.src.detune.setTargetAtTime(this.state.detune - variant.detune, now, 0.05);
        return;
      }
      if (!old) return; // between cues: _changeCue picks up the new state
      const token = this.token;
      let buffer;
      try {
        buffer = await this._buffer(variant.file);
      } catch (e) {
        return;
      }
      if (token !== this.token || this.voice !== old) return;
      const pos = this._position();
      this._kill(old, XFADE);
      this.voice = this._start(variant, buffer, pos, XFADE);
    }

    _static() {
      if (!this.staticNode) return;
      this.staticNode.parameters.get("amount").setValueAtTime(this.state.static, this.ctx.currentTime);
    }
  }

  root.CFMusic = MusicPlayer;
})(typeof self !== "undefined" ? self : this);
