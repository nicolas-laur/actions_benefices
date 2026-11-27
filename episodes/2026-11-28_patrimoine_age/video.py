"""Vidéo « Les Français de ton âge ont combien d'argent ? » (28/11/2026), cartoon 1930 en Technicolor, fil rouge : la toise.
Calage de la voix (segments transcrits dans voix/segments.json), deux silences de réaction ajoutés au montage, sous-titres, plan des clips
de Mister Coin, découpage en scènes et images source de chaque décor (les plages saines des vidéos Gemini, voir sr_tout.py).
Le rendu est dans video_col.py. Voix d'origine : voice_full.wav (48 kHz mono) ; voix montée : voice_montage.wav."""
import os, sys, wave
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D); sys.path.insert(0, f'{D}/../../mister_coin')
from scenes import NB, GD
from veo_coin import VeoCoin
FPS = 60; SRC = f'{D}/voice_full.wav'; VOICE = f'{D}/voice_montage.wav'
# silences de réaction (temps de la voix d'origine, durée) : sueur après « à rembourser », réflexion après « ça plafonne »
INS = [(35.62, 1.4), (46.84, 1.5)]
def sh(t): return t+sum(d for (a, d) in INS if t >= a)                     # temps voix d'origine -> temps vidéo
def _montage():
    if os.path.exists(VOICE) and os.path.getmtime(VOICE) > os.path.getmtime(SRC): return
    with wave.open(SRC) as w: sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
    parts, a = [], 0
    for (t, d) in INS: i = int(t*sr); parts += [x[a:i], np.zeros(int(d*sr), np.int16)]; a = i
    parts.append(x[a:]); y = np.concatenate(parts)
    with wave.open(VOICE, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())
_montage()
with wave.open(VOICE) as w: DUR_VOIX = w.getnframes()/w.getframerate()
DUR = round(min(80.0, DUR_VOIX+1.2), 2)
# sous-titres (voix d'origine) ; l'accroche est écrite en grand sur la plaque : pas de sous-titre doublé
_C = [(2.31, 3.55, "[Enregistre] cette vidéo,"),
      (3.60, 5.30, "dis-nous où tu te situes [en commentaire]."),
      (5.97, 7.95, "Les chiffres viennent de la dernière"),
      (8.00, 10.13, "enquête Patrimoine de l'[Insee], début [2024]."),
      (10.59, 12.45, f"On compte tout ce que possède le ménage{NB}:"),
      (12.50, 14.40, "livrets, placements, logement,"),
      (14.45, 15.85, "sans retirer les [crédits]."),
      (16.44, 17.21, "[Moins de 30 ans]."),
      (17.69, 20.58, f"La moitié des ménages a moins de [26{NB}100{NB}€]."),
      (21.10, 22.31, f"[30 à 39 ans]{NB}:"),
      (22.59, 24.32, f"[146{NB}200{NB}€]."),
      (24.65, 25.98, f"Plus de [5 fois plus]{NB}!"),
      (26.43, 26.96, f"Le secret{NB}?"),
      (27.33, 28.48, "Souvent, un [logement]."),
      (28.69, 29.98, f"Mais acheté [à crédit]{NB}:"),
      (30.20, 32.20, "selon l'Insee, chez ceux qui empruntent,"),
      (32.25, 35.52, f"il reste en médiane [119{NB}800{NB}€] à rembourser."),
      (36.10, 37.43, f"[40 à 49 ans]{NB}:"),
      (37.74, 39.42, f"[215{NB}200{NB}€]."),
      (39.83, 41.41, f"[50 à 59 ans]{NB}:"),
      (41.63, 43.57, f"[254{NB}100{NB}€]."),
      (43.93, 45.24, "[Le sommet]."),
      (45.55, 46.74, "Après, ça [plafonne]."),
      (47.19, 48.45, "Ce qui fait grimper la marque,"),
      (48.50, 49.76, "ce n'est pas que le salaire."),
      (49.98, 50.61, f"C'est [le temps]{NB}:"),
      (51.04, 52.75, "[l'épargne] de chaque mois,"),
      (52.80, 54.45, "[le crédit] qui se rembourse,"),
      (54.50, 55.55, "parfois [un héritage],"),
      (55.60, 57.01, "et des [intérêts] qui rapportent à leur tour."),
      (57.48, 57.91, f"Et toi{NB}?"),
      (58.09, 60.25, f"Ta marque est au-dessus ou en dessous de ton âge{NB}?")]
