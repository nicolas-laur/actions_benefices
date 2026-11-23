"""Black Friday : bonne affaire ou marketing ? (25/11/2026), cartoon 1930 en Technicolor : grand magasin Art déco (rue, hall, rayon, bureau d'enquêteur, vitrine),
plaques de verre, étiquette de prix géante, Mister Coin en couleurs (assis au bord du bureau pour les réflexes), pellicule, fondus aux changements de décor.
usage : python3 video_col.py info | png t1 t2 … | video out.mp4 f0 f1"""
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
    if f is None and not os.path.exists(f'{D}/decors/decor_{name}.mp4'):              # décor pas encore livré : fond provisoire (rue floutée)
        cap = cv2.VideoCapture(f'{D}/decors/decor_rue.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, 120); ok, f = cap.read(); cap.release()
        f = cv2.GaussianBlur(f, (0, 0), 9)//2+40
    elif f is None:                                                                     # aperçu sans le décor interpolé : image du décor d'origine
        cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); n = min(NMAX.get(name, 9999), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))); sp = min(1.0, (n-1)/24/max(.1, b-a))
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(n-1, int(max(0, t-a)*sp*24))); ok, f = cap.read(); cap.release()
        if name in LETTERBOX:                                                          # décor sorti en paysage (bandes floues) : provisoire, recadré
            y0, y1, xc = LETTERBOX[name]; f = f[y0:y1]; w = int((y1-y0)*9/16); f = f[:, xc-w//2:xc+w//2]
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    if name in ZOOM_TOP:                                                               # agrandi depuis le haut : le plateau descend sous les sous-titres
        z = ZOOM_TOP[name]; g = cv2.resize(g, (int(W*z), int(H*z)), interpolation=cv2.INTER_LINEAR); x0 = (g.shape[1]-W)//2; g = g[:H, x0:x0+W]
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
LETTERBOX = {}; ZOOM_TOP = {'enquete': 1.06}; NMAX = {'enquete': 140}       # bureau : on s'arrête avant que le travelling ne descende le plateau trop bas                                # décors sortis en paysage à recadrer (aucun : le notaire a été refait en 9:16)
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

# ================= fiches de verre =================
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
def bars(cv, t, t0, t1, cy=640):
    """panier moyen Black Week 2022 à 2025 (Joko) : quatre colonnes qui montent, 2022 et 2025 en or, 2023 et 2024 en gris"""
    DATA = [(2022, 193, True, sh(26.09)), (2023, 183, False, sh(27.2)), (2024, 233, False, sh(27.9)), (2025, 236, True, sh(28.6))]
    def d(kk, ww, hh):
        S.text(kk, "PANIER MOYEN DU BLACK FRIDAY", ww/2, 44, 'xb', 30, S.ICE, 'c', .95, 3)
        base = hh-70; top = 150; bw = 130; gap = (ww-4*bw)/5
        for i, (yr, v, hi, ta) in enumerate(DATA):
            u = inout((t-ta)/.8)
            if u <= 0: continue
            x = gap+i*(bw+gap); bh = (base-top)*v/250*u; c0, c1 = (GOLDC if hi else GREYC)
            rr(kk, x, base-bh, bw, bh, 14); g = cairo.LinearGradient(0, base-bh, 0, base)
            for st, cc in ((0, c0), (1, c1)): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .96)
            kk.set_source(g); kk.fill()
            S.text(kk, f"{int(round(v*u))}{NB}€", x+bw/2, base-bh-30, 'a', 44 if hi else 36, S.GD if hi else S.ICE, 'c', ent(t-ta, .3))
            S.text(kk, str(yr), x+bw/2, base+36, 'sb', 32, WHITE, 'c', ent(t-ta, .3))
    glass_card(cv, t, t0, d, cy=cy, w=900, h=480, t1=t1)
