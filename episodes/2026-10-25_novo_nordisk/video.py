"""Novo Nordisk (Ozempic) : laboratoire high-tech épuré (4 salles Gemini animées), Mister Coin qui grossit puis maigrit.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from mister_coin import MisterCoin
import decor_anim as A
FPS = int(os.environ.get('FPS', 60)); NB = ' '
INK = '0E2B2E'; TEAL = '13A39A'; TEAL2 = '7FE3DA'; RED = 'E0473C'; GREEN = '2DB36F'; WHITE = 'FFFFFF'; PAPER = 'F7FBFB'; GOLD = 'E2A72E'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 65,8 s + passage « chiffres » inséré à 59,8 s) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(intro=0.0, prog=2.22, celebre=3.59, ozem=6.23, depart=7.42, mais=12.13, perdent=14.75, y2021=16.4, moy=20.31,
         ruee=23.16, reseaux=24.39, y2023=27.84, danemark=31.88, regime=34.72, auregime=36.43, m74=37.44,
         pourquoi=41.35, lilly=42.35, lilly2=44.84, decoit=47.48, m20=50.22, prix=52.83, recul=56.4,
         pourtant=60.05, ventes=63.28, eur41=66.58, benef=68.56, bourse=71.39, onze=75.01,
         maigrir=77.32, actionnaires=79.1, toi=80.65, achet=81.35, end=83.7)
if os.path.exists(f'{D}/timing.json'): T.update(json.load(open(f'{D}/timing.json')))
DUR = T['end']
CAPS = [(T['intro'], "Bonjour à tous et bienvenue !"), (T['prog'], "Aujourd'hui au programme :"), (T['celebre'], "le médicament [le plus célèbre] du monde."),
        (T['ozem'], "[Ozempic]."), (T['depart'], "Au départ, un traitement contre [le diabète], fabriqué par le danois Novo Nordisk."),
        (T['mais'], "Mais les patients remarquent un effet inattendu :"), (T['perdent'], "ils [perdent du poids]."),
        (T['y2021'], "En 2021, sa version [Wegovy] est autorisée contre l'obésité :"), (T['moy'], "en moyenne, [15 %] du poids en moins !"),
        (T['ruee'], "C'est [la ruée]."), (T['reseaux'], "Les réseaux sociaux s'emballent, les pharmacies sont [en rupture]…"),
        (T['y2023'], "En 2023, Novo Nordisk devient l'entreprise [la plus chère d'Europe]."), (T['danemark'], "Elle vaut plus que toute [l'économie du Danemark] !"),
        (T['regime'], "Puis l'action se met…"), (T['auregime'], "[au régime]."), (T['m74'], "[−74 %] depuis son sommet de juin 2024."),
        (T['pourquoi'], "Pourquoi ?"), (T['lilly'], "D'abord, l'américain [Eli Lilly] fait mieux :"), (T['lilly2'], "son traitement fait perdre [encore plus de poids]."),
        (T['decoit'], "Ensuite, le nouveau médicament de Novo [déçoit] :"), (T['m20'], "[−20 %] en une seule journée."),
        (T['prix'], "Et aux États-Unis, [les prix baissent] sous la pression du gouvernement."), (T['recul'], "Pour la première fois, Novo Nordisk prévoit [des ventes en recul]."),
        (T['pourtant'], "Pourtant, Novo Nordisk reste [une machine à cash] :"), (T['ventes'], "[309 milliards] de couronnes de ventes en 2025,"),
        (T['eur41'], "environ [41 milliards d'euros],"), (T['benef'], "et près de [14 milliards d'euros] de bénéfice."),
        (T['bourse'], "En Bourse, elle ne vaut plus qu'environ [150 milliards d'euros]…"), (T['onze'], "à peine [11 fois] ses bénéfices."),
        (T['maigrir'], "Le médicament fait toujours maigrir…"), (T['actionnaires'], "surtout [les actionnaires]."),
        (T['toi'], "Et toi,"), (T['achet'], "tu [achèterais] Novo Nordisk à ce prix-là ?")]
HL = {T['celebre']: TEAL, T['ozem']: TEAL, T['depart']: TEAL, T['perdent']: GREEN, T['y2021']: TEAL, T['moy']: GREEN, T['ruee']: GREEN, T['reseaux']: RED,
      T['y2023']: GREEN, T['danemark']: GREEN, T['auregime']: RED, T['m74']: RED, T['lilly']: RED, T['lilly2']: RED, T['decoit']: RED, T['m20']: RED,
      T['prix']: RED, T['recul']: RED, T['pourtant']: GREEN, T['ventes']: GREEN, T['eur41']: GREEN, T['benef']: GREEN, T['bourse']: TEAL, T['onze']: TEAL,
      T['actionnaires']: RED, T['achet']: TEAL}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1770, size=44, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 880: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '0B2124', .7*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- éléments graphiques (cartes blanches épurées, liseré bleu-vert) ----------
def card(c, x, y, w, h, a=1, accent=TEAL, tilt=0.0):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt)
    rr(c, -w/2+6, -h/2+10, w, h, 22); col(c, '0B2124', .18*a); c.fill()
    rr(c, -w/2, -h/2, w, h, 22); col(c, PAPER, .96*a); c.fill()
    rr(c, -w/2, -h/2, 12, h, 6); col(c, accent, a); c.fill()
    c.restore()
def big(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s)
    c.move_to(-ext.x_advance/2+5, size*.36+7); c.text_path(s); col(c, '0B2124', .25*a); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(12); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, WHITE, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def tag(c, s, x, y, color, a=1, size=30, fg=WHITE):
    if a <= 0: return
    w = tw(c, s, 'xb', size, 2)+56; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, color, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=16)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def put_emoji(cv, ch, x, y, size, k):
    if k <= 0 or not os.path.exists(EMOJI_FONT): return
    s = back(k/.35, 2.2); e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))

# ---------- écran de la salle de contrôle ----------
CURVE = [(2024.48, 1033.2), (2024.70, 930), (2024.96, 875), (2024.975, 700), (2025.20, 600), (2025.40, 520), (2025.565, 485), (2025.575, 380),
         (2025.80, 405), (2026.05, 350), (2026.09, 288), (2026.14, 245), (2026.30, 228), (2026.55, 252), (2026.81, 264.75)]
SX0, SY0, SX1, SY1 = A.SCREEN
def screen_bg(c, a):
    rr(c, SX0, SY0, SX1-SX0, SY1-SY0, 10); col(c, '0B2A2E', .9*a); c.fill()
    c.set_line_width(1); col(c, TEAL2, .12*a)
    for x in range(int(SX0)+40, int(SX1), 60): c.move_to(x, SY0+8); c.line_to(x, SY1-8); c.stroke()
    for y in range(int(SY0)+30, int(SY1), 50): c.move_to(SX0+8, y); c.line_to(SX1-8, y); c.stroke()
def scanlines(c, t, a):
    y = SY0+((t*140) % (SY1-SY0)); g = cairo.LinearGradient(0, y-40, 0, y+4)
    g.add_color_stop_rgba(0, .5, .9, .85, 0); g.add_color_stop_rgba(1, .5, .9, .85, .12*a); c.rectangle(SX0, y-40, SX1-SX0, 44); c.set_source(g); c.fill()
def curve_xy(yr, v):
    x0, x1, y0, y1 = SX0+70, SX1-60, SY0+95, SY1-55
    return x0+(yr-2024.4)/(2026.9-2024.4)*(x1-x0), y1-(v/1100)*(y1-y0)
def sCurve(c, t, a):
    screen_bg(c, a); scanlines(c, t, a)
    text(c, "NOVO NORDISK · ACTION (COURONNES DANOISES)", SX0+40, SY0+42, 'xb', 22, TEAL2, 'l', .9*a, 2)
    u = inout((t-T['m74']-.1)/2.4)
    if u > 0:
        from scipy.interpolate import PchipInterpolator
        f = PchipInterpolator([p[0] for p in CURVE], [p[1] for p in CURVE])
        y_end = lerp(2024.48, 2026.81, u); xs = np.linspace(2024.48, y_end, 160)
        pts = [curve_xy(x, float(f(x))) for x in xs]
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]
        c.set_line_width(7); col(c, RED, a); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
        c.arc(*pts[-1], 9, 0, 6.3); col(c, WHITE, a); c.fill()
        px, py = curve_xy(2024.48, 1033.2)
        tag(c, "SOMMET · JUIN 2024 · 1 033", px+150, py-28, TEAL, a*ease((t-T['m74'])/.3), 22)
        if u >= 1:
            ex, ey = pts[-1]; k = t-T['m74']-2.5
            tag(c, "22 OCT. 2026 · 264,75", ex-150, ey+40, RED, a*ease(k/.3), 22)
    k = t-T['m74']-.4
    if k > 0: big(c, "−74 %", 830, 645, 140, RED, a*ease(k/.25), lerp(1.35, 1, back(k/.45)))
def sFigures(c, t, a):
    screen_bg(c, a); scanlines(c, t, a)
    text(c, "NOVO NORDISK · LES CHIFFRES", SX0+40, SY0+42, 'xb', 22, TEAL2, 'l', .9*a, 2)
    rows = [(T['ventes'], "VENTES 2025", "309 MD DKK", "41,4 MD€", GREEN), (T['benef'], "BÉNÉFICE NET 2025", "102 MD DKK", "13,7 MD€", GREEN),
            (T['bourse'], "VALEUR EN BOURSE", "≈ 1 110 MD DKK", "149 MD€", TEAL2)]
    for i, (t0, lab, v1, v2, cl) in enumerate(rows):
        u = ease((t-t0)/.35)
        if u <= 0: continue
        y = SY0+120+i*82
        text(c, lab, SX0+50, y, 'xb', 24, WHITE, 'l', .85*u, 2); text(c, v1, SX1-300, y, 'xb', 28, WHITE, 'r', .7*u)
        text(c, v2, SX1-50, y, 'a', 50, cl, 'r', u)
        c.set_line_width(1.5); col(c, WHITE, .12*u); c.move_to(SX0+50, y+34); c.line_to(SX1-50, y+34); c.stroke()
    k = t-T['onze']
    if k > 0:
        big(c, "× 11", 630, SY1-80, 110, TEAL2, a*ease(k/.25), lerp(1.3, 1, back(k/.4)))
        text(c, "LES BÉNÉFICES 2025", 790, SY1-92, 'xb', 22, WHITE, 'l', a*ease((k-.2)/.3), 1)
        text(c, "(recul prévu en 2026)", 790, SY1-60, 'b', 20, TEAL2, 'l', a*ease((k-.2)/.3))
def sQuestion(c, t, a):
    screen_bg(c, a); scanlines(c, t, a)
    k = t-T['toi']
    big(c, "ET TOI,", 628, SY0+95, 92, WHITE, a*ease(k/.3))
    kb = t-T['achet']
    big(c, "TU ACHÈTERAIS", 628, SY0+205, 78, TEAL2, a*ease(kb/.3), lerp(1.25, 1, back(kb/.4)))
    big(c, "À CE PRIX-LÀ ?", 628, SY0+300, 78, TEAL2, a*ease((kb-.15)/.3), lerp(1.25, 1, back((kb-.15)/.4)))

# ---------- Mister Coin ----------
def largeur(t):
    if t < T['y2023']-.5: return 1.0
    if t < T['y2023']: return lerp(1.0, 1.32, inout((t-T['y2023']+.5)/.5))
    if t < T['auregime']: return 1.32
    if t < T['auregime']+.7:                                   # il « dégonfle » avec un petit rebond
        u = (t-T['auregime'])/.7; return lerp(1.32, .58, inout(u))-.06*math.sin(math.pi*u)
    return .58
PLACES = {'labo': (560, 1655, .30), 'prod': (790, 1655, .30, True), 'ctrl': (300, 1665, .30), 'ess': (790, 1665, .30, True), 'ctrl2': (300, 1665, .30)}
# Mister Coin ne se déforme plus : il passe aux dessins « gros » puis « mince » et y reste (une seule silhouette par séquence)
ACTIONS = [(5.83, 6.23, 'ravi'), (9.4, 10.4, 'point'), (15.81, 16.4, 'ravi'), (20.4, 21.4, 'thumb'), (22.76, 23.16, 'ravi'),
           (27.36, 36.10, 'gros'), (36.10, 36.80, 'pique'), (36.80, 46.9, 'mince'), (46.9, 47.48, 'mince_abattu'), (47.48, 52.29, 'mince'),
           (52.29, 52.83, 'mince_abattu'), (52.83, 59.52, 'mince'), (59.52, 60.05, 'mince_abattu'), (60.05, 80.11, 'mince'),
           (80.11, 84.0, 'mince_abattu')]
SCN = [(0, 'labo'), (T['ruee'], 'prod'), (T['regime'], 'ctrl'), (T['pourquoi'], 'ess'), (T['pourtant'], 'ctrl2')]
MC = MisterCoin(VOICE, PLACES, 'labo', actions=ACTIONS,
                sauts_de_place=[(a-.25, p) for a, p in SCN[1:]], coucous=[(.1, 1.8)], petits_sauts=[T['moy']+.1],
                bulles=[(T['danemark']+.1, T['danemark']+2.0, "Je me sens à l'étroit…", 'gauche'),
                        (T['lilly2']+.05, T['lilly2']+1.9, "Même pas jaloux…", 'gauche'),
                        (T['onze']+.05, T['onze']+1.6, "C'est les soldes ?", 'droite')])

# ---------- scènes ----------
def room_at(t):
    r = 'labo'
    for a, p in SCN:
        if t >= a: r = p
    return r
ROOM = {'labo': lambda t: A.labo(t), 'prod': lambda t: A.production(t), 'ctrl': lambda t: A.controle(t), 'ess': None, 'ctrl2': lambda t: A.controle(t)}
def room_img(r, t):
    if r == 'ess':
        al = clamp((t-T['m20'])/.3)*(1-clamp((t-T['prix']-.5)/.5)); return A.essais(t, al)
    return ROOM[r](t)
def room_start(r): return dict((p, a) for a, p in SCN)[r]
def room_end(r):
    starts = [a for a, _ in SCN]+[DUR]; i = [p for _, p in SCN].index(r); return starts[i+1]
def sLabo(c, cv, t):
    tag(c, "ACTION −74 %", 900, 120, RED, 1-ease((t-T['ozem']+.3)/.3), 28)              # chiffre choc visible dès l'image 0
    if t < T['ozem']-.15:
        k = t-T['prog']; card(c, 540, 420, 860, 300, ease(k/.3))
        text(c, "AUJOURD'HUI AU PROGRAMME", 540, 330, 'xb', 28, TEAL, 'c', ease(k/.3), 3)
        k2 = t-T['celebre']
        for i, l in enumerate(("LE MÉDICAMENT LE PLUS", "CÉLÈBRE DU MONDE")):
            text(c, l, 540, 410+i*82, 'a', 76, INK, 'c', ease((k2-i*.15)/.3))
        return
    if t < T['y2021']-.15:
        k = t-T['ozem']; card(c, 540, 360, 820, 230, ease(k/.3))
        big(c, "OZEMPIC", 540, 330, 120, TEAL, ease(k/.25), lerp(1.3, 1, back(k/.4)))
        text(c, "CONTRE LE DIABÈTE · NOVO NORDISK (DANEMARK)", 540, 435, 'xb', 26, INK, 'c', ease((t-T['depart'])/.3), 1)
        k3 = t-T['perdent']
        if k3 > -.2:
            card(c, 540, 640, 640, 120, ease((k3+.2)/.3), GREEN, -.02)
            text(c, "EFFET INATTENDU : PERTE DE POIDS", 540, 642, 'xb', 32, INK, 'c', ease((k3+.2)/.3), 1)
        return
    k = t-T['y2021']; card(c, 540, 380, 860, 250, ease(k/.3))
    text(c, "2021 · WEGOVY", 540, 320, 'a', 84, TEAL, 'c', ease(k/.3))
    text(c, "AUTORISÉ CONTRE L'OBÉSITÉ", 540, 420, 'xb', 32, INK, 'c', ease((k-.3)/.3), 2)
    km = t-T['moy']
    if km > -.1:
        big(c, "−15 %", 540, 680, 180, GREEN, ease((km+.1)/.25), lerp(1.35, 1, back((km+.1)/.45)))
        text(c, "DU POIDS EN MOYENNE", 540, 820, 'xb', 32, INK, 'c', ease((km-.2)/.3), 2)
def sProd(c, cv, t):
    k = t-T['ruee']
    if t < T['y2023']-.15:
        big(c, "C'EST LA RUÉE", 540, 330, 120, TEAL, ease(k/.25), lerp(1.3, 1, back(k/.4)))
        kr = t-T['reseaux']
        if kr > 0:
            card(c, 540, 520, 700, 110, ease(kr/.3)); text(c, "RÉSEAUX SOCIAUX EN FOLIE", 600, 522, 'xb', 34, INK, 'c', ease(kr/.3), 1)
            put_emoji(cv, '📱', 245, 520, 70, kr)
        ks = t-T['reseaux']-1.4
        if ks > 0:
            c.save(); c.translate(560, 700); c.rotate(-.1); s_ = lerp(1.5, 1, back(ks/.35)); c.scale(s_, s_)
            c.set_line_width(7); col(c, RED, ease(ks/.2)); rr(c, -300, -55, 600, 110, 16); c.stroke()
            text(c, "RUPTURE DE STOCK", 0, 2, 'a', 72, RED, 'c', ease(ks/.2)); c.restore()
        return
    k = t-T['y2023']; card(c, 540, 400, 880, 280, ease(k/.3), GOLD)
    text(c, "2023 · N°1 EN EUROPE", 540, 330, 'a', 76, INK, 'c', ease(k/.3))
    text(c, "428 MILLIARDS DE DOLLARS EN BOURSE (SEPT. 2023)", 540, 420, 'xb', 26, INK, 'c', ease((k-1.5)/.3), 1)
    kd = t-T['danemark']
    if kd > 0:
        text(c, "PLUS QUE TOUTE L'ÉCONOMIE DU DANEMARK", 560, 490, 'xb', 28, GREEN, 'c', ease(kd/.3), 1)
        put_emoji(cv, '🇩🇰', 540, 640, 110, kd)
def sCtrl(c, cv, t):
    a = ease((t-T['regime'])/.4)
    screen_bg(c, a) if t < T['m74'] else sCurve(c, t, a)
    if t < T['m74']:
        scanlines(c, t, a); text(c, "NOVO NORDISK · ACTION (COURONNES DANOISES)", SX0+40, SY0+42, 'xb', 22, TEAL2, 'l', .9*a, 2)
        ka = t-T['auregime']
        if ka > 0: big(c, "AU RÉGIME", 628, 700, 130, TEAL2, ease(ka/.25), lerp(1.3, 1, back(ka/.4)))
        if T['auregime']-.6 < t < T['auregime']+1.2: put_emoji(cv, '💉', 790, 1330, 80, t-T['auregime']+.6)
def sEss(c, cv, t):
    k = t-T['pourquoi']
    if t < T['lilly']-.1:
        big(c, "POURQUOI ?", 540, 430, 150, INK, ease(k/.25), lerp(1.3, 1, back(k/.4))); return
    items = [(T['lilly'], T['lilly2'], "1 · ELI LILLY FAIT MIEUX", "SON TRAITEMENT FAIT PERDRE PLUS DE POIDS", RED),
             (T['decoit'], T['m20'], "2 · LE NOUVEAU MÉDICAMENT DÉÇOIT", "−20 % EN UNE JOURNÉE (DÉC. 2024)", RED),
             (T['prix'], T['recul'], "3 · PRIX AMÉRICAINS EN BAISSE", "VENTES 2026 PRÉVUES EN RECUL (−5 À −13 %)", RED)]
    for i, (t0, t1, h, s_, cl) in enumerate(items):
        u = ease((t-t0)/.35)
        if u <= 0: continue
        y = 230+i*190; card(c, 540, y, 900, 160, u, cl)
        text(c, h, 125, y-30, 'a', 54, INK, 'l', u)
        text(c, s_, 125, y+40, 'xb', 26, cl, 'l', ease((t-t1)/.3), 1)
    if T['m20']-.05 < t < T['prix']: big(c, "−20 %", 820, 760, 130, RED, ease((t-T['m20'])/.2), lerp(1.4, 1, back((t-T['m20'])/.4)), .05)
def sCtrl2(c, cv, t):
    a = ease((t-T['pourtant'])/.4)
    if t < T['maigrir']-.1:
        sFigures(c, t, a)
        if T['pourtant'] <= t < T['ventes']:
            big(c, "UNE MACHINE À CASH", 628, 720, 92, GREEN, ease((t-T['pourtant']-.6)/.3), lerp(1.3, 1, back((t-T['pourtant']-.6)/.4)))
            put_emoji(cv, '💰', 628, 590, 90, t-T['pourtant']-.8)
    elif t < T['toi']-.1:
        screen_bg(c, 1); scanlines(c, t, 1)
        big(c, "−74 %", 628, 640, 170, RED, 1.0)
        ka = t-T['actionnaires']
        text(c, "SURTOUT LES ACTIONNAIRES", 628, 790, 'xb', 34, WHITE, 'c', ease(ka/.3), 2)
    else: sQuestion(c, t, 1)
    if t > T['achet']+.4:
        al = ease((t-T['achet']-.4)/.4)
        c.push_group(); logo_symbol(c, 500, SY1-38, 40); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 530, SY1-38, 'b', 26, WHITE, 'l', al)
SCENE = {'labo': sLabo, 'prod': sProd, 'ctrl': sCtrl, 'ess': sEss, 'ctrl2': sCtrl2}

def room_frame(r, t):
    """décor animé + travelling avant propre à la salle"""
    im = room_img(r, t)
    cy = 820 if r in ('ctrl', 'ctrl2') else 950
    return A.camera(im, t, room_start(r), room_end(r), 1.0, 1.05, 560, cy)
def frame(t):
    r = room_at(t); ts = room_start(r)
    bg = room_frame(r, t)
    if r != 'labo' and t-ts < .5 and r != 'ctrl2':                # glissement latéral d'une salle à l'autre
        prev = [p for a, p in SCN if a < ts][-1]; u = inout((t-ts)/.5)
        old = room_frame(prev, t); cv = Image.new('RGBA', (W, H)); cv.paste(old, (int(-W*u), 0)); cv.paste(bg, (int(W*(1-u)), 0)); bg = cv
    elif r == 'ctrl2' and t-ts < .5:                              # même salle : simple fondu de l'écran
        pass
    cv = bg.convert('RGBA')
    s, c = surface(); SCENE[r](c, cv, t); cv.alpha_composite(to_img(s))
    ch = MC.layer(t); cv.alpha_composite(A.reflection(ch, 1665)); cv.alpha_composite(ch)
    cv = A.atmosphere(cv, t)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, TEAL), a=al)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'swish'), (T['celebre'], 'impact'), (T['ozem'], 'swish'), (T['perdent'], 'pop'), (T['y2021'], 'swish'), (T['moy'], 'boom'),
          (T['ruee'], 'swish'), (T['reseaux'], 'pop'), (T['reseaux']+1.4, 'thud'), (T['y2023'], 'swish'), (T['danemark'], 'coins'),
          (T['regime'], 'swish'), (T['auregime'], 'pop'), (T['m74']+.4, 'impact'), (T['m74']+.1, 'low'), (T['pourquoi'], 'swish'),
          (T['lilly'], 'pop'), (T['decoit'], 'pop'), (T['m20'], 'crash'), (T['prix'], 'pop'), (T['pourtant'], 'swish'), (T['pourtant']+.6, 'coins'),
          (T['ventes'], 'tick'), (T['benef'], 'tick'), (T['bourse'], 'tick'), (T['onze'], 'glint'), (T['actionnaires'], 'thud'),
          (T['toi'], 'swish'), (T['achet'], 'pop'), (T['achet']+.4, 'click')]
    ev += [(b[0], 'pop') for b in MC.bulles]
    return sorted(ev)

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
