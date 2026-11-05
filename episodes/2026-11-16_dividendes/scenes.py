"""Vidéo « Combien investir pour vivre de ses dividendes ? » (2 000 € nets par mois) : décor salle des coffres, verre épais,
piles de pièces, jauge du PEA, courbe. Chaque scène est une fonction draw(cv, c, u) avec u = avancement 0..1 (1 = état final).
usage : python3 scenes.py maquettes   → prev/maquette_<n>.png + prev/maquettes.png"""
import sys, os, math, functools, re
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
for p in ('lib', 'mister_coin', 'archives/msft', 'archives/btc'): sys.path.insert(0, f'{ROOT}/{p}')
from nty import text, surface, to_img, rr, col, tw, W, H
from bglass import glow_text, tilt_quad
from verre_epais import tplace
import veo_coin as VC
NB = '\u00a0'
GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4D5E'; OR = 'FFA63D'; CY = '35D6FF'; ICE = 'EEF1F6'; INK = '0B0E14'; WHITE = 'FFFFFF'; NAVY = '14213D'
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def fmt(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',').replace(' ', NB)

# ---------- chiffres (sources.md) ----------
NET_MOIS = 2000; NET_AN = 24000; PS = .186; PFU = .314
BRUT = NET_AN/(1-PS)                       # 29 484 € de dividendes bruts
CAP = {1.5: BRUT/.015, 3: BRUT/.03, 5: BRUT/.05}          # 1 965 602 / 982 801 / 589 680 €
CTO3 = NET_AN/(1-PFU)/.03                  # 1 166 181 €
SMIC, MEDIAN = 1478, 2190

# ---------- décor : scène de one man show ----------
DUR = 94.4
@functools.lru_cache(maxsize=1)
def stage():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('060507')); g.add_color_stop_rgb(.62, *rgb('0E0A0B')); g.add_color_stop_rgb(1, *rgb('050404')); c.set_source(g); c.paint()
    for side in (0, 1):                                   # rideaux de velours sur les côtés, plis verticaux
        for k in range(9):
            x = (k*26 if side == 0 else W-k*26-26); w = 30
            g = cairo.LinearGradient(x, 0, x+w, 0)
            a = .55*(1-k/9)
            g.add_color_stop_rgba(0, .16, .02, .04, a); g.add_color_stop_rgba(.5, .42, .06, .09, a); g.add_color_stop_rgba(1, .12, .01, .03, a)
            c.rectangle(x, 0, w, H); c.set_source(g); c.fill()
    for k in range(14):                                   # lambrequin en haut
        x = k*80; c.move_to(x, 0); c.curve_to(x+10, 95, x+70, 95, x+80, 0); c.close_path(); c.set_source_rgba(.32, .05, .07, .55); c.fill()
    g = cairo.LinearGradient(0, 1450, 0, H); g.add_color_stop_rgba(0, .2, .12, .06, .0); g.add_color_stop_rgba(.2, .22, .13, .07, .55); g.add_color_stop_rgba(1, .08, .05, .03, .9)
    c.rectangle(0, 1450, W, H-1450); c.set_source(g); c.fill()                       # plancher
    for i in range(10): c.move_to(0, 1480+i*i*5); c.line_to(W, 1480+i*i*5); c.set_line_width(1.2); c.set_source_rgba(0, 0, 0, .35); c.stroke()
    return to_img(s)
# argent qui tombe au fond (flou) et s'entasse en un parterre qui grandit avec le temps
@functools.lru_cache(maxsize=1)
def _drops():
    rng = np.random.default_rng(5); out = []
    for k in range(260):
        out.append(dict(t0=rng.uniform(-6, DUR), x=rng.uniform(60, W-60), v=rng.uniform(260, 420), kind=rng.choice(['c', 'c', 'c', 'b', 'b', 's']),
                        rot=rng.uniform(0, 6.28), spin=rng.uniform(-2.5, 2.5), sz=rng.uniform(.7, 1.15)))
    return out
