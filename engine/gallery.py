import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, instruments as I, librosa, librosa.display, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
items=[]
for k,f in I.DRUMS.items(): items.append((k, f({},0.9,0)))
for k,f in I.TONAL.items(): items.append((k, f({},220.0,0.8,1.0)))
items.append(('808', I.mono_voice('808',{},[dict(t0=0,n=30000,f=55,vel=.9,glide=False),dict(t0=30000,n=30000,f=82,vel=.9,glide=True)],90000)))
items.append(('bass', I.mono_voice('bass',{},[dict(t0=0,n=30000,f=55,vel=.9,glide=False)],50000)))
items.append(('lead', I.mono_voice('lead',{},[dict(t0=0,n=40000,f=440,vel=.9,glide=False)],60000)))
fig,axs=plt.subplots(5,5,figsize=(18,14)); axs=axs.ravel()
for ax,(k,x) in zip(axs,items):
    x=np.asarray(x,dtype=np.float32)[:int(2.0*44100)]
    M=librosa.feature.melspectrogram(y=x,sr=44100,n_fft=2048,hop_length=256,n_mels=128,fmax=18000)
    librosa.display.specshow(librosa.power_to_db(M+1e-10,ref=np.max),sr=44100,hop_length=256,y_axis='mel',x_axis='time',fmax=18000,ax=ax,cmap='magma')
    ax.set_title(f'{k} peak={np.abs(x).max():.2f}',fontsize=9); ax.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig('gallery.png',dpi=60)
