"""Fond Bitcoin : pluie de pièces ₿ en or au ralenti, flou de profondeur, bokeh chaud (même recette que la pluie de frites).
Boucle parfaite : chaque pièce descend exactement d'une hauteur de boucle avec un nombre entier de tours.
usage : python rain.py <out_dir|png> [rx ry samples f0 f1]"""
import bpy, bmesh, math, random, os, sys, time
sys.path.insert(0, '/home/claude/visa/b3d'); sys.path.insert(0, '/home/claude/btc')
import objs
from objs import mat
NF = 150; SPAN = 13.0

def gold(name, tint, rough):
    m = mat(name, tint, metal=1.0, rough=rough); return m

def make_coin(g_body, g_relief):
    """pièce : disque cannelé + anneau + ₿ en relief des deux côtés, fusionnés en un seul maillage"""
    me = bpy.data.meshes.new('c'); bm = bmesh.new(); n = 240; R, D, dep = 1.0, 0.16, 0.014
    pts = [((R-(dep if i % 2 else 0))*math.cos(2*math.pi*i/n), (R-(dep if i % 2 else 0))*math.sin(2*math.pi*i/n)) for i in range(n)]
    bot = [bm.verts.new((x, y, -D/2)) for x, y in pts]; top = [bm.verts.new((x, y, D/2)) for x, y in pts]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(n): bm.faces.new((bot[i], bot[(i+1) % n], top[(i+1) % n], top[i]))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('coin', me); bpy.context.collection.objects.link(o)
    o.data.materials.append(g_body); o.data.materials.append(g_relief)
    parts = [o]
    for s in (1, -1):
        cu = bpy.data.curves.new('b', 'FONT'); cu.body = '₿'; cu.font = bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
        cu.size = 1.05; cu.extrude = 0.02; cu.bevel_depth = 0.008; cu.bevel_resolution = 2; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        t = bpy.data.objects.new('g', cu); bpy.context.collection.objects.link(t); t.location = (0, 0, s*.085)
        t.rotation_euler = (0 if s > 0 else math.pi, 0, math.radians(-14 if s > 0 else 14))
        bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = t; t.select_set(True); bpy.ops.object.convert(target='MESH')
        t.data.materials.clear(); t.data.materials.append(g_body); t.data.materials.append(g_relief)
        for p in t.data.polygons: p.material_index = 1
        parts.append(t)
        # anneau en relief
        bpy.ops.mesh.primitive_torus_add(major_radius=.9, minor_radius=.035, major_segments=160, minor_segments=8, location=(0, 0, s*.075)); r = bpy.context.object
        r.scale = (1, 1, .5); bpy.ops.object.transform_apply(scale=True); r.data.materials.append(g_body); r.data.materials.append(g_relief)
        for p in r.data.polygons: p.material_index = 1
        parts.append(r)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.join()
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.01; bv.segments = 2; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(60)
    for p in o.data.polygons: p.use_smooth = False
    o.scale = (.34, .34, .34); bpy.ops.object.transform_apply(scale=True)
    return o

def build():
    random.seed(21)
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.010, 0.006, 0.003, 1); w.inputs[1].default_value = 1.0
    sc.view_settings.exposure = -0.1
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    gb = gold('gb', (0.95, 0.62, 0.22), .24); gr = gold('gr', (1.0, 0.72, 0.30), .1)
    proto = make_coin(gb, gr)
    coins = []
    for i in range(85):
        o = bpy.data.objects.new(f'c{i}', proto.data); bpy.context.collection.objects.link(o)
        depth = random.uniform(-4, 13)
        x = random.uniform(-1, 1)*0.13*(depth+9); z0 = random.uniform(-SPAN/2, SPAN/2)
        rot0 = (random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28)); spin = (random.choice([-1, 1]), random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        o.location = (x, depth, z0); o.rotation_euler = rot0; coins.append((o, x, depth, z0, rot0, spin))
    bpy.data.objects.remove(proto)
    # lumières chaudes floues au loin : bokeh
    for k in range(45):
        cc = random.choice([(1, .62, .12), (1, .62, .12), (1, .45, .08), (1, .8, .45), (.95, .35, .06)])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.07, 0.16), location=(random.uniform(-7, 7), random.uniform(28, 40), random.uniform(-10, 10)))
        s = bpy.context.object; s.data.materials.append(mat(f'n{k}', cc, emit=random.uniform(16, 36)))
    def area(loc, rot, size, e, col_):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = e; l.data.color = col_
    area((2.5, -1.5, 5), (math.radians(35), math.radians(20), 0), 4, 900, (1, .85, .6))
    area((0, 16, 2), (math.radians(-100), 0, 0), 6, 1400, (1, .62, .2))
    area((-5, 3, -2), (math.radians(80), 0, math.radians(-70)), 4, 400, (1, .5, .2))
    area((0, -12, 0), (math.radians(90), 0, 0), 8, 500, (1, .8, .55))      # grande source face : reflets sur les faces des pièces
    bpy.ops.object.camera_add(location=(0, -9.0, 0), rotation=(math.radians(90), 0, 0)); cam = bpy.context.object; cam.data.lens = 85
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 11.0; cam.data.dof.aperture_fstop = 0.8; sc.camera = cam
    for (o, x, depth, z0, rot0, spin) in coins:
        for f in (1, NF+1):
            u = (f-1)/NF
            o.location = (x, depth, z0-SPAN*u); o.rotation_euler = tuple(rot0[k]+spin[k]*2*math.pi*u for k in range(3))
            o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for layer in getattr(ad.action, 'layers', []):
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        for fc in cb.fcurves:
                            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    for (o, *_ ) in coins:
        o2 = o.copy(); bpy.context.collection.objects.link(o2); o2.delta_location = (0, 0, SPAN)
    sc.render.fps = 30; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.6
    sc.frame_start, sc.frame_end = 1, NF
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (720, 1280, 16)
    sc = build(); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[4]) if len(a) > 4 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[4]) if len(a) > 4 else 1; f1 = int(a[5]) if len(a) > 5 else NF
        for f in range(f0, f1+1):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
