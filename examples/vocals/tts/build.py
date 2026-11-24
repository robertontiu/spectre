"""Builds the `singer` source "tts" A/B in this folder (run from anywhere: python3 examples/vocals/tts/build.py [a b c d]).

a   the TTS word sampler speaking the line neutrally
b   the same line on a simple mid-register melody, dry, with the first (tuned) settings
b1  the same, dry, with the sung (natural) defaults, phrase mode
b2  per-word vs per-phrase speaking, same line, natural tuning, dry (word mode first, then phrase mode)
c1/c2/c3  the "Here You Are" pre-chorus and chorus (session 009) with the hook sung an octave below the original as a
    lead, mastered (`master --genre rock`): natural, medium and the first tuned settings, all in phrase mode, same
    voice, level and effects
d   a hard-tuned trance variant of the line over a short 138 bpm loop
Works on /tmp copies; never touches the session. Needs ffmpeg and the setup in AGENTS.md.
"""
import copy
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "engine"))
import singer  # noqa: E402
import tts_words  # noqa: E402

SR = 44100
TMP = "/tmp/spectre_tts_ab"
LINE = "here you are, round and round"


def mp3(y, name, kbps=128, normalize=True):
    os.makedirs(TMP, exist_ok=True)
    y = np.asarray(y, dtype=np.float64)
    if normalize:
        y = y / max(np.abs(y).max(), 1e-9) * 0.89  # -1 dBFS peak
    wav = os.path.join(TMP, name + ".wav")
    sf.write(wav, y.T if y.ndim == 2 else y, SR)
    dst = os.path.join(OUT, name + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", f"{kbps}k", dst + ".tmp.mp3"], check=True)
    os.replace(dst + ".tmp.mp3", dst)
    print(dst, os.path.getsize(dst) // 1024, "KB")


def studio(args, d):
    """Run the engine in d, after waiting for any other studio.py job to finish (renders must not overlap)."""
    import time
    while subprocess.run(["pgrep", "-f", "engine/studio.py"], capture_output=True).stdout.strip():
        time.sleep(5)
    subprocess.run([sys.executable, os.path.join(REPO, "engine", "studio.py")] + args, cwd=d,
                   env=dict(os.environ, BEAT_DIR=d), check=True)


def notes_at(bpm, spec):
    """'F#4:4 A4:4 ...' (lengths in 16ths, played back to back, '-' rests) -> singer notes."""
    from hand import note_to_midi
    q = 60.0 / bpm / 4
    t, out = 0.5, []
    for tok in spec.split():
        n, ln = tok.split(":")
        if n != "-":
            out.append(dict(t0=int(t * SR), n=int(float(ln) * q * SR * 0.95), f=440 * 2 ** ((note_to_midi(n) - 69) / 12),
                            vel=0.9, glide=False))
        t += float(ln) * q
    return out, int((t + 1.0) * SR)


def a():
    x = tts_words.spoken(LINE, tts_words.VOICES["female"], 0.9)
    mp3(np.concatenate([np.zeros(SR // 4), x, np.zeros(SR // 2)]), "a-tts-speaks")


B_MELODY = "F#4:4 A4:4 B4:8 A4:4 F#4:2 A4:10"


def b():
    notes, n = notes_at(100, B_MELODY)
    y = singer.sing(dict(singer.TTS_TUNED, source="tts", voice="female", lyrics=LINE, inhale=0, tts_mode="word"),
                    notes, n)
    mp3(y, "b-tts-autotuned-dry")


def b1():
    notes, n = notes_at(100, B_MELODY)
    mp3(singer.sing({"source": "tts", "voice": "female", "lyrics": LINE, "inhale": 0}, notes, n), "b1-natural-dry")


def b2():
    notes, n = notes_at(100, B_MELODY)
    yw = singer.sing({"source": "tts", "voice": "female", "lyrics": LINE, "inhale": 0, "tts_mode": "word"}, notes, n)
    yp = singer.sing({"source": "tts", "voice": "female", "lyrics": LINE, "inhale": 0, "tts_mode": "phrase"}, notes, n)
    mp3(np.concatenate([yw, np.zeros(int(0.5 * SR), dtype=yw.dtype), yp]), "b2-word-vs-phrase")


def _session_copy():
    d = os.path.join(TMP, "carousel")
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(REPO, "sessions", "009-carousel"), d, ignore=shutil.ignore_patterns("renders", "*.mp3",
                                                                                                       "*.png"))
    return d


VOCAL_DB = float(os.environ.get("VOCAL_DB", 13))  # post-compressor level of the sung lead in (c)
SING_TRACK = {"inst": {"type": "singer", "source": "tts", "voice": "female", "breath": 0.15, "double": 0.35,
                       "seed": 3},
              "humanize_ms": 0, "gain_db": 12, "send_reverb": 0.22, "send_delay": 0.12,
              "fx": [{"type": "hpf", "hz": 150}, {"type": "eq", "hz": 500, "gain_db": 3, "q": 0.8},
                     {"type": "eq", "hz": 3000, "gain_db": -3, "q": 0.9},
                     {"type": "comp", "threshold_db": -22, "ratio": 3}, {"type": "gain", "db": VOCAL_DB}]}
HOOK_LYRICS = ("here you are, round and round / hold on tight, round we go / "
               "here you are, round and round / and you stay on the ride").replace("/", " ")


VARIANTS = {  # pitch and phrasing only: the voice, effects and level are the same in all three
    "c1-natural": {},  # the `tts` defaults: tune 0.3, retune 120 ms, ~90 ms glides, late varied vibrato, drift
    "c2-medium": {"tune": 0.5, "retune_ms": 90, "portamento_ms": 70, "scoop_some": 0.2, "vib_late": 0.3},
    "c3-current": dict(singer.TTS_TUNED, tune=0.75),  # the first settings (the version that read as autotuned)
}


def c(gain_db=None, variant="c1-natural"):
    d = _session_copy()
    pj = json.load(open(os.path.join(d, "project.json")))
    tr = copy.deepcopy(SING_TRACK)
    if gain_db is not None:
        tr["gain_db"] = gain_db
    tr["inst"].update(VARIANTS[variant])
    pj["tracks"]["sing"] = tr
    pj["patterns"]["hookSing"] = {"bars": 8, "sing": {"notes": pj["patterns"]["hookD"]["voxD"], "lyrics": HOOK_LYRICS}}
    sec = next(s for s in pj["arrangement"] if s["name"] == "chorus1")
    pre = next(s for s in pj["arrangement"] if s["name"] == "pre1")
    sec = copy.deepcopy(sec)
    sec["play"] = [x for x in sec["play"] if x != "hook"] + ["hookSing"]  # the sung hook replaces the vox lead
    pj["arrangement"] = [copy.deepcopy(pre), sec, {"name": "tail", "bars": 2, "play": []}]
    json.dump(pj, open(os.path.join(d, "project.json"), "w"), indent=1)
    studio(["render"], d)
    return d


def d_():
    d = os.path.join(TMP, "trance")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    pj = {"title": "tts trance test", "bpm": 138, "swing": 0.5, "seed": 2,
          "tracks": {
              "kick": {"inst": {"type": "clubkick"}, "humanize_ms": 0},
              "clap": {"inst": {"type": "handclap", "clappers": 5}, "gain_db": -9, "send_reverb": 0.2,
                       "fx": [{"type": "hpf", "hz": 250}]},
              "hat": {"inst": {"type": "hat", "decay": 0.04}, "gain_db": -3, "humanize_ms": 0},
              "bass": {"inst": {"type": "trancebass"}, "humanize_ms": 0, "gain_db": -2,
                       "sidechain": {"source": "kick", "depth": 0.85, "release_ms": 95}},
              "pad": {"inst": {"type": "supersaw", "attack": 0.4, "release": 1.2, "cutoff": 2600}, "gain_db": -6,
                      "sidechain": {"source": "kick", "depth": 0.6, "release_ms": 160}, "fx": [{"type": "hpf", "hz": 250}]},
              "sing": {"inst": dict(singer.TTS_TUNED, type="singer", source="tts", voice="female", tune=1.0,
                                    retune_ms=6, vibrato=0.0, double=0.7, formant=0.5, seed=5, tts_mode="word"),
                       "gain_db": 2, "humanize_ms": 0, "send_reverb": 0.35, "send_delay": 0.25,
                       "sidechain": {"source": "kick", "depth": 0.25, "release_ms": 120},
                       "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 3200, "gain_db": 3, "q": 0.8},
                              {"type": "comp", "threshold_db": -22, "ratio": 4}, {"type": "gain", "db": 10}]}},
          "patterns": {
              "beat": {"bars": 1, "kick": "x...x...x...x...", "clap": "....x.......x...", "hat": "..x...x...x...x."},
              "music": {"bars": 4, "bass": {"chords": "F#m:16 D:16 A:16 E:16", "style": "stabs",
                                            "rhythm": "..x...x...x...x.", "stab_len": 2, "voicing": "root",
                                            "register": "F#2"},
                        "pad": {"chords": "F#m:16 D:16 A:16 E:16", "style": "sustain", "register": "F#4"}},
              "vocal": {"bars": 4, "sing": {"notes": "0:F#4:2 2:A4:2 4:B4:6 12:A4:2 14:F#4:2 16:A4:10 32:F#4:2 "
                                                     "34:A4:2 36:B4:6 44:C#5:2 46:B4:2 48:A4:12",
                                            "lyrics": LINE + " " + LINE}}},
          "arrangement": [{"name": "loop1", "bars": 4, "play": ["beat", "music", "vocal"]},
                          {"name": "loop2", "bars": 4, "play": ["beat", "music", "vocal"]}],
          "mix": {"reverb": {"size": 0.8, "damping": 0.5, "return_db": -5, "lpf": 7000},
                  "delay": {"beats": 0.75, "feedback": 0.35, "return_db": -8, "lpf": 4000}},
          "master": {"lufs": -10, "sat": 0.1, "glue": True}}
    json.dump(pj, open(os.path.join(d, "project.json"), "w"), indent=1)
    studio(["render"], d)
    y, _ = sf.read(os.path.join(d, "renders", "v001.wav"))
    mp3(y.T, "d-tts-hardtuned-trance-138", kbps=112)


if __name__ == "__main__":
    which = sys.argv[1:] or ["a", "b", "b1", "b2", "c1-natural", "c2-medium", "c3-current", "d"]
    for w in which:
        if w in VARIANTS:
            d = c(variant=w)
            studio(["master", "v001", "--genre", "rock"], d)  # the release master, pop rock target
            y, _ = sf.read(os.path.join(d, "renders", "v001.master.wav"))
            keep = os.path.join(TMP, w)
            shutil.rmtree(keep, ignore_errors=True)
            shutil.copytree(d, keep)  # kept for measurement
            mp3(y.T, w, kbps=88, normalize=False)
        else:
            {"a": a, "b": b, "b1": b1, "b2": b2, "d": d_}[w]()