def gauges(cv, t, t0, t1, cy=420):
    """deux jauges : prix +8 % (Insee 2023-2025) et panier +22 % (2022 -> 2025)"""
    def d(kk, ww, hh):
        for i, (lab, v, ta, cc) in enumerate(((f"PRIX", 8, sh(30.91)+.3, GREYC), (f"PANIER", 22, sh(32.9), GOLDC))):
            y = 70+i*100; u = inout((t-ta)/.9)
            S.text(kk, lab, 40, y, 'xb', 32, S.ICE, 'l', ent(t-ta+.2, .3), 2)
            x0 = 230; L = ww-x0-200; rr(kk, x0, y-22, L, 44, 22); col(kk, 'FFFFFF', .12); kk.fill()
            if u > 0:
                rr(kk, x0, y-22, max(44, L*v/25*u), 44, 22); g = cairo.LinearGradient(0, y-22, 0, y+22)
                for st, c_ in ((0, cc[0]), (1, cc[1])): r_, g_, b_ = rgb(c_)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .96)
                kk.set_source(g); kk.fill()
                S.text(kk, f"+{v*u:.0f}{NB}%", ww-40, y, 'a', 44, S.GD if i else S.ICE, 'r', ent(t-ta, .3))
        S.text(kk, "2022 → 2025", ww/2, hh-26, 'sb', 26, S.ICE, 'c', .8)
    glass_card(cv, t, t0, d, cy=cy, w=900, h=250, t1=t1)
def sectors(cv, t, t0, t1, cy=780):
    rows = [('🧴', "Beauté", "+4 %", S.GD, sh(34.75)), ('💻', "High-tech", "+3 %", S.GD, sh(35.6)), ('👗', "Mode", "−3 %", S.ICE, sh(36.54))]
    def d(kk, ww, hh):
        S.text(kk, "VENTES 2025 VS 2024", ww/2, 40, 'xb', 26, S.ICE, 'c', .9, 3)
        for i, (e, lab, v, cc, ta) in enumerate(rows):
            x = ww/6+i*ww/3; a = ent(t-ta, .3)
            S.text(kk, lab, x, 150, 'sb', 32, WHITE, 'c', a); S.text(kk, v, x, 205, 'a', 52, cc, 'c', a)
            S.text(kk, '▲' if v[0] == '+' else '▼', x, 250, 'b', 26, cc, 'c', a)
    glass_card(cv, t, t0, d, cy=cy, w=900, h=290, t1=t1)
    for i, (e, lab, v, cc, ta) in enumerate(rows):
        if t > ta and (t1 is None or t < t1): EMO.append((e, 540-450+150+i*300, cy-145+95, 56, ent(t-ta, .3)*(1-ent(t-(t1-.3), .3) if t1 else 1)))
