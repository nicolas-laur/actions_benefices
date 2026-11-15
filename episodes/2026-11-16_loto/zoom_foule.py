"""Plongée « 1 chance sur 19 068 840 » (v3, motion design) : une foule de petits personnages 1930 qui s'étend jusqu'à l'horizon,
vue d'une caméra qui pique du ciel (vue rasante, légère rotation) jusqu'à la verticale au-dessus de TOI, en doré, sous un projecteur.
Rendu : sol en perspective (homographie écran -> sol), échantillonné par bandes horizontales avec mip-maps (pas de scintillement),
brume de distance, projecteur au sol, faisceau de lumière, halo doré, flou de mouvement par sous-images.
frame(u, W, H) -> (image BGR float, (x, y, taille d'un personnage en px) de TOI à l'écran)."""
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__))
TX, TY = 2911.0, 1733.0
G, C = 4, 512                     # motif de 4 × 4 personnages, texture de 512 px
OUT = (55, 32, 24)
SHIRTS = [(226, 87, 76), (46, 150, 150), (232, 182, 64), (110, 150, 205), (120, 170, 90), (200, 110, 160), (240, 140, 70), (90, 110, 170)]
SKINS = [(247, 214, 182), (230, 184, 140), (190, 135, 95), (140, 95, 65)]
HAIRS = [(70, 45, 30), (30, 25, 25), (150, 95, 45), (215, 175, 90), (110, 70, 40)]
GROUND = (112, 84, 82)             # sol (RGB) : parquet de scène sombre
HAZE = np.float32([120, 80, 125])  # brume lointaine (RGB)
def ease(x): x = min(1., max(0., x)); return x*x*(3-2*x)
def _person(i, gold=False, P=128):
    S = 4; B0 = 128; im = Image.new('RGBA', (B0*S, B0*S), 0); d = ImageDraw.Draw(im); w = 5*S
    sh, sk, hr = SHIRTS[i % 8], SKINS[(i*3+1) % 4], HAIRS[(i*7+2) % 5]
    if gold: sh, sk, hr = (255, 196, 40), (255, 228, 150), (235, 165, 30)
    cx = B0*S//2; arm = 1 if i % 3 else -1
    d.ellipse([cx-26*S, 108*S, cx+26*S, 124*S], fill=(0, 0, 0, 70))                       # petite ombre au sol
    for sx in (-1, 1):
        d.line([(cx+sx*9*S, 92*S), (cx+sx*12*S, 116*S)], fill=OUT, width=11*S); d.line([(cx+sx*9*S, 92*S), (cx+sx*12*S, 116*S)], fill=(60, 60, 80), width=6*S)
    for sx in (-1, 1):
        y2 = 40*S if arm > 0 else 92*S
        d.line([(cx+sx*18*S, 62*S), (cx+sx*33*S, y2)], fill=OUT, width=10*S); d.line([(cx+sx*18*S, 62*S), (cx+sx*33*S, y2)], fill=sh, width=5*S)
        d.ellipse([cx+sx*33*S-6*S, y2-6*S, cx+sx*33*S+6*S, y2+6*S], fill=(250, 250, 245), outline=OUT, width=w//2)
    d.rounded_rectangle([cx-21*S, 55*S, cx+21*S, 96*S], radius=12*S, fill=sh, outline=OUT, width=w)
    d.ellipse([cx-20*S, 14*S, cx+20*S, 56*S], fill=sk, outline=OUT, width=w)
    d.chord([cx-20*S, 12*S, cx+20*S, 46*S], 180, 360, fill=hr, outline=OUT, width=w)
    for sx in (-1, 1): d.ellipse([cx+sx*8*S-3*S, 34*S-4*S, cx+sx*8*S+3*S, 34*S+4*S], fill=OUT)
    d.arc([cx-8*S, 36*S, cx+8*S, 48*S], 20, 160, fill=OUT, width=3*S)
    return im.crop((10*S, 6*S, 118*S, 114*S)).resize((P, P), Image.LANCZOS)          # personnage plus grand dans sa case : foule dense
MIPS = {}
def _build():
    q = C//G; cell = np.zeros((C, C, 3), np.float32); cell[:] = GROUND[::-1]
    for j in range(G*G):
        p = np.asarray(_person(j, False, q)).astype(np.float32); a = p[..., 3:]/255
        y, x = (j//G)*q, (j % G)*q; cell[y:y+q, x:x+q] = cell[y:y+q, x:x+q]*(1-a)+p[..., [2, 1, 0]]*a
    j = (int(TY) % G)*G+int(TX) % G; p = np.asarray(_person(j, True, C)).astype(np.float32)
    gold = np.dstack([p[..., [2, 1, 0]]*p[..., 3:]/255, p[..., 3:]/255])
    for k, t in (('n', cell), ('g', gold)):
        m = [t]
        while m[-1].shape[0] > 1: m.append(cv2.resize(m[-1], (max(1, m[-1].shape[1]//2),)*2, interpolation=cv2.INTER_AREA))
        MIPS[k] = m
def camera(u):
    """Paramètres de caméra le long de la plongée."""
    e = ease(u); e2 = ease(min(1, u*1.25))
    dist = math.exp(math.log(75)+(math.log(4.2)-math.log(75))*e)       # distance à TOI (en personnages)
    pitch = math.radians(36+(90-36)*e2)                                      # vue rasante -> verticale
    yaw = math.radians(28*(1-e)+6*math.sin(u*2.2))                           # légère rotation
    return dist, pitch, yaw
def _basis(pitch, yaw):
    h = np.array([math.sin(yaw), -math.cos(yaw), 0.])                        # regard horizontal vers -Y (têtes vers le lointain)
    fwd = h*math.cos(pitch)+np.array([0, 0, -math.sin(pitch)])
    right = np.array([math.cos(yaw), math.sin(yaw), 0.])
    down = np.cross(right, fwd); down /= np.linalg.norm(down)        # bas de l'écran = vers la caméra au sol
    return fwd, right, down
def frame(u, W=1080, H=1920, cy=None, sub=0.):
    if not MIPS: _build()
    cy = H*.47 if cy is None else cy; cx = W/2; f = W*1.05
    dist, pitch, yaw = camera(u)
    fwd, right, down = _basis(pitch, yaw)
    T = np.array([TX+.5, TY+.62, 0.]); cam = T-fwd*dist
    A = np.stack([right, down, fwd*f-right*cx-down*cy], 1)                     # d = A · (x, y, 1)
    Hs = np.stack([cam[0]*A[2]-cam[2]*A[0], cam[1]*A[2]-cam[2]*A[1], A[2]])   # écran -> sol (homogène)
    yy = np.arange(H, dtype=np.float64)
    dz = A[2, 1]*yy+A[2, 0]*cx+A[2, 2]                                        # composante verticale du rayon, colonne centrale
    valid = dz < -1e-9
    def ground(x, y):
        v = Hs@np.array([x, y, 1.]); return v[:2]/v[2]
    # niveau de mip par ligne (empreinte d'un pixel au sol, en personnages)
    lod = np.full(H, 99.)
    for y in range(0, H, 8):
        if not valid[y]: continue
        p0 = ground(cx, y); p1 = ground(cx+1, y); p2 = ground(cx, y+1)
        fp = max(np.hypot(*(p1-p0)), np.hypot(*(p2-p0)))
        lod[y:y+8] = math.log2(max(1e-6, fp*C/G))-.8                     # un peu plus net (le flou de mouvement lisse)
    img = np.zeros((H, W, 3), np.float32)
    rows = np.where(valid)[0]
    if len(rows):
        y = rows[0]
        while y < H:
            l = lod[y]; y2 = y
            while y2 < H and abs(lod[y2]-l) < .25 and y2-y < 96: y2 += 1
            band = 0
            L = max(0., l); l0 = int(L); fr = L-l0
            for li, wgt in ((l0, 1-fr), (l0+1, fr)):
                if wgt <= 1e-3: continue
                t = MIPS['n'][min(li, len(MIPS['n'])-1)]; r = t.shape[0]/G
                M = np.diag([r, r, 1.])@Hs@np.array([[1, 0, 0], [0, 1, y], [0, 0, 1.]])
                band = band+wgt*cv2.warpPerspective(t, M, (W, y2-y), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)
            img[y:y2] = band; y = y2
    # TOI en doré (un seul personnage)
    p0 = ground(cx, cy); p1 = ground(cx+1, cy); lg = max(0., math.log2(max(1e-6, np.hypot(*(p1-p0))*C)))
    g = 0
    for li, wgt in ((int(lg), 1-(lg-int(lg))), (int(lg)+1, lg-int(lg))):
        t = MIPS['g'][min(li, len(MIPS['g'])-1)]; r = t.shape[0]
        M = np.array([[r, 0, -r*int(TX)], [0, r, -r*int(TY)], [0, 0, 1.]])@Hs
        g = g+wgt*cv2.warpPerspective(t, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    # carte de distance au sol (basse résolution) : brume + projecteur
    s4 = 8; xs, ys = np.meshgrid(np.arange(0, W, s4)+s4/2, np.arange(0, H, s4)+s4/2)
    v = np.tensordot(Hs, np.stack([xs, ys, np.ones_like(xs)]), 1)
    ok = (A[2, 0]*xs+A[2, 1]*ys+A[2, 2]) < -1e-9
    gx, gy = v[0]/np.where(ok, v[2], 1), v[1]/np.where(ok, v[2], 1)
    rdist = np.hypot(gx-T[0], gy-T[1]); depth = np.where(ok, np.hypot(gx-cam[0], gy-cam[1]), 1e9)
    spot = np.where(ok, .72+1.1*np.exp(-(rdist/max(2.2, dist*.05))**2), 0)
    fog = np.where(ok, 1-np.exp(-depth/(dist*4+250)), 1)
    spot = cv2.resize(spot.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    fog = cv2.resize(fog.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    img = img*spot
    if isinstance(g, np.ndarray): img = img*(1-g[..., 3:])+g[..., :3]*(.6+.4*spot)
    img = img*(1-fog)+HAZE[::-1]*fog*.9
    # ciel (au-dessus de l'horizon) : velours sombre et faisceaux lents
    sky = ~valid
    if sky.any():
        hy = int(np.where(sky)[0].max())+1; yy2 = np.linspace(0, 1, hy)[:, None, None]
        top = np.float32([30, 14, 40])[::-1]; bot = np.float32([120, 80, 125])[::-1]
        img[:hy] = top*(1-yy2**1.6)+bot*yy2**1.6
    # faisceau du projecteur vers TOI
    Pt = A@np.array([cx, cy, 1.]); tx_, ty_ = cx, cy
    beam = np.zeros((H//4, W//4), np.float32); bw = max(6., 140/ max(1., dist**.35))
    pts = np.array([[tx_/4-bw/4, ty_/4], [tx_/4+bw/4, ty_/4], [W/8+60, -10], [W/8-60, -10]], np.int32)
    cv2.fillConvexPoly(beam, pts, 1.); beam = cv2.GaussianBlur(beam, (0, 0), 6)
    beam = cv2.resize(beam, (W, H))[..., None]; img = img+beam*np.float32([255, 230, 170])[::-1]*.18
    # halo doré autour de TOI
    if isinstance(g, np.ndarray):
        ga = cv2.GaussianBlur(g[..., 3], (0, 0), 18)[..., None]; img = img+ga*np.float32([255, 200, 80])[::-1]*.55
    # vignettage
    vy, vx = np.ogrid[:H, :W]; vg = 1-.45*(((vx-W/2)/(W*.75))**2+((vy-H*.5)/(H*.7))**2)
    img = img*np.clip(vg, .45, 1)[..., None]
    sz = abs(1/np.hypot(*(ground(cx+1, cy)-ground(cx, cy))))
    return img, (cx, cy, sz)
if __name__ == '__main__':
    import subprocess, sys
    from PIL import ImageFont
    W, H, F = (540, 960, 30) if 'petit' in sys.argv else (1080, 1920, 60)
    k_ = W/1080; FT = ImageFont.truetype(f'{D}/../../fonts/AlfaSlabOne-Regular.ttf', int(96*k_)); FS = ImageFont.truetype(f'{D}/../../fonts/AlfaSlabOne-Regular.ttf', int(60*k_))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(F), '-i', '-',
                           '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', f'{D}/zoom_apercu.mp4'], stdin=subprocess.PIPE)
    T0, DU = .6, 3.6
    for i in range(int(5.2*F)):
        t = i/F; acc = 0
        for k in range(2):                                     # flou de mouvement : 2 sous-images
            im, (x, y, sz) = frame(min(1, max(0, (t+(k-.5)/(2*F)-T0)/DU)), W, H); acc = acc+im/2
        pil = Image.fromarray(np.clip(acc[..., ::-1], 0, 255).astype(np.uint8)).convert('RGBA'); lay = Image.new('RGBA', pil.size, 0); dl = ImageDraw.Draw(lay)
        u = (t-T0)/DU; a1 = min(1, t/.3)*(1-min(1, max(0, (u-.45)/.15)))
        if a1 > 0: dl.text((W/2, 300*k_), "19 068 840 joueurs", font=FT, anchor='mm', fill=(255, 235, 200, int(255*a1)), stroke_width=int(7*k_), stroke_fill=(40, 20, 50, int(255*a1)))
        a2 = min(1, max(0, (u-.92)/.1))
        if a2 > 0:
            r = sz*.62
            dl.text((x, y-r-80*k_), "TOI", font=FT, anchor='mm', fill=(255, 205, 70, int(255*a2)), stroke_width=int(8*k_), stroke_fill=(40, 20, 50, int(255*a2)))
            dl.text((x, y+r+70*k_), "1 chance sur 19 068 840", font=FS, anchor='mm', fill=(255, 245, 225, int(255*a2)), stroke_width=int(6*k_), stroke_fill=(40, 20, 50, int(255*a2)))
        ff.stdin.write(np.asarray(Image.alpha_composite(pil, lay).convert('RGB')).tobytes())
    ff.stdin.close(); ff.wait()
