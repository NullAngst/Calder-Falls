"""The audio engine: MIDI cues sequenced live through FluidSynth.

Signal chain, per block:
    MIDI events -> FluidSynth (SoundFonts, its own big dark reverb)
    -> PS2 filter (narrow to near mono, hold at 32 kHz, dark lowpass, bit-crunch)
    -> static bleed (AM narrowing, dropouts, radio static)
    -> master gain -> sounddevice

Nothing is prerecorded. The engine reads the cue's MIDI events itself and
sends them to the synth at the right sample, which is what lets the game
change tempo, detune, drop layers and bleed static into a cue while it plays.

Thread model: public methods only queue commands. The audio callback (or
render() when offline) applies them at the start of the next block, so the
synth is only ever touched from one thread.
"""

import ctypes
import glob
import math
import os
import queue

import numpy as np
from scipy import signal

from .. import _libs, paths
from . import cues as cue_table

_libs.prepare()
import fluidsynth  # noqa: E402
import mido  # noqa: E402

DEFAULT_RATE = 48000
DRUM_CHANNEL = 9

SYSTEM_BANKS = (
    "/usr/share/sounds/sf3/FluidR3Mono_GM.sf3",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/soundfonts/FluidR3_GM.sf2",
    "/usr/share/soundfonts/FluidR3_GM.sf3",
    "/usr/share/sounds/sf2/default-GM.sf2",
    "/usr/share/soundfonts/default.sf2",
)


def find_base_bank():
    """The General MIDI bank under Calder.sf2. First hit wins:
    $CALDER_BASE_BANK, a GeneralUser GS the player downloaded,
    the bundled FluidR3 Mono, then the usual system locations."""
    env = os.environ.get("CALDER_BASE_BANK")
    if env and os.path.isfile(env):
        return env
    pref = os.path.join(paths.user_dir(), "base_bank")
    if os.path.isfile(pref):
        with open(pref, encoding="utf-8") as fh:
            chosen = fh.read().strip()
        if chosen and os.path.isfile(chosen):
            return chosen
    for name in ("FluidR3Mono_GM.sf3", "FluidR3_GM.sf2", "FluidR3_GM.sf3"):
        p = os.path.join(paths.soundfont_dir(), name)
        if os.path.isfile(p):
            return p
    for p in SYSTEM_BANKS:
        if os.path.isfile(p):
            return p
    hits = sorted(glob.glob(os.path.join(paths.user_soundfont_dir(), "*.sf[23]")))
    if hits:
        return hits[0]
    return None


def find_calder_bank():
    p = os.path.join(paths.soundfont_dir(), "Calder.sf2")
    return p if os.path.isfile(p) else None


# ------------------------------------------------------------------ cue data

class CueData:
    """A MIDI file flattened to (seconds, message) pairs at its own tempo."""

    def __init__(self, cue):
        self.cue = cue
        mid = mido.MidiFile(cue.path)
        t = 0.0
        events = []
        for msg in mid:           # merged tracks, msg.time already in seconds
            t += msg.time
            if msg.is_meta:
                if msg.type == "marker":
                    events.append((t, ("marker", msg.text)))
                continue
            events.append((t, msg))
        self.length = max(t, 0.1)
        self.times = [e[0] for e in events]
        self.events = [e[1] for e in events]
        chans = {m.channel for m in self.events
                 if not isinstance(m, tuple) and m.type == "note_on"}
        self.channels = sorted(chans)
        self.layers = sorted({cue_table.layer_of(c) for c in chans} - {None},
                             key=cue_table.LAYER_ORDER.index)


# ------------------------------------------------------------------ effects

class Wander:
    """Piecewise-linear random wander between 0 and 1, continuous across blocks."""

    def __init__(self, rng, sr, rate_hz):
        self.rng = rng
        self.step = rate_hz / sr
        self.phase = 0.0
        self.a = rng.random()
        self.b = rng.random()

    def take(self, n):
        out = np.empty(n)
        i = 0
        while i < n:
            remain = int(math.ceil((1.0 - self.phase) / self.step))
            m = max(1, min(n - i, remain))
            ph = self.phase + self.step * np.arange(m)
            out[i:i + m] = self.a + (self.b - self.a) * np.clip(ph, 0.0, 1.0)
            self.phase += self.step * m
            i += m
            if self.phase >= 1.0:
                self.phase -= 1.0
                self.a, self.b = self.b, self.rng.random()
        return out


