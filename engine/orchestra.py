"""Orchestral and trailer sounds for the cinematic hybrid genre (docs/CINEMATIC_HYBRID.md "Engine mapping"; docs/MANUAL.md
"Orchestra and trailer"). Additive: used only when a track names one of these instruments or the `hall` return.
Random draws come from generators seeded per call (the module RNG of instruments.py at call time), so per-track seeds
give each track its own stream.

  brass        horns, trumpets, trombones, bass trombone, tuba as sections (players with scatter): an additive model
               whose harmonic levels are measured on recordings (engine/orchestra_winds.json, fitted by
               examples/production/cinematic/fit_winds.py: University of Iowa MIS and VSCO-2-CE), interpolated by
               pitch and dynamic, and brightening with the note's instantaneous level, as brass does (the louder, the
               more upper harmonics: +13 to +36 dB at 2 kHz from soft to loud in the measured layers). Attack times
               measured per instrument. Articulations: stab, sfz, swell, cresc, dim, rip, fall.
  woodwind     flute, oboe, clarinet, bassoon by the same model (Iowa ff anchors; softer = darker by a hand-tuned
               tilt), breath noise, vibrato.
  timpani      tuned membrane modes (the air-loaded ratios of Rossing) with decays fitted to recordings, a pitch
               glide after the stroke; rolls.
  bassdrum, taiko, suscymbal   concert bass drum (fitted to VSCO-2-CE), a taiko ensemble (hand-tuned from the
               membrane mode ratios), a suspended cymbal hit or roll swell (fitted to VSCO-2-CE).
  braam, impact, whoosh, shepard   the trailer effects family.
  vox2choir    several `vox2` voices on one part, each its own take, timing and pan: a wordless choir section.
  accordion    free reeds in two or three ranks (musette detune), bellows swell.
"""
import json
import os

import numpy as np
from scipy import signal

import instruments as I

SR = I.SR
TWO_PI = 2 * np.pi
HERE = os.path.dirname(os.path.abspath(__file__))
_WINDS = None


def _rng(*key):
    import zlib
    return np.random.default_rng([zlib.crc32(repr(key).encode()) & 0xFFFFFFFF, int(I.RNG.integers(0, 2 ** 31))])


def winds():
    global _WINDS
    if _WINDS is None:
        with open(os.path.join(HERE, "orchestra_winds.json")) as fh:
            _WINDS = json.load(fh)
        _WINDS["_grid"] = np.log2(np.array(_WINDS["grid_hz"]))
    return _WINDS


# ------------------------------------------------------------------ the measured wind model

# instruments whose recordings have one dynamic: the loud-minus-soft difference they borrow (brass) or a tilt (woodwinds)
DONOR = {"bass_trombone": "trombone"}
WOODWIND_TILT = 8.0   # dB per octave above 1 kHz at dyn 0, scaled by (1 - dyn) [H: woodwinds brighten less than brass]
SPEC = {  # players, pan width, scatter (ms, cents), release s, vibrato (semitones, Hz), breath noise dB re peak, range
    "horn": dict(players=4, width=0.5, spread_ms=14, cents=5, release=0.18, vib=(0.0, 5.0), noise=-42, lo=34, hi=77),
    "trumpet": dict(players=3, width=0.4, spread_ms=10, cents=4, release=0.12, vib=(0.04, 5.5), noise=-44, lo=52, hi=84),
    "trombone": dict(players=3, width=0.45, spread_ms=12, cents=5, release=0.14, vib=(0.0, 5.0), noise=-44, lo=40, hi=72),
    "bass_trombone": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.15, vib=(0.0, 5.0), noise=-44, lo=28, hi=65),
    "tuba": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.16, vib=(0.0, 5.0), noise=-46, lo=26, hi=60),
    "flute": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.10, vib=(0.10, 5.0), noise=-24, lo=60, hi=96),
    "oboe": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.08, vib=(0.08, 5.5), noise=-40, lo=58, hi=91),
    "clarinet": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.09, vib=(0.0, 5.0), noise=-40, lo=50, hi=91),
    "bassoon": dict(players=1, width=0.0, spread_ms=0, cents=0, release=0.10, vib=(0.04, 5.0), noise=-40, lo=34, hi=75),
}
SECTIONS = {"horns": "horn", "horn": "horn", "trumpets": "trumpet", "trumpet": "trumpet", "trombones": "trombone",
            "trombone": "trombone", "bass_trombone": "bass_trombone", "tuba": "tuba"}
WOODWINDS = ("flute", "oboe", "clarinet", "bassoon")
_ENV_CACHE = {}


