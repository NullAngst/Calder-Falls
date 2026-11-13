/* Static bleed, live, as an AudioWorklet. A port of StaticBleed in
   calder_falls/audio/engine.py: the band narrows to AM, the signal fades
   like a station at the edge of its range, and radio static sits on top.
   amount 0 is clean (the music passes straight through), 1 is barely there.

   The Butterworth sections come from manifest.json, which
   calder_falls/audio/variants.py fills from scipy for each sample rate. */

class Wander {
  // Piecewise-linear random wander between 0 and 1
  constructor(rand, sr, rateHz) {
    this.rand = rand;
    this.step = rateHz / sr;
    this.phase = 0;
    this.a = rand();
    this.b = rand();
  }
  next() {
    const v = this.a + (this.b - this.a) * Math.min(1, this.phase);
    this.phase += this.step;
    if (this.phase >= 1) {
      this.phase -= 1;
      this.a = this.b;
      this.b = this.rand();
    }
    return v;
  }
}

class SOS {
  // Cascaded biquads, direct form II transposed, one state per channel
  constructor(sections, channels) {
    this.s = sections; // [[b0,b1,b2,a0,a1,a2], ...]
    this.z = [];
    for (let c = 0; c < channels; c++) this.z.push(sections.map(() => [0, 0]));
  }
  run(x, ch) {
    const z = this.z[ch];
    for (let i = 0; i < this.s.length; i++) {
      const [b0, b1, b2, , a1, a2] = this.s[i];
      const zi = z[i];
      const y = b0 * x + zi[0];
      zi[0] = b1 * x - a1 * y + zi[1];
      zi[1] = b2 * x - a2 * y;
      x = y;
    }
    return x;
  }
}

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

class StaticBleed extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [{ name: "amount", defaultValue: 0, minValue: 0, maxValue: 1, automationRate: "k-rate" }];
  }

  constructor(options) {
    super();
    const f = options.processorOptions.filters;
    const sr = sampleRate;
    this.rand = seeded(1610);
    this.noiseBp = new SOS(f.noise, 1);
    this.musicBp = new SOS(f.music, 2);
    this.crkBp = new SOS(f.crackle, 1);
    this.fade = new Wander(this.rand, sr, 1.8);
    this.drop = new Wander(this.rand, sr, 0.9);
    this.pitch = new Wander(this.rand, sr, 0.35);
    this.whistle = 0;
    this.amt = 0;
    this.spare = null;
  }

  gauss() {
    // Box-Muller, two at a time
    if (this.spare !== null) {
      const v = this.spare;
      this.spare = null;
      return v;
    }
    let u = 0;
    while (u === 0) u = this.rand();
    const r = Math.sqrt(-2 * Math.log(u));
    const t = 2 * Math.PI * this.rand();
    this.spare = r * Math.sin(t);
    return r * Math.cos(t);
  }

  process(inputs, outputs, params) {
    const inp = inputs[0];
    const out = outputs[0];
    const n = out[0].length;
    const target = params.amount[0];
    const a0 = this.amt;
    // smooth like the desktop engine: about 0.3 s to settle
    const a1 = a0 + (target - a0) * Math.min(1, n / (0.3 * sampleRate));
    this.amt = a1;
    const L = inp[0] || new Float32Array(n);
    const R = inp[1] || L;
    if (a0 < 1e-4 && a1 < 1e-4) {
      out[0].set(L);
      if (out[1]) out[1].set(R);
      return true;
    }
    const sr = sampleRate;
    for (let i = 0; i < n; i++) {
      const amt = a0 + ((a1 - a0) * i) / n;
      const noise = this.noiseBp.run(this.gauss(), 0);
      const fade = 0.35 + 0.65 * Math.pow(this.fade.next(), 1.5);
      const imp = this.rand() < 40 / sr ? (this.rand() - 0.5) * 6 : 0;
      const crackle = this.crkBp.run(imp, 0);
      const wf = 1450 + 700 * (this.pitch.next() - 0.5);
      this.whistle = (this.whistle + wf / sr) % 1;
      const wh = Math.sin(2 * Math.PI * this.whistle) * 0.04;
      const st = Math.tanh((noise * 1.6 * fade + crackle * 0.5 + wh) * 1.4) * amt * 0.32;
      const drop = 1 - 0.75 * amt * Math.pow(1 - this.drop.next(), 2);
      const l = L[i];
      const r = R[i];
      const nl = this.musicBp.run(l, 0);
      const nr = this.musicBp.run(r, 1);
      out[0][i] = Math.tanh((l * (1 - 0.85 * amt) + nl * 1.6 * 0.85 * amt) * drop + st);
      if (out[1]) out[1][i] = Math.tanh((r * (1 - 0.85 * amt) + nr * 1.6 * 0.85 * amt) * drop + st);
    }
    return true;
  }
}

registerProcessor("static-bleed", StaticBleed);
