"""Spot pub Instagram « Actions Bénéfices » (base : Pourquoi tu restes pauvre ?), dessin animé 1930 : décors Gemini noir et blanc (théâtre, mansarde, banque, rue commerçante),
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
COL_T, COL_D = V.COL_T, .3

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

# ================= décor Technicolor =================
@functools.lru_cache(maxsize=1)
def dec_col_frames():
    cap = cv2.VideoCapture(DEC['theatre_couleur']); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    return F
def decor_col(t):
    F = dec_col_frames(); n = len(F); sp = min(1.0, (n-1)/24/max(.1, DUR-V.BURST)); i = min(n-1, max(0, int((t-V.BURST)*sp*24)))
    g = cv2.resize(F[i], (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    return np.clip((g-128)*1.08+128+6, 0, 255)                                  # couleurs Technicolor un peu plus franches
# ================= objets dessinés =================
JARGON = ["ETF", "PER", "PFU", "CAC 40", "OPCVM", "dividende", "obligation", "inflation", "PEA", "taux directeur", "spread", "bilan", "Bourse", "FED", "marge"]
_jr = np.random.default_rng(11)
JPOS = [(200, 250), (860, 230), (520, 180), (330, 380), (760, 400), (150, 520), (900, 560), (560, 330), (240, 690), (800, 700), (520, 520), (380, 830), (700, 840), (150, 380), (930, 400)]
JW = [(w, JPOS[i][0], JPOS[i][1], 3.1+.13*i, _jr.random()*6.28, .6+_jr.random()*.6, (_jr.random()-.5)*.4) for i, w in enumerate(JARGON)]
def jargon(c, t):
    """mots de jargon qui flottent en désordre (monde gris et confus), balayés par l'explosion de couleurs"""
    for (w, x, y, t0, ph, sp, rot) in JW:
        k = t-t0
        if k <= 0: continue
        a = ent(k, .4)*.85; xx = x+26*math.sin(t*sp+ph); yy = y+18*math.cos(t*sp*1.3+ph)
        if t > V.BURST:                                                       # soufflés vers l'extérieur
            u = t-V.BURST; dx, dy = xx-540, yy-1350; d = math.hypot(dx, dy)+1e-3; xx += dx/d*2600*u*u; yy += dy/d*2600*u*u; a *= 1-ease(u/.5)
        if a <= .01: continue
        c.save(); c.translate(xx, yy); c.rotate(rot+.1*math.sin(t+ph)); ink_text(c, w, 0, 0, 30+int(14*sp), PAPER, 'Alfa Slab One', outline=3, a=a); c.restore()
def sign(c, x, y, label, k, t, w=520, h=96):
    """panneau suspendu à deux cordes, qui tombe du cintre et se balance"""
    if k <= 0: return
    drop = (1-ent(k, .45))*-700; sw = .09*math.exp(-k*1.8)*math.sin(k*7)
    c.save(); c.translate(x, y+drop); c.rotate(sw)
    for sx in (-w*.35, w*.35): ink_line(c, [(sx, -h/2), (sx*1.1, -y-drop-40)], 4, INKC, t=t, seed=int(abs(sx))+1 if sx > 0 else 2)
    rr(c, -w/2+6, -h/2+8, w, h, 14); col(c, '000000', .45); c.fill()
    rr(c, -w/2, -h/2, w, h, 14); col(c, PAPER); c.fill_preserve(); c.set_line_width(6); col(c, INKC); c.stroke()
    ink_text(c, label, 0, 0, 44, INKC, 'Alfa Slab One', outline=.8); c.restore()
CONF = [(_jr.random()*6.28, 400+_jr.random()*1700, _jr.choice(['E63946', 'F4C430', '2A9D8F', '4361EE', 'FF8FA3', 'FFFFFF', 'F77F00']), _jr.random()*6.28, 8+_jr.random()*10) for _ in range(140)]
def confetti(c, t):
    u = t-V.BURST
    if u <= 0 or u > 4.5: return
    for (ang, v0, colr, ph, sz) in CONF:
        x = 540+math.cos(ang)*v0*u*math.exp(-u*1.1); y = 1300+math.sin(ang)*v0*u*math.exp(-u*1.1)+220*u*u
        a = 1-ease((u-3.2)/1.2)
        if a <= 0 or y > 1700: continue
        c.save(); c.translate(x, y); c.rotate(ph+u*6); c.scale(1, abs(math.sin(u*7+ph))+.15); c.rectangle(-sz/2, -sz/4, sz, sz/2); col(c, colr, a); c.fill(); c.restore()
