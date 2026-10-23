"""Micron : allée de data center néon (cyan / violet), sol miroir, travelling avant en boucle d'un pas de baie.
Aucune marque. usage : python dc.py <out.png|dossier> [rx ry samples f0 f1]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/amzn/b3d')
import amz
from objs import mat, box
from anim import lin, setup_motion
NF = 90; STEP = 1.25
CYAN = (0.0, 0.85, 1.0); VIOLET = (0.5, 0.15, 1.0); MAG = (1.0, 0.2, 0.75)

def build():
    sc = amz.base(); sc.view_settings.exposure = -0.2
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.004, 0.004, 0.012, 1)
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    amz.floor((0.012, 0.012, 0.02), 0.06)
    rack = mat('rack', (0.012, 0.013, 0.02), metal=0.7, rough=0.3)
    door = mat('mesh', (0.03, 0.032, 0.045), metal=0.9, rough=0.28)
    leds = [mat('lc', CYAN, emit=16), mat('lv', VIOLET, emit=16), mat('lm', MAG, emit=12), mat('lw', (0.8, 0.9, 1.0), emit=10)]
    neon_c = mat('nc', CYAN, emit=24); neon_v = mat('nv', (0.5, 0.12, 1.0), emit=11)
    random.seed(11); pat = []
    for r in range(18):
        for c in range(6):
            if random.random() < 0.5: pat.append((r, c, random.choices(leds, (5, 3, 1, 2))[0]))
    def join(objs_):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs_: o.select_set(True)
        bpy.context.view_layer.objects.active = objs_[0]; bpy.ops.object.join(); return bpy.context.object
    def inst(proto, loc):
        o = proto.copy(); o.location = loc; bpy.context.collection.objects.link(o); return o
    for side in (-1, 1):
        parts = [box('rack', (0.9, 1.18, 2.5), loc=(0, 0, 1.25), bevel=0.01, seg=1, m=rack),
                 box('top', (0.95, 1.2, 0.08), loc=(0, 0, 2.54), bevel=0, m=door),
                 # néon vertical sur l'arête avant de chaque baie
                 box('nv', (0.02, 0.025, 2.3), loc=(-side*0.455, -0.585, 1.25), bevel=0, m=neon_c if side < 0 else neon_v),
                 # chemin de câbles lumineux au plafond
                 box('tray', (0.35, STEP, 0.04), loc=(0, 0, 2.75), bevel=0, m=door),
                 box('fib', (0.04, STEP, 0.02), loc=(-0.08, 0, 2.72), bevel=0, m=neon_v), box('fib2', (0.03, STEP, 0.02), loc=(0.08, 0, 2.72), bevel=0, m=neon_c)]
        for (r, c, m) in pat: parts.append(box('led', (0.02, 0.035, 0.014), loc=(-side*0.452, -0.45+c*0.17, 0.3+r*0.12), bevel=0, m=m))
        for r in range(18): parts.append(box('slot', (0.005, 1.0, 0.008), loc=(-side*0.451, 0, 0.36+r*0.12), bevel=0, m=door))
        for p in parts:
            for md in list(p.modifiers):
                bpy.context.view_layer.objects.active = p; bpy.ops.object.modifier_apply(modifier=md.name)
        proto = join(parts); proto.location = (side*1.6, -6*STEP, 0)
        for k in range(-5, 40): inst(proto, (side*1.6, k*STEP, 0))
    # lignes néon au sol le long de l'allée
    for x, m in ((-1.05, neon_c), (1.05, neon_v)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 20, 0.006)); f = bpy.context.object; f.scale = (0.03, 60, 0.01); f.data.materials.append(m)
    box('ceil', (6, 90, 0.1), loc=(0, 20, 3.3), bevel=0, m=mat('c', (0.004, 0.004, 0.008), rough=0.9))
    cam = amz.camera((0.0, -1.0, 1.35), (0.0, 10, 1.25), 24)
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 7.0; cam.data.dof.aperture_fstop = 2.2
    # fond de l'allée : halo violet/cyan, lumières attachées au travelling
    l = amz.area((0, 22, 2.8), (math.radians(-90), 0, 0), 4, 700, (0.45, 0.35, 1.0))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 58, 1.5), rotation=(math.radians(90), 0, 0)); g = bpy.context.object; g.scale = (3.2, 3.4, 1); g.data.materials.append(mat('glow', (0.3, 0.2, 1.0), emit=1.6))
    l2 = amz.area((0, 6, 2.9), (0, 0, 0), 1.0, 110, (0.4, 0.8, 1.0), sy=12)
    setup_motion(sc)
    for o in (cam, l, l2):
        y = o.location.y
        o.keyframe_insert('location', frame=1); o.location.y = y+STEP; o.keyframe_insert('location', frame=1+NF); lin(o)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (720, 1280, 16)
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
