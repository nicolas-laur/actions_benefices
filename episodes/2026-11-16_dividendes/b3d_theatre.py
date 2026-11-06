"""Décor 3D (Cycles) de la vidéo dividendes : scène de théâtre (rideaux de velours plissés, lambrequin, plancher en bois verni,
rampe de lumière), poursuite volumétrique rendue à part (décalée en compositing pour suivre Mister Coin), parterre de pièces et billets
en 10 étapes de croissance au premier plan, boucle de 8 s d'argent qui tombe (flou de profondeur et de mouvement).
Même caméra pour toutes les passes : Mister Coin (pieds vers y = 1660 à l'écran) se tient au centre de la scène.
usage : python3 b3d_theatre.py plateA | plateB | heap | money"""
import sys, os, math, random
D = os.path.dirname(os.path.abspath(__file__)); A = f'{D}/assets'; T = f'{D}/assets/theatre'; os.makedirs(T, exist_ok=True)
sys.path.insert(0, D)
import b3d_argent as BA
SAMPLES = int(os.environ.get('SAMPLES', '96'))

def base_scene(rx=1080, ry=1920, transparent=False):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.render.film_transparent = transparent
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.color_depth = '16'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.003, 0.003, 1)
    return sc
def camera(sc):
    import bpy, mathutils
    c = bpy.data.cameras.new('cam'); c.lens = 32; c.sensor_fit = 'VERTICAL'; c.sensor_height = 24
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); sc.camera = o
    o.location = (0, -13.0, 2.2); target = mathutils.Vector((0, 0, 3.55))
    o.rotation_euler = (target-o.location).to_track_quat('-Z', 'Y').to_euler()
    c.dof.use_dof = True; c.dof.focus_distance = 13.0; c.dof.aperture_fstop = 4.0
    return o
def velvet(name, col=(0.30, 0.012, 0.028)):
    import bpy
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = .62
    b.inputs['Sheen Weight'].default_value = 1.0; b.inputs['Sheen Roughness'].default_value = .35; b.inputs['Sheen Tint'].default_value = (1, .55, .5, 1)
    b.inputs['Specular IOR Level'].default_value = .25
    # léger grain du tissu
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 400; bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .08
    nt.links.new(nz.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m
def drape(name, x0, x1, z0, z1, y, folds, amp, mat, scallop=0.0, res=900):
    """rideau : plan plissé verticalement (amplitude variable) ; scallop > 0 : bas en festons (lambrequin)"""
    import bpy, bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new(); nx = res; nz = 40 if scallop == 0 else 90
    rnd = random.Random(hash(name) % 1000)
    WAVES = [(1.0, folds*rnd.uniform(.9, 1.1), rnd.uniform(0, 6.28)), (.55, folds*rnd.uniform(1.7, 2.2), rnd.uniform(0, 6.28)), (.3, folds*rnd.uniform(.35, .5), rnd.uniform(0, 6.28)), (.18, folds*rnd.uniform(3.1, 3.7), rnd.uniform(0, 6.28))]
    verts = []
    for j in range(nz+1):
        row = []
        for i in range(nx+1):
            u = i/nx; v = j/nz; x = x0+(x1-x0)*u; z = z0+(z1-z0)*v
            a = amp*(.8+.2*v if scallop == 0 else 1)*(1.15-.3*v)
            yy = y+sum(c_*math.sin(2*math.pi*fq*x+ph_) for (c_, fq, ph_) in WAVES)*a
            if scallop:
                per = (x1-x0)/scallop; uu = ((x-x0) % per)/per
                zb = z0+1.05*(1-(2*uu-1)**2)                                       # festons arrondis
                z = zb+(z1-zb)*v; yy -= .25*math.sin(math.pi*uu)*(1-v)
            row.append(bm.verts.new((x, yy, z)))
        verts.append(row)
    for j in range(nz):
        for i in range(nx): bm.faces.new((verts[j][i], verts[j][i+1], verts[j+1][i+1], verts[j+1][i]))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); return o
