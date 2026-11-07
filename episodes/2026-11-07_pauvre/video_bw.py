"""Vidéo « Pourquoi tu restes pauvre ? », dessin animé 1930 : décors Gemini noir et blanc (théâtre, mansarde, banque, rue commerçante),
Mister Coin en noir et blanc (il retrouve ses couleurs à la fin), seul l'or reste en or, effets de pellicule, iris aux changements de décor.
usage : python3 video_bw.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
from scenes import surface, to_img, rr, col, W, H, clamp, ease, rgb, NB
FPS = 60; DUR = V.DUR; VOICE = V.VOICE; euro, count_to = V.euro, V.count_to
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def ent(k, d=.45): return ease(k/d)
def back(x, s=1.9): x = clamp(x); return max(1e-3, 1+(s+1)*(x-1)**3+s*(x-1)**2)      # rebond « caoutchouc », jamais 0 (cairo)
GOLD = ('FFE27A', 'F2B82E', 'B97A12', '6B4006'); INKC = '0D0D0D'; PAPER = 'F4F1EA'

# ---------- décors Gemini (720×1280, 24 i/s) : lus une seule fois, ralentis pour couvrir tout le passage sur ce décor ----------
DEC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('scene', 'mansarde', 'banque', 'rue')}
@functools.lru_cache(maxsize=2)
def dec_frames(name):
    cap = cv2.VideoCapture(DEC[name]); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    return F
ZOOM = {'scene': 1.16}                                                       # théâtre agrandi depuis le haut : la tache de lumière descend sous Mister Coin
def decor(name, t):
    F = dec_frames(name); n = len(F)
    a, b = next((a, b) for (a, b, d) in BLOCS if d == name and a <= t < b+.5)
    sp = min(1.0, (n-1)/24/max(.1, b-a)); i = min(n-1, int((t-a)*sp*24))       # le décor avance à vitesse constante, sans boucle
    g = F[i].astype(np.float32); z = ZOOM.get(name, 1.0)
    g = cv2.resize(g, (int(W*z), int(H*z)), interpolation=cv2.INTER_CUBIC); x0 = (g.shape[1]-W)//2; g = g[:H, x0:x0+W]
    g = np.clip((g-12)*1.08, 0, 255)                                         # noirs plus profonds, comme une copie d'époque
    return g
# ---------- Mister Coin en noir et blanc ----------
def coin_bw(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, 540, Y)
    L = (rgb_[..., 0]*.30+rgb_[..., 1]*.59+rgb_[..., 2]*.11); L = np.clip((L-128)*1.25+140, 0, 255)
    fx = V.MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), V.FEET-3), (95, 15), 0, 0, 360, .6, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    coin = np.repeat(L[..., None], 3, 2)
    if t > COL_T:                                                     # fin : il retrouve ses couleurs, des pieds au chapeau
        rows = np.where(al.max(1) > .05)[0]
        if len(rows):
            top, bot = rows[0], rows[-1]; u = inout((t-COL_T)/COL_D); front = bot+60-(bot-top+180)*u
            yy = np.arange(H, dtype=np.float32)[:, None]
            m = np.clip((yy-front)/60+.5, 0, 1)                         # bord doux de 60 px
            glow = np.exp(-((yy-front)/26)**2)*(1-u)*.45              # liseré lumineux qui monte avec le front
            coin = coin*(1-m[..., None])+rgb_.astype(np.float32)*m[..., None]
            coin = coin+glow[..., None]*np.array([255, 226, 140], np.float32)
    return cv_rgb*(1-al[..., None])+coin*al[..., None]
COL_T, COL_D = V.COL_T, 1.6

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
# ================= objets dessinés =================
def box(c, x, y, w, h, label, fill=PAPER, txt=INKC, a=1.0, size=24):
    rr(c, x-w/2+6, y-h/2+8, w, h, 18); col(c, '000000', .4*a); c.fill()
    rr(c, x-w/2, y-h/2, w, h, 18); col(c, fill, a); c.fill_preserve(); c.set_line_width(5); col(c, INKC, a); c.stroke()
    ink_text(c, label, x, y, size, txt, 'Alfa Slab One', outline=.6 if txt == INKC else 3, a=a)
def arrow(c, x0, x1, y, u, t, seed=0):
    if u <= 0: return
    xe = x0+(x1-x0)*u; ink_line(c, [(x0+(xe-x0)*i/8, y) for i in range(9)], 7, INKC, seed=seed, t=t)
    c.move_to(xe+6, y); c.line_to(xe-16, y-14); c.line_to(xe-16, y+14); c.close_path(); col(c, INKC); c.fill()
def check(c, x, y, ok, k, t, seed=0):
    """coche ou croix tracée à l'encre, qui se dessine"""
    if k <= 0: return
    u = ent(k, .3)
    if ok: pts = [(x-20, y), (x-6, y+16), (x+24, y-20)]; n = max(2, int(3*u+.999)); ink_line(c, pts[:n], 8, INKC, seed=seed, t=t)
    else:
        ink_line(c, [(x-18, y-18), (x-18+36*u, y-18+36*u)], 8, INKC, seed=seed, t=t)
        if u > .5: ink_line(c, [(x+18, y-18), (x+18-36*(u-.5)*2, y-18+36*(u-.5)*2)], 8, INKC, seed=seed+1, t=t)
