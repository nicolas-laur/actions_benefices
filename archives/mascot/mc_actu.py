"""Calque Mister Coin pour l'actu du 23 octobre : il présente tout du long et saute d'une place à l'autre selon la scène."""
import sys, math, functools
sys.path.insert(0, '/home/claude/mascot')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import puppet as P, rig
W, H = 1080, 1920
FEET = np.array([1000., 2080.])
# places : (x du centre de la pièce, y des pieds, zoom)
POS = {'bas': (540, 1655, .40), 'gauche': (305, 1100, .30), 'cta': (540, 1665, .27)}
def build(T):
    # grimace (inquiet) et joie (ravi) seulement pendant les silences de la voix ; quand il parle d'une mauvaise nouvelle : sourcils inquiets + bouche qui parle
    actions = [(3.55, 5.33, 'souci'), (5.36, 5.8, 'inquiet'), (7.9, 8.62, 'souci'), (9.9, 10.9, 'thumb'),
               (11.7, 12.7, 'point'), (14.6, 17.64, 'souci'), (17.67, 18.2, 'inquiet'), (18.22, 20.6, 'souci'), (20.64, 21.2, 'inquiet'),
               (21.6, 22.6, 'point'), (25.55, 27.65, 'souci'), (27.68, 28.2, 'inquiet'), (28.3, 29.3, 'point'),
               (31.7, 32.7, 'point'), (34.9, 35.9, 'thumb'), (36.39, 36.8, 'ravi'), (38.26, 38.66, 'ravi'), (40.35, 41.7, 'ravi')]
    return dict(
        pup=P.Puppet('/home/claude/actu/voice_full.wav', actions),
        moves=[(T['nf']-.05, .55, 'bas', 'gauche'), (T['toi']-.05, .55, 'gauche', 'cta')],
        walk=(0.0, 1.3, 1350),                         # entrée : il arrive de la droite
        hops=[T['rassure'], T['mt'], T['mt_26'], T['achete']],
        waves=[(.2, 3.3), (40.3, 41.6)])
CFG = None
def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)

def pose_seg(t):
    """(pose, pose précédente, temps depuis le début de la pose) ; hors actions : 'wave' (pose de base)"""
    acts = CFG['pup'].actions; start, prev, pose = 0., 'wave', 'wave'
    for a, b, p in acts:
        if t < a: break
        if t < b: return p, (prev if abs(a-start) < .06 else 'wave'), t-a
        prev, pose, start = p, 'wave', b
    return 'wave', prev if t-start < .2 else 'wave', t-start

def jumpcurve(d, dur, height):
    """saut continu : (hauteur, étirement). d = temps depuis le décollage. Anticipation 0,15 s avant, réception amortie 0,3 s après."""
    if d < -.15 or d >= dur+.3: return 0., 0.
    if d < 0: return 0., -.07*math.sin(math.pi/2*(d+.15)/.15)
    if d < dur:
        p = d/dur; h = height*math.sin(math.pi*p)
        s = -.07+.13*ease(p/.25) if p < .25 else .06*(1-ease((p-.25)/.5))
        return h, s
    u = (d-dur)/.3; return 0., -.07*math.sin(math.pi*u)*(1-u)

def place_at(t):
    pos = POS['bas']; jump = 0.; st = 0.
    for t0, d, a, b in CFG['moves']:
        if t >= t0+d: pos = POS[b]
        if t0-.15 <= t < t0+d+.3:
            h, st = jumpcurve(t-t0, d, 320); jump = h
            if t0 <= t < t0+d:
                e = ease((t-t0)/d); A, B = POS[a], POS[b]; pos = tuple(A[i]+(B[i]-A[i])*e for i in range(3))
    return pos, jump, st

def hop_at(t):
    for h in CFG['hops']:
        if h-.15 <= t < h+.8: return jumpcurve(t-h, .5, 190)
    return 0., 0.

@functools.lru_cache(maxsize=1)
def smooth_level():
    """énergie de la voix lissée dans les deux sens (≈ 0,3 s) : le corps suit la phrase, pas chaque syllabe"""
    lv = CFG['pup'].level.astype(float); a = 1-math.exp(-1/(.3*30)); o = lv.copy()
    for k in range(1, len(o)): o[k] = o[k-1]+a*(o[k]-o[k-1])
    for k in range(len(o)-2, -1, -1): o[k] = o[k+1]+a*(o[k]-o[k+1])
    return o
