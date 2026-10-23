"""Test v2 : Mister Coin articulé + réalisation (plans large / moyen / gros plan, marche, sauts, coucou de la main).
usage : python3 film.py [t_debut t_fin] [sortie]"""
import sys, math, subprocess
sys.path.insert(0, '/home/claude/mascot')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import puppet as P, rig
A = '/home/claude/actu'; FPS = 30; W, H = 1080, 1920
T0 = float(sys.argv[1]) if len(sys.argv) > 2 else 0; T1 = float(sys.argv[2]) if len(sys.argv) > 2 else 41.6
OUT = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/mascot/test_mister_coin_v2.mp4'
FEET = np.array([1000., 2080.])

actions = [(3.5, 4.5, 'inquiet'), (7.9, 8.8, 'inquiet'), (11.1, 12.3, 'point'), (16.45, 17.5, 'inquiet'), (21.2, 22.4, 'point'),
           (25.55, 26.7, 'inquiet'), (31.25, 32.4, 'point'), (36.75, 38.2, 'thumb'), (39.25, 40.3, 'ravi')]
pup = P.Puppet(f'{A}/voice_full.wav', actions)
# cadrages : zoom (pixels écran par pixel du dessin), point du dessin visé, position à l'écran, suivi de la marche
SHOT = {'W': (.45, (1000, 1300), (540, 1250), 0), 'M': (.62, (930, 1050), (540, 1060), 1),
        'ML': (.58, (930, 1150), (470, 1130), 1), 'C': (1.1, (1000, 1000), (540, 900), 1)}
shots = [(0, 'W'), (3.5, 'C'), (5.75, 'M'), (7.9, 'C'), (8.8, 'ML'), (9.9, 'W'), (11.1, 'ML'), (14.6, 'C'), (16.45, 'M'),
         (17.85, 'W'), (21.2, 'ML'), (23.9, 'M'), (25.55, 'C'), (27.95, 'W'), (31.25, 'ML'), (34.9, 'C'), (36.75, 'M'),
         (38.6, 'C'), (40.3, 'W')]
walks = [(0, 1.5, 1500, 0), (17.85, 19.0, 0, 260), (27.95, 29.2, 260, 0)]
hops = [31.25, 36.75, 39.3]
waves = [(.2, 3.3), (40.3, 41.6)]

def ease(p): p = min(1, max(0, p)); return 1-(1-p)**3
def shot_at(t):
    cur = shots[0]
    for s in shots:
        if s[0] <= t: cur = s
    return cur
def walk_at(t):
    x, walking = 0, False
    for a, b, x0, x1 in walks:
        if t >= b: x = x1
        elif t >= a: x = x0+(x1-x0)*ease((t-a)/(b-a)) if x0 != 1500 else x0+(x1-x0)*(1-(1-(t-a)/(b-a))**1.6); walking = True; break
        else: break
    return x, walking
def hop_at(t):
    """hauteur du saut, écrasement (sx, sy)"""
    for h in hops:
        d = t-h
        if -.12 <= d < 0: k = -d/.12; return 0, 1+.07*(1-k), 1-.09*(1-k)          # anticipation : il se tasse
        if 0 <= d < .45: p = d/.45; return 230*4*p*(1-p), .95, 1.06                  # en l'air : étiré
        if .45 <= d < .8: k = math.exp(-(d-.45)*12)*math.cos((d-.45)*30); return 0, 1+.08*k, 1-.1*k  # réception
    return 0, 1, 1

