"""full.py: the whole arrangement of session 012 (Reunion). Used by build.py full."""
from build import *
import build as B

# knobs changed from iteration to iteration
K = dict(syl_street="loo", syl2="loo", syl3="ah")


def split_first(d):
    ns, ls = d["notes"].split(), d["lyrics"].split()
    return {"notes": ns[0], "lyrics": ls[0]}, {"notes": " ".join(ns[1:]), "lyrics": " ".join(ls[1:])}


def shift(d, off):
    """shift a sung part (or a token string) by off steps"""
    if isinstance(d, dict):
        return {"notes": shift(d["notes"], off), "lyrics": d["lyrics"]}
    out = []
    for tok in d.split():
        a = tok.split(":")
        out.append(":".join([str(int(a[0]) + off)] + a[1:]))
    return " ".join(out)


def part(src, mel, words, lines, off, syl, wordlines=(), last_len=None, drop_first=False, only_first=False):
    d = sung(src, mel, words, lines, off, syl=syl, wordlines=wordlines, last_len=last_len)
    f, r = split_first(d)
    return f if only_first else (r if drop_first else d)


def chd(s, vel=0.6, reg="D4"):
    return {"chords": s, "style": "sustain", "voicing": "close", "register": reg, "vel": vel}


def project():
    P = {"title": "Reunion", "bpm": 84, "swing": 0.5, "seed": 12, "tracks": tracks(), "patterns": {},
         "arrangement": [],
         "mix": {"reverb": {"size": 0.3, "damping": 0.4, "return_db": -7, "lpf": 9000}},
         "master": {"lufs": -14, "sat": 0.0, "tape": 0.0, "glue": False}}
    pat, arr = P["patterns"], P["arrangement"]
    S, S2, S3 = K["syl_street"], K["syl2"], K["syl3"]
    bell4 = up(cut(TUNE, 70, 93, off=-68))            # my a4 phrase on a bell, upbeat at step 2

    # ---- 0. the street: one handbell rings the home phrase (A-flat), then the upbeat of the question
    pat["bell"] = {"bars": 2, "bell_st": bell4,
                   "caller": part(TUNE, MEL, WORDS, [1], 32, S, only_first=True)}
    arr.append({"name": "bell", "bars": 2, "play": ["bell"], "bpm": 76, "auto": {"caller": {"lpf": [4500, 4500]}}})

    # ---- 1. the question alone; the house under line 3; line 4 answered from inside
    st = {"bars": 6}
    c = sung(TUNE, MEL, WORDS, [1, 2, 3], 0, syl=S)
    st["caller"] = split_first(c)[1]
    st["indoor"] = sung(TUNE, MEL, WORDS, [4], 0, syl=S)
    st["organ_door"] = chd(chords(48, 96, lead=48), vel=0.6)
    st["bell_st"] = "38:F5:6:0.35"
    pat["street"] = st
    arr.append({"name": "street", "bars": 6, "play": ["street"], "bpm": 76})

    # ---- 2. the door: A-flat holds, one inner voice rises a semitone (Ab -> F7), the filter opens
    pat["door"] = {"bars": 1, "organ_door": chd("Bb:4 G7:12", vel=0.6),
                   "q_sop": part(TUNE, MEL, WORDS, [5], -80, S, wordlines=(5,), only_first=True),
                   "q_alto": part(ALTO, AMEL, AWORDS, [5], -80, S, wordlines=(5,), only_first=True)}
    arr.append({"name": "door", "bars": 1, "play": ["door"], "bpm": 76,
                "auto": {"organ_door": {"lpf": [500, 5500], "gain_db": [0, 3]}}})   # the organ is filtered, never the words

    # ---- 3. the meeting (B-flat): the quote; the held D4 and the octave fall onto it; then home
    m = {"bars": 6}
    m["q_sop"] = part(TUNE, MEL, WORDS, [5], -96, S, wordlines=(5,), drop_first=True)
    m["q_alto"] = part(ALTO, AMEL, AWORDS, [5], -96, S, wordlines=(5,), drop_first=True)
    m["sop"] = sung(TUNE, MEL, WORDS, [6, 7, 8], -96, syl=S)
    m["alto"] = sung(ALTO, AMEL, AWORDS, [6, 7, 8], -96, syl=S)
    m["organ"] = chd("Bb:4 -:8 " + chords(108, 192), vel=0.45)
    m["pedal"] = cut(BASS, 144, 191, off=-96)
    m["bellL"] = "84:Bb5:10:0.4"
    pat["meet"] = m
    arr.append({"name": "meet", "bars": 6, "play": ["meet"],
                "auto": {"organ": {"gain_db": [-3, 0]}}})

    # ---- 4. bells between the verses: the home phrase passed from hand to hand
    # plain hunt on three handbells (Bb5, G5, F5), one row per half bar: 123 213 231 321 312 132 123
    rows, names = ["123", "213", "231", "321", "312", "132", "123"], {"1": "Bb5", "2": "G5", "3": "F5"}
    L, R = [], []
    for r, row in enumerate(rows):
        for i, bnum in enumerate(row):
            tok = "%d:%s:8:%.2f" % (r * 6 + i * 2, names[bnum], 0.5 if i == 0 else 0.4)
            (R if bnum == "2" else L).append(tok)
    i1 = {"bars": 3, "bellL": " ".join(L), "bellR": " ".join(R),
          "organ": chd("Bb:12 Eb:12 Cm7:6 Bb/D:6 Eb:6 F7:6", vel=0.5),
          "pedal": "0:Bb2:12 12:Eb3:12 24:C3:6 30:D3:6 36:Eb3:6 42:F3:6",
          "chorale": shift(up(cut(TUNE, -2, -2), -1), 48) + " " + shift(cut(TUNE, -2, -2, vel=0.6), 48), "cello": ""}
    pat["inter1"] = i1
    arr.append({"name": "inter1", "bars": 3, "play": ["inter1"],
                "auto": {"bellL": {"gain_db": [-2, -2]}, "bellR": {"gain_db": [-2, -2]}, "pedal": {"gain_db": [-6, -3]}}})

    # ---- 5. verse 2: the house plays (corner chorale on strings + organ), the voices answer; bells in the middle
    v = {"bars": 12}
    v["chorale"] = up(cut(TUNE, 0, 45), -1) + " " + cut(TUNE, 0, 45, vel=0.6)
    lo2 = sung(TUNE, MEL, WORDS, [3, 4], 0, syl=S2)
    v["sop"] = lo2
    al = [sung(ALTO, AMEL, AWORDS, [3, 4], 0, syl=S2), sung(ALTO, AMEL, AWORDS, [5, 6], 0, syl="ooh"),
          sung(ALTO, AMEL, AWORDS, [7, 8], 0, syl=S2)]
    v["alto"] = {"notes": " ".join(x["notes"] for x in al), "lyrics": " ".join(x["lyrics"] for x in al)}
    v["low"] = sung(LOW, {}, {}, [3, 4, 5, 6, 7, 8], 0, syl="ooh")
    s78 = sung(TUNE, MEL, WORDS, [7, 8], 0, syl=S2)
    v["sop"] = {"notes": lo2["notes"] + " " + s78["notes"], "lyrics": lo2["lyrics"] + " " + s78["lyrics"]}
    v["organ"] = chd(chords(0, 192), vel=0.6)
    v["pedal"] = cut(BASS, 0, 191)
    v["cello"] = cut(BASS, 0, 47) + " " + cut(BASS, 144, 191)
    v["bellL"] = "96:D5:6:0.5 108:G5:6:0.5 " + up(cut(TUNE, 118, 141))
    v["bellR"] = "102:F#5:6:0.45 114:Bb5:6:0.45 84:Bb5:8:0.4"
    pat["v2"] = v
    arr.append({"name": "v2", "bars": 12, "play": ["v2"],
                "auto": {"bellL": {"gain_db": [-3.5, -3.5]}, "bellR": {"gain_db": [-3.5, -3.5]}}})

    # ---- 6. the first bell again, now inside (B-flat), the organ under it
    i2 = {"bars": 3, "bellR": up(cut(TUNE, 70, 93, off=-58)),
          "organ": chd("Bb:12 Eb:6 F7:6 Bb:22 -:2", vel=0.45), "pedal": "0:Bb2:12 12:Eb3:6 18:F2:6 24:Bb2:22"}
    for tr, src, mel, w, syl in (("sop", TUNE, MEL, WORDS, S3), ("sop_b", TUNE, MEL, WORDS, S3),
                                 ("alto", ALTO, AMEL, AWORDS, S3), ("alto_b", ALTO, AMEL, AWORDS, S3),
                                 ("low", LOW, {}, {}, "ooh")):
        i2[tr] = part(src, mel, w, [1], 48, syl, only_first=True)
    pat["inter2"] = i2
    arr.append({"name": "inter2", "bars": 3, "play": ["inter2"], "auto": {"pedal": {"gain_db": [-5, -3]}}})

    # ---- 7. verse 3: everyone. a: lines 1-4 full; b: the quote a cappella, my rising line; c: home, slowing
    a, b, c = {"bars": 6}, {"bars": 3}, {"bars": 4}
    for tr, src, mel, w, syl in (("sop", TUNE, MEL, WORDS, S3), ("sop_b", TUNE, MEL, WORDS, S3),
                                 ("alto", ALTO, AMEL, AWORDS, S3), ("alto_b", ALTO, AMEL, AWORDS, S3),
                                 ("low", LOW, {}, {}, "ooh")):
        Q = {"sop": "q_sop", "sop_b": "q_sop2", "alto": "q_alto", "alto_b": "q_alto2"}.get(tr)
        # lines 1-4; the last note is shortened so there is an 8th of breath before the quote's "Peace"
        a[tr] = part(src, mel, w, [1, 2, 3, 4], 0, syl, drop_first=True, last_len=8)
        f7, r7 = split_first(sung(src, mel, w, [7, 8], -144, syl=syl, last_len=24))
        l6 = sung(src, mel, w, [6], -96, syl=syl)
        if Q:      # the quote on its own track: words, on the beat
            f5, r5 = split_first(sung(src, mel, w, [5], -96, syl=syl, wordlines=(5,)))
            a[Q] = {"notes": shift(f5["notes"], 96), "lyrics": f5["lyrics"]}
            b[Q] = r5
            b[tr] = {"notes": l6["notes"] + " " + shift(f7["notes"], 48), "lyrics": l6["lyrics"] + " " + f7["lyrics"]}
        else:      # the low voice hums through
            l5 = sung(src, mel, w, [5], -96, syl=syl)
            f5, r5 = split_first(l5)
            a[tr] = {"notes": a[tr]["notes"] + " " + shift(f5["notes"], 96), "lyrics": a[tr]["lyrics"] + " " + f5["lyrics"]}
            b[tr] = {"notes": r5["notes"] + " " + l6["notes"] + " " + shift(f7["notes"], 48),
                     "lyrics": r5["lyrics"] + " " + l6["lyrics"] + " " + f7["lyrics"]}
        c[tr] = r7
    a["organ"] = chd(chords(0, 96), vel=0.75)
    a["pedal"] = cut(BASS, 0, 95)
    a["cello"] = cut(BASS, 0, 95)
    a["bellL"] = "18:F5:4:0.5 36:C6:2:0.5 40:F5:2:0.45 66:D5:4:0.45 84:Bb5:2:0.55 88:F5:2:0.5"
    a["bellR"] = "38:A5:2:0.45 42:C5:4:0.45 86:D6:2:0.5 90:D5:4:0.5"
    b["organ"] = chd(chords(132, 144, lead=36), vel=0.55)
    b["pedal"] = cut(BASS, 132, 143, off=-96)
    c["organ"] = chd("Bb/D:6 Bb:6 Eb:6 Bb/F:6 Cm:6 F7:6 Bb:28", vel=0.8)
    c["pedal"] = cut(BASS, 144, 191, off=-144, shorten_last=28)
    c["cello"] = cut(BASS, 144, 191, off=-144, shorten_last=28)
    c["bellL"] = "18:F5:4:0.5 36:Bb5:2:0.6 40:F5:2:0.5 44:Bb4:6:0.5"
    c["bellR"] = "12:G5:4:0.4 38:D6:2:0.5 42:D5:2:0.5"
    pat["v3a"], pat["v3b"], pat["v3c"] = a, b, c
    V = ("sop", "sop_b", "alto", "alto_b", "low")
    QV = ("q_sop", "q_sop2", "q_alto", "q_alto2")
    arr.append({"name": "v3a", "bars": 6, "play": ["v3a"], "auto": dict({t: {"gain_db": [-2, 0]} for t in V}, alto_b={"gain_db": [-12, -3]})})
    arr.append({"name": "v3b", "bars": 3, "play": ["v3b"],
                "auto": dict({t: {"gain_db": [-5, -2]} for t in V}, organ={"gain_db": [-8, 0]}, low={"gain_db": [-8, -2]},
                             **{t: {"gain_db": [-2, -2]} for t in QV})})
    arr.append({"name": "v3c", "bars": 4, "play": ["v3c"], "bpm": [84, 60],
                "auto": dict({t: {"gain_db": [-1, 1]} for t in V}, organ={"gain_db": [0, -2]})})

    # ---- 8. the bell that started alone, answered
    pat["end"] = {"bars": 2, "bell_st": "0:G5:4:0.4 6:C6:20:0.45", "organ": chd("Bb:26 -:6", vel=0.5),
                  "pedal": "0:Bb2:26"}
    arr.append({"name": "end", "bars": 2, "play": ["end"], "bpm": 60,
                "auto": {"organ": {"gain_db": [-2, -14]}, "pedal": {"gain_db": [-5, -16]},
                         "bell_st": {"gain_db": [-3, -3]}}})
    for p in pat.values():       # bells: a soft strike (vel <= 0.6) and a note long enough that the ring is never cut
        for k in ("bell_st", "bellL", "bellR"):
            if p.get(k):
                out = []
                for tok in p[k].split():
                    a = tok.split(":")
                    v = min(float(a[3]), 0.6) if len(a) > 3 else 0.55
                    out.append("%s:%s:40:%.2f" % (a[0], a[1], v))
                p[k] = " ".join(out)
    for p in pat.values():       # drop empty parts
        for k in [k for k, x in p.items() if x == ""]:
            del p[k]
    return P
