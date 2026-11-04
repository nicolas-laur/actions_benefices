"""Aperçu de l'ouverture Ubisoft (≈ 7 s, sans voix) : vidéo Gemini du clocher, planche suivie image par image, Mister Coin de dos
qui avance jusqu'au bout de la planche (clip classique_dos_marche, détouré), chiffre choc « −95 % » dès l'image 0, tuile Ubisoft.
usage : python3 proto_intro.py png t1 t2 … | render"""
import sys, os, json, math, subprocess, functools
import numpy as np, cv2, cairo
from PIL import Image
from scipy.signal import savgol_filter
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from bglass import glow_text, with_alpha
import veo_coin as VC
FPS = 60; DUR = 9.0
AMB = os.environ.get('AMB', '1') == '1'
TXT = os.environ.get('TXT', '1') == '1'                                              # TXT=0 : image seule, sans chiffre ni sous-titre                                              # ambiance (vent, nappe, coups sourds) ; AMB=0 : pas seuls
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u

# ---------- décor : vidéo du clocher (24 i/s), images fondues pour un mouvement fluide à 60 i/s ----------
@functools.lru_cache(maxsize=1)
def bg_frames():
    cap = cv2.VideoCapture(f'{D}/decors/clocher.mp4'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC)[..., ::-1])
    return F
def bg(t):
    F = bg_frames(); x = t*24; i = int(x); u = x-i; i = min(i, len(F)-1); j = min(i+1, len(F)-1)
    return F[i].astype(np.float32)*(1-u)+F[j].astype(np.float32)*u
# ---------- suivi de la planche : bout de planche et échelle, lissés ----------
TR = np.array(json.load(open(f'{D}/decors/clocher_track.json')))
TRs = np.stack([savgol_filter(TR[:, k], 31, 3) for k in range(3)], 1)
TIP0 = np.array([536.0, 1438.0])
def track(t):
    x = t*24; i = int(x); u = x-i; i = min(i, len(TRs)-1); j = min(i+1, len(TRs)-1)
    return TRs[i]*(1-u)+TRs[j]*u
def plank_point(t, y0):
    """point de l'axe de la planche (exprimé sur l'image 0) suivi à l'instant t"""
    tx, ty, s = track(t); return tx+s*(TIP0[0]-TIP0[0]), ty+s*(y0-TIP0[1]), s

# ---------- Mister Coin de dos ----------
@functools.lru_cache(maxsize=2)
def clip_frames(name, crop):
    cap = cv2.VideoCapture(f'{ROOT}/mister_coin/veo/classique_dos_{name}.mp4'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        a, m = VC._key(np.asarray(f[..., ::-1])); cy, cx = slice(*crop[0]), slice(*crop[1])
        F.append((np.clip(a[cy, cx], 0, 255).astype(np.uint8), (m[cy, cx]*255).astype(np.uint8)))
    return F
# deux clips de dos : la marche (sur place) et le plongeon (inspiration, bras en croix, petit saut, chute)
CLIPS = {'marche': dict(crop=((300, 1080), (100, 620)), feet=1034-300, cx=360-100, diam=360.0),
         'plongeon': dict(crop=((300, 1280), (0, 720)), feet=978-300, cx=358, diam=360.0/1.18)}   # même taille à l'écran : 1,18 = rapport des hauteurs
WALK_END = 4.2                     # arrivée au bout de la planche
B_START, B_SPEED = 4.4, 1.5        # bascule sur le plongeon (pose neutre identique), joué ×1,5
def b_time(t): return .9+(t-B_START)*B_SPEED if t < B_START+(4.75-.9)/B_SPEED else 4.75+(t-(B_START+(4.75-.9)/B_SPEED))
T_JUMP = B_START+(4.75-.9)/B_SPEED  # quitte la planche (≈ 6,97 s)
def coin_state(t):
    u = clamp(t/WALK_END); u = u*.85+ease(u)*.15
    y0 = lerp(1905, 1470, u); x, y, s = plank_point(t, y0)
    diam = lerp(255, 205, u)
    if t < WALK_END: return x, y, diam, 'marche', 1.0+t*(6.0/WALK_END)
    if t < B_START: return x, y, diam, 'marche', 7.0+(t-WALK_END)
    return x, y, diam, 'plongeon', min(9.9, b_time(t))                                      # le clip tombe tout droit : on le laisse jouer
def coin_layer(t):
    x, y, diam, clip, ct = coin_state(t); C = CLIPS[clip]; F = clip_frames(clip, C['crop']); rgb, m = F[min(len(F)-1, int(ct*24))]
    k = diam/C['diam']
    kf = t-T_JUMP
    w, h = max(2, int(rgb.shape[1]*k)), max(2, int(rgb.shape[0]*k))
    rgb = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA); m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    ox, oy = int(x-C['cx']*k), int(y-C['feet']*k)
    if kf > 0:                                                                          # chute à pic : la chute du clip + la gravité
        x1, y1, _, _, _ = coin_state(T_JUMP); ox = int(x1-C['cx']*k); oy = int(y1-C['feet']*k+1400*kf*kf)
    return rgb, m, ox, oy, k