def lv_at(t):
    o = smooth_level(); return float(np.interp(t*30, np.arange(len(o)), o))
def fade(t, a, b, r=.25):
    """1 à l'intérieur de [a, b], 0 dehors, transitions douces de r secondes"""
    return ease((t-a)/r)*ease((b-t)/r)

def layer(t):
    """RGBA plein cadre : ombre + personnage"""
    pup = CFG['pup']; i = min(len(pup.mouth)-1, int(t*30)); lv = lv_at(t); TAU = 2*math.pi
    pose, prev, since = pose_seg(t)
    blink = any(0 <= t-b < .12 for b in pup.blinks) and pose != 'ravi'
    (cx, fy, z), jump, st1 = place_at(t)
    hy, st2 = hop_at(t); st = st1+st2
    w0, w1, wx0 = CFG['walk']
    wk = fade(t, w0-1, w1, .3)                                    # intensité de la marche
    wx = wx0*(1-ease((t-w0)/(w1-w0))) if t < w1 else 0
    # ---- au repos : respiration et balancement lents, un peu plus amples quand il parle
    legA = 3*math.sin(TAU*t/3.2); legB = -3*math.sin(TAU*t/3.2+.6)
    bob = 9*lv*(1-math.cos(TAU*t*1.35))/2
    rot = 1.8*math.sin(TAU*t/3.4)+1.6*lv*math.sin(TAU*t/1.5)
    # ---- marche (fondue avec le repos)
    ph = TAU*1.8*t
    legA += wk*20*math.sin(ph); legB -= wk*20*math.sin(ph); bob += wk*20*(1-math.cos(2*ph))/2; rot += wk*3*math.sin(ph)
    # ---- en l'air : jambes repliées progressivement
    air = min(1, (hy+jump)/120)
    legA = legA+(14-legA)*air; legB = legB+(-10-legB)*air
    # ---- bras : coucou lent fondu, pouce avec petit rebond amorti
    wv = max([fade(t, a, b) for a, b in CFG['waves']]+[0])
    armA = (1-wv)*(4*math.sin(TAU*t/2.9)+4*lv*math.sin(TAU*t/1.6))+wv*(-4+12*math.sin(TAU*1.7*t))
    if pose == 'thumb': armA = 8*math.exp(-since*5)*math.sin(since*12)
    # ---- changement d'expression : léger gonflement, pas de saut d'échelle
    swell = 1+.03*math.sin(math.pi*min(since, .35)/.35) if pose != 'wave' else 1
    breath = .01*math.sin(TAU*t/2.6)
    sx = swell*(1-.8*st)*(1-breath); sy = swell*(1+st)*(1+breath)
    m = int(pup.mouth[i])
    cv = rig.character(pose, m, blink, legA, legB, armA)
    k = ease(since/.14)                                           # fondu enchaîné direct depuis la pose précédente (0,14 s)
    if k < 1 and prev != pose: cv = Image.blend(rig.character(prev, m, blink, legA, legB, armA), cv, k)
    S = np.array([cx, fy], float); F = FEET.copy()
    off = np.array([wx, -hy-bob-jump/z])
    th = math.radians(rot); c, s_ = math.cos(th), math.sin(th)
    Rinv = np.array([[c, -s_], [s_, c]]); Dinv = np.diag([1/sx, 1/sy]); Mx = Dinv@Rinv/z
    b = FEET+Dinv@Rinv@(-S/z+F-off-FEET)
    char = cv.transform((W, H), Image.AFFINE, (Mx[0, 0], Mx[0, 1], b[0], Mx[1, 0], Mx[1, 1], b[1]), resample=Image.BICUBIC)
    out = Image.new('RGBA', (W, H), 0)
    # ombre douce sous les pieds, plus petite quand il saute
    k = 1/(1+(hy*z+jump)/120); fx = cx+z*wx; rw = 300*z*k
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((fx-rw, fy-24*z, fx+rw, fy+18*z), fill=int(160*k))
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(char)
    return out
