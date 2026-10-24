"""Krachs, épisode 2 : la bulle internet (2000). Décors cartoon rétro (Gemini), Mister Coin dynamique, courbe du Nasdaq en paysage.
usage : python3 kb.py png t1 t2 … | python3 kb.py seg out.mp4 f0 f1 | python3 kb.py info
Les temps T sont provisoires tant que la vraie voix n'est pas calée (VOICE)."""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))      # racine du dépôt
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from logo import logo_symbol
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from mister_coin import MisterCoin
D = os.path.dirname(os.path.abspath(__file__)); FPS = int(os.environ.get('FPS', 60)); NB = ' '
INK = '2A1C10'; CREAM = 'F7EDD8'; PAPER = 'FFF8EA'; RED = 'C8402F'; GREEN = '2E8B57'; GOLD = 'D79A2B'; WHITE = 'FFFFFF'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- voix et minutage ----------
TFILE = f'{D}/timing.json'
VOICE = f'{D}/voice_full.wav' if os.path.exists(f'{D}/voice_full.wav') else f'{D}/voice_placeholder.wav'
T = dict(intro=0.0, fall=46.45, s0=0.0, s1=1.5, s2=6.0, s3=7.4, s4=12.8, s5=15.1, s5n=19.6, s6=22.0, s7=24.5, s8=26.8, s9=29.5, s9e=32.4, s10=33.4, s11=37.0, s11n=38.6,
         s12=40.0, s12n=42.6, s13=43.8, s14=46.8, s14n=49.4, s15=51.4, end=54.5)
if os.path.exists(TFILE): T.update(json.load(open(TFILE)))
DUR = T['end']
CAPS = [(T['intro'], "Bonjour à tous et bienvenue dans [l'histoire de la semaine] !"), (T['s0'], "[216 euros]."), (T['s1'], "C'est ce qu'il restait de 1 000 euros placés dans le Nasdaq le [10 mars 2000]."),
        (T['s2'], "Retour en arrière."), (T['s3'], "Fin des années 90 : internet entre dans les foyers, et tout le monde veut [sa part]."),
        (T['s4'], "Les start-up entrent en Bourse [à la chaîne]."), (T['s5'], "En 1999, une nouvelle action gagne en moyenne [71 %] dès son premier jour."),
        (T['s6'], "Pourtant, [3 sur 4] perdent de l'argent."), (T['s7'], "Elles [brûlent] celui des investisseurs."),
        (T['s8'], "Puis la Fed relève ses taux, [encore et encore]."), (T['s9'], "L'argent devient cher, la confiance s'effondre : la bulle [éclate]."),
        (T['s10'], "Pets.com fait [faillite] neuf mois après son entrée en Bourse."), (T['s11'], "Même Amazon perd plus de [90 %]."),
        (T['s12'], "En deux ans et demi, le Nasdaq chute de [78 %]."), (T['s13'], "Il lui faudra [15 ans] pour retrouver son sommet."),
        (T['s14'], "Et pourtant, ces 1 000 euros valent aujourd'hui [4 526 euros]."), (T['s15'], "Et toi, tu aurais tenu [15 ans] ?")]
