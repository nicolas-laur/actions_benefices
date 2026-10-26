"""Mister Coin v2 : dessin du personnage articulé (bras et jambes « en caoutchouc » tracés en code, gants et chaussures en sprites,
visage animé en code : sourcils, paupières, bouche continue).

Repère « kit » : toile de 1792 × 3000 px (la même que rig.character), pieds au sol vers y = FEET_Y, pièce de la même taille que les poses v1.
Le dessin est fait à RES × cette taille (suréchantillonnage ×2 environ pour un affichage à zoom .28) ; les coordonnées des poses restent
exprimées dans le repère kit.

Pose (dict, toutes les clés facultatives) :
    corps   : (dx, dy, inclinaison°)              décalage de la pièce par rapport à son repos (inclinaison horaire > 0)
    visage  : dict sourcil (−1 bas … 1 haut), froncé (−1 inquiet … 1 fâché), paupiere (0 ouvert … 1 fermé),
              plisse (0 … 1, yeux rieurs), bouche (0 fermée … 1 grande ouverte), large (.7 … 1.3), sourire (−1 moue … 1 sourire)
    bras    : {'G': (x, y, gant, angle|None, courbure), 'D': …}  poignet dans le repère kit ; gant ∈ GANTS ;
              angle du gant en degrés (None : dans l'axe de l'avant-bras) ; courbure du coude (−1 … 1)
    jambes  : {'G': (x, y, angle°), 'D': …}         cheville dans le repère kit ; angle de la chaussure (pointe relevée > 0)
    objet   : (image RGBA, côté 'G'|'D', échelle)  objet tenu dans la main (gant 'tenir')
"""
import os, math, functools
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S2 = f'{D}/src2'
W0, H0 = 1792, 3000
RES = .55
COIN_C = np.array([965., 1646.])            # centre de la face de la pièce au repos (repère kit)
FEET_Y = 2680.
LINE = (56/255, 16/255, 12/255); FILL = (248/255, 169/255, 34/255); HI = (251/255, 214/255, 140/255)
LIMB_W, LINE_W = 54, 16

def _key(path):
    """détourage du fond vert (même méthode que le kit v1)"""
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

# ---------- la pièce ----------
SC = 837/280                                   # face dorée : 280 px dans le dessin Gemini, 837 dans le kit
FACE_CX, FACE_CY = 517, 331                    # centre de la face dans le dessin Gemini
# repères relevés sur l'image de la pièce mise à l'échelle SC
BROW_L = ((1325, 702), (1380, 662), (1445, 664)); BROW_R = ((1668, 690), (1725, 680), (1790, 752))
EYE_L = (1300, 722, 1462, 1022); EYE_R = (1578, 748, 1752, 1048)
MOUTH = (1515, 1160)
ERASE_BOX = [(1295, 625, 1475, 728), (1645, 640, 1815, 785), (1310, 1090, 1730, 1265)]

@functools.lru_cache(maxsize=1)
def _body_full():
    """pièce pleine résolution, bouche et sourcils d'origine effacés ; masques des yeux ; couleur de la pièce"""
    import cv2
    from scipy import ndimage
    im = _key(f'{S2}/corps.jpg'); im = im.resize((int(im.width*SC), int(im.height*SC)), Image.LANCZOS)
    a = np.asarray(im.convert('RGB')).copy(); m = np.zeros(a.shape[:2], np.uint8)
    R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    dark = (R < 150) & (G < 100)                                      # traits sombres (sourcils, bouche) dans leurs zones
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for (x0, y0, x1, y1) in ERASE_BOX:
        zone = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        for (ex0, ey0, ex1, ey1) in (EYE_L, EYE_R): zone &= ~((xx >= ex0-8) & (xx < ex1+8) & (yy >= ey0-4) & (yy < ey1))
        m[dark & zone] = 255
    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    a2 = cv2.inpaint(a, m, 15, cv2.INPAINT_TELEA)
    soft = cv2.GaussianBlur(a2, (0, 0), 9); mm = cv2.GaussianBlur(m.astype(np.float32)/255, (0, 0), 5)[..., None]
    a2 = (a2*(1-mm*.8)+soft*mm*.8).astype(np.uint8)          # lisse la zone effacée (pas de traînées)
    out = Image.fromarray(a2).convert('RGBA'); out.putalpha(im.getchannel('A'))
    masks = []
    for (x0, y0, x1, y1) in (EYE_L, EYE_R):
        sub = a[y0:y1, x0:x1].astype(int); R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
        gold = (R > 200) & (G > 130) & (B < 120) & (R-B > 90)
        inner = ndimage.binary_fill_holes(~gold); lab, n = ndimage.label(inner)
        if n: inner = lab == 1+np.argmax(ndimage.sum(inner, lab, range(1, n+1)))
        full = np.zeros(a.shape[:2], bool); full[y0:y1, x0:x1] = ndimage.binary_dilation(inner, iterations=9); masks.append(full)
    golds = []
    for (x0, y0, x1, y1) in (EYE_L, EYE_R):
        sub = a2[y0+60:y1-60, max(0, x0-70):x0-25].reshape(-1, 3).astype(float); sub2 = a2[y0+60:y1-60, x1+25:x1+70].reshape(-1, 3).astype(float)
        golds.append(tuple(np.median(np.vstack([sub, sub2]), 0)/255))
    return out, masks, golds