def bulbs(c, w, h, t, n=10, r=9):
    """ampoules de marquise de cinéma qui clignotent doucement en chenillard"""
    pts = [(-w/2+w*i/n, -h/2) for i in range(n)]+[(w/2, -h/2+h*i/n) for i in range(n)]+[(w/2-w*i/n, h/2) for i in range(n)]+[(-w/2, h/2-h*i/n) for i in range(n)]
    for j, (x, y) in enumerate(pts):
        on = .55+.45*math.sin(t*5-j*.8)
        c.arc(x, y, r*1.9, 0, 2*math.pi); col(c, 'FFE9A8', .18*on); c.fill()
        c.arc(x, y, r, 0, 2*math.pi); col(c, 'FFF6D8' if on > .6 else 'E9C46A'); c.fill_preserve(); c.set_line_width(2); col(c, '6B4006'); c.stroke()
_AF = {}
def affiche_surf(name, w):
    if (name, w) not in _AF:
        im = Image.open(f'{D}/affiche_{name}.png').convert('RGB'); im = im.resize((w, int(w*16/9)), Image.LANCZOS).convert('RGBA')
        _AF[(name, w)] = S.sprite(im) if hasattr(S, 'sprite') and False else cairo.ImageSurface.create_for_data(bytearray(np.asarray(im)[..., [2, 1, 0, 3]].tobytes()), cairo.FORMAT_ARGB32, im.width, im.height)
    return _AF[(name, w)]
AFF = [('2026-11-16_dividendes', 8.51, 250, -.12), ('2026-11-07_pauvre', 10.16, 440, -.04), ('2026-10-29_carburant', 11.6, 640, .05), ('2026-11-05_ubisoft', 12.68, 830, .13)]
def affiches(c, t, out=0.0):
    w = 300; h = int(w*16/9)
    for (name, t0, x, rot) in AFF:
        k = t-t0
        if k <= 0: continue
        s = back(k/.4); y = 560-(1-ent(k, .35))*80
        if out > 0: y -= 1400*ease(out); rot_ = rot*(1+2*out)
        else: rot_ = rot
        c.save(); c.translate(x, y); c.rotate(rot_); c.scale(s, s)
        rr(c, -w/2-34+10, -h/2-34+16, w+68, h+68, 16); col(c, '000000', .45); c.fill()
        rr(c, -w/2-34, -h/2-34, w+68, h+68, 16); col(c, 'B4161B'); c.fill_preserve(); c.set_line_width(7); col(c, '6B0A0D'); c.stroke()
        rr(c, -w/2-8, -h/2-8, w+16, h+16, 6); col(c, GOLD[1]); c.fill()
        c.set_source_surface(affiche_surf(name, w), -w/2, -h/2); c.paint()
        bulbs(c, w+44, h+44, t+x/100, n=8, r=8); c.restore()
