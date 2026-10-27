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
def flick(t, ph=0.0):
    """intensité du néon : respiration lente et douce, sans coupure (pas d'effet de saut d'image)"""
    return 1+.045*math.sin(t*2.2+ph)+.02*math.sin(t*5.1+ph*1.7)

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
    wave = (.5+.5*np.sin(yy/60-t*4))**3                               # des phares glissent doucement sur la route
    out += (trail*wave)[..., None]*np.array([45, 45, 40], np.float32)
    wave2 = (.5+.5*np.sin(yy/70+t*3.5))**3
    out += (tail*wave2)[..., None]*np.array([60, 6, 12], np.float32)
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
P_START, P_END = T_LAND+.35, DUR-1.1          # la pompe débite du début à la fin de l'exposé, comme une vraie pompe
def euros_at(t):
    u = clamp((t-P_START)/(P_END-P_START))
    g = .88*u+.12*inout(u)                                                # débit régulier, démarrage et arrêt adoucis
    return 117.78*g
def fmt(v, d=2): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
def counter(c, t, ox):
    x0, y0, x1, y1 = SCR; x0 += ox; x1 += ox; cx = (x0+x1)/2
    rr(c, x0+6, y0+6, x1-x0-12, y1-y0-12, 8); col(c, '07040A', .96); c.fill()
    e = euros_at(t); L = e/PRICE
    blink = 1.0
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
TUBE_X0, TUBE_X1, TUBE_Y1, TUBE_H = 70, 182, 902, 540
def rgb(h, k=1.0, mix_white=0.0):
    h = h.lstrip('#'); v = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    return [min(1, x*k*(1-mix_white)+mix_white) for x in v]
def panel(c, a):
    """carte en verre fumé, liseré néon doux"""
    if a <= 0: return
    for w_, al in ((10, .06), (5, .10)):
        rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_line_width(w_); col(c, NEON, al*a); c.stroke()
    g = cairo.LinearGradient(0, PY0, 0, PY1); g.add_color_stop_rgba(0, .07, .03, .08, .86*a); g.add_color_stop_rgba(1, .03, .01, .04, .90*a)
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_source(g); c.fill()
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_line_width(1.6); col(c, 'FF8FA6', .55*a); c.stroke()
def tube_path(c, inset=0):
    rr(c, TUBE_X0+inset, TUBE_Y1-TUBE_H-inset*0, TUBE_X1-TUBE_X0-2*inset, TUBE_H, 26-inset)
STARTS = lambda: [(T['abord'], T['c53']), (T['ensuite'], T['c14']), (T['accise'], T['c30']), (T['tva'], T['c20'])]
NAMES = ["PÉTROLE ET RAFFINAGE", "TRANSPORT ET STATION", "ACCISE (EX-TICPE)", "TVA"]
EMOS = ["🛢️", "🚚", "🏛️", "🏛️"]
def fill_k(i, t, final=False):
    if final: return 1.0
    return inout((t-STARTS()[i][1]+.25)/1.0)
