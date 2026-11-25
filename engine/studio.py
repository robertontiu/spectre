"""Beat studio: renders project.json into a mixed, mastered beat.

  python3 studio.py render [project.json]          render the whole beat (writes renders/vNNN.*)
  python3 studio.py render project.json --solo T   render only track T (and its sends)
  python3 studio.py listen                         ears on the latest render (overview)
  python3 studio.py listen --bars 17-24            zoom into a bar range (hi-res + timing roll)
  python3 studio.py listen --section hook1         zoom into a section
  python3 studio.py listen --mono / --lowpass      the 'squint' checks
  python3 studio.py listen --clarity [--section S] --genre G   stems: layer census, masking, EQ map (engine/clarity.py)
"""
import sys, os, json, time, glob, re, argparse
import numpy as np
import soundfile as sf
import pedalboard as pb
import pyloudnorm as pyln

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instruments as I
from hand import Hand, midi_to_hz

SR = I.SR
WORK = os.environ.get("BEAT_DIR", os.getcwd())
RENDERS = os.path.join(WORK, "renders")

DRUM_TYPES = set(I.DRUMS)
DEFAULT_GAIN = {"kokle": -7, "dudas": -13, "tridksnis": -12, "trembita": -9, "lira": -11, "cimbalom": -8, "fiddle": -9, "nai": -10, "darbuka": -6, "oud": -6, "ney": -10, "kick": -1, "snare": -4, "clap": -5, "hat": -13, "openhat": -15, "rim": -8, "shaker": -16,
                "snap": -8, "tom": -6, "crash": -14, "cowbell": -14, "808": -2, "bass": -4, "lead": -12,
                "ep": -9, "piano": -8, "pad": -14, "strings": -13, "choir": -14, "bell": -14, "musicbox": -12,
                "pluck": -10, "organ": -14, "sine": -10, "vinyl": -6, "tape": -6, "rain": -10}
DEFAULT_GAIN.update({"supersaw": -12, "trancebass": -6, "clubkick": -1, "kitkick": -2, "kitsnare": -2, "kittom": -6,
                     "kithat": -15, "kitride": -17, "kitcrash": -16, "eguitar": -11, "cleanguitar": -11, "ebass": -6,
                     "vox": -9})
DEFAULT_GAIN.update({"handclap": -5})
DEFAULT_GAIN.update({"singer": -9, "vox2": -9})
DEFAULT_GAIN.update({"violin": -8, "acguitar": -7, "toba": -4})
DEFAULT_GAIN.update({"celesta": -12, "glockenspiel": -12, "cello": -12, "viola": -10, "strings_section": -17,
                     "vibraphone": -14})
DEFAULT_GAIN.update({"polysynth": -12, "sub": -4, "kicksub": -1, "kickpunch": -8, "kickclick": -6, "metalhat": -13,
                     "air": -20})

# Opt-in production features (stacks, buses, returns, role EQ, ott/dyneq/clip/mseq, correlated humanizing) live in
# engine/mixbus.py; _CTX carries the render's events and genre to the fx that need them (dyneq, role EQ).
import mixbus as MB  # noqa: E402
_CTX = {"events": {}, "genre": None}


def _attach_lyrics(part, new, tname):
    """singer: a pattern part {"notes": ..., "lyrics": ...} puts one syllable on each note, in order."""
    if not (isinstance(part, dict) and part.get("lyrics")):
        return new
    import singer
    toks = singer.parse_lyrics(part["lyrics"])
    if len(toks) != len(new):
        print(f"warning: track '{tname}': {len(toks)} syllables for {len(new)} notes; extra notes hold the last "
              "syllable, extra syllables are dropped", file=sys.stderr)
    for i, e in enumerate(new):
        e["syl"] = toks[i] if i < len(toks) else "_"
    return new


# ------------------------------------------------------------------ helpers

def db(x):
    return 10 ** (x / 20)


def pan_stereo(mono, pan):
    pan = float(np.clip(pan, -1, 1))
    a = (pan + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)


def widen(st, width):
    if width <= 0:
        return st
    d = int(0.011 * SR)
    mid = (st[0] + st[1]) / 2
    side = (st[0] - st[1]) / 2
    delayed = np.concatenate([np.zeros(d, dtype=np.float32), mid[:-d]])
    side = side + (mid - delayed) * 0.5 * width
    return np.stack([mid + side, mid - side])


def wow_flutter(st, amount):
    n = st.shape[1]
    t = np.arange(n) / SR
    d = (0.0015 * amount * np.sin(2 * np.pi * 0.45 * t) + 0.0003 * amount * np.sin(2 * np.pi * 6.3 * t)) * SR
    idx = np.clip(np.arange(n) - d - 0.002 * SR * amount, 0, n - 1)
    return np.stack([np.interp(idx, np.arange(n), ch) for ch in st]).astype(np.float32)


def gate_curve(n, bpm, pattern, bars=1, depth=1.0, duty=0.8, smooth_ms=3.0):
    """Trance gate: a step pattern repeating from bar 1 (string length / bars = grid, like drum steps).
    Open steps (x, X, o, digits = level) stay open for `duty` of the step, then close to 1 - depth."""
    s = re.sub(r"[\s|]", "", pattern)
    steps = len(s)
    bar_n = 4 * 60.0 / bpm * SR
    step_n = bar_n * bars / steps
    lv = np.array([0.0 if c in ".-_" else {"X": 1.0, "x": 1.0, "o": 0.55, "g": 0.35}.get(c, int(c) / 9 if c.isdigit() else 1.0)
                   for c in s])
    pos = np.arange(n) / step_n
    k = np.floor(pos).astype(np.int64)
    frac = pos - k
    level = lv[k % steps] * (frac < duty)
    g = (1 - depth) + depth * level
    w = max(1, int(smooth_ms / 1000 * SR))
    if w > 1:
        from scipy.ndimage import uniform_filter1d
        g = uniform_filter1d(g, w)
    return g.astype(np.float32)


def room_fx(st, size=0.3, mix=0.25, damp=0.5):
    """Small-room ambience: early reflections (multi-tap, filtered) plus a short tail. For acoustic drums."""
    taps = [(0.0071, 0.55, -0.3), (0.0113, 0.45, 0.35), (0.0167, 0.38, -0.5), (0.0229, 0.3, 0.55), (0.0311, 0.24, -0.15),
            (0.0397, 0.18, 0.25)]
    n = st.shape[1]
    mono = st.mean(0)
    er = np.zeros((2, n), dtype=np.float32)
    k = 0.5 + 1.2 * size
    for d, g, pan in taps:
        i = int(d * k * SR)
        if i >= n:
            continue
        er[0, i:] += mono[:n - i] * g * (1 - pan) * 0.7
        er[1, i:] += mono[:n - i] * g * (1 + pan) * 0.7
    er = pb.Pedalboard([pb.HighpassFilter(150), pb.LowpassFilter(9000 - 5000 * damp)])(er, SR)
    tail = pb.Pedalboard([pb.Reverb(0.15 + 0.35 * size, damp, 1.0, 0.0, 1.0), pb.HighpassFilter(200)])(st, SR)
    wet = er + tail * 0.6
    return (st * (1 - mix * 0.5) + wet * mix).astype(np.float32)


