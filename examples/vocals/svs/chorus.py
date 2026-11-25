"""The c1 chorus shared by the svs studies (build.py chorus, blend.py): session 009's pre-chorus and chorus1 on a /tmp
copy of the session, with the hook (pattern hookD, track voxD) sung by a `singer` lead in place of the `vox` line.
Never touches the session folder."""
import copy
import json
import os
import shutil
import subprocess

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SR = 44100

HOOK_LYRICS = ("here you are, round and round / hold on tight, round we go / "
               "here you are, round and round / and you stay on the ride").replace("/", " ")
VOCAL_DB = float(os.environ.get("VOCAL_DB", 13))  # post-compressor level of the sung lead
SING_TRACK = {"inst": {"type": "singer", "source": "svs", "voice": "hanami", "double": 0.35, "seed": 3},
              "humanize_ms": 0, "gain_db": 12, "send_reverb": 0.22, "send_delay": 0.12,
              "fx": [{"type": "hpf", "hz": 150}, {"type": "eq", "hz": 500, "gain_db": 3, "q": 0.8},
                     {"type": "eq", "hz": 3000, "gain_db": -3, "q": 0.9},
                     {"type": "comp", "threshold_db": -22, "ratio": 3}, {"type": "gain", "db": VOCAL_DB}]}


def session_copy(d):
    """A fresh copy of session 009 (without renders, audio or images) in d."""
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(REPO, "sessions", "009-carousel"), d,
                    ignore=shutil.ignore_patterns("renders", "*.mp3", "*.png"))
    return d


def hook_chorus(pj, tr):
    """Put the sung lead `tr` on the hook and cut the arrangement to pre1 + chorus1 + a two-bar tail."""
    pj["tracks"]["sing"] = tr
    pj["patterns"]["hookSing"] = {"bars": 8, "sing": {"notes": pj["patterns"]["hookD"]["voxD"], "lyrics": HOOK_LYRICS}}
    sec = copy.deepcopy(next(s for s in pj["arrangement"] if s["name"] == "chorus1"))
    pre = next(s for s in pj["arrangement"] if s["name"] == "pre1")
    sec["play"] = [x for x in sec["play"] if x != "hook"] + ["hookSing"]  # the sung hook replaces the vox lead
    pj["arrangement"] = [copy.deepcopy(pre), sec, {"name": "tail", "bars": 2, "play": []}]
    return pj


def write_chorus(d, tr):
    """session_copy + hook_chorus, written to d/project.json."""
    session_copy(d)
    pj = hook_chorus(json.load(open(os.path.join(d, "project.json"))), tr)
    json.dump(pj, open(os.path.join(d, "project.json"), "w"), indent=1)
    return d


def mp3(y, name, out, tmp, kbps=128, normalize=True):
    """Write y (mono, or (2, n)) as out/<name>.mp3 through a WAV in tmp; normalize = -1 dBFS peak."""
    os.makedirs(tmp, exist_ok=True)
    y = np.asarray(y, dtype=np.float64)
    if normalize:
        y = y / max(np.abs(y).max(), 1e-9) * 0.89
    wav = os.path.join(tmp, name + ".wav")
    sf.write(wav, y.T if y.ndim == 2 else y, SR)
    dst = os.path.join(out, name + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", f"{kbps}k", dst + ".tmp.mp3"], check=True)
    os.replace(dst + ".tmp.mp3", dst)
    print(dst, os.path.getsize(dst) // 1024, "KB")