HL = {T['intro']: GOLD, T['s0']: RED, T['s1']: GOLD, T['s3']: GOLD, T['s4']: GOLD, T['s5']: GREEN, T['s6']: RED, T['s7']: RED, T['s8']: RED, T['s9']: RED,
      T['s10']: RED, T['s11']: RED, T['s12']: RED, T['s13']: GOLD, T['s14']: GREEN, T['s15']: GOLD}
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
def caption(c, words, hl, y=1760, size=44, a=1):
    """sous-titres sur bande sombre arrondie : lisibles sur tous les décors (clairs ou sombres)"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 880: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '1A120A', .62*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- éléments « papier » (style années 30 : crème, trait d'encre) ----------
def card(c, x, y, w, h, a=1, fill=PAPER, r=22, tilt=0.0):
    c.save(); c.translate(x, y); c.rotate(tilt)
    rr(c, -w/2+8, -h/2+10, w, h, r); col(c, '000000', .28*a); c.fill()
    rr(c, -w/2, -h/2, w, h, r); col(c, fill, .97*a); c.fill_preserve(); c.set_line_width(6); col(c, INK, a); c.stroke()
    c.restore()
def ink_text(c, s, x, y, size, color=INK, fam='a', align='c', a=1, track=0):
    text(c, s, x, y, fam, size, color, align, a, track)
def big_number(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0):
    """chiffre géant façon affiche : trait d'encre épais + couleur"""
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    w = tw(c, s, 'a', size)
    for dx, dy in ((7, 9),):
        text(c, s, dx, dy, 'a', size, '000000', 'c', .35*a)
    c.select_font_face('Anton'); c.set_font_size(size)
    ext = c.text_extents(s); c.move_to(-ext.x_advance/2, size*.36)
    c.text_path(s); c.set_line_width(14); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, INK, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def series_tag(c, a=1):
    card(c, 250, 120, 380, 64, a, fill=INK, r=32)
    ink_text(c, "KRACHS · ÉPISODE 2", 250, 121, 30, CREAM, 'xb', 'c', a, 3)

# ---------- décors ----------
@functools.lru_cache(maxsize=8)
def decor(name):
    im = Image.open(f'{D}/decors/{name}.jpg').convert('RGB').resize((W, H), Image.LANCZOS)
    return im
@functools.lru_cache(maxsize=4)
def decor_crash():
    im = decor('bourse'); im = ImageEnhance.Color(im).enhance(.25); im = ImageEnhance.Brightness(im).enhance(.62)
    a = np.asarray(im).astype(np.float32)*[1.0, .92, .9]; return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
@functools.lru_cache(maxsize=4)
def decor_hook():
    im = ImageEnhance.Brightness(decor('ciel')).enhance(.55); return im

# ---------- objets Gemini (fond vert détouré) ----------
@functools.lru_cache(maxsize=8)
def asset(name, h):
    a = np.asarray(Image.open(f'{D}/poses/{name}.png').convert('RGB')).astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = Image.fromarray((np.clip(1-(ks-25)/70, 0, 1)*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    a[..., 1] = np.where(ks > 0, np.maximum(R, B), G)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(al)
    im = im.crop(im.getbbox()); return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
def put_asset(cv, name, h, cx, base, a=1.0, shadow=True):
    im = asset(name, h); x, y = int(cx-im.width/2), int(base-im.height)
    if shadow:
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-im.width*.45, base-18, cx+im.width*.45, base+14), fill=int(130*a))
        cv.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v*a)))
    cv.alpha_composite(im, (x, y)); return x, y, im.size

# ---------- courbe du Nasdaq (clôtures annuelles + points clés, lissage monotone) ----------
PTS = [(1998.0, 2192.69), (1999.0, 4069.31), (2000.19, 5048.62), (2001.0, 2470.52), (2002.0, 1950.40), (2002.77, 1114.11), (2003.0, 1335.51),
       (2004.0, 2003.37), (2005.0, 2175.44), (2006.0, 2205.32), (2007.0, 2415.29), (2008.0, 2652.28), (2009.0, 1577.03), (2010.0, 2269.15),
       (2011.0, 2652.87), (2012.0, 2605.15), (2013.0, 3019.51), (2014.0, 4176.59), (2015.0, 4736.05), (2015.31, 5056.06), (2016.0, 5007.41),
       (2017.0, 5383.12), (2018.0, 6903.39), (2019.0, 6635.28), (2020.0, 8972.60), (2021.0, 12888.28), (2022.0, 15644.97), (2023.0, 10466.48),
       (2024.0, 15011.35), (2025.0, 19310.79), (2026.0, 23241.99), (2026.81, 26702.86)]
