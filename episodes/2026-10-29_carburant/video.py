"""Carburant : où part l'argent d'un plein de gazole ? Station-service néo-rétro de nuit, néons rouges.
Vue du ciel (voix off), descente de caméra jusqu'à la pompe, Mister Coin classique (clips Veo) ;
le compteur de la pompe défile au fil des postes, la jauge de décomposition se remplit à gauche.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
FPS = int(os.environ.get('FPS', 60)); NB = '\u00a0'
WHITE = 'FFFFFF'; INK = '120A10'; NEON = 'FF2D55'; NEON2 = 'FFB3C2'; GOLD = 'F2B53A'; GREEN = '2DB36F'; GREY = '9AA0AA'
C_PET, C_TRA, C_ACC, C_TVA = 'F08C2A', '2F8FE8', 'E8344A', '9B5CF6'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 58 s + 1 s de silence inséré à 3,25 s pour la descente) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(vo=0.0, cent=4.35, prix=5.99, prend=9.15, deux=11.13, alors=12.88, abord=14.82, c53=16.96, fevrier=18.34, ensuite=22.39, c14=24.57,
         station=25.63, etat=29.30, accise=30.77, c30=33.11, tva=34.11, c20=35.05, caroui=36.06, taxe=38.02, total=39.23, seul=42.34,
         paradoxe=44.66, an=45.71, auj=49.06, c42=49.76, nonpas=51.02, plus=52.65, flambe=53.96, fin=55.96, quand=57.29, end=59.7)
if os.path.exists(f'{D}/timing.json'): T.update(json.load(open(f'{D}/timing.json')))
DUR = T['end']
T_DESC, T_LAND = 3.25, 4.33          # plongée vers la station, puis Mister Coin se pose
CAPS = [(T['vo'], "Je vais te révéler ce qu'on ne te dit pas forcément sur [le prix du carburant]."), (3.3, ""),
        (T['cent'], "[118 euros] !"), (T['prix'], "C'est le prix d'un plein de [50 litres] de gazole en ce moment."),
        (T['prend'], "On prend le [gazole] pour notre démonstration :"), (T['deux'], "[2,36 €] le litre."),
        (T['alors'], "Alors, où part [ton argent] ?"), (T['abord'], "D'abord, le [pétrole] et son raffinage :"), (T['c53'], "[53 euros]."),
        (T['fevrier'], "Et depuis février, la marge des raffineurs a été [multipliée par six]."),
        (T['ensuite'], "Ensuite, le [transport] et la station :"), (T['c14'], "[14 euros]."),
        (T['station'], "Et la station, elle, ne garde [qu'1 à 4 euros] sur ton plein."),
        (T['etat'], "Et puis il y a [l'État]."), (T['accise'], "[L'accise], l'ancienne TICPE :"), (T['c30'], "[30 euros]."),
        (T['tva'], "Et la [TVA] :"), (T['c20'], "[20 euros]."), (T['caroui'], "Car oui, tu paies de la TVA… [sur une taxe] !"),
        (T['total'], "Au total, l'État encaisse [50 euros] sur ton plein."), (T['seul'], "À lui seul, c'est le [plus gros gagnant]."),
        (T['paradoxe'], "Le [paradoxe] ?"), (T['an'], "Il y a un an, les taxes pesaient [54 %] du prix."), (T['auj'], "Aujourd'hui, [42 %]."),
        (T['nonpas'], "Non pas parce que l'État prend moins, il encaisse [même plus],"), (T['flambe'], "mais parce que le pétrole [a flambé]."),
        (T['fin'], "Maintenant, tu comprendras tout quand tu iras faire [ton plein] d'essence !")]
HL = {T['vo']: NEON, T['cent']: NEON, T['prix']: NEON, T['prend']: GOLD, T['deux']: GOLD, T['alors']: NEON, T['abord']: C_PET, T['c53']: C_PET,
      T['fevrier']: C_PET, T['ensuite']: C_TRA, T['c14']: C_TRA, T['station']: C_TRA, T['etat']: GOLD, T['accise']: C_ACC, T['c30']: C_ACC,
      T['tva']: C_TVA, T['c20']: C_TVA, T['caroui']: C_TVA, T['total']: GOLD, T['seul']: GOLD, T['paradoxe']: GOLD, T['an']: GREY, T['auj']: GOLD,
      T['nonpas']: GREEN, T['flambe']: C_PET, T['fin']: NEON}
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
def caption(c, words, hl, y=1060, size=44, a=1):
    """zone sûre Réels / TikTok / Shorts : au-dessus de l'interface du bas (≥ 1500 px) et loin des icônes de droite (x > 950)"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '0E0610', .74*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- outils graphiques ----------
