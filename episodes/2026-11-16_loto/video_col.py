"""Le Loto toute ta vie contre la même somme placée (16/11/2026), cartoon 1930 en Technicolor : décors Gemini (bureau de tabac, scène de tirage,
machine à sous inversée, verger aux pièces d'or), accessoires Gemini détourés, plongée en perspective dans la foule des 19 068 840 joueurs
(zoom_foule.py), Mister Coin en couleurs, pellicule, iris aux changements de décor.
usage : python3 video_col.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
import veo_coin as VC
import zoom_foule as ZF
from scenes import surface, to_img, rr, col, W, H, clamp, ease, rgb, NB
FPS = 60; DUR = V.DUR; VOICE = V.VOICE; euro, tm = V.euro, V.tm
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def ent(k, d=.45): return ease(k/d)
def back(x, s=1.9): x = clamp(x); return max(1e-3, 1+(s+1)*(x-1)**3+s*(x-1)**2)      # rebond « caoutchouc », jamais 0 (cairo)
GOLD = ('FFE27A', 'F2B82E', 'B97A12', '6B4006'); INKC = '0D0D0D'; PAPER = 'F4F1EA'
# ---------- effets de pellicule ----------
@functools.lru_cache(maxsize=1)
def vignette():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xs-W/2)/(W*.62))**2+((ys-H/2)/(H*.62))**2)
    return np.clip(1-.55*np.clip(r-.55, 0, 1)**1.4*2.2, .3, 1)
def film(img, t):
    f = int(t*24); rng = np.random.default_rng(7000+f)
                                                                                                   # pas de flottement de l'image (il saccadait à 24 i/s)
    img = img*(1+rng.normal(0, .010))                                                                 # scintillement
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

# ================= décors Technicolor : lecture séquentielle, ralentie pour couvrir tout le passage, sans boucle ni retour arrière =================
DECC = {}                                                                     # décors interpolés en 60 i/s (decors_hd.py), un fichier par passage
class _Reader:
    def __init__(self): self.name = None; self.cap = None; self.i = -1; self.f = None
    def get(self, name, i):
        if name != self.name or i < self.i:
            if self.cap: self.cap.release()
            self.cap = cv2.VideoCapture(f'{D}/decors/hd/{name}.mp4'); self.name = name; self.i = -1; self.f = None
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
    key = f'{name}_{a:.2f}'
    i = int(round(max(0, t-a)*60))
    f = _RD.get(key, i) if os.path.exists(f'{D}/decors/hd/{key}.mp4') and not os.environ.get('APERCU') else None
    if f is None:                                                                       # aperçu sans le décor interpolé : image du décor d'origine
        cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); sp = min(1.0, (n-1)/24/max(.1, b-a))
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(n-1, int(max(0, t-a)*sp*24))); ok, f = cap.read(); cap.release()
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    g = g+.2*(g-cv2.GaussianBlur(g, (0, 0), 1.0))                               # légère accentuation (décors déjà agrandis par Real-ESRGAN)
    if name == 'tabac': g = g*(1-_newsmask()[..., None])+cv2.GaussianBlur(g, (0, 0), 7)*_newsmask()[..., None]   # faux texte des journaux adouci
    return np.clip((g-128)*1.06+130, 0, 255)
@functools.lru_cache(maxsize=1)
def _newsmask():
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (0, 760), (320, 1920), 1, -1); return cv2.GaussianBlur(m, (0, 0), 30)
MCX = []
def mcx(t): return [x for (a, x) in MCX if t >= a][-1]
def coin_col(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, mcx(t), Y)
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
YEL = 'FFE27A'; PINK = 'FF8A8A'
def title(c, s_, t, t0, y=290, size=64, fill=CREAM, t1=None, maxw=920):
    """titre peint qui arrive en rebond (et repart en fondu à t1)"""
    k = t-t0
    if k <= 0: return
    a = 1-ent(t-t1, .3) if t1 and t > t1 else 1
    if a <= 0: return
    sz = fit(c, s_, size, maxw); sc = back(k/.35); c.save(); c.translate(540, y); c.scale(sc, sc); paint(c, s_, 0, 0, sz, fill, a=a); c.restore()
def pop_text(c, s_, x, y, size, t, t0, fill=CREAM, rot=0.0, a=1.0):
    k = t-t0
    if k <= 0 or a <= 0: return
    sc = back(k/.35); c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc); paint(c, s_, 0, 0, size, fill, a=a); c.restore()
YEL = 'FFE27A'; PINK = 'FF8A8A'; MINT = '9DF2B5'
def title(c, s_, t, t0, y=290, size=64, fill=CREAM, t1=None, maxw=920):
    k = t-t0
    if k <= 0: return
    a = 1-ent(t-t1, .3) if t1 and t > t1 else 1
    if a <= 0: return
    sz = fit(c, s_, size, maxw); sc = back(k/.35); c.save(); c.translate(540, y); c.scale(sc, sc); paint(c, s_, 0, 0, sz, fill, a=a); c.restore()
def pop_text(c, s_, x, y, size, t, t0, fill=CREAM, rot=0.0, a=1.0, maxw=None):
    k = t-t0
    if k <= 0 or a <= 0: return
    if maxw: size = fit(c, s_, size, maxw)
    sc = back(k/.35); c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc); paint(c, s_, 0, 0, size, fill, a=a); c.restore()
def ink(c, s_, x, y, size, colr, a=1.0, maxw=None):
    """lettres peintes à l'encre sur un support (pancarte, certificat) : pleines, sans contour"""
    c.select_font_face('Alfa Slab One', 0, 0); c.set_font_size(size); e = c.text_extents(s_)
    if maxw and e.x_advance > maxw: size *= maxw/e.x_advance; c.set_font_size(size); e = c.text_extents(s_)
    c.move_to(x-e.x_advance/2, y+e.height/2-(e.height+e.y_bearing)/2); c.text_path(s_); col(c, colr, a); c.fill()