def floor_mat():
    import bpy
    m = bpy.data.materials.new('plancher'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 6, 1)
    br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.2; br.inputs['Mortar Size'].default_value = .004; br.offset = .5; br.squash = 1
    br.inputs['Color1'].default_value = (.20, .09, .035, 1); br.inputs['Color2'].default_value = (.13, .055, .02, 1); br.inputs['Mortar'].default_value = (.02, .01, .005, 1)
    br.inputs['Brick Width'].default_value = 2.4; br.inputs['Row Height'].default_value = .14
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3; wv.inputs['Distortion'].default_value = 8; wv.inputs['Detail'].default_value = 4
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = .35
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], br.inputs['Vector']); nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    nt.links.new(br.outputs['Color'], mix.inputs['A']); nt.links.new(wv.outputs['Color'], mix.inputs['B']); nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = .38; b.inputs['Coat Weight'].default_value = .7; b.inputs['Coat Roughness'].default_value = .12
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .25; nt.links.new(br.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m
def build_stage():
    import bpy
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -1, 0)); fl = bpy.context.active_object; fl.scale = (24, 14, 1); fl.data.materials.append(floor_mat())
    vb = velvet('velours'); vd = velvet('velours_sombre', (0.18, 0.008, 0.016))
    drape('fond', -7, 7, 0, 11, 4.5, 1.15, .22, vb)                                # rideau de fond
    drape('jambe_g', -6, -2.35, 0, 11, 1.4, 1.3, .3, vd); drape('jambe_d', 2.35, 6, 0, 11, 1.4, 1.3, .3, vd)
    drape('lambrequin', -6, 6, 7.2, 10, .9, 1.4, .2, vb, scallop=4)
    # bord de scène et rampe de lumière (ampoules chaudes)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.6, -.25)); e = bpy.context.active_object; e.scale = (24, .3, .5)
    m = bpy.data.materials.new('bord'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.05, .02, .01, 1); e.data.materials.append(m)
def lights_ambient():
    import bpy
    sc = bpy.context.scene; out = []
    def area(loc, rot, size, energy, colr, name):
        L = bpy.data.lights.new(name, 'AREA'); L.size = size; L.energy = energy; L.color = colr
        o = bpy.data.objects.new(name, L); o.location = loc; o.rotation_euler = rot; o.visible_camera = False; sc.collection.objects.link(o); out.append(o); return o
    for x in (-5, -2.5, 0, 2.5, 5):                                                 # rampe : lumière rasante qui monte sur le velours
        area((x, -4.5, .15), (math.radians(-70), 0, 0), 1.2, 160, (1, .72, .42), f'rampe{x}')
    area((0, -6, 9), (math.radians(35), 0, 0), 8, 260, (1, .55, .45), 'face')        # face très douce
    area((-7, 2, 6), (math.radians(60), 0, math.radians(-120)), 3, 220, (1, .5, .35), 'cote_g')
    area((7, 2, 6), (math.radians(60), 0, math.radians(120)), 3, 220, (1, .5, .35), 'cote_d')
    return out
def light_spot():
    import bpy, mathutils
    sc = bpy.context.scene
    L = bpy.data.lights.new('poursuite', 'SPOT'); L.energy = 5200; L.spot_size = math.radians(16); L.spot_blend = .35; L.color = (1, .88, .7); L.shadow_soft_size = .15
    o = bpy.data.objects.new('poursuite', L); sc.collection.objects.link(o); o.location = (0, -9, 12)
    o.rotation_euler = (mathutils.Vector((0, 0, 0))-o.location).to_track_quat('-Z', 'Y').to_euler(); return o
def volume_box():
    import bpy
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2, 6)); v = bpy.context.active_object; v.scale = (20, 16, 13)
    m = bpy.data.materials.new('air'); m.use_nodes = True; nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    pv = nt.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Density'].default_value = .028; pv.inputs['Anisotropy'].default_value = .35
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = .6; nz.inputs['Detail'].default_value = 3
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = .012; mr.inputs['To Max'].default_value = .045
    nt.links.new(nz.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], pv.inputs['Density'])
    nt.links.new(pv.outputs['Volume'], nt.nodes['Material Output'].inputs['Volume']); v.data.materials.append(m)
def check_feet():
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    import mathutils
    sc = bpy.context.scene; p = world_to_camera_view(sc, sc.camera, mathutils.Vector((0, 0, 0)))
    print('pieds à l\'écran : y =', round((1-p.y)*sc.render.resolution_y), flush=True)

def plateA():
    import bpy
    sc = base_scene(); camera(sc); build_stage(); lights_ambient(); check_feet()
    sc.render.filepath = f'{T}/plateA.png'; bpy.ops.render.render(write_still=True); print('plateA ok')
def plateB():
    """poursuite seule (faisceau dans l'air + tache au sol et sur le rideau), demi-résolution : elle est douce"""
    import bpy
    sc = base_scene(540, 960); camera(sc); build_stage(); light_spot(); volume_box()
    sc.cycles.volume_step_rate = 4; sc.render.filepath = f'{T}/plateB.png'; bpy.ops.render.render(write_still=True); print('plateB ok')