def big(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0, edge=WHITE, lw=12):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s)
    c.move_to(-ext.x_advance/2+5, size*.36+7); c.text_path(s); col(c, '000000', .35*a); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, edge, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def tag(c, s, x, y, color, a=1, size=30, fg=WHITE, align='c'):
    if a <= 0: return
    w = tw(c, s, 'xb', size, 2)+56; x0 = x-w/2 if align == 'c' else x
    rr(c, x0, y-size*.95, w, size*1.9, size*.95); col(c, color, a); c.fill(); text(c, s, x0+w/2, y, 'xb', size, fg, 'c', a, 2)
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
EMO = []
def put_emoji(ch, x, y, size, k, a=1.0):
    if k > 0 and a > 0: EMO.append((ch, x, y, size, k, a))
def draw_emoji(cv, ch, x, y, size, k, a):
    if not os.path.exists(EMOJI_FONT): return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    if a < 1: e = e.copy(); e.putalpha(e.getchannel('A').point(lambda v: int(v*a)))
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))

# ---------- néons : scintillement ----------
@functools.lru_cache(maxsize=1)
def _dips():
    rng = np.random.default_rng(29); out = []; t = .7
    while t < 80:
        d = rng.uniform(.04, .1); out.append((t, d, rng.uniform(.25, .55)))
        if rng.random() < .45: out.append((t+d+.05, rng.uniform(.03, .06), rng.uniform(.3, .6)))
        t += rng.uniform(1.6, 3.4)
    return out
def flick(t, ph=0.0):
    """intensité du néon : léger bourdonnement + coupures brèves irrégulières"""
    f = 1+.05*math.sin(t*9.1+ph)+.03*math.sin(t*23.7+ph*2)
    for a, d, lv in _dips():
        if a <= t+ph*.37 < a+d: f *= lv
    return f

# ---------- décors ----------
def _load(name):
    return np.asarray(Image.open(f'{D}/decors/{name}.jpg').convert('RGB')).astype(np.float32)
@functools.lru_cache(maxsize=1)
def aerial():
    """vue du ciel (pleine résolution 1792 × 2400) + masques : néons de l'auvent, reflets rouges, traînées de phares"""
    a = _load('station_haut'); R, G, B = a[..., 0], a[..., 1], a[..., 2]; h, w = R.shape
    yy, xx = np.mgrid[0:h, 0:w]
    neon = ((R > 175) & (R-G > 80) & (R-B > 40) & (yy < 1250)).astype(np.float32)
    refl = ((R > 110) & (R-G > 60) & (yy >= 1250)).astype(np.float32)
    trail = ((np.minimum(np.minimum(R, G), B) > 165) & (xx < 620) & (yy > 620) & (yy < 1500)).astype(np.float32)
    tail = ((R > 150) & (R-G > 70) & (xx < 620) & (yy > 1650)).astype(np.float32)
    bl = lambda m, s: cv2.GaussianBlur(m, (0, 0), s)
    return a, bl(neon, 1.2), bl(refl, 2), bl(trail, 1), bl(tail, 1.5), yy.astype(np.float32)
@functools.lru_cache(maxsize=1)
def ground():
    """vue au sol, mise à l'échelle finale (1434 × 1920, cadrage x 300 → 1380) + masques néons et reflets"""
    im = Image.open(f'{D}/decors/station_sol.jpg').convert('RGB'); im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; h, w = R.shape
    yy, xx = np.mgrid[0:h, 0:w]
    neon = ((R > 170) & (R-G > 70) & (R-B > 30) & (yy < 1000)).astype(np.float32)
    refl = ((R > 100) & (R-G > 55) & (yy >= 1350)).astype(np.float32)
    bl = lambda m, s: cv2.GaussianBlur(m, (0, 0), s)
    return a, bl(neon, 1.5), bl(refl, 2.5)
