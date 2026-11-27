"""Les Français de ton âge ont combien d'argent ? (28/11/2026), cartoon 1930 en Technicolor, fil rouge : la toise. Couloir (accroche, chute),
toise (moins de 30 ans, 30-39, 40-59 ans), horloge (le temps) ; plaques de verre, médianes qui montent puis se posent, Mister Coin debout
sur les plaques de laiton de la toise, qui saute de l'une à l'autre (la caméra suit), intégré au décor par lib/coin_integration.py.
Aides communes (verre, textes peints, pellicule) reprises du 26/11, partie propre à l'épisode à la fin du fichier.
usage : python3 video_col.py info | png t1 t2 … | video out.mp4 f0 f1   (APERCU=1 : décors d'origine, sans interpolation de Mister Coin)"""
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
def blk(t, name):
    return next((a, b) for (a, b, d) in BLOCS if d == name and a <= t < b+.5)
def src_index(name, a, b, t):
    """image source (24 i/s) montrée au temps t du passage [a, b] : images SRC[(nom, a)] = (i0, i1) étirées sur le passage"""
    i0, i1 = SRC[(name, round(a, 2))]; return i0+(i1-i0)*clamp((t-a)/max(.1, b-a))
def decor_c(name, t):
    a, b = blk(t, name); key = f'{name}_{a:.2f}'
    i = int(round(max(0, t-a)*60))
    f = _RD.get(key, i) if os.path.exists(f'{D}/decors/hd/{key}.mp4') and not os.environ.get('APERCU') else None
    zoom = 1.0
    if f is None:                                                                       # aperçu : image du décor d'origine (agrandi comme l'affinage le fera)
        cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(src_index(name, a, b, t)))); ok, f = cap.read(); cap.release()
        zoom = ZOOM_SR.get(name, 1.0)
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    if zoom > 1: g = cv2.resize(g, (int(W*zoom), int(H*zoom)), interpolation=cv2.INTER_LINEAR); x0 = (g.shape[1]-W)//2; g = g[:H, x0:x0+W]
    g = g+.2*(g-cv2.GaussianBlur(g, (0, 0), 1.0))                               # légère accentuation (décors déjà agrandis par Real-ESRGAN)
    g = np.clip((g-128)*1.06+130, 0, 255)
    if a >= V.T['fin']-.01: g = g*np.array([1.02, .90, .74])*.86                       # chute : le prêteur à la lumière du soir
    return g
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
    d_ = dos_at(t)
    if d_: return dos_col(cv_rgb, t, d_[0], d_[2])
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
ZOOM_SR = {'preteur': 1.12, 'garage': 1.22}                                       # même cadrage que sr_decors.ZOOM_TOP (comptoir et établi sous les sous-titres)
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


def value_card(cv, t, t0, t1, label, value, subs, cy=760, w=880, h=250, vsize=112):
    """fiche de verre : étiquette, montant, puis lignes de précision qui se succèdent (l'ancienne s'efface avant la nouvelle)"""
    def d(kk, ww, hh):
        k = t-t0
        S.text(kk, label, ww/2, 46, 'xb', 32, S.ICE, 'c', .95*ent(k, .3), 3)
        S.text(kk, value, ww/2, hh/2+6, 'a', vsize, S.GD, 'c', ent(k-.1, .3))
        for j, (ts, s_) in enumerate(subs):
            te = subs[j+1][0] if j+1 < len(subs) else None
            a = ent(t-ts-.05, .25)*(1-ent(t-(te-.25), .2) if te else 1)
            if a > 0: S.text(kk, s_, ww/2, hh-38, 'sb', 34, WHITE, 'c', a)
    glass_card(cv, t, t0, d, cy=cy, w=w, h=h, t1=t1)
# ================= images : tuiles logos et Polaroïds =================
_IS = {}
def isurf(path):
    if path not in _IS:
        im = Image.open(path).convert('RGBA'); a = np.asarray(im).astype(np.float32); pre = a.copy(); pre[..., :3] *= a[..., 3:4]/255
        buf = np.ascontiguousarray(pre[..., [2, 1, 0, 3]].astype(np.uint8))
        _IS[path] = (cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, im.width, im.height), im.width, im.height)
    return _IS[path]
