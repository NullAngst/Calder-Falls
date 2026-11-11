"""Build Calder.sf2, the game's own sound bank.

Every sample here is generated with numpy at build time. No recordings, so
the license question is closed: the bank is ours. Samples are mono at
32 kHz, which is close to what a lot of PS2 games actually shipped.

All presets live in bank 20 so they never collide with the General MIDI
base bank (bank 0, drums on 128). The MIDI cues select them with CC0 = 20.

Run from the repo root:
    python3 soundfonts/build_calder.py
Same seed, same bank, every time.
"""

import math
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sf2write import (  # noqa: E402
    Instrument, LOOP_CONTINUOUS, LOOP_NONE, Preset, Sample, Zone,
    abs_cents, timecents, write_sf2,
)

SR = 32000
BANK = 20
RNG = np.random.default_rng(1986)


# ---------------------------------------------------------------- helpers

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t(seconds):
    return np.arange(int(seconds * SR)) / SR


def sos_lp(fc, order=2):
    return signal.butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos")


def sos_hp(fc, order=2):
    return signal.butter(order, fc, "high", fs=SR, output="sos")


def sos_bp(lo, hi, order=2):
    return signal.butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos")


def filt(sos, x):
    return signal.sosfilt(sos, x)


def norm(x, peak=0.9):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def fade(x, fin=0.002, fout=0.01):
    x = x.copy()
    a = max(1, int(fin * SR))
    b = max(1, int(fout * SR))
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)
    return x


def bake_loop(x, ls, le, xf):
    """Make x[ls:le] loop seamlessly by crossfading the loop's tail into
    the material just before the loop start. Equal power, for noisy sounds."""
    x = x.copy()
    w = np.linspace(0, 1, xf)
    a = np.cos(w * math.pi / 2)
    b = np.sin(w * math.pi / 2)
    x[le - xf:le] = x[le - xf:le] * a + x[ls - xf:ls] * b
    return x


def fit_period(f0, approx_seconds):
    """Pick a loop length holding a whole number of cycles near f0.
    Returns (loop_samples, actual_freq, correction_cents)."""
    best = None
    lo = int(approx_seconds * SR * 0.8)
    hi = int(approx_seconds * SR * 1.2)
    for m in range(lo, hi):
        n = max(1, round(f0 * m / SR))
        f = n * SR / m
        cents = 1200 * math.log2(f / f0)
        if best is None or abs(cents) < abs(best[2]):
            best = (m, f, cents)
            if abs(cents) < 0.3:
                break
    return best


def correction_for(cents):
    """The synth plays the sample at its root; if the sample is sharp by c
    cents we tell the SF2 reader to correct by -c."""
    return int(round(-cents))


def smooth_noise(n, rate_hz, seed_rng=RNG):
    """Slow random wander, 0..1."""
    k = max(2, int(n / SR * rate_hz) + 2)
    pts = seed_rng.random(k)
    xs = np.linspace(0, n, k)
    return np.interp(np.arange(n), xs, pts)


def pink(n):
    w = RNG.standard_normal(n)
    # Paul Kellet's economy pink filter as an IIR
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


# ---------------------------------------------------------------- voices

def pluck(f0, dur, pos=0.14, bright=1.0, t60=1.6, courses=2, detune=4.0):
    """Additive plucked string: harmonic amplitudes from the pick position,
    higher partials die first, slight inharmonicity, doubled course."""
    tt = t(dur)
    out = np.zeros_like(tt)
    for c in range(courses):
        f = f0 * 2 ** ((detune * (c - (courses - 1) / 2)) / 1200)
        k = 1
        while True:
            fk = k * f * math.sqrt(1 + 0.00008 * k * k)
            if fk > SR * 0.42 or k > 60:
                break
            amp = abs(math.sin(math.pi * k * pos)) / k ** (1.25 / bright)
            decay = t60 / (1 + 0.12 * k ** 1.25)
            env = np.exp(-6.9 * tt / decay)
            ph = RNG.random() * 2 * math.pi
            out += amp * env * np.sin(2 * math.pi * fk * tt + ph)
            k += 1
    # pick noise
    nz = filt(sos_hp(2500), RNG.standard_normal(len(tt)))
    nz *= np.exp(-tt / 0.004) * 0.06
    out = out + nz
    # light body resonance
    body = filt(sos_bp(350, 700), out) * 0.5 + filt(sos_bp(2200, 3200), out) * 0.25
    return fade(out + body)


