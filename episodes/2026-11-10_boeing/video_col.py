"""Boeing (10/11/2026), cartoon 1930 en Technicolor : décors Gemini (ciel, hangar, piste, terminal), accessoires Gemini détourés,
Mister Coin en couleurs, pellicule discrète, iris aux changements de décor.
usage : python3 video_col.py info | png t1 t2 … | seg out.mp4 f0 f1"""
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
DECC = {n: f'{D}/decors/decor_{n}.mp4' for n in ('ciel', 'hangar', 'piste', 'terminal')}
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
# ================= accessoires animés =================
HOLE = (866, 292)                                    # emplacement du panneau arraché (coordonnées de avion.png, à la place du dernier hublot)
def plane(c, x, y, w, rot=0.0, hole=False, t=0.0, a=1.0, shake=0.0):
    """avion générique Gemini (tourné vers la droite) ; hole : le panneau a été arraché"""
    sf, iw, ih = psurf('avion'); s = w/iw
    j = shake*math.sin(t*61)*4, shake*math.cos(t*47)*3
    c.save(); c.translate(x+j[0], y+j[1]); c.rotate(rot); c.scale(s, s); c.translate(-iw/2, -ih/2)
    c.set_source_surface(sf, 0, 0); c.paint_with_alpha(a)
    if hole:
        hx, hy = HOLE; rng = np.random.default_rng(3); c.new_path(); N = 16
        for i in range(N+1):
            th = 2*math.pi*i/N; rx, ry = 66+rng.normal(0, 5), 78+rng.normal(0, 5)
            (c.move_to if i == 0 else c.line_to)(hx+rx*math.cos(th), hy+ry*math.sin(th))
        c.close_path(); col(c, '1B1410', a); c.fill_preserve(); c.set_line_width(9); col(c, BROWN, a); c.stroke()
    c.restore()
def hole_pos(x, y, w, rot=0.0):
    sf, iw, ih = psurf('avion'); s = w/iw; dx, dy = (HOLE[0]-iw/2)*s, (HOLE[1]-ih/2)*s
    return x+dx*math.cos(rot)-dy*math.sin(rot), y+dx*math.sin(rot)+dy*math.cos(rot)
def wind(c, x, y, t, n=7, L=260, a=.7):
    """traits de vitesse qui défilent vers la gauche"""
    for i in range(n):
        ph = (t*2.2+i*.37) % 1; yy = y+(i-n/2)*34+8*math.sin(i*2.1); xx = x+L*(1-ph)*1.6-L*.3
        c.move_to(xx, yy); c.line_to(xx-L*(.4+.3*math.sin(i)), yy); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, 'FFFFFF', a*math.sin(ph*math.pi)); c.stroke()
def banner_plane(c, x, y, s, l1, l2, t, a=1.0):
    """biplan rouge qui tire la banderole ; x, y = point d'attache de la corde ; la toile est allongée pour porter le texte"""
    sf, iw, ih = psurf('banderole'); RX, RY = 870, 330                    # attache de la corde sur la toile (coordonnées de banderole.png)
    bob = 6*math.sin(t*2.3)
    c.save(); c.translate(x, y+bob); c.scale(s, s)                          # biplan + corde : à l'échelle s
    c.rectangle(-10, -400, iw, 1400); c.clip(); c.set_source_surface(sf, -RX, -RY); c.paint_with_alpha(a); c.restore()
    sx, sy = s*2.05, s*1.9; wav = .025*math.sin(t*5.0)
    c.save(); c.translate(x, y+bob); c.rotate(wav); c.scale(sx, sy)            # toile : allongée en largeur et en hauteur
    c.rectangle(-RX, -400, RX+12, 1400); c.clip(); c.set_source_surface(sf, -RX, -RY); c.paint_with_alpha(a); c.restore()
    cx, cy = x-(RX-440)*sx, y+bob-(RY-322)*sy
    c.save(); c.translate(cx, cy); c.rotate(wav)
    sz = fit(c, l1, 44, 400)
    paint(c, l1, 0, -30 if l2 else 0, sz, RED, a=a); paint(c, l2, 0, 32, sz, RED, a=a) if l2 else None
    c.restore()
