"""Spot publicitaire Instagram « Actions Bénéfices » (abonnés) : données de calage (voix transcrite mot à mot, voix/mots_whisper.txt),
sous-titres, plan des clips de Mister Coin. Le rendu (noir et blanc puis Technicolor) est dans video_bw.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 19.2; S.DUR = DUR
C = [(0.04, 2.74), (3.08, 3.88), (4.22, 6.38), (6.84, 8.14), (8.48, 13.7), (14.02, 14.62), (14.96, 15.62), (15.84, 16.76)]
# v2 : « Rassure-toi, c'est normal. » coupé dans la voix (3,98 → 6,01 s de l'original) pour que l'explosion de couleurs arrive à 7,5 s
CAPS_SRC = [(0, "L'économie, la bourse, les [finances personnelles]…", GD), (1, "Tu n'y comprends [rien] ?", RD),
    (2, "Personne ne te les a jamais expliquées [simplement].", GD), (3, "Moi, c'est [Mister Coin] !", GD),
    (4, "Chaque jour, je te propose [une minute] pour comprendre l'argent, l'économie et comment fonctionne le monde.", GD),
    (5, "[Sans jargon].", GD), (6, "[Abonne-toi] !", GD), (7, "On commence [aujourd'hui] !", GD)]
def _split(txt, a, b, maxc=62):
    plain = lambda x: len(x.replace('[', '').replace(']', ''))
    n = max(1, math.ceil(plain(txt)/maxc)); words = txt.split(' ')
    if n == 1: return [(a, b, txt)]
    target = plain(txt)/n; parts = []; cur = ''
    for w in words:
        if cur and plain(cur) >= target*.92 and cur.count('[') == cur.count(']') and len(parts) < n-1: parts.append(cur); cur = w
        else: cur = (cur+' '+w).strip()
    parts.append(cur); L = [plain(p) for p in parts]; tot = sum(L); out = []; t = a
    for p, l in zip(parts, L): d = (b-a)*l/tot; out.append((t, t+d, p)); t += d
    return out
CAPS = []
for i, txt, hl in CAPS_SRC:
    a, b = C[i]
    for (x0, x1, p) in _split(txt, a, b): CAPS.append((x0, x1, p, hl))
FEET = 1660
BURST = 7.46                                                    # « Mister Coin » : tout passe en couleurs
COL_T = BURST
MC = VeoCoin([(0.0, 'classique_parle_question', 'voix'), (3.0, 'classique_parle_inquiet', 'voix'), (4.06, 'classique_parle_confidence', 'voix'),
              (6.56, 'classique_parle_enthousiaste', 'voix'), (8.36, 'classique_danse_parle_swing', 'voix'), (13.96, 'classique_parle_explique', 'voix'),
              (16.96, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=200, lisse=True)
def euro(v): return f"{int(round(v, -3)):,}".replace(',', NB)+" €"
def count_to(v, u): return v*ease(u)
def events():
    return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