# ================= étiquette de prix géante du rayon (suivie dans le décor) =================
_TAG = {}
def tag_box(arr, t):
    """boîte de l'étiquette crème au centre du décor du rayon (plus grande composante claire et peu saturée)"""
    k = int(t*24)
    if k not in _TAG:
        a = cv2.resize(arr.astype(np.uint8), (W//4, H//4), interpolation=cv2.INTER_AREA).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
        m = ((R > 185) & (G > 170) & (B > 130) & (R-B < 75) & (R-B > 5)).astype(np.uint8)
        m[:, :W//4//5] = 0; m[:, -W//4//5:] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        j = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])) if n > 1 else None
        _TAG[k] = None if j is None else tuple(int(v*4) for v in (st[j, 0], st[j, 1], st[j, 0]+st[j, 2], st[j, 1]+st[j, 3]))
        if len(_TAG) > 200: _TAG.clear()
    return _TAG[k]
def tag_text(c, box, t):
    """inscriptions à l'encre sur l'étiquette : promo affichée, puis la règle des 30 jours"""
    x0, y0, x1, y1 = box; cx = (x0+x1)/2; w = x1-x0; ys = y0+(y1-y0)*.30; h = (min(y1, 960)-ys)/.5; w = min(w, h*.9)
    a1 = ent(t-sh(38.6), .3)*(1-ent(t-sh(47.3), .3)); a2 = ent(t-sh(47.6), .3)*(1-ent(t-(V.T['enquete']-.6), .3))
    if a1 > 0:
        ys += h*.02; ink(c, "PROMO", cx, ys, w*.21, '7A1E12', a=a1, maxw=w*.8)
        ink(c, "199 €", cx, ys+h*.13, w*.16, '6B5A48', a=a1, maxw=w*.8)
        c.set_line_width(max(4, w*.015)); col(c, '7A1E12', a1); c.move_to(cx-w*.22, ys+h*.13); c.line_to(cx+w*.22, ys+h*.13); c.stroke()
        ink(c, "139 €", cx, ys+h*.28, w*.25, '2B1A0E', a=a1, maxw=w*.8)
        ink(c, "−30 %", cx, ys+h*.43, w*.19, '7A1E12', a=a1, maxw=w*.8)
    if a2 > 0:
        ink(c, "PRIX BARRÉ", cx, ys, w*.15, '7A1E12', a=a2, maxw=w*.84)
        ink(c, "=", cx, ys+h*.1, w*.12, '2B1A0E', a=a2)
        ink(c, "le plus bas", cx, ys+h*.2, w*.125, '2B1A0E', a=a2, maxw=w*.84)
        ink(c, "des 30", cx, ys+h*.31, w*.18, '2B1A0E', a=a2, maxw=w*.84)
        ink(c, "derniers jours", cx, ys+h*.42, w*.12, '2B1A0E', a=a2, maxw=w*.84)
# ================= courbe d'historique de prix (réflexe 2) =================
def price_chart(cv, t, t0, t1, cy=640):
    """prix stable à 139 € pendant un mois, gonflé à 199 € la veille, puis « −30 % » : on retombe au même prix"""
    def d(kk, ww, hh):
        S.text(kk, "HISTORIQUE DU PRIX", ww/2, 40, 'xb', 28, S.ICE, 'c', .9, 3)
        x0, x1, yb, yt = 70, ww-70, hh-60, 120
        def Y(v): return yb-(v-100)/(220-100)*(yb-yt)
        pts = [(0, 139), (.78, 139), (.8, 199), (.9, 199), (.92, 139), (1, 139)]
        u = inout((t-t0-.2)/1.6); kk.set_line_cap(cairo.LINE_CAP_ROUND); kk.set_line_join(cairo.LINE_JOIN_ROUND)
        kk.move_to(x0, Y(139))
        for (p, v) in pts[1:]:
            if p > u: pp = pts[[q for q, _ in pts].index(p)-1]; fr = (u-pp[0])/(p-pp[0]); kk.line_to(x0+(x1-x0)*u, Y(pp[1]+(v-pp[1])*fr)); break
            kk.line_to(x0+(x1-x0)*p, Y(v))
        kk.set_line_width(9); col(kk, 'FFE27A'); kk.stroke()
        S.text(kk, "139 € pendant un mois", x0+(x1-x0)*.36, Y(139)-40, 'sb', 28, WHITE, 'c', ent(t-t0-.6, .3))
        if u > .82: S.text(kk, "199 € la veille", x0+(x1-x0)*.78, Y(199)-36, 'sb', 28, WHITE, 'c', ent(t-t0-1.4, .3))
        if t > sh(64.28): S.text(kk, "« −30 % » = 139 €", x0+(x1-x0)*.8, Y(139)+44, 'a', 34, S.GD, 'c', ent(t-sh(64.28), .3))
        S.text(kk, "exemple", x1, hh-22, 'sb', 22, S.ICE, 'r', .7)
    glass_card(cv, t, t0, d, cy=cy, w=900, h=420, t1=t1)
def reflex(cv, t, t0, t1, n, head, sub, cy=330):
    def d(kk, ww, hh):
        S.text(kk, f"{n}", 70, hh/2, 'a', 96, S.GD, 'c', ent(t-t0, .3))
        S.text(kk, head, 140, hh/2-26, 'a', 50, WHITE, 'l', ent(t-t0, .3))
        S.text(kk, sub, 140, hh/2+38, 'sb', 32, S.GD2, 'l', ent(t-t0-.4, .3))
    glass_card(cv, t, t0, d, cy=cy, w=900, h=190, t1=t1)
# ================= 1. rue : l'origine du nom =================
def b_rue(cv, c, t, k):
    t1 = 3.6; a = 1-ent(t-t1, .3) if t > t1 else 1
    plate(c, 540, 400, 1000, 330, a)
    title(c, "POURQUOI ON L'APPELLE", t, -.5, 300, 60, CREAM, t1=t1)
    title(c, "« BLACK FRIDAY »", t, -.3, 410, 104, YEL, t1=t1)
    title(c, "?", t, -.1, 510, 80, YEL, t1=t1)
    if t > .8: EMO.append(('🤔', 945, 640, 84, a*ent(t-.8, .3)))
    if 7.3 < t < 17.0:
        value_card(cv, t, 7.4, 17.0, "ÉTATS-UNIS · ANNÉES 1960", "PHILADELPHIE", [(7.5, "la police baptise le lendemain de Thanksgiving"), (12.37, "foule · bouchons · journée noire")], cy=420, vsize=88)
        if t > 12.37: EMO.append(('🚓', 540-330, 420-60, 60, ent(t-12.37, .3)*(1-ent(t-16.7, .3))))
    if 14.89 < t < 17.9:
        stamp(c, "BIG FRIDAY ?", 540, 650, 64, t, 15.4, colr='F6E7C1', rot=-.06, a=1-ent(t-17.6, .3))
    if t > 17.05 and t < 17.9: stamp(c, "RATÉ", 600, 870, 70, t, 17.07, rot=.10, a=1-ent(t-17.6, .3))
    if t > 17.9:
        value_card(cv, t, 17.95, V.T['hall'], "ET EN FRANCE ?", "2013", [(18.0, "le nom est resté"), (20.15, "arrivé par le e-commerce")], cy=420)
# ================= 2. hall : le panier moyen et l'inflation =================
def b_hall(cv, c, t, k):
    t0 = V.T['hall']
    if t < sh(26.0):
        plate(c, 540, 380, 980, 150, ent(t-t0-.1, .3)*(1-ent(t-sh(25.7), .3)))
        pop_text(c, "ON DÉPENSE TOUJOURS PLUS", 540, 380, 60, t, t0+.2, YEL, maxw=900, a=1-ent(t-sh(25.7), .3))
        return
    bars(cv, t, sh(26.0), sh(34.6), cy=560 if t < sh(30.8) else 560+150*inout((t-sh(30.8))/.4))
    if t > sh(30.8) and t < sh(34.6): gauges(cv, t, sh(30.85), sh(34.6), cy=270)
    if t > sh(34.6): sectors(cv, t, sh(34.65), V.T['rayon'], cy=520)
# ================= 3. rayon : vraies ou fausses promos =================
def b_rayon(cv, c, t, k):
    t0 = V.T['rayon']; arr = np.asarray(cv.convert('RGB')); box = tag_box(arr, t)
    if box: tag_text(c, box, t)
    if t > sh(44.4) and t < sh(47.4):
        value_card(cv, t, sh(44.45), sh(47.4), "BLACK FRIDAY 2025 · 314 SITES CONTRÔLÉS", f"30{NB}%", [(sh(44.5), "des promos hors des règles (Commission européenne)")], cy=300, h=230, vsize=96)
# ================= 4. bureau d'enquêteur : penser comme un investisseur =================
def b_enquete(cv, c, t, k):
    t0 = V.T['enquete']
    if t < sh(54.1):
        plate(c, 540, 340, 980, 160, ent(t-t0-.1, .3)*(1-ent(t-sh(53.9), .3)))
        pop_text(c, "PENSE COMME UN INVESTISSEUR", 540, 340, 56, t, t0+.2, YEL, maxw=920, a=1-ent(t-sh(53.9), .3))
        if t > t0+.6: EMO.append(('🔍', 900, 250, 60, ent(t-t0-.6, .3)*(1-ent(t-sh(53.9), .3))))
        return
    if t < sh(60.5):
        reflex(cv, t, sh(54.2), sh(60.5), "1", "Ta liste avant", "= ta liste de surveillance")
        if t > sh(57.3): value_card(cv, t, sh(57.3), sh(60.5), "EXEMPLE", "La télé qu'il te faut", [(sh(58.85), "pas celle de la pub")], cy=620, h=230, vsize=58)
        if t > sh(57.5) and t < sh(60.3): EMO.append(('📺', 160, 530, 64, ent(t-sh(57.5), .3)*(1-ent(t-sh(60.2), .3))))
    elif t < sh(67.75):
        reflex(cv, t, sh(60.6), sh(67.75), "2", "L'historique du prix", "= le graphique d'une action")
        if t > sh(62.7): price_chart(cv, t, sh(62.75), sh(67.75), cy=650)
    else:
        reflex(cv, t, sh(67.85), V.T['vitrine'], "3", "Ton budget avant", "= ton allocation")
        if t > sh(70.6):
            value_card(cv, t, sh(70.65), V.T['vitrine'], "TON BUDGET", f"200{NB}€", [(sh(70.7), "et pas un compte à rebours")], cy=620, h=240)
            if t > sh(71.4): EMO.append(('⏱️', 880, 850, 72, ent(t-sh(71.4), .3)))
            if t > sh(71.6): cross(c, 880, 850, 50, (t-sh(71.6))/.5)
# ================= 5. vitrine : la question finale =================
def b_vitrine(cv, c, t, k):
    t0 = V.T['vitrine']
    plate(c, 540, 380, 980, 300, ent(t-t0-.1, .25))
    title(c, "UNE BONNE AFFAIRE ?", t, t0+.15, 320, 64, CREAM)
    title(c, "SEULEMENT SI TU EN AVAIS BESOIN AVANT LA PROMO", t, sh(75.6), 420, 34, CREAM, maxw=900)
    if t > sh(77.2):
        plate(c, 540, 590, 900, 130, ent(t-sh(77.2), .25)); pop_text(c, "ET TOI, TU VAS CRAQUER ?", 540, 590, 58, t, sh(77.25), YEL, maxw=860)
    if t > t0+.6:
        a = ent(t-t0-.6, .4); plate(c, 540, 860, 1030, 110, a*.9)
        paint(c, "Sources : Commission européenne, DGCCRF, Joko, Insee", 540, 840, 25, a=a)
        paint(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 882, 25, a=a)
T_ = V.T
SC = [(0.0, T_['hall'], b_rue, 'rue'), (T_['hall'], T_['rayon'], b_hall, 'hall'), (T_['rayon'], T_['enquete'], b_rayon, 'rayon'),
      (T_['enquete'], T_['vitrine'], b_enquete, 'enquete'), (T_['vitrine'], DUR, b_vitrine, 'vitrine')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
BLOCS_MIX = BLOCS
IRIS = [s_[0] for s_ in SC[1:]]
MCX = [(0, 540), (V.T['hall'], 330), (V.T['rayon'], 540)]     # hall : à gauche, sur le sol (le comptoir est à droite)
SEAT = 1500                                                   # bord avant du plateau du bureau (décor enquête, à affiner sur la maquette)
SEAT_DY = {'classique_parle_compte_doigts': 136, 'classique_loupe_parle': 154}   # des pieds pendants au bas de la pièce, mesuré sur chaque clip (échelle commune) : la pièce repose sur le bord
def clip_at(t):
    s0, seq = V.MC._global_sequence(); i = min(len(seq)-1, max(0, int(t*24)-s0)); return seq[i][0]
import json
def _bord():
    """bord avant du plateau du bureau (y à l'écran) image par image du décor d'origine, lissé (polynôme), mis en cache"""
    p = f'{D}/decors/enquete_bord.json'
    if os.path.exists(p): return np.poly1d(json.load(open(p)))
    cap = cv2.VideoCapture(f'{D}/decors/decor_enquete.mp4'); E = []
    for i in range(NMAX['enquete']):
        ok, f = cap.read()
        if not ok: break
        g = cv2.cvtColor(cv2.resize(f, (W, H)), cv2.COLOR_BGR2GRAY).astype(float); z = ZOOM_TOP['enquete']
        g = cv2.resize(g, (int(W*z), int(H*z)))[:H, (int(W*z)-W)//2:(int(W*z)-W)//2+W]
        pr = np.convolve(g[1250:1850, 380:700].mean(1), np.ones(9)/9, 'same'); d = pr[8:]-pr[:-8]; E.append(1254+int(np.argmin(d[10:-10]))+10)
    c = np.polyfit(np.arange(len(E)), E, 3).tolist(); json.dump(c, open(p, 'w')); return np.poly1d(c)
BORD = None
def seat_feet(t):
    global BORD
    if BORD is None: BORD = _bord()
    a, b = V.T['enquete'], V.T['vitrine']; sp = (NMAX['enquete']-1)/24/(b-a); i = clamp(t-a, 0, b-a)*sp*24
    return int(BORD(i))+SEAT_DY.get(clip_at(t), 136)-12
# Mister Coin de dos qui marche pendant les travellings (hall, puis vitrine jusqu'à la question finale) : clip classique_dos_marche en boucle sur deux pas
DOS = [];                     # marche de dos abandonnée (23/11) : marche de face en parlant (clips danse_parle)
DOS_CLIP = f'{S.ROOT}/mister_coin/veo/classique_dos_marche.mp4'; DOS_L0, DOS_L1 = 61, 128
class _Dos:
    def __init__(s): s.cap = None; s.i = -1; s.f = None
    def get(s, n):
        if s.cap is None or n < s.i: s.cap = cv2.VideoCapture(DOS_CLIP); s.i = -1
        while s.i < n:
            ok, fr = s.cap.read(); s.i += 1
            if ok: s.f = fr
        return s.f
_DS = _Dos()
def dos_at(t): return next(((a, b, x) for (a, b, x) in DOS if a <= t < b), None)
def dos_col(cv_rgb, t, a, X):
    n = 40+int((t-a)*24)
    if n >= DOS_L1: n = DOS_L0+(n-DOS_L0) % (DOS_L1-DOS_L0)
    rgb_, m = VC._key(_DS.get(n)[..., ::-1].copy()); sc = 170/314
    rgb_ = cv2.resize(rgb_.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA); m = cv2.resize(m.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    x0, y0 = int(X-360*sc), int(V.FEET-1035*sc); h, w = m.shape
    sh_ = np.zeros((H, W), np.float32); cv2.ellipse(sh_, (X, V.FEET-3), (95, 15), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(sh_, (0, 0), 9)[..., None])
    ya, yb_, xa, xb = max(0, y0), min(H, y0+h), max(0, x0), min(W, x0+w)
    mm = m[ya-y0:yb_-y0, xa-x0:xb-x0][..., None]; cv_rgb[ya:yb_, xa:xb] = cv_rgb[ya:yb_, xa:xb]*(1-mm)+rgb_[ya-y0:yb_-y0, xa-x0:xb-x0]*mm
    return cv_rgb
def feet(t):
    a, b = V.ASSIS
    if a-.25 <= t < a+.25:                                    # il saute du sol au bord du bureau (arc), pendant le fondu
        u = inout((t-(a-.25))/.5); return int(lerp(V.FEET, seat_feet(a+.3), u)-140*math.sin(math.pi*u))
    if a+.25 <= t < b-.25: return seat_feet(t)
    if b-.25 <= t < b+.25:
        u = inout((t-(b-.25))/.5); return int(lerp(seat_feet(b-.3), V.FEET, u)-100*math.sin(math.pi*u))
    return V.FEET
def coin_col(cv_rgb, t):
    d_ = dos_at(t)
    if d_: return dos_col(cv_rgb, t, d_[0], d_[2])
    F = feet(t); Y = F+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, mcx(t), Y)
    a, b = V.ASSIS; seated = a+.25 <= t < b-.25
    fx = V.MC.feet_x(al, Y) if not seated else mcx(t)
    if fx is not None:
        sy = F-3 if not seated else SEAT+4; m = np.zeros((H, W), np.float32)
        cv2.ellipse(m, (int(fx), int(sy)), (95, 15) if not seated else (110, 12), 0, 0, 360, .5, -1); cv_rgb *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    return cv_rgb*(1-al[..., None])+rgb_.astype(np.float32)*al[..., None]
def raw_bg(t):
    """décor + plaques et textes de la scène (sans Mister Coin, sans pellicule, sans sous-titres) : c'est ce qui se fond aux changements de scène"""
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
    return np.asarray(cv.convert('RGB')).astype(np.float32)
XF = .3                                                       # fondu enchaîné aux changements de décor (Mister Coin posé ensuite : jamais en double)
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
    ev = list(V.events()) + [(ta-XF/2, 'whoosh') for ta in IRIS]
    T = V.T
    ev += [(.0, 'impact'), (.8, 'pop'), (7.4, 'pop'), (15.4, 'thud'), (17.07, 'impact'), (17.95, 'pop'), (T['hall']+.2, 'pop')]
    ev += [(sh(26.09), 'tick'), (sh(27.2), 'tick'), (sh(27.9), 'tick'), (sh(28.6), 'glint'), (sh(30.91), 'pop'), (sh(34.75), 'pop'), (sh(35.6), 'pop'), (sh(36.54), 'pop')]
    ev += [(sh(38.6), 'swish'), (sh(44.45), 'impact'), (sh(47.6), 'swish'), (T['enquete']+.2, 'pop'), (sh(54.2), 'pop'), (sh(60.6), 'pop'), (sh(62.75), 'swish'),
           (sh(64.28), 'tick'), (sh(67.85), 'pop'), (sh(70.65), 'pop'), (sh(71.6), 'thud'), (T['vitrine']+.15, 'thud'), (sh(77.25), 'impact')]
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
