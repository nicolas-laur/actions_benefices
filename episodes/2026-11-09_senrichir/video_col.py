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
RED = 'B3161B'; CREAM = 'F6E7C1'; BROWN = '3B2412'; CHALK = 'F3F1E8'; SKY = '4361EE'
# ================= accessoires Gemini (détourés, dossier props/) =================
_PS = {}
def psurf(name):
    if name not in _PS:
        im = Image.open(f'{D}/props/{name}.png').convert('RGBA'); a = np.asarray(im).astype(np.float32)
        pre = a.copy(); pre[..., :3] *= a[..., 3:4]/255
        buf = np.ascontiguousarray(pre[..., [2, 1, 0, 3]].astype(np.uint8))
        _PS[name] = (cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, im.width, im.height), im.width, im.height)
    return _PS[name]
def prop(c, name, x, y, h=None, w=None, k=1.0, rot=0.0, a=1.0, shadow=True, ax=.5, ay=.5):
    """pose un accessoire (centre x, y) ; taille par hauteur h ou largeur w ; k = pop caoutchouc"""
    if k <= 0 or a <= 0: return 0, 0
    sf, iw, ih = psurf(name); s = (h/ih) if h else (w/iw); s *= back(k/.35)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    if shadow:
        c.save(); c.translate(10/s, 16/s); c.set_source_surface(sf, -iw*ax, -ih*ay); c.paint_with_alpha(.0); c.restore()
    c.set_source_surface(sf, -iw*ax, -ih*ay); c.paint_with_alpha(a); c.restore()
    return iw*s, ih*s
def paint(c, s_, x, y, size, fill=CREAM, a=1.0, align='c', rot=0.0, fam='Alfa Slab One'):
    """lettres peintes : crème/or, contour brun chaud, ombre portée"""
    if a <= 0: return
    c.save(); c.select_font_face(fam, 0, 0); c.set_font_size(size); e = c.text_extents(s_)
    xx = -e.x_advance/2 if align == 'c' else (-e.x_advance if align == 'r' else 0)
    c.translate(x, y); c.rotate(rot); c.translate(xx, size*.35); ol = max(3, size*.09)
    c.move_to(ol*.6, ol*.9); c.text_path(s_); c.set_source_rgba(0, 0, 0, .5*a); c.fill()
    c.move_to(0, 0); c.text_path(s_); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(ol*2); col(c, BROWN, a); c.stroke_preserve(); col(c, fill, a); c.fill()
    c.restore()
def fit(c, s_, size, maxw, fam='Alfa Slab One'):
    c.save(); c.select_font_face(fam, 0, 0); c.set_font_size(size); w = c.text_extents(s_).x_advance; c.restore()
    return size if w <= maxw else int(size*maxw/w)
def ribbon(c, s_, x, y, w, k, t, fill=CREAM, rot=0.0, size=40):
    """ruban rouge Gemini avec texte peint, qui se déroule (pop)"""
    if k <= 0: return
    sf, iw, ih = psurf('ruban'); s = w/iw; sx = s*back(k/.4); sy = s*min(1, back(k/.3))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sx, sy); c.set_source_surface(sf, -iw/2, -ih/2); c.paint(); c.restore()
    paint(c, s_, x, y-4, fit(c, s_, size, w*.62), fill, a=ent(k-.15, .2), rot=rot)
def sign_title(c, s_, t, t0, t_out=None):
    """enseigne Gemini suspendue à ses chaînes, qui descend du cintre et se balance"""
    k = t-t0
    if k <= 0: return
    sf, iw, ih = psurf('enseigne'); s = 560/iw
    drop = (1-ent(k, .5))*-420+(ease((t-t_out)/.45)*-520 if t_out and t > t_out else 0)
    sw = .06*math.exp(-k*1.6)*math.sin(k*6)+.012*math.sin(t*1.3)
    c.save(); c.translate(540, -165+drop); c.rotate(sw); c.scale(s, s); c.set_source_surface(sf, -iw/2, 0); c.paint(); c.restore()
    py = -165+drop+975*s
    c.save(); c.translate(540, -165+drop); c.rotate(sw); c.translate(-540, 165-drop)
    paint(c, s_, 540, py, fit(c, s_, 56, 330), BROWN if False else 'FFE27A'); c.restore()
