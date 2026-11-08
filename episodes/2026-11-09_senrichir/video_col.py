"""« Comment commencer à t'enrichir ? », cartoon 1930 en couleurs (base : Pourquoi tu restes pauvre ?), dessin animé 1930 : décors Gemini noir et blanc (théâtre, mansarde, banque, rue commerçante),
Mister Coin en noir et blanc (il retrouve ses couleurs à la fin), seul l'or reste en or, effets de pellicule, iris aux changements de décor.
usage : python3 video_bw.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw
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
DEC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('scene', 'theatre_couleur')}
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
COL_T, COL_D = -10, .3

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

# ================= décors Technicolor : lecture séquentielle, ralentie pour couvrir tout le passage, sans boucle ni retour arrière =================
DECC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('theatre_couleur', 'chambre', 'avenue', 'jardin')}
class _Reader:
    def __init__(self): self.name = None; self.cap = None; self.i = -1; self.f = None
    def get(self, name, i):
        if name != self.name or i < self.i:
            if self.cap: self.cap.release()
            self.cap = cv2.VideoCapture(DECC[name]); self.name = name; self.i = -1; self.f = None
        while self.i < i:
            ok, f = self.cap.read()
            if not ok: break
            self.f = f; self.i += 1
        return self.f
_RD = _Reader()
_NF = {}
def nframes(name):
    if name not in _NF: c = cv2.VideoCapture(DECC[name]); _NF[name] = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); c.release()
    return _NF[name]
def decor_c(name, t):
    a, b = next((a, b) for (a, b, d) in BLOCS if d == name and a <= t < b+.5)
    n = nframes(name); sp = min(1.0, (n-1)/24/max(.1, b-a)); i = min(n-1, int(max(0, t-a)*sp*24))
    f = _RD.get(name, i)
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    return np.clip((g-128)*1.06+130, 0, 255)
def coin_col(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, 540, Y)
    fx = V.MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), V.FEET-3), (95, 15), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    return cv_rgb*(1-al[..., None])+rgb_.astype(np.float32)*al[..., None]
RED = 'E63946'; GREEN = '2A9D8F'; SKY = '4361EE'
# ================= objets dessinés =================
def medal(c, x, y, r, label, k, t, fill=GOLD[1]):
    if k <= 0: return
    s = back(k/.35); c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(6, 10, r, 0, 2*math.pi); col(c, '000000', .4); c.fill()
    c.arc(0, 0, r, 0, 2*math.pi); col(c, fill); c.fill_preserve(); c.set_line_width(6); col(c, INKC); c.stroke()
    c.arc(0, 0, r*.78, 0, 2*math.pi); c.set_line_width(3); col(c, GOLD[2]); c.stroke()
    ink_text(c, label, 0, 4, int(r*1.05), INKC, 'Alfa Slab One', outline=.8); c.restore()
def gauge(c, x0, y, w, h, frac, colr, k, dashed=False):
    """barre de jauge dessinée à l'encre ; frac = remplissage visé (0-1), k = avancement"""
    rr(c, x0, y-h/2, w, h, h/2); col(c, PAPER); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke()
    u = ent(k, .8)*frac
    if u > .005:
        rr(c, x0+5, y-h/2+5, max(h-10, (w-10)*u), h-10, (h-10)/2); col(c, colr, .55 if dashed else 1); c.fill()
        if dashed:
            c.save(); rr(c, x0+5, y-h/2+5, max(h-10, (w-10)*u), h-10, (h-10)/2); c.clip()
            for k_ in range(-20, 60): c.move_to(x0+k_*22, y+h/2); c.line_to(x0+k_*22+h, y-h/2)
            c.set_line_width(6); col(c, colr); c.stroke(); c.restore()
def zzz(c, t, x, y):
    for i in range(3):
        u = ((t*.45+i/3) % 1); a = math.sin(u*math.pi)
        ink_text(c, "Z", x+40*u+12*math.sin(u*6), y-120*u, int(30+24*u), SKY, 'Alfa Slab One', a=a*.9, outline=4)
def emoji_tile(cv, x, y, e_, k, size=92):
    if k <= 0: return
    s = back(k/.35); S.put_emoji(cv, e_, int(x), int(y), max(8, int(size*s)))
