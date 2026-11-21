"""Buy, borrow, die (21/11/2026), cartoon 1930 en Technicolor : décors Gemini (manoir, salle des coffres, hall de banque, notaire, hémicycle,
petit salon, salle de bourse sous l'orage), accessoires Gemini détourés, panneaux de verre, Mister Coin en couleurs, pellicule, fondus aux changements de décor.
usage : python3 video_col.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
import veo_coin as VC
from scenes import surface, to_img, rr, col, W, H, clamp, ease, rgb, NB
FPS = 60; DUR = V.DUR; DUR_TOTAL = V.DUR; VOICE = V.VOICE; sh = V.sh
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
        if name in LETTERBOX:                                                          # décor sorti en paysage (bandes floues) : provisoire, recadré
            y0, y1, xc = LETTERBOX[name]; f = f[y0:y1]; w = int((y1-y0)*9/16); f = f[:, xc-w//2:xc+w//2]
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    g = g+.2*(g-cv2.GaussianBlur(g, (0, 0), 1.0))                               # légère accentuation (décors déjà agrandis par Real-ESRGAN)
    return np.clip((g-128)*1.06+130, 0, 255)
@functools.lru_cache(maxsize=1)
def _newsmask():
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (0, 760), (320, 1920), 1, -1); return cv2.GaussianBlur(m, (0, 0), 30)
MCX = []
def mcx(t): return [x for (a, x) in MCX if t >= a][-1]
def feet(t):
    return V.FEET
_RXC = {}
def _rx_layer(t, X, Y):
    """réaction muette (V.RX) : images f0 à f1 du clip étirées sur la fenêtre du silence ; None hors fenêtre"""
    for (t0, clip, f0, f1), t1 in zip(V.RX, V.RX_FIN):
        if t0 <= t < t1:
            if clip not in _RXC: _RXC[clip] = VC.VeoCoin([(0.0, clip, 'une')], x=540, pieds=V.FEET, largeur_piece=170)
            fr = f0+(f1-f0)*(t-t0)/(t1-t0); return _RXC[clip].layer((fr+.5)/24, X, Y)
    return None
def coin_col(cv_rgb, t):
    F = feet(t); r = _rx_layer(t, mcx(t), F)
    if r is None: Y = F+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, mcx(t), Y)
    else: Y = F; rgb_, al = r
    fx = V.MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), F-3), (95, 15), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
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
def paint(c, s_, x, y, size, fill=CREAM, a=1.0, align='c', rot=0.0, fam='Inter Display'):
    """lettres peintes : crème/or, contour brun chaud, ombre portée"""
    if a <= 0: return
    c.save(); c.select_font_face(fam, 0, 1); c.set_font_size(size); e = c.text_extents(s_)
    xx = -e.x_advance/2 if align == 'c' else (-e.x_advance if align == 'r' else 0)
    c.translate(x, y); c.rotate(rot); c.translate(xx, size*.35); ol = max(3, size*.09)
    c.move_to(ol*.6, ol*.9); c.text_path(s_); c.set_source_rgba(0, 0, 0, .5*a); c.fill()
    c.move_to(0, 0); c.text_path(s_); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(ol*2); col(c, BROWN, a); c.stroke_preserve(); col(c, fill, a); c.fill()
    c.restore()
def fit(c, s_, size, maxw, fam='Inter Display'):
    c.save(); c.select_font_face(fam, 0, 1); c.set_font_size(size); w = c.text_extents(s_).x_advance; c.restore()
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
YEL = 'FFE27A'; PINK = 'FF8A8A'; MINT = '9DF2B5'; WHITE = 'FFFFFF'
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
    c.select_font_face('Inter Display', 0, 1); c.set_font_size(size); e = c.text_extents(s_)
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

_CV = None; _T = 0.0                                          # image du décor en cours et temps (posés par raw) : les plaques de verre s'y dessinent sous les textes
_PC = {}
def plate(c, x, y, w, h, a, mood='or'):
    """plaque de verre 3D (scenes.tp, notre signature) derrière un texte, apparition et disparition en fondu.
    Le verre est recalculé 12 fois par seconde (assez pour le décor flouté derrière) et posé avec son masque : rendu 4 à 5 fois plus rapide."""
    if a <= 0 or _CV is None: return
    key = (int(x), int(y), int(w), int(h), mood); b = int(_T*12)
    hit = _PC.get(key)
    if hit is None or hit[0] != b:
        P = 260; x0, y0 = max(0, int(x-w/2-P)), max(0, int(y-h/2-P)); x1, y1 = min(W, int(x+w/2+P)), min(H, int(y+h/2+P))
        tmp = _CV.copy(); S.tp(tmp, w, h, lambda kk, ww, hh: None, x, y, mood, rx=.03, bev=int(max(12, min(26, h*.3))))
        o = np.asarray(_CV.convert('RGB').crop((x0, y0, x1, y1))).astype(np.int16); n_ = tmp.convert('RGB').crop((x0, y0, x1, y1))
        m = (np.abs(np.asarray(n_).astype(np.int16)-o).max(2) > 2).astype(np.uint8)*255
        m = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5), np.uint8)), (0, 0), 1.5)
        patch = n_.convert('RGBA'); patch.putalpha(Image.fromarray(m)); hit = (b, patch, (x0, y0)); _PC[key] = hit
        if len(_PC) > 40: _PC.clear(); _PC[key] = hit
    patch, pos = hit[1], hit[2]
    if a < .999: patch = patch.copy(); patch.putalpha(Image.fromarray((np.asarray(patch.getchannel('A')).astype(np.float32)*a).astype(np.uint8)))
    _CV.alpha_composite(patch, pos)
# ================= panneaux de verre (compteurs, jauges) =================
def glass_counter(cv, t, t0, v1, t_a, t_b, sub, cy=780, w=860, h=230, colr=None, a=1.0, t1=None):
    k = t-t0
    if k <= 0: return
    if t1 and t > t1-.3:
        return _fade(cv, lambda x: glass_counter(x, t, t0, v1, t_a, t_b, sub, cy, w, h, colr, a), 1-ent(t-(t1-.3), .3))
    def d(kk, ww, hh):
        v = v1*inout((t-t_a)/max(.01, t_b-t_a))
        S.text(kk, euro(v), ww/2, hh/2-14, 'a', 92, colr or S.GD, 'c', ent(k, .3))
        S.text(kk, sub, ww/2, hh-36, 'sb', 34, S.ICE, 'c', .9*ent(k-.3, .3))
    S.tp(cv, w, h, d, 540, cy+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=26)
def glass_bar(cv, t, t0, parts, cy=700, w=920, h=400, note=None, t1=None, head=None):
    """apparition en fondu sur 0,35 s, disparition en fondu sur 0,3 s avant t1"""
    a = ent(t-t0, .35)*(1-ent(t-(t1-.3), .3) if t1 else 1)
    if t-t0 <= 0 or a <= 0: return
    if a < .999: return _fade(cv, lambda x: _glass_bar(x, t, t0, parts, cy, w, h, note, head), a)
    _glass_bar(cv, t, t0, parts, cy, w, h, note, head)
def _glass_bar(cv, t, t0, parts, cy=700, w=920, h=400, note=None, head=None):
    """barre empilée : parts = [(fraction, couleur haute, couleur basse, texte haut, sous-texte, t_apparition, côté)]"""
    k = t-t0
    if k <= 0: return
    def d(kk, ww, hh):
        x0, x1 = 70, ww-70; y = 150+(50 if head else 0); bh = 130; L = x1-x0; x = x0
        if head and t > head[1]: S.text(kk, head[0], ww/2, 62, 'a', 54, S.GD, 'c', ent(t-head[1], .3))
        for (fr, c0, c1, lab, sub, ta, side) in parts:
            u = inout((t-ta)/1.0); bw = L*fr*u
            if bw > 2:
                rr(kk, x+(6 if x > x0 else 0), y, bw-(6 if x > x0 else 0), bh, 14); g = cairo.LinearGradient(0, y, 0, y+bh)
                for st, cc in ((0, c0), (1, c1)): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .96)
                kk.set_source(g); kk.fill()
            if t > ta:
                tx = x0+8 if side == 'l' else x1-8
                S.text(kk, lab, tx, y-46, 'a', 50, c0, side, ent(t-ta-.1, .3)); S.text(kk, sub, tx, y+bh+44, 'sb', 34, S.ICE, side, .9*ent(t-ta-.2, .3))
            x += L*fr
        if note: S.text(kk, note, ww/2, hh-24, 'sb', 28, S.ICE, 'c', .8*ent(k-.6, .3))
    S.tp(cv, w, h, d, 540, cy+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
LETTERBOX = {}                                # décors sortis en paysage à recadrer (aucun : le notaire a été refait en 9:16)
GOLDC = ('FFE27A', 'B97A12'); REDC = ('FFFFFF', 'BDB6C8');   # pas de rouge dans le verre (21/11) : blanc
MINTC = ('9DF2B5', '2E8B57'); GREYC = ('C9C2D6', '6E6680')
def num(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',').replace(' ', NB)
def glass_value(cv, t, t0, v1, t_a, t_b, fmt, sub, cy=700, w=860, h=220, colr=None, t1=None, head=None):
    """compteur en verre épais : la valeur monte de 0 à v1 entre t_a et t_b ; fmt(v) -> texte"""
    k = t-t0
    if k <= 0: return
    if t1 and t > t1-.3:
        return _fade(cv, lambda x: glass_value(x, t, t0, v1, t_a, t_b, fmt, sub, cy, w, h, colr, None, head), 1-ent(t-(t1-.3), .3))
    def d(kk, ww, hh):
        v = v1*inout((t-t_a)/max(.01, t_b-t_a)); y0 = 0
        if head: S.text(kk, head, ww/2, 42, 'xb', 28, S.ICE, 'c', .9*ent(k, .3), 2); y0 = 22
        S.text(kk, fmt(v), ww/2, hh/2-14+y0, 'a', 88, colr or S.GD, 'c', ent(k, .3))
        S.text(kk, sub, ww/2, hh-34, 'sb', 32, S.ICE, 'c', .9*ent(k-.3, .3))
    S.tp(cv, w, h, d, 540, cy+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=26)
def glass_card(cv, t, t0, draw, cy=600, w=900, h=300, mood='or', t1=None):
    k = t-t0
    if k <= 0: return
    a = ent(k, .35)*(1-ent(t-(t1-.3), .3) if t1 else 1)
    if a <= 0: return
    f = lambda x: S.tp(x, w, h, draw, 540, cy+30*(1-ent(k, .45)), mood, rx=round(.05+.25*(1-ent(k, .45)), 3), bev=26)
    if a < .999: return _fade(cv, f, a)
    f(cv)
def stamp(c, s_, x, y, size, t, t0, colr='D7262B', rot=-.12, a=1.0):
    """tampon encré : cadre et lettres rouges, arrive en écrasant (grand puis taille normale)"""
    k = t-t0
    if k <= 0 or a <= 0: return
    sc = 1+1.2*(1-ent(k, .22)); al = a*ent(k, .12)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    c.select_font_face('Inter Display', 0, 1); c.set_font_size(size); e = c.text_extents(s_); pw, ph = e.x_advance+size*.7, size*1.45
    rr(c, -pw/2, -ph/2, pw, ph, size*.18); c.set_line_width(size*.11); col(c, colr, al); c.stroke()
    c.move_to(-e.x_advance/2, size*.36); c.text_path(s_); col(c, colr, al); c.fill(); c.restore()
def row(cv, c, t, t0, y, txt, colr=CREAM, emo=None, sub=None, a=1.0, size=48, w=980):
    """ligne d'information sur une pastille sombre (lisible sur un décor chargé), avec émoji à droite"""
    k = t-t0
    if k <= 0 or a <= 0: return
    al = ent(k, .25)*a; hh = 118 if sub else 96
    plate(c, 540, y, w, hh, al)
    pop_text(c, txt, 520 if emo else 540, y-(16 if sub else 0), size, t, t0, colr, a=a, maxw=w-(190 if emo else 90))
    if sub: paint(c, sub, 520 if emo else 540, y+34, 28, a=ent(k-.2, .3)*a)
    if emo and k > .15: EMO.append((emo, 540+w/2-62, y, 58, al))
