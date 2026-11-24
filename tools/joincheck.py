"""joincheck: how does each word join sound when sung, compared with the same join in the spoken phrase?

For a lyric line sung by `singer` (source "tts"), this renders the DRY vocal (one take: no double, reverb, delay or
inhales) and compares every join between two syllables of a phrase with the same join in the TTS's spoken phrase.
It uses the singer's own segmentation and its frame map (which spoken frame was played at each sung frame), so both
sides are cut at the same syllable and consonant boundaries.

The join window runs from the last 30 ms of the previous vowel ("tail") through its coda and the next onset to the
first 30 ms of the next vowel ("head"). Per join, spoken vs sung:
- durations of tail / coda / onset / head and the warp (sung / spoken) of each; `cons_warp` is the consonants' warp
  (coda + onset), `fill` counts sung frames played from no part of the transition (release or bridge frames);
- `dtw`: spectral-envelope trajectory distance (MFCC c1-c12 per 5 ms, standardised on the spoken windows), DTW-aligned,
  and `tnorm` with both windows resampled to the same length, plus `worst` (the part where tnorm is largest);
- `flux`: peak spectral flux (envelope change per 5 ms) in the consonants, sung / spoken (over 1 = a sharper,
  "forced" transition) and `slope`: the mean flux there, sung / spoken;
- energy: `dip` (depth of the level dip in dB), sung minus spoken; `fall`/`rise`: steepest level slopes, sung / spoken;
- pitch and voicing: `vbreaks` (voiced-unvoiced-voiced breaks, sung minus spoken), `glide_in_vowel` (share of the
  pitch move from the previous note to the next that happens after the next vowel has started; in speech the pitch
  moves through the consonants), `glide_mid` (where the pitch passes halfway: tail, coda, onset, head or vowel);
- discontinuities: `plateau` (longest run of one held source frame inside the consonants, ms) and `jumps`
  (events where a sample step is over half the local peak and over 8x the local median step, hits within 2 ms
  counted once; sung minus spoken).
`score` combines them (0 = sung like spoken; weights in score()): |log2 cons_warp| + 0.5 (|log2 tail_warp| +
|log2 head_warp|) + dtw + |log2 flux| + 0.5 |log2 slope| + |dip| / 10 + 0.5 |log2 fall| + 0.5 |log2 rise| +
glide_in_vowel + plateau / 25 + 0.5 jumps + 0.5 |vbreaks|. Lower is better; compare configurations on the same line.

Usage (from the repo root):
  python3 tools/joincheck.py                       # the "Here You Are" chorus, c1-natural settings
  python3 tools/joincheck.py --config word '{"tts_mode": "word"}' --config prefix '{"keep_joins": false}'
  python3 tools/joincheck.py --lyrics "here you are round and round" --notes "0:F#4:4 4:A4:4 8:B4:8 ..." --bpm 100
Writes <out>/joincheck.json and one image per configuration (<out>/<config>.png: per join, spoken | sung in real
time, then both time-normalised). Default out: /tmp/joincheck. Needs the setup in AGENTS.md (Kokoro model files).
"""
import argparse
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import singer  # noqa: E402
import tts_words  # noqa: E402
from hand import note_to_midi  # noqa: E402

SR = 44100
FP = 5.0
HOP = SR * FP / 1000.0
EDGE = 6  # frames of vowel at each end of a join window (30 ms)

CHORUS_LYRICS = ("here you are round and round hold on tight round we go "
                 "here you are round and round and you stay on the ride")
# c1-natural: examples/vocals/tts/build.py SING_TRACK (without the double, which is a second take)
C1 = {"source": "tts", "voice": "female", "breath": 0.15, "seed": 3}


def chorus_notes():
    pj = json.load(open(os.path.join(REPO, "sessions", "009-carousel", "project.json")))
    return pj["patterns"]["hookD"]["voxD"], pj["bpm"]


def make_notes(spec, bpm, legato=0.95, start=0.3):
    q = 60.0 / bpm / 4
    out = []
    for tok in spec.split():
        st, nm, ln = tok.split(":")[:3]
        ln = ln.rstrip("~!.")
        out.append(dict(t0=int((start + float(st) * q) * SR), n=int(float(ln) * q * legato * SR),
                        f=440.0 * 2 ** ((note_to_midi(nm) - 69) / 12), vel=0.9, glide=False))
    return out


