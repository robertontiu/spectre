"""Helper: expand a riff spec into note tokens. Tokens 'step:note:len' or 'step:note:len:t' (t = tremolo 32nds)."""
import sys
def expand(spec, offset=0, vel=None):
    out = []
    for tok in spec.split():
        p = tok.split(":")
        st, n, ln = float(p[0]) + offset, p[1], float(p[2])
        trem = len(p) > 3 and p[3] == "t"
        if trem:
            k = int(ln * 2)
            for i in range(k):
                v = 0.95 if i == 0 else (0.62 if i % 2 else 0.78)
                out.append(f"{st + i*0.5:g}:{n}:0.5:{v}")
        else:
            out.append(f"{st:g}:{n}:{ln:g}" + (f":{vel}" if vel else ""))
    return " ".join(out)
if __name__ == "__main__":
    print(expand(sys.argv[1]))

import re as _re
def octave(spec, d=-1):
    """Shift every note name in a riff spec by d octaves."""
    return _re.sub(r":([A-G][b#]?)(\d)", lambda m: f":{m.group(1)}{int(m.group(2))+d}", spec)