# ================= scènes =================
def b_hook(cv, c, t, k):
    sw = 1+.03*math.sin(t*4)
    c.save(); c.translate(540, 420); c.scale(sw, sw)
    ink_text(c, "COMMENT COMMENCER", 0, -56, 62, PAPER, 'Alfa Slab One', outline=6)
    ink_text(c, "À T'ENRICHIR ?", 0, 46, 90, GOLD[0], 'Alfa Slab One', outline=7); c.restore()
    for i in range(3):
        kk = t-1.9-.2*i; wob = .18*math.sin((t-3.0)*12)*math.exp(-max(0, t-3.0)*2.5) if (i == 0 and t > 3.0) else 0
        c.save(); c.translate(300+240*i, 700); c.rotate(wob); medal(c, 0, 0, 74, str(i+1), kk, t); c.restore()
    if t > 2.9: ink_text(c, "la 1re va te surprendre !", 540, 850, 34, PAPER, 'Alfa Slab One', outline=4.5, a=ent(t-2.9, .3))
def step_title(c, n, sub, t, t0, t1):
    medal(c, 120, 258, 56, str(n), t-t0, t)
    if t > t1: ink_text(c, sub, 200, 262, min(46, int(1240/max(1, len(sub)))), PAPER, 'Alfa Slab One', align='l', outline=5.5, a=ent(t-t1, .3))
def b_step1(cv, c, t, k):
    step_title(c, 1, "NE LAISSE PAS DORMIR TON ARGENT" if t < 24.0 else "GARDE UNE RÉSERVE", t, 4.6, 6.1)
    if 6.1 < t < 8.6: zzz(c, t, 520, 900)
    if 8.4 <= t < 24.1:
        a = 1-ent(t-23.8, .3)
        c.save(); c.push_group(); card(c, 540, 620, 920, 560, t-8.4, t)
        rows = ((90, "LIVRET A", "aujourd'hui", 1.7, GOLD[1], 9.9, False), (230, "INFLATION", "sur un an", 3.4, RED, 13.2, False), (370, "LIVRET A", "février (estimation)", 2.5, GOLD[1], 20.9, True))
        for (y, lab, sub, v, colr, t0, dash) in rows:
            if t < t0-1.2: continue
            ink_text(c, lab, 140, y-12, 30, INKC, 'Alfa Slab One', outline=.6, a=ent(t-t0+1.2, .3)); ink_text(c, sub, 140, y+22, 19, INKC, 'Limelight', outline=.3, a=ent(t-t0+1.2, .3))
            gauge(c, 270, y, 470, 64, v/4.0, colr, t-t0, dash)
            if t > t0+.5: num(c, ("≈ " if dash else "")+f"{v:.1f}".replace('.', ',')+" %", 820, y+2, 40, t-t0-.5, gold=colr != RED)
        if t > 22.5:
            xi = 270+5+(470-10)*3.4/4.0; ink_line(c, [(xi, 30), (xi, 430)], 5, RED, a=ent(t-22.5, .3), seed=7, t=t)
            ink_text(c, "inflation", xi, 455, 22, RED, 'Alfa Slab One', outline=3, a=ent(t-22.5, .3))
        end_card(c); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
        stamp(c, 540, 950, "TOUJOURS SOUS L'INFLATION", None, t-22.6, t, rot=-.035, w=700, h=100) if t < 24.0 else None
    if t >= 24.0:
        card(c, 540, 600, 860, 420, t-24.0, t, rot=.012)
        emoji_tile(cv, 0, 0, '🛟', 0)
        ink_text(c, "ÉPARGNE DE SÉCURITÉ", 430, 80, 40, INKC, 'Alfa Slab One', outline=.8)
        num(c, "3 à 6 mois", 430, 190, 92, t-24.6)
        ink_text(c, "de dépenses", 430, 270, 34, INKC, 'Limelight', outline=.5, a=ent(t-25.2, .3))
        if t > 26.6: ink_text(c, "PAS PLUS !", 430, 350, 46, RED, 'Alfa Slab One', outline=4, a=ent(t-26.6, .25))
        end_card(c)
