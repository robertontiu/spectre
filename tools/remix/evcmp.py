"""Check that a remix kept the composition: every track of the published render must have identical events
(time, velocity, pitch) in the new render. Tracks added by the remix are listed.

usage: python3 evcmp.py <published vNNN.meta.json> <new vNNN.meta.json>      exit code 1 if any original track differs
"""
import json
import sys

a = json.load(open(sys.argv[1]))["events"]
b = json.load(open(sys.argv[2]))["events"]
bad = 0
for t, ev in a.items():
    if t not in b:
        print("MISSING", t)
        bad += 1
    elif json.dumps(ev, sort_keys=True) != json.dumps(b[t], sort_keys=True):
        print("DIFF", t, len(ev), len(b[t]))
        bad += 1
print(f"{len(a)} original tracks, {bad} differ; new tracks: {[t for t in b if t not in a]}")
sys.exit(1 if bad else 0)
