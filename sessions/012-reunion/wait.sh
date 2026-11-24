#!/bin/bash
# wait until no other engine job (a python process running studio/blend/master) is active
while pgrep -a -x python3 | grep -E "studio|blend|master" >/dev/null; do sleep 5; done
