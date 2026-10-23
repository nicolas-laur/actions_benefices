"""Séquences animées Visa (30 i/s, flou de mouvement via images clés denses).
usage : python vanim.py <seq> <out_dir> [rx ry samples f0 f1]
seq : tap (90), spin (120, boucle), dark (90, boucle), stack (120)"""
import bpy, math, sys, os, random, time
sys.path.insert(0, '/home/claude/visa/b3d')
import vscene as V
from objs import mat
D = V.D
NF = {'tap': 90, 'spin': 60, 'dark': 48, 'stack': 110}

def screen_textures():
    import cairo
    W, H = 600, 420
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s); c.set_source_rgb(.02, .03, .05); c.paint()
    c.select_font_face('Inter Display SemiBold', 0, 0); c.set_font_size(40); c.set_source_rgb(.62, .68, .78)
    for t, y in (('APPROCHEZ', 150), ('VOTRE CARTE', 205)):
        e = c.text_extents(t); c.move_to(300-e.x_advance/2, y); c.show_text(t)
    c.select_font_face('Inter Display Black', 0, 0); c.set_font_size(70); c.set_source_rgb(.95, .93, .88); t = '24,90 €'; e = c.text_extents(t); c.move_to(300-e.x_advance/2, 320); c.show_text(t)
    s.write_to_png(f'{D}/tex_wait.png')

def keyall(objs_, f):
    for o in objs_: o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)

def ease(x): x = max(0, min(1, x)); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def lerp3(a, b, u): return tuple(lerp(a[i], b[i], u) for i in range(3))

def build(seq):
    V.textures(); screen_textures()
    sc = bpy.context.scene
    if seq == 'tap':
        V.studio(-0.6)
        t = V.terminal(); t.location = (0.15, 0.3, -0.5); t.rotation_euler = (math.radians(-28), 0, math.radians(-12))
        wait = V.slab('t_wait', 0.56, 0.4, 0.002, 0.03, loc=(0, -0.1135, 0.33), parent=t, edge=0)
        V.planar_uv(wait, 0.56, 0.4); wait.data.materials.append(V.img_mat('wait', f'{D}/tex_wait.png', metal=0, rough=0.1, emit=1.6))
        c = V.card()
        bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.006, location=(0.12, 0.05, 0.02), rotation=(math.radians(62), 0, math.radians(-12)))
        ring = bpy.context.object; rm = mat('ring', (1.0, 0.75, 0.4), emit=8); ring.data.materials.append(rm)
        em = rm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
        cam = V.camera((0.2, -3.6, 0.55), (0, 0, 0.0), 50); cam.data.dof.use_dof = False
        A = ((-1.6, -0.9, 1.6), (math.radians(-20), math.radians(40), math.radians(-60)))     # entrée hors champ
        B = ((-0.15, -0.25, 0.42), (math.radians(-55), math.radians(18), math.radians(-20)))  # position de paiement
        Cc = ((-0.1, -0.3, 0.55), (math.radians(-50), math.radians(14), math.radians(-18)))   # léger rebond
        TAP = 34
        for f in range(1, NF['tap']+1):
            if f <= TAP: u = ease((f-1)/(TAP-1)); u = 1-(1-u)**2; p, r = lerp3(A[0], B[0], u), lerp3(A[1], B[1], u)
            elif f <= TAP+10: u = ease((f-TAP)/10); p, r = lerp3(B[0], Cc[0], u), lerp3(B[1], Cc[1], u)
            else: u = (f-TAP-10)/40; p = (Cc[0][0], Cc[0][1], Cc[0][2]+0.03*math.sin(u*math.pi)); r = Cc[1]
            c.location, c.rotation_euler = p, r; keyall([c], f)
            # anneau : pulse au contact, écran : bascule sur « PAYÉ »
            k = f-TAP; s = 1+0.6*max(0, k)/20 if k >= 0 else 1.0
            ring.scale = (s, s, s); ring.keyframe_insert('scale', frame=f)
            em.default_value = 8*max(0.0, 1-max(0, k)/20) if k >= 0 else 1.5; em.keyframe_insert('default_value', frame=f)
            ring.hide_render = k > 20; ring.keyframe_insert('hide_render', frame=f)
            wait.hide_render = f > TAP; wait.keyframe_insert('hide_render', frame=f)
        cam.location = (0.25, -3.7, 0.6); cam.keyframe_insert('location', frame=1); cam.location = (0.15, -3.3, 0.5); cam.keyframe_insert('location', frame=NF['tap'])
    elif seq in ('spin', 'dark'):
        V.studio(-0.45 if seq == 'spin' else -0.7)
        if seq == 'dark':   # contre-jours rouges, halo plus froid
            for o in bpy.data.objects:
                if o.type == 'LIGHT' and o.data.color[0] > 0.9 and o.data.color[2] < 0.5: o.data.color = (1.0, 0.18, 0.12)
                if o.type == 'LIGHT' and o.data.color[2] > 0.9 and o.data.color[0] < 0.3: o.data.energy *= 0.5
        c = V.card(); cam = V.camera((0.3, -3.0, 0.45), (0, 0, 0.05), 60)
        n = NF[seq]
        for f in range(1, n+1):
            ph = 2*math.pi*(f-1)/n
            c.location = (0.03*math.sin(ph), 0, 0.1+0.035*math.sin(2*ph))
            c.rotation_euler = (math.radians(-12+6*math.sin(ph)), math.radians(-10+8*math.cos(ph)), math.radians(22+16*math.sin(ph)))
            keyall([c], f)
    elif seq == 'stack':
        V.studio(-0.5); random.seed(4)
        cards = []
        for i in range(10):
            c = V.card(f'c{i}'); cards.append(c)
        hero = V.card('hero')
        cam = V.camera((0.25, -2.6, 0.3), (0, 0, -0.5), 45)
        for i, c in enumerate(cards):
            z1 = -1.2+0.006+i*0.0135; rz = math.radians(random.uniform(-14, 14)); t0 = 4+i*7
            for f in range(1, NF['stack']+1):
                u = ease((f-t0)/9)
                c.location = (random.Random(i).uniform(-.02, .02), 0, lerp(1.4, z1, u)); c.rotation_euler = (math.pi/2, lerp(0.6, 0, u), rz+lerp(1.2, 0, u))
                keyall([c], f)
        for f in range(1, NF['stack']+1):
            u = ease((f-70)/30); ph = (f-1)/NF['stack']*2*math.pi
            hero.location = (0.05, -0.1, lerp(1.6, -0.15, u)+0.02*math.sin(ph)); hero.rotation_euler = (math.radians(-10), math.radians(lerp(40, -8, u)), math.radians(lerp(-30, 15, u)))
            keyall([hero], f)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for layer in getattr(ad.action, 'layers', []):
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        for fc in cb.fcurves:
                            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    sc = bpy.context.scene
    sc.render.fps = 30; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    sc.frame_start, sc.frame_end = 1, NF[seq]
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; seq, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (540, 960, 32)
    sc = build(seq); V.link_softboxes()
    sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        f = int(a[5]) if len(a) > 5 else 1; sc.frame_set(f); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True)
        f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else NF[seq]
        for f in range(f0, f1+1):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
            print('frame', f, round(time.time()-t, 1), flush=True)
