"""Décollage en 3D : la fusée (rocket.py) sur un pas de tir, nuages de fumée en volutes qui jaillissent au sol puis colonne de fumée
qui suit la fusée. Fond transparent (le ciel est fait en 2D). Projection de la tuyère exportée pour la flamme 2D.
usage : python launch.py <dossier> [rx ry samples f0 f1]   (15 i/s, image 1 = t vidéo 0)"""
import bpy, bmesh, math, os, sys, time, random, json
sys.path.insert(0, '/home/claude/spcx'); sys.path.insert(0, '/home/claude/visa/b3d')
import rocket
from objs import mat
from bpy_extras.object_utils import world_to_camera_view
FPS = 15; T_END = 10.4; NFR = int(T_END*FPS)+1
IGN, LIFT = 2.30, 2.75

def rz(t):
    tau = t-LIFT
    if tau <= 0: return 0.0
    return .25*tau*tau if tau < 4 else 4.0+2.0*(tau-4)+.12*(tau-4)**2

def smoke_mat():
    m = bpy.data.materials.new('smoke'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.5, .49, .5, 1); b.inputs['Roughness'].default_value = 1.0
    b.inputs['Subsurface Weight'].default_value = .7; b.inputs['Subsurface Radius'].default_value = (1.0, .8, .6); b.inputs['Subsurface Scale'].default_value = .4
    b.inputs['Specular IOR Level'].default_value = 0.0
    return m

def puff_proto(m, seed):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0); o = bpy.context.object
    tex = bpy.data.textures.new(f'cl{seed}', 'CLOUDS'); tex.noise_scale = .55; tex.noise_depth = 3
    d = o.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.strength = .42; d.mid_level = .5; d.texture_coords = 'LOCAL'
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='d')
    o.location = (0, 0, -100); return o

