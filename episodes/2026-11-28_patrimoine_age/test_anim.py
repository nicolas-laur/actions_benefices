"""Test avant / après de l'intégration de Mister Coin (5 s, décor bibliothèque du 26/11, clip classique_parle_enthousiaste).
AVANT : méthode actuelle (clip à 24 i/s tenu sur 60 i/s, position fixe, ombre ovale).
APRÈS : clip interpolé en 60 i/s par flux optique, pieds accrochés à la table (suivi de caméra), ombre de contact,
reflet sur le bois verni, flaque de lumière chaude, lueur dorée, bords éclairés par le décor (light wrap), teinte calée sur la scène.
usage : python3 test_anim.py  ->  avant_apres.mp4"""
import sys, subprocess, numpy as np, cv2
R = '/home/claude/actions_benefices'
sys.path.insert(0, f'{R}/mister_coin'); sys.path.insert(0, f'{R}/episodes/2026-11-26_histoires_incroyables')
import veo_coin as VC
W, H, FPS, DUR = 1080, 1920, 60, 5.0
_ys, _xs = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1-.55*np.clip(np.sqrt(((_xs-W/2)/(W*.62))**2+((_ys-H/2)/(H*.62))**2)-.55, 0, 1)**1.4*2.2, .3, 1)[..., None]
def film(img, t):
    """même effet pellicule que video_col.py (scintillement, grain, poussières), sans les rayures pour la comparaison"""
    rng = np.random.default_rng(7000+int(t*24)); img = img*(1+rng.normal(0, .010))
    g = cv2.resize(rng.normal(0, 1, (H//2, W//2)).astype(np.float32), (W, H)); img = img+g[..., None]*9
    return np.clip(img*VIG, 0, 255)
N = int(DUR*FPS)
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def flow(a, b, s=.5):
    g = lambda x: cv2.cvtColor(cv2.resize(x, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    f = DIS.calc(g(a), g(b), None); return cv2.resize(f, (a.shape[1], a.shape[0]))/s
def read(path, n=None):
    cap = cv2.VideoCapture(path); fr = []
    while n is None or len(fr) < n:
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    return fr
def interp(frames, k, extra=(), sp=1.0):
    """image k/60 s d'une suite à 24 i/s : les deux voisines déformées le long du flux puis fondues (extra : couches déformées pareil)"""
    s = k/FPS*24*sp; i = min(int(s), len(frames)-2); a = s-i
    if a < 1e-3: return frames[i], [e[i] for e in extra]
    f01, f10 = flow(frames[i], frames[i+1]), flow(frames[i+1], frames[i])
    h, w = frames[i].shape[:2]; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    def mix(A, B):
        w0 = cv2.remap(A, gx-a*f01[..., 0], gy-a*f01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(B, gx-(1-a)*f10[..., 0], gy-(1-a)*f10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return cv2.addWeighted(w0, 1-a, w1, a, 0)
    return mix(frames[i], frames[i+1]), [mix(e[i], e[i+1]) for e in extra]

# ---------- décor : 1080×1920 (bicubique ici ; Real-ESRGAN dans le vrai pipeline) ----------
dec24 = [cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC) for f in read(f'{R}/episodes/2026-11-26_histoires_incroyables/decors/decor_bibliotheque.mp4', 130)]
print('décor', len(dec24), flush=True)
import os
STILL = os.environ.get('STILL')
if STILL and os.path.exists('cache.npz'):
    z = np.load('cache.npz'); KEEP = list(z['keep']); dec60 = {int(k): z[f'd{k}'] for k in KEEP}; anch, scl = z['anch'], z['scl']
else:
    dec60 = [interp(dec24, k, sp=.5)[0] for k in range(N)]   # décor ralenti comme dans le pipeline (vitesse 0,5)
print('décor 60 i/s', flush=True)

FEET0 = np.array([540., 1440.]); EDGE0 = 1585.   # milieu du plateau ; EDGE0 = bord avant de la table à l'image 0
if not (STILL and os.path.exists('cache.npz')):
    # ---------- suivi de caméra : transformation de la table (bas de l'image) image par image ----------
    anch = [FEET0.copy()]; scl = [1.0]; Mcum = np.eye(3)
    mask = np.zeros((H, W), np.uint8); mask[1380:1900, 60:1020] = 255
    prev = cv2.cvtColor(dec60[0], cv2.COLOR_RGB2GRAY)
    for k in range(1, N):
        cur = cv2.cvtColor(dec60[k], cv2.COLOR_RGB2GRAY)
        p0 = cv2.goodFeaturesToTrack(prev, 400, .005, 12, mask=mask)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None, winSize=(31, 31), maxLevel=4)
        ok = st.ravel() == 1; M, _ = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
        Mcum = np.vstack([M, [0, 0, 1]]) @ Mcum
        anch.append((Mcum @ [*FEET0, 1])[:2]); scl.append(float(np.sqrt(abs(np.linalg.det(Mcum[:2, :2]))))); prev = cur
    anch = np.array(anch); scl = np.array(scl)
    # lissage (le suivi par image tremble) : moyenne glissante centrée
    ker = np.ones(15)/15
    for j in range(2): anch[:, j] = np.convolve(np.pad(anch[:, j], 7, mode='edge'), ker, 'valid')
    scl = np.convolve(np.pad(scl, 7, mode='edge'), ker, 'valid')
    KEEP = [0, 75, 150, 225, 299]; np.savez('cache.npz', keep=KEEP, anch=anch, scl=scl, **{f'd{k}': dec60[k] for k in KEEP})
print('suivi : déplacement final', anch[-1]-anch[0], 'échelle', scl[-1], flush=True)

# ---------- clip Mister Coin : détouré, recadré, mis à l'échelle ----------
CW, CX, FY = 187, 647, 569          # catalogue : largeur de la pièce, centre, pieds dans le clip 16:9
S = 170*2.45/409                    # même taille que dans les épisodes (largeur_piece 170)
x0, x1, y0, y1 = CX-360, CX+360, 0, FY+30
raw = read(f'{R}/mister_coin/veo/classique_parle_enthousiaste.mp4')[52:52+int(DUR*24)+2]
cols, alps = [], []
for f in raw:
    c, a = VC._key(f[y0:y1, x0:x1]); cols.append(np.clip(c, 0, 255).astype(np.uint8)); alps.append((a*255).astype(np.uint8))
print('clip', len(raw), flush=True)
def coin_frame(k, smooth):
    if smooth: c, (a,) = interp(cols, k, (alps,)); return c.astype(np.float32), a.astype(np.float32)/255
    i = min(int(k/FPS*24), len(cols)-1); return cols[i].astype(np.float32), alps[i].astype(np.float32)/255
def place(c, a, feet, s):
    """pose le clip (recadré) pour que ses pieds tombent sur feet ; renvoie couleur et alpha plein cadre"""
    k = S*s; M = np.float32([[k, 0, feet[0]-(CX-x0)*k], [0, k, feet[1]-(FY-y0)*k]])
    C = cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR); A = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    return C, A, M

def avant(k):
    bg = dec60[k].astype(np.float32); c, a = coin_frame(k, False); C, A, _ = place(c, a, FEET0, 1.0)
    m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(FEET0[0]), int(FEET0[1])-3), (95, 15), 0, 0, 360, .5, -1)
    bg *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    return bg*(1-A[..., None])+C*A[..., None]

GOLD = np.array([255, 196, 92], np.float32)
def apres(k):
    bg = dec60[k].astype(np.float32); s = scl[k]; ft = anch[k]
    c, a = coin_frame(k, True); C, A, M = place(c, a, ft, s)
    fx, fy = ft; sc = s
    # 1. teinte calée sur la lumière de la scène : couleur moyenne du décor autour de lui
    roi = bg[int(fy-520*sc):int(fy+40), int(fx-300):int(fx+300)].reshape(-1, 3).mean(0)
    tint = roi/roi.mean(); C = C*(.7+.3*tint)
    # 2. lueur dorée (il « rayonne » comme une pièce d'or) et flaque de lumière chaude sur la table
    glow = cv2.GaussianBlur(A, (0, 0), 38*sc)
    pool = np.zeros((H, W), np.float32); cv2.ellipse(pool, (int(fx), int(fy)+10), (int(260*sc), int(60*sc)), 0, 0, 360, 1, -1)
    pool = cv2.GaussianBlur(pool, (0, 0), 40*sc)
    bg = bg+(glow*.55+pool*.45)[..., None]*GOLD*.55
    # 3. reflet sur le bois verni : symétrique sous les pieds, flou vertical, fondu vers le bas
    Mr = np.float32([[1, 0, 0], [0, -1, 2*fy]])          # symétrie de l'image composée autour de la ligne des pieds
    Cr = cv2.warpAffine(C, Mr, (W, H)); Ar = cv2.warpAffine(A, Mr, (W, H))
    yy = np.arange(H, dtype=np.float32)[:, None]; fadeR = np.clip(1-(yy-fy)/(340*sc), 0, 1)**1.3*(yy > fy)*(yy < fy+(EDGE0-FEET0[1])*sc-4)   # pas de reflet au-delà du bord de la table
    Ar = cv2.GaussianBlur(Ar*fadeR, (0, 0), sigmaX=1.2, sigmaY=3)*.68; Cr = cv2.GaussianBlur(Cr, (0, 0), sigmaX=1.2, sigmaY=3)*(.55+.45*bg/255)   # reflet teinté par le bois
    bg = bg*(1-Ar[..., None])+Cr*Ar[..., None]
    # 4. ombre de contact : serrée et sombre sous les pieds + ombre douce plus large
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(fx), int(fy)), (int(70*sc), int(9*sc)), 0, 0, 360, .75, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 5*sc)
    sh2 = np.zeros((H, W), np.float32); cv2.ellipse(sh2, (int(fx+18*sc), int(fy+4)), (int(150*sc), int(26*sc)), 0, 0, 360, .35, -1)
    sh = np.maximum(sh, cv2.GaussianBlur(sh2, (0, 0), 18*sc))
    bg *= (1-sh[..., None])
    # 5. light wrap : la lumière du décor « mord » sur ses contours
    blur = cv2.GaussianBlur(bg, (0, 0), 14); edge = np.clip(A-cv2.erode(A, np.ones((9, 9), np.uint8)), 0, 1)
    edge = cv2.GaussianBlur(edge, (0, 0), 4)[..., None]*.75
    C = C*(1-edge)+blur*edge
    # 6. liseré chaud en haut de la pièce (éclairée par les lampes de la salle)
    top = np.clip(A-np.roll(A, int(10*sc), axis=0), 0, 1); top = cv2.GaussianBlur(top, (0, 0), 3)[..., None]*.45
    C = C+top*(GOLD-C*.4)
    out = bg*(1-A[..., None])+C*A[..., None]
    return out

def label(img, txt):
    cv2.putText(img, txt, (60, 150), cv2.FONT_HERSHEY_DUPLEX, 2.2, (0, 0, 0), 10, cv2.LINE_AA)
    cv2.putText(img, txt, (60, 150), cv2.FONT_HERSHEY_DUPLEX, 2.2, (255, 226, 160), 4, cv2.LINE_AA); return img
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', 'avant_apres.mp4'], stdin=subprocess.PIPE)
if STILL:
    for k in KEEP[1:4]:
        cv2.imwrite(f'still_{k}.jpg', cv2.cvtColor(np.clip(film(apres(k), k/FPS), 0, 255).astype(np.uint8)[1000:1900, 140:940], cv2.COLOR_RGB2BGR))
    sys.exit()
for name, fn in (('AVANT', avant), ('APRES', apres)):
    for k in range(N):
        img = film(fn(k), k/FPS); img = label(np.clip(img, 0, 255).astype(np.uint8).copy(), name)
        ff.stdin.write(img.tobytes())
        if k in (0, 150, 299): cv2.imwrite(f'{name}_{k}.jpg', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(name, 'ok', flush=True)
ff.stdin.close(); ff.wait()