# NB : la valeur « au 1er janvier de l'année N » = clôture de fin d'année N-1
from scipy.interpolate import PchipInterpolator
_PX = np.array([p[0] for p in PTS]); _PY = np.array([p[1] for p in PTS]); NAS = PchipInterpolator(_PX, _PY)
def view(t):
    """cadrage de la courbe : (année gauche, année droite, valeur max visible)"""
    u = inout((t-T['s14']+.1)/1.3)
    return lerp(1998.0, 1998.0, u), lerp(2016.2, 2027.4, u), lerp(5900, 29500, u)
def to_screen(yr, v, t):
    y0, y1, vmax = view(t)
    x = 70+(yr-y0)/(y1-y0)*940; y = 1520-(v/vmax)*1020
    return x, y
def curve_poly(t, yr_end):
    xs = np.linspace(1998.0, yr_end, 500)
    return [to_screen(x, float(NAS(x)), t) for x in xs]
def draw_curve(cv, t, a=1.0, yr_end=2026.81):
    """terrain : sol sous la courbe (vert-brun, hachures d'encre), arête épaisse"""
    s, c = surface()
    pts = curve_poly(t, yr_end)
    c.move_to(pts[0][0], H); [c.line_to(x, y) for x, y in pts]; c.line_to(pts[-1][0], H); c.close_path()
    g = cairo.LinearGradient(0, 600, 0, H); g.add_color_stop_rgba(0, .55, .58, .33, a); g.add_color_stop_rgba(1, .30, .26, .16, a)
    c.set_source(g); c.fill_preserve(); c.save(); c.clip()
    c.set_line_width(2.2); col(c, INK, .22*a)
    for k in range(-40, 80):
        x0 = k*28; c.move_to(x0, H); c.line_to(x0+700, H-700); c.stroke()
    c.restore()
    c.new_path(); c.move_to(*pts[0]); [c.line_to(x, y) for x, y in pts[1:]]
    c.set_line_width(12); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, INK, a); c.stroke_preserve()
    c.set_line_width(5); col(c, 'E8D27A', a); c.stroke()
    cv.alpha_composite(to_img(s))
def slope_deg(yr, t):
    x1, y1 = to_screen(yr-.15, float(NAS(yr-.15)), t); x2, y2 = to_screen(yr+.15, float(NAS(yr+.15)), t)
    return math.degrees(math.atan2(y2-y1, x2-x1))

# ---------- Mister Coin ----------
ZC = .17
def mc_path(t):
    """position imposée pendant la courbe : il tombe du sommet de 2000 au creux de 2002, remonte jusqu'en 2015 puis jusqu'à aujourd'hui"""
    if not (T['s12']-.4 <= t < T['s15']-.25): return None
    if t < T['fall']: yr, walking, jump = 2000.19, 0.0, 0.0
    elif t < T['fall']+.5:                                   # chute dans le creux (silence après « 78 % »)
        u = (t-T['fall'])/.5; yr = lerp(2000.19, 2002.77, inout(u)); walking = 0.0; jump = 200*math.sin(math.pi*u)*(1-u)
    elif t < max(T['s13'], T['fall']+.5): yr, walking, jump = 2002.77, 0.0, 0.0
    elif t < T['s14']-.2:                                    # 15 ans de remontée à pied
        t0 = max(T['s13'], T['fall']+.5); u = (t-t0)/(T['s14']-.2-t0); yr = lerp(2002.77, 2015.31, u); walking = 1.0; jump = 0.0
    elif t < T['s14']+1.6:
        u = (t-(T['s14']-.2))/1.8; yr = lerp(2015.31, 2026.81, inout(u)); walking = .8; jump = 0.0
    else: yr, walking, jump = 2026.81, 0.0, 0.0
    x, y = to_screen(yr, float(NAS(yr)), t)
    x = min(x, 960)
    tilt = -clamp(slope_deg(yr, t), -35, 35)*.45 if walking else 0.0
    return (x, y+4, ZC, False, tilt, walking, jump)

PLACES = {'hook': (560, 1580, .26), 'salon': (330, 1450, .26), 'bourse': (560, 1560, .26), 'startup': (290, 1530, .26),
          'banque': (255, 1500, .26), 'crash': (800, 1540, .26, True), 'courbe': (180, 700, ZC), 'cta': (540, 1590, .26)}