def thermo(c, x, top, h, v, colr, k, t, est=None):
    """thermomètre Gemini ; liquide jusqu'à v (%) ; échelle 0-4 % entre les graduations"""
    sf, iw, ih = psurf('thermometre'); s = h/ih; x0 = x-iw*s/2
    Y = lambda yy: top+yy*s; X = lambda xx: x0+xx*s
    lvl = lambda p: 1112-(p/4)*(1112-327)
    c.save()
    u = ent(k, 1.0)*v
    if k > 0:
        c.arc(X(318), Y(1700), 118*s, 0, 2*math.pi); col(c, colr, .92); c.fill()
        yt = lvl(u); rr(c, X(268), Y(yt), (362-268)*s, Y(1640)-Y(yt), 40*s); col(c, colr, .92); c.fill()
        c.rectangle(X(282), Y(yt)+6, 14*s, Y(1600)-Y(yt)-6); col(c, 'FFFFFF', .28); c.fill()
    c.set_source_surface(sf, 0, 0); c.restore()
    c.save(); c.translate(x0, top); c.scale(s, s); c.set_source_surface(sf, 0, 0); c.paint_with_alpha(.55 if k > 0 else 1); c.restore()
    if est is not None and t > est[1]:                                        # repère hachuré de l'estimation de février
        ye = Y(lvl(est[0])); u2 = ent(t-est[1], .4)
        c.save(); c.set_dash([10, 7]); c.move_to(X(250), ye); c.line_to(X(250)+(X(380)-X(250))*u2, ye); c.set_line_width(5); col(c, 'FFE27A'); c.stroke(); c.restore()
    return Y(lvl(v)), lambda p: Y(lvl(p))
def coin_fall(c, x, y0, y1, k, size=58, spin=0.0):
    if k <= 0: return
    u = min(1, k/.45); y = y0+(y1-y0)*u*u
    prop(c, 'piece', x, y, h=size, rot=spin*k, shadow=False)
def chalk_line(c, pts, wdt=5, colr=CHALK, a=.9, seed=0):
    if len(pts) < 2: return
    rng = np.random.default_rng(seed)
    for pas in range(2):
        c.move_to(*pts[0])
        for (x, y) in pts[1:]: c.line_to(x+rng.normal(0, .8), y+rng.normal(0, .8))
        c.set_line_width(wdt*(1 if pas == 0 else .5)); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, colr, a*(.75 if pas == 0 else .5)); c.stroke()
def chalk_text(c, s_, x, y, size, colr=CHALK, a=.92, fam='Limelight'):
    c.save(); c.select_font_face(fam, 0, 0); c.set_font_size(size); e = c.text_extents(s_)
    c.move_to(x-e.x_advance/2, y+size*.35); c.text_path(s_); col(c, colr, a); c.fill(); c.restore()
# ================= scènes =================
def b_hook(cv, c, t, k):
    sw = 1+.025*math.sin(t*4)
    c.save(); c.translate(540, 400); c.scale(sw, sw)
    paint(c, "COMMENT COMMENCER", 0, -58, 64); paint(c, "À T'ENRICHIR ?", 0, 50, 96, 'FFE27A'); c.restore()
    for i in range(3):
        kk = t-1.9-.2*i; wob = .22*math.sin((t-3.0)*12)*math.exp(-max(0, t-3.0)*2.5) if (i == 0 and t > 3.0) else 0
        if kk <= 0: continue
        c.save(); c.translate(300+240*i, 690); c.rotate(wob+.15*math.sin(t*2+i))
        prop(c, 'piece', 0, 0, h=170, k=kk); s_ = back(kk/.35)
        c.scale(s_, s_); paint(c, str(i+1), 0, 4, 110, CREAM); c.restore()
    if t > 2.9: paint(c, "la 1re va te surprendre !", 540, 850, 36, a=ent(t-2.9, .3))