class PS2Filter:
    """The PS2 flavour, as far as a post-mix filter can get it.

    The SPU2 played mono samples, held at whatever rate the game used
    (32 kHz is typical), through Gaussian interpolation that took the top
    off. FluidSynth mixes every voice before Python sees it, so mono-sum
    per voice is approximated: Calder.sf2 and FluidR3 Mono are already
    all-mono, and the mix is narrowed until only panning is left.
    """

    def __init__(self, sr, hold_rate=32000, dark_hz=8500.0, bits=12, width=0.35):
        self.sr = sr
        self.ratio = hold_rate / sr
        self.width = width
        self.bits = bits
        self.pre = signal.butter(6, min(hold_rate * 0.46, sr * 0.45), "low", fs=sr, output="sos")
        self.post = signal.butter(2, dark_hz, "low", fs=sr, output="sos")
        self.zi_pre = np.zeros((self.pre.shape[0], 2, 2))
        self.zi_post = np.zeros((self.post.shape[0], 2, 2))
        self.count = 0
        self.last = np.zeros((1, 2))
        self.rng = np.random.default_rng(32000)

    def process(self, x):
        n = len(x)
        mid = (x[:, 0] + x[:, 1]) * 0.5
        side = (x[:, 0] - x[:, 1]) * 0.5 * self.width
        y = np.stack((mid + side, mid - side), axis=1)
        y, self.zi_pre = signal.sosfilt(self.pre, y, axis=0, zi=self.zi_pre)
        # sample and hold onto the 32 kHz grid
        k = self.count + np.arange(n)
        j = np.floor(k * self.ratio)
        src = np.ceil(j / self.ratio).astype(np.int64)
        local = src - self.count + 1
        ext = np.concatenate((self.last, y), axis=0)
        held = ext[np.clip(local, 0, n)]
        self.last = y[-1:].copy()
        self.count += n
        y, self.zi_post = signal.sosfilt(self.post, held, axis=0, zi=self.zi_post)
        q = float(2 ** (self.bits - 1))
        dither = (self.rng.random((n, 2)) - self.rng.random((n, 2))) / q
        return np.round(y * q + dither * q * 0.5) / q


class StaticBleed:
    """The static getting into the music: the band narrows to AM, the
    signal fades like a station at the edge of its range, and radio
    static sits on top. amount 0 is clean, 1 is barely there."""

    def __init__(self, sr, seed=1610):
        self.sr = sr
        self.rng = np.random.default_rng(seed)
        self.noise_bp = signal.butter(2, [250, 4200], "band", fs=sr, output="sos")
        self.music_bp = signal.butter(2, [380, 3400], "band", fs=sr, output="sos")
        self.crk_bp = signal.butter(2, [600, 7000], "band", fs=sr, output="sos")
        self.zi_n = np.zeros((self.noise_bp.shape[0], 2))
        self.zi_m = np.zeros((self.music_bp.shape[0], 2, 2))
        self.zi_c = np.zeros((self.crk_bp.shape[0], 2))
        self.fade = Wander(self.rng, sr, 1.8)
        self.drop = Wander(self.rng, sr, 0.9)
        self.pitch = Wander(self.rng, sr, 0.35)
        self.whistle_phase = 0.0

    def process(self, x, amount0, amount1):
        n = len(x)
        amt = np.linspace(amount0, amount1, n, endpoint=False)
        noise, self.zi_n = signal.sosfilt(self.noise_bp, self.rng.standard_normal(n), zi=self.zi_n)
        fade = 0.35 + 0.65 * self.fade.take(n) ** 1.5
        imp = np.zeros(n)
        hits = self.rng.random(n) < (40.0 / self.sr)
        imp[hits] = (self.rng.random(hits.sum()) - 0.5) * 6.0
        crackle, self.zi_c = signal.sosfilt(self.crk_bp, imp, zi=self.zi_c)
        wf = 1450.0 + 700.0 * (self.pitch.take(n) - 0.5)
        ph = self.whistle_phase + np.cumsum(wf) / self.sr
        self.whistle_phase = float(ph[-1] % 1.0)
        whistle = np.sin(2 * math.pi * ph) * 0.04
        static = np.tanh((noise * 1.6 * fade + crackle * 0.5 + whistle) * 1.4)
        narrow, self.zi_m = signal.sosfilt(self.music_bp, x, axis=0, zi=self.zi_m)
        drop = 1.0 - 0.75 * amt * (1.0 - self.drop.take(n)) ** 2
        a = amt[:, None]
        music = (x * (1.0 - 0.85 * a) + narrow * 1.6 * 0.85 * a) * drop[:, None]
        return music + (static * amt * 0.32)[:, None]