ACTIONS = [(4.73, 5.28, 'abattu'), (5.28, 9.03, 'souci'), (9.05, 9.56, 'abattu'), (12.7, 13.7, 'point'), (24.01, 24.52, 'ravi'),
           (24.52, 26.66, 'souci'), (26.68, 27.18, 'inquiet'), (27.3, 28.3, 'point'), (28.85, 29.37, 'billets'),
           (29.37, 32.2, 'souci'), (32.22, 32.64, 'bulle'), (32.64, 35.0, 'souci'), (35.01, 35.42, 'bulle'), (36.3, 36.95, 'chute'),
           (37.0, 39.97, 'souci'), (39.99, 40.38, 'inquiet'), (40.38, 42.74, 'souci'), (42.76, 43.22, 'inquiet'),
           (43.22, 46.43, 'souci'), (46.45, 46.95, 'chute'), (49.11, 56.7, 'barbe')]   # barbe jusqu'à la fin : 15 ans ont passé
MC = MisterCoin(VOICE, PLACES, 'hook', actions=ACTIONS,
                sauts_de_place=[(T['s2']-.2, 'salon'), (T['s4']-.25, 'bourse'), (T['s6']-.25, 'startup'), (T['s8']-.25, 'banque'),
                                (T['s10']-.25, 'crash'), (T['s15']-.25, 'cta')],
                coucous=[(.15, 2.9)], danses=[(T['s5n']+.1, T['s6']-.6), (T['s14n']+.1, T['s15']-.5)], petits_sauts=[T['s9e']],
                bulles=[(14.25, 15.7, "Bip… krrr… connecté !"), (T['s4']+.25, T['s5']-.2, "Je veux ma start-up !"),
                        (T['s7']+.4, T['s8']-.3, "Ça chauffe bien !", 'droite'), (47.6, 48.9, "Encore loin ?", 'haut')],
                trajet=mc_path)

# ---------- scènes ----------
def scene_of(t):
    for name, a in (('cta', T['s15']), ('courbe', T['s12']), ('crash', T['s10']), ('banque', T['s8']), ('startup', T['s6']),
                    ('bourse', T['s4']), ('salon', T['s2']), ('hook', 0)):
        if t >= a-.05: return name
    return 'hook'
def background(t):
    sc = scene_of(t)
    if sc == 'hook': return decor_hook().copy()
    if sc in ('courbe', 'cta'): return decor('ciel').copy()
    if sc == 'crash': return decor_crash().copy()
    return decor(sc).copy()

def sHook(cv, c, t):
    k = t-T['s0']
    big_number(c, "216 €", 540, 640, 260, 'E0564A', 1.0, (1+.12*math.exp(-max(0, k)*8)*(k > 0)) if k > -1 else 1.0, -.04)
    k1 = t-T['s1']
    if k1 > 0:
        card(c, 540, 900, 820, 120, ease(k1/.3), tilt=.015)
        ink_text(c, "1 000 € PLACÉS LE 10 MARS 2000", 540, 902, 46, INK, 'a', 'c', ease(k1/.3))
    series_tag(c, ease((t-.3)/.4))
def sSalon(cv, c, t):
    k = t-T['s2']
    if k < .55:                                              # retour en arrière : bandes VHS
        u = k/.55; rng = np.random.default_rng(int(t*60))
        for i in range(14):
            y = rng.uniform(0, H); c.rectangle(0, y, W, rng.uniform(4, 22)); col(c, WHITE, .25*(1-u)); c.fill()
        ink_text(c, "◀◀", 150, 220, 90, WHITE, 'a', 'c', 1-u)
    card(c, 220, 300, 260, 130, ease((k-.3)/.3), fill=PAPER, tilt=-.05)
    ink_text(c, "1999", 220, 303, 86, RED, 'a', 'c', ease((k-.3)/.3))
