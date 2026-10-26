"""Bande son Kering (moteur lo-fi) avec ambiances : brouhaha de boutique, déclencheurs au défilé, horloge et pluie dans la boutique vide.\nBande son AMD (reprend le moteur lo-fi Novo/Alphabet) + cri « façon Wilhelm » de synthèse (création originale, libre de droits).
Bande son Alphabet (moteur lo-fi v2) : plus lumineuse, clavier et souris : lo-fi douce et satisfaisante (~84 BPM), Rhodes chaleureux, basse ronde, petite cloche.
Passages de chute : simple filtrage, batterie retirée. Bruitages discrets, sans aigus agressifs."""
import sys
sys.argv = ['x', 'info']
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import video as V
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
BPM = 96; BEAT = 60/BPM; BAR = 4*BEAT
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
PROG = [(45, [60, 64, 67, 71]), (41, [60, 64, 69, 72]), (43, [62, 67, 71, 74]), (40, [59, 64, 67, 71])]   # Am7 Fmaj7 G6 Em7 : tendu mais pas lugubre   # Dm9 Bbmaj7 Fadd9 G6 : nocturne, électronique
MEL = [[76, 72, 71], [77, 76, 72], [74, 71, 67], [71, 67, 64]]
calm = [(V.T['ventes'], V.T['change']), (V.T['chute16'], V.T['alors'])]   # krach : musique voilée, batterie coupée
quiet = []
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
fade = np.interp(tl, [0, .05, DUR-.8, DUR, DUR+1.5], [0, 1, 1, 0, 0])
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
def beep():    # bip de paiement feutré, deux notes
    s = np.zeros(int(.5*SR))
    for k, (f, t0) in enumerate(((1318.5, 0), (1760, .09))):
        n = int(.16*SR); t = tt(n); add(s, lp(np.sin(2*np.pi*f*t)*np.exp(-t*22), 4000)*.035, t0)
    return s
def coin():   # petit tintement doré, discret
    n = int(1.0*SR); t = tt(n); return sum(np.sin(2*np.pi*f*t)*np.exp(-t*d) for f, d in ((2093, 6), (3136, 9), (4186, 12)))*.009
def paid():   # validation de paiement : carillon clair et rond, deux notes montantes (création originale)
    s = np.zeros(int(1.2*SR))
    for f, t0, g in ((1567.98, 0.0, 1.0), (2349.32, .085, .9)):
        n = int(1.0*SR); t = tt(n)
        x = (np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*9)+.12*np.sin(2*np.pi*3.01*f*t)*np.exp(-t*14))*np.exp(-t*5.5)*np.minimum(1, t/.002)
        add(s, x*.07*g, t0)
    return s
def key():     # touche de clavier : petit « tac » mat, légèrement varié
    n = int(.06*SR); t = tt(n); g = .7+.6*rng.random(); f = 2200+900*rng.random()
    return (bp(rng.standard_normal(n), f*.6, f*1.6)*np.exp(-t*140)*.22+np.sin(2*np.pi*(180+40*rng.random())*t)*np.exp(-t*90)*.12)*g
def click():   # clic de souris : appui + relâchement
    s = np.zeros(int(.2*SR))
    for t0, g in ((0, 1.0), (.065, .6)):
        n = int(.03*SR); t = tt(n); add(s, (hp(rng.standard_normal(n), 2500)*np.exp(-t*400)*.45+np.sin(2*np.pi*1900*t)*np.exp(-t*300)*.16)*g, t0)
    return s
def neon():    # néon qui s'allume : claquement + bourdonnement électrique bref
    n = int(.9*SR); t = tt(n); hum = (np.sign(np.sin(2*np.pi*100*t))*.5+np.sin(2*np.pi*200*t)*.5)
    return lp(hum, 1800)*np.exp(-t*4)*.05+hp(rng.standard_normal(n), 2000)*np.exp(-t*60)*.08
def pop():
    n = int(.15*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(500+900*np.exp(-t*40))/SR)*np.exp(-t*30)*.09
def kiosk():   # bip de borne : deux notes claires montantes
    s = np.zeros(int(.4*SR))
    for t0, f in ((0, 1046.5), (.09, 1568)):
        n = int(.14*SR); t = tt(n); add(s, (np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*2*f*t))*np.exp(-t*24)*np.minimum(1, t/.003)*.07, t0)
    return s
def printer():  # imprimante thermique : cliquetis rapides + moteur
    n = int(2.3*SR); t = tt(n); s = lp(rng.standard_normal(n), 900)*.025*(1+.5*np.sin(2*np.pi*31*t))
    k = 0.0
    while k < 2.2:
        m = int(.012*SR); tk = tt(m); add(s, hp(rng.standard_normal(m), 3000)*np.exp(-tk*300)*.06, k); k += .028
    return s*np.minimum(1, t/.05)*np.clip((2.3-t)/.1, 0, 1)