def _anchor_curve(inst, f0, dyn):
    """The harmonic-level curve (dB on the 1/6-octave grid, re the strongest harmonic) at (f0, dyn): inverse-distance
    weights over the three nearest recorded notes in (log2 f0 / 0.5, dyn / 0.35)."""
    W = winds()
    data = W[DONOR.get(inst, inst)] if inst not in W else W[inst]
    A = data["anchors"]
    own_dyns = {a["dyn"] for a in A}
    use_dyn = dyn if len(own_dyns) > 1 else 1.0
    d = np.array([np.hypot(np.log2(f0 / a["f0"]) / 0.5, (use_dyn - a["dyn"]) / 0.35) for a in A])
    idx = np.argsort(d)[:3]
    w = 1 / (d[idx] ** 2 + 0.02)
    cur = sum(wi * np.array(A[i]["curve"]) for wi, i in zip(w, idx)) / w.sum()
    if len(own_dyns) == 1 and dyn < 1.0:  # recordings at one dynamic: borrow the softening
        donor = DONOR.get(inst)
        g = W["grid_hz"]
        if donor:
            hi = _anchor_curve(donor, f0, 1.0)
            lo = _anchor_curve(donor, f0, dyn)
            cur = cur + (lo - hi)
        else:
            x = np.log2(np.array(g) / 1000.0)
            cur = cur - (1 - dyn) * WOODWIND_TILT * np.clip(x, 0, 3)
    return cur


def _levels(inst, f0, K, dyns):
    """Harmonic levels (dB) for harmonics 1..K at each dynamic in `dyns`: (len(dyns), K)."""
    key = (inst, round(float(np.log2(f0)) * 48), K, tuple(dyns))
    if key in _ENV_CACHE:
        return _ENV_CACHE[key]
    W = winds()
    lf = np.log2(f0 * np.arange(1, K + 1))
    out = np.array([np.interp(lf, W["_grid"], _anchor_curve(inst, f0, dv)) for dv in dyns])
    if len(_ENV_CACHE) > 4000:
        _ENV_CACHE.clear()
    _ENV_CACHE[key] = out
    return out


def _attack(inst, f0):
    W = winds()
    d = W.get(inst) or W[DONOR[inst]]
    return float(np.clip(d["attack_ms_220"] * (f0 / 220.0) ** d["attack_exp"], 12.0, 250.0)) / 1000


DYNS = (0.2, 0.4, 0.6, 0.8, 1.0)


def wind_voice(inst, p, f, vel, dur, rng, art=()):
    """One player's note. Returns mono float64."""
    sp = SPEC[inst]
    art = set(art or ())
    dyn = float(np.clip(p.get("dyn", vel), 0.05, 1.0))
    att = _attack(inst, f) * float(p.get("attack_scale", 1.0))
    rel = float(p.get("release", sp["release"]))
    if "stab" in art or "stac" in art:
        dur = min(dur, float(p.get("stab_len", 0.22)))
        att *= 0.6
        rel = min(rel, 0.08)
    hold = I._n(dur)
    n = hold + I._n(rel * 3)
    t = np.arange(n) / SR
    # the level envelope (0..1): attack, hold, release
    env = np.clip(t / att, 0, 1) ** 1.5
    env[hold:] *= np.exp(-(t[hold:] - t[hold]) / max(rel, 1e-3))
    # the dynamic shape over the note
    shape = np.ones(n)
    T = max(dur, 1e-3)
    if "sfz" in art:
        shape = np.where(t < 0.25, 1.3 - 0.85 * t / 0.25, 0.45 + 0.55 * np.clip((t - 0.25) / max(T - 0.25, 0.05), 0, 1))
    elif "swell" in art or "cresc" in art:
        shape = 0.3 + 0.7 * np.clip(t / T, 0, 1) ** 1.5
    elif "dim" in art:
        shape = 1.0 - 0.7 * np.clip(t / T, 0, 1)
    elif "stab" in art:
        shape = 1.15 - 0.4 * np.clip(t / 0.15, 0, 1)
    dyn_t = np.clip(dyn * shape * np.maximum(env, 0.25), 0.05, 1.0)
    # pitch: an onset scoop from below, vibrato that fades in, rip and fall
    semis = np.zeros(n)
    if "rip" in art:
        semis += -9.0 * np.clip(1 - t / 0.16, 0, 1) ** 1.5
    else:
        semis += -0.25 * np.exp(-t / 0.035)   # brass and reeds settle onto the pitch from slightly below [H]
    if "fall" in art:
        fs = 0.6 * T
        semis += np.where(t > fs, -6.0 * np.clip((t - fs) / max(T - fs, 0.05), 0, 1) ** 2, 0.0)
        env = env * np.where(t > fs, np.clip(1 - (t - fs) / max(T - fs + rel, 0.05), 0, 1), 1.0)
    vd, vr = sp["vib"]
    vd = float(p.get("vibrato", vd))
    if vd > 0:
        semis += vd * np.sin(TWO_PI * vr * t + rng.uniform(0, TWO_PI)) * np.clip((t - 0.3) / 0.4, 0, 1)
    semis += float(p.get("cents", 0.0)) / 100
    fr = f * 2 ** (semis / 12)
    ph = np.cumsum(fr) / SR
    K = int(max(1, min(160, 12000.0 / f, (SR * 0.45) / (f * 2 ** (1 / 12)))))  # up to 12 kHz (the tuba's top too)
    L = _levels(inst, f, K, DYNS)                  # (5, K) dB
    # per-sample levels: interpolate between the five dynamic layers by the instantaneous dynamic
    pos = np.clip((dyn_t - DYNS[0]) / (DYNS[1] - DYNS[0]), 0, len(DYNS) - 1.0001)
    i0 = pos.astype(np.int64)
    fr_ = pos - i0
    y = np.zeros(n)
    ph0 = rng.uniform(0, TWO_PI, K)
    for k in range(K):
        lv = L[i0, k] * (1 - fr_) + L[i0 + 1, k] * fr_
        y += 10 ** (lv / 20) * np.sin(TWO_PI * (k + 1) * ph + ph0[k])
    # breath / lip noise, band-passed around the strongest region, following the level
    nz = rng.standard_normal(n)
    lo_f = min(max(f * 2, 600.0), 5000.0)
    nz = signal.sosfilt(signal.butter(2, [lo_f, min(lo_f * 4, SR * 0.45)], btype="band", fs=SR, output="sos"), nz)
    y += nz * 10 ** (sp["noise"] / 20) * 3.0 * (1 + 2 * ("rip" in art) * np.exp(-t / 0.15))
    gain = (0.15 + 0.85 * dyn_t) ** 1.6       # overall level with the dynamic [H: about 20 dB from pp to ff]
    y *= env * gain
    return y / 3.0