def tile(c, name, x, y, w, t, t0, a=1.0):
    """tuile logo façon icône d'appli (logos/<nom>.png) qui arrive en rebond, ombre douce"""
    k = t-t0
    if k <= 0 or a <= 0: return
    sf, iw, ih = isurf(f'{D}/logos/{name}.png'); s_ = w/iw*back(k/.35)
    c.save(); c.translate(x, y); c.scale(s_, s_)
    rr(c, -iw/2+14, -ih/2+22, iw, ih, 115); c.set_source_rgba(0, 0, 0, .35*a); c.fill()
    c.set_source_surface(sf, -iw/2, -ih/2); c.paint_with_alpha(a); c.restore()
_PH = {}
def photo_sq(name):
    """photo carrée (visage) recadrée depuis photos/<nom>.* : carré de la largeur, calé un peu sous le haut ; tons chauds légèrement passés (Polaroïd)"""
    if name not in _PH:
        import glob
        im = Image.open(glob.glob(f'{D}/photos/{name}.*')[0]).convert('RGB'); w, h = im.size; s_ = min(w, h)
        y0 = int(min(h-s_, max(0, h*.06))) if h > w else 0; x0 = (w-s_)//2
        im = im.crop((x0, y0, x0+s_, y0+s_)).resize((420, 420), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32); a = a*.9+np.array([18, 10, 0])+6; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        im.save(f'{D}/tmp/ph_{name}.png'); _PH[name] = f'{D}/tmp/ph_{name}.png'
    return _PH[name]
def polaroid(c, name, label, x, y, w, t, t0, rot=0.0, a=1.0, hl=False):
    """Polaroïd : cadre crème, photo, nom écrit à l'encre dans la marge du bas ; hl = liseré or (personne mise en avant)"""
    k = t-t0
    if k <= 0 or a <= 0: return
    sf, iw, ih = isurf(photo_sq(name)); P = w*.07; Wd = w+2*P; Hd = w+P+w*.30; s_ = back(k/.35)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s_, s_)
    rr(c, -Wd/2+10, -Hd/2+16, Wd, Hd, 10); c.set_source_rgba(0, 0, 0, .40*a); c.fill()
    rr(c, -Wd/2, -Hd/2, Wd, Hd, 10); col(c, 'F7F1E3', a); c.fill()
    if hl: rr(c, -Wd/2, -Hd/2, Wd, Hd, 10); c.set_line_width(9); col(c, 'F2B82E', a); c.stroke()
    c.save(); c.translate(-w/2, -Hd/2+P); c.scale(w/iw, w/iw); c.set_source_surface(sf, 0, 0); c.paint_with_alpha(a); c.restore()
    ink(c, label, 0, -Hd/2+P+w+w*.15, w*.115, '2B1A0E', a=a, maxw=w*.95)
    c.restore()
# ================= étiquette de prix qui grimpe =================
def money(v):
    """montant en dollars lisible : 800 $, 750 000 $, 50 millions $, 5 100 milliards $"""
    if v < 1e6: return f"{num(v)}{NB}$"
    if v < 1e9: return f"{num(v/1e6)}{NB}millions{NB}$" if v < 1e7 else f"{num(v/1e6)}{NB}millions{NB}$"
    return f"{num(v/1e9)}{NB}milliards{NB}$"
def price_tag(cv, c, t, t0, t1, v0, v1, ta, tb, head, sub, cy=560, extra=None, logo=None, final=None):
    """plaque de verre en étiquette de prix : le montant part de v0 et grimpe (échelle logarithmique) jusqu'à v1 entre ta et tb, puis se pose ;
    extra = (texte, t) affiché sous le montant à la fin (multiplicateur)"""
    def d(kk, ww, hh):
        k = t-t0; u = inout((t-ta)/max(.01, tb-ta)); v = v0*(v1/v0)**u
        S.text(kk, head, ww/2, 50, 'xb', 30, S.ICE, 'c', .95*ent(k, .3), 3)
        txt = final if (u >= 1 and final) else money(round(v, -int(max(0, math.log10(max(v, 1))-2))))
        S.text(kk, txt, ww/2, hh/2+4, 'a', 92 if v < 1e9 else 84, S.GD, 'c', ent(k-.05, .3))
        if extra and t > extra[1]: S.text(kk, extra[0], ww/2, hh-42, 'a', 38, S.GD, 'c', ent(t-extra[1], .25))      # multiplicateur à la place de la ligne du bas
        else: S.text(kk, sub, ww/2, hh-40, 'sb', 30, WHITE, 'c', .9*ent(k-.2, .3))
    glass_card(cv, t, t0, d, cy=cy, w=920, h=270, t1=t1)
    if logo: tile(c, logo, 540-460+92, cy+28+30*(1-ent(t-t0, .45)), 100, t, t0+.15, a=1-ent(t-(t1-.3), .3) if t1 else 1)   # logo dans la plaque, à gauche du montant
