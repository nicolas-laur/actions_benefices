import bpy, math, sys, os, mathutils
sys.path.insert(0,'/home/claude/aapl/b3d')
import objs
job,style,obj,scrimg,n,r0,r1,scale=sys.argv[-8:]; n=int(n); r0=float(r0); r1=float(r1); scale=float(scale)
out=f'/home/claude/aapl/b3d/{job}'; os.makedirs(out,exist_ok=True)
sc=objs.reset(); objs.environment(style, pedestal=(obj!='none'))
dist={'retro':6.4,'player':5.0,'phone':5.4,'none':5.4}[obj]
objs.env_camera(dist=dist*1.15,h=1.0,lens=55,look_z=-0.5); cam=sc.camera; p0=cam.location.copy()
sc.render.use_persistent_data=True
r=None
if obj!='none':
    fn={'phone':objs.build_phone,'player':objs.build_player,'retro':objs.build_retro}[obj]
    r=fn(f'/home/claude/aapl/b3d/{scrimg}'); r.scale=(scale,)*3
    if obj=='retro': r.location.y=0.35
    bpy.context.view_layer.update()
    zs=[(o.matrix_world@mathutils.Vector(v)).z for o in bpy.data.objects if o.parent==r and o.type=='MESH' for v in o.bound_box]
    r.location.z+=-0.78-min(zs)+0.002
    if obj!='retro': r.location.y=0.2
for i in range(n):
    u=i/max(1,n-1); e=u*u*(3-2*u)
    if r: r.rotation_euler=(0,0,math.radians(r0+(r1-r0)*e))
    cam.location=p0+mathutils.Vector((0,0.35*e,-0.05*e))     # léger travelling avant
    sc.render.filepath=f'{out}/{i:04d}.png'
    if not os.path.exists(sc.render.filepath): bpy.ops.render.render(write_still=True)
print('ok',job)