def apply_fx(st, fx_list, bpm):
    """st: (2, n) float32. fx_list: list of dicts."""
    chain = []
    beat = 60.0 / bpm

    def flush(x):
        nonlocal chain
        if chain:
            x = pb.Pedalboard(chain)(x, SR)
            chain = []
        return x
    for fx in fx_list or []:
        k = fx["type"]
        if k in ("hpf", "lpf") and fx.get("slope"):  # steeper filters (opt-in; plain hpf/lpf stay first-order)
            st = MB.butter(flush(st), k, fx.get("hz", 120 if k == "hpf" else 5000), fx["slope"])
        elif k in ("ott", "dyneq", "clip", "mseq"):
            st = flush(st)
            if k == "ott":
                st = MB.ott(st, fx)
            elif k == "dyneq":
                st = MB.dyneq(st, fx, _CTX["events"])
            elif k == "clip":
                st = MB.clip(st, fx)
            else:
                st = MB.mseq(st, fx, lambda x, fl: apply_fx(x, fl, bpm))
        elif k == "hpf":
            chain.append(pb.HighpassFilter(fx.get("hz", 120)))
        elif k == "lpf":
            chain.append(pb.LowpassFilter(fx.get("hz", 5000)))
        elif k == "eq":
            chain.append(pb.PeakFilter(fx["hz"], fx.get("gain_db", 0), fx.get("q", 1.0)))
        elif k == "lowshelf":
            chain.append(pb.LowShelfFilter(fx.get("hz", 200), fx.get("gain_db", 0)))
        elif k == "highshelf":
            chain.append(pb.HighShelfFilter(fx.get("hz", 6000), fx.get("gain_db", 0)))
        elif k == "comp":
            chain.append(pb.Compressor(fx.get("threshold_db", -18), fx.get("ratio", 4), fx.get("attack_ms", 10), fx.get("release_ms", 120)))
        elif k == "drive":
            chain.append(pb.Distortion(fx.get("db", 10)))
        elif k == "bitcrush":
            chain.append(pb.Bitcrush(fx.get("bits", 10)))
        elif k == "chorus":
            chain.append(pb.Chorus(fx.get("rate", 0.8), fx.get("depth", 0.25), 7.0, 0.0, fx.get("mix", 0.5)))
        elif k == "phaser":
            chain.append(pb.Phaser(fx.get("rate", 0.5), fx.get("depth", 0.5), 1300, 0.0, fx.get("mix", 0.5)))
        elif k == "delay":
            chain.append(pb.Delay(fx.get("beats", 0.75) * beat, fx.get("feedback", 0.3), fx.get("mix", 0.25)))
        elif k == "reverb":
            chain.append(pb.Reverb(fx.get("size", 0.6), fx.get("damping", 0.5), fx.get("mix", 0.25), 1 - fx.get("mix", 0.25) * 0.5, 1.0))
        elif k == "gain":
            chain.append(pb.Gain(fx.get("db", 0)))
        elif k == "pitch":
            chain.append(pb.PitchShift(fx.get("semitones", 0)))
        elif k == "srr":
            chain.append(pb.Resample(fx.get("hz", 16000), pb.Resample.Quality.ZeroOrderHold))
        elif k in ("gate", "room"):
            st = flush(st)
            if k == "gate":
                st = st * gate_curve(st.shape[1], bpm, fx.get("pattern", "x.x.x.x.x.x.x.x."), fx.get("bars", 1),
                                     fx.get("depth", 1.0), fx.get("duty", 0.8), fx.get("smooth_ms", 3.0))
            else:
                st = room_fx(st, fx.get("size", 0.3), fx.get("mix", 0.25), fx.get("damping", 0.5))
            st = st.astype(np.float32)
        elif k in ("lofi", "tremolo", "sat", "width"):
            st = flush(st)
            if k == "lofi":
                a = fx.get("amount", 0.5)
                st = wow_flutter(st, a)
                st = pb.Pedalboard([pb.LowpassFilter(14000 - 9000 * a), pb.HighpassFilter(40 + 80 * a),
                                    pb.Resample(int(32000 - 14000 * a))])(st, SR)
                st = np.tanh(st * (1 + a)) / np.tanh(1 + a)
            elif k == "tremolo":
                t = np.arange(st.shape[1]) / SR
                rate = fx.get("rate", 4.0)
                dep = fx.get("depth", 0.3)
                st = st * np.stack([1 - dep * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)),
                                    1 - dep * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t + np.pi))])
            elif k == "sat":
                a = fx.get("amount", 0.3)
                st = np.tanh(st * (1 + 3 * a)) / np.tanh(1 + 3 * a)
            elif k == "width":
                st = widen(st, fx.get("amount", 0.5))
            st = st.astype(np.float32)
        else:
            raise ValueError(f"unknown fx type '{k}'")
    return flush(st).astype(np.float32)


