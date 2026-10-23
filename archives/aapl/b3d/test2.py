import bpy, math, sys, time
sys.path.insert(0,'.')
import objs
for name,fn,img,rot in (('phone',objs.build_phone,'scr_phone.png',-28),('player',objs.build_player,'scr_player.png',22),('retro',objs.build_retro,'scr_retro.png',-25)):
    sc=objs.reset(); objs.lights(); objs.camera(dist=5.6 if name=='retro' else 4.4)
    r=fn('/home/claude/aapl/b3d/'+img); r.rotation_euler=(0,0,math.radians(rot))
    sc.render.filepath=f'/home/claude/aapl/b3d/t_{name}.png'; t=time.time(); bpy.ops.render.render(write_still=True); print('t',name,round(time.time()-t,1))
