"""Scènes Amazon animées et fixes.
usage : python anim.py <scene> <out_dir_or_png> [rx ry samples f0 f1]
scènes : belt (boucle convoyeur), dc (boucle allée data center), garage, crash, stacks
"""
import bpy, math, random, os, sys
sys.path.insert(0, '/home/claude/amzn/b3d')
import amz, objs
from objs import mat, box
from amz import cbox, cardboard, area, camera

FPS = 30

def lin(obj, path='location'):
    ad = obj.animation_data if hasattr(obj, 'animation_data') else None
    if ad and ad.action:
        for fc in getattr(ad.action, 'fcurves', []):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        # Blender 5 : actions en couches
        for layer in getattr(ad.action, 'layers', []):
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

def belt_material(name='beltm'):
    """caoutchouc sombre avec nervures transversales tous les 20 cm, décalables"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    off = nt.nodes.new('ShaderNodeValue'); off.name = 'OFF'; off.outputs[0].default_value = 0.0
    sub = nt.nodes.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'
    dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = 0.2
    fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.86
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.010, 0.010, 0.012, 1); mix.inputs[7].default_value = (0.045, 0.045, 0.05, 1)
    nt.links.new(tc.outputs['Object'], sp.inputs[0]); nt.links.new(sp.outputs['Y'], sub.inputs[0]); nt.links.new(off.outputs[0], sub.inputs[1])
    nt.links.new(sub.outputs[0], dv.inputs[0]); nt.links.new(dv.outputs[0], fr.inputs[0]); nt.links.new(fr.outputs[0], gt.inputs[0])
    nt.links.new(gt.outputs[0], mix.inputs[0]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    rg = nt.nodes.new('ShaderNodeMapRange'); rg.inputs[3].default_value = 0.62; rg.inputs[4].default_value = 0.4
    nt.links.new(gt.outputs[0], rg.inputs[0]); nt.links.new(rg.outputs[0], b.inputs['Roughness'])
    return m, off

def label_mat():
    """étiquette blanche avec bande orange (texture procédurale en coordonnées UV générées)"""
    m = bpy.data.materials.new('lbl'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.8
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.86, 0.85, 0.82, 1); mix.inputs[7].default_value = (1.0, 0.42, 0.02, 1)
    nt.links.new(tc.outputs['Generated'], sp.inputs[0]); nt.links.new(sp.outputs['Y'], gt.inputs[0])
    nt.links.new(gt.outputs[0], mix.inputs[0]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.5
    return m

def parcel(name, loc, size, rot, card, tape, lbl, parent=None):
    """carton posé : la base est exactement à loc.z (contact)"""
    bpy.ops.object.empty_add(location=loc); root = bpy.context.object; root.name = name
    root.rotation_euler = (0, 0, rot)
    sx, sy, sz = size
    o = box(name + 'b', size, loc=(0, 0, sz / 2), bevel=min(size) * 0.035, seg=2, m=card); o.parent = root
    t = box(name + 't', (sx * 0.16, sy * 1.003, sz * 1.003), loc=(0, 0, sz / 2), bevel=0, m=tape); t.parent = root
    if lbl:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(sx * 0.22, -sy * 0.12, sz + 0.002)); l = bpy.context.object
        l.scale = (sx * 0.28, sy * 0.36, 1); l.data.materials.append(lbl); l.parent = root
    return root

def conveyor(y0=-12, y1=34, card=None, tape=None):
    steel = mat('steel2', (0.30, 0.32, 0.35), metal=1.0, rough=0.38)
    dark = mat('dk', (0.04, 0.04, 0.045), metal=0.6, rough=0.5)
    L = y1 - y0; yc = (y0 + y1) / 2
    bm, off = belt_material()
    belt = box('belt', (1.12, L, 0.06), loc=(0, yc, 0.78), bevel=0.01, seg=2, m=bm)   # dessus à z = 0.81
    # longerons latéraux et rails de guidage (les cartons glissent entre eux)
    for s in (-1, 1):
        box('chan', (0.07, L, 0.20), loc=(s * 0.62, yc, 0.73), bevel=0.008, seg=2, m=steel)
        box('rail', (0.035, L, 0.04), loc=(s * 0.60, yc, 0.93), bevel=0.006, seg=2, m=steel)
        for k in range(int(L / 1.6)):
            y = y0 + 0.8 + k * 1.6
            box('brk', (0.03, 0.04, 0.12), loc=(s * 0.61, y, 0.87), bevel=0, m=steel)      # supports de rail
    # rouleaux de retour visibles sous la bande + pieds
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.16, rotation=(0, math.pi / 2, 0), location=(0, y0, 0.66))
    proto = bpy.context.object; proto.data.materials.append(mat('roll', (0.5, 0.52, 0.55), metal=1, rough=0.3))
    for k in range(int(L / 0.6)):
        r = proto.copy(); r.location = (0, y0 + k * 0.6, 0.66); bpy.context.collection.objects.link(r)
    for k in range(int(L / 2.4)):
        y = y0 + k * 2.4
        for s in (-1, 1): box('leg', (0.06, 0.06, 0.62), loc=(s * 0.55, y, 0.31), bevel=0.005, seg=1, m=dark)
        box('cross', (1.1, 0.05, 0.05), loc=(0, y, 0.18), bevel=0, m=dark)
    return off

def setup_motion(sc):
    sc.render.fps = FPS; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5

def belt_scene():
    """boucle parfaite : motif de 2 cartons tous les 1,6 m, bande à 1 m/s, période 3,2 m = 96 images à 30 i/s"""
    random.seed(7)
    sc = amz.warehouse(1, conveyor=False)
    card = cardboard(); tape = mat('tape2', (0.72, 0.6, 0.42), rough=0.35); lbl = label_mat()
    off = conveyor(card=card, tape=tape)
    setup_motion(sc)
    sizes = [((0.50, 0.62, 0.40), 0.03), ((0.42, 0.48, 0.34), -0.05)]
    PER, V, NF = 3.2, 1.0, 96
    for k in range(-6, 22):
        size, rot = sizes[k % 2]
        p = parcel(f'p{k}', (0, k * 1.6, 0.81), size, rot, card, tape, lbl)
        for f, dy in ((1, 0.0), (1 + NF, PER)):
            p.location.y = k * 1.6 + dy; p.keyframe_insert('location', frame=f)
        lin(p)
    bt = bpy.data.materials['beltm'].node_tree
    off.outputs[0].default_value = 0.0; off.outputs[0].keyframe_insert('default_value', frame=1)
    off.outputs[0].default_value = PER; off.outputs[0].keyframe_insert('default_value', frame=1 + NF)
    lin(bt)
    # lumière zénithale douce au-dessus de la bande : ombres de contact nettes
    for k in range(5):
        area((0, 1 + k * 3.2, 2.6), (0, 0, 0), 0.5, 55, (1.0, 0.85, 0.65), sy=1.4)
    camera((0.42, -3.0, 1.7), (0, 8, 0.8), 28); sc.view_settings.exposure = -0.55
    sc.frame_start, sc.frame_end = 1, NF
    return sc

def dc_scene():
    """allée de data center, travelling avant d'exactement un pas de baie (1,25 m) : boucle"""
    sc = amz.base(); amz.floor((0.035, 0.04, 0.05), 0.1)
    rack = mat('rack', (0.02, 0.022, 0.026), metal=0.6, rough=0.35)
    door = mat('mesh', (0.05, 0.055, 0.065), metal=0.9, rough=0.3)
    leds = [mat('lb', (0.1, 0.55, 1.0), emit=14), mat('lo', (1.0, 0.55, 0.1), emit=12), mat('lg', (0.2, 1.0, 0.5), emit=8)]
    pat = []
    random.seed(11)
    for r in range(16):
        for c in range(5):
            if random.random() < 0.55: pat.append((r, c, random.choice(leds if random.random() < 0.55 else leds[:1])))
    STEP = 1.25
    def join(objs_):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs_: o.select_set(True)
        bpy.context.view_layer.objects.active = objs_[0]; bpy.ops.object.join(); return bpy.context.object
    def inst(proto, loc):
        o = proto.copy(); o.location = loc; bpy.context.collection.objects.link(o); return o
    protos = {}
    for side in (-1, 1):
        parts = [box('rack', (0.9, 1.18, 2.4), loc=(0, 0, 1.2), bevel=0.01, seg=1, m=rack),
                 box('top', (0.95, 1.2, 0.08), loc=(0, 0, 2.44), bevel=0, m=door),
                 box('cab', (0.3, STEP, 0.05), loc=(0, 0, 2.62), bevel=0, m=mat('cbl', (0.9, 0.5, 0.08), rough=0.5))]
        for (r, c, m) in pat: parts.append(box('led', (0.02, 0.03, 0.015), loc=(-side * 0.452, -0.4 + c * 0.2, 0.3 + r * 0.13), bevel=0, m=m))
        for r in range(16): parts.append(box('slot', (0.005, 1.0, 0.008), loc=(-side * 0.451, 0, 0.36 + r * 0.13), bevel=0, m=door))
        for p in parts:
            for md in list(p.modifiers):
                bpy.context.view_layer.objects.active = p; bpy.ops.object.modifier_apply(modifier=md.name)
        protos[side] = join(parts); protos[side].location = (side * 1.6, -6 * STEP, 0)
        for k in range(-5, 40): inst(protos[side], (side * 1.6, k * STEP, 0))
    em = mat('em2', (0.6, 0.8, 1.0), emit=6)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -6 * STEP, 3.0)); e = bpy.context.object; e.scale = (0.08, 0.9, 0.02); e.data.materials.append(em)
    for k in range(-5, 40): inst(e, (0, k * STEP, 3.0))
    box('ceil', (6, 90, 0.1), loc=(0, 20, 3.3), bevel=0, m=mat('c', (0.01, 0.012, 0.016), rough=0.9))
    cam = camera((0.15, -1.0, 1.45), (0.0, 10, 1.3), 26)
    # lumière de fond attachée à la caméra pour que la boucle soit invisible
    l = area((0, 17, 1.5), (math.radians(-90), 0, 0), 4, 500, (0.2, 0.5, 1.0)); l.location = (0, 22, 2.8)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 58, 1.5), rotation=(math.radians(90), 0, 0)); g = bpy.context.object; g.scale = (3.2, 3.4, 1); g.data.materials.append(mat('glow', (0.15, 0.45, 1.0), emit=3))
    l2 = area((0, 6, 2.9), (0, 0, 0), 1.0, 500, (0.5, 0.7, 1.0), sy=12)
    setup_motion(sc)
    NF = 75
    for o in (cam, l, l2):
        y = o.location.y
        o.keyframe_insert('location', frame=1); o.location.y = y + STEP; o.keyframe_insert('location', frame=1 + NF); lin(o)
    sc.frame_start, sc.frame_end = 1, NF
    return sc