def stamp(c, x, y, l1, l2, k, t, rot=-.05, w=640, h=118):
    if k <= 0: return
    s = back(k/.35); c.save(); c.translate(x, y); c.scale(s, s); c.rotate(rot); banner(c, 0, 0, w, h, t=t)
    ink_text(c, l1, 0, -16 if l2 else 0, 34, INKC, outline=1.2)
    if l2: ink_text(c, l2, 0, 28, 24, INKC, 'Limelight', outline=.5)
    c.restore()
def figure(c, x, y, r, sad, k, t, seed=0):
    """petit bonhomme noir dessiné : souriant, ou triste avec une larme (silhouette simple, pas un personnage connu)"""
    if k <= 0: return
    s = back(k/.35); c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(0, r*1.55, r*.95, math.pi, 2*math.pi); c.close_path(); col(c, '1A1A1A'); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke()
    c.arc(0, 0, r*.72, 0, 2*math.pi); col(c, '1A1A1A'); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke()
    for ex in (-r*.25, r*.25): c.arc(ex, -r*.12, r*.08, 0, 2*math.pi); col(c, PAPER); c.fill()
    c.new_path()
    if sad: c.arc(0, r*.42, r*.24, math.pi*1.15, math.pi*1.85)
    else: c.arc(0, r*.06, r*.28, math.pi*.15, math.pi*.85)
    c.set_line_width(5); col(c, PAPER); c.stroke()
    if sad:
        ty = r*.02+r*.25*((t*.8) % 1); c.move_to(r*.25, ty-r*.12); c.curve_to(r*.33, ty, r*.33, ty+r*.1, r*.25, ty+r*.1); c.curve_to(r*.17, ty+r*.1, r*.17, ty, r*.25, ty-r*.12)
        col(c, PAPER, .9); c.fill()
    c.restore()

# pluie d'abonnements : tuiles façon icône d'appli (logos demandés par Nicolas pour cette vidéo, dossier logos/)
LOGOS = ['netflix', 'apple', 'basicfit', 'spotify', 'canalplus', 'strava', 'youtube']
_LS = {}
def logo_surf(n):
    if n not in _LS: _LS[n] = cairo.ImageSurface.create_from_png(f'{D}/logos/{n}.png')
    return _LS[n]
_rng = np.random.default_rng(7)
RAIN = [(41.7+.13*i, 110+_rng.random()*860, LOGOS[i % len(LOGOS)], (_rng.random()-.5)*2.4, (_rng.random()-.5)*.6) for i in range(26)]
def rain(c, t):
    for (t0, x, n, spin, rot0) in RAIN:
        dt = t-t0
        if dt <= 0 or dt > 1.6: continue
        y = -140+60*dt+.5*2200*dt*dt; xx = x+18*math.sin(dt*5+x)
        a = 1-ease((y-780)/200)
        if a <= 0: continue
        c.save(); c.translate(xx, y); c.rotate(rot0+spin*dt); c.scale(124/256, 124/256)
        rr(c, -118, -114, 256, 256, 58); col(c, '000000', .35*a); c.fill()
        c.set_source_surface(logo_surf(n), -128, -128); c.paint_with_alpha(a); c.restore()

# ================= scènes =================
def b_hook(cv, c, t, k):
    num(c, "POURQUOI TU", 540, 370, 96, k, gold=False)
    num(c, "RESTES PAUVRE ?", 540, 500, 88, k-.35)
    stamp(c, 540, 690, "SPOILER :", "ce n'est pas qu'une question de salaire", t-1.84, t, rot=-.03, w=720)
