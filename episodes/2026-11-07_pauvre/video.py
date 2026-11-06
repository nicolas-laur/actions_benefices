"""Vidéo « Pourquoi tu restes pauvre ? » : données de calage (voix réelle transcrite mot à mot, voix/mots_whisper.txt),
sous-titres, plan des clips de Mister Coin et bruitages. Le rendu (dessin animé 1930) est dans video_bw.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 83.4; S.DUR = DUR

# plages de parole, une par phrase (début de phrase = transcription, bornes = silences de la voix)
C = [(0.1, 1.32), (1.84, 4.26), (4.98, 8.48), (8.96, 10.5), (11.04, 13.48), (14.12, 15.08), (15.5, 17.38), (17.94, 19.5), (20.04, 21.64), (21.88, 23.22),
     (23.7, 26.76), (27.32, 28.28), (28.7, 29.26), (29.78, 32.54), (32.96, 35.72), (36.26, 39.74), (40.3, 41.32), (41.62, 42.8), (43.28, 46.8), (47.26, 51.02),
     (51.5, 54.4), (54.86, 57.66), (58.14, 62.44), (62.88, 65.22), (65.58, 68.16), (68.6, 72.38), (72.9, 75.96), (76.4, 78.0), (78.52, 80.64)]
CAPS_SRC = [(0, "Pourquoi tu restes [pauvre] ?", GD), (1, "Spoiler : ce n'est pas qu'une question de [salaire].", GD),
    (2, "En France, [un Français sur quatre] est à découvert presque tous les mois.", RD), (3, "En moyenne, dès [le 18].", RD),
    (4, "Écoute bien jusqu'à la fin, c'est peut-être [ton cas].", GD), (5, "[Erreur n° 1] :", RD), (6, "tu épargnes ce qui reste à la [fin du mois].", GD),
    (7, "Sauf qu'il ne reste [jamais rien].", RD), (8, "Les gens organisés font [l'inverse] :", GD), (9, "ils se paient [en premier].", GD),
    (10, "Un [virement automatique] le jour de la paie, et tu vis avec le reste.", GD), (11, "[Erreur n° 2] :", RD), (12, "ton [loyer].", GD),
    (13, "Le repère, c'est [un tiers] de ton salaire maximum.", GD), (14, "Avec 2 000 € nets, ça fait [667 €].", GD),
    (15, "Au-delà, chaque mois commence déjà [dans le rouge], et ça va être compliqué.", RD), (16, "[Erreur n° 3] :", RD), (17, "les [petites dépenses].", GD),
    (18, "Les Français paient en moyenne [72 € par mois] d'abonnements loisirs.", GD), (19, "Placés à 7 % pendant 30 ans, ça fait près de [88 000 €].", GD),
    (20, "Vérifie [combien tu paies] d'abonnements, et ceux qui sont inutiles.", GD), (21, "La règle simple, c'est [50 / 30 / 20].", GD),
    (22, "[50 %] pour l'essentiel, [30] pour tes envies, [20] pour ton avenir.", GD), (23, "Sur 2 000 €, ça fait [400 € par mois].", GD),
    (24, "En 30 ans, près de [490 000 €].", GD), (25, "Et si ton salaire ne couvre même pas l'essentiel, [le problème ne vient pas de toi].", GD),
    (26, "Commence par [10 € par mois] en investissement pour ton futur.", GD), (27, "Ce qui compte, c'est [l'habitude].", GD),
    (28, "Et toi, tu te paies [en premier] au début du mois ?", GD)]
def _split(txt, a, b, maxc=62):
    """phrase trop longue → morceaux équilibrés de ≤ 2 lignes, durée au prorata des caractères ; jamais de coupure dans un mot surligné"""
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
    for (x0, x1, p) in _split(txt.replace('2 000', '2 000').replace('88 000', '88 000').replace('490 000', '490 000'), a, b): CAPS.append((x0, x1, p, hl))

# ---------- Mister Coin : un clip différent par scène, il parle quand la voix parle ----------
FEET = 1660
COL_T = 80.75                                                  # fin : il retrouve ses couleurs pendant sa joie
MC = VeoCoin([(0.0, 'classique_parle_question', 'voix'), (4.6, 'classique_parle_inquiet', 'voix'), (14.0, 'classique_danse_parle_compte', 'voix'),
              (27.0, 'classique_parle_triste', 'voix'), (40.0, 'classique_danse_parle_billets', 'voix'), (54.6, 'classique_parle_explique', 'voix'),
              (68.4, 'classique_parle_confidence', 'voix'), (78.3, 'classique_danse_parle_swing', 'voix'), (80.7, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=200, lisse=True)

def euro(v): return f"{int(round(v, -3)):,}".replace(',', NB)+" €"
def count_to(v, u): return v*ease(u)
def events():
    """bruitages calés sur les apparitions (les scènes ajoutent les leurs dans video_bw.events)"""
    ev = [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)]
    return sorted(ev)
