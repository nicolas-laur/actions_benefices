import sys
sys.argv = ['x', 'info']
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import ms as V
SR = 48000; DUR = V.DUR; N = int((DUR+1)*SR); rng = np.random.default_rng(11)
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
BPM = 120; B = 60/BPM; BAR = 4*B
PROG = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]   # Am F C G
DARK = [(45, [57, 60, 64]), (46, [58, 62, 65]), (45, [57, 60, 64]), (40, [56, 59, 64])]  # tension
dark_a, dark_b = V.T('c10'), V.T('c13')
kick, bass, synL, synR, hat, clap, arp = (np.zeros(N) for _ in range(7))
def saw(f, t): return 2*((f*t) % 1)-1
for b in range(int(DUR/BAR)+1):
    t0 = b*BAR; dark = dark_a <= t0 < dark_b; root, ch = (DARK if dark else PROG)[b % 4]
    for q in range(4):
        tq = t0+q*B; nk = int(.3*SR); tk = tt(nk)
        add(kick, np.sin(2*np.pi*np.cumsum(45+110*np.exp(-tk*35))/SR)*np.exp(-tk*9), tq)
        nh = int(.05*SR); th = tt(nh); add(hat, hp(rng.standard_normal(nh), 8000)*np.exp(-th*70), tq+B/2)
        if q in (1, 3): nc = int(.18*SR); tc = tt(nc); add(clap, bp(rng.standard_normal(nc), 1200, 5000)*np.exp(-tc*22), tq)
        for e in range(2):   # basse en croches décalées (pompe)
            nb = int(B/2*SR); tb = tt(nb); f = mtof(root-12 if e == 0 else root)
            env = np.minimum(1, tb/0.004)*np.exp(-tb*6); add(bass, (np.sin(2*np.pi*f*tb)+.3*np.sign(np.sin(2*np.pi*f*tb)))*env, tq+e*B/2)
    nS = int(BAR*SR); ts = tt(nS)
    for m in ch:
        for buf, det in ((synL, (0.993, 1.0, 1.006)), (synR, (0.996, 1.003, 1.009))):
            s = sum(saw(mtof(m)*d, ts) for d in det)/3
            pump = np.clip(((ts % B)/B)*3, 0.25, 1)   # sidechain
            add(buf, s*pump*.12, t0)
    for k in range(16):
        m = ch[[0, 1, 2, 1][k % 4]]+12+(12 if k % 8 >= 6 else 0); na = int(.14*SR); ta = tt(na)
        add(arp, saw(mtof(m), ta)*np.exp(-ta*20)*.15, t0+k*B/4)
def gate(segs, n=N):
    pts = [(0, 0)]
    for a, b, g in segs: pts += [(a, 0), (a+0.05, g), (b-0.05, g), (b, 0)]
    pts.append((DUR+1, 0)); pts.sort(); return np.interp(tt(n), [p[0] for p in pts], [p[1] for p in pts])
T = V.T; D = V.DUR
g_kick = gate([(T('c04'), T('c10'), 1), (T('c13'), D-0.3, 1)])
g_hat = gate([(T('c04'), T('c10'), .8), (T('c11'), T('c13'), .4), (T('c13'), D-0.3, .8)])
g_bass = gate([(0.2, D-0.2, 1)])
g_syn = gate([(0, D, 1)]); g_arp = gate([(T('c07'), T('c10'), 1), (T('c13'), D, 1)])
# filtre « build » sur l'intro : synthé passe-bas puis ouverture au drop
syn = lp(synL, 1800); synr = lp(synR, 1800)
pre = int(T('c04')*SR); syn[:pre] = lp(synL, 600)[:pre]; synr[:pre] = lp(synR, 600)[:pre]
dk = (tt(N) >= dark_a) & (tt(N) < dark_b); syn[dk] = lp(synL, 900)[dk]; synr[dk] = lp(synR, 900)[dk]
mono = kick*g_kick*.9+lp(bass, 400)*g_bass*.45+hp(hat, 6000)*g_hat*.25+clap*g_kick*.22+lp(arp, 6000)*g_arp*.5
fade = np.interp(tt(N), [0, .05, D-.5, D, D+1], [0, 1, 1, 0, 0])
musL = (mono+syn*g_syn)*fade; musR = (mono+synr*g_syn)*fade
pk = max(abs(musL).max(), abs(musR).max()); musL *= .5/pk; musR *= .5/pk
# ---------- bruitages ----------
def whoosh():
    n = int(.35*SR); t = tt(n); u = t/t[-1]; x = rng.standard_normal(n)
    return (bp(x, 300, 3000)*(1-u)+hp(x, 3000)*u)*np.sin(np.pi*u)**2*.22
def hit():
    n = int(.6*SR); t = tt(n)
    return np.sin(2*np.pi*np.cumsum(40+160*np.exp(-t*25))/SR)*np.exp(-t*6)*.6+hp(rng.standard_normal(n), 2000)*np.exp(-t*30)*.15