def sBourse(cv, c, t):
    k = t-T['s4']
    card(c, 540, 330, 760, 110, ease(k/.3), tilt=-.012)
    ink_text(c, "ENTRÉES EN BOURSE À LA CHAÎNE", 540, 333, 44, INK, 'a', 'c', ease(k/.3))
    k5 = t-T['s5n']
    if k5 > -.1:
        big_number(c, "+71 %", 540, 640, 230, '4CC27A', ease((k5+.1)/.2), lerp(1.4, 1, back((k5+.1)/.45)), .03)
        card(c, 540, 850, 600, 96, ease((k5-.2)/.3), tilt=-.01)
        ink_text(c, "DÈS LE PREMIER JOUR (1999)", 540, 853, 40, INK, 'a', 'c', ease((k5-.2)/.3))
STOVE = (845, 1300)          # porte du poêle (objet Gemini posé à côté de Mister Coin)
def sStartup(cv, c, t):
    k = t-T['s6']
    put_asset(cv, 'poele', 600, 800, 1625)
    card(c, 400, 300, 560, 170, ease(k/.3), tilt=.02)
    ink_text(c, "3 SUR 4", 400, 278, 86, RED, 'a', 'c', ease(k/.3))
    ink_text(c, "PERDENT DE L'ARGENT", 400, 350, 36, INK, 'a', 'c', ease(k/.3))
    k7 = t-T['s7']
    if k7 > 0:                                               # billets qui volent jusque dans le poêle
        for i in range(9):
            u = (k7-i*.22)/.9
            if 0 < u < 1:
                x0, y0 = 420, 1290; x = lerp(x0, STOVE[0], u); y = lerp(y0, STOVE[1], u)-330*math.sin(math.pi*u)
                c.save(); c.translate(x, y); c.rotate(u*6+i); s_ = 1-.6*max(0, u-.75)/.25
                c.scale(s_, s_); rr(c, -46, -24, 92, 48, 6); col(c, '8FBF7A', 1); c.fill_preserve(); c.set_line_width(3); col(c, INK, 1); c.stroke()
                c.arc(0, 0, 13, 0, 6.3); c.set_line_width(3); c.stroke(); c.restore()
        f = clamp(k7/.4)*(1-clamp((k7-3)/.5))                # flammes plus vives
        g = cairo.RadialGradient(STOVE[0], STOVE[1], 10, STOVE[0], STOVE[1], 170); g.add_color_stop_rgba(0, 1, .7, .2, .55*f); g.add_color_stop_rgba(1, 1, .4, .1, 0)
        c.set_source(g); c.arc(STOVE[0], STOVE[1], 170, 0, 6.3); c.fill()
RATES = [(0.0, "4,75 %"), (1, "5,00 %"), (2, "5,25 %"), (3, "5,50 %"), (4, "5,75 %"), (5, "6,00 %"), (6, "6,50 %")]
def rate_at(t):
    k = t-T['s8']-.2; n = int(clamp(k/2.6)*6.999); return RATES[n][1], n
def bubble_r(t):
    k = t-T['s8']; return 90+170*inout(clamp(k/((T['s9e'])-T['s8'])))
