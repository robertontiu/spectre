import sys, threading, time, os, traceback
sys.argv=['x']; sys.path.insert(0,'/home/claude/spectre/sessions/007-ecstasy')
import lomaster as L
peak=[0,'']; main_id=threading.get_ident()
def samp():
    while True:
        r=int(open('/proc/self/statm').read().split()[1])*4096
        f=sys._current_frames()[main_id]; st=traceback.extract_stack(f); lab=" < ".join(f"{s.name}:{s.lineno}" for s in st[-3:])
        if lab!=peak[1] or r>peak[0]*1.1: print(round(r/1e9,2), lab, flush=True); peak[1]=lab
        if r>peak[0]:
            f=sys._current_frames()[main_id]; st=traceback.extract_stack(f)
            peak[0]=r; peak[1]=' < '.join(f"{s.name}:{s.lineno}" for s in st[-4:])
        time.sleep(0.05)
threading.Thread(target=samp,daemon=True).start()
sys.argv=['master.py','/home/claude/spectre/sessions/007-ecstasy/scratch/p.premaster.wav','--genre','trance']
L.run(sys.argv[1])
print('PEAK', peak[0]/1e9, peak[1])