EMO = []
def dissolve_bar(c, t, t0, x0, x1, y, h, lab, dur=1.2, a=1.0):
    """la barre « PLUS-VALUE » se désagrège de gauche à droite en poussière d'or qui s'envole (et scintille), au lieu d'un simple fondu"""
    cs = 12; nx, ny = int((x1-x0)/cs)+1, int(h/cs)+1; rng_ = np.random.default_rng(7); noise = rng_.random((nx, ny)); drift = rng_.random((nx, ny))
    keep = []
    for i in range(nx):
        for j in range(ny):
            d = (i/nx)*dur*.75+noise[i, j]*dur*.25; u = (t-t0-d)/.9
            cx_, cy_ = x0+i*cs, y-h/2+j*cs
            if u <= 0: keep.append((cx_, cy_))
            elif u < 1:
                px = cx_+140*u+25*math.sin(6*u+i); py = cy_-(120+160*drift[i, j])*u**1.2; r_ = cs*(1-.7*u)
                c.rectangle(px, py, r_, r_); c.set_source_rgba(1.0, .80+.12*drift[i, j], .35, a*(1-u)); c.fill()
                if drift[i, j] > .93: c.arc(px, py, 3+4*(1-u), 0, 2*math.pi); c.set_source_rgba(1, 1, .9, a*(1-u)); c.fill()
    if keep:
        c.save()
        for (cx_, cy_) in keep: c.rectangle(cx_, cy_, cs+.5, cs+.5)
        c.clip(); gold_bar(c, x0, x1, y, h, a, lab); c.restore()
