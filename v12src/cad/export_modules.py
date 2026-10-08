import sys, os, json
sys.path.insert(0, os.environ.get('NF_CAD', '/workspace/moodnook/ai-design'))
from nookcad import *
from nookcad import _compound
OUT = sys.argv[1]
os.makedirs(OUT + '/mod', exist_ok=True)
STEP = os.environ.get('NF_STEP', '/workspace/moodnook/v11/step')
MODS = {}

def keep(m):
    return {k: round(v, 3) if isinstance(v, float) else v for k, v in m.meta.items() if isinstance(v, (int, float, str, bool, type(None))) or (isinstance(v, (list, tuple)) and len(v) < 8)}

def put(m, code=None):
    code = code or m.code
    if code in MODS:
        return
    c = _compound([[lab, p, mt] for lab, (p, mt) in m.parts.items()], code)
    f = code.replace('/', '_') + '.glb'
    export_gltf(c, f'{OUT}/mod/{f}', unit=Unit.MM, binary=True, linear_deflection=0.035, angular_deflection=0.35)
    bb = c.bounding_box()
    MODS[code] = dict(kind=m.kind, dir=m.dir, file='mod/' + f, meta=keep(m), bbox=[[round(bb.min.X, 2), round(bb.min.Y, 2), round(bb.min.Z, 2)], [round(bb.max.X, 2), round(bb.max.Y, 2), round(bb.max.Z, 2)]], mats=sorted({mt for _, mt in m.parts.values()}), mass_g=round(m.mass_g(), 1))
    print(code, os.path.getsize(f'{OUT}/mod/{f}') // 1024, 'kB', flush=True)
for fam, Hs in (('SR7', (12, 30)), ('SR8', (12, 30)), ('SQ7', (30,)), ('SK8', (12, 30)), ('OTD', (12,))):
    for H in Hs:
        put(make_post(fam, H))
for st in STEMS:
    put(make_stem(st), st)
for w in ('WR12', 'WR13', 'WD14', 'WS11', 'WT17'):
    put(make_washer(w))
for rd, vd in ((8, 8), (10, 10), (8, 12), (8, 13), (10, 15)):
    for st in 'RF':
        put(make_collar(rd, vd, st))
for D in DIRS:
    for cc in SYS['SPACINGS']:
        put(BAR_GEN[D](cc))
        if D == 'OS':
            put(bar_OS(cc, 'JS'))
    for s in 'SML':
        put(head(D, s))
    put(lever(D, 'door'))
    put(rose(D, 'door'))
    put(lever(D, 'win'))
    put(rose(D, 'win'))
    for e in ('PZ', 'BB', 'WCi', 'WCo'):
        put(escutcheon(D, e))
json.dump(dict(sys={k: SYS[k] for k in ('PZ_DIST', 'WC_DIST', 'SPACINGS')}, finish_default=FINISH_DEFAULT, knob_default=KNOB_DEFAULT, stems=STEMS, modules=MODS), open(f'{OUT}/modules.json', 'w'), indent=0)
print('modules', len(MODS))
if os.environ.get('NF_JS', '1') == '1':
    C = {}
    for cc in SYS['SPACINGS']:
        bar = bar_OS(cc, 'JS')
        col = make_collar(bar.meta['rod_d'], bar.meta['vis_d'], 'F')
        A = assemble_pull(bar, make_post('SR8', 30), make_washer('WR13'), col)
        A.name = f'OS-JS-pull-{cc}'
        export_assy(A, f'{STEP}/OS/assemblies', step=False)
        print(A.name, A.meta['sku'])