def wind_section(inst, p, f, vel, dur):
    """A section note: `players` takes of the same note, each a few cents and ms apart, spread across `width`."""
    sp = SPEC[inst]
    players = int(p.get("players", sp["players"]))
    width = float(np.clip(p.get("width", sp["width"]), 0, 1))
    spread = float(p.get("spread_ms", sp["spread_ms"]))
    cents = float(p.get("detune_cents", sp["cents"]))
    art = p.get("_art") or ()
    rng = _rng(inst, round(f, 2), round(vel, 3), round(dur, 3), int(p.get("seed", 1)))
    outs = []
    for j in range(players):
        dt = abs(rng.normal(0, spread)) / 1000 if spread > 0 else 0.0
        q = dict(p, cents=float(p.get("cents", 0.0)) + rng.normal(0, cents))
        y = wind_voice(inst, q, f, vel * rng.uniform(0.9, 1.0) if players > 1 else vel, dur, rng, art)
        d = int(dt * SR)
        if d:
            y = np.concatenate([np.zeros(d), y])
        outs.append(y)
    n = max(len(y) for y in outs)
    L = np.zeros(n)
    R = np.zeros(n)
    for j, y in enumerate(outs):
        pos = (j / max(players - 1, 1) - 0.5) * 2 * width if players > 1 else 0.0
        a = (pos + 1) * np.pi / 4
        L[:len(y)] += y * np.cos(a)
        R[:len(y)] += y * np.sin(a)
    return (np.stack([L, R]) * np.sqrt(2) / np.sqrt(players)).astype(np.float32)


def brass(p, f, vel, dur):
    sec = p.get("section", "horns")
    if sec not in SECTIONS:
        raise ValueError(f"brass: section must be one of {sorted(set(SECTIONS))}, not {sec!r}")
    return wind_section(SECTIONS[sec], p, f, vel, dur)


def woodwind(p, f, vel, dur):
    inst = p.get("instrument", "flute")
    if inst not in WOODWINDS:
        raise ValueError(f"woodwind: instrument must be one of {WOODWINDS}, not {inst!r}")
    return wind_section(inst, dict(p, players=p.get("players", 1)), f, vel, dur)


# ------------------------------------------------------------------ percussion

# timpani: the air-loaded membrane's modes, near 1 : 1.5 : 2 : 2.5 of the principal (Rossing, "Science of Percussion
# Instruments", 2000, ch. 1), with an inharmonic mode at 1.74 and others; ratios, levels (re the principal, 30 ms after
# the stroke) and T60s pooled (medians) over seven VSCO-2-CE timpani hits by examples/production/cinematic/fit_drums.py.
# The measured principals sit at 90-190 Hz: keep the notes within about F#2-G3.
TIMP = dict(ratios=[1.0, 1.496, 1.745, 2.022, 2.214, 2.49, 2.802], levels=[0.0, -3.2, -24.3, -13.4, -17.2, -19.0, -18.8],
            t60=[2.2, 3.98, 0.82, 5.5, 2.73, 6.12, 1.76], thump=0.35, thump_hz=0.55, glide=0.012)


