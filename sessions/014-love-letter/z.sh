#!/bin/bash
# z.sh <listen args>: a zoom or other listen, output to zoom.txt
cd /home/claude/spectre/sessions/014-love-letter && export BEAT_DIR=$PWD
echo 1000 > /proc/self/oom_score_adj
./wait.sh; python3 /home/claude/spectre/engine/studio.py listen "$@" > zoom.txt 2>&1; cat zoom.txt