def heap_h(x, t):
    g = .22+.78*clamp(t/DUR)                                                    # le tas monte au fil de la vidéo
    return 60+g*210*(.55+.45*math.cos((x-540)/W*2.4))
def _piece(c, kind, x, y, rot, sz, a=1):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sz, sz)
    if kind == 'c':
        c.save(); c.scale(1, .55+.45*abs(math.cos(rot*1.7))); g = cairo.RadialGradient(-8, -8, 2, 0, 0, 26); g.add_color_stop_rgba(0, 1, .95, .7, a); g.add_color_stop_rgba(.6, 1, .75, .25, a); g.add_color_stop_rgba(1, .6, .38, .05, a)
        c.arc(0, 0, 24, 0, 2*math.pi); c.set_source(g); c.fill(); c.restore()
    elif kind == 'b':
        rr(c, -46, -22, 92, 44, 5); c.set_source_rgba(.36, .62, .38, a); c.fill(); rr(c, -40, -16, 80, 32, 4); c.set_line_width(2); c.set_source_rgba(.75, .9, .7, a*.8); c.stroke()
        c.arc(0, 0, 10, 0, 2*math.pi); c.set_source_rgba(.75, .9, .7, a*.7); c.fill()
    else:
        c.move_to(-30, 34); c.curve_to(-46, 0, -24, -24, -10, -26); c.line_to(10, -26); c.curve_to(24, -24, 46, 0, 30, 34); c.close_path()
        g = cairo.LinearGradient(-40, 0, 40, 0); g.add_color_stop_rgba(0, .45, .32, .16, a); g.add_color_stop_rgba(.5, .72, .55, .3, a); g.add_color_stop_rgba(1, .4, .28, .14, a); c.set_source(g); c.fill()
        c.move_to(-12, -26); c.line_to(-18, -40); c.line_to(18, -40); c.line_to(12, -26); c.close_path(); c.set_source_rgba(.55, .4, .2, a); c.fill()
        c.rectangle(-14, -30, 28, 5); c.set_source_rgba(.9, .7, .3, a); c.fill()
        c.select_font_face('Inter Display', 0, 1); c.set_font_size(30); c.set_source_rgba(.95, .8, .4, a); c.move_to(-9, 18); c.show_text('€')
    c.restore()
def money(cv, t):
    s, c = surface()
    # parterre : pièces, billets et sacs entassés (positions fixes, on ne garde que ceux sous la hauteur du tas)
    rng = np.random.default_rng(9)
    for k in range(900):
        x = rng.uniform(-20, W+20); d = rng.uniform(0, 1); kind = rng.choice(['c', 'c', 'c', 'b', 's'], p=[.3, .3, .2, .15, .05]); rot = rng.uniform(0, 6.28); sz = rng.uniform(.7, 1.1)
        hh = heap_h(x, t); y = H-d*hh
        if d*hh < hh-2: _piece(c, kind, x, y, rot, sz, .95)
    for p in _drops():
        dt = t-p['t0']
        if dt < 0: continue
        y = -60+p['v']*dt; yl = H-heap_h(p['x'], t)
        if y > yl+10: continue
        _piece(c, p['kind'], p['x'], y, p['rot']+p['spin']*dt, p['sz'], .9)
    arr = cv2.GaussianBlur(np.asarray(to_img(s)), (0, 0), 3.2)                 # profondeur de champ : le fond est flou
    lay = Image.fromarray(arr, 'RGBA'); a = np.asarray(lay).astype(np.float32); a[..., :3] *= .62; cv.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'))
