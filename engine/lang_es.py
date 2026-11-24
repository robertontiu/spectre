"""Spanish letters to DiffSinger phonemes for `singer` `"source": "svs"` with `"lang": "es"`.

Hoshino Hanami (Lotte V) was trained on about 7 minutes of Spanish and ships a Spanish dictionary
(dsdict-es.yaml, MIT) that lists only exceptions (numbers, names, words with consonantal "y"); OpenUtau fills
the rest with a G2P. This module is that G2P for the bank's Spanish phoneme set (Lotte V's Phoneme_chart.md):
vowels a e i o u1; glides y w (before the nucleus) and I1 U1 (after it); stops b d g (after a pause or a nasal,
d also after l) and their approximants bh dh gh (everywhere else, also across words inside a phrase); unaspirated
px tx kx; tap rx and trill rr; l1 (clear l), ny, ch, x (jota), j (consonantal y and ll: yeismo), s (c/z before
e/i: seseo, as in Latin American Spanish). Spanish spelling is close to phonemic, so the rules are short; the
rules and their sources are in docs/voice/languages/es.md.
"""
import unicodedata

STRONG = set("aeoáéó")
ACC_HIGH = set("íú")
VOWELS = set("aeiouáéíóúü")
BILABIAL = set("bvpm")
LIQUID_ONSET = {("px", "rx"), ("px", "l1"), ("b", "rx"), ("b", "l1"), ("bh", "rx"), ("bh", "l1"), ("tx", "rx"),
                ("d", "rx"), ("dh", "rx"), ("kx", "rx"), ("kx", "l1"), ("g", "rx"), ("g", "l1"), ("gh", "rx"),
                ("gh", "l1"), ("f", "rx"), ("f", "l1"), ("tx", "l1")}
NUCLEI = {"a", "e", "i", "o", "u1"}
GLIDES = {"y", "w", "I1", "U1"}


def _clean(word):
    w = word.lower().strip(",.!?;:'\"¡¿()«»-")
    # keep Spanish letters; drop other diacritics
    out = []
    for ch in w:
        if ch in "áéíóúüñ" or ch.isascii():
            out.append(ch)
        else:
            out.append("".join(c for c in unicodedata.normalize("NFD", ch) if not unicodedata.combining(c)))
    return "".join(out)


def _vowel_roles(w):
    """For each vowel letter (and 'y' acting as a vowel): 'n' nucleus, 'pre' onglide, 'post' offglide."""
    roles = {}
    i = 0
    n = len(w)

    def isv(k):
        c = w[k]
        if c in VOWELS:
            # u after q, and after g before e/i, is silent (handled by the consonant rules)
            if c == "u" and k > 0 and (w[k - 1] == "q" or (w[k - 1] == "g" and k + 1 < n and w[k + 1] in "eiéí")):
                return False
            return True
        if c == "y":  # 'y' is a vowel at the end of a word or before a consonant ("hoy", "muy", "y")
            return k == n - 1 or (k + 1 < n and w[k + 1] not in VOWELS)
        return False

    while i < n:
        if not isv(i):
            i += 1
            continue
        j = i
        while j < n and isv(j):
            j += 1
        cl = list(range(i, j))
        strong = [k for k in cl if w[k] in STRONG or w[k] in ACC_HIGH]
        if not strong:  # only weak vowels: the last one carries the syllable (ciudad, muy, fui)
            strong = [cl[-1]]
        for k in cl:
            if k in strong:
                roles[k] = "n"
            else:
                after = any(s > k for s in strong)
                roles[k] = "pre" if after else "post"
        i = j
    return roles


