"""Vidéo « Combien il faut gagner pour faire partie des 10 % les mieux payés ? » (24/11/2026), cartoon 1930 en Technicolor :
calage de la voix (segments transcrits dans voix/segments.json, voix montée par voix_montage.py), sous-titres, plan des clips de Mister Coin.
Le rendu est dans video_col.py. Voix : voice_full.wav (48 kHz mono)."""
import os, sys, wave
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import NB, GD, GR, RD
from veo_coin import VeoCoin
from voix_montage import shift as sh
FPS = 60; VOICE = f'{D}/voice_full.wav'
with wave.open(VOICE) as w: DUR_VOIX = w.getnframes()/w.getframerate()
DUR = round(DUR_VOIX+3.0, 2); S.DUR = DUR
# sous-titres : (début, fin) dans la voix d'origine (voix/segments.json), texte réellement dit
SRC = [((0.10, 3.90), f"Combien tu dois gagner pour faire partie des 10{NB}% les mieux payés de France{NB}?", GD),
    ((4.61, 6.90), f"Monte avec moi, on va voir à quel [étage] tu t'arrêtes.", GD),
    ((7.25, 10.33), f"On parle [salaire net] par mois, à temps plein, dans le privé.", GD),
    ((10.93, 11.59), f"[Rez-de-chaussée]{NB}:", GD),
    ((11.95, 14.03), f"le [Smic], environ 1{NB}500{NB}€.", GD),
    ((14.59, 15.26), f"Premier arrêt{NB}:", GD),
    ((15.55, 17.12), f"[2{NB}238{NB}€].", GD),
    ((17.47, 18.45), f"C'est la [médiane]{NB}:", GD),
    ((18.55, 20.36), f"la moitié des salariés [gagne moins] que ça.", GD),
    ((20.74, 21.62), f"On continue de [monter].", GD),
    ((22.02, 23.91), f"[4{NB}441{NB}€]{NB}:", GD),
    ((24.19, 27.09), f"à partir de là, tu fais partie des [10{NB}% les mieux payés].", GR),
    ((27.36, 29.10), f"À peine le [double] de la médiane.", GD),
    ((29.55, 30.19), f"Et tout en [haut]{NB}?", GD),
    ((30.66, 32.40), f"Pour entrer dans le [1{NB}%],", GD),
    ((32.45, 34.93), f"il faut [10{NB}552{NB}€] par mois.", GD),
    ((35.37, 38.35), f"[Presque 5 fois] la médiane, plus de 7 fois le Smic.", GD),
    ((38.91, 40.39), f"Mais le salaire [ne fait pas tout].", GD),
    ((40.70, 42.20), f"Sur une vie, ce qui compte,", GD),
    ((42.25, 45.19), f"c'est ce que tu [gardes] chaque mois et ce que tu en fais.", GR),
    ((45.76, 47.23), f"Et toi, tu es à quel [étage]{NB}?", GD)]
CAPS = [(sh(a), sh(b), s_, hl) for (a, b), s_, hl in SRC[1:]]   # la question d'accroche est déjà écrite en grand à l'écran : pas de sous-titre doublé
# trajets d'ascenseur (temps de la vidéo) : (début du moteur, ding d'arrivée, étage d'arrivée)
RIDES = [(sh(14.31)-.0+.25, sh(14.31)+1.32, 1), (sh(21.82)+.05, sh(21.82)+.88, 2), (sh(29.32)+.05, sh(29.32)+.88, 3)]
# scènes (temps de la vidéo)
T = dict(hall=7.37, smic=sh(10.85), cabine=sh(14.31)+.05, etage=sh(21.82)+.95, sommet=sh(29.32)+.95, pont=sh(38.91)-.2, fin=sh(45.76)-.25)
FEET = 1650
EN, EX, QU, IN, CO, TR = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_inquiet', 'classique_parle_confidence', 'classique_parle_triste'
SW, CP, BI, PR = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent'
def _veo(nom):
    return nom if os.path.exists(f'{D}/../../mister_coin/veo/{nom}.mp4') else None
NEUTRE = _veo('classique_parle_neutre') or CP
MC = VeoCoin([(0.0, [QU], 'voix'), (T['hall'], [EX], 'voix'), (T['cabine'], [NEUTRE], 'voix'), (T['etage'], [EN], 'voix'),
              (T['sommet'], [CO], 'voix'), (T['pont'], [PR, CO], 'voix'), (T['fin'], [QU], 'voix')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7, coupe_silence=True)
# réactions muettes jouées dans les silences (images f0 à f1 du clip, accélérées) : la banque lisse ne les gère pas, video_col les substitue
RX_MED = _veo('classique_reflechit'); RX_TOP = _veo('classique_vertige')
RX = [(sh(20.36)+.1, RX_MED or 'classique_montre_haut_droite', 40 if not RX_MED else 20, 180 if not RX_MED else 200),
      (sh(38.35)+.1, RX_TOP or 'classique_choc', 56 if not RX_TOP else 20, 160 if not RX_TOP else 200),
      (DUR_VOIX+.1, 'classique_pouce', 60, 165)]
RX_FIN = [sh(20.74)-.1, sh(38.91)-.1, DUR-.05]
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
