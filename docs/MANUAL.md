# Studio manual

You make the beat by editing `project.json` in your working folder, rendering it, and listening with the ears.

```
python3 engine/studio.py render              # render project.json -> renders/vNNN.wav (~15-25 s)
python3 engine/studio.py render --solo 808   # render one track alone -> renders/solo_808.wav
python3 engine/studio.py listen              # overview -> ear.png + stats (whole beat)
python3 engine/studio.py listen --bars 9-12  # zoom: hi-res spectrogram + onset grid + timing roll -> ear_zoom.png
python3 engine/studio.py listen --section hook1
python3 engine/studio.py listen --mono / --lowpass    # squint checks (combine with --bars)
python3 engine/studio.py listen --wav renders/solo_808.wav --bars 1-4   # listen to a solo render
python3 engine/studio.py master [vNNN] [--lufs -11 --tp -1 --eq 0.9 --translate 0.5]
        # FINAL STEP: masters the premaster of vNNN -> renders/vNNN.master.wav/.mp3/.png/.report.json
```
Every render also writes `renders/vNNN.premaster.wav` (the raw mix bus). The quick master inside `render` is only for listening while you work. The release master comes from `master`, which applies sub-sonic cleanup, mono low end, two-pass linear-phase tonal EQ toward a hip-hop target curve, gentle 4-band compression, bass harmonics for small speakers, glue compression, and a soft clip into a 4x-oversampled true-peak limiter. It reports LUFS, true peak, PLR, loudness range, laptop-speaker loss and remaining tonal deviations. If the report shows the EQ hitting its 8 dB limit or the limiter working hard (over 6 dB), fix the mix rather than the master.
Always work from inside your session folder with `BEAT_DIR` set to it: `cd sessions/NNN-name && export BEAT_DIR=$PWD`, then call the engine as `python3 ../../engine/studio.py ...` (the commands above are written relative to the repo root for readability). After `listen`, open the printed image with the Read tool. That image plus the printed numbers are your ears.

How to read the ears:
- **Arrangement lanes**: which track sounds where and how loud. This is your arrangement view.
- **Mel spectrogram**: low notes at the bottom. Vertical stripes are drum hits (bright, full-height = snare/clap/hat; bottom = kick/808). Horizontal lines are sustained tones: chords and melody. Dense = busy; dark gaps = space.
- **Band energy** (sub, low, lowmid, high, air): the weight of the mix over time. Contrast between sections shows as steps.
- **Loudness curve**: the dynamics of the arrangement. A flat line from start to finish means no journey.
- **Zoom timing roll**: every hit the hand played against the 16th grid. Dot size = velocity. It shows swing, push/drag, ghost notes and rolls exactly.
- Stats: integrated LUFS, per-section loudness, centroid (brightness), onsets per second (busyness), stereo width, band levels, plus warnings.

## project.json

```json
{
  "title": "...",
  "bpm": 84,
  "swing": 0.58,                 // 0.5 straight .. 0.66 triplet shuffle (applies to odd 16ths)
  "seed": 1,
  "tracks": { "<name>": TRACK, ... },
  "patterns": { "<name>": PATTERN, ... },
  "arrangement": [ SECTION, ... ],
  "mix": {"reverb": {"size": 0.75, "damping": 0.55, "return_db": -4, "lpf": 7000},
          "delay": {"beats": 0.75, "feedback": 0.35, "return_db": -6, "lpf": 3500}},
  "master": {"lufs": -10.5, "sat": 0.15, "tape": 0.0, "glue": true}
}
```

