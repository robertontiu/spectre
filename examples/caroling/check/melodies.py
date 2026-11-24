"""The verified carol melodies of docs/CAROLING.md ("Verified melodies") as engine note strings, and the check
project that plays them (examples/caroling/project.json). Rebuild: python3 examples/caroling/check/melodies.py

Grid: a carol bar of three beats (6/8 felt as two dotted quarters, or 3/4) is 12 steps, so 4 carol bars = 3 engine bars.
CAROL (6/8): an eighth = 2 steps, engine bpm = the carol's quarter-note rate (dotted quarter = bpm / 1.5).
THE FIRST NOWELL (3/4): a quarter = 4 steps, engine bpm = the quarter-note rate.
"""
import json, os

# It Came Upon the Midnight Clear: tune CAROL, R. S. Willis (1850), words E. H. Sears (1849). B-flat major, 6/8.
CAROL_PICKUP = "14:F4:2"
CAROL = ("0:D5:4 4:C5:2 6:C5:2 8:Bb4:2 10:G4:2 12:F4:4 16:G4:2 18:F4:4 22:F4:2 "
         "24:G4:2 26:A4:2 28:Bb4:2 30:Bb4:2 32:C5:2 34:D5:2 36:C5:10 46:F4:2 "
         "48:D5:4 52:A4:2 54:C5:2 56:Bb4:2 58:G4:2 60:F4:4 64:G4:2 66:F4:4 70:F4:2 "
         "72:G4:4 76:G4:2 78:A4:2 80:G4:2 82:F4:2 84:Bb4:10 94:D5:2 "
         "96:D5:4 100:D4:2 102:D4:2 104:E4:2 106:F#4:2 108:G4:4 112:A4:2 114:Bb4:4 118:D5:2 "
         "120:C5:2 122:Bb4:2 124:A4:2 126:G4:2 128:A4:2 130:G4:2 132:F4:10 142:F4:2 "
         "144:D5:4 148:A4:2 150:C5:2 152:Bb4:2 154:G4:2 156:F4:4 160:G4:2 162:F4:4 166:F4:2 "
         "168:G4:4 172:G4:2 174:A4:2 176:G4:2 178:F4:2 180:Bb4:12")

# The First Nowell: traditional (W. Sandys 1833), as in Bramley & Stainer 1871. D major, 3/4.
NOWELL_PICKUP = "12:F#4:2 14:E4:2"
_HALF = ("{o}:D4:6 {o6}:E4:2 {o8}:F#4:2 {o10}:G4:2 {o12}:A4:8 {o20}:B4:2 {o22}:C#5:2 "
         "{o24}:D5:4 {o28}:C#5:4 {o32}:B4:4 {o36}:A4:8 {o44}:B4:2 {o46}:C#5:2 "
         "{o48}:D5:4 {o52}:C#5:4 {o56}:B4:4 {o60}:A4:4 {o64}:B4:4 {o68}:C#5:4 "
         "{o72}:D5:4 {o76}:A4:4 {o80}:G4:4 {o84}:F#4:8 {o92}:F#4:2 {o94}:E4:2")
def _half(o):
    return _HALF.format(**{"o": o, **{f"o{k}": o + k for k in range(2, 96, 2)}})
NOWELL = (_half(0) + " " + _half(96) + " "
          "192:D4:6 198:E4:2 200:F#4:2 202:G4:2 204:A4:8 212:D5:2 214:C#5:2 216:B4:8 224:B4:4 "
          "228:A4:8 236:A4:4 240:D5:4 244:C#5:4 248:B4:4 252:A4:4 256:B4:4 260:C#5:4 "
          "264:D5:4 268:A4:4 272:G4:4 276:F#4:12")

def project():
    tr = {"melody": {"inst": {"type": "piano", "felt": 0.2}, "gain_db": 0, "humanize_ms": 0, "vel_jitter": 0.0,
                     "legato": 0.92, "send_reverb": 0.15}}
    pats = {"carol_pickup": {"bars": 1, "melody": CAROL_PICKUP}, "carol": {"bars": 12, "melody": CAROL},
            "nowell_pickup": {"bars": 1, "melody": NOWELL_PICKUP}, "nowell": {"bars": 18, "melody": NOWELL}}
    arr = [{"name": "carol_pickup", "bars": 1, "play": ["carol_pickup"], "bpm": 84},
           {"name": "carol", "bars": 12, "play": ["carol"], "bpm": 84},
           {"name": "nowell_pickup", "bars": 1, "play": ["nowell_pickup"], "bpm": 104},
           {"name": "nowell", "bars": 18, "play": ["nowell"], "bpm": 104}]
    return {"title": "carol melody check (CAROL, Willis 1850; THE FIRST NOWELL, Stainer 1871)", "bpm": 84,
            "swing": 0.5, "seed": 1, "tracks": tr, "patterns": pats, "arrangement": arr,
            "mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -8, "lpf": 7000}},
            "master": {"lufs": -14, "sat": 0.0, "tape": 0.0, "glue": False}}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project.json")
    with open(out, "w") as fh:
        json.dump(project(), fh, indent=1)
    print("wrote", out)
