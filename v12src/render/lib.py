import bpy, math
from mathutils import Vector
MM = 0.001

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 200
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.015
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 10
    sc.cycles.glossy_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = -0.55
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 1200
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    sc.unit_settings.scale_length = 1.0
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.55, 0.45, 0.34, 1)
    bg.inputs[1].default_value = 0.035
    return sc

def _p(mat):
    return mat.node_tree.nodes['Principled BSDF']

def mat_brass(name='brass_satin', rough=0.34, color=(0.5, 0.355, 0.17), aniso=0.0, brushed=True):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = _p(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    if aniso:
        p.inputs['Anisotropic'].default_value = aniso
    if brushed:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (60, 4000, 4000)
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 1.0
        nz.inputs['Detail'].default_value = 4
        nt.links.new(tc.outputs['Object'], mp.inputs[0])
        nt.links.new(mp.outputs[0], nz.inputs[0])
        bm = nt.nodes.new('ShaderNodeBump')
        bm.inputs['Strength'].default_value = 0.03
        bm.inputs['Distance'].default_value = 5e-05
        nt.links.new(nz.outputs['Fac'], bm.inputs['Height'])
        nt.links.new(bm.outputs[0], p.inputs['Normal'])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs[3].default_value = rough * 0.85
        mr.inputs[4].default_value = rough * 1.15
        nt.links.new(nz.outputs['Fac'], mr.inputs[0])
        nt.links.new(mr.outputs[0], p.inputs['Roughness'])
    return m

def mat_polished(name='brass_polished'):
    return mat_brass(name, rough=0.05, color=(0.62, 0.45, 0.23), brushed=False)

def mat_simple(name, color, rough=0.5, spec=0.5, sheen=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = _p(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Specular IOR Level'].default_value = spec
    if sheen:
        p.inputs['Sheen Weight'].default_value = sheen
    if coat:
        p.inputs['Coat Weight'].default_value = coat
    return m

def mat_stone(name='stone', c1=(0.68, 0.6, 0.5), c2=(0.6, 0.52, 0.42), scale=6.0, rough=0.62, pores=True):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = _p(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = scale
    nz.inputs['Detail'].default_value = 8
    nz.inputs['Roughness'].default_value = 0.55
    nt.links.new(tc.outputs['Object'], nz.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*c2, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Specular IOR Level'].default_value = 0.35
    if pores:
        vo = nt.nodes.new('ShaderNodeTexVoronoi')
        vo.inputs['Scale'].default_value = 900.0
        vo.feature = 'F1'
        nt.links.new(tc.outputs['Object'], vo.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs[1].default_value = 0.0
        mr.inputs[2].default_value = 0.12
        mr.inputs[3].default_value = 0
        mr.inputs[4].default_value = 1
        nt.links.new(vo.outputs['Distance'], mr.inputs[0])
        nz2 = nt.nodes.new('ShaderNodeTexNoise')
        nz2.inputs['Scale'].default_value = 300
        nz2.inputs['Detail'].default_value = 6
        nt.links.new(tc.outputs['Object'], nz2.inputs[0])
        mx = nt.nodes.new('ShaderNodeMath')
        mx.operation = 'MULTIPLY'
        nt.links.new(mr.outputs[0], mx.inputs[0])
        nt.links.new(nz2.outputs['Fac'], mx.inputs[1])
        bm = nt.nodes.new('ShaderNodeBump')
        bm.inputs['Strength'].default_value = 0.12
        bm.inputs['Distance'].default_value = 0.0002
        nt.links.new(mx.outputs[0], bm.inputs['Height'])
        nt.links.new(bm.outputs[0], p.inputs['Normal'])
    return m

def mat_linen(name='linen', color=(0.7, 0.62, 0.52)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = _p(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    w1 = nt.nodes.new('ShaderNodeTexWave')
    w1.wave_type = 'BANDS'
    w1.bands_direction = 'X'
    w1.inputs['Scale'].default_value = 900
    w1.inputs['Distortion'].default_value = 2
    w2 = nt.nodes.new('ShaderNodeTexWave')
    w2.wave_type = 'BANDS'
    w2.bands_direction = 'Z'
    w2.inputs['Scale'].default_value = 900
    w2.inputs['Distortion'].default_value = 2
    for w in (w1, w2):
        nt.links.new(tc.outputs['Object'], w.inputs[0])
    mx = nt.nodes.new('ShaderNodeMath')
    mx.operation = 'ADD'
    nt.links.new(w1.outputs['Fac'], mx.inputs[0])
    nt.links.new(w2.outputs['Fac'], mx.inputs[1])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 25
    nt.links.new(tc.outputs['Object'], nz.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (color[0] * 0.9, color[1] * 0.9, color[2] * 0.88, 1)
    ramp.color_ramp.elements[1].color = (*color, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], p.inputs['Base Color'])
    bm = nt.nodes.new('ShaderNodeBump')
    bm.inputs['Strength'].default_value = 0.25
    bm.inputs['Distance'].default_value = 0.0003
    nt.links.new(mx.outputs[0], bm.inputs['Height'])
    nt.links.new(bm.outputs[0], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = 0.9
    p.inputs['Specular IOR Level'].default_value = 0.2
    p.inputs['Sheen Weight'].default_value = 0.3
    return m

def mat_wood(name='oak', c_light=(0.3, 0.16, 0.065), c_dark=(0.17, 0.085, 0.03), axis='X', ring_scale=60.0, rough=0.5, offset=(0, 0, 0), coat=0.0, fine_scale=900, mix_f=0.18):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = _p(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Location'].default_value = offset
    sc = {'X': (0.04, 1, 1), 'Y': (1, 0.04, 1), 'Z': (1, 1, 0.04)}[axis]
    mp.inputs['Scale'].default_value = sc
    nt.links.new(tc.outputs['Object'], mp.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 25.0
    nz.inputs['Detail'].default_value = 2
    nt.links.new(mp.outputs[0], nz.inputs[0])
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'
    wv.bands_direction = {'X': 'Y', 'Y': 'X', 'Z': 'X'}[axis]
    wv.inputs['Scale'].default_value = ring_scale
    wv.inputs['Distortion'].default_value = 6.0
    wv.inputs['Detail'].default_value = 2
    wv.inputs['Detail Scale'].default_value = max(2.0, ring_scale / 45.0)
    wv.wave_profile = 'SIN'
    nt.links.new(mp.outputs[0], wv.inputs[0])
    fine = nt.nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = fine_scale
    fine.inputs['Detail'].default_value = 2
    nt.links.new(mp.outputs[0], fine.inputs[0])
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 3.0
    nt.links.new(wv.outputs['Fac'], pw.inputs[0])
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'FLOAT'
    mx.inputs['Factor'].default_value = mix_f
    nt.links.new(pw.outputs[0], mx.inputs[2])
    nt.links.new(fine.outputs['Fac'], mx.inputs[3])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (*c_light, 1)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (*c_dark, 1)
    nt.links.new(mx.outputs[0], ramp.inputs[0])
    big = nt.nodes.new('ShaderNodeTexNoise')
    big.inputs['Scale'].default_value = 8.0
    nt.links.new(tc.outputs['Object'], big.inputs[0])
    hsv = nt.nodes.new('ShaderNodeHueSaturation')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs[3].default_value = 0.9
    mr.inputs[4].default_value = 1.08
    nt.links.new(big.outputs['Fac'], mr.inputs[0])
    nt.links.new(mr.outputs[0], hsv.inputs['Value'])
    nt.links.new(ramp.outputs[0], hsv.inputs['Color'])
    nt.links.new(hsv.outputs[0], p.inputs['Base Color'])
    bm = nt.nodes.new('ShaderNodeBump')
    bm.inputs['Strength'].default_value = 0.06
    bm.inputs['Distance'].default_value = 0.0001
    nt.links.new(mx.outputs[0], bm.inputs['Height'])
    nt.links.new(bm.outputs[0], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Specular IOR Level'].default_value = 0.3
    if coat:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = 0.3
    return m

def box(name, size, center, bevel=0.3, segs=3, mat=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0] * MM, size[1] * MM, size[2] * MM)
    ob.location = Vector(center) * MM
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        md = ob.modifiers.new('bev', 'BEVEL')
        md.width = bevel * MM
        md.segments = segs
        md.limit_method = 'NONE'
        md.harden_normals = False
    ob.data.shade_smooth()
    try:
        ob.data.set_sharp_from_angle(angle=math.radians(35))
    except Exception:
        pass
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob

def plane(name, size, loc, rot=(0, 0, 0), mat=None):
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    return ob

def studio(floor_mat=None, wall_mat=None, wall_dist=0.55, key=1.0, warm=True, floor=True, wall=True, dark_flags=True):
    if floor_mat is None:
        floor_mat = mat_stone()
    if wall_mat is None:
        wall_mat = mat_linen()
    if floor:
        plane('floor', (3, 3), (0, 0.4, 0), mat=floor_mat)
    if wall:
        plane('wall', (3, 2), (0, wall_dist, 1.0), rot=(math.radians(90), 0, 0), mat=wall_mat)
    col = (1.0, 0.93, 0.84) if warm else (1, 1, 1)

    def area(name, loc, size, energy, color=col, target=(0, 0, 0.02), spread=None):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.shape = 'RECTANGLE'
        ld.size = size[0]
        ld.size_y = size[1]
        ld.energy = energy
        ld.color = color
        if spread:
            ld.spread = math.radians(spread)
        ob = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(ob)
        ob.location = loc
        d = Vector(target) - Vector(loc)
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return ob
    area('key', (-0.5, 0.32, 0.55), (0.45, 0.45), 40 * key)
    area('strip', (0.45, -0.15, 0.3), (0.12, 0.9), 7 * key, color=(1, 0.97, 0.93))
    area('fill', (0.0, -0.9, 0.45), (1.2, 0.6), 3.5 * key, color=(1, 0.96, 0.9))
    if dark_flags:
        fl = mat_simple('flag', (0.03, 0.025, 0.02), rough=0.9)
        f = plane('flag1', (0.5, 0.5), (0.35, 0.35, 0.25), rot=(math.radians(90), 0, math.radians(-40)), mat=fl)
        f.visible_camera = False
        f2 = plane('flag2', (0.6, 0.3), (-0.4, -0.45, 0.25), rot=(math.radians(75), 0, math.radians(-40)), mat=fl)
        f2.visible_camera = False
        f3 = plane('flag3', (1.2, 1.2), (0.0, -0.2, 1.3), rot=(0, 0, 0), mat=fl)
        f3.visible_camera = False
        f3.visible_shadow = False

def camera(target, dist, elev_deg, azim_deg, lens=100, fstop=8.0, shift=(0, 0), focus=None):
    t = Vector(target) * MM
    e = math.radians(elev_deg)
    a = math.radians(azim_deg)
    loc = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cd = bpy.data.cameras.new('cam')
    cd.lens = lens
    cd.sensor_width = 36
    cd.shift_x, cd.shift_y = shift
    ob = bpy.data.objects.new('cam', cd)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (t - loc).to_track_quat('-Z', 'Y').to_euler()
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    cd.dof.focus_distance = ((Vector(focus) * MM if focus else t) - loc).length
    bpy.context.scene.camera = ob
    return ob

def render(path, samples=None):
    sc = bpy.context.scene
    if samples:
        sc.cycles.samples = samples
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
