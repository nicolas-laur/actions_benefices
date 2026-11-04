"""Assemblage provisoire Ubisoft, sans voix : obscurité et lueur → clocher (marche, saut, spirale qui se dessine) → fondu au noir
(on descend de la tour) → souterrain : la brèche, puis le premier panneau de verre. Les minutages se recaleront sur la voix.
usage : python3 assemble.py png t1 t2 … | render"""
import os, sys, math, subprocess
os.environ.setdefault('TXT', '0'); os.environ.setdefault('AMB', '0')
import numpy as np, cv2, functools
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import proto_intro as I, proto_breche as B
_SKY = I.sky_logo; I.sky_logo = lambda cv, t: None        # la spirale est dessinée ici, pour pouvoir la garder sur fond noir
W, H, FPS = I.W, I.H, 60
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def inout(x): x = clamp(x); return x*x*(3-2*x)
DARK = 3.92                                 # obscurité et lueur : deux mesures de musique avant que la scène s'ouvre
S_END = 13.9                                # fin de la scène du clocher (global 17,8 s) : spirale tracée, « Ubisoft » prononcé
T_TXT = 19.18                               # la spirale, seule sur fond noir, puis le texte (premier temps)
T_OUT = 22.6                                # spirale et texte s'effacent (la musique finit sur un fondu)
FADE = .7                                   # fondu au noir : on descend
B_SKIP = 1.16                               # l'explosion (3,08 s dans la vidéo Gemini) tombe sur le temps fort de 24,92 s
T_B = 23.0                                  # début de la brèche, sur un premier temps
DUR = T_B+(B.DUR-B_SKIP)
BEAT0, BEAT = .09, .4787                    # grille de la musique de Nicolas
@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); return xx, yy
_P = np.random.default_rng(9).uniform(0, 1, (90, 4))          # particules en orbite autour de l'orbe
def beat_pulse(t):
    """battement : montée brève puis retombée, plus fort sur le premier temps de chaque mesure"""
    k = (t-BEAT0)/BEAT; n = math.floor(k); d = (k-n)*BEAT
    if n < 0: return 0.0
    amp = 1.0 if n % 4 == 0 else .55
    return amp*math.exp(-d/.16)*min(1, d/.02)
UBI_BLUE = np.array([30, 110, 255.]); UBI_DEEP = np.array([12, 40, 140.]); UBI_ICE = np.array([190, 225, 255.])
# présages : fragments de l'histoire qui apparaissent autour de l'orbe, au rythme de la musique (temps d'apparition = numéro de temps)
OMENS = [("-95 %", 0, 540, 520, 96, 0.0), ("2018", 2, 250, 640, 44, .6), ("107,90 €", 3, 820, 600, 40, .3), ("6 JEUX ARRÊTÉS", 5, 280, 1050, 30, .5),
         ("-40 % EN UN JOUR", 6, 790, 1100, 30, .2), ("1,24 MD€ DE PERTES", 7, 540, 1180, 30, .7), ("TENCENT", 4, 840, 900, 32, .4), ("GAME OVER ?", 7.5, 540, 1300, 40, .9)]
GLY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%"
def scramble(s, u, seed):
    k = int(u*len(s)*1.0001); rng = np.random.default_rng(seed+int(u*40))
    return ''.join(ch if (i < k or ch in ' ,.€%-?') else GLY[rng.integers(len(GLY))] for i, ch in enumerate(s))
def _rel(t, b0):
    return t-(BEAT0+b0*BEAT)
DISS = .65                                   # durée de la dissolution d'un présage
def omen_end(s, b0):
    return (DARK-1.05) if s == "-95 %" else min(BEAT0+b0*BEAT+1.45, DARK-.8)            # tout est aspiré avant que l'orbe éclate
