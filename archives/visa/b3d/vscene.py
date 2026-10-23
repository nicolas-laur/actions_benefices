"""Visa : carte métal générique (aucun logo), terminal générique, studio bleu nuit et or."""
import bpy, math, sys, os, random
sys.path.insert(0, '/home/claude/visa/b3d')
import objs
from objs import mat, box, slab
D = '/home/claude/visa/b3d'

def textures():
    import cairo
    # face de carte : noir graphite, guillochage or très discret
    W, H = 1712, 1080
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, W, H); g.add_color_stop_rgb(0, .055, .058, .07); g.add_color_stop_rgb(1, .025, .027, .034); c.set_source(g); c.paint()
    c.set_line_width(1.4)
    for k in range(70):
        c.set_source_rgba(.85, .68, .38, .16 if k % 5 else .30)
        c.move_to(-200, 200+k*22)
        for x in range(-200, W+200, 40): c.line_to(x, 200+k*22+60*math.sin(x/170+k*0.21)-x*0.35)
        c.stroke()
    s.write_to_png(f'{D}/tex_card.png')
    # écran du terminal : validation
    W, H = 600, 420
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s); c.set_source_rgb(.02, .03, .05); c.paint()
    c.set_source_rgb(.24, .86, .52); c.set_line_width(26); c.set_line_cap(1); c.set_line_join(1)
    c.arc(300, 170, 95, 0, 2*math.pi); c.stroke()
    c.move_to(250, 172); c.line_to(287, 208); c.line_to(355, 135); c.stroke()
    c.select_font_face('Poppins', 0, 1); c.set_font_size(52); t = 'PAYÉ'; e = c.text_extents(t)
    c.move_to(300-e.x_advance/2, 350); c.show_text(t)
    s.write_to_png(f'{D}/tex_screen.png')

def img_mat(name, path, metal=0.9, rough=0.32, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    try: b.inputs['Anisotropic'].default_value = 0.6
    except Exception: pass
    if emit: nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    return m

def planar_uv(o, w, h):
    me = o.data; uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = ((v.x+w/2)/w, (v.z+h/2)/h)

def card(name='card', parent=None):
    """carte 85,6 × 54 mm à l'échelle ×1 m (0,856 × 0,54), face vers -Y"""
    root = objs.empty(name)
    W, H, T = 0.856, 0.54, 0.012
    body = slab(name+'_body', W, H, T, 0.045, m=mat('edge', (0.75, 0.58, 0.32), metal=1.0, rough=0.25), parent=root, edge=0.003)
    face = slab(name+'_face', W-0.004, H-0.004, 0.001, 0.043, loc=(0, -T/2-0.0006, 0), parent=root, edge=0)
    planar_uv(face, W, H); face.data.materials.append(img_mat('cardface', f'{D}/tex_card.png'))
    back = slab(name+'_back', W-0.004, H-0.004, 0.001, 0.043, loc=(0, T/2+0.0006, 0), m=mat('back', (0.03, 0.032, 0.04), metal=0.9, rough=0.4), parent=root, edge=0)
    # puce générique : plaque or + contacts gravés
    gold = mat('gold', (1.0, 0.76, 0.4), metal=1.0, rough=0.22)
    slab(name+'_chip', 0.12, 0.092, 0.004, 0.014, loc=(-0.25, -T/2-0.002, 0.04), m=gold, parent=root, edge=0.001)
    dark = mat('chipline', (0.25, 0.18, 0.08), metal=1.0, rough=0.4)
    for z in (0.012, 0.04, 0.068):
        box(name+'_cl', (0.12, 0.001, 0.003), loc=(-0.25, -T/2-0.0042, z), bevel=0, m=dark, parent=root)
    box(name+'_cv', (0.003, 0.001, 0.092), loc=(-0.25, -T/2-0.0042, 0.04), bevel=0, m=dark, parent=root)
    # symbole sans contact générique : 3 arcs
    for i, r in enumerate((0.022, 0.038, 0.054)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.0028, location=(0.29, -T/2-0.0015, 0.12), rotation=(math.pi/2, 0, 0))
        a = bpy.context.object; a.parent = root; a.data.materials.append(gold)
        bm_cut = a.modifiers.new('cut', 'BOOLEAN');
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.29-0.06, -T/2, 0.12)); cut = bpy.context.object; cut.scale = (0.12, 0.05, 0.2); cut.hide_render = True; cut.display_type = 'WIRE'; cut.parent = root
        bm_cut.object = cut; bm_cut.operation = 'DIFFERENCE'
    # liseré or en relief
    return root