def year_card(cv, c, t, t0, t1, n, logo, year, cy=330):
    """carte d'ouverture d'une histoire : tuile logo à gauche, « HISTOIRE N°x », année en grand"""
    def d(kk, ww, hh):
        k = t-t0
        S.text(kk, f"HISTOIRE N°{n}", ww/2+100, 62, 'xb', 32, S.ICE, 'c', .95*ent(k, .3), 4)
        S.text(kk, year, ww/2+100, hh/2+28, 'a', 150, S.GD, 'c', ent(k-.08, .3))
    glass_card(cv, t, t0, d, cy=cy, w=820, h=260, t1=t1)
    a = 1-ent(t-(t1-.3), .3) if t1 else 1
    tile(c, logo, 540-410+130, cy+30*(1-ent(t-t0, .45)), 170, t, t0+.15, a=a)                  # logo dans la plaque, à gauche
SC_PRICES = dict(apple=5.145e12, alphabet=3.43e12, netflix=234.9e9)  # capitalisations à la clôture du 24/11/2026 (sources.md)


# ======================================================================================================================
# Épisode du 28/11 : « Les Français de ton âge ont combien d'argent ? » — la toise. (Ce qui précède : aides communes reprises du 26/11.)
# ======================================================================================================================
sys.path.insert(0, f'{D}/../../lib')
import coin_integration as CI
T_ = V.T; J = V.JUMPS
SC_ORDER = [(0.0, 'couloir'), (T_['bas'], 'toise_bas'), (T_['milieu'], 'toise_milieu'), (T_['haut'], 'toise_haut'), (T_['horloge'], 'horloge'), (T_['fin'], 'couloir')]
# images source (vidéo Gemini, 24 i/s) montrées à chaque instant : nœuds (temps vidéo, image) ; uniquement les plages saines (sr_tout.py)
KN = {('couloir', 0.0): [(0.0, 0), (T_['bas'], 60)],
      ('toise_bas', T_['bas']): [(T_['bas'], 84), (T_['milieu'], 101)],
      ('toise_milieu', T_['milieu']): [(T_['milieu'], 28), (J['milieu'][0], 37), ((J['milieu'][0]+J['milieu'][1])/2, 42),
                                      ((J['milieu'][0]+J['milieu'][1])/2+1e-3, 141), (J['milieu'][1], 144), (T_['haut'], 152)],
      ('toise_haut', T_['haut']): [(T_['haut'], 18), (J['haut'][0], 27), (J['haut'][1], 101), (T_['horloge'], 111)],
      ('horloge', T_['horloge']): [(T_['horloge'], 0), (T_['fin'], 124)],
      ('couloir', T_['fin']): [(T_['fin'], 62), (V.DUR, 82)]}
def bloc(t):
    i = max(j for j, (a, d) in enumerate(SC_ORDER) if t >= a or j == 0); a, d = SC_ORDER[i]
    b = SC_ORDER[i+1][0] if i+1 < len(SC_ORDER) else V.DUR
    return a, b, d
BLOCS = [(a, (SC_ORDER[i+1][0] if i+1 < len(SC_ORDER) else V.DUR), d) for i, (a, d) in enumerate(SC_ORDER)]
BLOCS_MIX = BLOCS
def src_f(d, a, t):
    k = KN[(d, a)]; return float(np.interp(t, [u for u, _ in k], [v for _, v in k]))
