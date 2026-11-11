"""L'or : ni propriétaire, ni prêteur (12/11/2026), cartoon 1930 en Technicolor : décors Gemini (hangar au cube d'or, globe, trésor de Lydie,
mine, réserve d'une banque centrale, comptoir de change), accessoires Gemini détourés, Mister Coin en couleurs, pellicule, iris aux changements
de décor et travelling dans le globe vers la Lydie.
usage : python3 video_col.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
import veo_coin as VC
from scenes import surface, to_img, rr, col, W, H, clamp, ease, rgb, NB
FPS = 60; DUR = V.DUR; VOICE = V.VOICE; euro, count_to = V.euro, V.count_to
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

# ================= décors Technicolor : lecture séquentielle, ralentie pour couvrir tout le passage, sans boucle ni retour arrière =================
DECC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('hangar_cube', 'globe', 'lydie', 'mine', 'reserves', 'comptoir')}
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
def globe_t(t):   # globe : il tourne vite puis ralentit et s'arrête sur l'Europe (image 8 s du décor), puis reste figé
    return 2.0+6.0*(1-(1-clamp((t-7.95)/3.0))**3)
def decor_c(name, t):
    a, b = next((a, b) for (a, b, d) in BLOCS if d == name and a <= t < b+.5)
    n = nframes(name)
    if name == 'globe': i = min(n-1, int(globe_t(t)*24))
    else: sp = min(1.0, (n-1)/24/max(.1, b-a)); i = min(n-1, int(max(0, t-a)*sp*24))
    f = _RD.get(name, i)
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    return np.clip((g-128)*1.06+130, 0, 255)
def coin_col(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, V.MC.x, Y)
    fx = V.MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), V.FEET-3), (95, 15), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    return cv_rgb*(1-al[..., None])+rgb_.astype(np.float32)*al[..., None]
# Mister Coin de dos qui marche (scènes 3 et 4, travelling dans le trésor puis dans la mine) : clip classique_dos_marche en boucle sur deux pas
DOS = (13.5, 33.7); DOS_CLIP = f'{S.ROOT}/mister_coin/veo/classique_dos_marche.mp4'; DOS_L0, DOS_L1 = 61, 128; DOS_X = 540                    # de dos, il marche au milieu de l allée et des rails
class _Dos:
    def __init__(s): s.cap = None; s.i = -1; s.f = None
    def get(s, n):
        if s.cap is None or n < s.i: s.cap = cv2.VideoCapture(DOS_CLIP); s.i = -1
        while s.i < n:
            ok, fr = s.cap.read(); s.i += 1
            if ok: s.f = fr
        return s.f
_DS = _Dos()
def dos_col(cv_rgb, t):
    n = 40+int((t-DOS[0])*24)
    if n >= DOS_L1: n = DOS_L0+(n-DOS_L0) % (DOS_L1-DOS_L0)
    rgb_, m = VC._key(_DS.get(n)[..., ::-1].copy()); sc = 170/314
    rgb_ = cv2.resize(rgb_.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA); m = cv2.resize(m.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    x0, y0 = int(DOS_X-360*sc), int(V.FEET-1035*sc); h, w = m.shape
    sh = np.zeros((H, W), np.float32); cv2.ellipse(sh, (DOS_X, V.FEET-3), (95, 15), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(sh, (0, 0), 9)[..., None])
    ya, yb_, xa, xb = max(0, y0), min(H, y0+h), max(0, x0), min(W, x0+w)
    mm = m[ya-y0:yb_-y0, xa-x0:xb-x0][..., None]; cv_rgb[ya:yb_, xa:xb] = cv_rgb[ya:yb_, xa:xb]*(1-mm)+rgb_[ya-y0:yb_-y0, xa-x0:xb-x0]*mm
    return cv_rgb
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
# ================= 1. le cube (hangar) =================
CUBE_T, CUBE_R, CUBE_B = (0, 4, 8), (790, 812, 852), (1092, 1179, 1258)   # bord droit et bas des lingots mesurés sur le décor (le travelling avance)
def b_cube(cv, c, t, k):
    title(c, "TOUT L'OR JAMAIS EXTRAIT", t, .05, 250, 60)
    if t > 1.9: pop_text(c, f"219{NB}891 tonnes", 540, 335, 44, t, 1.95, YEL)
    xr = float(np.interp(t, CUBE_T, CUBE_R)); yb = float(np.interp(t, CUBE_T, CUBE_B)); yt = 430
    if t > 3.4:                                                              # cote de 22 m le long de l'arête droite du cube
        u = ent(t-3.4, .5); xc = xr+46; ym = (yt+yb)/2; h2 = (yb-yt)/2*u
        c.set_line_width(5); col(c, YEL); c.move_to(xc, ym-h2); c.line_to(xc, ym+h2); c.stroke()
        for yy in (ym-h2, ym+h2): c.move_to(xc-18, yy); c.line_to(xc+18, yy); c.stroke()
        if t > 3.85: pop_text(c, f"22{NB}m", min(xc+90, 930), ym, 64, t, 3.9, YEL, rot=-.05)
    if t > 4.3:                                                              # un bonhomme de 1,80 m au pied du cube, pour l'échelle
        hh = (yb-yt)/12.2; x = xr-80; a = ent(t-4.3, .3); c.save(); col(c, '1A1A22', .9*a)
        c.arc(x, yb-hh*.88, hh*.12, 0, 2*math.pi); c.fill(); rr(c, x-hh*.12, yb-hh*.75, hh*.24, hh*.42, hh*.08); c.fill()
        c.set_line_width(hh*.08); c.move_to(x-hh*.06, yb-hh*.35); c.line_to(x-hh*.08, yb); c.move_to(x+hh*.06, yb-hh*.35); c.line_to(x+hh*.08, yb); c.stroke(); c.restore()
        paint(c, f"toi : 1,80{NB}m", x-10, yb+38, 24, a=a*(1-ent(t-5.2, .3)), fam='Limelight')
    if t > 5.3:
        pop_text(c, "RARE = PRÉCIEUX", 540, 420, 52, t, 5.4, YEL, rot=-.03)
        twinkle(c, t, [(380, 520), (700, 600), (520, 760), (760, 900), (430, 980)], 26*ent(t-5.3, .4))
# ================= 2. Varna (globe) =================
VARNA = (618, 552)
def b_globe(cv, c, t, k):
    title(c, "LES PLUS VIEUX BIJOUX EN OR", t, 8.1, 250, 56, t1=12.9)
    if t > 8.75: prop(c, 'bijoux_varna', 730, 1280, w=330, k=t-8.8, rot=-.04)
    if t > 10.9:                                                             # le point de Varna clignote
        x, y = VARNA; p = .5+.5*math.sin((t-10.9)*7); u = ent(t-10.9, .3)
        c.arc(x, y, (26+22*p)*u, 0, 2*math.pi); col(c, RED, .35*(1-p)+.1); c.fill()
        c.arc(x, y, 13*u, 0, 2*math.pi); col(c, RED); c.fill_preserve(); c.set_line_width(4); col(c, 'FFFFFF'); c.stroke()
    if t > 11.15: pop_text(c, "VARNA (BULGARIE)", 618, 470, 40, t, 11.2, CREAM, a=1-ent(t-13.1, .2))
    if t > 12.4:
        pop_text(c, f"+ DE 6{NB}000 ANS", 618, 640, 58, t, 12.45, YEL, rot=-.03, a=1-ent(t-13.1, .2))
        paint(c, f"vers 4{NB}500 av. J.-C.", 618, 710, 30, a=ent(t-12.7, .3)*(1-ent(t-13.1, .2)), fam='Limelight')
# ================= 3. Crésus (trésor de Lydie) =================
RAIN = [(np.random.default_rng(31+i).uniform(60, 1020), np.random.default_rng(91+i).uniform(0, 2.2), np.random.default_rng(57+i).uniform(55, 115),
         np.random.default_rng(73+i).uniform(-3, 3)) for i in range(42)]
def b_cresus(cv, c, t, k):
    title(c, "LES PREMIÈRES PIÈCES", t, 13.65, 250, 64, t1=16.0)
    if t > 14.3:                                                             # la créséide, puis elle file dans le coin
        u = ent(t-15.95, .5) if t > 15.95 else 0
        prop(c, 'creseide', lerp(540, 860, u), lerp(620, 430, u), w=lerp(420, 190, u), k=t-14.35, rot=.04*math.sin(t*1.5))
        if t > 14.7: paint(c, "en or pur", lerp(540, 860, u), lerp(865, 560, u), lerp(36, 24, u), a=ent(t-14.7, .3)*(1-ent(t-19.2, .3)), fam='Limelight')
    title(c, "LE ROI CRÉSUS", t, 16.15, 250, 66, t1=19.2)
    if t > 16.15: prop(c, 'cresus', 470, 700, h=640, k=t-16.2, rot=.02*math.sin(t*2))
    if t > 16.8: paint(c, "Lydie, vers 560 av. J.-C.", 540, 330, 32, a=ent(t-16.85, .3)*(1-ent(t-19.2, .3)), fam='Limelight')
    if t > 19.3:                                                             # pluie de pièces (derrière Mister Coin)
        for (x, d0, sz, sp) in RAIN:
            kk = t-19.3-d0
            if kk <= 0: continue
            y = -80+kk*kk*620+kk*320
            if y < 1980: prop(c, 'creseide', x, y, w=sz, rot=sp*kk, shadow=False)
        title(c, "RICHE COMME CRÉSUS", t, 20.3, 270, 76, YEL)
# ================= 4. la mine =================
def b_mine(cv, c, t, k):
    title(c, "RARE", t, 21.8, 250, 80, t1=25.5)
    title(c, "IMPOSSIBLE À FABRIQUER", t, 22.2, 340, 50, YEL, t1=25.5)
    if t < 26.0: prop(c, 'pepite', 540, 620, w=380, k=t-21.85, rot=.03*math.sin(t*1.4), a=1-ent(t-25.5, .3))
    if 21.9 < t < 25.8: twinkle(c, t, [(400, 520), (680, 560), (560, 760)], 24)
    if t > 24.6: pop_text(c, "= UNE MONNAIE", 540, 870, 52, t, 24.65, YEL, a=1-ent(t-25.5, .3))
    fo = 1-ent(t-29.6, .3) if t > 29.6 else 1
    title(c, "JUSQU'EN 1971", t, 26.4, 250, 76, YEL, t1=29.6)
    if t > 27.65: prop(c, 'billet_dollar', 285, 620, w=390, k=t-27.7, rot=-.05, a=fo)
    if t > 28.0: paint(c, "le dollar", 285, 800, 34, a=ent(t-28.0, .3)*fo, fam='Limelight')
    if t > 28.85: prop(c, 'lingot', 800, 610, w=320, k=t-28.9, rot=.04, a=fo)
    if t > 29.0: paint(c, "l'or", 800, 800, 34, a=ent(t-29.0, .3)*fo, fam='Limelight')
    if t > 28.5:
        u = ent(t-28.5, .5)*fo; arrow(c, 500, 575, 630, 575, u, YEL); arrow(c, 630, 665, 500, 665, u, YEL)
    if t > 29.85:                                                            # le stock mondial ne grossit que d'une fine tranche par an
        title(c, f"MOINS DE 2{NB}% PAR AN", t, 32.4, 250, 64, YEL)
        stock_glass(cv, t, 29.95)
def stock_glass(cv, t, t0):
    k = t-t0
    def d(kk, w, h):
        s_ = 330; x0, y0 = w/2-s_/2-120, h/2-s_/2+40
        kk.rectangle(x0, y0, s_, s_); g = cairo.LinearGradient(0, y0, 0, y0+s_)
        for st, cc in ((0, 'FFE27A'), (.5, 'F2B82E'), (1, 'B97A12')): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgb(st, r_, g_, b_)
        kk.set_source(g); kk.fill()
        for i in range(1, 6): kk.move_to(x0, y0+i*s_/6); kk.line_to(x0+s_, y0+i*s_/6); kk.set_line_width(2); col(kk, '8A5A0A', .5); kk.stroke()
        S.text(kk, f"219{NB}891{NB}t", x0+s_/2, y0+s_/2, 'a', 46, '4A2C05', 'c', ent(t-t0-.3, .3))
        u = inout((t-t0-1.0)/1.0); th = s_*.017*u                          # 1,7 % du stock en 2025
        p = .6+.4*math.sin(t*6)
        kk.rectangle(x0, y0-th-6*u, s_, th+6*u); col(kk, 'FFF6C8', .95*u); kk.fill()
        kk.rectangle(x0-6, y0-th-14*u, s_+12, th+20*u); kk.set_line_width(3); col(kk, S.WHITE, .6*p*u); kk.stroke()
        xr = x0+s_+40
        S.text(kk, f"+3{NB}672{NB}t", xr, y0+10, 'a', 46, S.GD, 'l', ent(t-t0-1.3, .3)); S.text(kk, "extraites en 2025", xr, y0+52, 'sb', 24, S.ICE, 'l', .85*ent(t-t0-1.4, .3))
        S.text(kk, f"soit 1,7{NB}%", xr, y0+108, 'xb', 34, S.WHITE, 'l', ent(t-t0-1.8, .3)); S.text(kk, "du stock mondial", xr, y0+146, 'sb', 24, S.ICE, 'l', .85*ent(t-t0-1.9, .3))
        S.text(kk, "tout l'or extrait depuis toujours", w/2, h-30, 'sb', 22, S.ICE, 'c', .7*ent(t-t0-.4, .3))
    S.tp(cv, 880, 520, d, 540, 650+40*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
# ================= 5. qui en a le plus (réserve d'une banque centrale) =================
def flag(kk, code, x, y, w=72, h=48):
    kk.save(); rr(kk, x, y, w, h, 6); kk.clip()
    if code == 'US':
        for i in range(7): kk.rectangle(x, y+i*h/7, w, h/14); col(kk, 'B22234'); kk.fill()
        kk.rectangle(x, y+h/14, w, 0); kk.rectangle(x, y, w*.42, h*.54); col(kk, '3C3B6E'); kk.fill()
        for i in range(7): kk.rectangle(x, y+(2*i+1)*h/14, w, h/14); col(kk, 'FFFFFF'); kk.fill()
        kk.rectangle(x, y, w*.42, h*.54); col(kk, '3C3B6E'); kk.fill()
    elif code == 'DE':
        for i, cc in enumerate(('000000', 'DD0000', 'FFCE00')): kk.rectangle(x, y+i*h/3, w, h/3+1); col(kk, cc); kk.fill()
    else:
        cs = ('009246', 'FFFFFF', 'CE2B37') if code == 'IT' else ('0055A4', 'FFFFFF', 'EF4135')
        for i, cc in enumerate(cs): kk.rectangle(x+i*w/3, y, w/3+1, h); col(kk, cc); kk.fill()
    kk.restore(); rr(kk, x, y, w, h, 6); kk.set_line_width(2); col(kk, S.WHITE, .6); kk.stroke()
RES = [('US', "ÉTATS-UNIS", 8133.5, 35.0), ('DE', "ALLEMAGNE", 3350, 37.9), ('IT', "ITALIE", 2452, 38.1), ('FR', "FRANCE", 2437, 38.4)]
def reserves_glass(cv, t, t0):
    k = t-t0
    def d(kk, w, h):
        x0, x1 = 300, w-150; top = 70
        for i, (code, name, v, tt) in enumerate(RES):
            y = top+i*112; a = ent(t-tt, .3)
            if a <= 0: continue
            fr = code == 'FR'
            S.text(kk, f"{i+1}.", 40, y+24, 'a', 36, S.GD if fr else S.ICE, 'l', a); flag(kk, code, 86, y, 70, 47)
            S.text(kk, name, 172, y+24, 'xb', 28, S.GD if fr else S.WHITE, 'l', a)
            u = inout((t-tt)/(2.0 if code == 'US' else .9)); bw = (x1-x0)*v/8133.5*u
            rr(kk, x0, y+60, max(2, bw), 30, 10); g = cairo.LinearGradient(x0, 0, x0+bw+1, 0)
            for st, cc in ((0, 'B97A12'), (1, 'FFE27A')): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .95)
            kk.set_source(g); kk.fill()
            S.text(kk, f"{int(v*u):,}".replace(',', NB)+f"{NB}t", x0+bw+16, y+76, 'a', 32, S.GD if fr else S.WHITE, 'l', a)
        S.text(kk, "réserves officielles d'or, 2026", w/2, h-26, 'sb', 22, S.ICE, 'c', .7*ent(t-t0-.4, .3))
    S.tp(cv, 900, 540, d, 540, 690+40*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def b_reserves(cv, c, t, k):
    title(c, "QUI EN A LE PLUS ?", t, 33.85, 250, 70, t1=41.4)
    reserves_glass(cv, t, 34.0)
    if t > 41.5:
        title(c, "LES BANQUES CENTRALES ACHÈTENT", t, 41.55, 240, 48)
        pop_text(c, "× 2", 540, 345, 96, t, 43.15, YEL, rot=-.04)
# ================= 6. ni propriétaire, ni prêteur (comptoir de change) =================
def b_pari(cv, c, t, k):
    fo = 1-ent(t-50.8, .35) if t > 50.8 else 1; fl = 1-ent(t-53.85, .25) if t > 53.85 else 1
    if t > 45.85: prop(c, 'lingot', 540, 640, w=380, k=t-45.9, rot=.03*math.sin(t*1.2), a=fl)
    if t > 46.7: prop(c, 'certificat_action', 220, 470, w=270, k=t-46.75, rot=-.06, a=fo)
    if t > 47.1: cross(c, 220, 470, 95, ent(t-47.15, .35)*fo); paint(c, "NI DIVIDENDE", 220, 615, 38, a=ent(t-47.1, .3)*fo, fam='Limelight')
    if t > 47.5: prop(c, 'obligation_coupons', 860, 470, h=190, k=t-47.55, rot=.06, a=fo)
    if t > 47.9: cross(c, 860, 470, 95, ent(t-47.95, .35)*fo); paint(c, "NI INTÉRÊT", 860, 615, 38, a=ent(t-47.9, .3)*fo, fam='Limelight')
    title(c, "NI PROPRIÉTAIRE, NI PRÊTEUR", t, 48.9, 250, 54, t1=50.8)
    if t > 50.9:
        title(c, "UN PARI", t, 50.95, 250, 76, YEL, t1=53.85)
        if t > 52.9:
            arrow(c, 800, 760, 800, 470, ent(t-52.95, .4)*fl, '9DF2B5', 14)
            pop_text(c, "REVENDRE + CHER", 540, 880, 50, t, 53.3, MINT, a=fl)
# ================= 7. les chiffres (comptoir) =================
M = lambda y, m, d=15: y+(m-1)/12+(d-1)/365
GOLD_EUR = [(M(2006, 11), 486)] + [(y+.5, v) for y, v in zip(range(2007, 2026), (507, 593, 697, 924, 1129, 1299, 1062, 953, 1046, 1130, 1113, 1074, 1244, 1550, 1521, 1709, 1795, 2204, 3037))]
GOLD_EUR += [(M(2025, 12, 18), 3833), (M(2026, 1, 28), 4668), (M(2026, 11, 10), 3608)]
def g_at(d):
    for (d0, v0), (d1, v1) in zip(GOLD_EUR, GOLD_EUR[1:]):
        if d0 <= d <= d1: return v0+(v1-v0)*(d-d0)/(d1-d0)
    return GOLD_EUR[-1][1]
D0, D1 = M(2006, 11)-.2, M(2026, 11, 10)+.25
def curve_glass(cv, t, t0, a=1.0, full=False, rec=None):
    k = t-t0
    if k <= 0 or a <= 0: return
    T = S.text
    def d(kk, w, h):
        x0, x1, yb, yt = 100, w-50, h-70, 60
        X = lambda dd: x0+(dd-D0)/(D1-D0)*(x1-x0); Y = lambda v: yb-v/5000*(yb-yt)
        for v in (1000, 2000, 3000, 4000, 5000):
            kk.move_to(x0, Y(v)); kk.line_to(x1, Y(v)); kk.set_line_width(1); col(kk, S.WHITE, .1); kk.stroke(); T(kk, f"{v//1000}{NB}000{NB}€", x0-12, Y(v), 'sb', 18, S.ICE, 'r', .5)
        for yr in range(2008, 2027, 3): T(kk, str(yr), X(yr), yb+30, 'sb', 19, S.ICE, 'c', .6)
        dend = D1-.25 if full else D0+.2+(D1-.45-D0)*inout((t-t0-.3)/3.6)
        pts = [(X(dd), Y(v)) for dd, v in GOLD_EUR if dd <= dend]+[(X(dend), Y(g_at(dend)))]
        UP, DN = (1, .82, .30), (1, .30, .37)
        segs = [(p0, p1, UP if p1[1] <= p0[1] else DN) for p0, p1 in zip(pts, pts[1:])]
        for (p0, p1, cl) in segs:
            e_ = 1.2; kk.move_to(p0[0]-e_, yb); kk.line_to(p0[0]-e_, p0[1]); kk.line_to(p1[0]+e_, p1[1]); kk.line_to(p1[0]+e_, yb); kk.close_path()
            g = cairo.LinearGradient(0, yt, 0, yb); g.add_color_stop_rgba(0, *cl, .38); g.add_color_stop_rgba(1, *cl, 0); kk.set_source(g); kk.fill()
        kk.set_line_cap(cairo.LINE_CAP_ROUND)
        for wdt, al in ((16, .2), (6, 1.0)):
            for (p0, p1, cl) in segs: kk.move_to(*p0); kk.line_to(*p1); kk.set_line_width(wdt); kk.set_source_rgba(*cl, al); kk.stroke()
        def mark(dd, v, big, small, colr, dy, tt, xo=0):
            if dend < dd-.01 or t < tt: return
            x, y = X(dd), Y(v); u = ent(t-tt, .3)
            kk.arc(x, y, 10*u, 0, 2*math.pi); col(kk, colr); kk.fill_preserve(); kk.set_line_width(3); col(kk, S.WHITE, u); kk.stroke()
            T(kk, big, x+xo, y+dy, 'a', 40, colr, 'c', u); T(kk, small, x+xo, y+dy+(30 if dy > 0 else -32), 'sb', 20, S.ICE, 'c', .8*u)
        mark(M(2006, 11), 486, f"486{NB}€", "nov. 2006", S.GD, -44, t0+.4, 50)
        if rec is None: mark(M(2026, 11, 10), 3608, f"3{NB}608{NB}€", "10 nov. 2026", S.GD, 70, t0+3.9, -70)
        else:
            mark(M(2026, 1, 28), 4668, f"4{NB}668{NB}€", "record, 28 janv. 2026", S.GD, -44, rec, -150)
            mark(M(2026, 11, 10), 3608, f"3{NB}608{NB}€", "10 nov. 2026", S.RD, 70, rec+.4, -70)
    S.tp(cv, 900, 560, d, 540, 665+40*(1-ent(k, .45))+(1-a)*-60, 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30) if a >= 1 else _fade_tp(cv, d, a, k)
def _fade_tp(cv, d, a, k):
    tmp = cv.copy(); S.tp(tmp, 900, 560, d, 540, 665, 'or', rx=.05, bev=30); cv.paste(Image.blend(cv.convert('RGBA'), tmp.convert('RGBA'), a))
def bars2_glass(cv, t, t0):
    k = t-t0
    def d(kk, w, h):
        base = h-120; top = 110; mx = 7.0
        for i, (lab, v, colr, tt) in enumerate((("OR", 1.3, S.GD, 62.75), ("ACTIONS", 6.6, S.GR, 65.2))):
            x = w*(.3+.4*i); u = inout((t-tt)/.9)
            bh = (base-top)*v/mx*u; kk.rectangle(x-80, base-bh, 160, bh)
            g = cairo.LinearGradient(0, base-bh, 0, base); r_, g_, b_ = rgb(colr)[:3]; g.add_color_stop_rgba(0, r_, g_, b_, .95); g.add_color_stop_rgba(1, r_, g_, b_, .45); kk.set_source(g); kk.fill()
            S.text(kk, lab, x, base+44, 'xb', 36, S.WHITE, 'c', ent(t-t0-.2, .3))
            if u > 0: S.text(kk, f"{v*u:.1f}".replace('.', ',')+f"{NB}%", x, base-bh-34, 'a', 52, colr, 'c', ent(t-tt, .25))
        kk.move_to(60, base); kk.line_to(w-60, base); kk.set_line_width(2); col(kk, S.WHITE, .5); kk.stroke()
        S.text(kk, "par an, après inflation", w/2, h-28, 'sb', 30, S.ICE, 'c', .8*ent(t-t0-.4, .3))
        S.text(kk, "1900-2025 (actions américaines)", w/2, 44, 'sb', 28, S.ICE, 'c', .8*ent(t-t0-.6, .3))
    S.tp(cv, 860, 600, d, 540, 650+40*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def b_chiffres(cv, c, t, k):
    title(c, "EN 20 ANS", t, 54.3, 250, 76, t1=59.55)
    if t < 59.9:
        a = 1-ent(t-59.55, .3) if t > 59.55 else 1
        curve_glass(cv, t, 54.45, a=a)
        if t > 59.0: pop_text(c, f"× 7,4", 820, 360, 80, t, 59.05, YEL, rot=-.05, a=a)
    else:
        title(c, "SUR UN SIÈCLE", t, 59.9, 250, 72, t1=66.55)
        if t < 66.85: bars2_glass(cv, t, 60.0) if t < 66.55 else _fade_bars(cv, t)
def _fade_bars(cv, t):
    tmp = cv.copy(); bars2_glass(tmp, t, 60.0); cv.paste(Image.blend(cv.convert('RGBA'), tmp.convert('RGBA'), 1-ent(t-66.55, .3)))
# ================= 8. et demain ? (comptoir) =================
def b_demain(cv, c, t, k):
    title(c, "ET DEMAIN ?", t, 66.95, 250, 76, t1=72.9)
    fb = 1-ent(t-74.95, .3) if t > 74.95 else 1
    if t > 67.3 and t < 75.3:
        prop(c, 'boule_cristal', 540, 650, h=560, k=t-67.35, a=fb)
        if t > 69.7: pop_text(c, f"4{NB}800{NB}€", 540, 545, 58, t, 69.75, BROWN if False else YEL, a=fb)
        if t > 70.15: paint(c, "à", 540, 610, 34, a=ent(t-70.15, .2)*fb)
        if t > 70.6: pop_text(c, f"5{NB}600{NB}€", 540, 675, 58, t, 70.65, YEL, a=fb)
        if t > 71.9: paint(c, "l'once, fin 2027", 540, 960, 34, a=ent(t-71.95, .3)*fb, fam='Limelight')
        if t > 72.2: paint(c, "objectifs de Goldman Sachs et J.P. Morgan", 540, 345, 26, a=ent(t-72.25, .3)*fb*(1-ent(t-72.9, .3)), fam='Limelight')
    title(c, "DES PRÉVISIONS,", t, 73.05, 240, 62, t1=75.0)
    title(c, "PAS DES PROMESSES", t, 74.15, 320, 62, PINK, t1=75.0)
    if t > 75.15:
        title(c, "DEPUIS LE RECORD", t, 75.2, 250, 70)
        curve_glass(cv, t, 75.2, full=True, rec=75.9)
        if t > 76.0: pop_text(c, f"−23{NB}%", 830, 360, 84, t, 76.05, PINK, rot=-.05)
# ================= 9. question (hangar) =================
def b_fin(cv, c, t, k):
    title(c, "VALEUR REFUGE", t, 78.6, 250, 68, YEL)
    if t > 80.35: pop_text(c, "OU", 540, 335, 44, t, 80.4)
    title(c, "PLACEMENT QUI DORT ?", t, 80.65, 420, 62, CREAM)
    if t > 80.9:
        prop(c, 'lingot_dort', 720, 1335, w=330, k=t-80.95, rot=.02*math.sin(t*1.3))
        for i in range(3):                                                   # « z z z » qui montent
            kk = (t-81.2-i*.45) % 1.35
            if t > 81.2+i*.45: paint(c, "z", 840+kk*40, 1210-kk*120, 30+i*8, a=clamp(1-kk/1.35)*clamp(kk*4))
    if t > 82.0: paint(c, "Dis-le en commentaire", 540, 960, 36, a=ent(t-82.05, .3))
SC = [(0.0, 7.95, b_cube, 'hangar_cube'), (7.95, 13.5, b_globe, 'globe'), (13.5, 21.65, b_cresus, 'lydie'), (21.65, 33.7, b_mine, 'mine'),
      (33.7, 44.6, b_reserves, 'reserves'), (44.6, 54.15, b_pari, 'comptoir'), (54.15, 66.8, b_chiffres, 'comptoir'), (66.8, 78.35, b_demain, 'comptoir'),
      (78.35, DUR, b_fin, 'hangar_cube')]
BLOCS = []
for (a, b, f, d) in SC:
    if BLOCS and BLOCS[-1][2] == d and abs(BLOCS[-1][1]-a) < 1e-6: BLOCS[-1] = (BLOCS[-1][0], b, d)
    else: BLOCS.append((a, b, d))
IRIS = [7.95, 21.65, 33.7, 44.6, 78.35]; IR = .42
ZT, ZD = 13.5, .55                                                           # travelling dans le globe (Varna) puis ouverture sur la Lydie
def zoomed(img, s, cx, cy, flash):
    M_ = np.float32([[s, 0, cx-s*cx], [0, s, cy-s*cy]]); out = cv2.warpAffine(img, M_, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out*(1-flash)+np.array([255, 236, 170], np.float32)*flash
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    if ZT-ZD <= t < ZT:                                                      # on plonge dans le point de Varna
        u = ((t-(ZT-ZD))/ZD)**2; arr = zoomed(arr, 1+7*u, VARNA[0], VARNA[1], .85*u)
    elif ZT <= t < ZT+ZD:                                                    # la Lydie apparaît en reculant
        u = 1-ease((t-ZT)/ZD); arr = zoomed(arr, 1+.9*u, 540, 700, .85*u)
    arr = dos_col(arr, t) if DOS[0] <= t < DOS[1] else coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    if t > 82.1: S.put_emoji(out, '👇', 860, int(960+8*math.sin(t*5)), 46)
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
    ev = [e for e in V.events() if not (DOS[0]-.1 <= e[0] < DOS[1])] + [(ta-IR, 'whoosh') for ta in IRIS] + [(ZT-ZD, 'riser'), (ZT, 'glint')]
    ev += [(.05, 'thud'), (1.95, 'pop'), (3.4, 'swish'), (3.9, 'impact'), (4.3, 'pop'), (5.4, 'glint'),
           (8.1, 'thud'), (8.8, 'pop'), (10.95, 'tick'), (11.2, 'pop'), (12.45, 'impact'),
           (13.65, 'thud'), (14.35, 'glint'), (16.15, 'tadaa'), (20.3, 'impact'),
           (21.8, 'thud'), (21.85, 'glint'), (22.2, 'pop'), (24.65, 'impact'), (26.4, 'impact'), (27.7, 'pop'), (28.5, 'swish'), (28.9, 'glint'),
           (29.95, 'swish'), (31.0, 'fill1'), (32.4, 'impact'),
           (33.85, 'thud'), (34.0, 'swish'), (35.0, 'fill2'), (37.9, 'pop'), (38.1, 'pop'), (38.4, 'glint'), (41.55, 'thud'), (43.15, 'impact'),
           (45.9, 'glint'), (46.75, 'pop'), (47.15, 'bonk'), (47.55, 'pop'), (47.95, 'bonk'), (48.9, 'thud'), (50.95, 'impact'), (52.95, 'swish'), (53.3, 'pop'),
           (54.3, 'thud'), (54.45, 'swish'), (54.8, 'fill1'), (59.05, 'impact'), (59.9, 'thud'), (60.0, 'swish'), (62.75, 'fill1'), (65.2, 'fill2'),
           (66.95, 'thud'), (67.35, 'glint'), (69.75, 'pop'), (70.65, 'pop'), (73.05, 'thud'), (74.15, 'bonk'), (75.2, 'swish'), (76.05, 'crash'),
           (78.6, 'thud'), (80.4, 'pop'), (80.65, 'thud'), (80.95, 'pop')]
    ev += [(19.3+d0+.9, 'coin') for (x, d0, sz, sp) in RAIN[::4]] + [(35.0+.3*i, 'tick') for i in range(6)]
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
