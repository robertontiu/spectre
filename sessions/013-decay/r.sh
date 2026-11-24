#!/bin/bash
# r.sh : wait for other heavy jobs, then run studio.py with the args
cd /home/claude/spectre/sessions/013-decay && export BEAT_DIR=$PWD
echo 1000 > /proc/self/oom_score_adj
while pgrep -af "python3 .*studio.py" | grep -v "013-decay" | grep -q studio.py; do sleep 10; done
while ps -eo pcpu,args | awk '$1>40 && /python3/ && /(studio|blend|master)/' | grep -q python3; do sleep 10; done
python3 /home/claude/spectre/engine/studio.py "$@"
