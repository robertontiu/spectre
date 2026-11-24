#!/bin/bash
# wait until no other python process is using real CPU (other sessions' renders, masters, voice builds)
while ps -eo pid,pcpu,comm,args | awk '$3 ~ /python/ && $2 > 40' | grep -v "wq.py" | grep -q .; do sleep 6; done
