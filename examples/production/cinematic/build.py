"""A/B of the cinematic-hybrid sounds (2026-11-26): each new sound against the stand-in the genre brief names
(docs/CINEMATIC_HYBRID.md "Engine mapping", the "Without it" column), measured against recordings where CC0 / public
domain ones exist, and short phrases rendered through the engine for the ear.

    python3 examples/production/cinematic/build.py measure      # the table in README.md (needs the references)
    python3 examples/production/cinematic/build.py audio        # the mp3s (renders in a scratch folder)

References (not in git: University of Iowa MIS, VSCO-2-CE; fetched by the research agent into
~/.cache/spectre/refs/cinematic, override with REFS=...). The measured models were fitted on these same recordings
(fit_winds.py, fit_drums.py, fit_bass.py), so the distances below say how well each model and stand-in reproduces
them, not how it generalises.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "engine"))
REFS = os.environ.get("REFS", os.path.expanduser("~/.cache/spectre/refs/cinematic"))
SR = 44100
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(name, shift=0):
    m = re.match(r"([A-G])(b|#)?(-?\d)", name)
    k = NAMES[m.group(1)] + {"b": -1, "#": 1, None: 0}[m.group(2)] + 12 * (int(m.group(3)) + 1) + shift
    return 440.0 * 2 ** ((k - 69) / 12)


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    e = np.convolve(x ** 2, np.ones(441) / 441, "same")
    i = int(np.argmax(e > e.max() * 1e-3))
    return x[i:]


BANDS = 50 * 2 ** (np.arange(0, 25) / 3)   # 50 Hz - 12.7 kHz, third octaves


def third_oct(x, t0, t1):
    seg = np.asarray(x, dtype=np.float64)[int(t0 * SR):int(t1 * SR)]
    f, P = signal.welch(seg, SR, nperseg=8192)
    lv = np.array([P[(f >= b * 2 ** (-1 / 6)) & (f < b * 2 ** (1 / 6))].sum() for b in BANDS])
    lv = 10 * np.log10(lv + 1e-30)
    return lv - 10 * np.log10((10 ** (lv / 10)).sum())


def dist(ref, y, t0=0.3, t1=1.3):
    a, b = third_oct(ref, t0, t1), third_oct(y, t0, t1)
    m = a > a.max() - 30   # the bands that carry the sound (not the recording's noise floor between low harmonics)
    return float(np.mean(np.abs(a[m] - b[m])))


def decay_ms(x, dB=20):
    a = np.abs(signal.hilbert(np.asarray(x, dtype=np.float64)))
    a = signal.sosfiltfilt(signal.butter(2, 30, fs=SR, output="sos"), a)
    e = 20 * np.log10(np.maximum(a, 1e-12))
    pk = int(np.argmax(e))
    d = e[pk:] - e[pk]
    i = int(np.argmax(d < -dB))
    return i / SR * 1000 if i else float("nan")


def mono(y):
    y = np.asarray(y, dtype=np.float64)
    return y.mean(0) if y.ndim == 2 else y


def measure():
    import instruments as I
    import orchestra as O
    import chamber as C
    rows = []

    def note_line(kind, f, dur=1.6, p=None):
        nt = [dict(t0=0, n=int(dur * SR), f=f, vel=0.9, glide=False)]
        return mono(I.mono_voice(kind, dict(p or {}), nt, int((dur + 0.5) * SR)))

    def add(sound, ref, cands, t0=0.3, t1=1.3):
        r = load(ref)
        out = {k: round(dist(r, y, t0, t1), 2) for k, y in cands.items()}
        rows.append(dict(sound=sound, ref=os.path.relpath(ref, REFS), **out))
        print(sound, os.path.basename(ref), out, flush=True)

    poly = lambda f, d=1.6: mono(I.TONAL["polysynth"]({}, f, 0.9, d))
    winds = [("horn", "Horn", "Horn.ff.*.aif", 0), ("trumpet", "BbTrumpet", "Trumpet.novib.ff.*.aif", 0),
             ("trombone", "TenorTrombone", "TenorTrombone.ff.*.aif", 0), ("tuba", "Tuba", "Tuba.ff.*.aif", 0),
             ("bass_trombone", "BassTrombone", "BassTrombone.ff.*.aif", 0)]
    vs_brass = {"horn": "F Horn", "trombone": "Tenor Trombone", "trumpet": "Trumpet", "tuba": "Tuba"}
    for inst, d, pat, sh in winds:
        refs = sorted(glob.glob(os.path.join(REFS, d, pat)))
        if inst in vs_brass:  # VSCO-2-CE: the loudest layer of each note (named an octave low: C3 = 261 Hz)
            top = {}
            for q in glob.glob(os.path.join(REFS, "vsco", "Brass", vs_brass[inst], "sus", "*.wav")):
                m = re.match(r".*_sus_([A-G]#?-?\d)_v(\d)", q)
                if m and int(m.group(2)) >= top.get(m.group(1), (0, ""))[0]:
                    top[m.group(1)] = (int(m.group(2)), q)
            refs += [q for _, q in sorted(top.values(), key=lambda t: t[1])][::2]
        for ref in refs:
            if ref.endswith(".wav"):
                name = re.match(r".*_sus_([A-G]#?-?\d)_", ref).group(1)
                f = hz(name, 12)
                add(f"brass {inst}", ref, {"A polysynth": poly(f),
                                           "A trembita": note_line("trembita", f) if inst == "horn" else poly(f),
                                           "B brass": mono(O.brass({"section": inst, "players": 1}, f, 1.0, 1.6))})
                continue
            f = hz(os.path.basename(ref).split(".")[-3], sh)
            add(f"brass {inst}", ref, {"A polysynth": poly(f),
                                       "A trembita": note_line("trembita", f) if inst == "horn" else poly(f),
                                       "B brass": mono(O.brass({"section": inst, "players": 1}, f, 1.0, 1.6))})
    ww = [("flute", "Flute", "Flute.nonvib.ff.*.aif", "ney"), ("oboe", "Oboe", "Oboe.ff.*.aif", None),
          ("clarinet", "BbClarinet", "BbClarinet.ff.*.aif", None), ("bassoon", "Bassoon", "Bassoon.ff.*.aif", None)]
    for inst, d, pat, alt in ww:
        for ref in sorted(glob.glob(os.path.join(REFS, d, pat))):
            name = os.path.basename(ref).split(".")[-3]
            f = hz(name)  # Iowa names every file at sounding pitch (the clarinet's Bb3 peaks at 232 Hz)
            add(f"woodwind {inst}", ref, {"A " + (alt or "polysynth"): note_line(alt, f) if alt else poly(f),
                                          "B woodwind": mono(O.woodwind({"instrument": inst, "vibrato": 0.0}, f, 1.0, 1.6))})
    for ref in sorted(glob.glob(os.path.join(REFS, "DoubleBass", "*.aif")))[::3]:
        f = hz(os.path.basename(ref).split(".")[-3])
        nt = [dict(t0=0, n=int(1.6 * SR), f=f, vel=0.9, glide=False, art=[])]
        cel = mono(C.strings_section({"section": "celli", "vibrato": 0.0}, [dict(nt[0], f=2 * f)], int(2.1 * SR)))
        sub = mono(I.mono_voice("sub", {}, nt, int(2.1 * SR))) if "sub" in I.MONO else 0
        add("basses", ref, {"A celli 8va + sub": cel + 0.5 * sub,
                            "B basses": mono(C.strings_section({"section": "basses", "vibrato": 0.0}, nt, int(2.1 * SR)))})
    vs = os.path.join(REFS, "vsco", "Percussion")
    for ref, f1 in (("Timpani/Timpani1_Hit_v3_rr1_Sum.wav", 89.8), ("Timpani/Timpani3_Hit_v3_rr1_Sum.wav", 142.3),
                    ("Timpani/Timpani5_Hit_v3_rr1_Sum.wav", 190.4)):
        p = os.path.join(vs, ref)
        if os.path.exists(p):
            add("timpani", p, {"A tom": mono(I.DRUMS["tom"]({"tune": f1, "decay": 0.6}, 0.9)),
                               "B timpani": mono(O.timpani({}, f1, 0.9, 0.5))}, 0.0, 1.0)
            r = load(p)
            rows[-1]["decay_ms_-20dB"] = {"ref": round(decay_ms(r)), "A": round(decay_ms(I.DRUMS["tom"]({"tune": f1, "decay": 0.6}, 0.9))),
                                          "B": round(decay_ms(O.timpani({}, f1, 0.9, 0.5)))}
    p = os.path.join(vs, "BDrumNewhit_v5_rr1_Sum.wav")
    if os.path.exists(p):
        add("bassdrum", p, {"A toba": mono(I.DRUMS["toba"]({}, 0.9)), "B bassdrum": mono(O.bassdrum({}, 0.9))}, 0.0, 1.0)
        r = load(p)
        rows[-1]["decay_ms_-20dB"] = {"ref": round(decay_ms(r)), "A": round(decay_ms(I.DRUMS["toba"]({}, 0.9))),
                                      "B": round(decay_ms(O.bassdrum({}, 0.9)))}
    cy = os.path.join(REFS, "vsco", "VSCO 1 Percussion", "varMetal", "Cymbals", "susp")
    p = os.path.join(cy, "susp_hit_hardmall_f.wav")
    if os.path.exists(p):
        add("suscymbal hit", p, {"A crash": mono(I.DRUMS["crash"]({}, 0.9)),
                                 "B suscymbal": mono(O.suscymbal({"mode": "hit"}, 0, 0.9, 0.1))}, 0.0, 1.5)
    p = os.path.join(cy, "susp_hit_softmall_roll2_cresc.wav")
    if os.path.exists(p):
        r = load(p)
        pk = int(np.argmax(np.convolve(r ** 2, np.ones(4410), "same"))) / SR
        rev = mono(I.DRUMS["crash"]({}, 0.9))[::-1]
        add("suscymbal swell", p, {"A reversed crash": rev, "B suscymbal": mono(O.suscymbal({}, 0, 0.9, pk))},
            0.0, pk)
    # the hall against the algorithmic reverb at the size the brief names as the stand-in: the impulse response of each
    # return (as studio renders it), Schroeder T20 per octave, the gap to the first reflection
    import studio as ST
    x = np.zeros((2, 6 * SR), dtype=np.float32)
    x[:, 100] = 1.0
    for name, cfg in (("A reverb size 0.9", dict(REVERB["hall"], predelay_ms=0)), ("B hall", dict(HALL["hall"], predelay_ms=0))):
        ir = ST._process_return("h", cfg, x.copy(), 0.5, {}).astype(np.float64).mean(0)
        rt = {}
        for lo in (125, 250, 500, 1000, 2000, 4000):
            b = signal.sosfilt(signal.butter(2, [lo / 2 ** 0.5, lo * 2 ** 0.5], btype="band", fs=SR, output="sos"), ir)
            E = np.cumsum((b ** 2)[::-1])[::-1]
            L = 10 * np.log10(E / E[0] + 1e-30)
            i1, i2 = int(np.argmax(L < -5)), int(np.argmax(L < -25))
            rt[lo] = round(float(-60 / np.polyfit(np.arange(i1, i2) / SR, L[i1:i2], 1)[0]), 2)
        first = (int(np.argmax(np.abs(ir) > np.abs(ir).max() * 0.1)) - 100) / SR * 1000
        rows.append(dict(sound="hall", candidate=name, t20_s_by_octave=rt, first_reflection_ms=round(first, 1)))
        print("hall", name, "T20 by octave", rt, "first reflection", round(first, 1), "ms", flush=True)
    json.dump(rows, open(os.path.join(HERE, "measurements.json"), "w"), indent=1)
    print("wrote measurements.json")


# ------------------------------------------------------------------ audio A/B

def proj(tracks, patterns, arrangement, bpm=90, returns=None, genre="cinematic"):
    P = {"title": "ab", "bpm": bpm, "key": "D minor", "seed": 3, "genre": genre, "tracks": tracks,
         "patterns": patterns, "arrangement": arrangement, "mix": {}}
    if returns:
        P["mix"]["returns"] = returns
    return P


HALL = {"hall": {"type": "hall", "predelay_ms": 20, "return_db": -6}}
REVERB = {"hall": {"type": "reverb", "size": 0.9, "predelay_ms": 20, "return_db": -6}}


def ab_brass(new):
    inst = ({"type": "brass", "section": "horns"} if new else {"type": "polysynth"})
    low = ({"type": "brass", "section": "trombones"} if new else {"type": "polysynth"})
    t = {"horns": {"inst": inst, "sends": {"hall": 0.35}}, "low": {"inst": low, "sends": {"hall": 0.3}, "gain_db": -2}}
    pat = {"a": {"bars": 4, "horns": "0:D4:12/swell 12:F4:4 16:A4:16 32:G4:8/sfz 40:F4:8 48:E4:16",
                 "low": "0:D3:16 16:A2:16 32:Bb2:16 48:A2:4/stab 52:A2:4/stab 56:A2:8/fall"}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 80, HALL)


def ab_drums(new):
    if new:
        t = {"timp": {"inst": {"type": "timpani"}, "sends": {"hall": 0.2}},
             "taiko": {"inst": {"type": "taiko"}, "sends": {"hall": 0.25}},
             "gran": {"inst": {"type": "bassdrum"}, "sends": {"hall": 0.3}},
             "cym": {"inst": {"type": "suscymbal"}, "sends": {"hall": 0.2}}}
        pat = {"a": {"bars": 4, "timp": "0:D2:2 6:D2:2 8:A2:2 14:A2:2 16:D2:2 24:A2:2 48:D2:16/roll,cresc",
                     "taiko": "x..x..x.x...x.x." * 3 + "x.x.x.x.x.x.xxxx",
                     "gran": "x...............x...............x...............x...............",
                     "cym": "48:C4:16"}}
    else:
        t = {"timp": {"inst": {"type": "tom", "tune": 73, "decay": 0.6}, "sends": {"hall": 0.2}},
             "taiko": {"inst": {"type": "kittom"}, "sends": {"hall": 0.25}},
             "gran": {"inst": {"type": "toba"}, "sends": {"hall": 0.3}},
             "cym": {"inst": {"type": "crash"}, "sends": {"hall": 0.2}}}
        pat = {"a": {"bars": 4, "timp": "x.....x.x.....x.x.......x.......................xxxxxxxxxxxxxxxx",
                     "taiko": "x..x..x.x...x.x." * 3 + "x.x.x.x.x.x.xxxx",
                     "gran": "x...............x...............x...............x...............",
                     "cym": "................................................................"}}
    P = proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}, {"name": "hit", "bars": 1, "play": ["a"]}], 100, HALL)
    if not new:
        P["arrangement"][1]["enter"] = {"crash": 0.8}
    return P


def ab_basses(new):
    t = {"celli": {"inst": {"type": "strings_section", "section": "celli"}, "sends": {"hall": 0.25}}}
    ost = " ".join(f"{k}:{'D3' if k % 4 != 2 else 'A3'}:1/sp" for k in range(0, 32))
    low = " ".join(f"{k}:{'D2' if k % 4 != 2 else 'A2'}:1/sp" for k in range(0, 32))
    pat = {"a": {"bars": 2, "celli": ost}}
    if new:
        t["basses"] = {"inst": {"type": "strings_section", "section": "basses"}, "sends": {"hall": 0.2}}
        pat["a"]["basses"] = low
    else:
        t["sub"] = {"inst": {"type": "sub"}}
        pat["a"]["sub"] = " ".join(f"{k}:D1:4" for k in range(0, 32, 4))
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 120, HALL)


def ab_hall(new):
    t = {"horns": {"inst": {"type": "brass", "section": "horns"}, "sends": {"hall": 0.4}},
         "timp": {"inst": {"type": "timpani"}, "sends": {"hall": 0.3}}}
    pat = {"a": {"bars": 4, "horns": "0:D4:6/stab 8:F4:6/stab 16:A4:24/sfz",
                 "timp": "0:D2:2 8:D2:2 16:A2:2"}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 80, HALL if new else REVERB)


def ab_choir(new):
    line = "0:D4:8 8:E4:8 16:F4:16 32:A4:12 44:G4:4 48:F4:16"
    if new:
        t = {"choir": {"inst": {"type": "vox2choir", "voices": 6, "vowels": ["a", "o"], "onset": "h"},
                       "sends": {"hall": 0.45}},
             "pad": {"inst": {"type": "choir"}, "gain_db": -6, "sends": {"hall": 0.4}}}
        pat = {"a": {"bars": 4, "choir": line, "pad": {"chords": "Dm:16 Bb:16 F:16 C:16", "style": "sustain"}}}
    else:
        t = {f"v{j}": {"inst": {"type": "vox2", "seed": j + 1, "vowels": ["a", "o"], "onset": "h"},
                       "pan": (j / 5 - 0.5) * 1.2, "gain_db": -6, "sends": {"hall": 0.45}} for j in range(6)}
        t["pad"] = {"inst": {"type": "choir"}, "gain_db": -6, "sends": {"hall": 0.4}}
        pat = {"a": {"bars": 4, **{f"v{j}": line for j in range(6)},
                     "pad": {"chords": "Dm:16 Bb:16 F:16 C:16", "style": "sustain"}}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 80, HALL)


def ab_trailer(new):
    if new:
        t = {"braam": {"inst": {"type": "braam"}, "sends": {"hall": 0.3}},
             "hit": {"inst": {"type": "impact"}, "sends": {"hall": 0.4}},
             "rise": {"inst": {"type": "shepard"}},
             "air": {"inst": {"type": "whoosh"}}}
        pat = {"a": {"bars": 4, "rise": "0:C4:48", "air": "40:C4:8",
                     "hit": "................................................x...............",
                     "braam": "48:D2:16"}}
    else:
        t = {"braam": {"inst": {"type": "fmgrowl"}, "sends": {"hall": 0.3}},
             "braamsub": {"inst": {"type": "sub"}},
             "hit": {"inst": {"type": "toba"}, "sends": {"hall": 0.4}},
             "rise": {"inst": {"type": "supersaw"}}}
        pat = {"a": {"bars": 4, "rise": "0:C3:48~", "hit": "................................................x...............",
                     "braam": "48:D2:16", "braamsub": "48:D1:16"}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 90, HALL)


def ab_winds(new):
    if new:
        t = {"fl": {"inst": {"type": "woodwind", "instrument": "flute"}, "sends": {"hall": 0.35}},
             "cl": {"inst": {"type": "woodwind", "instrument": "clarinet"}, "sends": {"hall": 0.3}},
             "bn": {"inst": {"type": "woodwind", "instrument": "bassoon"}, "sends": {"hall": 0.3}}}
    else:
        t = {"fl": {"inst": {"type": "ney"}, "sends": {"hall": 0.35}},
             "cl": {"inst": {"type": "polysynth"}, "sends": {"hall": 0.3}},
             "bn": {"inst": {"type": "polysynth"}, "sends": {"hall": 0.3}}}
    pat = {"a": {"bars": 4, "fl": "0:F#5:4 4:F#5:4 8:G5:4 12:A5:4 16:A5:4 20:G5:4 24:F#5:4 28:E5:4",
                 "cl": "0:D4:8 8:E4:8 16:F#4:8 24:G4:8",
                 "bn": "32:D3:4 36:E3:4 40:F#3:4 44:D3:4 48:E3:4 52:F#3:2 54:G3:2 56:F#3:4 60:D3:4"}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 90, HALL)


def ab_accordion(new):
    inst = {"type": "accordion"} if new else {"type": "organ"}
    t = {"acc": {"inst": inst, "sends": {"hall": 0.25}}}
    pat = {"a": {"bars": 4, "acc": "0:F#4:4 4:F#4:4 8:G4:4 12:A4:4 16:A4:4 20:G4:4 24:F#4:4 28:E4:4 "
                                    "32:D4:4 36:D4:4 40:E4:4 44:F#4:4 48:F#4:6 54:E4:2 56:E4:8"}}
    return proj(t, pat, [{"name": "s", "bars": 4, "play": ["a"]}], 100, HALL)


JOBS = {"brass": ab_brass, "drums": ab_drums, "basses": ab_basses, "hall": ab_hall, "choir": ab_choir,
        "trailer": ab_trailer, "winds": ab_winds, "accordion": ab_accordion}


def audio(names):
    tmp = tempfile.mkdtemp(prefix="cin-ab-")
    try:
        for name in names:
            for tag, new in (("A", False), ("B", True)):
                d = os.path.join(tmp, f"{name}-{tag}")
                os.makedirs(d)
                json.dump(JOBS[name](new), open(os.path.join(d, "project.json"), "w"), indent=1)
                subprocess.run([sys.executable, os.path.join(REPO, "engine", "studio.py"), "render"], cwd=d,
                               env=dict(os.environ, BEAT_DIR=d), check=True, stdout=subprocess.DEVNULL)
                wav = sorted(glob.glob(os.path.join(d, "renders", "v*.wav")))[0]
                out = os.path.join(HERE, f"{name}-{tag}.mp3")
                # both sides at -20 LUFS integrated, so the A/B compares sound, not level
                r = subprocess.run(["ffmpeg", "-nostats", "-i", wav, "-af", "ebur128", "-f", "null", "-"],
                                   capture_output=True, text=True).stderr
                lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
                subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-i", wav, "-af", f"volume={-20 - lufs:.2f}dB",
                                "-b:a", "128k", out], check=True)
                print("wrote", os.path.basename(out), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "measure"
    if job == "measure":
        measure()
    else:
        audio(sys.argv[2:] or list(JOBS))
