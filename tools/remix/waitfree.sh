#!/bin/bash
# Wait for a free slot before a heavy job, sized to this machine's memory (AGENTS.md rule 7).
#   waitfree.sh render   a render or listen: no master running, fewer than MAX_RENDERS renders running,
#                        and RENDER_MB available
#   waitfree.sh master   a master: nothing else heavy running (no render, listen, master or Whisper),
#                        and MASTER_MB available
#   waitfree.sh whisper  a Whisper check: no other Whisper and no master running, and WHISPER_MB available
#   waitfree.sh          (no argument) the old rule: nothing heavy running and RENDER_MB available
# MAX_RENDERS defaults from total memory: 2 on a machine with at least 14 GB, else 1 (the old one-at-a-time
# rule of the 8 GB server). Memory figures are the measured peaks plus a margin (AGENTS.md rule 7). Processes are matched by name (real python processes only, so waiting shell wrappers whose
# command lines contain "studio.py" never count); each condition must hold twice, 1 s apart.
# Prints the available memory when it returns.
KIND=${1:-any}
TOTAL_MB=$(free -m | awk '/Mem/{print $2}')
if [ -z "${MAX_RENDERS:-}" ]; then
  if [ "$TOTAL_MB" -ge 14000 ]; then MAX_RENDERS=2; else MAX_RENDERS=1; fi
fi
RENDER_MB=${RENDER_MB:-${MIN_FREE_MB:-7000}}
MASTER_MB=${MASTER_MB:-7000}
WHISPER_MB=${WHISPER_MB:-5000}
procs() { ps -C python3,python,python3.11,python3.12,python3.13 -o args= 2>/dev/null ; }
count() { procs | grep -cE "$1" ; }
renders() { count 'studio\.py (render|listen)' ; }
masters() { count 'studio\.py master|master\.py' ; }
whispers() { count 'whisper' ; }
avail() { free -m | awk '/Mem/{print $7}' ; }
ok() {
  case "$KIND" in
    render)  [ "$(masters)" = 0 ] && [ "$(renders)" -lt "$MAX_RENDERS" ] && [ "$(avail)" -ge "$RENDER_MB" ] ;;
    master)  [ "$(masters)" = 0 ] && [ "$(renders)" = 0 ] && [ "$(whispers)" = 0 ] && [ "$(avail)" -ge "$MASTER_MB" ] ;;
    whisper) [ "$(whispers)" = 0 ] && [ "$(masters)" = 0 ] && [ "$(avail)" -ge "$WHISPER_MB" ] ;;
    *)       [ "$(masters)" = 0 ] && [ "$(renders)" = 0 ] && [ "$(avail)" -ge "$RENDER_MB" ] ;;
  esac
}
while true; do
  if ok; then sleep 1; ok && break; fi
  sleep 1
done
echo "available MB $(avail)"
