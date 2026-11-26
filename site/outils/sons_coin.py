"""Bruitages courts de Mister Coin pour l'accueil (26/11/2026) : synthétisés ici, doux et cartoon, un par famille d'expressions.
Écrit site/assets/anim/s_<nom>.mp3 (mono 44,1 kHz). Relancer : python3 site/outils/sons_coin.py"""
import numpy as np, subprocess, pathlib, tempfile, wave
SR = 44100
OUT = pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'anim'

def t(d): return np.arange(int(SR * d)) / SR
def env(n, a=.005, r=.08):
    e = np.ones(n); na, nr = int(SR * a), int(SR * r)
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e
def osc(f, d, forme='sin'):
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(f, t(d).shape)) / SR
    return np.sin(ph) if forme == 'sin' else np.sign(np.sin(ph)) * .3 + np.sin(ph) * .7
def cloche(f0, d, part=(1, 2.76, 5.4), dec=(6, 9, 14)):
    x = t(d); return sum(np.exp(-k * x) * np.sin(2 * np.pi * f0 * p * x) / (i + 1) for i, (p, k) in enumerate(zip(part, dec)))

S = {}
# sifflet qui monte (joie, saut, étoiles)
x = t(.42); S['monte'] = osc(np.geomspace(520, 1500, len(x)), .42) * env(len(x), .01, .12) * (1 + .15 * np.sin(2 * np.pi * 9 * x))
# sifflet qui descend (triste, inquiet, sueur)
x = t(.55); S['descend'] = osc(np.geomspace(900, 300, len(x)), .55) * env(len(x), .01, .2) * (1 + .2 * np.sin(2 * np.pi * 6 * x))
# pop de bulle (salut, pouce, question)
x = t(.12); S['pop'] = np.sin(2 * np.pi * np.cumsum(np.geomspace(380, 1100, len(x))) / SR) * np.exp(-28 * x)
# ding d'idée (réfléchit, loupe)
S['ding'] = cloche(1318, .9) * env(int(SR * .9), .002, .3)
# tiroir-caisse (trophée, tirelire)
x = t(.5); ka = np.random.default_rng(1).normal(0, 1, int(SR * .05)) * np.exp(-60 * t(.05))
S['caisse'] = np.concatenate([ka * .5, np.zeros(int(SR * .04)), cloche(1760, .41) * .9])[:len(x)] * env(len(x), .002, .15)
# double note « hm hm » (sceptique, haussement)
a = osc(392, .14, 'carre') * env(int(SR * .14), .01, .05); b = osc(330, .2, 'carre') * env(int(SR * .2), .01, .08)
S['hmm'] = np.concatenate([a, np.zeros(int(SR * .05)), b]) * .6
# trompette de choc (choc, facepalm)
x = t(.35); f = 700 - 400 * x / .35; S['choc'] = (osc(f, .35, 'carre') + .5 * osc(f * 1.5, .35)) * env(len(x), .005, .12) * .5
# ronflement doux (dort)
x = t(1.1); bruit = np.random.default_rng(2).normal(0, 1, len(x)); lis = np.convolve(bruit, np.ones(60) / 60, 'same')
S['ronfle'] = (lis * 3 + .3 * np.sin(2 * np.pi * 95 * x)) * np.sin(np.pi * x / 1.1) ** 2 * .6
# mégaphone (petite fanfare de deux notes)
S['annonce'] = np.concatenate([osc(523, .12, 'carre') * env(int(SR * .12), .005, .04), osc(784, .25, 'carre') * env(int(SR * .25), .005, .1)]) * .5
# course (parapluie, court) : trois pas rapides
pas = np.sin(2 * np.pi * 180 * t(.05)) * np.exp(-70 * t(.05))
S['pas'] = np.concatenate([np.concatenate([pas, np.zeros(int(SR * .07))]) for _ in range(4)])

for nom, y in S.items():
    y = y / np.max(np.abs(y)) * .5
    with tempfile.NamedTemporaryFile(suffix='.wav') as w:
        with wave.open(w.name, 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((y * 32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', w.name, '-af', 'loudnorm=I=-22:TP=-3', '-ar', '44100', '-ac', '1', '-b:a', '64k', str(OUT / f's_{nom}.mp3')], check=True)
    print(nom, round(len(y) / SR, 2), 's')
