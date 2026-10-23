"""Globe 3D (continents en points) qui tourne selon le minutage de la voix PEA/CTO.
Deux rendus par image : beauté (globe sombre, points lumineux discrets) + masque (R = toutes les terres, G = pays éligibles PEA)
que le montage utilise pour allumer les continents. Fond transparent : le globe est placé et éclairé au montage.
usage : python globe.py <out_dossier> [res samples f0 f1 step]  |  python globe.py <out.png> res samples t"""
import bpy, math, os, sys, time
sys.path.insert(0, '/home/claude/aapl/b3d'); sys.path.insert(0, '/home/claude/amzn/b3d')
import objs
from objs import mat
D = '/home/claude/pea'; FPS = 15; DUR = 36.9

# ---------- rotation : (temps, longitude face caméra, latitude) ----------
KEYS = [(0.0, -28, 22), (4.6, 2, 32),            # accroche : lente dérive Atlantique -> Europe/Afrique
        (4.85, 2, 32), (7.9, 362, 30),           # compte-titres : un tour complet du monde
        (8.6, 375, 47), (11.8, 382, 45),         # PEA : l'Europe face à nous
        (13.0, 392, 40), (29.6, 430, 38),        # fond pendant les panneaux : très lente dérive
        (30.3, 372, 46), (31.9, 374, 46),        # « tes actions européennes » : Europe
        (32.7, 265, 38), (34.2, 262, 38), (DUR, 255, 36)]   # « américaines » : Amérique du Nord
