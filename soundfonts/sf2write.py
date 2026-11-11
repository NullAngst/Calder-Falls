"""Minimal SoundFont 2.01 writer.

Writes mono 16-bit samples, instruments with key-ranged zones, and one preset
per instrument. That is all Calder.sf2 needs. I did not find a maintained
Python library that writes SF2 files (sf2utils and friends only read them),
so this is the one piece of the music chain we write ourselves.

Format reference: SoundFont Technical Specification 2.01, sections 5 to 8.
"""

import math
import struct
from dataclasses import dataclass, field

import numpy as np

# Generator operator numbers (spec section 8.1.2)
GEN = {
    "initialFilterFc": 8,
    "initialFilterQ": 9,
    "chorusEffectsSend": 15,
    "reverbEffectsSend": 16,
    "pan": 17,
    "delayVolEnv": 33,
    "attackVolEnv": 34,
    "holdVolEnv": 35,
    "decayVolEnv": 36,
    "sustainVolEnv": 37,
    "releaseVolEnv": 38,
    "instrument": 41,
    "keyRange": 43,
    "velRange": 44,
    "initialAttenuation": 48,
    "coarseTune": 51,
    "fineTune": 52,
    "sampleID": 53,
    "sampleModes": 54,
    "scaleTuning": 56,
    "exclusiveClass": 57,
    "overridingRootKey": 58,
}

LOOP_NONE = 0
LOOP_CONTINUOUS = 1
LOOP_THEN_RELEASE = 3


def timecents(seconds):
    """Seconds to SF2 timecents. 0.001 s is the practical floor."""
    seconds = max(seconds, 0.001)
    return int(round(1200 * math.log2(seconds)))


def abs_cents(hz):
    """Hz to SF2 absolute cents, used by initialFilterFc."""
    return int(round(1200 * math.log2(hz / 8.176)))


@dataclass
class Sample:
    name: str
    data: np.ndarray            # float, -1..1, mono
    rate: int
    root: int                   # MIDI key the sample sounds at
    correction: int = 0         # pitch correction in cents, -99..99
    loop: tuple | None = None   # (start, end) in samples, end exclusive


@dataclass
class Zone:
    sample: Sample
    key_lo: int = 0
    key_hi: int = 127
    gens: dict = field(default_factory=dict)


@dataclass
class Instrument:
    name: str
    zones: list


@dataclass
class Preset:
    name: str
    bank: int
    program: int
    instrument: Instrument


def _name20(name):
    raw = name.encode("ascii", "replace")[:19]
    return raw + b"\0" * (20 - len(raw))


def _chunk(cid, payload):
    if len(payload) % 2:
        payload += b"\0"
    return cid + struct.pack("<I", len(payload)) + payload


def _list(lid, *chunks):
    body = lid + b"".join(chunks)
    return b"LIST" + struct.pack("<I", len(body)) + body


def _zstr(text):
    raw = text.encode("ascii", "replace") + b"\0"
    if len(raw) % 2:
        raw += b"\0"
    return raw


def _gen_bytes(oper, value):
    if oper in (GEN["keyRange"], GEN["velRange"]):
        lo, hi = value
        return struct.pack("<HBB", oper, lo, hi)
    if oper in (GEN["instrument"], GEN["sampleID"], GEN["sampleModes"],
                GEN["overridingRootKey"], GEN["exclusiveClass"],
                GEN["scaleTuning"]):
        return struct.pack("<HH", oper, int(value))
    return struct.pack("<Hh", oper, int(max(-32768, min(32767, value))))


def _ordered(gens):
    """keyRange first, velRange second, sampleID/instrument last (spec 8.1.1)."""
    first = []
    rest = []
    last = []
    for name, value in gens.items():
        oper = GEN[name]
        if name == "keyRange":
            first.insert(0, (oper, value))
        elif name == "velRange":
            first.append((oper, value))
        elif name in ("sampleID", "instrument"):
            last.append((oper, value))
        else:
            rest.append((oper, value))
    return first + rest + last


