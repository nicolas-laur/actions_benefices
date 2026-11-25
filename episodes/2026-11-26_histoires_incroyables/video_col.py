"""3 histoires incroyables que tu ne connaissais peut-être pas ! (26/11/2026), cartoon 1930 en Technicolor : prêteur sur gages (accroche et chute),
garage d'Apple, bibliothèque de Google, cinéma de Netflix ; plaques de verre, tuiles logos, Polaroïds des fondateurs, étiquette de prix qui grimpe
jusqu'à la valeur d'aujourd'hui, tampons « REFUSÉ », Mister Coin debout sur le comptoir et l'établi puis marchant de face dans les allées.
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
# ================= 1. prêteur sur gages : l'accroche =================
def b_preteur(cv, c, t, k):
    t1 = 2.85; a = 1-ent(t-t1, .3) if t > t1 else 1
    if t < t1+.3:
        plate(c, 540, 420, 1000, 360, a*ent(t+.2, .3))
        title(c, "TU VENDRAIS", t, -.4, 300, 54, CREAM, t1=t1)
        tile(c, 'apple', 880, 330, 112, t, .1, a=a)
        title(c, f"10{NB}% D'APPLE", t, -.25, 400, 104, YEL, t1=t1)
        title(c, f"POUR 800{NB}$ ?", t, .9, 515, 92, YEL, t1=t1)
    if 2.95 < t < 9.9:
        tt = sh(3.0)
        a2 = ent(t-tt, .3)*(1-ent(t-(sh(6.4)), .3))
        if a2 > 0:
            plate(c, 540, 430, 1000, 420, a2)
            pop_text(c, "3 HISTOIRES", 540, 300, 84, t, tt, YEL, a=a2)
            pop_text(c, "INCROYABLES", 540, 395, 84, t, tt+.15, YEL, a=a2)
            for i, n in enumerate(('apple', 'google', 'netflix')): tile(c, n, 540+(i-1)*230, 560, 160, t, sh(3.9)+i*.35, a=a2)
        if t > sh(6.45):                                                       # invitation : trois grandes pastilles (aime, enregistre, partage), en rebond l'une après l'autre
            a3 = ent(t-sh(6.45), .3)*(1-ent(t-9.75, .25)); plate(c, 540, 470, 1000, 470, a3)
            for i, (e, lab, ti) in enumerate((('❤️', "AIME", sh(6.55)), ('🔖', "ENREGISTRE", sh(7.25)), ('📤', "PARTAGE", sh(8.1)))):
                x = 540+(i-1)*315; k_ = ent(t-ti, .25)
                if k_ > 0: EMO.append((e, x, 400, int(150*back((t-ti)/.35)), a3*k_)); pop_text(c, lab, x, 560, 46 if i != 1 else 42, t, ti+.05, YEL, a=a3, maxw=290)
            pop_text(c, "la vidéo", 540, 645, 40, t, sh(6.9), CREAM, a=a3)
# ================= 2. garage : Apple, 1976 =================
def b_garage(cv, c, t, k):
    t0 = V.T['garage']
    if t < sh(13.7): year_card(cv, c, t, t0+.1, sh(13.75), 1, 'apple', "1976")
    if sh(13.75) < t < sh(20.3):
        aa = 1-ent(t-sh(20.0), .3)
        polaroid(c, 'jobs', "Steve Jobs", 205, 470, 260, t, sh(13.84), rot=-.06, a=aa)
        polaroid(c, 'wozniak', "Steve Wozniak", 875, 470, 260, t, sh(14.75), rot=.05, a=aa)
        polaroid(c, 'wayne', "Ronald Wayne", 540, 420, 300, t, sh(15.6), rot=.0, a=aa, hl=True)
        if t > sh(17.3): EMO.append(('😰', 700, 230, 72, ent(t-sh(17.3), .3)*aa))
        if t > sh(17.6):
            a4 = ent(t-sh(17.6), .3)*aa; plate(c, 540, 830, 700, 100, a4); pop_text(c, "peur des dettes", 540, 830, 50, t, sh(17.6), CREAM, a=a4)
    if sh(20.3) < t < sh(24.0):
        value_card(cv, t, sh(20.35), sh(23.95), "12 JOURS APRÈS LA CRÉATION", f"10{NB}% → 800{NB}$", [(sh(20.4), "revendus à Jobs et Wozniak")], cy=420, vsize=104)
        if t > sh(21.8): polaroid(c, 'wayne', "Ronald Wayne", 540, 760, 200, t, sh(21.8), rot=-.04, a=1-ent(t-sh(23.8), .3))
    if t > sh(24.0):
        price_tag(cv, c, t, sh(24.0), V.T['bibliotheque'], 800, SC_PRICES['apple'], sh(24.2), sh(25.6), "LA VALEUR D'APPLE AUJOURD'HUI", "capitalisation boursière au 24/11/2026", cy=470, logo='apple', final=f"5{NB}145{NB}milliards{NB}$")
# ================= 3. bibliothèque : Google, 1999 =================
def b_bibliotheque(cv, c, t, k):
    t0 = V.T['bibliotheque']
    if t < sh(29.6): year_card(cv, c, t, t0+.1, sh(29.65), 2, 'google', "1999")
    if sh(29.65) < t < sh(36.1):
        aa = 1-ent(t-sh(35.9), .3)
        polaroid(c, 'page', "Larry Page", 330, 450, 280, t, sh(30.4), rot=-.05, a=aa)
        polaroid(c, 'brin', "Sergey Brin", 750, 450, 280, t, sh(31.3), rot=.05, a=aa)
        if t > sh(34.3):
            a4 = ent(t-sh(34.3), .3)*aa; plate(c, 540, 800, 800, 120, a4)
            pop_text(c, "EXCITE", 540, 782, 50, t, sh(34.3), YEL, a=a4); paint(c, "un géant d'internet en 1999", 540, 830, 28, a=a4)
    if sh(36.1) < t < sh(42.6):
        def d(kk, ww, hh):
            S.text(kk, "LE PRIX DEMANDÉ À EXCITE", ww/2, 50, 'xb', 30, S.ICE, 'c', .95, 3)
            u1 = ent(t-sh(36.25), .3); S.text(kk, f"1{NB}000{NB}000{NB}$", ww/2, 150, 'a', 84 if t < sh(38.95) else 60, S.GD if t < sh(38.95) else S.ICE, 'c', u1)
            if t > sh(38.95): S.text(kk, f"750{NB}000{NB}$", ww/2, 255, 'a', 92, S.GD, 'c', ent(t-sh(38.95), .3))
        glass_card(cv, t, sh(36.15), d, cy=520, w=860, h=330, t1=sh(42.6))
        aa = 1-ent(t-sh(42.3), .3)
        if t > sh(38.95):                                                   # premier prix barré
            u = clamp((t-sh(38.95))/.35); c.set_line_width(9); col(c, 'F3F1E8', .9*aa); c.move_to(540-230, 520-165+150); c.line_to(540-230+460*u, 520-165+150); c.stroke()
        stamp(c, "REFUSÉ", 760, 430, 62, t, sh(38.21), rot=.16, a=aa*(1-ent(t-sh(38.95), .25)) if t < sh(41.4) else 0)
        stamp(c, "REFUSÉ", 700, 640, 70, t, sh(41.41), rot=-.12, a=aa)
    if sh(42.6) < t < sh(43.9):
        a4 = ent(t-sh(42.66), .3)*(1-ent(t-sh(43.85), .3)); plate(c, 540, 470, 900, 300, a4)
        pop_text(c, "CE MOTEUR,", 540, 380, 56, t, sh(42.66), CREAM, a=a4); pop_text(c, "C'EST GOOGLE", 540, 470, 88, t, sh(43.55), YEL, a=a4)
    if t > sh(43.9):
        price_tag(cv, c, t, sh(43.9), V.T['cinema'], 750000, SC_PRICES['alphabet'], sh(44.1), sh(45.3), "LA VALEUR DE GOOGLE AUJOURD'HUI", "Alphabet, capitalisation boursière au 24/11/2026", cy=470, logo='google', final=f"3{NB}430{NB}milliards{NB}$")
# ================= 4. cinéma : Netflix, 2000 =================
def b_cinema(cv, c, t, k):
    t0 = V.T['cinema']
    if t < sh(51.75): year_card(cv, c, t, t0+.1, sh(51.8), 3, 'netflix', "2000")
    if sh(48.6) < t < sh(51.9):
        a4 = ent(t-sh(48.61), .3)*(1-ent(t-sh(51.7), .3)); plate(c, 540, 650, 900, 200, a4)
        pop_text(c, "DES DVD PAR LA POSTE", 540, 620, 60, t, sh(48.65), YEL, a=a4, maxw=760); paint(c, "et une entreprise qui perd de l'argent", 540, 690, 32, a=a4*ent(t-sh(50.0), .3))
        EMO.append(('📀', 150, 650, 64, a4)); EMO.append(('✉️', 930, 650, 64, a4))
    if sh(51.9) < t < sh(55.6):
        aa = 1-ent(t-sh(55.4), .3)
        polaroid(c, 'hastings', "Reed Hastings", 300, 430, 250, t, sh(52.0), rot=-.05, a=aa)
        polaroid(c, 'randolph', "Marc Randolph", 780, 430, 250, t, sh(52.6), rot=.05, a=aa)
        if t > sh(54.1):
            a5 = ent(t-sh(54.1), .3)*aa; plate(c, 540, 770, 860, 120, a5)
            pop_text(c, "BLOCKBUSTER", 540, 752, 50, t, sh(54.1), YEL, a=a5); paint(c, "le roi de la location vidéo", 540, 800, 28, a=a5)
        if t > sh(55.6): EMO.append(('🎬', 900, 770, 60, ent(t-sh(55.6), .3)*aa))
    if sh(55.55) < t < sh(60.3):
        value_card(cv, t, sh(55.6), sh(60.3), "LE PRIX PROPOSÉ À BLOCKBUSTER", f"50{NB}millions{NB}$", [(sh(55.65), "pour racheter Netflix")], cy=430, vsize=96)
        if t > sh(57.61): stamp(c, "REFUSÉ", 760, 640, 64, t, sh(57.7), rot=.14, a=1-ent(t-sh(60.1), .3)); EMO.append(('😂', 320, 640, 72, ent(t-sh(58.6), .3)*(1-ent(t-sh(60.1), .3))))
    if sh(60.3) < t < sh(62.95):
        value_card(cv, t, sh(60.42), sh(62.95), "10 ANS PLUS TARD · 2010", "FAILLITE", [(sh(60.5), "pour Blockbuster")], cy=430, vsize=110)
    if t > sh(62.95):
        price_tag(cv, c, t, sh(62.95), V.T['fin'], 50e6, SC_PRICES['netflix'], sh(63.1), sh(64.25), "LA VALEUR DE NETFLIX AUJOURD'HUI", "capitalisation boursière au 24/11/2026", cy=470,
                  extra=(f"soit ×{NB}{num(SC_PRICES['netflix']/50e6, 0)} le prix de 2000", sh(64.6)), logo='netflix', final=f"234,9{NB}milliards{NB}$")
# ================= 5. prêteur sur gages, le soir : la chute =================
def b_fin(cv, c, t, k):
    t0 = V.T['fin']
    a1 = ent(t-sh(66.1), .3)*(1-ent(t-sh(70.55), .3))
    if a1 > 0:
        plate(c, 540, 430, 1000, 420, a1)
        pop_text(c, "1 ACTION =", 540, 290, 58, t, sh(66.1), CREAM, a=a1); pop_text(c, "UN MORCEAU D'ENTREPRISE", 540, 375, 66, t, sh(66.9), YEL, a=a1, maxw=840)
        for i, (n, p_) in enumerate((('apple', f"800{NB}$"), ('google', f"750{NB}000{NB}$"), ('netflix', f"50{NB}M{NB}$"))):
            x = 540+(i-1)*300; tile(c, n, x, 520, 120, t, sh(68.55)+i*.3, a=a1)
            if t > sh(68.7)+i*.3: paint(c, p_, x, 615, 34, YEL, a=a1*ent(t-sh(68.7)-i*.3, .3))
    if t > sh(70.6):
        a2 = ent(t-sh(70.6), .3); plate(c, 540, 380, 1000, 300, a2)
        pop_text(c, "ET TOI ?", 540, 300, 84, t, sh(70.65), YEL, a=a2)
        pop_text(c, "QUELLE ENTREPRISE TU REGRETTERAIS", 540, 395, 44, t, sh(71.2), CREAM, a=a2, maxw=920)
        pop_text(c, "DE NE PAS AVOIR ACHETÉE ?", 540, 455, 44, t, sh(72.0), CREAM, a=a2, maxw=920)
        a3 = ent(t-sh(72.6), .4); plate(c, 540, 860, 1030, 110, a3*.9)
        paint(c, "Sources : Fortune, CNBC, Marketplace, cours du 24/11/2026", 540, 840, 25, a=a3)
        paint(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 882, 25, a=a3)
T_ = V.T
SC = [(0.0, T_['garage'], b_preteur, 'preteur'), (T_['garage'], T_['bibliotheque'], b_garage, 'garage'), (T_['bibliotheque'], T_['cinema'], b_bibliotheque, 'bibliotheque'),
      (T_['cinema'], T_['fin'], b_cinema, 'cinema'), (T_['fin'], DUR, b_fin, 'preteur')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
BLOCS_MIX = BLOCS
# images source de chaque passage (i0, i1) : prêteur, début du travelling ; bibliothèque, après la table du premier plan ; cinéma, après la descente depuis la cabine
SRC = {('preteur', 0.0): (40, 120), ('garage', round(T_['garage'], 2)): (0, 239), ('bibliotheque', round(T_['bibliotheque'], 2)): (110, 239),
       ('cinema', round(T_['cinema'], 2)): (45, 239), ('preteur', round(T_['fin'], 2)): (100, 160)}
IRIS = [s_[0] for s_ in SC[1:]]
import json
_PIEDS = {}
SEAT_DY = {'classique_parle_compte_doigts': 136, 'classique_loupe_parle': 154}   # des pieds pendants au bas de la pièce, mesuré sur chaque clip (échelle commune) : la pièce repose sur le bord
def clip_at(t): return V.MC.clip(t)
def bord_preteur(t, a, b):
    """bord avant du comptoir à l'écran (suivi image par image du décor d'origine, lissé : decors/preteur_bord.json)"""
    if 'p' not in _PIEDS: _PIEDS['p'] = np.poly1d(json.load(open(f'{D}/decors/preteur_bord.json'))['poly'])
    return float(_PIEDS['p'](src_index('preteur', a, b, t)))
def pieds_preteur(t, a, b):
    """assis au bord du comptoir, jambes pendantes : la pièce repose sur le bord, suivi image par image pendant le travelling"""
    return bord_preteur(t, a, b)+SEAT_DY.get(clip_at(t), 136)-12
_BG = None
def pieds_garage(t, a, b):
    """pieds sur l'établi, juste derrière son bord avant (bords.py, suivi image par image puis lissé)"""
    global _BG
    if _BG is None: _BG = np.poly1d(json.load(open(f'{D}/decors/garage_bord.json'))['poly'])
    return float(_BG(src_index('garage', a, b, t)))-22
