"""Builds the chamber-score instrument A/B in this folder (python3 examples/chamberscore/build.py [names...]).

The old stand-in first, then the new instrument, on the same notes (waltz at quarter = 168 on the 12-step grid):
a  glockenspiel stand-in: `bell` (decay 1.3, ratio 2.76), as in examples/chamberscore-test.json
b  `glockenspiel` (hardness 0.5: the Iowa plastic mallet)        c  `glockenspiel` hardness 0.9 (towards brass)
d  celesta stand-in: `musicbox`                                   e  `celesta`
f  `bell` decay 2.2 on sparse notes, as it was (cut 22 dB down)   g  the same with `"clean": true` (no clicks)
h  the string swell as it was: `strings` (the synth pad)
i  the same chords on `strings_section`: violins, violas and celli sections with `"bow_env": "swell"`
j  section pizzicato (violins and celli, `"pizz": true`) on the waltz
k  `cello` alone: a legato phrase with a swell (`/swell`), a crescendo, then pizzicato
l  `viola` alone: the same phrase a fifth up
o  `vibraphone` on the theme with chords, pedal down, motor at 4.5 Hz (the motor's depth is hand-tuned, see MANUAL)
m  examples/chamberscore-test.json as it is (all the stand-ins)
n  the same project with the new instruments (celesta for the music box, glockenspiel for the bell, section
   pizzicato and celli for the pizz, strings_section for the pad)
spectrograms.png: each new instrument beside a reference recording at the same pitch (needs the references in
~/.cache/spectre/refs/chamber, see docs/MANUAL.md "Chamber score instruments"; skipped without them). The
references are only analysed, never shipped. Works in /tmp/spectre_chamber_ab; never touches a session.
"""
import copy
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.dirname(os.path.abspath(__file__))
TMP = "/tmp/spectre_chamber_ab"
STUDIO = os.path.join(REPO, "engine", "studio.py")
REFS = os.path.expanduser("~/.cache/spectre/refs/chamber")

GLOCK = "0:C6:4 4:A5:2 6:C6:2 8:F6:4 12:E6:8 20:C6:4 24:D6:4 28:F6:4 32:D6:4 36:Db6:8 44:C6:4"
THEME = "0:C5:4 4:A4:2 6:C5:2 8:F5:4 12:E5:8 20:C5:4 24:D5:4 28:F5:4 32:D5:4 36:Db5:8 44:C5:4"
SPARSE = "0:C6:8 16:A5:8 32:F6:8"
CHORDS = "F:12 Am:12 Bb:12 Bbm:12"
CELLO = ("0:F3:12/swell 12:E3:12/s 24:D3:10 34:C#3:2/s 36:Db3:12/cresc "
         "48:C3:4/pz 52:A3:4/pz 56:F3:4/pz 60:C3:4/pz 64:Bb2:4/pz 68:Bb3:4/pz 72:Db3:8/pz")


def waltz(tracks, patterns, bars=3, reps=2, bpm=168, reverb=0.7):
    arr = [{"name": f"s{i}", "bars": bars, "play": list(patterns)} for i in range(reps)]
    return {"title": "chamber A/B", "bpm": bpm, "swing": 0.5, "seed": 7, "tracks": tracks, "patterns": patterns,
            "arrangement": arr, "mix": {"reverb": {"size": reverb, "damping": 0.5, "return_db": -5, "lpf": 7000}},
            "master": {"lufs": -15, "sat": 0.0, "tape": 0.0, "glue": False}}


def lead(inst, notes, send=0.25, pan=0.0, gain=0):
    return waltz({"lead": {"inst": inst, "gain_db": gain, "humanize_ms": 5, "send_reverb": send, "pan": pan}},
                 {"p": {"bars": 3, "lead": notes}})


def strings_new(pizz=False):
    t = {"vln": {"inst": {"type": "strings_section", "section": "violins", "bow_env": "swell", "pizz": pizz},
                 "send_reverb": 0.35, "humanize_ms": 0},
         "vla": {"inst": {"type": "strings_section", "section": "violas", "bow_env": "swell", "pizz": pizz,
                          "seed": 8}, "send_reverb": 0.35, "humanize_ms": 0, "gain_db": -2},
         "vc": {"inst": {"type": "strings_section", "section": "celli", "bow_env": "swell", "pizz": pizz, "seed": 9},
                "send_reverb": 0.35, "humanize_ms": 0, "gain_db": -1}}
    if pizz:
        pat = {"bars": 3, "vln": "4:A4:2 8:C5:2 16:A4:2 20:C5:2 28:D5:2 32:F5:2 40:Db5:2 44:F5:2",
               "vc": "0:F2:4 12:A2:4 24:Bb2:4 36:Bb2:4"}
        t.pop("vla")
    else:
        pat = {"bars": 3, "vln": {"chords": CHORDS, "style": "sustain", "register": "C5", "voicing": "close",
                                  "vel": 0.7},
               "vla": {"chords": CHORDS, "style": "sustain", "register": "F4", "voicing": "root", "vel": 0.65},
               "vc": {"chords": CHORDS, "style": "sustain", "register": "F2", "voicing": "root", "vel": 0.7}}
    return waltz(t, {"p": pat})