def terminal(parent=None):
    root = objs.empty('term')
    body = mat('term', (0.008, 0.009, 0.011), metal=0.0, rough=0.5, coat=0.3)
    slab('t_body', 0.72, 1.25, 0.22, 0.09, m=body, parent=root, edge=0.02)
    scr = slab('t_scr', 0.56, 0.4, 0.002, 0.03, loc=(0, -0.112, 0.33), parent=root, edge=0)
    planar_uv(scr, 0.56, 0.4); scr.data.materials.append(img_mat('scr', f'{D}/tex_screen.png', metal=0, rough=0.1, emit=1.6))
    keym = mat('key', (0.03, 0.032, 0.038), rough=0.32)
    for r in range(4):
        for cc in range(3):
            slab('t_k', 0.14, 0.08, 0.02, 0.02, loc=(-0.17+cc*0.17, -0.115, -0.03-r*0.11), m=keym, parent=root, edge=0.004)
    return root

def softbox(name, loc, rot, size, strength, color, sy=None, cam=False):
    """panneau émissif : n'apparaît que dans les reflets (invisible à la caméra)"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot); p = bpy.context.object; p.name = name
    p.scale = (size, sy or size, 1)
    m = bpy.data.materials.new(name+'m'); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1); em.inputs['Strength'].default_value = strength
    # dégradé doux sur le panneau pour des reflets « produit »
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs[1].default_value = 0.0; mr.inputs[2].default_value = 1.0; mr.inputs[3].default_value = 0.15; mr.inputs[4].default_value = 1.0
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Y'], mr.inputs[0]); nt.links.new(mr.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], em.inputs['Strength'])
    nt.links.new(em.outputs[0], out.inputs[0]); p.data.materials.append(m)
    p.visible_camera = cam; p.visible_shadow = False; p.visible_diffuse = False; p.visible_volume_scatter = False; p.visible_transmission = False
    return p

def studio(exposure=-0.6):
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.0, 0.0, 0.0, 1); w.inputs[1].default_value = 0.0
    sc.view_settings.exposure = exposure
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    # cyclorama : sol + courbe + fond, sans ligne d'horizon
    import bmesh
    me = bpy.data.meshes.new('cyc'); bm = bmesh.new(); R = 3.0
    prof = [(y, 0.0) for y in (-10, -4, 0.0)]
    for k in range(1, 25): a = math.radians(90*k/24); prof.append((R*math.sin(a), R-R*math.cos(a)))
    prof += [(R, R+6)]
    vs = [[bm.verts.new((x, y+2.5, z-1.2)) for y, z in prof] for x in (-15, 15)]
    for j in range(len(prof)-1): bm.faces.new((vs[0][j], vs[0][j+1], vs[1][j+1], vs[1][j]))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('cyc', me); bpy.context.collection.objects.link(o)
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(mat('cycm', (0.006, 0.01, 0.026), rough=0.5))
    def area(loc, rot, size, e, col, sy=None, spread=None):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = e; l.data.color = col
        if sy: l.data.shape = 'RECTANGLE'; l.data.size_y = sy
        if spread: l.data.spread = math.radians(spread)
        return l
    # halo bleu nuit sur le fond, derrière le sujet
    area((0, 1.4, -1.05), (math.radians(112), 0, 0), 1.5, 300, (0.22, 0.4, 1.0), spread=70)
    # grande boîte à lumière douce au-dessus (clé), lumière directe faible
    area((0, -1.6, 2.6), (math.radians(32), 0, 0), 1.6, 60, (0.9, 0.93, 1.0), sy=0.8, spread=28)
    # deux fins strips dorés en contre-jour : liserés nets sur les tranches
    area((2.2, 1.4, 0.6), (math.radians(90), 0, math.radians(125)), 0.12, 160, (1.0, 0.74, 0.42), sy=3.5)
    area((-2.2, 1.4, 0.6), (math.radians(90), 0, math.radians(-125)), 0.12, 130, (1.0, 0.70, 0.40), sy=3.5)
    # panneaux de reflet (invisibles à la caméra) : dégradés propres sur le métal
    softbox('sb_top', (0, -1.6, 2.2), (math.radians(40), 0, 0), 3.2, 3.0, (0.85, 0.9, 1.0), sy=1.1)
    softbox('sb_gold', (2.4, -0.8, 0.4), (math.radians(90), 0, math.radians(60)), 0.35, 6.0, (1.0, 0.72, 0.4), sy=2.6)
    softbox('sb_cool', (-2.4, -1.0, 0.6), (math.radians(90), 0, math.radians(-60)), 0.6, 1.5, (0.5, 0.65, 1.0), sy=2.4)
    return sc

def camera(loc, look, lens=50):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; c.data.lens = lens
    d = [look[i]-loc[i] for i in range(3)]
    c.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0])-math.pi/2)
    bpy.context.scene.camera = c; c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 2.8
    c.data.dof.focus_distance = math.dist(loc, look); return c

def link_softboxes():
    """les panneaux de reflet n'éclairent que les objets héros, pas le sol"""
    hero = bpy.data.collections.new('hero'); bpy.context.scene.collection.children.link(hero)
    for o in bpy.data.objects:
        if o.type == 'MESH' and not o.name.startswith(('cyc', 'sb_')): hero.objects.link(o)
    for o in bpy.data.objects:
        if o.name.startswith('sb_'): o.light_linking.receiver_collection = hero

