#!/bin/bash
# Stage 1, remaster: re-render the published project unchanged as a new version, check its events against the
# published render, master it twice (--genre trap, kept in scratch; --genre hiphop, kept in renders/), read both and
# the published master in Bark bands against the catalogue, then run `listen --clarity --genre hiphop`.
# usage: stage1.sh <session dir> <published vNNN> [extra master flags, e.g. the published master's --lufs/--eq]
# scratch (logs, the trap master, clarity text): $REMIX_SCRATCH, default /tmp/remix-scratch/<session>
set -e
T=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$T/../.." && pwd)
cd "$1"; export BEAT_DIR=$PWD; pub=$2; shift 2
echo 1000 > /proc/self/oom_score_adj
S=${REMIX_SCRATCH:-/tmp/remix-scratch/$(basename "$PWD")}; mkdir -p "$S"
cmp <(python3 -m json.tool project.json) <(python3 -m json.tool renders/$pub.project.json) && echo "project.json = $pub"
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" render 2>&1 | grep rendered
v=$(python3 -c "import json,os;print(os.path.basename(json.load(open('renders/latest.json'))['wav'])[:4])")
python3 "$T/evcmp.py" renders/$pub.meta.json renders/$v.meta.json
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" master $v --genre trap "$@" > "$S/$v.trap.log" 2>&1
for f in renders/$v.master.*; do mv "$f" "$S/trap.$(basename "$f")"; done
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" master $v --genre hiphop "$@" > "$S/$v.hiphop.log" 2>&1
python3 "$T/barkcmp.py" *-mastered.mp3 "$S/trap.$v.master.mp3" renders/$v.master.mp3
grep -E "^OUT|tonal EQ moves|NOTE: tonal" "$S/$v.trap.log" "$S/$v.hiphop.log" || true
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" listen --clarity --genre hiphop 2>&1 | tee "$S/clarity_$v.txt"