BOARD = (30, 975, 1195, 1715)                                           # planche seule de la pancarte (sans les cordes), coordonnées de pancarte.png
def board(c, x, y, w, k, rot=0.0, lines=()):
    """planche de la pancarte sans cordes, clouée sur un support du décor ; lignes de texte à l'encre"""
    if k <= 0: return
    sf, iw, ih = psurf('pancarte'); x0, y0, x1, y1 = BOARD; s = w/(x1-x0)*back(k/.35)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.translate(-(x0+x1)/2, -(y0+y1)/2)
    c.rectangle(x0, y0, x1-x0, y1-y0); c.clip(); c.set_source_surface(sf, 0, 0); c.paint()
    n = len(lines); cy = (y0+y1)/2
    for i, (tx, sz, colr) in enumerate(lines): ink(c, tx, (x0+x1)/2, cy+(i-(n-1)/2)*sz*1.15, sz, colr, maxw=(x1-x0)*.8)
    for (nx, ny) in ((x0+55, y0+55), (x1-55, y0+55), (x0+55, y1-55), (x1-55, y1-55)):     # clous
        c.arc(nx, ny, 18, 0, 2*math.pi); col(c, '5A4A3A'); c.fill()
    c.restore()
def fade(t, t0, t1=None, d=.3): return ent(t-t0, d)*(1-ent(t-t1, d) if t1 is not None else 1)
def on_prop(c, name, x, y, w=None, h=None, k=1.0, rot=0.0, a=1.0, texts=()):
    """accessoire + textes écrits dessus, en coordonnées de l'image de l'accessoire : (texte, px, py, taille, couleur)"""
    sf, iw, ih = psurf(name); s = (w/iw if w else h/ih)*back(k/.35) if k > 0 else 0
    if s <= 0 or a <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.set_source_surface(sf, -iw/2, -ih/2); c.paint_with_alpha(a)
    for (tx, px, py, sz, colr) in texts: ink(c, tx, px-iw/2, py-ih/2, sz, colr, a=a, maxw=iw*.78)
    c.restore()
