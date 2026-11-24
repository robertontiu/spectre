#!/bin/bash
# lm.sh vNNN: run lomaster.py when the shared 6 GiB sandbox has room; retry if OOM-killed
cd /home/claude/spectre/sessions/007-ecstasy
CG=$(ls -d /sys/fs/cgroup/memory/process_api/*/claude-code-bash | head -1)
for i in $(seq 1 6); do
  while [ $(awk "/^total_rss /{print \$2}" $CG/memory.stat) -gt 2200000000 ]; do sleep 3; done
  python3 lomaster.py "$@" > m.txt 2>&1 && { grep -E "IN |OUT|tonal|NOTE|largest|WARN|limiter|glue|tp_guard" m.txt; exit 0; }
  echo "attempt $i failed: $(tail -1 m.txt)"; sleep 8
done