def render(lyrics, notes, params):
    p = dict(C1)
    p.update(params)
    p.update(double=0, inhale=0)
    for k, v in singer.TTS_DEFAULTS.items():
        p.setdefault(k, v)
    p["_lyrics"] = singer.parse_lyrics(lyrics)
    tr = {}
    p["_trace"] = tr
    total = notes[-1]["t0"] + notes[-1]["n"] + SR
    y = singer._take(p, notes, total, singer._seed("singer", p.get("seed", 1), 0),
                     time_jit_ms=float(p.get("loose_ms", 0)))
    y = y * singer._norm(y)
    return np.asarray(y, dtype=np.float64), tr, p


# ------------------------------------------------------------------ features

def _mel_matrix():
    import librosa
    return librosa.filters.mel(sr=SR, n_fft=1024, n_mels=40, fmin=80, fmax=8000)


MEL = None


def frame_feats(y, centers):
    """MFCC c1-c12 and level (dB) at the given sample centres (1024-sample Hann windows)."""
    global MEL
    if MEL is None:
        MEL = _mel_matrix()
    from scipy.fft import dct
    win = np.hanning(1024)
    yp = np.pad(y, (512, 512 + 1024))
    fr = np.stack([yp[c:c + 1024] * win for c in centers])
    P = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    lm = np.log(MEL @ P.T + 1e-10).T
    cc = dct(lm, type=2, axis=1, norm="ortho")[:, 1:13]
    h = int(HOP)
    lvl = np.array([10 * np.log10(np.mean(yp[c + 512 - h:c + 512 + h] ** 2) + 1e-12) for c in centers])
    return cc, lvl


def dtw_cost(A, B):
    m, n = len(A), len(B)
    C = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(2))
    D = np.full((m + 1, n + 1), np.inf)
    D[0, 0] = 0
    L = np.zeros((m + 1, n + 1))
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            opts = (D[i - 1, j - 1], D[i - 1, j], D[i, j - 1])
            k = int(np.argmin(opts))
            pi, pj = [(i - 1, j - 1), (i - 1, j), (i, j - 1)][k]
            D[i, j] = C[i - 1, j - 1] + opts[k]
            L[i, j] = L[pi, pj] + 1
    return D[m, n] / max(L[m, n], 1)


def resample(X, n=40):
    t = np.linspace(0, len(X) - 1, n)
    return np.stack([np.interp(t, np.arange(len(X)), X[:, d]) for d in range(X.shape[1])], 1)


# ------------------------------------------------------------------ joins

def phrases_of(groups, p):
    gap = float(p.get("phrase_gap_s", 0.3)) * SR
    out, cur, prev_end = [], [], None
    for gi, g in enumerate(groups):
        if cur and g["tok"][1] == 0 and prev_end is not None and g["notes"][0]["t0"] - prev_end >= gap:
            out.append(cur)
            cur = []
        cur.append(gi)
        prev_end = g["notes"][-1]["t0"] + g["notes"][-1]["n"]
    if cur:
        out.append(cur)
    return out


def parts_of(s):
    """Sub-part frame ranges of a join's two syllables: (tail, coda) of the first, (onset, head) of the second."""
    return s


def ref_window(sa, sb):
    """Spoken window [a, b) of a join inside one analysis, with a label per frame."""
    nu_a, co_a, on_b, nu_b = sa["nu"], sa["co"], sb["on"], sb["nu"]
    a = max(nu_a[0], nu_a[1] - EDGE)
    b = min(nu_b[1], nu_b[0] + EDGE)
    lab = []
    for i in range(a, b):
        lab.append("tail" if i < nu_a[1] else "coda" if i < co_a[1] else "onset" if i < nu_b[0] else "head")
    return a, b, lab


