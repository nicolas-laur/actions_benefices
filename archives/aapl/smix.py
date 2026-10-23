import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; D=2.8; DUR=D*3+0.3; N=int(DUR*SR)+SR; rng=np.random.default_rng(1)
def tt(n): return np.arange(n)/SR
def mtof(m): return 440*2**((m-69)/12)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def add(b,x,t0,g=1):
    i=int(t0*SR); j=min(len(b),i+len(x)); b[i:j]+=g*x[:j-i]
def piano(m,dur=3,v=.5):
    n=int(dur*SR); t=tt(n); f=mtof(m); s=sum(a*np.sin(2*np.pi*f*h*t)*np.exp(-t*d) for h,a,d in [(1,1,1.2),(2,.4,2),(3,.15,3.5)])
    return lp(s*np.minimum(1,t/.005),2500)*v
L=np.zeros(N); R=np.zeros(N)
CH=[(48,[64,67,71,74]),(45,[64,67,72,76]),(41,[60,65,69,72])]   # Cmaj9, Am, F
for i,(r,ch) in enumerate(CH):
    t0=i*D
    add(L,piano(r-12,4,.6),t0); add(R,piano(r-12,4,.6),t0)
    for k,m in enumerate(ch): add(L if k%2 else R,piano(m,3.5,.28),t0+0.05+k*0.18)
    n=int(D*SR); t=tt(n); pad=sum(np.sin(2*np.pi*mtof(m-12)*t*(1+d)) for m in ch for d in (-.002,.002))*np.minimum(1,t/.8)*np.minimum(1,(D-t)/.4)*.03
    add(L,pad,t0); add(R,pad,t0)
    # souffle de transition + impact doux
    n2=int(.6*SR); u=tt(n2)/.6; w=lp(rng.standard_normal(n2),3000)*np.sin(np.pi*u)**2*.05; add(L,w,t0-0.35 if t0>0 else 0); add(R,w,t0-0.33 if t0>0 else 0)
    n3=int(.8*SR); t3=tt(n3); hit=np.sin(2*np.pi*np.cumsum(50+60*np.exp(-t3*20))/SR)*np.exp(-t3*5)*.35; add(L,hit,t0+0.02); add(R,hit,t0+0.02)
st=np.stack([L,R],1)[:int(DUR*SR)]; fade=np.minimum(1,(DUR-np.arange(len(st))/SR)/.4)[:,None]; st*=fade; st=np.tanh(st*1.2); st*=.9/abs(st).max()
wavfile.write('smix.wav',SR,(st*32767).astype(np.int16)); print('ok')