def b_step2(cv, c, t, k):
    step_title(c, 2, "DEVIENS ACTIONNAIRE", t, 27.6, 28.5)
    if t < 29.9: return
    card(c, 540, 630, 920, 600, t-29.9, t, rot=-.01)
    items = (("TÉLÉPHONE", 30.0, 150), ("BASKETS", 30.95, 450), ("CAFÉ", 31.75, 750))
    for lab, t0, x in items:
        if t > t0: ink_text(c, lab, x, 200, 26, INKC, 'Alfa Slab One', outline=.5, a=ent(t-t0, .3))
    if t > 33.0:
        for i, (lab, t0, x) in enumerate(items):
            u = ent(t-33.0-.12*i, .35); ink_line(c, [(x, 215), (x+(450-x)*u*.85, 215+105*u)], 6, INKC, seed=30+i, t=t)
        sb = back((t-33.6)/.35) if t > 33.6 else 0
        if sb > 0:
            c.save(); c.translate(450, 360); c.scale(sb, sb); box(c, 0, 0, 520, 96, "ENTREPRISE COTÉE", GOLD[1], size=34); c.restore()
    if t > 36.2:
        a2 = ent(t-36.2, .3); ink_text(c, "tu es son", 450, 470, 28, INKC, 'Limelight', outline=.5, a=a2)
        ink_text(c, "CLIENT", 230, 535, 46, '6B6B6B', 'Alfa Slab One', outline=.8, a=a2)
        if t > 37.7:
            u = ent(t-37.7, .25); ink_line(c, [(140, 540), (140+180*u, 528)], 7, RED, seed=41, t=t)
            ink_line(c, [(365, 535), (365+60*u, 535)], 7, INKC, seed=42, t=t)
            if u > .9: c.move_to(437, 535); c.line_to(415, 520); c.line_to(415, 550); c.close_path(); col(c, INKC); c.fill()
            num(c, "ACTIONNAIRE", 650, 535, 48, t-37.85)
    end_card(c)
def emojis_step2(cv, t):
    if not (29.9 <= t < 39.6): return
    cx, cy = 540, 630; x0, y0 = cx-460, cy-300                       # repère de la carte (approximatif, sans rotation)
    for (e_, t0, x) in (('📱', 30.0, 150), ('👟', 30.95, 450), ('☕', 31.75, 750)):
        emoji_tile(cv, x0+x, y0+78, e_, t-t0, 96)
PRICES = [100, 92, 80, 71, 77, 88, 84, 95, 108, 102, 116, 124]
def b_step3(cv, c, t, k):
    step_title(c, 3, "INVESTIS TOUS LES MOIS", t, 39.7, 40.5)
    if 42.8 <= t < 51.2:
        a = 1-ent(t-50.9, .3); c.save(); c.push_group()
        card(c, 540, 640, 940, 600, t-42.8, t)
        ink_text(c, "DCA = la même somme, chaque mois", 470, 45, 30, INKC, 'Alfa Slab One', outline=.6)
        ink_text(c, "(Dollar Cost Averaging)", 470, 82, 20, INKC, 'Limelight', outline=.3)
        X = lambda i: 90+i*(770/11); Y = lambda p: 300-(p-60)*2.6
        n = clamp((t-43.0)/4.6)*11
        pts = [(X(i), Y(p)) for i, p in enumerate(PRICES) if i <= n]
        if n > 0 and len(pts) < 12: i = int(n); f = n-i; pts.append((X(i)+(X(i+1)-X(i))*f, Y(PRICES[i]+(PRICES[i+1]-PRICES[i])*f)))
        if len(pts) > 1: ink_line(c, pts, 6, SKY, seed=50, t=t)
        ink_text(c, "cours de la bourse", 120, 118, 23, SKY, 'Alfa Slab One', outline=2.5, align='l')
        for i, p in enumerate(PRICES):
            ti = 43.0+i*4.6/11
            if t < ti: continue
            hb = 100/p*140; u = ent(t-ti, .3)
            rr(c, X(i)-22, 470-hb*u, 44, hb*u, 6); col(c, GREEN); c.fill_preserve(); c.set_line_width(3); col(c, INKC); c.stroke()
            c.arc(X(i), Y(p), 9, 0, 2*math.pi); col(c, GOLD[1]); c.fill_preserve(); c.set_line_width(3); col(c, INKC); c.stroke()
        if t > 43.6: ink_text(c, "parts achetées avec 100 €", 470, 505, 22, GREEN, 'Alfa Slab One', outline=2.5, a=ent(t-43.6, .3))
        if t > 48.3:
            hm = len(PRICES)/sum(1/p for p in PRICES); u = ent(t-48.3, .5); yy = Y(hm)
            c.save(); c.set_dash([18, 10]); c.move_to(X(0), yy); c.line_to(X(0)+(X(11)-X(0))*u, yy); c.set_line_width(5); col(c, GOLD[2]); c.stroke(); c.restore()
            if t > 48.8: ink_text(c, "ton prix moyen, lissé", X(11)-10, yy-26, 22, GOLD[2], 'Alfa Slab One', outline=3, align='r', a=ent(t-48.8, .3))
        end_card(c); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    if t >= 51.1:
        card(c, 540, 620, 900, 580, t-51.1, t, rot=.01)
        ink_text(c, "100 €/mois · ETF monde · PEA", 450, 50, 32, INKC, 'Alfa Slab One', outline=.6)
        ink_text(c, "7 % par an pendant 30 ans", 450, 92, 22, INKC, 'Limelight', outline=.3, a=ent(t-54.6, .3))
        base = 485
        for (x, lab, val, t0, d, colr) in ((260, "versé", 36000, 56.9, 1.0, 'B8B8B8'), (640, "au bout de 30 ans", 121997, 59.0, 1.1, GOLD[1])):
            if t < t0-.3: continue
            u = ent(t-t0+.3, d); h_ = val/121997*245*u
            rr(c, x-90, base-h_, 180, h_, 10); col(c, colr); c.fill_preserve(); c.set_line_width(5); col(c, INKC); c.stroke()
            ink_text(c, lab, x, base+30, 24, INKC, 'Alfa Slab One', outline=.5)
            num(c, ("≈ " if val > 50000 else "")+V.euro(count_to(val, (t-t0+.3)/d)), x, base-h_-40, 50 if val < 50000 else 60, t-t0+.3, gold=val > 50000)
        ink_text(c, "hypothèse : 7 % par an, jamais garanti", 450, 560, 18, INKC, 'Limelight', outline=.3, a=.85*ent(t-54.6, .5))
        end_card(c)