_CAPS = {}
def _orig(d, i):
    """image d'origine (aperçu) : lecture directe de la vidéo Gemini"""
    key = (d, i)
    if key not in _CAPS:
        if len(_CAPS) > 30: _CAPS.clear()
        cap = cv2.VideoCapture(f'{D}/decors/decor_{d}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read(); cap.release()
        _CAPS[key] = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
    return _CAPS[key]
def decor_c(name, t):
    a, b, d = bloc(t); key = f'{d}_{a:.2f}'; i = int(round(max(0, t-a)*60))
    f = _RD.get(key, i) if os.path.exists(f'{D}/decors/hd/{key}.mp4') and not os.environ.get('APERCU') else None
    if f is None:
        s = src_f(d, a, t); i0 = int(s); u = s-i0
        g0 = _orig(d, i0).astype(np.float32); g = g0 if u < .02 else g0*(1-u)+_orig(d, i0+1).astype(np.float32)*u
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LANCZOS4)
    else: g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H)).astype(np.float32)
    g = g+.2*(g-cv2.GaussianBlur(g, (0, 0), 1.0)); g = np.clip((g-128)*1.06+130, 0, 255)
    if a >= T_['fin']-.01: g = g*np.array([1.02, .90, .74])*.86                         # chute : le couloir à la lumière du soir
    return g

# ---------------- où se tiennent ses pieds : plaques de la toise (suivies), sol du couloir et de l'horloge (suivis) ----------------
import json
_TR = {}
def _track(name):
    if name not in _TR: _TR[name] = json.load(open(f'{D}/decors/{name}.json'))
    return _TR[name]
def _interp_track(P, s):
    P = np.asarray(P); i = int(np.clip(s, 0, len(P)-1.001)); u = s-i; return P[i]*(1-u)+P[min(i+1, len(P)-1)]*u
def ground(t):
    """(x, y des pieds, échelle, bord avant de la surface ou None, reflet ?) au temps t"""
    a, b, d = bloc(t); s = src_f(d, a, t)
    if d in ('couloir', 'horloge'):
        tr = _track(f'sol_{d}'); p = _interp_track(tr['p'], s-tr['i0']); sc = float(np.interp(s-tr['i0'], range(len(tr['s'])), tr['s']))
        sc = 1+(sc-1)*.6                                                                # il grandit avec le travelling, sans gros plan
        return p[0], p[1], sc, None, d == 'horloge'                                    # tapis du couloir : pas de reflet ; parquet ciré de l'horloge : reflet
    P = _track(f'plaques_{d}')
    if d == 'toise_milieu' and s > 100: tr = _track('sol_toise_milieu_b2'); p = _interp_track(tr['p'], s-tr['i0'])
    elif d == 'toise_haut' and s > 60: p = _interp_track(P['h'], s)+np.array([0, 22])       # plaque du haut : surface 22 px sous le point suivi (mesuré)
    else: p = _interp_track(P['b'], s)
    return p[0], p[1]-6, 1.0, p[1]+18, True                                            # debout sur la plaque de laiton poli (reflet court)
def feet(t):
    """pieds de Mister Coin : suivis sur la surface ; en arc pendant les sauts (changement de décor et saut de plaque en plaque)"""
    arcs = [(ta-.3, ta+.3) for ta in IRIS]+list(J.values())
    for (j0, j1) in arcs:
        if j0 <= t < j1:
            u = inout((t-j0)/(j1-j0)); g0 = ground(j0-1e-3); g1 = ground(j1)
            x = lerp(g0[0], g1[0], u); yg = lerp(g0[1], g1[1], u); hgt = 90*math.sin(math.pi*u)
            return x, yg-hgt, lerp(g0[2], g1[2], u), (g0[1] if u < .5 else g1[1]), hgt, True                    # en l'air : (…, sol sous lui, hauteur, saut)
    g = ground(t); return (*g, False)