# the residual layers (third-octave bands above the fitted modes): levels and T60s fitted closed-loop to VSCO-2-CE by
# examples/production/cinematic/fit_drums.py (filled below by that fit; empty = off)
# (5 passes: the timpani's median band levels within 1.5 dB of the recordings', the bass drum's within 2.5 dB, over
# the bands within 40 dB of the loudest; a band that needed more than +20 dB is held at +20)
TIMP_RES = dict(ratios=[0.5, 0.63, 0.794, 1.0, 1.26, 1.587, 2.0, 2.52, 3.175, 4.0, 5.04, 6.35, 8.0, 10.079, 12.699, 16.0,
                        20.159, 25.398, 32.0, 40.317, 50.797, 64.0],
                levels=[-47.0, -22.1, 20.0, -43.2, 9.4, -54.6, -36.9, -25.6, 3.0, 1.6, -0.2, -1.5, -2.7, -4.8, -20.1,
                        -44.3, -41.6, -51.2, -64.7, -79.5, -72.8, -70.2],
                t60=[2.43, 2.43, 2.03, 2.19, 4.08, 4.39, 5.67, 3.8, 2.66, 3.2, 2.69, 1.9, 1.31, 1.14, 0.95, 1.92, 6.0, 6.0,
                     6.0, 6.0, 6.0, 6.0])
BD_RES = dict(hz=[40.0, 50.4, 63.5, 80.0, 100.8, 127.0, 160.0, 201.6, 254.0, 320.0, 403.2, 508.0, 640.0, 806.3, 1015.9,
                  1280.0, 1612.7, 2031.9, 2560.0, 3225.4, 4063.7, 5120.0, 6450.8, 8127.5, 10240.0, 12901.6, 16255.0],
              levels=[20.0, -5.8, 20.0, -39.1, -38.4, -47.5, -62.8, -54.5, 7.7, 3.4, 0.5, 7.0, -0.2, 1.5, -5.9, -16.3,
                      -10.3, -15.4, -20.3, -23.2, -36.3, -68.6, -75.1, -81.7, -87.1, -89.6, -73.7],
              t60=[1.17, 2.66, 2.18, 1.65, 1.82, 3.18, 2.2, 2.67, 2.36, 3.27, 2.16, 1.44, 0.98, 0.62, 0.68, 0.72, 0.63,
                   0.57, 0.57, 0.6, 0.59, 0.75, 5.45, 6.0, 6.0, 6.0, 5.98])


def _residual(fc, levels, t60, n, rng, vel, bright=0.0):
    """The head's dense upper modes and the stick, as one layer: noise in third-octave bands at `fc` (Hz), each at its
    level (dB, fitted) and with its own T60, brighter with velocity (`bright` dB per octave above 500 Hz at vel 1)."""
    t = np.arange(n) / SR
    src = rng.standard_normal(n)
    y = np.zeros(n)
    for c, lv, d in zip(fc, levels, t60):
        if c * 2 ** (1 / 6) >= SR * 0.45:
            continue
        b = signal.sosfilt(signal.butter(2, [c * 2 ** (-1 / 6), c * 2 ** (1 / 6)], btype="band", fs=SR, output="sos"), src)
        tilt = bright * (vel - 0.9) * max(0.0, np.log2(c / 500.0))
        y += b * 10 ** ((lv + tilt) / 20) * np.exp(-6.9 * t / max(d, 0.01))
    return y * np.clip(t / 0.0005, 0, 1)


def _membrane(f, vel, ratios, levels, t60, n, rng, glide=0.0, thump=0.0, thump_ratio=0.5, stick=0.15):
    t = np.arange(n) / SR
    x = np.zeros(n)
    g = 1 + glide * np.exp(-t / 0.08) * vel          # the head's pitch falls as the stroke's extra tension relaxes
    bright = 0.4 + 0.6 * vel
    for r, lv, d in zip(ratios, levels, t60):
        fm = f * r
        if fm > SR * 0.45:
            continue
        a = 10 ** ((lv - (1 - bright) * 6 * np.log2(r + 1e-9)) / 20)
        x += a * np.sin(TWO_PI * np.cumsum(fm * g) / SR + rng.uniform(0, TWO_PI)) * np.exp(-6.9 * t / d)
    if thump > 0:
        x += thump * np.sin(TWO_PI * f * thump_ratio * t) * np.exp(-t / 0.06)
    k = min(n, I._n(0.008))
    x[:k] += I.bp(rng.standard_normal(k).astype(np.float32), 800, 6000) * np.exp(-t[:k] / 0.0015) * stick * vel
    x *= np.clip(t / 0.0008, 0, 1)
    return x


