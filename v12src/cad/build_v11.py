import sys, os, json, time, argparse
sys.path.insert(0, '/workspace/moodnook/ai-design')
from nookcad import *
ROOT = '/workspace/moodnook/v11/step'
ap = argparse.ArgumentParser()
ap.add_argument('--only', default=','.join(DIRS))
ap.add_argument('--sys', action='store_true')
ap.add_argument('--mix', action='store_true')
ap.add_argument('--all', action='store_true')
a = ap.parse_args()
t0 = time.time()
C = {}

def log(*x):
    print(f'[{time.time() - t0:6.1f}s]', *x, flush=True)

def dump(path, obj):
    json.dump(obj, open(path, 'w'), indent=1, ensure_ascii=False, default=str)
if a.sys or a.all:
    d = f'{ROOT}/SYS/parts'
    man = []
    for fam, Hs in (('SR7', (12, 30)), ('SR8', (12, 30)), ('SQ7', (30,)), ('SK8', (12, 30)), ('OTD', (12,))):
        for H in Hs:
            man.append(export_mod(make_post(fam, H), d))
    for st in STEMS:
        man.append(export_mod(make_stem(st), d))
    for w in ('WR12', 'WR13', 'WD14', 'WS11', 'WT17'):
        man.append(export_mod(make_washer(w), d))
    for rd, vd in ((8, 8), (10, 10), (8, 12), (8, 13), (10, 15)):
        for st in 'RF':
            man.append(export_mod(make_collar(rd, vd, st), d))
    for L in STUD_LENGTHS:
        man.append(export_mod(m4_stud(L), d))
    for L in (22, 25, 30, 35):
        man.append(export_mod(m4_screw(L), d))
    dump(f'{ROOT}/SYS/manifest.json', dict(modules=man, density_g_mm3=SYS['RHO'], material='CW724R (CuZn21Si3P)'))
    log('SYS', len(man))
for D in [x for x in a.only.split(',') if x] if not a.mix or a.all else []:
    pd, ad = (f'{ROOT}/{D}/parts', f'{ROOT}/{D}/assemblies')
    mods, assys = ([], [])
    for cc in SYS['SPACINGS']:
        mods.append(export_mod(C.setdefault(('bar', D, cc), BAR_GEN[D](cc)), pd))
        if D == 'OS':
            mods.append(export_mod(bar_OS(cc, 'JS'), pd))
    for s in 'SML':
        mods.append(export_mod(C.setdefault(('head', D, s), head(D, s)), pd))
    lv, rs = (lever(D, 'door'), rose(D, 'door'))
    wh, wr = (lever(D, 'win'), rose(D, 'win'))
    escs = {e: escutcheon(D, e) for e in ('PZ', 'BB', 'WCi', 'WCo')}
    for m in [lv, rs, wh, wr] + list(escs.values()):
        mods.append(export_mod(m, pd))
    log(D, 'parts', len(mods))
    for cc in SYS['SPACINGS']:
        A = family_pull(D, cc, C)
        A.name = f'{D}-pull-{cc}'
        assys.append(export_assy(A, ad))
    for s in 'SML':
        A = family_knob(D, s, C)
        A.name = f'{D}-knob-{s}'
        assys.append(export_assy(A, ad))
    for nm, es in (('door-PZ', ['PZ']), ('door-BB', ['BB']), ('door-WC-in', ['WCi']), ('door-WC-out', ['WCo']), ('door', [])):
        A = assemble_door(lv, rs, [escs[e] for e in es], name=f'{D}-{nm}')
        assys.append(export_assy(A, ad))
    A = assemble_window(wh, wr, name=f'{D}-window')
    assys.append(export_assy(A, ad))
    dump(f'{ROOT}/{D}/manifest.json', dict(direction=DIR_NAMES[D], modules=mods, assemblies=assys, density_g_mm3=SYS['RHO'], material='CW724R (CuZn21Si3P)'))
    log(D, 'assemblies', len(assys))
MIX = [('MIX1_KS-bar_on_PN-SQ7', lambda: assemble_pull(bar_KS(128), make_post('SQ7', 30), make_washer('WS11'))), ('MIX2_OB-ring_on_OS-oak', lambda: assemble_pull(bar_OS(128), make_post('SR8', 30), make_washer('WR12'), make_collar(8, 12, 'R'), 'SB.PB')), ('MIX3_PN-fin_on_KS-SK8', lambda: assemble_pull(bar_PN(128), make_post('SK8', 30), None)), ('MIX4_OB-rod_on_KS-SK8', lambda: assemble_pull(bar_OB(128), make_post('SK8', 30), None, make_collar(8, 8, 'R'), 'SB.PB')), ('MIX5_OT-pebble_on_SR8-WR12', lambda: assemble_pull(bar_OT(128), make_post('SR8', 12), make_washer('WR12'), None, 'SB.PB')), ('MIX6_OS-ash_on_KS-SK8', lambda: assemble_pull(bar_OS(128, 'JS'), make_post('SK8', 30), None, make_collar(8, 12, 'F'))), ('MIX7_PN-fin_on_SR7-WT17', lambda: assemble_pull(bar_PN(128), make_post('SR7', 30), make_washer('WT17'))), ('MIX8_KS-knob_on_OB-stem', lambda: assemble_knob(head('KS', 'M'), make_stem('SR7-K21'), make_washer('WR12'), 'SB.PB')), ('MIX9_OB-knob_on_KS-stem', lambda: assemble_knob(head('OB', 'M'), make_stem('SK8-K18.5'), None, 'SB.PB')), ('MIX10_OS-lever_on_KS-rose', lambda: assemble_door(lever('OS'), rose('KS'), [escutcheon('KS', 'PZ')]))]
if a.mix or a.all:
    out = []
    for nm, fn in MIX:
        A = fn()
        A.name = nm
        out.append(export_assy(A, f'{ROOT}/MIX'))
        log(nm, A.meta.get('sku'))
    dump(f'{ROOT}/MIX/manifest.json', dict(assemblies=out))
log('done')
