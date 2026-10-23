import bpy, math, sys, time, os
sys.path.insert(0,'/home/claude/aapl/b3d')
import objs
style=sys.argv[-1]
ONLY=os.environ.get('ONLY')
for name,fn,rot,dist,zoff in (('retro',objs.build_retro,-22,6.4,0.0),('player',objs.build_player,20,5.0,-0.35),('phone',objs.build_phone,-24,5.4,-0.1)):
    if ONLY and name!=ONLY: continue
    sc=objs.reset(); objs.environment(style); objs.env_camera(dist=dist*1.15,h=1.0,lens=55,look_z=-0.5)
    r=fn(f'/home/claude/aapl/b3d/scr_{name}.png'); r.rotation_euler=(0,0,math.radians(rot))
    if name=='retro': r.scale=(0.72,0.72,0.72); r.location.y=0.35
    if name=='phone': r.scale=(0.78,0.78,0.78)
    # poser l'objet sur le socle (dessus du socle à z=-0.78)
    import mathutils
    bpy.context.view_layer.update()
    zs=[ (o.matrix_world@mathutils.Vector(v)).z for o in bpy.data.objects if o.parent==r and o.type=='MESH' for v in o.bound_box]
    r.location.z+=-0.78-min(zs)+0.002; r.location.y=r.location.y if name=='retro' else 0.2
    sc.render.filepath=f'/home/claude/aapl/b3d/env_{style}_{name}.png'; t=time.time(); bpy.ops.render.render(write_still=True); print('t',name,round(time.time()-t,1))
