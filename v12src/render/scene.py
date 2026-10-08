"""v11 scene renderer: places GLBs (true mm) in the v10 studio and assigns materials by node-name prefix.
blender -b --factory-startup -P scene.py -- spec.json
spec: {out, samples, res:[w,h], camera:{target,dist,elev,azim,lens,fstop,focus}, key,
       items:[{glb, loc:[mm], rot:[deg x,y,z], scale}], boxes:[{size,center,mat,bevel}], anchors:{name:[mm xyz]}}"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view
from lib import *

spec = json.load(open(sys.argv[sys.argv.index('--') + 1]))
sc = reset()
W, H = spec.get('res', [1600, 1200]); sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = int(spec.get('pct', 100))
sc.cycles.samples = spec.get('samples', 96)
studio(key=spec.get('key', 1.0), wall_dist=spec.get('wall_dist', 0.55))
M = {'brass': mat_brass(), 'pol': mat_polished(), 'matte': mat_brass('brass_matte', rough=0.47),
     'steel': mat_brass('steel', rough=0.28, color=(0.30, 0.30, 0.31), brushed=False),
     'oakpanel': mat_wood('oakpanel', c_light=(0.36, 0.21, 0.09), c_dark=(0.22, 0.12, 0.05), axis='Z', ring_scale=140, rough=0.55),
     'sand': mat_stone('sandlacquer', c1=(0.62, 0.55, 0.46), c2=(0.58, 0.51, 0.42), scale=3, rough=0.5, pores=False),
     'taupe': mat_simple('taupe', (0.30, 0.25, 0.20), rough=0.45, spec=0.4),
     'greige': mat_simple('greige', (0.42, 0.37, 0.31), rough=0.45, spec=0.4)}
wood_cache = {}


def wood(kind, axis):
    k = (kind, axis)
    if k not in wood_cache:
        # handle-scale grain: object space is metres, so ~1 mm grain needs scale ~ 1000/m (v10 values were furniture-scale)
        if kind == 'oak':   # natural oiled oak
            wood_cache[k] = mat_wood('oak_' + axis, c_light=(0.30, 0.165, 0.07), c_dark=(0.13, 0.065, 0.027), axis=axis,
                                     ring_scale=700, fine_scale=2600, mix_f=0.30, rough=0.52)
        else:               # ash: pale but with clearly visible darker latewood lines
            wood_cache[k] = mat_wood('ash_' + axis, c_light=(0.50, 0.38, 0.24), c_dark=(0.22, 0.145, 0.075), axis=axis,
                                     ring_scale=650, fine_scale=2600, mix_f=0.26, rough=0.55)
    return wood_cache[k]


for i, it in enumerate(spec.get('items', [])):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=it['glb'])
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(f'item{i}', None); bpy.context.collection.objects.link(root)
    root.location = Vector(it.get('loc', (0, 0, 0))) * MM
    rx, ry, rz = [math.radians(v) for v in it.get('rot', (0, 0, 0))]
    root.rotation_euler = Euler((rx, ry, rz), 'XYZ')
    off = it.get('explode', {})
    for o in new:
        if o.parent is None:
            o.parent = root
        if o.type != 'MESH':
            continue
        nm = o.name
        pre = nm.split('_')[0].lower()
        if pre in ('oak', 'ash'):
            dims = o.dimensions
            ax = 'XYZ'[max(range(3), key=lambda k: dims[k])]
            mat = wood(pre, ax)
        else:
            mat = M.get(pre, M['brass'])
        if it.get('mat_override') and pre in ('brass', 'matte'):
            mat = M[it['mat_override']]
        o.data.materials.clear(); o.data.materials.append(mat)
        for key, dz in off.items():
            if key in nm:
                o.location = o.location + Vector(dz) * MM
for b in spec.get('boxes', []):
    box(b.get('name', 'box'), b['size'], b['center'], bevel=b.get('bevel', 0.8), segs=2, mat=M[b.get('mat', 'sand')])
c = spec['camera']
cam = camera(tuple(c['target']), c['dist'], c['elev'], c['azim'], lens=c.get('lens', 100), fstop=c.get('fstop', 10),
             focus=tuple(c['focus']) if c.get('focus') else None)
bpy.context.view_layer.update()
anch = {}
for k, p in spec.get('anchors', {}).items():
    v = world_to_camera_view(sc, cam, Vector(p) * MM)
    anch[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
if anch:
    json.dump(anch, open(os.path.splitext(spec['out'])[0] + '_anchors.json', 'w'), indent=1)
render(os.path.abspath(spec['out']), spec.get('samples', 96))
