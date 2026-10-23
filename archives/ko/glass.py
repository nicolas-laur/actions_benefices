"""Coca-Cola : verre droit générique (aucune forme ni marque déposée) qui se remplit de cola, puis gros plan sur les bulles.
plans :  fill = remplissage (non bouclé, NFILL images) ;  bub = macro des bulles qui montent dans le liquide (boucle NB images)
usage : python glass.py <fill|bub> <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/aapl/b3d'); sys.path.insert(0, '/home/claude/amzn/b3d')
import objs
from objs import mat
NFILL = 96; NPOUR = 139; NB = 120; PMESH = '/home/claude/ko/pmesh'; TAU = 2*math.pi

def glass_mat():
    m = bpy.data.materials.new('glass'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (1, 1, 1, 1); b.inputs['Roughness'].default_value = 0.0; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.5
    return m
def cola_mat(density=40.0):
    m = bpy.data.materials.new('cola'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    b.inputs['Base Color'].default_value = (0.9, 0.45, 0.2, 1); b.inputs['Roughness'].default_value = 0.0; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.34
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption'); vol.inputs['Color'].default_value = (0.6, 0.22, 0.06, 1); vol.inputs['Density'].default_value = density
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
    sc.cycles.caustics_refractive = False; sc.cycles.caustics_reflective = False; sc.cycles.blur_glossy = 1.0
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    lights(sc); rnd = random.Random(3)
    cola, foam, bub = cola_mat(), foam_mat(), bubble_mat()
    if shot in ('fill', 'pour'):
        NF_ = NPOUR if shot == 'pour' else NFILL
        # éclairage « packshot » : fond sombre avec halo ambré flou derrière le verre, deux bandes de contre-jour latérales
        for o in list(bpy.data.objects):
            if o.type == 'LIGHT' or (o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('bgglow')): bpy.data.objects.remove(o)
        A = __import__('amz').area
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 7, 1.6), rotation=(math.radians(90), 0, 0)); bk = bpy.context.object; bk.scale = (40, 40, 1)
        bm_ = bpy.data.materials.new('bk'); bm_.use_nodes = True; nt = bm_.node_tree; em = nt.nodes['Principled BSDF']; em.inputs['Base Color'].default_value = (0, 0, 0, 1)
        gt = nt.nodes.new('ShaderNodeTexGradient'); gt.gradient_type = 'SPHERICAL'; tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (12, 9, 1)
        nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], gt.inputs['Vector'])
        pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2; nt.links.new(gt.outputs['Fac'], pw.inputs[0])
        mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = 3.2; nt.links.new(pw.outputs[0], mr.inputs[0])
        em.inputs['Emission Color'].default_value = (1, .5, .2, 1); nt.links.new(mr.outputs[0], em.inputs['Emission Strength']); bk.data.materials.append(bm_)
        bl_ = A((0, 2.2, .9), (math.radians(-90), 0, 0), 1.2, 260, (1, .6, .3), sy=2.0)            # contre-jour derrière le verre (éclaire, mais invisible à travers le verre : pas de bruit)
        bl_.visible_transmission = False
        for sx in (-1, 1):                                                                     # bandes latérales : liserés verticaux sur le verre
            l = A((sx*1.9, .8, .9), (math.radians(90), 0, math.radians(sx*-115)), .25, 140, (1, .93, .85), sy=2.6)
        A((0, -3, 3.2), (math.radians(45), 0, 0), 2.5, 40 if shot == 'fill' else 90, (1, .95, .9))                    # face très douce
        tl_ = A((0, -.6, 3.0), (math.radians(10), 0, 0), .8, 90 if shot == 'fill' else 260, (1, .9, .75)); tl_.visible_glossy = False   # lumière du dessus : fait ressortir la mousse
        for o in bpy.data.objects:
            if o.type == 'LIGHT':
                try: o.visible_camera = False; o.visible_glossy = True
                except Exception: pass
        bpy.ops.mesh.primitive_plane_add(size=30); p = bpy.context.object; p.data.materials.append(mat('bar', (0.006, 0.005, 0.005), rough=.06, coat=.6))
        R, Hh = .42, 1.5
        bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=R, depth=Hh, location=(0, 0, Hh/2)); g = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT'); import bmesh; bm = bmesh.from_edit_mesh(g.data)
        top = [f for f in bm.faces if f.normal.z > .9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bmesh.update_edit_mesh(g.data); bpy.ops.object.mode_set(mode='OBJECT')
        sd = g.modifiers.new('s', 'SOLIDIFY'); sd.thickness = .02; sd.offset = -1
        bv = g.modifiers.new('b', 'BEVEL'); bv.width = .008; bv.segments = 3
        g.data.materials.append(glass_mat()); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=R-.02, depth=.12, location=(0, 0, .06)); fb = bpy.context.object; fb.data.materials.append(glass_mat()); bpy.ops.object.shade_smooth()   # fond épais
        if shot == 'fill':
            cola = cola_mat(26.0); cola.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value = 1.02   # quasi sans réfraction : le cola s'assombrit au centre et rougeoie sur les bords, sans effet de loupe
            bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=R-.021, depth=1, location=(0, 0, .5)); liq = bpy.context.object; liq.data.materials.append(cola); bpy.ops.object.shade_smooth()
            # mousse : galette irrégulière beige
            bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=R-.022, depth=1, location=(0, 0, 0)); fo = bpy.context.object
            fm = mat('foam2', (0.55, 0.36, 0.2), rough=.7); fm.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = .4; fo.data.materials.append(fm)
            froth = bpy.data.objects.new('froth', None); bpy.context.collection.objects.link(froth)
            fbm = mat('foamb', (0.8, 0.62, 0.44), rough=.3); fbb = fbm.node_tree.nodes['Principled BSDF']; fbb.inputs['Transmission Weight'].default_value = .2; fbb.inputs['Subsurface Weight'].default_value = .5
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1); proto_ = bpy.context.object; proto_.data.materials.append(fbm); bpy.ops.object.shade_smooth(); proto_.location = (0, 0, -40)
            for i in range(520):
                ang = rnd.uniform(0, TAU); rr_ = (R-.035)*math.sqrt(rnd.random()); r_ = rnd.uniform(.008, .026)*(1.25 if rr_ > R-.12 else 1)
                o = bpy.data.objects.new('fb', proto_.data); bpy.context.collection.objects.link(o); o.parent = froth
                o.location = (rr_*math.cos(ang), rr_*math.sin(ang), rnd.uniform(-.004, .03)+.02*(rr_/R)**3); o.scale = (r_, r_, r_*.8)
            # filet : fin, ondulant, texture qui coule vers le bas (coordonnées d'un repère animé)
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.028, depth=3, location=(.05, 0, 3)); st = bpy.context.object
            bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.loopcut_and_slide(MESH_OT_loopcut={"number_cuts": 80, "edge_index": 1}) if False else None
            bpy.ops.object.mode_set(mode='OBJECT')
            bm2 = bmesh.new(); bm2.from_mesh(st.data)
            ed = [e for e in bm2.edges if abs(e.verts[0].co.z-e.verts[1].co.z) > .5]
            bmesh.ops.subdivide_edges(bm2, edges=ed, cuts=90, use_grid_fill=True); bm2.to_mesh(st.data); bm2.free()
            st.data.materials.append(cola_mat(90.0)); bpy.ops.object.shade_smooth()
            flow = bpy.data.objects.new('flow', None); bpy.context.collection.objects.link(flow)
            sdm = st.modifiers.new('d', 'DISPLACE'); tx2 = bpy.data.textures.new('sn', 'CLOUDS'); tx2.noise_scale = .12; sdm.texture = tx2; sdm.strength = .012
            sdm.texture_coords = 'OBJECT'; sdm.texture_coords_object = flow; sdm.direction = 'NORMAL'
            flow.location = (0, 0, 0); flow.keyframe_insert('location', frame=1); flow.location = (0, 0, -9); flow.keyframe_insert('location', frame=NFILL+1)
            __import__('anim').lin(flow)
            for f in range(1, NFILL+1):
                u = (f-1)/(NFILL-1); fill = 1-(1-min(1, u/.85))**2.0; h = .02+1.22*fill
                liq.scale = (1, 1, h); liq.location.z = .12+h/2; liq.keyframe_insert('scale', frame=f); liq.keyframe_insert('location', frame=f)
                fh = .02+.05*math.sin(min(1, u/.9)*math.pi*.75); fo.scale = (1, 1, fh); fo.location.z = .12+h+fh/2-.012; fo.keyframe_insert('scale', frame=f); fo.keyframe_insert('location', frame=f)
                fs = .35+.65*math.sin(min(1, u/.9)*math.pi*.75); froth.location.z = .12+h+fh-.01; froth.scale = (1, 1, fs); froth.keyframe_insert('location', frame=f); froth.keyframe_insert('scale', frame=f)
                on = 1.0 if u < .8 else max(0.0, 1-(u-.8)/.08)
                st.scale = (max(.001, on), max(.001, on), 1); st.location.z = .12+h+1.5 if on > 0 else 8; st.keyframe_insert('scale', frame=f); st.keyframe_insert('location', frame=f)
            # bulles qui montent le long de la paroi et au centre
            for i in range(45):
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=rnd.uniform(.005, .012)); b_ = bpy.context.object; b_.data.materials.append(bub)
                ang = rnd.uniform(0, TAU); rr_ = rnd.uniform(.05, R-.04); x, y = rr_*math.cos(ang), rr_*math.sin(ang); ph = rnd.random(); sp = rnd.uniform(.6, 1.4)
                for f in range(1, NFILL+1, 3):
                    u = (f-1)/(NFILL-1); h = .02+1.22*(1-(1-min(1, u/.85))**2.0)
                    z = .14+((u*sp*3+ph) % 1)*max(.03, h-.05)
                    b_.location = (x+.008*math.sin(f*.3+i), y, z); b_.keyframe_insert('location', frame=f)
        else:
            # versement simulé : liquide maillé image par image (pour.py + mesh.py), mousse en nuage de bulles
            colap = cola_mat(18.0); colap.name = 'colap'; colap.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value = 1.15
            me = bpy.data.meshes.new('lq0'); lq = bpy.data.objects.new('liqm', me); bpy.context.collection.objects.link(lq); me.materials.append(colap)
            fbm = mat('foamb', (0.95, 0.68, 0.42), rough=.35, coat=.6); fbb = fbm.node_tree.nodes['Principled BSDF']; fbb.inputs['Coat Roughness'].default_value = .05
            ng = bpy.data.node_groups.new('pts', 'GeometryNodeTree')
            ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
            gi = ng.nodes.new('NodeGroupInput'); go = ng.nodes.new('NodeGroupOutput'); mtp = ng.nodes.new('GeometryNodeMeshToPoints'); na = ng.nodes.new('GeometryNodeInputNamedAttribute')
            na.data_type = 'FLOAT'; na.inputs['Name'].default_value = 'rad'; smt = ng.nodes.new('GeometryNodeSetMaterial'); smt.inputs['Material'].default_value = fbm
            ng.links.new(gi.outputs[0], mtp.inputs['Mesh']); ng.links.new(na.outputs['Attribute'], mtp.inputs['Radius']); ng.links.new(mtp.outputs['Points'], smt.inputs['Geometry']); ng.links.new(smt.outputs['Geometry'], go.inputs[0])
            fme = bpy.data.meshes.new('fm0'); fo_ = bpy.data.objects.new('foamp', fme); bpy.context.collection.objects.link(fo_)
            gnm = fo_.modifiers.new('gn', 'NODES'); gnm.node_group = ng
            # filet au-dessus de l'arrivée de la simulation (z = 1,62) : même rayon, ondulation qui coule
            bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=.062, depth=3, location=(.05, 0, 1.605+1.5)); st = bpy.context.object; st.name = 'streamtop'
            bm2 = bmesh.new(); bm2.from_mesh(st.data); ed = [e for e in bm2.edges if abs(e.verts[0].co.z-e.verts[1].co.z) > .5]
            bmesh.ops.subdivide_edges(bm2, edges=ed, cuts=90, use_grid_fill=True); bm2.to_mesh(st.data); bm2.free()
            colas = cola_mat(40.0); colas.name = 'colas'; st.data.materials.append(colas); bpy.ops.object.shade_smooth()
            flow = bpy.data.objects.new('flow', None); bpy.context.collection.objects.link(flow)
            sdm = st.modifiers.new('d', 'DISPLACE'); tx2 = bpy.data.textures.new('sn', 'CLOUDS'); tx2.noise_scale = .12; sdm.texture = tx2; sdm.strength = .006
            sdm.texture_coords = 'OBJECT'; sdm.texture_coords_object = flow; sdm.direction = 'NORMAL'
            flow.location = (0, 0, 0); flow.keyframe_insert('location', frame=1); flow.location = (0, 0, -14); flow.keyframe_insert('location', frame=NF_+1)
            __import__('anim').lin(flow)
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 50
        tgt = bpy.data.objects.new('tgt', None); bpy.context.collection.objects.link(tgt)
        tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
        for f, (x, y, z, tz) in ((1, (.35, -4.9, 1.05, 1.15)), (NF_, (-.2, -4.3, .85, .95))):
            cam.location = (x, y, z); cam.keyframe_insert('location', frame=f); tgt.location = (0, 0, tz); tgt.keyframe_insert('location', frame=f)
        cam.data.dof.use_dof = True; cam.data.dof.focus_object = g; cam.data.dof.aperture_fstop = 2.4
        sc.frame_start, sc.frame_end = 1, NF_
    else:
        # macro : on est DANS le cola, les bulles montent devant un contre-jour ambré
        for o in list(bpy.data.objects):
            if (o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('bgglow')) or (o.type == 'LIGHT' and o.data.size == 2.0):
                bpy.data.objects.remove(o)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); box_ = bpy.context.object; box_.scale = (9, 6.4, 12); cb_ = cola_mat(1.7); [n for n in cb_.node_tree.nodes if n.type == 'VOLUME_ABSORPTION'][0].inputs['Color'].default_value = (0.85, 0.78, 0.635, 1); box_.data.materials.append(cb_)   # la caméra est DANS le liquide
        A = __import__('amz').area
        for sx in (-1, 1):   # reflets argentés sur les bulles
            l = A((sx*1.4, -.9, .9), (math.radians(70), 0, math.radians(sx*-60)), .6, 120, (1, .95, .88), sy=2.4); l.visible_camera = False
        l = A((0, -1.0, 2.2), (math.radians(30), 0, 0), 1.2, 60, (1, .9, .8)); l.visible_camera = False
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 4.0, 0), rotation=(math.radians(90), 0, 0)); bk = bpy.context.object; bk.scale = (14, 14, 1)
        bm_ = bpy.data.materials.new('bk'); bm_.use_nodes = True; nt = bm_.node_tree; em = nt.nodes['Principled BSDF']; em.inputs['Base Color'].default_value = (0, 0, 0, 1)
        gt = nt.nodes.new('ShaderNodeTexGradient'); gt.gradient_type = 'SPHERICAL'; tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], gt.inputs['Vector'])
        pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.6; nt.links.new(gt.outputs['Fac'], pw.inputs[0])
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (3.2, 2.0, 1); nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], gt.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = 30.0; nt.links.new(pw.outputs[0], mr.inputs[0])
        em.inputs['Emission Color'].default_value = (1, .75, .45, 1); nt.links.new(mr.outputs[0], em.inputs['Emission Strength']); bk.data.materials.append(bm_)
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

def load_pour(f):
    import numpy as np
    d = np.load(f'{PMESH}/f{f-1:04d}.npz')
    lq = bpy.data.objects['liqm']; old = lq.data; me = bpy.data.meshes.new(f'lq{f}')
    if len(d['v']): me.from_pydata(d['v'].tolist(), [], d['f'].tolist()); me.polygons.foreach_set('use_smooth', [True]*len(me.polygons))
    me.materials.append(bpy.data.materials['colap']); lq.data = me; bpy.data.meshes.remove(old)
    fo_ = bpy.data.objects['foamp']; old = fo_.data; fm = bpy.data.meshes.new(f'fm{f}')
    keep = d['fr'] > .0015; P = d['fp'][keep]
    if len(P):
        fm.vertices.add(len(P)); fm.vertices.foreach_set('co', P.ravel()); a = fm.attributes.new('rad', 'FLOAT', 'POINT'); a.data.foreach_set('value', d['fr'][keep])
    fo_.data = fm; bpy.data.meshes.remove(old)
    st = bpy.data.objects['streamtop']; st.hide_render = not bool(d['stream'])
    hs = float(d['hs']); L = 4.6-hs; st.scale.z = L/3; st.location.z = hs+L/2

if __name__ == '__main__':
    a = sys.argv[1:]; shot, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (432, 768, 24)
    sc = build(shot); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        f_ = int(a[5]) if len(a) > 5 else 1; sc.frame_set(f_)
        if shot == 'pour': load_pour(f_)
        sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else sc.frame_end; st = int(a[7]) if len(a) > 7 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f)
            if shot == 'pour': load_pour(f)
            sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