GX0 = 300                                    # cadrage final dans l'image au sol
SCR = (640, 768, 864, 984)                   # écran de la pompe (coordonnées écran final)
def aerial_img(t):
    a, neon, refl, trail, tail, yy = aerial()
    f = flick(t); fr = 1+(f-1)*.6
    out = a*(1+neon[..., None]*(f-1)*.95)*(1+refl[..., None]*(fr-1)*.8)
    wave = np.maximum(0, np.sin(yy/38-t*7))**6                         # des phares filent sur la route
    out += (trail*wave)[..., None]*np.array([90, 90, 80], np.float32)
    wave2 = np.maximum(0, np.sin(yy/45+t*6))**6
    out += (tail*wave2)[..., None]*np.array([110, 10, 20], np.float32)
    return np.clip(out, 0, 255)
def ground_img(t):
    a, neon, refl = ground()
    f = flick(t, 1.3); fr = 1+(f-1)*.7
    out = a*(1+neon[..., None]*(f-1)*.95)
    sh = .08*np.sin(t*2.3)                                             # les flaques ondulent un peu
    out = out*(1+refl[..., None]*((fr-1)*.8+sh))
    return np.clip(out, 0, 255)

# ---------- compteur de la pompe (dessiné sur l'image au sol) ----------
PRICE = 2.3555; PARTS = [(53.35, C_PET), (14.42, C_TRA), (30.38, C_ACC), (19.63, C_TVA)]
def euros_at(t):
    if t < T['cent']: return 0.0
    if t < T['alors']: return 117.78*inout((t-T['cent'])/1.9)
    acc = 0.0; marks = [T['c53'], T['c14'], T['c30'], T['c20']]
    for (v, _), m in zip(PARTS, marks):
        if t > m-.25: acc += v*inout((t-m+.25)/1.0)
    return acc
def fmt(v, d=2): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
def counter(c, t, ox):
    x0, y0, x1, y1 = SCR; x0 += ox; x1 += ox; cx = (x0+x1)/2
    rr(c, x0+6, y0+6, x1-x0-12, y1-y0-12, 8); col(c, '07040A', .96); c.fill()
    e = euros_at(t); L = e/PRICE
    blink = 1.0
    if T['alors'] <= t < T['alors']+.7: blink = .25+.75*(int((t-T['alors'])*8) % 2)
    text(c, "TOTAL", x0+22, y0+34, 'xb', 15, NEON2, 'l', .9, 2); text(c, "€", x1-22, y0+34, 'xb', 18, NEON2, 'r', .9)
    c.save(); c.select_font_face('Anton')
    s = fmt(e); c.set_font_size(74); ext = c.text_extents(s)
    for r_, al in ((7, .18), (3, .35)):
        c.move_to(x1-24-ext.x_advance, y0+108); c.text_path(s); c.set_line_width(r_*2); col(c, NEON, al*blink); c.stroke()
    c.move_to(x1-24-ext.x_advance, y0+108); c.text_path(s); col(c, 'FF5A78', blink); c.fill(); c.restore()
    c.move_to(x0+16, y0+128); c.line_to(x1-16, y0+128); c.set_line_width(1.5); col(c, NEON, .35); c.stroke()
    text(c, "LITRES", x0+22, y0+152, 'xb', 14, NEON2, 'l', .9, 2); text(c, fmt(L), x1-24, y0+152, 'a', 30, 'FF8FA3', 'r', blink)
    text(c, "PRIX/L", x0+22, y0+190, 'xb', 14, NEON2, 'l', .9, 2); text(c, "2,356", x1-24, y0+190, 'a', 30, 'FFC2CF', 'r', .95)

