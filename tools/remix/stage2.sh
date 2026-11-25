#!/bin/bash
# Stage 2, one remix move: render the edited project.json, check its events against the published render, run
# `listen --clarity --genre hiphop` on one section, master with --genre hiphop (skip with NOMASTER=1).
# usage: stage2.sh <session dir> <published vNNN> <section[,section]> [extra master flags]
# then: deliver.py <session dir> <published mp3> <vNNN> <section> --contour-only   (the section contour)
set -e
T=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$T/../.." && pwd)
cd "$1"; export BEAT_DIR=$PWD; pub=$2; sec=$3; shift 3
echo 1000 > /proc/self/oom_score_adj
S=${REMIX_SCRATCH:-/tmp/remix-scratch/$(basename "$PWD")}; mkdir -p "$S"
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" render 2>&1 | grep rendered
v=$(python3 -c "import json,os;print(os.path.basename(json.load(open('renders/latest.json'))['wav'])[:4])")
python3 "$T/evcmp.py" renders/$pub.meta.json renders/$v.meta.json
"$T/waitfree.sh"
python3 "$REPO/engine/studio.py" listen --clarity --genre hiphop --section $sec > "$S/clarity_$v.txt" 2>&1
grep -vE "^crest|^stem|^region|^CLARITY|^wrote|^$" "$S/clarity_$v.txt" || true
if [ "$NOMASTER" != "1" ]; then
  "$T/waitfree.sh"
  python3 "$REPO/engine/studio.py" master $v --genre hiphop "$@" > "$S/$v.hiphop.log" 2>&1
  grep -E "^OUT|tonal EQ moves|NOTE: tonal|top end|PHONE out|WARN" "$S/$v.hiphop.log" || true
fi