def timpani(p, f, vel, dur):
    """A timpano at the note's pitch (keep it within about C2-G3). `roll`: a long note with "/roll" (or "roll": true)
    is a single-stroke roll at `roll_rate` strokes per second (18), swelling with "/cresc"."""
    q = dict(TIMP)
    q.update({k: v for k, v in p.items() if k in TIMP})
    rng = _rng("timp", round(f, 2), round(vel, 3), round(dur, 3), int(p.get("seed", 1)))
    art = set(p.get("_art") or ())
    roll = "roll" in art or p.get("roll")
    n = I._n(dur + max(q["t60"]) * 0.8 if roll else max(q["t60"]) * 1.2)
    y = np.zeros(n)
    hits = [0.0]
    if roll:
        rate = float(p.get("roll_rate", 18.0))
        hits = list(np.arange(0, dur, 1 / rate))
    for i, h in enumerate(hits):
        v = vel
        if roll:
            v = vel * (0.35 + 0.65 * (h / max(dur, 1e-3)) if "cresc" in art else 0.8) * rng.uniform(0.85, 1.0)
        s = int((h + (rng.normal(0, 0.004) if roll and i else 0)) * SR)
        s = max(s, 0)
        m = n - s
        if m <= 0:
            continue
        y[s:] += _membrane(f, v, q["ratios"], q["levels"], q["t60"], m, rng, q["glide"], q["thump"], q["thump_hz"])
        if TIMP_RES["levels"]:
            y[s:] += _residual([f * r for r in TIMP_RES["ratios"]], TIMP_RES["levels"], TIMP_RES["t60"], m, rng, v,
                               float(p.get("bright", 3.0))) * v
    k = I._n(0.08)
    y[-k:] *= np.linspace(1, 0, k)  # the cut at the end of the ring, faded
    return (y * 0.5).astype(np.float32)


# concert bass drum: the strongest mode at 83-88 Hz and the modes above it (pooled over three VSCO-2-CE velocity
# layers, examples/production/cinematic/fit_drums.py): a loosely tuned, inharmonic membrane
BASSDRUM = dict(f=85.0, ratios=[1.0, 1.3, 1.55, 1.65, 1.85, 2.0, 2.4], levels=[0.0, -4.0, -7.0, -9.0, -9.0, -8.0, -16.0],
                t60=[1.6, 1.5, 1.4, 1.2, 1.5, 1.3, 2.1], noise=0.3)


def bassdrum(p, vel, ps=0.0):
    """Concert bass drum (gran cassa): a large, loosely tuned membrane (ideal-membrane mode ratios), fitted to
    VSCO-2-CE's bass drum. `tune` (85 Hz), `decay` (1.0: x the fitted decays), `beater` (0.3: felt to hard)."""
    q = dict(BASSDRUM)
    f = float(p.get("tune", q["f"])) * 2 ** (ps / 12)
    dec = float(p.get("decay", 1.0))
    rng = _rng("bd", round(vel, 3), round(ps, 2), int(p.get("seed", 1)))
    n = I._n(max(q["t60"]) * dec * 1.2)
    x = _membrane(f, vel, q["ratios"], q["levels"], [d * dec for d in q["t60"]], n, rng, 0.02, 0.0, 0.5,
                  stick=float(p.get("beater", 0.3)))
    t = np.arange(n) / SR
    if BD_RES["levels"]:
        nz = _residual([c * f / q["f"] for c in BD_RES["hz"]], BD_RES["levels"], [d * dec for d in BD_RES["t60"]], n,
                       rng, vel, float(p.get("bright", 3.0)))
    else:
        nz = I.lp(rng.standard_normal(n).astype(np.float32), 400) * np.exp(-t / 0.08) * q["noise"] * vel
    y = (x + nz) * vel * 0.6
    k = I._n(0.08)
    y[-k:] *= np.linspace(1, 0, k)
    return y.astype(np.float32)


def taiko(p, vel, ps=0.0):
    """A taiko ensemble hit: `players` (3) large drums (`tune` 72 Hz, each a little apart) struck within `spread_ms`
    (12) of each other; membrane modes with a short decay (`decay` 0.6 s) and a hard stick. Hand-tuned [H]: the
    ideal-membrane ratios and the size of a nagado-daiko; no recording was available to fit."""
    players = int(p.get("players", 3))
    spread = float(p.get("spread_ms", 12.0))
    f0 = float(p.get("tune", 72.0)) * 2 ** (ps / 12)
    dec = float(p.get("decay", 0.6))
    rng = _rng("taiko", round(vel, 3), round(ps, 2), int(p.get("seed", 1)))
    n = I._n(dec * 2.5 + 0.06)
    y = np.zeros(n)
    for j in range(players):
        s = int(abs(rng.normal(0, spread)) / 1000 * SR) if j else 0
        f = f0 * 2 ** (rng.normal(0, 0.6) / 12)
        m = n - s
        y[s:] += _membrane(f, vel * rng.uniform(0.85, 1.0), BASSDRUM["ratios"], [0, -3, -6, -9, -10, -12, -14],
                           [dec, dec * 0.7, dec * 0.55, dec * 0.5, dec * 0.4, dec * 0.35, dec * 0.3], m, rng, 0.04, 0.4,
                           0.6, stick=0.5)
    return (y * vel * 0.55 / np.sqrt(players)).astype(np.float32)