# ---------- caméra ----------
def view(arr, box):
    """recadre une zone (x0, y0, w, h) de l'image source sur 1080 × 1920"""
    x0, y0, w, h = box; sx, sy = W/w, H/h
    M = np.float32([[sx, 0, -x0*sx], [0, sy, -y0*sy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
AP = (1050., 1000.)                          # centre de l'auvent dans la vue du ciel (pleine résolution)
def aerial_box(z):
    x0, w = 221., 1350.; y0, h = 0., 2400.
    return (AP[0]+(x0-AP[0])/z, AP[1]+(y0-AP[1])/z, w/z, h/z)
def aerial_frame(t):
    if t < T_DESC: z = 1+.13*inout(t/T_DESC)
    else: u = clamp((t-T_DESC)/.75); z = 1.13+2.6*u**2.2
    img = aerial_img(t)
    if t < T_DESC: return view(img, aerial_box(z))
    acc = sum(view(img, aerial_box(z*k)) for k in (1, .965, .93, .895)) / 4    # flou de vitesse pendant la plongée
    return acc
def ground_box(t):
    final = (GX0, 0., 1080., 1920.)
    if t >= T_LAND+.35: return final
    u = ease((t-3.8)/(T_LAND+.35-3.8)); s = lerp(1.85, 1, u)
    w, h = 1080/s, 1920/s; cx = lerp(1010, GX0+540, u); y0 = 0.
    return (cx-w/2, y0, w, h)

# ---------- panneau de gauche (jauge, paradoxe) ----------
PX0, PY0, PX1, PY1 = 36, 218, 566, 940
TUBE_X0, TUBE_X1, TUBE_Y1, TUBE_H = 76, 176, 900, 540
def panel(c, a):
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 28); col(c, '0B0610', .80*a); c.fill()
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 28); c.set_line_width(2); col(c, NEON, .45*a); c.stroke()
def gauge(c, t, a, mode='parts'):
    """jauge verticale : les quatre postes s'empilent quand ils sont nommés"""
    pxe = TUBE_H/117.78
    rr(c, TUBE_X0-6, TUBE_Y1-TUBE_H-14, TUBE_X1-TUBE_X0+12, TUBE_H+20, 18); col(c, 'FFFFFF', .08*a); c.fill()
    rr(c, TUBE_X0-6, TUBE_Y1-TUBE_H-14, TUBE_X1-TUBE_X0+12, TUBE_H+20, 18); c.set_line_width(2); col(c, 'FFFFFF', .25*a); c.stroke()
    starts = [(T['abord'], T['c53']), (T['ensuite'], T['c14']), (T['accise'], T['c30']), (T['tva'], T['c20'])]
    names = [("🛢️", "PÉTROLE ET RAFFINAGE"), ("🚚", "TRANSPORT ET STATION"), ("🏛️", "ACCISE (EX-TICPE)"), ("🏛️", "TVA 20 %")]
    y = TUBE_Y1; tops = []
    final = mode == 'final'
    for i, ((v, colr), (tn, tv)) in enumerate(zip(PARTS, starts)):
        k = 1.0 if final else inout((t-tv+.25)/1.0)
        hgt = v*pxe*k; dim = 1.0
        if mode == 'etat' and i < 2: dim = .35
        if hgt > .5:
            rr(c, TUBE_X0, y-hgt, TUBE_X1-TUBE_X0, hgt, 10 if i in (0, 3) else 4); col(c, colr, a*dim); c.fill()
            g = cairo.LinearGradient(TUBE_X0, 0, TUBE_X1, 0); g.add_color_stop_rgba(0, 1, 1, 1, .0); g.add_color_stop_rgba(.3, 1, 1, 1, .22*a*dim); g.add_color_stop_rgba(.6, 1, 1, 1, 0)
            c.rectangle(TUBE_X0, y-hgt, TUBE_X1-TUBE_X0, hgt); c.set_source(g); c.fill()
        ymid = y-v*pxe/2; tops.append((y-v*pxe, y, ymid))
        ka = 1.0 if final else ease((t-tn)/.35)
        if ka > 0 and not (mode == 'etat' and i >= 2):
            lx = 206; al = ka*a*dim
            put_emoji(names[i][0], lx+20, ymid-(26 if i != 1 else 18), 34, 1.0 if final else t-tn, al)
            text(c, names[i][1], lx+46, ymid-(26 if i != 1 else 18), 'xb', 19 if i != 0 else 18, WHITE, 'l', al, 1)
            kv = 1.0 if final else ease((t-tv)/.3)
            if kv > 0: text(c, fmt(v)+" €", lx, ymid+(16 if i != 1 else 18), 'a', 40, colr, 'l', kv*a*dim)
            if i == 0 and t > T['fevrier'] and not final:
                kf = ease((t-T['fevrier']-.9)/.35); text(c, "MARGE DES RAFFINEURS ×6", lx, ymid+64, 'xb', 19, 'FFB27A', 'l', kf*a, 1)
                put_emoji('📈', lx+300, ymid+63, 26, t-T['fevrier']-1.1, kf*a)
            if i == 1 and t > T['station'] and not final:
                ks = ease((t-T['station']-1.2)/.35); text(c, "DONT STATION : 1 À 4 €", 360, ymid+16, 'xb', 16, '9CC8FF', 'l', ks*a, 1)
        y -= v*pxe
    return tops
def arrow(c, x0, y0, x1, y1, bend, colr, a, w=5):
    """flèche courbe de (x0,y0) vers (x1,y1)"""
    mx, my = (x0+x1)/2+bend, (y0+y1)/2
    c.move_to(x0, y0); c.curve_to(mx, y0, mx, y1, x1, y1); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, colr, a); c.stroke()
    ang = math.atan2(y1-y1, x1-mx)
    for s_ in (-1, 1):
        c.move_to(x1, y1); c.line_to(x1-18*math.cos(ang+s_*.5), y1-18*math.sin(ang+s_*.5))
    c.stroke()
