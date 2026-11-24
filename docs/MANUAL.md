# Studio manual

You make the beat by editing `project.json` in your working folder, rendering it, and listening with the ears.

```
python3 engine/studio.py render              # render project.json -> renders/vNNN.wav (~15-25 s)
python3 engine/studio.py render --solo 808   # render one track alone -> renders/solo_808.wav (real level, not loudness-normalized; doesn't change latest.json)
python3 engine/studio.py listen              # overview -> ear.png + stats (whole beat)
python3 engine/studio.py listen --bars 9-12  # zoom: hi-res spectrogram + onset grid + timing roll -> ear_zoom.png
python3 engine/studio.py listen --section hook1
python3 engine/studio.py listen --mono / --lowpass    # squint checks (combine with --bars)
python3 engine/studio.py listen --wav renders/solo_808.wav --bars 1-4   # listen to a solo render
python3 engine/studio.py listen --phone --genre hiphop   # phone-speaker check: top end vs the genre curve, hiss per section
python3 engine/studio.py master [vNNN] --genre trap|hiphop|trance|rock [--lufs .. --tp .. --eq .. --translate .. --target ..]
        # FINAL STEP: masters the premaster of vNNN -> renders/vNNN.master.wav/.mp3/.png/.report.json
        # (--legacy-master reproduces the masters released before 2026-11-24; never use it for new work)
```
Every render also writes `renders/vNNN.premaster.wav` (the raw mix bus). The quick master inside `render` is only for listening while you work. The release master comes from `master`, which applies sub-sonic cleanup, mono low end, two-pass linear-phase tonal EQ toward the genre's target curve, gentle 4-band compression, bass harmonics for small speakers, glue compression, and a soft clip into a 4x-oversampled true-peak limiter. It reports LUFS, true peak (of the WAV and of the MP3, which the encoder pushes up by about 0.5 dB), PLR, loudness range, stereo width (side minus mid), laptop-speaker loss, remaining tonal deviations, `top_end` (each band from 1 to 16 kHz against the curve, with the curve laid over the master at its level around 1 kHz) and a `phone` check of the premaster and the master. Since master version 2 (2026-11-24) the master measures its own output and corrects again until every band from 1 to 16 kHz is within about 1.5 dB of the curve; it cuts excess top end at full strength but boosts a dull top end by at most +2 dB, so a dull mix stays dull and has to be fixed in the mix. If the report notes the EQ at its limit (-8/+4 dB, `eq_at_limit`) or the limiter working hard (over 6 dB), fix the mix rather than the master.

**The phone check (`listen --phone`, and `phone` in the master report).** Phones play almost nothing below 300 Hz and lift 2-5 kHz, so on a phone the top end and any raw noise is what you hear first; a hat, rain, vinyl or breath noise that sits fine on big speakers can read as loud "static". The check plays the track through a small-speaker model (high-pass 280 Hz, +4 dB at 3 kHz, low-pass 12 kHz) and prints: `6-12 kHz vs 1-2.8 kHz` against the same ratio of the genre curve heard through the same speaker (`air_excess_db`; 0 = on the curve), `5-16 kHz` likewise, the spectral flatness of 4-16 kHz (1 = white noise, 0 = pure tones; a mix's top made of hats and hiss reads about 0.15-0.25, a top that is nothing but noise 0.35 and up), the worst 3-second window, and a per-section table (`<- bright`: more than 3 dB over the curve; `<- hissy`: bright and noise-like). Run it on your render before you master (`listen --phone --genre <genre>`; add `--section`/`--bars` to zoom). What to do: a section flagged bright or hissy, or a worst window more than about 6 dB over the curve, is a mix fix, not a master fix. Find the source with solos (`render --solo hat`) and shape it: lower it, low-pass or high-shelf its top (hats rarely need much above 10-12 kHz; rain, wind, vinyl and breath noise usually belong under 4-6 kHz), or give it less time exposed on its own. The master can move the whole track's top end onto the curve, but it can't turn down one noise in one section.
**`--genre` is required** (there is no default): it sets the target curve, loudness, true peak, EQ strength and translation from `engine/genres.json`; any flag you add overrides that one value. Genres: `trap` (808 beats; target `beat`, a hand-tuned curve, -10.5 LUFS: the setup of sessions 001-006 as first released), `hiphop` (the same with the measured hip-hop curve; use it for beat sessions: sessions 001-006 were remastered with it on 2026-11-24), `trance` (-10 LUFS, translate 0.4), `rock` (pop rock; -10 LUFS, translate 0.3). The trance, rock and hiphop curves are measured from commercial records (docs/MASTERING.md): `rock` asks for a lot of 100-400 Hz body and `trance` for a 80-160 Hz punch with little 31-50 Hz sub, so a sub-heavy kick or thin guitars show up as EQ at its limit. Louder than about -9.5 LUFS gains little: a true-peak guard turns the master down if inter-sample peaks would pass `--tp`, and the report then shows `tp_guard_db`.
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
 "sidechain": {"source": "kick", "depth": 0.6, "release_ms": 120},   // works on any track, from any drum track
 "choke_by": "hat",                                // another track's hits cut this track's ring (open hat choked by the closed hat)
 "fx": [ {"type": "...", ...}, ... ],
 "mute": false}
