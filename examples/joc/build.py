"""Builds the lăutar-band A/B in this folder (python3 examples/joc/build.py [names...]). What each file is:

a  the old `fiddle` playing a joc phrase (G minor, 2/4 at quarter = 110), dry-ish
b  the new `violin` (bowed waveguide + body) playing the same phrase and articulations
c  the same with `"cold": 1` (less vibrato, drier, a clearer upper body: one reading of "vioară rece")
d  the violin's articulations one after another at quarter = 80: grace, mordent, trill, false lăutar trill,
   slide-in, fall, turn, double stop, flageolet, pizzicato, spiccato, portamento, bowed tremolo, a long vibrato
e  the phrase of b at quarter = 50 (the reference score's first practice tempo)
f  the band at quarter = 110: violin, `acguitar` (nylon) afterbeat chops (țiitură), `ebass` on the beats, `toba`
   (bass drum and cinel), `kitsnare` afterbeats, `handclap`
g  f with the old `cleanguitar` in place of `acguitar`
h  f with a tempo ramp (section "bpm": [100, 140]): the accelerando of a joc's last round
i  the percussion alone (toba boom / cinel, snare afterbeats, claps)
spectrograms.png: b, f, the guitar alone and the percussion alone.
Works in /tmp/spectre_joc_ab; never touches a session. Needs ffmpeg.
"""
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.dirname(os.path.abspath(__file__))
TMP = "/tmp/spectre_joc_ab"
STUDIO = os.path.join(REPO, "engine", "studio.py")

# An original phrase in the idiom (G minor with the raised 4th C#, grace notes from a semitone below, mordents,
# sixteenth runs slurred in fours, a pedal double stop, a trill, a terminal fall). 8 engine bars = 16 bars of 2/4.
VLN = ("0:D5:1 1:C#5:1/s 2:D5:1/s 3:Eb5:1/s 4:D5:2 6:Bb4:2 8:G4:2/g-1 10:A4:2 12:Bb4:1 13:C#5:1/s 14:D5:2/m+1 "
       "16:F#5:3/g-1 19:Eb5:1/s 20:D5:2 22:C5:1 23:A4:1/s 24:F#4:2/sl-2 26:A4:2 28:D5:4/fall-3 "
       "32:G5:2/acc 34:F#5:1 35:Eb5:1/s 36:D5:2 38:C#5:1/g-1 39:D5:1/s 40:Bb4:2 42:G4:2 44:D4:4/d=A4 "
       "48:Eb5:2/g-1 50:D5:1 51:C5:1/s 52:Bb4:2 54:A4:2 56:G4:1 57:A4:1/s 58:Bb4:1/s 59:C#5:1/s 60:D5:4/tr+1 "
       "64:D5:6/ftr+1 70:Bb4:1 71:C#5:1/s 72:D5:2 74:G5:2/acc 76:F#5:4/vib "
       "80:Ab5:2/g-1 82:G5:1 83:F5:1/s 84:Eb5:2 86:D5:2 88:C#5:1 89:D5:1/s 90:Eb5:1/s 91:F#5:1/s 92:G5:4/m+2 "
       "96:Eb5:1 97:D5:1/s 98:C5:1/s 99:Bb4:1/s 100:A4:2/turn 102:G4:2 104:Bb4:2/g-1 106:D5:2 108:G5:4/h "
       "112:F#5:2/g-1 114:Eb5:2 116:D5:2 118:C#5:2 120:D5:8/vib")
CHORDS = "Gm:16 D7:16 Gm:16 Cm:8 D7:8 Gm:16 Ab:8 D7:8 Cm:8 Gm:8 D7:16"
BASS = ("0:G2:2 4:D2:2 8:G2:2 12:D2:2 16:D2:2 20:A2:2 24:D2:2 28:F#2:2 32:G2:2 36:D2:2 40:G2:2 44:Bb2:2 "
        "48:C3:2 52:G2:2 56:D2:2 60:A2:2 64:G2:2 68:D2:2 72:G2:2 76:D2:2 80:Ab2:2 84:Eb2:2 88:D2:2 92:A2:2 "
        "96:C3:2 100:G2:2 104:G2:2 108:D2:2 112:D2:2 116:A2:2 120:D2:2 124:F#2:2")
ORN = ("0:D5:6/g-1 8:D5:6/m+1 16:D5:6/tr+1 24:D5:6/ftr+1 32:D5:6/sl-3 40:D5:6/fall-4 48:D5:6/turn "
       "56:Bb4:6/d=D4 64:G5:6/h 72:D5:2/pz 74:Bb4:2/pz 76:G4:2/pz 80:D5:1/sp 81:C#5:1/sp 82:D5:1/sp 83:Eb5:1/sp "
       "84:D5:2/sp 88:G4:2 90:D5:6~ 96:D5:8/trem 104:G4:16/vib")


