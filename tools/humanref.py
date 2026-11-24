"""humanref: measure how human singers time and shape English words, from the GTSinger corpus.

GTSinger (Zhang et al., NeurIPS 2024; https://huggingface.co/datasets/GTSinger/GTSinger; CC BY-NC-SA 4.0) has
studio singing with phoneme-level alignment, the score's note durations, and the same lyrics read by the same singer
("paired speech"). We only measure it: nothing from it is copied into the repo or used in a track. Files are cached
in ~/.cache/spectre/refs/gtsinger (outside git).

What it measures (on the "Control_Group" takes, i.e. plain singing):
- which point of a sung syllable singers put on the beat: the score grid (running sum of the notes' score durations,
  rests included) is fitted to the audio by least squares (offset + tempo) using different anchors (the word's
  first phone, the vowel onset, and points in between); the anchor with the smallest residual is what lands on the
  beat. Residuals are reported in ms;
- per word: the consonant lead (phones before the first vowel), the vowel and coda lengths against the note's
  score length, and the same word read aloud (paired speech): how a singer turns speech timing into sung timing;
- rules for the engine: the consonant lead against the spoken onset length and the time available before the note.
Usage: python3 tools/humanref.py [--max N] [--json out.json]
"""
import argparse
import concurrent.futures as cf
import json
import os
import urllib.parse
import urllib.error
import urllib.request

import numpy as np

BASE = "https://huggingface.co/datasets/GTSinger/GTSinger/resolve/main/"
API = "https://huggingface.co/api/datasets/GTSinger/GTSinger"
CACHE = os.path.expanduser("~/.cache/spectre/refs/gtsinger")


def fetch(path):
    dst = os.path.join(CACHE, path)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        import time
        for k in range(6):  # Hugging Face rate-limits bursts (HTTP 429): back off and retry
            try:
                data = urllib.request.urlopen(BASE + urllib.parse.quote(path), timeout=120).read()
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or k == 5:
                    return None
                time.sleep(5 * 2 ** k)
        tmp = dst + ".tmp"
        open(tmp, "wb").write(data)
        os.replace(tmp, dst)
    return dst


def listing():
    idx = os.path.join(CACHE, "_files.json")
    if not os.path.exists(idx):
        os.makedirs(CACHE, exist_ok=True)
        info = json.load(urllib.request.urlopen(API, timeout=120))
        json.dump([s["rfilename"] for s in info["siblings"]], open(idx, "w"))
    return json.load(open(idx))


def is_vowel(ph):
    return ph[-1:].isdigit()  # ARPAbet vowels carry a stress digit


def words_of(seg):
    """Words with their phones, vowel indices and notes (score durations), plus the score time of each word."""
    out, t_score = [], 0.0
    for w in seg:
        nd = [float(x) for x in w.get("note_dur", [])]
        if w["word"] in ("<SP>", "<AP>"):
            t_score += sum(nd) if nd else 0.0
            continue
        ph, ps, pe = w["ph"], w["ph_start"], w["ph_end"]
        vi = [i for i, p in enumerate(ph) if is_vowel(p)]
        out.append(dict(word=w["word"].lower(), ph=ph, ps=ps, pe=pe, vi=vi, note_dur=nd, score=t_score,
                        start=w["start_time"], end=w["end_time"], notes=w.get("note", [])))
        t_score += sum(nd)
    return out


def syllables(words):
    """One entry per sung syllable that maps 1:1 to a note: (score onset, word start or syllable start, vowel onset,
    onset consonant length, vowel length, coda length, note length)."""
    rows = []
    for wi, w in enumerate(words):
        if not w["vi"] or len(w["vi"]) != len(w["note_dur"]):
            continue
        sc = w["score"]
        for k, v in enumerate(w["vi"]):
            first = 0 if k == 0 else w["vi"][k - 1] + 1  # consonants between vowels go to the next syllable
            last = (w["vi"][k + 1] - 1) if k + 1 < len(w["vi"]) else len(w["ph"]) - 1
            on = w["ps"][v] - w["ps"][first] if first < v else 0.0
            co = w["pe"][last] - w["pe"][v] if last > v else 0.0
            rows.append(dict(word=w["word"], syl=k, score=sc, start=w["ps"][first], v0=w["ps"][v],
                             onset=on, n_on=v - first, vowel=w["pe"][v] - w["ps"][v], coda=co,
                             n_co=max(last - v, 0), note=w["note_dur"][k], wi=wi,
                             initial=(k == 0)))
            sc += w["note_dur"][k]
    return rows