COUPONS = [(70, 250), (290, 470), (510, 690), (736, 916), (960, 1140), (1180, 1360)]; CY0, CY1 = 1530, 1840
def bond(c, x, y, h, t, k=1.0, a=1.0, gone=0, tgo=(), label=True):
    """obligation à coupons : les coupons détachés (gone) s'envolent vers la gauche et deviennent des pièces (intérêts)"""
    sf, iw, ih = psurf('obligation_coupons'); s = h/ih*back(k/.35) if k > 0 else 0
    if s <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s); c.translate(-iw/2, -ih/2)
    c.rectangle(0, 0, iw, ih); 
    for i in range(gone): x0, x1 = COUPONS[i]; c.rectangle(x1+8, CY0-12, x0-x1-16, CY1-CY0+24)
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.clip(); c.set_source_surface(sf, 0, 0); c.paint_with_alpha(a); c.restore()
    if label:
        c.save(); c.translate(x, y); c.scale(s, s); c.translate(-iw/2, -ih/2); ink(c, "OBLIGATION", 715, 292, 110, '1E3A5F', a=a, maxw=480); c.restore()
    for i in range(gone):                                              # coupons en vol, puis pièce
        kk = t-tgo[i]
        if kk < 0 or kk > 1.3: continue
        x0, x1 = COUPONS[i]; cx_, cy_ = x+((x0+x1)/2-iw/2)*s, y+((CY0+CY1)/2-ih/2)*s
        u = ease(kk/1.1); px, py = cx_+(250-cx_)*u, cy_-260*math.sin(u*math.pi)+(820-cy_)*u
        if kk < .55:
            c.save(); c.translate(px, py); c.rotate(-1.5*kk); c.scale(s, s); c.rectangle(-(x1-x0)/2, -(CY1-CY0)/2, x1-x0, CY1-CY0); c.clip()
            c.set_source_surface(sf, -(x0+x1)/2, -(CY0+CY1)/2); c.paint(); c.restore()
        else:
            r = 26*(1-ent(kk-1.1, .2)); c.arc(px, py, r, 0, 2*math.pi); col(c, 'F2B82E'); c.fill_preserve(); c.set_line_width(4); col(c, BROWN); c.stroke()
            paint(c, "€", px, py, 26*r/26, BROWN) if r > 8 else None
def star(c, x, y, r):
    c.move_to(x, y-r)
    for i in range(1, 8): rr_ = r if i % 2 == 0 else r*.28; th = -math.pi/2+i*math.pi/4; c.line_to(x+rr_*math.cos(th), y+rr_*math.sin(th))
    c.close_path(); col(c, 'FFF6C8', .95); c.fill()
def cross(c, x, y, r, u):
    """grande croix rouge tracée à la main (u de 0 à 1)"""
    if u <= 0: return
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_width(22)
    for (x0, y0, x1, y1), uu in (((x-r, y-r, x+r, y+r), clamp(u*2)), ((x+r, y-r, x-r, y+r), clamp(u*2-1))):
        if uu <= 0: continue
        c.move_to(x0, y0); c.line_to(x0+(x1-x0)*uu, y0+(y1-y0)*uu); col(c, 'D7262B', .92); c.stroke()
def arrow(c, x0, y0, x1, y1, u, colr=CREAM, wd=12):
    if u <= 0: return
    xe, ye = x0+(x1-x0)*u, y0+(y1-y0)*u; ang = math.atan2(ye-y0, xe-x0)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_width(wd); c.move_to(x0, y0); c.line_to(xe, ye); col(c, BROWN); c.set_line_width(wd+8); c.stroke_preserve(); c.set_line_width(wd); col(c, colr); c.stroke()
    for s_ in (1, -1):
        c.move_to(xe, ye); c.line_to(xe-34*math.cos(ang+s_*.5), ye-34*math.sin(ang+s_*.5)); c.set_line_width(wd+8); col(c, BROWN); c.stroke_preserve(); c.set_line_width(wd); col(c, colr); c.stroke()
def twinkle(c, t, pts, r=22):
    for i, (x, y) in enumerate(pts):
        u = .5+.5*math.sin(t*3.1+i*1.7)
        if u > .25: star(c, x, y, r*u)
def _fade(cv, f, a):
    tmp = cv.copy(); f(tmp); cv.paste(Image.blend(cv.convert('RGBA'), tmp.convert('RGBA'), clamp(a)))

def plate(c, x, y, w, h, a):
    """pastille sombre derrière un texte posé sur un décor chargé (lisibilité)"""
    if a <= 0: return
    rr(c, x-w/2, y-h/2, w, h, h/2); c.set_source_rgba(.13, .06, .16, .6*a); c.fill()
