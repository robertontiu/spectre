#!/usr/bin/env python3
"""stackview.py [stack ...]: per section, the clarity census, vs_target, stems and the layers of the named stacks (from clarity.json)"""
import json, sys
c = json.load(open("clarity.json"))
want = sys.argv[1:]
for s in c["sections"]:
    nm = s.get("name") or s.get("section") or "?"
    print("==", nm, "sounding", s["sounding"])
    print("  census", " ".join("%s %.0f%%/%.2f[%s]" % (r["region"], 100*r["share"], r["occupancy"], ",".join(w[0] for w in r["within_10db"])) for r in s["census"]))
    print("  vs", s.get("vs_target"))
    for st in s["stems"]:
        print("  stem %-8s %-10s lvl %6.1f masked %3.0f%% own %3.0f%% by %s eq %s" % (st["name"], st["role"], st["level_db"], 100*st["masked"], 100*st["own"], st["masker"], st.get("eq")))
    for stk in s.get("stacks", []):
        if stk["stack"] in s["sounding"] and (not want or stk["stack"] in want):
            for L in stk["layers"]:
                print("    %-7s %-6s %-10s %5.1f dB share %3.0f%% %s" % (stk["stack"], L["layer"], L["role"], L["level_db"], 100*L["share"], " ".join("%s%.0f" % (k[:3], 100*v) for k, v in L["regions"].items())))
