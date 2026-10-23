"""Meta : téléphone générique (aucune marque) qui flotte dans un studio sombre, écran noir brillant.
Le contenu de l'écran (stories) est composé en 2D : on exporte les coins de l'écran projetés à chaque image.
usage : python phone.py <out.png|dossier> [rx ry samples f0 f1 step]  |  python phone.py proj"""
import bpy, math, os, sys, json, time
sys.path.insert(0, '/home/claude/aapl/b3d')
import objs
from objs import mat, slab, empty
from bpy_extras.object_utils import world_to_camera_view
NF = 240; TAU = 2*math.pi
SW, SH, SR = 0.66, 1.42, 0.095

def build():
    sc = objs.reset(); sc.render.film_transparent = False
    objs.environment('dark', pedestal=False)
    sc.view_settings.exposure = -1.6
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    root = empty('phone')
    body = mat('graphite', (0.10, 0.105, 0.115), metal=1.0, rough=0.3)
    glass = mat('glass', (0.004, 0.004, 0.005), rough=0.03, coat=1.0)
    slab('body', 0.74, 1.5, 0.075, 0.12, m=body, parent=root, edge=0.02)
    slab('front', 0.715, 1.475, 0.002, 0.11, loc=(0, -0.0385, 0), m=glass, parent=root, edge=0)
    scr = slab('scr', SW, SH, 0.001, SR, loc=(0, -0.0405, 0), m=mat('scrm', (0.0, 0.0, 0.0), rough=0.05, coat=1.0), parent=root, edge=0)
    # boutons latéraux et module photo arrière discrets (génériques)
    for z, h in ((.32, .16), (.12, .1)): objs.box('btn', (.012, .02, h), loc=(.375, 0, z), bevel=.004, seg=2, m=body, parent=root)
    # lumière d'accent bleue (fond) + reflet qui balaie l'écran
    def area(loc, rot, size, energy, color=(1, 1, 1)):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object; l.data.size = size; l.data.energy = energy; l.data.color = color; return l
    area((0, 2.6, 1.8), (math.radians(-60), 0, 0), 2.0, 380, (0.25, 0.45, 1.0))
    area((-2.2, -2.2, 2.2), (math.radians(55), 0, math.radians(-45)), 1.2, 160, (1, .95, .9))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 4.5, 1.2), rotation=(math.radians(90), 0, 0)); g = bpy.context.object; g.scale = (5, 4, 1)
    g.data.materials.append(mat('halo', (0.15, 0.3, 1.0), emit=0.35))
    bpy.ops.object.camera_add(location=(0, -4.6, 0.25)); cam = bpy.context.object; cam.data.lens = 60
    cam.rotation_euler = (math.radians(90-3), 0, 0); sc.camera = cam
    cam.data.dof.use_dof = False
    root.location = (0, 0, 0.12)
    for f in range(1, NF+1):
        u = TAU*(f-1)/NF
        root.rotation_euler = (math.radians(4+3*math.sin(u*2)), math.radians(-3+2*math.sin(u)), math.radians(16*math.sin(u)))
        root.location = (0, 0, 0.12+0.035*math.sin(u*2+.6))
        root.keyframe_insert('rotation_euler', frame=f); root.keyframe_insert('location', frame=f)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    return sc, scr, cam

def project(sc, scr, cam, rx, ry):
    """coins de l'écran (haut-gauche, haut-droit, bas-droit, bas-gauche) en pixels, pour chaque image"""
    out = {}
    for f in range(1, NF+1):
        sc.frame_set(f); M = scr.matrix_world; pts = []
        for x, z in ((-SW/2, SH/2), (SW/2, SH/2), (SW/2, -SH/2), (-SW/2, -SH/2)):
            from mathutils import Vector
            p = world_to_camera_view(sc, cam, M @ Vector((x, -0.0006, z)))
            pts.append((p.x*rx, (1-p.y)*ry))
        out[f] = pts
    return out

if __name__ == '__main__':
    a = sys.argv[1:]
    sc, scr, cam = build()
    if a[0] == 'proj':
        sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
        json.dump(project(sc, scr, cam, 1080, 1920), open('/home/claude/meta/proj.json', 'w')); print('proj ok'); sys.exit()
    out = a[0]; rx, ry, samples = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (540, 960, 24)
    sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[4]) if len(a) > 4 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[4]) if len(a) > 4 else 1; f1 = int(a[5]) if len(a) > 5 else NF; st = int(a[6]) if len(a) > 6 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