def sung_window(tr, k, sa, sb):
    """Sung frames of the join between syllables k and k+1, with labels, from the singer's frame map."""
    src_w, src_i, sid = tr["src_w"], tr["src_i"], tr["sid"]
    wa, wb = sa["w"], sb["w"]
    labs = {}
    for f in range(len(src_w)):
        w, i, g = src_w[f], src_i[f], sid[f]
        if w is None or g not in (k, k + 1):
            continue
        if g == k and w is wa:
            if i >= sa["nu"][1] - EDGE and i < sa["nu"][1]:
                labs[f] = "tail"
            elif sa["nu"][1] <= i < max(sa["co"][1], sa["nu"][1] + 1):
                labs[f] = "coda"
            elif i >= sa["co"][1]:
                labs[f] = "fill"
        elif g == k + 1 and w is wb:
            if i < sb["on"][1] and i >= sb["on"][0]:
                labs[f] = "onset"
            elif sb["nu"][0] <= i < sb["nu"][0] + EDGE:
                labs[f] = "head"
        elif g == k:
            labs[f] = "fill"  # a release or bridge frame
    tails = [f for f, l in labs.items() if l == "tail"]
    heads = [f for f, l in labs.items() if l == "head"]
    if not tails or not heads:
        return None
    a, b = min(tails), max(heads) + 1
    lab = [labs.get(f, "vowel") for f in range(a, b)]
    return a, b, lab


def measure(lyrics, notes, params, ref_stats=None):
    y, tr, p = render(lyrics, notes, params)
    groups = tr["groups"]
    voice = tts_words.kokoro_voice(p)
    speed = float(p.get("tts_speed", 0.9))
    joins = []
    for ph in phrases_of(groups, p):
        toks = [groups[gi]["tok"] for gi in ph]
        words = [t[0] for t in toks if t[1] == 0]
        ref = tts_words.phrase_syllables(words, p)
        if ref is None or len(ref) != len(ph):
            continue
        wref = ref[0]["w"]
        xs = tts_words.spoken(wref["text"], voice, speed)
        for j in range(len(ph) - 1):
            k = ph[j]
            sa, sb = groups[k]["syl"], groups[k + 1]["syl"]
            if sa is None or sb is None:
                continue
            ra, rb, rlab = ref_window(ref[j], ref[j + 1])
            sw = sung_window(tr, k, sa, sb)
            if sw is None or rb - ra < 3:
                continue
            fa, fb, slab = sw
            rc = [int(round((i + wref["off"]) * HOP)) for i in range(ra, rb)]
            scn = [int(round(f * HOP)) for f in range(fa, fb)]
            A, la = frame_feats(xs, rc)
            B, lb = frame_feats(y, scn)
            name = f"{words_at(groups, k)}|{words_at(groups, k + 1)}"
            joins.append(dict(name=name, k=k, A=A, B=B, la=la, lb=lb, rlab=rlab, slab=slab,
                              rf0=tts_words.analyze(wref["text"], voice, speed)["f0"][ra:rb] if False else
                              wref["f0"][ra:rb], sf0=tr["f0"][fa:fb], svoiced=tr["voiced"][fa:fb],
                              note_a=groups[k]["notes"][-1]["f"], note_b=groups[k + 1]["notes"][0]["f"],
                              src=[(id(tr["src_w"][f]), float(tr["src_i"][f])) for f in range(fa, fb)],
                              ya=xs[rc[0]:rc[-1] + int(HOP)], yb=y[scn[0]:scn[-1] + int(HOP)]))
    if ref_stats is None:
        allA = np.concatenate([j["A"] for j in joins])
        ref_stats = (allA.mean(0), allA.std(0) + 1e-6)
    mu, sd = ref_stats
    for j in joins:
        j.update(metrics(j, mu, sd))
    return joins, ref_stats


def words_at(groups, k):
    wd, si, n = groups[k]["tok"]
    pieces = [x for x in wd.split("-") if x]
    return pieces[si] if n > 1 else wd


def _dur(lab, part):
    return lab.count(part) * FP


def _w(s, r):
    return (s + FP / 2) / (r + FP / 2)


