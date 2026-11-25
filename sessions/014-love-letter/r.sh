#!/bin/bash
# r.sh [loop|full] [listen args]: build, wait for the machine, render, overview listen -> listen.txt
cd /home/claude/spectre/sessions/014-love-letter && export BEAT_DIR=$PWD
echo 1000 > /proc/self/oom_score_adj
MODE=${1:-full}; shift
python3 build.py $MODE || exit 1
./wait.sh; python3 /home/claude/spectre/engine/studio.py render > render.txt 2>&1; tail -12 render.txt
./wait.sh; python3 /home/claude/spectre/engine/studio.py listen "$@" > listen.txt 2>&1; cat listen.txt
