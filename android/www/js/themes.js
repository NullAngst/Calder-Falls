/* Midnight and the four stages it decays through. A port of
   calder_falls/themes/__init__.py: same colors, same effect strengths,
   same accessibility rules. The page reads the colors as CSS variables. */

(function (root) {
  "use strict";

  const ORDER = ["midnight", "fog", "bleed", "static", "dead_signal"];
  const FX = ["grain", "haze", "flicker", "swap", "scanlines", "split", "stutter", "drift"];

  function stage(name, bg, text, accent, fx) {
    const s = { name, bg, text, accent };
    for (const f of FX) s[f] = 0;
    s.grain = 0.05;
    return Object.assign(s, fx || {});
  }

  const STAGES = {
    midnight: stage("midnight", "#0B0F1A", "#C8CDD8", "#4A6FA5", { grain: 0.05 }),
    fog: stage("fog", "#1A1C1F", "#D0D0CC", "#8A9099", { grain: 0.06, haze: 0.5 }),
    bleed: stage("bleed", "#1A0D0A", "#D9C2B0", "#8C2F1B", { grain: 0.08, haze: 0.15, flicker: 0.35, swap: 0.35 }),
    static: stage("static", "#0E0E10", "#C4C4C4", "#5E8C8C", { grain: 0.1, scanlines: 0.35, split: 1.2, flicker: 0.15 }),
    dead_signal: stage("dead_signal", "#050505", "#9E9A94", "#7A1414", {
      grain: 0.12, scanlines: 0.2, split: 0.6, flicker: 0.2, stutter: 0.12, drift: 0.25,
    }),
  };

  function push(name, steps = 1) {
    const i = ORDER.indexOf(name);
    return ORDER[Math.min(ORDER.length - 1, (i < 0 ? 0 : i) + steps)];
  }

  function rgb(h) {
    h = h.replace("#", "");
    return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  }

  function hex(c) {
    return "#" + c.map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0")).join("").toUpperCase();
  }

  function mix(a, b, t) {
    const ca = rgb(a);
    const cb = rgb(b);
    return hex(ca.map((x, i) => x + (cb[i] - x) * t));
  }

  function interpolate(a, b, t) {
    if (t <= 0) return a;
    if (t >= 1) return b;
    const s = Object.assign({}, a, { name: b.name, bg: mix(a.bg, b.bg, t), text: mix(a.text, b.text, t), accent: mix(a.accent, b.accent, t) });
    for (const f of FX) s[f] = a[f] + (b[f] - a[f]) * t;
    return s;
  }

  // The flicker setting. off kills every flash and scanline, gentle halves them.
  function calm(s, flicker) {
    if (flicker === "off") return Object.assign({}, s, { flicker: 0, scanlines: 0, split: 0, swap: 0 });
    if (flicker === "gentle") return Object.assign({}, s, { flicker: s.flicker * 0.4, scanlines: s.scanlines * 0.6 });
    return s;
  }

  // QColor.lighter(factor): scale the HSV value, spill into saturation past white
  function lighter(h, factor) {
    let [r, g, b] = rgb(h).map((v) => v / 255);
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let hue = 0;
    const d = max - min;
    if (d) {
      if (max === r) hue = ((g - b) / d) % 6;
      else if (max === g) hue = (b - r) / d + 2;
      else hue = (r - g) / d + 4;
      hue *= 60;
      if (hue < 0) hue += 360;
    }
    let s = max ? d / max : 0;
    let v = max * factor;
    if (v > 1) {
      s = Math.max(0, s - (v - 1));
      v = 1;
    }
    const c = v * s;
    const x = c * (1 - Math.abs(((hue / 60) % 2) - 1));
    const m = v - c;
    const seg = Math.floor(hue / 60) % 6;
    [r, g, b] = [[c, x, 0], [x, c, 0], [0, c, x], [0, x, c], [x, 0, c], [c, 0, x]][seg];
    return hex([r + m, g + m, b + m].map((u) => u * 255));
  }

  // The same derived colors midnight.qss uses
  function cssVars(s) {
    return {
      "--bg": s.bg,
      "--text": s.text,
      "--accent": s.accent,
      "--panel": mix(s.bg, s.text, 0.05),
      "--panel2": mix(s.bg, s.text, 0.09),
      "--border": mix(s.bg, s.text, 0.16),
      "--dim": mix(s.bg, s.text, 0.55),
      "--hover": mix(s.bg, s.accent, 0.25),
      "--radio": lighter(s.accent, 1.5),
    };
  }

  root.CFThemes = { ORDER, STAGES, push, mix, interpolate, calm, cssVars, rgb, lighter };
})(typeof self !== "undefined" ? self : this);
