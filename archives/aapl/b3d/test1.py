import bpy, math, sys, time
sys.path.insert(0,'.')
import objs
sc=objs.reset(); objs.lights(); objs.camera()
r=objs.build_phone('/home/claude/aapl/b3d/scr_phone.png'); r.rotation_euler=(0,0,math.radians(-28))
sc.render.filepath='/home/claude/aapl/b3d/t_phone.png'; t=time.time(); bpy.ops.render.render(write_still=True); print('t',time.time()-t)
