import bpy, math, random, os, sys
sys.path.insert(0,'/home/claude/amzn/b3d')
import objs
from objs import mat, box
def cardboard():
    m=bpy.data.materials.new('card'); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=40; n.inputs['Detail'].default_value=6
    r=nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(0.42,0.27,0.14,1); r.color_ramp.elements[1].color=(0.60,0.42,0.24,1)
    nt.links.new(n.outputs['Fac'],r.inputs['Fac']); nt.links.new(r.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.85
    return m
def cbox(loc,size,rot=0,m=None,tape=None):
    o=box('cb',size,loc=loc,bevel=min(size)*0.04,seg=2,m=m); o.rotation_euler=(0,0,rot)
    if tape: t=box('tape',(size[0]*0.18,size[1]*1.002,size[2]*1.004),loc=loc,bevel=0,m=tape); t.rotation_euler=(0,0,rot)
    return o
def base(style='warehouse'):
    sc=objs.reset(); sc.render.film_transparent=False
    w=sc.world.node_tree.nodes['Background']; w.inputs[0].default_value=(0.01,0.012,0.02,1); w.inputs[1].default_value=1.0
    sc.view_settings.exposure=-0.3
    return sc
def area(loc,rot,size,energy,color=(1,1,1),shape='SQUARE',sy=None):
    bpy.ops.object.light_add(type='AREA',location=loc,rotation=rot); l=bpy.context.object; l.data.size=size; l.data.energy=energy; l.data.color=color
    if sy: l.data.shape='RECTANGLE'; l.data.size_y=sy
    return l
def floor(color=(0.06,0.06,0.065),rough=0.25):
    bpy.ops.mesh.primitive_plane_add(size=80,location=(0,0,0)); f=bpy.context.object
    f.data.materials.append(mat('floor',color,rough=rough)); return f
def camera(loc,look,lens=35):
    bpy.ops.object.camera_add(location=loc); c=bpy.context.object; c.data.lens=lens
    d=[look[i]-loc[i] for i in range(3)]
    c.rotation_euler=(math.atan2(math.hypot(d[0],d[1]),-d[2]),0,math.atan2(d[1],d[0])-math.pi/2)
    bpy.context.scene.camera=c; return c
def warehouse(seed=1, conveyor=True, stacks=None):
    random.seed(seed); sc=base(); floor((0.035,0.035,0.04),0.5)
    box('ceiling',(30,60,0.2),loc=(0,10,6.8),bevel=0,m=mat('ceil',(0.015,0.015,0.02),rough=0.9))
    for k in range(12): box('truss',(12,0.15,0.3),loc=(0,-2+k*3,6.5),bevel=0,m=mat('tr',(0.08,0.08,0.09),metal=1,rough=0.5))
    card=cardboard(); tape=mat('tape',(0.72,0.6,0.42),rough=0.4)
    steel=mat('steel',(0.25,0.27,0.3),metal=1.0,rough=0.45); orange=mat('orng',(1.0,0.45,0.05),rough=0.5)
    # rayonnages de part et d'autre, en profondeur
    for side in (-1,1):
        for k in range(7):
            y=4+k*3.2; x=side*4.2
            for lv in range(4):
                box('beam',(0.12,3.0,0.1),loc=(x-side*0.6,y,0.6+lv*1.2),bevel=0,m=orange)
                box('beam',(0.12,3.0,0.1),loc=(x+side*0.6,y,0.6+lv*1.2),bevel=0,m=orange)
                for j in range(3):
                    if random.random()<0.85:
                        s=random.uniform(0.5,0.85); cbox((x+random.uniform(-0.2,0.2),y-1+j*1.0,0.65+lv*1.2+s/2),(s,s*random.uniform(0.9,1.3),s),random.uniform(-.1,.1),card,tape)
            for dy in (-1.5,1.5):
                for dx in (-0.6,0.6): box('post',(0.1,0.1,5.0),loc=(x+side*dx,y+dy,2.5),bevel=0,m=steel)
    if conveyor:
        box('belt',(1.1,30,0.12),loc=(0,6,0.75),bevel=0.02,m=mat('belt',(0.03,0.03,0.035),rough=0.6))
        box('frame',(1.3,30,0.18),loc=(0,6,0.62),bevel=0.02,m=steel)
        for i in range(10):
            s=random.uniform(0.38,0.55); cbox((random.uniform(-0.15,0.15),-1.2+i*1.6,0.81+s/2),(s,s*1.2,s*0.8),random.uniform(-.3,.3),card,tape)
    if stacks:
        wood=mat('wood',(0.45,0.32,0.18),rough=0.8)
        for (x,y,n,s) in stacks:
            for px in (-0.36,0,0.36): box('pal',(0.12,1.2,0.12),loc=(x+px*1.6,y,0.06),bevel=0,m=wood)
            box('palt',(1.2,1.2,0.04),loc=(x,y,0.14),bevel=0,m=wood)
            for i in range(n):
                col_=i%2; row=i//2
                cbox((x-0.28+col_*0.56+random.uniform(-.02,.02),y+random.uniform(-.02,.02),0.16+s/2+row*s),(0.54,0.6,s*0.98),random.uniform(-.05,.05),card,tape)
    # lumières : bandeaux suspendus chauds + contre-jour orange
    for k in range(7):
        y=3+k*3.2; area((0,y,5.5),(0,0,0),0.3,140,(1.0,0.78,0.5),sy=2.5)
        bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,5.55)); e=bpy.context.object; e.scale=(0.15,1.25,0.03); e.data.materials.append(mat('em',(1,0.8,0.55),emit=2.2))
    area((0,30,3),(math.radians(-90),0,0),8,2500,(1.0,0.5,0.15))
    area((-3,-4,4),(math.radians(50),0,math.radians(-30)),3,300,(0.6,0.7,1.0))
    return sc