def b_step1(cv, c, t, k):
    sign_title(c, "ÉTAPE 1", t, 4.6)
    ribbon(c, "NE LAISSE PAS DORMIR TON ARGENT" if t < 24.0 else "GARDE UNE RÉSERVE", 540, 370, 800, t-(6.1 if t < 24.0 else 24.0), t)
    if 6.1 < t < 8.6: zzz(c, t, 520, 900)
    if 8.4 <= t < 24.6:
        out = ease((t-24.0)/.5) if t > 24.0 else 0
        for (x, lab, v, colr, t0, t1, est) in ((330, "LIVRET A", 1.7, 'F2B82E', 8.4, 9.9, (2.5, 20.9)), (750, "INFLATION", 3.4, RED, 10.8, 13.2, None)):
            kk = t-t0
            if kk <= 0: continue
            xx = x+(-500 if x < 540 else 500)*out
            yl, Lv = thermo(c, xx, 535+(1-ent(kk, .4))*600, 450, v, colr, t-t1, t, est)
            paint(c, lab, xx, 515+(1-ent(kk, .4))*600, 36, 'FFE27A' if x < 540 else 'FF8A8A')
            if t > t1+.6: paint(c, f"{v:.1f} %".replace('.', ','), (165 if x < 540 else 915)+(xx-x), yl, 52, 'FFE27A' if x < 540 else 'FF8A8A', a=ent(t-t1-.6, .3))
            if est and t > est[1]:
                paint(c, "≈ 2,5 %", 165+(xx-x), Lv(2.5)-34, 38, CREAM, a=ent(t-est[1], .3)); paint(c, "en février ?", 165+(xx-x), Lv(2.5)-72, 22, CREAM, a=ent(t-est[1]-.2, .3))
        if t > 22.5 and out < 1:
            _, Lv = thermo.__defaults__ and (None, None) or (None, None)
            y_inf = 535+(1112-(3.4/4)*(1112-327))*(450/2055)
            u = ent(t-22.5, .4); c.save(); c.set_dash([16, 10]); c.move_to(750, y_inf); c.line_to(750-(750-330)*u, y_inf); c.set_line_width(6); col(c, RED, 1-out); c.stroke(); c.restore()
        if t > 22.6 and t < 24.2: ribbon(c, "TOUJOURS SOUS L'INFLATION", 540, 905, 700, t-22.6, t, rot=-.02)
    if t >= 24.0:
        kk = t-24.1
        prop(c, 'coffre_securite', 540, 650, h=360, k=kk, rot=.02*math.sin(t*1.5))
        if t > 24.6: ribbon(c, "3 À 6 MOIS DE DÉPENSES", 540, 900, 700, t-24.6, t, rot=.015)
        if t > 26.6:
            sc = back((t-26.6)/.3); c.save(); c.translate(800, 520); c.rotate(.18); c.scale(sc, sc); paint(c, "PAS PLUS !", 0, 0, 58, 'FF8A8A'); c.restore()
def zzz(c, t, x, y):
    for i in range(3):
        u = ((t*.45+i/3) % 1); a = math.sin(u*math.pi)
        paint(c, "Z", x+40*u+12*math.sin(u*6), y-120*u, int(30+24*u), 'B9D7FF', a=a*.9)
def b_step2(cv, c, t, k):
    sign_title(c, "ÉTAPE 2", t, 27.6)
    ribbon(c, "DEVIENS ACTIONNAIRE", 540, 370, 720, t-28.5, t)
    cert = t > 37.7
    for (name, lab, t0, x, h, w) in (('telephone', "TON TÉLÉPHONE", 30.0, 210, 250, None), ('basket', "TES BASKETS", 30.95, 540, None, 290), ('cafe', "TON CAFÉ", 31.75, 870, None, 250)):
        kk = t-t0
        if kk <= 0: continue
        a = 1-ent(t-37.7, .3) if cert else 1
        bob = 6*math.sin(t*2.2+x)
        prop(c, name, x, 640+bob, h=h, w=w, k=kk, a=a, rot=.05*math.sin(t*1.7+x))
        paint(c, lab, x, 800, 32, a=a*ent(kk-.1, .3))
        if t > 33.1:
            u = ent(t-33.1-.1*(x/330), .4); ink_line(c, [(x, 828), (x+(540-x)*u*.6, 828+40*u)], 6, BROWN, a=a, seed=x, t=t)
    if 33.4 < t and not cert: ribbon(c, "= DES ENTREPRISES COTÉES", 540, 905, 700, t-33.4, t)
    if 36.2 < t < 37.9: paint(c, "et toi, tu n'es que CLIENT…", 540, 1000-60, 34, 'FF8A8A', a=ent(t-36.2, .3)*(1-ent(t-37.6, .25)))
    if cert:
        kk = t-37.75; sc = back(kk/.4)
        c.save(); c.translate(540, 680); c.rotate(-.03+.01*math.sin(t*1.4)); c.scale(sc, sc)
        prop(c, 'certificat', 0, 0, h=560)
        paint(c, "ACTIONNAIRE :", 0, -120, 44, CREAM); paint(c, "TOI !", 0, -10, 120, 'FFE27A')
        c.restore()