def fade_gate(n, ranges, fade=0.012):
    """Gain curve that is 0 inside ranges (sample tuples), with short fades."""
    g = np.ones(n, dtype=np.float32)
    f = int(fade * SR)
    for a, b in ranges:
        a, b = max(0, a), min(n, b)
        if b <= a:
            continue
        g[a:b] = 0
        lo = max(0, a - f)
        g[lo:a] = np.minimum(g[lo:a], np.linspace(1, 0, a - lo))
        hi = min(n, b + f // 3)
        g[b:hi] = np.minimum(g[b:hi], np.linspace(0, 1, hi - b))
    return g


def block_lpf(st, a, b, f0, f1):
    """Sweep a low-pass from f0 to f1 over samples [a,b) (in place)."""
    from scipy import signal
    a, b = max(0, a), min(st.shape[1], b)
    B = 1024
    zis = [np.zeros((1, 2)), np.zeros((1, 2))]
    for s in range(a, b, B):
        fr = f0 * (f1 / f0) ** ((s - a) / max(b - a, 1))
        sos = signal.butter(2, min(max(fr, 30), SR * 0.45), btype="low", fs=SR, output="sos")
        e = min(s + B, b)
        for c in range(2):
            y, zis[c] = signal.sosfilt(sos, st[c, s:e], zi=zis[c])
            st[c, s:e] = y
    return st


def block_hpf(st, a, b, f0, f1):
    """Sweep a high-pass from f0 to f1 over samples [a,b) (in place). Trance builds thin the music out this way."""
    from scipy import signal
    a, b = max(0, a), min(st.shape[1], b)
    B = 1024
    zis = [np.zeros((1, 2)), np.zeros((1, 2))]
    for s in range(a, b, B):
        fr = f0 * (f1 / f0) ** ((s - a) / max(b - a, 1))
        sos = signal.butter(2, min(max(fr, 10), SR * 0.45), btype="high", fs=SR, output="sos")
        e = min(s + B, b)
        for c in range(2):
            y, zis[c] = signal.sosfilt(sos, st[c, s:e], zi=zis[c])
            st[c, s:e] = y
    return st


def limit(x, ceiling_db=-1.0, look=0.004, release=0.09):
    """Look-ahead peak limiter with smooth release. x: (2, n)."""
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    c = db(ceiling_db)
    peak = np.abs(x).max(0)
    need = np.minimum(1.0, c / (peak + 1e-9))
    w = max(1, int(look * SR))
    g = minimum_filter1d(need, size=2 * w + 1)
    # release: let gain recover slowly (computed on a decimated grid)
    D = 32
    gd = g[::D].copy()
    a = np.exp(-D / (release * SR))
    cur = 1.0
    for i in range(len(gd)):
        v = gd[i]
        cur = v if v < cur else v + (cur - v) * a
        gd[i] = cur
    g2 = np.repeat(gd, D)[:len(g)]
    g2 = np.minimum(g2, g)
    g2 = uniform_filter1d(g2, size=w)
    y = x * g2
    return np.clip(y, -c, c).astype(np.float32)


def tapestop(mix, a, b):
    """Slow playback to a halt over [a, b); silence after until b."""
    n = b - a
    if n <= 10:
        return mix
    r = np.linspace(1, 0, n) ** 1.3
    pos = a + np.cumsum(r)
    for c in range(2):
        mix[c, a:b] = np.interp(pos, np.arange(mix.shape[1]), mix[c])
    return mix


# ------------------------------------------------------------------ render

# Random streams. By default (every project made before 2026-11-25) the hand draws its humanizing from one generator
# seeded by the project seed, and every instrument draws from the shared module generator instruments.RNG, in the
# order tracks are scheduled and rendered: adding, removing or reordering a track shifts the random phases, timing
# and velocities of the others. A project with "seeds": "per-track" gives every track its own streams, seeded from
# the project seed and the track's name (the hand's and the instruments'), plus one for the transition fx bus, so a
# track renders the same whatever else is in the project. Opt-in, so every published project renders bit for bit
# as before.
def per_track_seeds(P):
    mode = P.get("seeds", "shared")
    if mode not in ("shared", "per-track"):
        raise ValueError(f'"seeds" must be "shared" (default) or "per-track", not {mode!r}')
    return mode == "per-track"


def track_rng(P, name, stream):
    """The generator of one track's stream (0 = the hand's, 1 = the instruments'), in per-track seed mode."""
    import zlib
    return np.random.default_rng([int(P.get("seed", 1)) & 0xFFFFFFFF, zlib.crc32(name.encode("utf-8")), stream])


def schedule(P, hand):
    """Expand arrangement into per-track event lists + section map."""
    tracks = P["tracks"]
    patterns = P["patterns"]
    per_track = per_track_seeds(P)
    shared_rng, rngs = hand.rng, {}

    def use(tname):  # per-track seeds: the hand draws from this track's own stream
        if per_track:
            if tname not in rngs:
                rngs[tname] = track_rng(P, tname, 0)
            hand.rng = rngs[tname]
    bar = hand.bar_sec()
    events = {k: [] for k in tracks}
    holds = {k: [] for k in tracks}  # texture on-ranges (sec)
    sections = []
    chord_state = {}
    t = 0.0
    bar_i = 0
    for sec in P["arrangement"]:
        bars = sec["bars"]
        s0 = t
        sections.append(dict(name=sec["name"], start=s0, end=s0 + bars * bar, bar0=bar_i + 1, bars=bars))
        fills = sec.get("fill") or {}
        fill_pat = patterns.get(fills["pattern"]) if isinstance(fills, dict) and fills.get("pattern") else None
        fill_bars = (fill_pat or {}).get("bars", 1)
        for pname in sec.get("play", []):
            if pname not in patterns:
                raise ValueError(f"section '{sec['name']}' plays unknown pattern '{pname}'")
            pat = patterns[pname]
            pb_ = pat.get("bars", 1)
            reps = int(np.ceil(bars / pb_))
            for r in range(reps):
                pstart_bar = r * pb_
                if pstart_bar >= bars:
                    break
                t0 = s0 + pstart_bar * bar
                for tname, part in pat.items():
                    if tname == "bars":
                        continue
                    if tname not in tracks:
                        raise ValueError(f"pattern '{pname}' uses unknown track '{tname}'")
                    in_fill = fill_pat is not None and tname in fill_pat and pstart_bar + pb_ > bars - fill_bars
                    tr = tracks[tname]
                    use(tname)
                    typ = tr["inst"]["type"]
                    new = []
                    if typ in I.TEXTURES:
                        holds[tname].append((t0, t0 + min(pb_, bars - pstart_bar) * bar))
                        continue
                    if typ in DRUM_TYPES:
                        new = hand.drum_events(part, pb_, t0, tr)
                    elif isinstance(part, dict) and "chords" in part:
                        cs = chord_state.setdefault(tname, {})
                        new = hand.chord_events(part, pb_, t0, tr, cs)
                    else:
                        spec = part["notes"] if isinstance(part, dict) else part
                        new = hand.note_events(spec, t0, tr)
                        new = _attach_lyrics(part, new, tname)
                    lim = s0 + bars * bar
                    if in_fill:
                        lim = min(lim, s0 + (bars - fill_bars) * bar)
                    events[tname] += [e for e in new if e["t"] < lim - 1e-4]
        if fill_pat is not None:
            t0 = s0 + (bars - fill_bars) * bar
            for tname, part in fill_pat.items():
                if tname == "bars":
                    continue
                tr = tracks[tname]
                use(tname)
                typ = tr["inst"]["type"]
                if typ in DRUM_TYPES:
                    new = hand.drum_events(part, fill_bars, t0, tr)
                elif isinstance(part, dict) and "chords" in part:
                    new = hand.chord_events(part, fill_bars, t0, tr, chord_state.setdefault(tname, {}))
                else:
                    new = hand.note_events(part["notes"] if isinstance(part, dict) else part, t0, tr)
                    new = _attach_lyrics(part, new, tname)
                events[tname] += new
        t += bars * bar
        bar_i += bars
    hand.rng = shared_rng
    if any(isinstance(tr.get("humanize"), dict) for tr in tracks.values()):  # opt-in correlated humanizing
        MB.apply_humanize(P, events, tracks, t, bar)
    if any(sec.get("bpm") for sec in P["arrangement"]):
        return _tempo_warp(P, hand, events, holds, sections, t)
    return events, holds, sections, t


def _tempo_warp(P, hand, events, holds, sections, total):
    """Per-section tempo: a section's "bpm" (a number, or [from, to] = a tempo ramp across the section, linear in
    beats) replaces the project bpm there. Events are scheduled on the project's grid first, then every time is
    mapped onto the real clock, so swing, humanizing, rolls and note lengths scale with the local tempo. Only runs
    when a section sets "bpm"; projects without it are untouched."""
    beat0 = 60.0 / P["bpm"]
    segs = []  # (nominal start, nominal end, real start, b0, b1, beats)
    real = 0.0
    for sec, S in zip(P["arrangement"], sections):
        b = sec.get("bpm") or P["bpm"]
        b0, b1 = (float(b[0]), float(b[-1])) if isinstance(b, (list, tuple)) else (float(b), float(b))
        U = S["bars"] * 4.0
        segs.append((S["start"], S["end"], real, b0, b1, U))
        real += _ramp_time(U, b0, b1, U)
    def W(t):
        for (a, e, r, b0, b1, U) in segs:
            if t < e or (a, e, r, b0, b1, U) == segs[-1]:
                if t < a and a == segs[0][0]:
                    return r + (t - a) / beat0 * 60.0 / b0
                u = (t - a) / beat0
                if u <= U:
                    return r + _ramp_time(u, b0, b1, U)
                return r + _ramp_time(U, b0, b1, U) + (u - U) * 60.0 / b1
        return t
    for name, evs in events.items():
        for ev in evs:
            t0 = ev["t"]
            ev["t"] = W(t0)
            if "dur" in ev:
                ev["dur"] = W(t0 + ev["dur"]) - ev["t"]
    for name in holds:
        holds[name] = [(W(a), W(b)) for a, b in holds[name]]
    for S, (a, e, r, b0, b1, U) in zip(sections, segs):
        S["start"], S["end"] = W(a), W(e)
        S["bpm"] = [b0, b1] if b0 != b1 else b0
        S["beat_start"], S["beat_end"] = 60.0 / b0, 60.0 / b1
    n16 = int(round(total / (beat0 / 4)))
    hand.grid16 = [round(W(k * beat0 / 4), 5) for k in range(n16 + 1)]
    return events, holds, sections, W(total)


def _ramp_time(u, b0, b1, U):
    """Seconds from the section start to beat u when the tempo moves linearly (in beats) from b0 to b1 over U beats."""
    if abs(b1 - b0) < 1e-9:
        return u * 60.0 / b0
    k = (b1 - b0) / U
    return 60.0 / k * np.log((b0 + k * u) / b0)


def _role_fx(tr, role=None):
    """The role EQ preset of a track or layer with `"eq"` ("auto" or a dict of overrides), from the project genre's
    map (engine/eqmaps.json via mixbus.role_eq). Nothing without "eq" (or with "eq": "none")."""
    spec = tr.get("eq")
    if not spec or spec == "none":
        return []
    role = role or tr.get("role")
    genre = (spec.get("genre") if isinstance(spec, dict) else None) or _CTX.get("genre")
    if not genre:
        _warn_once("eq-genre", 'warning: "eq": "auto" needs the project\'s "genre" (or "eq": {"genre": ...}); '
                   "role EQ presets skipped")
        return []
    fx = MB.role_eq(genre, role, spec)
    if not fx:
        _warn_once(f"eq-{genre}-{role}", f"warning: no EQ map entry for role '{role}' in genre '{genre}'")
    return fx


_WARNED = set()


def _warn_once(key, msg):
    if key not in _WARNED:
        _WARNED.add(key)
        print(msg, file=sys.stderr)


def _layer_events(evs, L, parent_is_drum):
    """A stack layer's copy of the parent's events: `notes` all / lowest / highest (per chord), `offset_ms`, `vel`
    (a factor), and for a tonal layer under drum steps a fixed `note` held `len` 16ths."""
    from hand import note_to_midi
    out = [dict(e) for e in evs]
    sel = L.get("notes", "all")
    if sel in ("lowest", "highest") and out and "midi" in out[0]:
        out.sort(key=lambda e: e["t"])
        groups, cur = [], [out[0]]
        for e in out[1:]:
            if e["t"] - cur[0]["t"] < 0.03:  # a chord's notes (spread a few ms by the hand)
                cur.append(e)
            else:
                groups.append(cur)
                cur = [e]
        groups.append(cur)
        pick = min if sel == "lowest" else max
        out = [pick(g, key=lambda e: e["midi"]) for g in groups]
    off = float(L.get("offset_ms", 0)) / 1000
    vs = float(L.get("vel", 1.0))
    for e in out:
        e["t"] = e["t"] + off
        if "vel" in e:
            e["vel"] = float(np.clip(e["vel"] * vs, 0.03, 1.0))
        if parent_is_drum and "midi" not in e and L.get("note"):
            e["midi"] = note_to_midi(L["note"])
            e["dur"] = float(L.get("len", 2)) * 60.0 / _CTX["bpm"] / 4
            e["glide"] = False
    return out


def stack_type(tr):
    """How a stack's pattern is read: as its own `inst` if it has one, else as its first layer's instrument."""
    if tr.get("inst"):
        return tr["inst"]["type"]
    return tr["layers"][0]["inst"]["type"]


def render_stack(name, tr, evs, holds, total_n, bpm):
    """A track with `"layers"`: every layer plays the track's notes with its own instrument, octave, level, pan,
    width, role EQ and fx; the layers are summed into the stack's bus, which runs the track's own `fx`, `gain_db`
    (no per-type default: the layers carry those), `pan` (balance) and `width`. Sends, sidechain, choke and section
    automation then act on the bus like on any track."""
    parent_is_drum = stack_type(tr) in DRUM_TYPES
    acc = np.zeros((2, total_n), dtype=np.float32)
    for i, L in enumerate(tr["layers"]):
        if L.get("mute"):
            continue
        lname = L.get("name") or f"layer{i + 1}"
        inst = dict(L["inst"])
        semis = 12 * float(L.get("octave", 0)) + float(L.get("semi", 0))
        if semis:
            inst["transpose"] = inst.get("transpose", 0) + semis
        role = L.get("role")
        fx = _role_fx(dict(L, eq=L.get("eq", "auto")), role) if role else []
        ltr = {"inst": inst, "gain_db": L.get("gain_db", 0), "pan": L.get("pan", 0), "width": L.get("width", 0),
               "fx": fx + list(L.get("fx") or [])}
        if _CTX.get("layer_rng"):
            _CTX["layer_rng"](f"{name}.{lname}")
        x = render_track(f"{name}.{lname}", ltr, _layer_events(evs, L, parent_is_drum), holds, total_n, bpm)
        if _CTX.get("layer_hook"):
            _CTX["layer_hook"](name, lname, role, x)
        acc += x
    st = acc * np.float32(db(tr.get("gain_db", 0)))
    p = float(np.clip(tr.get("pan", 0), -1, 1))
    if p:
        a = (p + 1) * np.pi / 4
        st = (st * np.array([[np.cos(a)], [np.sin(a)]]) * np.sqrt(2)).astype(np.float32)
    if tr.get("width"):
        st = widen(st, tr["width"])
    return apply_fx(st, _role_fx(tr) + list(tr.get("fx") or []), bpm)


def render_track(name, tr, evs, holds, total_n, bpm):
    if tr.get("layers"):
        return render_stack(name, tr, evs, holds, total_n, bpm)
    if tr.get("eq") and tr["eq"] != "none":
        tr = dict(tr, fx=_role_fx(tr) + list(tr.get("fx") or []))
    typ = tr["inst"]["type"]
    p = tr["inst"]
    mono = np.zeros(total_n, dtype=np.float32)
    st_buf = None
    if typ in DRUM_TYPES:
        fn = I.DRUMS[typ]
        if typ == "clap" and p.get("spread", 0.009) > 0.05:  # warning only: the sound stays as it was
            print(f"warning: track '{name}': clap spread={p['spread']} is in seconds (default 0.009 = 9 ms between "
                  "bursts); over 0.05 the bursts become separate hits off the beat. Use handclap (spread_ms) "
                  "for a truer clap", file=sys.stderr)
        cache = {}
        rr = int(p.get("rr", 4)) if typ in getattr(I, "ROUND_ROBIN", ()) else 0
        for j, e in enumerate(sorted(evs, key=lambda e: e["t"])):
            key = (round(e["vel"] * 24), round(e.get("ps", 0) * 4))
            if rr > 1:  # round-robin kit pieces: 12 velocity layers x rr variants
                key = (2 * round(e["vel"] * 12), key[1], j % rr)
            if key not in cache:
                cache[key] = fn(p, key[0] / 24, key[1] / 4)
            x = cache[key]
            i = max(0, int(e["t"] * SR))  # hits pushed before 0:00 play at 0:00
            if i >= total_n:
                continue
            m = min(len(x), total_n - i)
            if tr.get("choke"):
                mono[i:] *= 0  # monophonic: a new hit cuts the previous ring (open hats)
            mono[i:i + m] += x[:m]
    elif typ in I.MONO:
        evs = sorted(evs, key=lambda e: e["t"])
        notes = [dict(t0=max(0, int(e["t"] * SR)), n=int(e["dur"] * SR), f=midi_to_hz(e["midi"] + p.get("transpose", 0)),
                      vel=e["vel"], glide=e.get("glide", False)) for e in evs]
        for nt, e in zip(notes, evs):
            if "syl" in e:  # singer: the syllable on this note
                nt["syl"] = e["syl"]
            if "art" in e:  # violin: articulations written after the note length
                nt["art"] = e["art"]
        mono = I.mono_voice(typ, p, notes, total_n)
        if mono.ndim == 2:  # stereo voices (singer with a double): pan acts as balance
            st_buf, mono = mono, np.zeros(total_n, dtype=np.float32)
    elif typ in I.TONAL:
        fn = I.TONAL[typ]
        for e in evs:
            x = fn(p, midi_to_hz(e["midi"] + p.get("transpose", 0)), e["vel"], max(e["dur"], 0.02))
            i = max(0, int(e["t"] * SR))  # hits pushed before 0:00 play at 0:00
            if i >= total_n:
                continue
            if x.ndim == 2:  # stereo instruments (supersaw)
                if st_buf is None:
                    st_buf = np.zeros((2, total_n), dtype=np.float32)
                m = min(x.shape[1], total_n - i)
                st_buf[:, i:i + m] += x[:, :m]
                continue
            m = min(len(x), total_n - i)
            mono[i:i + m] += x[:m]
    elif typ in I.TEXTURES:
        if holds:
            src = I.TEXTURES[typ](p, total_n)
            g = np.zeros(total_n, dtype=np.float32)
            for a, b in holds:
                g[int(a * SR):int(b * SR)] = 1
            k = int(0.05 * SR)
            g = np.convolve(g, np.ones(k) / k, mode="same").astype(np.float32)
            mono = src * g
    else:
        raise ValueError(f"track '{name}': unknown instrument type '{typ}'")
    post = getattr(I, "POST", {}).get(typ)
    if post is not None:  # whole-track processor (guitar amp): sees the summed chord, like a real amp
        y = post(p, mono)
        if y.ndim == 2:
            st_buf = y if st_buf is None else st_buf + y
            mono = np.zeros(total_n, dtype=np.float32)
        else:
            mono = y
    gain = DEFAULT_GAIN.get(typ, -10) + tr.get("gain_db", 0)
    st = pan_stereo(mono * db(gain), tr.get("pan", 0)).astype(np.float32)
    if st_buf is not None:  # stereo sources: pan acts as balance
        a = (float(np.clip(tr.get("pan", 0), -1, 1)) + 1) * np.pi / 4
        st = st + (st_buf * db(gain) * np.array([[np.cos(a)], [np.sin(a)]]) * np.sqrt(2)).astype(np.float32)
    if tr.get("width"):
        st = widen(st, tr["width"])
    st = apply_fx(st, tr.get("fx"), bpm)
    return st


# Tracks a window render (`render(..., window=...)`, the ears' stem analysis) still renders whole and then crops:
# a sung phrase cut at the window's edge would be a new phrase to synthesize.
WHOLE_TYPES = {"singer"}


def _window(events, holds, sections, total, window, pre):
    """Events, holds and sections of the span [t0 - pre, t1), shifted so the span starts at 0 (a window render).
    Returns them with the new total and the offset."""
    t0, t1 = window
    off = max(0.0, t0 - pre)
    t1 = min(t1, total)
    ev = {k: [dict(e, t=e["t"] - off) for e in v if off - 1e-9 <= e["t"] < t1] for k, v in events.items()}
    ho = {k: [(max(a, off) - off, min(b, t1) - off) for a, b in v if b > off and a < t1] for k, v in holds.items()}
    se = [dict(S, start=S["start"] - off, end=S["end"] - off) for S in sections]
    return ev, ho, se, t1 - off, off


def _window_auto(st, au, a, b, n):
    """A section's automation in a window render, where the section may start before the window (a < 0) or end after
    it (b > n): the ramps and sweeps keep the values they have at the window's edges."""
    a1, b1 = max(a, 0), min(b, n)
    span = max(b - a, 1)

    def at(v0, v1, p, log=False):
        x = (p - a) / span
        return v0 * (v1 / v0) ** x if log else v0 + (v1 - v0) * x
    if au.get("mute"):
        st[:, a1:b1] = 0
    gdb = au.get("gain_db")
    if gdb is not None:
        g0, g1 = (gdb if isinstance(gdb, list) else [gdb, gdb])
        st[:, a1:b1] *= db(np.linspace(at(g0, g1, a1), at(g0, g1, b), b - a1)).astype(np.float32)[:b1 - a1]
    for key, fn, lo in (("lpf", block_lpf, 30), ("hpf", block_hpf, 10)):
        v = au.get(key)
        if v:
            f0, f1 = (v if isinstance(v, list) else [v, v])
            f0, f1 = max(f0, lo), max(f1, lo)
            st = fn(st, a1, b1, at(f0, f1, a1, True), at(f0, f1, b1, True))
    return st


def _prepare(P):
    """A stack track without its own `inst` reads its pattern as its first layer's instrument: give the scheduler a
    copy of the project where it has one (the project itself is not changed)."""
    if not any(tr.get("layers") and not tr.get("inst") for tr in P["tracks"].values()):
        return P
    tracks = {k: (dict(tr, inst={"type": stack_type(tr)}) if tr.get("layers") and not tr.get("inst") else tr)
              for k, tr in P["tracks"].items()}
    return dict(P, tracks=tracks)


def _sidechain(st, sc, events, total_n):
    g = np.ones(total_n, dtype=np.float32)
    depth, rel = sc.get("depth", 0.6), sc.get("release_ms", 140) / 1000
    k = np.arange(int(rel * 5 * SR)) / SR
    curve = 1 - depth * np.exp(-k / rel)
    att = int(0.003 * SR)
    curve[:att] = np.minimum(curve[:att], np.linspace(1, 1 - depth, att))
    for e in events[sc["source"]]:
        i = int(e["t"] * SR) - att
        if 0 <= i < total_n:
            m = min(len(curve), total_n - i)
            g[i:i + m] = np.minimum(g[i:i + m], curve[:m])
    st *= g
    return st


def _section_moves(P, name, st, sec_by_name, whole, total_n, beat):
    """Per-section automation and exits that touch the track (or bus) `name`."""
    for sec in P["arrangement"]:
        S = sec_by_name[sec["name"]]
        a, b = int(S["start"] * SR), int(S["end"] * SR)
        if whole is not None:  # window render: sections outside the span do nothing; clip the rest
            if b <= 0 or a >= total_n:
                continue
            au = (sec.get("auto") or {}).get(name)
            if au:
                st = _window_auto(st, au, a, b, total_n)
            a = max(a, 0)
        au = (sec.get("auto") or {}).get(name) if whole is None else None
        if au:
            if au.get("mute"):
                st[:, a:b] = 0
            gdb = au.get("gain_db")
            if gdb is not None:
                g0, g1 = (gdb if isinstance(gdb, list) else [gdb, gdb])
                st[:, a:b] *= db(np.linspace(g0, g1, b - a)).astype(np.float32)
            lpf = au.get("lpf")
            if lpf:
                f0, f1 = (lpf if isinstance(lpf, list) else [lpf, lpf])
                st = block_lpf(st, a, b, f0, f1)
            hpf = au.get("hpf")
            if hpf:
                f0, f1 = (hpf if isinstance(hpf, list) else [hpf, hpf])
                st = block_hpf(st, a, b, max(f0, 10), max(f1, 10))
        ex = sec.get("exit") or {}
        cut = ex.get("cut")
        bt_e = S.get("beat_end", beat)  # the local beat in a tempo-mapped section
        if cut and (name in cut.get("tracks", []) or (cut.get("tracks") == "all")):
            st *= fade_gate(total_n, [(b - int(cut["beats"] * bt_e * SR), b)])
        xl = ex.get("lpf")
        if xl and name in xl.get("tracks", []):
            st = block_lpf(st, b - int(xl["beats"] * bt_e * SR), b, 18000, xl.get("to_hz", 400))
    return st


def _named_sends(st, tr, returns_in, total_n):
    """`"sends": {"hall": 0.2, ...}`: into the project's named returns (mix.returns); `reverb_predelay_ms` applies."""
    for rn, amt in (tr.get("sends") or {}).items():
        if not amt:
            continue
        if rn not in returns_in:
            raise ValueError(f'send to unknown return "{rn}" (define it in mix.returns)')
        returns_in[rn] += st * amt


def _bus_order(buses):
    """Buses in processing order: a bus that feeds another (`"bus": "<name>"`) comes before it."""
    order, seen = [], set()

    def visit(b, path=()):
        if b in seen:
            return
        if b in path:
            raise ValueError(f"bus cycle: {' -> '.join(path + (b,))}")
        nxt = (buses.get(b) or {}).get("bus")
        if nxt:
            if nxt not in buses:
                raise ValueError(f'bus "{b}" feeds unknown bus "{nxt}"')
            visit(nxt, path + (b,))
        seen.add(b)
        order.append(b)
    for b in buses:
        visit(b)
    return order[::-1]


def _process_return(rn, cfg, x, beat, duck_env):
    """A named return (mix.returns): `type` reverb (size, damping, predelay_ms, width) or delay (beats, feedback,
    pingpong, offset_ms), then hpf / lpf (12 dB/oct; defaults 250 Hz / 7 kHz for reverbs, 300 Hz / 3.5 kHz for
    delays), `fx` (any fx chain: an eq cut at 300-600 Hz, ott...), `duck` ({key, depth_db, attack_ms, release_ms}:
    the return dips while the key plays), return_db."""
    typ = cfg.get("type", "reverb")
    x = MB.predelay(x, float(cfg.get("predelay_ms", 0)))
    if typ == "reverb":
        wet = pb.Pedalboard([pb.Reverb(cfg.get("size", 0.75), cfg.get("damping", 0.55), 1.0, 0.0,
                                       cfg.get("width", 1.0))])(x, SR)
        hp, lp = cfg.get("hpf", 250), cfg.get("lpf", 7000)
    elif typ == "delay":
        if cfg.get("pingpong"):
            wet = MB.pingpong(x, beat, cfg.get("beats", 0.75), cfg.get("feedback", 0.35), cfg.get("offset_ms", 0.0))
        else:
            d = cfg.get("beats", 0.75) * beat + cfg.get("offset_ms", 0.0) / 1000
            wet = pb.Pedalboard([pb.Delay(d, cfg.get("feedback", 0.35), 1.0)])(x, SR)
        hp, lp = cfg.get("hpf", 300), cfg.get("lpf", 3500)
    else:
        raise ValueError(f'return "{rn}": type must be reverb or delay')
    if hp:
        wet = MB.butter(wet, "hpf", hp, 12)
    if lp:
        wet = MB.butter(wet, "lpf", lp, 12)
    wet = apply_fx(wet.astype(np.float32), cfg.get("fx"), 60.0 / beat)
    du = cfg.get("duck")
    if du:
        if du.get("key") not in duck_env:
            raise ValueError(f'return "{rn}": duck key "{du.get("key")}" is not a track or bus')
        e = MB.follower_db(duck_env[du["key"]], du.get("attack_ms", 10.0), du.get("release_ms", 250.0))
        wet = wet * MB.duck_curve(e, du.get("depth_db", 6.0))[None, :].astype(np.float32)
    return (wet * db(cfg.get("return_db", -4))).astype(np.float32)


def render(P, solo=None, out_prefix=None, quiet=False, stem_hook=None, window=None, pre_roll=None, layer_hook=None):
    """Render a project. `stem_hook(name, st)` (optional) is called with every track's final stereo signal as it goes
    into the mix, and with the returns "(reverb)", "(delay)" and "(fx)"; it must not change them. `window=(t0, t1)`
    (seconds) renders only that span plus a pre-roll (default two bars) for the ears' stem analysis: the result
    starts `meta["window_offset"]` seconds into the track, has no quick master, and its random draws differ from a
    full render (the stems are the same sounds, not the same samples)."""
    t_start = time.time()
    P = _prepare(P)
    hand = Hand(P["bpm"], P.get("swing", 0.5), P.get("seed", 1))
    events, holds, sections, total = schedule(P, hand)
    whole, offset = None, 0.0
    if window is not None:
        whole = dict(events=events, holds=holds, total=total)
        pre = 2 * 4 * 60.0 / P["bpm"] if pre_roll is None else pre_roll
        events, holds, sections, total, offset = _window(events, holds, sections, total, window, pre)
    per_track = per_track_seeds(P)
    shared_rng = I.RNG
    _CTX.update(events=events, genre=P.get("genre"), bpm=P["bpm"], layer_hook=layer_hook,
                layer_rng=(lambda nm: setattr(I, "RNG", track_rng(P, nm, 1))) if per_track else None)
    tail = 3.0
    total_n = int((total + tail) * SR)
    tracks = P["tracks"]
    mix_cfg = P.get("mix", {})
    rv = mix_cfg.get("reverb", {})
    dl = mix_cfg.get("delay", {})
    rev_bus = np.zeros((2, total_n), dtype=np.float32)
    del_bus = np.zeros((2, total_n), dtype=np.float32)
    mix = np.zeros((2, total_n), dtype=np.float32)
    stems_rms = {}
    beat = 60.0 / P["bpm"]
    sec_by_name = {s["name"]: s for s in sections}
    buses = P.get("buses") or {}
    bus_in = {b: np.zeros((2, total_n), dtype=np.float32) for b in buses}
    returns_cfg = mix_cfg.get("returns") or {}
    returns_in = {r: np.zeros((2, total_n), dtype=np.float32) for r in returns_cfg}
    duck_keys = {(c.get("duck") or {}).get("key") for c in list(returns_cfg.values()) + [rv, dl]} - {None}
    duck_env = {}
    names = list(tracks)
    if solo:
        names = [solo]
    for name in names:
        tr = tracks[name]
        if tr.get("mute"):
            continue
        if per_track:
            I.RNG = track_rng(P, name, 1)
        if whole is not None and tr["inst"]["type"] in WHOLE_TYPES:  # window render: render whole, then crop
            full = render_track(name, tr, whole["events"][name], whole["holds"][name],
                                int((whole["total"] + tail) * SR), P["bpm"])
            a0 = int(round(offset * SR))
            st = np.zeros((2, total_n), dtype=np.float32)
            m_ = max(0, min(total_n, full.shape[1] - a0))
            st[:, :m_] = full[:, a0:a0 + m_]
            del full
        else:
            st = render_track(name, tr, events[name], holds[name], total_n, P["bpm"])
        # choke: another track's hits cut this track's ring (closed hat chokes the open hat)
        cb = tr.get("choke_by")
        if cb and cb in events:
            own = np.sort(np.array([e["t"] for e in events[name]] or [1e9]))
            ranges = []
            for e in events[cb]:
                tc = e["t"]
                k = np.searchsorted(own, tc + 0.012)
                prev_own = own[k - 1] if k > 0 else None
                if prev_own is None or prev_own > tc - 0.012:
                    continue  # nothing of ours ringing (or we hit together)
                nxt = own[k] if k < len(own) else total_n / SR
                ranges.append((int(tc * SR), int(nxt * SR) - int(0.002 * SR)))
            if ranges:
                st *= fade_gate(total_n, ranges, fade=0.008)
        # sidechain ducking from another track's hit times
        sc = tr.get("sidechain")
        if sc and sc.get("source") in events:
            st = _sidechain(st, sc, events, total_n)
        # per-section automation and exits that touch this track
        st = _section_moves(P, name, st, sec_by_name, whole, total_n, beat)
        pd_n = int(tr.get("reverb_predelay_ms", 0) / 1000 * SR)  # the reverb hears this track later
        if pd_n > 0 and tr.get("send_reverb", 0):
            rev_bus[:, pd_n:] += st[:, :-pd_n] * tr["send_reverb"]
        else:
            rev_bus += st * tr.get("send_reverb", 0)
        del_bus += st * tr.get("send_delay", 0)
        if tr.get("sends"):
            _named_sends(MB.predelay(st, tr.get("reverb_predelay_ms", 0)), tr, returns_in, total_n)
        if tr.get("bus"):  # a group bus: summed there, processed after every track
            if tr["bus"] not in bus_in:
                raise ValueError(f'track "{name}" routes to unknown bus "{tr["bus"]}" (define it in "buses")')
            bus_in[tr["bus"]] += st
        else:
            mix += st
        if name in duck_keys:
            duck_env[name] = st.mean(0)
        if stem_hook is not None:
            stem_hook(name, st)
        env = np.sqrt(np.convolve(st.mean(0) ** 2, np.ones(2205) / 2205, mode="same")[::2205])
        stems_rms[name] = env.tolist()
    # group buses ("buses"): each sums its tracks (and buses), then fx, gain, pan, width, sidechain, section moves and
    # sends, like a track, and goes on to the mix or to the bus it names
    for bname in _bus_order(buses):
        B = buses[bname] or {}
        st = bus_in[bname] * np.float32(db(B.get("gain_db", 0)))
        if B.get("pan"):
            a = (float(np.clip(B["pan"], -1, 1)) + 1) * np.pi / 4
            st = (st * np.array([[np.cos(a)], [np.sin(a)]]) * np.sqrt(2)).astype(np.float32)
        if B.get("width"):
            st = widen(st, B["width"])
        st = apply_fx(st, B.get("fx"), P["bpm"])
        sc = B.get("sidechain")
        if sc and sc.get("source") in events:
            st = _sidechain(st, sc, events, total_n)
        st = _section_moves(P, bname, st, sec_by_name, whole, total_n, beat)
        rev_bus += st * B.get("send_reverb", 0)
        del_bus += st * B.get("send_delay", 0)
        if B.get("sends"):
            _named_sends(st, B, returns_in, total_n)
        if B.get("bus"):
            bus_in[B["bus"]] += st
        else:
            mix += st
        if bname in duck_keys:
            duck_env[bname] = st.mean(0)
    # transition fx (risers, impacts, reverse cymbals) live on their own bus
    fxb = np.zeros((2, total_n), dtype=np.float32)
    if per_track:
        I.RNG = track_rng(P, "(fx)", 1)
    if not solo:
        for sec in P["arrangement"]:
            S = sec_by_name[sec["name"]]
            a, b = int(S["start"] * SR), int(S["end"] * SR)
            if whole is not None and (b <= 0 or a >= total_n):
                continue
            en = sec.get("enter") or {}
            ex = sec.get("exit") or {}

            def put(x, at, g):
                at = max(0, at)
                m = min(len(x), total_n - at)
                if m > 0:
                    fxb[:, at:at + m] += x[:m] * g
            if en.get("impact"):
                put(I.impact(), a, db(-6) * en["impact"])
            if en.get("crash"):
                put(I.crash({}, 1.0), a, db(-12) * en["crash"])
            bt_s, bt_e = S.get("beat_start", beat), S.get("beat_end", beat)
            if en.get("downlifter"):
                put(I.downlifter(en["downlifter"] * bt_s), a, db(-14))
            if ex.get("riser"):
                x = I.riser(ex["riser"] * bt_e)
                put(x, b - len(x), db(-14))
            if ex.get("reverse"):
                x = I.reverse_cymbal(ex["reverse"] * bt_e)
                put(x, b - len(x), db(-12))
            if ex.get("rise"):
                x = I.pitch_riser(ex["rise"] * bt_e)
                put(x, b - len(x), db(-18))
        mix += fxb * 0.9
        if stem_hook is not None and np.any(fxb):
            stem_hook("(fx)", fxb * 0.9)
        rev_bus += fxb * 0.4
        extra = ("fx", "duck", "predelay_ms", "hpf", "pingpong", "offset_ms", "width")
        if np.any(rev_bus):
            if any(k in rv for k in extra):  # opt-in return processing on the shared reverb
                wet = _process_return("reverb", dict(rv, type="reverb"), rev_bus, beat, duck_env)
                mix += wet
                if stem_hook is not None:
                    stem_hook("(reverb)", wet)
            else:
                wet = pb.Pedalboard([pb.HighpassFilter(250), pb.Reverb(rv.get("size", 0.75), rv.get("damping", 0.55), 1.0, 0.0, 1.0),
                                     pb.LowpassFilter(rv.get("lpf", 7000))])(rev_bus, SR)
                mix += wet * db(rv.get("return_db", -4))
                if stem_hook is not None:
                    stem_hook("(reverb)", wet * db(rv.get("return_db", -4)))
        if np.any(del_bus):
            if any(k in dl for k in extra):
                wet = _process_return("delay", dict(dl, type="delay", return_db=dl.get("return_db", -6)), del_bus, beat,
                                      duck_env)
                mix += wet
                if stem_hook is not None:
                    stem_hook("(delay)", wet)
            else:
                wet = pb.Pedalboard([pb.HighpassFilter(300), pb.Delay(dl.get("beats", 0.75) * beat, dl.get("feedback", 0.35), 1.0),
                                     pb.LowpassFilter(dl.get("lpf", 3500))])(del_bus, SR)
                mix += wet * db(dl.get("return_db", -6))
                if stem_hook is not None:
                    stem_hook("(delay)", wet * db(dl.get("return_db", -6)))
        for rn, cfg in returns_cfg.items():  # named returns (mix.returns)
            if np.any(returns_in[rn]):
                wet = _process_return(rn, cfg, returns_in[rn], beat, duck_env)
                mix += wet
                if stem_hook is not None:
                    stem_hook(f"({rn})", wet)
        # section-level whole-mix moves
        for sec in P["arrangement"]:
            S = sec_by_name[sec["name"]]
            a, b = int(S["start"] * SR), int(S["end"] * SR)
            if whole is not None and (b <= 0 or b > total_n):  # window render: only exits that end inside it
                continue
            ex = sec.get("exit") or {}
            bt_e = S.get("beat_end", beat)
            if ex.get("tapestop"):
                mix = tapestop(mix, b - int(ex["tapestop"] * bt_e * SR), b)
            if ex.get("silence"):
                mix *= fade_gate(total_n, [(b - int(ex["silence"] * bt_e * SR), b)])
    if per_track:
        I.RNG = shared_rng
    if whole is not None:  # window render: the premaster only (no quick master)
        meta = dict(bpm=P["bpm"], sections=sections, duration=total, window_offset=offset, stems_rms=stems_rms,
                    rms_hop=2205 / SR, render_sec=round(time.time() - t_start, 1), solo=solo, _premaster=mix)
        return mix, meta
    premaster = mix.copy()
    # master
    ms = P.get("master", {})
    chain = [pb.HighpassFilter(25)]
    if ms.get("glue", True):
        chain.append(pb.Compressor(ms.get("glue_threshold_db", -14), 2.0, 25, 200))
    mix = pb.Pedalboard(chain)(mix, SR)
    if ms.get("tape", 0):
        mix = wow_flutter(mix, ms["tape"] * 0.5)
        mix = np.tanh(mix * (1 + ms["tape"])) / np.tanh(1 + ms["tape"])
    if ms.get("sat", 0.15):
        a = ms.get("sat", 0.15)
        mix = (np.tanh(mix * (1 + 2 * a)) / np.tanh(1 + 2 * a)).astype(np.float32)
    # end fade
    fo = int(min(tail, 2.5) * SR)
    mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
    meter = pyln.Meter(SR)
    target = ms.get("lufs", -10.5)
    src = mix.copy()
    L0 = meter.integrated_loudness(src.T)
    if np.isfinite(L0) and not solo:  # solo renders keep their real level so tracks can be compared
        g = target - L0
        for _ in range(4):
            mix = limit(src * db(g), -1.0)
            L = meter.integrated_loudness(mix.T)
            if abs(L - target) < 0.3:
                break
            g += target - L
    mix = np.clip(mix, -1, 1).astype(np.float32)
    meta = dict(bpm=P["bpm"], sections=sections, duration=total, stems_rms=stems_rms, rms_hop=2205 / SR,
                events={k: [dict(t=round(e["t"], 4), v=round(e["vel"], 2), m=e.get("midi")) for e in v] for k, v in events.items()},
                render_sec=round(time.time() - t_start, 1), solo=solo)
    if getattr(hand, "grid16", None):  # tempo-mapped project: the real time of every 16th, for the ears
        meta["grid16"] = hand.grid16
    meta["_premaster"] = premaster
    return mix, meta


def next_version():
    os.makedirs(RENDERS, exist_ok=True)
    # count every versioned file (wav, json, mp3, png): WAVs are deleted at clean-up, the rest stay
    vs = [int(m.group(1)) for f in glob.glob(os.path.join(RENDERS, "v*"))
          for m in [re.match(r"v(\d+)\.", os.path.basename(f))] if m]
    return max(vs, default=0) + 1


def cmd_render(args):
    P = json.load(open(args.project))
    mix, meta = render(P, solo=args.solo)
    if args.solo:
        path = os.path.join(RENDERS, f"solo_{args.solo}.wav")
        os.makedirs(RENDERS, exist_ok=True)
    else:
        v = next_version()
        path = os.path.join(RENDERS, f"v{v:03d}.wav")
        json.dump(P, open(os.path.join(RENDERS, f"v{v:03d}.project.json"), "w"), indent=1)
    sf.write(path, mix.T, SR, subtype="PCM_16")
    pre = meta.pop("_premaster")
    if not args.solo:
        sf.write(path.replace(".wav", ".premaster.wav"), pre.T, SR, subtype="FLOAT")
    json.dump(meta, open(path.replace(".wav", ".meta.json"), "w"))
    if not args.solo:  # a solo render must not become "latest": listen should keep hearing the mix
        json.dump(dict(wav=path), open(os.path.join(RENDERS, "latest.json"), "w"))
    m, s = divmod(meta["duration"], 60)
    print(f"rendered {os.path.basename(path)}  {int(m)}:{s:04.1f}  ({meta['render_sec']}s)")
    print("sections:", ", ".join(f"{x['name']}[bars {x['bar0']}-{x['bar0'] + x['bars'] - 1}]" for x in meta["sections"]))
    if meta.get("grid16"):
        print("tempo:", ", ".join(f"{x['name']} {x['bpm']}" for x in meta["sections"]))


def main():
    import signal
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # piping into head must not crash
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("render")
    r.add_argument("project", nargs="?", default=os.path.join(WORK, "project.json"))
    r.add_argument("--solo")
    l = sub.add_parser("listen")
    l.add_argument("--bars")
    l.add_argument("--section")
    l.add_argument("--mono", action="store_true")
    l.add_argument("--lowpass", action="store_true")
    l.add_argument("--wav")
    l.add_argument("--phone", action="store_true",
                   help="phone-speaker check: top end vs the genre curve, noise-likeness, worst moments per section")
    l.add_argument("--genre", help="with --phone: the genre whose target curve to compare with (default hiphop); with "
                   "--clarity: the genre whose EQ map and target to check against")
    l.add_argument("--clarity", action="store_true",
                   help="stem analysis of a section (default: the loudest; --section NAME, --section all, --bars): "
                   "layer census, masked and own share per stem, occupancy, low-mid build-up, crest per region, "
                   "flags against the genre's EQ map (engine/eqmaps.json); writes clarity.json")
    m = sub.add_parser("master")
    m.add_argument("version", nargs="?", help="e.g. v027 (default: latest)")
    m.add_argument("--genre", help="genre configuration (engine/genres.json): trap, hiphop, trance, trance_radio, rock, joc, caroling, "
                   "latinpop, chamberscore; required unless --target is given; sets target, lufs, tp, eq and translate")
    m.add_argument("--lufs", type=float)
    m.add_argument("--tp", type=float)
    m.add_argument("--eq", type=float)
    m.add_argument("--translate", type=float)
    m.add_argument("--target", help="tonal target curve override (beat = the trap curve), e.g. trance_2015, hiphop_2015, "
                   "rock_2015, the reference curves in engine/targets.json, or the older hiphop, trance, rock")
    m.add_argument("--published", action="store_true",
                   help="the genre's settings from before its era target (what its released tracks were mastered with)")
    m.add_argument("--legacy-master", action="store_true",
                   help="master version 1: reproduces the masters released before 2026-11-24 exactly")
    a = ap.parse_args()
    if a.cmd == "render":
        cmd_render(a)
    elif a.cmd == "master":
        import subprocess
        v = a.version or os.path.basename(json.load(open(os.path.join(RENDERS, "latest.json")))["wav"])[:-4]
        pre = os.path.join(RENDERS, f"{v}.premaster.wav")
        if not os.path.exists(pre):
            raise SystemExit(f"no premaster for {v}: re-render it (studio.py render renders/{v}.project.json)")
        if a.genre is None and a.target is None:
            import master as _m
            raise SystemExit("master: no genre given. Use --genre " + "|".join(_m.load_genres()) +
                             " (see engine/genres.json and docs/ORCHESTRATION.md, Genre conventions).")
        flags = []
        for k in ("genre", "target", "lufs", "tp", "eq", "translate"):
            if getattr(a, k) is not None:
                flags += [f"--{k}", str(getattr(a, k))]
        if a.legacy_master:
            flags.append("--legacy-master")
        if a.published:
            flags.append("--published")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "master.py"), pre]
                       + flags, check=True)
        out = pre.replace(".premaster.wav", ".master.wav")
        mp3 = out.replace(".wav", ".mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-b:a", "320k", mp3], check=True)
        # the MP3 encoder adds inter-sample overshoot: measure the file that ships and keep it in the report
        import master as _m
        dec = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-f", "f32le", "-ac", "2", "-"],
                             capture_output=True, check=True).stdout
        tp_mp3 = round(_m.true_peak_db(np.frombuffer(dec, dtype=np.float32).reshape(-1, 2).T.astype(np.float64)), 2)
        rp = out.replace(".wav", ".report.json")
        rep = json.load(open(rp))
        rep["out"]["mp3_true_peak"] = tp_mp3
        json.dump(rep, open(rp, "w"), indent=1)
        print(f"mp3: {mp3}  (true peak of the MP3 {tp_mp3} dBTP)")
    elif a.cmd == "listen":
        import ear
        ear.listen(a, RENDERS)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