def sBanque(cv, c, t):
    k = t-T['s8']
    card(c, 548, 660, 460, 270, ease(k/.3))                 # panneau posé sur le coffre gris du décor
    ink_text(c, "TAUX DE LA FED", 548, 585, 38, INK, 'a', 'c', ease(k/.3), 2)
    r, n = rate_at(t)
    big_number(c, r, 548, 675, 110, 'E0564A' if n >= 5 else GOLD, ease(k/.3), 1+.08*max(0, 1-((t-T['s8']-.2) % (2.6/6.999))*6) if n > 0 else 1)
    ink_text(c, "JUIN 1999 → MAI 2000", 548, 760, 28, INK, 'xb', 'c', ease(k/.3), 2)
    ke = t-T['s9e']; cx, cy = 560, 300
    if ke < 0:                                               # la bulle « .com » gonfle
        R = bubble_r(t); wob = 1+.03*math.sin(t*7)
        g = cairo.RadialGradient(cx-R*.3, cy-R*.35, R*.1, cx, cy, R)
        g.add_color_stop_rgba(0, 1, 1, 1, .55); g.add_color_stop_rgba(.7, .75, .9, 1, .18); g.add_color_stop_rgba(1, .6, .85, 1, .45)
        c.save(); c.translate(cx, cy); c.scale(wob, 1/wob); c.translate(-cx, -cy)
        c.arc(cx, cy, R, 0, 6.3); c.set_source(g); c.fill_preserve(); c.set_line_width(5); col(c, INK, .8); c.stroke()
        c.arc(cx-R*.42, cy-R*.42, R*.16, 0, 6.3); col(c, WHITE, .8); c.fill(); c.restore()
        ink_text(c, ".COM", cx, cy+4, int(R*.55), '2F6FB5', 'a', 'c', .9)
    elif ke < .5:                                            # éclatement : anneau + gouttes
        u = ke/.5; R = bubble_r(T['s9e']-1e-3)*(1+.6*u)
        c.arc(cx, cy, R, 0, 6.3); c.set_line_width(8*(1-u)+1); col(c, WHITE, 1-u); c.stroke()
        for i in range(16):
            ang = i/16*6.283; rr_ = R*(1+.4*u)
            c.arc(cx+math.cos(ang)*rr_, cy+math.sin(ang)*rr_+120*u*u, 10*(1-u)+2, 0, 6.3); col(c, 'BFE6FF', 1-u); c.fill()
        ink_text(c, "POP !", cx, cy, 140, INK, 'a', 'c', 1-u)
def sCrash(cv, c, t):
    k = t-T['s10']
    card(c, 470, 400, 800, 200, ease(k/.3), tilt=-.02)
    ink_text(c, "PETS.COM", 470, 365, 80, INK, 'a', 'c', ease(k/.3))
    ink_text(c, "FAILLITE 9 MOIS APRÈS SON ENTRÉE EN BOURSE", 470, 440, 30, RED, 'xb', 'c', ease(k/.3), 1)
    k2 = t-T['s11']
    if k2 > 0:
        card(c, 470, 720, 640, 250, ease(k2/.3), tilt=.025)
        ink_text(c, "AMAZON", 470, 650, 64, INK, 'a', 'c', ease(k2/.3))
        big_number(c, "−90 %", 470, 760, 140, 'E0564A', ease((k2-.15)/.2), lerp(1.3, 1, back((k2-.15)/.4)), .02)
def sCourbe(cv, c, t):
    yr_end = lerp(2016.0, 2026.81, inout((t-T['s14']+.1)/1.6)) if t > T['s14']-.1 else 2016.0
    draw_curve(cv, t, 1.0, yr_end)
    # repère : niveau du sommet de 2000, en pointillés jusqu'au retour de 2015
    xA, yA = to_screen(2000.19, 5048.62, t); xB, _ = to_screen(2015.31, 5056.06, t)
    a = clamp((t-T['s12'])/.4)*(1-clamp((t-T['s14'])/.5))
    c.set_dash([18, 14]); c.set_line_width(4); col(c, INK, .75*a); c.move_to(xA, yA); c.line_to(xB, yA); c.stroke(); c.set_dash([])
    if a > 0:
        card(c, xA+150, yA-62, 260, 64, a, tilt=-.02); ink_text(c, "SOMMET 2000", xA+150, yA-60, 30, INK, 'a', 'c', a, 1)
    k = t-T['s12n']
    if k > -.1 and t < T['s13']:
        big_number(c, "−78 %", 760, 420, 190, 'E0564A', ease((k+.1)/.2), lerp(1.4, 1, back((k+.1)/.45)), -.03)
        card(c, 760, 600, 470, 84, ease((k-.2)/.3)); ink_text(c, "EN 2 ANS ET DEMI", 760, 603, 38, INK, 'a', 'c', ease((k-.2)/.3))
    if T['s13']-.2 <= t < T['s14']+.3:                         # pancarte plantée sur la courbe : les années défilent
        a2 = ease((t-T['s13']+.2)/.3)*(1-ease((t-T['s14']-.0)/.3))
        u = clamp((t-max(T['s13'], T['fall']+.5))/(T['s14']-.2-max(T['s13'], T['fall']+.5))); yr = int(lerp(2002.77, 2015.31, u))
        gx, gy = to_screen(2011.6, float(NAS(2011.6)), t)
        x0, y0, (sw, sh_) = put_asset(cv, 'pancarte', 430, gx+20, gy+30, a2, shadow=False)
        bx, by = x0+sw*.5, y0+sh_*.33
        ink_text(c, str(yr), bx, by-14, 92, INK, 'a', 'c', a2)
        ink_text(c, f"{yr-2000} AN{'S' if yr-2000 > 1 else ''} APRÈS LE SOMMET", bx, by+62, 22, RED, 'xb', 'c', a2, 1)
    k14 = t-T['s14n']
    if k14 > -.1:
        big_number(c, "4 526 €", 430, 520, 170, '4CC27A', ease((k14+.1)/.2), lerp(1.4, 1, back((k14+.1)/.45)), -.03)
        card(c, 430, 690, 520, 84, ease((k14-.2)/.3)); ink_text(c, "AUJOURD'HUI (HORS DIVIDENDES)", 430, 693, 30, INK, 'a', 'c', ease((k14-.2)/.3))
