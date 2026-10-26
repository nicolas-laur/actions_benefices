"""Mister Coin v2 : bras et jambes « en caoutchouc » tracés en code (style années 1930), gants et chaussures en sprites.
La pièce seule (src2/corps.jpg) + 5 gants + 1 chaussure suffisent pour n'importe quelle pose, une vraie marche et des gestes fluides.

Repère : toile de 1792 × 3000 px, la même que rig.character (les pieds au sol à FEET = (1000, 2680)), pièce de même taille que les poses v1.
Une pose est un dict :
    corps : (dx, dy, inclinaison en degrés)        décalage de la pièce par rapport à sa place de repos
    bouche : None (sourire d'origine) ou 0..3     bouches animées de la v1 greffées
    cligne : bool
    bras : {'G': (x, y, gant, angle|None, courbure), 'D': …}   position du poignet dans la toile ; gant parmi GANTS ;
           angle du gant en degrés (None : dans l'axe de l'avant-bras) ; courbure du coude (-1..1)
    jambes : {'G': (x, y, angle, sens), 'D': …}   position de la cheville ; angle de la chaussure ; sens +1 pointe à droite, -1 à gauche
"""
import os, math, functools
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S2 = f'{D}/src2'
W0, H0 = 1792, 3000
COIN_C = np.array([965., 1646.])            # centre de la face de la pièce au repos (même place que les poses v1 + marge haute)
FEET_Y = 2680.
LEG_FILL, LEG_LINE, LEG_HI = (248/255, 169/255, 34/255), (56/255, 16/255, 12/255), (251/255, 214/255, 140/255)
LIMB_W, LINE_W = 54, 16

def _key(path):
    """détourage du fond vert (même méthode que le kit v1) et recadrage sur l'élément"""
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = 1-np.clip((ks-25)/70, 0, 1)
    from scipy import ndimage
    lab, n = ndimage.label(al > .5); sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1))
    al = al*ndimage.binary_dilation(lab == 1+np.argmax(sizes), iterations=3)
    a[..., 1] = np.where(ks > 0, np.maximum(R, B), G)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    im.putalpha(Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8)))
    return im

@functools.lru_cache(maxsize=1)
def body():
    """pièce seule mise à l'échelle des poses v1 ; renvoie (image, position du coin haut-gauche dans la toile, repères)"""
    im = _key(f'{S2}/corps.jpg'); sc = 837/280                     # face dorée : 280 px dans le dessin Gemini, 837 dans le kit
    cx, cy = 517, 331                                               # centre de la face dans le dessin
    im = im.resize((int(im.width*sc), int(im.height*sc)), Image.LANCZOS)
    off = (COIN_C[0]-cx*sc, COIN_C[1]-cy*sc)
    P = lambda x, y: (off[0]+x*sc, off[1]+y*sc)
    marks = dict(epaule_G=P(392, 345), epaule_D=P(690, 330), hanche_G=P(470, 492), hanche_D=P(590, 486),
                 bouche=P(517, 389), oeil_G=P(463, 290), oeil_D=P(553, 290), sc=sc)
    return im, off, marks

@functools.lru_cache(maxsize=8)
def body_with_mouth(mouth):
    """bouche d'origine (sourire) ou bouche animée de la v1 greffée à sa place"""
    im, off, mk = body()
    if mouth is None: return im
    import cv2, puppet as P
    a = np.asarray(im.convert('RGB')).copy(); m = np.zeros(a.shape[:2], np.uint8)
    bx, by = mk['bouche'][0]-off[0], mk['bouche'][1]-off[1]; sc = mk['sc']
    cv2.ellipse(m, (int(bx), int(by)), (int(76*sc), int(31*sc)), 0, 0, 360, 255, -1)
    a2 = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
    out = Image.fromarray(a2).convert('RGBA'); out.putalpha(im.getchannel('A'))
    mo = P.keyed(['bouche_fermee', 'bouche_mi', 'bouche_ouverte', 'bouche_o'][mouth]).crop((760, 1110, 1040, 1330))
    k = 1.0; mo = mo.resize((int(mo.width*k), int(mo.height*k)), Image.LANCZOS)
    mk_ = Image.new('L', mo.size, 0); ImageDraw.Draw(mk_).ellipse((mo.width*.08, mo.height*.08, mo.width*.92, mo.height*.92), fill=255)
    out.paste(mo, (int(bx-mo.width/2), int(by-mo.height/2+8)), mk_.filter(ImageFilter.GaussianBlur(8)))
    return out

GANTS = ('ouvert', 'poing', 'index', 'pouce', 'tenir')
@functools.lru_cache(maxsize=8)
def glove(kind):
    """gant détouré, poignet (milieu du revers) placé en bas au centre ; renvoie (image, point du poignet)"""
    im = _key(f'{S2}/gant_{kind}.jpg')
    if kind == 'tenir':                                              # on retire la petite pièce tenue pour garder une main vide en C
        a = np.asarray(im).copy(); R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
        gold = (R > 150) & (B < 120) & (R-B > 60)
        from scipy import ndimage
        gold = ndimage.binary_dilation(gold, iterations=4); a[..., 3][gold] = 0; im = Image.fromarray(a)
    bb = im.getbbox(); im = im.crop(bb)
    target_h = {'ouvert': 370, 'poing': 310, 'index': 370, 'pouce': 280, 'tenir': 320}[kind]
    k = target_h/im.height; im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    al = np.asarray(im.getchannel('A')); rows = np.where(al[-12:].max(0) > 128)[0]
    wx = (rows.min()+rows.max())/2 if len(rows) else im.width/2
    return im, (wx, im.height-6)