def write_sf2(path, presets, bank_name, comment=""):
    # Collect unique instruments and samples in a stable order
    instruments = []
    for p in presets:
        if p.instrument not in instruments:
            instruments.append(p.instrument)
    samples = []
    for inst in instruments:
        for z in inst.zones:
            if z.sample not in samples:
                samples.append(z.sample)

    # sdta: each sample followed by 46 zero points (spec 6.1)
    smpl = bytearray()
    shdr = bytearray()
    pos = 0
    for s in samples:
        pcm = np.clip(np.asarray(s.data, dtype=np.float64), -1.0, 1.0)
        pcm = np.round(pcm * 32767).astype("<i2")
        n = len(pcm)
        smpl += pcm.tobytes() + b"\0" * (46 * 2)
        start = pos
        end = pos + n
        if s.loop:
            ls, le = s.loop
            loop_start, loop_end = pos + ls, pos + le
        else:
            loop_start, loop_end = start + 8, end - 8
        shdr += struct.pack("<20sIIIIIBbHH", _name20(s.name), start, end,
                            loop_start, loop_end, s.rate, s.root,
                            max(-99, min(99, s.correction)), 0, 1)
        pos = end + 46
    shdr += struct.pack("<20sIIIIIBbHH", _name20("EOS"), 0, 0, 0, 0, 0, 0, 0, 0, 0)

    # Instrument level
    inst_b = bytearray()
    ibag = bytearray()
    igen = bytearray()
    gen_count = 0
    bag_count = 0
    for inst in instruments:
        inst_b += struct.pack("<20sH", _name20(inst.name), bag_count)
        for z in inst.zones:
            ibag += struct.pack("<HH", gen_count, 0)
            bag_count += 1
            gens = dict(z.gens)
            gens["keyRange"] = (z.key_lo, z.key_hi)
            gens["sampleID"] = samples.index(z.sample)
            for oper, value in _ordered(gens):
                igen += _gen_bytes(oper, value)
                gen_count += 1
    inst_b += struct.pack("<20sH", _name20("EOI"), bag_count)
    ibag += struct.pack("<HH", gen_count, 0)
    igen += struct.pack("<HH", 0, 0)
    imod = b"\0" * 10

    # Preset level: one zone per preset pointing at its instrument
    phdr = bytearray()
    pbag = bytearray()
    pgen = bytearray()
    pgen_count = 0
    for i, p in enumerate(sorted(presets, key=lambda x: (x.bank, x.program))):
        phdr += struct.pack("<20sHHHIII", _name20(p.name), p.program, p.bank,
                            i, 0, 0, 0)
        pbag += struct.pack("<HH", pgen_count, 0)
        pgen += _gen_bytes(GEN["instrument"], instruments.index(p.instrument))
        pgen_count += 1
    phdr += struct.pack("<20sHHHIII", _name20("EOP"), 0, 0, len(presets), 0, 0, 0)
    pbag += struct.pack("<HH", pgen_count, 0)
    pgen += struct.pack("<HH", 0, 0)
    pmod = b"\0" * 10

    info = _list(
        b"INFO",
        _chunk(b"ifil", struct.pack("<HH", 2, 1)),
        _chunk(b"isng", _zstr("EMU8000")),
        _chunk(b"INAM", _zstr(bank_name)),
        _chunk(b"ICMT", _zstr(comment)),
        _chunk(b"ISFT", _zstr("calder-falls sf2write.py")),
    )
    sdta = _list(b"sdta", _chunk(b"smpl", bytes(smpl)))
    pdta = _list(
        b"pdta",
        _chunk(b"phdr", bytes(phdr)),
        _chunk(b"pbag", bytes(pbag)),
        _chunk(b"pmod", pmod),
        _chunk(b"pgen", bytes(pgen)),
        _chunk(b"inst", bytes(inst_b)),
        _chunk(b"ibag", bytes(ibag)),
        _chunk(b"imod", imod),
        _chunk(b"igen", bytes(igen)),
        _chunk(b"shdr", bytes(shdr)),
    )
    body = b"sfbk" + info + sdta + pdta
    with open(path, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", len(body)) + body)