def ground(t):
    a, b, d = next((a, b, d) for (a, b, d) in BLOCS[::-1] if t >= a)
    if d == 'preteur': return pieds_preteur(t, a, b)
    if d == 'garage': return pieds_garage(t, a, b)
    return V.FEET
def feet(t):
    for ta in IRIS:                                            # saut d'un décor à l'autre (arc), pendant le fondu
        if ta-.25 <= t < ta+.25:
            u = inout((t-(ta-.25))/.5); return int(lerp(ground(ta-.26), ground(ta+.26), u)-120*math.sin(math.pi*u))
    return int(ground(t))
MCX = [(0, 540)]
def coin_col(cv_rgb, t):
    F = feet(t); r = _rx_layer(t, mcx(t), F)
    if r is None: Y = F+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, mcx(t), Y)
    else: Y = F; rgb_, al = r
    a, b, d = next((a, b, d) for (a, b, d) in BLOCS[::-1] if t >= a)
    seated = d == 'preteur' and all(not (ta-.25 <= t < ta+.25) for ta in IRIS)
    fx = V.MC.feet_x(al, Y) if not seated else mcx(t)
    if fx is not None:
        sy = F-3 if not seated else bord_preteur(t, a, b)+4; m = np.zeros((H, W), np.float32)
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
    ev += [(.0, 'impact'), (.9, 'pop'), (sh(3.0), 'pop'), (sh(3.9), 'tick'), (sh(4.25), 'tick'), (sh(4.6), 'tick'), (sh(6.5), 'pop'),
           (T['garage']+.1, 'impact'), (sh(13.84), 'shutter'), (sh(14.75), 'shutter'), (sh(15.6), 'shutter'), (sh(20.35), 'pop'), (sh(23.72), 'bonk'),
           (sh(24.0), 'swish'), (sh(24.2), 'riser'), (sh(25.6), 'tadaa'),
           (T['bibliotheque']+.1, 'impact'), (sh(30.4), 'shutter'), (sh(31.3), 'shutter'), (sh(34.3), 'pop'), (sh(36.25), 'tick'), (sh(38.21), 'thud'), (sh(38.95), 'swish'),
           (sh(41.41), 'thud'), (sh(42.66), 'pop'), (sh(43.9), 'swish'), (sh(44.1), 'riser'), (sh(45.3), 'tadaa'),
           (T['cinema']+.1, 'impact'), (sh(48.65), 'pop'), (sh(52.0), 'shutter'), (sh(52.6), 'shutter'), (sh(54.1), 'pop'), (sh(55.6), 'pop'), (sh(57.7), 'thud'),
           (sh(60.42), 'impact'), (sh(62.95), 'swish'), (sh(63.1), 'riser'), (sh(64.25), 'tadaa'),
           (sh(66.1), 'pop'), (sh(68.55), 'tick'), (sh(68.85), 'tick'), (sh(69.15), 'tick'), (sh(70.65), 'impact')]
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