def left(c, t):
    a = 1.0
    if t < T['alors']-.15:                                                 # intro : le chiffre choc
        k = t-T['cent']
        big(c, "118 €", 300, 420, 190, 'FF5A78', ease(k/.2), lerp(1.3, 1, back(k/.45)), edge=WHITE, lw=10)
        kp = t-T['prix']
        if kp > 0:
            text(c, "UN PLEIN DE 50 LITRES", 300, 600, 'xb', 34, WHITE, 'c', ease(kp/.3), 1)
            put_emoji('⛽', 300, 700, 80, kp-.2)
        kg = t-T['prend']
        if kg > 0: tag(c, "GAZOLE · 2,36 €/L", 300, 820, GOLD, ease(kg/.3), 30, INK)
        kd = t-T['deux']
        if kd > 0: text(c, "PRIX MOYEN · SEMAINE DU 2 OCTOBRE", 300, 890, 'xb', 17, 'D8C9D4', 'c', ease(kd/.3), 1)
        return
    if t < T['paradoxe']-.12:                                              # la jauge se remplit
        ka = ease((t-T['alors'])/.35); panel(c, ka)
        text(c, "OÙ PART TON ARGENT ?", (PX0+PX1)/2, PY0+48, 'a', 46, WHITE, 'c', ka)
        mode = 'etat' if t >= T['total'] else 'parts'
        tops = gauge(c, t, ka, mode)
        if T['caroui'] <= t < T['total']:                                  # la TVA se paie aussi sur l'accise
            kt = ease((t-T['taxe']+.2)/.4)
            (a3, b3, m3), (a4, b4, m4) = tops[2], tops[3]
            if kt > 0:
                arrow(c, TUBE_X0-4, m4, TUBE_X0-4, m3, -46, 'FFD34D', kt)
                tag(c, "TVA AUSSI SUR L'ACCISE", 300, PY0+104, 'D99A00', kt, 20, INK)
        if t >= T['total']:
            (a3, b3, _), (a4, b4, _) = tops[2], tops[3]; ke = ease((t-T['total'])/.35)
            c.move_to(TUBE_X1+16, a4+4); c.line_to(TUBE_X1+30, a4+4); c.line_to(TUBE_X1+30, b3-4); c.line_to(TUBE_X1+16, b3-4)
            c.set_line_width(5); col(c, GOLD, ke); c.stroke()
            ym = (a4+b3)/2
            text(c, "L'ÉTAT", 372, ym-70, 'xb', 26, GOLD, 'c', ke, 2)
            big(c, "50 €", 372, ym+6, 110, GOLD, ke, lerp(1.25, 1, back((t-T['total'])/.45)), edge=INK, lw=8)
            text(c, "42 % DU PLEIN", 372, ym+92, 'xb', 22, WHITE, 'c', ease((t-T['total']-.5)/.3), 1)
            ks = t-T['seul']
            if ks > 0:
                tag(c, "LE PLUS GROS GAGNANT", 372, ym+148, GOLD, ease(ks/.3), 19, INK); put_emoji('👑', 372, ym-128, 60, ks-.2)
        return
    if t < T['fin']-.12:                                                   # le paradoxe
        kp = t-T['paradoxe']; panel(c, ease(kp/.3))
        text(c, "LE PARADOXE", (PX0+PX1)/2, PY0+50, 'a', 50, GOLD, 'c', ease(kp/.3))
        text(c, "PART DES TAXES DANS LE PRIX", (PX0+PX1)/2, PY0+104, 'xb', 19, 'D8C9D4', 'c', ease((kp-.2)/.3), 2)
        for i, (t0, lab, v, cl) in enumerate(((T['an'], "IL Y A UN AN", 54, GREY), (T['auj'], "AUJOURD'HUI", 42, GOLD))):
            u = inout((t-t0-.3)/.7)
            if t < t0: continue
            y = 390+i*125; w = 300*v/54*u
            text(c, lab, 76, y, 'xb', 22, WHITE, 'l', ease((t-t0)/.3), 1)
            rr(c, 76, y+22, max(4, w), 50, 12); col(c, cl, 1); c.fill()
            text(c, f"{v} %", 76+w+14, y+48, 'a', 44, WHITE, 'l', ease((t-t0-.3)/.3))
        kn = t-T['plus']+.4
        if kn > 0:
            text(c, "TAXES PAR LITRE", 76, 680, 'xb', 20, 'D8C9D4', 'l', ease(kn/.3), 2)
            text(c, "≈ 0,88 € → 1,00 €", 76, 724, 'xb', 38, GREEN, 'l', ease(kn/.3)); put_emoji('⬆️', 470, 720, 44, kn-.3)
        kf = t-T['flambe']-.5
        if kf > 0:
            text(c, "PÉTROLE PAR LITRE", 76, 800, 'xb', 20, 'D8C9D4', 'l', ease(kf/.3), 2)
            text(c, "≈ 0,52 € → 1,07 €", 76, 844, 'xb', 38, C_PET, 'l', ease(kf/.3)); put_emoji('🔥', 470, 838, 50, kf-.3)
        return
    kf = t-T['fin']; ka = ease(kf/.35); panel(c, ka)                       # récapitulatif final
    text(c, "TON PLEIN DE 117,78 €", (PX0+PX1)/2, PY0+48, 'a', 44, WHITE, 'c', ka)
    gauge(c, t, ka, 'final')
    al = ease((t-T['quand']-.6)/.4)
    if al > 0:
        c.push_group(); logo_symbol(c, 214, PY0+94, 18); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 232, PY0+94, 'b', 19, WHITE, 'l', al)