def spotlight(cv, cx, feet=1650):
    """poursuite de théâtre : cône de lumière venu d'en haut qui suit Mister Coin, tache au sol, le reste plonge dans l'ombre"""
    arr = np.asarray(cv).astype(np.float32); ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    top = (cx*0.4+540*0.6, -80); half_top, half_bot = 40, 250
    u = np.clip((ys-top[1])/(feet-top[1]), 0, 1.15); xc = top[0]+(cx-top[0])*u; half = half_top+(half_bot-half_top)*u
    cone = np.clip(1-np.abs(xs-xc)/half, 0, 1)**.7*np.clip(1-(ys-feet-20)/60, 0, 1)
    pool = np.exp(-(((xs-cx)/300)**2+((ys-feet+10)/70)**2))
    light = .30*cone+.55*pool; dark = .55+.45*np.clip(cone*1.6+pool, 0, 1)
    arr[..., :3] = arr[..., :3]*dark[..., None]+255*light[..., None]*np.array([1, .9, .72], np.float32)*.55
    cv.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'))
def base_frame(t=0, cx=540):
    cv = stage().copy(); money(cv, t); spotlight(cv, cx); return cv

# ---------- verre épais ----------
def tp(cv, w, h, draw, cx, cy, mood='or', rx=.05, ry=0.0, bev=30):
    P = bev-10; W2, H2 = w+2*P, h+2*P
    base = np.asarray(cv.convert('RGB')).astype(np.float32)/255
    def dd(k, ww, hh): k.translate(P, P); draw(k, w, h)
    tplace(cv, base, W2, H2, dd, tilt_quad(cx, cy, W2, H2, ry=ry, rx=rx), 1.0, mood, bevel=bev, r=40, frost=30, dim=.45, cache=False)
def gpill(c, s, x, y, colr, size=34, fg=INK, a=1):
    w = tw(c, s, 'xb', size, 2)+60; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2); return w
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def put_emoji(cv, ch, x, y, size):
    e = emoji(ch, size); cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
def logo(cv, key, cx, cy, size=80, cross=False):
    p = f'{D}/logos/{key}.png'
    if os.path.exists(p): im = Image.open(p).convert('RGBA')
    else:                                                 # tuile provisoire tant que le logo manque
        im = Image.new('RGBA', (256, 256), 0); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, 255, 255), 56, fill=(245, 245, 245, 255))
        f = ImageFont.truetype(f'{ROOT}/fonts/InterDisplay-Black.otf', 70); s = key[:3]; w = d.textlength(s, font=f); d.text(((256-w)/2, 80), s, font=f, fill=(40, 40, 40, 255))
    k = size/max(im.size); im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    s, c = surface(); rr(c, cx-im.width/2+3, cy-im.height/2+6, im.width, im.height, im.width*.22); col(c, '000000', .4); c.fill()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(cy-im.height/2)))
    if cross:
        s, c = surface(); c.set_line_width(7); col(c, RD); c.move_to(cx-size*.55, cy-size*.55); c.line_to(cx+size*.55, cy+size*.55); c.stroke(); cv.alpha_composite(to_img(s))

