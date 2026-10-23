"""Fond McDonald's : pluie de frites au ralenti (frites seules, aucun emballage), flou de profondeur, bokeh de néons.
Boucle parfaite : chaque frite descend exactement d'une hauteur de boucle, avec un nombre entier de tours.
usage : python fries.py <out_dir|png> [rx ry samples f0 f1]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/visa/b3d')
import objs
from objs import mat
from mathutils import Vector
NF = 150; SPAN = 13.0

def fry_material():
    m = bpy.data.materials.new('fry'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 18; n.inputs['Detail'].default_value = 6
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color = (0.80, 0.50, 0.12, 1); rp.color_ramp.elements[1].color = (1.0, 0.78, 0.30, 1)
    nt.links.new(n.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25; nt.links.new(n.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = 0.42
    try:
        b.inputs['Subsurface Weight'].default_value = 0.25; b.inputs['Subsurface Radius'].default_value = (0.6, 0.35, 0.1)
    except Exception: pass
    try: b.inputs['Coat Weight'].default_value = 0.15
    except Exception: pass
    return m
def make_fry(m, L):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.scale = (0.095, 0.095, L); bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.012; bv.segments = 3
    sd = o.modifiers.new('sub', 'SUBSURF'); sd.levels = 1; sd.render_levels = 1
    bd = o.modifiers.new('bend', 'SIMPLE_DEFORM'); bd.deform_method = 'BEND'; bd.angle = math.radians(random.uniform(-14, 14)); bd.deform_axis = 'Z'
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def build():
    random.seed(12)
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.012, 0.004, 0.003, 1); w.inputs[1].default_value = 1.0
    sc.view_settings.exposure = -0.2
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    m = fry_material()
    protos = [make_fry(m, L) for L in (0.7, 0.85, 1.0, 1.1)]
    fries = []
    for i in range(80):
        p = random.choice(protos); o = p.copy(); bpy.context.collection.objects.link(o)
        depth = random.uniform(-4, 12)
        x = random.uniform(-1, 1)*0.13*(depth+9); z0 = random.uniform(-SPAN/2, SPAN/2)
        rot0 = (random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28)); spin = (random.choice([-1, 1]), random.choice([-1, 0, 1]), random.choice([-1, 1]))
        o.location = (x, depth, z0); o.rotation_euler = rot0
        fries.append((o, x, depth, z0, rot0, spin))
    for p in protos: bpy.data.objects.remove(p)
    # néons flous au loin : de vraies sources lumineuses pour un bokeh naturel
    for k in range(45):
        cc = random.choice([(1, .78, .17), (1, .78, .17), (1, .45, .1), (1, .2, .12), (1, .9, .6)])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.07, 0.16), location=(random.uniform(-7, 7), random.uniform(28, 40), random.uniform(-10, 10)))
        s = bpy.context.object; s.data.materials.append(mat(f'neon{k}', cc, emit=random.uniform(18, 40)))
    # lumière : clé chaude au-dessus, contre-jour jaune, remplissage rouge
    def area(loc, rot, size, e, col_):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = e; l.data.color = col_
    area((2.5, -1.5, 5), (math.radians(35), math.radians(20), 0), 4, 900, (1, .82, .55))
    area((0, 16, 2), (math.radians(-100), 0, 0), 6, 1500, (1, .7, .2))
    area((-5, 3, -2), (math.radians(80), 0, math.radians(-70)), 4, 500, (1, .25, .15))
    bpy.ops.object.camera_add(location=(0, -9.0, 0), rotation=(math.radians(90), 0, 0)); cam = bpy.context.object; cam.data.lens = 85
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 11.0; cam.data.dof.aperture_fstop = 0.8; sc.camera = cam
    print('DOF', cam.data.dof.use_dof, cam.data.dof.focus_distance, cam.data.dof.aperture_fstop, flush=True)
    # animation linéaire bouclée
    for (o, x, depth, z0, rot0, spin) in fries:
        sp = SPAN*(depth/8)**0.25     # légère parallaxe : les frites lointaines semblent plus lentes
        for f in (1, NF+1):
            u = (f-1)/NF
            o.location = (x, depth, z0-SPAN*u); o.rotation_euler = (rot0[0]+spin[0]*2*math.pi*u, rot0[1]+spin[1]*2*math.pi*u, rot0[2]+spin[2]*2*math.pi*u)
            o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for layer in getattr(ad.action, 'layers', []):
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        for fc in cb.fcurves:
                            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    # doublons décalés d'une hauteur de boucle au-dessus : continuité parfaite à la jonction
    for (o, x, depth, z0, rot0, spin) in fries:
        o2 = o.copy(); bpy.context.collection.objects.link(o2); o2.delta_location = (0, 0, SPAN)
    sc.render.fps = 30; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.6
    sc.frame_start, sc.frame_end = 1, NF
    return bpy.context.scene

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
