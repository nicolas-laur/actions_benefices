"""Vidéo « Action, obligation, fonds euros : propriétaire ou prêteur ? » (cartoon 1930 en Technicolor) : calage (voix transcrite mot à mot,
voix/mots_whisper.txt), sous-titres, plan des clips de Mister Coin. Le rendu est dans video_col.py."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import ease, clamp, GD, GR, RD, OR, CY, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'
# Montage du 10/11 : passage « fonds euros » retiré (accroche et bloc de 11 s). La voix d'origine (voix/voice_full_v1_avec_fonds_euros.wav)
# est coupée aux plages CUTS ; les scènes gardent leurs temps d'origine (t_orig), la vidéo est en temps de sortie (t).
CUTS = [(2.0, 3.4), (39.6, 49.6)]; DUR_O = 65.5
def inv(to):   # temps d'origine -> temps de sortie (un instant coupé tombe sur le point de coupe)
    d = 0.0
    for a, b in CUTS:
        if to >= b: d += b-a
        elif to > a: return a-d
    return to-d
def tm(t):     # temps de sortie -> temps d'origine
    return t+sum(b-a for a, b in CUTS if t >= inv(a))
def in_cut(to): return any(a < to < b for a, b in CUTS)
DUR = inv(DUR_O); S.DUR = DUR
# plages de parole par phrase (début et fin = premier et dernier mot de la transcription)
CAPS_SRC = [((0.10, 3.72), "Action, obligation…", GD),
    ((4.12, 5.50), "tu sais vraiment ce que tu [achètes] ?", GD),
    ((6.68, 9.30), "Imagine une [boulangerie] qui veut ouvrir une deuxième boutique.", GD),
    ((9.68, 11.56), "Pour trouver l'argent, elle a [deux solutions].", GD),
    ((12.22, 14.46), "Un : elle te vend une [part] de la boulangerie.", GD),
    ((14.82, 16.96), "C'est une [action] : tu deviens [propriétaire].", GD),
    ((17.42, 19.88), "Si elle cartonne, tu touches une part des [bénéfices],", GD),
    ((20.02, 22.24), "le [dividende], et ta part prend de la valeur.", GD),
    ((22.68, 25.06), "Mais si elle fait [faillite], tu peux tout perdre.", RD),
    ((25.54, 27.50), "Deux : elle t'[emprunte] de l'argent.", GD),
    ((27.78, 30.04), "C'est une [obligation] : tu deviens [prêteur].", GD),
    ((30.50, 33.10), "Elle te verse des [intérêts fixes], puis te rembourse à la fin.", GD),
    ((33.54, 35.46), "Moins de risque, mais [pas de jackpot].", GD),
    ((35.84, 39.36), f"L'État fait pareil : il emprunte sur 10{NB}ans à [plus de 4{NB}%].", GD),
    ((49.72, 52.06), "Sur le long terme, la différence est [énorme] :", GD),
    ((52.38, 57.90), f"aux États-Unis, depuis 1900, les actions ont rapporté [6,6{NB}%] par an après inflation.", GD),
    ((58.34, 60.18), f"Les obligations, [1,6{NB}%].", GD),
    ((60.62, 63.42), "Alors toi : plutôt [propriétaire], ou [prêteur] ?", GD)]
CAPS_SRC = [((inv(a), inv(b)), txt, hl) for (a, b), txt, hl in CAPS_SRC]
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
MC = VeoCoin([(inv(a), clip, m) for a, clip, m in [(0.0, 'classique_parle_question', 'voix'), (6.6, 'classique_parle_explique', 'voix'), (12.2, 'classique_parle_enthousiaste', 'voix'),
              (22.6, 'classique_parle_inquiet', 'voix'), (25.4, 'classique_parle_confidence', 'voix'), (30.4, 'classique_danse_parle_compte', 'voix'),
              (35.7, 'classique_parle_explique', 'voix'), (49.6, 'classique_danse_parle_billets', 'voix'),
              (60.5, 'classique_danse_parle_swing', 'voix'), (63.6, 'classique_danse_joie_silence', 'une')]],
             voix=VOICE, duree=DUR, x=300, pieds=FEET, largeur_piece=170, lisse=True)
def euro(v): return f"{int(round(v)):,}".replace(',', NB)+NB+"€"
def count_to(v, u): return v*ease(u)
def events(): return sorted([(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)])