def frame(t):
    i = min(len(pup.mouth)-1, int(t*FPS)); lv = float(pup.level[i])
    pose, since, _ = pup.pose_at(t)
    blink = any(0 <= t-b < .12 for b in pup.blinks) and pose != 'ravi'
    wx, walking = walk_at(t); hy, hsx, hsy = hop_at(t)
    # ---- articulations
    if walking:
        ph = 2*math.pi*2.2*t; legA, legB = 22*math.sin(ph), -22*math.sin(ph); bob = 40*abs(math.sin(ph)); rot = 4*math.sin(ph)
    else:
        legA = 2.5*math.sin(1.7*t)+5*lv*max(0, math.sin(4.3*t)); legB = -2*math.sin(1.7*t+1)-3*lv*max(0, math.sin(4.3*t+2))
        bob = 18*lv*abs(math.sin(5.6*t)); rot = 2.5*math.sin(1.25*t)+2.2*lv*math.sin(4.9*t)
    if hy > 0: legA, legB = 14, -10
    waving = any(a <= t < b for a, b in waves)
    if waving: armA = 16*math.sin(2*math.pi*2.4*t)-6
    elif pose == 'thumb': armA = 14*math.exp(-since*7)*math.cos(since*22)
    else: armA = 4*math.sin(1.1*t)+7*lv*math.sin(3.4*t)
    pop = 1+.07*math.exp(-since*12) if since < .6 else 1
    sx = hsx*pop*(1+.015*lv*math.sin(6*t)); sy = hsy*pop*(1-.015*lv*math.sin(6*t))
    cv = rig.character(pose, int(pup.mouth[i]), blink, legA, legB, armA)
    # ---- caméra
    st0, kind = shot_at(t); z, F, S, follow = SHOT[kind]; pt = t-st0
    z = z*(1+.035*min(pt, 3)/3)*(1-.05*math.exp(-pt*9))         # léger travelling avant + petit « punch » à la coupe
    hx = 5*math.sin(t*1.7)+3*math.sin(t*3.1); hyc = 4*math.sin(t*1.3+1)+2*math.sin(t*2.7)
    F = np.array(F, float)+[wx*follow, 0]; S = np.array(S, float)+[hx, hyc]
    off = np.array([wx, -hy-bob])
    th = math.radians(rot); c, s_ = math.cos(th), math.sin(th)
    Rinv = np.array([[c, -s_], [s_, c]])                        # inverse de la rotation PIL (sens écran)
    Dinv = np.diag([1/sx, 1/sy]); Mx = Dinv@Rinv/z
    b = FEET+Dinv@Rinv@(-S/z+F-off-FEET)
    char = cv.transform((W, H), Image.AFFINE, (Mx[0, 0], Mx[0, 1], b[0], Mx[1, 0], Mx[1, 1], b[1]), resample=Image.BICUBIC)
    # ---- décor : studio, flou selon le plan, zoom en parallaxe
    bgi = Image.open(f'{A}/bg30/{min(int(t*FPS), 1264):04d}.jpg').convert('RGB')
    bz = 1+.5*(z-.45); cw, ch = W/bz, H/bz; px = (F[0]-1000)*z*.25/bz
    bgi = bgi.crop((int((W-cw)/2+px), int((H-ch)/2), int((W+cw)/2+px), int((H+ch)/2))).resize((W, H), Image.BICUBIC)
    bgi = bgi.filter(ImageFilter.GaussianBlur(3+9*(z-.45)))
    bgi = ImageEnhance.Brightness(bgi).enhance(.62)
    bga = np.asarray(bgi).astype(np.float32)*[1.06, .96, .84]
    # halo chaud derrière le personnage
    cxs, cys = S+z*(np.array([1000, 1040])-F+off)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot(xx-cxs, yy-cys)/(700*max(z, .6))
    bga += (np.exp(-r**2)*55)[..., None]*[1, .72, .35]
    frame_im = Image.fromarray(np.clip(bga, 0, 255).astype(np.uint8)).convert('RGBA')
    # ombre au sol (ne monte pas avec le saut)
    fx, fy = S+z*(FEET-F+[wx, 0])
    sh = Image.new('L', (W, H), 0); k = 1/(1+hy/300); rw = 300*z*k
    ImageDraw.Draw(sh).ellipse((fx-rw, fy-28*z, fx+rw, fy+22*z), fill=int(150*k))
    frame_im.paste((10, 6, 2, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(18*z+4)))
    frame_im.alpha_composite(char)
    # ---- finition : vignette, grain
    out = np.asarray(frame_im.convert('RGB')).astype(np.float32)
    vig = 1-.38*np.clip(((xx-W/2)/(W*.75))**2+((yy-H/2)/(H*.7))**2, 0, 1)
    out *= vig[..., None]
    out += np.random.default_rng(int(t*FPS)).normal(0, 4.5, (H, W, 1))
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-ss', str(T0), '-t', str(T1-T0), '-i', f'{A}/amix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '15',
           '-preset', 'medium', '-pix_fmt', 'yuv420p', '-b:v', '16M', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT]
    if OUT.endswith('.png'):
        Image.fromarray(frame(T0)).save(OUT); sys.exit()
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(T0*FPS), int(T1*FPS)):
        ff.stdin.write(frame(f/FPS).tobytes())
        if f % 60 == 0: print(f, flush=True)
    ff.stdin.close(); ff.wait(); print('ok')
