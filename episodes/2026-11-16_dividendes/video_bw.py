"""Vidéo dividendes, version « dessin animé 1930 » : décors Gemini noir et blanc (scène de music-hall, salle des coffres, campagne),
Mister Coin en noir et blanc, seul l'or reste en or (pièces, piles, chiffres). Effets de pellicule (grain, scintillement, image qui
flotte, poussières, rayures, vignette), ouvertures et fermetures à l'iris aux changements de décor, objets dessinés à l'encre.
Calage, sous-titres et plan des clips de Mister Coin repris de video.py.
usage : python3 video_bw.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
from scenes import surface, to_img, rr, col, W, H, clamp, ease, rgb, CAP, BRUT, NB
FPS = 60; DUR = V.DUR; VOICE = V.VOICE
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def ent(k, d=.45): return ease(k/d)
def back(x, s=1.9): x = clamp(x); return max(1e-3, 1+(s+1)*(x-1)**3+s*(x-1)**2)      # rebond « caoutchouc », jamais 0 (cairo)
GOLD = ('FFE27A', 'F2B82E', 'B97A12', '6B4006'); INKC = '0D0D0D'; PAPER = 'F4F1EA'

# ---------- décors Gemini (720×1280, 24 i/s) : lus en aller-retour pour boucler sans raccord ----------
DEC = {'scene': f'{D}/decors/decor_scene.mp4', 'coffre': f'{D}/decors/decor_coffre.mp4', 'campagne': f'{D}/decors/decor_campagne.mp4'}
@functools.lru_cache(maxsize=3)
def dec_frames(name):
    p = DEC[name] if os.path.exists(DEC[name]) else DEC['scene']
    cap = cv2.VideoCapture(p); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    return F
ZOOM = 1.16                                                                  # le décor est agrandi depuis le haut : la tache de lumière descend sous Mister Coin
def decor(name, t):
    F = dec_frames(name); n = len(F); i = int(t*24) % (2*n-2); i = i if i < n else 2*n-2-i
    g = F[i].astype(np.float32)
    g = cv2.resize(g, (int(W*ZOOM), int(H*ZOOM)), interpolation=cv2.INTER_CUBIC); x0 = (g.shape[1]-W)//2; g = g[:H, x0:x0+W]
    g = np.clip((g-12)*1.08, 0, 255)                                         # noirs plus profonds, comme une copie d'époque
    return g
# ---------- Mister Coin en noir et blanc ----------
def coin_bw(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, 540, Y)
    L = (rgb_[..., 0]*.30+rgb_[..., 1]*.59+rgb_[..., 2]*.11); L = np.clip((L-128)*1.25+140, 0, 255)
    fx = V.MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), V.FEET-3), (95, 15), 0, 0, 360, .6, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    return cv_rgb*(1-al[..., None])+L[..., None]*al[..., None]

# ---------- or dessiné : rendu Blender passé en aplats + contour à l'encre ----------
def toon(rgba, outline=3):
    a = rgba[..., 3].astype(np.float32)/255; L = rgba[..., :3].astype(np.float32).mean(2)
    q = np.digitize(L, [70, 130, 200]); pal = np.array([rgb(GOLD[3]), rgb(GOLD[2]), rgb(GOLD[1]), rgb(GOLD[0])], np.float32)*255
    col_ = pal[q]
    ed = cv2.Canny(cv2.GaussianBlur(L.astype(np.uint8), (0, 0), 1.2), 40, 110) > 0
    col_[ed] = col_[ed]*.25
    am = (a > .5).astype(np.uint8); dil = cv2.dilate(am, np.ones((2*outline+1, 2*outline+1), np.uint8))
    out = np.zeros(rgba.shape, np.float32); out[..., :3] = col_; out[..., 3] = am*255
    ring = (dil > 0) & (am == 0); out[ring, :3] = 13; out[ring, 3] = 255
    return out.astype(np.uint8)
@functools.lru_cache(maxsize=2)
def stack_toon(w):
    full, face, pitch = V.stack_scaled(w); return Image.fromarray(toon(np.asarray(full)), 'RGBA'), face, pitch
def pile(cv, cx, base, n_target, t, t0, t1, crack=0.0, w=170):
    full, face, pitch = stack_toon(w)
    u = clamp((t-t0)/(t1-t0)); n = n_target if t >= t1 else int(round(n_target*(u**1.15)))
    if n <= 0: return base, 0
    hh = int(face+n*pitch); im = full.crop((0, 0, w, min(full.height, hh)))
    s2, k = surface(); k.save(); k.translate(cx, base); k.scale(w*.75, 16); k.arc(0, 0, 1, 0, 2*math.pi); k.restore(); col(k, INKC, .55); k.fill(); cv.alpha_composite(to_img(s2))
    top = base-im.height; cv.alpha_composite(im, (int(cx-w/2), int(top)))
    if t0 < t < t1:
        dt_c = (t1-t0)/max(1, n_target); ph = ((t-t0) % dt_c)/dt_c
        cv.alpha_composite(full.crop((0, 0, w, int(face+pitch*1.4))), (int(cx-w/2), int(top-pitch-260*(1-ph)**2)))
    if crack > 0:
        s3, kk = surface(); y = top+face*.5; kk.move_to(cx+6, y); pts = [(cx-14, y+50), (cx+18, y+110), (cx-8, y+180), (cx+14, y+260)]
        for (x2, y2) in pts[:max(1, int(len(pts)*crack))]: kk.line_to(x2, min(y2, base-12))
        kk.set_line_width(6); col(kk, INKC); kk.stroke(); cv.alpha_composite(to_img(s3))
    return top, n

# ---------- lettrage « carton de 1930 » : encre noire épaisse, ombre portée ----------
def ink_text(c, s_, x, y, size, fill=PAPER, fam='Alfa Slab One', align='c', a=1.0, outline=None, wob=0.0, rot=0.0):
    c.save(); c.select_font_face(fam, 0, 0); c.set_font_size(size); e = c.text_extents(s_)
    xx = x-e.x_advance/2 if align == 'c' else (x-e.x_advance if align == 'r' else x)
    c.translate(xx, y+size*.35); c.rotate(rot)
    ol = outline or max(4, size*.10)
    c.move_to(ol*.5, ol*.7); c.text_path(s_); c.set_source_rgba(0, 0, 0, .55*a); c.fill()               # ombre
    c.move_to(0, 0); c.text_path(s_); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(ol*2); col(c, INKC, a); c.stroke_preserve(); col(c, fill, a); c.fill()
    c.restore(); return e.x_advance
def ink_line(c, pts, wdt=6, colr=INKC, a=1.0, seed=0, t=0.0):
    """trait à l'encre qui « bout » légèrement (le dessin bouge d'une image dessinée à l'autre, 12 fois par seconde)"""
    rng = np.random.default_rng(seed+int(t*12)); c.new_path()
    for i, (x, y) in enumerate(pts):
        j = rng.normal(0, .9, 2); (c.move_to if i == 0 else c.line_to)(x+j[0], y+j[1])
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(wdt); col(c, colr, a); c.stroke()
def banner(c, x, y, w, h, a=1.0, t=0.0):
    """bandeau de papier à bords ondulés, cerné d'encre (support des titres)"""
    rng = np.random.default_rng(int(t*12)); c.new_path(); N = 24
    pts = [(x-w/2+w*i/N, y-h/2+rng.normal(0, 1.2)) for i in range(N+1)]+[(x+w/2+rng.normal(0, 1.2), y+h/2)]+[(x+w/2-w*i/N, y+h/2+rng.normal(0, 1.2)) for i in range(N+1)]
    c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.close_path()
    col(c, PAPER, a); c.fill_preserve(); c.set_line_width(5); col(c, INKC, a); c.stroke()