ALT_HUB = (742, 750); ALT_R = 505; ALT_A0 = 34.0                     # moyeu de l'aiguille, rayon du cadran, angle d'origine de l'aiguille
def alti(c, x, y, h, pct, k, t=0.0, shake=0.0):
    """altimètre Gemini : on fait tourner le cadran (graduations régulières) pour placer l'aiguille ; 100 % = record, 0 % en bas à gauche"""
    if k <= 0: return
    sf, iw, ih = psurf('altimetre'); s = h/ih*back(k/.35)
    ang = math.radians(-120+240*pct/100-ALT_A0)+shake*.04*math.sin(t*40)
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_source_surface(sf, -ALT_HUB[0], -ALT_HUB[1]); c.paint()
    c.arc(0, 0, ALT_R, 0, 2*math.pi); c.clip(); c.rotate(ang); c.set_source_surface(sf, -ALT_HUB[0], -ALT_HUB[1]); c.paint()
    c.restore()
BCOL = [270, 422, 574, 726, 880, 1034, 1186]; BROW = [262, 512, 760, 1000]; BCW, BCH = 118, 196     # cases du panneau des départs
FLAPS = "ABCDEFGHIJKLMNOPRSTUVZ0123456789"
def board(c, x, y, h, rows, t, t0, a=1.0, k=1.0):
    """panneau des départs Gemini : les palettes défilent puis s'arrêtent sur le texte (4 lignes de 7 cases)"""
    if k <= 0 or a <= 0: return []
    sf, iw, ih = psurf('panneau_depart'); s = h/ih*back(k/.35)
    c.save(); c.translate(x, y); c.scale(s, s); c.translate(-iw/2, -ih/2); c.set_source_surface(sf, 0, 0); c.paint_with_alpha(a)
    settle = []
    for r, txt in enumerate(rows):
        txt = txt.center(7)[:7]
        for i, ch in enumerate(txt):
            d = t0+.10*i+.18*r; end = d+.55+.05*i
            if ch == ' ' or t < d: continue
            settle.append(end)
            shown = ch if t >= end else FLAPS[int((t*24+i*7+r*13)) % len(FLAPS)]
            cx, cy = BCOL[i], BROW[r]
            rr(c, cx-BCW/2, cy-BCH/2, BCW, BCH, 12); col(c, '17181C', a); c.fill()
            c.select_font_face('Alfa Slab One', 0, 0); c.set_font_size(150); e = c.text_extents(shown)
            c.move_to(cx-e.x_bearing-e.width/2, cy+e.height/2); c.text_path(shown); col(c, 'F3E6C4' if t >= end else 'D9CDB0', a); c.fill()
            c.rectangle(cx-BCW/2, cy-3, BCW, 6); col(c, '0B0B0D', a); c.fill()
            for sx_ in (-1, 1): rr(c, cx+sx_*(BCW/2-6)-5, cy-14, 10, 28, 3); col(c, '2B2C31', a); c.fill()
    c.restore(); return settle
# ================= scènes =================
def b_hook(cv, c, t, k):
    sw = 1+.02*math.sin(t*4)
    c.save(); c.translate(540, 0); c.scale(sw, 1)
    paint(c, "COMMENT L'AVION", 0, 290, 70); paint(c, "LE PLUS SÛR DU MONDE", 0, 372, 60)
    paint(c, "A PU PERDRE", 0, 456, 60); paint(c, "UNE PORTE EN VOL ?", 0, 548, 74, YEL); c.restore()
    T = 2.98; x = 150+180*t; y = 760+10*math.sin(t*2.6); r = .03*math.sin(t*2)
    plane(c, x, y, 560, r, hole=t > T, t=t, shake=1 if t > T else 0)
    if t > T: tear(c, *hole_pos(x, y, 560, r), t-T, 260)
def tear(c, hx, hy, k, h):
    """le panneau arraché part en tournoyant vers l'arrière et vers le bas"""
    if k < 0: return
    px, py = hx-520*k-120*k*k, hy-60*k+520*k*k; prop(c, 'porte', px, py, h=h*.42, rot=-3.2*k, shadow=False, a=1-ent(k-.9, .4))
    for i in range(5):                                              # bourrasque qui sort du trou
        u = (k*3+i*.2) % 1
        if k > 1.2: break
        c.move_to(hx-30-200*u, hy-20+i*12); c.line_to(hx-90-300*u, hy-26+i*14); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, 'FFFFFF', .8*(1-u)); c.stroke()