def mandolin_note(root):
    f0 = mtof(root)
    t60 = 1.8 * (196 / f0) ** 0.35
    return norm(pluck(f0, 2.4, pos=0.12, t60=t60))


def tremolo_mandolin_note(root):
    """Repeated picks summed into a sample that is exactly periodic after the
    first second, so the loop needs no crossfade at all."""
    f0 = mtof(root)
    pick_rate = 12.5
    picks_per_loop = 8
    period = int(round(SR / pick_rate))
    loop_len = period * picks_per_loop
    h_len = 1.3
    h_samples = int(h_len * SR)
    # two strokes, down and up, a little different
    rng = np.random.default_rng(root)
    strokes = []
    for i in range(2):
        strokes.append(pluck(f0, h_len, pos=0.11 + 0.03 * i,
                             t60=0.55 * (196 / f0) ** 0.3, bright=1.0 - 0.15 * i))
    jitter = rng.integers(-90, 90, picks_per_loop)
    jitter[0] = 0
    vel = 0.75 + 0.25 * rng.random(picks_per_loop)
    vel[0] = 1.0
    loop_start = h_samples + period * 2
    total = loop_start + loop_len
    out = np.zeros(total + h_samples)
    j = 0
    pos = 0
    while pos < total + period:
        idx = j % picks_per_loop
        p = pos + int(jitter[idx])
        if p >= 0:
            s = strokes[idx % 2] * vel[idx]
            out[p:p + h_samples] += s[:len(out) - p]
        j += 1
        pos += period
    out = out[:total]
    return norm(out, 0.85), (loop_start, total)


def epiano_note(root, dur=6.0):
    """FM electric piano, two voices pulled apart by about 9 cents."""
    f0 = mtof(root)
    tt = t(dur)
    out = np.zeros_like(tt)
    t60 = 6.0 * (130 / f0) ** 0.45
    for d in (-9.0, 9.0):
        f = f0 * 2 ** (d / 1200)
        index = 1.6 * np.exp(-tt / 0.5) + 0.35
        mod = np.sin(2 * math.pi * f * tt)
        car = np.sin(2 * math.pi * f * tt + index * mod)
        env = np.exp(-6.9 * tt / t60)
        tine_f = f * 14.0
        tine = 0.0
        if tine_f < SR * 0.4:
            tine = 0.22 * np.sin(2 * math.pi * tine_f * tt) * np.exp(-tt / 0.06)
        out += (car + tine) * env
    att = np.minimum(1, tt / 0.003)
    out = filt(sos_lp(7000), out * att)
    return norm(fade(out, 0.001, 0.2))


def piano_note(root, dur=3.2):
    """Plain additive piano, used reversed."""
    f0 = mtof(root)
    tt = t(dur)
    out = np.zeros_like(tt)
    k = 1
    while True:
        fk = k * f0 * math.sqrt(1 + 0.0004 * k * k)
        if fk > SR * 0.4 or k > 40:
            break
        amp = (1 / k ** 1.4) * (1 + 0.6 * math.cos(k * 0.7))
        decay = 5.0 * (130 / f0) ** 0.5 / (1 + 0.08 * k)
        out += amp * np.exp(-6.9 * tt / decay) * np.sin(2 * math.pi * fk * tt + RNG.random() * 6.28)
        k += 1
    ham = filt(sos_bp(800, 4000), RNG.standard_normal(len(tt))) * np.exp(-tt / 0.01) * 0.05
    return out + ham


def reversed_piano_note(root):
    x = piano_note(root)[::-1].copy()
    x = filt(sos_lp(6000), x)
    # the swell ends hard, which is the point; just avoid a click
    return norm(fade(x, 0.05, 0.004))


def distorted_bass_note(root):
    f0 = mtof(root)
    m, f, cents = fit_period(f0, 0.5)
    lead_in = int(0.25 * SR)
    total = lead_in + m * 3
    tt = np.arange(total) / SR
    ph = (f * tt) % 1.0
    saw = 2 * ph - 1
    sub = np.sin(2 * math.pi * f * tt)
    x = saw * 0.7 + sub * 0.4
    x = filt(sos_lp(900), x)
    x = np.tanh(x * 3.2)
    x = filt(sos_lp(2600), x)
    # bright pick at the front
    x[:lead_in] *= 1 + 0.6 * np.exp(-tt[:lead_in] / 0.03)
    ls = lead_in + m
    le = ls + m
    x = x[:le]
    return norm(fade(x, 0.002, 0.0)), (ls, le), correction_for(cents)


