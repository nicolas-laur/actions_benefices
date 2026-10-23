"""Bande son Apple : piano et cordes électroniques, ~100 BPM, passages sombres sur 1985-1997 et sur le doute."""
import sys
sys.argv = ['x', 'info']
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import ap as V
SR = 48000; DUR = V.DUR; N = int((DUR+1.5)*SR); rng = np.random.default_rng(5)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def mtof(m): return 440*2**((m-69)/12)
def add(b, x, t0, g=1.0):
    i = int(round(t0*SR))
    if i < 0: x = x[-i:]; i = 0
    if i >= len(b): return
    j = min(len(b), i+len(x)); b[i:j] += g*x[:j-i]
def piano(m, dur=3.0, v=.5):
    n = int(dur*SR); t = tt(n); f = mtof(m)
    s = sum(a*np.sin(2*np.pi*f*h*(1+.0003*h*h)*t)*np.exp(-t*d*(1+m/100)) for h, a, d in [(1, 1, 1.0), (2, .45, 1.8), (3, .18, 3), (4, .07, 4.5)])
    return lp(s*np.minimum(1, t/.005)*np.clip((dur-t)/.3, 0, 1), 1800+1500*v)*v
BEAT = 60/100; BAR = 4*BEAT
BRIGHT = [(48, [64, 67, 71, 74]), (45, [64, 67, 72, 76]), (41, [60, 65, 69, 72]), (43, [62, 67, 71, 74])]   # Cmaj9 Am F G
DARK = [(45, [60, 64, 69, 71]), (41, [60, 65, 68, 72]), (44, [60, 63, 68, 70]), (43, [62, 65, 67, 71])]
dark_spans = [(V.T('c06'), V.T('c08')), (V.T('c18'), V.T('c21'))]
def is_dark(t): return any(a <= t < b for a, b in dark_spans)
pL, pR, padL, padR, bass, pulse = (np.zeros(N) for _ in range(6))
for b in range(int(DUR/BAR)+1):
    t0 = b*BAR; root, ch = (DARK if is_dark(t0) else BRIGHT)[b % 4]
    add(bass, piano(root-12, 4.0, .55), t0)
    for k, beat in enumerate((0, 1, 1.5, 2.5, 3)):
        m = ch[k % 4]+(12 if (b % 2 and k in (3, 4)) else 0)
        x = piano(m, 2.6, .26*(0.9+0.2*rng.random())); add(pL if k % 2 else pR, x, t0+beat*BEAT); add(pR if k % 2 else pL, x*.5, t0+beat*BEAT+0.01)
    n = int((BAR+1.0)*SR); t = tt(n); env = np.minimum(1, t/1.0)*np.clip((BAR+1.0-t)/1.0, 0, 1)
    for m in ch:
        for buf, d in ((padL, .997), (padR, 1.003)):
            saw = 2*((mtof(m-12)*d*t) % 1)-1; add(buf, saw*env*.018, t0)
    for q in range(8):   # pulsation douce (cordes électroniques)
        nq = int(BEAT/2*SR); tq = tt(nq); add(pulse, np.sin(2*np.pi*mtof(root)*tq)*np.exp(-tq*9)*.12, t0+q*BEAT/2)
def gate(spans, g):
    pts = [(0, 0)]
    for a, b in spans: pts += [(a, 0), (a+.8, g), (b-.8, g), (b, 0)]
    pts.append((DUR+1.5, 0)); pts.sort(); return np.interp(tt(N), [p[0] for p in pts], [p[1] for p in pts])
g_pulse = gate([(V.T('c08'), V.T('c18')), (V.T('c21'), DUR)], 1)
def verb(x, taps):
    y = x.copy()
    for d, g in taps: k = int(d*SR); y[k:] += g*x[:-k]
    return y
fade = np.interp(tt(N), [0, .3, DUR-.8, DUR, DUR+1.5], [0, 1, 1, 0, 0])
musL = (verb(pL, ((.029, .35), (.051, .3), (.083, .24), (.131, .18), (.197, .12))) + lp(padL, 2200) + lp(bass, 700) + lp(pulse, 1200)*g_pulse)*fade
musR = (verb(pR, ((.037, .33), (.061, .28), (.097, .22), (.149, .16), (.223, .1))) + lp(padR, 2200) + lp(bass, 700) + lp(pulse, 1200)*g_pulse)*fade
pk = max(abs(musL).max(), abs(musR).max()); musL *= .5/pk; musR *= .5/pk
def swell():
    n = int(1.4*SR); t = tt(n); u = t/t[-1]; return lp(rng.standard_normal(n), 2500)*u**2*np.exp(-np.maximum(0, t-1.2)*25)*.06
def trans():
    n = int(.6*SR); u = tt(n)/.6; return lp(rng.standard_normal(n), 1800)*np.sin(np.pi*u)**2*.05
def hit():
    n = int(1.2*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(42+70*np.exp(-t*18))/SR)*np.exp(-t*3.5)*.4+hp(rng.standard_normal(n), 3000)*np.exp(-t*12)*.04
def low():
    n = int(2.0*SR); t = tt(n); return (np.sin(2*np.pi*41.2*t)+.5*np.sin(2*np.pi*43.6*t))*np.minimum(1, t/.3)*np.exp(-t*1.2)*.22
def tick():
    s = np.zeros(int(2.4*SR)); tk = 0
    while tk < 2.2: n = int(.02*SR); t = tt(n); add(s, np.sin(2*np.pi*1500*t)*np.exp(-t*200)*.05, tk); tk += .15
    return s
def count():
    s = np.zeros(int(1.4*SR)); tk = 0; k = 0
    while tk < 1.1: n = int(.02*SR); t = tt(n); add(s, np.sin(2*np.pi*(1300+k*25)*t)*np.exp(-t*190)*.06, tk); k += 1; tk += .04+.05*(tk/1.1)
    return s
MAP = dict(swell=swell, trans=trans, hit=hit, low=low, tick=tick, count=count)
fx = np.zeros(N)
for t0, k in V.events(): add(fx, MAP[k](), t0-(1.2 if k == 'swell' else (.3 if k == 'trans' else 0)))
d = int(.11*SR); fL, fR = fx.copy(), fx.copy(); fL[d:] += .2*fx[:-d]; fR[int(1.4*d):] += .16*fx[:-int(1.4*d)]
st = np.stack([musL+fL, musR+fR], 1)[:int(DUR*SR)]; st = np.tanh(st*1.1)/np.tanh(1.1); st *= .95/abs(st).max()
wavfile.write('apmix.wav', SR, (st*32767).astype(np.int16)); print('ok', round(DUR, 2))
