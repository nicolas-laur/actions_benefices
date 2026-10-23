"""Mister Coin v2 : marionnette articulée (« cutout ») + réalisation dynamique.
Le dessin est découpé en couches : jambe gauche, jambe droite, bras qui salue, corps (pièce + chapeau + bras sur la hanche).
Chaque couche tourne autour de son articulation, cachée derrière la pièce : les raccords ne se voient pas.
Les visages (bouches, clignements, expressions) viennent toujours des images Gemini (puppet.compose)."""
import math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import puppet as P
P.S = 1.0                                                  # pleine résolution (gros plans nets)
CX, CY, RX, RY = 1000, 1040, 525, 535                      # ellipse de la pièce (image d'origine 1792×2400)
HIP_L, HIP_R, SHOULDER = (848, 1555), (1061, 1585), (520, 1200)
W0, H0 = 1792, 2400

def _masks():
    yy, xx = np.mgrid[0:H0, 0:W0]
    inside = ((xx-CX)/RX)**2+((yy-CY)/RY)**2 < 1
    out = ~inside
    arm = out & (xx < CX-200) & (yy > 600) & (yy < 1320)
    rhand = (xx > 1270) & (yy < 1700)
    legs = out & (yy > 1500) & ~rhand
    # séparation des deux jambes : droite passant par (936,1580) et (1096,2080)
    side = (xx-936)-(yy-1580)*(160/500)
    legL, legR = legs & (side < 0), legs & (side >= 0)
    def im(m): return Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
    return im(arm), im(legL), im(legR)
M_ARM, M_LEGL, M_LEGR = _masks()

def cut(img, mask):
    """découpe + ne garde que les gros morceaux (évite les filets de contour de la pièce qui partiraient avec le bras)"""
    from scipy import ndimage
    a = np.minimum(np.asarray(img.getchannel('A')), np.asarray(mask))
    lab, n = ndimage.label(a > 60)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1)); keep = np.isin(lab, 1+np.nonzero(sizes > sizes.max()*.15)[0])
        keep = ndimage.binary_dilation(keep, iterations=2); a = np.where(keep, a, 0).astype(np.uint8)
    o = img.copy(); o.putalpha(Image.fromarray(a)); return o
def minus(img, *masks):
    a = np.asarray(img.getchannel('A')).astype(np.int32)
    for m in masks: a = a*(255-np.asarray(m).astype(np.int32))//255
    o = img.copy(); o.putalpha(Image.fromarray(a.astype(np.uint8))); return o

@functools.lru_cache(maxsize=4)
def legs():
    base = P.keyed('bouche_ouverte')
    out = []
    for m in (M_LEGL, M_LEGR):
        l = cut(base, m); bb = l.getbbox(); out.append((l.crop(bb), bb))
    return out

@functools.lru_cache(maxsize=12)
def layers(pose, mouth, blink):
    """renvoie (corps, bras ou None) en pleine résolution"""
    full = P.compose(pose, mouth, blink)
    if pose == 'point':                                     # le bras croise la pièce : il reste dans le corps
        return minus(full, M_LEGL, M_LEGR), None
    src = P.keyed({'thumb': 'thumb'}.get(pose, 'bouche_ouverte'))
    arm = cut(src, M_ARM); bb = arm.getbbox()
    return minus(full, M_LEGL, M_LEGR, M_ARM), (arm.crop(bb), bb)

def rot_piece(canvas, piece, bb, pivot, ang):
    """colle une couche découpée sur la toile après rotation autour de son articulation"""
    im, (x0, y0, _, _) = piece, bb
    px, py = pivot[0]-x0, pivot[1]-y0
    pad = int(max(im.size)*.6)
    big = Image.new('RGBA', (im.width+2*pad, im.height+2*pad), 0); big.paste(im, (pad, pad))
    big = big.rotate(ang, resample=Image.BICUBIC, center=(px+pad, py+pad))
    canvas.alpha_composite(big, (x0-pad, y0-pad)) if x0-pad >= 0 and y0-pad >= 0 else canvas.paste(big, (x0-pad, y0-pad), big)

def character(pose, mouth, blink, legA, legB, armA):
    """toile pleine résolution du personnage articulé"""
    cv = Image.new('RGBA', (W0, H0+200), 0)
    (lL, bL), (lR, bR) = legs()
    rot_piece(cv, lL, bL, HIP_L, legA)
    rot_piece(cv, lR, bR, HIP_R, legB)
    body, arm = layers(pose, mouth, blink)
    if arm is not None: rot_piece(cv, arm[0], arm[1], SHOULDER, armA)
    cv.alpha_composite(body)
    return cv
