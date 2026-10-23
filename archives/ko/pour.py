"""Simulation physique du versement de cola dans un verre droit (MLS-MPM 3D, fluide faiblement compressible, Taichi CPU).
Unités de la scène Blender (verre : rayon intérieur 0,40, fond intérieur à z = 0,12, bord à z = 1,50 ; échelle ×10 du réel,
gravité ×10 pour garder le temps réel). Sortie : positions des particules + mousse, une image toutes les 1/30 s.
usage : python pour.py <dossier_sortie> [duree_s]"""
import sys, os, math, time
import numpy as np
import taichi as ti
ti.init(arch=ti.cpu, default_fp=ti.f32, cpu_max_num_threads=2)

OUT = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 4.6
os.makedirs(OUT, exist_ok=True)
X0, Y0 = -.55, -.55                 # coin du domaine
dx = 1.1/48; inv_dx = 1/dx
NX, NY, NZ = 48, 48, 76            # 1,10 × 1,10 × 1,74
RI, RO, ZF, ZR = .40, .425, .12, 1.50     # paroi intérieure / extérieure, fond intérieur, bord
G = 98.1                            # gravité ×10 (verre ×10)
PPC = 4; VP = dx**3/PPC; PM = VP    # volume et masse d'une particule (densité 1)
E = 5500.0                          # module de compressibilité (vitesse du son ≈ 74)
DT = 1.0e-4
SX, SY, SZ = .05, 0.0, 1.62         # centre de l'arrivée du filet
RS, V0 = .062, 12.0                 # rayon et vitesse du filet à l'arrivée
TARGET = math.pi*RI**2*(1.30-ZF)    # volume final (niveau ≈ 1,30, la mousse finit au bord)
NMAX = int(TARGET/VP*1.02)+2000
print('particules max', NMAX, flush=True)

x = ti.Vector.field(3, ti.f32, NMAX); v = ti.Vector.field(3, ti.f32, NMAX)
C = ti.Matrix.field(3, 3, ti.f32, NMAX); J = ti.field(ti.f32, NMAX)
gv = ti.Vector.field(3, ti.f32, (NX, NY, NZ)); gm = ti.field(ti.f32, (NX, NY, NZ))
n_act = ti.field(ti.i32, ())

@ti.func
def world(I):
    return ti.Vector([X0+I[0]*dx, Y0+I[1]*dx, I[2]*dx])

@ti.kernel
def p2g():
    for I in ti.grouped(gm): gv[I] = ti.Vector.zero(ti.f32, 3); gm[I] = 0.0
    for p in range(n_act[None]):
        Xp = (x[p]-ti.Vector([X0, Y0, 0.0]))*inv_dx
        base = int(Xp-.5); fx = Xp-base
        w = [.5*(1.5-fx)**2, .75-(fx-1)**2, .5*(fx-.5)**2]
        stress = -DT*4*E*VP*(J[p]-1)*inv_dx*inv_dx
        affine = ti.Matrix.identity(ti.f32, 3)*stress+PM*C[p]
        for i, j, k in ti.static(ti.ndrange(3, 3, 3)):
            off = ti.Vector([i, j, k]); dpos = (off-fx)*dx; wt = w[i][0]*w[j][1]*w[k][2]
            idx = base+off
            if 0 <= idx[0] < NX and 0 <= idx[1] < NY and 0 <= idx[2] < NZ:
                gv[idx] += wt*(PM*v[p]+affine@dpos); gm[idx] += wt*PM

@ti.kernel
def grid_op():
    for I in ti.grouped(gm):
        if gm[I] > 0:
            vv = gv[I]/gm[I]; vv[2] -= DT*G
            P = world(I); r = ti.sqrt(P[0]**2+P[1]**2)
            # verre : paroi (coquille) et fond épais ; glissement le long des surfaces
            if P[2] <= ZR and RI-dx*.9 <= r < RI and vv[0]*P[0]+vv[1]*P[1] > 0:     # marge d'une cellule : la paroi arrête le liquide avant de l'atteindre
                vr = (vv[0]*P[0]+vv[1]*P[1])/ti.max(r, 1e-6); vv[0] -= vr*P[0]/r; vv[1] -= vr*P[1]/r
            if P[2] <= ZR and RI <= r <= RO+dx*.5:
                n = ti.Vector([P[0], P[1], 0.0])/ti.max(r, 1e-6)
                if r < (RI+RO)*.5: n = -n
                if P[2] > ZR-dx and r > RI+dx*.3: n = ti.Vector([0.0, 0.0, 1.0])
                vn = vv.dot(n)
                if vn < 0: vv -= vn*n
            if r < RO and P[2] <= ZF+dx*.9:
                if vv[2] < 0: vv[2] = 0.0
                vv[0] *= .9; vv[1] *= .9
            if P[2] < dx*2 and vv[2] < 0: vv[2] = 0.0      # comptoir
            if (I[0] < 2 and vv[0] < 0) or (I[0] > NX-3 and vv[0] > 0): vv[0] = 0.0
            if (I[1] < 2 and vv[1] < 0) or (I[1] > NY-3 and vv[1] > 0): vv[1] = 0.0
            if I[2] > NZ-3 and vv[2] > 0: vv[2] = 0.0
            gv[I] = vv