@functools.lru_cache(maxsize=1)
def body():
    """(image de la pièce à RES, position haut-gauche dans le repère kit, repères en coordonnées kit)"""
    im, masks, gold = _body_full()
    off = (COIN_C[0]-FACE_CX*SC, COIN_C[1]-FACE_CY*SC)
    small = im.resize((int(im.width*RES), int(im.height*RES)), Image.LANCZOS)
    P = lambda x, y: (off[0]+x*SC, off[1]+y*SC)
    marks = dict(epaule_G=P(392, 345), epaule_D=P(690, 330), hanche_G=P(470, 492), hanche_D=P(590, 486),
                 bouche=(off[0]+MOUTH[0], off[1]+MOUTH[1]), chapeau=P(600, 70))
    return small, off, marks

@functools.lru_cache(maxsize=1)
def _eyeless_small():
    """la pièce sans les yeux (texture de paupière qui se fond dans la pièce), à RES"""
    import cv2
    im, masks, gold = _body_full(); a = np.asarray(im.convert('RGB')).copy()
    m = (np.maximum(masks[0], masks[1])*255).astype(np.uint8); m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    x0, y0, x1, y1 = FACE_BOX; sub = cv2.inpaint(a[y0:y1, x0:x1], m[y0:y1, x0:x1], 25, cv2.INPAINT_TELEA)
    sub = cv2.GaussianBlur(sub, (0, 0), 4)
    img = Image.fromarray(sub).resize((int((x1-x0)*RES), int((y1-y0)*RES)), Image.LANCZOS)
    return np.asarray(img).astype(np.float32)
@functools.lru_cache(maxsize=1)
def _eye_masks_small():
    im, masks, gold = _body_full(); out = []
    for m in masks:
        mi = Image.fromarray((m*255).astype(np.uint8)).resize((int(im.width*RES), int(im.height*RES)), Image.BILINEAR)
        out.append(np.asarray(mi).astype(np.float32)/255)
    return out, gold