# suspended cymbal, fitted to VSCO-2-CE (examples/production/cinematic/fit_drums.py): the spectrum peaks around
# 500 Hz-1 kHz, with a second peak near 4 kHz under a hard mallet, and falls on average 7.8 dB per octave above 1 kHz
# struck with a hard mallet, 12.6 dB per octave in a soft-mallet roll; T60 5.9 s at 1 kHz, 3.5 s at 4 kHz, 2.5 s at 8 kHz (about 5.9 s x (f / 1 kHz)^-0.4).
SUSCYM = dict(lo=250.0, hi=16000.0, slope_hit=-7.8, slope_roll=-12.6, t60=5.9, partials=200)
# the partials' spectral envelope per stroke (dB at third octaves from 250 Hz), fitted closed-loop to VSCO-2-CE's hard-
# mallet hit and soft-mallet crescendo roll by fit_drums.py `cymbal` (the straight slopes above are what a track gets
# when it sets `slope` itself): 8 damped passes, 4 strokes averaged; the hit within about 2 dB of the recording per
# band, the swell within 0.5 dB
SUSCYM_BANDS = [250.0 * 2 ** (k / 3) for k in range(19)]
SUSCYM_ENV = {"hit": [-16.9, -19.0, -8.6, 7.8, 0.4, 1.2, 11.1, -0.1, -2.9, 5.2, 5.3, 12.0, 12.9, 11.4, 7.6, 2.1, 1.6, -15.1,
                      -24.9],
              "swell": [-0.9, -16.7, -3.2, 6.3, -1.0, -3.2, 2.7, -10.7, -7.9, 1.3, 1.1, 1.4, 5.7, 1.7, -5.9, -11.2, -16.3,
                        -30.0, -34.2]}
_CYM = {}


def suscymbal(p, f, vel, dur):
    """Suspended cymbal (pitch ignored): `mode` "swell" (default: a soft-mallet roll that crescendos over the note and
    rings on: the swell into a downbeat; place the note so that it ends on the downbeat) or "hit" (one hard-mallet
    stroke). `decay` (5.9: T60 in s at 1 kHz), `ring` (6 s after the note: then a 0.3 s fade), `slope` (dB per octave
    above 1 kHz: -12.6 swell, -7.8 hit)."""
    q = dict(SUSCYM)
    mode = p.get("mode", "swell")
    slope = float(p.get("slope", q["slope_roll"] if mode == "swell" else q["slope_hit"]))
    rng = _rng("cym", round(vel, 3), round(dur, 3), int(p.get("seed", 1)))
    key = int(q["partials"])
    if key not in _CYM:  # one fixed set of partials: the same cymbal on every note
        srng = np.random.default_rng(77)
        fr = np.exp(srng.uniform(np.log(q["lo"]), np.log(q["hi"]), key))
        _CYM[key] = (fr, srng.uniform(0.5, 1.0, key), srng.uniform(0.7, 1.3, key), srng.uniform(0, TWO_PI, key))
    fr, amp, dk, ph = _CYM[key]
    env = SUSCYM_ENV.get("swell" if mode == "swell" else "hit")
    if env and "slope" not in p:
        amp = amp * 10 ** (np.interp(np.log2(fr), np.log2(SUSCYM_BANDS), env) / 20)
    else:
        amp = amp * 10 ** (slope / 20 * np.maximum(np.log2(fr / 1000.0), 0)) * np.clip(fr / 500.0, 0, 1)
    t60 = float(p.get("decay", q["t60"]))
    ring = float(p.get("ring", 6.0))
    T = max(dur, 0.05) if mode == "swell" else 0.0
    n = I._n(T + ring)
    t = np.arange(n) / SR
    if mode == "swell":  # the roll: dense soft strokes rising to the note's end
        exc = np.where(t < T, (t / T) ** 2.2, 0.0) * rng.standard_normal(n)
    else:
        exc = np.zeros(n)
        k = I._n(0.003)
        exc[:k] = rng.standard_normal(k) * np.hanning(k)
    m = I._n(ring)
    tt = np.arange(m) / SR
    ir = np.zeros(m)
    for fk, ak, dd, pk in zip(fr, amp, dk, ph):
        ir += ak * np.sin(TWO_PI * fk * tt + pk) * np.exp(-6.9 * tt / (t60 * dd * (fk / 1000.0) ** -0.4))
    y = signal.oaconvolve(exc, ir)[:n]
    k = I._n(0.3)
    y[-k:] *= np.linspace(1, 0, k)
    y /= np.abs(y).max() + 1e-9
    return (y * vel * 0.5).astype(np.float32)