def build():
    sc = rocket.build()
    root = bpy.data.objects['rocket']; root.location = (0, 0, 0)
    for o in bpy.data.objects:   # la lumière de flamme suit la fusée
        if o.type == 'LIGHT' and o.data.type == 'POINT': o.parent = root; flame_light = o
    # sol et pas de tir
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.75)); g = bpy.context.object; g.data.materials.append(mat('ground', (.02, .02, .025), rough=.85))
    bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=.3, location=(0, 0, -.9)); p = bpy.context.object; p.data.materials.append(mat('pad', (.16, .16, .17), rough=.6))
    for x in (-1.5, 1.5):   # deux mâts génériques de part et d'autre
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x*2.6, 2.2, 4)); t_ = bpy.context.object; t_.scale = (.18, .18, 9.5); t_.data.materials.append(mat('mast', (.03, .03, .035), metal=.5, rough=.5))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.08, location=(x*2.6, 2.2, 8.8)); r_ = bpy.context.object; r_.data.materials.append(mat('red', (1, .1, .05), emit=40))
    m = smoke_mat(); protos = [puff_proto(m, k) for k in range(4)]
    random.seed(9); puffs = []
    # nuage au sol : jaillit de part et d'autre du pas de tir
    for i in range(72):
        side = random.choice((-1, 1)); ang = random.uniform(-.7, .7)
        puffs.append(dict(kind='ground', b=IGN+random.uniform(0, 3.2), dx=side*math.cos(ang), dy=-abs(math.sin(ang))*random.uniform(.2, 1.1)+random.uniform(-.1, .4),
                          v=random.uniform(5, 14), r0=random.uniform(.4, .7), rmax=random.uniform(2.2, 4.4), rise=random.uniform(.08, .45)))
    # vapeur avant l'allumage
    for i in range(8):
        puffs.append(dict(kind='vapor', b=0.0, x=random.uniform(-1.2, 1.2), y=random.uniform(-.3, .6), r0=random.uniform(.25, .45)))
    # colonne : émise depuis la tuyère pendant l'ascension
    for i in range(64):
        bt = LIFT+.1+i*.1
        puffs.append(dict(kind='col', b=bt, z=rz(bt)-1.1, x=random.uniform(-.3, .3), y=random.uniform(-.25, .25), r0=random.uniform(.45, .7), rmax=random.uniform(1.4, 2.4)))
    objs_ = []
    for k, P in enumerate(puffs):
        o = protos[k % 4].copy(); o.data = protos[k % 4].data; bpy.context.collection.objects.link(o); o.rotation_euler = (random.uniform(0, 6), random.uniform(0, 6), random.uniform(0, 6)); objs_.append(o)
        spin = random.uniform(-.25, .25)
        for f in range(1, NFR+1):
            t = (f-1)/FPS; a = t-P['b']
            if P['kind'] == 'vapor':
                s = P['r0']*(1+.15*math.sin(t*1.3+k)) if t < IGN+.4 else P['r0']*max(0, 1-(t-IGN-.4)/.6)
                o.location = (P['x']+.1*t, P['y'], -.7+.15*t); o.scale = (s, s, s*.8)
            elif a < 0:
                o.location = (0, 0, -100); o.scale = (.001, .001, .001)
            elif P['kind'] == 'ground':
                d = P['v']/.9*(1-math.exp(-.9*a)); r = P['r0']+(P['rmax']-P['r0'])*(1-math.exp(-.7*a))
                o.location = (P['dx']*d, P['dy']*d+1.0, -.75+r*.55+P['rise']*a); o.scale = (r, r, r*.8)
            else:
                r = P['r0']+(P['rmax']-P['r0'])*(1-math.exp(-.5*a))
                o.location = (P['x']+.12*a, P['y'], P['z']-.25*a); o.scale = (r, r, r)
            o.rotation_euler.z += 0
            o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
    bpy.ops.object.light_add(type='POINT', location=(0, .5, -.2)); gl = bpy.context.object; gl.data.color = (1, .5, .15); gl.data.shadow_soft_size = 1.5
    cam = sc.camera; cam.location = (0, -31, 1.2); cam.data.lens = 50
    look = (0, 0, 4.2); d = [look[i]-cam.location[i] for i in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0])-math.pi/2)
    # fusée : immobile puis ascension
    for f in range(1, NFR+1):
        t = (f-1)/FPS; root.location.z = rz(t); root.keyframe_insert('location', frame=f)
        flame_light.data.energy = 0 if t < IGN else 9000*min(1, (t-IGN)/.3)*(1+.1*math.sin(t*40))
        gl.data.energy = 0 if t < IGN else 14000*min(1, (t-IGN)/.3)*math.exp(-max(0, t-LIFT-2)*.35); gl.data.keyframe_insert('energy', frame=f); flame_light.data.keyframe_insert('energy', frame=f)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for layer in getattr(ad.action, 'layers', []):
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        for fc in cb.fcurves:
                            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    sc.frame_start, sc.frame_end = 1, NFR; sc.render.fps = FPS
    sc.render.use_motion_blur = False
    return sc

def export_proj(sc, path):
    """position écran de la tuyère par image (pour la flamme 2D)"""
    root = bpy.data.objects['rocket']; out = {}
    for f in range(1, NFR+1):
        sc.frame_set(f); w = root.matrix_world @ __import__('mathutils').Vector((0, 0, -.68))
        v = world_to_camera_view(sc, sc.camera, w); out[f] = (v.x, 1-v.y)
    json.dump(out, open(path, 'w'))

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]
    rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (720, 1280, 16)
    sc = build(); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out == 'proj': export_proj(sc, '/home/claude/spcx/launch_proj.json'); print('proj ok'); sys.exit()
    if out.endswith('.png'):
        sc.frame_set(int(a[4]) if len(a) > 4 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True); sys.exit()
    os.makedirs(out, exist_ok=True); f0 = int(a[4]) if len(a) > 4 else 1; f1 = int(a[5]) if len(a) > 5 else NFR
    for f in range(f0, f1+1):
        p = f'{out}/f{f:04d}.png'
        if os.path.exists(p): continue
        t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
