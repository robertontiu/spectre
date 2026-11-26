"""Ears for form: section seams (`listen --seams`) and the through-line (`listen --coherence`).

Analysis only: reads a render (or any audio file with `--wav`) plus its section map (the render's meta.json, or
`--map` a meta.json or project.json), never renders and never touches the mix. docs/PRODUCTION.md "Seams and the
through-line" has the research behind it; docs/MANUAL.md "Seams and coherence" how to read it.

--seams: for every section boundary, the change across ten dimensions between the last two bars before and the
first two bars after (level, low end, spectral balance, brightness, kick pulse, onset density, groove, timbre,
harmony, width), each divided by a hand-tuned step size, so 1.0 = a clearly audible step, grouped into five
families (loudness, spectrum, rhythm, harmony, space) plus `streams`: an automated filter or gain of a sound
carried across the line that jumps at it. Then how much of the change was PREPARED: the share of each dimension's
move (from eight bars before to the new section) that already happened before the line, the dimensions that moved
AWAY from where the next section lands, the stems kept across the line, whether the new section returns to a state
heard before, and the devices the project declares (exit risers and sweeps, fills, entry hits, ramps). The gesture
is read too: a drop-out or drop-in (the energy dimensions moving together) and layering over a kept bed are the
arrangement's grammar and are never flagged; a swap (content changing at the same energy) is. A seam is flagged
when it is broad (several families, or a high score) and little of it was prepared, unless the incoming section
says `"seam": "cut"` (a deliberate hard cut, explained in the journal).

--coherence: per section, four fingerprints: the motifs (transposition-free melodic cells of four notes from the
notes of every pitched track, rhythm-free, so a riff moved to another instrument or played at half speed still
counts), the pitch-class profile (from the project's notes), the palette (which pitched stems play, from the
render's stem levels) and the timbre (audio MFCC and chroma). Section-by-section similarity matrices, the split
where the motif matrix breaks into two blocks (Foote's checkerboard) and the share of the second block's cells
already heard in the first. Flags a track that splits into two songs, unless the project says
`"form": {"acts": "intended"}`.

All thresholds are hand-tuned (2026-11-26), calibrated on sessions 016-020; treat flags as candidates to check by
ear and by zoom.
"""
import os, json
from collections import Counter
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 44100
FSR = 22050          # feature sample rate
HOP = 512
OUT = os.environ.get("BEAT_DIR", os.getcwd())

# step sizes per dimension: a change of one step is clearly audible (hand-tuned 2026-11-26; see PRODUCTION.md)
DIMS = [  # name, step, unit
    ("level", 3.0, "dB"),          # RMS level of the mix
    ("low end", 5.0, "dB"),        # 20-150 Hz relative to the mix
    ("balance", 2.5, "dB"),        # mean |change| of the four bands above 150 Hz, relative to the mix
    ("brightness", 0.4, "oct"),    # spectral centroid
    ("pulse", 4.0, "dB"),          # low-band (30-150 Hz) onset strength: the kick's pulse
    ("density", 0.8, "log2"),      # onsets per second (0.8 = x1.74)
    ("groove", 0.25, "1-cos"),     # onset strength on the 16 sixteenths of the bar
    ("timbre", 1.0, "z"),          # MFCC mean, in units of the track's own spread between 2-bar blocks (x3)
    ("harmony", 0.15, "1-cos"),    # chroma
    ("width", 4.0, "dB"),          # side/mid
]
# perceptual families: the dimensions inside one family move together (a hat entering moves balance, brightness,
# timbre at once), so a seam's breadth is counted in families, each family's step = its largest dimension's
FAMILIES = [("loudness", ("level",)), ("spectrum", ("low end", "balance", "brightness", "timbre")),
            ("rhythm", ("pulse", "density", "groove")), ("harmony", ("harmony",)), ("space", ("width",))]
BANDS = [(20, 150), (150, 400), (400, 2000), (2000, 6000), (6000, 18000)]
# genre norms: how many dimensions may step at once and how little preparation is still fine (hand-tuned). DJ
# genres prepare their seams over 8-32 bars; song genres and hip hop cut more (switch-ups, beat drops).
NORMS = {"default": dict(jumps=3, prep=0.35, score=5.0),
         "dj": dict(jumps=3, prep=0.35, score=5.0),
         "song": dict(jumps=3, prep=0.3, score=6.0)}
FAMILY = {"techno": "dj", "trance": "dj", "trance_radio": "dj", "psytrance": "dj", "dubstep": "dj",
          "trap": "song", "hiphop": "song", "hiphop_golden": "song", "boombap": "song", "rock": "song",
          "latinpop": "song", "joc": "song", "caroling": "song", "chamberscore": "song", "cinematic": "song"}
PREP_DEVICES = {"riser", "rise", "reverse", "lpf", "tapestop"}
SIGNAL_DEVICES = {"cut", "silence"}
LAND_DEVICES = {"impact", "crash", "downlifter"}


