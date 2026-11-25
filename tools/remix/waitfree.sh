#!/bin/bash
# Wait until no other lane renders or masters and memory is free: no real python process (by process name, so
# waiting shell wrappers whose command lines contain "studio.py" never count) runs studio.py or master.py, and
# `free -m` shows at least $MIN_FREE_MB available (default 3000), both confirmed twice 1 s apart.
# usage: waitfree.sh            (prints the available memory when it returns)
MIN=${MIN_FREE_MB:-3000}
busy() { ps -C python3,python,python3.11,python3.12,python3.13 -o args= 2>/dev/null | grep -cE '(studio|master)\.py' ; }
avail() { free -m | awk '/Mem/{print $7}' ; }
ok() { [ "$(busy)" = "0" ] && [ "$(avail)" -ge "$MIN" ] ; }
while true; do
  if ok; then sleep 1; ok && break; fi
  sleep 1
done
echo "available MB $(avail)"