```

Instrument types and their main params (all optional):
- **Drums**: `kick` (tune Hz 40-70, decay, punch 0-2, click 0-1, drive), `snare` (tone, decay, snap 0-1, body, drive), `clap` (tone, decay, spread), `hat` (decay 0.02-0.08, tone Hz, tune, noise), `openhat` (decay 0.15-0.6), `rim`, `shaker`, `snap`, `tom` (tune, decay), `crash` (decay, tone), `cowbell`, `tridksnis` (Latvian trīdeksnis: a staff of metal plates and rings: a scatter of clinks over a thud; decay, thud 0-1), `darbuka` (stroke: doum = deep centre, tek = bright rim, ka = muted rim, slap; tune, decay). Use one darbuka track per stroke type
- **Monophonic with glide**: `808` (decay 0.3-3, drive 0-1, punch, tone 0-0.5 = 2nd harmonic, glide_ms, release), `bass` (cutoff, sub, drive, attack, release), `lead` (cutoff, square, vibrato, glide_ms), `ney` (breathy reed flute: breath 0-1, vibrato, attack, glide_ms; use `~` glides and short grace notes for maqam-style ornaments), `nai` (Romanian pan flute: purer tone with a breathy chiff on each new note; breath, vibrato, glide_ms), `dudas` (Latvian bagpipe: constant-pressure reedy chanter, no dynamics; pulse 0.2-0.45 = reed colour, drone = Hz of a built-in drone under the chanter, drone_level; ornaments via short grace notes since a bagpipe can't articulate with silence), `trembita` (Hutsul long wooden horn: natural-harmonic, swells brassier; attack, bright 0-1, blare 0-1, breath; sounds best on roots and fifths, low register, glides between harmonics), `fiddle` (folk violin, bowed: vibrato, grit 0-1 for a rough lăutar edge, bow_noise, attack, glide_ms; glides and grace notes make the ornaments)
- **Polyphonic**: `kokle` (Latvian box zither: plucked, bright, long ring with a soft shimmer; ring 0-1, bright, damped true for short notes; traditionally diatonic with low strings used as drones), `lira` (hurdy-gurdy: steady nasal wheel-bowed tone; long notes = drones; buzz 0-1 and buzz_rate for the rhythmic trompette buzz), `cimbalom` (țambal, hammered dulcimer: hard 0-1, damp 0-1; repeated 32nds = the classic tremolo roll; chords as arpeggiated or rolled accompaniment), `oud` (fretless lute (with `bright` near 1 and `damp` about 0.99 it doubles as a Romanian cobza): damp 0.98-0.997, bright; fast repeated 16ths/32nds = tremolo picking), `ep` (electric piano: bright, sustain, release), `piano` (felt 0-1, release), `pad` (attack, release, cutoff, voices, detune cents), `strings` (attack, release, cutoff, vibrato, detune), `choir` (vowel ah/oo/ee/oh, attack, release), `bell` (decay, ratio), `musicbox`, `pluck` (damp 0.99-0.999, bright), `organ` (drawbars [..]), `sine` (attack, release)
- **Textures** (continuous while a pattern lists them with the value `"on"`): `vinyl` (density), `tape`, `rain`
- Any tonal instrument accepts `"transpose": semitones`.

**Trance** (see `docs/TRANCE.md`; example project `examples/trance-test.json`):
- `clubkick` (drum): four-on-the-floor club kick. tune Hz 45-60 (default 50), punch 0-2 (pitch drop), click 0-1, top 0-1 (909-style noise top), drive, hold s (0.045), tail s (0.085; short so the bass rolls between kicks), length s (0.32).
- `supersaw` (polyphonic, **stereo**): the JP-8000-style supersaw for leads, chords, plucks and pads. voices (7), detune cents (25; under 10 thin, over 30 out of tune), mix 0-1 (side voices vs centre, 0.7), spread 0-1 (stereo width of the side voices, 0.8), cutoff Hz (9000), reso 0-1, env Hz (filter envelope, 0 = off), fdecay s, attack, decay, sustain_level, release. `pan` acts as balance. Pluck: `"sustain_level": 0, "decay": 0.15, "cutoff": 900, "env": 6000, "fdecay": 0.07`. Pad: `"attack": 1.2, "release": 2.0, "cutoff": 2500`. High-pass chords (`hpf` 200-300).
- `trancebass` (polyphonic, short notes): offbeat/rolling bass, two detuned saws through a plucky filter over a sine sub. cutoff Hz (260), env Hz (2200), fdecay s (0.07), reso, sub 0-1 (0.8), detune, drive, decay, sustain_level, release. Play it with chord stabs and `"voicing": "root"` and sidechain it to the kick: offbeat `"..x...x...x...x."` stab_len 2, rolling `".xxx.xxx.xxx.xxx"` stab_len 1.

**Pop rock** (see `docs/POP_ROCK.md`; example project `examples/poprock-test.json`):
- Acoustic kit (drums; each repeated hit cycles through `rr` slightly different variants, default 4, so it doesn't machine-gun): `kitkick` (tune 50-65, decay 0.15-0.4, beater 0-1 felt to plastic click, shell, drive), `kitsnare` (tune 170-260, wires 0-1, rim 0-1 rimshot crack, decay = wire ring, body, drive; soft hits get darker), `kittom` (tune ~150-200 rack, 80-100 floor; decay 0.3-0.8), `kithat` (open 0 closed, ~0.4 half-open sizzle, 0.7-1 open; pedal true = foot chick; decay, tone, tune), `kitride` (decay 2-5, bell 0-1), `kitcrash` (decay 1.5-3.5, tone <1 darker >1 brighter; the old `crash` is a thin hiss above 4 kHz). Use one track per articulation (closed hat, open hat with `"choke_by"`, pedal hat).
- `eguitar` (polyphonic): electric guitar. Each note is a plucked string; the **amp runs on the whole track afterwards**, so chords distort together like a real amp. drive 0-1 (0.7; 0.3-0.5 crunch, 0.7-0.9 rock rhythm), mute 0-1 (palm mute; 0.7-0.9 = chug), dark 0-1 (cabinet darkness, 0.4), scoop 0-1 (mid cut), pickup 0.08-0.25 (bridge bite to neck warmth, 0.1), bright 0-1 (pick), pick_pos, sustain s. Use voicings `power` or `guitar` and stab `strum`. Double-track: two `eguitar` tracks at pan -0.85/0.85 with different drive, dark, pickup or voicings.
- `cleanguitar` (polyphonic, **stereo** after its amp): clean electric guitar (neck pickup) through a clean amp and stereo chorus. chorus 0-1 (0.5), chorus_rate Hz, drive 0-0.3, bright, pickup, mute, sustain. Arpeggios: `"style": "arp", "voicing": "guitar"`.
- `ebass` (polyphonic, play one note at a time): electric bass guitar. pick 0-1 (fingers to pick, 0.7), mute 0-1 (palm mute), drive 0-1 (0.2), tone Hz (amp low-pass, 3500), sustain s. Roots with stabs and `"voicing": "root"`, `register` D2-E2, `legato` 0.9.
- `vox` (monophonic with glide): wordless vocal-like lead ("ooh"/"ah") for the sung melody. An additive voice through a 5-formant vocal tract that stays put while the pitch moves, so glides and vibrato sound sung. voice `soprano` / `alto` (default) / `tenor`, vowel `ah` `eh` `ee` `oh` `oo`, vowel2 + morph s (each note moves from vowel to vowel2), vibrato semitones (0.3), vib_rate (5.3), vib_delay s (0.22), scoop semitones (0.5: singers slide up into a fresh note), glide_ms (90, for `~` notes), breath 0-1 (0.25), bright 0-1 (0.6), ring 0-1 (singer's formant around 2.9 kHz, 0.5), attack, release, sustain_level. Write phrases with breaths (rests) between them; `~` glides; reverb and delay sends.

FX types (in order): `hpf` {hz}, `lpf` {hz}, `eq` {hz, gain_db, q}, `lowshelf`/`highshelf` {hz, gain_db}, `comp` {threshold_db, ratio, attack_ms, release_ms}, `drive` {db}, `sat` {amount}, `bitcrush` {bits}, `srr` {hz}, `lofi` {amount 0-1: wow/flutter, sample-rate, dust}, `chorus` {rate, depth, mix}, `phaser`, `tremolo` {rate, depth}, `delay` {beats, feedback, mix}, `reverb` {size, mix}, `pitch` {semitones}, `width` {amount}, `gain` {db}, `gate` {pattern, bars, depth 0-1, duty 0-1, smooth_ms} (trance gate: a step pattern from bar 1, string length / bars = grid like drum steps; `x`/`X` open, `o` half, `1`-`9` level, `.` closed; each open step stays open for `duty` of the step, e.g. `{"type": "gate", "pattern": "x.xx.xx.x.xx.x.x", "depth": 0.85, "duty": 0.75}`), `room` {size 0-1, mix, damping} (small-room early reflections plus a short tail: put it on each acoustic kit piece so the kit sounds like one room)

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
  style: `sustain`, `strum` (strum_ms), `stabs` (with `"rhythm": "x..x..x...x....."` per bar, `stab_len`; the string length sets the grid like drum steps, so 12 characters = 8th-note triplets), `arp` (`rate` in 16ths, `pattern` up/down/updown/random, `octaves`).
  voicing: `keys` (left-hand root plus right-hand close voicing), `close`, `spread`. Instrument shapes (no voice leading; the lowest note lands within a tritone of `register`): `root` (just the root: bass lines), `octave` (root + octave), `power` (root, fifth, octave: guitar power chord), `guitar` (an open-chord shape: root, fifth, octave, third and any 7th/9th above, up to 6 notes).
  Strumming (guitars): stabs accept `"strum": "down" | "up" | "alt"`, `strum_ms` (time across the strings, default 12) and `strum_grid` (8 or 16: with `alt`, hits on the grid's on-beats strum down, the others up). Up-strokes start on the top string, are lighter, and skip the two lowest strings of big chords. `"style": "strum"` takes `"strum_dir"` the same way.
  Qualities: "", m, maj7, m7, 7, m9, maj9, 9, add9, madd9, 6, m6, sus2, sus4, 7sus4, dim, dim7, m7b5, aug, 7b9, 7#9, m7b9, 11, m11, 13, maj13, 6/9, maj7#11, 7b13, mmaj7, m(maj9), 5
- **Texture**: `"vinyl": "on"`

### SECTION
```json
{"name": "hook1", "bars": 8, "play": ["keysA", "beatB", "bassA"],
 "fill": {"pattern": "fillA"},                       // replaces those tracks in the last bar(s) of the section
 "auto": {"keys": {"lpf": [600, 8000], "hpf": [20, 800], "gain_db": [-6, 0], "mute": false}},   // ramps across the section
 "enter": {"impact": 0.8, "crash": 0.6, "downlifter": 2},                       // on the first downbeat (downlifter in beats)
 "exit":  {"riser": 4, "reverse": 2, "rise": 16,                                // ending exactly at the section end (beats); rise = pitched build riser
           "cut": {"tracks": ["kick", "808"], "beats": 1},                       // drop-out before the next section ("all" for every track)
           "lpf": {"tracks": ["keys"], "beats": 4, "to_hz": 400},
           "tapestop": 2, "silence": 1}}
