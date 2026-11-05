"""Rendus Blender (Cycles) des éléments « argent » de la vidéo dividendes : pièce d'or qui tournoie, billet qui ondule,
sac de pièces, piles de pièces et parterre de pièces et billets. Textures (relief de la pièce, billet générique) dessinées en PIL.
usage : python3 b3d_argent.py textures | coin | bill | bag | stack | heap   (sorties dans assets/)"""
import sys, os, math, random
D = os.path.dirname(os.path.abspath(__file__)); A = f'{D}/assets'; os.makedirs(A, exist_ok=True)
SAMPLES = int(os.environ.get('SAMPLES', '64'))

# ---------- textures ----------
def textures():
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    F = '/home/claude/actions_benefices/fonts/InterDisplay-Black.otf'
    # relief de la face de la pièce (blanc = en relief) : listel, grènetis, couronne d'étoiles, « € »
    S = 1024; im = Image.new('L', (S, S), 90); d = ImageDraw.Draw(im); c = S/2
    d.ellipse((8, 8, S-8, S-8), fill=230); d.ellipse((60, 60, S-60, S-60), fill=90)
    for k in range(120):
        a = k/120*2*math.pi; x, y = c+430*math.cos(a), c+430*math.sin(a); d.ellipse((x-9, y-9, x+9, y+9), fill=200)
    for k in range(12):
        a = k/12*2*math.pi-math.pi/2; x, y = c+340*math.cos(a), c+340*math.sin(a); r = 26
        pts = [(x+r*math.cos(a2+i*2*math.pi/10)*(1 if i % 2 == 0 else .45), y+r*math.sin(a2+i*2*math.pi/10)*(1 if i % 2 == 0 else .45)) for i, a2 in [(i, -math.pi/2) for i in range(10)]]
        d.polygon(pts, fill=215)
    f = ImageFont.truetype(F, 470); w = d.textlength('€', font=f); d.text((c-w/2, c-300), '€', font=f, fill=240)
    im = im.filter(ImageFilter.GaussianBlur(3)); im.save(f'{A}/tex_coin_bump.png')
    # billet générique (pas un vrai billet) : fond dégradé, rosaces guillochées, « 100 », « € »
    Wb, Hb = 1400, 720; b = Image.new('RGB', (Wb, Hb)); px = b.load()
    for y in range(Hb):
        for x in range(0, Wb):
            t = x/Wb; px[x, y] = (int(28+40*t), int(92+38*t), int(52+20*t))
    d = ImageDraw.Draw(b)
    for (cx, cy, R) in ((330, 360, 250), (1080, 360, 200)):
        for k in range(90):
            a = k/90*2*math.pi; pts = []
            for j in range(0, 361, 6):
                th = math.radians(j); r = R*(.55+.45*math.cos(5*th+a))
                pts.append((cx+r*math.cos(th+a*.1), cy+r*math.sin(th+a*.1)))
            d.line(pts, fill=(150, 205, 150), width=2)
    for y in range(40, Hb-40, 9): d.line([(40, y), (Wb-40, y)], fill=(95, 150, 105), width=1)
    d.rectangle((24, 24, Wb-24, Hb-24), outline=(225, 240, 210), width=10); d.rectangle((46, 46, Wb-46, Hb-46), outline=(160, 200, 150), width=3)
    f = ImageFont.truetype(F, 210); d.text((60, 40), '100', font=f, fill=(235, 245, 225)); d.text((Wb-430, Hb-260), '100', font=f, fill=(235, 245, 225))
    f2 = ImageFont.truetype(F, 330); d.text((620, 150), '€', font=f2, fill=(240, 220, 140))
    b.save(f'{A}/tex_bill.png')
    # toile de jute du sac
    s = Image.new('RGB', (512, 512), (150, 112, 68)); d = ImageDraw.Draw(s)
    for i in range(0, 512, 4): d.line([(i, 0), (i, 512)], fill=(130, 95, 55)); d.line([(0, i), (512, i)], fill=(165, 125, 78))
    f = ImageFont.truetype(F, 260); d.text((150, 110), '€', font=f, fill=(60, 40, 20)); s.save(f'{A}/tex_bag.png')
    print('textures ok')

# ---------- scène Blender ----------
def scene(rx, ry):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.05, 0.035, 0.02, 1); bg.inputs[1].default_value = 1.0
    def area(loc, rot, size, energy, colr):
        L = bpy.data.lights.new('l', 'AREA'); L.size = size; L.energy = energy; L.color = colr
        o = bpy.data.objects.new('l', L); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    # environnement de studio : dégradé chaud (haut clair, bas sombre) pour que l'or ait des reflets riches
    nt = w.node_tree; tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = .45; ramp.color_ramp.elements[0].color = (0.02, 0.012, 0.006, 1); ramp.color_ramp.elements[1].position = .62; ramp.color_ramp.elements[1].color = (1.0, 0.85, 0.6, 1)
    e = ramp.color_ramp.elements.new(.8); e.color = (0.25, 0.16, 0.08, 1); e2 = ramp.color_ramp.elements.new(.95); e2.color = (1.2, 1.05, .9, 1)
    nt.links.new(ramp.outputs['Color'], bg.inputs[0]); bg.inputs[1].default_value = 1.6
    area((-3, -4, 5), (math.radians(50), 0, math.radians(-35)), 4, 900, (1, .92, .8))      # lumière clé chaude (poursuite)
    area((4, -2, 2), (math.radians(70), 0, math.radians(60)), 3, 300, (.8, .85, 1))       # contre froid
    area((0, 4, 3), (math.radians(-60), 0, math.radians(180)), 3, 500, (1, .85, .6))       # liseré arrière
    return sc