@ti.kernel
def g2p():
    for p in range(n_act[None]):
        Xp = (x[p]-ti.Vector([X0, Y0, 0.0]))*inv_dx
        base = int(Xp-.5); fx = Xp-base
        w = [.5*(1.5-fx)**2, .75-(fx-1)**2, .5*(fx-.5)**2]
        nv = ti.Vector.zero(ti.f32, 3); nC = ti.Matrix.zero(ti.f32, 3, 3)
        for i, j, k in ti.static(ti.ndrange(3, 3, 3)):
            off = ti.Vector([i, j, k]); dpos = off-fx; wt = w[i][0]*w[j][1]*w[k][2]
            idx = base+off
            if 0 <= idx[0] < NX and 0 <= idx[1] < NY and 0 <= idx[2] < NZ:
                g = gv[idx]; nv += wt*g; nC += 4*inv_dx*wt*g.outer_product(dpos)
        v[p] = nv; x[p] += DT*nv; J[p] *= 1+DT*nC.trace(); C[p] = nC
        # sécurité : une particule entrée dans le verre est replacée contre la paroi
        P = x[p]; r = ti.sqrt(P[0]**2+P[1]**2)
        if P[2] <= ZR and RI-.004 < r < (RI+RO)*.5:
            s = (RI-.004)/r; x[p][0] *= s; x[p][1] *= s
            vr = (v[p][0]*P[0]+v[p][1]*P[1])/r
            if vr > 0: v[p][0] -= vr*P[0]/r; v[p][1] -= vr*P[1]/r
        if r < RI and P[2] < ZF+.003: x[p][2] = ZF+.003; v[p][2] = ti.max(v[p][2], 0.0)
        J[p] = ti.min(ti.max(J[p], .6), 1.2)
        for d in ti.static(range(3)):
            lo = (X0, Y0, 0.0)[d]+dx*1.5; hi = (X0, Y0, 0.0)[d]+(NX, NY, NZ)[d]*dx-dx*1.5
            x[p][d] = ti.min(ti.max(x[p][d], lo), hi)

@ti.kernel
def emit(n: ti.i32, rs: ti.f32, t: ti.f32):
    for q in range(n):
        p = n_act[None]+q
        a = ti.random()*2*math.pi; rr = rs*ti.sqrt(ti.random())
        ox = .006*ti.sin(t*7.0); oy = .004*ti.sin(t*5.3+1)          # léger tremblement du filet
        x[p] = ti.Vector([SX+ox+rr*ti.cos(a), SY+oy+rr*ti.sin(a), SZ-ti.random()*V0*DT])
        v[p] = ti.Vector([0.0, 0.0, -V0]); C[p] = ti.Matrix.zero(ti.f32, 3, 3); J[p] = 1.0

# ---------- mousse (bulles d'air entraînées par l'impact, qui remontent et forment le col) ----------
rng = np.random.default_rng(5)
F = dict(p=np.zeros((0, 3), np.float32), u=np.zeros(0, np.float32), life=np.zeros(0, np.float32), age=np.zeros(0, np.float32), r=np.zeros(0, np.float32), id=np.zeros(0, np.int64))
next_id = [0]
def surface_map(P):
    """hauteur du liquide par colonne : première cellule vide en montant depuis le fond, puis médiane large (exclut le filet)"""
    from scipy.ndimage import median_filter, gaussian_filter
    occ = np.zeros((NX, NY, NZ), np.int32)
    i = ((P[:, 0]-X0)*inv_dx).astype(int).clip(0, NX-1); j = ((P[:, 1]-Y0)*inv_dx).astype(int).clip(0, NY-1); k = (P[:, 2]*inv_dx).astype(int).clip(0, NZ-1)
    np.add.at(occ, (i, j, k), 1)
    k0 = int(ZF*inv_dx)+2; full = occ[:, :, k0:] >= 1
    first_empty = np.argmin(full, axis=2)            # index de la première cellule vide
    allfull = full.all(axis=2); first_empty[allfull] = full.shape[2]
    h = ((k0+first_empty)*dx).astype(np.float32)
    h = gaussian_filter(median_filter(h, 11), 1.0)
    return h
def sample(h, P):
    i = ((P[:, 0]-X0)*inv_dx).clip(0, NX-1.001); j = ((P[:, 1]-Y0)*inv_dx).clip(0, NY-1.001)
    i0, j0 = i.astype(int), j.astype(int); fi, fj = i-i0, j-j0
    return (h[i0, j0]*(1-fi)*(1-fj)+h[i0+1, j0]*fi*(1-fj)+h[i0, j0+1]*(1-fi)*fj+h[i0+1, j0+1]*fi*fj)