def gold_bar(c, x0, x1, y, h, a, lab):
    rr(c, x0, y-h/2, x1-x0, h, 18); g = cairo.LinearGradient(0, y-h/2, 0, y+h/2)
    for st, cc in ((0, 'FFE27A'), (1, 'B97A12')): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, a)
    c.set_source(g); c.fill_preserve(); c.set_line_width(5); col(c, BROWN, a); c.stroke()
    paint(c, lab, (x0+x1)/2, y, 46, BROWN if False else CREAM, a=a)

# ================= 1. accroche, le chiffre, les trois mots (salon du manoir) =================
def b_manoir(cv, c, t, k):
    if t < 4.5:
        a = 1-ent(t-4.25, .25) if t > 4.25 else 1
        plate(c, 540, 380, 1010, 380, a)
        title(c, "VIVRE COMME UN", t, -.5, 260, 64, CREAM, t1=4.25)
        title(c, "MILLIARDAIRE", t, -.5, 370, 104, YEL, t1=4.25)
        title(c, "SANS PRESQUE PAYER D'IMPÔT ?", t, -.5, 490, 58, WHITE, t1=4.25)
        if t > .8: EMO.append(('🤔', 930, 230, 70, a*ent(t-.8, .3)))
    elif t < V.T['trois']:
        t9 = sh(18.1)
        a = 1-ent(t-(V.T['trois']-.3), .25)
        title(c, "LES 25 AMÉRICAINS", t, 4.7, 250, 72, CREAM, t1=V.T['trois']-.3)
        title(c, "LES PLUS RICHES", t, 5.1, 340, 72, YEL, t1=V.T['trois']-.3)
        if t > 5.7: plate(c, 540, 430, 720, 62, ent(t-5.7, .25)*a); paint(c, "2014-2018 · enquête ProPublica (2021)", 540, 430, 32, a=ent(t-5.7, .3)*a)
        if t < t9+.3:
            glass_bar(cv, t, 8.1, [(1-12.4/364.8, *GOLDC, f"+364,8{NB}Md€", "de fortune en plus", 9.7, 'l'),
                                   (12.4/364.8, *REDC, f"12,4{NB}Md€", "d'impôt sur le revenu", 16.45, 'r')], cy=700, h=360, t1=t9+.3)
        if t > t9:
            if t > t9+.3: plate(c, 540, 650, 760, 290, ent(t-t9-.3, .2)*a)
            pop_text(c, "VRAI TAUX D'IMPOSITION", 540, 565, 46, t, t9+.35, CREAM, a=a)
            pop_text(c, f"3,4{NB}%", 540, 690, 150, t, t9+.5, WHITE, rot=-.04, a=a)
    else:
        title(c, "LEUR MÉTHODE", t, V.T['trois']+.1, 250, 80, CREAM)
        for i, (w_, fr, ta) in enumerate((("BUY", "acheter", sh(22.9)), ("BORROW", "emprunter", sh(23.6)), ("DIE", "mourir", sh(24.41)))):
            y = 450+i*195
            if t > ta:
                plate(c, 540, y+10, 600, 140, ent(t-ta, .2)); pop_text(c, w_, 540, y-10, 92, t, ta, YEL, rot=(-.03, .02, -.02)[i])
                paint(c, fr, 540, y+58, 34, a=ent(t-ta-.15, .3))