def strings_old():
    return waltz({"str": {"inst": {"type": "strings", "attack": 0.8, "release": 1.2, "cutoff": 3000}, "gain_db": 2,
                          "send_reverb": 0.35, "width": 0.6, "fx": [{"type": "hpf", "hz": 90}]}},
                 {"p": {"bars": 3, "str": {"chords": CHORDS, "style": "sustain", "register": "F4",
                                           "voicing": "close", "vel": 0.6}}})


def mix_new():
    P = json.load(open(os.path.join(REPO, "examples", "chamberscore-test.json")))
    P = copy.deepcopy(P)
    P["tracks"]["glock"]["inst"] = {"type": "glockenspiel", "hardness": 0.45}
    P["tracks"]["glock"]["gain_db"] = -6
    P["tracks"]["musicbox"]["inst"] = {"type": "celesta"}
    P["tracks"]["pizz"]["inst"] = {"type": "strings_section", "section": "violins", "pizz": True}
    P["tracks"]["pizz"]["gain_db"] = 0
    P["tracks"]["strings"] = {"inst": {"type": "strings_section", "section": "violins", "bow_env": "swell"},
                              "send_reverb": 0.35, "humanize_ms": 0, "gain_db": -1}
    P["tracks"]["celli"] = {"inst": {"type": "strings_section", "section": "celli", "bow_env": "swell", "seed": 9},
                            "send_reverb": 0.3, "humanize_ms": 0, "gain_db": -3}
    P["patterns"]["waltzB"]["celli"] = {"chords": "F:12 Am:12 Bb:12 Bbm:12", "style": "sustain", "register": "F2",
                                        "voicing": "root", "vel": 0.6}
    P["patterns"]["waltzB"]["strings"]["voicing"] = "close"
    return P


JOBS = {
    "a-glock-old-bell": lead({"type": "bell", "decay": 1.3, "ratio": 2.76}, GLOCK, 0.3, 0.0, -2),
    "b-glockenspiel": lead({"type": "glockenspiel", "hardness": 0.5}, GLOCK, 0.3, 0.0, -4),
    "c-glockenspiel-hard": lead({"type": "glockenspiel", "hardness": 0.9}, GLOCK, 0.3, 0.0, -6),
    "d-celesta-old-musicbox": lead({"type": "musicbox"}, THEME, 0.3),
    "e-celesta": lead({"type": "celesta"}, THEME, 0.3),
    "f-bell-old-click": lead({"type": "bell", "decay": 2.2}, SPARSE, 0.0),
    "g-bell-clean": lead({"type": "bell", "decay": 2.2, "clean": True}, SPARSE, 0.0),
    "h-strings-old-pad": strings_old(),
    "i-strings-section": strings_new(),
    "j-pizzicato-section": strings_new(pizz=True),
    "k-cello": waltz({"vc": {"inst": {"type": "cello"}, "send_reverb": 0.25, "humanize_ms": 3}},
                     {"p": {"bars": 6, "vc": CELLO}}, bars=6, reps=1, bpm=120),
    "l-viola": waltz({"va": {"inst": {"type": "viola", "transpose": 7}, "send_reverb": 0.25, "humanize_ms": 3}},
                     {"p": {"bars": 6, "va": CELLO}}, bars=6, reps=1, bpm=120),
    "o-vibraphone": waltz({"vib": {"inst": {"type": "vibraphone", "pedal": True, "motor": 4.5}, "send_reverb": 0.25,
                               "humanize_ms": 5},
                       "vibc": {"inst": {"type": "vibraphone", "pedal": True, "motor": 4.5, "hardness": 0.25},
                                "send_reverb": 0.25, "gain_db": -6, "humanize_ms": 6}},
                      {"p": {"bars": 3, "vib": THEME, "vibc": {"chords": CHORDS, "style": "sustain", "register": "A3",
                                                               "voicing": "close", "vel": 0.5}}}),
    "m-mix-old": json.load(open(os.path.join(REPO, "examples", "chamberscore-test.json"))),
    "n-mix-new": mix_new(),
}


