"""Coca-Cola : verre droit générique (aucune forme ni marque déposée) qui se remplit de cola, puis gros plan sur les bulles.
plans :  fill = remplissage (non bouclé, NFILL images) ;  bub = macro des bulles qui montent dans le liquide (boucle NB images)
usage : python glass.py <fill|bub> <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/aapl/b3d'); sys.path.insert(0, '/home/claude/amzn/b3d')
import objs
from objs import mat
NFILL = 96; NB = 120; TAU = 2*math.pi

def glass_mat():
    m = bpy.data.materials.new('glass'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (1, 1, 1, 1); b.inputs['Roughness'].default_value = 0.02; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.5
    return m
def cola_mat(density=40.0):
    m = bpy.data.materials.new('cola'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    b.inputs['Base Color'].default_value = (0.9, 0.45, 0.2, 1); b.inputs['Roughness'].default_value = 0.03; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.34
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption'); vol.inputs['Color'].default_value = (0.62, 0.3, 0.08, 1); vol.inputs['Density'].default_value = density
    L(vol.outputs[0], nt.nodes['Material Output'].inputs['Volume']); return m
def foam_mat():
    m = bpy.data.materials.new('foam'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.78, 0.58, 0.38, 1); b.inputs['Roughness'].default_value = .7
    b.inputs['Subsurface Weight'].default_value = .5; return m
def bubble_mat():
    m = bpy.data.materials.new('bub'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (1, 1, 1, 1); b.inputs['Roughness'].default_value = 0.0; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 0.75
    return m

def lights(sc):
    a = __import__('amz').area
    l0 = a((0, 3.0, 1.0), (math.radians(-85), 0, 0), 2.0, 700, (1, .55, .28))       # contre-jour ambré : fait briller le cola
    a((-2.6, -2, 2.4), (math.radians(55), 0, math.radians(-50)), 1.4, 260, (1, .97, .92))
    a((2.8, -1.2, 1.2), (math.radians(75), 0, math.radians(60)), 1.0, 160, (.6, .75, 1))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 4.5, 1.4), rotation=(math.radians(90), 0, 0)); g = bpy.context.object; g.scale = (6, 4, 1)
    g.data.materials.append(mat('bgglow', (1.0, 0.35, 0.12), emit=0.12))   # fond chaud dégradé (flou en profondeur de champ)
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            try: o.visible_camera = False
            except Exception: pass

def build(shot):
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.01, 0.006, 0.004, 1); w.inputs[1].default_value = 1
    sc.view_settings.exposure = -0.3; sc.cycles.transmission_bounces = 10; sc.cycles.max_bounces = 12; sc.cycles.volume_bounces = 2
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    lights(sc); rnd = random.Random(3)
    cola, foam, bub = cola_mat(), foam_mat(), bubble_mat()
    if shot == 'fill':
        # comptoir sombre brillant
        bpy.ops.mesh.primitive_plane_add(size=20); p = bpy.context.object; p.data.materials.append(mat('bar', (0.012, 0.009, 0.008), rough=.3, coat=.4))
        R, Hh = .42, 1.5
        # verre droit : cylindre creux (solidify) avec fond épais
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=R, depth=Hh, location=(0, 0, Hh/2)); g = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT'); import bmesh; bm = bmesh.from_edit_mesh(g.data)
        top = [f for f in bm.faces if f.normal.z > .9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bmesh.update_edit_mesh(g.data); bpy.ops.object.mode_set(mode='OBJECT')
        sd = g.modifiers.new('s', 'SOLIDIFY'); sd.thickness = .025; sd.offset = -1
        bv = g.modifiers.new('b', 'BEVEL'); bv.width = .008; bv.segments = 3
        g.data.materials.append(glass_mat()); bpy.ops.object.shade_smooth()
        # liquide qui monte + mousse au sommet
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=R-.03, depth=1, location=(0, 0, .5)); liq = bpy.context.object; liq.data.materials.append(cola); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=R-.03, depth=1, location=(0, 0, 0)); fo = bpy.context.object; fo.data.materials.append(foam)
        dm = fo.modifiers.new('d', 'DISPLACE'); tx = bpy.data.textures.new('fn', 'CLOUDS'); tx.noise_scale = .08; dm.texture = tx; dm.strength = .03
        sub = fo.modifiers.new('ss', 'SUBSURF'); sub.levels = 2; fo.modifiers.move(1, 0)
        # filet qui tombe du haut
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.045, depth=3, location=(.06, 0, 3)); st = bpy.context.object; st.data.materials.append(cola)
        sdm = st.modifiers.new('d', 'DISPLACE'); tx2 = bpy.data.textures.new('sn', 'CLOUDS'); tx2.noise_scale = .05; sdm.texture = tx2; sdm.strength = .02
        for f in range(1, NFILL+1):
            u = (f-1)/(NFILL-1); fill = 1-(1-min(1, u/.85))**2.2; h = .03+1.33*fill
            liq.scale = (1, 1, h); liq.location.z = .02+h/2; liq.keyframe_insert('scale', frame=f); liq.keyframe_insert('location', frame=f)
            fh = .04+.10*math.sin(min(1, u/.9)*math.pi*.8); fo.scale = (1, 1, fh); fo.location.z = .02+h+fh/2-.01; fo.keyframe_insert('scale', frame=f); fo.keyframe_insert('location', frame=f)
            on = 1.0 if u < .8 else max(0.0, 1-(u-.8)/.08)
            st.scale = (on, on, 1); st.location.z = .02+h+1.5 if on > 0 else 6; st.keyframe_insert('scale', frame=f); st.keyframe_insert('location', frame=f)
            tx.noise_basis = 'BLENDER_ORIGINAL'
        # bulles dans le liquide
        for i in range(70):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=rnd.uniform(.006, .016)); b_ = bpy.context.object; b_.data.materials.append(bub)
            x, y = rnd.uniform(-.3, .3), rnd.uniform(-.3, .3); ph = rnd.random(); sp = rnd.uniform(.5, 1.2)
            for f in range(1, NFILL+1, 3):
                u = (f-1)/(NFILL-1); h = .03+1.33*(1-(1-min(1, u/.85))**2.2)
                z = .05+((u*sp*3+ph) % 1)*max(.05, h-.08)
                b_.location = (x+.01*math.sin(f*.3+i), y, z); b_.keyframe_insert('location', frame=f)
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 50
        cam.location = (0, -4.6, 1.25); cam.rotation_euler = (math.radians(88), 0, 0)
        for f, (y, z) in ((1, (-4.8, 1.45)), (NFILL, (-4.2, 1.0))):
            cam.location = (0, y, z); cam.keyframe_insert('location', frame=f)
        cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 4.4; cam.data.dof.aperture_fstop = 2.8
        sc.frame_start, sc.frame_end = 1, NFILL
    else:
        # macro : on est DANS le cola, les bulles montent devant un contre-jour ambré
        for o in list(bpy.data.objects):
            if (o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('bgglow')) or (o.type == 'LIGHT' and o.data.size == 2.0):
                bpy.data.objects.remove(o)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.0, 0)); box_ = bpy.context.object; box_.scale = (6, 1.2, 8); box_.data.materials.append(cola_mat(4.5))
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 4.0, 0), rotation=(math.radians(90), 0, 0)); bk = bpy.context.object; bk.scale = (14, 14, 1)
        bm_ = bpy.data.materials.new('bk'); bm_.use_nodes = True; nt = bm_.node_tree; em = nt.nodes['Principled BSDF']; em.inputs['Base Color'].default_value = (0, 0, 0, 1)
        gt = nt.nodes.new('ShaderNodeTexGradient'); gt.gradient_type = 'SPHERICAL'; tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], gt.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = 9.0; nt.links.new(gt.outputs['Fac'], mr.inputs[0])
        em.inputs['Emission Color'].default_value = (1, .6, .3, 1); nt.links.new(mr.outputs[0], em.inputs['Emission Strength']); bk.data.materials.append(bm_)
        for i in range(160):
            r = rnd.uniform(.012, .07) if i % 9 else rnd.uniform(.09, .14)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r); b_ = bpy.context.object; b_.data.materials.append(bub); bpy.ops.object.shade_smooth()
            b_.scale = (1, 1, .92); x, y = rnd.uniform(-1.4, 1.4), rnd.uniform(.5, 1.5); ph = rnd.random(); cyc = rnd.choice((1, 2, 2, 3))
            for f in range(1, NB+2, 2):
                u = ((f-1)/NB*cyc+ph) % 1.0; z = -2.6+u*5.2
                b_.location = (x+.04*math.sin(u*TAU*3+i), y, z); b_.keyframe_insert('location', frame=f)
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 35
        cam.location = (0, -1.2, 0); cam.rotation_euler = (math.radians(90), 0, 0)
        cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 2.1; cam.data.dof.aperture_fstop = 2.2
        sc.frame_start, sc.frame_end = 1, NB
    sc.render.fps = 30
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; shot, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (432, 768, 24)
    sc = build(shot); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[5]) if len(a) > 5 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else sc.frame_end; st = int(a[7]) if len(a) > 7 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
