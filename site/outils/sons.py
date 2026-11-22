"""Bruitages du site, mêmes recettes que les vidéos (episodes/2026-11-16_loto/mix.py) : pièces qui tintent, fanfare, « boing ».
Usage : python3 site/outils/sons.py  -> site/assets/anim/*.mp3 (et normalise le son des clips de Mister Coin)."""
import os, subprocess, tempfile, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'anim'))
SR = 48000; rng = np.random.default_rng(7)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def mtof(m): return 440*2**((m-69)/12)
def add(b, x, t0, g=1.0):
    i = int(round(t0*SR)); j = min(len(b), i+len(x)); b[i:j] += g*x[:j-i]
def piece():    # une pièce attrapée : « cling » doré
    n = int(.6*SR); t = tt(n); f = 3136
    return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*d) for m, a, d in ((1, 1, 9), (2.76, .45, 14), (5.4, .2, 22)))*np.minimum(1, t/.002)*.25
def pieces():   # pluie de pièces qui tintent
    s = np.zeros(int(1.6*SR))
    for k in range(9):
        n = int(.9*SR); t = tt(n); f = rng.uniform(2600, 4200)
        x = sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*d) for m, a, d in ((1, 1, 9), (2.76, .5, 14), (5.4, .25, 22)))
        add(s, x*.2*rng.uniform(.6, 1), k*.08+rng.uniform(0, .04))
    return s
def fanfare():  # petite fanfare cuivrée (création originale des vidéos) suivie de pièces
    s = np.zeros(int(2.4*SR))
    for t0, notes, d in ((0, [67, 71, 74], .14), (.16, [72, 76, 79, 84], 1.0)):
        for m in notes:
            n = int(d*SR); t = tt(n); f = mtof(m)
            x = sum(np.sin(2*np.pi*f*k*t)/k**1.3 for k in range(1, 7))*np.minimum(1, t/.02)*np.exp(-t*(1.6 if d > .5 else 9))
            add(s, lp(x, 3500)*.3, t0)
    add(s, pieces(), .55, .7)
    return s
def boing():    # petit saut de Mister Coin
    n = int(.35*SR); t = tt(n); return np.sin(2*np.pi*np.cumsum(260+340*t/.35)/SR)*np.exp(-t*9)*np.minimum(1, t/.01)*.6
def rate():     # mauvaise réponse : « bonk » cartoon doux
    n = int(.7*SR); t = tt(n)
    hit_ = np.sin(2*np.pi*np.cumsum(180+260*np.exp(-t*30))/SR)*np.exp(-t*22)
    return (hit_+np.sin(2*np.pi*np.cumsum(330+90*np.sin(2*np.pi*11*t)*np.exp(-t*3))/SR)*np.exp(-t*4.5)*.45)*.5
def bon():      # bonne réponse : carillon clair, deux notes montantes
    s = np.zeros(int(1.1*SR))
    for f, t0 in ((1567.98, 0), (2349.32, .085)):
        n = int(1.0*SR); t = tt(n); add(s, (np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*9))*np.exp(-t*5.5)*np.minimum(1, t/.002)*.35, t0)
    return s
with tempfile.TemporaryDirectory() as d:
    for nom, f in dict(piece=piece, pieces=pieces, fanfare=fanfare, boing=boing, rate=rate, bon=bon).items():
        x = f(); x = .8*x/abs(x).max(); wavfile.write(f'{d}/{nom}.wav', SR, (x*32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{d}/{nom}.wav', '-ac', '1', '-b:a', '64k', f'{OUT}/s_{nom}.mp3'], check=True)
    # son des clips Veo : volume ramené à un niveau commun
    for nom in ('saut', 'joie', 'rire', 'danse'):
        src = f'{OUT}/{nom}.mp3'; tmp = f'{d}/{nom}.mp3'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', 'loudnorm=I=-20:TP=-2', '-ac', '1', '-b:a', '64k', tmp], check=True); os.replace(tmp, src)
    for nom in ('pouce', 'choc'):   # clips muets
        p = f'{OUT}/{nom}.mp3'
        if os.path.exists(p): os.remove(p)
print(sorted(os.listdir(OUT)))