FACE_BOX = (1220, 560, 1860, 1330)               # zone du visage dans l'image de la pièce (pleine résolution)
def face_layer(v):
    """sourcils, paupières et bouche dans la boîte du visage (à RES) ; renvoie (image RGBA, coin haut-gauche à RES)"""
    x0, y0, x1, y1 = FACE_BOX; w, h = int((x1-x0)*RES), int((y1-y0)*RES)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.scale(RES, RES); c.translate(-x0, -y0)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    brow, frown = v.get('sourcil', 0.), v.get('froncé', 0.)
    lid, squint = v.get('paupiere', 0.), v.get('plisse', 0.)
    mo, wide, smile = v.get('bouche', 0.), v.get('large', 1.), v.get('sourire', .6)
    masks, gold = _eye_masks_small()
    if lid > .02 or squint > .02:                     # paupières : la couleur de la pièce recouvre l'œil, bord sombre
        lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); k = cairo.Context(lay); k.scale(RES, RES); k.translate(-x0, -y0)
        k.set_line_cap(cairo.LINE_CAP_ROUND)
        for si, (side, (ex0, ey0, ex1, ey1)) in enumerate((('G', EYE_L), ('D', EYE_R))):
            cx = (ex0+ex1)/2; hh = ey1-ey0; tl = -frown*(1 if side == "G" else -1)*.16*hh   # paupière inclinée selon l'humeur
            yl = ey0+lid*hh*1.04
            if lid > .02:
                k.move_to(ex0-40, ey0-80); k.line_to(ex1+40, ey0-80); k.line_to(ex1+40, yl-tl)
                k.curve_to(cx+30, yl+hh*.10-tl*.5, cx-30, yl+hh*.10+tl*.5, ex0-40, yl+tl); k.close_path()
            if squint > .02:                          # yeux rieurs : la joue remonte par le bas
                yb = ey1-squint*hh*.55
                k.move_to(ex0-40, ey1+80); k.line_to(ex1+40, ey1+80); k.line_to(ex1+40, yb)
                k.curve_to(cx+30, yb-hh*.14, cx-30, yb-hh*.14, ex0-40, yb); k.close_path()
            k.set_source_rgb(1, 1, 1); k.fill()
        lay.flush(); arr = np.ndarray((h, lay.get_stride()//4, 4), np.uint8, lay.get_data())[:, :w].astype(np.float32)
        ox, oy = int(x0*RES), int(y0*RES); mk = np.maximum(masks[0], masks[1])[oy:oy+h, ox:ox+w]
        mk = np.pad(mk, ((0, max(0, h-mk.shape[0])), (0, max(0, w-mk.shape[1]))))[:h, :w]
        al = arr[..., 3]/255*mk; tex = _eyeless_small()[:h, :w]
        rgba = np.dstack([tex[..., 2]*al, tex[..., 1]*al, tex[..., 0]*al, al*255]).astype(np.uint8)      # BGRA prémultiplié
        mimg = cairo.ImageSurface.create_for_data(bytearray(np.ascontiguousarray(rgba).tobytes()), cairo.FORMAT_ARGB32, w, h, w*4)
        c.save(); c.identity_matrix(); c.set_source_surface(mimg, 0, 0); c.paint(); c.restore()
        c.set_line_width(20); c.set_source_rgb(*LINE)
        for side, (ex0, ey0, ex1, ey1) in (('G', EYE_L), ('D', EYE_R)):
            cx = (ex0+ex1)/2; hh = ey1-ey0; tl = -frown*(1 if side == "G" else -1)*.16*hh; yl = min(ey0+lid*hh*1.04, ey1-hh*.06)
            ins = .5*hh*math.sqrt(max(0, 1-((yl-(ey0+ey1)/2)/(hh/2))**2))/(hh/2)*(ex1-ex0)/2      # demi-largeur de l'œil à cette hauteur
            if lid > .02: c.move_to(cx-ins-4, yl+tl); c.curve_to(cx-30, yl+hh*.06+tl*.5, cx+30, yl+hh*.06-tl*.5, cx+ins+4, yl-tl); c.stroke()
            if squint > .02:
                yb = ey1-squint*hh*.55; ins = math.sqrt(max(0, 1-((yb-(ey0+ey1)/2)/(hh/2))**2))*(ex1-ex0)/2
                c.move_to(cx-ins-4, yb); c.curve_to(cx-30, yb-hh*.14, cx+30, yb-hh*.14, cx+ins+4, yb); c.stroke()
    for side, pts in (('G', BROW_L), ('D', BROW_R)):  # sourcils : montent, descendent, s'inclinent (intérieur relevé = inquiet)
        inner = pts[2] if side == 'G' else pts[0]; dy = -brow*42-squint*16
        def P(x, y):
            t_in = 1-min(1, math.dist((x, y), inner)/150)
            return x, y+dy+frown*48*t_in
        p0, p1, p2 = P(*pts[0]), P(*pts[1]), P(*pts[2])
        c.move_to(*p0); c.curve_to(p0[0]*.3+p1[0]*.7, p1[1]-10, p2[0]*.3+p1[0]*.7, p1[1]-10, *p2)
        c.set_line_width(30); c.set_source_rgb(*LINE); c.stroke()
    mx, my = MOUTH; hw = 168*wide*(1-.22*mo); up = smile*42; sag = smile*58; op = mo*150      # bouche continue
    Lp, Rp = (mx-hw, my-up), (mx+hw, my-up*.85)
    def upper(): c.move_to(*Lp); c.curve_to(mx-hw*.45, my+sag*.55-op*.10, mx+hw*.45, my+sag*.55-op*.10, *Rp)
    if op < 8:
        upper(); c.set_line_width(20); c.set_source_rgb(*LINE); c.stroke()
        if smile > .25:                                # fossettes au bout du sourire et petite lèvre du dessous
            for (x, y), sg in ((Lp, -1), (Rp, 1)):
                c.move_to(x-sg*4, y-22); c.curve_to(x+sg*10, y-6, x+sg*10, y+8, x-sg*2, y+20); c.set_line_width(14); c.stroke()
            yy = my+sag*.55+52; c.move_to(mx-55, yy); c.curve_to(mx-20, yy+14, mx+20, yy+14, mx+55, yy); c.set_line_width(12); c.stroke()
    else:
        def shape(): upper(); c.curve_to(mx+hw*.5, my+sag*.6+op, mx-hw*.5, my+sag*.6+op, *Lp); c.close_path()
        shape(); c.set_source_rgb(.24, .05, .04); c.fill_preserve(); c.save(); c.clip()
        c.rectangle(mx-hw, my-up-60, 2*hw, 40+op*.12); c.set_source_rgb(1, .98, .94); c.fill()
        c.arc(mx, my+sag*.6+op*.95, hw*.55, 0, 2*math.pi); c.set_source_rgb(.93, .38, .33); c.fill()
        c.restore(); shape(); c.set_line_width(18); c.set_source_rgb(*LINE); c.stroke()
    s.flush(); img = Image.frombuffer('RGBA', (w, h), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
    return img, (int(x0*RES), int(y0*RES))

# ---------- gants, chaussures ----------
GANTS = ('ouvert', 'poing', 'index', 'pouce', 'tenir')
@functools.lru_cache(maxsize=16)
def glove(kind, flip=False):
    """gant détouré à RES, poignet (milieu du revers) en bas ; renvoie (image, point du poignet)"""
    im = _key(f'{S2}/gant_{kind}.jpg')
    if kind == 'tenir':                                              # retire la petite pièce tenue : main vide en C
        a = np.asarray(im).copy(); R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
        from scipy import ndimage
        gold = ndimage.binary_dilation((R > 150) & (B < 120) & (R-B > 60), iterations=4); a[..., 3][gold] = 0; im = Image.fromarray(a)
    im = im.crop(im.getbbox())
    target_h = {'ouvert': 370, 'poing': 310, 'index': 370, 'pouce': 280, 'tenir': 320}[kind]*RES
    k = target_h/im.height; im = im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.LANCZOS)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    al = np.asarray(im.getchannel('A')); rows = np.where(al[-max(3, int(12*RES)):].max(0) > 128)[0]
    wx = (rows.min()+rows.max())/2 if len(rows) else im.width/2
    return im, (wx, im.height-6*RES)

@functools.lru_cache(maxsize=2)
def shoe(flip=False):
    im = _key(f'{S2}/chaussure.jpg'); bb = im.getbbox(); im = im.crop(bb)
    k = 345*RES/im.width; im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS); anc = ((364.7-bb[0])*k, (262-bb[1])*k)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); anc = (im.width-anc[0], anc[1])
    return im, anc

