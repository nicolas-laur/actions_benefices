"""Particules du versement -> surface du liquide (champ de densité lissé + marching cubes), recollée au verre.
usage : python mesh.py <dossier_sim> <dossier_mesh> [f0 f1]"""
import sys, os, numpy as np
from scipy.ndimage import gaussian_filter
from scipy import sparse
from skimage.measure import marching_cubes
SIM, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
X0, Y0, DXS = -.55, -.55, 1.1/48
H = DXS/2; NX, NY, NZ = 96, 96, 152
RI, ZF, ZR = .40, .12, 1.50
def build(P):
    g = np.zeros((NX+1, NY+1, NZ+1), np.float32)
    q = np.empty_like(P); q[:, 0] = (P[:, 0]-X0)/H; q[:, 1] = (P[:, 1]-Y0)/H; q[:, 2] = P[:, 2]/H
    q = q.clip(0, [NX-1.001, NY-1.001, NZ-1.001]); b = q.astype(int); f = q-b
    for dx_ in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx_ else 1-f[:, 0])*(f[:, 1] if dy else 1-f[:, 1])*(f[:, 2] if dz else 1-f[:, 2])
                np.add.at(g, (b[:, 0]+dx_, b[:, 1]+dy, b[:, 2]+dz), w)
    g = gaussian_filter(g, 1.45)
    g[0], g[-1], g[:, 0], g[:, -1], g[:, :, 0], g[:, :, -1] = 0, 0, 0, 0, 0, 0
    if g.max() < .25: return None
    v, fa, _, _ = marching_cubes(g, .17, spacing=(H, H, H))
    v[:, 0] += X0; v[:, 1] += Y0
    return v.astype(np.float32), fa.astype(np.int32)
def taubin(v, f, it=10, lam=.55, mu=-.58):
    n = len(v); e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    A = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)); A = ((A+A.T) > 0).astype(np.float32).tocsr()
    deg = np.asarray(A.sum(1)).ravel()+1e-9
    for _ in range(it):
        for k in (lam, mu): v = v+k*(A@v/deg[:, None]-v)
    return v
def stick(v):
    """recolle le liquide à la paroi et au fond intérieurs du verre (pas de lame d'air)"""
    r = np.hypot(v[:, 0], v[:, 1]); inside = (v[:, 2] < ZR) & (r < RI+.08)
    wall = inside & (r > RI-.04); s = (RI-.0015)/np.maximum(r[wall], 1e-6); v[wall, 0] *= s; v[wall, 1] *= s
    flo = inside & (v[:, 2] < ZF+.035) & (r < RI); v[flo, 2] = ZF+.0008
    return v
fr = sorted(k for k in os.listdir(SIM) if k.endswith('.npz'))
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 10**6)
for k in fr:
    i = int(k[1:5])
    if not a <= i <= b or os.path.exists(f'{OUT}/{k}'): continue
    d = np.load(f'{SIM}/{k}'); P = d['x'].astype(np.float32)
    r = build(P) if len(P) > 50 else None
    if r is None: v, fa = np.zeros((0, 3), np.float32), np.zeros((0, 3), np.int32)
    else: v, fa = r; v = stick(taubin(v, fa))
    # le filet au-dessus de la surface est remplacé par un cylindre lisse dans Blender : on retire sa partie maillée
    ra = np.hypot(P[:, 0]-.05, P[:, 1]); ring = (ra > .13) & (ra < .32) & (P[:, 2] < ZR)
    hs = float(np.percentile(P[ring, 2], 90)) if ring.sum() > 50 else ZF
    if bool(d['stream']) and len(v):
        rv = np.hypot(v[:, 0]-.05, v[:, 1]); cut = (rv < .11) & (v[:, 2] > hs+.03)
        fa = fa[~cut[fa].all(1)]
    # mousse : chaque bulle simulée devient un petit amas de bulles fines (tirage fixe par bulle : pas de scintillement)
    fp, frr, fid = d['fp'].astype(np.float32), d['fr'].astype(np.float32), d['fid']
    K = 7; rs = np.random.default_rng(fid[:, None]*K+np.arange(K)[None, :] if len(fid) else 0) if False else None
    if len(fid):
        u = ((fid[:, None]*2654435761+np.arange(K)[None, :]*40503) % 1000003)/1000003.0
        a1, a2, a3 = (u*7.31) % 1, (u*13.7) % 1, (u*29.3) % 1
        th = a1*2*np.pi; ph = np.arccos(2*a2-1); rad = frr[:, None]*1.3*a3**(1/3)
        off = np.stack([rad*np.sin(ph)*np.cos(th), rad*np.sin(ph)*np.sin(th), rad*np.cos(ph)*.6], -1)
        sub = (frr[:, None]*(.32+.3*((u*51.1) % 1)))
        fp = (fp[:, None, :]+off).reshape(-1, 3).astype(np.float32); frr = sub.reshape(-1).astype(np.float32)
        r_ = np.hypot(fp[:, 0], fp[:, 1]); o_ = r_ > RI-frr-.002; fp[o_, :2] *= ((RI-frr[o_]-.002)/r_[o_])[:, None]
    if len(fp):   # col de mousse plus fin et plus serré
        ab = fp[:, 2] > hs; fp[ab, 2] = hs+(fp[ab, 2]-hs)*.42
    np.savez(f'{OUT}/{k}', v=v, f=fa, fp=fp, fr=frr, stream=d['stream'], hs=hs)
    print(k, len(v), len(fa), flush=True)
