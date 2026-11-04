"""Aperçu de la brèche Ubisoft (≈ 9 s, sans voix) : vidéo Gemini du mur qui explose, trou en fond vert détouré, derrière lequel
attend notre décor « PEA/CTO » (salle sombre, panneau de verre 3D) ; la caméra traverse le trou pour entrer dans l'argumentaire.
usage : python3 proto_breche.py png t1 t2 … | render"""
import sys, os, math, subprocess, functools
import numpy as np, cv2, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from bglass import gpanel, place, glow_text, tilt_quad, with_alpha
import veo_coin as VC
FPS = 60; DUR = 9.4
HOLE = (555, 920)                                                    # centre du trou (mesuré sur le fond vert)
T_PUSH = 6.4                                                         # la caméra traverse le trou
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]

@functools.lru_cache(maxsize=1)
def breach_frames():
    cap = cv2.VideoCapture(f'{D}/decors/breche.mp4'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        f = cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC)[..., ::-1]
        a, m = VC._key(np.asarray(f))
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
        F.append((np.clip(a, 0, 255).astype(np.uint8), (np.clip(m, 0, 1)*255).astype(np.uint8)))
    return F
def breach(t):
    F = breach_frames(); x = t*24; i = min(int(x), len(F)-1); return F[i]

# ---------- la salle derrière le mur : sombre, froide, une lumière rasante, poussière ----------
@functools.lru_cache(maxsize=1)
def room_base():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('05070C')); g.add_color_stop_rgb(.55, *rgb('0A0F18')); g.add_color_stop_rgb(1, *rgb('06080D')); c.set_source(g); c.paint()
    r = cairo.RadialGradient(540, 820, 0, 540, 820, 900); r.add_color_stop_rgba(0, .21, .84, 1, .16); r.add_color_stop_rgba(1, .21, .84, 1, 0); c.set_source(r); c.paint()
    for i in range(0, H, 120):                                                     # sol et lignes de fuite discrètes
        c.move_to(0, 1500+i*.4); c.line_to(W, 1500+i*.4); c.set_source_rgba(1, 1, 1, .025); c.set_line_width(1); c.stroke()
    return to_img(s)
def room(t):
    cv = room_base().copy(); s, c = surface()
    rng = np.random.default_rng(4)
    for k in range(70):                                                            # poussière qui retombe après l'explosion
        x = (rng.uniform(0, W)+12*math.sin(t*.5+k)) % W; y = (rng.uniform(0, H)+t*25) % H; r = rng.uniform(.8, 2.4)
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(.85, .9, 1, rng.uniform(.05, .22)); c.fill()
    cv.alpha_composite(to_img(s))
    k = t-(T_PUSH-.4)
    def d(kk, w, h):
        text(kk, "LE RECORD", w/2, 60, 'xb', 30, 'E8EEF8', 'c', .9, 6)
        text(kk, "18 JUILLET 2018", w/2, h-60, 'xb', 28, 'E8EEF8', 'c', .8, 4)
    u = ease(k/.9)
    place(cv, gpanel(780, 420, d, tint='CFE8FF', ta=.08, edge=.75), tilt_quad(540, 860, 780, 420, rx=.08+.22*(1-u)), 1.0, 18, .5)
    glow_text(cv, "107,90 €", 540, 860, 150, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.6, a=1.0, reflect=False)
    return cv
def push(t):
    """traversée du trou : zoom sur le mur, la salle derrière avance moins vite (parallaxe)"""
    return inout((t-T_PUSH)/1.3)
def frame(t):
    u = push(t)
    cv = room(t)
    zr = lerp(1.18, 1.0, u)                                                        # la salle, vue à travers le trou, se rapproche doucement
    if zr != 1:
        M = cv2.getRotationMatrix2D(HOLE, 0, zr); cv = Image.fromarray(cv2.warpAffine(np.asarray(cv), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), 'RGBA')
    if u < .999:
        a, m = breach(t); zb = lerp(1.0, 3.2, u*u)                                   # le mur, au premier plan, file hors du cadre
        if zb != 1:
            M = cv2.getRotationMatrix2D(HOLE, 0, zb)
            a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); m = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
            if u > .2: bl = 6*u; a = cv2.GaussianBlur(a, (0, 0), bl)
        lay = np.dstack([a, m]); cv.alpha_composite(Image.fromarray(lay, 'RGBA'))
    return finish(cv, t, 2.5)
def main():
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/b_{ts}.png')
        return
    os.makedirs(f'{D}/out', exist_ok=True)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', f'{D}/out/apercu_breche_ubisoft_muet.mp4'], stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('ok')
if __name__ == '__main__': main()
