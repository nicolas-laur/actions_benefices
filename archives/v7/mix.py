import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import premium as P
SR = 48000; DUR = P.DUR; N = int((DUR+1)*SR)
rng = np.random.default_rng(4)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def mtof(m): return 440*2**((m-69)/12)
def add(buf, x, t0, g=1.0):
    i = int(round(t0*SR))
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i+len(x)); buf[i:j] += g*x[:j-i]
# musique : nappe chaude + pulsation douce + arpège cristallin, 112 BPM
BEAT = 60/112; BAR = 4*BEAT
CH = [(45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
padL, padR, bass, kick, hat, arp = (np.zeros(N) for _ in range(6))
for b in range(int(DUR/BAR)+1):
    t0 = b*BAR; root, notes = CH[b % 4]; n = int((BAR+1.0)*SR); t = tt(n)
    env = np.minimum(1, t/0.6)*np.clip((BAR+1.0-t)/1.0, 0, 1)
    for m in notes:
        for buf, dt in ((padL, 0.997), (padR, 1.003)):
            add(buf, (np.sin(2*np.pi*mtof(m)*dt*t)+0.15*np.sin(4*np.pi*mtof(m)*dt*t))*env*0.07, t0)
    for q in range(4):
        tq = t0+q*BEAT; nb = int(0.5*SR); tb = tt(nb)
        add(bass, np.sin(2*np.pi*mtof(root)*tb)*np.exp(-tb*4)*np.minimum(1, tb/0.01)*0.5, tq)
        nk = int(0.25*SR); tk = tt(nk); add(kick, np.sin(2*np.pi*np.cumsum(48+70*np.exp(-tk*40))/SR)*np.exp(-tk*12), tq)
        nh = int(0.04*SR); th = tt(nh); add(hat, hp(rng.standard_normal(nh), 9000)*np.exp(-th*90), tq+BEAT/2)
    for k in range(8):
        m = notes[[0, 2, 3, 1, 2, 3, 1, 0][k]]+24; na = int(0.5*SR); ta = tt(na)
        add(arp, np.sin(2*np.pi*mtof(m)*ta)*np.exp(-ta*7)*np.minimum(1, ta/0.004)*0.12, t0+k*BEAT/2)
def gate(segs):
    pts = [(0, 0)]
    for a, b, g in segs: pts += [(a, 0), (a+0.3, g), (b-0.3, g), (b, 0)]
    pts.append((DUR+1, 0)); pts.sort(); return np.interp(tt(N), [p[0] for p in pts], [p[1] for p in pts])
g_k = gate([(2.6, 15.6, 0.7)]); g_h = gate([(5.6, 15.6, 0.5)]); g_b = gate([(0.3, 15.8, 0.9)]); g_a = gate([(0.2, 15.9, 1)])
mono = lp(bass, 500)*g_b+kick*g_k*0.8+hat*g_h*0.35+lp(arp, 7000)*g_a
fade = np.interp(tt(N), [0, 0.4, DUR-0.8, DUR, DUR+1], [0, 1, 1, 0, 0])
musL, musR = (lp(padL, 2500)+mono)*fade, (lp(padR, 2500)+mono)*fade
pk = max(abs(musL).max(), abs(musR).max()); musL *= 0.5/pk; musR *= 0.5/pk
# design sonore discret, synchronisé sur chaque mouvement
def whoosh():
    n = int(0.55*SR); t = tt(n); x = rng.standard_normal(n); u = t/t[-1]
    return (lp(x, 700)*(1-u)+hp(lp(x, 5000), 1200)*u)*np.sin(np.pi*u)**2*0.14
def shimmer():
    n = int(1.2*SR); t = tt(n); s = sum(np.sin(2*np.pi*f*t)*np.exp(-t*(3+i)) for i, f in enumerate([1760, 2637, 3520]))
    return s*np.minimum(1, t/0.08)*0.05
def click():
    n = int(0.05*SR); t = tt(n); return (np.sin(2*np.pi*1900*t)+0.4*hp(rng.standard_normal(n), 4000))*np.exp(-t*90)*0.12
def tick(): n = int(0.03*SR); t = tt(n); return np.sin(2*np.pi*2600*t)*np.exp(-t*160)*0.08
def line():
    n = int(0.6*SR); t = tt(n); return bp(rng.standard_normal(n), 3000, 7000)*np.sin(np.pi*t/t[-1])*0.04
def fill(i):
    n = int(0.45*SR); t = tt(n); f = 300*2**(i*2/12)+250*t/t[-1]
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/t[-1])*0.09
def segs(i):
    n = int(0.18*SR); t = tt(n); return np.sin(2*np.pi*(880*2**(i/12))*t)*np.exp(-t*30)*0.09
def chime(f0=1318.5, g=0.16):
    n = int(1.6*SR); t = tt(n)
    return sum(a*np.sin(2*np.pi*f0*h*t)*np.exp(-t*d) for h, a, d in [(1, 1, 2.5), (2, .3, 4), (3.01, .12, 7)])*np.minimum(1, t/0.004)*g
def gift():
    s = np.zeros(int(1.8*SR)); add(s, chime(1568, 0.14), 0); add(s, chime(2093, 0.12), 0.08); add(s, shimmer(), 0.02); return s
def count(k): n = int(0.03*SR); t = tt(n); return np.sin(2*np.pi*(1500+k*60)*t)*np.exp(-t*150)*0.06
MAP = {'whoosh': whoosh, 'shimmer': shimmer, 'click': click, 'tick': tick, 'line': line, 'chime': chime, 'gift': gift}
fx = np.zeros(N)
for e in P.EVENTS:
    t0, kind = e[0], e[1]
    x = fill(e[2]) if kind == 'fill' else segs(e[2]) if kind == 'seg' else count(e[2]) if kind == 'count' else MAP[kind]()
    add(fx, x, t0-(0.3 if kind == 'whoosh' else 0))
d = int(0.12*SR); fxL, fxR = fx.copy(), fx.copy(); fxL[d:] += 0.22*fx[:-d]; fxR[2*d:] += 0.16*fx[:-2*d]
st = np.stack([musL+fxL, musR+fxR], 1)[:int(DUR*SR)]; st = np.tanh(st*1.1)/np.tanh(1.1); st *= 0.95/abs(st).max()
wavfile.write('mix.wav', SR, (st*32767).astype(np.int16)); print('ok')