# ---------------- Mister Coin : clip en 60 i/s (flux optique), pose fixe pour la réflexion, intégration lumière ----------------
_POSE = {}
def _pose(name, X, Y):
    if name not in _POSE:
        im = np.asarray(Image.open(f'{D}/../../mister_coin/poses/{name}.png').convert('RGBA')).astype(np.float32)
        a = im[..., 3]; ys, xs = np.nonzero(a > 20); im = im[ys.min():ys.max()+1, xs.min():xs.max()+1]
        k = 170*2.45/im.shape[0]; _POSE[name] = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    p = _POSE[name]; h, w = p.shape[:2]; C = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32)
    x0, y0 = int(X-w/2), int(Y-h); xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0+w), min(H, y0+h)
    if xb > xa and yb > ya:
        C[ya:yb, xa:xb] = p[ya-y0:yb-y0, xa-x0:xb-x0, :3]; A[ya:yb, xa:xb] = p[ya-y0:yb-y0, xa-x0:xb-x0, 3]/255
    return C, A
def _rx(t, X, Y):
    for (t0, clip, f0, f1), t1 in zip(V.RX, V.RX_FIN):
        if t0 <= t < t1:
            if clip.startswith('pose:'):
                br = 1+.012*math.sin((t-t0)*2*math.pi*.8); C, A = _pose(clip[5:], X, Y)
                if abs(br-1) > 1e-4:                                                     # respiration lente
                    M = np.float32([[1, 0, 0], [0, br, Y*(1-br)]]); C = cv2.warpAffine(C, M, (W, H)); A = cv2.warpAffine(A, M, (W, H))
                return C, A
            if clip not in _RXC: _RXC[clip] = VC.VeoCoin([(0.0, clip, 'une')], x=540, pieds=V.FEET, largeur_piece=170)
            fr = f0+(f1-f0)*(t-t0)/(t1-t0); r, al = _RXC[clip].layer((fr+.5)/24, X, Y); return r.astype(np.float32), al
    return None
def _layer24(t, X, Y):
    r = _rx(t, X, Y)
    if r is not None: return r
    rgb_, al = V.MC.layer(t, X, Y+V.MC.hop_dy(t)); return rgb_.astype(np.float32), al.astype(np.float32)
def coin_layer(t, X, Y):
    """image de Mister Coin à 60 i/s : les deux images voisines du clip (24 i/s) interpolées par flux optique, sur la zone utile seulement"""
    i = math.floor(t*24+1e-6); u = t*24-i
    C0, A0 = _layer24((i+.5)/24, X, Y)
    if u < .05 or os.environ.get('APERCU'): return C0, A0
    C1, A1 = _layer24((i+1.5)/24, X, Y)
    m = (A0 > .01) | (A1 > .01)
    if not m.any(): return C0, A0
    ys, xs = np.nonzero(m); y0, y1 = max(0, ys.min()-24), min(H, ys.max()+25); x0, x1 = max(0, xs.min()-24), min(W, xs.max()+25)
    fr = [np.clip(C0[y0:y1, x0:x1], 0, 255).astype(np.uint8), np.clip(C1[y0:y1, x0:x1], 0, 255).astype(np.uint8)]
    al = [(A0[y0:y1, x0:x1]*255).astype(np.uint8), (A1[y0:y1, x0:x1]*255).astype(np.uint8)]
    c, (a,) = CI.fluidite60(fr, u, (al,), fps=1, src_fps=1)
    C = C0.copy(); A = A0.copy(); C[y0:y1, x0:x1] = c.astype(np.float32); A[y0:y1, x0:x1] = a.astype(np.float32)/255
    return C, A
def _pieds_bas(A, x):
    """ligne la plus basse de Mister Coin (semelles) autour de x"""
    band = A[:, max(0, int(x)-160):min(W, int(x)+160)] > .5; rows = np.nonzero(band.any(1))[0]
    return rows.max() if len(rows) else None
