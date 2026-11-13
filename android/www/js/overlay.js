/* The painted layer over the whole screen: grain, fog, light flicker,
   scanlines and the dark CRT edges. A port of calder_falls/themes/overlay.py.
   Touches pass straight through it (pointer-events: none in the CSS). */

(function (root) {
  "use strict";

  function seeded(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function noiseTile(seed, size = 192) {
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const g = c.getContext("2d");
    const img = g.createImageData(size, size);
    const r = seeded(seed + 1);
    for (let i = 0; i < size * size; i++) {
      const v = r();
      if (v > 0.55) {
        const lum = 120 + Math.floor(r() * 136);
        const a = Math.floor(((v - 0.55) * 255) / 0.45 * 0.6);
        img.data.set([lum, lum, lum, a], i * 4);
      }
    }
    g.putImageData(img, 0, 0);
    return c;
  }

  function scanTile() {
    const c = document.createElement("canvas");
    c.width = 8;
    c.height = 3;
    const g = c.getContext("2d");
    g.fillStyle = "#000";
    g.fillRect(0, 2, 8, 1);
    return c;
  }

  class Overlay {
    constructor(canvas) {
      this.canvas = canvas;
      this.g = canvas.getContext("2d");
      this.stage = null;
      this.tiles = [0, 1, 2].map((i) => noiseTile(i));
      this.patterns = this.tiles.map((t) => this.g.createPattern(t, "repeat"));
      this.scan = this.g.createPattern(scanTile(), "repeat");
      this.frame = 0;
      this.flash = 0;
      this.fogSeed = [0, 1, 2].map(() => Math.random() * 100);
      this.rand = seeded(1986);
      this.mode = "gentle";
      this.grainXY = [0, 0];
      this.grainTile = 0;
      this.timer = null;
      this.dpr = 1;
      this.resize();
      window.addEventListener("resize", () => this.resize());
      this._retime();
    }

    resize() {
      // The grain is a pixel texture, so draw at CSS pixels, not device pixels
      this.canvas.width = Math.max(1, Math.floor(this.canvas.clientWidth));
      this.canvas.height = Math.max(1, Math.floor(this.canvas.clientHeight));
      this.paint();
    }

    setStage(s) {
      this.stage = s;
      this._retime();
      this.paint();
    }

    setMode(mode) {
      // off: a still picture, nothing on this layer moves, the fog included
      this.mode = mode;
      this.flash = 0;
      this.grainXY = [0, 0];
      this.grainTile = 0;
      this._retime();
      this.paint();
    }

    _retime() {
      const interval = this.mode === "full" ? 70 : this.mode === "gentle" ? 120 : 0;
      if (this.timer && this.timer.interval === interval) return;
      if (this.timer) clearInterval(this.timer.id);
      this.timer = null;
      if (interval) this.timer = { interval, id: setInterval(() => this._tick(), interval) };
    }

    _tick() {
      this.frame += 1;
      const s = this.stage;
      if (!s) return;
      if (this.mode === "full") {
        this.grainTile = this.frame % this.tiles.length;
        this.grainXY = [Math.floor(this.rand() * 192), Math.floor(this.rand() * 192)];
      } else if (this.mode === "gentle") {
        // one pixel at a time: the texture creeps, it never jumps
        this.grainXY = [this.frame % 192, Math.floor(this.frame / 2) % 192];
      }
      if (this.mode !== "off") {
        if (this.flash > 0) this.flash = Math.max(0, this.flash - 0.12);
        else if (s.flicker > 0 && this.rand() < s.flicker * 0.05) this.flash = 0.15 + 0.25 * s.flicker * this.rand();
      }
      this.paint();
    }

    paint() {
      const s = this.stage;
      const g = this.g;
      const w = this.canvas.width;
      const h = this.canvas.height;
      g.clearRect(0, 0, w, h);
      if (!s) return;

      if (s.haze > 0) {
        const t = this.mode === "off" ? 0 : this.frame * 0.004;
        this.fogSeed.forEach((seed, i) => {
          const cx = w * (0.5 + 0.45 * Math.sin(t * (0.6 + i * 0.2) + seed));
          const cy = h * (0.5 + 0.35 * Math.cos(t * (0.4 + i * 0.15) + seed));
          const rad = Math.max(w, h) * (0.45 + 0.1 * i);
          const grad = g.createRadialGradient(cx, cy, 0, cx, cy, rad);
          grad.addColorStop(0, `rgba(150,152,156,${(70 * s.haze) / 255})`);
          grad.addColorStop(1, "rgba(150,152,156,0)");
          g.fillStyle = grad;
          g.fillRect(0, 0, w, h);
        });
      }

      if (s.grain > 0) {
        g.save();
        g.globalAlpha = Math.min(1, s.grain * 1.6);
        g.translate(-this.grainXY[0], -this.grainXY[1]);
        g.fillStyle = this.patterns[this.grainTile];
        g.fillRect(0, 0, w + 192, h + 192);
        g.restore();
      }

      if (s.scanlines > 0) {
        g.save();
        g.globalAlpha = s.scanlines * 0.35;
        g.fillStyle = this.scan;
        g.fillRect(0, 0, w, h);
        g.restore();
      }

      // CRT edges: darker at the borders than the middle
      const r = Math.max(w, h) * 0.75;
      const edge = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, r);
      edge.addColorStop(0.55, "rgba(0,0,0,0)");
      edge.addColorStop(1, `rgba(0,0,0,${120 / 255})`);
      g.fillStyle = edge;
      g.fillRect(0, 0, w, h);

      if (this.flash > 0 && this.mode !== "off") {
        g.fillStyle = `rgba(0,0,0,${this.flash})`;
        g.fillRect(0, 0, w, h);
      }
    }
  }

  root.CFOverlay = Overlay;
  root.CFSeeded = seeded;
})(typeof self !== "undefined" ? self : this);