# ------------------------------------------------------------------ trailer effects

def braam(p, f, vel, dur):
    """The braam: low brass (trombones and tuba an octave under, sfz into a swell), a distorted saw layer and a sine
    sub, at the note's pitch (C2-G2 typical) for the note's length (1-3 s). `synth` (0.5) and `sub` (0.6) set the two
    layers against the brass."""
    tb = wind_section("trombone", dict(p, _art=["sfz"], players=3), f * 2, vel, dur)
    tu = wind_section("tuba", dict(p, _art=["sfz"], players=1), f, vel, dur)
    n = max(tb.shape[1], tu.shape[1])
    y = np.zeros((2, n))
    y[:, :tb.shape[1]] += tb
    y[:, :tu.shape[1]] += tu * 0.9
    t = np.arange(n) / SR
    env = np.clip(t / 0.03, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.3))
    swell = 0.6 + 0.4 * np.clip(t / max(dur, 0.1), 0, 1)
    rng = _rng("braam", round(f, 2), round(vel, 3), round(dur, 3))
    saw = sum(I.polyblep_saw(f * 2 ** (c / 1200), n, rng.random()) for c in (-12, 0, 12)).astype(np.float64) / 3
    saw = np.tanh(3 * saw) * env * swell
    saw = I.lp(saw.astype(np.float32), 1800).astype(np.float64)
    sub = np.sin(TWO_PI * f / 2 * t) * env
    s = float(p.get("synth", 0.5))
    u = float(p.get("sub", 0.6))
    y += np.stack([saw, saw]) * s * 0.25 + np.stack([sub, sub]) * u * 0.3
    return (y * vel).astype(np.float32)


def impact(p, vel, ps=0.0):
    """A trailer hit: a sine boom falling from `boom_hz` (70) to half of it, a noise crack, a low tail of `tail` s (2.5);
    send it to a hall."""
    rng = _rng("impact", round(vel, 3), int(p.get("seed", 1)))
    tail = float(p.get("tail", 2.5))
    n = I._n(tail + 0.2)
    t = np.arange(n) / SR
    f0 = float(p.get("boom_hz", 70.0)) * 2 ** (ps / 12)
    fr = f0 * (0.5 + 0.5 * np.exp(-t / 0.25))
    boom = np.sin(TWO_PI * np.cumsum(fr) / SR) * np.exp(-t / (tail / 5)) * np.clip(t / 0.002, 0, 1)
    crack = I.bp(rng.standard_normal(n).astype(np.float32), 300, 9000) * np.exp(-t / 0.03)
    rumble = I.lp(rng.standard_normal(n).astype(np.float32), 150) * np.exp(-t / (tail / 3)) * 0.6
    y = np.tanh(1.5 * (boom + 0.5 * crack + rumble))
    return (y * vel * 0.8).astype(np.float32)


def whoosh(p, f, vel, dur):
    """Air rushing past over the note's length (pitch ignored): band noise sweeping up then down (`peak` 0.6 of the
    way), panned across."""
    rng = _rng("whoosh", round(vel, 3), round(dur, 3))
    n = I._n(dur + 0.1)
    t = np.arange(n) / SR
    pk = float(p.get("peak", 0.6))
    x = np.clip(t / max(dur, 0.05), 0, 1)
    shape = np.where(x < pk, (x / pk) ** 2, np.exp(-(x - pk) / max(1 - pk, 0.05) * 3))
    fc = 300 * 2 ** (5 * shape)
    from bass import svf
    nz = rng.standard_normal(n)
    y = svf(nz, fc, np.full(n, 1.2), 1) * shape
    pan = np.clip(2 * x - 1, -1, 1) * float(p.get("pan_sweep", 0.8))
    a = (pan + 1) * np.pi / 4
    return (np.stack([y * np.cos(a), y * np.sin(a)]) * vel * 0.5).astype(np.float32)