def metrics(j, mu, sd):
    A, B = (j["A"] - mu) / sd, (j["B"] - mu) / sd
    rl, sl = j["rlab"], j["slab"]
    m = {}
    for part in ("tail", "coda", "onset", "head"):
        m[f"{part}_ms"] = (_dur(rl, part), _dur(sl, part))
    m["fill_ms"] = _dur(sl, "fill") + _dur(sl, "vowel")
    m["cons_warp"] = _w(_dur(sl, "coda") + _dur(sl, "onset") + m["fill_ms"], _dur(rl, "coda") + _dur(rl, "onset"))
    m["tail_warp"] = _w(_dur(sl, "tail"), _dur(rl, "tail"))
    m["head_warp"] = _w(_dur(sl, "head"), _dur(rl, "head"))
    m["dtw"] = dtw_cost(A, B) / np.sqrt(A.shape[1])
    Ar, Br = resample(A), resample(B)
    d = np.sqrt(((Ar - Br) ** 2).sum(1)) / np.sqrt(A.shape[1])
    m["tnorm"] = float(d.mean())
    m["worst"] = rl[min(int(np.argmax(d) / 39 * (len(rl) - 1)), len(rl) - 1)]

    def cons_idx(lab):
        idx = [i for i, l in enumerate(lab) if l in ("coda", "onset", "fill")]
        return idx or list(range(len(lab)))

    fa = np.r_[0, np.sqrt((np.diff(A, axis=0) ** 2).sum(1))]
    fb = np.r_[0, np.sqrt((np.diff(B, axis=0) ** 2).sum(1))]
    ia, ib = cons_idx(rl), cons_idx(sl)
    ia2 = sorted(set(ia) | {max(i - 1, 0) for i in ia} | {min(i + 1, len(fa) - 1) for i in ia})
    ib2 = sorted(set(ib) | {max(i - 1, 0) for i in ib} | {min(i + 1, len(fb) - 1) for i in ib})
    m["flux"] = (fb[ib2].max() + 0.1) / (fa[ia2].max() + 0.1)
    m["slope"] = (fb[ib2].mean() + 0.1) / (fa[ia2].mean() + 0.1)
    la, lb = j["la"] - j["la"].max(), j["lb"] - j["lb"].max()
    m["dip"] = float((lb.max() - lb.min()) - (la.max() - la.min()))
    da, db = np.diff(la), np.diff(lb)
    m["fall"] = (max(-db.min(), 0) + 1) / (max(-da.min(), 0) + 1)
    m["rise"] = (max(db.max(), 0) + 1) / (max(da.max(), 0) + 1)

    def breaks(v):
        v = np.asarray(v) > 0
        segs = np.sum(v[1:] & ~v[:-1]) + (1 if v[0] else 0)
        return max(int(segs) - 1, 0)

    m["vbreaks"] = breaks(j["svoiced"]) - breaks(j["rf0"])
    # the pitch move from the previous note to the next: where it happens
    st = 12 * np.log2(np.maximum(j["sf0"], 1) / 440.0)
    sa_, sb_ = 12 * np.log2(j["note_a"] / 440.0), 12 * np.log2(j["note_b"] / 440.0)
    if abs(sb_ - sa_) >= 0.5:
        prog = np.clip((st - sa_) / (sb_ - sa_), 0, 1.2)
        heads = [i for i, l in enumerate(sl) if l == "head"]
        h0 = heads[0] if heads else len(sl)
        before = prog[max(h0 - 1, 0)] if h0 > 0 else 0.0
        m["glide_in_vowel"] = float(np.clip(1 - before, 0, 1))
        mid = int(np.argmax(prog >= 0.5)) if (prog >= 0.5).any() else len(sl) - 1
        m["glide_mid"] = sl[mid]
    else:
        m["glide_in_vowel"] = 0.0
        m["glide_mid"] = "-"
    # discontinuities
    cons = set(cons_idx(sl))
    run, best, prev = 0, 0, None
    for i, s in enumerate(j["src"]):
        if i in cons and s == prev:
            run += 1
            best = max(best, run)
        else:
            run = 0
        prev = s
    m["plateau_ms"] = (best + 1) * FP if best else 0.0

    def jumps(x):
        """Samples whose step is large against the local signal: over half the local peak (within 2 ms) and over
        8x the local median step (within 5 ms). Natural audio, bursts included, rarely does both."""
        dx = np.abs(np.diff(x))
        from scipy.ndimage import maximum_filter1d, median_filter
        pk = maximum_filter1d(np.abs(x[:-1]), 177)
        md = median_filter(dx, 441) + 1e-9
        hit = np.where((dx > 0.5 * pk) & (dx > 8 * md) & (pk > 1e-4 * np.abs(x).max()))[0]
        return int(np.sum(np.diff(hit) > 88) + 1) if len(hit) else 0  # events: hits within 2 ms count once

    m["jumps"] = jumps(j["yb"]) - jumps(j["ya"])
    m["score"] = score(m)
    return m