# ================= panneaux de verre (compteurs, jauges) =================
def glass_counter(cv, t, t0, v1, t_a, t_b, sub, cy=780, w=860, h=230, colr=None, a=1.0, t1=None):
    k = t-t0
    if k <= 0: return
    if t1 and t > t1-.3:
        return _fade(cv, lambda x: glass_counter(x, t, t0, v1, t_a, t_b, sub, cy, w, h, colr, a), 1-ent(t-(t1-.3), .3))
    def d(kk, ww, hh):
        v = v1*inout((t-t_a)/max(.01, t_b-t_a))
        S.text(kk, euro(v), ww/2, hh/2-14, 'a', 92, colr or S.GD, 'c', ent(k, .3))
        S.text(kk, sub, ww/2, hh-34, 'sb', 26, S.ICE, 'c', .85*ent(k-.3, .3))
    S.tp(cv, w, h, d, 540, cy+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=26)
def glass_bar(cv, t, t0, parts, cy=700, w=920, h=400, note=None, t1=None):
    """apparition en fondu sur 0,35 s, disparition en fondu sur 0,3 s avant t1"""
    a = ent(t-t0, .35)*(1-ent(t-(t1-.3), .3) if t1 else 1)
    if t-t0 <= 0 or a <= 0: return
    if a < .999: return _fade(cv, lambda x: _glass_bar(x, t, t0, parts, cy, w, h, note), a)
    _glass_bar(cv, t, t0, parts, cy, w, h, note)
