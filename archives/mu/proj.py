import sys, json; sys.argv = ['x', 'none']
sys.path.insert(0, '/home/claude/mu')
import hbm, bpy
from bpy_extras.object_utils import world_to_camera_view
sc = hbm.build(); cam = sc.camera
hero = bpy.data.objects['stack-11']; gpu = bpy.data.objects['gpu']
out = {}
for f in range(1, hbm.NF+1):
    sc.frame_set(f)
    kids = [o for o in hero.children]; top = max(kids, key=lambda o: o.matrix_world.translation.z)
    mid = sorted(kids, key=lambda o: o.matrix_world.translation.z)[len(kids)//2]
    r = {}
    for k, o in (('top', top), ('mid', mid), ('gpu', gpu)):
        v = world_to_camera_view(sc, cam, o.matrix_world.translation); r[k] = (v.x, 1-v.y)
    out[f] = r
json.dump(out, open('/home/claude/mu/proj.json', 'w'))
print(out[1], out[61])