def b_hangar(cv, c, t, k):
    # l'âge d'or : l'avion rutilant, la banderole du biplan
    if t < 13.3:
        out = ease((t-12.5)/.7) if t > 12.5 else 0
        plane(c, 540+out*1100, 760+4*math.sin(t*1.5), 700, -.02)
        if 4.5 < t < 13.0:
            for i in range(3):                                         # éclats de brillance sur la carlingue
                ph = ((t-4.5)*.8+i*.33) % 1; S_ = math.sin(ph*math.pi)
                if S_ > .1: star(c, 380+170*i+out*1100, 690+30*math.sin(i*2), 26*S_)
    if 4.6 < t < 9.4:
        u = ease((t-4.6)/1.4); uo = ease((t-8.9)/.6) if t > 8.9 else 0
        bx = -700+(610+700)*u+uo*1400
        banner_plane(c, bx, 420, .30, "IF IT'S NOT BOEING,", "I'M NOT GOING", t)
    # cotée depuis 1962, puis le record
    title(c, "COTÉ À NEW YORK", t, 9.0, 290, 62, t1=12.6)
    pop_text(c, "DEPUIS 1962", 540, 400, 92, t, 11.6, YEL, a=1-ent(t-12.6, .3))
    if t > 12.6:
        title(c, "LE RECORD", t, 12.8, 290, 70)
        kk = t-12.9; sw = .03*math.sin(t*1.6)
        prop(c, 'trophee', 540, 665, h=430, k=kk, rot=sw)
        if t > 15.6:
            v = count_to(387, (t-15.6)/.9); pop_text(c, f"{int(round(v))}{NB}€", 540, 395, 96, t, 15.6, YEL)
            if t > 16.6: paint(c, "par action · 1er mars 2019", 540, 915, 32, a=ent(t-16.6, .3))
        for i in range(4):
            ph = ((t-12.9)*.7+i*.25) % 1; S_ = math.sin(ph*math.pi)
            if kk > .3 and S_ > .1: star(c, 540+(-170, 160, -120, 190)[i], 520+(0, 40, 200, 170)[i], 30*S_)
def star(c, x, y, r):
    c.move_to(x, y-r)
    for i in range(1, 8): rr_ = r if i % 2 == 0 else r*.28; th = -math.pi/2+i*math.pi/4; c.line_to(x+rr_*math.cos(th), y+rr_*math.sin(th))
    c.close_path(); col(c, 'FFF6C8', .95); c.fill()
def b_max(cv, c, t, k):
    title(c, "LE 737 MAX", t, 18.0, 290, 80, YEL, t1=25.0)
    if t < 25.3:
        u = ease((t-18.1)/1.5); dive = clamp((t-23.95)/1.25)
        x = -500+1040*u+dive*520; y = 690+6*math.sin(t*2)+dive*dive*260; r = .04*math.sin(t*1.7)+dive*.62
        a = 1-ent(t-24.7, .5)
        if t < 20.0 or 20.4 < t < 21.2: wind(c, x-200, y+10, t)
        if t > 18.1: plane(c, x, y, 640, r, t=t, a=a, shake=.6 if 23.4 < t < 24.6 else 0)
        if 22.4 < t < 25.0:
            pop_text(c, "UN LOGICIEL MAL CONÇU", 540, 430, 50, t, 22.4, PINK, rot=-.03, a=1-ent(t-24.6, .3))
    # deux crashs : sobre, sans rebond
    if 25.2 < t < 27.9:
        a = ent(t-25.2, .5)*(1-ent(t-27.5, .35))
        prop(c, 'ruban_noir', 540, 610, h=380, a=a, shadow=False)
        paint(c, "2 CRASHS", 540, 300, 72, CREAM, a=a); paint(c, f"346{NB}MORTS", 540, 880, 64, CREAM, a=ent(t-26.1, .5)*(1-ent(t-27.5, .35)))
        paint(c, "Indonésie, octobre 2018 · Éthiopie, mars 2019", 540, 950, 24, CREAM, a=ent(t-26.4, .5)*(1-ent(t-27.5, .35)), fam='Limelight')
    if t > 27.6:
        title(c, "CLOUÉ AU SOL", t, 27.6, 290, 74)
        kk = t-27.7; plane(c, 540, 700+(1-ent(kk, .4))*-500, 640, 0, t=t)
        prop(c, 'chaines', 540, 700, h=360, k=t-28.3, rot=.02*math.sin(t*1.3))
        pop_text(c, f"20{NB}MOIS", 540, 395, 96, t, 29.25, YEL)
        if t > 29.6: paint(c, "mars 2019 → novembre 2020", 540, 920, 26, a=ent(t-29.6, .3), fam='Limelight')