# ================= 2. Buy (salle des coffres) =================
def b_coffres(cv, c, t, k):
    t0 = V.T['buy']
    title(c, "1. BUY", t, t0+.1, 250, 92, YEL)
    if t > t0+.5: plate(c, 540, 368, 720, 66, ent(t-t0-.5, .25)); paint(c, "acheter, et ne jamais vendre", 540, 368, 38, a=ent(t-t0-.5, .3))
    prop(c, 'certificat_action', 540, 600, w=480, k=t-(t0+.4), rot=-.04)
    prop(c, 'cadenas', 560, 630, h=240, k=t-sh(27.0), rot=.08+.03*math.sin(t*2))
    if t > sh(28.5): row(cv, c, t, sh(28.5), 850, f"PAS DE VENTE = 0{NB}€ D'IMPÔT", MINT, sub="sur la plus-value", w=860, size=46)
# ================= 3. Borrow et le cas réel (hall de banque) =================
def b_guichet(cv, c, t, k):
    t0 = V.T['borrow']; t1 = V.T['ellison']
    if t < t1:
        a = 1-ent(t-(t1-.25), .25) if t > t1-.25 else 1
        title(c, "2. BORROW", t, t0+.1, 250, 92, YEL, t1=t1-.25)
        if t > t0+.5: plate(c, 540, 368, 760, 66, ent(t-t0-.5, .25)*a); paint(c, "emprunter sur ses actions", 540, 368, 38, a=ent(t-t0-.5, .3)*a)
        prop(c, 'certificat_action', 265, 560, w=380, k=t-sh(31.6), rot=-.05, a=a)
        arrow(c, 470, 560, 610, 560, ent(t-sh(32.4), .4)*(a > .01))
        prop(c, 'billet', 815, 560, w=340, k=t-sh(32.9), rot=.06+.03*math.sin(t*2.4), a=a)
        if t > sh(32.9): paint(c, "un prêt", 815, 705, 36, a=ent(t-sh(33.0), .3)*a)
        if t > sh(34.6): row(cv, c, t, sh(34.6), 850, "UN PRÊT N'EST PAS UN REVENU", CREAM, sub="donc 0 € d'impôt", w=900, a=a)
    else:
        title(c, "EXEMPLE RÉEL", t, t1+.1, 250, 80, CREAM)
        tp_ = sh(37.3)
        polaroid(c, 280, 488, t, tp_, w=280)
        if t > tp_+.35:
            al = ent(t-tp_-.35, .3); plate(c, 740, 490, 440, 270, al)
            pop_text(c, "LARRY ELLISON", 740, 398, 46, t, tp_+.35, YEL, maxw=430)
            for i, l_ in enumerate(("cofondateur d'Oracle (1977)", "président du conseil", "et directeur technique", "né en 1944")):
                paint(c, l_, 740, 458+i*42, 28, a=ent(t-tp_-.6-i*.12, .3))
        tv = sh(43.6)
        glass_value(cv, t, sh(40.8), 413e6, sh(41.0), sh(42.6), lambda v: num(v), "actions Oracle en garantie de prêts", cy=830, w=860, h=180, t1=tv+.3)
        def d41(kk, ww, hh):
            S.text(kk, f"SOIT 41,5 MILLIARDS D'EUROS", ww/2, 70, 'a', 64, S.GD, 'c')
            S.text(kk, "36 % de ses actions · cours du 19/11/2026", ww/2, 132, 'sb', 28, S.ICE, 'c', .9)
            S.text(kk, "source : rapport d'Oracle du 25/09/2026", ww/2, 170, 'sb', 24, S.ICE, 'c', .7)
        glass_card(cv, t, tv+.35, d41, cy=830, w=900, h=190)                 # après la disparition complète du compteur : jamais de texte sur du texte
