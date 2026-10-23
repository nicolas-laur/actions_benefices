import bpy, math, sys, os
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'
    sc.cycles.samples=int(os.environ.get('SAMPLES','24')); sc.cycles.use_denoising=True
    try: sc.cycles.denoiser='OPENIMAGEDENOISE'
    except Exception: pass
    sc.render.film_transparent=True
    sc.render.resolution_x=sc.render.resolution_y=int(os.environ.get('RES','600'))
    sc.view_settings.view_transform='AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.0
    return sc
def mat(name,base,metal=0.0,rough=0.4,emit=None,img=None,coat=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*base,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if coat: b.inputs['Coat Weight'].default_value=coat
    if img:
        t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(img)
        nt.links.new(t.outputs['Color'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=emit or 1.0
        nt.links.new(t.outputs['Color'],b.inputs['Base Color'])
    elif emit: b.inputs['Emission Color'].default_value=(*base,1); b.inputs['Emission Strength'].default_value=emit
    return m
def box(name,size,loc=(0,0,0),bevel=0.05,seg=8,m=None,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.scale=size
    bpy.ops.object.transform_apply(scale=True)
    if bevel>0:
        md=o.modifiers.new('bv','BEVEL'); md.width=bevel; md.segments=seg; md.limit_method='NONE'
    if m: o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    if parent: o.parent=parent
    return o
def slab(name,w,h,d,r,loc=(0,0,0),m=None,parent=None,edge=0.012,seg=32):
    import bmesh
    me=bpy.data.meshes.new(name); bm=bmesh.new(); pts=[]
    for cx,cz,a0 in ((w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)):
        for i in range(seg+1):
            a=math.radians(a0+90*i/seg); pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    vs=[bm.verts.new((x,-d/2,z)) for x,z in pts]; f=bm.faces.new(vs)
    ex=bmesh.ops.extrude_face_region(bm,geom=[f]); nv=[e for e in ex['geom'] if isinstance(e,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,verts=nv,vec=(0,d,0)); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.location=loc
    if edge>0:
        md=o.modifiers.new('bv','BEVEL'); md.width=edge; md.segments=4; md.limit_method='ANGLE'; md.angle_limit=math.radians(50)
    if m: o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    if parent: o.parent=parent
    return o
def rscreen(name,w,h,r,loc,img,parent,strength=1.2):
    o=slab(name,w,h,0.001,r,loc=loc,edge=0)
    # UV planaires depuis X/Z
    me=o.data; uv=me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=((v.x+w/2)/w,(v.z+h/2)/h)
    o.data.materials.append(mat(name+'m',(0,0,0),rough=0.08,emit=strength,img=img)); o.parent=parent; return o
def screen_plane(name,w,h,loc,img,parent,strength=1.2,rot=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_plane_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.scale=(w,h,1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat(name+'m',(0,0,0),rough=0.08,emit=strength,img=img)); o.parent=parent; return o
def empty(name):
    bpy.ops.object.empty_add(location=(0,0,0)); e=bpy.context.object; e.name=name; return e
def lights(rim=(1.0,0.45,0.25), rim2=(0.4,0.6,1.0)):
    def area(loc,rot,size,energy,color=(1,1,1)):
        bpy.ops.object.light_add(type='AREA',location=loc,rotation=rot); l=bpy.context.object; l.data.size=size; l.data.energy=energy; l.data.color=color; return l
    area((-2.2,-2.5,2.6),(math.radians(55),0,math.radians(-40)),2.2,420)
    area((2.6,-1.8,1.2),(math.radians(75),0,math.radians(55)),1.2,180)
    area((0.0,2.4,1.6),(math.radians(-55),0,0),1.6,520,rim)
    area((-2.4,1.8,-0.6),(math.radians(-110),0,math.radians(-50)),1.2,260,rim2)
def camera(dist=5.0,h=0.35,lens=70):
    bpy.ops.object.camera_add(location=(0,-dist,h),rotation=(math.radians(88),0,0)); c=bpy.context.object; c.data.lens=lens; bpy.context.scene.camera=c
# ---------- objets génériques ----------
def build_phone(img):
    root=empty('phone')
    alu=mat('alu',(0.62,0.63,0.66),metal=1.0,rough=0.28)
    glass=mat('glass',(0.005,0.005,0.006),rough=0.04,coat=1.0)
    slab('body',0.74,1.5,0.075,0.12,m=alu,parent=root,edge=0.02)
    slab('front',0.715,1.475,0.002,0.11,loc=(0,-0.0385,0),m=glass,parent=root,edge=0)
    rscreen('scr',0.66,1.42,0.095,(0,-0.0405,0),img,root)
    return root
def build_player(img):
    root=empty('player')
    shell=mat('shell',(0.92,0.92,0.93),rough=0.15,coat=1.0)
    back=mat('back',(0.75,0.76,0.78),metal=1.0,rough=0.18)
    slab('back',0.62,1.0,0.09,0.09,m=back,parent=root,edge=0.025)
    slab('front',0.6,0.98,0.004,0.085,loc=(0,-0.047,0),m=shell,parent=root,edge=0)
    rscreen('scr',0.48,0.36,0.02,(0,-0.05,0.22),img,root,1.0)
    pad=mat('pad',(0.86,0.87,0.88),metal=0.3,rough=0.35)
    slab('pad',0.4,0.3,0.004,0.06,loc=(0,-0.05,-0.24),m=pad,parent=root,edge=0)
    line=mat('line',(0.6,0.61,0.64),metal=0.5,rough=0.3)
    slab('padline',0.004,0.22,0.002,0.001,loc=(0,-0.0525,-0.24),m=line,parent=root,edge=0)
    return root
def build_retro(img):
    root=empty('retro')
    beige=mat('beige',(0.62,0.55,0.40),rough=0.55)
    dark=mat('dark',(0.05,0.05,0.05),rough=0.5)
    box('monitor',(1.3,0.95,1.0),loc=(0,0.1,0.35),bevel=0.08,seg=6,m=beige,parent=root)
    box('bezel',(1.06,0.05,0.76),loc=(0,-0.39,0.38),bevel=0.05,seg=6,m=dark,parent=root)
    screen_plane('scr',0.92,0.64,(0,-0.418,0.38),img,root,1.4)
    box('kbd',(1.4,0.55,0.12),loc=(0,-0.75,-0.32),bevel=0.04,seg=4,m=beige,parent=root)
    key=mat('key',(0.52,0.46,0.34),rough=0.6)
    for r in range(4):
        for k in range(12):
            box(f'k{r}{k}',(0.085,0.085,0.05),loc=(-0.55+k*0.1,-0.92+r*0.11,-0.24),bevel=0.015,seg=2,m=key,parent=root)
    return root

def environment(style='light', pedestal=True):
    sc=bpy.context.scene; sc.render.film_transparent=False
    w=sc.world.node_tree.nodes['Background']
    if style=='light':
        floor_c,wall_c,ped=(0.78,0.78,0.79),(0.82,0.82,0.83),('alu',(0.80,0.81,0.83),1.0,0.22)
        w.inputs[0].default_value=(0.6,0.6,0.62,1); w.inputs[1].default_value=0.35
    else:
        sc.view_settings.exposure=-1.4
        floor_c,wall_c,ped=(0.05,0.05,0.055),(0.04,0.04,0.045),('anod',(0.22,0.225,0.24),1.0,0.3)
        w.inputs[0].default_value=(0.02,0.02,0.025,1); w.inputs[1].default_value=1.0
    # cyclorama : sol + arrondi + mur, sans angle visible
    import bmesh
    me=bpy.data.meshes.new('cyc'); bm=bmesh.new(); prof=[]
    R=2.0
    for i in range(0,25): prof.append((-6+i*0.25*0+(-6+i*(4/24))*0, 0))  # placeholder
    prof=[(y,0.0) for y in [ -8,-4,-1,0.5,1.5 ]]
    for k in range(1,17):
        a=math.radians(90*k/16); prof.append((1.5+R*math.sin(a), R-R*math.cos(a)))
    prof+= [(1.5+R,R+3),(1.5+R,R+8)]
    vs=[]
    for x in (-12,12):
        vs.append([bm.verts.new((x,y,z-1.0)) for y,z in prof])
    for j in range(len(prof)-1): bm.faces.new((vs[0][j],vs[0][j+1],vs[1][j+1],vs[1][j]))
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new('cyc',me); bpy.context.collection.objects.link(o)
    for p in o.data.polygons: p.use_smooth=True
    m=bpy.data.materials.new('cycm'); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*floor_c,1); b.inputs['Roughness'].default_value=0.55 if style=='light' else 0.8
    if style=='dark':   # béton : bruit dans la rugosité et le relief
        n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=60; n.inputs['Detail'].default_value=8
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.12
        nt.links.new(n.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],b.inputs['Normal'])
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.03,0.03,0.033,1); ramp.color_ramp.elements[1].color=(0.075,0.075,0.08,1)
        nt.links.new(n.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],b.inputs['Base Color'])
    o.data.materials.append(m)
    # socle en aluminium
    if pedestal:
        bpy.ops.mesh.primitive_cylinder_add(radius=1.05,depth=0.22,location=(0,0.2,-0.89),vertices=128); p=bpy.context.object
        md=p.modifiers.new('bv','BEVEL'); md.width=0.02; md.segments=4; bpy.ops.object.shade_smooth()
        p.data.materials.append(mat(ped[0],ped[1],metal=ped[2],rough=ped[3]))
    # éclairage studio doux
    for l in [o_ for o_ in bpy.data.objects if o_.type=='LIGHT']: bpy.data.objects.remove(l)
    def area(loc,rot,size,energy,color=(1,1,1)):
        bpy.ops.object.light_add(type='AREA',location=loc,rotation=rot); l=bpy.context.object; l.data.size=size; l.data.energy=energy; l.data.color=color; return l
    if style=='light':
        area((0,0.2,4.5),(0,0,0),5,900); area((-3.2,-2.5,1.8),(math.radians(65),0,math.radians(-50)),2.5,300); area((3,-2,1.2),(math.radians(75),0,math.radians(55)),2,150)
    else:
        area((0,0.3,3.6),(0,0,0),1.6,380); area((0,2.8,1.4),(math.radians(-70),0,0),2.2,650,(0.7,0.82,1.0)); area((-3,-2.2,1.0),(math.radians(75),0,math.radians(-55)),1.2,70)
def env_camera(dist=5.2,h=0.9,lens=55,look_z=0.05):
    bpy.ops.object.camera_add(location=(0,-dist,h)); c=bpy.context.object; c.data.lens=lens
    ang=math.atan2(h-look_z,dist); c.rotation_euler=(math.radians(90)-ang,0,0); bpy.context.scene.camera=c
    bpy.context.scene.render.resolution_x=int(os.environ.get('RX','540')); bpy.context.scene.render.resolution_y=int(os.environ.get('RY','960'))