def datacenter(seed=2):
    random.seed(seed); sc=base(); floor((0.04,0.045,0.055),0.12)
    rack=mat('rack',(0.02,0.022,0.026),metal=0.6,rough=0.35)
    leds=[mat('lb',(0.1,0.55,1.0),emit=12),mat('lo',(1.0,0.55,0.1),emit=12),mat('lg',(0.2,1.0,0.5),emit=8)]
    for side in (-1,1):
        for k in range(10):
            y=1.5+k*1.25; x=side*1.6
            box('rack',(0.9,1.15,2.4),loc=(x,y,1.2),bevel=0.01,seg=1,m=rack)
            for r in range(16):
                for c in range(5):
                    if random.random()<0.55:
                        m=random.choice(leds if random.random()<0.6 else leds[:1])
                        box('led',(0.02,0.03,0.015),loc=(x-side*0.452,y-0.4+c*0.2,0.3+r*0.13),bevel=0,m=m)
                box('slot',(0.005,1.0,0.008),loc=(x-side*0.451,y,0.36+r*0.13),bevel=0,m=mat('sl',(0.06,0.065,0.07),rough=0.4))
    for k in range(10):
        y=1.5+k*1.25; bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,3.0)); e=bpy.context.object; e.scale=(0.08,0.9,0.02); e.data.materials.append(mat('em2',(0.6,0.8,1.0),emit=8))
    area((0,6,2.8),(0,0,0),1.0,500,(0.5,0.7,1.0),sy=12)
    area((0,16,1.5),(math.radians(-90),0,0),4,1200,(0.2,0.5,1.0))
    return sc
def render(path,rx=540,ry=960,samples=24):
    sc=bpy.context.scene; sc.render.resolution_x=rx; sc.render.resolution_y=ry; sc.cycles.samples=samples; sc.render.filepath=path
    bpy.ops.render.render(write_still=True)
