/* The story text: typed out at a readable pace, and allowed to lie.
   A port of calder_falls/ui/storyview.py onto the DOM.

   Typewriter reveal and its stutter, words that swap for a moment, color
   split on the letter edges, letters drifting off their line, earlier
   paragraphs that change while you are not looking, and the flashlight in
   dark scenes. On a touch screen the flashlight follows your finger and
   stays where you lift it. */

(function (root) {
  "use strict";

  const UNEASY = {
    door: "mouth", house: "throat", hallway: "hallway", light: "eye",
    radio: "choir", June: "you", children: "count", wall: "skin",
    window: "mouth", quiet: "counted", home: "here", father: "vessel",
    kitchen: "listening room", phone: "open line", you: "we",
  };

  class Para {
    constructor(text, kind = "story", pause = 0) {
      this.text = text;
      this.kind = kind; // story, echo, radio, system, pause
      this.shown = 0;
      this.pause = pause;
      this.el = null;
      this.shownEl = null;
      this.restEl = null;
      this.drifted = false;
    }
  }

  class StoryView {
    constructor(scroll, inner, dark, onRevealed) {
      this.scroll = scroll; // the scrolling element
      this.inner = inner; // where paragraphs go
      this.darkEl = dark; // the flashlight layer over the pane
      this.onRevealed = onRevealed;
      this.paras = [];
      this.stage = null;
      this.speed = 55;
      this.flashlightCone = true;
      this.flickerMode = "gentle";
      this.dark = false;
      this.batteryLow = false;
      this.shadow = "";
      this.light = null; // [x, y] in pane coordinates, null until placed
      this.rand = CFSeeded(7);
      this.tempSwap = null; // { para, until }
      this.pendingScrollback = [];
      this.driftSeed = 0;
      this.lastTick = performance.now() / 1000;
      this.carry = 0;
      this.pauseUntil = 0;
      this.follow = true;
      this.autoScroll = false;
      this.lastScroll = 0;

      this.shadowEl = document.createElement("div");
      this.shadowEl.className = "shadow-text";
      this.darkEl.appendChild(this.shadowEl);

      scroll.addEventListener("scroll", () => this._scrolled());
      scroll.addEventListener("click", () => {
        if (this.isRevealing()) this.skip();
      });
      const move = (e) => {
        const b = this.scroll.getBoundingClientRect();
        this.light = [e.clientX - b.left, e.clientY - b.top];
        if (this.dark) this._paintDark();
      };
      scroll.addEventListener("pointermove", move);
      scroll.addEventListener("pointerdown", move);
      new ResizeObserver(() => {
        if (this.follow) this._followNow();
      }).observe(scroll);

      const tick = () => {
        this._tick();
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      setInterval(() => this._fx(), 90);
    }

    // ------------------------------------------------------------ content
    clear() {
      this.paras = [];
      this.tempSwap = null;
      this.inner.textContent = "";
    }

    add(text, kind = "story") {
      const p = new Para(text, kind);
      this._build(p);
      this.paras.push(p);
      if (kind === "echo") this.follow = true;
      if (this.follow) requestAnimationFrame(() => this._followNow());
    }

    addPause(seconds) {
      this.paras.push(new Para("", "pause", seconds));
    }

    loadTranscript(lines) {
      this.clear();
      for (const line of lines) {
        const p = line.startsWith("> ") ? new Para(line.slice(2), "echo") : new Para(line);
        p.shown = p.text.length;
        this._build(p);
        this.paras.push(p);
      }
      requestAnimationFrame(() => this._setScroll(this.scroll.scrollHeight));
    }

    skip() {
      for (const p of this.paras) {
        p.shown = p.text.length;
        p.pause = 0;
        this._render(p);
      }
      this.pauseUntil = 0;
      this.follow = true;
      requestAnimationFrame(() => this._followNow());
      this.onRevealed();
    }

    isRevealing() {
      return this.paras.some((p) => p.shown < p.text.length || p.pause > 0);
    }

    scrollback(find, replace) {
      this.pendingScrollback.push([find, replace]);
      this._scrolled();
    }

    setDark(on) {
      this.dark = on;
      if (on && !this.light) this.light = [this.scroll.clientWidth / 2, this.scroll.clientHeight / 2];
      this._paintDark();
    }

    setStage(s) {
      this.stage = s;
      const split = s ? s.split : 0;
      if (split) {
        const red = CFWidgets.rgba(s.accent, 0.35);
        this.inner.style.setProperty("--split", `${-split}px 0 0 ${red}, ${split}px 0 0 rgba(90,200,210,0.27)`);
      } else this.inner.style.setProperty("--split", "none");
    }

    // ------------------------------------------------------------ DOM
    _build(p) {
      if (p.kind === "pause") return;
      p.el = document.createElement("p");
      p.el.className = "para " + p.kind;
      p.shownEl = document.createElement("span");
      p.restEl = document.createElement("span");
      p.restEl.className = "rest";
      p.el.append(p.shownEl, p.restEl);
      this._render(p);
      this.inner.appendChild(p.el);
    }

    _render(p, text) {
      if (!p.el) return;
      text = text === undefined ? p.text : text;
      const n = text === p.text ? p.shown : text.length;
      p.shownEl.textContent = text.slice(0, n);
      p.restEl.textContent = text.slice(n);
      p.drifted = false;
    }

    // ------------------------------------------------------------ reveal
    _tick() {
      const now = performance.now() / 1000;
      const dt = Math.min(0.25, now - this.lastTick);
      this.lastTick = now;
      if (this.dark) this._paintDark();
      if (now < this.pauseUntil) return;
      const target = this.paras.find((p) => p.shown < p.text.length || p.pause > 0);
      if (!target) return;
      if (target.kind === "pause") {
        this.pauseUntil = now + target.pause;
        target.pause = 0;
        return;
      }
      if (this.speed <= 0) target.shown = target.text.length;
      else {
        this.carry += dt * this.speed;
        let n = Math.floor(this.carry);
        if (n <= 0) return;
        this.carry -= n;
        if (this.stage && this.stage.stutter && this.rand() < this.stage.stutter) {
          this.pauseUntil = now + 0.08 + this.rand() * 0.27;
          n = 1;
        }
        target.shown = Math.min(target.text.length, target.shown + n);
        // a little breath at the end of a sentence
        if (target.shown < target.text.length && ".?!".includes(target.text[target.shown - 1])) this.pauseUntil = now + 0.12;
      }
      this._render(target);
      if (this.follow) this._followNow();
      if (!this.isRevealing()) this.onRevealed();
    }

    _revealBottom() {
      // Bottom of the last line actually typed out, in scroll coordinates
      for (let i = this.paras.length - 1; i >= 0; i--) {
        const p = this.paras[i];
        if (p.kind === "pause" || p.shown <= 0 || !p.el) continue;
        const r = p.shownEl.getClientRects();
        const last = r[r.length - 1];
        const top = this.scroll.getBoundingClientRect().top;
        if (!last) return p.el.offsetTop + p.el.offsetHeight;
        return last.bottom - top + this.scroll.scrollTop;
      }
      return 0;
    }

    _setScroll(v) {
      this.autoScroll = true;
      this.scroll.scrollTop = v;
      this.lastScroll = this.scroll.scrollTop;
      requestAnimationFrame(() => (this.autoScroll = false));
    }

    _followNow() {
      if (!this.follow) return;
      // keep the typing line about one line above the bottom edge
      const target = Math.max(0, this._revealBottom() + 28 - this.scroll.clientHeight);
      if (target > this.scroll.scrollTop + 1) this._setScroll(target);
    }

    _scrolled() {
      const sc = this.scroll;
      if (!this.autoScroll) {
        // the player scrolled: going up means they're reading back, so stop
        // following; coming back down to the typing line resumes it
        if (sc.scrollTop < this.lastScroll - 2) this.follow = false;
        else if (sc.scrollTop + sc.clientHeight >= this._revealBottom()) this.follow = true;
      }
      this.lastScroll = sc.scrollTop;
      if (this.dark) this._paintDark();
      if (!this.pendingScrollback.length) return;
      const top = sc.scrollTop;
      const bottom = top + sc.clientHeight;
      const keep = [];
      for (const [find, rep] of this.pendingScrollback) {
        let done = true; // nothing to change any more
        for (let i = this.paras.length - 1; i >= 0; i--) {
          const p = this.paras[i];
          if (p.text.includes(find)) {
            const pt = p.el ? p.el.offsetTop : 0;
            const pb = pt + (p.el ? p.el.offsetHeight : 0);
            if (pb < top || pt > bottom) {
              p.text = p.text.split(find).join(rep);
              p.shown = p.text.length;
              this._render(p);
            } else done = false;
            break;
          }
        }
        if (!done) keep.push([find, rep]);
      }
      this.pendingScrollback = keep;
    }

    // ------------------------------------------------------------ effects
    _fx() {
      const s = this.stage;
      const now = performance.now() / 1000;
      if (this.tempSwap && now > this.tempSwap.until) {
        this._render(this.tempSwap.para);
        this.tempSwap = null;
      }
      if (s && s.swap > 0 && !this.tempSwap && this.paras.length && this.rand() < s.swap * 0.09) {
        const visible = this.paras.filter((p) => p.kind === "story" && p.shown === p.text.length && p.el);
        if (visible.length) {
          const recent = visible.slice(-6);
          const p = recent[Math.floor(this.rand() * recent.length)];
          const hits = Object.keys(UNEASY).filter((w) => p.text.includes(w));
          if (hits.length) {
            const w = hits[Math.floor(this.rand() * hits.length)];
            const at = p.text.indexOf(w);
            this._render(p, p.text.slice(0, at) + UNEASY[w] + p.text.slice(at + w.length));
            this.tempSwap = { para: p, until: now + 0.22 };
          }
        }
      }
      if (s && s.drift > 0) {
        // with no flicker the letters stay where they drifted to
        if (this.flickerMode !== "off") this.driftSeed = Math.floor(now * 1.3);
        this._drift(s.drift);
      } else {
        for (const p of this.paras) if (p.drifted) this._render(p);
      }
    }

    _drift(amount) {
      const last = this.paras.filter((p) => p.el).slice(-3);
      for (const p of this.paras) if (p.drifted && !last.includes(p)) this._render(p);
      last.forEach((p) => {
        if (p.shown < p.text.length || (this.tempSwap && this.tempSwap.para === p)) return;
        const idx = this.paras.indexOf(p);
        const key = this.driftSeed * 131 + idx;
        if (p.drifted === key) return;
        const r = CFSeeded(key);
        const count = Math.floor(p.text.length * 0.02 * amount) + 1;
        const moved = new Map();
        for (let i = 0; i < count; i++) {
          const at = Math.floor(r() * Math.max(1, p.text.length));
          const dy = (r() < 0.5 ? -1 : 1) * (3 + r() * 6) * amount * 2;
          if (p.text[at] && p.text[at].trim()) moved.set(at, dy);
        }
        const frag = document.createDocumentFragment();
        let from = 0;
        for (const at of [...moved.keys()].sort((a, b) => a - b)) {
          frag.append(p.text.slice(from, at));
          const s = document.createElement("span");
          s.className = "drift";
          s.style.top = `${moved.get(at).toFixed(1)}px`;
          s.textContent = p.text[at];
          frag.append(s);
          from = at + 1;
        }
        frag.append(p.text.slice(from));
        p.shownEl.textContent = "";
        p.shownEl.append(frag);
        p.restEl.textContent = "";
        p.drifted = key;
      });
    }

    _paintDark() {
      const el = this.darkEl;
      if (!this.dark) {
        el.style.display = "none";
        return;
      }
      el.style.display = "block";
      const bg = this.stage ? this.stage.bg : "#0B0F1A";
      if (!this.flashlightCone) {
        el.style.background = CFWidgets.rgba(bg, 0.55);
        this.shadowEl.style.display = "none";
        return;
      }
      let radius = 150;
      const now = performance.now() / 1000;
      if (this.batteryLow) {
        if (this.flickerMode === "full") {
          radius *= 0.75 + 0.25 * this.rand();
          if (this.rand() < 0.04) radius = 0;
        } else if (this.flickerMode === "gentle") {
          // a slow fade in and out, about once every four seconds
          radius *= 0.85 + 0.15 * Math.sin(now * 1.5);
        } else radius *= 0.85; // dimmer, and still
      }
      const [x, y] = this.light || [-1000, -1000];
      const R = Math.max(radius, 1);
      el.style.background = `radial-gradient(circle ${R}px at ${x}px ${y}px, ${CFWidgets.rgba(bg, 0)} 0%, rgba(0,0,0,0.16) 55%, #000 100%)`;
      if (this.shadow && radius > 0 && this.light) {
        const ang = (now * 0.3) % 6.283;
        this.shadowEl.style.display = "block";
        this.shadowEl.textContent = this.shadow;
        this.shadowEl.style.left = `${x + Math.cos(ang) * radius * 1.05}px`;
        this.shadowEl.style.top = `${y + Math.sin(ang) * radius * 1.05}px`;
      } else this.shadowEl.style.display = "none";
    }
  }

  root.CFStoryView = StoryView;
})(typeof self !== "undefined" ? self : this);