PHOTO = f'{D}/photos/ellison.jpg'
@functools.lru_cache(maxsize=1)
def _photo_surf(w, h):
    if os.path.exists(PHOTO):
        im = Image.open(PHOTO).convert('RGB'); k = max(w/im.width, h/im.height); im = im.resize((int(im.width*k)+1, int(im.height*k)+1), Image.LANCZOS)
        x0 = (im.width-w)//2; y0 = int((im.height-h)*.25); im = im.crop((x0, y0, x0+w, y0+h))
        a = np.asarray(im).astype(np.float32); g = a.mean(2, keepdims=True); a = a*.8+g*.2; a = a*np.array([1.04, 1.0, .9])     # léger virage chaud, façon tirage ancien
        rgba = np.dstack([np.clip(a, 0, 255), np.full((h, w, 1), 255.)]).astype(np.uint8)
    else:
        rgba = np.zeros((h, w, 4), np.uint8); rgba[..., :3] = (70, 62, 58); rgba[..., 3] = 255
    buf = np.ascontiguousarray(rgba[..., [2, 1, 0, 3]])
    return cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
def polaroid(c, x, y, t, t0, w=300, rot=-.07):
    """tirage instantané : cadre blanc cassé, marge large en bas, ombre portée ; arrive en rebond, légère oscillation"""
    k = t-t0
    if k <= 0: return
    pw, ph = w-36, int((w-36)*1.12); H_ = 18+ph+70; sc = back(k/.35)
    c.save(); c.translate(x, y); c.rotate(rot+.015*math.sin(t*1.3)); c.scale(sc, sc)
    rr(c, -w/2+8, -H_/2+12, w, H_, 6); c.set_source_rgba(0, 0, 0, .35); c.fill()
    rr(c, -w/2, -H_/2, w, H_, 6); col(c, 'F7F3EA'); c.fill_preserve(); c.set_line_width(2); col(c, 'C9BFA8'); c.stroke()
    c.set_source_surface(_photo_surf(pw, ph), -pw/2, -H_/2+18); c.paint()
    if not os.path.exists(PHOTO): paint(c, "PHOTO", 0, -H_/2+18+ph/2, 40, a=.6)
    c.select_font_face('Rye', 0, 0); c.set_font_size(30); e = c.text_extents("Larry Ellison")
    c.move_to(-e.x_advance/2, H_/2-26); c.text_path("Larry Ellison"); col(c, '3B2412', .85); c.fill()
    c.restore()