def coin_col(cv_rgb, t):
    x, y, sc, bord, reflet, saut = feet(t)
    C, A = coin_layer(t, x, y)
    if abs(sc-1) > 1e-3:                                                                 # taille liée au travelling, autour des pieds
        M = np.float32([[sc, 0, x*(1-sc)], [0, sc, y*(1-sc)]]); C = cv2.warpAffine(C, M, (W, H)); A = cv2.warpAffine(A, M, (W, H))
    yb = _pieds_bas(A, x)
    if saut:                                                                              # en l'air : ombre sur la surface en dessous, plus petite et plus pâle quand il monte
        sol, hgt = bord, reflet
        if yb is not None and abs(yb-y) > 2: M = np.float32([[1, 0, 0], [0, 1, y-yb]]); C = cv2.warpAffine(C, M, (W, H)); A = cv2.warpAffine(A, M, (W, H))
        m = np.zeros((H, W), np.float32); k = 1-hgt/140
        cv2.ellipse(m, (int(x), int(sol)), (int(110*k), int(16*k)), 0, 0, 360, .55*k, -1); cv_rgb = cv_rgb*(1-cv2.GaussianBlur(m, (0, 0), 10)[..., None])
        return cv_rgb*(1-A[..., None])+C*A[..., None]
    # pieds verrouillés sur la surface : si le clip le fait rebondir (parle_enthousiaste), on le repose au sol, il ne flotte jamais
    C, A = CI.poser_au_sol(C, A, x, y)
    return CI.integrer(cv_rgb, C, A, (x, y), sc, bord_y=bord, reflet=reflet)

# ---------------- plaques de verre de chaque scène ----------------
SRCL = "Insee, enquête Patrimoine, début 2024"
def age_card(cv, c, t, t0, t1, head, v, ta, tb, sub, cy=430, extra=None):
    """plaque d'une tranche d'âge : tranche en tête, médiane qui monte (1,3 s) puis tenue, sous-titre et source en petit"""
    def d(kk, ww, hh):
        k = t-t0; u = inout((t-ta)/max(.01, tb-ta)); val = round(v*u, -2) if u < 1 else v
        S.text(kk, head, ww/2, 52, 'xb', 34, S.ICE, 'c', .95*ent(k, .3), 4)
        S.text(kk, f"{num(val)}{NB}€", ww/2, hh/2+6, 'a', 104, S.GD, 'c', ent(k-.05, .3))
        S.text(kk, sub, ww/2, hh-64, 'sb', 30, WHITE, 'c', .92*ent(t-ta, .3))
        S.text(kk, SRCL, ww/2, hh-26, 'sb', 22, S.ICE, 'c', .7*ent(t-ta, .3))
        if extra and t > extra[1]: S.text(kk, extra[0], ww-70, 56, 'a', 44, S.GD, 'r', ent(t-extra[1], .25))
    glass_card(cv, t, t0, d, cy=cy, w=900, h=300, t1=t1)
def b_couloir(cv, c, t, k):
    sh = V.sh
    a = ent(t, .35)*(1-ent(t-2.0, .3))
    if a > 0:
        plate(c, 540, 400, 960, 300, a)
        pop_text(c, "LES FRANÇAIS DE TON ÂGE", 540, 340, 62, t, .05, CREAM, a=a, maxw=880)
        pop_text(c, f"ONT COMBIEN D'ARGENT{NB}?", 540, 440, 72, t, .35, YEL, a=a, maxw=880)
    a2 = ent(t-2.3, .3)*(1-ent(t-5.5, .3))
    if a2 > 0:                                                                            # invitation : grande, trois pictos en rebond (25/11)
        plate(c, 540, 430, 960, 300, a2)
        for i, (e, lab) in enumerate((('❤️', 'AIME'), ('🔖', 'ENREGISTRE'), ('💬', 'COMMENTE'))):
            x = 540+(i-1)*300; k_ = t-(2.35+i*.35)
            if k_ > 0:
                bob = 10*math.sin(max(0, k_-.4)*5)*math.exp(-max(0, k_-.4)*1.2)
                EMO.append((e, x, 395-bob, 96*back(k_/.35), a2)); paint(c, lab, x, 500, 34, YEL if i == 1 else CREAM, a=a2*ent(k_, .3))
    a3 = ent(t-5.95, .35)*(1-ent(t-15.9, .3))
    if a3 > 0:
        plate(c, 540, 450, 980, 460, a3)
        pop_text(c, "PATRIMOINE BRUT DU MÉNAGE", 540, 290, 50, t, 6.0, YEL, a=a3, maxw=900)
        paint(c, "Insee · enquête Histoire de vie et Patrimoine", 540, 352, 28, a=a3*ent(t-6.4, .3))
        paint(c, "situation début 2024", 540, 390, 28, a=a3*ent(t-8.9, .3))
        for i, (e, lab, tt) in enumerate((('🏦', 'livrets', 12.5), ('📈', 'placements', 13.2), ('🏠', 'logement', 13.8))):
            x = 540+(i-1)*290
            if t > tt: EMO.append((e, x, 475, 70*back((t-tt)/.35), a3)); paint(c, lab, x, 540, 32, CREAM, a=a3*ent(t-tt, .3))
        if t > 14.5: pop_text(c, "crédits non déduits", 540, 605, 36, t, 14.5, YEL, a=a3)
        paint(c, "âge de la personne qui apporte le plus de revenus", 540, 655, 27, a=a3*.85*ent(t-10.6, .3))