# ---------- vue du ciel : titre néon ----------
def neon_title(c, t):
    f = flick(t, 2.1) if t > .4 else 1.0; a = clamp(f, .3, 1)
    for s_, y, size in (("118 €", 330, 210), ("LE PLEIN", 520, 104)):
        c.save(); c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s_)
        x = 540-ext.x_advance/2
        for wdt, al in ((26, .10), (16, .18), (8, .35)):
            c.move_to(x, y+size*.36); c.text_path(s_); c.set_line_width(wdt); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NEON, al*a); c.stroke()
        c.move_to(x, y+size*.36); c.text_path(s_); c.set_line_width(4); col(c, NEON2, a); c.stroke_preserve(); col(c, 'FFF1F4', .95*a); c.fill(); c.restore()
    text(c, "CE QU'ON NE TE DIT PAS SUR TON PLEIN", 540, 640, 'xb', 26, WHITE, 'c', ease((t-.3)/.4), 2)

# ---------- pluie ----------
@functools.lru_cache(maxsize=1)
def drops():
    rng = np.random.default_rng(11); return rng.uniform(0, W, 150), rng.uniform(0, H, 150), rng.uniform(900, 1500, 150), rng.uniform(18, 40, 150), rng.uniform(25, 70, 150)
def rain(lay, t, k=1.0):
    d = ImageDraw.Draw(lay); X, Y, S, L, A = drops()
    for x0, y0, s, l, a in zip(X, Y, S, L, A):
        y = (y0+s*t) % (H+60)-30; x = (x0-s*t*.12) % W
        d.line((x, y, x-l*.12, y+l), fill=(220, 225, 255, int(a*k)), width=2)