# ================= 4. Die (bureau du notaire) =================
def b_notaire(cv, c, t, k):
    t0 = V.T['die']; tE = sh(51.48); tS = sh(53.0)
    title(c, "3. DIE", t, t0+.1, 250, 92, YEL)
    if t < tS:
        a = 1-ent(t-(tS-.3), .3) if t > tS-.3 else 1
        if t > t0+.5: plate(c, 540, 368, 600, 66, ent(t-t0-.5, .25)*a); paint(c, "au décès", 540, 368, 38, a=ent(t-t0-.5, .3)*a)
        prop(c, 'testament', 540, 560, h=320, k=t-(t0+.6), rot=-.04+.02*math.sin(t*1.6), a=a)
        if t > sh(50.3): row(cv, c, t, sh(50.3), 765, "LES ACTIONS À LEUR VALEUR DU JOUR", CREAM, w=960, size=40, a=a)
        if t > tE:
            if t < tE+.7: gold_bar(c, 200, 880, 905, 92, a*ent(t-tE, .2), "PLUS-VALUE")
            else: dissolve_bar(c, t, tE+.7, 200, 880, 905, 92, "PLUS-VALUE", a=a)
            stamp(c, "EFFACÉE", 540, 905, 70, t, tE+1.9, a=a)
    else:
        def d(kk, ww, hh):
            S.text(kk, "DROITS DE SUCCESSION (ÉTATS-UNIS)", ww/2, 48, 'xb', 30, S.ICE, 'c', .9, 2)
            if t > sh(54.9): S.text(kk, f"40{NB}%", ww/2, 160, 'a', 120, WHITE, 'c', ent(t-sh(54.9), .3))
            if t > sh(55.6): S.text(kk, f"au-delà de 13,6{NB}M€ par personne", ww/2, 265, 'sb', 34, S.ICE, 'c', .9*ent(t-sh(55.6), .3))
        glass_card(cv, t, tS+.1, d, cy=620, w=880, h=320, mood='orange')
# ================= 5. En France (hémicycle) =================
def b_hemicycle(cv, c, t, k):
    t0 = V.T['france']; tz = sh(66.3)
    if t < tz:
        a = 1-ent(t-(tz-.3), .3) if t > tz-.3 else 1
        title(c, "ET EN FRANCE ?", t, t0+.1, 250, 84, CREAM, t1=tz-.3)
        row(cv, c, t, sh(59.4), 450, "LE CRÉDIT LOMBARD EXISTE", CREAM, emo='✅', a=a, size=44)
        row(cv, c, t, sh(61.2), 620, "PLUS-VALUE EFFACÉE AU DÉCÈS", CREAM, emo='✅', a=a, size=44)
        row(cv, c, t, sh(63.3), 805, f"DROITS DE SUCCESSION : JUSQU'À 45{NB}%", WHITE, sub="après 100 000 € d'abattement par enfant", a=a, size=42)
    else:
        title(c, "16 OCTOBRE 2026", t, tz+.1, 250, 80, CREAM)
        if t > tz+.4: plate(c, 540, 365, 760, 62, ent(t-tz-.4, .25)); paint(c, "Assemblée nationale, budget 2027", 540, 365, 34, a=ent(t-tz-.4, .3))
        board(c, 540, 560, 540, t-sh(68.4), lines=(("TAXE ZUCMAN", 150, BROWN),))
        stamp(c, "REJETÉE", 540, 775, 60, t, sh(69.3), rot=-.08)
        if t > sh(70.15): row(cv, c, t, sh(70.15), 892, f"2{NB}% PAR AN AU-DELÀ DE 100{NB}M€", YEL, sub="de patrimoine (impôt minimum proposé)", w=900, size=46)
