"""Vidéo « Comment vivre comme un milliardaire sans presque payer d'impôt ? » (buy, borrow, die, 21/11/2026), cartoon 1930 en Technicolor :
calage de la voix (segments transcrits dans voix/segments.json, voix montée par voix_montage.py), sous-titres, plan des clips de Mister Coin.
Le rendu est dans video_col.py. Voix : voice_full.wav (48 kHz mono)."""
import os, sys, math, wave
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import NB, GD, GR, RD
from veo_coin import VeoCoin
from voix_montage import shift as sh
FPS = 60; VOICE = f'{D}/voice_full.wav'
with wave.open(VOICE) as w: DUR_VOIX = w.getnframes()/w.getframerate()
DUR = round(DUR_VOIX+3.0, 2); S.DUR = DUR
# sous-titres : (début, fin) dans la voix d'origine (voix/segments.json), texte réellement dit
SRC = [((0.04, 2.15), f"Comment vivre comme un [milliardaire]…", GD),
    ((2.44, 4.20), f"sans presque payer d'[impôt]{NB}?", GD),
    ((4.78, 7.63), f"Aux États-Unis, l'enquête [ProPublica] a fait le calcul{NB}:", GD),
    ((7.97, 10.6), f"en 5 ans, la fortune des 25 Américains les plus riches", GD),
    ((10.6, 14.22), f"a grimpé d'environ [365 milliards d'euros].", GD),
    ((14.80, 15.95), f"Leur impôt sur le revenu{NB}:", GD),
    ((16.37, 17.73), f"un peu plus de [12 milliards].", RD),
    ((18.18, 19.45), f"[3,4{NB}%].", RD),
    ((20.82, 22.50), f"Leur méthode tient en [trois mots]{NB}:", GD),
    ((22.90, 23.50), f"[Buy],", GD), ((23.60, 24.30), f"Buy, [borrow],", GD), ((24.41, 25.10), f"Buy, borrow, [die].", GD),
    ((25.44, 28.17), f"Un{NB}: acheter des actions et [ne jamais les vendre].", GD),
    ((28.50, 30.50), f"Pas de vente, [pas d'impôt] sur la plus-value.", GD),
    ((30.86, 33.91), f"Deux{NB}: [emprunter] en mettant ses actions en garantie.", GD),
    ((34.27, 36.70), f"Un prêt n'est [pas un revenu], donc pas d'impôt.", GD),
    ((37.11, 40.39), f"Exemple réel{NB}: [Larry Ellison], le fondateur d'Oracle.", GD),
    ((40.85, 43.60), f"[413 millions] de ses actions garantissent des prêts personnels,", GD),
    ((43.60, 46.74), f"soit environ [41,5 milliards d'euros].", GD),
    ((47.20, 51.22), f"Trois{NB}: au décès, les héritiers reçoivent les actions à leur [valeur du jour].", GD),
    ((51.48, 52.75), f"La plus-value est [effacée].", RD),
    ((53.04, 54.58), f"Il reste les [droits de succession]{NB}:", GD),
    ((54.91, 57.77), f"[40{NB}%] au-delà d'environ 13,5 millions d'euros.", GD),
    ((58.27, 58.95), f"Et en [France]{NB}?", GD),
    ((59.29, 62.79), f"Le [crédit lombard] existe, et la plus-value est aussi effacée au décès.", GD),
    ((63.04, 66.01), f"Mais les droits de succession montent jusqu'à [45{NB}%].", GD),
    ((66.45, 69.91), f"Et le 16 octobre, les députés ont rejeté la [taxe Zucman]{NB}:", GD),
    ((70.15, 73.18), f"[2{NB}% par an] sur les patrimoines de plus de 100 millions d'euros.", GD),
    ((73.70, 76.01), f"À ton échelle, [ne pas vendre] compte aussi.", GR),
    ((76.38, 79.70), f"Après 5 ans, ton [PEA] échappe à l'impôt sur le revenu,", GR),
    ((79.70, 82.60), f"mais pas aux [18,6{NB}%] de prélèvements sociaux,", GD),
    ((82.76, 84.65), f"que tu connais déjà si tu nous suis régulièrement.", GD),
    ((84.86, 87.05), f"Et ton capital continue de [composer].", GR),
    ((87.57, 89.69), f"Mais emprunter sur ses actions est [risqué]{NB}:", RD),
    ((89.91, 91.80), f"si elles chutent, la banque peut [vendre].", RD),
    ((92.07, 94.30), f"L'action Oracle a perdu [plus de la moitié] de sa valeur", RD),
    ((94.30, 96.59), f"depuis son sommet des 12 derniers mois.", RD),
    ((97.10, 98.90), f"Maintenant que tu sais tout,", GD),
    ((99.20, 100.45), f"qu'est-ce que tu penses de [tout ça]{NB}?", GD)]
CAPS = [(sh(a), sh(b), s_, hl) for (a, b), s_, hl in SRC[2:]]   # la question d'accroche est déjà écrite en grand à l'écran : pas de sous-titre doublé
# scènes (temps de la vidéo)
T = dict(chiffre=4.5, trois=sh(20.7), buy=sh(25.25), borrow=sh(30.7), ellison=sh(36.95), die=sh(47.05), france=sh(58.1), pea=sh(73.5), risque=sh(87.4), fin=sh(96.95))
FEET = 1650
EN, EX, QU, IN, CO, TR = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_inquiet', 'classique_parle_confidence', 'classique_parle_triste'
SW, CP, BI, PR = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent'
def _veo(nom):
    return nom if os.path.exists(f'{D}/../../mister_coin/veo/{nom}.mp4') else None
NEUTRE = _veo('classique_parle_neutre') or EX
MC = VeoCoin([(0.0, [QU], 'voix'), (T['chiffre'], [EX, CP], 'voix'), (T['trois'], [CO], 'voix'), (T['buy'], [EN], 'voix'), (T['borrow'], [BI], 'voix'),
              (T['ellison'], [CP, SW], 'voix'), (T['die'], [IN, TR], 'voix'), (T['france'], [NEUTRE, PR], 'voix'), (T['pea'], [EN, SW], 'voix'),
              (T['risque'], [PR, IN], 'voix'), (T['fin'], [QU], 'voix')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7, coupe_silence=True)
# réactions muettes jouées dans les silences (images f0 à f1 du clip, accélérées) : la banque lisse ne les gère pas, video_col les substitue
RX = [(sh(19.37)+.08, 'classique_choc', 56, 160), (sh(52.68)+.1, 'classique_facepalm', 70, 170), (DUR_VOIX+.1, 'classique_pouce', 60, 165)]
RX_FIN = [sh(20.82)-.1, sh(53.04)-.1, DUR-.05]
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