def garage_scene():
    """1994 : un seul carton sous une ampoule, dans un garage"""
    random.seed(3)
    sc = amz.base(); sc.view_settings.exposure = -0.2
    amz.floor((0.05, 0.05, 0.05), 0.5)
    conc = mat('wall', (0.16, 0.15, 0.14), rough=0.9)
    box('wallB', (8, 0.2, 5), loc=(0, 3.0, 2.5), bevel=0, m=conc)
    box('wallL', (0.2, 8, 5), loc=(-2.6, 0, 2.5), bevel=0, m=conc)
    # porte de garage sectionnelle (panneaux)
    pan = mat('door', (0.22, 0.22, 0.24), metal=0.5, rough=0.45)
    for i in range(6): box('dpan', (3.4, 0.06, 0.38), loc=(0.6, 2.86, 0.22 + i * 0.4), bevel=0.01, seg=2, m=pan)
    card = cardboard(); tape = mat('tape3', (0.72, 0.6, 0.42), rough=0.35); lbl = label_mat()
    parcel('p0', (0, 0.4, 0), (0.62, 0.5, 0.42), 0.35, card, tape, lbl)
    # bureau-porte générique sur tréteaux, à gauche, et une lampe
    wood = mat('wood', (0.38, 0.26, 0.15), rough=0.6)
    box('desk', (0.9, 2.0, 0.05), loc=(-1.8, 1.4, 0.76), bevel=0.01, seg=2, m=wood)
    for dy in (-0.8, 0.8):
        for dx in (-0.35, 0.35): box('trest', (0.04, 0.04, 0.74), loc=(-1.8 + dx, 1.4 + dy, 0.37), bevel=0, m=mat('tr', (0.1, 0.1, 0.1), rough=0.5))
    box('crt', (0.42, 0.42, 0.38), loc=(-1.85, 1.8, 0.98), bevel=0.04, seg=3, m=mat('beige', (0.55, 0.52, 0.45), rough=0.5))
    for i in range(3): box('book', (0.22, 0.3, 0.05), loc=(-1.75, 0.8, 0.81 + i * 0.05), bevel=0.005, seg=1, m=mat(f'bk{i}', [(0.5, 0.1, 0.08), (0.1, 0.2, 0.4), (0.7, 0.6, 0.3)][i], rough=0.6))
    # ampoule et cône de lumière
    bpy.ops.object.light_add(type='SPOT', location=(0.1, 0.35, 2.0)); s = bpy.context.object; s.data.energy = 700; s.data.spot_size = math.radians(55); s.data.spot_blend = 0.6; s.data.color = (1.0, 0.78, 0.5); s.data.shadow_soft_size = 0.05
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(0.1, 0.35, 2.06)); bpy.context.object.data.materials.append(mat('bulb', (1, 0.8, 0.5), emit=40))
    bpy.ops.object.light_add(type='POINT', location=(0.1, 0.35, 2.12)); pl = bpy.context.object; pl.data.energy = 25; pl.data.color = (1, 0.75, 0.45); pl.data.shadow_soft_size = 0.05
    box('cord', (0.006, 0.006, 2.0), loc=(0.1, 0.35, 3.1), bevel=0, m=mat('cd', (0.02, 0.02, 0.02)))
    area((2.5, -2, 2), (math.radians(60), 0, math.radians(50)), 2, 14, (0.4, 0.55, 0.9))
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.003, 0.004, 0.006, 1)
    camera((0.75, -2.6, 0.95), (-0.05, 0.6, 0.85), 30)
    return sc

