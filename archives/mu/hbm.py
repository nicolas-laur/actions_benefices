"""Produit phare : mémoire HBM (puces empilées) autour d'un processeur IA, sur interposeur et substrat.
Modèle générique (aucun logo, aucun marquage), rendu sur fond transparent pour être composé devant le data center.
Animation en boucle : rotation lente + la pile héros se déploie en vue éclatée puis se referme.
usage : python hbm.py <out.png|dossier> [rx ry samples f0 f1]"""
import bpy, bmesh, math, os, sys, time
sys.path.insert(0, '/home/claude/visa/b3d')
import objs
from objs import mat
NF = 120

def node_mat(name, base, metal, rough, film=0.0, coat=0.0, grid=None):
    m = mat(name, base, metal=metal, rough=rough); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    if film: b.inputs['Thin Film Thickness'].default_value = film; b.inputs['Thin Film IOR'].default_value = 1.6
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = .05
    if grid:   # motif de circuit : grille de cellules qui module rugosité et couleur (aspect « wafer »)
        tc = nt.nodes.new('ShaderNodeTexCoord'); br = nt.nodes.new('ShaderNodeTexBrick')
        br.inputs['Scale'].default_value = grid; br.inputs['Mortar Size'].default_value = .03; br.offset = 0; br.squash = 1
        br.inputs['Color1'].default_value = (*base, 1); br.inputs['Color2'].default_value = tuple(min(1, v*1.18) for v in base)+(1,); br.inputs['Mortar'].default_value = (.6, .5, .3, 1)
        nt.links.new(tc.outputs['Object'], br.inputs['Vector']); nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[3].default_value = rough*.6; mr.inputs[4].default_value = rough*1.8
        nt.links.new(br.outputs['Fac'], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    return m

def slab(name, sx, sy, sz, loc, m, bevel=.004, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name; o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def build():
    sc = objs.reset(); sc.render.film_transparent = True
    sc.view_settings.exposure = 0.0
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.004, 0.005, 0.01, 1); w.inputs[1].default_value = 1.0
    sub = node_mat('sub', (0.010, 0.022, 0.018), 0.0, .38, coat=.6)
    gold = node_mat('gold', (1.0, 0.70, 0.30), 1.0, .18)
    inter = node_mat('inter', (0.22, 0.24, 0.28), 0.9, .14, film=420, grid=40)
    gpu = node_mat('gpu', (0.025, 0.03, 0.045), 0.7, .07, film=520, grid=48)
    dram = node_mat('dram', (0.10, 0.11, 0.13), 0.85, .16, film=380)
    cap = node_mat('cap', (0.05, 0.055, 0.07), 0.7, .10, film=560, grid=60)
    root = bpy.data.objects.new('root', None); bpy.context.collection.objects.link(root)
    # substrat avec rangées de pastilles dorées sur les bords
    slab('sub', 4.2, 3.2, .12, (0, 0, -.06), sub, .02, root)
    for i in range(36):
        for y in (-1.52, 1.52): slab('pad', .06, .1, .012, (-1.98+i*.113, y, .006), gold, 0, root)
    for i in range(26):
        for x in (-2.02, 2.02): slab('pad', .1, .06, .012, (x, -1.42+i*.113, .006), gold, 0, root)
    # composants passifs
    for i in range(14):
        for y in (-1.25, 1.25): slab('cap_', .12, .07, .06, (-1.6+i*.24, y, .03), node_mat(f'p{i}{y}', (.35, .25, .15), .2, .4), .008, root)
    slab('inter', 3.3, 2.1, .06, (0, 0, .03), inter, .006, root)
    slab('gpu', 1.35, 1.65, .14, (0, 0, .13), gpu, .008, root)
    # piles HBM : 4 de chaque côté, 12 puces + couche de liaison dorée entre chaque
    hero = None; stacks = []
    for sx in (-1, 1):
        for k in range(4):
            x = sx*1.12; y = -.75+k*.5
            st = bpy.data.objects.new(f'stack{sx}{k}', None); bpy.context.collection.objects.link(st); st.parent = root; st.location = (x, y, .06)
            layers = []
            for j in range(12):
                d = slab('d', .62, .42, .028, (0, 0, .02+j*.036), dram, .003, st)
                b_ = slab('b', .58, .38, .006, (0, 0, .037+j*.036), gold, 0, st); layers.append((d, b_, j))
            top = slab('top', .62, .42, .05, (0, 0, .02+12*.036+.012), cap, .004, st); layers.append((top, None, 12))
            stacks.append((st, layers))
            if sx == -1 and k == 1: hero = (st, layers)
    # lumière : clé douce, contre-jours cyan et violet, panneaux de reflet
    def area(loc, rot, size, e, col_, sy=None):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = e; l.data.color = col_
        if sy: l.data.shape = 'RECTANGLE'; l.data.size_y = sy
        return l
    for l in (area((0, -3, 6), (math.radians(28), 0, 0), 5, 350, (.9, .95, 1.0), sy=2),
              area((-5, 4, 2.2), (math.radians(70), 0, math.radians(-130)), 2, 2600, (0.0, .8, 1.0)),
              area((5, 4, 2.2), (math.radians(70), 0, math.radians(130)), 2, 2600, (.55, .2, 1.0)),
              area((0, -6, 1.2), (math.radians(80), 0, 0), 6, 120, (.6, .8, 1.0), sy=.6)): l.visible_glossy = False
    sys.path.insert(0, '/home/claude/visa/b3d'); from vscene import softbox
    softbox('sb_top', (0, 9.5, 4.6), (math.radians(116), 0, 0), 9, 2.0, (.75, .85, 1.0), sy=3.5)
    softbox('sb_front', (0, -6.5, -1.4), (math.radians(-64), 0, 0), 8, 1.6, (.5, .7, 1.0), sy=1.5)
    softbox('sb_c', (-4.5, 1.5, 2.5), (math.radians(80), 0, math.radians(-110)), .5, 14, (0.0, .85, 1.0), sy=5)
    softbox('sb_v', (4.5, 1.5, 2.5), (math.radians(80), 0, math.radians(110)), .5, 14, (.6, .25, 1.0), sy=5)
    bpy.ops.object.camera_add(location=(0.6, -8.4, 3.9)); cam = bpy.context.object; cam.data.lens = 58
    look = (-.15, .1, .25); d = [look[i]-cam.location[i] for i in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0])-math.pi/2)
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = hero[0]; cam.data.dof.aperture_fstop = 2.4; sc.camera = cam
    # boucle : rotation lente de l'ensemble + vue éclatée de la pile héros
    for f in range(1, NF+2):
        u = (f-1)/NF
        root.rotation_euler = (0, 0, math.radians(-14)+math.radians(10)*math.sin(2*math.pi*u)); root.keyframe_insert('rotation_euler', frame=f)
        e = (1-math.cos(2*math.pi*u))/2; e = e*e*(3-2*e)
        st, layers = hero
        st.location.z = .06+.22*e; st.keyframe_insert('location', frame=f)
        for (dd, bb, j) in layers:
            dz = j*.065*e
            dd.location.z = .02+j*.036+(.012 if j == 12 else 0)+dz; dd.keyframe_insert('location', index=2, frame=f)
            if bb: bb.location.z = .037+j*.036+dz+.02*e; bb.keyframe_insert('location', index=2, frame=f)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (900, 900, 24)
    sc = build(); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[4]) if len(a) > 4 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[4]) if len(a) > 4 else 1; f1 = int(a[5]) if len(a) > 5 else NF
        st = int(a[6]) if len(a) > 6 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