def b_bas(cv, c, t, k):
    sh = V.sh
    age_card(cv, c, t, 16.3, T_['milieu']+.1, "MOINS DE 30 ANS", 26100, 17.9, 19.2, "la moitié des ménages a moins")
def b_milieu(cv, c, t, k):
    sh = V.sh
    age_card(cv, c, t, 20.95, J['milieu'][0]+.2, "30 À 39 ANS", 146200, 21.3, 22.6, "médiane", extra=(f"×{NB}5,6", 24.7))
    a = ent(t-(J['milieu'][1]+.05), .3)*(1-ent(t-30.0, .3))
    if a > 0:
        plate(c, 540, 430, 900, 220, a)
        pop_text(c, f"LE SECRET{NB}?", 540, 380, 62, t, 26.45, YEL, a=a)
        if t > 27.35: pop_text(c, "un logement…", 540, 460, 46, t, 27.35, CREAM, a=a)
        if t > 28.7: pop_text(c, "acheté à crédit", 540, 520, 46, t, 28.7, YEL, a=a)
        if t > 27.35: EMO.append(('🏠', 840, 460, 70*back((t-27.35)/.35), a))
    def d(kk, ww, hh):
        k_ = t-30.15; u = inout((t-32.0)/1.3); val = round(119800*u, -2) if u < 1 else 119800
        S.text(kk, "RESTE À REMBOURSER", ww/2, 52, 'xb', 34, S.ICE, 'c', .95*ent(k_, .3), 4)
        S.text(kk, f"{num(val)}{NB}€", ww/2, hh/2+6, 'a', 104, S.GD, 'c', ent(k_-.05, .3))
        S.text(kk, "médiane · ménages de 30-39 ans qui ont un crédit", ww/2, hh-64, 'sb', 28, WHITE, 'c', .92*ent(t-32.0, .3))
        S.text(kk, "Insee, dettes des ménages, début 2024", ww/2, hh-26, 'sb', 22, S.ICE, 'c', .7*ent(t-32.0, .3))
    glass_card(cv, t, 30.15, d, cy=430, w=900, h=300, t1=T_['haut']+.1)
def b_haut(cv, c, t, k):
    sh = V.sh
    age_card(cv, c, t, T_['haut']+.05, J['haut'][0]+.2, "40 À 49 ANS", 215200, sh(37.74)-1.3, sh(37.74), "médiane")
    age_card(cv, c, t, J['haut'][1]+.05, T_['horloge']+.1, "50 À 59 ANS", 254100, sh(41.63)-1.3, sh(41.63), "médiane",
             extra=("LE SOMMET", sh(43.9)))
    a = ent(t-sh(45.5), .3)*(1-ent(t-(T_['horloge']-.2), .3))
    if a > 0:
        plate(c, 540, 680, 900, 120, a)
        paint(c, f"après 60 ans, ça plafonne{NB}: 245{NB}000{NB}€ puis 247{NB}600{NB}€", 540, 680, 28, a=a)