def heap():
    """parterre au premier plan (y = −5 … −2,5), flou de profondeur, éclairé comme la scène ; 10 étapes"""
    import bpy
    sc = base_scene(1080, 1920, transparent=True); camera(sc); lights_ambient(); sp = light_spot(); sp.data.spot_size = math.radians(40)
    sc.render.use_border = True; sc.render.border_min_y = 0.0; sc.render.border_max_y = .34; sc.render.use_crop_to_border = False
    BA.textures() if not os.path.exists(f'{A}/tex_bill.png') else None
    g = BA.gold(); random.seed(11)
    bpy.ops.mesh.primitive_plane_add(size=1); bill = bpy.context.active_object; bill.scale = (1.4*.42, .72*.42, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=10); bpy.ops.object.mode_set(mode='OBJECT')
    m = bpy.data.materials.new('bill'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bill.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .55; bill.data.materials.append(m)
    coin = BA.coin_obj('base', g, r=.2, t=.03, verts=96, bev=.012, seg=4)
    def mound(x, y): return max(0, 1.0*math.exp(-(x/5.0)**2-((y+3.6)/1.1)**2))
    objs = []
    for i in range(4200):
        x = random.uniform(-6.5, 6.5); y = random.uniform(-5.6, -2.2); u = random.random()**.7; z = .02+mound(x, y)*u
        if mound(x, y) < .03 and random.random() < .7: continue
        if random.random() < .1:
            o = bill.copy(); o.data = bill.data; md = o.modifiers.new('b', 'SIMPLE_DEFORM'); md.deform_method = 'BEND'; md.deform_axis = 'Y'; md.angle = math.radians(random.uniform(-40, 40))
        else: o = coin.copy(); o.data = coin.data
        sc.collection.objects.link(o); o.location = (x, y, z); o.rotation_euler = (random.uniform(-.6, .6), random.uniform(-.6, .6), random.uniform(0, 6.3)); objs.append((u, o))
    bill.hide_render = coin.hide_render = True
    N = int(os.environ.get('STAGES', '10'))
    for k in range(1, N+1):
        for u, o in objs: o.hide_render = u > k/N
        sc.render.filepath = f'{T}/heap_{k:02d}.png'; bpy.ops.render.render(write_still=True); print('stage', k, flush=True)
    print('heap ok')
def money():
    """boucle de 8 s (30 i/s) d'argent qui tombe derrière Mister Coin (y = 1,5 … 4) ; tout est périodique pour boucler sans raccord"""
    import bpy
    sc = base_scene(540, 960, transparent=True); camera(sc); lights_ambient(); sp = light_spot(); sp.data.spot_size = math.radians(55); sp.data.energy = 3000
    sc.render.fps = 30; Tn = 240; sc.frame_start, sc.frame_end = 0, Tn-1
    sc.render.use_motion_blur = False                                             # le retour en haut ferait une traînée
    g = BA.gold(); random.seed(5)
    bpy.ops.mesh.primitive_plane_add(size=1); bill = bpy.context.active_object; bill.scale = (1.4*.5, .72*.5, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=12); bpy.ops.object.mode_set(mode='OBJECT')
    m = bpy.data.materials.new('bill'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{A}/tex_bill.png')
    nt.links.new(im.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .55; bill.data.materials.append(m)
    coin = BA.coin_obj('base', g, r=.24, t=.035, verts=96, bev=.014, seg=4)
    H0, H1 = 13.5, -.5; span = H0-H1
    for i in range(70):
        kind = 'b' if random.random() < .22 else 'c'; o = (bill if kind == 'b' else coin).copy(); o.data = (bill if kind == 'b' else coin).data
        if kind == 'b': md = o.modifiers.new('b', 'SIMPLE_DEFORM'); md.deform_method = 'BEND'; md.deform_axis = 'Y'; md.angle = math.radians(random.uniform(20, 45))
        sc.collection.objects.link(o); x0 = random.uniform(-6, 6); y0 = random.uniform(1.5, 4.0); ph = random.random()
        laps = 1 if kind == 'b' else random.choice([3, 4])                         # tours de chute sur la boucle : billets lents, pièces rapides
        sw = random.choice([2, 3]); sp_ = random.choice([2, 3, 4])
        for f in range(Tn+1):
            u = f/Tn; z = H0-((ph+u*laps) % 1.0)*span
            if kind == 'b':
                th = 2*math.pi*(u*sw*laps+ph); o.location = (x0+.8*math.sin(th), y0, z+.12*math.cos(2*th)); o.rotation_euler = (math.radians(30)*math.cos(th), math.radians(18)*math.sin(th), th*.25)
            else:
                th = 2*math.pi*(u*sp_+ph); o.location = (x0, y0, z); o.rotation_euler = (th, th*.5, ph*6)
            o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
        # pas d'interpolation fantôme au moment où l'objet revient en haut (il est alors hors champ)
    bill.hide_render = coin.hide_render = True
    sc.render.filepath = f'{T}/money_'; bpy.ops.render.render(animation=True); print('money ok')
if __name__ == '__main__':
    {'plateA': plateA, 'plateB': plateB, 'heap': heap, 'money': money}[sys.argv[1]]()
