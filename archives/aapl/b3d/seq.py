import bpy, math, sys, os
sys.path.insert(0,'/home/claude/aapl/b3d')
import objs
name=sys.argv[-3]; n=int(sys.argv[-2]); rot0=float(sys.argv[-1])
os.makedirs(f'/home/claude/aapl/b3d/seq_{name}',exist_ok=True)
fn={'phone':objs.build_phone,'player':objs.build_player,'retro':objs.build_retro}[name]
sc=objs.reset(); objs.lights(); objs.camera(dist={'retro':5.4,'player':3.9,'phone':4.2}[name])
r=fn(f'/home/claude/aapl/b3d/scr_{name}.png')
if name=='retro': r.location=(0,0.25,-0.05)
for i in range(n):
    u=i/(n-1); e=u*u*(3-2*u)
    r.rotation_euler=(0,0,math.radians(rot0-32+52*e)); r.location.z=(-0.05 if name=='retro' else 0)+0.04*math.sin(u*math.pi)
    sc.render.filepath=f'/home/claude/aapl/b3d/seq_{name}/{i:04d}.png'; bpy.ops.render.render(write_still=True)
print('ok',name)