# ---------- pièces empilées (pile 3D) ----------
def pile(c, cx, base, h, w=150, colr=('FFE08A', 'C98A1E', '7A4E0A'), crack=0.0):
    t = 13; n = max(1, int(h/t)); ry = w*.16
    for i in range(n):
        y = base-i*t
        g = cairo.LinearGradient(cx-w/2, 0, cx+w/2, 0); g.add_color_stop_rgb(0, *rgb(colr[2])); g.add_color_stop_rgb(.35, *rgb(colr[0])); g.add_color_stop_rgb(.6, *rgb(colr[1])); g.add_color_stop_rgb(1, *rgb(colr[2]))
        c.save(); c.translate(cx, y); c.scale(w/2, ry); c.arc(0, 0, 1, 0, math.pi); c.restore(); c.line_to(cx-w/2, y-t+2); c.save(); c.translate(cx, y-t+2); c.scale(w/2, ry); c.arc_negative(0, 0, 1, math.pi, 0); c.restore(); c.close_path()
        c.set_source(g); c.fill()
        for k in range(1, 18):                                                   # cannelures
            x = cx-w/2+w*k/18; c.move_to(x, y-t+4); c.line_to(x, y+ry*math.sin(math.acos(clamp(abs(x-cx)/(w/2), 0, .999)))-2); c.set_line_width(1); c.set_source_rgba(0, 0, 0, .12); c.stroke()
    y = base-(n-1)*t-t+2
    g = cairo.RadialGradient(cx-w*.15, y-ry*.4, 4, cx, y, w*.6); g.add_color_stop_rgb(0, *rgb('FFF4C8')); g.add_color_stop_rgb(.6, *rgb(colr[0])); g.add_color_stop_rgb(1, *rgb(colr[1]))
    c.save(); c.translate(cx, y); c.scale(w/2, ry); c.arc(0, 0, 1, 0, 2*math.pi); c.restore(); c.set_source(g); c.fill()
    c.save(); c.translate(cx, y); c.scale(w/2*.78, ry*.78); c.arc(0, 0, 1, 0, 2*math.pi); c.restore(); c.set_line_width(2); c.set_source_rgba(.5, .3, 0, .35); c.stroke()
    if crack > 0:                                                                # fissure qui descend dans la pile
        c.move_to(cx+8, y); pts = [(cx-10, y+40), (cx+16, y+90), (cx-6, y+150), (cx+12, y+220)]
        for (x2, y2) in pts[:max(1, int(len(pts)*crack))]: c.line_to(x2, y2)
        c.set_line_width(4); c.set_source_rgba(.08, .03, 0, .9); c.stroke()
    return y

# ---------- Mister Coin : une image d'un clip détouré ----------
@functools.lru_cache(maxsize=16)
def coin_frame(clip, i, h=470):
    cap = cv2.VideoCapture(f'{ROOT}/mister_coin/veo/classique_{clip}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read()
    a, m = VC._key(f[:, :, ::-1]); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((np.clip(m, 0, 1)*255).astype(np.uint8)))
    im = im.crop(im.getbbox()); return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
CUR_X = [540]
def mister(cv, clip, i, cx=None, feet=1650, h=470):
    cx = CUR_X[0] if cx is None else cx
    im = coin_frame(clip, i, h); s, c = surface(); c.save(); c.translate(cx, feet); c.scale(im.width*.4, 16)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .6); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(feet-h)))

# ---------- sous-titres (même style que les vidéos précédentes) ----------
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    out = []
    for tok in s.split(' '):
        while '[' in tok:
            pre, rest = tok.split('[', 1); mid, post = rest.split(']', 1)
            if pre: out.append((pre, False, True))
            out.append((mid, True, bool(post))); tok = post
        if tok: out.append((tok, False, False))
    return out
