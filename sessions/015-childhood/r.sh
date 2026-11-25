#!/bin/bash
# r.sh : wait for other heavy jobs, then run studio.py with the args
cd /home/claude/spectre/sessions/015-childhood && export BEAT_DIR=$PWD
echo 1000 > /proc/self/oom_score_adj
while pgrep -af "python3 .*studio.py" | grep -v "015-childhood" | grep -q studio.py; do sleep 8; done
while ps -eo pcpu,args | awk '$1>40 && /python3/ && /(studio|blend|master)/' | grep -q python3; do sleep 8; done
python3 /home/claude/spectre/engine/studio.py "$@"