# ---------- effets de pellicule ----------
@functools.lru_cache(maxsize=1)
def vignette():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xs-W/2)/(W*.62))**2+((ys-H/2)/(H*.62))**2)
    return np.clip(1-.55*np.clip(r-.55, 0, 1)**1.4*2.2, .3, 1)
def film(img, t):
    f = int(t*24); rng = np.random.default_rng(7000+f)
    dx, dy = 1.4*math.sin(f*1.7)+rng.normal(0, .5), 1.2*math.sin(f*1.13+1)+rng.normal(0, .5)           # l'image flotte dans le couloir
    M = np.float32([[1, 0, dx], [0, 1, dy]]); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    img = img*(1+rng.normal(0, .025))                                                                 # scintillement
    g = cv2.resize(rng.normal(0, 1, (H//2, W//2)).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    img = img+g[..., None]*9                                                                           # grain
    for _ in range(rng.integers(2, 7)):                                                                # poussières
        x, y = rng.integers(0, W), rng.integers(0, H); r = rng.uniform(1.5, 4.5); v = 0 if rng.random() < .7 else 240
        cv2.circle(img, (int(x), int(y)), int(r), (v, v, v), -1, lineType=cv2.LINE_AA)
    if rng.random() < .35:                                                                             # rayure verticale
        x = int(rng.uniform(80, W-80)); cv2.line(img, (x, 0), (x+int(rng.normal(0, 6)), H), (210, 210, 210), 1, cv2.LINE_AA)
    return np.clip(img*vignette()[..., None], 0, 255)
def iris(img, u, cx=540, cy=1250):
    """fermeture à l'iris : u = 0 ouvert, 1 fermé"""
    if u <= 0: return img
    R = (1-u)*1300; m = np.zeros((H, W), np.float32); cv2.circle(m, (cx, cy), max(0, int(R)), 1, -1, lineType=cv2.LINE_AA)
    return img*m[..., None]

# ================= scènes =================
def card(c, x, y, w, h, k, t, rot=-.015):
    """carton de papier cerné d'encre qui arrive en rebond"""
    s_ = back(k/.42); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s_, s_)
    rng = np.random.default_rng(int(t*12)); c.new_path(); N = 18
    pts = [(-w/2+w*i/N, -h/2+rng.normal(0, 1)) for i in range(N+1)]+[(w/2+rng.normal(0, 1), -h/2+h*i/N) for i in range(1, N+1)]
    pts += [(w/2-w*i/N, h/2+rng.normal(0, 1)) for i in range(1, N+1)]+[(-w/2+rng.normal(0, 1), h/2-h*i/N) for i in range(1, N)]
    c.move_to(pts[0][0]+8, pts[0][1]+10); [c.line_to(p[0]+8, p[1]+10) for p in pts[1:]]; c.close_path(); col(c, '000000', .45); c.fill()
    c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.close_path(); col(c, PAPER); c.fill_preserve(); c.set_line_width(6); col(c, INKC); c.stroke()
    c.translate(-w/2, -h/2); return s_
def end_card(c): c.restore()
def title_bw(c, s_, k, t, y=262):
    if k < 0: return
    a = ent(k, .3); ink_text(c, s_, 540, y, 38, PAPER, 'Alfa Slab One', a=a, outline=4)
def num(c, s_, x, y, size, k, gold=True, align='c'):
    if k < 0: return
    s = back(k/.35); c.save(); c.translate(x, y); c.scale(s, s); ink_text(c, s_, 0 if align == 'c' else 0, 0, size, GOLD[0] if gold else PAPER, align=align); c.restore()

def b_hook(cv, c, t, k):
    ink_text(c, "LES DIVIDENDES", 540, 262, 38, PAPER, 'Alfa Slab One', a=ent(k, .3), outline=4)
    num(c, "2 000 €", 540, 450, 200, k)
    num(c, "PAR MOIS", 540, 620, 88, k-.5, gold=False)
    if k > 1.4:
        s = back((k-1.4)/.35); c.save(); c.translate(540, 760); c.scale(s, s); c.rotate(-.03); banner(c, 0, 0, 560, 100, t=t); ink_text(c, "SANS TRAVAILLER ?", 0, 0, 46, INKC, 'Alfa Slab One', outline=1.2); c.restore()
def b_reperes(cv, c, t, k):
    title_bw(c, "POUR TE SITUER", k, t)
    card(c, 540, 640, 920, 560, k, t)
    x0, x1 = 70, 850; lo, hi = 1000, 2600; X = lambda v: x0+(v-lo)/(hi-lo)*(x1-x0); y = 330
    ink_line(c, [(x0+(x1-x0)*i/30*ent(k, .6), y) for i in range(31)], 10, INKC, seed=3, t=t)
    for v in range(1000, 2601, 250): ink_line(c, [(X(v), y+12), (X(v), y+30)], 4, INKC, seed=v, t=t)
    for (t0, v, lab, sub, gold, up) in ((V.SMIC_T, S.SMIC, "SMIC", "1 478 €", False, True), (V.MED_T, S.MEDIAN, "MÉDIAN", "2 190 €", False, True), (V.OBJ_T, S.NET_MOIS, "TON OBJECTIF", "2 000 €", True, False)):
        kk = t-t0
        if kk < 0: continue
        s = back(kk/.35); x = X(v); yy = y-150 if up else y+130
        ink_line(c, [(x, y), (x, lerp(y, yy+(50 if up else -50), clamp(s)))], 6, INKC, seed=int(v), t=t)
        c.arc(x, y, 14, 0, 2*math.pi); col(c, GOLD[1] if gold else INKC); c.fill_preserve(); c.set_line_width(4); col(c, INKC); c.stroke()
        c.save(); c.translate(x, yy); c.scale(s, s)
        ink_text(c, lab, 0, -30, 26, INKC, 'Limelight', outline=.8); ink_text(c, sub, 0, 18, 54, GOLD[0] if gold else PAPER); c.restore()
    end_card(c)
def b_impot(cv, c, t, k):
    title_bw(c, "DANS UN PEA DE PLUS DE 5 ANS", k, t)
    card(c, 540, 640, 900, 580, k, t, rot=.012)
    ink_text(c, "2 000 € × 12 MOIS", 450, 60, 30, INKC, 'Limelight', outline=.8, a=ent(t-14.4, .3))
    num(c, f"{int(V.count_to(24000, (t-15.6)/1.2)):,} € par an".replace(',', NB), 450, 140, 70, t-15.5)
    x0, x1, y = 70, 830, 290; xn = x0+(x1-x0)*S.NET_AN/BRUT
    g1 = ent(t-16.6, .5)
    if g1 > 0:
        rr(c, x0, y-42, (xn-x0)*g1, 84, 16); col(c, GOLD[1]); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke()
        if g1 > .7: ink_text(c, "CE QUE TU TOUCHES", (x0+xn)/2, y, 24, PAPER, outline=3)
    if t > 20.9:
        s = back((t-20.9)/.35); c.save(); c.translate((xn+x1)/2+4, y); c.scale(s, s)
        rr(c, -(x1-xn)/2, -42, x1-xn-6, 84, 16); col(c, '3A3A3A'); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke(); ink_text(c, "18,6 %", 0, 0, 30, PAPER, outline=3); c.restore()
        ink_text(c, "pour l'État", (xn+x1)/2, y+70, 24, INKC, 'Limelight', outline=.6, a=ent(t-21.2, .3))
    if t > 24.4:
        ink_text(c, "IL TE FAUT", 450, 410, 28, INKC, 'Limelight', outline=.8, a=ent(t-24.4, .3))
        num(c, f"{int(V.count_to(BRUT, (t-24.5)/1.4)):,} €".replace(',', NB), 450, 480, 86, t-24.5)
        ink_text(c, "de dividendes par an", 450, 545, 26, INKC, 'Limelight', outline=.6, a=ent(t-24.8, .3))
    end_card(c)
def b_rendement(cv, c, t, k):
    title_bw(c, "LE RENDEMENT", k, t)
    card(c, 540, 600, 900, 440, k, t)
    a1 = ent(t-29.3, .3); ink_text(c, "ce qu'une action te verse chaque année,", 450, 60, 28, INKC, 'Limelight', outline=.6, a=a1); ink_text(c, "rapporté à son prix", 450, 102, 28, INKC, 'Limelight', outline=.6, a=a1)
    num(c, "100 €", 200, 270, 100, t-33.6, gold=False)
    if t > 34.6:
        u = ent(t-34.6, .4); ink_line(c, [(340+190*u*i/10, 270) for i in range(11)], 9, INKC, seed=5, t=t)
        xe = 340+190*u; c.move_to(xe+10, 270); c.line_to(xe-18, 250); c.line_to(xe-18, 290); c.close_path(); col(c, INKC); c.fill()
        ink_text(c, "3 %", 435, 225, 36, GOLD[0])
    num(c, "3 €", 690, 270, 100, t-35.6)
    ink_text(c, "chaque année", 690, 355, 26, INKC, 'Limelight', outline=.6, a=ent(t-35.8, .3))
    end_card(c)
def b_piles(cv, c, t, k, show3=False, crack=0.0):
    if t < 66.4: title_bw(c, "POUR 2 000 € NETS PAR MOIS", k, t)
    base = 885
    for i, (x, r_, lab, tint, vc, t0, t1) in enumerate(V.PILES):
        if (i == 2 and not show3) or t < t0-.4: continue
        top, n = pile(cv, x, base, V.N_COINS[r_], t, t0, t1, crack if i == 2 else 0)
        v = CAP[r_]*min(1, n/V.N_COINS[r_]); ty = min(top, base-20)
        ink_text(c, V.euro(v) if v >= 1e6 else f"{int(round(v, -3)):,} €".replace(',', NB), x, ty-62, 54 if r_ != 1.5 else 58, GOLD[0])
        ink_text(c, f"{str(r_).replace('.', ',')} %", x, ty-122, 34, PAPER)
        ink_text(c, lab, x, base+42, 21 if r_ != 5 else 17, PAPER, 'Alfa Slab One', outline=3)
    if show3 and t > 66.6:
        s = back((t-66.6)/.35); c.save(); c.translate(700, 262); c.scale(s, s); c.rotate(.03); banner(c, 0, 0, 520, 112, t=t)
        ink_text(c, "STELLANTIS : 0 €", 0, -14, 34, INKC, outline=1.2); ink_text(c, "plus rien depuis avril 2025", 0, 26, 22, INKC, 'Limelight', outline=.5); c.restore()
def b_piles1(cv, c, t, k): b_piles(cv, c, t, k)
def b_piles2(cv, c, t, k): b_piles(cv, c, t, 9, True, ent(t-64.6, 1.0))
def b_actions(cv, c, t, k):
    title_bw(c, "LES GROS DIVIDENDES DU CAC 40", k, t)
    card(c, 540, 600, 860, 560, k, t, rot=-.01)
    for i, (key, nom, r_, t0) in enumerate(V.ACT):
        y = 70+i*96
        if i: ink_line(c, [(40, y-48), (820, y-48)], 2, INKC, a=.5, seed=i, t=t)
        if t > t0: ink_text(c, nom, 150, y, 30, INKC, 'Alfa Slab One', 'l', outline=.6, a=ent(t-t0, .25))
        if t > 58.2+i*.12: num(c, r_, 760, y, 46, t-58.2-i*.12)
    ink_text(c, "rendement sur le dividende 2025, cours au 1er novembre 2026", 430, 530, 18, INKC, 'Limelight', outline=.3, a=.8*ent(k, .5))
    end_card(c)
def b_plafond(cv, c, t, k):
    title_bw(c, "LE PIÈGE DU PLAFOND", k, t)
    card(c, 540, 620, 920, 640, k, t, rot=.01)
    x0, x1, y0, y1 = 110, 870, 490, 80; T = 27; Vv = 340000; X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/Vv
    ink_line(c, [(x0, y1-20), (x0, y0), (x1, y0)], 4, INKC, seed=1, t=t)
    for v in (100000, 200000, 300000): ink_text(c, f"{v//1000} k€", x0-14, Y(v), 20, INKC, 'Limelight', 'r', outline=.3)
    for yr in (0, 10, 20): ink_text(c, f"{yr} ans", X(yr), y0+30, 20, INKC, 'Limelight', outline=.3)
    xc = X(12.5); u1 = inout((t-71.2)/2.4)
    if u1 > 0: ink_line(c, [(X(12.5*u1*i/20), Y(150000*u1*i/20)) for i in range(21)], 8, GOLD[2], seed=2, t=t)
    if t > 73.7:
        ink_line(c, [(xc, Y(150000)), (X(T), Y(150000))], 8, GOLD[2], seed=4, t=t)
        ink_text(c, "PLAFOND DU PEA : 150 000 €", X(19.5), Y(150000)+36, 24, INKC, 'Alfa Slab One', outline=.5, a=ent(t-73.7, .3))
    u2 = inout((t-74.4)/3.0)
    if u2 > 0:
        xe = 12.5+(T-12.5)*u2; c.move_to(xc, Y(150000)); c.line_to(X(xe), Y(12000*xe)); c.line_to(X(xe), Y(150000)); c.close_path(); col(c, '9A9A9A', .5); c.fill()
        ink_line(c, [(xc+(X(xe)-xc)*i/12, Y(150000+(12000*xe-150000)*i/12)) for i in range(13)], 5, INKC, seed=6, t=t)
        ink_text(c, "COMPTE-TITRES", X(20.5), Y(230000), 24, INKC, 'Alfa Slab One', outline=.5, a=ent(u2-.4, .3)); ink_text(c, "31,4 % de flat tax", X(20.5), Y(230000)+32, 20, INKC, 'Limelight', outline=.4, a=ent(u2-.4, .3))
    if t > 78.4:
        ink_text(c, "Tout en compte-titres, à 3 % :", 360, 585, 26, INKC, 'Limelight', outline=.6, a=ent(t-78.4, .3)); num(c, V.euro(V.count_to(S.CTO3, (t-78.5)/1.5)), 720, 585, 44, t-78.5)
    end_card(c)
def b_courbe(cv, c, t, k):
    title_bw(c, "LA BONNE NOUVELLE", k, t)
    card(c, 540, 620, 920, 620, k, t, rot=-.012)
    x0, x1, y0, y1 = 110, 870, 520, 70; T = 34; Vv = 1100000; X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/Vv
    ink_line(c, [(x0, y1-20), (x0, y0), (x1, y0)], 4, INKC, seed=1, t=t)
    for v in (250000, 500000, 750000, 1000000): ink_text(c, f"{v//1000} k€" if v < 1e6 else "1 M€", x0-14, Y(v), 20, INKC, 'Limelight', 'r', outline=.3)
    for yr in (0, 10, 20, 30): ink_text(c, f"{yr} ans", X(yr), y0+30, 20, INKC, 'Limelight', outline=.3)
    u = inout((t-83.2)/8.2); Mmax = int(397*u); r = .07/12; val = 0; pts = []
    for m in range(0, Mmax+1):
        if m > 0: val = val*(1+r)+(1000 if m <= 150 else 0)
        if m % 3 == 0 or m == Mmax: pts.append((X(m/12), Y(val)))
    if len(pts) > 1:
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts]; c.line_to(pts[-1][0], y0); c.line_to(x0, y0); c.close_path(); col(c, GOLD[1], .55); c.fill()
        ink_line(c, pts, 8, GOLD[2], seed=7, t=t); ink_line(c, pts, 2, INKC, seed=8, t=t)
        num(c, "1 MILLION €" if Mmax >= 397 else V.euro(val), min(pts[-1][0], 720), pts[-1][1]-40, 40, 1, align='c')
    if t > 84.0: [ink_text(c, l_, 340, 140+28*i_, 22, INKC, 'Limelight', outline=.4, a=ent(t-84, .3)) for i_, l_ in enumerate(("1 000 €/mois pendant 12 ans et demi,", "puis plus rien"))]
    if t > 91.4: ink_text(c, "en 33 ans !", 340, 240, 34, INKC, 'Alfa Slab One', outline=.6, a=ent(t-91.4, .3))
    ink_text(c, "hypothèse : 7 % par an, jamais garanti", 460, 590, 20, INKC, 'Limelight', outline=.4, a=ent(k, .5))
    end_card(c)
def b_fin(cv, c, t, k):
    num(c, "ET TOI,", 540, 420, 130, k, gold=False); num(c, "TU EN ES OÙ ?", 540, 580, 110, k-.3)
    if k > .9: ink_text(c, "Dis-le en commentaire", 540, 740, 36, PAPER, 'Alfa Slab One', a=ent(k-.9, .3), outline=4); S.put_emoji(cv, '👇', 540, 815+8*math.sin(k*5), 56)
SC = [(0.0, 3.4, b_hook, 'scene'), (3.4, 14.2, b_reperes, 'scene'), (14.2, 27.2, b_impot, 'scene'), (27.2, 37.2, b_rendement, 'scene'), (37.2, 51.8, b_piles1, 'coffre'),
      (51.8, 60.0, b_actions, 'coffre'), (60.0, 70.0, b_piles2, 'coffre'), (70.0, 82.0, b_plafond, 'scene'), (82.0, 92.8, b_courbe, 'campagne'), (92.8, DUR, b_fin, 'scene')]
IRIS = [a for (a, b, f, d), (a0, b0, f0, d0) in zip(SC[1:], SC[:-1]) if d != d0]          # iris à chaque changement de décor
IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    # pendant l'iris on reste sur le décor d'avant jusqu'à la fermeture complète
    img = np.repeat(decor(dec, t)[..., None], 3, 2).astype(np.float32)
    cv = Image.fromarray(img.astype(np.uint8)).convert('RGBA')
    # contenu : fondu court entre deux scènes d'un même décor, coupe franche sous l'iris
    for j in (i-1, i):
        if j < 0: continue
        a_, b_, f_, d_ = SC[j]
        if j == i-1 and (t-a > .3 or d_ != dec): continue
        al = 1-ent(t-b_, .3) if j == i-1 else (ent(t-a, .3) if (i > 0 and SC[i-1][3] == dec) else 1)
        lay = cv.copy(); s, c = surface(); f_(lay, c, t, max(0.0, t-a_)); lay.alpha_composite(to_img(s))
        cv = Image.blend(cv, lay, al) if al < .999 else lay
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_bw(arr, t)
    arr = film(arr, t)
    for ta in IRIS:
        if ta-IR <= t < ta: arr = iris(arr, inout((t-(ta-IR))/IR))
        elif ta <= t < ta+IR: arr = iris(arr, 1-inout((t-ta)/IR))
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_bw(c, t); out.alpha_composite(to_img(s))
    return out
def cap_bw(c, t):
    """sous-titres : seul l'or surligne (les mises en garde sont surlignées en blanc papier)"""
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else PAPER, a=al); return
def events():
    ev = [e for e in V.events() if e[1] != 'swish'] + [(ta-IR, 'whoosh') for ta in IRIS]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/bw_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(k/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
