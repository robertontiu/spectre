"""humanref: measure how human singers time and shape English words, from the GTSinger corpus.

GTSinger (Zhang et al., NeurIPS 2024; https://huggingface.co/datasets/GTSinger/GTSinger; CC BY-NC-SA 4.0) has
studio singing with phoneme-level alignment, the score's note durations, and the same lyrics read by the same singer
("paired speech"). We only measure it: nothing from it is copied into the repo or used in a track. Files are cached
in ~/.cache/spectre/refs/gtsinger (outside git), and so is the per-syllable table this tool writes (--json, default
_summary.json there): it is an adaptation of CC BY-NC-SA data, so it stays out of this MIT repository; the summary
numbers it prints are quoted in docs/voice/GENERAL.md, and this tool regenerates the table from the corpus.

What it measures (on the "Control_Group" takes, i.e. plain singing):
- which point of a sung syllable singers put on the beat: the score grid (running sum of the notes' score durations,
  rests included) is fitted to the audio by least squares (offset + tempo) using different anchors (the word's
  first phone, the vowel onset, and points in between); the anchor with the smallest residual is what lands on the
  beat. Residuals are reported in ms;
- per word: the consonant lead (phones before the first vowel), the vowel and coda lengths against the note's
  score length, and the same word read aloud (paired speech): how a singer turns speech timing into sung timing;
- the consonant lead against the spoken onset length and against the time available before the note.
These are the human reference in docs/voice/GENERAL.md "Timing": a yardstick for how a sung voice times its words.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=240, help="segments to analyse (annotations only)")
    ap.add_argument("--json", default=os.path.join(CACHE, "_summary.json"))
    a = ap.parse_args()
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