### TRACK
```json
{"inst": {"type": "...", ...sound params},
 "gain_db": 0, "pan": 0.0, "width": 0.0,          // gain is relative to a sensible default per type
 "push_ms": 0,                                     // + = late (laid back), - = early (urgent)
 "humanize_ms": 4, "vel_jitter": 0.06,             // the hand's looseness
 "swing": null,                                    // override global swing for this track
 "dyn": [1.0, 0.7, 0.88, 0.66],                    // velocity shape per 16th position (drums)
 "roll_pitch": 0,                                  // semitones a roll climbs (+) or falls (-)
 "legato": 0.95, "choke": false,
 "send_reverb": 0.0, "send_delay": 0.0,
 "sidechain": {"source": "kick", "depth": 0.6, "release_ms": 120},
 "fx": [ {"type": "...", ...}, ... ],
 "mute": false}
```

Instrument types and their main params (all optional):
- **Drums**: `kick` (tune Hz 40-70, decay, punch 0-2, click 0-1, drive), `snare` (tone, decay, snap 0-1, body, drive), `clap` (tone, decay, spread), `hat` (decay 0.02-0.08, tone Hz, tune, noise), `openhat` (decay 0.15-0.6), `rim`, `shaker`, `snap`, `tom` (tune, decay), `crash` (decay, tone), `cowbell`, `darbuka` (stroke: doum = deep centre, tek = bright rim, ka = muted rim, slap; tune, decay). Use one darbuka track per stroke type
- **Monophonic with glide**: `808` (decay 0.3-3, drive 0-1, punch, tone 0-0.5 = 2nd harmonic, glide_ms, release), `bass` (cutoff, sub, drive, attack, release), `lead` (cutoff, square, vibrato, glide_ms), `ney` (breathy reed flute: breath 0-1, vibrato, attack, glide_ms; use `~` glides and short grace notes for maqam-style ornaments), `nai` (Romanian pan flute: purer tone with a breathy chiff on each new note; breath, vibrato, glide_ms), `trembita` (Hutsul long wooden horn: natural-harmonic, swells brassier; attack, bright 0-1, blare 0-1, breath; sounds best on roots and fifths, low register, glides between harmonics), `fiddle` (folk violin, bowed: vibrato, grit 0-1 for a rough lăutar edge, bow_noise, attack, glide_ms; glides and grace notes make the ornaments)
- **Polyphonic**: `lira` (hurdy-gurdy: steady nasal wheel-bowed tone; long notes = drones; buzz 0-1 and buzz_rate for the rhythmic trompette buzz), `cimbalom` (țambal, hammered dulcimer: hard 0-1, damp 0-1; repeated 32nds = the classic tremolo roll; chords as arpeggiated or rolled accompaniment), `oud` (fretless lute (with `bright` near 1 and `damp` about 0.99 it doubles as a Romanian cobza): damp 0.98-0.997, bright; fast repeated 16ths/32nds = tremolo picking), `ep` (electric piano: bright, sustain, release), `piano` (felt 0-1, release), `pad` (attack, release, cutoff, voices, detune cents), `strings` (attack, release, cutoff, vibrato, detune), `choir` (vowel ah/oo/ee/oh, attack, release), `bell` (decay, ratio), `musicbox`, `pluck` (damp 0.99-0.999, bright), `organ` (drawbars [..]), `sine` (attack, release)
- **Textures** (continuous while a pattern lists them with the value `"on"`): `vinyl` (density), `tape`, `rain`
- Any tonal instrument accepts `"transpose": semitones`.

FX types (in order): `hpf` {hz}, `lpf` {hz}, `eq` {hz, gain_db, q}, `lowshelf`/`highshelf` {hz, gain_db}, `comp` {threshold_db, ratio, attack_ms, release_ms}, `drive` {db}, `sat` {amount}, `bitcrush` {bits}, `srr` {hz}, `lofi` {amount 0-1: wow/flutter, sample-rate, dust}, `chorus` {rate, depth, mix}, `phaser`, `tremolo` {rate, depth}, `delay` {beats, feedback, mix}, `reverb` {size, mix}, `pitch` {semitones}, `width` {amount}, `gain` {db}