def g2p(word, prev=None):
    """Phonemes of one Spanish word. `prev`: the last phoneme of the previous word in the same phrase (None after a
    pause), so word-initial b/d/g become approximants after a vowel, as in connected speech ("la vida" la-bhi-dha)."""
    w = _clean(word)
    if not w:
        return []
    roles = _vowel_roles(w)
    out = []
    n = len(w)
    i = 0

    def last():
        return out[-1] if out else prev

    def after_pause_or_nasal(kind):
        p = last()
        if p is None:
            return True
        if p in ("m", "n", "ny", "ng"):
            return True
        if kind == "d" and p == "l1":
            return True
        return False

    while i < n:
        c = w[i]
        nx = w[i + 1] if i + 1 < n else ""
        if i in roles:
            r = roles[i]
            base = {"a": "a", "á": "a", "e": "e", "é": "e", "o": "o", "ó": "o", "i": "i", "í": "i", "y": "i",
                    "u": "u1", "ú": "u1", "ü": "u1"}[c]
            if r == "n":
                out.append(base)
            elif base == "i":
                out.append("y" if r == "pre" else "I1")
            elif base == "u1":
                out.append("w" if r == "pre" else "U1")
            else:  # a strong vowel can't be a glide; keep it (hiatus)
                out.append(base)
            i += 1
            continue
        if c == "c" and nx == "h":
            out.append("ch"); i += 2; continue
        if c == "l" and nx == "l":
            out.append("j"); i += 2; continue
        if c == "r" and nx == "r":
            out.append("rr"); i += 2; continue
        if c == "q":
            out.append("kx"); i += 2 if nx == "u" else 1; continue
        if c == "g" and nx == "u" and i + 2 < n and w[i + 2] in "eiéí":
            out.append("g" if after_pause_or_nasal("g") else "gh"); i += 2; continue
        if c == "g" and nx == "ü":
            out.append("g" if after_pause_or_nasal("g") else "gh"); i += 1; continue
        if c == "g":
            if nx in "eiéí":
                out.append("x")
            else:
                out.append("g" if after_pause_or_nasal("g") else "gh")
            i += 1; continue
        if c == "c":
            out.append("s" if nx in "eiéí" else "kx"); i += 1; continue
        if c in "bv":
            out.append("b" if after_pause_or_nasal("b") else "bh"); i += 1; continue
        if c == "d":
            out.append("d" if after_pause_or_nasal("d") else "dh"); i += 1; continue
        if c == "r":
            p = last()
            out.append("rr" if (not out and prev is None) or (not out) or p in ("n", "l1", "s") else "rx")
            i += 1; continue
        if c == "n":
            out.append("m" if nx in BILABIAL or nx == "f" else "n"); i += 1; continue
        simple = {"p": "px", "t": "tx", "k": "kx", "f": "f", "s": "s", "z": "s", "m": "m", "l": "l1", "ñ": "ny",
                  "j": "x", "y": "j", "w": "w"}
        if c in simple:
            out.append(simple[c]); i += 1; continue
        if c == "x":
            out.extend(["kx", "s"]); i += 1; continue
        if c == "h":  # silent
            i += 1; continue
        i += 1  # anything else: ignored
    return out


def syllables(phs, n):
    """Cut a word's phonemes into n syllables at the Spanish boundaries: one consonant between two nuclei goes to
    the next syllable; of two or more, the last goes (or the last two when they form an onset like pr, bl, tr);
    glides stay with their nucleus. Returns None if the word doesn't have n nuclei."""
    vi = [k for k, p in enumerate(phs) if p in NUCLEI]
    if len(vi) != n:
        return None
    cuts = [0]
    for a, b in zip(vi, vi[1:]):
        lo = a + 1
        while lo < b and phs[lo] in ("I1", "U1"):  # offglides stay with the previous nucleus
            lo += 1
        hi = b
        while hi - 1 >= lo and phs[hi - 1] in ("y", "w"):  # onglides go with the next nucleus
            hi -= 1
        cons = phs[lo:hi]
        if len(cons) == 0:
            cut = hi
        elif len(cons) >= 2 and (cons[-2], cons[-1]) in LIQUID_ONSET:
            cut = hi - 2
        else:
            cut = hi - 1
        cuts.append(cut)
    cuts.append(len(phs))
    return [phs[cuts[k]:cuts[k + 1]] for k in range(n)]


def count_syllables(word):
    return sum(1 for p in g2p(word) if p in NUCLEI)
