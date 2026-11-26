#!/bin/bash
# Wait for a free slot before a heavy job, sized to this machine's memory (AGENTS.md rule 7).
#   waitfree.sh render   a render or listen: no master running, fewer than MAX_RENDERS renders running,
#                        and RENDER_MB available
#   waitfree.sh master   a master: no other master and no Whisper, at most MAX_RENDERS-1 renders (so on a
#                        14 GB machine a master may run beside one render, and a busy lane cannot starve it),
#                        and MASTER_MB available
#   waitfree.sh whisper  a Whisper check: no other Whisper and no master running, and WHISPER_MB available
#   waitfree.sh          (no argument) the old rule: nothing heavy running and RENDER_MB available
# MAX_RENDERS defaults from total memory: 2 on a machine with at least 14 GB, else 1 (the old one-at-a-time
# rule of the 8 GB server). Memory figures are the measured peaks plus a margin (AGENTS.md rule 7). Processes are matched by name (real python processes only, so waiting shell wrappers whose
# command lines contain "studio.py" never count); each condition must hold twice, 1 s apart.
# Prints the available memory when it returns, and what it is waiting for every 60 s. Works on Linux and macOS;
# on a machine under about 12 GB the memory margins shrink to 60% of the total (one heavy job at a time).
KIND=${1:-any}
# Memory in MB: Linux (free) or macOS (sysctl, vm_stat); empty when neither works, and the memory check is skipped.
total_mb() {
  if command -v free >/dev/null 2>&1; then free -m | awk '/Mem/{print $2}'
  elif command -v sysctl >/dev/null 2>&1; then echo $(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1048576 ))
  fi
}
avail() {
  if command -v free >/dev/null 2>&1; then free -m | awk '/Mem/{print $7}'
  elif command -v vm_stat >/dev/null 2>&1; then
    vm_stat | awk '/page size of/{ps=$8} /Pages (free|inactive|speculative)/{gsub(/\./,"",$NF); n+=$NF} END{printf "%d\n", n*ps/1048576}'
  fi
}
TOTAL_MB=$(total_mb); TOTAL_MB=${TOTAL_MB:-0}
if [ -z "${MAX_RENDERS:-}" ]; then
  if [ "$TOTAL_MB" -ge 14000 ]; then MAX_RENDERS=2; else MAX_RENDERS=1; fi
fi
RENDER_MB=${RENDER_MB:-${MIN_FREE_MB:-7000}}
MASTER_MB=${MASTER_MB:-7000}
WHISPER_MB=${WHISPER_MB:-5000}
# On a smaller machine (under about 12 GB) the 7 GB margin could never be free: wait for 60% of the total instead,
# so the script cannot wait forever (one heavy job at a time still holds there: MAX_RENDERS is 1).
if [ "$TOTAL_MB" -gt 0 ]; then
  CAP=$(( TOTAL_MB * 60 / 100 ))
  for v in RENDER_MB MASTER_MB WHISPER_MB; do
    if [ "${!v}" -gt "$CAP" ]; then eval "$v=$CAP"; fi
  done
fi
# Real python processes only (the first word of the command line is a python binary), so waiting shell wrappers
# whose command lines contain "studio.py" never count. `ps -eo args=` works on Linux and macOS.
procs() { ps -eo args= 2>/dev/null | awk '{n=$1; sub(/.*\//,"",n)} n ~ /^python[0-9.]*$/' ; }
count() { procs | grep -cE "$1" ; }
renders() { count 'studio\.py (render|listen)' ; }
masters() { count 'studio\.py master|master\.py' ; }
whispers() { count 'whisper' ; }
memok() { local need=$1 a; a=$(avail); [ -z "$a" ] && return 0; [ "$a" -ge "$need" ] ; }
ok() {
  case "$KIND" in
    render)  [ "$(masters)" = 0 ] && [ "$(renders)" -lt "$MAX_RENDERS" ] && memok "$RENDER_MB" ;;
    master)  [ "$(masters)" = 0 ] && [ "$(renders)" -lt "$MAX_RENDERS" ] && [ "$(whispers)" = 0 ] && memok "$MASTER_MB" ;;
    whisper) [ "$(whispers)" = 0 ] && [ "$(masters)" = 0 ] && memok "$WHISPER_MB" ;;
    *)       [ "$(masters)" = 0 ] && [ "$(renders)" = 0 ] && memok "$RENDER_MB" ;;
  esac
}
WAITED=0
while true; do
  if ok; then sleep 1; ok && break; fi
  sleep 1; WAITED=$((WAITED + 1))
  if [ $((WAITED % 60)) = 0 ]; then
    echo "waitfree: still waiting ($KIND) after ${WAITED} s: renders $(renders), masters $(masters), whisper $(whispers), available MB $(avail)" >&2
  fi
done
echo "available MB $(avail)"