def sCta(cv, c, t):
    draw_curve(cv, t, 1.0, 2026.81)
    s2, c2 = surface(); c2.rectangle(0, 0, W, H); col(c2, '000000', .35*clamp((t-T['s15'])/.4)); c2.fill(); cv.alpha_composite(to_img(s2))
    k = t-T['s15']
    big_number(c, "ET TOI,", 540, 430, 150, WHITE, ease(k/.3), 1.0, -.02)
    big_number(c, "TU AURAIS TENU 15 ANS ?", 540, 620, 92, 'F2C14E', ease((k-.4)/.3), lerp(1.3, 1, back((k-.4)/.4)), .01)
    series_tag(c, ease((k-.8)/.4))
SCENES = {'hook': sHook, 'salon': sSalon, 'bourse': sBourse, 'startup': sStartup, 'banque': sBanque, 'crash': sCrash, 'courbe': sCourbe, 'cta': sCta}
def transition(cv, t):
    """coupe + petit flash crème aux changements de décor"""
    for key in ('s2', 's4', 's6', 's8', 's10', 's12', 's15'):
        d = t-(T[key]-.05)
        if 0 <= d < .18:
            s, c = surface(); c.rectangle(0, 0, W, H); col(c, 'FFF6E0', .55*(1-d/.18)); c.fill(); cv.alpha_composite(to_img(s))

def frame(t):
    cv = background(t).convert('RGBA')
    s, c = surface()
    SCENES[scene_of(t)](cv, c, t)
    cv.alpha_composite(to_img(s))
    cv.alpha_composite(MC.layer(t))
    s2, c2 = surface()
    kk = cap_at(t)
    if kk is not None and t < DUR-1.0:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al)
    cv.alpha_composite(to_img(s2))
    transition(cv, t)
    return finish(cv, t, 5.0)

def events():
    ev = [(0.0, 'impact'), (T['s1'], 'low'), (T['s2'], 'swish'), (T['s4'], 'swish'), (T['s5n'], 'boom'), (T['s5n'], 'coins'), (T['s6'], 'swish'),
          (T['s7'], 'riser'), (T['s8'], 'swish'), (T['s9e'], 'impact'), (T['s10'], 'swish'), (T['s10'], 'thud'), (T['s11'], 'crash'),
          (T['s12'], 'swish'), (T['s12n'], 'impact'), (T['s14n'], 'boom'), (T['s14n'], 'coins'), (T['s15'], 'swish')]
    for i in range(1, 7): ev.append((T['s8']+.2+i*2.6/6.999, 'tick'))
    ev += [(b[0], 'pop') for b in MC.bulles]
    ev += [(m[0]+.05, 'swish') for m in MC.moves if m[4] == 'saut' and m[0] > .5]
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