# ---------------------------------------------------------------- loading
def load_map(path, duration=None):
    """Sections (and stems, events) from a render's meta.json, or sections from a project.json."""
    d = json.load(open(path))
    if "sections" in d:
        return d
    bpm0 = d["bpm"]
    t, bar, secs = 0.0, 1, []
    for s in d["arrangement"]:
        b = s.get("bpm", bpm0)
        b = (b[0] + b[1]) / 2 if isinstance(b, list) else b
        dur = s["bars"] * 4 * 60 / b
        secs.append(dict(name=s["name"], start=t, end=t + dur, bar0=bar, bars=s["bars"]))
        t += dur
        bar += s["bars"]
    return dict(bpm=bpm0, sections=secs, duration=t, events={}, stems_rms={}, rms_hop=0.05)


def find_project(latest, meta_path, a):
    for p in (getattr(a, "map", None), meta_path.replace(".meta.json", ".project.json") if meta_path else None,
              os.path.join(OUT, "project.json")):
        if p and os.path.exists(p):
            d = json.load(open(p))
            if "arrangement" in d:
                return d
    return None


def bar_edges(meta):
    """Start time of every bar, from the sections (each section's bars split evenly) or the tempo map."""
    g = meta.get("grid16")
    if g:
        return np.array(g[::16])
    e = []
    for s in meta["sections"]:
        e += list(np.linspace(s["start"], s["end"], s["bars"] + 1)[:-1])
    e.append(meta["sections"][-1]["end"])
    return np.array(e)


def features(y, edges):
    """Per-bar features. y: stereo (2, n) at 44.1 kHz."""
    import librosa
    mono = librosa.resample(y.mean(0).astype(np.float32), orig_sr=SR, target_sr=FSR)
    S = np.abs(librosa.stft(mono, n_fft=2048, hop_length=HOP)) ** 2
    fr = librosa.fft_frequencies(sr=FSR, n_fft=2048)
    nfr = S.shape[1]
    tfr = np.arange(nfr) * HOP / FSR
    tot = S.sum(0) + 1e-12
    bands = np.array([S[(fr >= lo) & (fr < hi)].sum(0) for lo, hi in BANDS]) + 1e-12
    cent = (S * fr[:, None]).sum(0) / tot
    mel = librosa.feature.melspectrogram(S=S, sr=FSR, n_mels=64)
    mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel), n_mfcc=20)[1:]
    chroma = librosa.feature.chroma_stft(S=S, sr=FSR)
    on = librosa.onset.onset_strength(S=librosa.power_to_db(mel), sr=FSR, hop_length=HOP)
    lowb = (fr >= 30) & (fr < 150)
    lowfl = np.maximum(np.diff(np.sqrt(S[lowb].sum(0)), prepend=0), 0)
    peaks = librosa.onset.onset_detect(onset_envelope=on, sr=FSR, hop_length=HOP, units="time")
    # stereo width per frame (time domain, 44.1 kHz, frames of the same duration)
    mid, side = (y[0] + y[1]) / 2, (y[0] - y[1]) / 2
    nb = len(edges) - 1
    F = dict(pulse=np.zeros(nb), level=np.zeros(nb), low=np.zeros(nb), bands=np.zeros((nb, 4)), cent=np.zeros(nb), rate=np.zeros(nb),
             groove=np.zeros((nb, 16)), mfcc=np.zeros((nb, mfcc.shape[0])), chroma=np.zeros((nb, 12)),
             width=np.zeros(nb), silent=np.zeros(nb, bool))
    for i in range(nb):
        a, b = edges[i], edges[i + 1]
        m = (tfr >= a) & (tfr < b)
        if m.sum() < 2:
            F["silent"][i] = True
            continue
        P = tot[m].mean()
        F["level"][i] = 10 * np.log10(P)
        bl = 10 * np.log10(bands[:, m].mean(1)) - 10 * np.log10(P)
        F["low"][i], F["bands"][i] = bl[0], bl[1:]
        F["cent"][i] = np.log2((cent[m] * tot[m]).sum() / tot[m].sum() + 1)
        F["pulse"][i] = 20 * np.log10(lowfl[m].mean() + 1e-6)
        F["rate"][i] = ((peaks >= a) & (peaks < b)).sum() / (b - a)
        w = tot[m] / tot[m].sum()
        F["mfcc"][i] = (mfcc[:, m] * w).sum(1)
        F["chroma"][i] = chroma[:, m].mean(1)
        idx = np.clip(((tfr[m] - a) / (b - a) * 16).astype(int), 0, 15)
        F["groove"][i] = np.bincount(idx, weights=on[m], minlength=16) / np.maximum(np.bincount(idx, minlength=16), 1)
        sa, sb = int(a * SR), int(b * SR)
        F["width"][i] = 10 * np.log10(((side[sa:sb] ** 2).mean() + 1e-12) / ((mid[sa:sb] ** 2).mean() + 1e-12))
        F["silent"][i] = F["level"][i] < -70
    return F


def _cos(u, v):
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-12))


def block(F, i0, i1):
    """Feature summary of bars [i0, i1)."""
    i0, i1 = max(i0, 0), min(i1, len(F["level"]))
    sl = slice(i0, i1)
    P = 10 ** (F["level"][sl] / 10)
    return dict(pulse=F["pulse"][sl].mean(), level=10 * np.log10(P.mean() + 1e-12), low=F["low"][sl].mean(), bands=F["bands"][sl].mean(0),
                cent=F["cent"][sl].mean(), rate=F["rate"][sl].mean(), groove=F["groove"][sl].mean(0),
                mfcc=F["mfcc"][sl].mean(0), chroma=F["chroma"][sl].mean(0), width=F["width"][sl].mean())


