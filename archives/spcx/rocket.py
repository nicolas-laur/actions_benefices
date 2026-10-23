"""Fusée originale (design maison : ivoire, bande graphite, liseré cyan, 4 ailerons delta, 3 tuyères) + flamme animée en boucle.
Rendu sur fond transparent pour composition 2D (ciel, fumée, chiffres). Aucun élément de SpaceX.
usage : python rocket.py <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, bmesh, math, os, sys, time
sys.path.insert(0, '/home/claude/visa/b3d')
import objs
from objs import mat
NF = 48

def revolve(name, prof, m, seg=96, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    for r, z in prof: rings.append([bm.verts.new((r*math.cos(2*math.pi*k/seg), r*math.sin(2*math.pi*k/seg), z)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg): bm.faces.new((a[k], a[(k+1) % seg], b[(k+1) % seg], b[k]))
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o

def paint(name, base, rough=.32, coat=.4, panels=True):
    m = mat(name, base, metal=0.0, rough=rough); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = .08
    if panels:   # lignes de panneaux discrètes (anneaux) en relief
        tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'Z'
        wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 0
        rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = .96; rp.color_ramp.elements[1].position = .99
        bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .25
        nt.links.new(tc.outputs['Object'], wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def flame_mat(name, col_in, col_out, strength, density):
    """flamme : émission bruitée (bruit 4D bouclé), bords transparents"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); mix = nt.nodes.new('ShaderNodeMixShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission')
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = 3.5; nz.inputs['Detail'].default_value = 6; nz.inputs['Roughness'].default_value = .6
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); grad = nt.nodes.new('ShaderNodeMapRange')   # z local : 0 en haut (tuyère) -> -1 en bas
    grad.inputs[1].default_value = -1.0; grad.inputs[2].default_value = 0.0; grad.inputs[3].default_value = 0.0; grad.inputs[4].default_value = 1.0
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = .35
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color = (*col_out, 1); rp.color_ramp.elements[1].color = (*col_in, 1)
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6
    st = nt.nodes.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = strength
    cl = nt.nodes.new('ShaderNodeMath'); cl.operation = 'MULTIPLY'; cl.inputs[1].default_value = density; cl.use_clamp = True
    L = nt.links.new
    L(tc.outputs['Object'], nz.inputs['Vector']); L(tc.outputs['Object'], sep.inputs[0]); L(sep.outputs['Z'], grad.inputs[0])
    L(lw.outputs['Facing'], inv.inputs[1])          # 1 au centre (face caméra), 0 sur les bords
    L(inv.outputs[0], m1.inputs[0]); L(nz.outputs['Fac'], m1.inputs[1]); L(m1.outputs[0], m2.inputs[0]); L(grad.outputs[0], m2.inputs[1])
    L(m2.outputs[0], pw.inputs[0]); L(pw.outputs[0], rp.inputs['Fac']); L(pw.outputs[0], st.inputs[0]); L(pw.outputs[0], cl.inputs[0])
    L(rp.outputs['Color'], em.inputs['Color']); L(st.outputs[0], em.inputs['Strength'])
    L(cl.outputs[0], mix.inputs['Fac']); L(tr.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2]); L(mix.outputs[0], out.inputs[0])
    return m, nz