```
Note: an exit `cut` only silences its own window; 808 and reverb tails can ring on into the next section. For true silence in a section, also add `"auto": {"<track>": {"mute": true}}` there.
Section names must be unique. Bars per section should be multiples of 4 (2 for short breaks).

## Tips from the bench
- Trance: `"swing": 0.5` and `humanize_ms` 0-1 on drums and bass (machine-tight is the style). Sidechain bass, chords and pads to the kick (bass depth 0.8-0.9 / release 80-110 ms, chords 0.5-0.7 / 140-180 ms). A build: snare roll pattern, `"exit": {"rise": 16, "riser": 8, "cut": {"tracks": "all", "beats": 1}}` and `auto` `hpf` sweeps on the music. The breakdown has no kick: leave the kick's pattern out (a muted pattern still sends sidechain triggers).
- Pop rock: `humanize_ms` 4-8 on kit pieces, `push_ms` +3..+6 on the snare for a laid-back backbeat, `room` on kit pieces plus a shared reverb send. Guitars and bass are thin at 100-300 Hz: add body with `eq`/`lowshelf` there before mastering (the measured rock target expects +5 to +7 dB at 100-250 Hz relative to 1 kHz). Kick and bass guitar want different homes (kick body 60-80 Hz with `eq`, bass growl 150-250 Hz).
- Melodic and pad instruments sit far below drums by default; raise `gain_db` in steps of 2-3 dB.
- Hats live and die by `dyn`, `humanize_ms`, swing and rolls. The 808 should almost always sidechain to the kick or follow it.
- High-pass melodic tracks (`hpf` 120-200) so the 808 owns the low end.
- `lofi` plus `send_reverb` on keys gives the "sampled record" feel; `width` 0.3-0.7 on pads and keys opens the stereo field (the default is quite mono).
- For per-section track levels, read `stems_rms` in `renders/vNNN.meta.json` (one RMS value per 0.05 s per track); see `sessions/004-hustle/levels.py` or `sessions/005-fuck-war/stems.py`.
- The ears' "no contrast" warning only compares loudness, band levels and onset density; a purely rhythmic or textural change between sections can trip it. Check with a zoom before acting on it.
- The key detector reads modal material (Dorian, Romanian minor, Hijaz) as the nearest major/minor key; trust your own mode. In the zoom timing roll, row labels can look shifted by one track when several drum tracks share a hit; identify rows by their timing.
- `gain_db` acts before the track's fx: on tracks with heavy drive, saturation flattens the change; use a `gain` fx at the end of the chain to change the post-drive level.
- A render is about 20 s; an overview listen about 25 s. Zoom listens are faster. Projects with many acoustic cymbals or long distorted guitar parts render slower (the first cymbal hits are costly; later ones are cached).