def render(name, P):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    json.dump(P, open(os.path.join(d, "project.json"), "w"), indent=1)
    env = dict(os.environ, BEAT_DIR=d)
    subprocess.run([sys.executable, STUDIO, "render"], cwd=d, env=env, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-i", os.path.join(d, "renders", "v001.wav"), "-b:a", "128k",
                    os.path.join(OUT, name + ".mp3")], check=True)
    print("wrote", name + ".mp3")


def spectrograms():
    """Each new instrument beside a reference recording at the same pitch (2.5 s, mel spectrogram)."""
    if not os.path.isdir(REFS):
        print("no references in", REFS, "- spectrograms skipped")
        return
    import numpy as np
    sys.path.insert(0, os.path.join(REPO, "engine"))
    import librosa
    import librosa.display
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import chamber as C
    SR = 44100

    def load(p):
        raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).astype(np.float64)
        e = np.convolve(x ** 2, np.ones(64) / 64, "same")
        i = int(np.argmax(e > e.max() * 1e-3))
        return x[max(0, i - 2000):]

    def note(kind, f, dur=2.0, art=None, p=None):
        p = dict(p or {})
        nt = [dict(t0=2000, n=int(dur * SR), f=f, vel=0.9, glide=False, art=art or [])]
        if kind in ("cello", "viola"):
            y = C.string_body(kind, p, C.string_line(kind, dict(p, vibrato=0.0), nt, int((dur + 1.5) * SR)))
        elif kind == "strings_section":
            y = C.strings_section(p, nt, int((dur + 1.5) * SR)).mean(0)
        else:
            y = np.concatenate([np.zeros(2000), getattr(C, kind)(p, f, 0.9, dur)])
        return np.asarray(y, dtype=np.float64)

    pairs = [("celesta F4", "celesta/pjcohen/Celesta_F4.mp3", note("celesta", 349.4, 3.0, p={"pedal": True})),
             ("glockenspiel C6, plastic mallet / hardness 0.5", "glockenspiel/iowa/bells.plastic.ff.C6.stereo.aif",
              note("glockenspiel", 1055.0, 3.0, p={"hardness": 0.5})),
             ("glockenspiel G6, brass mallet / hardness 1", "glockenspiel/iowa/bells.brass.ff.G6.stereo.aif",
              note("glockenspiel", 1581.3, 3.0, p={"hardness": 1.0})),
             ("cello A3 arco (Iowa: no vibrato)", "cello/iowa/Cello.arco.ff.sulD.A3.stereo.aif", note("cello", 220.0)),
             ("cello D3 pizzicato", "cello/iowa/Cello.pizz.ff.sulG.D3.stereo.aif", note("cello", 146.8, 1.0, ["pz"])),
             ("viola D4 arco (Iowa: no vibrato)", "viola/iowa/Viola.arco.ff.sulG.D4.stereo.aif", note("viola", 293.7)),
             ("violin section C5 (VSCO-2-CE)", "section/vsco-2-ce/VlnEns_susVib_C4_v2.wav",
              note("strings_section", 524.2, 2.0, p={"section": "violins"})),
             ("vibraphone C5, motor off (Iowa sustain)", "vibraphone/iowa/Vibraphone.sustain.ff.C5.stereo.aif",
              np.concatenate([np.zeros(2000), C.vibraphone({"pedal": True}, [dict(t0=0, n=3 * SR, f=526.4, vel=0.9)],
                                                           4 * SR)]).astype(np.float64)),
             ("cello section C4 (VSCO-2-CE)", "section/vsco-2-ce/susvib_C3_v3_1.wav",
              note("strings_section", 261.8, 2.0, p={"section": "celli"}))]
    fig, axs = plt.subplots(len(pairs), 2, figsize=(12, 2.4 * len(pairs)))
    for row, (title, ref, y) in zip(axs, pairs):
        for ax, (lab, x) in zip(row, (("reference", load(os.path.join(REFS, ref))), ("Spectre", y))):
            x = x[:int(2.5 * SR)]
            M = librosa.feature.melspectrogram(y=x, sr=SR, n_fft=2048, hop_length=256, n_mels=128, fmax=16000)
            librosa.display.specshow(librosa.power_to_db(M + 1e-12, ref=np.max), sr=SR, hop_length=256,
                                     y_axis="mel", x_axis="time", fmax=16000, ax=ax, cmap="magma", vmin=-80, vmax=0)
            ax.set_title(f"{title}: {lab}", fontsize=8)
            ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "spectrograms.png"), dpi=55)
    print("wrote spectrograms.png")


if __name__ == "__main__":
    names = sys.argv[1:] or list(JOBS) + ["spectrograms"]
    for nm in names:
        if nm == "spectrograms":
            spectrograms()
        else:
            render(nm, JOBS[nm])
    shutil.rmtree(TMP, ignore_errors=True)
