"""Beat studio: renders project.json into a mixed, mastered beat.

  python3 studio.py render [project.json]          render the whole beat (writes renders/vNNN.*)
  python3 studio.py render project.json --solo T   render only track T (and its sends)
  python3 studio.py listen                         ears on the latest render (overview)
  python3 studio.py listen --bars 17-24            zoom into a bar range (hi-res + timing roll)
  python3 studio.py listen --section hook1         zoom into a section
  python3 studio.py listen --mono / --lowpass      the 'squint' checks
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
DEFAULT_GAIN = {"trembita": -9, "lira": -11, "cimbalom": -8, "fiddle": -9, "nai": -10, "darbuka": -6, "oud": -6, "ney": -10, "kick": -1, "snare": -4, "clap": -5, "hat": -13, "openhat": -15, "rim": -8, "shaker": -16,
                "snap": -8, "tom": -6, "crash": -14, "cowbell": -14, "808": -2, "bass": -4, "lead": -12,
                "ep": -9, "piano": -8, "pad": -14, "strings": -13, "choir": -14, "bell": -14, "musicbox": -12,
                "pluck": -10, "organ": -14, "sine": -10, "vinyl": -6, "tape": -6, "rain": -10}


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
        if k == "hpf":
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

def schedule(P, hand):
    """Expand arrangement into per-track event lists + section map."""
    tracks = P["tracks"]
    patterns = P["patterns"]
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
                typ = tr["inst"]["type"]
                if typ in DRUM_TYPES:
                    new = hand.drum_events(part, fill_bars, t0, tr)
                elif isinstance(part, dict) and "chords" in part:
                    new = hand.chord_events(part, fill_bars, t0, tr, chord_state.setdefault(tname, {}))
                else:
                    new = hand.note_events(part["notes"] if isinstance(part, dict) else part, t0, tr)
                events[tname] += new
        t += bars * bar
        bar_i += bars
    return events, holds, sections, t


def render_track(name, tr, evs, holds, total_n, bpm):
    typ = tr["inst"]["type"]
    p = tr["inst"]
    mono = np.zeros(total_n, dtype=np.float32)
    if typ in DRUM_TYPES:
        fn = I.DRUMS[typ]
        cache = {}
        for e in sorted(evs, key=lambda e: e["t"]):
            key = (round(e["vel"] * 24), round(e.get("ps", 0) * 4))
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
        mono = I.mono_voice(typ, p, notes, total_n)
    elif typ in I.TONAL:
        fn = I.TONAL[typ]
        for e in evs:
            x = fn(p, midi_to_hz(e["midi"] + p.get("transpose", 0)), e["vel"], max(e["dur"], 0.02))
            i = max(0, int(e["t"] * SR))  # hits pushed before 0:00 play at 0:00
            if i >= total_n:
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
    gain = DEFAULT_GAIN.get(typ, -10) + tr.get("gain_db", 0)
    st = pan_stereo(mono * db(gain), tr.get("pan", 0)).astype(np.float32)
    if tr.get("width"):
        st = widen(st, tr["width"])
    st = apply_fx(st, tr.get("fx"), bpm)
    return st


def render(P, solo=None, out_prefix=None, quiet=False):
    t_start = time.time()
    hand = Hand(P["bpm"], P.get("swing", 0.5), P.get("seed", 1))
    events, holds, sections, total = schedule(P, hand)
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
    names = list(tracks)
    if solo:
        names = [solo]
    for name in names:
        tr = tracks[name]
        if tr.get("mute"):
            continue
        st = render_track(name, tr, events[name], holds[name], total_n, P["bpm"])
        # sidechain ducking from another track's hit times
        sc = tr.get("sidechain")
        if sc and sc.get("source") in events:
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
        # per-section automation and exits that touch this track
        for sec in P["arrangement"]:
            S = sec_by_name[sec["name"]]
            a, b = int(S["start"] * SR), int(S["end"] * SR)
            au = (sec.get("auto") or {}).get(name)
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
            ex = sec.get("exit") or {}
            cut = ex.get("cut")
            if cut and (name in cut.get("tracks", []) or (cut.get("tracks") == "all")):
                st *= fade_gate(total_n, [(b - int(cut["beats"] * beat * SR), b)])
            xl = ex.get("lpf")
            if xl and name in xl.get("tracks", []):
                st = block_lpf(st, b - int(xl["beats"] * beat * SR), b, 18000, xl.get("to_hz", 400))
        rev_bus += st * tr.get("send_reverb", 0)
        del_bus += st * tr.get("send_delay", 0)
        mix += st
        env = np.sqrt(np.convolve(st.mean(0) ** 2, np.ones(2205) / 2205, mode="same")[::2205])
        stems_rms[name] = env.tolist()
    # transition fx (risers, impacts, reverse cymbals) live on their own bus
    fxb = np.zeros((2, total_n), dtype=np.float32)
    if not solo:
        for sec in P["arrangement"]:
            S = sec_by_name[sec["name"]]
            a, b = int(S["start"] * SR), int(S["end"] * SR)
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
            if en.get("downlifter"):
                put(I.downlifter(en["downlifter"] * beat), a, db(-14))
            if ex.get("riser"):
                x = I.riser(ex["riser"] * beat)
                put(x, b - len(x), db(-14))
            if ex.get("reverse"):
                x = I.reverse_cymbal(ex["reverse"] * beat)
                put(x, b - len(x), db(-12))
        mix += fxb * 0.9
        rev_bus += fxb * 0.4
        if np.any(rev_bus):
            wet = pb.Pedalboard([pb.HighpassFilter(250), pb.Reverb(rv.get("size", 0.75), rv.get("damping", 0.55), 1.0, 0.0, 1.0),
                                 pb.LowpassFilter(rv.get("lpf", 7000))])(rev_bus, SR)
            mix += wet * db(rv.get("return_db", -4))
        if np.any(del_bus):
            wet = pb.Pedalboard([pb.HighpassFilter(300), pb.Delay(dl.get("beats", 0.75) * beat, dl.get("feedback", 0.35), 1.0),
                                 pb.LowpassFilter(dl.get("lpf", 3500))])(del_bus, SR)
            mix += wet * db(dl.get("return_db", -6))
        # section-level whole-mix moves
        for sec in P["arrangement"]:
            S = sec_by_name[sec["name"]]
            a, b = int(S["start"] * SR), int(S["end"] * SR)
            ex = sec.get("exit") or {}
            if ex.get("tapestop"):
                mix = tapestop(mix, b - int(ex["tapestop"] * beat * SR), b)
            if ex.get("silence"):
                mix *= fade_gate(total_n, [(b - int(ex["silence"] * beat * SR), b)])
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
    if np.isfinite(L0):
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
    meta["_premaster"] = premaster
    return mix, meta


def next_version():
    os.makedirs(RENDERS, exist_ok=True)
    vs = [int(re.findall(r"v(\d+)", f)[0]) for f in glob.glob(os.path.join(RENDERS, "v*.wav"))]
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
    json.dump(dict(wav=path), open(os.path.join(RENDERS, "latest.json"), "w"))
    m, s = divmod(meta["duration"], 60)
    print(f"rendered {os.path.basename(path)}  {int(m)}:{s:04.1f}  ({meta['render_sec']}s)")
    print("sections:", ", ".join(f"{x['name']}[bars {x['bar0']}-{x['bar0'] + x['bars'] - 1}]" for x in meta["sections"]))


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
    m = sub.add_parser("master")
    m.add_argument("version", nargs="?", help="e.g. v027 (default: latest)")
    m.add_argument("--lufs", type=float, default=-11.0)
    m.add_argument("--tp", type=float, default=-1.0)
    m.add_argument("--eq", type=float, default=0.7)
    m.add_argument("--translate", type=float, default=0.5)
    a = ap.parse_args()
    if a.cmd == "render":
        cmd_render(a)
    elif a.cmd == "master":
        import subprocess
        v = a.version or os.path.basename(json.load(open(os.path.join(RENDERS, "latest.json")))["wav"])[:-4]
        pre = os.path.join(RENDERS, f"{v}.premaster.wav")
        if not os.path.exists(pre):
            raise SystemExit(f"no premaster for {v}: re-render it (studio.py render renders/{v}.project.json)")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "master.py"), pre,
                        "--lufs", str(a.lufs), "--tp", str(a.tp), "--eq", str(a.eq), "--translate", str(a.translate)], check=True)
        out = pre.replace(".premaster.wav", ".master.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-b:a", "320k", out.replace(".wav", ".mp3")], check=True)
        print("mp3:", out.replace(".wav", ".mp3"))
    elif a.cmd == "listen":
        import ear
        ear.listen(a, RENDERS)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