def score(m):
    l2 = lambda x: abs(np.log2(max(x, 1e-3)))
    return float(l2(m["cons_warp"]) + 0.5 * (l2(m["tail_warp"]) + l2(m["head_warp"])) + m["dtw"] + l2(m["flux"])
                 + 0.5 * l2(m["slope"]) + abs(m["dip"]) / 10 + 0.5 * l2(m["fall"]) + 0.5 * l2(m["rise"])
                 + m["glide_in_vowel"] + m["plateau_ms"] / 25 + 0.5 * max(m["jumps"], 0) + 0.5 * abs(m["vbreaks"]))


# ------------------------------------------------------------------ output

COLS = ["score", "cons_warp", "tail_warp", "head_warp", "dtw", "tnorm", "worst", "flux", "slope", "dip", "fall", "rise",
        "glide_in_vowel", "glide_mid", "vbreaks", "plateau_ms", "jumps"]


def fmt(v):
    if isinstance(v, str):
        return v
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    return f"{v:.2f}"


def table(name, joins):
    print(f"\n== {name}: mean score {np.mean([j['score'] for j in joins]):.2f} over {len(joins)} joins")
    print(f"{'join':14s} " + " ".join(f"{c[:8]:>8s}" for c in COLS) + "   ms spoken/sung: tail coda onset head")
    for j in joins:
        durs = " ".join(f"{j[p + '_ms'][0]:.0f}/{j[p + '_ms'][1]:.0f}" for p in ("tail", "coda", "onset", "head"))
        print(f"{j['name']:14s} " + " ".join(f"{fmt(j[c]):>8s}" for c in COLS) + f"   {durs}")


def image(path, joins):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(joins)
    fig, ax = plt.subplots(n, 4, figsize=(14, 1.6 * n + 0.6), squeeze=False)

    def spec(x):
        from scipy import signal
        f, t, S = signal.spectrogram(x, SR, nperseg=512, noverlap=448)
        return f, t, 10 * np.log10(S + 1e-12)

    for r, j in enumerate(joins):
        for c, (x, ttl) in enumerate([(j["ya"], "spoken"), (j["yb"], "sung")]):
            f, t, S = spec(x)
            ax[r][c].pcolormesh(t * 1000, f, S, cmap="magma", vmin=S.max() - 70, shading="auto")
            ax[r][2 + c].imshow(np.repeat(S[:, :, None], 1, 2)[:, :, 0], origin="lower", aspect="auto", cmap="magma",
                                vmin=S.max() - 70, extent=[0, 1, 0, f[-1]])
            for a_ in (ax[r][c], ax[r][2 + c]):
                a_.set_ylim(0, 6000)
                a_.tick_params(labelsize=6)
            ax[r][c].set_title(f"{j['name']} {ttl} (ms)", fontsize=7)
            ax[r][2 + c].set_title(f"{ttl}, time-normalised", fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=60)
    plt.close(fig)


def _tilt(P, f):
    """Relative energy 2-8 kHz vs 0.1-1 kHz (dB): the strongest acoustic cue of stress (Campbell 1995)."""
    hi = P[:, (f >= 2000) & (f < 8000)].sum(1)
    lo = P[:, (f >= 100) & (f < 1000)].sum(1)
    return 10 * np.log10((hi + 1e-12) / (lo + 1e-12))


