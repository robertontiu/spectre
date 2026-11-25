#!/usr/bin/env python3
"""Demos and A/Bs of the modern-strand tools (2026-11-25; docs/MANUAL.md "Modern strands"): shimmer, granular /
freeze, acid, the 909 snare / clap / ride, slide and accent on the polysynth, section automation of sounds, and the
resonance suppressor. For the owner's ear: each case is a short project rendered twice (A: what the engine could do
before, B: the new tool), through the engine's quick master (both loudness-matched at -10.5 LUFS), as 192 kbps MP3
excerpts, with mel spectrograms (<case>.png) and the numbers in numbers.json.

    python3 examples/production/modern/build.py            # every case (about 2 minutes)
    python3 examples/production/modern/build.py shimmer    # one

Run tools/remix/waitfree.sh first (one heavy job at a time). Writes only into this folder; temporary WAVs go to a
temporary folder that is removed.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import studio as ST  # noqa: E402

SR = ST.SR
BPM = 138
BAR = 4 * 60 / BPM


def proj(tracks, patterns, arrangement, returns=None, seed=11):
    return {"title": "demo", "bpm": BPM, "swing": 0.5, "seed": seed, "seeds": "per-track", "genre": "trance",
            "tracks": tracks, "patterns": patterns, "arrangement": arrangement,
            "mix": {"reverb": {"size": 0.6, "return_db": -10}, "returns": returns or {}},
            "master": {"lufs": -10.5}}


KICK = {"inst": {"type": "clubkick", "tune": 50}, "humanize_ms": 0, "vel_jitter": 0.02}
PLUCK = {"inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 12}], "cutoff": 1100,
                  "env": 5000, "fdecay": 0.1, "sustain_level": 0, "decay": 0.22, "release": 0.15},
         "role": "pluck", "eq": "auto", "humanize_ms": 0}
ARP = "0:A4:2 2:E5:2 4:C5:2 6:A5:2 8:E5:2 10:C5:2 12:B4:2 14:E5:2 16:F4:2 18:C5:2 20:A4:2 22:F5:2 24:C5:2 26:A4:2 28:G4:2 30:E5:2"
HALL = {"type": "reverb", "size": 0.92, "damping": 0.4, "predelay_ms": 30, "return_db": -6}


def case_shimmer():
    tr = {"pluck": dict(PLUCK, sends={"space": 0.5})}
    pats = {"p": {"bars": 2, "pluck": ARP}}
    arr = [{"name": "play", "bars": 4, "play": ["p"]}, {"name": "tail", "bars": 4, "play": []}]
    A = proj(tr, pats, arr, {"space": HALL})
    B = proj(tr, pats, arr, {"space": {"type": "shimmer", "decay": 7, "amount": 0.7, "predelay_ms": 30,
                                       "return_db": -6}})
    return A, B, "A: the pluck into a long hall; B: the same send into a shimmer return (+12, decay 7 s, amount 0.7)"


def case_granular():
    tr = {"pluck": dict(PLUCK, sends={"space": 0.6})}
    pats = {"p": {"bars": 2, "pluck": ARP}}
    arr = [{"name": "play", "bars": 4, "play": ["p"]}, {"name": "hold", "bars": 4, "play": []}]
    A = proj(tr, pats, arr, {"space": HALL})
    cloud = {"type": "granular", "pitch_spread": 0.08, "intervals": [0, 0, 12], "scan": 0.5, "dissolve": 6,
             "return_db": -9}
    arrB = copy.deepcopy(arr)
    arrB[1]["auto"] = {"return:space": {"scan": 0}}
    B = proj(tr, pats, arrB, {"space": cloud})
    return A, B, ("A: the pluck into a long hall; B: the same send into a granular return (its pad defaults): "
                  "stretched to half speed while the pluck plays, then frozen (scan 0) and dissolving over 6 s")


ACID_NOTES = ("0:A1:2 2:A2:1! 3:A1:1 4:C2:2~ 6:A1:1 7:E2:1! 8:A1:2 10:G2:2~ 12:A1:1 13:A2:1! 14:A1:2 16:A1:2 "
              "18:A2:1! 19:A1:1 20:C2:2 22:D2:2~ 24:A1:1! 25:A1:1! 26:A1:1! 27:A2:1 28:G2:4~")


def case_acid():
    pats = {"k": {"bars": 1, "kick": "X...X...X...X..."}, "a": {"bars": 2, "acid": ACID_NOTES}}
    arr = [{"name": "a1", "bars": 8, "play": ["k", "a"]}]
    approx = {"inst": {"type": "polysynth", "osc": [{"shape": "saw"}], "cutoff": 400, "reso": 0.8, "env": 2500,
                       "fdecay": 0.15, "sustain_level": 0.6, "decay": 0.2, "release": 0.03},
              "humanize_ms": 0, "vel_jitter": 0, "fx": [{"type": "drive", "db": 8}]}
    acid = {"inst": {"type": "acid", "cutoff": 260, "env_mod": 0.55, "reso": 0.82, "decay": 0.4, "accent": 0.8,
                     "drive": 0.35}, "humanize_ms": 0, "vel_jitter": 0}
    A = proj({"kick": KICK, "acid": approx}, pats, arr)
    arrB = copy.deepcopy(arr)
    arrB[0]["auto"] = {"acid": {"inst": {"cutoff": [180, 700, "log"], "decay": [0.25, 0.7]}}}
    B = proj({"kick": KICK, "acid": acid}, pats, arrB)
    return A, B, ("A: the old approximation (polysynth saw, resonant filter with an envelope, drive): no accent "
                  "coupling, no slide; B: `acid` (accents `!`, slides `~`), cutoff 180 to 700 Hz and decay 0.25 to "
                  "0.7 s automated over the 8 bars")


def case_909():
    pats = {"d": {"bars": 1, "kick": "X...X...X...X...", "clap": "....X.......X...", "ride": "..x...x...x...x.",
                  "snare": "......o.....x..o"}}
    arr = [{"name": "d", "bars": 8, "play": ["d"]}]
    A = proj({"kick": KICK, "clap": {"inst": {"type": "handclap"}}, "snare": {"inst": {"type": "snare"}, "gain_db": -4},
              "ride": {"inst": {"type": "kitride"}}}, pats, arr)
    B = proj({"kick": KICK, "clap": {"inst": {"type": "clap909"}}, "snare": {"inst": {"type": "snare909"}, "gain_db": -4},
              "ride": {"inst": {"type": "ride909"}}}, pats, arr)
    return A, B, "A: handclap, snare, kitride; B: clap909, snare909, ride909 (same patterns, clubkick in both)"


def case_slide():
    lead = {"inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 10}, {"shape": "pulse",
                                                                                                 "level": 0.5}],
                     "cutoff": 700, "env": 3500, "fdecay": 0.18, "reso": 0.4, "sustain_level": 0.7, "release": 0.1},
            "humanize_ms": 0}
    notes = "0:E4:3 3:G4:3! 6:A4:2~ 8:C5:4 12:B4:2 14:G4:2~ 16:A4:3! 19:E4:3 22:G4:2~ 24:D5:6! 30:C5:2~"
    pats = {"k": {"bars": 1, "kick": "X...X...X...X..."}, "l": {"bars": 2, "lead": notes}}
    arr = [{"name": "l", "bars": 8, "play": ["k", "l"]}]
    B_lead = copy.deepcopy(lead)
    B_lead["inst"].update(glide_ms=90, accent=0.9)
    return (proj({"kick": KICK, "lead": lead}, pats, arr), proj({"kick": KICK, "lead": B_lead}, pats, arr),
            "A: a polysynth line where `~` and `!` do nothing but velocity; B: the same with `glide_ms` 90 (slides) "
            "and `accent` 0.9 (accented notes open the filter further)")


def case_automation():
    pad = {"inst": {"type": "supersaw", "model": 2, "detune": 12, "drift": 0.05, "attack": 0.3, "release": 0.8,
                    "cutoff": 2600, "lfo": [{"dest": "cutoff", "rate": 0.3, "depth": 0.05}]},
           "role": "pad", "eq": "auto", "send_reverb": 0.2}
    pats = {"p": {"bars": 4, "pad": {"chords": "Am9:16 Fmaj7:16 Cadd9:16 G6:16", "style": "stabs",
                                     "rhythm": "x.......x.......", "stab_len": 8, "register": "A3", "vel": 0.7}}}
    arr = [{"name": "a", "bars": 8, "play": ["p"]}]
    A = proj({"pad": pad}, pats, arr)
    arrB = copy.deepcopy(arr)
    arrB[0]["auto"] = {"pad": {"inst": {"detune": [8, 34], "drift": [0.0, 0.8], "lfo.0.depth": [0.02, 0.9],
                                        "lfo.0.rate": [0.3, 3.0, "log"], "cutoff": [1500, 5000, "log"]}}}
    B = proj({"pad": pad}, pats, arrB)
    return A, B, ("A: a supersaw pad, every chord the same; B: the same pad with section `inst` automation over 8 "
                  "bars: detune 8 to 34 cents, drift 0 to 0.8, cutoff LFO depth 0.02 to 0.9 octave and rate 0.3 to "
                  "3 Hz, cutoff 1.5 to 5 kHz (each chord takes the values at its onset)")


def case_suppress():
    lead = {"inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 9}], "cutoff": 2400,
                     "reso": 0.9, "sustain_level": 0.9, "release": 0.1},
            "humanize_ms": 0, "fx": [{"type": "drive", "db": 14}, {"type": "sat", "amount": 0.4}]}
    notes = "0:A4:4 4:C5:4 8:E5:4 12:D5:4 16:C5:4 20:B4:4 24:A4:8"
    pats = {"l": {"bars": 2, "lead": notes}}
    arr = [{"name": "l", "bars": 8, "play": ["l"]}]
    B_lead = copy.deepcopy(lead)
    B_lead["fx"] = B_lead["fx"] + [{"type": "suppress", "depth": 8, "threshold": 2}]
    return (proj({"lead": lead}, pats, arr), proj({"lead": B_lead}, pats, arr),
            "A: a saturated resonant lead (drive 14 dB, sat 0.4); B: the same with `suppress` after the saturation "
            "(depth 8 dB, threshold 2 dB)")


CASES = {"shimmer": case_shimmer, "granular": case_granular, "acid": case_acid, "909": case_909, "slide": case_slide,
         "automation": case_automation, "suppress": case_suppress}


# ------------------------------------------------------------------ measurements

def third_octave(x, lo=100, hi=16000):
    X = np.abs(np.fft.rfft(x.mean(0) if x.ndim == 2 else x)) ** 2
    f = np.fft.rfftfreq(x.shape[-1], 1 / SR)
    cs = 1000 * 2 ** (np.arange(-15, 14) / 3)
    cs = cs[(cs >= lo) & (cs <= hi)]
    return cs, np.array([10 * np.log10(X[(f >= c * 2 ** -(1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in cs])


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)) + 1e-12))


def measure(name, a, b):
    """A few numbers per case (on the quick-mastered excerpts)."""
    m = {}
    if name in ("shimmer", "granular"):
        t0 = int(4 * BAR * SR)
        for k, x in (("A", a), ("B", b)):
            m[f"{k} tail (bars 6-8) vs playing (bars 1-4), dB"] = round(rms_db(x[:, int(5 * BAR * SR):int(8 * BAR * SR)])
                                                                     - rms_db(x[:, :t0]), 1)
            cs, s = third_octave(x[:, t0:int(8 * BAR * SR)], 1000, 16000)
            m[f"{k} tail: 4-16 kHz vs 1-4 kHz, dB"] = round(float(10 * np.log10(np.sum(10 ** (s[cs >= 4000] / 10)))
                                                                - 10 * np.log10(np.sum(10 ** (s[cs < 4000] / 10)))), 1)
    if name == "suppress":
        from scipy import signal
        from scipy.ndimage import maximum_filter1d
        for k, x in (("A", a), ("B", b)):
            f, P = signal.welch(x.mean(0), SR, nperseg=8192)
            d = 10 * np.log10(P + 1e-20)
            u = maximum_filter1d(d, int(250 / (f[1] - f[0])) | 1)
            lf = 2 ** np.arange(np.log2(500), np.log2(12000), 1 / 12)
            g = np.interp(lf, f, u)
            from scipy.ndimage import gaussian_filter1d
            tr = gaussian_filter1d(g, 12 / 2.355)
            m[f"{k} largest bulge of the spectrum's peak envelope over its 1-octave trend, 0.5-12 kHz, dB"] = \
                round(float(np.max(g - tr)), 1)
    if name == "automation":
        for k, x in (("A", a), ("B", b)):
            out = []
            for b0 in (0, 6):  # bars 1-2 and 7-8
                seg_x = x[:, int(b0 * BAR * SR):int((b0 + 2) * BAR * SR)].mean(0)
                X = np.abs(np.fft.rfft(seg_x)) ** 2
                fx = np.fft.rfftfreq(len(seg_x), 1 / SR)
                out.append(round(float((fx * X).sum() / X.sum())))
            m[f"{k} spectral centroid bars 1-2 / 7-8, Hz"] = out
    return m


def chroma_events(x, a, b, thr=0.15):
    """Harmonic events of a mono signal over [a, b) s: 12-bin chroma (4096-point STFT, 11.6 ms hop) averaged over
    100 ms; novelty = 1 - cosine between the chroma now and 150 ms before; events = novelty peaks over 0.15, at least
    116 ms apart. Returns [events per second, 95th percentile of the novelty]: a melody (new notes) scores high, a
    held pad near 0."""
    import librosa
    from scipy.ndimage import uniform_filter1d
    from scipy.signal import find_peaks
    seg = np.asarray(x[int(a * SR):int(b * SR)], dtype=np.float32)
    C = uniform_filter1d(librosa.feature.chroma_stft(y=seg, sr=SR, n_fft=4096, hop_length=512), 9, axis=1)
    A_, B_ = C[:, 13:], C[:, :-13]
    nv = 1 - (A_ * B_).sum(0) / (np.linalg.norm(A_, axis=0) * np.linalg.norm(B_, axis=0) + 1e-9)
    pk, _ = find_peaks(nv, height=thr, distance=10)
    return [round(len(pk) / (b - a), 2), round(float(np.percentile(nv, 95)), 3)]


def timbre(x, a, b):
    """Spectral centroid (Hz), the strongest peak (Hz) and its share of the energy (+-1 semitone), share above 2 kHz."""
    seg = np.asarray(x[int(a * SR):int(b * SR)], dtype=np.float64)
    X = np.abs(np.fft.rfft(seg)) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    k = int(np.argmax(X * (f > 80)))
    m = (f > f[k] * 2 ** (-1 / 12)) & (f < f[k] * 2 ** (1 / 12))
    return {"centroid": int((f * X).sum() / X.sum()), "peak_hz": int(f[k]), "peak_share": round(float(X[m].sum() / X.sum()), 2),
            "above_2k": round(float(X[f > 2000].sum() / X.sum()), 2)}


def bumps(x, a, b):
    """Level bumps of a mono signal over [a, b) s: 10 ms RMS frames against their 200 ms running median (dB); returns
    [frames more than 3 dB over it, the largest excess]: what is heard as single grains or stray notes in a cloud."""
    from scipy.ndimage import median_filter
    seg = np.asarray(x[int(a * SR):int(b * SR)], dtype=np.float64)
    k = int(0.01 * SR)
    e = 20 * np.log10(np.sqrt((seg[:len(seg) // k * k].reshape(-1, k) ** 2).mean(1)) + 1e-12)
    d = e - median_filter(e, 21)
    return [int(np.sum(d > 3)), round(float(d.max()), 1)]


def mp3(x, path):
    with tempfile.TemporaryDirectory() as td:
        import soundfile as sf
        w = os.path.join(td, "x.wav")
        sf.write(w, x.T, SR, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "192k", path], check=True)


def picture(name, a, b, path, title):
    import librosa
    import librosa.display
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.6), sharey=True)
    for ax, x, lab in ((axs[0], a, "A"), (axs[1], b, "B")):
        M = librosa.feature.melspectrogram(y=x.mean(0), sr=SR, n_fft=2048, hop_length=512, n_mels=128, fmax=18000)
        librosa.display.specshow(librosa.power_to_db(M + 1e-10, ref=np.max), sr=SR, hop_length=512, y_axis="mel",
                                 x_axis="time", fmax=18000, ax=ax, cmap="magma", vmin=-80)
        ax.set_title(f"{name} {lab}", fontsize=10)
    fig.suptitle(title, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)


def main():
    names = sys.argv[1:] or list(CASES)
    numbers = {}
    npath = os.path.join(HERE, "numbers.json")
    if os.path.exists(npath):
        numbers = json.load(open(npath))
    for name in names:
        A, B, desc = CASES[name]()
        outs = []
        for P in (A, B):
            mix, meta = ST.render(P)
            n = int(min(meta["duration"] + 0.5, mix.shape[1] / SR) * SR)
            x = mix[:, :n].copy()
            fo = int(0.4 * SR)
            x[:, -fo:] *= np.linspace(1, 0, fo)
            outs.append(x)
        a, b = outs
        if name == "granular":  # the cloud alone, as first built and now: stray notes, harmonic events, freeze timbre
            extra_g = {}
            before = {"grain_ms": 160, "density": 40, "spray_ms": 120, "position_ms": 250, "smooth": 2,
                      "blur_ms": 200, "tone_hz": 0, "dissolve": 0}
            for lab, over in (("as heard in the second demo (grain 160 ms, density 40, spray 120 ms, blur 200 ms, no "
                               "tone or dissolve)", before), ("now (defaults, dissolve 6 s)", {})):
                Pq = copy.deepcopy(B)
                Pq["mix"]["returns"]["space"].update(over)
                st = {}
                ST.render(Pq, stem_hook=lambda nm, x: st.__setitem__(nm, x.mean(0).copy()))
                c = st["(space)"]
                extra_g[f"cloud alone, {lab}"] = {
                    "stretch bars 1-4, harmonic events per s and p95 chroma novelty": chroma_events(c, 0.7, 4 * BAR),
                    "freeze bars 5-8, 10 ms level bumps > 3 dB over the 200 ms running median, count and max dB":
                        bumps(c, 4.3 * BAR, 7.8 * BAR),
                    "freeze bars 5-6, timbre": timbre(c, 4.5 * BAR, 6 * BAR),
                    "freeze level every 1 s from its start, dB": [round(rms_db(c[int((4 * BAR + k) * SR):int((4 * BAR + k + 1) * SR)])
                                                                  - rms_db(c[int(4 * BAR * SR):int((4 * BAR + 1) * SR)]), 1)
                                                            for k in range(6)]}
            dry = st["pluck"]
            extra_g["dry pluck, bars 1-4: harmonic events per s and p95 chroma novelty"] = chroma_events(dry, 0.2, 4 * BAR)
            extra_g["dry pluck timbre"] = timbre(dry, 0, 4 * BAR)
        else:
            extra_g = {}
        if name == "automation":  # the values each chord of B was rendered with (read back from the engine)
            ev = []
            for t in sorted(e["t"] for e in meta["events"]["pad"]):
                if not ev or t - ev[-1] > 0.05:  # one onset per chord
                    ev.append(t)
            p = B["tracks"]["pad"]["inst"]
            per = [ST._inst_at(p, ["pad"], t)[0] for t in ev]
            numbers.setdefault(name, {})
            extra = {"B per chord: detune, drift, lfo depth, lfo rate, cutoff":
                     [[round(q["detune"], 1), round(q["drift"], 2), round(q["lfo"][0]["depth"], 2),
                       round(q["lfo"][0]["rate"], 2), round(q["cutoff"])] for q in per]}
        else:
            extra = {}
        mp3(a, os.path.join(HERE, f"{name}-A.mp3"))
        mp3(b, os.path.join(HERE, f"{name}-B.mp3"))
        picture(name, a, b, os.path.join(HERE, f"{name}.png"), desc)
        numbers[name] = dict(what=desc, **measure(name, a, b), **extra, **extra_g)
        print(name, json.dumps(numbers[name], indent=1))
    json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
