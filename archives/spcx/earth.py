"""Terre vue de l'orbite (procédurale, aucune image externe) : océans, continents, nuages, atmosphère, lumières des villes côté nuit.
Arc de planète en bas à droite, pour la couverture SpaceX.  usage : python earth.py out.png [rx ry samples]"""
import bpy, math, sys
sys.path.insert(0, '/home/claude/visa/b3d')
import objs

def earth_mat():
    m = bpy.data.materials.new('earth'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 1.6; n.inputs['Detail'].default_value = 12; n.inputs['Roughness'].default_value = .62
    L(tc.outputs['Object'], n.inputs['Vector'])
    land = nt.nodes.new('ShaderNodeMapRange'); land.inputs[1].default_value = .50; land.inputs[2].default_value = .53   # masque terre/mer net
    L(n.outputs['Fac'], land.inputs[0])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 9; n2.inputs['Detail'].default_value = 8; L(tc.outputs['Object'], n2.inputs['Vector'])
    terr = nt.nodes.new('ShaderNodeValToRGB'); e = terr.color_ramp.elements
    e[0].color = (.04, .08, .03, 1); e[1].color = (.42, .33, .18, 1); e.new(.55).color = (.10, .14, .05, 1)
    L(n2.outputs['Fac'], terr.inputs['Fac'])
    ocean = nt.nodes.new('ShaderNodeValToRGB'); ocean.color_ramp.elements[0].color = (.004, .02, .07, 1); ocean.color_ramp.elements[1].color = (.01, .06, .16, 1)
    L(n.outputs['Fac'], ocean.inputs['Fac'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; L(land.outputs[0], mix.inputs['Factor']); L(ocean.outputs['Color'], mix.inputs[6]); L(terr.outputs['Color'], mix.inputs[7])
    L(mix.outputs[2], b.inputs['Base Color'])
    rough = nt.nodes.new('ShaderNodeMapRange'); rough.inputs[3].default_value = .25; rough.inputs[4].default_value = .85; L(land.outputs[0], rough.inputs[0]); L(rough.outputs[0], b.inputs['Roughness'])
    # lumières des villes côté nuit (émission uniquement sur la terre, points de bruit fin)
    cn = nt.nodes.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value = 40; cn.inputs['Detail'].default_value = 2; L(tc.outputs['Object'], cn.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeMapRange'); cr.inputs[1].default_value = .62; cr.inputs[2].default_value = .72; L(cn.outputs['Fac'], cr.inputs[0])
    cm = nt.nodes.new('ShaderNodeMath'); cm.operation = 'MULTIPLY'; L(cr.outputs[0], cm.inputs[0]); L(land.outputs[0], cm.inputs[1])
    # côté nuit : produit scalaire normale / direction du soleil
    geo = nt.nodes.new('ShaderNodeNewGeometry'); dot = nt.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; dot.inputs[1].default_value = (.85, -.2, .45)
    L(geo.outputs['Normal'], dot.inputs[0]); night = nt.nodes.new('ShaderNodeMapRange'); night.inputs[1].default_value = .05; night.inputs[2].default_value = -.25
    L(dot.outputs['Value'], night.inputs[0]); cm2 = nt.nodes.new('ShaderNodeMath'); cm2.operation = 'MULTIPLY'; L(cm.outputs[0], cm2.inputs[0]); L(night.outputs[0], cm2.inputs[1])
    b.inputs['Emission Color'].default_value = (1, .62, .25, 1); L(cm2.outputs[0], b.inputs['Emission Strength'])
    return m

def cloud_mat():
    m = bpy.data.materials.new('clouds'); m.use_nodes = True; nt = m.node_tree; L = nt.links.new
    for x in list(nt.nodes): nt.nodes.remove(x)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); mx = nt.nodes.new('ShaderNodeMixShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); df = nt.nodes.new('ShaderNodeBsdfDiffuse')
    df.inputs['Color'].default_value = (1, 1, 1, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 3.2; n.inputs['Detail'].default_value = 14; n.inputs['Roughness'].default_value = .65
    mp = nt.nodes.new('ShaderNodeVectorMath'); mp.operation = 'MULTIPLY'; mp.inputs[1].default_value = (1, 1, 2.6)   # bandes étirées
    L(tc.outputs['Object'], mp.inputs[0]); L(mp.outputs[0], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeMapRange'); r.inputs[1].default_value = .5; r.inputs[2].default_value = .68; L(n.outputs['Fac'], r.inputs[0])
    L(r.outputs[0], mx.inputs['Fac']); L(tr.outputs[0], mx.inputs[1]); L(df.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs[0])
    return m

def atmo_mat():
    """halo atmosphérique : émission bleue sur le bord (fresnel), transparent au centre"""
    m = bpy.data.materials.new('atmo'); m.use_nodes = True; nt = m.node_tree; L = nt.links.new
    for x in list(nt.nodes): nt.nodes.remove(x)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); add = nt.nodes.new('ShaderNodeAddShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (.25, .55, 1.0, 1)
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = .25
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0; L(lw.outputs['Facing'], pw.inputs[0])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); dot = nt.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; dot.inputs[1].default_value = (.85, -.2, .45)
    L(geo.outputs['Normal'], dot.inputs[0]); day = nt.nodes.new('ShaderNodeMapRange'); day.inputs[1].default_value = -.35; day.inputs[2].default_value = .4; L(dot.outputs['Value'], day.inputs[0])
    st = nt.nodes.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; L(pw.outputs[0], st.inputs[0]); L(day.outputs[0], st.inputs[1])
    st2 = nt.nodes.new('ShaderNodeMath'); st2.operation = 'MULTIPLY'; st2.inputs[1].default_value = 14.0; L(st.outputs[0], st2.inputs[0]); L(st2.outputs[0], em.inputs['Strength'])
    L(tr.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1]); L(add.outputs[0], out.inputs[0])
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m

def build():
    sc = objs.reset(); sc.render.film_transparent = True; sc.view_settings.exposure = 0.3
    try: sc.view_settings.look = 'AgX - High Contrast'
    except Exception: pass
    R = 10.0
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1); e = bpy.context.object; e.scale = (R, R, R); e.data.materials.append(earth_mat()); bpy.ops.object.shade_smooth()
    e.rotation_euler = (math.radians(20), math.radians(-15), math.radians(40))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.006); cl = bpy.context.object; cl.scale = (R, R, R); cl.data.materials.append(cloud_mat()); bpy.ops.object.shade_smooth()
    cl.rotation_euler = (math.radians(-30), math.radians(25), math.radians(10))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.03); at = bpy.context.object; at.scale = (R, R, R); at.data.materials.append(atmo_mat()); bpy.ops.object.shade_smooth()
    at.visible_shadow = False
    bpy.ops.object.light_add(type='SUN', rotation=(0, 0, 0)); sun = bpy.context.object; sun.data.energy = 4.5; sun.data.angle = math.radians(1.5)
    d = (.85, -.2, .45); sun.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), d[2]), 0, math.atan2(d[1], d[0])+math.pi/2)
    sun.rotation_mode = 'QUATERNION'; import mathutils; sun.rotation_quaternion = mathutils.Vector(d).to_track_quat('Z', 'Y')
    # caméra : la planète occupe le coin bas-droit, horizon courbe en diagonale
    bpy.ops.object.camera_add(location=(-9.5, -27, 9.5)); cam = bpy.context.object; cam.data.lens = 50
    look = (-6.5, 0, 7.8); dd = [look[i]-cam.location[i] for i in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(dd[0], dd[1]), -dd[2]), 0, math.atan2(dd[1], dd[0])-math.pi/2); sc.camera = cam
    return sc

if __name__ == '__main__':
    a = sys.argv[1:]; out = a[0]; rx, ry, s = (int(a[1]), int(a[2]), int(a[3])) if len(a) > 3 else (1080, 1920, 48)
    sc = build(); sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.cycles.samples = s; sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