def b_ciel(cv, c, t, k):
    # Covid : le ciel vide, l'altimètre plonge
    if t < 36.2:
        out = ease((t-35.6)/.55) if t > 35.6 else 0
        title(c, "COVID", t, 30.3, 290, 84, t1=35.5)
        if t > 30.9: paint(c, "le ciel se vide", 540, 375, 40, a=ent(t-30.9, .3)*(1-out))
        pct = 100-78*inout((t-32.7)/1.3) if t > 32.7 else 100
        alti(c, 540-out*1100, 650, 440, pct, t-30.5, t, shake=1 if 32.7 < t < 34.0 else 0)
        if t > 31.0 and t < 32.7: paint(c, f"387{NB}€", 540-out*1100, 905, 44, YEL, a=ent(t-31.0, .3))
        if t > 33.9: pop_text(c, f"−78{NB}%", 360-out*1100, 905, 72, t, 33.9, PINK, a=1-out)
        if t > 34.6: pop_text(c, f"{NB}89{NB}€", 730-out*1100, 905, 72, t, 34.6, YEL, a=1-out)
        if t > 35.0: paint(c, "20 mars 2020", 730-out*1100, 962, 28, a=ent(t-35.0, .3)*(1-out))
    else:
        title(c, "5 JANVIER 2024", t, 35.8, 290, 70)
        T = 41.28; u = ease((t-36.0)/2.2)
        x = -420+960*u; y = 680+8*math.sin(t*2.4); r = .03*math.sin(t*1.8)
        if t < T: wind(c, x-230, y, t, a=.5)
        plane(c, x, y, 620, r, hole=t > T, t=t, shake=1.2 if T < t < T+1.2 else 0)
        if t > T: tear(c, *hole_pos(x, y, 620, r), t-T, 300)
        if t > 42.15:
            pop_text(c, "4 BOULONS MANQUANTS", 540, 410, 58, t, 42.15, PINK, rot=-.02)
            hx, hy = hole_pos(x, y, 620, r)
            for i in range(4):
                kk = t-(42.3+.32*i)
                if kk <= 0: continue
                bx = hx-60+40*i-90*kk; by = hy+40+430*kk*kk
                if by < 990: prop(c, 'boulon', bx, by, h=105, rot=5*kk+i, shadow=False, a=1-ent(by-900, 80))
            if t > 43.6: paint(c, "retirés à l'usine, jamais remis", 540, 900, 30, a=ent(t-43.6, .3), fam='Limelight')
# cours de Boeing en dollars (clôtures non ajustées) : fins d'année 2017-2019 et 2020-2024, record et plus bas Covid, puis fins de mois 2025-2026
M = lambda y, m, d=28: y+(m-1)/12+(d-1)/365
BA = [(M(2017, 12), 294.91), (M(2018, 12), 322.50), (M(2019, 3, 1), 440.62), (M(2019, 12), 325.76), (M(2020, 3, 20), 95.01), (M(2020, 12), 214.06),
      (M(2021, 12), 201.32), (M(2022, 12), 190.49), (M(2023, 12), 260.66), (M(2024, 11), 155.44), (M(2024, 12), 177.00)]
BA += [(M(2025, m), v) for m, v in enumerate([176.52, 174.63, 170.55, 183.24, 207.32, 209.53, 221.84, 234.68, 215.83, 201.02, 189.00, 217.12], 1)]
BA += [(M(2026, m), v) for m, v in enumerate([233.72, 227.53, 199.03, 229.03, 231.15, 216.47, 216.14, 207.78, 186.05], 1)]
BA += [(M(2026, 10, 26), 188.31), (M(2026, 10, 27), 168.18), (M(2026, 10, 30), 171.55), (M(2026, 11, 6), 173.40)]
def ba_at(d):
    for (d0, v0), (d1, v1) in zip(BA, BA[1:]):
        if d0 <= d <= d1: return v0+(v1-v0)*(d-d0)/(d1-d0)
    return BA[-1][1]