def project(bpm, sections, vln_inst=None, gtr_inst=None, parts=("band", "kit")):
    gtr = {"chords": CHORDS, "style": "stabs", "rhythm": "..x...x...x...x.", "stab_len": 1, "register": "G3",
           "voicing": "guitar", "strum": "down", "strum_ms": 9, "vel": 0.75}
    return {
        "title": "joc A/B", "bpm": bpm, "swing": 0.5, "seed": 5,
        "tracks": {
            "vln": {"inst": vln_inst or {"type": "violin"}, "gain_db": 2, "humanize_ms": 4, "vel_jitter": 0.05,
                    "legato": 0.97, "send_reverb": 0.14, "pan": 0.05},
            "gtr": {"inst": gtr_inst or {"type": "acguitar", "chop": 0.8, "scrape": 0.4}, "humanize_ms": 5,
                    "vel_jitter": 0.08, "pan": -0.3, "send_reverb": 0.08, "fx": [{"type": "hpf", "hz": 110}]},
            "bass": {"inst": {"type": "ebass", "pick": 0.2, "drive": 0.15, "tone": 2500}, "gain_db": -1,
                     "humanize_ms": 3, "legato": 0.6},
            "toba": {"inst": {"type": "toba", "stroke": "boom", "tune": 62}, "gain_db": -3, "humanize_ms": 4,
                     "fx": [{"type": "room", "size": 0.4, "mix": 0.15}]},
            "tobacin": {"inst": {"type": "toba", "stroke": "cinel", "cinel_decay": 0.18, "bright": 0.4},
                        "gain_db": -16, "humanize_ms": 4, "pan": 0.25,
                        "fx": [{"type": "hpf", "hz": 400}, {"type": "lpf", "hz": 9000}]},
            "snare": {"inst": {"type": "kitsnare", "tune": 230, "wires": 0.5, "decay": 0.12}, "gain_db": -10,
                      "humanize_ms": 5, "pan": -0.1,
                      "fx": [{"type": "room", "size": 0.35, "mix": 0.2}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
            "clap": {"inst": {"type": "handclap", "clappers": 5}, "gain_db": -14, "humanize_ms": 6, "width": 0.4,
                     "send_reverb": 0.2, "fx": [{"type": "hpf", "hz": 250}]}},
        "patterns": {
            "band": {"bars": 8, "vln": VLN, "gtr": gtr, "bass": BASS},
            "solo": {"bars": 8, "vln": VLN},
            "orn": {"bars": 8, "vln": ORN},
            "kit": {"bars": 1, "toba": "X...x...X...x...", "tobacin": "X.......X.......",
                    "snare": "..x...x...x.o.x.", "clap": "......x.......x."}},
        "arrangement": sections,
        "mix": {"reverb": {"size": 0.55, "damping": 0.6, "return_db": -8, "lpf": 7000}},
        "master": {"lufs": -14, "sat": 0.05, "glue": True}}


ITEMS = {
    "a-fiddle-old": project(110, [{"name": "a", "bars": 8, "play": ["solo"]}], {"type": "fiddle", "grit": 0.15}),
    "b-violin-new": project(110, [{"name": "a", "bars": 8, "play": ["solo"]}]),
    "c-violin-cold": project(110, [{"name": "a", "bars": 8, "play": ["solo"]}], {"type": "violin", "cold": 1.0}),
    "d-violin-articulations": project(80, [{"name": "a", "bars": 8, "play": ["orn"]}]),
    "e-violin-quarter50": project(50, [{"name": "a", "bars": 4, "play": ["solo"]}]),
    "f-band-quarter110": project(110, [{"name": "a", "bars": 8, "play": ["band", "kit"]}]),
    "g-band-old-cleanguitar": project(110, [{"name": "a", "bars": 8, "play": ["band", "kit"]}], None,
                                      {"type": "cleanguitar", "chorus": 0.3, "mute": 0.6}),
    "h-band-accelerando-100-140": project(100, [{"name": "a", "bars": 8, "play": ["band", "kit"], "bpm": [100, 140]}]),
    "i-percussion": project(110, [{"name": "a", "bars": 4, "play": ["kit"]}]),
}


def render(name, P, solo=None):
    d = os.path.join(TMP, name)
    if solo is None:
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    json.dump(P, open(os.path.join(d, "project.json"), "w"), indent=1)
    env = dict(os.environ, BEAT_DIR=d)
    cmd = [sys.executable, STUDIO, "render"] + (["--solo", solo] if solo else [])
    subprocess.run(cmd, cwd=d, env=env, check=True, capture_output=True)
    return os.path.join(d, "renders", f"solo_{solo}.wav" if solo else "v001.wav")


def mp3(wav, name):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", os.path.join(OUT, name + ".mp3")],
                   check=True)


def spectrograms(paths, out):
    import numpy as np
    import soundfile as sf
    import librosa
    import librosa.display
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(len(paths), 1, figsize=(14, 3.3 * len(paths)))
    for ax, (label, p) in zip(axs, paths):
        y, sr = sf.read(p)
        y = y.mean(1) if y.ndim > 1 else y
        S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=4096, hop_length=256)), ref=np.max)
        librosa.display.specshow(S, sr=sr, hop_length=256, x_axis="time", y_axis="log", ax=ax, cmap="magma", vmin=-80)
        ax.set_ylim(60, 16000)
        ax.set_title(label, fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=55)


def main():
    names = sys.argv[1:] or list(ITEMS)
    wavs = {}
    for name in names:
        wavs[name] = render(name, ITEMS[name])
        mp3(wavs[name], name)
        print("built", name)
    if set(ITEMS) <= set(wavs):
        gtr = render("f-band-quarter110", ITEMS["f-band-quarter110"], solo="gtr")
        spectrograms([("b: violin (new), phrase at quarter = 110", wavs["b-violin-new"]),
                      ("a: fiddle (old), same phrase", wavs["a-fiddle-old"]),
                      ("f: the band (violin, acguitar chops, ebass, toba, snare, claps)", wavs["f-band-quarter110"]),
                      ("acguitar alone: nylon afterbeat chops (țiitură)", gtr),
                      ("i: percussion alone (toba boom on the beats, cinel on 1, snare afterbeats, claps)",
                       wavs["i-percussion"])], os.path.join(OUT, "spectrograms.png"))
        print("built spectrograms.png")


if __name__ == "__main__":
    main()