def b_decouvert(cv, c, t, k):
    title_bw(c, "À DÉCOUVERT", k, t)
    card(c, 540, 600, 900, 560, k, t)
    num(c, "1 FRANÇAIS SUR 4", 450, 80, 64, t-5.6)
    for i in range(4): figure(c, 150+200*i, 215, 62, i == 3 and t > 7.0, t-5.9-.18*i, t, seed=i)
    ink_text(c, "à découvert presque tous les mois", 450, 360, 28, INKC, 'Limelight', outline=.6, a=ent(t-7.2, .3))
    if t > 9.0:
        s = back((t-9.0)/.35); c.save(); c.translate(600, 465); c.rotate(.06); c.scale(s, s)
        rr(c, -70, -70, 140, 140, 10); col(c, PAPER); c.fill_preserve(); c.set_line_width(6); col(c, INKC); c.stroke()
        rr(c, -70, -70, 140, 36, 10); col(c, INKC); c.fill(); ink_text(c, "18", 0, 18, 70, GOLD[0]); c.restore()
        ink_text(c, "dès le", 400, 465, 34, INKC, 'Alfa Slab One', outline=.6, a=ent(t-9.0, .3))
    end_card(c)
    stamp(c, 540, 930, "ET SI C'ÉTAIT TON CAS ?", None, t-11.6, t, rot=.03, w=620, h=96)
def b_erreur1(cv, c, t, k):
    title_bw(c, "ERREUR N° 1", k, t)
    card(c, 540, 600, 900, 600, k, t, rot=.012)
    xs = (150, 450, 750)
    if t > 15.4:
        ink_text(c, "CE QUE TU FAIS", 450, 50, 26, INKC, 'Limelight', outline=.6, a=ent(t-15.4, .3))
        for i, lab in enumerate(("SALAIRE", "DÉPENSES", "ÉPARGNE")):
            kk = t-15.6-.55*i
            if kk > 0: s = back(kk/.35); c.save(); c.translate(xs[i], 140); c.scale(s, s); box(c, 0, 0, 230, 92, lab); c.restore()
            if i: arrow(c, xs[i-1]+118, xs[i]-122, 140, ent(t-15.4-.55*i, .3), t, seed=i)
        if t > 18.2: num(c, "= 0 €", 750, 228, 54, t-18.2, gold=False)
    if t > 20.0:
        ink_text(c, "LES GENS ORGANISÉS", 450, 315, 26, INKC, 'Limelight', outline=.6, a=ent(t-20.0, .3))
        for i, lab in enumerate(("SALAIRE", "ÉPARGNE", "DÉPENSES")):
            kk = t-20.3-.5*i; gold = i == 1 and t > 21.9
            if kk > 0: s = back(kk/.35); c.save(); c.translate(xs[i], 405); c.scale(s, s); box(c, 0, 0, 230, 92, lab, GOLD[1] if gold else PAPER); c.restore()
            if i: arrow(c, xs[i-1]+118, xs[i]-122, 405, ent(t-20.1-.5*i, .3), t, seed=10+i)
        if t > 21.9: ink_text(c, "EN PREMIER !", 450, 482, 28, GOLD[0], outline=3.5, a=ent(t-21.9, .3))
    end_card(c)
    stamp(c, 540, 955, "VIREMENT AUTOMATIQUE", "le jour de la paie", t-24.0, t, rot=-.04, w=620)