def tape_pad_note(root, dur=7.0):
    f0 = mtof(root)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    wow = 1 + (6 / 1200) * np.log(2) * np.sin(2 * math.pi * 0.5 * tt)
    out = np.zeros(n)
    for d in (-7, 0, 7):
        f = f0 * 2 ** (d / 1200)
        phase = np.cumsum(f * wow) / SR + RNG.random()
        out += 2 * (phase % 1.0) - 1
    out = filt(sos_lp(min(1800, f0 * 10)), out)
    out = np.tanh(out * 1.4)
    out = filt(sos_lp(3000), out)
    out += pink(n) * 0.01
    ls = int(1.5 * SR)
    le = int(5.5 * SR)
    out = bake_loop(out, ls, le, int(0.6 * SR))
    out = out[:le]
    att = np.minimum(1, tt[:le] / 0.4)
    return norm(out * att, 0.8), (ls, le)


def sub_drone_note(root, dur=9.0):
    f0 = mtof(root)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    breathe = 0.85 + 0.15 * np.sin(2 * math.pi * 0.11 * tt)
    out = (np.sin(2 * math.pi * f0 * tt)
           + 0.35 * np.sin(2 * math.pi * 2 * f0 * tt + 0.3)
           + 0.12 * np.sin(2 * math.pi * 3.01 * f0 * tt))
    out *= breathe
    rumble = filt(sos_lp(90, 4), RNG.standard_normal(n)) * 0.6
    out = out + rumble
    ls = int(1.0 * SR)
    le = int(8.0 * SR)
    out = bake_loop(out, ls, le, int(1.0 * SR))[:le]
    return norm(out, 0.85), (ls, le)


def modal(freqs, amps, decays, dur, strike_lp=6000, strike=0.15):
    tt = t(dur)
    out = np.zeros_like(tt)
    for f, a, d in zip(freqs, amps, decays):
        if f >= SR * 0.45:
            continue
        out += a * np.exp(-6.9 * tt / d) * np.sin(2 * math.pi * f * tt + RNG.random() * 6.28)
    hit = filt(sos_lp(strike_lp), RNG.standard_normal(len(tt))) * np.exp(-tt / 0.006) * strike
    return out + hit


def plate(base, n_modes, dur, t60_low, bright=1.0):
    freqs = []
    for m in range(1, 9):
        for k in range(1, 9):
            freqs.append(base * (m * m + k * k) / 2 * (1 + 0.02 * RNG.standard_normal()))
    freqs = sorted(freqs)[:n_modes]
    amps = [(1 / (1 + i * 0.15)) * (0.5 + RNG.random()) for i in range(len(freqs))]
    decays = [t60_low / (1 + (f / base) ** 0.6 * 0.08 / bright) for f in freqs]
    return modal(freqs, amps, decays, dur)


def metal_kit():
    """Six hits. Each lands on two keys, the upper one a step higher."""
    hits = []
    hits.append(("SheetLow", norm(fade(plate(38, 40, 4.0, 3.5), 0.0005, 0.3))))
    hits.append(("SheetMid", norm(fade(plate(110, 45, 3.0, 2.2), 0.0005, 0.3))))
    hits.append(("Ping", norm(fade(modal([1240, 3420, 6710, 9800], [1, .5, .3, .15],
                                         [2.5, 1.2, .6, .3], 2.6), 0.0005, 0.3))))
    # rattle: a burst of small hits
    dur = 1.6
    r = np.zeros(int(dur * SR))
    pos = 0
    while pos < int(0.5 * SR):
        h = plate(260 + RNG.random() * 80, 20, 0.6, 0.35) * (0.4 + 0.6 * RNG.random())
        end = min(len(r), pos + len(h))
        r[pos:end] += h[:end - pos]
        pos += int(SR * (0.012 + 0.03 * RNG.random()))
    hits.append(("Rattle", norm(fade(r, 0.0005, 0.2))))
    # hollow pipe: free-free bar ratios
    base = 180
    ratios = [1, 2.756, 5.404, 8.933, 13.34]
    hits.append(("Pipe", norm(fade(modal([base * x for x in ratios], [1, .7, .4, .25, .12],
                                         [3.0, 2.0, 1.2, .7, .4], 3.2), 0.0005, 0.3))))
    # chain: many tiny high hits
    c = np.zeros(int(1.2 * SR))
    for _ in range(26):
        p = int(RNG.random() * 0.35 * SR)
        h = modal([2000 + 3000 * RNG.random(), 5000 + 3000 * RNG.random()], [1, .4],
                  [0.15, 0.08], 0.3, strike=0.3) * (0.3 + 0.7 * RNG.random())
        c[p:p + len(h)] += h[:len(c) - p]
    hits.append(("Chain", norm(fade(c, 0.0005, 0.1))))
    return hits