def smooth(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
def pose(t):
    for (t0, l0, a0), (t1, l1, a1) in zip(KEYS[:-1], KEYS[1:]):
        if t0 <= t <= t1:
            u = smooth((t-t0)/max(1e-6, t1-t0))
            if t1-t0 > 6: u = (t-t0)/(t1-t0)              # longues dérives : vitesse constante
            return l0+(l1-l0)*u, a0+(a1-a0)*u
    return KEYS[-1][1], KEYS[-1][2]

def tex_node(nt, path, vec, non_color=True):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.interpolation = 'Cubic'; t.extension = 'REPEAT'
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(vec, t.inputs['Vector']); return t
def sph_uv(nt):
    """coordonnées objet -> (lon, lat) équirectangulaires : u = atan2(y,x)/2π + 0,5 ; v = asin(z)/π + 0,5"""
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
    nm = nt.nodes.new('ShaderNodeVectorMath'); nm.operation = 'NORMALIZE'; nt.links.new(tc.outputs['Object'], nm.inputs[0]); sp2 = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(nm.outputs[0], sp2.inputs[0])
    at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; nt.links.new(sp2.outputs['Y'], at.inputs[0]); nt.links.new(sp2.outputs['X'], at.inputs[1])
    u = nt.nodes.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; nt.links.new(at.outputs[0], u.inputs[0]); u.inputs[1].default_value = 1/(2*math.pi); u.inputs[2].default_value = .5
    asn = nt.nodes.new('ShaderNodeMath'); asn.operation = 'ARCSINE'; nt.links.new(sp2.outputs['Z'], asn.inputs[0])
    v = nt.nodes.new('ShaderNodeMath'); v.operation = 'MULTIPLY_ADD'; nt.links.new(asn.outputs[0], v.inputs[0]); v.inputs[1].default_value = 1/math.pi; v.inputs[2].default_value = .5
    cb = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(u.outputs[0], cb.inputs['X']); nt.links.new(v.outputs[0], cb.inputs['Y'])
    return cb.outputs[0]

def beauty_mat():
    m = bpy.data.materials.new('globe'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    b.inputs['Base Color'].default_value = (0.004, 0.009, 0.02, 1); b.inputs['Roughness'].default_value = .4
    b.inputs['Coat Weight'].default_value = .5; b.inputs['Coat Roughness'].default_value = .25
    uv = sph_uv(nt); dots = tex_node(nt, f'{D}/dots.png', uv)
    em = nt.nodes.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = .28; L(dots.outputs['Color'], em.inputs[0])
    b.inputs['Emission Color'].default_value = (.62, .72, .86, 1); L(em.outputs[0], b.inputs['Emission Strength'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .25; bp.inputs['Distance'].default_value = .003; L(dots.outputs['Color'], bp.inputs['Height']); L(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def mask_mat():
    m = bpy.data.materials.new('mask'); m.use_nodes = True; nt = m.node_tree; L = nt.links.new
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    uv = sph_uv(nt); a = tex_node(nt, f'{D}/m_all_dots.png', uv); e = tex_node(nt, f'{D}/m_eu_dots.png', uv)
    cb = nt.nodes.new('ShaderNodeCombineColor'); L(a.outputs['Color'], cb.inputs[0]); L(e.outputs['Color'], cb.inputs[1])
    es = nt.nodes.new('ShaderNodeEmission'); L(cb.outputs[0], es.inputs['Color']); es.inputs['Strength'].default_value = 1
    L(es.outputs[0], nt.nodes['Material Output'].inputs['Surface']); return m

def build():
    sc = objs.reset(); sc.render.film_transparent = True
    sc.view_settings.exposure = 0
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1); g = bpy.context.object; bpy.ops.object.shade_smooth()
    g.rotation_mode = 'ZYX'; g.name = 'globe'
    MB, MM = beauty_mat(), mask_mat(); g.data.materials.append(MB)
    A = __import__('amz').area
    A((-3.2, 1.8, 2.2), (math.radians(-60), 0, math.radians(-120)), 6, 700, (.55, .8, 1), shape='DISK')     # contre-jour froid : liseré
    A((3.0, -2.5, 1.5), (math.radians(65), 0, math.radians(50)), 7, 160, (1, .92, .8), shape='DISK')        # clé douce chaude
    for o in bpy.data.objects:
        if o.type == 'LIGHT': o.visible_camera = False
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 85; cam.location = (0, -5.6, 0); cam.rotation_euler = (math.radians(90), 0, 0)
    return sc, g, MB, MM

def set_pose(g, t):
    lon, lat = pose(t); g.rotation_euler = (math.radians(lat), 0, math.radians(-90-lon))

def render_pair(sc, g, MB, MM, t, p_b, p_m, res, samples):
    set_pose(g, t)
    g.data.materials[0] = MB; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'; sc.render.filepath = p_b; bpy.ops.render.render(write_still=True)
    g.data.materials[0] = MM; sc.cycles.samples = 4; sc.cycles.use_denoising = False
    sc.view_settings.view_transform = 'Standard'; sc.render.filepath = p_m; bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    sc, g, MB, MM = build(); res = int(a[1]) if len(a) > 1 else 1200
    sc.render.resolution_x = sc.render.resolution_y = res; sc.render.use_persistent_data = True
    samples = int(a[2]) if len(a) > 2 else 16
    if out.endswith('.png'):
        render_pair(sc, g, MB, MM, float(a[3]) if len(a) > 3 else 0.0, out, out.replace('.png', '_m.png'), res, samples)
    else:
        os.makedirs(f'{out}/b', exist_ok=True); os.makedirs(f'{out}/m', exist_ok=True)
        n = int(DUR*FPS)+1; f0 = int(a[3]) if len(a) > 3 else 0; f1 = int(a[4]) if len(a) > 4 else n-1; st = int(a[5]) if len(a) > 5 else 1
        for f in range(f0, f1+1, st):
            pb, pm = f'{out}/b/{f:04d}.png', f'{out}/m/{f:04d}.png'
            if os.path.exists(pb) and os.path.exists(pm): continue
            t0 = time.time(); render_pair(sc, g, MB, MM, f/FPS, pb, pm, res, samples); print('frame', f, round(time.time()-t0, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