def gold(name='gold', bump=True, tint=(1.0, 0.66, 0.16)):
    import bpy
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tint, 1); b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.17
    if bump:
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (.5, .5, 0)
        im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_coin_bump.png'); im.image.colorspace_settings.name = 'Non-Color'; im.extension = 'CLIP'
        bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .9; bu.inputs['Distance'].default_value = .02
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], im.inputs['Vector']); nt.links.new(im.outputs['Color'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m
def coin_obj(name='coin', mat=None, r=.5, t=.075, verts=96, bev=.012, seg=3):
    import bpy, bmesh
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=t); o = bpy.context.active_object; o.name = name
    mod = o.modifiers.new('bev', 'BEVEL'); mod.width = bev; mod.segments = seg; mod.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth()
    # cannelures sur la tranche (léger relief par un deuxième matériau rugueux) : on garde simple, la bump fait la face
    o.data.materials.append(mat or gold()); return o
def cam(sc, loc, look, lens=50, ortho=None):
    import bpy, mathutils
    c = bpy.data.cameras.new('c'); c.lens = lens
    if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new('c', c); o.location = loc; sc.collection.objects.link(o); sc.camera = o
    d = mathutils.Vector(look)-mathutils.Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return o

def r_coin():
    sc = scene(224, 224); o = coin_obj(); cam(sc, (0, -3.2, 0), (0, 0, 0), lens=60)
    N = 36; sc.frame_start, sc.frame_end = 1, N
    for f in range(1, N+1):
        u = (f-1)/N; o.rotation_euler = (math.radians(90)+2*math.pi*u, 2*math.pi*u*.5, math.radians(20)); o.keyframe_insert('rotation_euler', frame=f)
    for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action, 'fcurves') else []:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    sc.render.filepath = f'{A}/coin_'; import bpy; bpy.ops.render.render(animation=True); print('coin ok')
def r_bill():
    import bpy
    sc = scene(300, 220); bpy.ops.mesh.primitive_plane_add(size=1); o = bpy.context.active_object; o.scale = (1.4, .72, 1)
    bpy.ops.object.transform_apply(scale=True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=40); bpy.ops.object.mode_set(mode='OBJECT')
    m = bpy.data.materials.new('bill'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bill.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .55
    try: b.inputs['Sheen Weight'].default_value = .3
    except Exception: pass
    o.data.materials.append(m)
    sd = o.modifiers.new('b', 'SIMPLE_DEFORM'); sd.deform_method = 'BEND'; sd.deform_axis = 'Y'; sd.angle = math.radians(50)
    tw_ = o.modifiers.new('t', 'SIMPLE_DEFORM'); tw_.deform_method = 'TWIST'; tw_.deform_axis = 'X'; tw_.angle = math.radians(25)
    cam(sc, (0, -2.6, 1.4), (0, 0, 0), lens=55)
    N = 36; sc.frame_start, sc.frame_end = 1, N
    for f in range(1, N+1):
        u = (f-1)/N; o.rotation_euler = (math.radians(20)*math.sin(2*math.pi*u), math.radians(25)*math.sin(2*math.pi*u+1), 2*math.pi*u*.25); o.keyframe_insert('rotation_euler', frame=f)
    sc.render.filepath = f'{A}/bill_'; bpy.ops.render.render(animation=True); print('bill ok')
def r_bag():
    import bpy
    sc = scene(280, 320)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48, radius=.5); o = bpy.context.active_object
    for v in o.data.vertices:
        z = v.co.z; k = 1.0
        if z < -.3: k = 1-(-.3-z)*1.2                     # fond aplati
        if z > .18: k = max(.18, 1-((z-.18)/.32)**1.4*.85)   # col resserré
        if z > .42: k = .18+(z-.42)*3.2                     # collerette qui s'ouvre
        v.co.x *= k*1.05; v.co.y *= k
        if z < -.42: v.co.z = -.42+(z+.42)*.3
    tex = bpy.data.textures.new('n', 'CLOUDS'); tex.noise_scale = .18; d = o.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.strength = .035
    sub = o.modifiers.new('s', 'SUBSURF'); sub.levels = 1; bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=.11, minor_radius=.03, location=(0, 0, .43)); tie = bpy.context.active_object; bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new('jute'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bag.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .9
    o.data.materials.append(m); o.rotation_euler = (0, 0, math.radians(-90))
    rope = bpy.data.materials.new('rope'); rope.use_nodes = True; rope.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.55, .08, .06, 1); tie.data.materials.append(rope)
    cam(sc, (0, -3.0, .55), (0, 0, .02), lens=52); sc.render.filepath = f'{A}/bag.png'; bpy.ops.render.render(write_still=True); print('bag ok')