def paste_rot(cv, im, anchor, pos, ang, scale=1.):
    """colle im sur cv : anchor (dans im) sur pos (dans cv), après rotation de ang° (horaire si > 0)"""
    if scale != 1.: im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.BICUBIC); anchor = (anchor[0]*scale, anchor[1]*scale)
    if abs(ang) < .05:
        x, y = int(round(pos[0]-anchor[0])), int(round(pos[1]-anchor[1]))
        if x >= 0 and y >= 0: cv.alpha_composite(im, (x, y))
        else: cv.paste(im, (x, y), im)
        return
    import cv2                                                        # rotation rapide (OpenCV) dans une boîte agrandie
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    w2 = int(abs(im.width*ca)+abs(im.height*sa))+4; h2 = int(abs(im.width*sa)+abs(im.height*ca))+4
    M = cv2.getRotationMatrix2D((anchor[0], anchor[1]), -ang, 1.0)
    ax, ay = w2/2+(anchor[0]-im.width/2)*ca-(anchor[1]-im.height/2)*sa, h2/2+(anchor[0]-im.width/2)*sa+(anchor[1]-im.height/2)*ca
    M[0, 2] += ax-anchor[0]; M[1, 2] += ay-anchor[1]
    big = Image.fromarray(cv2.warpAffine(np.asarray(im), M, (w2, h2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)), 'RGBA')
    x, y = int(round(pos[0]-ax)), int(round(pos[1]-ay))
    if x >= 0 and y >= 0: cv.alpha_composite(big, (x, y))
    else: cv.paste(big, (x, y), big)