# ---------- Mister Coin (clips Veo, version classique) ----------
EXP, ENT = 'classique_parle_explique', 'classique_parle_enthousiaste'
CX_COIN, FEET = 330, 1700
INQ, TRI = 'classique_parle_inquiet', 'classique_parle_triste'
# humeur selon le propos (changements calés dans les silences) : enthousiaste au début, inquiet quand l'État arrive, triste sur le total et le paradoxe, de nouveau enjoué à la fin
MC = VeoCoin([(3.95, [ENT, EXP], 'voix'), (29.0, [INQ, EXP], 'voix'), (39.0, [TRI, INQ], 'voix'), (55.7, [ENT, EXP], 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220)
def coin_pos(t):
    """il tombe du ciel avec la caméra et se pose devant la pompe"""
    t0 = 3.95
    if t < t0: return None
    if t < T_LAND: u = (t-t0)/(T_LAND-t0); return CX_COIN, lerp(-150, FEET, u**1.8)
    if t < T_LAND+.22: return CX_COIN, FEET+16*math.sin(math.pi*(t-T_LAND)/.22)
    return CX_COIN, FEET

def frame(t):
    EMO.clear()
    if t < 4.05:                                                           # vue du ciel, puis plongée
        A = aerial_frame(t)
    if t >= 3.8:                                                           # vue au sol, la caméra descend
        G = ground_img(t)
        gi = Image.fromarray(G.astype(np.uint8)).convert('RGBA'); s0, c0 = surface()
        lay = Image.new('RGBA', gi.size, 0); s1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, gi.size[0], gi.size[1]); c1 = cairo.Context(s1)
        counter(c1, t, GX0); s1.flush()
        cnt = Image.frombuffer('RGBA', gi.size, bytes(s1.get_data()), 'raw', 'BGRa', s1.get_stride(), 1)
        gi.alpha_composite(cnt); Gv = view(np.asarray(gi.convert('RGB')).astype(np.float32), ground_box(t))
    if t < 3.8: base = A
    elif t < 4.05:
        u = inout((t-3.8)/.25); base = A*(1-u)+Gv*u
        fl = math.sin(math.pi*u)*.35; base = base*(1-fl)+np.array([255, 120, 150], np.float32)*fl      # éclair néon au passage
    else: base = Gv
    cv = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface()
    if t < T_DESC+.35:
        neon_title(c, t); a_t = 1-ease((t-T_DESC)/.35)
        if a_t < 1:
            im = to_img(s); im.putalpha(im.getchannel('A').point(lambda v: int(v*a_t))); cv.alpha_composite(im)
        else: cv.alpha_composite(to_img(s))
    elif t >= T_LAND-.1:
        left(c, t); cv.alpha_composite(to_img(s))
        for e in EMO: draw_emoji(cv, *e)
    p = coin_pos(t)
    if p is not None:
        X, Y = p; rgb, al = MC.layer(t, X, Y)
        a = np.asarray(cv.convert('RGB')).astype(np.float32)
        fx = MC.feet_x(al, Y) if Y > FEET-30 else None
        if fx is not None:                                                 # ombre douce au sol
            m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (100, 15), 0, 0, 360, .45, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
            a *= (1-m[..., None])
        a = a*(1-al[..., None])+rgb*al[..., None]
        cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), 0); rain(lay, t, .8 if t < 4 else 1.0); cv.alpha_composite(lay)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, NEON), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'neon'), (1.2, 'trans'), (T_DESC, 'whoosh'), (T_DESC+.1, 'riser'), (T_LAND, 'thud'), (T['cent'], 'impact'), (T['cent']+.05, 'pump'),
          (T['prix'], 'pop'), (T['prend'], 'swish'), (T['deux'], 'tick'), (T['alors'], 'beep'), (T['abord'], 'pop'), (T['c53']-.25, 'pump'),
          (T['fevrier']+.9, 'pop'), (T['ensuite'], 'pop'), (T['c14']-.25, 'pump'), (T['station']+1.2, 'pop'), (T['etat'], 'swish'),
          (T['accise'], 'pop'), (T['c30']-.25, 'pump'), (T['tva'], 'pop'), (T['c20']-.25, 'pump'), (T['taxe']-.2, 'glint'),
          (T['total'], 'impact'), (T['total']+.1, 'coins'), (T['seul'], 'glint'), (T['paradoxe'], 'swish'), (T['paradoxe'], 'low'),
          (T['an']+.3, 'tick'), (T['auj']+.3, 'tick'), (T['plus']-.4, 'pop'), (T['flambe']+.5, 'pop'), (T['fin'], 'swish'), (T['quand']+.6, 'paid')]
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