# ------------------------------------------------------------------ engine

class AudioEngine:
    def __init__(self, samplerate=DEFAULT_RATE, blocksize=1024, output=True,
                 base_bank=None, calder_bank=None):
        self.sr = int(samplerate)
        self.blocksize = blocksize
        self.base_bank = base_bank or find_base_bank()
        self.calder_bank = calder_bank or find_calder_bank()
        if not self.base_bank:
            raise RuntimeError("No General MIDI sound bank found. Install FluidR3 Mono "
                               "(fluidr3mono-gm-soundfont) or set CALDER_BASE_BANK.")
        if not self.calder_bank:
            raise RuntimeError("Calder.sf2 not found. Run soundfonts/build_calder.py.")
        self.synth = fluidsynth.Synth(gain=1.0, samplerate=self.sr, **{
            "synth.polyphony": 384,
            "synth.reverb.active": 1,
            "synth.chorus.active": 1,
        })
        self.base_id = self.synth.sfload(self.base_bank)
        self.calder_id = self.synth.sfload(self.calder_bank)
        if self.base_id < 0 or self.calder_id < 0:
            raise RuntimeError("FluidSynth could not load the sound banks.")
        # Big and dark, standing in for the SPU2's hardware reverb
        self.synth.set_reverb(roomsize=0.9, damping=0.82, width=0.65, level=0.75)
        self.synth.set_chorus(nr=3, level=0.6, speed=0.25, depth=6.0, type=0)
        self._write = fluidsynth._fl.fluid_synth_write_float
        self._write.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                                ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self._write.restype = ctypes.c_int

        self._cmds = queue.SimpleQueue()
        self._cache = {}
        # live controls (only the audio thread writes these)
        self.tempo = 1.0
        self.detune = 0.0
        self.ps2 = True
        self.static = 0.0
        self.volume = 0.9
        self.layers = {name: True for name in cue_table.LAYER_ORDER}
        # playback state
        self.data = None
        self.position = 0.0
        self.playing = False
        self.loop = True
        self._ev = 0
        self._active = set()
        self._file_vol = [100] * 16
        self._file_bend = [0] * 16
        self._sent_vol = [-1] * 16
        self._sent_bend = [None] * 16
        self._layer_gain = np.ones(16)
        self._fade = 1.0
        self._fade_target = 1.0
        self._fade_rate = 1.0
        self._hold = 0           # samples of forced silence
        self._pending = None     # (CueData, loop) to start after fade
        self._ps2_mix = 1.0
        self._cue_gain = 1.0
        self._pending_start = None
        self._static_cur = 0.0
        self.ps2_filter = PS2Filter(self.sr)
        self.bleed = StaticBleed(self.sr)
        self.error = None
        self.stream = None
        self.output_error = None
        if output:
            self._open_output()

    # -------------------------------------------------------------- output
    def _open_output(self):
        try:
            import sounddevice as sd
            self.stream = sd.OutputStream(samplerate=self.sr, blocksize=self.blocksize,
                                          channels=2, dtype="float32", latency="high",
                                          callback=self._callback)
            self.stream.start()
        except Exception as exc:  # no device, no PortAudio, busy device
            self.stream = None
            self.output_error = str(exc)

    def _callback(self, outdata, frames, _time, _status):
        try:
            outdata[:] = self.render_block(frames)
        except Exception as exc:
            outdata.fill(0)
            self.error = repr(exc)

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.synth.delete()

    # -------------------------------------------------------------- public API
    def load(self, name):
        if name not in self._cache:
            self._cache[name] = CueData(cue_table.get(name))
        return self._cache[name]

    def play(self, name, loop=None, fade=0.8):
        data = self.load(name)
        self._cmds.put(("play", data, data.cue.loop if loop is None else loop, fade))

    def stop(self, fade=0.8):
        self._cmds.put(("stop", fade))

    def set_tempo(self, factor):
        self._cmds.put(("tempo", max(0.25, min(2.0, float(factor)))))

    def set_detune(self, cents):
        self._cmds.put(("detune", max(-200.0, min(200.0, float(cents)))))

    def set_layer(self, layer, on):
        if layer not in cue_table.LAYERS:
            raise ValueError(f"unknown music layer: {layer}")
        self._cmds.put(("layer", layer, bool(on)))

    def set_ps2(self, on):
        self._cmds.put(("ps2", bool(on)))

    def set_static(self, amount):
        self._cmds.put(("static", max(0.0, min(1.0, float(amount)))))

    def set_volume(self, v):
        self._cmds.put(("volume", max(0.0, min(1.0, float(v)))))

    def apply_tag(self, tag):
        """Handle an Ink music tag (without the #). Returns False for tags
        that are not music tags, raises ValueError for a malformed one.
            music:cobb_road      music:stop
            music_layer:drums off
            music_detune:30      music_tempo:0.8
            music_static:0.4     music_ps2:off
        """
        tag = tag.strip().lstrip("#").strip()
        key, _, value = tag.partition(":")
        key = key.strip()
        value = value.strip()
        if not key.startswith("music"):
            return False
        try:
            if key == "music":
                if value == "stop":
                    self.stop()
                else:
                    self.play(value)
            elif key == "music_layer":
                layer, state = value.split()
                if state not in ("on", "off"):
                    raise ValueError(state)
                self.set_layer(layer, state == "on")
            elif key == "music_detune":
                self.set_detune(float(value))
            elif key == "music_tempo":
                self.set_tempo(float(value))
            elif key == "music_static":
                self.set_static(float(value))
            elif key == "music_ps2":
                if value not in ("on", "off"):
                    raise ValueError(value)
                self.set_ps2(value == "on")
            else:
                raise ValueError(key)
        except (ValueError, KeyError) as exc:
            raise ValueError(f"bad music tag '# {tag}': {exc}") from None
        return True

    # -------------------------------------------------------------- offline
    def render(self, seconds):
        frames = int(seconds * self.sr)
        out = np.empty((frames, 2), dtype=np.float32)
        i = 0
        while i < frames:
            n = min(self.blocksize, frames - i)
            out[i:i + n] = self.render_block(n)
            i += n
        return out

    def seek(self, seconds):
        """Jump straight to a point in the current cue. Offline use only:
        notes already sounding at that point are skipped."""
        self._drain()
        if self.data is None:
            return
        self._all_notes_off()
        self.position = seconds % self.data.length
        self._ev = 0
        while self._ev < len(self.data.times) and self.data.times[self._ev] < self.position:
            m = self.data.events[self._ev]
            if not isinstance(m, tuple) and m.type not in ("note_on", "note_off"):
                self._send(m)
            self._ev += 1

    # -------------------------------------------------------------- audio thread
    def _drain(self):
        while True:
            try:
                cmd = self._cmds.get_nowait()
            except queue.Empty:
                return
            kind = cmd[0]
            if kind == "play":
                _, data, loop, fade = cmd
                if self.playing and fade > 0:
                    self._pending = (data, loop)
                    self._fade_target = 0.0
                    self._fade_rate = 1.0 / (fade * self.sr)
                else:
                    self._start(data, loop)
            elif kind == "stop":
                self._pending = None
                if fade_time := cmd[1]:
                    self._fade_target = 0.0
                    self._fade_rate = 1.0 / (fade_time * self.sr)
                    self._pending = ("stop", None)
                else:
                    self._halt()
            elif kind == "tempo":
                self.tempo = cmd[1]
            elif kind == "detune":
                self.detune = cmd[1]
            elif kind == "layer":
                self.layers[cmd[1]] = cmd[2]
            elif kind == "ps2":
                self.ps2 = cmd[1]
            elif kind == "static":
                self.static = cmd[1]
            elif kind == "volume":
                self.volume = cmd[1]

    def _halt(self):
        self._all_notes_off()
        for ch in range(16):
            self.synth.all_sounds_off(ch)
        self.playing = False
        self._pending = None

    def _start(self, data, loop):
        self._all_notes_off()
        for ch in range(16):
            self.synth.all_sounds_off(ch)
            self.synth.cc(ch, 121, 0)
        self.synth.program_reset()
        self.data = data
        self.loop = loop
        self._cue_gain = 10 ** (data.cue.gain_db / 20.0)
        self.position = 0.0
        self._ev = 0
        self._file_vol = [100] * 16
        self._file_bend = [0] * 16
        self._sent_vol = [-1] * 16
        self._sent_bend = [None] * 16
        for ch in range(16):
            lay = cue_table.layer_of(ch)
            self._layer_gain[ch] = 1.0 if lay is None or self.layers.get(lay, True) else 0.0
        self.playing = True
        self._fade = 1.0
        self._fade_target = 1.0

    def _all_notes_off(self):
        for ch, key in list(self._active):
            self.synth.noteoff(ch, key)
        self._active.clear()

    def _send(self, m):
        if isinstance(m, tuple):
            if m[0] == "marker" and m[1] == "calder:cut":
                self._all_notes_off()
                for ch in range(16):
                    self.synth.all_sounds_off(ch)
                self._fade = 0.0
                self._hold = int(3.0 * self.sr)
            return
        t = m.type
        ch = getattr(m, "channel", 0)
        if t == "note_on" and m.velocity > 0:
            self.synth.noteon(ch, m.note, m.velocity)
            self._active.add((ch, m.note))
        elif t == "note_off" or t == "note_on":
            self.synth.noteoff(ch, m.note)
            self._active.discard((ch, m.note))
        elif t == "control_change":
            if m.control == 7:
                self._file_vol[ch] = m.value
                self._sent_vol[ch] = -1
            else:
                self.synth.cc(ch, m.control, m.value)
        elif t == "program_change":
            self.synth.program_change(ch, m.program)
        elif t == "pitchwheel":
            self._file_bend[ch] = m.pitch
            self._sent_bend[ch] = None

    def _update_mix(self, n):
        step = n / (0.15 * self.sr)
        detune_bend = int(round(self.detune / 200.0 * 8192))
        for ch in range(16):
            lay = cue_table.layer_of(ch)
            target = 1.0 if lay is None or self.layers.get(lay, True) else 0.0
            g = self._layer_gain[ch]
            if g != target:
                g = min(target, g + step) if target > g else max(target, g - step)
                self._layer_gain[ch] = g
            vol = int(round(self._file_vol[ch] * g))
            if vol != self._sent_vol[ch]:
                self.synth.cc(ch, 7, vol)
                self._sent_vol[ch] = vol
            bend = self._file_bend[ch] + (0 if ch == DRUM_CHANNEL else detune_bend)
            bend = max(-8192, min(8191, bend))
            if bend != self._sent_bend[ch]:
                self.synth.pitch_bend(ch, bend)
                self._sent_bend[ch] = bend

    def _synth_into(self, buf, start, count):
        if count <= 0:
            return
        view = buf[start:start + count]
        ptr = view.ctypes.data
        self._write(self.synth.synth, count, ptr, 0, 2, ptr, 1, 2)

    def _sequence(self, buf, n):
        d = self.data
        off = 0
        guard = 0
        while off < n:
            guard += 1
            if guard > 100000:
                raise RuntimeError("sequencer stalled")
            rate = self.tempo / self.sr            # file seconds per output sample
            if self._ev < len(d.times):
                to_ev = int(math.ceil((d.times[self._ev] - self.position) / rate))
            else:
                to_ev = n
            to_end = int(math.ceil((d.length - self.position) / rate))
            step = max(0, min(n - off, to_ev, to_end))
            if step:
                self._synth_into(buf, off, step)
                off += step
                self.position += step * rate
            while self._ev < len(d.times) and d.times[self._ev] <= self.position + 1e-9:
                self._send(d.events[self._ev])
                self._ev += 1
            if self.position >= d.length - 1e-9:
                if self.loop:
                    self._all_notes_off()
                    self.position -= d.length
                    self._ev = 0
                else:
                    self._all_notes_off()
                    self.playing = False
                    self._synth_into(buf, off, n - off)
                    return
            elif step == 0 and to_ev > 0 and to_end > 0:
                # nothing scheduled inside this block
                self._synth_into(buf, off, n - off)
                self.position += (n - off) * rate
                return

    def render_block(self, n):
        self._drain()
        self._update_mix(n)
        buf = np.zeros((n, 2), dtype=np.float32)
        if self.playing and self.data is not None:
            self._sequence(buf, n)
        else:
            self._synth_into(buf, 0, n)
        x = buf.astype(np.float64)

        # PS2 filter, crossfaded so the toggle never clicks
        target = 1.0 if self.ps2 else 0.0
        mix0 = self._ps2_mix
        mix1 = mix0 + max(-1.0, min(1.0, target - mix0)) * min(1.0, n / (0.05 * self.sr))
        wet = self.ps2_filter.process(x)
        w = np.linspace(mix0, mix1, n, endpoint=False)[:, None]
        x = x * (1.0 - w) + wet * w
        self._ps2_mix = mix1

        # static bleed
        s0 = self._static_cur
        s1 = s0 + (self.static - s0) * min(1.0, n / (0.3 * self.sr))
        if s0 > 1e-4 or s1 > 1e-4:
            x = self.bleed.process(x, s0, s1)
        self._static_cur = s1

        # fades, cut holds, master volume
        if self._hold > 0:
            self._hold = max(0, self._hold - n)
            g = np.zeros(n)
            if self._hold == 0:
                self._fade = 1.0
        else:
            f0 = self._fade
            if self._fade_target < f0:
                f1 = max(self._fade_target, f0 - self._fade_rate * n)
            else:
                f1 = min(1.0, f0 + n / (0.01 * self.sr))
            g = np.linspace(f0, f1, n, endpoint=False)
            self._fade = f1
            if f1 <= 0.0 and self._pending is not None:
                pending, self._pending = self._pending, None
                if pending[0] == "stop":
                    self._halt()
                else:
                    self._halt()
                    self._pending_start = pending
                    self._hold = int(0.6 * self.sr)
            elif self._hold == 0 and self._pending_start:
                data, loop = self._pending_start
                self._pending_start = None
                self._start(data, loop)
        x = x * (g * self.volume * self._cue_gain)[:, None]
        return np.tanh(x).astype(np.float32)


def render_cue_to_file(name, path, loops=1, tail=4.0, **controls):
    """Render one cue offline, the same chain the game uses, to .ogg/.wav/.flac."""
    import soundfile as sf
    eng = AudioEngine(output=False)
    try:
        for key, value in controls.items():
            getattr(eng, f"set_{key}")(value)
        data = eng.load(name)
        eng.play(name, loop=data.cue.loop)
        seconds = data.length * (loops if data.cue.loop else 1) + tail
        audio = eng.render(seconds)
    finally:
        eng.close()
    # Written in chunks: libsndfile's Vorbis encoder can crash on one huge write.
    with sf.SoundFile(path, "w", samplerate=eng.sr, channels=2) as fh:
        for i in range(0, len(audio), 16384):
            fh.write(audio[i:i + 16384])
    return audio