def dist(A, B, tscale):
    """Signed-free distance per dimension between two block summaries (raw units)."""
    return np.array([
        abs(A["level"] - B["level"]),
        abs(A["low"] - B["low"]),
        np.abs(A["bands"] - B["bands"]).mean(),
        abs(A["cent"] - B["cent"]),
        abs(A["pulse"] - B["pulse"]),
        abs(np.log2((A["rate"] + 0.25) / (B["rate"] + 0.25))),
        1 - _cos(A["groove"], B["groove"]),
        np.linalg.norm(A["mfcc"] - B["mfcc"]) / tscale,
        1 - _cos(A["chroma"], B["chroma"]),
        abs(A["width"] - B["width"]),
    ])


def load_audio(latest):
    y, sr = sf.read(latest, always_2d=True, dtype="float32")
    if sr != SR:
        import librosa
        y = librosa.resample(y.T, orig_sr=sr, target_sr=SR).T
    return y.T


# ---------------------------------------------------------------- stems (from the render's meta)
def stem_levels(meta, t0, t1):
    st, hop = meta.get("stems_rms") or {}, meta.get("rms_hop", 0.05)
    out = {}
    for n, e in st.items():
        e = np.asarray(e)
        a, b = int(t0 / hop), int(t1 / hop)
        seg = e[a:b]
        out[n] = float((seg ** 2).mean()) if len(seg) else 0.0
    return out


def pitched_tracks(meta, project):
    ev = meta.get("events") or {}
    p = {n for n, e in ev.items() if any(x.get("m") is not None for x in e[:200])}
    return p


# ---------------------------------------------------------------- seams
def section_devices(arr, k):
    """Devices the project declares around the seam into arrangement[k]."""
    prev, nxt = arr[k - 1], arr[k]
    dv = []
    ex = prev.get("exit") or {}
    dv += [x for x in ex if x in PREP_DEVICES]
    sig = [x for x in ex if x in SIGNAL_DEVICES]
    if prev.get("fill"):
        sig.append("fill")
    land = [x for x in (nxt.get("enter") or {}) if x in LAND_DEVICES]
    ramps = 0
    for tr, au in (prev.get("auto") or {}).items():
        stack = [au]
        while stack:
            d = stack.pop()
            if isinstance(d, dict):
                stack += list(d.values())
            elif isinstance(d, list) and len([v for v in d if not isinstance(v, str)]) >= 2:
                ramps += 1
    return dv, sig, land, ramps


def _flat(d, pre=""):
    """{'inst': {'cutoff': [a, b]}} -> {'inst.cutoff': [a, b]}"""
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{pre}{k}."))
        else:
            out[f"{pre}{k}"] = v
    return out