def b_fin(cv, c, t, k):
    if t < 65.7:
        a = 1-ent(t-65.4, .3)
        c.save(); c.push_group()
        ink_text(c, "Le meilleur moment pour commencer :", 540, 330, 36, PAPER, 'Alfa Slab One', outline=4.5, a=ent(t-60.6, .3))
        if t > 62.5: num(c, "IL Y A 10 ANS", 540, 430, 76, t-62.5, gold=False)
        if t > 63.4: ink_text(c, "Le deuxième meilleur :", 540, 560, 36, PAPER, 'Alfa Slab One', outline=4.5, a=ent(t-63.4, .3))
        if t > 64.5: num(c, "AUJOURD'HUI !", 540, 670, 100, t-64.5)
        c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    else:
        num(c, "ET TOI,", 540, 330, 96, t-65.75, gold=False)
        ink_text(c, "de quelle marque", 540, 450, 54, PAPER, 'Alfa Slab One', outline=5, a=ent(t-66.0, .3))
        ink_text(c, "aimerais-tu être", 540, 525, 54, PAPER, 'Alfa Slab One', outline=5, a=ent(t-66.4, .3))
        num(c, "ACTIONNAIRE ?", 540, 625, 92, t-67.1)
        if t > 68.2: ink_text(c, "Dis-le en commentaire", 540, 760, 38, PAPER, 'Alfa Slab One', a=ent(t-68.2, .3), outline=4.5); S.put_emoji(cv, '👇', 540, int(835+8*math.sin(t*5)), 56)
SC = [(0.0, 4.5, b_hook, 'theatre_couleur'), (4.5, 27.5, b_step1, 'chambre'), (27.5, 39.5, b_step2, 'avenue'), (39.5, 60.44, b_step3, 'jardin'), (60.44, DUR, b_fin, 'theatre_couleur')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [s_[0] for s_ in SC[1:]]; IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
    if f is b_step2: emojis_step2(cv, t)
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28                      # pellicule discrète : l'image reste éclatante
    for ta in IRIS:
        if ta-IR <= t < ta: arr = iris(arr, inout((t-(ta-IR))/IR))
        elif ta <= t < ta+IR: arr = iris(arr, 1-inout((t-ta)/IR))
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    return out
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else 'FF8A8A', a=al); return
def events():
    ev = V.events() + [(ta-IR, 'whoosh') for ta in IRIS]
    ev += [(1.9, 'pop'), (2.1, 'pop'), (2.3, 'pop'), (3.0, 'bonk'), (4.66, 'pop'), (9.9, 'fill1'), (13.2, 'thud'), (20.9, 'tick'), (22.6, 'thud'),
           (24.6, 'glint'), (26.6, 'thud'), (27.7, 'pop'), (30.0, 'pop'), (30.95, 'pop'), (31.75, 'pop'), (33.6, 'impact'), (37.85, 'tadaa'),
           (39.8, 'pop'), (48.3, 'glint'), (56.6, 'tick'), (58.7, 'tick'), (60.0, 'coins'), (64.5, 'glint'), (67.1, 'impact')]
    ev += [(43.0+i*4.6/11, 'coin') for i in range(12)]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/c_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(k/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
