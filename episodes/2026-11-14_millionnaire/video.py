"""Vidéo « Combien placer par mois pour devenir millionnaire ? » (cartoon 1930 en Technicolor) : calage de la voix, sous-titres,
plan des clips de Mister Coin. Le rendu est dans video_col.py.
La voix brute (voix/voice_brut.wav, phrase « 193 000 € » réenregistrée dans voix/voice_brut_corrige.wav) reçoit deux silences ajoutés : 1,5 s après « par mois » (gros plan aux yeux en étoiles + « wow »)
et 1 s après « Presque cinq fois plus » (réaction de Mister Coin). voice_full.wav est la voix montée."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'
INS = [(3.35, 1.5), (15.1, .974), (34.6, 1.0)]           # décalages par rapport à la voix brute d'origine (temps, durée) : silence du gros plan,
                                                         # phrase « 193 000 € » réenregistrée (0,97 s plus longue), silence après « 5 fois plus »
def tm(t): return t+sum(d for (a, d) in INS if t > a)   # temps de la voix brute -> temps de la vidéo
DUR = 67.0; S.DUR = DUR
GP = (3.30, 4.72)                                        # gros plan aux yeux en étoiles (coupe franche aller et retour)
WOW = 3.40                                               # le « wow » démarre quand les étoiles s'allument
E = '€'
SRC = [((0.04, 1.63), "Comment devenir [millionnaire] ?", GD),
    ((2.00, 3.33), f"[402{NB}€] par mois.", GD),
    ((3.50, 6.00), "C'est tout ce qu'il te faut pour devenir [millionnaire].", GD),
    ((6.00, 10.30), "À une condition : commencer à [25 ans], et ne jamais t'arrêter.", GD),
    ((10.50, 14.97), f"Avec [7{NB}%] par an en moyenne, à 65 ans, tu as [ton million].", GD),
    ((15.00, 18.45), f"Et le plus fou : tu n'auras versé que [193{NB}000{NB}€].", GD),
    ((18.50, 21.45), f"Les [807{NB}000{NB}€] restants, ce sont les [intérêts composés] :", GD),
    ((21.50, 24.40), "tes gains qui produisent eux-mêmes des gains.", GD),
    ((24.50, 26.45), "Tu commences à [35 ans] ?", GD),
    ((26.50, 28.45), f"Il te faut [850{NB}€] par mois.", GD),
    ((28.53, 29.60), "Plus du [double].", GD),
    ((30.00, 30.95), "À [45 ans] ?", RD),
    ((31.00, 32.95), f"[1{NB}959{NB}€].", RD),
    ((33.00, 34.55), "Presque [5 fois plus].", RD),
    ((35.00, 38.45), "Chaque dizaine d'années d'attente [double], voire plus, l'effort à fournir.", GD),
    ((38.50, 42.40), f"Attention : le [PEA] est plein à [150{NB}000{NB}€] versés.", GD),
    ((42.50, 45.45), "Au-delà, il faudra une [assurance vie] ou un [compte-titres].", GD),
    ((45.50, 49.45), "Et un million dans 40 ans n'aura pas la valeur d'un [million d'aujourd'hui].", RD),
    ((49.50, 53.40), f"Avec 2{NB}% d'inflation par an, il en vaudra environ [450{NB}000{NB}€].", RD),
    ((53.50, 56.45), "Le meilleur moment pour commencer, c'était [il y a 10 ans].", GD),
    ((56.53, 59.45), "Le deuxième meilleur, c'est [aujourd'hui].", GD),
    ((59.50, 61.50), "Et toi, tu as commencé [à quel âge] ?", GD)]
CAPS_SRC = [((tm(a), tm(b)), s, h) for ((a, b), s, h) in SRC]
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
EN, EX, QU, IN, CO = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_inquiet', 'classique_parle_confidence'
SW, CP, BI, PR = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent'
# scènes : rayons 0-7,5 | chambre 7,5-11,95 | haricot 11,95-25,95 | gare 25,95-39,95 | banque 39,95-54,95 | haricot géant 54,95-fin
MC = VeoCoin([(0.0, [QU], 'voix'), (4.72, [EN], 'voix'), (7.5, [EX, SW], 'voix'), (11.95, [EN, BI, CP], 'voix'),
              (25.95, [EX, CP], 'voix'), (35.9, [IN, PR], 'voix'),
              (39.95, [EX, CO, PR], 'voix'), (54.95, [EN, SW], 'voix'), (64.3, 'classique_danse_joie_silence', 'une')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7)
def euro(v): return f"{int(round(v)):,}".replace(',', NB)+NB+"€"
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