# ================= 6. À ton échelle (petit salon) =================
def b_salon(cv, c, t, k):
    t0 = V.T['pea']; tc = sh(84.7)
    title(c, "À TON ÉCHELLE", t, t0+.1, 250, 84, MINT)
    if t < sh(76.3):
        if t > sh(74.6): plate(c, 540, 368, 700, 66, ent(t-sh(74.6), .25)*(1-ent(t-(sh(76.3)-.25), .25))); paint(c, "ne pas vendre compte aussi", 540, 368, 38, a=ent(t-sh(74.6), .3)*(1-ent(t-(sh(76.3)-.25), .25)))
    else:
        title(c, "PEA DE PLUS DE 5 ANS", t, sh(76.4), 350, 56, YEL)
    if t < tc+.3:
        a = 1-ent(t-tc, .3) if t > tc else 1
        if t > sh(78.4): row(cv, c, t, sh(78.4), 450, f"0{NB}€ D'IMPÔT SUR LE REVENU", MINT, emo='✅', w=900, size=44, a=a)
        glass_bar(cv, t, sh(80.2), [(.814, *MINTC, f"81,40{NB}€", "pour toi", sh(80.5), 'l'),
                                    (.186, *REDC, f"18,60{NB}€", "prélèvements sociaux", sh(80.8), 'r')], cy=748, h=376, t1=tc+.3, head=(f"SUR 100{NB}€ DE GAINS RETIRÉS", sh(79.9)))
    if t > tc:
        pop_text(c, "TON CAPITAL", 540, 520, 64, t, tc+.3, CREAM)
        pop_text(c, "CONTINUE DE COMPOSER", 540, 610, 64, t, tc+.6, YEL, rot=-.02)
        twinkle(c, t, [(380, 760), (690, 720), (560, 860), (300, 900), (780, 880)], 24)
# ================= 7. Le risque (salle de bourse sous l'orage) =================
def b_krach(cv, c, t, k):
    t0 = V.T['risque']; tg = sh(92.0)
    title(c, "ATTENTION", t, t0+.1, 250, 92, PINK)
    if t > t0+.5: plate(c, 540, 368, 780, 66, ent(t-t0-.5, .25)); paint(c, "emprunter sur ses actions", 540, 368, 38, a=ent(t-t0-.5, .3))
    if t > sh(89.9): row(cv, c, t, sh(89.9), 480, "SI ELLES CHUTENT, LA BANQUE PEUT VENDRE", CREAM, w=1000, size=38)
    if t > tg:
        def d(kk, ww, hh):
            S.text(kk, "ACTION ORACLE", ww/2, 44, 'xb', 30, S.ICE, 'c', .9, 3)
            x0, x1 = 60, ww-60; L = x1-x0
            for i, (lab, val, fr, cc, ta) in enumerate((("plus haut sur 12 mois", f"250,25{NB}$", 1.0, GOLDC, tg+.3), ("19/11/2026", f"110,57{NB}$", 110.57/250.25, REDC, tg+1.1))):
                y = 120+i*120; u = inout((t-ta)/.9)
                if t > ta:
                    S.text(kk, lab, x0, y-30, 'sb', 28, S.ICE, 'l', .9*ent(t-ta, .3))
                    bw = L*.62*fr*u
                    if bw > 2:
                        rr(kk, x0, y-4, bw, 56, 12); g = cairo.LinearGradient(0, y-4, 0, y+52)
                        for st, cc_ in ((0, cc[0]), (1, cc[1])): r_, g_, b_ = rgb(cc_)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .96)
                        kk.set_source(g); kk.fill()
                    S.text(kk, val, x0+bw+20, y+24, 'a', 46, cc[0], 'l', ent(t-ta-.5, .3))
            if t > tg+2.0: S.text(kk, f"−55,8{NB}%", x1, hh-52, 'a', 66, WHITE, 'r', ent(t-tg-2.0, .3))
        glass_card(cv, t, tg, d, cy=760, w=920, h=320, mood='orange')
# ================= 8. Question finale (salon du manoir) =================
def b_fin(cv, c, t, k):
    t0 = V.T['fin']
    plate(c, 540, 385, 1010, 300, ent(t-t0-.1, .25))
    title(c, "MAINTENANT QUE TU SAIS TOUT,", t, t0+.15, 280, 50, CREAM)
    title(c, "QU'EST-CE QUE TU PENSES", t, sh(99.2), 390, 66, YEL)
    title(c, "DE TOUT ÇA ?", t, sh(99.9), 480, 76, YEL)
    if t > sh(100.5): plate(c, 540, 660, 640, 92, ent(t-sh(100.5), .3)); paint(c, "Dis-le en commentaire", 500, 660, 46, a=ent(t-sh(100.5), .3)); EMO.append(('👇', 835, 660+8*math.sin(t*5), 56, ent(t-sh(100.5), .3)))
    if t > t0+.6:
        a = ent(t-t0-.6, .4); plate(c, 540, 878, 1030, 110, a*.9)
        paint(c, "Contenu pédagogique, ni conseil fiscal ni conseil en investissement.", 540, 858, 26, a=a)
        paint(c, "Montants au taux BCE du 19/11/2026 · sources en commentaire", 540, 900, 26, a=a)
