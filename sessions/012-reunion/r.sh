#!/bin/bash
# r.sh: wait for the machine, render project.json, overview listen -> listen.txt
cd /home/claude/spectre/sessions/012-reunion && export BEAT_DIR=$PWD
echo 1000 > /proc/self/oom_score_adj
python3 build.py full >/dev/null; ./wait.sh; python3 /home/claude/spectre/engine/studio.py render 2>&1 | tail -6 > render.txt
./wait.sh; python3 /home/claude/spectre/engine/studio.py listen "$@" > listen.txt 2>&1
echo done >> render.txt