def big_title(c, t):
    k = t-V.BURST-.05
    if k <= 0 or t > 8.86: return
    a = 1-ease((t-8.41)/.4)
    c.save(); c.translate(540, 390); s = back(k/.35); c.scale(s, s)
    for g_, a_ in ((40, .10), (22, .16)): ink_text(c, "MISTER COIN", 0, 0, 122+g_//4, 'FFE27A', 'Alfa Slab One', a=a*a_, outline=g_)
    ink_text(c, "MISTER COIN", 0, 0, 122, GOLD[0], 'Alfa Slab One', a=a, outline=7)
    ink_text(c, "par Actions Bénéfices", 0, 92, 36, PAPER, 'Limelight', a=a*ent(k-.25, .3), outline=3.5); c.restore()
_AV = None
def avatar_surf(d=440):
    global _AV
    if _AV is None:
        im = Image.open(f'{D}/../../branding/avatar_profil_zoom.png').convert('RGBA').resize((d, d), Image.LANCZOS)
        m = Image.new('L', (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d-1, d-1), fill=255); im.putalpha(m)
        _AV = cairo.ImageSurface.create_for_data(bytearray(np.asarray(im)[..., [2, 1, 0, 3]].tobytes()), cairo.FORMAT_ARGB32, d, d)
    return _AV
def end_card(c_, t):
    k = t-14.91
    if k <= 0: return
    d = 440; s = back(k/.4); c_.save(); c_.translate(540, 470); c_.scale(s, s)
    c_.arc(10, 16, d/2+22, 0, 2*math.pi); col(c_, '000000', .45); c_.fill()
    c_.arc(0, 0, d/2+22, 0, 2*math.pi); col(c_, GOLD[1]); c_.fill_preserve(); c_.set_line_width(7); col(c_, '6B4006'); c_.stroke()
    c_.set_source_surface(avatar_surf(d), -d/2, -d/2); c_.paint()
    n = 22
    for j in range(n):
        an = 2*math.pi*j/n; on = .55+.45*math.sin(t*5-j*.9); x, y = math.cos(an)*(d/2+11), math.sin(an)*(d/2+11)
        c_.arc(x, y, 15, 0, 2*math.pi); col(c_, 'FFE9A8', .2*on); c_.fill(); c_.arc(x, y, 7, 0, 2*math.pi); col(c_, 'FFF6D8' if on > .6 else 'E9C46A'); c_.fill()
    c_.restore()
    kc = t-14.96
    if kc > 0:
        sc = back(kc/.35)*(1+.03*math.sin(t*6)); c_.save(); c_.translate(540, 800); c_.rotate(-.035); c_.scale(sc, sc); banner(c_, 0, 0, 660, 128, t=t)
        ink_text(c_, "ABONNE-TOI !", 0, 0, 62, INKC, 'Alfa Slab One', outline=1.2); c_.restore()
    if t > 15.84: ink_text(c_, "déjà +10 000 vues ce mois-ci", 540, 915, 34, PAPER, 'Alfa Slab One', outline=4.5, a=ent(t-15.84, .3))
# ================= scènes =================
def hook(c, t):
    """la question écrite en très grand dès la 1re image (son coupé) ; elle tremble quand la voix la prononce"""
    if t > 4.2: return
    a = 1-ease((t-3.9)/.3); sh_ = 6*math.sin(t*60)*math.exp(-max(0, t-3.08)*6) if t > 3.08 else 0
    s_ = 1+.04*math.sin(t*4)                                           # visible dès l'image 0, légère respiration
    c.save(); c.translate(540+sh_, 830); c.scale(s_, s_)
    ink_text(c, "TU N'Y COMPRENDS", 0, -52, 76, GOLD[0], 'Alfa Slab One', a=a, outline=6)
    ink_text(c, "RIEN ?", 0, 44, 112, GOLD[0], 'Alfa Slab One', a=a, outline=7); c.restore()
def b_intro(cv, c, t, k):
    hook(c, t)
    sign(c, 540, 300, "L'ÉCONOMIE", t-.05, t, w=560); sign(c, 540, 450, "LA BOURSE", t-.84, t, w=500); sign(c, 540, 600, "LES FINANCES PERSO", t-1.54, t, w=700)
def b_flou(cv, c, t, k):
    for i, (lab, y, w) in enumerate((("L'ÉCONOMIE", 300, 560), ("LA BOURSE", 450, 500), ("LES FINANCES PERSO", 600, 700))):   # les panneaux se décrochent et tombent
        u = t-3.08-.12*i
        if u < 0: sign(c, 540, y, lab, 9, t, w=w); continue
        yy = y+1600*u*u
        if yy < 1300: c.save(); c.translate(0, yy-y); c.rotate(.12*u*(1 if i % 2 else -1)); sign(c, 540, y, lab, 9, t, w=w); c.restore()
    hook(c, t); jargon(c, t)
    stamp(c, 540, 860, "C'EST NORMAL", None, t-4.3, t, rot=-.04, w=480, h=96)
def b_couleur(cv, c, t, k):
    jargon(c, t); confetti(c, t); big_title(c, t)
    if t > 8.36:
        out = ease((t-14.56)/.45) if t > 14.56 else 0
        affiches(c, t, out)
    stamp(c, 540, 905, "SANS JARGON", None, t-14, t, rot=.04, w=470, h=96) if t < 14.91 else None
    end_card(c, t)
SC = [(0.0, 3.0, b_intro, 'scene'), (3.0, V.BURST, b_flou, 'scene'), (V.BURST, DUR, b_couleur, 'couleur')]
BLOCS = [(0.0, V.BURST, 'scene')]
def burst_r(t): return 1500*ease((t-V.BURST)/.5) if t > V.BURST else 0
def frame(t):
    i = max(j for j, s_ in enumerate(SC) if t >= s_[0] or j == 0); a, b, f, dec = SC[i]
    bw = None
    if t < V.BURST+.55: bw = np.repeat(decor('scene', min(t, V.BURST-.01))[..., None], 3, 2).astype(np.float32)
    img = bw
    if t >= V.BURST:
        colr = decor_col(t); r = burst_r(t)
        if r >= 1499: img = colr
        else:
            yy, xx = np.ogrid[:H, :W]; m = np.clip((r-np.sqrt((xx-540.)**2+(yy-1350.)**2))/30+.5, 0, 1)[..., None].astype(np.float32)
            img = bw*(1-m)+colr*m
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    for j in (i-1, i):
        if j < 0: continue
        a_, b_, f_, d_ = SC[j]
        if j == i-1 and t-a > .3: continue
        al = 1-ent(t-b_, .3) if j == i-1 else (ent(t-a, .3) if i > 0 else 1)
        if j == i-1 and SC[i][2] is b_couleur: al = 1-ent(t-b_, .15)
        lay = cv.copy(); s, c = surface(); f_(lay, c, t, max(0.0, t-a_)); lay.alpha_composite(to_img(s))
        cv = Image.blend(cv, lay, al) if al < .999 else lay
    arr = np.asarray(cv.convert('RGB')).astype(np.float32)
    arr = coin_bw(arr, t)
    if t < V.BURST: arr = film(arr, t)
    else:                                                                  # après l'explosion : grain léger seulement, l'image reste éclatante
        fl = film(arr.copy(), t); arr = arr*.7+fl*.3
        u = t-V.BURST                                                      # éclair blanc de l'explosion
        if u < .35: arr = arr+(255-arr)*(.75*(1-u/.35))
        r = burst_r(t)
        if 0 < r < 1499:
            yy, xx = np.ogrid[:H, :W]; ring = np.exp(-((np.sqrt((xx-540.)**2+(yy-1350.)**2)-r)/22)**2)[..., None]; arr = arr+(255-arr)*ring*.8
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); cap_bw(c, t); out.alpha_composite(to_img(s))
    return out
def cap_bw(c, t):
    for k, (a, b, s_, hl) in enumerate(V.CAPS):
        nxt = V.CAPS[k+1][0] if k+1 < len(V.CAPS) else DUR; end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(V.CAPS) else 1)
            S.caption(c, s_, hl=S.GD if hl in (S.GD, S.GR) else PAPER, a=al); return
IRIS = []; IR = .42
def events():
    ev = V.events() + [(.05, 'pop'), (.84, 'pop'), (1.54, 'pop'), (3.1, 'crash'), (4.3, 'thud'), (6.85, 'riser'), (V.BURST, 'tadaa'), (V.BURST+.05, 'impact'),
                       (V.BURST+.15, 'coins'), (8.51, 'pop'), (10.16, 'pop'), (11.6, 'pop'), (12.68, 'pop'), (14, 'thud'), (14.56, 'whoosh'),
                       (14.91, 'glint'), (14.96, 'pop'), (15.84, 'coin'), (COL_T+.05, 'glint')]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/bw_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(k/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
