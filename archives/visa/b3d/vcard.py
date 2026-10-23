"""Rendus nets 1080×1920 : studio seul, carte seule (fond transparent, dos visible = support d'infographies),
plus les coins de la zone d'affichage projetés en pixels (JSON) pour y plaquer les graphiques en perspective.
usage : python vcard.py bg|A|B|darkA [samples]"""
import bpy, math, sys, os, json
sys.path.insert(0, '/home/claude/visa/b3d')
import vscene as V
from objs import mat, box
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D = V.D
POSES = {'A': ((0.0, 0.0, 0.02), (math.radians(-9), math.radians(-5), math.radians(180+9))),
         'B': ((0.0, 0.0, 0.02), (math.radians(-7), math.radians(6), math.radians(180-10)))}

def card_back_stripe(root):
    """bande magnétique noire brillante au dos : la carte se lit immédiatement comme une carte"""
    T = 0.012
    o = box('stripe', (0.852, 0.0012, 0.085), loc=(0, T/2+0.0014, 0.165), bevel=0, m=mat('stripe', (0.006, 0.006, 0.008), metal=0.4, rough=0.18))
    o.parent = root

def setup(which):
    V.textures()
    style = 'dark' if which.startswith('dark') else 'gold'
    V.studio(-0.5 if style == 'gold' else -0.7)
    if style == 'dark':
        for o in bpy.data.objects:
            if o.type == 'LIGHT' and o.data.color[0] > 0.9 and o.data.color[2] < 0.5: o.data.color = (1.0, 0.2, 0.14)
        for m in bpy.data.materials:
            if m.name == 'sb_goldm': m.node_tree.nodes['Emission'].inputs['Color'].default_value = (1.0, 0.25, 0.18, 1)
    cam = V.camera((0.0, -2.22, 0.26), (0.0, 0.0, 0.06), 50); cam.data.dof.use_dof = False
    sc = bpy.context.scene
    if which == 'bg': return sc, None
    c = V.card(); card_back_stripe(c)
    p = POSES[which.replace('dark', '')]; c.location, c.rotation_euler = p
    for o in bpy.data.objects:
        if o.name == 'cyc': o.visible_camera = False
    sc.render.film_transparent = True
    return sc, c

def corners(c):
    """coins de la zone d'affichage au dos (sous la bande), dans l'ordre haut-gauche, haut-droit, bas-droit, bas-gauche à l'écran"""
    bpy.context.view_layer.update()
    sc = bpy.context.scene; cam = sc.camera; T = 0.012
    pts = [(-0.39, T/2+0.002, 0.10), (0.39, T/2+0.002, 0.10), (0.39, T/2+0.002, -0.235), (-0.39, T/2+0.002, -0.235)]
    out = []
    for p in pts:
        w = c.matrix_world @ Vector(p); v = world_to_camera_view(sc, cam, w)
        out.append((v.x*sc.render.resolution_x, (1-v.y)*sc.render.resolution_y))
    out.sort(key=lambda q: q[1]); top = sorted(out[:2]); bot = sorted(out[2:])
    return [top[0], top[1], bot[1], bot[0]]

if __name__ == '__main__':
    which = sys.argv[1]; samples = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    sc, c = setup(which)
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.cycles.samples = samples
    if c is not None:
        json.dump(corners(c), open(f'{D}/card_{which}.json', 'w'))
    V.link_softboxes()
    sc.render.filepath = f'{D}/st_{which}.png'; bpy.ops.render.render(write_still=True)