CAPS = [(sh(a), sh(b), s_, GD) for (a, b, s_) in _C]
# scènes (temps de la vidéo)
T = dict(bas=16.2, milieu=20.85, haut=sh(35.85), horloge=sh(46.97), fin=sh(57.30))
# sauts de Mister Coin d'une plaque à la suivante pendant une scène (début, fin) : la caméra suit son saut
JUMPS = {'milieu': (25.95, 26.55), 'haut': (sh(39.55), sh(39.55)+.6)}
FEET = 1650
EN, EX, QU, CO, IQ = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_confidence', 'classique_parle_inquiet'
PLAN = [(0.0, [QU], 'voix'), (5.9, [EX], 'voix'),
        (T['bas'], [IQ], 'voix'),
        (T['milieu'], [EN], 'voix'), (JUMPS['milieu'][1], [CO], 'voix'),
        (T['haut'], [EX], 'voix'), (JUMPS['haut'][1], [EN], 'voix'),
        (T['horloge'], [CO], 'voix'),
        (T['fin'], [QU], 'voix')]
class ParScene:
    """une banque VeoCoin par scène : le clip change net au changement de décor (pendant le saut), au lieu d'attendre un silence"""
    def __init__(self, bornes, **kw):
        self.parts = []; base = None
        for a, b in zip(bornes, bornes[1:]+[DUR+1]):
            pl = [p for p in PLAN if a-.01 <= p[0] < b-.01]; m = VeoCoin(pl, **kw)
            if base is None: base = m
            else: m._frames, m._feat = base._frames, base._feat
            self.parts.append((a, b, m))
        import pickle, hashlib
        key = hashlib.md5(repr((PLAN, DUR, os.path.getmtime(VOICE))).encode()).hexdigest()[:10]; cp = f'{D}/tmp/mc_seq_{key}.pkl'
        if os.path.exists(cp):
            for (a, b, m), (sq, hp) in zip(self.parts, pickle.load(open(cp, 'rb'))): m.seq, m.hops = sq, hp
        else:
            for (a, b, m) in self.parts: m._global_sequence()
            os.makedirs(f'{D}/tmp', exist_ok=True); pickle.dump([(m.seq, m.hops) for (a, b, m) in self.parts], open(cp, 'wb'))
            base._frames.cache_clear(); import gc; gc.collect()
        self.hops = [h for (a, b, m) in self.parts for h in m.hops if a*24 <= h < b*24]
    def at(self, t): return next(m for (a, b, m) in self.parts[::-1] if t >= a-1e-6)
    def layer(self, t, X=None, Y=None): return self.at(t).layer(t, X, Y)
    def hop_dy(self, t): return self.at(t).hop_dy(t)
    def feet_x(self, al, Y=None): return self.parts[0][2].feet_x(al, Y)
    def clip(self, t):
        m = self.at(t); s0, seq = m._global_sequence(); i = min(len(seq)-1, max(0, int(t*24)-s0)); return seq[i][0]
    def _global_sequence(self): return True
BORNES = [0.0, T['bas'], T['milieu'], JUMPS['milieu'][1], T['haut'], JUMPS['haut'][1], T['horloge'], T['fin']]
MC = ParScene(BORNES, voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7, coupe_silence=True)
# réactions muettes dans les silences ajoutés : (début, clip ou pose fixe, image de départ, image de fin) ; fins dans RX_FIN
RX = [(35.62, 'classique_choc', 60, 125), (sh(46.84)-1.5, 'pose:reflechit', 0, 0)]
RX_FIN = [35.62+1.4, sh(46.84)]
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
