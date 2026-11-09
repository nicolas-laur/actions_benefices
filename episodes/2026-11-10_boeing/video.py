"""Vidéo « Boeing : de la confiance absolue aux portes qui s'envolent » (cartoon 1930 en Technicolor) : calage (voix transcrite mot à mot,
voix/mots_whisper.txt), sous-titres, plan des clips de Mister Coin. Le rendu est dans video_col.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 64.0; S.DUR = DUR
# plages de parole par phrase (début et fin = premier et dernier mot de la transcription)
CAPS_SRC = [((0.10, 3.88), "Comment l'avion le plus sûr du monde a-t-il pu perdre une [porte] en plein vol ?", GD),
    ((4.12, 6.65), "Pendant des décennies, les pilotes disaient :", GD),
    ((6.65, 8.88), "« If it's not [Boeing], I'm not going. »", GD),
    ((8.88, 12.76), "Coté à la Bourse de New York depuis [1962],", GD),
    ((12.76, 15.62), "Boeing bat son [record] en mars 2019 :", GD),
    ((15.62, 17.80), f"[387{NB}€] l'action.", GD),
    ((17.80, 22.32), "Mais pour rattraper Airbus, Boeing veut aller [vite] avec son 737 MAX.", GD),
    ((22.32, 25.20), "Un logiciel mal conçu fait [piquer] l'avion.", RD),
    ((25.20, 27.40), f"Deux crashs, [346{NB}morts].", RD),
    ((27.50, 30.20), f"Le MAX est [cloué au sol] pendant 20{NB}mois.", RD),
    ((30.20, 32.08), "Puis le Covid [vide le ciel] :", GD),
    ((32.08, 35.72), f"l'action perd près de [80{NB}%] et tombe à [89{NB}€].", RD),
    ((35.72, 38.40), "Et en janvier 2024, en plein vol,", GD),
    ((38.40, 42.12), "un panneau de porte d'un 737 MAX presque neuf [s'arrache].", RD),
    ((42.12, 44.36), "[4 boulons] n'avaient jamais été remis.", RD),
    ((44.36, 48.28), f"Aujourd'hui, l'action vaut encore [60{NB}% de moins] qu'à son record.", RD),
    ((48.28, 52.00), f"Fin octobre, elle a perdu près de [11{NB}%] en une seule journée :", RD),
    ((52.00, 53.60), "les livraisons prennent du [retard].", RD),
    ((53.60, 57.20), f"Pourtant, plus de [6{NB}300 avions] attendent d'être livrés.", GD),
    ((57.30, 58.43), "Un [record].", GD),
    ((58.43, 61.80), "Alors, Boeing : avion en [panne], ou bonne [affaire] ?", GD)]
C = [ab for ab, _, _ in CAPS_SRC]
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
for (a, b), txt, hl in CAPS_SRC:
    for (x0, x1, p) in _split(txt, a, b): CAPS.append((x0, x1, p, hl))
FEET = 1660
MC = VeoCoin([(0.0, 'classique_parle_question', 'voix'), (4.12, 'classique_parle_explique', 'voix'), (8.88, 'classique_parle_enthousiaste', 'voix'),
              (17.8, 'classique_parle_inquiet', 'voix'), (25.2, 'classique_parle_triste', 'voix'), (30.2, 'classique_parle_confidence', 'voix'),
              (35.72, 'classique_parle_explique', 'voix'), (44.36, 'classique_danse_parle_prudent', 'voix'), (53.6, 'classique_danse_parle_billets', 'voix'),
              (58.43, 'classique_danse_parle_swing', 'voix'), (61.9, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=200, lisse=True)
def euro(v): return f"{int(round(v)):,}".replace(',', NB)+NB+"€"
def count_to(v, u): return v*ease(u)
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