@functools.lru_cache(maxsize=1)
def shoe():
    """chaussure de profil (pointe à droite) ; renvoie (image, cheville)"""
    im = _key(f'{S2}/chaussure.jpg'); bb = im.getbbox(); im = im.crop(bb)
    k = 345/im.width; im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    return im, ((364.7-bb[0])*k, (262-bb[1])*k)

def _paste_rot(cv, im, anchor, pos, ang):
    """colle im sur cv en faisant coïncider anchor (dans im) avec pos (dans cv), après rotation de ang degrés autour de anchor"""
    pad = int(max(im.size)); big = Image.new('RGBA', (im.width+2*pad, im.height+2*pad), 0); big.paste(im, (pad, pad))
    ax, ay = anchor[0]+pad, anchor[1]+pad
    big = big.rotate(ang, resample=Image.BICUBIC, center=(ax, ay))
    cv.alpha_composite(big, (int(round(pos[0]-ax)), int(round(pos[1]-ay)))) if pos[0]-ax >= 0 and pos[1]-ay >= 0 else cv.paste(big, (int(round(pos[0]-ax)), int(round(pos[1]-ay))), big)

def _tube(c, p0, p1, bend):
    """membre en caoutchouc : courbe de Bézier de p0 à p1, coude/genou déporté perpendiculairement de bend × longueur"""
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1-p0; L = np.linalg.norm(v)+1e-6; n = np.array([-v[1], v[0]])/L
    c1 = p0+v*.33+n*bend*L*.35; c2 = p0+v*.66+n*bend*L*.35
    for w, colr in ((LIMB_W+2*LINE_W, LEG_LINE), (LIMB_W, LEG_FILL)):
        c.move_to(*p0); c.curve_to(*c1, *c2, *p1); c.set_line_width(w); c.set_source_rgb(*colr); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    off = n*LIMB_W*.22                                                # reflet clair sur un côté
    c.move_to(*(p0+off)); c.curve_to(*(c1+off), *(c2+off), *(p1+off)); c.set_line_width(LIMB_W*.22); c.set_source_rgba(*LEG_HI, .9); c.stroke()
    t = .97; q = (1-t)**3*p0+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*p1    # direction en bout de membre
    d = p1-q; return math.degrees(math.atan2(d[0], -d[1]))            # angle pour orienter le gant (0 = vers le haut)

def _surf():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W0, H0); return s, cairo.Context(s)
def _img(s):
    s.flush(); return Image.frombuffer('RGBA', (W0, H0), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()

REST = {'corps': (0, 0, 0), 'bouche': None, 'cligne': False,
        'bras': {'G': (430, 2010, 'ouvert', None, .45), 'D': (1520, 1990, 'ouvert', None, -.45)},
        'jambes': {'G': (870, 2560, 0, -1), 'D': (1100, 2560, 0, 1)}}

def draw(pose):
    """assemble Mister Coin pour une pose ; renvoie une toile RGBA 1792 × 3000"""
    p = dict(REST); p.update(pose)
    im, off, mk = body(); dx, dy, tilt = p['corps']
    piv = COIN_C+np.array([dx, dy])
    def T(pt):                                                       # repère du corps (pièce inclinée et décalée)
        v = np.array(pt)-COIN_C; a = math.radians(-tilt); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        return piv+R@v
    cv = Image.new('RGBA', (W0, H0), 0)
    # jambes (derrière la pièce) puis chaussures
    s, c = _surf()
    for side in ('G', 'D'):
        ax, ay, ang, sens = p['jambes'][side]; _tube(c, T(mk['hanche_'+side]), (ax, ay-10), .12*(-1 if side == 'G' else 1))
    cv.alpha_composite(_img(s))
    sh, sa = shoe()
    for side in ('G', 'D'):
        ax, ay, ang, sens = p['jambes'][side]; img, anc = (sh, sa) if sens > 0 else (sh.transpose(Image.FLIP_LEFT_RIGHT), (sh.width-sa[0], sa[1]))
        _paste_rot(cv, img, anc, (ax, ay), ang*sens)
    # bras (derrière la pièce)
    s, c = _surf(); hands = []
    for side in ('G', 'D'):
        hx, hy, kind, gang, bend = p['bras'][side]
        a = _tube(c, T(mk['epaule_'+side]), (hx, hy), bend)
        hands.append((kind, (hx, hy), a if gang is None else gang, side))
    cv.alpha_composite(_img(s))
    # pièce
    b = body_with_mouth(p['bouche'])
    if p['cligne']:
        b = b.copy(); d = ImageDraw.Draw(b)
        for e in ('oeil_G', 'oeil_D'):
            ex, ey = mk[e][0]-off[0], mk[e][1]-off[1]; r = 32*mk['sc']/2.99*3
            d.ellipse((ex-r*.75, ey-r, ex+r*.75, ey+r*.9), fill=(246, 178, 52, 255))
            d.arc((ex-r*.75, ey-r*.2, ex+r*.75, ey+r*.9), 20, 160, fill=(56, 16, 12, 255), width=10)
    bt = b.rotate(tilt, resample=Image.BICUBIC, center=(COIN_C[0]-off[0], COIN_C[1]-off[1]), expand=False)
    cv.alpha_composite(bt, (int(off[0]+dx), int(off[1]+dy))) if off[0]+dx >= 0 and off[1]+dy >= 0 else cv.paste(bt, (int(off[0]+dx), int(off[1]+dy)), bt)
    # gants (devant)
    for kind, pos, ang, side in hands:
        g, wa = glove(kind)
        if side == 'G' and kind in ('pouce', 'tenir', 'index'): g, wa = g.transpose(Image.FLIP_LEFT_RIGHT), (g.width-wa[0], wa[1])
        _paste_rot(cv, g, wa, pos, -ang)
    return cv
