"""Bande son LVMH : piano feutré + nappe, 88 BPM, bruitages cristallins synchronisés sur les événements de lvmh.py."""
import sys
sys.argv = ['x', 'info']
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import lvmh as V
SR = 48000; DUR = V.DUR; N = int((DUR+1.5)*SR)
rng = np.random.default_rng(7)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def mtof(m): return 440*2**((m-69)/12)
def add(buf, x, t0, g=1.0):
    i = int(round(t0*SR))
    if i < 0: x = x[-i:]; i = 0
    if i >= len(buf): return
    j = min(len(buf), i+len(x)); buf[i:j] += g*x[:j-i]

# ---------- musique ----------
BEAT = 60/88; BAR = 4*BEAT
LIGHT = [(50, [62, 66, 69, 73, 76]), (47, [59, 62, 66, 69, 74]), (43, [55, 59, 62, 66, 71]), (45, [57, 62, 64, 69, 73])]
DARK = [(47, [59, 62, 66, 71, 74]), (43, [55, 59, 62, 67, 71]), (40, [52, 55, 59, 62, 67]), (42, [54, 58, 61, 66, 70])]
dark_a, dark_b = V.T('c18')-0.3, V.T('c22')-0.3       # passage mineur pendant la chute
def piano(m, dur=2.4, vel=0.5):
    n = int(dur*SR); t = tt(n); f = mtof(m)
    s = sum(a*np.sin(2*np.pi*f*h*(1+0.0004*h*h)*t)*np.exp(-t*d*(1+m/90)) for h, a, d in [(1, 1, 1.1), (2, .45, 2.0), (3, .2, 3.2), (4, .08, 4.5)])
    s *= np.minimum(1, t/0.006)*np.clip((dur-t)/0.3, 0, 1)
    return lp(s, 1600+vel*1800)*vel
pianoL, pianoR, padL, padR, bass, brush = (np.zeros(N) for _ in range(6))
PAT = [(0, 0, .55), (1, 1, .32), (1.5, 2, .30), (2, 3, .38), (3, 4, .30), (3.5, 2, .26)]
for b in range(int(DUR/BAR)+2):
    t0 = b*BAR; dark = dark_a <= t0 < dark_b
    root, notes = (DARK if dark else LIGHT)[b % 4]; n = int((BAR+1.2)*SR); t = tt(n)
    env = np.minimum(1, t/0.9)*np.clip((BAR+1.2-t)/1.2, 0, 1)
    for m in notes[:4]:
        for buf, dt in ((padL, 0.996), (padR, 1.004)):
            add(buf, (np.sin(2*np.pi*mtof(m-12)*dt*t)+0.2*np.sin(4*np.pi*mtof(m-12)*dt*t))*env*0.05, t0)
    add(bass, piano(root, 3.2, 0.6), t0); add(bass, piano(root+7, 2.0, 0.25), t0+2*BEAT)
    for beat, k, vel in PAT:
        x = piano(notes[k]+12 if k in (3, 4) and b % 2 else notes[k], 2.2, vel*(0.9+0.2*rng.random()))
        pan = 0.35*np.sin(k)
        add(pianoL, x*(1-pan), t0+beat*BEAT+rng.uniform(0, 0.012)); add(pianoR, x*(1+pan), t0+beat*BEAT+rng.uniform(0, 0.012))
    for q in range(8):
        nb = int(0.12*SR); th = tt(nb); add(brush, bp(rng.standard_normal(nb), 2500, 8000)*np.exp(-th*35)*(0.5 if q % 2 else 0.3), t0+q*BEAT/2)
def gate(segs):
    pts = [(0, 0)]
    for a, b, g in segs: pts += [(a, 0), (a+0.6, g), (b-0.6, g), (b, 0)]
    pts.append((DUR+1.5, 0)); pts.sort(); return np.interp(tt(N), [p[0] for p in pts], [p[1] for p in pts])
g_br = gate([(V.T('c04'), V.T('c17'), 0.6), (V.T('c22'), V.T('c26'), 0.7)])
g_ba = gate([(0.2, DUR+0.5, 0.9)])
def verb(x, taps=((0.031, .35), (0.047, .3), (0.071, .25), (0.113, .2), (0.167, .15), (0.241, .1))):
    y = x.copy()
    for d, g in taps: k = int(d*SR); y[k:] += g*x[:-k]
    return y
fade = np.interp(tt(N), [0, 0.6, DUR-0.9, DUR, DUR+1.5], [0, 1, 1, 0, 0])
musL = (verb(pianoL)+lp(padL, 1800)+lp(bass, 900)*g_ba+brush*g_br*0.25)*fade
musR = (verb(pianoR, ((0.037, .33), (0.053, .3), (0.083, .24), (0.127, .18), (0.181, .14), (0.263, .1)))+lp(padR, 1800)+lp(bass, 900)*g_ba+brush*g_br*0.22)*fade
pk = max(abs(musL).max(), abs(musR).max()); musL *= 0.5/pk; musR *= 0.5/pk

