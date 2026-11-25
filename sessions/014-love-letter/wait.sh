#!/bin/bash
# wait until no other engine render/master (python3 ... studio.py) is running and at least 2.5 GB RAM is available
while pgrep -a -x python3 | grep -E "studio\.py" >/dev/null || [ $(free -m | awk 'NR==2{print $7}') -lt 2500 ]; do sleep 5; done
