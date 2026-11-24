#!/bin/bash
# build, render, overview listen
cd /home/claude/spectre/sessions/006-revolution && export BEAT_DIR=$PWD
python3 build.py && python3 /home/claude/spectre/engine/studio.py render 2>&1 | tail -4 && python3 /home/claude/spectre/engine/studio.py listen "$@" > listen.txt 2>&1; cat listen.txt