# ---------- bruitages ----------
def whoosh():   # soie qui glisse
    n = int(0.6*SR); t = tt(n); x = rng.standard_normal(n); u = t/t[-1]
    return (lp(x, 600)*(1-u)+bp(x, 1500, 6000)*u*0.6)*np.sin(np.pi*u)**2*0.11
def shimmer():
    n = int(1.6*SR); t = tt(n)
    s = sum(np.sin(2*np.pi*f*t)*np.exp(-t*(2.2+i)) for i, f in enumerate([1760, 2637, 3520, 4186]))
    return s*np.minimum(1, t/0.1)*0.04
def click():
    n = int(0.06*SR); t = tt(n); return (np.sin(2*np.pi*1200*t)*0.7+0.3*bp(rng.standard_normal(n), 2000, 6000))*np.exp(-t*80)*0.09
def bell(f0, g=0.12, dur=2.0, dec=2.2):
    n = int(dur*SR); t = tt(n)
    return sum(a*np.sin(2*np.pi*f0*h*t)*np.exp(-t*dec*d) for h, a, d in [(1, 1, 1), (2.76, .35, 1.8), (5.4, .12, 3), (8.93, .05, 4.5)])*np.minimum(1, t/0.003)*g
PENTA = [74, 76, 78, 81, 83, 86, 88, 90, 93, 95, 98]
def ting(i): return bell(mtof(PENTA[i % len(PENTA)]), 0.045, 1.2, 3.0)
def chime(): s = np.zeros(int(2.2*SR)); add(s, bell(mtof(86), 0.09), 0); add(s, bell(mtof(93), 0.07), 0.07); return s
def node(i): return bell(mtof([62, 66, 69, 74, 78][i % 5]), 0.1, 2.2, 1.6)
def orbit():
    n = int(1.1*SR); t = tt(n); u = t/t[-1]; f = 2400+2600*u
    return bp(rng.standard_normal(n), 2000, 9000)*np.sin(np.pi*u)**2*0.035+np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*u)**3*0.012
def thud():
    n = int(0.9*SR); t = tt(n); return lp(np.sin(2*np.pi*np.cumsum(55+40*np.exp(-t*12))/SR)*np.exp(-t*5), 400)*0.35
def seal():     # cachet de cire : coup sourd + papier
    n = int(0.5*SR); t = tt(n)
    return (np.sin(2*np.pi*np.cumsum(90+120*np.exp(-t*30))/SR)*np.exp(-t*14)*0.3+bp(rng.standard_normal(n), 800, 4000)*np.exp(-t*40)*0.06)
def roll():
    s = np.zeros(int(1.4*SR)); k = 0; tk = 0.0
    while tk < 1.2:
        n = int(0.025*SR); t = tt(n); add(s, np.sin(2*np.pi*(1600+k*25)*t)*np.exp(-t*170)*0.04, tk); k += 1; tk += 0.035+0.06*(tk/1.2)**2
    return s
def stop(): return bell(mtof(81), 0.06, 1.4, 2.5)
def swell():
    n = int(1.4*SR); t = tt(n); u = t/t[-1]; return bp(rng.standard_normal(n), 400, 5000)*u**2*np.exp(-np.maximum(0, t-1.2)*30)*0.05
def rise():
    n = int(1.5*SR); t = tt(n); u = t/t[-1]; f = 500*2**(1.2*u)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*u)*0.05+bp(rng.standard_normal(n), 3000, 8000)*u*np.sin(np.pi*u)*0.02
def sweep():    # reflet sur l'or
    n = int(1.0*SR); t = tt(n); u = t/t[-1]
    return sum(np.sin(2*np.pi*f*t)*np.sin(np.pi*u)**2 for f in (3136, 4186, 5274))*0.012
MAP = dict(whoosh=whoosh, shimmer=shimmer, click=click, chime=chime, orbit=orbit, thud=thud, seal=seal, roll=roll, stop=stop,
           swell=swell, rise=rise, sweep=sweep)
fx = np.zeros(N)
for e in V.events():
    t0, kind = e[0], e[1]
    x = ting(e[2]) if kind == 'ting' else node(e[2]) if kind == 'node' else MAP[kind]()
    add(fx, x, t0-(0.35 if kind == 'whoosh' else 0))
d = int(0.14*SR); fxL, fxR = fx.copy(), fx.copy(); fxL[d:] += 0.25*fx[:-d]; fxR[int(1.6*d):] += 0.2*fx[:-int(1.6*d)]
st = np.stack([musL+fxL*1.1, musR+fxR*1.1], 1)[:int(DUR*SR)]
st = np.tanh(st*1.05)/np.tanh(1.05); st *= 0.95/abs(st).max()
wavfile.write('mix.wav', SR, (st*32767).astype(np.int16)); print('ok', round(DUR, 2))
