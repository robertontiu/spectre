#!/bin/bash
# mst.sh vNNN: run the trance master, waiting for memory (another session shares this machine); retries if killed
cd /home/claude/spectre/sessions/007-ecstasy && export BEAT_DIR=$PWD
for i in 1 2 3 4 5 6 7 8; do
  while pgrep -f "engine/master.py" >/dev/null || [ $(free -m | awk '/Mem:/{print $7}') -lt 6000 ]; do sleep 4; done
  python3 ../../engine/studio.py master $1 --genre trance > m.txt 2>&1 && { grep -E "IN |OUT|tonal|NOTE|largest|WARN|limiter|glue|tp_guard" m.txt; exit 0; }
  echo "attempt $i killed"; sleep 10
done
