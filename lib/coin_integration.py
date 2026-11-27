"""Intégration de Mister Coin dans les décors : le niveau validé par Nicolas le 27/11 (test bibliothèque, « à garder partout et tout le temps »).
Toute vidéo avec Mister Coin passe par ce module, quel que soit le format.

Trois briques :
1. fluidite60(frames, k, extra) : image k (en 60 i/s) d'une suite à 24 i/s, interpolée par flux optique (couleur et alpha déformés ensemble).
   À appliquer aux clips Veo AVANT de les poser, sinon chaque image est tenue 2 ou 3 fois et il saccade.
2. suivi_surface(frames60, pied0, zone) : positions et échelles des pieds image par image, accrochés à la surface où il se tient
   (points suivis dans `zone`, transformation similitude, lissée). Évite qu'il flotte quand la caméra bouge.
3. integrer(bg, C, A, pieds, ech, bord_y=None, reflet=True) : compose Mister Coin dans le décor avec la lumière de la scène :
   teinte calée sur le décor, lueur dorée et flaque de lumière chaude, reflet sur les surfaces vernies (coupé au bord bord_y),
   ombre de contact serrée plus ombre douce, light wrap sur les contours, liseré chaud en haut de la pièce.
   bg, C : float32 H×W×3 (0-255) ; A : float32 H×W (0-1), C et A déjà posés plein cadre (pieds sur `pieds`).

Règles qui vont avec (docs/retours.md, 27/11) :
- Il se tient sur une vraie surface du décor (table, plancher, plaque), jamais en l'air ; le reflet demande de la place sous ses pieds.
- reflet=False sur les surfaces mates (tapis, terre, tissu) ; l'ombre et la lumière restent toujours.
Exemple complet : episodes/2026-11-28_patrimoine_age/test_anim.py (avant / après)."""
import numpy as np, cv2

GOLD = np.array([255, 196, 92], np.float32)
_DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

def _flow(a, b, s=.5):
    g = lambda x: cv2.cvtColor(cv2.resize(x, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    return cv2.resize(_DIS.calc(g(a), g(b), None), (a.shape[1], a.shape[0]))/s

def fluidite60(frames, k, extra=(), sp=1.0, fps=60, src_fps=24):
    """image k/fps s d'une suite à src_fps (uint8 RGB) ; extra : autres couches (alpha…) déformées par le même flux ; sp : vitesse"""
    s = k/fps*src_fps*sp; i = min(int(s), len(frames)-2); a = s-i
    if a < 1e-3: return frames[i], [e[i] for e in extra]
    f01, f10 = _flow(frames[i], frames[i+1]), _flow(frames[i+1], frames[i])
    h, w = frames[i].shape[:2]; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    def mix(P, Q):
        w0 = cv2.remap(P, gx-a*f01[..., 0], gy-a*f01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(Q, gx-(1-a)*f10[..., 0], gy-(1-a)*f10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return cv2.addWeighted(w0, 1-a, w1, a, 0)
    return mix(frames[i], frames[i+1]), [mix(e[i], e[i+1]) for e in extra]

def suivi_surface(frames60, pied0, zone, lissage=15):
    """frames60 : décor en 60 i/s (uint8 RGB) ; pied0 : (x, y) des pieds sur la première image ; zone : (x0, y0, x1, y1) de la surface.
    Renvoie (pieds N×2, échelles N)."""
    H, W = frames60[0].shape[:2]; m = np.zeros((H, W), np.uint8); x0, y0, x1, y1 = zone; m[y0:y1, x0:x1] = 255
    P = [np.array(pied0, float)]; S = [1.0]; Mc = np.eye(3); prev = cv2.cvtColor(frames60[0], cv2.COLOR_RGB2GRAY)
    for f in frames60[1:]:
        cur = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        p0 = cv2.goodFeaturesToTrack(prev, 400, .005, 12, mask=m)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None, winSize=(31, 31), maxLevel=4); ok = st.ravel() == 1
        M, _ = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
        if M is not None: Mc = np.vstack([M, [0, 0, 1]]) @ Mc
        P.append((Mc @ [*pied0, 1])[:2]); S.append(float(np.sqrt(abs(np.linalg.det(Mc[:2, :2]))))); prev = cur
    P, S = np.array(P), np.array(S); r = lissage//2; ker = np.ones(lissage)/lissage
    for j in range(2): P[:, j] = np.convolve(np.pad(P[:, j], r, mode='edge'), ker, 'valid')
    return P, np.convolve(np.pad(S, r, mode='edge'), ker, 'valid')

def integrer(bg, C, A, pieds, ech=1.0, bord_y=None, reflet=True, lueur=1.0):
    H, W = A.shape; fx, fy = pieds; sc = ech
    # 1. teinte de la scène
    roi = bg[max(0, int(fy-520*sc)):int(fy+40), max(0, int(fx-300)):int(fx+300)].reshape(-1, 3).mean(0)
    C = C*(.7+.3*roi/(roi.mean()+1e-6))
    # 2. lueur dorée et flaque de lumière chaude
    glow = cv2.GaussianBlur(A, (0, 0), 38*sc)
    pool = np.zeros((H, W), np.float32); cv2.ellipse(pool, (int(fx), int(fy)+10), (int(260*sc), int(60*sc)), 0, 0, 360, 1, -1)
    bg = bg+(cv2.GaussianBlur(pool, (0, 0), 40*sc)*.45+glow*.55)[..., None]*GOLD*.55*lueur
    # 3. reflet (symétrie autour de la ligne des pieds, teinté par la surface, fondu, coupé au bord)
    if reflet:
        Mr = np.float32([[1, 0, 0], [0, -1, 2*fy]]); Cr = cv2.warpAffine(C, Mr, (W, H)); Ar = cv2.warpAffine(A, Mr, (W, H))
        yy = np.arange(H, dtype=np.float32)[:, None]
        f = np.clip(1-(yy-fy)/(340*sc), 0, 1)**1.3*(yy > fy)
        if bord_y is not None: f = f*(yy < bord_y-4)
        Ar = cv2.GaussianBlur(Ar*f, (0, 0), sigmaX=1.2, sigmaY=3)*.68; Cr = cv2.GaussianBlur(Cr, (0, 0), sigmaX=1.2, sigmaY=3)*(.55+.45*bg/255)
        bg = bg*(1-Ar[..., None])+Cr*Ar[..., None]
    # 4. ombre de contact
    sh = np.zeros((H, W), np.float32); cv2.ellipse(sh, (int(fx), int(fy)), (int(70*sc), int(9*sc)), 0, 0, 360, .75, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 5*sc)
    s2 = np.zeros((H, W), np.float32); cv2.ellipse(s2, (int(fx+18*sc), int(fy+4)), (int(150*sc), int(26*sc)), 0, 0, 360, .35, -1)
    bg = bg*(1-np.maximum(sh, cv2.GaussianBlur(s2, (0, 0), 18*sc))[..., None])
    # 5. light wrap
    blur = cv2.GaussianBlur(bg, (0, 0), 14); e = np.clip(A-cv2.erode(A, np.ones((9, 9), np.uint8)), 0, 1)
    e = cv2.GaussianBlur(e, (0, 0), 4)[..., None]*.75; C = C*(1-e)+blur*e
    # 6. liseré chaud en haut de la pièce
    top = cv2.GaussianBlur(np.clip(A-np.roll(A, int(10*sc), axis=0), 0, 1), (0, 0), 3)[..., None]*.45
    C = C+top*(GOLD-C*.4)
    return bg*(1-A[..., None])+C*A[..., None]