def drop():
    n = int(1.2*SR); t = tt(n)
    sub = np.sin(2*np.pi*np.cumsum(32+90*np.exp(-t*12))/SR)*np.exp(-t*3)*.8
    return sub+lp(rng.standard_normal(n), 800)*np.exp(-t*8)*.25+hp(rng.standard_normal(n), 4000)*np.exp(-t*15)*.12
def count():
    s = np.zeros(int(1.3*SR)); tk = 0; k = 0
    while tk < 1.1:
        n = int(.02*SR); t = tt(n); add(s, np.sin(2*np.pi*(1800+k*30)*t)*np.exp(-t*200)*.12, tk); k += 1; tk += .03+.04*(tk/1.1)
    return s
def click(): n = int(.04*SR); t = tt(n); return (np.sin(2*np.pi*2400*t)+.4*hp(rng.standard_normal(n), 5000))*np.exp(-t*120)*.18
def blip(i): n = int(.09*SR); t = tt(n); return np.sign(np.sin(2*np.pi*mtof(76+[0, 3, 7, 10][i % 4])*t))*np.exp(-t*40)*.07
def glitch():
    n = int(.4*SR); x = rng.standard_normal(n); x = np.round(x*3)/3
    gate_ = (np.floor(tt(n)*40) % 2); return hp(x, 1500)*gate_*np.exp(-tt(n)*5)*.18
def spin(): n = int(1.2*SR); t = tt(n); return bp(rng.standard_normal(n), 400, 2500)*(.5+.5*np.sin(2*np.pi*35*t))*np.sin(np.pi*t/t[-1])*.08
def rise():
    n = int(1.0*SR); t = tt(n); u = t/t[-1]; return np.sin(2*np.pi*np.cumsum(300*2**(2*u))/SR)*u*np.sin(np.pi*u)*.08
def riser():
    n = int(1.4*SR); t = tt(n); u = t/t[-1]; return hp(rng.standard_normal(n), 1000)*u**2*.12+np.sin(2*np.pi*np.cumsum(200*2**(3*u))/SR)*u**2*.05
def low():
    n = int(.6*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(500*2**(-2*t/t[-1]))/SR)*np.exp(-t*4)*.12
def tension(): n = int(3.0*SR); t = tt(n); return (np.sin(2*np.pi*55*t)+.5*np.sin(2*np.pi*58.3*t))*np.minimum(1, t/.5)*np.exp(-t*.6)*.18
def stamp(): n = int(.5*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(70+120*np.exp(-t*40))/SR)*np.exp(-t*10)*.6+bp(rng.standard_normal(n), 500, 3000)*np.exp(-t*30)*.2
def fall(): n = int(1.0*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(900*2**(-4*t))/SR)*np.exp(-t*2.5)*.15
def shimmer():
    n = int(1.2*SR); t = tt(n); return sum(np.sin(2*np.pi*f*t)*np.exp(-t*(3+i)) for i, f in enumerate([1760, 2637, 3520]))*np.minimum(1, t/.05)*.05
def load():
    s = np.zeros(int(2.2*SR)); tk = 0
    while tk < 2.0: n = int(.03*SR); t = tt(n); add(s, np.sin(2*np.pi*1200*t)*np.exp(-t*150)*.05, tk); tk += .12
    return s
def type_():
    s = np.zeros(int(1.6*SR)); tk = 0
    while tk < 1.2:
        n = int(.03*SR); t = tt(n); add(s, bp(rng.standard_normal(n), 2000, 7000)*np.exp(-t*120)*.18, tk); tk += rng.uniform(.04, .09)
    return s
def pop():
    n = int(.15*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(500+900*np.exp(-t*40))/SR)*np.exp(-t*25)*.14
def error():
    s = np.zeros(int(.6*SR))
    for i, f in enumerate((440, 330)): n = int(.18*SR); t = tt(n); add(s, np.sign(np.sin(2*np.pi*f*t))*np.exp(-t*8)*.06, i*.16)
    return s
MAP = dict(load=load, type=type_, pop=pop, error=error, whoosh=whoosh, hit=hit, drop=drop, count=count, click=click, glitch=glitch, spin=spin, rise=rise, riser=riser, low=low,
           tension=tension, stamp=stamp, fall=fall, shimmer=shimmer)
fx = np.zeros(N)
for e in V.events():
    t0, kind = e[0], e[1]
    x = blip(e[2]) if kind == 'blip' else MAP[kind]()
    add(fx, x, t0-(.2 if kind == 'whoosh' else (1.4 if kind == 'riser' else 0)))
d = int(.09*SR); fxL, fxR = fx.copy(), fx.copy(); fxL[d:] += .2*fx[:-d]; fxR[int(1.5*d):] += .15*fx[:-int(1.5*d)]
st = np.stack([musL+fxL, musR+fxR], 1)[:int(DUR*SR)]; st = np.tanh(st*1.2)/np.tanh(1.2); st *= .95/abs(st).max()
wavfile.write('mix.wav', SR, (st*32767).astype(np.int16)); print('ok', round(DUR, 2))