### PATTERN
A pattern is a set of parts for several tracks, `bars` long. Sections loop patterns.
```json
"beatA": {"bars": 1,
  "kick":  "X.....x...x.....",
  "snare": "....X..o....X...",
  "hat":   "x.x.x.x.x.x.x.xr"}
```
- **Drum steps**: the string length / bars = grid (16 = 16ths, 12 = 8th-note triplets, 24 = 16th triplets, 32 = 32nds). `|` and spaces are ignored.
  `X` accent 1.0, `x` normal 0.82, `o` ghost 0.45, `g` faint 0.3, `1`-`9` exact velocity, `.` rest.
  Rolls inside one step: `r` 2 hits, `t` 3, `q` 4, `s` 6, `z` 8. Uppercase (`R`, `T`, `Q`, `S`, `Z`) = crescendo roll.
- **Notes** (808, bass, lead, any instrument as a melody): `"step:note:len"` tokens, step and len in 16ths from the pattern start.
  `"0:F1:6 6:F1:2 10:Ab1:6~ 16:Db2:8"`. Suffix `~` on len = glide into this note from the previous one, `!` = accent, `.` = soft; an optional 4th field sets velocity (`"8:C5:2:0.5"`).
- **Chords** (polyphonic tracks): `{"chords": "Fm9:16 Dbmaj7:16 Bbm9:8 C7b9:8", "style": "sustain", "register": "Ab4", "voicing": "keys", "vel": 0.7}`
  Lengths in 16ths (16 = one bar). `-:8` = rest. Slash chords work (`Ab/C`). The hand voice-leads between chords.
  style: `sustain`, `strum` (strum_ms), `stabs` (with `"rhythm": "x..x..x...x....."` per bar, `stab_len`), `arp` (`rate` in 16ths, `pattern` up/down/updown/random, `octaves`).
  voicing: `keys` (left-hand root plus right-hand close voicing), `close`, `spread`.
  Qualities: "", m, maj7, m7, 7, m9, maj9, 9, add9, madd9, 6, m6, sus2, sus4, 7sus4, dim, dim7, m7b5, aug, 7b9, 7#9, m7b9, 11, m11, 13, maj13, 6/9, maj7#11, 7b13, mmaj7, m(maj9), 5
- **Texture**: `"vinyl": "on"`

### SECTION
```json
{"name": "hook1", "bars": 8, "play": ["keysA", "beatB", "bassA"],
 "fill": {"pattern": "fillA"},                       // replaces those tracks in the last bar(s) of the section
 "auto": {"keys": {"lpf": [600, 8000], "gain_db": [-6, 0], "mute": false}},   // ramps across the section
 "enter": {"impact": 0.8, "crash": 0.6, "downlifter": 2},                       // on the first downbeat (downlifter in beats)
 "exit":  {"riser": 4, "reverse": 2,                                            // ending exactly at the section end (beats)
           "cut": {"tracks": ["kick", "808"], "beats": 1},                       // drop-out before the next section ("all" for every track)
           "lpf": {"tracks": ["keys"], "beats": 4, "to_hz": 400},
           "tapestop": 2, "silence": 1}}
```
Note: an exit `cut` only silences its own window; 808 and reverb tails can ring on into the next section. For true silence in a section, also add `"auto": {"<track>": {"mute": true}}` there.
Section names must be unique. Bars per section should be multiples of 4 (2 for short breaks).

## Tips from the bench
- Melodic and pad instruments sit far below drums by default; raise `gain_db` in steps of 2-3 dB.
- Hats live and die by `dyn`, `humanize_ms`, swing and rolls. The 808 should almost always sidechain to the kick or follow it.
- High-pass melodic tracks (`hpf` 120-200) so the 808 owns the low end.
- `lofi` plus `send_reverb` on keys gives the "sampled record" feel; `width` 0.3-0.7 on pads and keys opens the stereo field (the default is quite mono).
- A render is about 20 s; an overview listen about 25 s. Zoom listens are faster.
