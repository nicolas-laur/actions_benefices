"""Intel : processeur générique (aucune marque) sur une carte, pistes parcourues d'impulsions de courant.
deux plans en boucle :  cpu = orbite lente autour du processeur ;  net = travelling au ras des pistes, comme dans un réseau.
usage : python chip.py <cpu|net> <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/aapl/b3d'); sys.path.insert(0, '/home/claude/amzn/b3d')
import objs
from objs import mat, box
NF = 120; TAU = 2*math.pi; TILE = 4.0

def pulse_mat(name, axis='Y', period=1.0, speed_cycles=1, base=(0.05, 0.06, 0.08), glow=(0.1, 0.85, 1.0), strength=30):
    """cuivre doré + impulsions lumineuses qui courent le long de l'axe (bouclées sur NF images)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Metallic'].default_value = 1; b.inputs['Roughness'].default_value = .25
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Object'], sep.inputs[0])
    add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'; L(sep.outputs[axis], add.inputs[0])
    add.inputs[1].default_value = 0; add.inputs[1].keyframe_insert('default_value', frame=1)
    add.inputs[1].default_value = -period*speed_cycles; add.inputs[1].keyframe_insert('default_value', frame=1+NF)
    fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = period
    L(add.outputs[0], dv.inputs[0]); L(dv.outputs[0], fr.inputs[0])
    rmp = nt.nodes.new('ShaderNodeMapRange'); rmp.inputs[1].default_value = .9; rmp.inputs[2].default_value = 1.0; L(fr.outputs[0], rmp.inputs[0])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0; L(rmp.outputs[0], pw.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength; L(pw.outputs[0], mul.inputs[0])
    b.inputs['Emission Color'].default_value = (*glow, 1)
    bias = nt.nodes.new('ShaderNodeMath'); bias.operation = 'ADD'; bias.inputs[1].default_value = 0.06
    L(mul.outputs[0], bias.inputs[0]); L(bias.outputs[0], b.inputs['Emission Strength'])
    ad = nt.animation_data
    if ad and ad.action:
        for fc in getattr(ad.action, 'fcurves', []):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        for layer in getattr(ad.action, 'layers', []):
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    return m

def pcb_mat():
    m = bpy.data.materials.new('pcb'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 90; n.inputs['Detail'].default_value = 4
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (0.004, 0.004, 0.008, 1); r.color_ramp.elements[1].color = (0.012, 0.010, 0.022, 1)
    L(n.outputs['Fac'], r.inputs['Fac']); L(r.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .38; b.inputs['Coat Weight'].default_value = .6
    return m

def trace(x0, y0, pts, w, m, z=0.004):
    """piste plate qui suit une polyligne (segments à 0°/45°/90°)"""
    import bmesh
    me = bpy.data.meshes.new('tr'); bm = bmesh.new(); P = [(x0, y0)]+pts
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        dx, dy = bx-ax, by-ay; l = math.hypot(dx, dy)
        if l < 1e-6: continue
        nx, ny = -dy/l*w/2, dx/l*w/2
        vs = [bm.verts.new((ax+nx, ay+ny, z)), bm.verts.new((bx+nx, by+ny, z)), bm.verts.new((bx-nx, by-ny, z)), bm.verts.new((ax-nx, ay-ny, z))]
        bm.faces.new(vs)
    for (bx, by) in P[1:-1]:   # pastilles aux coudes
        bmesh.ops.create_circle(bm, cap_ends=True, radius=w*.5, segments=12, matrix=__import__('mathutils').Matrix.Translation((bx, by, z)))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('tr', me); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def via(x, y, r, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=.01, location=(x, y, .005)); o = bpy.context.object; o.data.materials.append(m); return o

def build(shot):
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.003, 0.004, 0.006, 1); w.inputs[1].default_value = 1
    sc.view_settings.exposure = -0.4
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    pcb = pcb_mat(); gold = mat('gold', (0.8, 0.55, 0.2), metal=1, rough=.25)
    rnd = random.Random(4)
    if shot == 'cpu':
        bpy.ops.mesh.primitive_plane_add(size=30); p = bpy.context.object; p.data.materials.append(pcb)
        pm = [pulse_mat('px', 'X', .8, 3), pulse_mat('py', 'Y', .8, 3, glow=(1.0, 0.15, 0.75)), pulse_mat('px2', 'X', 1.1, 2, glow=(1.0, 0.15, 0.75)), pulse_mat('py2', 'Y', 1.1, 2)]
        # processeur : substrat + capot métal brossé + petits composants
        box('sub', (1.7, 1.7, .06), loc=(0, 0, .03), bevel=.01, seg=2, m=mat('subm', (0.04, 0.12, 0.08), rough=.45))
        ihs = mat('ihs', (0.08, 0.085, 0.1), metal=1, rough=.18)
        neon_c = mat('nc', (0.1, 0.85, 1.0), emit=40); neon_m = mat('nm', (1.0, 0.15, 0.75), emit=30)
        for (w_, d_, mm, zz) in ((1.24, .012, neon_c, .155), (1.74, .01, neon_m, .065)):
            for sx, sy, lx, ly in ((0, 1, w_, d_), (0, -1, w_, d_), (1, 0, d_, w_), (-1, 0, d_, w_)):
                box('ne', (lx, ly, .012), loc=(sx*w_/2, sy*w_/2, zz), bevel=0, m=mm)
        core = mat('core', (0.1, 0.85, 1.0), emit=6); cn = core.node_tree.nodes['Principled BSDF']
        for f, v in ((1, 2), (31, 14), (61, 2), (91, 14), (121, 2)):
            cn.inputs['Emission Strength'].default_value = v; cn.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
        bpy.ops.mesh.primitive_plane_add(size=.5, location=(0, 0, .1665)); g_ = bpy.context.object; g_.data.materials.append(core)
        for i in range(5):
            box('gl', (.6, .006, .004), loc=(0, -.33+i*.165, .167), bevel=0, m=neon_c)
        box('ihs', (1.2, 1.2, .09), loc=(0, 0, .105), bevel=.03, seg=4, m=ihs)
        box('ihs2', (1.0, 1.0, .02), loc=(0, 0, .155), bevel=.01, seg=3, m=ihs)
        cap = mat('cap', (0.25, 0.18, 0.1), rough=.5)
        for i in range(14):
            for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                t = -0.7+i*.108; x, y = (sx*.78, t) if sx else (t, sy*.78)
                box('c', (.05, .03, .025) if sx else (.03, .05, .025), loc=(x, y, .07), bevel=0, m=cap if i % 3 else gold)
        # socket et pistes qui rayonnent vers l'extérieur
        box('sock', (2.3, 2.3, .03), loc=(0, 0, .015), bevel=.01, seg=2, m=mat('sock', (0.012, 0.012, 0.014), rough=.5))
        for side in range(4):
            for k in range(26):
                off = -1.0+k*.08; L_ = rnd.uniform(3, 9); bend = rnd.uniform(.3, 1.4); d = rnd.choice((-1, 1))
                pts = [(1.2+bend, off), (1.2+bend+.4, off+d*.4), (1.2+L_, off+d*.4)]
                ang = side*math.pi/2; ca, sa = math.cos(ang), math.sin(ang)
                P = [(x*ca-y*sa, x*sa+y*ca) for x, y in [(1.18, off)]+pts]
                o = trace(P[0][0], P[0][1], P[1:], .025, pm[(side % 2)+2*(k % 2)])
                ex, ey = P[-1]; via(ex, ey, .04, gold)
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 40
        cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 5.0; cam.data.dof.aperture_fstop = 2.0
        tgt = bpy.data.objects.new('tgt', None); bpy.context.collection.objects.link(tgt); tgt.location = (0, 0, .1)
        tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
        for f in range(1, NF+1, 2):
            u = TAU*(f-1)/NF; R = 4.2
            ang = .32*math.sin(u); cam.location = (R*math.sin(ang), -R*math.cos(ang), 3.3+.18*math.sin(u+1.0)); cam.keyframe_insert('location', frame=f)
        # lumières : clé douce, contre-jour cyan, reflet qui glisse sur le capot
        objs_area = __import__('amz').area
        objs_area((0, 0, 6), (0, 0, 0), 4, 90, (.7, .8, 1)); objs_area((0, -3, 3), (math.radians(45), 0, 0), 5, 120, (.6, .9, 1)); objs_area((-4, 4, 2), (math.radians(-60), 0, math.radians(-135)), 3, 700, (.1, .8, 1))
        objs_area((4, -3, 1.5), (math.radians(70), 0, math.radians(50)), 3, 600, (1, .15, .7))
    else:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 60, 0)); p = bpy.context.object; p.scale = (14, 160, 1); pcb.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0; pcb.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .7; p.data.materials.append(pcb)
        pm = pulse_mat('pn', 'Y', TILE/4, 4, strength=30); pm2 = pulse_mat('pn2', 'Y', TILE/2, 4, glow=(1.0, .15, .75), strength=26)
        # couloir de pistes parallèles qui se ramifient, répété tous les TILE (boucle parfaite)
        lanes = [(-2.4+i*.16) for i in range(31)]
        for k in range(-3, 30):
            y0 = k*TILE
            for i, x in enumerate(lanes):
                r_ = random.Random(i*100+(k % 2))
                if abs(x) < .35: continue
                if r_.random() < .25:
                    d = 1 if x > 0 else -1; yb = y0+r_.uniform(.5, 2.5)
                    trace(x, y0, [(x, yb), (x+d*.16, yb+.16), (x+d*.16, y0+TILE)], .035, pm if i % 3 else pm2)
                else:
                    trace(x, y0, [(x, y0+TILE)], .035, pm if i % 3 else pm2)
                if r_.random() < .2: via(x, y0+r_.uniform(0, TILE), .05, gold)
            # petits composants de part et d'autre du couloir
            for s in (-1, 1):
                for j in range(3):
                    box('chip', (.5, .4, .12), loc=(s*rnd.uniform(2.8, 3.6), y0+j*1.3+.4, .06), bevel=.01, seg=2, m=mat('ic', (0.02, 0.02, 0.022), rough=.4))
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 22
        cam.rotation_euler = (math.radians(74), 0, 0); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 2.2; cam.data.dof.aperture_fstop = 2.2
        for f in (1, 1+NF):
            cam.location = (0, (f-1)/NF*TILE, .9); cam.keyframe_insert('location', frame=f)
        __import__('anim').lin(cam)
        a = __import__('amz').area
        a((0, 14, 3), (0, 0, 0), 6, 80, (.6, .7, 1)); a((-4, 10, 1.2), (math.radians(80), 0, math.radians(-90)), 4, 160, (1, .15, .7)); a((4, 10, 1.2), (math.radians(80), 0, math.radians(90)), 4, 160, (.1, .8, 1))
        l = a((0, 1.5, 2.5), (0, 0, 0), 2, 120, (1, .9, .8))
        for f in (1, 1+NF): l.location.y = 1.5+(f-1)/NF*TILE; l.keyframe_insert('location', frame=f)
        __import__('anim').lin(l)
        sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.008, 0.004, 0.02, 1)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; shot, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (540, 960, 20)
    sc = build(shot); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[5]) if len(a) > 5 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else NF; st = int(a[7]) if len(a) > 7 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