def gauge(c, t, a, mode='parts'):
    """réservoir en verre : le carburant monte par couches, surface ondulante, bulles ; étiquettes reliées à chaque couche"""
    pxe = TUBE_H/117.78; final = mode == 'final'; X0, X1 = TUBE_X0+7, TUBE_X1-7
    # verre (fond)
    tube_path(c); col(c, 'FFFFFF', .05*a); c.fill()
    for k in range(1, 6):                                                    # graduations tous les 20 €
        yy = TUBE_Y1-k*20*pxe; c.move_to(TUBE_X1-16, yy); c.line_to(TUBE_X1-4, yy); c.set_line_width(2); col(c, 'FFFFFF', .22*a); c.stroke()
    ks = [fill_k(i, t, final) for i in range(4)]; hs = [v*pxe*k for (v, _), k in zip(PARTS, ks)]
    top = TUBE_Y1-sum(hs); filling = any(0 < k < 1 for k in ks)
    amp = 5.5 if filling else 2.2
    c.save(); tube_path(c, 7); c.clip()
    y = TUBE_Y1; bounds = []
    for i, ((v, colr), h_) in enumerate(zip(PARTS, hs)):
        if h_ <= .3: bounds.append(None); continue
        dim = .32 if (mode == 'etat' and i < 2) else 1.0
        y1 = y-h_; is_top = i == max(j for j in range(4) if hs[j] > .3)
        c.new_path()
        if is_top:                                                           # surface ondulée du liquide
            c.move_to(X0, y)
            for xx in range(int(X0), int(X1)+1, 4): c.line_to(xx, y1+amp*math.sin(xx*.075+t*5.2)+amp*.5*math.sin(xx*.13-t*3.1))
            c.line_to(X1, y); c.close_path()
        else: c.rectangle(X0, y1, X1-X0, h_)
        g = cairo.LinearGradient(0, y1, 0, y); g.add_color_stop_rgba(0, *rgb(colr, 1.0, .28), a*dim); g.add_color_stop_rgba(1, *rgb(colr, .78), a*dim)
        c.set_source(g); c.fill()
        if i > 0 and hs[i-1] > .3: c.move_to(X0, y); c.line_to(X1, y); c.set_line_width(1.5); col(c, 'FFFFFF', .28*a); c.stroke()
        bounds.append((y1, y)); y = y1
    rng = np.random.default_rng(5)                                           # bulles qui remontent dans le carburant
    for k in range(16):
        bx = rng.uniform(X0+10, X1-10); sp_ = rng.uniform(40, 90); ph = rng.uniform(0, 600); r = rng.uniform(2, 4.5)
        H_ = max(1, TUBE_Y1-top-6); by = TUBE_Y1-((t*sp_+ph) % H_)
        if by < top+6: continue
        c.arc(bx+3*math.sin(t*3+k), by, r, 0, 2*math.pi); c.set_line_width(1.4); col(c, 'FFFFFF', .35*a); c.stroke()
    c.restore()
    # verre (reflets et contour)
    g = cairo.LinearGradient(TUBE_X0, 0, TUBE_X1, 0)
    g.add_color_stop_rgba(0, 1, 1, 1, .0); g.add_color_stop_rgba(.12, 1, 1, 1, .26*a); g.add_color_stop_rgba(.24, 1, 1, 1, .04*a); g.add_color_stop_rgba(.85, 1, 1, 1, 0); g.add_color_stop_rgba(.93, 1, 1, 1, .12*a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    tube_path(c); c.set_source(g); c.fill()
    tube_path(c); c.set_line_width(2.5); col(c, 'FFFFFF', .42*a); c.stroke()
    # étiquettes
    tops = []; y = TUBE_Y1
    for i, (v, colr) in enumerate(PARTS):
        ymid = y-v*pxe/2; tops.append((y-v*pxe, y, ymid)); y -= v*pxe
    for i, (v, colr) in enumerate(PARTS):
        tn, tv = STARTS()[i]; ka = 1.0 if final else ease((t-tn)/.4)
        if ka <= 0 or (mode == 'etat' and i >= 2): continue
        dim = .32 if mode == 'etat' else 1.0; al = ka*a*dim; ym = tops[i][2]; dx = 24*(1-ka)
        c.move_to(TUBE_X1+4, ym); c.line_to(TUBE_X1+26, ym); c.set_line_width(2); col(c, colr, al); c.stroke()
        c.arc(TUBE_X1+26, ym, 4, 0, 2*math.pi); col(c, colr, al); c.fill()
        lx = TUBE_X1+42+dx
        put_emoji(EMOS[i], lx+14, ym-20, 28, 1.0 if final else t-tn, al)
        text(c, NAMES[i], lx+36, ym-20, 'xb', 17, 'E6DDEA', 'l', al, 1)
        kv = 1.0 if final else ease((t-tv)/.3)
        if kv > 0: text(c, fmt(v)+" €", lx, ym+20, 'a', 44, fmt_col(colr), 'l', kv*al)
        if not final and mode != 'etat':
            if i == 0 and t > T['fevrier']+.9: note(c, "MARGE DES RAFFINEURS ×6", lx, ym+68, C_PET, ease((t-T['fevrier']-.9)/.35))
            if i == 1 and t > T['station']+1.2: note(c, "DONT STATION : 1 À 4 €", lx, ym+66, C_TRA, ease((t-T['station']-1.2)/.35))
    return tops
def fmt_col(colr): return '%02X%02X%02X' % tuple(int(x*255) for x in rgb(colr, 1.0, .22))
def note(c, s_, x, y, colr, a, size=16):
    """petite pastille contour, pour une précision"""
    if a <= 0: return
    w = tw(c, s_, 'xb', size, 1)+28; rr(c, x, y-size*.95, w, size*1.9, size*.95); col(c, colr, .22*a); c.fill_preserve(); c.set_line_width(1.6); col(c, colr, a); c.stroke()
    text(c, s_, x+14, y, 'xb', size, WHITE, 'l', a, 1)
def arrow(c, x0, y0, x1, y1, bend, colr, a, w=4):
    """flèche courbe de (x0,y0) vers (x1,y1), en pointillés"""
    mx = (x0+x1)/2+bend
    c.set_dash([10, 7]); c.move_to(x0, y0); c.curve_to(mx, y0, mx, y1, x1, y1); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, colr, a); c.stroke(); c.set_dash([])
    for s_ in (-1, 1):
        c.move_to(x1, y1); c.line_to(x1-15*math.cos(s_*.55), y1-15*math.sin(s_*.55))
    c.set_line_width(w); c.stroke()
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
        text(c, "OÙ PART TON ARGENT ?", (PX0+PX1)/2, PY0+50, 'a', 46, WHITE, 'c', ka)
        c.move_to((PX0+PX1)/2-60, PY0+82); c.line_to((PX0+PX1)/2+60, PY0+82); c.set_line_width(3); col(c, NEON, .8*ka); c.stroke()
        mode = 'etat' if t >= T['total'] else 'parts'
        tops = gauge(c, t, ka, mode)
        if T['caroui'] <= t < T['total']:                                  # la TVA se paie aussi sur l'accise
            kt = ease((t-T['taxe']+.2)/.4)
            (a3, b3, m3), (a4, b4, m4) = tops[2], tops[3]
            if kt > 0:
                arrow(c, TUBE_X0-2, m4, TUBE_X0-2, m3, -40, 'FFD34D', kt)
                note(c, "TVA CALCULÉE AUSSI SUR L'ACCISE", 160, PY0+102, 'FFC21A', kt, 16)
        if t >= T['total']:
            (a3, b3, _), (a4, b4, _) = tops[2], tops[3]; ke = ease((t-T['total'])/.35); bx = TUBE_X1+14
            for w_, al in ((10, .18), (4, 1.0)):
                c.move_to(bx, a4+4); c.line_to(bx+14, a4+4); c.line_to(bx+14, b3-4); c.line_to(bx, b3-4); c.set_line_width(w_); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, GOLD, al*ke); c.stroke()
            ym = (a4+b3)/2; cx_ = 392
            ks = t-T['seul']
            if ks > 0: note(c, "LE PLUS GROS GAGNANT", cx_-126, ym-128, GOLD, ease(ks/.3), 17); put_emoji('👑', cx_+150, ym-132, 44, ks-.2)
            text(c, "L'ÉTAT", cx_, ym-66, 'xb', 24, GOLD, 'c', ke, 3)
            big(c, "50 €", cx_, ym+6, 112, GOLD, ke, lerp(1.25, 1, back((t-T['total'])/.45)), edge=INK, lw=8)
            text(c, "42 % DU PLEIN", cx_, ym+88, 'xb', 22, WHITE, 'c', ease((t-T['total']-.5)/.3), 2)
        return
    if t < T['fin']-.12:                                                   # le paradoxe
        kp = t-T['paradoxe']; panel(c, ease(kp/.3))
        text(c, "LE PARADOXE", (PX0+PX1)/2, PY0+50, 'a', 50, GOLD, 'c', ease(kp/.3))
        text(c, "PART DES TAXES DANS LE PRIX", (PX0+PX1)/2, PY0+104, 'xb', 19, 'D8C9D4', 'c', ease((kp-.2)/.3), 2)
        for i, (t0, lab, v, cl) in enumerate(((T['an'], "IL Y A UN AN", 54, GREY), (T['auj'], "AUJOURD'HUI", 42, GOLD))):
            u = inout((t-t0-.3)/.7)
            if t < t0: continue
            y = 380+i*130; w = 330*v/54*u; ka_ = ease((t-t0)/.3)
            text(c, lab, 76, y, 'xb', 21, 'E6DDEA', 'l', ka_, 2)
            rr(c, 76, y+24, 330, 52, 26); col(c, 'FFFFFF', .07*ka_); c.fill()
            if w > 4:
                g = cairo.LinearGradient(76, 0, 76+w, 0); g.add_color_stop_rgba(0, *rgb(cl, .8), 1); g.add_color_stop_rgba(1, *rgb(cl, 1, .25), 1)
                rr(c, 76, y+24, max(52, w), 52, 26); c.set_source(g); c.fill()
            text(c, f"{v} %", 76+max(52, w)+16, y+52, 'a', 46, WHITE, 'l', ease((t-t0-.3)/.3))
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
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t):
    """il tombe du ciel avec la caméra et se pose devant la pompe"""
    t0 = 3.95
    if t < t0: return None
    if t < T_LAND: u = (t-t0)/(T_LAND-t0); return CX_COIN, lerp(-150, FEET, u**1.8)
    if t < T_LAND+.22: return CX_COIN, FEET+16*math.sin(math.pi*(t-T_LAND)/.22)
    return CX_COIN, FEET+MC.hop_dy(t)                                     # petit saut sur place quand il change de geste

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
        fx = MC.feet_x(al, Y) if Y > FEET-30 else (X if Y > 300 else None)
        if fx is not None:                                                 # ombre douce au sol (plus petite quand il est en l'air)
            k = 1/(1+max(0, FEET-Y)/150)
            m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .45*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
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
    ev = [(0.0, 'neon'), (1.2, 'trans'), (T_DESC, 'whoosh'), (T_DESC+.1, 'riser'), (T_LAND, 'thud'), (T['cent'], 'impact'), (P_START-.05, 'nozzle'),
          (T['prix'], 'pop'), (T['prend'], 'swish'), (T['deux'], 'tick'), (T['alors'], 'swish'),
          (T['c53']-.25, 'fill0'), (T['c14']-.25, 'fill1'), (T['c30']-.25, 'fill2'), (T['c20']-.25, 'fill3'),
          (T['fevrier']+.9, 'pop'), (T['station']+1.2, 'pop'), (T['etat'], 'swish'), (T['taxe']-.2, 'glint'),
          (T['total'], 'impact'), (T['total']+.1, 'coins'), (T['seul'], 'glint'), (T['paradoxe'], 'swish'), (T['paradoxe'], 'low'),
          (T['an']+.3, 'tick'), (T['auj']+.3, 'tick'), (T['plus']-.4, 'pop'), (T['flambe']+.5, 'pop'), (T['fin'], 'swish'),
          (P_END, 'clack'), (T['quand']+.6, 'paid')]
    ev += [(h-.05, 'hop') for h in MC._global_sequence() and MC.hops]
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