def render(path, rx=540, ry=960, samples=24):
    link_softboxes()
    sc = bpy.context.scene; sc.render.resolution_x = rx; sc.render.resolution_y = ry; sc.cycles.samples = samples; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    textures()
    which = sys.argv[1]
    if which == 'k1':   # carte qui vient taper le terminal
        studio(); t = terminal(); t.location = (0.15, 0.3, -0.5); t.rotation_euler = (math.radians(-28), 0, math.radians(-12))
        c = card(); c.location = (-0.15, -0.25, 0.42); c.rotation_euler = (math.radians(-55), math.radians(18), math.radians(-20))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.006, location=(0.12, 0.05, 0.02), rotation=(math.radians(62), 0, math.radians(-12)))
        bpy.context.object.data.materials.append(mat('ring', (1.0, 0.75, 0.4), emit=8))
        camera((0.2, -3.6, 0.55), (0, 0, 0.0), 50)
    elif which == 'k2':  # carte héroïque en gros plan
        studio(-0.4); c = card(); c.location = (0, 0, 0.1); c.rotation_euler = (math.radians(-12), math.radians(-10), math.radians(22))
        camera((0.3, -3.0, 0.45), (0, 0, 0.05), 60)
    elif which == 'k3':  # pile de cartes / révélation
        studio(-0.5)
        for i in range(9):
            c = card(f'c{i}'); c.location = (random.uniform(-.02, .02), 0, -1.2+0.006+i*0.0135); c.rotation_euler = (math.pi/2, 0, math.radians(random.uniform(-14, 14)))
        c = card('hero'); c.location = (0.05, -0.1, -0.05); c.rotation_euler = (math.radians(-10), math.radians(-8), math.radians(15))
        camera((0.25, -2.6, 0.3), (0, 0, -0.5), 45)
    render(f'{D}/kf_{which}.png', 540, 960, int(os.environ.get('S', '24')))
