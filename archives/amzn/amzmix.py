"""Bande son Amazon v2 : lo-fi douce et satisfaisante (~84 BPM), Rhodes chaleureux, basse ronde, petite cloche.
Passages de chute : simple filtrage, batterie retirée. Bruitages discrets, sans aigus agressifs."""
import sys
sys.argv = ['x', 'info']
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import am as V
SR = 48000; DUR = V.DUR; N = int((DUR+1.5)*SR); rng = np.random.default_rng(4)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def mtof(m): return 440*2**((m-69)/12)
def add(b, x, t0, g=1.0):
    i = int(round(t0*SR))
    if i < 0: x = x[-i:]; i = 0
    if i >= len(b): return
    j = min(len(b), i+len(x)); b[i:j] += g*x[:j-i]
BPM = 84; BEAT = 60/BPM; BAR = 4*BEAT
def rhodes(m, d, v=.12):
    n = int(d*SR); t = tt(n); f = mtof(m)
    trem = 1+.12*np.sin(2*np.pi*4.5*t)
    x = (np.sin(2*np.pi*f*t+.9*np.sin(2*np.pi*f*t)*np.exp(-t*3)) + .25*np.sin(2*np.pi*2*f*t)*np.exp(-t*2))
    return lp(x*np.exp(-t*.9)*np.minimum(1, t/.008)*np.clip((d-t)/.25, 0, 1)*trem, 2200)*v
def bell(m, v=.05):
    n = int(1.6*SR); t = tt(n); f = mtof(m)
    return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*4))*np.exp(-t*2.6)*np.minimum(1, t/.004)*v
def bassn(m, d):
    n = int(d*SR); t = tt(n); return lp(np.sin(2*np.pi*mtof(m)*t)*np.minimum(1, t/.02)*np.clip((d-t)/.08, 0, 1), 300)*.32
def kick():
    n = int(.35*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(48+55*np.exp(-t*28))/SR)*np.exp(-t*9)*.45
def rim():
    n = int(.12*SR); t = tt(n); return lp(bp(rng.standard_normal(n), 1200, 3500)*np.exp(-t*45), 3000)*.09
def shaker():
    n = int(.09*SR); t = tt(n); return lp(hp(rng.standard_normal(n), 4000), 9000)*np.exp(-t*50)*np.sin(np.pi*t/t[-1])*.025
# Fmaj9  Em7  Dm9  Cmaj9 : progression douce et ouverte
PROG = [(41, [64, 67, 69, 72]), (40, [62, 64, 67, 71]), (38, [60, 64, 65, 69]), (36, [59, 62, 64, 67])]
MEL = [[76, 74, 72], [74, 71, 67], [72, 69, 65], [71, 67, 64]]
calm = [(V.T('c06'), V.E('c08')), (V.T('c13'), V.E('c13')), (V.T('c18'), V.E('c19'))]
quiet = [(V.T('c20')-.05, V.T('c20')+1.9)]
def inside(t, sp): return any(a <= t < b for a, b in sp)
keys, bass, drums, bells = (np.zeros(N) for _ in range(4))
for b in range(int(DUR/BAR)+1):
    t0 = b*BAR; root, ch = PROG[b % 4]
    for k, m in enumerate(ch): add(keys, rhodes(m, BAR+.4, .10), t0+k*.018)      # accord légèrement égrené
    add(keys, rhodes(ch[1]+12, 1.2, .05), t0+2.5*BEAT)
    add(bass, bassn(root, BEAT*1.8), t0); add(bass, bassn(root+7 if b % 2 else root, BEAT*1.2), t0+2*BEAT+BEAT/2)
    if b % 2 == 1:
        for j, m in enumerate(MEL[b % 4]): add(bells, bell(m), t0+j*BEAT*.75+BEAT)
    for s in range(8):
        ts = t0+s*BEAT/2
        if inside(ts, calm) or inside(ts, quiet) or ts > DUR: continue
        if s in (0, 5): add(drums, kick(), ts)
        if s in (2, 6): add(drums, rim(), ts)
        add(drums, shaker(), ts+(.03 if s % 2 else 0), 1 if s % 2 == 0 else .6)
# filtrage doux sur les passages de chute (on garde la musique, on la voile)
tl = tt(N); g = np.ones(N)
for a, b_ in calm: g -= np.clip(np.minimum((tl-a)/.6, (b_-tl)/.6), 0, 1)
dark_keys = lp(keys, 700)
keys_mix = keys*g+dark_keys*(1-g)*1.1
def verb(x, taps):
    y = x.copy()
    for d, gg in taps: k = int(d*SR); y[k:] += gg*x[:-k]
    return y
KL = verb(keys_mix+bells, ((.043, .3), (.089, .24), (.137, .18), (.211, .12), (.307, .07)))
KR = verb(keys_mix+bells, ((.051, .28), (.097, .22), (.151, .16), (.233, .1), (.331, .06)))
vinyl = lp(rng.standard_normal(N), 3000)*.004
fade = np.interp(tl, [0, .4, DUR-.8, DUR, DUR+1.5], [0, 1, 1, 0, 0])
musL = (KL+bass+drums+vinyl)*fade; musR = (KR+bass+drums+vinyl)*fade
pk = max(abs(musL).max(), abs(musR).max()); musL *= .6/pk; musR *= .6/pk
# ---------- bruitages discrets ----------
def whoosh():
    n = int(.6*SR); u = tt(n)/.6; return lp(rng.standard_normal(n), 1500)*np.sin(np.pi*u)**2*.03
def trans():
    n = int(.3*SR); u = tt(n)/.3; return lp(rng.standard_normal(n), 1200)*np.sin(np.pi*u)**2*.012
def hit():     # impact grave et rond, sans craquement
    n = int(.9*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(45+40*np.exp(-t*18))/SR)*np.exp(-t*5)*.16
def thud():    # carton posé : petit « toc » mat
    n = int(.25*SR); t = tt(n); return lp(np.sin(2*np.pi*np.cumsum(110+60*np.exp(-t*50))/SR)*np.exp(-t*28)+bp(rng.standard_normal(n), 300, 1200)*np.exp(-t*60)*.3, 1500)*.13
def crash():   # chute : grave qui descend, sans métal
    n = int(1.2*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(70*np.exp(-t*1.5)+30)/SR)*np.exp(-t*2.5)*.16
def low():
    n = int(1.6*SR); t = tt(n); return np.sin(2*np.pi*55*t)*np.minimum(1, t/.3)*np.exp(-t*1.5)*.08
def count():   # petit cliquetis doux de compteur
    s = np.zeros(int(1.3*SR)); tk = 0; k = 0
    while tk < 1.0:
        n = int(.03*SR); t = tt(n); add(s, np.sin(2*np.pi*(880+k*12)*t)*np.exp(-t*120)*.012, tk); k += 1; tk += .05+.05*tk
    return s
MAP = dict(whoosh=whoosh, trans=trans, hit=hit, thud=thud, crash=crash, low=low, count=count)
fx = np.zeros(N)
for t0, k in V.events(): add(fx, MAP[k](), t0-(.35 if k == 'whoosh' else (.12 if k == 'trans' else 0)))
d = int(.08*SR); fL, fR = fx.copy(), fx.copy(); fL[d:] += .15*fx[:-d]; fR[int(1.3*d):] += .12*fx[:-int(1.3*d)]
st = np.stack([musL+fL, musR+fR], 1)[:int(DUR*SR)]; st = np.tanh(st*1.05)/np.tanh(1.05); st *= .9/abs(st).max()
wavfile.write('amzmix.wav', SR, (st*32767).astype(np.int16)); print('ok', round(DUR, 2))