def metal_scrape(dur=5.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    # stick-slip: pulse rate wanders between 40 and 260 Hz
    rate = 40 + 220 * smooth_noise(n, 1.5)
    phase = np.cumsum(rate) / SR
    pulses = (np.diff(np.floor(phase), prepend=0) > 0).astype(float)
    exc = pulses * (0.5 + RNG.random(n)) + RNG.standard_normal(n) * 0.08
    out = np.zeros(n)
    for f in (420, 1180, 2310, 3770, 5240):
        q = signal.iirpeak(f, 35, fs=SR)
        out += signal.lfilter(*q, exc) * (1.0 / (1 + f / 2000))
    out *= 0.4 + 0.6 * smooth_noise(n, 0.8)
    ls = int(1.0 * SR)
    le = int(4.5 * SR)
    out = bake_loop(out, ls, le, int(0.5 * SR))[:le]
    att = np.minimum(1, tt[:le] / 0.15)
    return norm(out * att, 0.85), (ls, le)


def tape_hiss(dur=6.0):
    n = int(dur * SR)
    x = filt(sos_hp(900), pink(n) * 0.5 + RNG.standard_normal(n) * 0.25)
    x = filt(sos_lp(11000), x)
    x *= 1 + 0.08 * np.sin(2 * math.pi * 4.2 * np.arange(n) / SR)
    ls = int(1.0 * SR)
    le = int(5.0 * SR)
    x = bake_loop(x, ls, le, int(0.5 * SR))[:le]
    return norm(x, 0.7), (ls, le)


def radio_static(dur=9.0):
    """AM band at night: band-limited noise that fades in and out, crackle,
    and a heterodyne whistle that drifts."""
    n = int(dur * SR)
    base = filt(sos_bp(250, 4200), RNG.standard_normal(n))
    fadeenv = 0.35 + 0.65 * smooth_noise(n, 0.6) ** 1.5
    crackle = np.zeros(n)
    for _ in range(int(dur * 25)):
        p = int(RNG.random() * (n - 200))
        crackle[p] += (RNG.random() - 0.5) * 8
    crackle = filt(sos_bp(500, 7000), crackle)
    wf = 1500 + 700 * (smooth_noise(n, 0.3) - 0.5)
    whistle = 0.08 * np.sin(2 * math.pi * np.cumsum(wf) / SR)
    x = base * fadeenv + crackle * 0.6 + whistle
    x = np.tanh(x * 1.5)
    ls = int(1.5 * SR)
    le = int(8.0 * SR)
    x = bake_loop(x, ls, le, int(0.8 * SR))[:le]
    return norm(x, 0.8), (ls, le)


def fridge_hum(dur=6.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = (np.sin(2 * math.pi * 60 * tt) * 0.6 + np.sin(2 * math.pi * 120 * tt) * 0.9
         + np.sin(2 * math.pi * 180 * tt) * 0.3 + np.sin(2 * math.pi * 240 * tt) * 0.15)
    rattle = filt(sos_bp(300, 1500), RNG.standard_normal(n)) * (0.5 + 0.5 * np.sin(2 * math.pi * 120 * tt)) * 0.15
    x = x + rattle
    ls = 1600 * 20          # 60 Hz repeats every 1600 samples at 32 kHz
    le = ls + 1600 * 80
    x = bake_loop(x, ls, le, 1600 * 4)[:le]
    return norm(x, 0.7), (ls, le)


def clock(freq):
    x = modal([freq, freq * 2.3, freq * 3.9], [1, .4, .2], [0.05, 0.03, 0.02], 0.15,
              strike_lp=9000, strike=0.4)
    return norm(fade(x, 0.0002, 0.02))


# ---------------------------------------------------------------- bank

def zone(sample, lo, hi, **gens):
    return Zone(sample=sample, key_lo=lo, key_hi=hi, gens=gens)


def multisampled(name, roots, make, **gens):
    """One sample per root, each covering the keys halfway to its neighbours."""
    zones = []
    for i, r in enumerate(roots):
        lo = 0 if i == 0 else (roots[i - 1] + r) // 2 + 1
        hi = 127 if i == len(roots) - 1 else (r + roots[i + 1]) // 2
        res = make(r)
        loop = None
        corr = 0
        if isinstance(res, tuple):
            data = res[0]
            loop = res[1]
            if len(res) > 2:
                corr = res[2]
        else:
            data = res
        s = Sample(f"{name[:12]}{r}", data, SR, r, corr, loop)
        g = dict(gens)
        g["sampleModes"] = LOOP_CONTINUOUS if loop else LOOP_NONE
        zones.append(zone(s, lo, hi, **g))
    return Instrument(name, zones)


def unpitched(name, data, loop, key_lo=0, key_hi=127, root=60, **gens):
    s = Sample(name[:20], data, SR, root, 0, loop)
    g = dict(gens)
    g["sampleModes"] = LOOP_CONTINUOUS if loop else LOOP_NONE
    return Instrument(name, [zone(s, key_lo, key_hi, **g)])


def build(path):
    presets = []

    def add(prog, inst):
        presets.append(Preset(inst.name, BANK, prog, inst))

    add(0, multisampled("Tremolo Mandolin", [55, 62, 69, 76, 83], tremolo_mandolin_note,
                        releaseVolEnv=timecents(0.35), reverbEffectsSend=250))
    add(1, multisampled("Mandolin", [55, 62, 69, 76, 83], mandolin_note,
                        releaseVolEnv=timecents(0.6), reverbEffectsSend=250))
    add(2, multisampled("Detuned EPiano", [36, 48, 60, 72, 84], epiano_note,
                        releaseVolEnv=timecents(0.5), reverbEffectsSend=200))
    add(3, multisampled("Reversed Piano", [48, 60, 72], reversed_piano_note,
                        releaseVolEnv=timecents(0.05), reverbEffectsSend=350))
    add(4, multisampled("Distorted Bass", [28, 40, 52], distorted_bass_note,
                        releaseVolEnv=timecents(0.12), reverbEffectsSend=50))
    add(5, multisampled("Tape Pad", [36, 48, 60, 72], tape_pad_note,
                        attackVolEnv=timecents(0.6), releaseVolEnv=timecents(2.0),
                        reverbEffectsSend=300, initialFilterFc=abs_cents(4500)))
    add(6, multisampled("Sub Drone", [24, 36], sub_drone_note,
                        attackVolEnv=timecents(1.5), releaseVolEnv=timecents(3.0),
                        initialAttenuation=80,
                        reverbEffectsSend=100))

    # Metal kit: keys 36..47, two keys per hit
    kit_zones = []
    for i, (nm, data) in enumerate(metal_kit()):
        root = 36 + 2 * i
        s = Sample(nm, data, SR, root, 0, None)
        kit_zones.append(zone(s, root, root + 1, sampleModes=LOOP_NONE,
                              releaseVolEnv=timecents(3.0), reverbEffectsSend=400))
    add(8, Instrument("Sheet Metal Kit", kit_zones))

    data, loop = metal_scrape()
    s = Sample("Scrape", data, SR, 60, 0, loop)
    add(9, Instrument("Metal Scrape", [zone(s, 0, 127, sampleModes=LOOP_CONTINUOUS,
                                            releaseVolEnv=timecents(0.8),
                                            reverbEffectsSend=400)]))

    data, loop = tape_hiss()
    add(10, unpitched("Tape Hiss", data, loop, scaleTuning=0,
                      releaseVolEnv=timecents(1.0), attackVolEnv=timecents(0.3)))

    data, loop = radio_static()
    add(11, unpitched("Radio Static", data, loop,
                      releaseVolEnv=timecents(1.2), attackVolEnv=timecents(0.4),
                      reverbEffectsSend=150))

    hum, hum_loop = fridge_hum()
    house = Instrument("House Sounds", [
        zone(Sample("FridgeHum", hum, SR, 60, 0, hum_loop), 60, 60,
             sampleModes=LOOP_CONTINUOUS, releaseVolEnv=timecents(0.3),
             attackVolEnv=timecents(0.4), scaleTuning=0),
        zone(Sample("Tick", clock(3200), SR, 62, 0, None), 62, 62,
             sampleModes=LOOP_NONE, releaseVolEnv=timecents(0.3), reverbEffectsSend=300),
        zone(Sample("Tock", clock(2400), SR, 64, 0, None), 64, 64,
             sampleModes=LOOP_NONE, releaseVolEnv=timecents(0.3), reverbEffectsSend=300),
    ])
    add(12, house)

    write_sf2(path, presets, "Calder Falls",
              "Generated by build_calder.py. All samples synthesized with numpy.")
    return presets


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "Calder.sf2")
    presets = build(out)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, {len(presets)} presets)")
