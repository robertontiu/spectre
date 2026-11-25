#!/usr/bin/env python3
"""A/B of the production upgrade (queue item 9b, sound side): a published trance excerpt against the same notes
rebuilt with stacks, the new synth voice and the low/top-end sources.

    python3 examples/production/build.py                 # both examples
    python3 examples/production/build.py first-light     # one

For each case: the section is rendered twice in memory (a window render with two bars of pre-roll, as `listen
--clarity` does): A = the session's project.json as published, B = the same project with the kick, bass and lead
replaced by stacks (same patterns, same arrangement; the published octave double of the lead becomes the stack's
support layer). Each B stack is level-matched to the A tracks it replaces (A-weighted energy over the excerpt), so
the comparison is of sound, not of level (the kick by its peak, as kicks are set in a mix; bass and lead by
A-weighted energy; the match is a gain at the end of each stack's bus chain). Both excerpts then go through the same quick master (the engine's: high-pass
25 Hz, 2:1 glue, -10 LUFS, -1 dBFS limiter; no tonal EQ, so the master does not hide the difference) and become
`<case>-A-published.mp3` and `<case>-B-stacks.mp3`. The clarity analysis (engine/clarity.py) of both excerpts goes to
`<case>.json`, a picture (mel spectrograms and the 1/3-octave balance against the genre's era target) to
`<case>.png`. Nothing in the sessions is changed. Uses the session's own seeds mode (shared), so the tracks that were
not rebuilt keep their notes and sound but not their random phases (inaudible: free-running oscillators).
"""
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.environ.get("SPECTRE_ENGINE", os.path.join(REPO, "engine")))
import clarity as CL  # noqa: E402
import master as MA  # noqa: E402
import studio as ST  # noqa: E402
from hand import Hand  # noqa: E402

SR = ST.SR
GENRE, TARGET = "trance", "trance_2015"


# ------------------------------------------------------------------ the rebuilds (same notes, new sound)

