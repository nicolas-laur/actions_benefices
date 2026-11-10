"""Action, obligation, fonds euros (11/11/2026), cartoon 1930 en Technicolor : décors Gemini (rue, fournil, salle des coffres), accessoires Gemini détourés,
Mister Coin Boulanger (clip Gemini qui jongle, en boucle) à côté de Mister Coin,
Mister Coin en couleurs, pellicule discrète, iris aux changements de décor.
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
DECC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('rue', 'fournil', 'coffres')}
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
DSLOW = {('fournil', 12.0): .3}                                       # fournil de l'action : travelling ralenti (le boulanger reste derrière le comptoir)
def decor_c(name, t):
    a, b = next((a, b) for (a, b, d) in BLOCS if d == name and a <= t < b+.5)
    n = nframes(name); sp = min(1.0, (n-1)/24/max(.1, b-a))*DSLOW.get((name, a), 1.0); i = min(n-1, int(max(0, t-a)*sp*24))
    f = _RD.get(name, i)
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    return np.clip((g-128)*1.06+130, 0, 255)
def coin_col(cv_rgb, t):
    Y = V.FEET+V.MC.hop_dy(t); rgb_, al = V.MC.layer(t, V.MC.x, Y)
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
# ================= scènes =================
def b_rue1(cv, c, t, k):
    paint(c, "ACTION, OBLIGATION, FONDS EUROS…", 540, 290, fit(c, "ACTION, OBLIGATION, FONDS EUROS…", 52, 960))
    paint(c, "TU SAIS CE QUE TU ACHÈTES ?", 540, 370, fit(c, "TU SAIS CE QUE TU ACHÈTES ?", 66, 960), YEL)
    out = ease((t-6.1)/.45) if t > 6.1 else 0
    for i, (nm, lab, t0, x) in enumerate((('certificat_action', "ACTION", .1, 195), ('obligation_coupons', "OBLIGATION", .8, 540), ('coffre', "FONDS EUROS", 2.3, 885))):
        if t < t0: continue
        bob = 8*math.sin(t*2+i); y = 590+bob+out*900
        if nm == 'certificat_action': prop(c, nm, x, y, w=300, k=t-t0, rot=-.04)
        elif nm == 'obligation_coupons': prop(c, nm, x, y, h=300, k=t-t0, rot=.03)
        else: prop(c, nm, x, y, h=250, k=t-t0, rot=-.02)
        pop_text(c, lab, x, 790+out*900, 40, t, t0+.1, CREAM if i != 1 else CREAM)
    if t > 4.1: pop_text(c, "?", 540, 900+out*900, 120, t, 4.15, YEL)
def b_rue2(cv, c, t, k):
    sw = .04*math.sin(t*1.7)
    board(c, 952, 836, 262, t-7.9, rot=-.03, lines=(("BOUTIQUE", 165, BROWN), ("N° 2", 210, RED)))
    title(c, "UNE BOULANGERIE", t, 6.7, 290, 70, t1=9.6)
    title(c, "IL LUI FAUT DE L'ARGENT", t, 9.7, 290, 56, t1=10.75)
    if t > 11.0: pop_text(c, "2 SOLUTIONS", 540, 290, 78, t, 11.05, YEL)
def b_action(cv, c, t, k):
    if t < 22.6:
        title(c, "1. L'ACTION", t, 12.25, 290, 80, YEL)
        mv = inout((t-17.4)/.7) if t > 17.4 else 0                    # le certificat se range à gauche pour laisser place au dividende
        cx_, cy_, w_ = 540-260*mv, 560-60*mv, 520-210*mv
        grow = 1+.14*inout((t-21.0)/.8) if t > 21.0 else 1
        on_prop(c, 'certificat_action', cx_, cy_, w=w_*grow, k=t-12.9, rot=-.03+.02*math.sin(t*1.3),
                texts=(("UNE PART", 833, 300, 120, BROWN), ("DE LA BOULANGERIE", 833, 560, 96, BROWN)))
        if t > 14.85: pop_text(c, "ACTION = PROPRIÉTAIRE", 540, 735, 52, t, 14.85, YEL, maxw=900, a=1-ent(t-17.3, .25))
        if t > 17.4:
            for i in range(6):                                           # les croissants du dividende tombent en pile
                t0 = 17.9+.32*i; kk = t-t0
                if kk <= 0: continue
                tx, ty = 735+(-60, 60, 0, -70, 70, 0)[i], 720-(0, 0, 80, 150, 150, 230)[i]
                y = ty-560*(1-ent(kk, .45)); prop(c, 'croissant', tx, y, w=170, rot=(-.2, .2, .05, -.15, .15, 0)[i], shadow=False)
            if t > 20.0: pop_text(c, "DIVIDENDE", 735, 760, 60, t, 20.05, YEL)
            if t > 21.2:
                pop_text(c, "+ DE VALEUR", 280, 655, 44, t, 21.2, MINT, rot=-.04)
                for i in range(3):
                    ph = ((t-21.2)*.8+i*.33) % 1; S_ = math.sin(ph*math.pi)
                    if S_ > .1: star(c, 280+(-130, 120, 150)[i], 420+(0, 30, 250)[i], 24*S_)
    else:
        title(c, "FAILLITE", t, 22.7, 290, 90, PINK)
        sh = 6*math.sin(t*38)*(1-ent(t-23.6, .6)) if t > 23.0 else 0
        prop(c, 'tirelire_fissuree', 540+sh, 620, h=470, k=t-22.8, rot=.03*math.sin(t*2))
        if t > 24.2: pop_text(c, "TU PEUX TOUT PERDRE", 540, 905, 54, t, 24.2, PINK, maxw=900)
def b_oblig(cv, c, t, k):
    title(c, "2. L'OBLIGATION", t, 25.6, 290, 76, YEL, t1=35.6)
    if t < 28.0:
        a = 1-ent(t-27.6, .3)
        prop(c, 'poignee_de_main', 540, 590+6*math.sin(t*3), w=480, k=t-25.9, a=a)
        if t > 26.4: pop_text(c, "UN PRÊT", 540, 790, 60, t, 26.4, CREAM, a=a)
    elif t < 36.0:
        out = ease((t-35.5)/.5) if t > 35.5 else 0
        gone = sum(1 for g in (30.9, 31.25, 31.6) if t > g)
        bond(c, 540-out*1100, 585, 520, t, k=t-27.85, gone=gone, tgo=(30.9, 31.25, 31.6))
        if t > 28.8: pop_text(c, "OBLIGATION = PRÊTEUR", 540-out*1100, 940, 52, t, 28.8, YEL, maxw=900, a=1-ent(t-30.4, .25))
        if t > 30.6: pop_text(c, "INTÉRÊTS FIXES", 540-out*1100, 940, 54, t, 30.6, YEL, a=1-ent(t-32.0, .25))
        if t > 32.1: pop_text(c, "+ REMBOURSÉ À LA FIN", 540-out*1100, 940, 52, t, 32.1, MINT, maxw=900, a=1-ent(t-33.5, .25))
        if t > 33.6: pop_text(c, "MOINS DE RISQUE", 540-out*1100, 895, 44, t, 33.6, MINT)
        if t > 34.45: pop_text(c, "PAS DE JACKPOT", 540-out*1100, 955, 44, t, 34.45, PINK)
    else:
        bond(c, 540, 585, 520, t, k=t-36.0, label=False)
        sf_, iw_, ih_ = psurf('obligation_coupons'); s_ = 520/ih_*back((t-36.0)/.35)
        if t > 36.0:
            c.save(); c.translate(540, 585); c.scale(s_, s_); c.translate(-iw_/2, -ih_/2)
            ink(c, "ÉTAT FRANÇAIS", 715, 292, 100, '1E3A5F', maxw=480); ink(c, "SUR 10 ANS", 705, 595, 90, '1E3A5F', maxw=560); c.restore()
        if t > 38.4: pop_text(c, f"+ DE 4{NB}%", 540, 660, 110, t, 38.4, RED, rot=-.08)
        title(c, "L'ÉTAT AUSSI", t, 35.9, 290, 74)
        if t > 38.9: paint(c, f"4,44{NB}% en moyenne en septembre 2026", 540, 935, 28, a=ent(t-38.9, .3))
def b_fonds(cv, c, t, k):
    if t < 49.6:
        title(c, "LE FONDS EUROS", t, 39.85, 290, 76, YEL)
        mv = inout((t-41.8)/.6) if t > 41.8 else 0; back_ = inout((t-44.7)/.6) if t > 44.7 else 0
        m = mv*(1-back_)
        cx_, h_ = 540-290*m, 380-120*m
        prop(c, 'coffre', cx_, 620+40*m, h=h_, k=t-40.0, rot=.02*math.sin(t*1.4))
        if 41.9 < t < 45.4: pie_glass(cv, t, 41.9, 45.0)
        if t > 44.8:
            prop(c, 'parapluie', 540, 470, h=330, k=t-44.85, rot=.03*math.sin(t*1.8))
            pop_text(c, "CAPITAL GARANTI", 540, 860, 52, t, 45.0, MINT)
            if t > 45.6: paint(c, "par l'assureur", 540, 915, 28, a=ent(t-45.6, .3))
        if t > 47.1:
            pop_text(c, f"2,6{NB}%", 875, 560, 92, t, 47.15, YEL, rot=.05)
            paint(c, "en 2025", 875, 630, 30, a=ent(t-47.4, .3))
    else:
        title(c, "SUR LE LONG TERME", t, 49.75, 290, 70)
        bars_glass(cv, t, 50.0)
def pie_glass(cv, t, t0, t1):
    k = t-t0; a = 1-ent(t-t1, .35)
    def d(kk, w, h):
        cx_, cy_, R = w/2-90, h/2+10, 140; u = inout((t-t0-.3)/1.1)
        kk.move_to(cx_, cy_); kk.arc(cx_, cy_, R, -math.pi/2, -math.pi/2+2*math.pi*.8*u); kk.close_path(); col(kk, '5AA9FF', .95); kk.fill()
        if u >= 1: kk.move_to(cx_, cy_); kk.arc(cx_, cy_, R, -math.pi/2+2*math.pi*.8, 3*math.pi/2); kk.close_path(); col(kk, S.GD, .9); kk.fill()
        kk.arc(cx_, cy_, R, 0, 2*math.pi); kk.set_line_width(3); col(kk, S.WHITE, .7); kk.stroke()
        S.text(kk, f"80{NB}%", w-150, h/2-40, 'a', 64, '5AA9FF', 'c', ent(t-t0-.9, .3)); S.text(kk, "obligations", w-150, h/2+10, 'sb', 32, S.ICE, 'c', ent(t-t0-1.0, .3))
        S.text(kk, "le reste : actions,", w-150, h/2+80, 'sb', 25, S.ICE, 'c', .8*ent(t-t0-1.5, .3)); S.text(kk, "immobilier…", w-150, h/2+112, 'sb', 25, S.ICE, 'c', .8*ent(t-t0-1.5, .3))
    S.tp(cv, 620, 400, d, 650+(1-a)*900, 640+40*(1-ent(k, .45)), 'bleu', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=28)
def bars_glass(cv, t, t0):
    k = t-t0
    def d(kk, w, h):
        base = h-120; top = 110; mx = 7.0
        for i, (lab, v, colr, tt) in enumerate((("ACTIONS", 6.6, S.GR, 54.4), ("OBLIGATIONS", 1.6, '5AA9FF', 58.4))):
            x = w*(.3+.4*i); u = inout((t-tt)/.9)
            bh = (base-top)*v/mx*u; kk.rectangle(x-80, base-bh, 160, bh)
            g = cairo.LinearGradient(0, base-bh, 0, base); r_, g_, b_ = rgb(colr)[:3]; g.add_color_stop_rgba(0, r_, g_, b_, .95); g.add_color_stop_rgba(1, r_, g_, b_, .45); kk.set_source(g); kk.fill()
            S.text(kk, lab, x, base+44, 'xb', 36, S.WHITE, 'c', ent(t-t0-.2, .3))
            if u > 0: S.text(kk, f"{v*u:.1f}".replace('.', ',')+f"{NB}%", x, base-bh-34, 'a', 52, colr, 'c', ent(t-tt, .25))
        kk.move_to(60, base); kk.line_to(w-60, base); kk.set_line_width(2); col(kk, S.WHITE, .5); kk.stroke()
        S.text(kk, "par an, après inflation", w/2, h-28, 'sb', 30, S.ICE, 'c', .8*ent(t-t0-.4, .3))
        S.text(kk, "États-Unis, 1900-2025", w/2, 44, 'sb', 30, S.ICE, 'c', .8*ent(t-t0-.6, .3))
    S.tp(cv, 860, 600, d, 540, 650+40*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def b_fin(cv, c, t, k):
    on_prop(c, 'pancarte', 285, 390+(1-ent(t-61.2, .45))*-800, w=470, k=1, rot=.03*math.sin(t*1.6), texts=(("PROPRIÉTAIRE", 610, 1345, 122, BROWN),))
    on_prop(c, 'pancarte', 795, 390+(1-ent(t-62.6, .45))*-800, w=470, k=1, rot=.03*math.sin(t*1.6+1), texts=(("PRÊTEUR", 610, 1345, 150, BROWN),))
    title(c, "ALORS TOI :", t, 60.6, 290, 66)
    if t > 61.6: prop(c, 'certificat_action', 285, 820, w=250, k=t-61.6, rot=-.05)
    if t > 63.0: bond(c, 795, 830, 250, t, k=t-63.0, label=False)
    if t > 62.6: pop_text(c, "OU", 540, 590, 54, t, 62.6, YEL)
    if t > 63.6: paint(c, "Dis-le en commentaire", 540, 960, 36, a=ent(t-63.7, .3))
# ================= Mister Coin Boulanger =================
BAK = f'{S.ROOT}/mister_coin/veo/boulanger_jongle.mp4'; BAK_X, BAK_FEET, BAK_S = 745, 1650, .60; BAK_FOOT_Y = 1035
BAK_ON = [('fond', 12.3, 22.5), ('cote', 25.45, None)]                  # au fond derrière le comptoir du fournil, puis à côté de Mister Coin
FOND_X, FOND_S = 300, .52
CPT_T, CPT_Y = (12.0, 15.0, 18.0, 21.0, 25.3), (1151, 1160, 1169, 1180, 1196)   # bord arrière du comptoir (mesuré sur le décor ralenti)             # comptoir : bord arrière du plateau (le boulanger est coupé en dessous)
class _Bak:
    def __init__(s): s.cap = None; s.i = -1; s.f = None
    def get(s, n):
        if s.cap is None: s.cap = cv2.VideoCapture(BAK); s.n = int(s.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n %= s.n
        if n < s.i or s.f is None and n > 0: s.cap.set(cv2.CAP_PROP_POS_FRAMES, n); s.i = n-1
        while s.i < n:
            ok, fr = s.cap.read(); s.i += 1
            if not ok: s.cap.set(cv2.CAP_PROP_POS_FRAMES, 0); s.i = -1; continue
            s.f = fr
        a, m = VC._key(s.f[..., ::-1].copy())
        rgba = np.dstack([np.clip(a, 0, 255), m*255]).astype(np.uint8)
        im = Image.fromarray(rgba, 'RGBA'); return im.resize((int(im.width*BAK_S), int(im.height*BAK_S)), Image.LANCZOS)
_BK = _Bak()
def baker_state(t):
    """(mode, décalage) : au fond, il monte de derrière le comptoir puis redescend ; à côté, il entre et sort par la droite"""
    for mode, a, b in BAK_ON:
        if t < a-.6 or (b is not None and t > b+.6): continue
        if mode == 'fond':
            if t < a: return 'fond', 450*(1-ease((t-a+.6)/.6))
            if t > b: return 'fond', 450*ease((t-b)/.6)
            return 'fond', 0
        dx = 700*(1-ease((t-a+.6)/.6)) if t < a else 0
        if b is not None and t > b: dx = 700*ease((t-b)/.6)
        return ('cote', dx) if dx < 699 else None
    return None
def baker(out, t):
    st = baker_state(t)
    if st is None: return
    mode, off = st; im = _BK.get(int(t*24))
    if mode == 'fond':
        im = im.resize((int(im.width*FOND_S/BAK_S), int(im.height*FOND_S/BAK_S)), Image.LANCZOS)
        cpt = float(np.interp(t, CPT_T, CPT_Y)); x = int(FOND_X-im.width/2); y = int(cpt+70+off-BAK_FOOT_Y*FOND_S)
        h = int(cpt)-y
        if h <= 0: return
        im = im.crop((0, 0, im.width, min(im.height, h)))
    else:
        x = int(BAK_X+off-im.width/2); y = int(BAK_FEET-BAK_FOOT_Y*BAK_S)
    if x < W: out.alpha_composite(im, (max(x, 0), y), (max(0, -x), 0))

SC = [(0.0, 6.5, b_rue1, 'rue'), (6.5, 12.0, b_rue2, 'rue'), (12.0, 25.3, b_action, 'fournil'), (25.3, 39.6, b_oblig, 'rue'),
      (39.6, 60.45, b_fonds, 'coffres'), (60.45, DUR, b_fin, 'fournil')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [12.0, 25.3, 39.6, 60.45]; IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    st = baker_state(t)
    if st and st[0] == 'fond': baker(cv, t)                             # au fond : derrière les accessoires de la scène
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
    if st and st[0] == 'cote': baker(cv, t)
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    for ta in IRIS:
        if ta-IR <= t < ta: arr = iris(arr, inout((t-(ta-IR))/IR))
        elif ta <= t < ta+IR: arr = iris(arr, 1-inout((t-ta)/IR))
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    if t > 63.7: S.put_emoji(out, '👇', 860, int(960+8*math.sin(t*5)), 46)
    return out
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else 'FF8A8A', a=al); return
def events():
    ev = V.events() + [(ta-IR, 'whoosh') for ta in IRIS]
    ev += [(.1, 'pop'), (.8, 'pop'), (2.3, 'pop'), (4.15, 'impact'), (6.6, 'swish'), (6.7, 'thud'), (7.9, 'swish'), (9.7, 'thud'), (11.05, 'impact'),
           (12.25, 'thud'), (12.9, 'glint'), (14.85, 'impact'), (17.4, 'swish'), (20.05, 'tadaa'), (21.2, 'glint'),
           (22.7, 'thud'), (22.8, 'crash'), (24.2, 'impact'), (25.45, 'swish'), (25.6, 'thud'), (25.9, 'pop'), (27.85, 'glint'), (28.8, 'impact'),
           (32.1, 'thud'), (33.6, 'pop'), (34.45, 'bonk'), (35.9, 'thud'), (36.0, 'swish'), (37.0, 'impact'),
           (39.85, 'thud'), (40.0, 'thud'), (41.9, 'swish'), (42.3, 'fill1'), (44.85, 'pop'), (45.0, 'glint'), (47.15, 'impact'),
           (49.75, 'thud'), (50.0, 'swish'), (54.4, 'fill1'), (55.3, 'tadaa'), (58.4, 'fill2'), (60.55, 'swish'), (60.6, 'thud'), (61.2, 'swish'), (62.6, 'swish'), (63.6, 'impact')]
    ev += [(30.9+.35*i+.55, 'coin') for i in range(3)] + [(17.9+.32*i+.4, 'tick') for i in range(6)]
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
