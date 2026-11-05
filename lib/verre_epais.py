"""Verre épais façon « pièces de puzzle » : biseau arrondi qui réfracte le décor, dispersion arc-en-ciel sur les arêtes,
reflet spéculaire, tranche visible (épaisseur), lumière qui traverse et éclaire le décor derrière.
Prototype du 04/11 : thick_panel(cv, x, y, w, h) dessine directement sur cv (PIL RGBA 1080×1920)."""
import math
import numpy as np, cv2
from PIL import Image

def _sdf(w, h, r, m):
    """distance signée au rectangle arrondi (négative dedans), sur la zone panneau + marge m"""
    ys, xs = np.mgrid[0:h+2*m, 0:w+2*m].astype(np.float32)
    px = np.abs(xs-m-w/2)-(w/2-r); py = np.abs(ys-m-h/2)-(h/2-r)
    out = np.hypot(np.maximum(px, 0), np.maximum(py, 0)); ins = np.minimum(np.maximum(px, py), 0)
    return out+ins-r

def _hsv(hue):
    h6 = (hue % 1.0)*6
    r = np.clip(np.abs(h6-3)-1, 0, 1); g = np.clip(2-np.abs(h6-2), 0, 1); b = np.clip(2-np.abs(h6-4), 0, 1)
    return np.stack([r, g, b], -1)

