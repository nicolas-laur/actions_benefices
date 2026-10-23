"""Pièce ₿ en or massif, studio sombre et chaud. Glyphe ₿ générique (police Liberation Sans), pas de logo officiel.
usage : python coin.py <out.png | dossier> [rx ry samples f0 f1]"""
import bpy, bmesh, math, os, sys, time
sys.path.insert(0, '/home/claude/visa/b3d')
import objs
from objs import mat
import vscene
from vscene import softbox
NF = 180   # boucle de 6 s à 30 i/s

def gold(name='gold', tint=(1.0, 0.66, 0.22), rough=0.14):
    m = mat(name, tint, metal=1.0, rough=rough)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    # micro-variations de rugosité : or brossé très léger
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 40; n.inputs['Detail'].default_value = 2
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[3].default_value = rough*.85; mr.inputs[4].default_value = rough*1.15
    nt.links.new(n.outputs['Fac'], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    return m

def reeded_disc(R=1.0, D=0.16, ridges=160, depth=0.012):
    """disque à tranche cannelée"""
    me = bpy.data.meshes.new('coin'); bm = bmesh.new(); n = ridges*2
    pts = [((R-(depth if i % 2 else 0))*math.cos(2*math.pi*i/n), (R-(depth if i % 2 else 0))*math.sin(2*math.pi*i/n)) for i in range(n)]
    bot = [bm.verts.new((x, y, -D/2)) for x, y in pts]; top = [bm.verts.new((x, y, D/2)) for x, y in pts]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(n): bm.faces.new((bot[i], bot[(i+1) % n], top[(i+1) % n], top[i]))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('coin', me); bpy.context.collection.objects.link(o)
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.012; bv.segments = 3; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(60)
    for p in o.data.polygons: p.use_smooth = True
    return o

def ring(r_in, r_out, h, z, parent, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r_out, depth=h, location=(0, 0, z)); a = bpy.context.object
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r_in, depth=h*3, location=(0, 0, z)); b = bpy.context.object
    md = a.modifiers.new('cut', 'BOOLEAN'); md.object = b; md.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier='cut'); bpy.data.objects.remove(b)
    bv = a.modifiers.new('bv', 'BEVEL'); bv.width = 0.006; bv.segments = 2
    a.data.materials.clear(); a.data.materials.append(m); bv.harden_normals = True; bpy.ops.object.shade_flat(); a.parent = parent; return a

def glyph(z, parent, m, size=1.05):
    cu = bpy.data.curves.new('b', 'FONT'); cu.body = '₿'; cu.font = bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
    cu.size = size; cu.extrude = 0.022; cu.bevel_depth = 0.008; cu.bevel_resolution = 3; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('glyph', cu); bpy.context.collection.objects.link(o); o.location = (0, 0, z); o.rotation_euler = (0, 0, math.radians(-14))
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target='MESH')
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    o.data.materials.clear(); o.data.materials.append(m); o.parent = parent; return o

def build():
    sc = vscene.studio(exposure=0.1)
    # fond : cyclorama brun très sombre, halo ambre derrière la pièce
    for o in bpy.data.objects:
        if o.name == 'cyc': o.data.materials[0] = mat('cycw', (0.008, 0.005, 0.003), rough=0.7)
        if o.type == 'LIGHT': o.data.color = (1.0, .8, .55) if o.data.color[2] > .8 else o.data.color; o.data.energy *= .6; o.visible_glossy = False
        if o.type == 'LIGHT' and o.data.color[2] > .9 and o.data.color[0] < .3: o.data.color = (1.0, 0.45, 0.08); o.data.energy = 420
    g = gold(); g2 = gold('gold_m', (0.95, 0.60, 0.20), .30); g3 = gold('gold_g', (1.0, .70, .26), .1)   # champ satiné, reliefs polis
    root = bpy.data.objects.new('root', None); bpy.context.collection.objects.link(root)
    c = reeded_disc(); c.data.materials.append(g2); c.parent = root
    for s in (1, -1):
        ring(.86, .94, .04, s*.08, root, g)
        ring(.30, .31, .02, s*.08, root, g) if False else None
        gl = glyph(s*.085, root, g3)
        if s < 0: gl.rotation_euler = (math.pi, 0, math.radians(14))
    # petits points gravés en couronne
    for k in range(48):
        a = 2*math.pi*k/48
        for s in (1, -1):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=.012, location=(.78*math.cos(a), .78*math.sin(a), s*.08)); d = bpy.context.object; d.data.materials.append(g); d.parent = root
    root.location = (0, 0.3, 0.55)
    for o in bpy.data.objects:
        if o.name.startswith('sb_') and o.active_material:
            em = [n for n in o.active_material.node_tree.nodes if n.type == 'EMISSION'][0]
            st = [n for n in o.active_material.node_tree.nodes if n.type == 'MATH'][0]; st.inputs[1].default_value *= 1.4
            em.inputs['Color'].default_value = {'sb_top': (1.0, .82, .55, 1), 'sb_cool': (1.0, .55, .25, 1)}.get(o.name, tuple(em.inputs['Color'].default_value))
    softbox('sb_front', (0, -4.0, -1.2), (math.radians(70), 0, 0), 3.0, 2.2, (1.0, .7, .35), sy=1.4)
    softbox('sb_rim', (0, 2.2, 1.8), (math.radians(-60), 0, 0), 2.5, 2.5, (1.0, .78, .5), sy=.4)
    cam = vscene.camera((0, -7.6, 0.2), (0, 0.3, 0.05), lens=70); cam.data.dof.aperture_fstop = 2.0
    # animation : la pièce se tient face caméra, balancement lent et continu (boucle parfaite)
    for f in range(1, NF+2):
        u = (f-1)/NF
        root.rotation_euler = (math.radians(90)+math.radians(9)*math.sin(2*math.pi*u), math.radians(6)*math.sin(4*math.pi*u), math.radians(26)*math.sin(2*math.pi*u+.6))
        root.location = (0, 0.3, 0.55+0.04*math.sin(2*math.pi*u))
        root.keyframe_insert('rotation_euler', frame=f); root.keyframe_insert('location', frame=f)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    vscene.link_softboxes()
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (720, 1280, 24)
    sc = build(); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[4]) if len(a) > 4 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[4]) if len(a) > 4 else 1; f1 = int(a[5]) if len(a) > 5 else NF
        for f in range(f0, f1+1):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
