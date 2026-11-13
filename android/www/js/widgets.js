/* The painted pieces: Brennick's LCD watch, the Nerve meter, the spiral
   notebook, Polaroids on a corkboard, the county map, the AM dial and the
   police knob. Ports of calder_falls/ui/widgets.py and ui/sidebar.py, drawn
   on canvas with the same shapes and colors. */

(function (root) {
  "use strict";

  const HAND = "Caveat";
  const LEDGER_HAND = "Cedarville Cursive";

  // Size a canvas to its CSS box at the screen's pixel density
  function fit(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(1, canvas.clientWidth);
    const h = Math.max(1, canvas.clientHeight);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    const g = canvas.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, h);
    return [g, w, h];
  }

  // Seeded random from a string, so a Polaroid always tilts the same way
  function strRand(s) {
    let h = 2166136261;
    for (const ch of String(s)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
    return CFSeeded(h >>> 0);
  }

  function rgba(hex, a) {
    const [r, g, b] = CFThemes.rgb(hex);
    return `rgba(${r},${g},${b},${a})`;
  }

  function shade(hex, f) {
    // QColor.lighter/darker, near enough: scale the channels
    const c = CFThemes.rgb(hex).map((v) => Math.max(0, Math.min(255, v * f)));
    return `rgb(${c.map(Math.round).join(",")})`;
  }

  // ---------------------------------------------------------------- watch
  const SEGMENTS = {
    0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd",
    6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcdfg", "-": "g", " ": "",
  };

  class Watch {
    constructor(canvas) {
      this.canvas = canvas;
      this.text = "--:--";
      this.blink = true;
      setInterval(() => {
        this.blink = !this.blink;
        this.paint();
      }, 1000);
    }
    set(text) {
      this.text = text && text.length === 5 ? text : "--:--";
      this.paint();
    }
    paint() {
      const [g, W, H] = fit(this.canvas);
      const k = H / 38;
      g.save();
      g.scale(k, k);
      g.fillStyle = "#1A1A1A";
      g.strokeStyle = "#3A3A3A";
      g.lineWidth = 2;
      g.beginPath();
      g.roundRect(1, 1, 116, 36, 6);
      g.fill();
      g.stroke();
      g.fillStyle = "#7C8A6A";
      g.fillRect(7, 6, 104, 26);
      const on = "#1E2418";
      const off = "rgba(30,36,24,0.11)";
      const dw = 16;
      const dh = 22;
      let x = 15;
      const y = 9;
      g.lineCap = "butt";
      for (const ch of this.text) {
        if (ch === ":") {
          if (this.blink) {
            g.fillStyle = on;
            g.fillRect(x + 1, y + 6, 3, 3);
            g.fillRect(x + 1, y + 14, 3, 3);
          }
          x += 8;
          continue;
        }
        const segs = SEGMENTS[ch] || "";
        const P = {
          a: [[2, 0], [dw - 2, 0]], b: [[dw, 2], [dw, dh / 2 - 1]], c: [[dw, dh / 2 + 1], [dw, dh - 2]],
          d: [[2, dh], [dw - 2, dh]], e: [[0, dh / 2 + 1], [0, dh - 2]], f: [[0, 2], [0, dh / 2 - 1]],
          g: [[2, dh / 2], [dw - 2, dh / 2]],
        };
        for (const s of "abcdefg") {
          g.strokeStyle = segs.includes(s) ? on : off;
          g.lineWidth = 3;
          g.beginPath();
          g.moveTo(x + P[s][0][0] * 0.8, y + P[s][0][1]);
          g.lineTo(x + P[s][1][0] * 0.8, y + P[s][1][1]);
          g.stroke();
        }
        x += dw * 0.8 + 6;
      }
      g.restore();
      void W;
    }
  }

  // ---------------------------------------------------------------- nerve
  class Nerve {
    constructor(canvas) {
      this.canvas = canvas;
      this.value = 10;
      this.accent = "#4A6FA5";
    }
    set(v, accent) {
      this.value = Math.max(0, Math.min(10, Math.trunc(v)));
      if (accent) this.accent = accent;
      this.paint();
    }
    paint() {
      const [g, W, H] = fit(this.canvas);
      const k = H / 30;
      g.save();
      g.scale(k, k);
      g.fillStyle = "rgba(200,200,200,0.6)";
      g.font = "11px 'Courier Prime', monospace";
      g.textBaseline = "middle";
      g.fillText("NERVE", 0, 15);
      for (let i = 0; i < 10; i++) {
        let c = i < this.value ? this.accent : "rgba(255,255,255,0.1)";
        if (this.value <= 3 && i < this.value) c = "#A33A2A";
        g.fillStyle = c;
        g.fillRect(50 + i * 9, 8, 6, 14);
      }
      g.restore();
      void W;
    }
  }

  // ---------------------------------------------------------------- notebook
  class Notebook {
    constructor(canvas) {
      this.canvas = canvas;
      this.lines = [];
      this.page = 0;
      this.ledger = false;
      this.perPage = 16;
    }
    wrapped() {
      const out = [];
      const width = 30;
      for (const entry of this.lines) {
        let cur = "";
        for (const w of entry.split(/\s+/).filter(Boolean)) {
          if (cur && cur.length + w.length + 1 > width) {
            out.push(cur);
            cur = w;
          } else cur = (cur + " " + w).trim();
        }
        if (cur) out.push(cur);
        out.push("");
      }
      return out;
    }
    pages() {
      return Math.max(1, Math.ceil(this.wrapped().length / this.perPage));
    }
    setLines(lines) {
      this.lines = lines.slice();
      this.page = this.pages() - 1;
    }
    flip(d) {
      this.page = Math.max(0, Math.min(this.pages() - 1, this.page + d));
    }
    paint() {
      const [g, W, H] = fit(this.canvas);
      // The desktop pad holds 16 lines. A tall phone gets more lines per
      // page instead of 16 lines spread thin.
      const per = Math.max(16, Math.floor((H - 56) / 30));
      if (per !== this.perPage) {
        this.perPage = per;
        this.page = Math.min(this.page, this.pages() - 1);
      }
      const r = { l: 8, t: 18, w: W - 16, h: H - 26 };
      g.fillStyle = this.ledger ? "#D8CFB4" : "#E9E2CF";
      g.fillRect(r.l, r.t, r.w, r.h);
      g.strokeStyle = "#6B6B6B";
      g.lineWidth = 2;
      for (let x = r.l + 14; x < r.l + r.w - 8; x += 18) {
        g.beginPath();
        g.ellipse(x + 4, r.t - 1, 4, 9, 0, 0, Math.PI * 2);
        g.stroke();
      }
      const lh = (r.h - 30) / this.perPage;
      g.strokeStyle = "rgba(110,140,180,0.35)";
      g.lineWidth = 1;
      for (let i = 0; i <= this.perPage; i++) {
        const y = r.t + 26 + i * lh;
        g.beginPath();
        g.moveTo(r.l, y);
        g.lineTo(r.l + r.w, y);
        g.stroke();
      }
      g.strokeStyle = "rgba(190,70,70,0.47)";
      g.beginPath();
      g.moveTo(r.l + 34, r.t);
      g.lineTo(r.l + 34, r.t + r.h);
      g.stroke();
      const size = Math.min(this.ledger ? 20 : 23, lh * 0.95);
      g.font = `${size}px '${this.ledger ? LEDGER_HAND : HAND}', cursive`;
      g.fillStyle = this.ledger ? "#3A1F14" : "#1F2A44";
      g.textBaseline = "alphabetic";
      const lines = this.wrapped().slice(this.page * this.perPage, (this.page + 1) * this.perPage);
      lines.forEach((text, i) => g.fillText(text, r.l + 42, r.t + 26 + (i + 1) * lh - 5, r.w - 48));
      if (!this.lines.length) {
        g.fillStyle = "rgba(31,42,68,0.47)";
        g.fillText("Nothing yet.", r.l + 42, r.t + 26 + lh - 5);
      }
    }
  }

  // ---------------------------------------------------------------- evidence
  function paintPolaroid(canvas, eid, info) {
    const [g, W, H] = fit(canvas);
    const rand = strRand(eid);
    const tilt = (rand() * 8 - 4) * (Math.PI / 180);
    g.save();
    g.translate(W / 2, H / 2);
    g.rotate(tilt);
    const w = W - 18;
    const h = H - 18;
    const fx = -w / 2;
    const fy = -h / 2;
    g.fillStyle = "rgba(0,0,0,0.35)";
    g.fillRect(fx + 2, fy + 3, w, h);
    const kind = info.kind || "photo";
    const paper = { photo: "#EEEBE2", statement: "#F2EED8", object: "#E4DCC8", time: "#E8E4D4" }[kind] || "#EEEBE2";
    g.fillStyle = paper;
    g.fillRect(fx, fy, w, h);
    const ix = fx + 7;
    const iy = fy + 7;
    const iw = w - 14;
    const ih = h - 46;
    const r2 = strRand(eid + "#");
    if (kind === "photo") {
      const base = ["#3B3A33", "#2E3439", "#40352B", "#2B2F2A"][Math.floor(r2() * 4)];
      const grad = g.createLinearGradient(ix, iy, ix + iw, iy + ih);
      grad.addColorStop(0, shade(base, 1.4));
      grad.addColorStop(1, shade(base, 1 / 1.6));
      g.fillStyle = grad;
      g.fillRect(ix, iy, iw, ih);
      for (let i = 0; i < 5; i++) {
        g.fillStyle = `rgba(${60 + Math.floor(r2() * 100)},${50 + Math.floor(r2() * 90)},${40 + Math.floor(r2() * 80)},0.47)`;
        g.beginPath();
        g.ellipse(ix + r2() * iw, iy + r2() * ih, 6 + r2() * 16, 6 + r2() * 16, 0, 0, Math.PI * 2);
        g.fill();
      }
      g.fillStyle = "rgba(255,255,240,0.24)";
      g.beginPath();
      g.arc(ix + iw * 0.7, iy + ih * 0.3, 10, 0, Math.PI * 2);
      g.fill();
    } else {
      g.fillStyle = shade(paper, 1 / 1.08);
      g.fillRect(ix, iy, iw, ih);
      g.strokeStyle = "rgba(60,60,80,0.39)";
      g.lineWidth = 1;
      for (let i = 0; i < 6; i++) {
        const y = iy + 10 + i * 11;
        if (y > iy + ih - 2) break;
        g.beginPath();
        g.moveTo(ix + 6, y);
        g.lineTo(ix + iw - (6 + r2() * 24), y);
        g.stroke();
      }
      g.font = "8px 'Courier Prime', monospace";
      g.fillStyle = "#282828";
      g.textAlign = "right";
      g.textBaseline = "top";
      g.fillText(kind.toUpperCase(), ix + iw - 4, iy + 2);
      g.textAlign = "left";
    }
    // caption, wrapped onto at most three lines
    g.font = `13px '${HAND}', cursive`;
    g.fillStyle = "#1D1D24";
    g.textAlign = "center";
    g.textBaseline = "middle";
    const words = String(info.title || "").split(/\s+/);
    const lines = [];
    let cur = "";
    for (const wd of words) {
      const t = cur ? cur + " " + wd : wd;
      if (g.measureText(t).width > w - 8 && cur) {
        lines.push(cur);
        cur = wd;
      } else cur = t;
    }
    if (cur) lines.push(cur);
    const shown = lines.slice(0, 3);
    const capTop = iy + ih + 1;
    shown.forEach((ln, i) => g.fillText(ln, 0, capTop + 19 - (shown.length - 1) * 6.5 + i * 13));
    g.textAlign = "left";
    g.fillStyle = "#9C2B1F";
    g.beginPath();
    g.arc(0, fy + 2, 4, 0, Math.PI * 2);
    g.fill();
    g.restore();
  }

  // ---------------------------------------------------------------- map
  const PLACES = {
    cobb_road: [0.22, 0.3, "22 Cobb Rd"],
    substation: [0.55, 0.47, "County substation"],
    hospital: [0.7, 0.38, "Ostrander Co. Hospital"],
    pruitt: [0.35, 0.62, "Pruitt house"],
    dorsey: [0.62, 0.7, "Dorsey house"],
    mill_street: [0.48, 0.58, "9 Mill St"],
    st_adalberts: [0.52, 0.36, "St. Adalbert's"],
    spindle: [0.44, 0.5, "The Spindle"],
    library: [0.6, 0.28, "Public library"],
    mill: [0.4, 0.75, "Ostrander Paper"],
    water_tower: [0.33, 0.8, "Water tower"],
    rest_stop: [0.88, 0.12, "Rest stop, Rt 9"],
  };

  function paintMap(canvas, marks) {
    const [g, W, H] = fit(canvas);
    const r = { l: 6, t: 6, w: W - 12, h: H - 12 };
    g.fillStyle = "#E6DFC8";
    g.fillRect(r.l, r.t, r.w, r.h);
    const pt = (x, y) => [r.l + x * r.w, r.t + y * r.h];
    const line = (a, b) => {
      g.beginPath();
      g.moveTo(...a);
      g.lineTo(...b);
      g.stroke();
    };
    g.strokeStyle = "rgba(0,0,0,0.12)";
    g.lineWidth = 1;
    for (const i of [1, 2]) line([r.l + (r.w * i) / 3, r.t], [r.l + (r.w * i) / 3, r.t + r.h]);
    line([r.l, r.t + r.h / 2], [r.l + r.w, r.t + r.h / 2]);
    g.strokeStyle = "#7FA0B8";
    g.lineWidth = 5;
    g.beginPath();
    g.moveTo(...pt(0, 0.85));
    g.bezierCurveTo(...pt(0.3, 0.72), ...pt(0.45, 0.9), ...pt(0.6, 0.78));
    g.bezierCurveTo(...pt(0.75, 0.66), ...pt(0.9, 0.74), ...pt(1.0, 0.62));
    g.stroke();
    g.strokeStyle = "#B5523B";
    g.lineWidth = 3;
    line(pt(0.05, 0.5), pt(0.95, 0.45));
    line(pt(0.5, 0.05), pt(0.5, 0.95));
    g.strokeStyle = "#C9A54A";
    g.lineWidth = 2;
    line(pt(0.2, 0.25), pt(0.5, 0.48));
    line(pt(0.5, 0.48), pt(0.9, 0.1));
    line(pt(0.3, 0.65), pt(0.65, 0.72));
    g.strokeStyle = "rgba(0,0,0,0.24)";
    g.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
      line(pt(0.42, 0.4 + i * 0.05), pt(0.62, 0.4 + i * 0.05));
      line(pt(0.42 + i * 0.05, 0.4), pt(0.42 + i * 0.05, 0.6));
    }
    g.fillStyle = "#333";
    g.font = "bold 10px 'Courier Prime', monospace";
    g.textBaseline = "top";
    g.fillText("OSTRANDER COUNTY  ·  ROAD MAP", r.l + 6, r.t + 6);
    g.font = "9px 'Courier Prime', monospace";
    g.textBaseline = "alphabetic";
    g.fillText("CALDER FALLS", ...pt(0.44, 0.39));
    g.fillText("RT 9", ...pt(0.05, 0.48));
    g.font = `15px '${HAND}', cursive`;
    for (const key of marks) {
      if (!(key in PLACES)) continue;
      const [x, y, label] = PLACES[key];
      const [cx, cy] = pt(x, y);
      g.strokeStyle = "rgba(20,30,90,0.78)";
      g.fillStyle = "rgba(20,30,90,0.85)";
      g.lineWidth = 2;
      g.beginPath();
      g.ellipse(cx, cy, 9, 7, 0, 0, Math.PI * 2);
      g.stroke();
      // keep labels on the paper on a narrow phone
      const tw = g.measureText(label).width;
      const lx = cx + 11 + tw > r.l + r.w ? cx - 11 - tw : cx + 11;
      g.fillText(label, lx, cy + 4);
    }
  }

  // ---------------------------------------------------------------- radio
  class Dial {
    constructor(canvas, onTune) {
      this.canvas = canvas;
      this.freq = 880;
      this.LO = 530;
      this.HI = 1700;
      this.onTune = onTune;
      const set = (e) => {
        const b = canvas.getBoundingClientRect();
        const x = e.clientX - b.left;
        const fl = 14;
        const fw = b.width - 28;
        const f = this.LO + ((x - fl) / fw) * (this.HI - this.LO);
        this.setFreq(Math.round(f / 10) * 10);
      };
      canvas.addEventListener("pointerdown", (e) => {
        canvas.setPointerCapture(e.pointerId);
        set(e);
      });
      canvas.addEventListener("pointermove", (e) => {
        if (e.buttons) set(e);
      });
      canvas.addEventListener("wheel", (e) => {
        e.preventDefault();
        this.setFreq(this.freq + (e.deltaY < 0 ? 10 : -10));
      }, { passive: false });
    }
    setFreq(f, emit = true) {
      this.freq = Math.trunc(Math.max(this.LO, Math.min(this.HI, f)));
      this.paint();
      if (emit && this.onTune) this.onTune(this.freq);
    }
    paint() {
      const [g, W, H] = fit(this.canvas);
      g.fillStyle = "#2A1E14";
      g.strokeStyle = "#120C08";
      g.lineWidth = 2;
      g.beginPath();
      g.roundRect(4, 4, W - 8, H - 8, 8);
      g.fill();
      g.stroke();
      const r = { l: 14, t: 16, w: W - 28, h: H - 32 };
      const grad = g.createLinearGradient(0, r.t, 0, r.t + r.h);
      grad.addColorStop(0, "rgba(232,190,110,0.78)");
      grad.addColorStop(1, "rgba(180,120,50,0.78)");
      g.fillStyle = grad;
      g.fillRect(r.l, r.t, r.w, r.h);
      const xf = (f) => r.l + ((f - this.LO) / (this.HI - this.LO)) * r.w;
      g.strokeStyle = g.fillStyle = "rgb(40,25,10)";
      g.lineWidth = 1;
      g.font = "9px 'Courier Prime', monospace";
      for (const f of [540, 600, 700, 800, 1000, 1200, 1400, 1600]) {
        const x = xf(f);
        g.beginPath();
        g.moveTo(x, r.t + r.h - 14);
        g.lineTo(x, r.t + r.h - 4);
        g.stroke();
        g.fillText(String(Math.floor(f / 10)), x - 8, r.t + r.h - 18);
      }
      g.fillText("AM  kHz x10", r.l + 4, r.t + 12);
      const x = xf(this.freq);
      g.strokeStyle = "#B23A22";
      g.lineWidth = 2;
      g.beginPath();
      g.moveTo(x, r.t + 2);
      g.lineTo(x, r.t + r.h - 2);
      g.stroke();
    }
  }

  function paintKnob(canvas, active) {
    const [g] = fit(canvas);
    g.fillStyle = "#1C1C1C";
    g.strokeStyle = "#444";
    g.lineWidth = 2;
    g.beginPath();
    g.arc(35, 35, 28, 0, Math.PI * 2);
    g.fill();
    g.stroke();
    const ang = ((active ? 40 : -60) * Math.PI) / 180;
    g.strokeStyle = "#B8B8B8";
    g.lineWidth = 3;
    g.beginPath();
    g.moveTo(35, 35);
    g.lineTo(35 + Math.cos(ang) * 22, 35 + Math.sin(ang) * 22);
    g.stroke();
    g.fillStyle = active ? "#B23A22" : "#3A1A14";
    g.beginPath();
    g.arc(60, 8, 4, 0, Math.PI * 2);
    g.fill();
  }

  root.CFWidgets = { fit, Watch, Nerve, Notebook, paintPolaroid, paintMap, Dial, paintKnob, rgba, PLACES };
})(typeof self !== "undefined" ? self : this);