def impact():  # le chiffre tombe : sub rond + corps + petit claquement feutré (pas d'aigus agressifs)
    n = int(1.1*SR); t = tt(n)
    sub_ = np.sin(2*np.pi*np.cumsum(38+70*np.exp(-t*22))/SR)*np.exp(-t*4.2)
    body = np.sin(2*np.pi*np.cumsum(120+180*np.exp(-t*60))/SR)*np.exp(-t*18)*.5
    snap = lp(hp(rng.standard_normal(n), 900), 5000)*np.exp(-t*70)*.18
    return (sub_+body+snap)*np.minimum(1, t/.002)*.30
def swish():   # souffle d'entrée de scène, filtre qui s'ouvre
    n = int(.45*SR); u = tt(n)/.45; x = rng.standard_normal(n)
    return (lp(x, 900)*(1-u)+lp(x, 3500)*u)*np.sin(np.pi*u)**1.5*.05
def tick():    # compteur : cliquetis audibles qui accélèrent puis ralentissent
    s = np.zeros(int(1.6*SR)); tk = 0; k = 0
    while tk < 1.3:
        n = int(.025*SR); t = tt(n); add(s, (np.sin(2*np.pi*1250*t)+.4*np.sin(2*np.pi*2500*t))*np.exp(-t*160)*.035, tk)
        k += 1; tk += .045+.09*(tk/1.3)**2
    return s
def glint():   # éclat doré sur les chiffres or
    n = int(1.3*SR); t = tt(n); return sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*d) for f, a, d in ((1975.5, 1, 4.5), (2959.9, .6, 6), (3951, .35, 8)))*.022
def riser():   # montée de tension avant la révélation
    n = int(1.3*SR); t = tt(n); u = t/t[-1]
    tone = np.sin(2*np.pi*np.cumsum(110+330*u**2)/SR)*.4
    x = rng.standard_normal(n); nz = lp(x, 900)*(1-u)+lp(x, 5500)*u
    return (nz*.5+tone)*u**2.2*.07
def proj():   # projecteur qui démarre : cliquetis de défilement à 24 i/s qui s'éteint doucement
    n = int(3.2*SR); t = tt(n); s = np.zeros(n); k = 0.0
    while k < 3.0:
        m = int(.02*SR); tk = tt(m); add(s, bp(rng.standard_normal(m), 600, 2600)*np.exp(-tk*220)*.05, k); k += 1/24
    return lp(s, 3000)*np.minimum(1, t/.05)*np.exp(-t*.8)+lp(rng.standard_normal(n), 400)*.01*np.exp(-t*1.2)
def bid():    # enchère : petit « ding » de comptoir, clair et court
    n = int(.9*SR); t = tt(n); return sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*d) for f, a, d in ((1318.5, 1, 7), (2637, .3, 11), (3951, .12, 15)))*.05
def gavel():  # marteau du commissaire-priseur : deux coups de bois
    s = np.zeros(int(.8*SR))
    for t0, g in ((0, 1.0), (.18, .75)):
        n = int(.2*SR); t = tt(n); x = bp(rng.standard_normal(n), 300, 1800)*np.exp(-t*55)*.5+np.sin(2*np.pi*np.cumsum(240+120*np.exp(-t*80))/SR)*np.exp(-t*35)
        add(s, x*.22*g, t0)
    return s
def coins():   # pièces qui tintent : plusieurs « cling » métalliques
    s = np.zeros(int(1.4*SR))
    for k in range(6):
        n = int(.9*SR); t = tt(n); f = rng.uniform(2600, 4200)
        x = sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*d) for m, a, d in ((1, 1, 9), (2.76, .5, 14), (5.4, .25, 22)))
        add(s, x*.018*rng.uniform(.6, 1), k*.07+rng.uniform(0, .04))
    return s
def boom():   # explosion : sub profond + souffle
    n = int(2.0*SR); t = tt(n)
    sub_ = np.sin(2*np.pi*np.cumsum(32+80*np.exp(-t*10))/SR)*np.exp(-t*2.2)
    air = lp(rng.standard_normal(n), 1200)*np.exp(-t*3.5)*.5
    return (sub_+air)*np.minimum(1, t/.003)*.42