def glass_local(reg, w, h, m, r=52, bevel=44, depth=(14, 24), light=(-.55, -.75), tint=(1.0, .86, .62),
                warm=(1.0, .78, .45), frost=16, refr=8, disp=.35, irid=.16, glow=.55, back=.0, dim=.80):
    """calcule le verre sur reg (float 0..1, (h+2m)×(w+2m)×3, panneau posé à (m, m)) ; renvoie l'image modifiée"""
    H_, W_ = reg.shape[:2]; reg = reg.copy()
    d = _sdf(w, h, r, m)                                                   # face avant
    ox, oy = depth
    ds = np.full_like(d, 1e3)                                               # tranche : la forme balayée de l'avant vers l'arrière
    for i in range(1, 9):
        sx, sy = int(round(ox*i/8)), int(round(oy*i/8)); sh_ = np.full_like(d, 1e3); sh_[sy:, sx:] = d[:H_-sy, :W_-sx]; ds = np.minimum(ds, sh_)
    dback = np.full_like(d, 1e3); dback[oy:, ox:] = d[:H_-oy, :W_-ox]
    # ---------- lumière qui traverse : halo chaud autour et sous le panneau (pas dedans) ----------
    dm = np.minimum(d, ds)
    lit = np.clip(1-np.maximum(dm, 0)/110, 0, 1)**2*(dm > 0)
    reg = reg+glow*.30*lit[..., None]*np.array(warm, np.float32)
    if back > 0:                                                            # lumière large derrière le panneau (le décor s'éclaire)
        bl = np.exp(-(np.maximum(dm, 0)/(m*.45))**2)*np.clip((m-8-np.maximum(dm, 0))/40, 0, 1)
        reg = reg+back*bl[..., None]*np.array(warm, np.float32)*(.25+.75*np.clip(reg.mean(2, keepdims=True)*6, 0, 1))
    # ---------- normales du biseau (profil arrondi) ----------
    t = np.clip(-d/bevel, 0, 1); hgt = np.sqrt(np.clip(1-(1-t)**2, 0, 1))*bevel*.9
    gy, gx = np.gradient(cv2.GaussianBlur(hgt, (0, 0), 1.0))
    n = np.dstack([-gx, -gy, np.ones_like(gx)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    nx, ny, nz = n[..., 0], n[..., 1], n[..., 2]
    n2 = np.hypot(nx, ny)+1e-6; ux, uy = nx/n2, ny/n2                      # direction du biseau vers l'extérieur
    # ---------- réfraction avec dispersion (rouge, vert, bleu décalés différemment) ----------
    soft = cv2.GaussianBlur(reg, (0, 0), 2.5); fro = cv2.GaussianBlur(reg, (0, 0), frost)
    src = soft*(1-t[..., None])+fro*t[..., None]
    gx_, gy_ = np.meshgrid(np.arange(W_, dtype=np.float32), np.arange(H_, dtype=np.float32))
    ref = np.empty_like(reg)
    for c, f in enumerate((1-disp, 1.0, 1+disp)):
        mx = gx_-nx*refr*f*3.0; my = gy_-ny*refr*f*3.0                       # le biseau « aspire » le décor vers l'intérieur
        ref[..., c] = cv2.remap(np.ascontiguousarray(src[..., c]), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    WARM = np.array(warm, np.float32); TINT = np.array(tint, np.float32)
    plateau = t >= .999
    body = ref*TINT*np.where(plateau, dim, .62)[..., None]+.02               # plateau : transparent, juste un peu assombri
    # ---------- biseau : lignes concentriques façon verre épais ----------
    Lx, Ly = light; Ln = math.hypot(Lx, Ly); Lx, Ly = Lx/Ln, Ly/Ln
    k = ux*Lx+uy*Ly                                                         # 1 : face tournée vers la lumière ; -1 : à l'opposé
    face = np.clip(k, 0, 1); dos = np.clip(-k, 0, 1)
    bev = (t > 0) & ~plateau
    p = t
    lines = (1.15*np.exp(-((p-.10)/.07)**2)*(.25+.75*face)                     # arête extérieure brillante côté lumière
             + .65*np.exp(-((p-.80)/.06)**2)*(.30+.70*face)                    # filet clair près du plateau
             - .45*np.exp(-((p-.45)/.14)**2))                                  # bande sombre au cœur du biseau (épaisseur)
    trans = .95*np.exp(-((p-.35)/.22)**2)*dos**1.3                            # lumière transmise : le bord opposé s'allume en chaud
    lines = lines*bev; trans = trans*bev
    body = body*(1+np.minimum(lines, 0)[..., None])+np.maximum(lines, 0)[..., None]*np.array([1, .97, .92], np.float32)*.85
    body += trans[..., None]*WARM
    # dispersion visible : arc-en-ciel fin sur les arêtes
    rb = _hsv(np.arctan2(uy, ux)/(2*math.pi)*2+p*1.6)
    body += irid*rb*(np.exp(-((p-.22)/.10)**2)+.6*np.exp(-((p-.65)/.08)**2))[..., None]*bev[..., None]
    # reflet large et doux sur le plateau (diagonale)
    diag = (gx_*.6+gy_)/(W_*.6+H_)
    body += plateau[..., None]*(.05*np.exp(-((diag-.30)/.05)**2)+.03*np.exp(-((diag-.40)/.02)**2))[..., None]
    # reflet spéculaire ponctuel (coin face à la lumière)
    Lv = np.array([Lx*.8, Ly*.8, .6], np.float32); Lv /= np.linalg.norm(Lv); Hh = Lv+np.array([0, 0, 1], np.float32); Hh /= np.linalg.norm(Hh)
    spec = np.clip(nx*Hh[0]+ny*Hh[1]+nz*Hh[2], 0, 1)**140*bev
    body += 2.2*spec[..., None]
    # liseré extérieur net
    rim = np.exp(-((d+1.0)/1.1)**2); body += rim[..., None]*(.25+.6*face)[..., None]
    # ---------- tranche : verre plus sombre, liseré chaud en bas, irisée ----------
    sidec = fro*TINT*.42+.04*WARM
    edge_s = np.exp(-((ds+1.6)/1.5)**2)+.5*np.exp(-((dback+1.2)/1.2)**2)*(d > 0)
    sidec += edge_s[..., None]*(.35*WARM+.25)
    sidec += irid*.9*_hsv(gx_/W_*1.4+gy_/H_*.6+.3)*np.exp(-((ds+3)/3.5)**2)[..., None]
    sidec += .35*WARM*np.clip(1-(d/(max(depth)*1.2)), 0, 1)[..., None]*(d > 0)[..., None]*.5   # lumière qui fuit dans la tranche
    # ---------- assemblage avec antialias ----------
    af = np.clip(.5-d, 0, 1); asd = np.clip(.5-ds, 0, 1)*(1-af)
    out = reg*(1-af[..., None]-asd[..., None]*.92)+body*af[..., None]+sidec*asd[..., None]*.92
    sh = cv2.GaussianBlur(np.clip(-np.minimum(d, ds)+30, 0, 1).astype(np.float32), (0, 0), 28)
    sh = np.roll(sh, 40, axis=0)*(1-np.maximum(af, asd))
    out *= (1-.35*sh)[..., None]
    return out

def thick_panel(cv, x, y, w, h, a=1.0, **kw):
    """version à plat : x, y = coin haut gauche du panneau, dessine directement sur cv"""
    if a <= .01: return
    m = 140; X0, Y0 = int(x)-m, int(y)-m; W_, H_ = w+2*m, h+2*m
    big = np.asarray(cv.convert('RGB')).astype(np.float32)/255
    pad = np.pad(big, ((m+200, m+200), (m+200, m+200), (0, 0)), mode='edge')
    reg = pad[Y0+m+200:Y0+m+200+H_, X0+m+200:X0+m+200+W_]
    out = glass_local(reg, w, h, m, **kw); out = reg+(out-reg)*a
    xa, ya = max(X0, 0), max(Y0, 0); xb, yb = min(X0+W_, cv.width), min(Y0+H_, cv.height)
    big[ya:yb, xa:xb] = np.clip(out[ya-Y0:yb-Y0, xa-X0:xb-X0], 0, 1)
    cv.paste(Image.fromarray((big*255).astype(np.uint8), 'RGB').convert('RGBA'))

# ---------- humeurs : la couleur du verre dit si l'information est neutre, mauvaise ou bonne ----------
MOODS = {'or': dict(tint=(1.0, .88, .70), warm=(1.0, .76, .42)),
         'orange': dict(tint=(1.0, .86, .74), warm=(1.0, .55, .22)),
         'rouge': dict(tint=(1.0, .80, .80), warm=(1.0, .34, .30)),
         'vert': dict(tint=(.84, 1.0, .90), warm=(.32, 1.0, .56)),
         'bleu': dict(tint=(.86, .93, 1.0), warm=(.55, .85, 1.0))}
MARGIN = 200
_CACHE = {}
def _content(w, h, m, draw):
    import cairo
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w+2*m, h+2*m); c = cairo.Context(s); c.translate(m, m); draw(c, w, h); s.flush()
    b = np.frombuffer(s.get_data(), np.uint8).reshape(h+2*m, s.get_stride()//4, 4)[:, :w+2*m].astype(np.float32)/255
    return b[..., [2, 1, 0]], b[..., 3:]                                      # couleurs prémultipliées, alpha
def tplace(cv, base, w, h, draw, quad, a=1.0, mood='or', cache=True, **kw):
    """panneau de verre épais en perspective. base : décor statique (array float 0..1, H×W×3) sur lequel le verre est calculé
    (mis en cache tant que le panneau ne bouge pas) ; on ajoute à cv la différence verre − décor, plus le contenu (draw)."""
    if a <= .01: return
    m = MARGIN; W_, H_ = w+2*m, h+2*m
    src = np.float32([[m, m], [m+w, m], [m+w, m+h], [m, m+h]]); dst = np.float32(quad)
    Hm = cv2.getPerspectiveTransform(src, dst)
    key = (id(base), w, h, mood, tuple(np.round(dst, 1).ravel()), tuple(sorted(kw.items())))
    if not cache: _CACHE.pop(key, None)          # base éphémère : son id() peut être réutilisé, ne jamais s'y fier
    if key not in _CACHE:
        L = cv2.warpPerspective(base, Hm, (W_, H_), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        p = dict(MOODS[mood]); p.update(kw); G = glass_local(L, w, h, m, back=.22, **p)
        if len(_CACHE) > 24: _CACHE.clear()
        _CACHE[key] = (G-L, L)
    delta, L = _CACHE[key] if cache else _CACHE.pop(key)
    cr, ca = _content(w, h, m, draw)
    G = L+delta; delta = G*(1-ca)+cr-L                                         # le contenu se pose sur le verre
    # boîte englobante à l'écran
    corners = cv2.perspectiveTransform(np.float32([[[0, 0]], [[W_, 0]], [[W_, H_]], [[0, H_]]]), Hm).reshape(-1, 2)
    x0, y0 = np.floor(corners.min(0)).astype(int); x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, cv.width), min(y1, cv.height)
    if x1 <= x0 or y1 <= y0: return
    T = np.float64([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]])@Hm
    dw = cv2.warpPerspective(delta, T, (x1-x0, y1-y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    arr = np.asarray(cv).copy(); sub = arr[y0:y1, x0:x1, :3].astype(np.float32)/255
    sub = np.clip(sub+a*dw, 0, 1); arr[y0:y1, x0:x1, :3] = (sub*255+.5).astype(np.uint8)
    cv.paste(Image.fromarray(arr, cv.mode))
