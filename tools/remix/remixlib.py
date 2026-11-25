"""helpers for the trap-family remixes: stack an existing track (the original instrument as the first layer, level
and fx unchanged) and add doubling layers; nothing touches patterns, arrangement, bpm, swing or seed."""
import json, copy
FROZEN = ("bpm", "swing", "seed", "patterns", "arrangement")

def as_stack(tr, first="main"):
    """the track turned into a stack whose first layer is the original sound at its original level; keys that act
    on events (humanize, dyn, push, legato...) stay on the track; fx stay on the bus (same order as before)."""
    t = copy.deepcopy(tr)
    if t.get("layers"):
        return t
    inst = t["inst"]
    t["layers"] = [{"name": first, "inst": copy.deepcopy(inst), "gain_db": t.pop("gain_db", 0), "eq": "none"}]
    return t

def add_layer(t, layer):
    t["layers"].append(layer)
    return t

def check_frozen(old, new):
    for k in FROZEN:
        assert json.dumps(old.get(k), sort_keys=True) == json.dumps(new.get(k), sort_keys=True), k
    for k in old["tracks"]:
        assert k in new["tracks"], k
    return True
