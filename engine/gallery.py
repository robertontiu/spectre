import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, instruments as I, librosa, librosa.display, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
items=[]
for k,f in I.DRUMS.items(): items.append((k, f({},0.9,0)))
for k,f in I.TONAL.items():
    x = np.asarray(f({},220.0,0.8,1.0))
    post = getattr(I, 'POST', {}).get(k)
    if post is not None: x = post({}, x)
    items.append((k, x))
items.append(('808', I.mono_voice('808',{},[dict(t0=0,n=30000,f=55,vel=.9,glide=False),dict(t0=30000,n=30000,f=82,vel=.9,glide=True)],90000)))
items.append(('bass', I.mono_voice('bass',{},[dict(t0=0,n=30000,f=55,vel=.9,glide=False)],50000)))
items.append(('lead', I.mono_voice('lead',{},[dict(t0=0,n=40000,f=440,vel=.9,glide=False)],60000)))
items.append(('vox', I.mono_voice('vox',{},[dict(t0=0,n=40000,f=440,vel=.9,glide=False),dict(t0=40000,n=40000,f=523,vel=.9,glide=True)],90000)))
items.append(('acid', I.mono_voice('acid',{},[dict(t0=0,n=5000,f=55,vel=.9,glide=False,acc=True),dict(t0=11000,n=5000,f=110,vel=.9,glide=False),dict(t0=22000,n=11000,f=82.4,vel=.9,glide=True)],60000)))
cols=6; rows=int(np.ceil(len(items)/cols))
fig,axs=plt.subplots(rows,cols,figsize=(21,2.9*rows)); axs=axs.ravel()
for ax,(k,x) in zip(axs,items):
    x=np.asarray(x,dtype=np.float32)
    if x.ndim==2: x=x.mean(0)  # stereo instruments (supersaw, cleanguitar)
    x=x[:int(2.0*44100)]
    M=librosa.feature.melspectrogram(y=x,sr=44100,n_fft=2048,hop_length=256,n_mels=128,fmax=18000)
    librosa.display.specshow(librosa.power_to_db(M+1e-10,ref=np.max),sr=44100,hop_length=256,y_axis='mel',x_axis='time',fmax=18000,ax=ax,cmap='magma')
    ax.set_title(f'{k} peak={np.abs(x).max():.2f}',fontsize=9); ax.tick_params(labelsize=6)
for ax in axs[len(items):]: ax.axis('off')
fig.tight_layout(); fig.savefig('gallery.png',dpi=60)