@functools.lru_cache(maxsize=16)
def text_points(s, size, fam):
    """points tirés des pixels du texte (centré sur 0,0), pour le faire partir en poussière"""
    import cairo
    w, h = int(size*len(s)*.8)+40, int(size*1.8)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(surf); I.text(c, s, w/2, h/2, fam, size, 'FFFFFF', 'c', 1, 3); surf.flush()
    al = np.frombuffer(surf.get_data(), np.uint8).reshape(h, surf.get_stride()//4, 4)[:, :w, 3]
    ys, xs = np.where(al > 128); rng = np.random.default_rng(len(s)); idx = rng.choice(len(xs), min(len(xs), 260), replace=False)
    return np.stack([xs[idx]-w/2, ys[idx]-h/2], 1).astype(np.float32), rng.uniform(0, .25, len(idx)).astype(np.float32)
def omens(c, t, cx=540, cy=820):
    """chaque fragment surgit en se décodant, scintille sur les temps, puis se dissout en particules aspirées par l'orbe ;
    le −95 % est là dès l'image 0 (test chiffre choc)"""
    for s, b0, x, y, size, ph in OMENS:
        k = _rel(t, b0); te = omen_end(s, b0); fam = 'k' if s == "-95 %" else 'xb'
        dy = -18*k if s != "-95 %" else 0
        if t < te:
            if s == "-95 %": a = .95; txt = s
            else:
                if k < 0: continue
                a = min(1, k/.12)*(.75+.25*beat_pulse(t)); txt = scramble(s, clamp(k/.45), 3+int(ph*10))
            I.text(c, txt, x, y+dy, fam, size, 'D6E6FF' if s != "-95 %" else 'FFFFFF', 'c', a, 3)
        else:
            kd = (t-te)/DISS
            if kd >= 1: continue
            P, dl = text_points(s, size, fam); y0 = y+(-18*(te-(BEAT0+b0*BEAT)) if s != "-95 %" else 0)
            if kd < .25: I.text(c, s, x, y0, fam, size, 'D6E6FF', 'c', 1-kd/.25, 3)
            for (px, py), d in zip(P, dl):
                u = clamp((kd-d)/(1-d)); e = u*u*u                                   # accélère en approchant du cœur
                sx, sy = x+px, y0+py; X, Y = sx+(cx-sx)*e, sy+(cy-sy)*e
                X += 14*math.sin(u*9+px)*(1-u); c.arc(X, Y, 1.8*(1-.6*u), 0, 2*math.pi); c.set_source_rgba(.8, .9, 1, .9*(1-u**4)); c.fill()
def orb(t, cx=540, cy=820):
    """orbe d'énergie aux couleurs d'Ubisoft (bleu électrique, cœur blanc) : elle pulse sur la musique, ses anneaux vibrent, ses particules battent"""
    xx, yy = _grid(); d = np.hypot(xx-cx, yy-cy)
    p = beat_pulse(t); grow = inout((t-(DARK-1.0))/1.0)
    R = 44*(1+.2*p)*(1+1.4*grow)+5*math.sin(t*5)
    core = np.exp(-(d/R)**2); halo = np.exp(-(d/(R*3.0))**2)*(.6+.5*p); far = np.exp(-(d/(R*9))**2)*.22*(1+p)
    img = core[..., None]*np.array([255, 255, 255.])+halo[..., None]*UBI_BLUE*.85+far[..., None]*UBI_DEEP
    # anneaux, particules et présages dessinés au vecteur, puis lissés en halo
    s, c = I.surface()
    for n in range(3):                                                              # anneaux qui vibrent (ondulation + tremblement sur les temps)
        ph = (t*.8+n/3) % 1; rr = R*(1.7+3.2*ph); al = (1-ph)*.75
        c.new_path()
        for k in range(181):
            a_ = k/180*2*math.pi
            wob = 1+.035*math.sin(6*a_+t*9+n)+.05*p*math.sin(11*a_-t*23)
            x, y = cx+rr*wob*math.cos(a_), cy+rr*wob*math.sin(a_)*.92
            (c.move_to if k == 0 else c.line_to)(x, y)
        c.close_path(); c.set_line_width(3+3*p); c.set_source_rgba(.65, .82, 1, al); c.stroke()
    for a0, r0, sp, sz in _P:                                                       # particules qui battent avec la musique
        ang = a0*6.283+t*(.6+sp)*(1 if sp > .5 else -1); r = R*(1.6+r0*4.5)*(1+.12*p)
        x, y = cx+r*math.cos(ang), cy+r*math.sin(ang)*.85; rad = (1.4+sz*2.6)*(1+1.3*p*(.5+sz))
        c.arc(x, y, rad, 0, 2*math.pi); c.set_source_rgba(.78, .9, 1, .35+.6*p*sz+.25); c.fill()
    omens(c, t)
    lay = np.asarray(I.to_img(s)).astype(np.float32)
    rgbL, aL = lay[..., :3], lay[..., 3:]/255
    glow = cv2.GaussianBlur(rgbL*aL, (0, 0), 9)*1.3
    img = img+glow*np.array([.55, .75, 1.0])+rgbL*aL
    return np.clip(img, 0, 255)
import mty
mty.FAM['cyb'] = ('Orbitron', 1); mty.FAM['raj'] = ('Rajdhani', 1)
CYAN, MAG = (0, 240, 255), (255, 46, 136)
TITLE = ("ACTIONS BÉNÉFICES PRÉSENTE", "L'ACTION UBISOFT", "UBI | EURONEXT PARIS")
GLY2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%/<>[]_=+"
def scramble2(s, u, seed):
    k = int(u*len(s)*1.0001); rng = np.random.default_rng(seed+int(u*50))
    return ''.join(ch if (i < k or ch in " |'") else GLY2[rng.integers(len(GLY2))] for i, ch in enumerate(s))
GL_BURSTS = [(0.0, .50, 1.0), (1.35, .14, .55), (2.2, .10, .4), (2.85, .16, .6)]      # (début après T_TXT, durée, force)
def glitch_level(t):
    k = t-T_TXT; g = 0.0
    for s0, d, f in GL_BURSTS:
        if s0 <= k < s0+d: g = max(g, f*(1-.6*(k-s0)/d))
    if t >= T_OUT: g = max(g, .5+.5*clamp((t-T_OUT)/.35))
    return g
def glitch(img, t, g):
    """effet glitch cyberpunk : décalage RVB, tranches déplacées, blocs corrompus, lignes de balayage"""
    a = img.astype(np.float32); fr = int(t*30)                                     # le motif change toutes les 2 images
    rng = np.random.default_rng(1000+fr)
    dx = int(2+26*g)
    out = a.copy(); out[..., 0] = np.roll(a[..., 0], dx, 1); out[..., 2] = np.roll(a[..., 2], -dx, 1)
    if g > .05:
        for _ in range(int(4+18*g)):                                                # tranches horizontales décalées
            y0 = rng.integers(0, H-60); hh = rng.integers(4, 46); sh = int(rng.normal(0, 90*g))
            out[y0:y0+hh] = np.roll(out[y0:y0+hh], sh, 1)
        for _ in range(int(2+6*g)):                                                 # blocs corrompus teintés cyan / magenta
            y0 = rng.integers(500, 1450); x0 = rng.integers(60, 900); hh = rng.integers(10, 60); ww = rng.integers(60, 320)
            tint = np.array(CYAN if rng.random() < .5 else MAG, np.float32)
            blk = out[y0:y0+hh, x0:x0+ww]; out[y0:y0+hh, x0:x0+ww] = np.maximum(blk*.6, tint*(.25+.5*rng.random())*(blk.mean(2, keepdims=True) > 30))
        noise = (rng.random((H, W)) < .004*g)[..., None]*255; out = np.maximum(out, noise)
    out[::3] *= .82                                                                 # lignes de balayage (toujours là, discrètes)
    return np.clip(out, 0, 255)
def title_layer(t):
    """titre cyberpunk sous la spirale : texte qui se décode, ticker dans un cadre aux coins coupés"""
    kt = t-T_TXT; ss, c = I.surface()
    if kt <= 0: return ss, c
    u1 = clamp(kt/.7); u2 = clamp((kt-.25)/.8); u3 = clamp((kt-.7)/.7)
    I.text(c, scramble2(TITLE[0], u1, 31), 540, 1135, 'raj', 40, 'BFF6FF', 'c', min(1, kt/.1), 9)
    for off, colr, al in (((-3, 0), 'FF2E88', .7), ((3, 0), '00F0FF', .7), ((0, 0), 'FFFFFF', 1)):     # titre en relief chromatique
        if u2 > 0: I.text(c, scramble2(TITLE[1], u2, 32), 540+off[0], 1225+off[1], 'cyb', 66, colr, 'c', al*min(1, (kt-.25)/.1), 3)
    if u3 > 0:
        s3 = scramble2(TITLE[2], u3, 33); w = I.tw(c, TITLE[2], 'cyb', 30, 4)+70; x0, y0, hh, cut = 540-w/2, 1290, 66, 16
        c.new_path(); c.move_to(x0+cut, y0); c.line_to(x0+w, y0); c.line_to(x0+w, y0+hh-cut); c.line_to(x0+w-cut, y0+hh); c.line_to(x0, y0+hh); c.line_to(x0, y0+cut); c.close_path()
        c.set_source_rgba(0, .94, 1, .12*ease_(u3)); c.fill_preserve(); c.set_line_width(2.5); c.set_source_rgba(0, .94, 1, .95*ease_(u3)); c.stroke()
        c.rectangle(x0+w-8, y0+6, 4, 18); c.set_source_rgba(1, .18, .53, .9*ease_(u3)); c.fill()
        I.text(c, s3, 540, y0+hh/2, 'cyb', 30, 'E8FDFF', 'c', ease_(u3), 4)
    return ss, c
def ease_(x): x = clamp(x); return 1-(1-x)**3
def logo_layer(t):
    """la spirale (tracée au saut), qui descend au centre de l'écran noir, scintille sur la musique ; puis le texte se décode dessous"""
    s = t-DARK; cv = Image.new('RGBA', (W, H), 0)
    if s <= I.T_JUMP+.05: return cv
    _SKY(cv, s)
    k = t-(DARK+S_END); u = inout(k/1.2) if k > 0 else 0.0
    arr = np.asarray(cv).astype(np.float32)
    if u > 0: M = np.float32([[1, 0, 0], [0, 1, 330*u]]); arr = cv2.warpAffine(arr, M, (W, H))
    if k > 0:                                                                       # scintillement : reflet qui balaie la spirale + battement
        p = beat_pulse(t); band = ((t-T_TXT) % 1.915)/1.915
        xx, yy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        sweep = np.exp(-(((xx-yy*.6)-(-200+1600*band))/60)**2)
        al = arr[..., 3:]/255; arr[..., :3] = np.clip(arr[..., :3]*(1+.25*p)+255*sweep[..., None]*al*.8, 0, 255)
        arr[..., 3] = np.clip(arr[..., 3]*(1+.15*p), 0, 255)
    cv = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    ss, _ = title_layer(t); cv.alpha_composite(I.to_img(ss))
    return cv
def frame(t):
    if t < T_B:
        s = max(0.0, t-DARK)                                                              # la scène reste figée dans le noir, puis démarre
        im = I.frame(min(s, S_END)).convert('RGB')
        if t < DARK: im = Image.fromarray(orb(t).astype(np.uint8))
        elif t < DARK+.6:                                                            # l'orbe éclate en lumière blanche qui dévoile le clocher
            u = (t-DARK)/.6; a_ = np.asarray(im).astype(np.float32); fl = (1-inout(u))**1.5
            a_ = a_*(1-fl)+np.array([255, 250, 238])*fl; im = Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))
        kf = t-(DARK+S_END)
        if kf > 0:                                                                        # la scène s'éteint, la spirale reste
            u = inout(kf/FADE); a = np.asarray(im).astype(np.float32)*(1-u); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        if t > DARK:
            im = im.convert('RGBA'); im.alpha_composite(logo_layer(t)); im = im.convert('RGB')
        if t >= T_TXT-.02:
            arr = glitch(np.asarray(im), t, glitch_level(t))
            if t > T_OUT+.18:                                                            # extinction façon vieil écran : l'image s'écrase en une ligne
                u = clamp((t-(T_OUT+.18))/.2); sy = max(.004, (1-u)**3); sx = 1 if u < .7 else max(.002, 1-(u-.7)/.3)
                M = np.float32([[sx, 0, 540*(1-sx)], [0, sy, 960*(1-sy)]]); arr = cv2.warpAffine(arr, M, (W, H))
                arr = arr*(1+2.5*u*(u < .95))
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        return im
    bt = B_SKIP+(t-T_B); im = B.frame(bt).convert('RGB')
    k = t-T_B
    if k < .45: im = Image.fromarray((np.asarray(im).astype(np.float32)*inout(k/.45)).astype(np.uint8))
    return im
def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), round(T_B, 2)); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]: frame(float(ts)).save(f'{D}/prev/a_{ts}.png')
        return
    out = f'{D}/out/apercu_assemblage_ubisoft_muet.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('ok', out)
if __name__ == '__main__': main()
