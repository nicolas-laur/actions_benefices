"""Vidéo « Comment commencer à t'enrichir ? » (cartoon 1930 en couleurs) : calage (voix transcrite mot à mot, voix/mots_whisper.txt),
sous-titres, plan des clips de Mister Coin. Le rendu est dans video_col.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 70.6; S.DUR = DUR
C = [(0.06, 1.48), (1.84, 4.38), (4.66, 5.08), (6.12, 7.9), (8.42, 14.26), (14.94, 18.16), (18.52, 21.52), (22.58, 23.64), (24.2, 27.26),
     (27.7, 28.04), (28.52, 29.58), (30.04, 32.64), (33.08, 36.0), (36.26, 37.3), (37.78, 39.28), (39.72, 40.02), (40.52, 42.5),
     (42.92, 47.9), (48.38, 50.64), (51.18, 54.16), (54.64, 58.08), (58.32, 60.24), (60.64, 63.08), (63.48, 65.32), (65.78, 68.08)]
CAPS_SRC = [(0, "Comment commencer à [t'enrichir] ?", GD), (1, "[Trois étapes], et la première va te surprendre.", GD), (2, "[Un] :", GD),
    (3, "arrête de laisser [dormir] ton argent.", GD), (4, "Ton Livret A rapporte [1,7 %], alors que les prix ont augmenté de [3,4 %] en un an.", RD),
    (5, "Le gouvernement vient d'annoncer une hausse du [taux] et du [plafond] pour février,", GD),
    (6, "mais les premières estimations le placent autour de [2,5 %] :", GD), (7, "toujours [sous l'inflation].", RD),
    (8, "Garde [3 à 6 mois] de dépenses de côté, pas plus.", GD), (9, "[Deux] :", GD), (10, "regarde [autour de toi].", GD),
    (11, "Ton téléphone, tes baskets, ton café du matin.", GD), (12, "Derrière chaque produit, il y a une [entreprise cotée] en bourse.", GD),
    (13, "Tu es son [client]…", GD), (14, "Pourquoi ne pas devenir son [actionnaire] ?", GD), (15, "[Trois] :", GD),
    (16, "investis un peu, mais [tous les mois].", GD), (17, "Avec la même somme chaque mois, tu achètes [plus de parts] quand la bourse baisse, et moins quand elle monte.", GD),
    (18, "Tu [lisses] ton prix d'entrée, sans chercher le bon moment.", GD), (19, "[100 € par mois] sur un ETF monde, dans un PEA :", GD),
    (20, "à 7 % par an, en 30 ans, tu verses [36 000 €]…", GD), (21, "et tu en as près de [122 000 €] !", GD),
    (22, "Le meilleur moment pour commencer, c'était [il y a 10 ans].", GD), (23, "Le deuxième meilleur, c'est [aujourd'hui].", GD),
    (24, "Et toi, de quelle marque aimerais-tu être [actionnaire] ?", GD)]
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
    for (x0, x1, p) in _split(txt.replace('36 000', '36 000').replace('122 000', '122 000').replace('100 €', '100 €'), a, b): CAPS.append((x0, x1, p, hl))
FEET = 1660
MC = VeoCoin([(0.0, 'classique_parle_question', 'voix'), (4.5, 'classique_parle_explique', 'voix'), (14.8, 'classique_parle_inquiet', 'voix'),
              (24.0, 'classique_danse_parle_prudent', 'voix'), (27.5, 'classique_parle_enthousiaste', 'voix'), (36.1, 'classique_parle_confidence', 'voix'),
              (39.5, 'classique_danse_parle_compte', 'voix'), (51.0, 'classique_danse_parle_billets', 'voix'), (60.44, 'classique_parle_explique', 'voix'),
              (65.6, 'classique_danse_parle_swing', 'voix'), (68.3, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=200, lisse=True)
def euro(v): return f"{int(round(v, -3)):,}".replace(',', NB)+" €"
def count_to(v, u): return v*ease(u)
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