def fit(rows, anchor):
    t = np.array([r["score"] for r in rows])
    y = np.array([anchor(r) for r in rows])
    A = np.stack([np.ones_like(t), t], 1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ coef, coef


def _segments_mono(files, n, min_words=5):
    """Control-group segments whose sung words are all one syllable on one note (so the engine can sing the same
    lyrics note for note)."""
    ctrl = sorted(f for f in files if f.startswith("English/") and "/Control_Group/" in f and f.endswith(".json"))
    rng = np.random.default_rng(7)
    out = []
    for i in rng.permutation(len(ctrl)):
        p = ctrl[i]
        if fetch(p) is None:
            continue
        ws = words_of(json.load(open(os.path.join(CACHE, p))))
        if len(ws) >= min_words and all(len(w["vi"]) == 1 and len(w["note_dur"]) == 1 for w in ws) \
                and all(w["word"].isalpha() for w in ws):
            out.append(p)
            if len(out) >= n:
                break
    return out


def _band_db(y, sr, times, half=0.005):
    from scipy import signal as sg
    b = sg.sosfiltfilt(sg.butter(3, [300, 3000], "bandpass", fs=sr, output="sos"), y)
    h = int(half * sr)
    return np.array([10 * np.log10(np.mean(b[max(0, int(t * sr) - h):int(t * sr) + h] ** 2) + 1e-12) for t in times])


def _measure_line(sylls, f0_t, f0_st, y, sr, beat):
    """Per syllable: consonant start and vowel onset against the beat, consonant length, vowel share of the note;
    per join: where the pitch move crosses halfway (ms from the next vowel onset; negative = in the consonants or
    before) and the level dip between the two vowels (dB under the mean of their levels)."""
    rows = []
    for i, s in enumerate(sylls):
        r = dict(word=s["word"], c_dev=(s["start"] - beat[i]) * 1000, v_dev=(s["v0"] - beat[i]) * 1000,
                 onset=(s["v0"] - s["start"]) * 1000, vshare=s["vowel"] / max(s["note"], 1e-3))
        # perceived onset (P-centre), estimated as the fastest rise of the 300-3000 Hz level around the
        # consonant-vowel transition ("maxD"; Rathcke 2026 citing Sturm & Volin)
        tt = np.arange(s["start"] - 0.01, s["v0"] + 0.06, 0.005)
        if len(tt) > 3:
            lv = _band_db(y, sr, tt)
            d = np.diff(np.convolve(lv, np.ones(3) / 3, mode="same"))
            r["p_dev"] = (tt[int(np.argmax(d)) + 1] - beat[i]) * 1000
        if i > 0:
            a, b = sylls[i - 1], s
            pa, pb = a["midi"], b["midi"]
            if abs(pb - pa) >= 1:
                m = (f0_t > a["v0"]) & (f0_t < b["v0"] + b["vowel"]) & np.isfinite(f0_st)
                tt, st = f0_t[m], f0_st[m]
                prog = (st - pa) / (pb - pa)
                k = np.argmax(prog >= 0.5) if (prog >= 0.5).any() else None
                r["glide_ms"] = (tt[k] - b["v0"]) * 1000 if k is not None else np.nan
            else:
                r["glide_ms"] = np.nan
            ta = np.linspace(a["v0"], a["v0"] + a["vowel"], 6)[1:-1]
            tb = np.linspace(b["v0"], b["v0"] + b["vowel"], 6)[1:-1]
            tj = np.arange(a["v0"] + a["vowel"] * 0.5, b["v0"] + b["vowel"] * 0.5, 0.005)
            la, lb, lj = _band_db(y, sr, ta).mean(), _band_db(y, sr, tb).mean(), _band_db(y, sr, tj).min()
            r["dip"] = (la + lb) / 2 - lj
        rows.append(r)
    return rows


def compare(n, params):
    """Human (GTSinger) vs engine on the same lyrics, notes and tempo."""
    import sys
    import soundfile as sf
    import pyworld as pw
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import joincheck as J
    files = listing()
    out = {"human": [], "engine": []}
    for p in _segments_mono(files, n):
        wav = fetch(p.replace(".json", ".wav"))
        if wav is None:
            continue
        ws = words_of(json.load(open(os.path.join(CACHE, p))))
        rows = syllables(ws)
        for r, w in zip(rows, ws):
            r["midi"] = float(w["notes"][0])
        # human: beat from the score grid fitted to the syllable starts (what these singers put on the beat)
        _, coef = fit(rows, lambda r: r["start"])
        beat_h = [coef[0] + coef[1] * r["score"] for r in rows]
        y, sr = sf.read(wav)
        y = y.mean(1) if y.ndim > 1 else y
        f0, t = pw.harvest(np.ascontiguousarray(y.astype(np.float64)), sr, frame_period=5.0, f0_floor=70, f0_ceil=900)
        st = np.where(f0 > 0, 69 + 12 * np.log2(np.maximum(f0, 1) / 440.0), np.nan)
        hum = _measure_line(rows, t, st, y, sr, beat_h)
        # engine: the same words on the same notes (score timing, metronomic)
        t0s = 0.3 - rows[0]["score"]
        notes = [dict(t0=int((t0s + r["score"]) * J.SR), n=int(r["note"] * 0.95 * J.SR),
                      f=440.0 * 2 ** ((r["midi"] - 69) / 12), vel=0.9, glide=False) for r in rows]
        lyr = " ".join(r["word"] for r in rows)
        ye, tr, pe = J.render(lyr, notes, params)
        er = []
        for k, (g, r) in enumerate(zip(tr["groups"], rows)):
            fr = np.where(tr["sid"] == k)[0]
            sy = g["syl"]
            nu = [f for f in fr if tr["src_w"][f] is sy["w"] and sy["nu"][0] <= tr["src_i"][f] < sy["nu"][1]]
            v0 = (nu[0] if nu else fr[0]) * 0.005
            er.append(dict(word=r["word"], start=fr[0] * 0.005, v0=v0, vowel=len(nu) * 0.005, note=r["note"],
                           midi=r["midi"]))
        fe = np.array(tr["f0"])
        te = np.arange(len(fe)) * 0.005
        ste = np.where(np.array(tr["voiced"]) > 0, 69 + 12 * np.log2(np.maximum(fe, 1) / 440.0), np.nan)
        eng = _measure_line(er, te, ste, ye, J.SR, [n_["t0"] / J.SR for n_ in notes])
        seg = os.path.basename(os.path.dirname(os.path.dirname(p))) + "/" + os.path.basename(p)
        out["human"].append((seg, hum))
        out["engine"].append((seg, eng))
        print(f"\n== {seg}: {lyr}")
        print(f"{'word':10s} | human: {'cons':>5s} {'vowel':>5s} {'lead':>4s} {'vsh':>4s} {'glide':>6s} {'dip':>5s} | engine: "
              f"{'cons':>5s} {'vowel':>5s} {'lead':>4s} {'vsh':>4s} {'glide':>6s} {'dip':>5s}   (ms vs beat; dB)")
        for h, e in zip(hum, eng):
            def f_(x, k, fmt):
                v = x.get(k, np.nan)
                return format(v, fmt) if np.isfinite(v) else " " * len(format(0, fmt))
            print(f"{h['word']:10s} | {f_(h, 'c_dev', '+6.0f')} {f_(h, 'v_dev', '+5.0f')} {f_(h, 'onset', '4.0f')} "
                  f"{f_(h, 'vshare', '4.2f')} {f_(h, 'glide_ms', '+6.0f')} {f_(h, 'dip', '5.1f')} | "
                  f"{f_(e, 'c_dev', '+6.0f')} {f_(e, 'v_dev', '+5.0f')} {f_(e, 'onset', '4.0f')} {f_(e, 'vshare', '4.2f')} "
                  f"{f_(e, 'glide_ms', '+6.0f')} {f_(e, 'dip', '5.1f')}")
    summ = {}
    for who in ("human", "engine"):
        R = [r for _, rows in out[who] for r in rows]
        g = lambda k: np.array([r.get(k, np.nan) for r in R], dtype=float)
        ons = g("onset") > 0
        summ[who] = dict(c_dev_med=np.nanmedian(g("c_dev")[ons]), v_dev_med=np.nanmedian(g("v_dev")[ons]),
                         onset_med=np.nanmedian(g("onset")[ons]), vshare_med=np.nanmedian(g("vshare")),
                         glide_med=np.nanmedian(g("glide_ms")), dip_med=np.nanmedian(g("dip")),
                         p_med=np.nanmedian(g("p_dev")), p_sd=np.nanstd(g("p_dev")),
                         v_dev_sd=np.nanstd(g("v_dev")), c_dev_sd=np.nanstd(g("c_dev")))
    print("\nsummary (syllables with a consonant onset for the timing columns):")
    print(f"{'':8s} {'cons start vs beat':>18s} {'vowel vs beat':>14s} {'lead':>6s} {'vowel share':>11s} "
          f"{'pitch halfway vs vowel':>22s} {'dip dB':>7s} {'P-centre vs beat':>17s}")
    for who, m in summ.items():
        print(f"{who:8s} {m['c_dev_med']:+12.0f} (sd {m['c_dev_sd']:3.0f}) {m['v_dev_med']:+8.0f} (sd {m['v_dev_sd']:3.0f}) "
              f"{m['onset_med']:6.0f} {m['vshare_med']:11.2f} {m['glide_med']:+22.0f} {m['dip_med']:7.1f} "
              f"{m['p_med']:+9.0f} (sd {m['p_sd']:3.0f})")
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=240, help="segments to analyse (annotations only)")
    ap.add_argument("--json", default=os.path.join(CACHE, "_summary.json"))
    ap.add_argument("--compare", type=int, default=0, help="compare N human phrases with the engine singing them")
    ap.add_argument("--set", default="{}", help="engine params (JSON) for --compare")
    a = ap.parse_args()
    if a.compare:
        compare(a.compare, json.loads(a.set))
        return
    files = listing()
    ctrl = sorted(f for f in files if f.startswith("English/") and "/Control_Group/" in f and f.endswith(".json"))
    # spread over singers and songs
    rng = np.random.default_rng(1)
    pick = [ctrl[i] for i in sorted(rng.choice(len(ctrl), size=min(a.max, len(ctrl)), replace=False))]
    pairs = [(p, p.replace("/Control_Group/", "/Paired_Speech_Group/")) for p in pick]
    have = set(files)
    with cf.ThreadPoolExecutor(3) as ex:
        list(ex.map(fetch, [p for p, _ in pairs] + [s for _, s in pairs if s in have]))
    anchors = {"word start": lambda r: r["start"], "start+25% onset": lambda r: r["start"] + 0.25 * r["onset"],
               "start+50% onset": lambda r: r["start"] + 0.5 * r["onset"],
               "start+75% onset": lambda r: r["start"] + 0.75 * r["onset"], "vowel onset": lambda r: r["v0"]}
    res = {k: [] for k in anchors}
    sylls, pairs_rows = [], []
    for p, sp in pairs:
        if not os.path.exists(os.path.join(CACHE, p)):
            continue
        seg = json.load(open(os.path.join(CACHE, p)))
        ws = words_of(seg)
        rows = syllables(ws)
        if len(rows) < 6:
            continue
        span = rows[-1]["score"] - rows[0]["score"]
        if span <= 0:
            continue
        for k, f in anchors.items():
            r_, coef = fit(rows, f)
            res[k] += list(r_)
        r_v, coef = fit(rows, anchors["vowel onset"])
        for r, e in zip(rows, r_v):
            r["beat_v"] = coef[0] + coef[1] * r["score"]  # the fitted beat (vowel-anchored)
            r["tempo"] = coef[1]
        # gap available before each syllable: from the previous syllable's vowel onset
        for i, r in enumerate(rows):
            r["gap"] = (r["v0"] - rows[i - 1]["v0"]) if i > 0 else np.nan
            r["prev_note"] = rows[i - 1]["note"] if i > 0 else np.nan
            r["seg"] = p
        sylls += rows
        # paired speech: same words in order
        if sp in have and os.path.exists(os.path.join(CACHE, sp)):
            sws = [w for w in words_of(json.load(open(os.path.join(CACHE, sp))))]
            sw = [w for w in sws if w["vi"]]
            gw = [w for w in ws if w["vi"]]
            if [w["word"] for w in sw] == [w["word"] for w in gw]:
                for g, s in zip(gw, sw):
                    v, vs = g["vi"][0], s["vi"][0]
                    if v != vs or len(g["ph"]) != len(s["ph"]):
                        continue
                    pairs_rows.append(dict(word=g["word"], n_on=v,
                                           sung_on=g["ps"][v] - g["ps"][0], spoken_on=s["ps"][vs] - s["ps"][0],
                                           sung_co=(g["pe"][-1] - g["pe"][g["vi"][-1]]) if len(g["vi"]) == 1 else np.nan,
                                           spoken_co=(s["pe"][-1] - s["pe"][s["vi"][-1]]) if len(s["vi"]) == 1 else np.nan,
                                           sung_v=g["pe"][v] - g["ps"][v], spoken_v=s["pe"][vs] - s["ps"][vs],
                                           note=sum(g["note_dur"])))
    print(f"GTSinger English, plain singing: {len(set(r['seg'] for r in sylls))} segments, {len(sylls)} syllables "
          f"(1 note each), {len(pairs_rows)} words with paired speech\n")
    print("Which point lands on the beat (residual of the score grid fitted to each anchor; smaller = on the grid):")
    for k, v in res.items():
        v = np.array(v) * 1000
        print(f"  {k:16s} sd {v.std():5.1f} ms, median |res| {np.median(np.abs(v)):5.1f} ms")
    S = sylls
    on = np.array([r["onset"] for r in S]) * 1000
    non = np.array([r["n_on"] for r in S])
    note = np.array([r["note"] for r in S]) * 1000
    gap = np.array([r["gap"] for r in S]) * 1000
    vow = np.array([r["vowel"] for r in S]) * 1000
    co = np.array([r["coda"] for r in S]) * 1000
    print("\nConsonant lead before the vowel (sung), by number of onset consonants:")
    for n in (0, 1, 2, 3):
        m = non == n
        if m.sum() > 5:
            print(f"  {n} consonants: median {np.median(on[m]):5.0f} ms, IQR {np.percentile(on[m], 25):.0f}-"
                  f"{np.percentile(on[m], 75):.0f} ms (n={m.sum()})")
    m = (non > 0) & np.isfinite(gap) & (gap > 0)
    frac = on[m] / gap[m]
    print(f"  lead / time since the previous vowel onset: median {np.median(frac):.2f}, 90th pct "
          f"{np.percentile(frac, 90):.2f}, max {frac.max():.2f}")
    for lo, hi in ((0, 250), (250, 500), (500, 1000), (1000, 5000)):
        mm = m & (gap >= lo) & (gap < hi)
        if mm.sum() > 5:
            print(f"  gap {lo}-{hi} ms: lead median {np.median(on[mm]):.0f} ms (n={mm.sum()})")
    print("\nSyllable shape against its note (vowel share = vowel / (onset + vowel + coda)):")
    share = vow / np.maximum(on + vow + co, 1)
    for lo, hi in ((0, 200), (200, 400), (400, 800), (800, 5000)):
        mm = (note >= lo) & (note < hi)
        if mm.sum() > 5:
            print(f"  note {lo}-{hi} ms: vowel {np.median(vow[mm]):4.0f} ms, onset {np.median(on[mm]):3.0f} ms, coda "
                  f"{np.median(co[mm]):3.0f} ms, vowel share {np.median(share[mm]):.2f} (n={mm.sum()})")
    if pairs_rows:
        P = pairs_rows
        so = np.array([r["sung_on"] for r in P]) * 1000
        po = np.array([r["spoken_on"] for r in P]) * 1000
        sv = np.array([r["sung_v"] for r in P]) * 1000
        pv = np.array([r["spoken_v"] for r in P]) * 1000
        sc = np.array([r["sung_co"] for r in P], dtype=float) * 1000
        pc = np.array([r["spoken_co"] for r in P], dtype=float) * 1000
        m = po > 0
        print("\nSpeech -> singing, same singer, same words:")
        print(f"  onset consonants: sung/spoken median {np.median(so[m] / po[m]):.2f} (sung {np.median(so[m]):.0f} ms, "
              f"spoken {np.median(po[m]):.0f} ms; n={m.sum()})")
        b, a0 = np.polyfit(po[m], so[m], 1)
        print(f"  fit: sung onset = {a0:.0f} ms + {b:.2f} x spoken onset")
        mc = np.isfinite(sc) & np.isfinite(pc) & (pc > 0)
        print(f"  codas: sung/spoken median {np.median(sc[mc] / pc[mc]):.2f} (n={mc.sum()})")
        print(f"  vowels: sung/spoken median {np.median(sv / np.maximum(pv, 1)):.1f}")
    json.dump(dict(sylls=[{k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in r.items()}
                          for r in S], pairs=pairs_rows), open(a.json, "w"))
    print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