def shatter():   # verre qui éclate : éclats aigus brefs
    s = np.zeros(int(1.2*SR))
    for k in range(26):
        n = int(.08*SR); t = tt(n); f = rng.uniform(3000, 7000)
        add(s, (np.sin(2*np.pi*f*t)*.6+hp(rng.standard_normal(n), 4000)*.4)*np.exp(-t*rng.uniform(40, 90))*.05*rng.uniform(.4, 1), rng.uniform(0, .5)**1.5)
    return lp(s, 9000)
def cdbeep():   # bip de compte à rebours, sec et radio
    n = int(.18*SR); t = tt(n); return bp(np.sign(np.sin(2*np.pi*1000*t))*.5, 600, 2500)*np.exp(-t*14)*np.minimum(1, t/.003)*.09
def ignite():   # allumage : grondement qui monte, puis tient
    n = int(7.5*SR); t = tt(n); env = np.clip(t/.35, 0, 1)*np.exp(-np.clip(t-.9, 0, None)*.9)
    roar = lp(rng.standard_normal(n), 380)*1.6+lp(rng.standard_normal(n), 1600)*.35
    crack = hp(rng.standard_normal(n), 1500)*np.exp(-t*3)*.3
    return (roar+crack)*env*(1+.15*np.sin(2*np.pi*7*t))*.12
def cutoff():   # moteur coupé : grondement qui s'éteint + claquement sourd
    n = int(1.6*SR); t = tt(n); return lp(rng.standard_normal(n), 400)*np.exp(-t*4)*.22+np.sin(2*np.pi*np.cumsum(90*np.exp(-t*8)+40)/SR)*np.exp(-t*10)*.2
def tadaa():   # petite fanfare cuivrée de surprise (création originale)
    s = np.zeros(int(1.4*SR))
    for t0, notes, d in ((0, [67, 71, 74], .14), (.16, [72, 76, 79, 84], 1.0)):
        for m in notes:
            n = int(d*SR); t = tt(n); f = mtof(m)
            x = sum(np.sin(2*np.pi*f*k*t)/k**1.3 for k in range(1, 7))*np.minimum(1, t/.02)*np.exp(-t*(1.6 if d > .5 else 9))
            add(s, lp(x, 3500)*.035, t0)
    return s
def bonk():   # « bonk » cartoon : choc mat + petit ressort
    n = int(.7*SR); t = tt(n)
    hit_ = np.sin(2*np.pi*np.cumsum(180+260*np.exp(-t*30))/SR)*np.exp(-t*22)
    boing = np.sin(2*np.pi*np.cumsum(330+90*np.sin(2*np.pi*11*t)*np.exp(-t*3))/SR)*np.exp(-t*4.5)*.45
    return (hit_+boing)*.16
def shutter():   # déclencheur d'appareil photo : deux clics secs
    s = np.zeros(int(.12*SR))
    for t0, g in ((0, 1.0), (.045, .7)):
        n = int(.025*SR); t = tt(n); add(s, bp(rng.standard_normal(n), 1800, 7000)*np.exp(-t*260)*.22*g, t0)
    return s
def zoom():   # inutile ici, conservé pour compatibilité
    return np.zeros(10)
def scream(): return np.zeros(10)
MAP = dict(tadaa=tadaa, bonk=bonk, shutter=shutter, scream=scream, zoom=zoom, cdbeep=cdbeep, ignite=ignite, cutoff=cutoff, coins=coins, boom=boom, shatter=shatter, proj=proj, bid=bid, gavel=gavel, neon=neon, pop=pop, kiosk=kiosk, printer=printer, key=key, click=click, impact=impact, swish=swish, tick=tick, glint=glint, riser=riser, paid=paid, beep=beep, coin=coin, whoosh=whoosh, trans=trans, hit=hit, thud=thud, crash=crash, low=low, count=count)
fx = np.zeros(N); duck = np.ones(N)
for t0, k in V.events():
    add(fx, MAP[k](), t0-(.35 if k == 'whoosh' else (.12 if k in ('trans', 'swish') else 0)), .45 if k == 'ignite' else 1.0)
    if k in ('impact', 'boom'):     # la musique s'efface brièvement sous l'impact : plus de punch sans monter le volume
        i = int(t0*SR); m = int(.5*SR); env = 1-.45*np.exp(-np.arange(m)/(.12*SR))
        if i+m < N: duck[i:i+m] = np.minimum(duck[i:i+m], env)
musL *= duck; musR *= duck
# ---------- ambiances de lieu ----------
amb = np.zeros(N)
def seg(a, b, x, fade_=.6):
    i, j = int(a*SR), min(N, int(b*SR)); x = x[:j-i]; e = np.ones(len(x)); k = int(fade_*SR)
    e[:k] = np.linspace(0, 1, min(k, len(e)))[:len(e[:k])]; e[-k:] = np.minimum(e[-k:], np.linspace(1, 0, min(k, len(e)))[-len(e[-k:]):]); amb[i:j] += x*e