def b_horloge(cv, c, t, k):
    sh = V.sh; t0 = T_['horloge']
    a = ent(t-t0-.05, .35)*(1-ent(t-(T_['fin']-.1), .3))
    if a <= 0: return
    plate(c, 540, 470, 980, 520, a)
    pop_text(c, "CE QUI FAIT GRIMPER LA MARQUE", 540, 270, 44, t, t0+.1, CREAM, a=a, maxw=900)
    if t > sh(49.98): pop_text(c, "LE TEMPS", 540, 345, 72, t, sh(49.98), YEL, a=a)
    for i, (e, lab, tt) in enumerate((('🐖', "l'épargne", 51.04), ('🏠', "le crédit remboursé", 52.8), ('🎁', "un héritage", 54.5), ('📈', "les intérêts composés", 55.6))):
        x = 300+(i % 2)*480; y = 470+(i//2)*150; tt = sh(tt)
        if t > tt: EMO.append((e, x-150, y, 68*back((t-tt)/.35), a)); paint(c, lab, x+30, y, 32, CREAM, a=a*ent(t-tt, .3), fam='Inter Display')
def b_fin(cv, c, t, k):
    sh = V.sh
    a = ent(t-sh(57.45), .3)
    if a > 0:
        plate(c, 540, 400, 1000, 300, a)
        pop_text(c, f"ET TOI{NB}?", 540, 330, 88, t, sh(57.45), YEL, a=a)
        pop_text(c, "TA MARQUE EST AU-DESSUS", 540, 425, 44, t, sh(58.1), CREAM, a=a, maxw=900)
        pop_text(c, f"OU EN DESSOUS DE TON ÂGE{NB}?", 540, 485, 44, t, sh(58.9), CREAM, a=a, maxw=900)
    a3 = ent(t-(V.DUR-2.6), .4)
    if a3 > 0:
        plate(c, 540, 760, 1030, 110, a3*.9)
        paint(c, "Source : Insee, enquête Histoire de vie et Patrimoine 2023-2024", 540, 740, 24, a=a3)
        paint(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 780, 24, a=a3)
FN = {('couloir', 0.0): b_couloir, ('toise_bas', T_['bas']): b_bas, ('toise_milieu', T_['milieu']): b_milieu, ('toise_haut', T_['haut']): b_haut,
      ('horloge', T_['horloge']): b_horloge, ('couloir', T_['fin']): b_fin}
SC = [(a, b, FN[(d, a)], d) for (a, b, d) in BLOCS]
IRIS = [s_[0] for s_ in SC[1:]]
def raw_bg(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    global _CV, _T
    s, c = surface(); EMO.clear(); _CV = cv; _T = t; f(cv, c, t, max(0.0, t-a)); _CV = None; cv.alpha_composite(to_img(s))
    for (ch, x, y, sz, al) in EMO:
        if al > .01 and sz > 2:
            e = S.emoji(ch, int(sz)).copy()
            if al < .999: e.putalpha(Image.fromarray((np.asarray(e.getchannel('A')).astype(np.float32)*al).astype(np.uint8)))
            cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
    return np.asarray(cv.convert('RGB')).astype(np.float32)
XF = .3
def frame(t):
    for ta in IRIS:
        if ta-XF/2 <= t < ta+XF/2:
            k = inout((t-(ta-XF/2))/XF); arr = raw_bg(min(t, ta-1/FPS))*(1-k)+raw_bg(max(t, ta))*k; break
    else: arr = raw_bg(t)
    arr = coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    return out
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD, a=al, y=1060); return
def events():
    sh = V.sh
    ev = list(V.events()) + [(ta-XF/2, 'whoosh') for ta in IRIS] + [(j0, 'swish') for (j0, j1) in J.values()]
    ev += [(.05, 'impact'), (2.35, 'pop'), (2.7, 'pop'), (3.05, 'pop'), (6.0, 'pop'), (12.5, 'tick'), (13.2, 'tick'), (13.8, 'tick'),
           (17.9, 'tick'), (19.2, 'impact'), (21.3, 'tick'), (22.6, 'impact'), (24.7, 'glint'), (26.45, 'pop'), (28.7, 'pop'),
           (32.0, 'tick'), (33.3, 'impact'), (35.62, 'bonk'), (sh(37.74)-1.3, 'tick'), (sh(37.74), 'impact'), (sh(41.63)-1.3, 'tick'), (sh(41.63), 'impact'),
           (sh(43.9), 'tadaa'), (sh(49.98), 'pop'), (sh(51.04), 'pop'), (sh(52.8), 'pop'), (sh(54.5), 'pop'), (sh(55.6), 'pop'), (sh(57.45), 'impact')]
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