def occluder(t):
    """planche et rebord du clocher (plus proches que le vide) : ils passent devant lui une fois qu'il a sauté"""
    tx, ty, s = track(t); mk = np.zeros((H, W), np.float32)
    def P(x, y): return [int(tx+s*(x-TIP0[0])), int(ty+s*(y-TIP0[1]))]
    cv2.fillPoly(mk, [np.array([P(432, 1438), P(640, 1438), P(676, 1712), P(398, 1712)])], 1.0)
    cv2.fillPoly(mk, [np.array([P(-400, 1712), P(1480, 1712), P(1480, 2600), P(-400, 2600)])], 1.0)
    return cv2.GaussianBlur(mk, (0, 0), 1.5)
def paste(base, rgb, m, ox, oy):
    h, w = m.shape; x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+w), min(H, oy+h)
    if x1 <= x0 or y1 <= y0: return base
    a = m[y0-oy:y1-oy, x0-ox:x1-ox, None].astype(np.float32)/255
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1]*(1-a)+rgb[y0-oy:y1-oy, x0-ox:x1-ox].astype(np.float32)*a
    return base

# ---------- chiffre choc et tuile ----------
@functools.lru_cache(maxsize=8)
def tile(size):
    from PIL import ImageDraw, ImageFilter
    im = Image.open(f'{D}/logos/UBI.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size+60, size+60), 0); mm = Image.new('L', (size+60, size+60), 0)
    ImageDraw.Draw(mm).rounded_rectangle((30, 40, 30+size, 40+size), radius=size*.22, fill=160)
    sh.putalpha(mm.filter(ImageFilter.GaussianBlur(12))); sh.alpha_composite(im, (30, 30)); return sh
def overlay(cv, t):
    s, c = surface()
    # voile sombre en haut pour que le chiffre se lise sur le ciel clair
    g = cairo.LinearGradient(0, 0, 0, 820); g.add_color_stop_rgba(0, 0, 0, .02, .55); g.add_color_stop_rgba(1, 0, 0, .02, 0); c.set_source(g); c.rectangle(0, 0, W, 820); c.fill()
    cv.alpha_composite(to_img(s))
    sc = 1+.04*math.sin(min(t, 1.2)/1.2*math.pi/2)                                       # chiffre présent dès l'image 0, il respire à peine
    glow_text(cv, "-95 %", 540, 480, 230, top='FFFFFF', bottom='FFC2C9', glow='FF4057', ga=.75, a=1.0, scale=sc, reflect=False)
    im = tile(120); cv.alpha_composite(im, (int(540-60-30-250), int(250-60-30)))
    s, c = surface()
    text(c, "UBISOFT", 540-120, 250, 'k', 64, 'FFFFFF', 'l', 1, 4)
    w = tw(c, "DEPUIS SON RECORD DE 2018", 'xb', 30, 3)+60; rr(c, 540-w/2, 655-30, w, 60, 30); col(c, '0B0E14', .78); c.fill()
    text(c, "DEPUIS SON RECORD DE 2018", 540, 655, 'xb', 30, 'FFFFFF', 'c', 1, 3)
    # emplacement des sous-titres pendant l'ouverture (remontés au-dessus de Mister Coin)
    cap1, cap2 = "Plus de 95 %. C'est ce qu'a perdu", "l'action Ubisoft…"
    rr(c, 540-410, 880-50, 820, 130, 26); col(c, '0B0E14', .72); c.fill()
    text(c, cap1, 540, 880, 'b', 42, 'FFFFFF', 'c', 1); text(c, cap2, 540, 940, 'b', 42, 'FFFFFF', 'c', 1)
    text(c, "(sous-titre provisoire, en attendant la voix)", 540, 1010, 'sb', 20, 'FFFFFF', 'c', .6)
    cv.alpha_composite(to_img(s))
@functools.lru_cache(maxsize=1)
def spiral():
    return Image.open(f'{D}/logos/UBI_spirale_blanche.png').convert('RGBA')
@functools.lru_cache(maxsize=1)
def spiral_glow():
    from PIL import ImageFilter
    im = spiral(); g = Image.new('RGBA', (im.width+240, im.height+240), 0); g.alpha_composite(im, (120, 120))
    a = g.getchannel('A').filter(ImageFilter.GaussianBlur(40)); out = Image.new('RGBA', g.size, (255, 236, 200, 0)); out.putalpha(a.point(lambda v: int(v*.9))); return out
T_LOGO = None
def sky_logo(cv, t):
    """au moment du saut, la spirale Ubisoft apparaît dans le ciel, avec un halo, et tourne lentement"""
    k = t-(T_JUMP+.05)
    if k <= 0: return
    a = ease(k/.35); sc = lerp(.6, 1.0, 1-(1-clamp(k/.6))**3)*(1+.03*math.sin(k*2)); size = int(380*sc)
    rot = -12*k
    for img, extra in ((spiral_glow(), 1.4), (spiral(), 1.0)):
        im = img.resize((int(size*extra*img.width/600/ (1.4 if extra > 1 else 1)), int(size*extra*img.height/600/(1.4 if extra > 1 else 1))), Image.LANCZOS) if extra == 1.0 else img.resize((int(size*img.width/600), int(size*img.height/600)), Image.LANCZOS)
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        cv.alpha_composite(with_alpha(im, a*(.85 if extra > 1 else .95)), (int(540-im.width/2), int(470-im.height/2)))
def plunge(t):
    """caméra qui plonge dans le vide après le saut : on descend et on avance"""
    return ease((t-(T_JUMP+.05))/1.1)
def frame(t):
    base = bg(t)
    rgb, m, ox, oy, k = coin_layer(t)
    x, y, diam, clip, ct = coin_state(t)
    if t < T_JUMP+.05:                                                                   # ombre douce sous les pieds, sur les lattes
        sh = np.zeros((H, W), np.float32); cv2.ellipse(sh, (int(x), int(y)), (int(diam*.55), int(diam*.09)), 0, 0, 360, .45, -1); sh = cv2.GaussianBlur(sh, (0, 0), 6+diam*.03)
        base *= (1-sh[..., None])
    M = None
    behind = base.copy()
    base = paste(base, rgb, m, ox, oy)
    if t > T_JUMP:                                                                      # la planche, plus proche que lui, passe devant
        oc = occluder(t)
        if M is not None: oc = cv2.warpAffine(oc, M, (W, H))
        base = base*(1-oc[..., None])+behind*oc[..., None]
    cv = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    sky_logo(cv, t)
    if TXT: overlay(cv, t)
    return finish(cv, t, 2.5)
STEPS = [1.21, 1.58, 2.04, 2.46, 2.83, 3.17, 3.54, 3.79, 4.04, 4.5, 5.0, 5.25, 5.71, 5.96, 6.42]
def sound():
    SR = 48000; n = int(DUR*SR); tt = np.arange(n)/SR; rng = np.random.default_rng(1); out = np.zeros(n)
    from scipy.signal import butter, sosfilt
    def bp(x, a, b): return sosfilt(butter(2, [a, b], 'bandpass', fs=SR, output='sos'), x)
    def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
    wind = lp(rng.standard_normal(n), 600)*(.05+.03*np.sin(2*np.pi*.18*tt))+bp(rng.standard_normal(n), 1500, 3000)*.006*(1+np.sin(2*np.pi*.11*tt))
    if AMB: out += wind
    for st in STEPS:                                                                     # pas sur le bois : choc sourd + craquement
        t0 = (st-1.0)*WALK_END/6.0
        if not 0 <= t0 < WALK_END+.1: continue
        m = int(.18*SR); u = np.arange(m)/SR; i = int(t0*SR)
        thump = np.sin(2*np.pi*95*u)*np.exp(-u*38)*.35+bp(rng.standard_normal(m), 300, 1400)*np.exp(-u*45)*.18
        creak = np.sin(2*np.pi*np.cumsum(420+90*np.sin(2*np.pi*7*u))/SR)*np.exp(-((u-.06)/.03)**2)*.03
        out[i:i+m] += (thump+creak)[:max(0, n-i)]
    for k, f0 in enumerate((55, 41.2, 49, 36.7) if AMB else ()):                                         # nappe grave épique qui monte, grosse caisse à la fin
        a, b = k*1.6, k*1.6+2.0; i, j = int(a*SR), min(n, int(b*SR)); u = np.arange(j-i)/SR
        out[i:j] += (np.sin(2*np.pi*f0*u)+.5*np.sin(2*np.pi*2*f0*u)+.25*np.sin(2*np.pi*3*f0*u))*np.sin(np.pi*u/2.0)*.08*(1+k*.25)
    for t0 in ((0.0, 5.8) if AMB else ()):
        m = int(.6*SR); u = np.arange(m)/SR; i = int(t0*SR)
        out[i:i+m] += (np.sin(2*np.pi*np.cumsum(70*np.exp(-u*5)+38)/SR)*np.exp(-u*5.5)*.6)[:max(0, n-i)]
    out = np.tanh(out*1.2); out *= .85/abs(out).max(); return SR, out
def main():
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/i_{ts}.png')
        return
    os.makedirs(f'{D}/out', exist_ok=True); tmp = f'{D}/out/_intro_v.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    from scipy.io import wavfile
    SR, a = sound(); wavfile.write(f'{D}/out/_intro.wav', SR, (np.stack([a, a], 1)*32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', f'{D}/out/_intro.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', f'{D}/out/apercu_intro_ubisoft.mp4'], check=True)
    os.remove(tmp); os.remove(f'{D}/out/_intro.wav'); print('ok')
if __name__ == '__main__': main()
