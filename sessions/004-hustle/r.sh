#!/bin/bash
# render + overview listen (or zoom with args): bash r.sh [listen args...]
cd /home/claude/spectre/sessions/004-hustle && export BEAT_DIR=$PWD
python3 build.py >/dev/null
V=$(python3 /home/claude/spectre/engine/studio.py render 2>&1 | grep -o 'v[0-9]*\.wav' | head -1)
echo "rendered $V"
python3 /home/claude/spectre/engine/studio.py listen --wav renders/$V "$@" > listen.txt 2>&1; cat listen.txt