def build():
    sc = objs.reset(); sc.render.film_transparent = True; sc.view_settings.exposure = -0.2
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.01, 0.015, 0.03, 1); sc.world.node_tree.nodes['Background'].inputs[1].default_value = 1
    ivory = paint('ivory', (0.82, 0.80, 0.76)); graph = paint('graph', (0.03, 0.035, 0.04), .45, .2, False)
    cyan = mat('cyan', (0.0, 0.8, 1.0), emit=6); metal = mat('noz', (0.08, 0.075, 0.07), metal=1.0, rough=.35)
    root = bpy.data.objects.new('rocket', None); bpy.context.collection.objects.link(root)
    R = .5
    revolve('body', [(R, 0.0), (R, 5.4)], ivory, parent=root)
    revolve('band', [(R+.004, 3.6), (R+.004, 4.2)], graph, parent=root)
    revolve('ring', [(R+.008, 4.25), (R+.008, 4.29)], cyan, parent=root)
    nose = [(R*math.cos(math.asin(min(1, k/24)))**.9 if k < 24 else 0.0, 5.4+2.1*(k/24)) for k in range(25)]
    nose = [(R*(1-(k/24)**1.8)**.55, 5.4+2.1*k/24) for k in range(25)]
    revolve('nose', nose, ivory, parent=root)
    revolve('skirt', [(R, 0.0), (R*1.08, -.25), (R*1.08, -.3)], graph, parent=root)
    for k in range(4):   # ailerons delta
        a = math.pi/4+k*math.pi/2; me = bpy.data.meshes.new('fin'); bm = bmesh.new()
        pts = [(R, 0, -.2), (R+.55, 0, -.25), (R+.55, 0, .15), (R, 0, 1.3)]
        v = [bm.verts.new(p) for p in pts]; f = bm.faces.new(v)
        ex = bmesh.ops.extrude_face_region(bm, geom=[f]); nv = [e for e in ex['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=nv, vec=(0, .05, 0)); bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -.025, 0))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('fin', me); bpy.context.collection.objects.link(o); o.data.materials.append(graph); o.rotation_euler = (0, 0, a); o.parent = root
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = .01; bv.segments = 2
    for k in range(3):
        a = k*2*math.pi/3; x, y = .22*math.cos(a), .22*math.sin(a)
        o = revolve('noz', [(.06, -.3), (.08, -.4), (.16, -.62), (.2, -.7)], metal, 48, root); o.location = (x, y, 0)
    # flamme : trois couches (cœur blanc, flamme orange, panache diffus)
    fl = []
    for name, rr_, ln, ci, co, s_, d_ in (('core', .2, 2.2, (1, .97, .85), (1, .7, .3), 60, 3.0), ('mid', .34, 3.8, (1, .78, .35), (1, .35, .05), 26, 2.2),
                                          ('plume', .55, 6.0, (1, .55, .15), (.6, .15, .02), 8, 1.2)):
        prof = [(rr_*(.55+.45*math.sin(math.pi*min(1, u*1.6)))*(1-u)**.6+.01, -.68-ln*u) for u in [i/30 for i in range(31)]]
        m, nz = flame_mat('f'+name, ci, co, s_, d_)
        o = revolve('fl_'+name, prof, m, 48, root); o.scale = (1, 1, 1)
        # coordonnées objet : z de 0 (tuyère) à -1 (bout) pour le dégradé
        o.data.transform(__import__('mathutils').Matrix.Translation((0, 0, .68))); o.location.z = -.68
        o.data.transform(__import__('mathutils').Matrix.Diagonal((1, 1, 1/ln, 1))); o.scale.z = ln
        fl.append(nz); o.visible_shadow = False; o.hide_render = True   # flamme faite en 2D
    # lumière de la flamme sur le bas de la fusée
    bpy.ops.object.light_add(type='POINT', location=(0, 0, -1.2)); L = bpy.context.object; L.data.energy = 900; L.data.color = (1, .55, .2); L.data.shadow_soft_size = .6
    def area(loc, rot, size, e, col_):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = e; l.data.color = col_; return l
    area((-6, -4, 7), (math.radians(55), 0, math.radians(-55)), 4, 1400, (.75, .85, 1.0))     # lune froide
    area((6, -2, 3), (math.radians(80), 0, math.radians(70)), 3, 500, (1, .7, .4))            # remplissage chaud
    area((0, 6, 4), (math.radians(-60), 0, 0), 3, 900, (.4, .8, 1.0))                        # contre-jour cyan
    bpy.ops.object.camera_add(location=(0, -17, 1.0)); cam = bpy.context.object; cam.data.lens = 52
    look = (0, 0, 3.0); d = [look[i]-cam.location[i] for i in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0])-math.pi/2); sc.camera = cam
    root.rotation_euler = (0, 0, math.radians(20))
    # boucle de la flamme : W du bruit sur un cercle -> on anime W linéairement sur une période de NF images
    for f in range(1, NF+2):
        u = (f-1)/NF
        for k, nz in enumerate(fl):
            nz.inputs['W'].default_value = 2.0*math.sin(2*math.pi*u)+k; nz.inputs['W'].keyframe_insert('default_value', frame=f)
            nz.inputs['Scale'].default_value = 3.5+.4*math.cos(2*math.pi*u); nz.inputs['Scale'].keyframe_insert('default_value', frame=f)
        L.data.energy = 900*(1+.12*math.sin(2*math.pi*u*3)); L.data.keyframe_insert('energy', frame=f)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 24
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (600, 1200, 24)
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