def shepard(p, f, vel, dur):
    """A Shepard-tone riser over the note's length: `voices` (6) octave-spaced tones climbing `octaves_per_s` (0.25)
    under a fixed bell-shaped spectral window, so the pitch seems to rise without end (`direction` -1 falls)."""
    n = I._n(dur + 0.2)
    t = np.arange(n) / SR
    V = int(p.get("voices", 6))
    rate = float(p.get("octaves_per_s", 0.25)) * float(p.get("direction", 1))
    base = 40.0
    y = np.zeros(n)
    for v in range(V):
        pos = (v + rate * t) % V
        fr = base * 2 ** pos
        w = np.exp(-0.5 * ((pos - V / 2) / (V / 5)) ** 2)
        y += w * np.sin(TWO_PI * np.cumsum(fr) / SR)
    env = np.clip(t / 0.3, 0, 1) * np.clip((dur + 0.2 - t) / 0.2, 0, 1) * (0.3 + 0.7 * np.clip(t / max(dur, 0.1), 0, 1))
    y = y * env / np.sqrt(V)
    return (np.stack([y, y]) * vel * 0.4).astype(np.float32)


# ------------------------------------------------------------------ voices and reeds

def vox2choir(p, notes, total_n):
    """A wordless choir part from `vox2`: `voices` (4) takes of the same line, each its own `seed`, a timing scatter of
    `spread_ms` (18, on the vowel onsets), `detune_cents` (8) and a place in the section (`width` 0.6); vibrato a
    little narrower per voice (`vibrato` 0.2 by default: ensembles narrow vibrato for blend). Every `vox2` key works
    (voice, vowels, onset, rd, breath...)."""
    import singer as _s
    V = int(p.get("voices", 4))
    spread = float(p.get("spread_ms", 18.0))
    cents = float(p.get("detune_cents", 8.0))
    width = float(np.clip(p.get("width", 0.6), 0, 1))
    base = {k: v for k, v in p.items() if k not in ("voices", "spread_ms", "detune_cents", "width", "type")}
    base.setdefault("vibrato", 0.2)
    rng = np.random.default_rng(4242 + int(p.get("seed", 1)))
    out = np.zeros((2, total_n), dtype=np.float32)
    for j in range(V):
        q = dict(base, seed=int(p.get("seed", 1)) * 100 + j)
        q["vibrato"] = float(base["vibrato"]) * rng.uniform(0.7, 1.2)
        ns = []
        for nt in notes:
            d = dict(nt)
            d["t0"] = max(0, int(nt["t0"] + rng.normal(0, spread) / 1000 * SR))
            d["f"] = nt["f"] * 2 ** (rng.normal(0, cents) / 1200)
            d["vel"] = float(np.clip(nt["vel"] * rng.uniform(0.85, 1.0), 0.05, 1.0))
            ns.append(d)
        y = _s.vox2_line(q, ns, total_n)
        pos = (j / max(V - 1, 1) - 0.5) * 2 * width if V > 1 else 0.0
        a = (pos + 1) * np.pi / 4
        out[0] += (y * np.cos(a)).astype(np.float32)
        out[1] += (y * np.sin(a)).astype(np.float32)
    return out * np.sqrt(2) / np.sqrt(V)


def accordion(p, f, vel, dur):
    """Accordion: free reeds in `ranks` (2: two 8' reeds, the second `musette` cents (12) sharp; 3 adds a third as
    many cents flat), a reed spectrum (harmonic k at about -5 x log2(k) dB with a soft top, hand-tuned), a bellows
    attack of `attack` s (0.03) and an optional bellows `swell` (art "/swell"); release 0.06 s."""
    rng = _rng("acc", round(f, 2), round(vel, 3), round(dur, 3))
    ranks = int(p.get("ranks", 2))
    mus = float(p.get("musette", 12.0))
    att = float(p.get("attack", 0.03))
    n = I._n(dur + 0.1)
    t = np.arange(n) / SR
    hold = I._n(dur)
    env = np.clip(t / att, 0, 1)
    env[hold:] *= np.exp(-(t[hold:] - t[hold]) / 0.06)
    if "swell" in (p.get("_art") or ()):
        env *= 0.4 + 0.6 * np.clip(t / max(dur, 0.05), 0, 1)
    K = int(min(40, 9000 / f))
    y = np.zeros(n)
    dets = [0.0, mus, -mus][:ranks]
    for c in dets:
        fr = f * 2 ** (c / 1200) * (1 + 0.002 * np.sin(TWO_PI * 4.5 * t + rng.uniform(0, 6)))
        ph = np.cumsum(fr) / SR
        for k in range(1, K + 1):
            a = 10 ** ((-5 * np.log2(k) - 6 * max(0.0, np.log2(k * f / 3000))) / 20) * (1.0 if k % 2 else 0.8)
            y += a * np.sin(TWO_PI * k * ph + rng.uniform(0, TWO_PI))
    y += I.bp(rng.standard_normal(n).astype(np.float32), 1500, 6000) * 0.01
    y = y * env * (0.3 + 0.7 * vel) / np.sqrt(ranks)
    return (y * 0.25).astype(np.float32)