def b_loyer(cv, c, t, k):
    title_bw(c, "ERREUR N° 2 : TON LOYER", k, t)
    card(c, 540, 580, 900, 520, k, t)
    x0, x1, y, h = 70, 830, 210, 116; xt = x0+(x1-x0)/3
    if t > 29.8:
        a = ent(t-29.8, .3); ink_text(c, "TON SALAIRE", 450, 70, 28, INKC, 'Limelight', outline=.6, a=a)
        if t > 33.1: num(c, "2 000 € nets", 450, 120, 46, t-33.1, gold=False)
        u = ent(t-30.9, .6)
        if u > 0: rr(c, x0, y-h/2, (xt-x0)*u, h, 14); col(c, GOLD[1]); c.fill()
        u2 = ent(t-36.4, 1.2)
        if u2 > 0:
            for g_, a_ in ((18, .10), (10, .18), (4, .3)): rr(c, xt-g_, y-h/2-g_, (x1-x0)*.22*u2+2*g_, h+2*g_, 14+g_); col(c, 'FF1E3C', a_*u2); c.fill()
            c.rectangle(xt, y-h/2, (x1-x0)*.22*u2, h); col(c, 'FF1E3C'); c.fill()
        rr(c, x0, y-h/2, x1-x0, h, 14); c.set_line_width(6); col(c, INKC, a); c.stroke()
        for q in (1, 2): ink_line(c, [(x0+(x1-x0)*q/3, y-h/2), (x0+(x1-x0)*q/3, y+h/2)], 4, INKC, a=a*.6, seed=q, t=t)
        if t > 31.0: ink_text(c, "1/3 MAX", (x0+xt)/2, y, 34, INKC, outline=1.0, a=ent(t-31.0, .3))
        if t > 36.6: ink_text(c, "AU-DELÀ", xt+(x1-x0)*.11, y, 26, PAPER, outline=3, a=ent(t-36.6, .3))
    if t > 35.1:
        ink_line(c, [((x0+xt)/2, y+h/2+6), ((x0+xt)/2, y+h/2+60*ent(t-35.1, .3))], 6, INKC, seed=4, t=t)
        num(c, "667 €", (x0+xt)/2+30, 365, 92, t-35.2); ink_text(c, "de loyer maximum", (x0+xt)/2+30, 430, 24, INKC, 'Limelight', outline=.5, a=ent(t-35.4, .3))
    if t > 37.4: ink_text(c, "le mois commence", 640, 360, 28, INKC, 'Limelight', outline=.6, a=ent(t-37.4, .3)); ink_text(c, "DANS LE ROUGE", 640, 410, 36, 'FF1E3C', outline=3.5, a=ent(t-37.6, .3))
    end_card(c)
def b_depenses(cv, c, t, k):
    title_bw(c, "ERREUR N° 3 : LES PETITES DÉPENSES", k, t)
    card(c, 540, 610, 900, 600, k, t, rot=-.012)
    if t > 45.0:
        num(c, "72 € / mois", 450, 90, 78, t-45.0); ink_text(c, "d'abonnements loisirs, en moyenne", 450, 160, 26, INKC, 'Limelight', outline=.5, a=ent(t-45.3, .3))
    if t > 47.6:
        ink_line(c, [(450, 200), (450, 200+50*ent(t-47.6, .3))], 7, INKC, seed=3, t=t)
        ink_text(c, "placés à 7 % pendant 30 ans", 450, 282, 26, INKC, 'Limelight', outline=.5, a=ent(t-47.7, .3))
        if t > 49.9: num(c, euro(count_to(87838, (t-49.9)/1.0)), 450, 362, 96, t-49.9)
    items = (("VIDÉO", True), ("MUSIQUE", True), ("SPORT", False), ("APPLI OUBLIÉE", False))
    if t > 51.4:
        ink_text(c, "À VÉRIFIER :", 450, 432, 26, INKC, 'Alfa Slab One', outline=.5, a=ent(t-51.4, .3))
        for i, (lab, ok) in enumerate(items):
            x = 130+210*i; kk = t-51.8-.45*i
            if kk > 0: ink_text(c, lab, x+10, 535, 21, INKC, 'Alfa Slab One', outline=.4, a=ent(kk, .25)); check(c, x+10, 492, ok, kk-.2, t, seed=20+i)
    ink_text(c, "hypothèse : 7 % par an, jamais garanti", 450, 578, 18, INKC, 'Limelight', outline=.3, a=.85*ent(t-47.7, .5))
    end_card(c)
    rain(c, t)
def b_regle(cv, c, t, k):
    title_bw(c, "LA RÈGLE 50 / 30 / 20", k, t)
    card(c, 540, 600, 920, 580, k, t, rot=.01)
    x0, x1, y, h = 60, 860, 140, 130
    segs = ((.5, "50 %", "ESSENTIEL", 'BDBDBD', 58.1), (.3, "30 %", "ENVIES", '8C8C8C', 60.0), (.2, "20 %", "AVENIR", GOLD[1], 61.15))
    xa = x0
    for (p, lab, sub, colr, t0) in segs:
        w = (x1-x0)*p; u = ent(t-t0, .45)
        if u > 0:
            c.rectangle(xa, y-h/2, w*u, h); col(c, colr); c.fill()
            if u > .6: ink_text(c, lab, xa+w/2, y-16, 40, PAPER if colr == '8C8C8C' else INKC, outline=3 if colr == '8C8C8C' else .8); ink_text(c, sub, xa+w/2, y+30, 20, INKC, 'Alfa Slab One', outline=.4)
        xa += w
    if t > 54.9: rr(c, x0, y-h/2, x1-x0, h, 14); c.set_line_width(6); col(c, INKC); c.stroke()
    xg = x0+(x1-x0)*.9
    if t > 64.5:
        ink_line(c, [(xg, y+h/2+4), (xg, y+h/2+4+40*ent(t-64.5, .3)), (680, y+h/2+44)], 6, INKC, seed=5, t=t)
        ink_text(c, "sur 2 000 € :", 190, 290, 30, INKC, 'Limelight', outline=.6, a=ent(t-64.5, .3)); num(c, "400 € / mois", 560, 290, 62, t-64.55)
    if t > 66.7:
        ink_text(c, "en 30 ans", 450, 380, 28, INKC, 'Limelight', outline=.6, a=ent(t-66.7, .3))
        num(c, "≈ "+euro(count_to(490000, (t-66.75)/1.1)), 450, 455, 96, t-66.75)
    ink_text(c, "hypothèse : 7 % par an, jamais garanti", 460, 550, 18, INKC, 'Limelight', outline=.3, a=.85*ent(t-66.7, .5))
    end_card(c)