def babble(d):   # brouhaha de clients : voix lointaines (bruit filtré dans les formants, modulé en syllabes) + pas
    n = int(d*SR); t = tt(n); x = np.zeros(n)
    for k in range(9):
        src = rng.standard_normal(n); f1, f2 = rng.uniform(350, 800), rng.uniform(1000, 2400)
        syl = (.5+.5*np.sin(2*np.pi*rng.uniform(3, 5.5)*t+rng.uniform(0, 6)))**2*(.5+.5*np.sin(2*np.pi*rng.uniform(.15, .4)*t+k))
        x += (bp(src, f1*.8, f1*1.2)+.6*bp(src, f2*.85, f2*1.15))*syl
    steps = np.zeros(n); tk = .2
    while tk < d-.1:
        m = int(.05*SR); u = tt(m); add(steps, bp(rng.standard_normal(m), 1500, 5000)*np.exp(-u*90)*.5, tk); tk += rng.uniform(.25, .6)
    return lp(x, 3000)*.010+steps*.010
def ticktock(d):
    n = int(d*SR); s = np.zeros(n)
    for k in range(int(d)):
        m = int(.04*SR); u = tt(m); add(s, bp(rng.standard_normal(m), 2000 if k % 2 else 1500, 5000)*np.exp(-u*160)*.05, k+.0)
    return s
def rain(d):
    n = int(d*SR); return lp(hp(rng.standard_normal(n), 1500), 6000)*.004
def hum(d):
    n = int(d*SR); t = tt(n); return lp(rng.standard_normal(n), 250)*.010+np.sin(2*np.pi*60*t)*.002
seg(0, V.T['y2015']+.3, babble(V.T['y2015']+.3)*.75)
seg(V.T['y2015'], V.T['mais'], babble(V.T['mais']-V.T['y2015'])*.35)
seg(V.T['mais'], V.T['ventes'], hum(V.T['ventes']-V.T['mais']))
seg(V.T['ventes'], V.T['change'], ticktock(V.T['change']-V.T['ventes']+1)+rain(V.T['change']-V.T['ventes']+1))
seg(V.T['change'], DUR, hum(DUR-V.T['change'])*.5)
d = int(.08*SR); fL, fR = fx.copy(), fx.copy(); fL[d:] += .15*fx[:-d]; fR[int(1.3*d):] += .12*fx[:-int(1.3*d)]
_, vo = wavfile.read(V.VOICE); vo = vo.astype(np.float32)/32768
if vo.ndim > 1: vo = vo.mean(1)
v = np.zeros(N); v[:min(N, len(vo))] = vo[:N]; v *= .9/abs(v).max()
def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 1e-4]**2))
# enveloppe de voix (attaque rapide, relâche lente) pour baisser la musique quand ça parle
env = np.abs(v); k = int(.05*SR); env = np.convolve(env, np.ones(k)/k, 'same'); env = np.clip(env/(np.percentile(env, 95)+1e-6), 0, 1)
sm = np.zeros_like(env); a_, r_ = 1-np.exp(-1/(.03*SR)), 1-np.exp(-1/(.35*SR)); acc = 0.0
for i in range(0, N, 64):
    e = env[i]; acc += (a_ if e > acc else r_)*64*(e-acc); acc = min(max(acc, 0), 1); sm[i:i+64] = acc
mg = 1-.45*sm
mL, mR = musL*mg, musR*mg
mscale = .25*rms(v)/rms((musL+musR)/2)          # musique ~ -16 dB sous la voix
fscale = .55*rms(v)/max(1e-6, rms(fx))*.48
voL, voR = v, v
ascale = .8*rms(v)/max(1e-6, rms(amb))*.12
mixL = voL+mL*mscale+fL*fscale+amb*ascale; mixR = voR+mR*mscale+fR*fscale+amb*ascale
st = np.stack([mixL, mixR], 1)[:int(DUR*SR)]; st = np.tanh(st*1.05)/np.tanh(1.05); st *= .9/abs(st).max()
wavfile.write(V.D+'/mix.wav', SR, (st*32767).astype(np.int16))
sx = np.stack([voL+fL*fscale+amb*ascale, voR+fR*fscale+amb*ascale], 1)[:int(DUR*SR)]; sx *= .9/abs(sx).max()
wavfile.write(V.D+'/mix_sans_musique.wav', SR, (sx*32767).astype(np.int16)); print('ok', round(DUR, 2), round(mscale, 3), round(fscale, 3))
