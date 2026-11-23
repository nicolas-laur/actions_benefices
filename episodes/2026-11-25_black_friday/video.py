"""Vidéo « Black Friday : bonne affaire ou marketing ? » (25/11/2026), cartoon 1930 en Technicolor :
calage de la voix (segments transcrits dans voix/segments.json, voix gardée telle quelle à la demande de Nicolas), sous-titres, plan des clips de Mister Coin.
Le rendu est dans video_col.py. Voix : voice_full.wav (48 kHz mono)."""
import os, sys, wave
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D); sys.path.insert(0, f'{D}/../../mister_coin')
import scenes as S
from scenes import NB, GD, GR, RD
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'
with wave.open(VOICE) as w: DUR_VOIX = w.getnframes()/w.getframerate()
DUR = round(min(80.0, DUR_VOIX+.8), 2); S.DUR = DUR                       # plafond de 80 s
def sh(t): return t                                                        # voix non retouchée
# sous-titres : (début, fin) dans la voix, texte réellement dit (la question d'accroche est écrite en grand : pas de sous-titre doublé)
CAPS = [(4.03, 6.37, f"Au départ, rien à voir avec les [bonnes affaires].", GD),
    (7.40, 9.45, f"Dans les années 60, à [Philadelphie],", GD),
    (9.55, 12.05, f"la [police] appelle ainsi le lendemain de Thanksgiving.", GD),
    (12.37, 14.55, f"[Foule], bouchons, journée noire.", GD),
    (14.89, 16.83, f"Les commerçants ont voulu le [rebaptiser].", GD),
    (17.07, 17.70, f"[Raté]{NB}!", GD),
    (17.88, 20.10, f"Le nom est resté, et il arrive en France", GD),
    (20.15, 21.64, f"vers [2013], dans le e-commerce.", GD),
    (22.02, 25.74, f"Et malgré la [hausse des prix], on dépense toujours plus.", GD),
    (26.09, 28.55, f"[Panier moyen]{NB}: 193{NB}€ en 2022,", GD),
    (28.60, 30.66, f"[236{NB}€] l'an dernier.", GD),
    (30.91, 34.26, f"Les prix ont pris 8{NB}% en 3 ans, le panier [22{NB}%].", GD),
    (34.75, 36.39, f"La beauté et le [high-tech] montent,", GD),
    (36.54, 38.09, f"la [mode], elle, recule.", GD),
    (38.53, 40.02, f"Mais ces promos sont-elles [vraies]{NB}?", GD),
    (40.43, 44.10, f"L'an dernier, la [Commission européenne] a contrôlé 314 sites{NB}:", GD),
    (44.50, 47.08, f"[30{NB}%] des promotions ne respectaient pas les règles.", GD),
    (47.54, 49.10, f"Pourtant, la règle est simple{NB}:", GD),
    (49.15, 52.00, f"le [prix barré] doit être le plus bas des 30 derniers jours.", GD),
    (52.31, 53.82, f"Alors pense comme un [investisseur].", GD),
    (54.24, 55.70, f"[Un]{NB}: fais ta liste avant,", GD),
    (55.84, 57.07, f"comme les actions que tu [surveilles].", GD),
    (57.34, 58.72, f"La [télévision] qu'il te faut,", GD),
    (58.89, 60.40, f"pas celle qu'on te pousse par la pub.", GD),
    (60.64, 62.63, f"[Deux]{NB}: vérifie l'historique du prix,", GD),
    (62.80, 63.92, f"comme le graphique d'une action.", GD),
    (64.28, 66.00, f"[−30{NB}%] sur un prix gonflé la veille,", GD),
    (66.05, 67.63, f"ce n'est pas une affaire.", GD),
    (67.89, 69.38, f"[Trois]{NB}: fixe ton budget,", GD),
    (69.60, 70.43, f"comme une allocation.", GD),
    (70.68, 72.40, f"[200{NB}€], et aucun compte à rebours", GD),
    (72.45, 73.84, f"ne décide à ta place.", GD),
    (74.08, 75.60, f"Une promo n'est une [bonne affaire]", GD),
    (75.65, 76.98, f"que si tu l'aurais achetée sans elle.", GD),
    (77.27, 78.97, f"Et toi, tu vas [craquer]{NB}?", GD)]
# scènes (temps de la vidéo)
T = dict(hall=21.85, rayon=38.30, enquete=52.15, vitrine=73.95)
FEET = 1650
EN, EX, QU, CO, PR = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_question', 'classique_parle_confidence', 'classique_danse_parle_prudent'
DOIGTS, LOUPE = 'classique_parle_compte_doigts', 'classique_loupe_parle'            # clips assis (jambes pendantes) : posés au bord du bureau
SW, CP, BI = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets'     # il marche sur place, de face, en parlant (travellings)
MC = VeoCoin([(0.0, [QU], 'voix'), (7.3, [EX], 'voix'), (T['hall'], [SW], 'voix'), (30.8, [CP], 'voix'), (T['rayon'], [CO], 'voix'),
              (T['enquete'], [DOIGTS], 'voix'), (61.1, [LOUPE], 'voix'), (67.75, [DOIGTS], 'voix'), (T['vitrine'], [PR], 'voix'), (77.15, [QU], 'voix')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7, coupe_silence=True)
ASSIS = (T['enquete'], T['vitrine'])                                       # passage assis : pieds pendants sous le bord du bureau
RX, RX_FIN = [], []                                                        # pas de silence de réaction (voix gardée telle quelle, 80 s maximum)
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