def b_habitude(cv, c, t, k):
    title_bw(c, "LE PLUS IMPORTANT", k, t)
    card(c, 540, 520, 880, 420, k, t, rot=-.01)
    ink_text(c, "et si ton salaire ne suffit pas ?", 440, 60, 28, INKC, 'Limelight', outline=.6, a=ent(t-68.6, .3))
    if t > 71.1: ink_text(c, "LE PROBLÈME", 440, 130, 40, INKC, outline=1.0, a=ent(t-71.1, .3)); ink_text(c, "NE VIENT PAS DE TOI", 440, 185, 40, INKC, outline=1.0, a=ent(t-71.4, .3))
    if t > 72.8: ink_text(c, "COMMENCE PAR", 440, 265, 28, INKC, 'Limelight', outline=.6, a=ent(t-72.8, .3)); num(c, "10 € / mois", 440, 340, 80, t-73.4)
    end_card(c)
    stamp(c, 540, 860, "CE QUI COMPTE :", "l'habitude", t-77.3, t, rot=.035, w=560)
def b_fin(cv, c, t, k):
    num(c, "ET TOI,", 540, 380, 120, k, gold=False); num(c, "TU TE PAIES", 540, 520, 96, k-.4); num(c, "EN PREMIER ?", 540, 640, 96, k-.9)
    if t > 81.0: ink_text(c, "Dis-le en commentaire", 540, 780, 36, PAPER, 'Alfa Slab One', a=ent(t-81.0, .3), outline=4); S.put_emoji(cv, '👇', 540, 855+8*math.sin(t*5), 56)
SC = [(0.0, 4.6, b_hook, 'scene'), (4.6, 14.0, b_decouvert, 'mansarde'), (14.0, 27.0, b_erreur1, 'banque'), (27.0, 40.0, b_loyer, 'mansarde'),
      (40.0, 54.6, b_depenses, 'rue'), (54.6, 68.4, b_regle, 'banque'), (68.4, 78.3, b_habitude, 'scene'), (78.3, DUR, b_fin, 'scene')]
BLOCS = []
for (a, b, f, d) in SC:
    if BLOCS and BLOCS[-1][2] == d: BLOCS[-1] = (BLOCS[-1][0], b, d)
    else: BLOCS.append((a, b, d))
IRIS = [a for (a, b, f, d), (a0, b0, f0, d0) in zip(SC[1:], SC[:-1]) if d != d0]
IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = np.repeat(decor(dec, t)[..., None], 3, 2).astype(np.float32)
    cv = Image.fromarray(img.astype(np.uint8)).convert('RGBA')
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
    ev = V.events() + [(ta-IR, 'whoosh') for ta in IRIS] + [(COL_T+.05, 'glint')]
    ev += [(.35, 'impact'), (1.9, 'pop'), (5.6, 'pop'), (7.0, 'thud'), (9.0, 'pop'), (11.6, 'pop'), (18.2, 'thud'), (21.9, 'glint'), (24.0, 'pop'),
           (30.9, 'tick'), (35.2, 'glint'), (36.4, 'thud'), (45.0, 'pop'), (41.80, 'tick'), (42.28, 'tick'), (42.76, 'tick'), (43.24, 'tick'), (43.72, 'tick'), (44.20, 'tick'), (49.9, 'tick'), (51.0, 'glint'), (58.1, 'pop'), (60.0, 'pop'), (61.15, 'glint'),
           (64.55, 'pop'), (66.75, 'tick'), (67.9, 'glint'), (71.1, 'pop'), (73.4, 'glint'), (77.3, 'pop'), (78.3, 'impact')]
    ev += [(51.8+.45*i+.2, 'tick') for i in range(4)]
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
