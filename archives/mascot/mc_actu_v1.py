"""Calque Mister Coin pour l'actu du 23 octobre : il présente tout du long et saute d'une place à l'autre selon la scène."""
import sys, math, functools
sys.path.insert(0, '/home/claude/mascot')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import puppet as P, rig
W, H = 1080, 1920
FEET = np.array([1000., 2080.])
# places : (x du centre de la pièce, y des pieds, zoom)
POS = {'bas': (540, 1655, .40), 'gauche': (235, 1100, .34), 'cta': (540, 1665, .27)}
def build(T):
    actions = [(3.5, 4.6, 'inquiet'), (7.9, 8.7, 'inquiet'), (9.9, 10.9, 'thumb'),
               (11.7, 12.7, 'point'), (14.6, 15.4, 'inquiet'), (16.45, 17.3, 'inquiet'), (17.85, 18.9, 'inquiet'),
               (21.6, 22.6, 'point'), (25.55, 26.6, 'inquiet'), (27.95, 28.9, 'point'),
               (31.7, 32.7, 'point'), (34.9, 35.9, 'thumb'), (36.75, 37.7, 'ravi'),
               (39.3, 40.3, 'ravi')]
    return dict(
        pup=P.Puppet('/home/claude/actu/voice_full.wav', actions),
        moves=[(T['nf']-.05, .55, 'bas', 'gauche'), (T['toi']-.05, .55, 'gauche', 'cta')],
        walk=(0.0, 1.3, 1350),                         # entrée : il arrive de la droite
        hops=[T['rassure'], T['mt'], T['mt_26'], T['achete']],
        waves=[(.2, 3.3), (40.3, 41.6)])
CFG = None
def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)

def place_at(t):
    m = CFG['moves']; pos = POS['bas']; jump = 0; air = None
    for t0, d, a, b in m:
        if t >= t0+d: pos = POS[b]
        elif t >= t0:
            p = (t-t0)/d; e = ease(p); A, B = POS[a], POS[b]
            pos = tuple(A[i]+(B[i]-A[i])*e for i in range(3)); jump = 300*4*p*(1-p); air = p
            break
        else: break
    return pos, jump, air

def hop_at(t):
    for h in CFG['hops']:
        d = t-h
        if -.1 <= d < 0: k = -d/.1; return 0, 1+.07*(1-k), 1-.09*(1-k)
        if 0 <= d < .42: p = d/.42; return 220*4*p*(1-p), .95, 1.06
        if .42 <= d < .75: k = math.exp(-(d-.42)*12)*math.cos((d-.42)*30); return 0, 1+.08*k, 1-.1*k
    return 0, 1, 1

def layer(t):
    """RGBA plein cadre : ombre + personnage"""
    pup = CFG['pup']; i = min(len(pup.mouth)-1, int(t*30)); lv = float(pup.level[i])
    pose, since, _ = pup.pose_at(t)
    blink = any(0 <= t-b < .12 for b in pup.blinks) and pose != 'ravi'
    (cx, fy, z), jump, air = place_at(t)
    hy, hsx, hsy = hop_at(t)
    w0, w1, wx0 = CFG['walk']; walking = w0 <= t < w1
    wx = wx0*(1-(min(1, max(0, (t-w0)/(w1-w0))))**1) if t < w1 else 0
    wx = wx0*(1-(t-w0)/(w1-w0))**1.3 if walking else 0
    if air is not None:                                 # pendant le grand saut : jambes repliées, étirement
        hsx, hsy = .94, 1.07
        if air > .85: k = (air-.85)/.15; hsx, hsy = 1+.06*k, 1-.08*k
    if walking:
        ph = 2*math.pi*2.3*t; legA, legB = 22*math.sin(ph), -22*math.sin(ph); bob = 40*abs(math.sin(ph)); rot = 4*math.sin(ph)
    else:
        legA = 2.5*math.sin(1.7*t)+5*lv*max(0, math.sin(4.3*t)); legB = -2*math.sin(1.7*t+1)-3*lv*max(0, math.sin(4.3*t+2))
        bob = 18*lv*abs(math.sin(5.6*t)); rot = 2.5*math.sin(1.25*t)+2.2*lv*math.sin(4.9*t)
    if hy > 0 or jump > 0: legA, legB = 14, -10
    if any(a <= t < b for a, b in CFG['waves']): armA = 16*math.sin(2*math.pi*2.4*t)-6
    elif pose == 'thumb': armA = 14*math.exp(-since*7)*math.cos(since*22)
    else: armA = 4*math.sin(1.1*t)+7*lv*math.sin(3.4*t)
    pop = 1+.07*math.exp(-since*12) if since < .6 else 1
    sx = hsx*pop*(1+.015*lv*math.sin(6*t)); sy = hsy*pop*(1-.015*lv*math.sin(6*t))
    cv = rig.character(pose, int(pup.mouth[i]), blink, legA, legB, armA)
    S = np.array([cx, fy], float); F = FEET.copy()
    off = np.array([wx, -hy-bob-jump/z])
    th = math.radians(rot); c, s_ = math.cos(th), math.sin(th)
    Rinv = np.array([[c, -s_], [s_, c]]); Dinv = np.diag([1/sx, 1/sy]); Mx = Dinv@Rinv/z
    b = FEET+Dinv@Rinv@(-S/z+F-off-FEET)
    char = cv.transform((W, H), Image.AFFINE, (Mx[0, 0], Mx[0, 1], b[0], Mx[1, 0], Mx[1, 1], b[1]), resample=Image.BICUBIC)
    out = Image.new('RGBA', (W, H), 0)
    # ombre douce sous les pieds (posée sur la carte ou le sol), plus petite quand il saute
    k = 1/(1+(hy*z+jump)/120); fx = cx+z*wx; rw = 300*z*k
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((fx-rw, fy-24*z, fx+rw, fy+18*z), fill=int(160*k))
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(char)
    return out