D0, D1 = 2017.85, 2026.95
def chart_glass(cv, t, t0, dx=0.0):
    """panneau de verre épais (lib/verre_epais) : la courbe du cours se trace de fin 2017 à aujourd'hui, avec les repères de l'histoire"""
    k = t-t0
    if k <= 0: return
    T = S.text
    def d(kk, w, h):
        x0, x1, yb, yt = 92, w-46, h-74, 70
        X = lambda dd: x0+(dd-D0)/(D1-D0)*(x1-x0); Y = lambda v: yb-v/470*(yb-yt)
        for v in (100, 200, 300, 400):
            kk.move_to(x0, Y(v)); kk.line_to(x1, Y(v)); kk.set_line_width(1); col(kk, S.WHITE, .1); kk.stroke()
            T(kk, f"{v} $", x0-12, Y(v), 'sb', 19, S.ICE, 'r', .5)
        for yr in range(2018, 2027): T(kk, str(yr), X(yr), yb+30, 'sb', 19, S.ICE, 'c', .6)
        dend = D0+(2026.86-D0)*inout((t-t0-.3)/2.9)
        if dend <= D0+.01: return
        pts = [(X(dd), Y(v)) for dd, v in BA if dd <= dend]+[(X(dend), Y(ba_at(dend)))]
        UP, DN = (.25, .88, .54), (1, .30, .37)                          # vert quand le cours monte, rouge quand il baisse
        segs = [(p0, p1, UP if p1[1] <= p0[1] else DN) for p0, p1 in zip(pts, pts[1:])]
        for (p0, p1, cl) in segs:                                         # aire sous la courbe, teintée segment par segment
            e_ = 1.2; kk.move_to(p0[0]-e_, yb); kk.line_to(p0[0]-e_, p0[1]); kk.line_to(p1[0]+e_, p1[1]); kk.line_to(p1[0]+e_, yb); kk.close_path()
            g = cairo.LinearGradient(0, yt, 0, yb); g.add_color_stop_rgba(0, *cl, .38); g.add_color_stop_rgba(1, *cl, 0); kk.set_source(g); kk.fill()
        kk.set_line_cap(cairo.LINE_CAP_ROUND)
        for wdt, al in ((16, .2), (6, 1.0)):
            for (p0, p1, cl) in segs: kk.move_to(*p0); kk.line_to(*p1); kk.set_line_width(wdt); kk.set_source_rgba(*cl, al); kk.stroke()
        kk.arc(*pts[-1], 9, 0, 2*math.pi); col(kk, S.WHITE); kk.fill()
        def mark(dd, v, big, small, colr, dy, tt, xo=0):
            if dend < dd or t < tt: return
            x, y = X(dd), Y(v); u = ent(t-tt, .3)
            kk.arc(x, y, 10*u, 0, 2*math.pi); col(kk, colr); kk.fill_preserve(); kk.set_line_width(3); col(kk, S.WHITE, u); kk.stroke()
            T(kk, big, x+xo, y+dy, 'a', 40, colr, 'c', u); T(kk, small, x+xo, y+dy+(30 if dy > 0 else -32), 'sb', 20, S.ICE, 'c', .8*u)
        mark(M(2019, 3, 1), 440.62, f"387{NB}€", "record, mars 2019", S.GD, 4, t0+.75, 128)
        mark(M(2020, 3, 20), 95.01, f"89{NB}€", "Covid, mars 2020", S.RD, 14, t0+1.05, 112)
        if dend > 2024.02 and t > t0+1.9:
            x, y = X(2024.02), Y(ba_at(2024.02)); prop(kk, 'porte', x, y-58, h=52, k=t-t0-1.9, rot=-.2, shadow=False)
            T(kk, "la porte, janv. 2024", x, y-104, 'sb', 20, S.ICE, 'c', .8*ent(t-t0-2.0, .3))
        mark(M(2026, 11, 6), 173.40, f"155{NB}€", "le 6 novembre", S.RD, 74, t0+3.2, -40)
        if t > 46.3:
            a = ent(t-46.3, .3)*(1-ent(t-48.3, .25)); T(kk, f"−60{NB}% depuis le record", w-60, 40, 'xb', 30, S.RD, 'r', a)
        if t > 48.4:
            x, y = X(M(2026, 10, 27)), Y(168.18); u = ent(t-48.4, .35)
            kk.arc(x, y, 40*u, 0, 2*math.pi); kk.set_line_width(5); col(kk, S.RD); kk.stroke()
            T(kk, f"−10,7{NB}% le 27 octobre", w-60, 40, 'xb', 30, S.RD, 'r', ent(t-48.45, .3)*(1-ent(t-51.9, .2)))
        if t > 52.1: T(kk, "les livraisons prennent du retard", w-60, 40, 'xb', 30, S.RD, 'r', ent(t-52.1, .3))
    S.tp(cv, 900, 560, d, 540+dx, 665+40*(1-ent(k, .45)), 'or', rx=round(.05+.25*(1-ent(k, .45)), 3), bev=30)