def _glass_bar(cv, t, t0, parts, cy=700, w=920, h=400, note=None):
    """barre empilée : parts = [(fraction, couleur haute, couleur basse, texte haut, sous-texte, t_apparition, côté)]"""
    k = t-t0
    if k <= 0: return
    def d(kk, ww, hh):
        x0, x1 = 70, ww-70; y = 150; bh = 130; L = x1-x0; x = x0
        for (fr, c0, c1, lab, sub, ta, side) in parts:
            u = inout((t-ta)/1.0); bw = L*fr*u
            if bw > 2:
                rr(kk, x+(6 if x > x0 else 0), y, bw-(6 if x > x0 else 0), bh, 14); g = cairo.LinearGradient(0, y, 0, y+bh)
                for st, cc in ((0, c0), (1, c1)): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .96)
                kk.set_source(g); kk.fill()
            if t > ta:
                tx = x0+8 if side == 'l' else x1-8
                S.text(kk, lab, tx, y-46, 'a', 50, c0, side, ent(t-ta-.1, .3)); S.text(kk, sub, tx, y+bh+40, 'sb', 28, S.ICE, side, .85*ent(t-ta-.2, .3))
            x += L*fr
        if note: S.text(kk, note, ww/2, hh-22, 'sb', 22, S.ICE, 'c', .7*ent(k-.6, .3))
    S.tp(cv, w, h, d, 540, cy+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def ball(c, x, y, r, num, k=1.0, rot=0.0):
    """boule de loto avec son numéro peint dans la pastille"""
    if k <= 0: return
    sf, iw, ih = psurf('boule_loto'); s = 2*r/iw*back(k/.35)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.set_source_surface(sf, -iw/2, -ih/2); c.paint()
    ink(c, num, 0, -18, 330, BROWN, maxw=400); c.restore()
# ================= 1. accroche et coût (bureau de tabac) =================
def b_tabac(cv, c, t, k):
    if t < 5.0:
        a = 1-ent(t-4.75, .25) if t > 4.75 else 1
        title(c, "LE LOTO", t, .1, 230, 92, YEL, t1=4.75)
        title(c, "OU LE PLACEMENT ?", t, 2.15, 330, 66, CREAM, t1=4.75)
        prop(c, 'grille_loto', 290, 660, h=380, k=t-.45, rot=-.12+.03*math.sin(t*2), a=a)
        if t > 1.9: pop_text(c, "VS", 540, 660, 90, t, 1.95, PINK, rot=-.08, a=a)
        if t > 2.25: prop(c, 'tirelire', 790, 680, w=330, k=t-2.3, a=a)
        if t > 3.7: twinkle(c, t, [(700, 520), (900, 560)], 22)
    if 5.0 <= t < 12.6:
        a = 1-ent(t-12.35, .25) if t > 12.35 else 1
        prop(c, 'grille_loto', 540, 600, h=430, k=t-5.05, rot=-.06, a=a)
        if t > 6.1: pop_text(c, f"2,20{NB}€", 540, 300, 120, t, 6.15, YEL, rot=-.04, a=a*(1-ent(t-10.95, .25)))
        for i, (lab, ta) in enumerate((("LUNDI", 8.63), ("MERCREDI", 9.2), ("SAMEDI", 10.23))):
            if t > ta: pop_text(c, lab, 220+i*320, 880, 44, t, ta, CREAM, rot=(-.05, .03, -.04)[i], a=a)
        if t > 10.85: pop_text(c, "× 3", 870, 640, 80, t, 10.85, PINK, rot=.08, a=a)
    if t > 10.8 and t < 12.7:
        pop_text(c, f"= 6,60{NB}€ / SEMAINE", 540, 300 if t < 12.35 else 300, 60, t, 11.2, YEL, a=1-ent(t-12.4, .25) if t > 12.4 else 1) if t > 11.2 else None
    if t > 12.66:
        title(c, "DE 25 À 65 ANS", t, 12.7, 250, 72)
        glass_counter(cv, t, 13.3, 13728, 13.6, 15.6, "6 240 grilles en 40 ans", cy=640)
        if t > 15.4: prop(c, 'pluie_pieces', 540, 900, h=200, k=t-15.45, rot=.1*math.sin(t*2), shadow=False)
# ================= 2. les chances (scène de tirage + plongée dans la foule) =================
def b_tirage(cv, c, t, k):
    zs, ze = V.ZOOM
    if t < zs:
        title(c, "LE JACKPOT ?", t, 16.5, 250, 84, YEL)
        for i, (x, y, n, ta) in enumerate(((300, 620, "7", 16.8), (540, 560, "19", 17.1), (780, 640, "42", 17.4))):
            if t > ta: ball(c, x, y+12*math.sin(t*2.4+i), 95, n, k=t-ta, rot=.15*math.sin(t*1.3+i))
    if t > ze:
        if t < 27.0:
            a = 1-ent(t-26.8, .25) if t > 26.8 else 1
            title(c, "40 ANS DE JEU", t, ze+.05, 250, 76, CREAM, t1=26.8)
            if t > 23.3: plate(c, 540, 372, 420, 80, ent(t-23.3, .2)*a); pop_text(c, f"6{NB}240 GRILLES", 540, 372, 52, t, 23.3, CREAM, a=a)
            if t > 24.55:
                plate(c, 540, 660, 940, 230, ent(t-24.55, .2)*a)
                pop_text(c, f"1 CHANCE SUR 3{NB}000", 540, 625, 78, t, 24.6, PINK, rot=-.03, a=a)
            if t > 25.7: paint(c, "de gagner le jackpot une seule fois", 540, 718, 40, a=ent(t-25.7, .3)*a)
        if 27.0 <= t < 32.0:
            title(c, f"SUR 100{NB}€ JOUÉS", t, 27.15, 250, 72, CREAM, t1=31.9)
            glass_bar(cv, t, 27.6, [(.5435, 'FFE27A', 'B97A12', f"54{NB}€", "reversés aux gagnants", 28.6, 'l'),
                                    (.4565, 'C9C2D6', '6E6680', f"46{NB}€", "gardés", 30.4, 'r')], cy=640,
                      note="taux de retour aux joueurs du Loto : 54,35 % depuis le 4 mai 2026", t1=32.0)
        if t >= 32.0:
            title(c, "EN MOYENNE", t, 32.05, 250, 76, CREAM)
            prop(c, "ticket_froisse", 540, 520, h=300, k=t-32.2, rot=-.1+.04*math.sin(t*3))
            if t > 33.6: plate(c, 540, 850, 620, 150, ent(t-33.6, .2)); pop_text(c, f"− 6{NB}267{NB}€", 540, 850, 104, t, 33.65, PINK, rot=-.04)
def crowd(t):
    """plongée : image de la foule (RGB float), flou de mouvement par 2 sous-images"""
    zs, ze = V.ZOOM; u0, u1 = zs+.1, 21.9
    acc = 0
    for kk in (-.25, .25):
        im, pos = ZF.frame(clamp((t+kk/FPS-u0)/(u1-u0)), W, H, cy=640, ta=t); acc = acc+im/2
    return acc[..., ::-1].copy(), pos
def crowd_text(c, t, pos):
    zs, ze = V.ZOOM; u = (t-(zs+.1))/(21.9-(zs+.1))
    a1 = ent(t-zs-.15, .3)*(1-ent(u-.5, .15))
    if a1 > 0: paint(c, f"19{NB}068{NB}840 JOUEURS", 540, 260, 70, CREAM, a=a1)
    if u > .9:
        x, y, sz = pos; r = sz*.62
        t0 = zs+.1+.92*(21.9-zs-.1); ty = y-r-60
        rr(c, x-130, ty-66, 260, 132, 48); c.set_source_rgba(.13, .06, .16, .62*ent(t-t0, .25)); c.fill()      # pastille sombre : TOI lisible sur la foule
        pop_text(c, "TOI", x, ty, 96, t, t0, YEL, rot=-.04)   # « une sur 19 millions » est déjà dans le sous-titre : pas d'autre texte
# ================= 3. le placement (machine à sous inversée) =================
def b_machine(cv, c, t, k):
    if t < 39.0:
        title(c, "ET SI TU PLAÇAIS", t, 34.7, 230, 66, CREAM, t1=38.95)
        title(c, "CES 6,60 € ?", t, 36.3, 320, 76, YEL, t1=38.95)
        if t > 38.2: pop_text(c, f"7{NB}% PAR AN", 540, 820, 72, t, 38.25, MINT, rot=-.04, a=1-ent(t-38.95, .25) if t > 38.95 else 1)
    if 39.0 <= t < 42.0:
        title(c, "À 65 ANS", t, 39.05, 250, 80, YEL, t1=41.95)
        glass_counter(cv, t, 39.3, 71086, 39.5, 40.9, "28,60 € par mois pendant 40 ans, à 7 %", cy=700, t1=42.0)
    if t >= 42.0:
        title(c, "TU N'AS VERSÉ QUE", t, 42.05, 250, 64, CREAM)
        glass_bar(cv, t, 42.3, [(13728/71086, '7FB2FF', '2E4FA8', f"13{NB}728{NB}€", "versés", 42.9, 'l'),
                                (57358/71086, 'FFE27A', 'B97A12', f"+ 57{NB}358{NB}€", "intérêts composés", 44.3, 'r')], cy=700,
                  note="hypothèse de 7 % par an non garantie, avant frais et impôts")
# ================= 4. face-à-face et question (verger) =================
def b_verger(cv, c, t, k):
    if t < 53.0:
        a = 1-ent(t-52.8, .25) if t > 52.8 else 1
        paint(c, "LE LOTO", 280, 260, 64, PINK, a=ent(t-46.1, .3)*a)
        prop(c, 'ticket_froisse', 280, 520, h=330, k=t-46.2, rot=-.08+.03*math.sin(t*2.5), a=a)
        if t > 46.7: plate(c, 280, 790, 470, 170, ent(t-46.7, .2)*a); pop_text(c, f"− 6{NB}267{NB}€", 280, 760, 66, t, 46.75, PINK, a=a)
        if t > 47.1: paint(c, "un rêve", 280, 832, 34, a=ent(t-47.1, .3)*a)
        if t > 49.1:
            paint(c, "LE PLACEMENT", 800, 260, 56, MINT, a=ent(t-49.1, .3)*a)
            prop(c, 'tirelire', 800, 530, w=330, k=t-49.2, a=a)
            if t > 49.7: plate(c, 800, 790, 470, 170, ent(t-49.7, .2)*a); pop_text(c, f"+ 57{NB}358{NB}€", 800, 760, 66, t, 49.75, YEL, a=a)
            if t > 51.0: paint(c, "il travaille pour toi", 800, 832, 34, a=ent(t-51.0, .3)*a)
            twinkle(c, t, [(700, 420), (920, 470)], 20)
    if 53.0 <= t < 57.0:
        a = 1-ent(t-56.8, .25) if t > 56.8 else 1
        title(c, "POUR LE PLAISIR ?", t, 53.1, 250, 72, CREAM, t1=56.8)
        if t > 54.3: pop_text(c, "POURQUOI PAS", 540, 350, 60, t, 54.35, MINT, a=a)
        if t > 55.4: pop_text(c, "MAIS CE N'EST PAS", 540, 700, 60, t, 55.4, CREAM, a=a)
        if t > 55.9: pop_text(c, "UN PLACEMENT", 540, 790, 84, t, 55.95, PINK, rot=-.03, a=a)
    if t >= 57.0:
        title(c, "ET TOI,", t, 57.05, 250, 80)
        title(c, "TU JOUES AU LOTO ?", t, 57.75, 350, 72, YEL)
    if t > 59.0: plate(c, 540, 470, 640, 90, ent(t-59.05, .3)); paint(c, "Dis-le en commentaire", 500, 470, 44, a=ent(t-59.05, .3))
SC = [(0.0, 16.4, b_tabac, 'tabac'), (16.4, 34.6, b_tirage, 'tirage'), (34.6, 46.0, b_machine, 'machine'), (46.0, DUR, b_verger, 'verger')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [s_[0] for s_ in SC[1:]]+list(V.ZOOM); IR = .42
MCX = [(0, 540), (SC[1][0], 540), (SC[2][0], 540), (SC[3][0], 540)]
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    zs, ze = V.ZOOM; inz = zs <= t < ze
    if inz: img, pos = crowd(t)
    else: img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface()
    if inz: crowd_text(c, t, pos)
    else: f(cv, c, t, max(0.0, t-a))
    cv.alpha_composite(to_img(s))
    arr = coin_col(np.asarray(cv.convert('RGB')).astype(np.float32), t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    if t > 59.05: S.put_emoji(out, "👇", 900, int(470+8*math.sin(t*5)), 60)
    arr = np.asarray(out.convert('RGB')).astype(np.float32); u = 0
    for ta in IRIS:
        if ta-IR <= t < ta: u = inout((t-(ta-IR))/IR)
        elif ta <= t < ta+IR: u = 1-inout((t-ta)/IR)
    if u > 0: arr = iris(arr, u)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else 'FF8A8A', a=al); return
def events():
    zs, ze = V.ZOOM
    ev = [e for e in V.events()] + [(ta-IR, 'whoosh') for ta in IRIS]
    ev += [(.1, 'impact'), (.5, 'pop'), (1.95, 'bonk'), (2.15, 'thud'), (2.3, 'pop'), (5.05, 'pop'), (6.15, 'impact'), (8.63, 'pop'), (9.2, 'pop'), (10.23, 'pop'),
           (10.85, 'bonk'), (11.2, 'coin'), (12.7, 'thud'), (13.3, 'swish'), (13.6, 'fill1'), (15.45, 'coins')]
    ev += [(16.5, 'impact'), (16.8, 'pop'), (17.1, 'pop'), (17.4, 'pop'), (zs+.15, 'riser'), (zs+.1+.92*(21.9-zs-.1), 'tadaa'), (ze+.05, 'thud'), (23.3, 'pop'), (24.6, 'crash'),
           (27.15, 'thud'), (27.6, 'swish'), (28.6, 'fill1'), (30.4, 'pop'), (32.05, 'thud'), (32.2, 'pop'), (33.65, 'bonk')]
    ev += [(34.7, 'thud'), (36.3, 'impact'), (38.25, 'pop'), (39.05, 'impact'), (39.3, 'swish'), (39.5, 'fill2'), (40.9, 'coins'), (42.05, 'thud'), (42.3, 'swish'), (42.9, 'fill0'), (44.3, 'fill2'), (44.6, 'glint')]
    ev += [(46.2, 'pop'), (46.75, 'bonk'), (49.2, 'pop'), (49.75, 'tadaa'), (53.1, 'thud'), (54.35, 'pop'), (55.4, 'pop'), (55.95, 'impact'), (57.05, 'thud'), (57.75, 'impact')]
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
