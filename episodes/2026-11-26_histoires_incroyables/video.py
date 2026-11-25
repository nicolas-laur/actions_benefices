"""Vidéo « 3 histoires incroyables que tu ne connaissais peut-être pas ! » (26/11/2026), cartoon 1930 en Technicolor :
calage de la voix (segments transcrits dans voix/segments.json), trois silences de réaction ajoutés au montage, sous-titres, plan des clips de Mister Coin.
Le rendu est dans video_col.py. Voix d'origine : voice_full.wav (48 kHz mono) ; voix montée : voice_montage.wav (avec les silences)."""
import os, sys, wave
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D); sys.path.insert(0, f'{D}/../../mister_coin')
import scenes as S
from scenes import NB, GD
from veo_coin import VeoCoin
FPS = 60; SRC = f'{D}/voice_full.wav'; VOICE = f'{D}/voice_montage.wav'
# silences de réaction insérés dans la voix (temps de la voix d'origine, durée) : choc après « huit cents dollars », facepalm après « Refusé encore », rire après « fait faillite »
INS = [(23.85, 1.4), (42.48, 1.4), (62.80, 1.4)]
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
DUR = round(min(80.0, DUR_VOIX+.8), 2); S.DUR = DUR                       # plafond de 80 s
# sous-titres : (début, fin) dans la voix d'origine, texte réellement dit (l'accroche est écrite en grand : pas de sous-titre doublé)
_C = [(3.00, 4.62, f"Voici [3 histoires incroyables]"),
    (4.66, 6.18, f"que tu ne connaissais peut-être pas."),
    (6.51, 7.95, f"[Aime] et [enregistre] la vidéo."),
    (8.05, 9.62, f"Tu vas avoir envie de les raconter."),
    (10.19, 11.47, f"[1976]."),
    (11.79, 13.59, f"[Apple] naît avec trois fondateurs{NB}:"),
    (13.84, 16.65, f"Steve Jobs, Steve Wozniak et [Ronald Wayne]."),
    (17.00, 20.01, f"Wayne a [peur des dettes] de cette petite entreprise."),
    (20.33, 21.72, f"[12 jours] plus tard,"),
    (21.78, 23.64, f"il revend ses 10{NB}% pour [800{NB}dollars]."),
    (24.02, 27.54, f"Aujourd'hui, Apple vaut environ [5{NB}000 milliards de dollars]."),
    (28.02, 29.40, f"[1999]."),
    (29.66, 32.10, f"Deux étudiants, [Larry Page] et [Sergey Brin],"),
    (32.15, 34.25, f"proposent leur moteur de recherche"),
    (34.30, 35.78, f"à [Excite], un géant d'internet."),
    (36.23, 37.77, f"Prix{NB}: [1 million de dollars]."),
    (38.21, 38.71, f"[Refusé]."),
    (38.98, 41.03, f"Ils descendent à [750{NB}000]."),
    (41.41, 42.30, f"[Refusé encore]{NB}!"),
    (42.66, 44.45, f"Ce moteur, c'est [Google]."),
    (44.55, 47.36, f"Sa maison mère vaut aujourd'hui [plus de 3{NB}000 milliards]."),
    (47.77, 48.34, f"[2000]."),
    (48.61, 51.58, f"[Netflix] loue des DVD par la poste et perd de l'argent."),
    (51.97, 54.05, f"Ses fondateurs proposent à [Blockbuster],"),
    (54.10, 55.55, f"le roi de la location vidéo,"),
    (55.60, 57.27, f"de les racheter pour [50 millions]."),
    (57.61, 59.92, f"Le patron refuse, [presque en riant]."),
    (60.42, 62.59, f"[10 ans] plus tard, Blockbuster fait [faillite]."),
    (62.98, 66.0, f"Netflix vaut aujourd'hui [près de 5{NB}000 fois] ce prix."),
    (66.09, 68.22, f"Une action, c'est un [morceau d'entreprise]."),
    (68.51, 70.24, f"Eux l'ont laissé filer pour [presque rien]."),
    (70.64, 71.95, f"Et toi, quelle entreprise"),
    (72.00, 73.50, f"tu [regretterais] de ne pas avoir achetée{NB}?")]
CAPS = [(sh(a), sh(b), s_, GD) for (a, b, s_) in _C]
# scènes (temps de la vidéo) : un décor par histoire, retour au prêteur sur gages pour la chute
T = dict(garage=10.0, bibliotheque=29.25, cinema=50.4, fin=70.1)
FEET = 1650
EN, EX, QU, CO = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_confidence'
DOIGTS, LOUPE = 'classique_parle_compte_doigts', 'classique_loupe_parle'            # clips assis (jambes pendantes) : posés au bord du comptoir du prêteur
SW, CP, BI, PR = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent'   # il marche de face en parlant (travellings)
PLAN = [(0.0, [DOIGTS], 'voix'), (T['garage'], [EX], 'voix'), (sh(17.0), [CO], 'voix'), (sh(24.0), [EN], 'voix'),
        (T['bibliotheque'], [SW], 'voix'), (sh(38.9), [CP], 'voix'), (sh(42.6), [BI], 'voix'),
        (T['cinema'], [PR], 'voix'), (sh(51.9), [SW], 'voix'), (sh(57.5), [BI], 'voix'),
        (T['fin'], [LOUPE], 'voix')]
class ParScene:
    """une banque VeoCoin par scène : le clip change net au changement de décor (pendant le saut d'un décor à l'autre), au lieu d'attendre un silence"""
    def __init__(self, bornes, **kw):
        self.parts = []; base = None
        for a, b in zip(bornes, bornes[1:]+[DUR+1]):
            pl = [p for p in PLAN if a-.01 <= p[0] < b-.01]; m = VeoCoin(pl, **kw)
            if base is None: base = m
            else: m._frames, m._feat = base._frames, base._feat                 # images des clips partagées entre les scènes (sinon 5 copies en mémoire)
            self.parts.append((a, b, m))
        import pickle, hashlib                                                    # séquences calculées une fois et gardées sur disque (le calcul charge tous les clips : 3 Go)
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
MC = ParScene([0.0, T['garage'], T['bibliotheque'], T['cinema'], T['fin']], voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5,
              silence_min=7, coupe_silence=True, boucle=(SW, CP, BI, PR))
# réactions muettes dans les silences ajoutés : (début, clip, image de départ, image de fin), fins dans RX_FIN
RX = [(23.72, 'classique_choc', 60, 125), (43.80, 'classique_facepalm', 78, 150), (65.50, 'classique_rire', 40, 112)]
RX_FIN = [25.32, 45.35, 67.10]
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