def crash_scene():
    """entrepôt à l'arrêt : lumières coupées, éclairage de secours rouge, cartons tombés"""
    random.seed(21)
    sc = amz.warehouse(5, conveyor=False)
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT': bpy.data.objects.remove(o)
    for m in bpy.data.materials:
        if m.name.startswith('em'):
            b = m.node_tree.nodes['Principled BSDF']; b.inputs['Emission Strength'].default_value = 0.0
    card = cardboard(); tape = mat('tape4', (0.72, 0.6, 0.42), rough=0.35); lbl = label_mat()
    conveyor(card=card, tape=tape)
    for k in range(9):
        s = random.uniform(0.38, 0.6)
        if k % 3 == 0:   # carton tombé au sol, couché
            p = parcel(f'f{k}', (random.choice((-1, 1)) * random.uniform(0.9, 1.6), k * 1.7 + random.uniform(-.3, .3), 0), (s, s * 1.2, s * 0.8), random.uniform(0, 3), card, tape, lbl)
        else:            # carton immobile sur la bande
            p = parcel(f'b{k}', (random.uniform(-.08, .08), k * 1.7, 0.81), (s, s * 1.15, s * 0.8), random.uniform(-.15, .15), card, tape, lbl)
    red = (1.0, 0.08, 0.04)
    for k in range(4):
        y = 2 + k * 6
        for s in (-1, 1):
            bpy.ops.object.light_add(type='POINT', location=(s * 3.2, y, 4.2)); l = bpy.context.object; l.data.energy = 110; l.data.color = red; l.data.shadow_soft_size = 0.1
            box('beacon', (0.12, 0.12, 0.12), loc=(s * 3.25, y, 4.3), bevel=0.02, seg=2, m=mat('rb', red, emit=25))
    area((0, 30, 3), (math.radians(-90), 0, 0), 8, 900, (0.25, 0.35, 0.7))
    area((-3, -4, 4), (math.radians(50), 0, math.radians(-30)), 3, 120, (0.5, 0.6, 0.9))
    camera((0.42, -3.0, 1.7), (0, 8, 0.8), 28)
    return sc

def stacks_scene():
    amz.warehouse(3, conveyor=False, stacks=[(-0.85, 1.6, 10, 0.42), (0.85, 1.6, 17, 0.42)])
    return amz.camera((0, -7.5, 2.0), (0, 1.6, 2.0), 36)

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    scene, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (540, 960, 16)
    sc = {'belt': belt_scene, 'dc': dc_scene, 'garage': garage_scene, 'crash': crash_scene, 'stacks': stacks_scene}[scene]()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples
    sc.render.use_persistent_data = True
    if out.endswith('.png'):
        f = int(a[5]) if len(a) > 5 else 1
        sc.frame_set(f); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True)
        f0 = int(a[5]) if len(a) > 5 else sc.frame_start; f1 = int(a[6]) if len(a) > 6 else sc.frame_end
        import time
        for f in range(f0, f1 + 1):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
            print('frame', f, round(time.time() - t, 1), flush=True)
