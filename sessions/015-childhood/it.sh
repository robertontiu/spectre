#!/bin/bash
# it.sh [loop|full] [listen args...] : build, render, overview listen
cd /home/claude/spectre/sessions/015-childhood
python3 build.py $1 > /dev/null || exit 1
shift
./r.sh render 2>&1 | grep -v "^tempo\|^sections" | tail -4
./r.sh listen "$@" 2>&1 | cut -c1-330
