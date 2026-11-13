"""Combien placer par mois pour devenir millionnaire ? (14/11/2026), cartoon 1930 en Technicolor : décors Gemini (rayons art déco,
chambre, haricot magique, gare, hall de banque, haricot géant), accessoires Gemini détourés, Mister Coin en couleurs (gros plan aux yeux en étoiles
sur le « wow »), pellicule, iris aux changements de décor.
usage : python3 video_col.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
import video as V
import veo_coin as VC
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
    return np.clip((g-128)*1.06+130, 0, 255)
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
# ================= gros plan aux yeux en étoiles (clip Gemini 9:16, détouré) =================
GP_CLIP = f'{D}/coin/gros_plan_etoiles.mp4'; GP_T0 = 1.22                     # image du clip au début du gros plan (zoom avant fini, étoiles juste après)
_GPF = {}
def gp_frame(n):
    if not _GPF:
        cap = cv2.VideoCapture(GP_CLIP)
        while True:
            ok, f = cap.read()
            if not ok: break
            _GPF[len(_GPF)] = f
    return _GPF[min(n, len(_GPF)-1)]
def closeup(arr, t):
    """coupe franche : Mister Coin en gros plan sur les rayons, les étoiles s'allument au moment du « wow »"""
    u = t-V.GP[0]; n = int((GP_T0+u)*24)
    rgb_, m = VC._key(gp_frame(n)[..., ::-1].copy())
    sc = W/rgb_.shape[1]*.96; rgb_ = cv2.resize(rgb_.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    m = cv2.resize(m.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    pulse = 1+.025*math.sin(u*18)*math.exp(-u*2)                               # petit tremblement d'émerveillement
    h, w = m.shape; x0 = int(W/2-w/2); y0 = int(530-(pulse-1)*400)                 # le bas de la pièce sort du cadre : on ne voit pas qu'il n'a pas de jambes
    out = arr.copy(); ya, yb, xa, xb = max(0, y0), min(H, y0+h), max(0, x0), min(W, x0+w)
    mm = m[ya-y0:yb-y0, xa-x0:xb-x0][..., None]; out[ya:yb, xa:xb] = out[ya:yb, xa:xb]*(1-mm)+rgb_[ya-y0:yb-y0, xa-x0:xb-x0]*mm
    return out
# ================= 1. accroche (rayons) =================
def b_hook(cv, c, t, k):
    title(c, "COMMENT DEVENIR", t, .05, 230, 66)
    title(c, "MILLIONNAIRE ?", t, .45, 320, 88, YEL)
    if t > 1.95:                                                               # le chiffre tombe
        pop_text(c, f"402{NB}€", 540, 520, 180, t, 2.0, YEL, rot=-.03)
        pop_text(c, "PAR MOIS", 540, 665, 60, t, 2.45, CREAM)
    if t > 4.85: pop_text(c, "=", 540, 755, 64, t, 4.9)
    if t > 5.05:                                                               # « … pour devenir millionnaire »
        pop_text(c, f"1{NB}000{NB}000{NB}€", 540, 860, 96, t, 5.1, YEL, rot=-.02)
        prop(c, 'pluie_pieces', 165, 700, h=280, k=t-5.15, rot=-.15+.05*math.sin(t*2), shadow=False)
        prop(c, 'pluie_pieces', 915, 700, h=280, k=t-5.25, rot=.2+.05*math.sin(t*2.3), shadow=False)
        twinkle(c, t, [(250, 420), (840, 430), (540, 960)], 24)
# ================= 2. commencer à 25 ans (chambre) =================
CAL = (611, 1022, 900)                                                       # zone vierge de la page de calendrier (coordonnées de l'accessoire)
def calendar(c, x, y, h, t, k, label, sub=None, tear=None):
    sf, iw, ih = psurf('page_calendrier'); s = h/ih*back(k/.35)
    if s <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s); c.set_source_surface(sf, -iw/2, -ih/2); c.paint()
    ink(c, label, CAL[0]-iw/2, CAL[1]-ih/2-60, 250, RED, maxw=760)
    if sub: ink(c, sub, CAL[0]-iw/2, CAL[1]-ih/2+170, 90, BROWN, maxw=760)
    c.restore()
    if tear:                                                                   # la page arrachée s'envole en tournoyant
        lab, u = tear; sx = x+u*520; sy = y-u*380+u*u*900; c.save(); c.translate(sx, sy); c.rotate(u*2.4); c.scale(s*(1-.3*u), s*(1-.3*u))
        c.set_source_surface(sf, -iw/2, -ih/2); c.paint_with_alpha(1-u*u); ink(c, lab, CAL[0]-iw/2, CAL[1]-ih/2-60, 250, RED, a=1-u*u, maxw=760); c.restore()
def b_chambre(cv, c, t, k):
    t0 = tm(6.0)
    title(c, "UNE CONDITION", t, t0+.1, 230, 70)
    age = 25; tear = None
    tf = tm(8.95)                                                              # « et ne jamais t'arrêter » : les années défilent jusqu'à 65 ans
    if t > tf:
        p = clamp((t-tf)/2.6); f = 40*inout(p); age = 25+int(f); fr = f-int(f)
        if age < 65 and p < 1: tear = (f"{age} ANS", fr); age += 1
    calendar(c, 540, 660, 600, t, t-(t0+.4), f"{age} ANS", "tu commences" if age == 25 else ("ton million" if age == 65 else None), tear)
    if t > t0+1.0:                                                            # la tirelire reçoit 402 € chaque mois
        prop(c, 'tirelire', 230, 1330, w=300, k=t-(t0+1.05))
        paint(c, f"402{NB}€ / mois", 230, 1530, 40, YEL, a=ent(t-(t0+1.3), .3))
        for i in range(12):
            kk = (t-(t0+1.4)-i*.38)
            if 0 < kk < .5: u = kk/.5; c.arc(230-40+20*u, 1110+u*u*120, 18, 0, 2*math.pi); col(c, 'F2B82E'); c.fill_preserve(); c.set_line_width(3); col(c, BROWN); c.stroke()
# ================= 3. intérêts composés (haricot magique) =================
def counter_glass(cv, t, t0, a=1.0):
    k = t-t0
    def d(kk, w, h):
        v = 1e6*inout((t-t0-.2)/1.6)
        S.text(kk, euro(v), w/2, h/2-8, 'a', 92, S.GD, 'c', ent(k, .3))
        S.text(kk, "à 65 ans, avec 402 € par mois dès 25 ans", w/2, h-34, 'sb', 24, S.ICE, 'c', .8*ent(k-.3, .3))
    S.tp(cv, 860, 230, d, 540, 470+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=26)
def split_glass(cv, t, t0):
    """barre empilée : ce que tu as versé (bleu) contre les intérêts composés (or)"""
    k = t-t0
    if k <= 0: return
    def d(kk, w, h):
        x0, x1 = 70, w-70; y = 150; bh = 130; L = x1-x0
        u1 = inout((t-t0-.2)/.8); u2 = inout((t-tm(18.6))/1.4)
        bw1 = L*.193*u1; bw2 = L*.807*u2
        rr(kk, x0, y, max(2, bw1), bh, 14); g = cairo.LinearGradient(0, y, 0, y+bh); g.add_color_stop_rgba(0, .45, .65, 1, .95); g.add_color_stop_rgba(1, .2, .35, .8, .95); kk.set_source(g); kk.fill()
        if bw2 > 2:
            rr(kk, x0+bw1+6, y, bw2-6, bh, 14); g = cairo.LinearGradient(0, y, 0, y+bh)
            for st, cc in ((0, 'FFE27A'), (.55, 'F2B82E'), (1, 'B97A12')): r_, g_, b_ = rgb(cc)[:3]; g.add_color_stop_rgba(st, r_, g_, b_, .97)
            kk.set_source(g); kk.fill()
        S.text(kk, f"193{NB}000{NB}€", x0+8, y-46, 'a', 46, '7FB2FF', 'l', ent(t-t0-.3, .3)); S.text(kk, "versés", x0+8, y+bh+40, 'sb', 28, S.ICE, 'l', .85*ent(t-t0-.4, .3))
        if t > tm(18.6):
            S.text(kk, f"807{NB}000{NB}€", x1-8, y-46, 'a', 56, S.GD, 'r', ent(t-tm(18.7), .3))
            S.text(kk, "intérêts composés", x1-8, y+bh+40, 'xb', 30, S.GD, 'r', ent(t-tm(20.2), .3))
    S.tp(cv, 900, 400, d, 540, 640+30*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def b_haricot(cv, c, t, k):
    t0 = tm(10.5)
    title(c, f"7{NB}% PAR AN", t, t0, 230, 84, YEL, t1=tm(14.95))
    if t > tm(12.0) and t < tm(15.2): paint(c, "en moyenne, hypothèse non garantie", 540, 320, 30, a=fade(t, tm(12.0), tm(14.95)), fam='Limelight')
    if tm(12.9) < t < tm(15.05): counter_glass(cv, t, tm(12.95)) if t < tm(14.75) else _fade(cv, lambda x: counter_glass(x, t, tm(12.95)), 1-ent(t-tm(14.75), .3))
    if t > tm(15.0):
        title(c, "LE PLUS FOU", t, tm(15.05), 230, 74, t1=tm(21.4))
        split_glass(cv, t, tm(15.6))
    if t > tm(21.5):
        title(c, "TES GAINS", t, tm(21.55), 230, 74, YEL)
        title(c, "FONT DES GAINS", t, tm(22.4), 320, 64, CREAM)
        split_glass(cv, t, tm(15.6))
        twinkle(c, t, [(300, 560), (700, 590), (520, 760), (820, 720)], 26)
def _fade(cv, f, a):
    tmp = cv.copy(); f(tmp); cv.paste(Image.blend(cv.convert('RGBA'), tmp.convert('RGBA'), clamp(a)))
# ================= 4. plus tu attends, plus ça coûte (gare) =================
def b_gare(cv, c, t, k):
    t0 = tm(24.5)
    title(c, "ET SI TU ATTENDS ?", t, t0+.05, 230, 70, t1=tm(34.95))
    xs = (190, 470, 815); hs = (170, 250, 380)
    for i, (age, m, ta, tb) in enumerate(((25, 402, tm(24.55), tm(24.6)), (35, 850, tm(24.9), tm(26.6)), (45, 1959, tm(30.05), tm(31.05)))):
        if t < ta: continue
        x = xs[i]; base = 830
        prop(c, 'tirelire', x, base-hs[i]/2, h=hs[i], k=t-ta)
        if t > tb: pop_text(c, euro(m) if i < 2 else euro(m), x, base+50, 46 if i < 2 else 54, t, tb, YEL if i < 2 else PINK)
        if t > ta+.2: paint(c, f"dès {age} ans", x, base+102, 32, CREAM if i < 2 else PINK, a=ent(t-ta-.2, .3))
    if t > tm(28.55): pop_text(c, "× 2,1", 470, 520, 54, t, tm(28.6), YEL, rot=-.06)
    if t > tm(33.4): pop_text(c, "× 4,9", 815, 390, 66, t, tm(33.45), PINK, rot=-.06)
    if t > tm(35.0):
        title(c, "10 ANS D'ATTENTE", t, tm(35.05), 230, 70)
        title(c, "= L'EFFORT × 2", t, tm(36.6), 320, 70, YEL)
# ================= 5. PEA plein, assurance vie, inflation (banque) =================
def b_banque(cv, c, t, k):
    t0 = tm(38.5); tb = tm(45.45)
    fo = 1-ent(t-tb, .35) if t > tb else 1
    if t < tb+.4:
        title(c, "ATTENTION", t, t0+.05, 230, 76, PINK, t1=tb)
        if t > tm(39.5):
            prop(c, 'coffre_deborde', 300, 640, h=430, k=t-tm(39.55), a=fo)
            paint(c, "PEA", 300, 380, 56, YEL, a=ent(t-tm(39.6), .3)*fo)
        if t > tm(40.7): pop_text(c, f"PLEIN À 150{NB}000{NB}€", 300, 900, 44, t, tm(40.75), YEL, a=fo)
        if t > tm(43.2):
            prop(c, 'coffre', 790, 660, h=380, k=t-tm(43.25), a=fo)
            paint(c, "ASSURANCE VIE", 790, 420, 40, CREAM, a=ent(t-tm(43.3), .3)*fo)
        if t > tm(44.5): paint(c, "ou compte-titres", 790, 890, 36, CREAM, a=ent(t-tm(44.55), .3)*fo)
        if t > tm(43.0): arrow(c, 470, 640, 600, 640, ent(t-tm(43.05), .4)*fo, YEL)
    if t > tb:
        title(c, "DANS 40 ANS", t, tb+.1, 230, 76)
        u = inout((t-tm(51.2))/1.6)                                            # le billet rétrécit avec l'inflation
        w = 820*(1-.45*u); a_ = ent(t-(tb+.3), .3)
        txt = euro(1e6-547110*u) if t > tm(51.2) else f"1{NB}000{NB}000{NB}€"
        on_prop(c, 'billet', 540, 640, w=w, k=t-(tb+.35), texts=((txt, 818, 435, 190, BROWN),))
        if t > tm(49.5): pop_text(c, f"INFLATION 2{NB}% / AN", 540, 340, 48, t, tm(49.55), PINK)
        if t > tm(52.6): paint(c, "en euros d'aujourd'hui", 540, 920, 38, YEL, a=ent(t-tm(52.65), .3))
# ================= 6. fin (haricot géant) =================
def b_fin(cv, c, t, k):
    t0 = tm(53.5)
    title(c, "LE MEILLEUR MOMENT ?", t, t0+.05, 230, 64, t1=tm(59.45))
    if t > tm(55.85): pop_text(c, "IL Y A 10 ANS", 540, 340, 70, t, tm(55.9), YEL, rot=-.03, a=1-ent(t-tm(56.5), .3))
    if t > tm(56.55):
        pop_text(c, "LE DEUXIÈME :", 540, 340, 56, t, tm(56.6), CREAM, a=1-ent(t-tm(59.45), .3))
        if t > tm(58.0): pop_text(c, "AUJOURD'HUI", 540, 440, 84, t, tm(58.05), YEL, rot=-.03, a=1-ent(t-tm(59.45), .3))
    if t > tm(59.5):
        title(c, "ET TOI,", t, tm(59.55), 240, 76)
        title(c, "TU AS COMMENCÉ", t, tm(60.0), 330, 56, CREAM)
        title(c, "À QUEL ÂGE ?", t, tm(60.6), 420, 76, YEL)
    if t > tm(61.6): paint(c, "Dis-le en commentaire", 540, 930, 36, a=ent(t-tm(61.65), .3))
SC = [(0.0, V.GP[1], b_hook, 'rayons'), (V.GP[1], tm(10.45), b_chambre, 'chambre'), (tm(10.45), tm(24.45), b_haricot, 'haricot_pousse'),
      (tm(24.45), tm(38.45), b_gare, 'gare'), (tm(38.45), tm(53.45), b_banque, 'banque'), (tm(53.45), DUR, b_fin, 'haricot_geant')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [s_[0] for s_ in SC[1:]]; IR = .42
MCX = [(0, 540), (SC[1][0], 790), (SC[2][0], 790), (SC[3][0], 540), (SC[4][0], 540), (SC[5][0], 790)]
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    gp = V.GP[0] <= t < V.GP[1]
    arr = closeup(arr, t) if gp else coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    if gp and t > V.WOW:
        s, c = surface(); pop_text(c, "WOW !", 540, 420, 140, t, V.WOW+.05, YEL, rot=-.08); out.alpha_composite(to_img(s))
    if not gp: s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    if t > tm(61.7): S.put_emoji(out, '👇', 860, int(930+8*math.sin(t*5)), 46)
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
    ev = [e for e in V.events() if not (V.GP[0]-.1 <= e[0] < V.GP[1]+.1)] + [(ta-IR, 'whoosh') for ta in IRIS]
    ev += [(.05, 'thud'), (.45, 'impact'), (2.0, 'impact'), (2.45, 'pop'), (V.GP[0], 'swish'),
           (4.9, 'pop'), (5.1, 'tadaa'), (5.15, 'coins'),
           (tm(6.1), 'thud'), (tm(6.4), 'pop'), (tm(7.05), 'pop')] + [(tm(7.4)+i*.38+.5, 'coin') for i in range(8)]
    ev += [(tm(8.95)+.1+i*.13, 'tick') for i in range(18)] + [(tm(11.5), 'tadaa')]
    ev += [(tm(10.5), 'impact'), (tm(12.95), 'swish'), (tm(13.15), 'fill1'), (tm(15.05), 'thud'), (tm(15.6), 'swish'), (tm(15.8), 'fill0'), (tm(18.6), 'fill2'), (tm(20.2), 'glint'),
           (tm(21.55), 'thud'), (tm(22.4), 'impact')]
    ev += [(tm(24.55), 'thud'), (tm(24.6), 'pop'), (tm(24.9), 'pop'), (tm(26.6), 'pop'), (tm(28.6), 'impact'), (tm(30.05), 'bonk'), (tm(31.05), 'pop'), (tm(33.45), 'crash'),
           (tm(35.05), 'thud'), (tm(36.6), 'impact')]
    ev += [(tm(38.55), 'impact'), (tm(39.55), 'coins'), (tm(40.75), 'pop'), (tm(43.05), 'swish'), (tm(43.25), 'thud'), (tm(45.55), 'thud'), (tm(45.8), 'glint'),
           (tm(49.55), 'bonk'), (tm(51.2), 'low'), (tm(52.65), 'pop')]
    ev += [(tm(53.55), 'thud'), (tm(55.9), 'impact'), (tm(56.6), 'pop'), (tm(58.05), 'tadaa'), (tm(59.55), 'thud'), (tm(60.0), 'pop'), (tm(60.6), 'impact')]
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