def b_today(cv, c, t, k):
    if t < 54.2:
        out = ease((t-53.6)/.55) if t > 53.6 else 0
        title(c, "AUJOURD'HUI", t, 44.4, 290, 76, t1=53.5)
        if out < 1: chart_glass(cv, t, 44.5, dx=-out*1100)
    else:
        title(c, "EN ATTENTE DE LIVRAISON", t, 53.7, 290, 56)
        board(c, 540, 640, 470, ["", f"6{NB}300", "AVIONS", ""], t, 54.3, k=t-53.9)
        if t > 57.3:
            prop(c, 'trophee', 870, 860, h=210, k=t-57.3, rot=.04*math.sin(t*2))
            pop_text(c, "RECORD !", 260, 880, 60, t, 57.4, YEL, rot=-.06)
def b_fin(cv, c, t, k):
    title(c, "ALORS, BOEING :", t, 58.5, 290, 64)
    board(c, 278, 590, 380, ["", "EN", "PANNE", ""], t, 59.5, k=t-59.3)
    board(c, 802, 590, 380, ["", "BONNE", "AFFAIRE", ""], t, 60.5, k=t-60.3)
    if t > 60.2: pop_text(c, "OU", 540, 590, 50, t, 60.2, YEL)
    if t > 61.9:
        pop_text(c, "?", 540, 850, 110, t, 61.9, YEL)
        paint(c, "Dis-le en commentaire", 540, 945, 38, a=ent(t-62.3, .3))
SC = [(0.0, 4.12, b_hook, 'ciel'), (4.12, 17.8, b_hangar, 'hangar'), (17.8, 30.2, b_max, 'piste'), (30.2, 44.36, b_ciel, 'ciel'),
      (44.36, 58.43, b_today, 'hangar'), (58.43, DUR, b_fin, 'terminal')]
BLOCS = [(a, b, d) for (a, b, f, d) in SC]
IRIS = [s_[0] for s_ in SC[1:]]; IR = .42
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    img = decor_c(dec, t)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); f(cv, c, t, max(0.0, t-a)); cv.alpha_composite(to_img(s))
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_col(arr, t)
    fl = film(arr.copy(), t); arr = arr*.72+fl*.28
    for ta in IRIS:
        if ta-IR <= t < ta: arr = iris(arr, inout((t-(ta-IR))/IR))
        elif ta <= t < ta+IR: arr = iris(arr, 1-inout((t-ta)/IR))
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_c(c, t); out.alpha_composite(to_img(s))
    if t > 62.3: S.put_emoji(out, '👇', 860, int(945+8*math.sin(t*5)), 50)
    return out
def cap_c(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else 'FF8A8A', a=al); return
def events():
    ev = V.events() + [(ta-IR, 'whoosh') for ta in IRIS]
    ev += [(2.98, 'crash'), (4.7, 'swish'), (9.0, 'thud'), (11.6, 'impact'), (12.8, 'thud'), (12.9, 'tadaa'), (15.6, 'tick'), (16.5, 'glint'),
           (18.0, 'thud'), (18.2, 'whoosh'), (22.4, 'swish'), (23.95, 'riser'), (27.6, 'thud'), (28.3, 'crash'), (29.25, 'impact'),
           (30.3, 'thud'), (32.7, 'crash'), (33.9, 'impact'), (34.6, 'impact'), (35.8, 'thud'), (36.0, 'whoosh'), (41.28, 'crash'), (42.15, 'swish'),
           (44.4, 'thud'), (44.6, 'swish'), (45.1, 'glint'), (45.4, 'crash'), (46.3, 'impact'), (47.5, 'tick'), (48.4, 'crash'), (53.7, 'thud'), (57.3, 'tadaa'), (58.5, 'thud'), (60.2, 'pop'), (61.9, 'impact')]
    ev += [(42.3+.32*i+.55, 'tick') for i in range(4)]
    for (t0, n) in ((54.3, 12), (59.5, 7), (60.5, 12)): ev += [(t0+.12*i, 'click') for i in range(n)]
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
