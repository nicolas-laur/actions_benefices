"""Krachs ép. 1 : corbeille de salle de marché générique (aucune marque, aucun bâtiment réel), traders-mannequins sans visage.
mode up = euphorie (écrans verts, bras levés) ; mode down = panique (écrans rouges, mains sur la tête, papiers qui tombent).
usage : python pit.py <up|down> <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/amzn/b3d'); sys.path.insert(0, '/home/claude/visa/b3d')
import amz
from objs import mat, box
from anim import lin
D = '/home/claude/krach08'; NF = 60; TAU = 2*math.pi

def img_mat(name, path, strength, scroll=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.extension = 'REPEAT'
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); L(tc.outputs['UV'], mp.inputs['Vector']); L(mp.outputs[0], t.inputs['Vector'])
    if scroll:
        sx, rep = scroll; mp.inputs['Scale'].default_value = (rep, 1, 1)
        mp.inputs['Location'].default_value = (0, 0, 0); mp.inputs['Location'].keyframe_insert('default_value', frame=1)
        mp.inputs['Location'].default_value = (sx, 0, 0); mp.inputs['Location'].keyframe_insert('default_value', frame=1+NF)
        for fc in (m.node_tree.animation_data.action.fcurves if hasattr(m.node_tree.animation_data.action, 'fcurves') else []):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        lin(m.node_tree)
    b.inputs['Base Color'].default_value = (0, 0, 0, 1); b.inputs['Roughness'].default_value = .25
    L(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = strength
    return m

def ellip(name, r, loc, m, parent=None, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg//2, radius=1, location=loc); o = bpy.context.object; o.name = name
    o.scale = r; bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth(); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def emp(name, loc, parent=None):
    bpy.ops.object.empty_add(location=loc); o = bpy.context.object; o.name = name
    if parent: o.parent = parent; o.location = loc
    return o

def figure(i, loc, yaw, suit, skin, tie, mode, rnd):
    """mannequin articulé : racine aux hanches, torse, tête (sans visage), bras épaule/coude"""
    root = emp(f'r{i}', loc); root.rotation_euler = (0, 0, yaw)
    s = rnd.uniform(.93, 1.07); root.scale = (s, s, s)
    for sx in (-1, 1): ellip('leg', (.075, .075, .44), (sx*.09, 0, -.46), suit, root)
    hips = emp(f'h{i}', (0, 0, 0), root)
    ellip('pelvis', (.17, .11, .12), (0, 0, .02), suit, hips)
    ellip('torso', (.2, .125, .3), (0, 0, .33), suit, hips)
    ellip('shirt', (.06, .03, .12), (0, -.11, .5), mat('sh', (.85, .86, .9), rough=.5), hips)
    ellip('tie', (.025, .02, .14), (0, -.125, .44), tie, hips)
    neck = emp(f'n{i}', (0, 0, .62), hips)
    ellip('neck', (.045, .045, .06), (0, 0, .02), skin, neck)
    ellip('head', (.095, .105, .125), (0, -.005, .15), skin, neck)
    arms = []
    for side in (-1, 1):
        sh = emp(f's{i}{side}', (side*.23, 0, .52), hips)
        ellip('upper', (.072, .072, .17), (0, 0, -.15), suit, sh)
        el = emp(f'e{i}{side}', (0, 0, -.3), sh)
        ellip('fore', (.062, .062, .15), (0, 0, -.13), suit, el)
        ellip('hand', (.045, .035, .06), (0, 0, -.29), skin, el)
        arms.append((side, sh, el))
    # rôle et phase propres à chaque figurine
    role = rnd.choice(('wave', 'wave', 'point', 'phone') if mode == 'up' else ('head', 'head', 'face', 'slump', 'phone'))
    ph = rnd.uniform(0, TAU); k = rnd.choice((1, 1, 2))
    for f in range(1, NF+2, 2):
        t = TAU*(f-1)/NF*k+ph; sn = math.sin(t); cs = math.cos(t)
        lean = nod = 0.0; bob = 0.0; pose = {}
        for side, sh, el in arms:
            if mode == 'up':
                if role == 'wave' or (role == 'point' and side == 1):
                    a = (-2.55+.3*sn*side, side*(.35+.15*cs), 0, -.35-.35*math.sin(t*2+side))
                    if role == 'point': a = (-1.75+.08*sn, side*.15, 0, -.1)
                elif role == 'phone' and side == 1: a = (-.35, side*.55, 0, -2.55)
                else: a = (-.25+.15*sn, side*.12, 0, -.5)
                bob = .03*abs(sn); lean = -.06+.05*cs
            else:
                if role == 'head': a = (-2.0, side*1.05, 0, -2.25+.06*sn)
                elif role == 'face': a = (-1.05, side*.25, 0, -2.25)
                elif role == 'phone' and side == 1: a = (-.35, side*.55, 0, -2.55)
                else: a = (-.25, side*.12, 0, -.25)
                lean = {'head': .12, 'face': .32, 'slump': .55, 'phone': .1}[role]+.04*sn; nod = {'head': .25, 'face': .45, 'slump': .6, 'phone': .2}[role]
            sh.rotation_euler = (a[0], a[1], a[2]); el.rotation_euler = (a[3], 0, 0)
            sh.keyframe_insert('rotation_euler', frame=f); el.keyframe_insert('rotation_euler', frame=f)
        hips.rotation_euler = (lean, 0, .12*math.sin(t*.5) if mode == 'up' else .05*sn); hips.location = (0, 0, bob)
        neck.rotation_euler = (nod + (.15*sn if mode == 'up' else 0), 0, .2*cs if mode == 'up' else 0)
        for o in (hips, neck): o.keyframe_insert('rotation_euler', frame=f)
        hips.keyframe_insert('location', frame=f)
    return root

def build(mode):
    up = mode == 'up'
    sc = amz.base(); sc.view_settings.exposure = -0.1
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.006, 0.007, 0.012, 1)
    amz.floor((0.05, 0.045, 0.04), 0.55)
    wood = mat('wood', (0.16, 0.09, 0.05), rough=.45); carpet = mat('carpet', (0.05, 0.06, 0.09), rough=.9)
    rail = mat('rail', (0.6, 0.6, 0.62), metal=1, rough=.25)
    # corbeille octogonale en gradins
    for k, (r, z) in enumerate(((5.2, .45), (4.0, .3), (2.8, .15))):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=r, depth=z, location=(0, 4, z/2)); o = bpy.context.object; o.rotation_euler.z = math.pi/8
        o.data.materials.append(carpet if k % 2 else wood)
        # murs d'écrans géants en arc au fond
    big = img_mat('big', f'{D}/board_{mode}.png', 4.5, scroll=(1.0, 1.2))
    band = img_mat('band', f'{D}/band_{mode}.png', 5.5, scroll=(-1.0, 1.6))
    frame = mat('frame', (0.02, 0.02, 0.025), metal=.8, rough=.35)
    for j in range(-3, 4):
        a = j*.33; x = 10.5*math.sin(a); y = 4+10.5*math.cos(a)
        for (zc, hh, mm, wdt) in ((5.5, 2.5, big, 3.4), (3.65, .62, band, 3.4), (7.35, .62, band, 3.4)):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, zc), rotation=(math.pi/2, 0, -a)); p = bpy.context.object; p.scale = (wdt, hh, 1)
            p.data.materials.append(mm)
            # décalage d'UV par panneau pour que les tickers ne se répètent pas
            for lp in p.data.uv_layers[0].data: lp.uv = (lp.uv[0]*.25+(j+3)*.25, lp.uv[1])
            box('fr', (wdt+.12, .1, hh+.12), loc=(x+.06*math.sin(a), y+.06*math.cos(a), zc), bevel=0, m=frame).rotation_euler.z = -a
    box('ceil', (30, 30, .2), loc=(0, 4, 8.6), bevel=0, m=mat('ceil', (.01, .01, .012), rough=.9))
    for k in range(3): box('strip', (14, .1, .04), loc=(0, 1+k*3.5, 8.45), bevel=0, m=mat('strip', (1, .95, .85), emit=1.5))
    # grappes de moniteurs suspendues au-dessus de la corbeille
    mons = [img_mat(f'm{k}', f'{D}/mon_{mode}_{k}.png', 3.2) for k in range(6)]
    for (cx, cy, rot) in ((-3.3, 2.0, .5), (3.3, 2.0, -.5), (-3.9, 5.6, .9), (3.9, 5.6, -.9)):
        box('pole', (.06, .06, 2.0), loc=(cx, cy, 4.3), bevel=0, m=frame)
        for q in range(4):
            ang = rot+q*math.pi/2; px = cx+.42*math.sin(ang); py = cy-.42*math.cos(ang)
            bx = box('mon', (.78, .06, .5), loc=(px, py, 3.0), bevel=.01, seg=2, m=frame); bx.rotation_euler.z = ang
            bpy.ops.mesh.primitive_plane_add(size=1, location=(cx+.455*math.sin(ang), cy-.455*math.cos(ang), 3.0), rotation=(math.pi/2, 0, ang))
            s_ = bpy.context.object; s_.scale = (.72, .44, 1); s_.data.materials.append(mons[(q+int(cx*7)) % 6])
    # traders
    suits = [mat('s1', (0.025, 0.03, 0.05), rough=.6), mat('s2', (0.05, 0.05, 0.055), rough=.6), mat('s3', (0.02, 0.035, 0.06), rough=.6)]
    vest = mat('vest', (0.55, 0.32, 0.08), rough=.7)   # vestes de corbeille colorées, génériques
    skin = mat('skin', (0.72, 0.62, 0.52), rough=.5); skin.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = .15
    ties = [mat('t1', (0.5, 0.05, 0.06)), mat('t2', (0.05, 0.12, 0.4)), mat('t3', (0.35, 0.3, 0.06))]
    rnd = random.Random(5 if up else 8); spots = []
    for ring, (r, z, n) in enumerate(((1.6, .3, 7), (2.6, .3, 10), (3.5, .45, 13), (4.6, .45, 16))):
        for q in range(n):
            a = TAU*q/n+ring*.3+rnd.uniform(-.12, .12); x = r*math.sin(a); y = 4+r*math.cos(a)
            if y < 1.2 and abs(x) < 0.9: continue          # dégage l'axe caméra
            spots.append((x, y, z+.92, math.atan2(x, -(y-4)) + math.pi + rnd.uniform(-.5, .5)))
    for i, (x, y, z, yaw) in enumerate(spots):
        figure(i, (x, y, z), yaw, vest if rnd.random() < .3 else rnd.choice(suits), skin, rnd.choice(ties), mode, rnd)
    # papiers : au sol, et qui tombent en mode panique
    paper = mat('paper', (.85, .85, .82), rough=.6); paper.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = .2
    pr = random.Random(3)
    for k in range(70 if up else 140):
        x, y = pr.uniform(-5, 5), pr.uniform(.5, 8.5); bpy.ops.mesh.primitive_plane_add(size=.22, location=(x, y, .47 if math.hypot(x, y-4) < 5.2 else .01))
        p = bpy.context.object; p.scale.y = 1.3; p.rotation_euler = (pr.uniform(-.1, .1), pr.uniform(-.1, .1), pr.uniform(0, TAU)); p.data.materials.append(paper)
    if not up:
        for k in range(45):
            x, y = pr.uniform(-4.5, 4.5), pr.uniform(1, 8); z0 = pr.uniform(.5, 6); spd = pr.uniform(.6, 1.2)
            bpy.ops.mesh.primitive_plane_add(size=.2, location=(x, y, z0)); p = bpy.context.object; p.scale.y = 1.3; p.data.materials.append(paper)
            ph = pr.uniform(0, 1); r1, r2 = pr.uniform(0, TAU), pr.uniform(1, 3)
            for f in range(1, NF+2, 2):
                u = ((f-1)/NF+ph) % 1.0; zz = 6.2-u*6.0
                p.location = (x+.25*math.sin(TAU*u*2+r1), y+.2*math.cos(TAU*u*2+r1), zz); p.rotation_euler = (r2*u*TAU*.5, math.sin(TAU*u*3+r1)*.8, r1+u*TAU)
                p.keyframe_insert('location', frame=f); p.keyframe_insert('rotation_euler', frame=f)
            # pas de saut visible au bouclage : la feuille réapparaît en haut hors cadre
    # éclairage
    warm = (1.0, .78, .55) if up else (1.0, .45, .4); key = (1.0, .95, .85) if up else (.75, .8, 1.0)
    amz.area((0, 4, 7.5), (0, 0, 0), 9, 900 if up else 520, key)
    amz.area((0, 15, 5), (math.radians(-90), 0, 0), 12, 1500, (.3, 1, .5) if up else (1, .15, .12))
    amz.area((-7, -2, 3.5), (math.radians(70), 0, math.radians(-60)), 3, 250, warm)
    amz.area((6, 0, 2.5), (math.radians(75), 0, math.radians(60)), 3, 160, (.4, .55, 1.0))
    cam = amz.camera((0, -1.6, 2.2), (0, 6, 3.2), 21)
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 5.5; cam.data.dof.aperture_fstop = 2.4
    # léger flottement caméra, bouclé
    for f in range(1, NF+2, 4):
        u = TAU*(f-1)/NF
        cam.location = (.08*math.sin(u), -1.6+.05*math.sin(2*u), 2.2+.04*math.cos(u)); cam.keyframe_insert('location', frame=f)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    sc.render.use_motion_blur = False
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; mode, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (720, 1280, 20)
    sc = build(mode); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[5]) if len(a) > 5 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else NF; st = int(a[7]) if len(a) > 7 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