def kick_stack(note, fx_bus=None, sub_gain=-2):
    """Sub/body tuned to the key, a short punch, a click; the bus soft-clips (trance: clip the kick or drum bus in
    the mix so the master does not have to, docs/TRANCE.md 'Mastering')."""
    return {"role": "kick", "humanize_ms": 0, "vel_jitter": 0.02,
            "fx": fx_bus or [{"type": "clip", "drive_db": 2, "ceiling_db": -1.5, "knee": 0.4}],
            "layers": [
                {"name": "sub", "inst": {"type": "kicksub", "note": note, "punch": 14, "hold": 0.03, "tail": 0.09,
                                         "drive": 0.3},
                 "role": "kick", "eq": {"own_db": 0, "cut_db": 0}, "gain_db": sub_gain},
                {"name": "punch", "inst": {"type": "kickpunch", "tune": 115, "decay": 0.05}, "role": "kick",
                 "eq": {"hp": 80, "own_db": 0}, "gain_db": 1},
                {"name": "click", "inst": {"type": "kickclick", "tone": 3200}, "role": "kick",
                 "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}}]}


def bass_stack(sidechain, sub_gain=0):
    """Sub (a clean sine, the only thing under ~120 Hz besides the kick), the rolling bass high-passed with its body
    at 150-250 Hz and bite at 0.7-2 kHz, an upper bass an octave up speaking at 0.8-3 kHz (docs/TRANCE.md B)."""
    return {"role": "bass", "humanize_ms": 0, "vel_jitter": 0.03, "sidechain": sidechain,
            "fx": [{"type": "comp", "threshold_db": -20, "ratio": 2, "attack_ms": 10, "release_ms": 80},
                   {"type": "sat", "amount": 0.15}],
            "layers": [
                {"name": "sub", "inst": {"type": "sub", "attack": 0.004, "release": 0.04, "harmonics": 0.2}, "role": "sub",
                 "gain_db": sub_gain},
                {"name": "roll", "inst": {"type": "trancebass", "sub": 0, "cutoff": 700, "env": 2600, "fdecay": 0.06,
                                          "drive": 0.35, "reso": 0.2}, "role": "bass", "gain_db": 3,
                 "eq": {"hp": 90, "own_db": 3}},
                {"name": "upper", "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 10},
                                                                         {"shape": "pulse", "pw": 0.3, "level": 0.5}],
                                           "cutoff": 1400, "env": 3500, "fdecay": 0.05, "decay": 0.1,
                                           "sustain_level": 0.25, "release": 0.04},
                 "role": "upper-bass", "octave": 1, "gain_db": 8}]}


def lead_stack(src, sends):
    """Main supersaw (Szabo's model 2: tracking high-pass, mix curve, drift, a delayed vibrato), supporting saws an
    octave up (slower attack, longer release, wide), an air layer, a narrow centre; the bus glues them (OTT at partial
    depth, 2:1). The main layer keeps the published lead's filter shape."""
    i = src["inst"]
    main = {"type": "supersaw", "model": 2, "voices": i.get("voices", 7), "detune": i.get("detune", 22),
            "mix": i.get("mix", 0.65), "spread": i.get("spread", 0.85), "attack": i.get("attack", 0.005),
            "release": i.get("release", 0.3), "cutoff": i.get("cutoff", 5000) * 1.3, "env": i.get("env", 2000),
            "fdecay": i.get("fdecay", 0.2), "reso": i.get("reso", 0.0), "drift": 0.35, "vibrato": 10,
            "vib_delay": 0.3}
    return dict({"role": "lead", "humanize_ms": 0, "legato": src.get("legato", 0.95), "sidechain": src.get("sidechain"),
                 "fx": [{"type": "ott", "depth": 0.3},
                        {"type": "comp", "threshold_db": -18, "ratio": 2, "attack_ms": 15, "release_ms": 150},
                        {"type": "chorus", "rate": 0.3, "depth": 0.2, "mix": 0.15}],
                 "layers": [
                     {"name": "main", "inst": main, "role": "lead"},
                     {"name": "support", "inst": dict(main, voices=7, detune=30, attack=0.03, release=0.55,
                                                       spread=1.0, drift=0.5, vibrato=0),
                      "octave": 1, "role": "support", "gain_db": -7, "width": 0.5},
                     {"name": "air", "inst": {"type": "air", "octave": 1, "noise": 0.45, "attack": 0.02,
                                              "release": 0.4}, "role": "air", "gain_db": 6},
                     {"name": "centre", "inst": {"type": "polysynth", "osc": [{"shape": "square"}],
                                                 "cutoff": 2200, "attack": 0.005, "release": 0.2},
                      "role": "lead", "eq": "none", "gain_db": -10, "fx": [{"type": "hpf", "hz": 200, "slope": 12}]}]},
                **sends)


def first_light(P):
    B = copy.deepcopy(P)
    B["genre"] = GENRE
    T = B["tracks"]
    lead = T["lead"]
    T["kick"] = kick_stack("Ab1")                    # the track is in Ab / F minor; Ab1 = 51.9 Hz
    T["bass"] = bass_stack(T["bass"]["sidechain"])
    T["lead"] = lead_stack(lead, {"send_reverb": lead.get("send_reverb", 0), "send_delay": lead.get("send_delay", 0)})
    T["lead2"]["mute"] = True                        # its notes are the lead's: now the stack's support layer
    return B, {"kick": ["kick"], "bass": ["bass"], "lead": ["lead", "lead2"]}


def half_of_me(P):
    B = copy.deepcopy(P)
    B["genre"] = GENRE
    T = B["tracks"]
    lead = T["lead"]
    T["kick"] = kick_stack("F#1", sub_gain=-4)       # F# minor; F#1 = 46.2 Hz
    T["ksub"]["mute"] = True                         # the published sine thump: now the kick's own sub layer
    T["bass"] = bass_stack(T["bass"]["sidechain"], sub_gain=-5)  # the rolling bass sits on F#1 too: a lower sub
    T["lead"] = lead_stack(lead, {"send_reverb": lead.get("send_reverb", 0), "send_delay": lead.get("send_delay", 0)})
    return B, {"kick": ["kick", "ksub"], "bass": ["bass"], "lead": ["lead"]}


CASES = {
    "first-light": dict(session="007-ecstasy", title="First Light (007), second wave", section="rel2", bars=8,
                        rebuild=first_light),
    "half-of-me": dict(session="013-decay", title="Half of Me (013), main drop", section="mainA", bars=8,
                       rebuild=half_of_me),
}


# ------------------------------------------------------------------ render, measure, write

def span_of(P, section, bars):
    _, _, sections, _ = ST.schedule(ST._prepare(P), Hand(P["bpm"], P.get("swing", 0.5), P.get("seed", 1)))
    S = next(s for s in sections if s["name"] == section)
    bar = 4 * 60.0 / P["bpm"]
    return S["start"], min(S["end"], S["start"] + bars * bar)


def render_excerpt(P, t0, t1):
    ST.I.RNG = np.random.default_rng(1234)  # as a fresh process: A and B do not depend on what rendered before
    pre = 2 * 4 * 60.0 / P["bpm"]
    off = max(0.0, t0 - pre)
    a0, a1 = int(round((t0 - off) * SR)), int(round((t1 - off) * SR))
    stems, layers, aw = {}, {}, {}

    def hook(name, st):
        m = ((st[0, a0:a1] + st[1, a0:a1]) * 0.5).astype(np.float32)
        stems[name] = CL.band_power(m)
        aw[name] = (float((stems[name] * CL.AW[:, None]).sum()), float(np.abs(st[:, a0:a1]).max()))

    def lhook(stack, layer, role, st):
        layers.setdefault(stack, {})[layer] = (role, CL.band_power(((st[0, a0:a1] + st[1, a0:a1]) * 0.5)
                                                                   .astype(np.float32)))
    _, m = ST.render(P, window=(t0, t1), stem_hook=hook, pre_roll=pre, layer_hook=lhook)
    return m["_premaster"][:, a0:a1].copy(), stems, layers, aw


def analyse(P, pre, stems, layers):
    eqmap, _ = CL.load_eqmap(GENRE)
    roles = {n: CL.role_of(n, tr, set(ST.DRUM_TYPES)) for n, tr in P["tracks"].items()}
    roles.update({"(reverb)": ("return", False), "(delay)": ("return", False), "(fx)": ("fx", False)})
    roles.update({f"({r})": ("return", False) for r in (P.get("mix") or {}).get("returns") or {}})
    mono = ((pre[0] + pre[1]) * 0.5).astype(np.float32)
    return CL.analyse(stems, roles, mono, TARGET, eqmap, True, layers or None)


def quick_master(pre):
    """The engine's quick master (studio.render), the same for A and B: no tonal EQ."""
    import pedalboard as pb
    import pyloudnorm as pyln
    x = pb.Pedalboard([pb.HighpassFilter(25), pb.Compressor(-14, 2.0, 25, 200)])(pre.astype(np.float32), SR)
    meter = pyln.Meter(SR)
    L0 = meter.integrated_loudness(x.T)
    g = -10.0 - L0
    for _ in range(4):
        y = ST.limit(x * ST.db(g), -1.0)
        L = meter.integrated_loudness(y.T)
        if abs(L + 10.0) < 0.2:
            break
        g += -10.0 - L
    f = int(0.02 * SR)
    y[:, :f] *= np.linspace(0, 1, f)
    y[:, -f:] *= np.linspace(1, 0, f)
    return y, L


def write_mp3(x, path):
    import soundfile as sf
    tmp = path[:-4] + ".tmp.wav"
    sf.write(tmp, x.T, SR, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-b:a", "192k", path], check=True)
    os.remove(tmp)


def thirds_vs_target(pre):
    tb = MA.third_octave(((pre[0] + pre[1]) * 0.5).astype(np.float64))
    dev = tb - MA.target_curve(MA.THIRD, TARGET)
    off = MA.ref_offset(dev, 2)
    return tb - off, MA.target_curve(MA.THIRD, TARGET)


def picture(case, title, preA, preB, path, rA, rB):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import signal
    fig = plt.figure(figsize=(12, 9.5))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.1])
    for k, (pre, lab) in enumerate(((preA, "A: as published"), (preB, "B: stacks (same notes)"))):
        ax = fig.add_subplot(gs[k, :])
        m = (pre[0] + pre[1]) * 0.5
        f, t, S = signal.spectrogram(m, SR, nperseg=4096, noverlap=3072)
        S = 10 * np.log10(S + 1e-14)
        ax.pcolormesh(t, f, S, shading="auto", cmap="magma", vmin=S.max() - 90, vmax=S.max())
        ax.set_yscale("log")
        ax.set_ylim(25, 18000)
        ax.set_ylabel("Hz")
        ax.set_title(f"{title} - {lab}", fontsize=10)
    ax = fig.add_subplot(gs[2, 0])
    a, tc = thirds_vs_target(preA)
    b, _ = thirds_vs_target(preB)
    ax.semilogx(MA.THIRD, tc, color="0.5", lw=2, label=f"{TARGET} (era target)")
    ax.semilogx(MA.THIRD, a, color="#c05050", label="A published")
    ax.semilogx(MA.THIRD, b, color="#3070c0", label="B stacks")
    ax.set_xlabel("Hz (1/3 octave)")
    ax.set_ylabel("dB, at the target's level around 1 kHz")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_title("tonal balance against the target", fontsize=10)
    ax = fig.add_subplot(gs[2, 1])
    regs = [c["region"] for c in rA["census"]]
    x = np.arange(len(regs))
    ax.bar(x - 0.2, [c["occupancy"] for c in rA["census"]], 0.4, color="#c05050", label="A")
    ax.bar(x + 0.2, [c["occupancy"] for c in rB["census"]], 0.4, color="#3070c0", label="B")
    ax.set_xticks(x)
    ax.set_xticklabels(regs, fontsize=8)
    ax.set_ylabel("occupancy (stems within 6 dB per cell)")
    ax.legend(fontsize=8)
    ax.set_title("layer occupancy per region (listen --clarity)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)


def summary(r, groups):
    vt = r["vs_target"]
    out = dict(vs_target={k: vt[k] for k in ("kick_sub_50_80", "buildup_100_250", "lowmid_315_400", "presence_2k_5k",
                                            "air_8k_12k")},
               occupancy={c["region"]: c["occupancy"] for c in r["census"]},
               within_10db={c["region"]: len(c["within_10db"]) for c in r["census"]},
               crest_db=r["crest_db"],
               stems={s["name"]: dict(role=s["role"], level_db=s["level_db"], masked=s["masked"], own=s["own"])
                      for s in r["stems"] if any(s["name"] in g for g in groups.values())},
               flags=r["flags"])
    if r.get("stacks"):
        out["stacks"] = {st["stack"]: {l["layer"]: dict(role=l["role"], share=l["share"], regions=l["regions"],
                                                         level_db=l["level_db"]) for l in st["layers"]}
                         for st in r["stacks"]}
    return out


def build(case):
    c = CASES[case]
    A = json.load(open(os.path.join(REPO, "sessions", c["session"], "project.json")))
    B, groups = c["rebuild"](A)
    t0, t1 = span_of(A, c["section"], c["bars"])
    print(f"{case}: {c['section']} {t0:.1f}-{t1:.1f} s")
    preA, stA, _, awA = render_excerpt(A, t0, t1)
    for g in groups:  # the level match: a gain at the end of the stack's bus chain
        B["tracks"][g]["fx"] = list(B["tracks"][g].get("fx") or []) + [{"type": "gain", "db": 0.0}]
    for it in range(3):  # kick by peak, bass and lead by A-weighted energy, against the A tracks they replace
        preB, stB, lyB, awB = render_excerpt(B, t0, t1)
        for g, members in groups.items():
            if g == "kick":
                d = 20 * np.log10(max(awA[m][1] for m in members if m in awA) / awB[g][1])
            else:
                d = 10 * np.log10(sum(awA[m][0] for m in members if m in awA) / awB[g][0])
            mg = B["tracks"][g]["fx"][-1]
            mg["db"] = round(mg["db"] + d, 2)
            print(f"  level match {g}: {d:+.2f} dB -> {mg['db']} dB")
    preB, stB, lyB, awB = render_excerpt(B, t0, t1)
    rA, rB = analyse(A, preA, stA, None), analyse(B, preB, stB, lyB)
    xa, La = quick_master(preA)
    xb, Lb = quick_master(preB)
    write_mp3(xa, os.path.join(HERE, f"{case}-A-published.mp3"))
    write_mp3(xb, os.path.join(HERE, f"{case}-B-stacks.mp3"))
    picture(case, c["title"], preA, preB, os.path.join(HERE, f"{case}.png"), rA, rB)
    res = dict(case=case, title=c["title"], session=c["session"], section=c["section"], seconds=[round(t0, 2), round(t1, 2)],
               genre=GENRE, target=TARGET, groups=groups, A=summary(rA, groups), B=summary(rB, groups),
               B_tracks={g: B["tracks"][g] for g in groups})
    json.dump(res, open(os.path.join(HERE, f"{case}.json"), "w"), indent=1)
    for lab, r in (("A", res["A"]), ("B", res["B"])):
        print(f"  {lab}: vs target {r['vs_target']}")
        print(f"     occupancy {r['occupancy']}")
    return res


if __name__ == "__main__":
    for case in (sys.argv[1:] or list(CASES)):
        build(case)