PRICES = [100, 92, 80, 71, 77, 88, 84, 95, 108, 102, 116, 124]
def b_step3(cv, c, t, k):
    sign_title(c, "ÉTAPE 3", t, 39.7, t_out=42.6)
    if t < 43.2: ribbon(c, "INVESTIS TOUS LES MOIS", 540, 370, 760, t-40.5, t, rot=0)
    if 42.6 <= t < 51.6:
        kk = t-42.6; out = ease((t-51.0)/.55) if t > 51.0 else 0
        sf, iw, ih = psurf('tableau'); s = .92; slide = (1-ent(kk, .45))*900+out*-1100
        bx = 540+slide; by = -40
        c.save(); c.translate(bx-iw*s/2, by); c.scale(s, s); c.set_source_surface(sf, 0, 0); c.paint(); c.restore()
        L, T = bx-iw*s/2+205*s, by+318*s; R, B = bx-iw*s/2+912*s, by+1020*s               # ardoise
        cx = (L+R)/2
        if t > 43.0:
            chalk_text(c, "DCA : la même somme, chaque mois", cx, T+34, 30, 'FFF6A8')
            chalk_text(c, "(Dollar Cost Averaging)", cx, T+72, 21)
        X = lambda i: L+40+i*((R-L-80)/11); Y = lambda p: T+300-(p-65)*2.9
        n = clamp((t-43.0)/4.6)*11
        pts = [(X(i), Y(p)) for i, p in enumerate(PRICES) if i <= n]
        if 0 < n < 11: i = int(n); f = n-i; pts.append((X(i)+(X(i+1)-X(i))*f, Y(PRICES[i]+(PRICES[i+1]-PRICES[i])*f)))
        chalk_line(c, pts, 5, CHALK, seed=3)
        if t > 43.2: chalk_text(c, "cours de la bourse", L+130, T+118, 25, 'BFE3FF')
        for i, p in enumerate(PRICES):
            ti = 43.0+i*4.6/11
            if t < ti: continue
            hb = 100/p*150*ent(t-ti, .3); x = X(i)
            c.save(); c.rectangle(x-15, B-25-hb, 30, hb); c.clip()
            for j in range(-12, 30): c.move_to(x-15, B-25-hb+j*8); c.line_to(x+15, B-25-hb+j*8-14)
            c.set_line_width(3); col(c, 'FFE27A', .85); c.stroke(); c.restore()
            c.rectangle(x-15, B-25-hb, 30, hb); c.set_line_width(2.5); col(c, 'FFE27A', .9); c.stroke()
        if t > 43.6: chalk_text(c, "parts achetées avec 100 €", cx, B-6, 25, 'FFE27A')
        if t > 48.3:
            hm = len(PRICES)/sum(1/p for p in PRICES); u = ent(t-48.3, .5); yy = Y(hm)
            c.save(); c.set_dash([14, 9]); c.move_to(X(0), yy); c.line_to(X(0)+(X(11)-X(0))*u, yy); c.set_line_width(4); col(c, 'FF9EC4', .95); c.stroke(); c.restore()
            if t > 48.8: chalk_text(c, "ton prix moyen, lissé", cx+80, yy+28, 23, 'FF9EC4')
    if t >= 51.0:
        ribbon(c, "100 €/MOIS · ETF MONDE · PEA", 540, 300, 900, t-51.1, t)
        jx, jy, jh = 300, 700, 400
        prop(c, 'bocal', jx, jy, h=jh, k=t-51.2)
        n_in = int(clamp((t-51.6)/5.2)*14)
        for i in range(n_in):                                              # pièces empilées au fond du bocal
            row, colm = divmod(i, 4); prop(c, 'piece', jx-75+50*colm+(row % 2)*20, jy+jh*.36-row*36, h=56, shadow=False, rot=.3*math.sin(i))
        if 51.6 < t < 56.8:
            ph = ((t-51.6)/5.2*14) % 1; coin_fall(c, jx+10, jy-330, jy+jh*.36-(n_in//4)*36, ph*.45/.45, 60, 4)
        prop(c, 'bocal', jx, jy, h=jh, k=t-51.2, a=.35, shadow=False)          # reflet du verre par-dessus les pièces
        if t > 56.6:
            paint(c, "versé", jx, 935, 30, a=ent(t-56.6, .3)); paint(c, V.euro(count_to(36000, (t-56.6)/1.0)), jx, 455, 48, CREAM, a=ent(t-56.6, .3))
        if t > 58.3:
            prop(c, 'tresor', 770, 715, h=420*(.6+.4*ent(t-58.3, 1.0)), k=t-58.3)
            paint(c, "≈ "+V.euro(count_to(121997, (t-58.3)/1.1)), 770, 455, 62, 'FFE27A')
            paint(c, "au bout de 30 ans", 770, 935, 30, a=ent(t-58.6, .3))
        if t > 54.6: paint(c, "hypothèse : 7 % par an pendant 30 ans, jamais garanti", 540, 968, 20, a=.9*ent(t-54.6, .5), fam='Limelight')
def b_fin(cv, c, t, k):
    if t < 65.7:
        a = 1-ent(t-65.4, .3)
        c.save(); c.push_group()
        paint(c, "Le meilleur moment pour commencer :", 540, 290, 36, a=ent(t-60.6, .3))
        ribbon(c, "IL Y A 10 ANS", 540, 425, 620, t-62.5, t, rot=-.02, size=56)
        if t > 63.4: paint(c, "Le deuxième meilleur :", 540, 590, 36, a=ent(t-63.4, .3))
        if t > 64.5:
            sc = back((t-64.5)/.35); c.save(); c.translate(540, 710); c.scale(sc, sc); paint(c, "AUJOURD'HUI !", 0, 0, 100, 'FFE27A'); c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    else:
        paint(c, "ET TOI,", 540, 330, 92, a=ent(t-65.75, .3))
        paint(c, "de quelle marque", 540, 450, 52, a=ent(t-66.0, .3)); paint(c, "aimerais-tu être", 540, 525, 52, a=ent(t-66.4, .3))
        ribbon(c, "ACTIONNAIRE ?", 540, 640, 760, t-67.1, t, size=72)
        if t > 68.2: paint(c, "Dis-le en commentaire", 540, 790, 38, a=ent(t-68.2, .3)); S.put_emoji(cv, '👇', 540, int(865+8*math.sin(t*5)), 56)
SC = [(0.0, 4.5, b_hook, 'theatre_couleur'), (4.5, 27.5, b_step1, 'chambre'), (27.5, 39.5, b_step2, 'avenue'), (39.5, 60.44, b_step3, 'jardin'), (60.44, DUR, b_fin, 'theatre_couleur')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [s_[0] for s_ in SC[1:]]; IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
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
    ev += [(1.9, 'pop'), (2.1, 'pop'), (2.3, 'pop'), (3.0, 'bonk'), (4.7, 'thud'), (6.1, 'swish'), (9.9, 'fill1'), (13.2, 'fill2'), (20.9, 'tick'), (22.6, 'thud'),
           (24.1, 'thud'), (24.6, 'swish'), (26.6, 'bonk'), (27.7, 'thud'), (28.5, 'swish'), (30.0, 'pop'), (30.95, 'pop'), (31.75, 'pop'), (33.4, 'swish'),
           (37.75, 'tadaa'), (39.8, 'thud'), (40.5, 'swish'), (42.7, 'whoosh'), (48.3, 'glint'), (51.1, 'swish'), (56.6, 'tick'), (58.3, 'coins'), (64.5, 'glint'), (67.1, 'impact')]
    ev += [(51.6+i*5.2/14+.4, 'coin') for i in range(14)]
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
