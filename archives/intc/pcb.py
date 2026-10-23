"""Intel v2 : carte mère macro réaliste (générique, aucune marque) + touches néon.
Carte texturée haute définition (pcbtex.py) + composants 3D instanciés (passifs, condensateurs, selfs, puces, socket, processeur).
plans : cpu = lent travelling/balancement au-dessus du socket ; net = glissé rasant au-dessus des pistes, paquets néon qui circulent.
usage : python pcb.py <cpu|net> <out.png|dossier> [rx ry samples f0 f1 step]"""
import bpy, math, random, os, sys, time
sys.path.insert(0, '/home/claude/aapl/b3d'); sys.path.insert(0, '/home/claude/amzn/b3d'); sys.path.insert(0, '/home/claude/intc')
import objs
from objs import mat, box
from chip import pulse_mat, trace
NF = 120; TAU = 2*math.pi; D = '/home/claude/intc'
BW = 26.0   # côté de la carte (unités) : la texture 4096 px couvre BW

def board_mat():
    m = bpy.data.materials.new('board'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1/BW, 1/BW, 1); mp.inputs['Location'].default_value = (.5, .5, 0)
    L(tc.outputs['Object'], mp.inputs['Vector'])
    def img(p, non_color=False):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.interpolation = 'Cubic'
        if non_color: t.image.colorspace_settings.name = 'Non-Color'
        L(mp.outputs[0], t.inputs['Vector']); return t
    c, hgt, met = img(f'{D}/pcb_col.png'), img(f'{D}/pcb_h.png', True), img(f'{D}/pcb_m.png', True)
    L(c.outputs['Color'], b.inputs['Base Color']); L(met.outputs['Color'], b.inputs['Metallic'])
    rg = nt.nodes.new('ShaderNodeMapRange'); rg.inputs[3].default_value = .32; rg.inputs[4].default_value = .18; L(met.outputs['Color'], rg.inputs[0]); L(rg.outputs[0], b.inputs['Roughness'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .35; bp.inputs['Distance'].default_value = .004; L(hgt.outputs['Color'], bp.inputs['Height']); L(bp.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Coat Weight'].default_value = .5; b.inputs['Coat Roughness'].default_value = .12   # vernis épargne brillant
    return m

def brushed(name, c=(0.72, 0.73, 0.75)):
    m = mat(name, c, metal=1, rough=.28); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Anisotropic'].default_value = .7
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 400; n.inputs['Detail'].default_value = 2
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 60, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeMapRange'); r.inputs[3].default_value = .2; r.inputs[4].default_value = .36; nt.links.new(n.outputs['Fac'], r.inputs[0]); nt.links.new(r.outputs[0], b.inputs['Roughness'])
    return m

def charge_mat(name, color, rmax, axis=None, period=None, cycles=1, strength=60.0):
    """axis=None : onde radiale depuis l'origine (distance) ; axis='Y' : vagues successives le long de Y (période `period`)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    b.inputs['Base Color'].default_value = (0.03, 0.035, 0.045, 1); b.inputs['Metallic'].default_value = 1; b.inputs['Roughness'].default_value = .3
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    if axis is None:
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; L(geo.outputs['Position'], ln.inputs[0]); dist = ln.outputs['Value']
    else:
        sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'], sep.inputs[0]); dist = sep.outputs[axis]
    fr = nt.nodes.new('ShaderNodeValue'); fd = nt.nodes.new('ShaderNodeValue')
    for f in range(1, NF+2, 2):
        u = (f-1)/NF*cycles % 1.0
        if axis is None: fr.outputs[0].default_value = -0.5+(rmax+1.5)*min(1, u/.62)   # front qui part du processeur
        else: fr.outputs[0].default_value = (f-1)/NF*cycles*period
        fd.outputs[0].default_value = 1.0 if (axis is not None or u < .72) else max(0.0, 1-(u-.72)/.2)
        fr.outputs[0].keyframe_insert('default_value', frame=f); fd.outputs[0].keyframe_insert('default_value', frame=f)
    sub = nt.nodes.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'; L(fr.outputs[0], sub.inputs[0]); L(dist, sub.inputs[1])   # x = front - d
    if axis is not None:   # vagues répétées : x modulo la période
        md = nt.nodes.new('ShaderNodeMath'); md.operation = 'FLOORED_MODULO'; md.inputs[1].default_value = period; L(sub.outputs[0], md.inputs[0]); x = md.outputs[0]
    else: x = sub.outputs[0]
    # remplissage : 0 devant le front, 1 derrière ; tête brillante juste derrière le front
    fill = nt.nodes.new('ShaderNodeMapRange'); fill.inputs[1].default_value = 0.0; fill.inputs[2].default_value = 0.08; L(x, fill.inputs[0])
    head = nt.nodes.new('ShaderNodeMath'); head.operation = 'MULTIPLY'; head.inputs[1].default_value = -4.0 if axis is None else -6.0; L(x, head.inputs[0])
    ex = nt.nodes.new('ShaderNodeMath'); ex.operation = 'EXPONENT'; L(head.outputs[0], ex.inputs[0])
    hb = nt.nodes.new('ShaderNodeMath'); hb.operation = 'MULTIPLY_ADD'; hb.inputs[1].default_value = 3.0; hb.inputs[2].default_value = 1.0; L(ex.outputs[0], hb.inputs[0])
    if axis is not None:   # la traîne s'estompe derrière la tête
        tail = nt.nodes.new('ShaderNodeMapRange'); tail.inputs[1].default_value = period*.55; tail.inputs[2].default_value = period*.2; L(x, tail.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; L(fill.outputs[0], m2.inputs[0]); L(tail.outputs[0], m2.inputs[1]); fillo = m2.outputs[0]
    else: fillo = fill.outputs[0]
    e1 = nt.nodes.new('ShaderNodeMath'); e1.operation = 'MULTIPLY'; L(fillo, e1.inputs[0]); L(hb.outputs[0], e1.inputs[1])
    e2 = nt.nodes.new('ShaderNodeMath'); e2.operation = 'MULTIPLY'; L(e1.outputs[0], e2.inputs[0]); L(fd.outputs[0], e2.inputs[1])
    e3 = nt.nodes.new('ShaderNodeMath'); e3.operation = 'MULTIPLY'; e3.inputs[1].default_value = strength; L(e2.outputs[0], e3.inputs[0])
    b.inputs['Emission Color'].default_value = (*color, 1); L(e3.outputs[0], b.inputs['Emission Strength'])
    ad = nt.animation_data
    if ad and ad.action:
        for layer in getattr(ad.action, 'layers', []):
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        for fc in getattr(ad.action, 'fcurves', []):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    return m

LIB = {}
def proto(name, build):
    """objet modèle caché ; les copies partagent le maillage (instances légères)"""
    if name in LIB: return LIB[name]
    objs_ = build(); bpy.ops.object.select_all(action='DESELECT')
    for o in objs_:
        o.select_set(True)
        for md in list(o.modifiers): bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.context.view_layer.objects.active = objs_[0]; bpy.ops.object.join(); p = bpy.context.object; p.name = name
    p.location = (0, 0, -50); LIB[name] = p; return p
def inst(name, loc, rz=0.0, s=1.0):
    p = LIB[name]; o = bpy.data.objects.new(name+'_i', p.data); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler.z = rz; o.scale = (s, s, s); return o

def build_lib():
    tin = mat('tin', (0.8, 0.8, 0.78), metal=1, rough=.2); blk = mat('blk', (0.025, 0.025, 0.028), rough=.35); cer = mat('cer', (0.45, 0.36, 0.25), rough=.5)
    alu = brushed('alu', (0.78, 0.79, 0.8)); fer = mat('fer', (0.18, 0.18, 0.2), metal=.6, rough=.45); gold = mat('gold', (0.85, 0.62, 0.25), metal=1, rough=.2)
    def passive(body):
        def f():
            a = box('p', (.10, .05, .035), loc=(0, 0, .0175), bevel=.004, seg=2, m=body); e1 = box('e', (.022, .052, .037), loc=(-.045, 0, .0185), bevel=.003, seg=2, m=tin); e2 = box('e', (.022, .052, .037), loc=(.045, 0, .0185), bevel=.003, seg=2, m=tin)
            return [a, e1, e2]
        return f
    proto('res', passive(blk)); proto('cap', passive(cer))
    def polycap():
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.14, depth=.32, location=(0, 0, .16)); c = bpy.context.object; c.data.materials.append(alu)
        md = c.modifiers.new('b', 'BEVEL'); md.width = .02; md.segments = 3; bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.142, depth=.06, location=(0, 0, .27)); band = bpy.context.object; band.data.materials.append(mat('band', (0.35, 0.05, 0.4), metal=.3, rough=.35)); bpy.ops.object.shade_smooth()
        base = box('pb', (.3, .3, .02), loc=(0, 0, .01), bevel=.005, seg=2, m=blk)
        return [c, band, base]
    proto('pcap', polycap)
    def choke():
        a = box('ch', (.42, .42, .26), loc=(0, 0, .13), bevel=.03, seg=3, m=fer); t1 = box('t', (.44, .08, .02), loc=(0, -.12, .005), bevel=0, m=tin); t2 = box('t', (.44, .08, .02), loc=(0, .12, .005), bevel=0, m=tin)
        return [a, t1, t2]
    proto('choke', choke)
    def mos():
        a = box('m', (.26, .3, .06), loc=(0, 0, .03), bevel=.01, seg=2, m=blk); tab = box('tab', (.26, .1, .012), loc=(0, .19, .006), bevel=0, m=tin)
        legs = [box('l', (.03, .08, .01), loc=(-.09+i*.09, -.18, .005), bevel=0, m=tin) for i in range(3)]
        return [a, tab]+legs
    proto('mos', mos)
    def qfp(n=12):
        def f():
            a = box('q', (.6, .6, .07), loc=(0, 0, .035), bevel=.01, seg=2, m=blk); out = [a]
            for i in range(n):
                t = -.26+i*.52/(n-1)
                for sx, sy, w, h in ((t, .33, .015, .07), (t, -.33, .015, .07), (.33, t, .07, .015), (-.33, t, .07, .015)):
                    out.append(box('pin', (w, h, .012), loc=(sx, sy, .006), bevel=0, m=tin))
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.025, depth=.004, location=(-.2, -.2, .071)); d_ = bpy.context.object; d_.data.materials.append(mat('dot', (0.08, 0.08, 0.09), rough=.6)); out.append(d_)
            return out
        return f
    proto('qfp', qfp())
    return dict(tin=tin, blk=blk, alu=alu, gold=gold)

def socket_cpu(M):
    """socket LGA générique + processeur (substrat vert, capot argent brossé, gravure neutre)"""
    sock = mat('sock', (0.05, 0.05, 0.055), rough=.5)
    box('frame', (2.9, 2.9, .12), loc=(0, 0, .06), bevel=.02, seg=2, m=sock)
    box('bed', (2.3, 2.3, .02), loc=(0, 0, .125), bevel=0, m=mat('pins', (0.6, 0.45, 0.2), metal=1, rough=.35))
    # plaque de maintien + levier
    steel = mat('steel', (0.55, 0.56, 0.58), metal=1, rough=.32)
    for sx, sy, w, h in ((0, 1.48, 3.1, .12), (0, -1.48, 3.1, .12), (1.48, 0, .12, 3.1), (-1.48, 0, .12, 3.1)): box('ret', (w, h, .05), loc=(sx, sy, .16), bevel=.01, seg=2, m=steel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.03, depth=3.0, location=(1.75, 0, .1), rotation=(math.pi/2, 0, 0)); lv = bpy.context.object; lv.data.materials.append(steel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.03, depth=.5, location=(1.75, -1.75, .1), rotation=(0, math.pi/2, 0)); lv2 = bpy.context.object; lv2.data.materials.append(steel); lv2.location.x = 1.55
    sub = mat('sub', (0.05, 0.14, 0.08), rough=.4)
    box('substrate', (2.2, 2.2, .07), loc=(0, 0, .17), bevel=.01, seg=2, m=sub)
    gold = M['gold']
    for i in range(22):
        t = -1.0+i*2.0/21
        for sx, sy in ((t, 1.05), (t, -1.05), (1.05, t), (-1.05, t)): box('gp', (.03, .03, .004), loc=(sx, sy, .206), bevel=0, m=gold)
    ihs = brushed('ihs', (0.8, 0.81, 0.82))
    box('ihs', (1.6, 1.6, .12), loc=(0, 0, .26), bevel=.05, seg=5, m=ihs)
    box('ihs2', (1.25, 1.25, .04), loc=(0, 0, .335), bevel=.02, seg=4, m=ihs)
    # gravure : texte générique en léger relief
    bpy.ops.object.text_add(location=(-.52, .18, .356)); tx = bpy.context.object; tx.data.body = "x86-64 CORE\n3.8 GHZ  ·  2026"; tx.data.size = .11; tx.data.extrude = .002
    tx.data.materials.append(mat('etch', (0.5, 0.51, 0.53), metal=1, rough=.55))
    # néon discret : liseré cyan sous le substrat (lumière qui « s'échappe » du socket)
    neon = mat('neonc', (0.15, 0.85, 1.0), emit=25)
    for sx, sy, w, h in ((0, 1.13, 2.24, .015), (0, -1.13, 2.24, .015), (1.13, 0, .015, 2.24), (-1.13, 0, .015, 2.24)): box('nl', (w, h, .01), loc=(sx, sy, .135), bevel=0, m=neon)

def populate(rnd, xr, yr, clear=None, dens=1.0):
    """sème les composants sur la carte (en évitant la zone `clear`)"""
    def ok(x, y, r):
        return not (clear and abs(x-clear[0]) < clear[2]+r and abs(y-clear[1]) < clear[3]+r)
    for k in range(int(260*dens)):
        x, y = rnd.uniform(*xr), rnd.uniform(*yr)
        if ok(x, y, .1): inst(rnd.choice(('res', 'cap', 'cap')), (x, y, 0), rnd.choice((0, math.pi/2)))
    # rangées de régulation : selfs + condensateurs polymère + MOSFET (typique d'une carte mère)
    for k in range(int(6*dens)):
        x0, y0 = rnd.uniform(*xr), rnd.uniform(*yr); horiz = rnd.random() < .5
        for i in range(rnd.randint(4, 8)):
            x, y = (x0+i*.55, y0) if horiz else (x0, y0+i*.55)
            if not ok(x, y, .6): continue
            inst('choke', (x, y, 0), 0 if horiz else math.pi/2)
            inst('pcap', (x+(0 if horiz else .55), y+(.55 if horiz else 0), 0))
            inst('mos', (x+(0 if horiz else -.5), y+(-.5 if horiz else 0), 0), 0 if horiz else math.pi/2)
    for k in range(int(10*dens)):
        x, y = rnd.uniform(*xr), rnd.uniform(*yr)
        if ok(x, y, .5): inst('qfp', (x, y, 0), rnd.choice((0, math.pi/2)), rnd.uniform(.8, 1.5))

def build(shot):
    sc = objs.reset(); sc.render.film_transparent = False
    w = sc.world.node_tree.nodes['Background']; w.inputs[0].default_value = (0.02, 0.025, 0.035, 1); w.inputs[1].default_value = 1
    sc.view_settings.exposure = -0.2
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    bpy.ops.mesh.primitive_plane_add(size=90, location=(0, 0, 0)); bd = bpy.context.object; bd.data.materials.append(board_mat())
    M = build_lib(); rnd = random.Random(7)
    A = __import__('amz').area
    # éclairage studio réaliste (clé douce froide, contre-jour) + accents néon discrets
    A((-3, -4, 6), (math.radians(40), 0, math.radians(-35)), 6, 900, (.92, .96, 1))
    A((4, 5, 3), (math.radians(-60), 0, math.radians(140)), 4, 500, (.85, .9, 1))
    A((6, -2, .8), (math.radians(85), 0, math.radians(75)), 3, 160, (.5, .7, 1))
    A((-6, 2, .8), (math.radians(85), 0, math.radians(-75)), 3, 260, (.15, .8, 1))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); sc.camera = cam
    tgt = bpy.data.objects.new('tgt', None); bpy.context.collection.objects.link(tgt)
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    if shot == 'cpu':
        socket_cpu(M); populate(rnd, (-9, 9), (-6, 14), clear=(0, 0, 1.75, 1.75), dens=1.8)
        # pistes héros qui partent du socket, avec paquets de données néon
        pm = [charge_mat('c1', (.1, .75, 1.0), 9.0, strength=16), charge_mat('c2', (.1, .75, 1.0), 9.0, strength=11)]
        for side in range(4):
            for k in range(26):
                off = -1.25+k*.1; L_ = rnd.uniform(2.0, 8.5); bend = rnd.uniform(.15, 1.2); d = rnd.choice((-1, 1)); j = rnd.uniform(.2, .6)
                pts = [(1.8+bend, off), (1.8+bend+j, off+d*j), (1.8+L_*.6, off+d*j)]
                if rnd.random() < .6: pts += [(1.8+L_*.6+j, off+d*2*j), (1.8+L_, off+d*2*j)]
                ang = side*math.pi/2; ca, sa = math.cos(ang), math.sin(ang)
                P = [(x*ca-y*sa, x*sa+y*ca) for x, y in [(1.6, off)]+pts]
                trace(P[0][0], P[0][1], P[1:], .016, pm[k % 2], z=.003)
                ex, ey = P[-1]; bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.035, depth=.006, location=(ex, ey, .004)); v_ = bpy.context.object; v_.data.materials.append(pm[k % 2])
        cam.data.lens = 45; cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 2.8
        tgt.location = (0, .9, .3)
        for f in range(1, NF+1, 2):
            u = TAU*(f-1)/NF; ang = -.35+.25*math.sin(u)
            cam.location = (7.2*math.sin(ang), -7.2*math.cos(ang), 4.6+.2*math.sin(u+1)); cam.keyframe_insert('location', frame=f)
    else:
        TILE = 4.0
        populate(rnd, (-5, 5), (-8, 14), clear=(0, 0, 1.2, 99), dens=2.6)
        pm = charge_mat('n1', (.1, .75, 1.0), 0, axis='Y', period=TILE, cycles=3, strength=18); pm2 = charge_mat('n2', (.1, .75, 1.0), 0, axis='Y', period=TILE/2, cycles=4, strength=13)
        for k in range(-2, 5):
            y0 = k*TILE-7.5+8
            for i in range(22):
                x = -1.05+i*.1; r_ = random.Random(i)      # même motif à chaque tuile : boucle parfaite
                if r_.random() < .45:   # décrochement à 45° qui revient sur sa voie
                    d = r_.choice((-1, 1))*.1; a1 = r_.uniform(.4, 1.6); a2 = a1+r_.uniform(.6, 1.4)
                    pts = [(x, y0+a1), (x+d, y0+a1+.1), (x+d, y0+a2), (x, y0+a2+.1), (x, y0+TILE)]
                else: pts = [(x, y0+TILE)]
                trace(x, y0, pts, .016, pm if i % 3 else pm2, z=.003)
        cam.data.lens = 28; cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 2.0
        for f in (1, 1+NF):
            y = -6+(f-1)/NF*TILE; cam.location = (0, y, 1.15); cam.keyframe_insert('location', frame=f); tgt.location = (0, y+1.9, 0); tgt.keyframe_insert('location', frame=f)
        __import__('anim').lin(cam); __import__('anim').lin(tgt)
    sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 30
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; shot, out = a[0], a[1]
    rx, ry, samples = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (1080, 1920, 24)
    sc = build(shot); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = samples; sc.render.use_persistent_data = True
    if out.endswith('.png'):
        sc.frame_set(int(a[5]) if len(a) > 5 else 1); sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(out, exist_ok=True); f0 = int(a[5]) if len(a) > 5 else 1; f1 = int(a[6]) if len(a) > 6 else NF; st = int(a[7]) if len(a) > 7 else 1
        for f in range(f0, f1+1, st):
            p = f'{out}/f{f:04d}.png'
            if os.path.exists(p): continue
            t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('frame', f, round(time.time()-t, 1), flush=True)
        open(f'{out}/done', 'w').write('ok')
