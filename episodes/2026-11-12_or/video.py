"""Vidéo « L'or : ni propriétaire, ni prêteur » (cartoon 1930 en Technicolor) : calage (voix transcrite mot à mot, voix/mots_whisper.txt),
sous-titres, plan des clips de Mister Coin. Le rendu est dans video_col.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 83.8; S.DUR = DUR
def inv(t): return t
def tm(t): return t
# plages de parole par phrase (premier et dernier mot de la transcription)
CAPS_SRC = [((0.05, 5.10), f"Tout l'or extrait depuis le début de l'humanité tiendrait dans un cube de [22{NB}mètres] de côté.", GD),
    ((5.24, 7.85), "C'est pour ça qu'il vaut [si cher].", GD),
    ((8.04, 11.72), "Les plus vieux bijoux en or ont été retrouvés en Bulgarie, à [Varna].", GD),
    ((11.76, 13.39), f"Ils ont plus de [6{NB}000{NB}ans].", GD),
    ((13.60, 16.52), "Les premières pièces en or pur, on les doit au roi [Crésus],", GD),
    ((16.67, 19.00), f"en Lydie, il y a plus de [2{NB}500{NB}ans].", GD),
    ((19.24, 21.60), "D'où l'expression « [riche comme Crésus] ».", GD),
    ((21.80, 25.54), "Rare, impossible à fabriquer, il a longtemps servi de [monnaie] :", GD),
    ((25.76, 29.76), "jusqu'en [1971], le dollar s'échangeait contre de l'or.", GD),
    ((29.85, 33.57), f"Et chaque année, les mines n'ajoutent même pas [2{NB}%] au stock mondial.", GD),
    ((33.84, 36.45), "Aujourd'hui, ce sont les [États-Unis] qui en ont le plus :", GD),
    ((36.64, 38.08), f"plus de [8{NB}000{NB}tonnes].", GD),
    ((38.28, 41.40), f"La France est quatrième, avec [2{NB}400{NB}tonnes].", GD),
    ((41.48, 44.46), "Et les banques centrales en achètent [deux fois plus] qu'il y a dix ans.", GD),
    ((45.52, 48.24), "Mais l'or ne verse [ni dividende], [ni intérêt] :", RD),
    ((48.52, 50.74), "tu n'es [ni propriétaire], [ni prêteur].", GD),
    ((50.92, 54.02), "Tu paries seulement que quelqu'un te le rachètera [plus cher].", GD),
    ((54.28, 59.64), f"En 20{NB}ans, l'once est passée de 485{NB}€ à [plus de 3{NB}600{NB}€].", GD),
    ((59.69, 64.70), f"Mais sur plus d'un siècle, l'or n'a rapporté que [1,3{NB}%] par an après inflation,", GD),
    ((64.81, 66.68), f"contre [6,6{NB}%] pour les actions.", GD),
    ((66.92, 67.52), "Et [demain] ?", GD),
    ((67.76, 72.76), f"Les grandes banques visent entre [4{NB}800 et 5{NB}600{NB}€] l'once fin 2027.", GD),
    ((73.04, 74.94), "Ce sont des prévisions, [pas des promesses] :", GD),
    ((75.16, 78.22), f"l'or vaut déjà [20{NB}% de moins] qu'à son record de janvier.", RD),
    ((78.48, 81.82), "Alors l'or : [valeur refuge], ou [placement qui dort] ?", GD)]
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
FEET = 1650
# Mister Coin dynamique (méthode du 10/11) : plusieurs clips par scène, changement de geste pendant un petit saut dans les silences.
EN, EX, QU, IN, CO = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_inquiet', 'classique_parle_confidence'
SW, CP, BI, PR = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent'
MC = VeoCoin([(0.0, [QU, EN], 'voix'), (7.95, [EX, SW], 'voix'), (13.5, [EN, BI, SW], 'voix'), (21.65, [EX, CP], 'voix'),
              (33.7, [CP, EN, EX], 'voix'), (44.6, [CO, PR], 'voix'), (54.15, [EX, BI, CP], 'voix'), (66.8, [CO, PR, IN], 'voix'),
              (78.35, [QU, SW], 'voix'), (82.0, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=300, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7)
def euro(v): return f"{int(round(v)):,}".replace(',', NB)+NB+"€"
def count_to(v, u): return v*ease(u)
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