def _spec_frames(y, centers):
    win = np.hanning(1024)
    yp = np.pad(y, (512, 1536))
    fr = np.stack([yp[c:c + 1024] * win for c in centers])
    return np.abs(np.fft.rfft(fr, axis=1)) ** 2, np.fft.rfftfreq(1024, 1 / SR)


def prosody(lyrics, notes, params):
    """Per syllable: the spoken stress cues and what survives in the sung vocal. Tilt is measured on the spectral
    envelope (spoken: the TTS analysis; sung: the envelope the singer synthesised), because on the audio it depends on
    which harmonics of the sung note fall in each band."""
    y, tr, p = render(lyrics, notes, params)
    groups = tr["groups"]
    voice, speed = tts_words.kokoro_voice(p), float(p.get("tts_speed", 0.9))
    rows = []
    for ph in phrases_of(groups, p):
        words = [groups[gi]["tok"][0] for gi in ph if groups[gi]["tok"][1] == 0]
        ref = tts_words.phrase_syllables(words, p)
        if ref is None or len(ref) != len(ph):
            continue
        w = ref[0]["w"]
        xs = tts_words.spoken(w["text"], voice, speed)
        f0 = w["f0"]
        med = np.median(12 * np.log2(f0[f0 > 0] / 440.0))
        lv = []
        for j, gi in enumerate(ph):
            s, g = ref[j], groups[gi]
            nu = range(*s["nu"])
            on = range(*s["on"])
            P, f = None, None
            lev = float(np.mean(w["r"][s["nu"][0]:s["nu"][1]]))
            onl = float(np.max(w["r"][s["on"][0]:s["on"][1]])) - lev if len(on) else float("nan")
            fv = f0[s["nu"][0]:s["nu"][1]]
            st = float(np.mean(12 * np.log2(fv[fv > 0] / 440.0)) - med) if (fv > 0).any() else float("nan")
            # sung: the frames of this syllable's vowel
            ss = g["syl"]
            fr = [k for k in range(len(tr["src_w"])) if tr["sid"][k] == gi and tr["src_w"][k] is ss["w"]
                  and ss["nu"][0] <= tr["src_i"][k] < ss["nu"][1]]
            fo = [k for k in range(len(tr["src_w"])) if tr["sid"][k] == gi and tr["src_w"][k] is ss["w"]
                  and ss["on"][0] <= tr["src_i"][k] < ss["on"][1]]
            Ps, fs = _spec_frames(y, [int(round(k * HOP)) for k in fr]) if fr else (None, None)
            slev = 10 * np.log10(Ps.sum(1).mean() + 1e-12) if fr else float("nan")
            sonl = (10 * np.log10(_spec_frames(y, [int(round(k * HOP)) for k in fo])[0].sum(1).max() + 1e-12) - slev
                    if fo else float("nan"))
            tgt = np.array([gg["f"] for gg in g["notes"]]).mean()
            dev = (1200 * np.log2(np.maximum(tr["f0"][fr], 1) / tgt)) if fr else np.array([np.nan])
            rows.append(dict(word=words_at(groups, gi), seg=(s["co"][1] - s["on"][0]) * FP, on_ms=len(on) * FP,
                             vow_ms=len(nu) * FP, lev=lev, tilt=tts_words._tilt(w, s["nu"]), f0=st, onf=onl,
                             s_lev=slev, s_tilt=float(np.mean(tr["env_tilt"][fr])) if fr else float("nan"),
                             s_onf=sonl,
                             s_dev=float(np.sqrt(np.nanmean(dev ** 2))), note_ms=sum(n["n"] for n in g["notes"]) / SR * 1000))
            lv.append(lev)
        for r in rows[-len(ph):]:
            r["lev"] -= max(lv)
    top = max(r["s_lev"] for r in rows)
    for r in rows:
        r["s_lev"] -= top
    print(f"\n{'syllable':9s} | spoken: {'seg':>4s} {'onset':>5s} {'vowel':>5s} {'level':>6s} {'tilt':>6s} {'F0 st':>6s} "
          f"{'onsetF':>6s} | sung: {'note':>5s} {'level':>6s} {'tilt':>6s} {'onsetF':>6s} {'dev c':>6s}")
    for r in rows:
        print(f"{r['word']:9s} |         {r['seg']:4.0f} {r['on_ms']:5.0f} {r['vow_ms']:5.0f} {r['lev']:6.1f} {r['tilt']:6.1f} "
              f"{r['f0']:6.1f} {r['onf']:6.1f} |       {r['note_ms']:5.0f} {r['s_lev']:6.1f} {r['s_tilt']:6.1f} "
              f"{r['s_onf']:6.1f} {r['s_dev']:6.0f}")
    sp = np.array([[r["tilt"], r["s_tilt"], r["onf"], r["s_onf"]] for r in rows], dtype=float)
    ok = ~np.isnan(sp).any(1)
    print(f"spread across syllables (std): tilt spoken {np.nanstd(sp[:, 0]):.1f} dB, sung {np.nanstd(sp[:, 1]):.1f} dB; "
          f"onset force spoken {np.nanstd(sp[:, 2]):.1f} dB, sung {np.nanstd(sp[:, 3]):.1f} dB; "
          f"tilt carried into song: r = {np.corrcoef(sp[ok, 0], sp[ok, 1])[0, 1]:.2f}")
    return rows


