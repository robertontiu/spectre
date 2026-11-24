#!/bin/bash
# wait until no other heavy engine job is running (a python render/master/build using CPU)
busy() { for pid in $(pgrep -f "^(/usr/local/bin/)?python3? .*(studio.py (render|master)|master.py|blend.py|build.py|voices.py)"); do
  c=$(ps -o %cpu= -p $pid 2>/dev/null | cut -d. -f1); [ -n "$c" ] && [ "$c" -gt 5 ] && return 0; done; return 1; }
while busy; do sleep 10; done