T_ = V.T
SC = [(0.0, T_['buy'], b_manoir, 'manoir'), (T_['buy'], T_['borrow'], b_coffres, 'coffres'), (T_['borrow'], T_['die'], b_guichet, 'guichet'),
      (T_['die'], T_['france'], b_notaire, 'notaire'), (T_['france'], T_['pea'], b_hemicycle, 'hemicycle'), (T_['pea'], T_['risque'], b_salon, 'salon'),
      (T_['risque'], T_['fin'], b_krach, 'krach'), (T_['fin'], DUR, b_fin, 'manoir')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
BLOCS_MIX = BLOCS
IRIS = [s_[0] for s_ in SC[1:]]
MCX = [(0, 540), (T_['pea'], 230), (T_['risque'], 540)]
def raw(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    global _CV, _T
    s, c = surface(); EMO.clear(); _CV = cv; _T = t; f(cv, c, t, max(0.0, t-a)); _CV = None; cv.alpha_composite(to_img(s))
    for (ch, x, y, sz, al) in EMO:
        if al > .01:
            e = S.emoji(ch, int(sz)).copy()
            if al < .999: e.putalpha(Image.fromarray((np.asarray(e.getchannel('A')).astype(np.float32)*al).astype(np.uint8)))
            cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    return np.asarray(out.convert('RGB')).astype(np.float32)
XF = .3                                                       # fondu enchaîné aux changements de décor
def frame(t):
    for ta in IRIS:
        if ta-XF/2 <= t < ta+XF/2:
            k = inout((t-(ta-XF/2))/XF); arr = raw(min(t, ta-1/FPS))*(1-k)+raw(max(t, ta))*k; break
    else: arr = raw(t)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else 'FF8A8A', a=al, y=1060); return
def events():
    ev = [e for e in V.events()] + [(ta-XF/2, 'whoosh') for ta in IRIS]
    T = V.T
    ev += [(.0, 'impact'), (.8, 'pop'), (4.7, 'thud'), (5.1, 'thud'), (8.1, 'swish'), (sh(9.7), 'fill2'), (sh(16.45), 'fill0'), (sh(18.1)+.35, 'thud'), (sh(18.1)+.5, 'impact')]
    ev += [(T['trois']+.1, 'thud')]+[(sh(x), 'bonk') for x in (22.9, 23.6, 24.41)]
    ev += [(T['buy']+.1, 'impact'), (T['buy']+.4, 'pop'), (sh(27.0), 'clack'), (sh(28.5), 'pop'), (sh(29.3), 'coin')]
    ev += [(T['borrow']+.1, 'impact'), (sh(31.6), 'pop'), (sh(32.4), 'swish'), (sh(32.9), 'pop'), (sh(34.6), 'thud'), (sh(35.9), 'coin')]
    ev += [(T['ellison']+.1, 'thud'), (sh(37.3), 'pop'), (sh(37.65), 'swish'), (sh(40.8), 'swish'), (sh(41.0), 'tick'), (sh(43.65), 'impact'), (sh(44.0), 'glint')]
    ev += [(T['die']+.1, 'impact'), (T['die']+.6, 'pop'), (sh(50.3), 'pop'), (sh(51.48), 'fill1'), (sh(51.48)+.7, 'whoosh'), (sh(51.48)+1.0, 'glint'), (sh(51.48)+1.9, 'gavel'), (sh(53.1), 'swish'), (sh(54.9), 'impact')]
    ev += [(T['france']+.1, 'thud'), (sh(59.4), 'pop'), (sh(61.2), 'pop'), (sh(63.3), 'bonk'), (sh(66.4), 'thud'), (sh(68.4), 'pop'), (sh(69.3), 'gavel'), (sh(70.15), 'pop')]
    ev += [(T['pea']+.1, 'thud'), (sh(76.4), 'pop'), (sh(77.0), 'swish'), (sh(78.4), 'fill2'), (sh(80.5), 'fill0'), (sh(84.7)+.3, 'pop'), (sh(84.7)+.6, 'glint')]
    ev += [(T['risque']+.1, 'impact'), (sh(89.9), 'pop'), (sh(92.0), 'swish'), (sh(92.0)+.3, 'fill2'), (sh(92.0)+1.1, 'crash'), (sh(92.0)+2.0, 'bonk')]
    ev += [(T['fin']+.15, 'thud'), (sh(99.2), 'impact'), (sh(99.9), 'pop'), (sh(100.5), 'pop')]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR_TOTAL); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/c_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a_, min(b_, int(DUR_TOTAL*FPS))): ff.stdin.write(frame(k/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR_TOTAL*FPS))
if __name__ == '__main__': main()