def timing(lyrics, notes, params, bpm, quiet=False):
    """Per syllable, against the score: where the vowel starts, where the perceived onset is (P-centre, estimated as
    the fastest rise of the 300-3000 Hz energy around the consonant-vowel transition, the 'maxD' landmark), how much
    consonant is placed before the note, the inter-onset intervals, and the syllable's length against its note."""
    from scipy import signal as sg
    y, tr, p = render(lyrics, notes, params)
    groups, sid, src_w, src_i = tr["groups"], tr["sid"], tr["src_w"], tr["src_i"]
    beat = 60.0 / bpm
    band = sg.sosfiltfilt(sg.butter(3, [300, 3000], "bandpass", fs=SR, output="sos"), y)
    h = int(HOP)
    nF = len(src_w)
    e = np.array([10 * np.log10(np.mean(band[max(0, int(k * HOP) - h):int(k * HOP) + h] ** 2) + 1e-12)
                  for k in range(nF)])
    de = np.convolve(np.r_[0, np.diff(np.convolve(e, np.ones(3) / 3, mode="same"))], np.ones(2) / 2, mode="same")
    rows = []
    for k, g in enumerate(groups):
        s = g["syl"]
        fr = np.where(sid == k)[0]
        if s is None or not len(fr):
            continue
        score = g["notes"][0]["t0"] / SR
        nu = [f for f in fr if src_w[f] is s["w"] and s["nu"][0] <= src_i[f] < s["nu"][1]]
        v0 = (nu[0] if nu else fr[0])
        a0 = fr[0]
        lo, hi = max(a0 - 2, 0), min(v0 + 12, nF - 1)
        pc = lo + int(np.argmax(de[lo:hi + 1]))
        cons = sum(1 for f in fr if not (src_w[f] is s["w"] and s["nu"][0] <= src_i[f] < s["nu"][1]))
        rows.append(dict(word=words_at(groups, k), score=score, lead=(v0 - a0) * FP,
                         v_dev=(v0 * FP / 1000 - score) * 1000, p_dev=(pc * FP / 1000 - score) * 1000,
                         p=pc * FP / 1000, sung=len(fr) * FP, note=sum(n["n"] for n in g["notes"]) / SR * 1000,
                         cons=cons * FP, vowel=len(nu) * FP))
    for i, r in enumerate(rows):
        if i + 1 < len(rows):
            r["ioi_score"] = (rows[i + 1]["score"] - r["score"]) * 1000
            r["ioi_sung"] = (rows[i + 1]["p"] - r["p"]) * 1000
        else:
            r["ioi_score"] = r["ioi_sung"] = float("nan")
        # Friberg & Sundberg (1995): JND about 6 ms below 240 ms IOI, 2.5% of the IOI above
        ioi = r["ioi_score"] if np.isfinite(r["ioi_score"]) else 500.0
        r["jnd"] = max(6.0, 0.025 * ioi)
        r["flag"] = "!!" if abs(r["p_dev"]) > 3 * r["jnd"] else "!" if abs(r["p_dev"]) > r["jnd"] else ""
    if not quiet:
        print(f"{'syllable':9s} {'score s':>7s} {'lead':>5s} {'vowel':>6s} {'P-ctr':>6s} {'/beat':>6s} {'IOI sc':>6s} "
              f"{'IOI sg':>6s} {'note':>5s} {'sung':>5s} {'cons':>5s} {'vowel':>5s}  flag (JND: Friberg & Sundberg 1995)")
        for r in rows:
            print(f"{r['word']:9s} {r['score']:7.3f} {r['lead']:5.0f} {r['v_dev']:+6.0f} {r['p_dev']:+6.0f} "
                  f"{r['p_dev'] / 1000 / beat:+6.2f} {r['ioi_score']:6.0f} {r['ioi_sung']:6.0f} {r['note']:5.0f} "
                  f"{r['sung']:5.0f} {r['cons']:5.0f} {r['vowel']:5.0f}  {r['flag']}")
        pd = np.array([r["p_dev"] for r in rows])
        di = np.array([r["ioi_sung"] - r["ioi_score"] for r in rows[:-1]])
        print(f"P-centre vs score: mean {pd.mean():+.0f} ms, sd {pd.std():.0f} ms, max |dev| {np.abs(pd).max():.0f} ms; "
              f"IOI error sd {di.std():.0f} ms; beyond JND: {sum(1 for r in rows if r['flag'])}/{len(rows)}, "
              f"beyond 3x JND: {sum(1 for r in rows if r['flag'] == '!!')}")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lyrics")
    ap.add_argument("--notes")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--set", default="{}", help="JSON params on top of the c1-natural settings")
    ap.add_argument("--config", nargs=2, action="append", metavar=("NAME", "JSON"),
                    help="extra configuration to compare (params on top of --set)")
    ap.add_argument("--out", default="/tmp/joincheck")
    ap.add_argument("--prosody", action="store_true", help="per-syllable stress cues, spoken vs sung, then exit")
    ap.add_argument("--timing", action="store_true", help="per-syllable onsets against the score, then exit")
    a = ap.parse_args()
    if a.lyrics:
        spec, bpm, lyr = a.notes, a.bpm, a.lyrics
    else:
        spec, bpm = chorus_notes()
        lyr = CHORUS_LYRICS
    notes = make_notes(spec, bpm)
    base = json.loads(a.set)
    if a.timing:
        for name, params in [("current", base)] + [(n, dict(base, **json.loads(js))) for n, js in (a.config or [])]:
            print(f"\n== timing: {name}")
            timing(lyr, notes, params, bpm)
        return
    if a.prosody:
        for name, params in [("current", base)] + [(n, dict(base, **json.loads(js))) for n, js in (a.config or [])]:
            print(f"\n== prosody: {name}")
            prosody(lyr, notes, params)
        return
    configs = [("current", base)] + [(n, dict(base, **json.loads(js))) for n, js in (a.config or [])]
    os.makedirs(a.out, exist_ok=True)
    stats, out = None, {}
    for name, params in configs:
        joins, stats = measure(lyr, notes, params, stats)
        table(name, joins)
        image(os.path.join(a.out, f"{name}.png"), joins)
        out[name] = [{c: (j[c] if isinstance(j[c], str) else float(j[c])) for c in COLS} | {"join": j["name"]}
                     for j in joins]
    if len(configs) > 1:
        print("\nper join score: " + "  ".join(n for n, _ in configs))
        for i in range(len(out["current"])):
            row = [out[n][i]["score"] if i < len(out[n]) and out[n][i]["join"] == out["current"][i]["join"]
                   else float("nan") for n, _ in configs]
            print(f"{out['current'][i]['join']:14s} " + "  ".join(f"{v:6.2f}" for v in row))
    json.dump(out, open(os.path.join(a.out, "joincheck.json"), "w"), indent=1)
    print(f"\nwrote {a.out}/joincheck.json and {', '.join(n + '.png' for n, _ in configs)}")


if __name__ == "__main__":
    main()