def foam_step(P, V, h, fdt, pouring, thick_prev):
    global F
    # naissance : particules rapides sous la surface, dans la zone d'impact
    if pouring:
        r2 = P[:, 0]**2+P[:, 1]**2; spd = np.linalg.norm(V, axis=1)
        cand = np.where((r2 < (RI-.02)**2) & (P[:, 2] < sample(h, P)) & (P[:, 2] > ZF) & (spd > 5.0))[0]
        nb = min(len(cand), int(9000*fdt))
        if nb > 0:
            pick = rng.choice(cand, nb, replace=False)
            pos = P[pick]+rng.normal(0, .01, (nb, 3)).astype(np.float32)
            F['p'] = np.vstack([F['p'], pos]); F['u'] = np.concatenate([F['u'], rng.random(nb).astype(np.float32)])
            F['life'] = np.concatenate([F['life'], rng.uniform(2.0, 5.5, nb).astype(np.float32)]); F['age'] = np.concatenate([F['age'], np.zeros(nb, np.float32)])
            F['r'] = np.concatenate([F['r'], (rng.lognormal(np.log(.0085), .45, nb)).clip(.004, .024).astype(np.float32)])
            F['id'] = np.concatenate([F['id'], np.arange(next_id[0], next_id[0]+nb)]); next_id[0] += nb
    if len(F['u']) == 0: return thick_prev
    p = F['p']; F['age'] += fdt
    # épaisseur du col : volume de mousse par colonne
    i = ((p[:, 0]-X0)*inv_dx).astype(int).clip(0, NX-1); j = ((p[:, 1]-Y0)*inv_dx).astype(int).clip(0, NY-1)
    hs = sample(h, p); top = p[:, 2] >= hs-.03
    vol = np.zeros((NX, NY), np.float32); np.add.at(vol, (i[top], j[top]), (4/3*np.pi*F['r'][top]**3)/.55)
    from scipy.ndimage import gaussian_filter
    thick = gaussian_filter(vol/(dx*dx), 2.0)
    thick = np.minimum(thick, np.maximum(ZR-.008-h, 0)); thick = .6*thick_prev+.4*thick if thick_prev is not None else thick
    # mouvement : les bulles sous la surface remontent ; en surface elles s'étalent et flottent
    below = ~top
    p[below, 2] += fdt*(1.8+F['r'][below]*60)
    p[below, :2] += fdt*rng.normal(0, .25, (below.sum(), 2)).astype(np.float32)
    # étalement depuis la zone d'impact, vers les bords du verre
    d = p[:, :2]-np.array([SX, SY], np.float32); dn = np.linalg.norm(d, axis=1, keepdims=True)+1e-6
    spread = (.55 if pouring else .12)*np.exp(-dn/.25)
    p[top, :2] += fdt*(d[top]/dn[top])*spread[top]
    rr = np.linalg.norm(p[:, :2], axis=1, keepdims=True); over = rr[:, 0] > RI-F['r']-.003
    p[over, :2] *= ((RI-F['r'][over, None]-.003)/rr[over])
    ft = sample(thick, p); hs = sample(h, p)
    p[top, 2] = hs[top]+F['u'][top]*ft[top]+F['r'][top]*.6
    F['p'] = p
    alive = F['age'] < F['life']
    for k in F: F[k] = F[k][alive]
    return thick

# ---------- boucle ----------
FPS_OUT = 30; steps_per = int(round(1/(FPS_OUT*DT))); frames = int(DUR*FPS_OUT)
acc = 0.0; stopped_at = None; t = 0.0; thick = None; t0 = time.time()
rate = math.pi*RS**2*V0/VP          # particules par seconde
stream_log = []
for fr in range(frames+1):
    for s in range(steps_per if fr > 0 else 0):
        t += DT
        if stopped_at is None:
            nleft = NMAX-2000-n_act[None]
            taper = 1.0
            if nleft*VP < rate*VP*.25: taper = max(.25, nleft/(rate*.25))      # le filet s'amincit avant de s'arrêter
            acc += rate*DT*taper; n = min(int(acc), nleft)
            if n > 0: emit(n, RS*math.sqrt(taper), t); n_act[None] += n; acc -= n
            if nleft <= 0: stopped_at = t
        p2g(); grid_op(); g2p()
    n = n_act[None]
    P = x.to_numpy()[:n]; V = v.to_numpy()[:n]
    h = surface_map(P)
    thick = foam_step(P, V, h, 1/FPS_OUT, stopped_at is None or t-stopped_at < .2, thick)
    stream_log.append((fr, 1 if stopped_at is None else 0))
    np.savez_compressed(f'{OUT}/f{fr:04d}.npz', x=P.astype(np.float16), fp=F['p'].astype(np.float16), fr=(F['r']*np.clip((F['life']-F['age'])/.35, 0, 1)).astype(np.float16), fid=F['id'], stream=stopped_at is None)
    if fr % 10 == 0: print('frame', fr, 'part', n, 'mousse', len(F['u']), 'niveau', round(float(np.median(h[20:28, 20:28])), 3), round(time.time()-t0), 's', flush=True)
open(f'{OUT}/done', 'w').write('ok')