def _tube(c, p0, p1, bend, w=LIMB_W):
    """membre en caoutchouc (repère kit) : courbe de Bézier, coude ou genou déporté de bend × longueur"""
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1-p0; L = np.linalg.norm(v)+1e-6; n = np.array([-v[1], v[0]])/L
    c1 = p0+v*.33+n*bend*L*.35; c2 = p0+v*.66+n*bend*L*.35
    for ww, colr in ((w+2*LINE_W, LINE), (w, FILL)):
        c.move_to(*p0); c.curve_to(*c1, *c2, *p1); c.set_line_width(ww); c.set_source_rgb(*colr); c.stroke()
    off = n*w*.22
    c.move_to(*(p0+off)); c.curve_to(*(c1+off), *(c2+off), *(p1+off)); c.set_line_width(w*.22); c.set_source_rgba(*HI, .9); c.stroke()
    t = .97; q = (1-t)**3*p0+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*p1
    d = p1-q; return math.degrees(math.atan2(d[0], -d[1]))            # direction en bout de membre (0 = vers le haut, horaire > 0)

REST = {'corps': (0, 0, 0), 'visage': {}, 'bras': {'G': (430, 2010, 'ouvert', None, .45), 'D': (1520, 1990, 'ouvert', None, -.45)},
        'jambes': {'G': (870, 2560, 0), 'D': (1100, 2560, 0)}, 'objet': None}
WK, HK = int(W0*RES), int(H0*RES)
def draw(pose):
    """assemble Mister Coin ; renvoie une toile RGBA à RES (WK × HK) du repère kit"""
    p = dict(REST); p.update(pose)
    im, off, mk = body(); dx, dy, tilt = p['corps']
    piv = COIN_C+np.array([dx, dy]); a = math.radians(tilt); Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    T = lambda pt: piv+Rm@(np.array(pt)-COIN_C)
    cv = Image.new('RGBA', (WK, HK), 0)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WK, HK); c = cairo.Context(s); c.scale(RES, RES); c.set_line_cap(cairo.LINE_CAP_ROUND)
    legs = p['jambes']
    for side in ('G', 'D'):
        ax, ay, ang = legs[side]; _tube(c, T(mk['hanche_'+side]), (ax, ay-12), .10*(-1 if side == 'G' else 1))
    arms = p['bras']; ends = {}
    for side in ('G', 'D'):
        hx, hy, kind, gang, bend = arms[side]; ends[side] = _tube(c, T(mk['epaule_'+side]), (hx, hy), bend)
    s.flush(); cv.alpha_composite(Image.frombuffer('RGBA', (WK, HK), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1))
    for side in ('G', 'D'):                                           # chaussures, pointes vers l'extérieur
        ax, ay, ang = legs[side]; img, anc = shoe(flip=side == 'G')
        paste_rot(cv, img, anc, (ax*RES, ay*RES), -ang if side == 'D' else ang)
    b = im.copy(); fl, fo = face_layer(p['visage']); b.alpha_composite(fl, fo)
    paste_rot(cv, b, (FACE_CX*SC*RES, FACE_CY*SC*RES), (piv[0]*RES, piv[1]*RES), tilt)
    ob = p.get('objet')
    for side in ('G', 'D'):                                           # gants devant la pièce
        hx, hy, kind, gang, bend = arms[side]; g, wa = glove(kind, side == 'G')
        ang = ends[side] if gang is None else gang
        if ob is not None and ob[1] == side and kind == 'tenir':      # objet tenu : dans le creux du C
            oi, _, sc_ = ob; r = math.radians(ang); sg = -1 if side == 'G' else 1
            gx = hx+175*math.sin(r)+sg*55*math.cos(r); gy = hy-175*math.cos(r)+sg*55*math.sin(r)
            o = oi.resize((max(1, int(oi.width*sc_*RES)), max(1, int(oi.height*sc_*RES))), Image.LANCZOS)
            paste_rot(cv, o, (o.width/2, o.height/2), (gx*RES, gy*RES), ang*.3)
        paste_rot(cv, g, wa, (hx*RES, hy*RES), ang)
    return cv