def _ends(v):
    xs = [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return (xs[0], xs[-1]) if xs else None


def stream_breaks(prev, nxt, carried):
    """Automated parameters of a carried track that jump at the line: the end of the old section's value against
    the start of the new one's (filters in octaves, gains in dB). A sound the ear follows across the line that
    changes character in one step breaks its stream (Bregman); a ramp into the new value would not."""
    out = []
    pa, na = prev.get("auto") or {}, nxt.get("auto") or {}
    for key in set(pa) & set(na):
        tr = key.split(".")[0]
        if tr.startswith("return:") or (carried is not None and tr not in carried):
            continue
        fp, fn = _flat(pa[key]), _flat(na[key])
        for par in set(fp) & set(fn):
            e, s0 = _ends(fp[par]), _ends(fn[par])
            if not e or not s0:
                continue
            last = par.split(".")[-1]
            if last in ("cutoff", "lpf", "hpf", "to_hz") and e[1] > 0 and s0[0] > 0:
                st = abs(np.log2(s0[0] / e[1])) / 1.0          # one octave = one step (hand-tuned)
                txt = f"{key} {last} {e[1]:g}->{s0[0]:g} Hz"
            elif last == "gain_db":
                st = abs(s0[0] - e[1]) / 6.0                   # 6 dB = one step (hand-tuned)
                txt = f"{key} gain {e[1]:g}->{s0[0]:g} dB"
            else:
                continue
            if st >= 1.0:
                out.append((round(float(st), 2), txt))
    return sorted(out, reverse=True)


def run_seams(a, renders, latest, meta, meta_path):
    project = find_project(latest, meta_path, a)
    y = load_audio(latest)
    edges = bar_edges(meta)
    F = features(y, edges)
    nb = len(F["level"])
    # the track's own timbre spread: MFCC distance between neighbouring 2-bar blocks (median), x3 = one step
    blocks = [F["mfcc"][i:i + 2].mean(0) for i in range(0, nb - 1, 2)]
    tsc = 3 * float(np.median([np.linalg.norm(blocks[i + 1] - blocks[i]) for i in range(len(blocks) - 1)]) + 1e-9)
    genre = getattr(a, "genre", None) or (project or {}).get("genre")
    norm = dict(NORMS[FAMILY.get(genre, "default")])
    gj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genres.json")
    try:
        norm.update(json.load(open(gj)).get(genre, {}).get("seams", {}))
    except Exception:
        pass
    steps = np.array([d[1] for d in DIMS])
    arr = (project or {}).get("arrangement") or []
    byname = {s["name"]: i for i, s in enumerate(arr)}
    secs = meta["sections"]
    W = 2
    rows = []
    bar_of = lambda t: int(np.argmin(np.abs(edges - t)))
    for k in range(1, len(secs)):
        s0, s1 = secs[k - 1], secs[k]
        b = bar_of(s1["start"])
        wb = min(W, s0["bars"]) if s0["bars"] >= 1 else 1
        wa = min(W, s1["bars"])
        before, after = block(F, b - wb, b), block(F, b, b + wa)
        far = block(F, b - 8, b - 6) if b >= 8 else block(F, 0, max(b - wb, 1))
        jump = dist(before, after, tsc) / steps
        total = dist(far, after, tsc) / steps
        move = dist(far, before, tsc) / steps
        n = np.minimum(jump, 3.0)
        jumps = jump >= 1.0
        dn = [d[0] for d in DIMS]
        fam = {f: max(float(n[dn.index(x)]) for x in xs) for f, xs in FAMILIES}
        fjumps = [f for f, v in fam.items() if v >= 1.0]
        # preparation per dimension: the share of the far->after move that happened before the line; a dimension
        # where the bars before moved AWAY from where the next section lands is 'against'
        prep_d = np.where(total > 0.5, np.clip(1 - jump / np.maximum(total, 1e-9), 0, 1), 1.0)
        against = (jump > total + 0.5) & (move > 0.5) & jumps
        wsum = n[jumps].sum()
        prep_audio = float((prep_d[jumps] * n[jumps]).sum() / wsum) if wsum > 0 else 1.0
        # stems carried across: presence overlap (each stem weighted 0-1 over 40 dB below the loudest stem)
        carry = None
        new, gone = [], []
        if meta.get("stems_rms"):
            ta, tb, tp = edges[b], edges[min(b + wa, nb)], edges[max(b - wb, 0)]
            La, Lb = stem_levels(meta, ta, tb), stem_levels(meta, tp, ta)
            mx = max(max(La.values(), default=0), max(Lb.values(), default=0)) + 1e-12
            pres = lambda v: float(np.clip((10 * np.log10(v / mx + 1e-12) + 40) / 40, 0, 1))
            pa = {t: pres(v) for t, v in La.items()}
            pb_ = {t: pres(v) for t, v in Lb.items()}
            # kept: the share of what played before the line that is still there after it (entries over a kept
            # bed are layering; a bed pulled away is a change of ground)
            def kept(Lx):
                px = {t: pres(v) for t, v in Lx.items()}
                den = sum(px.values())
                return float(sum(min(pa.get(t, 0), v) for t, v in px.items()) / den) if den else 1.0
            # the bed before the last bar too (a fill in the last bar is not the bed)
            carry = max(kept(Lb), kept(stem_levels(meta, edges[max(b - 4, 0)], edges[max(b - 1, 1)])))
            # stems that enter after the line (> -30 dB of the loudest) but were not heard in the 8 bars before
            L8 = stem_levels(meta, edges[max(b - 8, 0)], ta)
            new = [t for t, v in La.items() if v > mx * 1e-3 and L8.get(t, 0) < mx * 1e-5]
            gone = [t for t, v in Lb.items() if v > mx * 1e-3 and La.get(t, 0) < mx * 1e-5]
        # a return: the new section lands somewhere the track has already been (the drop after a breakdown) is
        # expected, not forced. 1 = the after-state matches an earlier 2-bar block as closely as nothing changed.
        js = float(np.minimum(jump, 3).sum())
        ret = 0.0
        if b - wb >= 2 and js > 0:
            dmin = min(float(np.minimum(dist(block(F, j, j + 2), after, tsc) / steps, 3).sum())
                       for j in range(0, b - wb - 1, 2))
            ret = float(np.clip(1 - dmin / js, 0, 1))
        dv, sig, land, ramps = ([], [], [], 0)
        intended = False
        breaks = []
        if s1["name"] in byname and byname[s1["name"]] > 0:
            ki = byname[s1["name"]]
            dv, sig, land, ramps = section_devices(arr, ki)
            intended = arr[ki].get("seam") in ("cut", "intended")
            carried = None
            if meta.get("stems_rms"):
                carried = {t for t in pb_ if pb_[t] > 0.25 and pa.get(t, 0) > 0.25}
            breaks = stream_breaks(arr[ki - 1], arr[ki], carried)
        # the gesture: do the energy dimensions (level, low-band level, pulse, density) move together? A drop-out
        # or a drop-in is the arrangement's grammar and reads at once; a change of content at the same energy
        # (a swap) has to be prepared to read as intended
        sgn = lambda key: after[key] - before[key]
        e = np.array([sgn("level") / 3.0, (sgn("level") + sgn("low")) / 5.0, sgn("pulse") / 4.0,
                      np.log2((after["rate"] + 0.25) / (before["rate"] + 0.25)) / 0.8])
        moving = e[np.abs(e) >= 0.5]
        coherent = len(moving) >= 2 and (np.all(moving > 0) or np.all(moving < 0)) and (abs(e[0]) >= 0.67 or abs(e[1]) >= 1)
        layering = carry is not None and carry >= 0.6 and not breaks  # the bed stays: entries over it, or exits
        gesture = (("drop-in" if moving.mean() > 0 else "drop-out") if coherent else
                   "layering" if layering else ("swap" if len(fjumps) >= 2 else "small"))
        device = s1["bars"] <= 2  # into a short section (a cliff, a squeal, a stop): judged at the seam after it
        dev_score = min(1.0, 0.35 * len(dv) + 0.1 * min(ramps, 3) + 0.1 * len(land) + 0.05 * len(sig))
        prep = (0.4 * prep_audio + 0.2 * (carry if carry is not None else 0.5) + 0.25 * ret + 0.15 * dev_score)
        if ret < 0.5:  # moving away from where the next section lands, into new ground: a promise broken
            prep -= 0.1 * int(against.sum())
        prep = float(np.clip(prep, 0, 1))
        if breaks:
            fam["streams"] = min(max(b_[0] for b_ in breaks), 3.0)
            fjumps.append("streams")
        score = float(sum(fam.values()))
        flag = ((len(fjumps) >= norm["jumps"] or score >= norm["score"]) and prep < norm["prep"]
                and not coherent and not layering and not device)
        rows.append(dict(seam=f"{s0['name']} > {s1['name']}", bar=int(b + 1), time=round(float(edges[b]), 1),
                         steps={d[0]: round(float(v), 2) for d, v in zip(DIMS, jump)},
                         jumps=[d[0] for d, j in zip(DIMS, jumps) if j], families=fjumps,
                         family_steps={f: round(v, 2) for f, v in fam.items()},
                         against=[d[0] for d, j in zip(DIMS, against) if j],
                         score=round(score, 1), prep_audio=round(prep_audio, 2),
                         carry=None if carry is None else round(carry, 2), ret=round(ret, 2), devices=dv + sig + land
                         + ([f"{ramps} ramps"] if ramps else []), new=new, gone=gone,
                         prep=round(prep, 2), gesture=gesture, breaks=[b_[1] for b_ in breaks], device=device,
                         intended=intended, flag=bool(flag and not intended)))
    # print
    print(f"SEAMS: {os.path.basename(latest)}  {len(rows)} seams  genre {genre or '-'}  norm: flag when >= "
          f"{norm['jumps']} families step (or family score >= {norm['score']}) and prep < {norm['prep']}")
    print("steps: 1.0 = one audible step (" + ", ".join(f"{d[0]} {d[1]} {d[2]}" for d in DIMS) + ")")
    print(f"{'bar':>4s} {'time':>6s}  {'seam':28s} {'score':>5s} {'#':>2s} {'prep':>5s} {'audio':>5s} {'carry':>5s} {'ret':>5s}  "
          "stepping dimensions / against / devices")
    for r in rows:
        m, s = divmod(r["time"], 60)
        mark = ("FLAG " if r["flag"] else ("cut  " if r["intended"] else "")) + r["gesture"] + ": "
        print(f"{r['bar']:4d} {int(m)}:{s:04.1f}  {r['seam'][:28]:28s} {r['score']:5.1f} {len(r['families']):2d} "
              f"{r['prep']:5.2f} {r['prep_audio']:5.2f} {'-' if r['carry'] is None else format(r['carry'], '5.2f'):>5s} {r['ret']:5.2f}  "
              f"{mark}{','.join(r['jumps']) or '-'}"
              + (f" | against: {','.join(r['against'])}" if r["against"] else "")
              + (f" | jumps: {'; '.join(r['breaks'])}" if r["breaks"] else "")
              + (f" | {','.join(r['devices'])}" if r["devices"] else "")
              + (f" | in: {','.join(r['new'][:4])}" if r["new"] else "") + (f" | out: {','.join(r['gone'][:4])}" if r["gone"] else ""))
    fl = [r for r in rows if r["flag"]]
    for r in fl:
        print(f"FLAG bar {r['bar']} ({r['seam']}): {len(r['families'])} families step at once "
              f"({', '.join(r['families'])}: {', '.join(r['jumps'])}), score {r['score']}, prepared {r['prep']:.2f}"
              + (f"; moving away before the line: {', '.join(r['against'])}" if r["against"] else "")
              + (f"; carried sounds jumping: {'; '.join(r['breaks'])}" if r["breaks"] else "")
              + ". Prepare it (an element of the next section entering early, one of this one carried across, a ramp "
                "toward the new state, fewer dimensions at once) or mark the section `\"seam\": \"cut\"` with a reason.")
    if not fl:
        print("no seam flagged")
    # picture
    fig, axs = plt.subplots(2, 1, figsize=(15, 7), gridspec_kw=dict(height_ratios=[2.2, 1]), sharex=True)
    x = np.arange(len(rows))
    bot = np.zeros(len(rows))
    cmap = plt.cm.tab10
    for j, (nm, _, _) in enumerate(DIMS):
        v = np.array([min(r["steps"][nm], 3) for r in rows])
        axs[0].bar(x, v, bottom=bot, color=cmap(j), label=nm, width=0.7)
        bot += v
    for i, r in enumerate(rows):
        if r["flag"]:
            axs[0].text(i, bot[i] + 0.3, "FLAG", ha="center", color="r", fontsize=8, weight="bold")
        elif r["intended"]:
            axs[0].text(i, bot[i] + 0.3, "cut", ha="center", color="k", fontsize=8)
    axs[0].axhline(norm["score"], color="r", lw=0.6, ls="--")
    axs[0].legend(fontsize=7, ncol=9, loc="upper left")
    axs[0].set_title("seams: step per dimension (1 = one audible step, capped at 3); dashed: the genre's score line",
                     fontsize=8, loc="left")
    axs[1].bar(x - 0.2, [r["prep"] for r in rows], width=0.4, color="tab:green", label="prepared (0-1)")
    axs[1].bar(x + 0.2, [r["carry"] or 0 for r in rows], width=0.4, color="tab:gray", label="carried across (stems)")
    axs[1].axhline(norm["prep"], color="r", lw=0.6, ls="--")
    axs[1].set_ylim(0, 1)
    axs[1].legend(fontsize=7, loc="upper left")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels([f"{r['bar']} {r['seam'].split(' > ')[1]}" for r in rows], rotation=60, fontsize=7)
    fig.tight_layout()
    path = os.path.join(OUT, "seams.png")
    fig.savefig(path, dpi=80)
    plt.close(fig)
    json.dump(dict(norm=norm, seams=rows), open(os.path.join(OUT, "seams.json"), "w"), indent=1)
    print(f"-> {path}, seams.json")
    return rows


# ---------------------------------------------------------------- coherence
def _quant(meta, t):
    g = meta.get("grid16")
    if g:
        return int(np.argmin(np.abs(np.asarray(g) - t)))
    return int(round(t / (60 / meta["bpm"] / 4)))


def motifs(meta, ptracks, t0, t1):
    """Transposition-free melodic cells: interval 3-grams of each pitched track's top line (onsets on 16ths).
    Rhythm-free, so augmentation (half speed) and re-voicing keep the cell; the trivial cell (0,0,0) is skipped."""
    c = Counter()
    for n in ptracks:
        ev = [x for x in meta["events"][n] if t0 <= x["t"] < t1 and x.get("m") is not None]
        top = {}
        for x in ev:
            q = _quant(meta, x["t"])
            top[q] = max(top.get(q, -1), x["m"])
        line = [top[q] for q in sorted(top)]
        # collapse immediate repeats (a repeated-note pulse is rhythm, not melody)
        ln = [p for i, p in enumerate(line) if i == 0 or p != line[i - 1]]
        for i in range(len(ln) - 3):
            cell = (ln[i + 1] - ln[i], ln[i + 2] - ln[i + 1], ln[i + 3] - ln[i + 2])
            if all(abs(v) <= 12 for v in cell):
                c[cell] += 1
    return c


def pc_profile(meta, ptracks, t0, t1):
    h = np.zeros(12)
    for n in ptracks:
        for x in meta["events"][n]:
            if t0 <= x["t"] < t1 and x.get("m") is not None:
                h[int(x["m"]) % 12] += x.get("v", 1)
    return h


def wjacc(a, b):
    if not a or not b:
        return np.nan
    ks = set(a) | set(b)
    # presence-weighted (log counts): a cell that recurs counts, but a cell repeated 64 times doesn't swamp the rest
    num = sum(min(np.log1p(a[k]), np.log1p(b[k])) for k in ks)
    den = sum(max(np.log1p(a[k]), np.log1p(b[k])) for k in ks)
    return num / den if den else np.nan


def run_coherence(a, renders, latest, meta, meta_path):
    project = find_project(latest, meta_path, a)
    secs = [s for s in meta["sections"]]
    n = len(secs)
    dur = np.array([s["end"] - s["start"] for s in secs])
    ptracks = pitched_tracks(meta, project)
    # palette: pitched stems' level share per section (presence weighted in dB above -40 of the section's loudest)
    mats, names = {}, []
    if meta.get("stems_rms") and ptracks:
        tr = sorted(ptracks)
        V = np.zeros((n, len(tr)))
        for i, s in enumerate(secs):
            L = stem_levels(meta, s["start"], s["end"])
            v = np.array([L.get(t, 0) for t in tr])
            dbv = 10 * np.log10(v + 1e-12) - 10 * np.log10(v.max() + 1e-12)
            V[i] = np.clip((dbv + 40) / 40, 0, 1)
        mats["palette"] = np.array([[_cos(V[i], V[j]) if V[i].any() and V[j].any() else np.nan for j in range(n)]
                                    for i in range(n)])
    if meta.get("events") and ptracks:
        H = [pc_profile(meta, ptracks, s["start"], s["end"]) for s in secs]
        mats["pitch"] = np.array([[_cos(H[i], H[j]) if H[i].any() and H[j].any() else np.nan for j in range(n)]
                                  for i in range(n)])
        Mo = [motifs(meta, ptracks, s["start"], s["end"]) for s in secs]
        mats["motif"] = np.array([[wjacc(Mo[i], Mo[j]) for j in range(n)] for i in range(n)])
    else:
        Mo = None
    # timbre from the audio: MFCC + chroma per section, standardized across sections
    y = load_audio(latest)
    edges = bar_edges(meta)
    F = features(y, edges)
    bar_of = lambda t: int(np.argmin(np.abs(edges - t)))
    X = []
    for s in secs:
        bl = block(F, bar_of(s["start"]), bar_of(s["end"]))
        X.append(np.concatenate([bl["mfcc"], 3 * bl["chroma"] / (bl["chroma"].sum() + 1e-9)]))
    X = np.array(X)
    Z = (X - X.mean(0)) / (X.std(0) + 1e-9)
    D = np.linalg.norm(Z[:, None] - Z[None], axis=2)
    mats["timbre"] = np.exp(-D / (np.median(D[np.triu_indices(n, 1)]) + 1e-9))
    keys = [k for k in ("motif", "pitch", "palette", "timbre") if k in mats]
    # combined: the foreground (motif, pitch, palette) carries the identity; timbre is the audio check
    wts = dict(motif=0.4, pitch=0.2, palette=0.2, timbre=0.2)
    C = np.zeros((n, n))
    Wt = np.zeros((n, n))
    for k in keys:
        m = mats[k]
        ok = ~np.isnan(m)
        C[ok] += wts[k] * m[ok]
        Wt[ok] += wts[k]
    C = np.where(Wt > 0, C / np.maximum(Wt, 1e-9), np.nan)
    # strongest two-block split: maximize within - cross (duration-weighted), each block >= 25% of the length
    T = dur.sum()
    best = None
    for k in range(1, n):
        if dur[:k].sum() < 0.25 * T or dur[k:].sum() < 0.25 * T:
            continue
        w = np.outer(dur, dur)
        A = np.zeros((n, n), bool); A[:k, :k] = True; A[k:, k:] = True
        np.fill_diagonal(A, False)
        Xm = np.zeros((n, n), bool); Xm[:k, k:] = True
        ok = ~np.isnan(C)
        within = (C * w)[A & ok].sum() / w[A & ok].sum()
        cross = (C * w)[Xm & ok].sum() / w[Xm & ok].sum()
        if best is None or within - cross > best[1] - best[2]:
            best = (k, within, cross)
    k0, within0, cross0 = best
    # the weakest motivic link: for every split (each block >= 25% of the length), the share of the second block's
    # melodic cells already heard in the first and, for the
    # record, of the first block's cells that come back in the second (a bass line alone can carry that one)
    weakest = None
    if Mo:
        for kk in range(1, n):
            if dur[:kk].sum() < 0.25 * T or dur[kk:].sum() < 0.25 * T:
                continue
            f1 = sum((Mo[i] for i in range(kk)), Counter())
            f2 = sum((Mo[j] for j in range(kk, n)), Counter())
            n1, n2 = sum(f1.values()), sum(f2.values())
            if n1 < 0.1 * (n1 + n2) or n2 < 0.1 * (n1 + n2):  # one block has (almost) no melody: nothing to split
                continue
            fwd = sum(v for c, v in f2.items() if c in f1) / n2
            back = sum(v for c, v in f1.items() if c in f2) / n1
            # the split is where the motif matrix breaks into two blocks (Foote's checkerboard): the most
            # shared within the blocks against the least across them
            Mm = mats["motif"]
            A_ = np.zeros((n, n), bool); A_[:kk, :kk] = True; A_[kk:, kk:] = True
            np.fill_diagonal(A_, False)
            X_ = np.zeros((n, n), bool); X_[:kk, kk:] = True
            okm = ~np.isnan(Mm)
            wm = np.outer(dur, dur)
            cmt = ((Mm * wm)[A_ & okm].sum() / max(wm[A_ & okm].sum(), 1e-9)
                   - (Mm * wm)[X_ & okm].sum() / max(wm[X_ & okm].sum(), 1e-9))
            if weakest is None or cmt > weakest[4]:
                weakest = (kk, fwd, fwd, back, cmt)
    k = weakest[0] if weakest else k0
    w_ = np.outer(dur, dur)
    A = np.zeros((n, n), bool); A[:k, :k] = True; A[k:, k:] = True
    np.fill_diagonal(A, False)
    Xm = np.zeros((n, n), bool); Xm[:k, k:] = True
    ok = ~np.isnan(C)
    within = (C * w_)[A & ok].sum() / w_[A & ok].sum()
    cross = (C * w_)[Xm & ok].sum() / w_[Xm & ok].sum()
    # what links the two blocks: per dimension, for each later section its best match in the first block
    link = {}
    for key in keys:
        m = mats[key]
        v = [np.nanmax(m[j, :k]) for j in range(k, n) if not np.all(np.isnan(m[j, :k]))]
        link[key] = float(np.average(v, weights=dur[k:][:len(v)])) if v else np.nan
    shared = []
    if Mo:
        first = sum((Mo[i] for i in range(k)), Counter())
        second = sum((Mo[j] for j in range(k, n)), Counter())
        sm = sum(second.values())
        motif_share = sum(v for c, v in second.items() if c in first) / sm if sm else np.nan
        shared = [c for c, _ in second.most_common() if c in first][:5]
    else:
        motif_share = np.nan
    # pitched stems that sound in both blocks (> -30 dB of their own peak, in at least one section of each)
    through, newstems = [], []
    if "palette" in mats:
        for t in sorted(ptracks):
            lv = np.array([stem_levels(meta, s["start"], s["end"]).get(t, 0) for s in secs])
            on = lv > lv.max() * 1e-3
            if on[:k].any() and on[k:].any():
                through.append(t)
            elif on[k:].any() and not on[:k].any() and lv.max() > 1e-6:
                newstems.append(t)
    contrast = within - cross
    intended = ((project or {}).get("form") or {}).get("acts") == "intended"
    if weakest:  # hand-tuned: liked tracks share 47-100% of their cells across their weakest split, All Hands 19%
        split = bool(weakest[1] < 0.35 and link.get("motif", 0) < 0.35)
    else:        # no melody to follow: the audio alone, a clear two-block matrix with little across
        split = bool(contrast > 0.15 and link.get("timbre", 1) < 0.35)
    flag = split and not intended
    # print
    print(f"COHERENCE: {os.path.basename(latest)}  {n} sections, pitched stems: {', '.join(sorted(ptracks)) or '-'}")
    print("similarity 0-1 per section pair: motif (shared melodic cells), pitch (pitch-class profile), palette "
          "(pitched stems), timbre (audio MFCC+chroma); combined = 0.4 motif + 0.2 each other")
    print(f"strongest split (combined): before '{secs[k0]['name']}' (bar {secs[k0]['bar0']}): within {within0:.2f}, "
          f"across {cross0:.2f}, contrast {within0 - cross0:.2f}")
    if weakest:
        print(f"motivic split: before '{secs[k]['name']}' (bar {secs[k]['bar0']}, "
              f"{int(secs[k]['start'] // 60)}:{secs[k]['start'] % 60:04.1f}): cells of the second block heard in the "
              f"first {weakest[2]:.0%}, of the first coming back in the second {weakest[3]:.0%}; motif contrast "
              f"{weakest[4]:.2f}; within {within:.2f}, "
              f"across {cross:.2f}")
    print("best match in the first block, for the second block's sections: "
          + ", ".join(f"{kk} {link[kk]:.2f}" for kk in keys if not np.isnan(link[kk])))
    if not np.isnan(motif_share):
        print(f"at that split, second-block cells already heard: {motif_share:.0%}"
              + (f"  (top shared: {shared})" if shared else ""))
    print(f"pitched stems sounding in both blocks: {', '.join(through) or 'none'}"
          + (f"; heard only in the second (not foreshadowed): {', '.join(newstems)}" if newstems else ""))
    print("section  " + " ".join(f"{s['name'][:7]:>7s}" for s in secs))
    for i, s in enumerate(secs):
        print(f"{s['name'][:8]:8s} " + " ".join("      ." if np.isnan(C[i, j]) else f"{C[i, j]:7.2f}" for j in range(n)))
    if flag:
        print(f"FLAG two songs: the track splits before '{secs[k]['name']}' and the second block shares little "
              f"foreground with the first (motif cells {motif_share:.0%}, best-match motif/pitch "
              f"{link.get('motif', np.nan):.2f}/{link.get('pitch', np.nan):.2f}). Carry a through-line across: a motif "
              "of the first act transformed in the second, the second act's new material foreshadowed in the first, a "
              "sound that stays; or mark `\"form\": {\"acts\": \"intended\"}` in project.json with the reason.")
    elif split and intended:
        print("two acts, marked intended")
    else:
        print("no two-songs split flagged")
    # picture
    ncol = len(keys) + 1
    fig, axs = plt.subplots(1, ncol, figsize=(4.2 * ncol, 4.6))
    lab = [s["name"] for s in secs]
    for ax, (nm, m) in zip(axs, [("combined", C)] + [(kk, mats[kk]) for kk in keys]):
        ax.imshow(m, vmin=0, vmax=1, cmap="viridis", interpolation="nearest")
        ax.set_title(nm, fontsize=9)
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels(lab, rotation=90, fontsize=6); ax.set_yticklabels(lab, fontsize=6)
        ax.axhline(k - 0.5, color="r", lw=1); ax.axvline(k - 0.5, color="r", lw=1)
    fig.suptitle(f"coherence: section x section similarity (bright = shared); red: the split, before "
                 f"{secs[k]['name']}" + ("  FLAG two songs" if flag else ""), fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUT, "coherence.png")
    fig.savefig(path, dpi=80)
    plt.close(fig)
    json.dump(dict(split=dict(before=secs[k]["name"], bar=secs[k]["bar0"], within=within, cross=cross,
                              strongest=secs[k0]["name"], link_share=None if not weakest else weakest[1],
                              contrast=contrast, link=link, motif_share=motif_share, through=through, flag=flag,
                              intended=intended),
                   sections=lab, combined=np.nan_to_num(C).round(3).tolist(),
                   **{kk: np.nan_to_num(mats[kk]).round(3).tolist() for kk in keys}),
              open(os.path.join(OUT, "coherence.json"), "w"), indent=1)
    print(f"-> {path}, coherence.json")


def run(a, renders, latest, meta_path):
    mp = getattr(a, "map", None) or meta_path
    if mp is None or not os.path.exists(mp):
        raise SystemExit("no section map: give --map renders/vNNN.meta.json (or a project.json)")
    meta = load_map(mp)
    if getattr(a, "seams", False):
        run_seams(a, renders, latest, meta, mp)
    if getattr(a, "coherence", False):
        run_coherence(a, renders, latest, meta, mp)