def caption(c, s, hl=GD, y=1060, size=44, a=1):
    words = parse(s)
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k, g in words]; gaps = [0 if g else sp for w, k, g in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(gaps[i-1] if cur else 0)
        if cur and cw+need > 760 and not words[i-1][2]: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(l for _, l in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, INK, .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k, g = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, NAVY if hl == GD else WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+gaps[i]

# ================= scènes =================
def s_hook(cv, c, u):
    text(c, "LES DIVIDENDES", 540, 250, 'sb', 30, GD2, 'c', .85, 8)
    glow_text(cv, "2 000 €", 540, 430, 230, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.75)
    glow_text(cv, "PAR MOIS", 540, 600, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.5, reflect=False)
    gpill(c, "SANS TRAVAILLER ?", 540, 745, GD, 44)
    put_emoji(cv, '🤔', 800, 250, 70)
    caption(c, "Combien il te faut pour toucher [2 000 € par mois] sans travailler ?")
    mister(cv, 'danse_parle_swing', 60)
def s_reperes(cv, c, u):
    text(c, "POUR TE SITUER", 540, 250, 'sb', 30, GD2, 'c', .85, 8)
    def d(k, w, h):
        x0, x1 = 70, w-70; lo, hi = 1000, 2600
        X = lambda v: x0+(v-lo)/(hi-lo)*(x1-x0)
        y = 300
        g = cairo.LinearGradient(x0, 0, x1, 0); g.add_color_stop_rgb(0, *rgb('3A6B8C')); g.add_color_stop_rgb(1, *rgb('FFC24A'))
        rr(k, x0, y-9, x1-x0, 18, 9); k.set_source(g); k.fill()
        for v in range(1000, 2601, 250):
            k.move_to(X(v), y+16); k.line_to(X(v), y+30); k.set_line_width(2); col(k, WHITE, .4); k.stroke()
        for v, lab, sub, colr, up in ((SMIC, "SMIC", "1 478 €", CY, True), (MEDIAN, "SALAIRE MÉDIAN", "2 190 €", WHITE, True), (NET_MOIS, "TON OBJECTIF", "2 000 €", GD, False)):
            x = X(v); k.arc(x, y, 17 if colr == GD else 12, 0, 2*math.pi); col(k, colr); k.fill()
            yy = y-150 if up else y+120
            k.move_to(x, y+(-20 if up else 20)); k.line_to(x, yy+(48 if up else -48)); k.set_line_width(2.5); col(k, colr, .8); k.stroke()
            text(k, lab, x, yy-24, 'xb', 26, colr, 'c', 1, 2); text(k, sub, x, yy+20, 'a', 52, colr, 'c')
        text(k, "net par mois, temps plein (SMIC au 1er juin 2026, médian du privé 2024)", w/2, h-36, 'sb', 21, ICE, 'c', .7)
    tp(cv, 920, 560, d, 540, 640, 'or', rx=.05)
    caption(c, "Le [SMIC], c'est environ 1 480 € nets par mois.", hl=CY)
    mister(cv, 'danse_parle_compte', 150)
def s_impot(cv, c, u):
    text(c, "DANS UN PEA DE PLUS DE 5 ANS", 540, 250, 'sb', 30, GD2, 'c', .85, 4)
    def d(k, w, h):
        text(k, "2 000 € × 12 MOIS", w/2, 52, 'xb', 30, ICE, 'c', .9, 2)
        text(k, "24 000 € / an", w/2, 120, 'a', 74, GD, 'c')
        x0, x1, y = 70, w-70, 260; tot = BRUT; xn = x0+(x1-x0)*NET_AN/tot
        rr(k, x0, y-40, xn-x0, 80, 18); col(k, GD); k.fill(); text(k, "CE QUE TU TOUCHES", (x0+xn)/2, y, 'xb', 24, INK, 'c', 1, 2)
        rr(k, xn+6, y-40, x1-xn-6, 80, 18); col(k, RD); k.fill(); text(k, "18,6 %", (xn+x1)/2+3, y, 'xb', 28, WHITE, 'c')
        text(k, "prélèvements sociaux", (xn+x1)/2+3, y+66, 'sb', 22, RD, 'c')
        text(k, "IL TE FAUT", w/2, 370, 'xb', 26, ICE, 'c', .85, 3)
        text(k, "29 484 €", w/2, 440, 'a', 90, WHITE, 'c'); text(k, "de dividendes par an", w/2, 510, 'sb', 26, ICE, 'c', .8)
    tp(cv, 900, 560, d, 540, 640, 'orange', rx=.05, ry=.04)
    caption(c, "Il te faut donc près de [30 000 €] de dividendes.")
    mister(cv, 'danse_parle_compte', 120)
def s_rendement(cv, c, u):
    text(c, "LE RENDEMENT", 540, 250, 'sb', 30, GD2, 'c', .85, 8)
    def d(k, w, h):
        text(k, "ce qu'une action te verse chaque année,", w/2, 56, 'sb', 30, ICE, 'c', .9)
        text(k, "rapporté à son prix", w/2, 100, 'sb', 30, ICE, 'c', .9)
        text(k, "100 €", 200, 270, 'a', 110, WHITE, 'c'); text(k, "placés", 200, 350, 'sb', 28, ICE, 'c', .8)
        k.move_to(350, 270); k.line_to(540, 270); k.set_line_width(6); col(k, GD); k.stroke(); k.move_to(540, 270); k.line_to(515, 252); k.line_to(515, 288); k.close_path(); k.fill()
        text(k, "3 %", 445, 236, 'xb', 34, GD, 'c')
        text(k, "3 €", 680, 270, 'a', 110, GD, 'c'); text(k, "chaque année", 680, 350, 'sb', 28, GD2, 'c', .9)
    tp(cv, 900, 430, d, 540, 600, 'or', rx=.05)
    put_emoji(cv, '🪙', 540+250, 860, 64)
    caption(c, "À [3 %], 100 € placés te rapportent [3 €] par an.")
    mister(cv, 'danse_parle_billets', 60)
def s_piles(cv, c, u):
    text(c, "POUR 2 000 € NETS PAR MOIS", 540, 240, 'sb', 30, GD2, 'c', .85, 4)
    s2, k = surface(); base = 900; Hmax = 470
    cols = [(220, 1.5, "ETF MONDE", "1,97 M€", ('FFE08A', 'C98A1E', '7A4E0A'), WHITE),
            (540, 3, "ETF DIVIDENDES", "983 000 €", ('FFE08A', 'C98A1E', '7A4E0A'), GD),
            (860, 5, "ACTIONS À GROS DIVIDENDES", "590 000 €", ('FFC08A', 'D0662A', '7A300A'), OR)]
    for x, r_, lab, val, cc, vc in cols:
        h = Hmax*CAP[r_]/CAP[1.5]; top = pile(k, x, base, h, 170, cc, crack=1.0 if r_ == 5 else 0)
        text(k, val, x, top-70, 'a', 54 if r_ != 1.5 else 60, vc, 'c'); text(k, f"{str(r_).replace('.', ',')} %", x, top-130, 'xb', 32, ICE, 'c', .9)
        text(k, lab, x, base+60, 'xb', 22 if r_ != 5 else 19, ICE, 'c', .85, 1)
    cv.alpha_composite(to_img(s2))
    caption(c, "Un ETF monde ne verse que [1,5 %] : il te faudrait près de [2 millions].")
    mister(cv, 'danse_parle_billets', 150)
def s_actions(cv, c, u):
    text(c, "LES GROS DIVIDENDES DU CAC 40", 540, 240, 'sb', 30, GD2, 'c', .85, 4)
    rows = [('CA', "CRÉDIT AGRICOLE", "7,5 %"), ('BNP', "BNP PARIBAS", "6,0 %"), ('ENGIE', "ENGIE", "5,8 %"), ('AXA', "AXA", "5,4 %"), ('ORANGE', "ORANGE", "5,2 %")]
    def d(k, w, h):
        for i, (key, nom, r_) in enumerate(rows):
            y = 60+i*92
            if i: k.move_to(40, y-46); k.line_to(w-40, y-46); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
            text(k, nom, 150, y, 'xb', 30, WHITE, 'l', 1, 1); text(k, r_, w-60, y, 'a', 52, GR, 'r')
        y = 60+5*92+20; rr(k, 30, y-44, w-60, 92, 22); col(k, RD, .16); k.fill_preserve(); k.set_line_width(2.5); col(k, RD, .9); k.stroke()
        text(k, "STELLANTIS", 150, y-12, 'xb', 30, WHITE, 'l', 1, 1); text(k, "plus rien depuis avril 2025", 150, y+24, 'sb', 22, ICE, 'l', .85); text(k, "0 €", w-60, y, 'a', 52, RD, 'r')
        text(k, "rendement sur le dividende 2025, cours au 1er novembre 2026", w/2, h-28, 'sb', 20, ICE, 'c', .65)
    tp(cv, 860, 640, d, 540, 625, 'orange', rx=.05, ry=-.04)
    for i, (key, _, _) in enumerate(rows): logo(cv, key, 540-430+20+80, 625-320+20+60+i*92, 60)
    logo(cv, 'STLA', 540-430+20+80, 625-320+20+60+5*92+20, 60, cross=True)
    caption(c, "Mais un dividende peut être [coupé du jour au lendemain].", hl=RD)
    mister(cv, 'danse_parle_prudent', 90)
def s_plafond(cv, c, u):
    text(c, "LE PIÈGE DU PLAFOND", 540, 240, 'sb', 30, GD2, 'c', .85, 6)
    def d(k, w, h):
        x0, x1, y0, y1 = 110, w-50, h-150, 80; T = 27; V = 340000
        X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/V
        for v in (100000, 200000, 300000):
            k.move_to(x0, Y(v)); k.line_to(x1, Y(v)); k.set_line_width(1); col(k, WHITE, .1); k.stroke(); text(k, f"{v//1000} k€", x0-14, Y(v), 'sb', 20, ICE, 'r', .6)
        for yr in (0, 10, 20): text(k, f"{yr} ans", X(yr), y0+30, 'sb', 20, ICE, 'c', .6)
        xc = X(12.5)
        # versements cumulés (1 000 €/mois) : au-delà de 150 000 €, ils débordent sur le compte-titres
        k.move_to(xc, Y(150000)); k.line_to(X(T), Y(1000*12*T)); k.line_to(X(T), Y(150000)); k.close_path(); col(k, OR, .28); k.fill()
        k.move_to(X(0), Y(0)); k.line_to(xc, Y(150000)); k.line_to(X(T), Y(150000)); k.set_line_width(6); col(k, GD); k.stroke()
        k.move_to(xc, Y(150000)); k.line_to(X(T), Y(1000*12*T)); k.set_dash([10, 8]); k.set_line_width(4); col(k, OR); k.stroke(); k.set_dash([])
        k.arc(xc, Y(150000), 11, 0, 2*math.pi); col(k, WHITE); k.fill()
        text(k, "PLAFOND DU PEA : 150 000 €", X(19.5), Y(150000)+34, 'xb', 24, GD, 'c', 1, 1)
        text(k, "COMPTE-TITRES", X(21), Y(220000), 'xb', 24, OR, 'c', 1, 1); text(k, "31,4 % de flat tax", X(21), Y(220000)+32, 'sb', 22, OR, 'c', .9)
        text(k, "versements de 1 000 €/mois", X(9), Y(40000), 'sb', 21, ICE, 'c', .75)
        rr(k, 60, h-104, w-120, 76, 22); col(k, OR, .14); k.fill()
        text(k, "Tout en compte-titres, à 3 % :", w/2-110, h-66, 'sb', 26, WHITE, 'c'); text(k, "1,17 M€", w/2+200, h-66, 'a', 46, OR, 'c')
    tp(cv, 920, 640, d, 540, 620, 'orange', rx=.05, ry=-.04)
    put_emoji(cv, '🔒', 540-460+20+110+(920-160)*12.5/27, 620-320+20+80+(640-230)*(1-150000/340000)-72, 46)
    caption(c, "Le PEA est plafonné à [150 000 €] de versements.")
    mister(cv, 'danse_parle_prudent', 170)
def s_courbe(cv, c, u):
    text(c, "LA BONNE NOUVELLE", 540, 240, 'sb', 30, GD2, 'c', .85, 6)
    def d(k, w, h):
        x0, x1, y0, y1 = 110, w-50, h-90, 70; T = 34; V = 1100000
        X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/V
        for v in (250000, 500000, 750000, 1000000):
            k.move_to(x0, Y(v)); k.line_to(x1, Y(v)); k.set_line_width(1); col(k, WHITE, .1); k.stroke(); text(k, f"{v//1000} k€" if v < 1e6 else "1 M€", x0-14, Y(v), 'sb', 20, ICE, 'r', .6)
        for yr in (0, 10, 20, 30): text(k, f"{yr} ans", X(yr), y0+30, 'sb', 20, ICE, 'c', .6)
        r = .07/12; pts = []; pv = []; val = 0; vers = 0
        for m in range(0, T*12+1):
            if m > 0: val = val*(1+r)+(1000 if m <= 150 else 0); vers = min(150000, 1000*m)
            pts.append((X(m/12), Y(val))); pv.append((X(m/12), Y(vers)))
        k.move_to(*pv[0]); [k.line_to(*p) for p in pv]; k.set_line_width(4); col(k, CY, .9); k.stroke()
        k.move_to(*pts[0]); [k.line_to(*p) for p in pts]; k.line_to(pts[-1][0], y0); k.line_to(x0, y0); k.close_path()
        g = cairo.LinearGradient(0, y1, 0, y0); g.add_color_stop_rgba(0, 1, .76, .29, .45); g.add_color_stop_rgba(1, 1, .76, .29, 0); k.set_source(g); k.fill()
        k.move_to(*pts[0]); [k.line_to(*p) for p in pts]; k.set_line_width(6); col(k, GD); k.stroke()
        xm = X(32.8); k.move_to(xm, Y(982800)); k.line_to(xm, y0); k.set_dash([6, 6]); k.set_line_width(2); col(k, WHITE, .6); k.stroke(); k.set_dash([])
        k.arc(xm, Y(982800), 11, 0, 2*math.pi); col(k, WHITE); k.fill()
        text(k, "983 000 €", xm-14, Y(982800)-36, 'a', 44, GD, 'r'); text(k, "en 33 ans", xm-14, Y(982800)+4, 'sb', 24, GD2, 'r')
        text(k, "1 000 €/mois pendant 12 ans et demi, puis plus rien", X(17), Y(150000)-30, 'sb', 22, CY, 'c'); text(k, "150 000 € versés", X(28), Y(150000)+30, 'xb', 22, CY, 'c')
        text(k, "hypothèse : 7 % par an, jamais garanti", w/2, h-34, 'sb', 21, ICE, 'c', .75)
    tp(cv, 920, 620, d, 540, 620, 'vert', rx=.05)
    caption(c, "Tu atteins le [million] en [33 ans] environ.", hl=GR)
    mister(cv, 'danse_joie_silence', 100)
def s_fin(cv, c, u):
    glow_text(cv, "ET TOI,", 540, 420, 140, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6)
    glow_text(cv, "TU EN ES OÙ ?", 540, 590, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 740, 'sb', 36, ICE, 'c', .85); put_emoji(cv, '👇', 540, 810, 56)
    caption(c, "Et toi, tu en es où ?")
    mister(cv, 'danse_parle_swing', 200)
SCENES = [s_hook, s_reperes, s_impot, s_rendement, s_piles, s_actions, s_plafond, s_courbe, s_fin]
POS = [540, 430, 650, 540, 540, 420, 640, 540, 540]
def still(i, t=0):
    cv = base_frame(t, POS[i]); CUR_X[0] = POS[i]; s, c = surface(); SCENES[i](cv, c, 1.0); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__':
    os.makedirs(f'{D}/prev', exist_ok=True)
    ims = []
    for i in range(len(SCENES)):
        im = still(i, [2, 10, 22, 32, 44, 55, 68, 80, 92][i]); im.save(f'{D}/prev/maquette_{i+1}.png'); ims.append(im)
    P = Image.new('RGB', (360*5, 640*2), (0, 0, 0))
    for k, im in enumerate(ims): P.paste(im.resize((360, 640)), ((k % 5)*360, (k//5)*640))
    P.save(f'{D}/prev/maquettes.png'); print('ok')
