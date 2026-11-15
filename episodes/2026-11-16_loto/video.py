"""Vidéo « Le Loto toute ta vie contre la même somme placée » (cartoon 1930 en Technicolor) : calage de la voix, sous-titres,
plan des clips de Mister Coin. Le rendu est dans video_col.py. Voix : voice_full.wav (48 kHz mono, sans montage)."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; VOICE_RAW = f'{D}/voix/voice_orig.wav'
import wave
def _d(p):
    with wave.open(p) as w: return w.getnframes()/w.getframerate()
import json
_J = json.load(open(f'{D}/voix/accroche.json')); HA, HB, CUT = _J['A'], _J['B'], _J['CUT']
# ligne de temps : 0-HA ouverture sur la foule (« S'enrichir en jouant au Loto ? Vraiment ? ») ; HA-HB scène d'ouverture du tabac (temps d'origine 0-CUT,
# étirés) sous « Jouer au Loto toute ta vie… qui finit le plus riche ? » ; après HB, la voix d'origine à partir de CUT
def to_raw(T): return None if T < HA else (T-HA)*CUT/(HB-HA) if T < HB else T-HB+CUT
def from_raw(t): return HA+t*(HB-HA)/CUT if t < CUT else t-CUT+HB
def tm(t): return t
DUR_RAW = 60.4; DUR = HB+DUR_RAW-CUT; S.DUR = DUR_RAW
_O = HA-2.82                                             # décalage entre l'enregistrement de l'accroche et la vidéo
HOOK_CAPS = [((_O+.1, _O+1.62), f"[S'enrichir] en jouant au [Loto]{NB}?"), ((_O+1.72, HA), f"[Vraiment]{NB}?"),
             ((HA+.16, _O+6.0), "Jouer au [Loto] toute ta vie, ou bien [placer] le même montant"),
             ((_O+6.0, _O+7.2), "chaque semaine en [bourse]."), ((_O+7.2, HB), f"Qui finit le plus [riche]{NB}?")]
ZOOM = (18.75, 22.75)                                    # plongée dans la foule des 19 068 840 joueurs (remplace le décor)
SRC = [((5.00, 7.20), f"Une grille coûte [2,20{NB}€].", GD),
    ((7.20, 10.80), f"Tu joues à chaque tirage, le lundi, le mercredi et le samedi{NB}:", GD),
    ((10.80, 12.66), f"[6,60{NB}€] par semaine.", GD),
    ((12.66, 16.40), f"De 25 à 65 ans, ça fait près de [14{NB}000{NB}€].", GD),
    ((16.40, 19.00), f"Tes chances de décrocher le [jackpot]{NB}?", GD),
    ((19.00, 22.00), f"[Une sur 19 millions], à chaque grille.", RD),
    ((22.00, 27.00), f"Même en jouant pendant 40 ans, tu as à peine [une chance sur 3{NB}000] de le gagner une seule fois.", RD),
    ((27.11, 28.45), f"Et sur 100{NB}€ joués,", RD),
    ((28.48, 32.00), f"la Française{NB}des{NB}Jeux n'en reverse qu'environ [54] aux gagnants.", RD),
    ((32.00, 34.60), f"En moyenne, tu perds donc plus de [6{NB}000{NB}€].", RD),
    ((34.60, 39.00), f"Maintenant, place ces mêmes 6,60{NB}€ par semaine, à [7{NB}%] par an.", GD),
    ((39.00, 42.00), f"À 65 ans, tu as environ [71{NB}000{NB}€].", GD),
    ((42.00, 43.95), f"Tu n'as versé que 14{NB}000{NB}€.", GD),
    ((44.00, 46.00), f"Les [intérêts composés] ont fait le{NB}reste.", GD),
    ((46.00, 49.00), f"Le Loto te vend un [rêve] à une chance sur 19 millions.", RD),
    ((49.00, 53.00), f"Le placement ne fait pas rêver, mais il [travaille pour toi] chaque semaine.", GD),
    ((53.06, 57.00), f"Jouer pour le plaisir, pourquoi pas{NB}? Mais ce n'est [pas un placement].", GD),
    ((57.00, 59.00), f"Et toi, tu joues au [Loto]{NB}?", GD)]
CAPS_SRC = SRC
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
# scènes : tabac 0-16,4 | tirage 16,4-34,6 (plongée 18,75-22,6) | machine 34,6-46 | verger 46-fin
MC = VeoCoin([(0.0, [QU, EX, CP], 'voix'), (16.4, [IN, PR, EX], 'voix'), (34.6, [EN, BI, CP], 'voix'),
              (46.0, [CO, EX, SW], 'voix'), (59.05, 'classique_danse_joie_silence', 'une')],
             voix=VOICE_RAW, duree=DUR_RAW, x=540, pieds=FEET, largeur_piece=170, lisse=True, variete=1.5, silence_min=7, coupe_silence=True)
def euro(v): return f"{int(round(v)):,}".replace(',', NB)+NB+"€"
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