def r_stack():
    import bpy
    sc = scene(420, 1500); g = gold(); random.seed(3); t = .06
    proto = coin_obj('proto', g, t=t, verts=192, bev=.024, seg=8)
    for i in range(95):
        o = proto.copy(); o.data = proto.data; sc.collection.objects.link(o); o.location = (random.uniform(-.012, .012), random.uniform(-.012, .012), i*t*1.02); o.rotation_euler = (0, 0, random.uniform(0, 6.3))
    proto.hide_render = True
    H = 95*t*1.02; cam(sc, (0, -13, H+3.4), (0, 0, H*.52), lens=85)
    sc.render.filepath = f'{A}/stack.png'; bpy.ops.render.render(write_still=True); print('stack ok')
def r_heap():
    import bpy
    sc = scene(1080, 560); g = gold(); random.seed(7)
    bpy.ops.mesh.primitive_plane_add(size=1); bill = bpy.context.active_object; bill.scale = (1.4*.55, .72*.55, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=10); bpy.ops.object.mode_set(mode='OBJECT')
    m = bpy.data.materials.new('bill'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bill.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .6; bill.data.materials.append(m)
    sd = bill.modifiers.new('b', 'SIMPLE_DEFORM'); sd.deform_method = 'BEND'; sd.angle = math.radians(35); sd.deform_axis = 'Y'
    base = coin_obj('base', g, r=.28, t=.045)
    def mound(x, y): return max(0, 1.1*math.exp(-(x/6.5)**2-(y/2.2)**2))
    for i in range(1500):
        x = random.uniform(-7.5, 7.5); y = random.uniform(-2.5, 2.5); z = mound(x, y)*random.uniform(.6, 1)
        if random.random() < .12: o = bill.copy(); o.data = bill.data; o.modifiers.new('b', 'SIMPLE_DEFORM').angle = math.radians(random.uniform(-40, 40))
        else: o = base.copy(); o.data = base.data
        sc.collection.objects.link(o); o.location = (x, y, z); o.rotation_euler = (random.uniform(-.6, .6), random.uniform(-.6, .6), random.uniform(0, 6.3))
    bill.hide_render = True; base.hide_render = True
    c = cam(sc, (0, -11, 2.6), (0, 0, .3), lens=55); c.data.dof.use_dof = True; c.data.dof.focus_distance = 11; c.data.dof.aperture_fstop = 2.2
    sc.render.filepath = f'{A}/heap.png'; bpy.ops.render.render(write_still=True); print('heap ok')
def r_heap_stages():
    """parterre qui se constitue : objets à hauteur fixe z = mound × u ; l'étape s montre ceux dont u ≤ s (le tas grandit sans que rien ne bouge)"""
    import bpy
    sc = scene(1080, 560); g = gold(); random.seed(7); sc.render.use_persistent_data = True
    bpy.ops.mesh.primitive_plane_add(size=1); bill = bpy.context.active_object; bill.scale = (1.4*.55, .72*.55, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=10); bpy.ops.object.mode_set(mode='OBJECT')
    m = bpy.data.materials.new('bill'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bill.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .6; bill.data.materials.append(m)
    base = coin_obj('base', g, r=.28, t=.045)
    def mound(x, y): return max(0, 1.1*math.exp(-(x/6.5)**2-(y/2.2)**2))
    objs = []
    for i in range(3200):
        x = random.uniform(-7.5, 7.5); y = random.uniform(-2.5, 2.5); u = random.random()**.7; z = .02+mound(x, y)*u
        if random.random() < .12: o = bill.copy(); o.data = bill.data; md = o.modifiers.new('b', 'SIMPLE_DEFORM'); md.deform_method = 'BEND'; md.deform_axis = 'Y'; md.angle = math.radians(random.uniform(-40, 40))
        else: o = base.copy(); o.data = base.data
        sc.collection.objects.link(o); o.location = (x, y, z); o.rotation_euler = (random.uniform(-.6, .6), random.uniform(-.6, .6), random.uniform(0, 6.3)); objs.append((u, o))
    bill.hide_render = True; base.hide_render = True
    c = cam(sc, (0, -11, 2.6), (0, 0, .3), lens=55); c.data.dof.use_dof = True; c.data.dof.focus_distance = 11; c.data.dof.aperture_fstop = 2.2
    N = int(os.environ.get('STAGES', '10'))
    for k in range(1, N+1):
        s_ = k/N
        for u, o in objs: o.hide_render = u > s_
        sc.render.filepath = f'{A}/heap_{k:02d}.png'; bpy.ops.render.render(write_still=True); print('stage', k, flush=True)
    print('heap stages ok')
if __name__ == '__main__':
    {'textures': textures, 'coin': r_coin, 'bill': r_bill, 'bag': r_bag, 'stack': r_stack, 'heap': r_heap, 'heapst': r_heap_stages}[sys.argv[1]]()
