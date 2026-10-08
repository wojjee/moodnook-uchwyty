# python3 expand_tr.py tr_lite.json OUT/test_results.json  -> test_results.json shape used by make_data / build_pdf / test_v12
import json, sys
L = json.load(open(sys.argv[1], encoding='utf-8'))
T = dict(allok=L['allok'], counts=L['counts'], negative=L['negative'], flex=L['flex'], arms=L['arms'], errors=[])
T['pull'] = [dict(key=[s[:2]], sku=s, ok=bool(o), fails=[], metrics=dict(clearance=c, delta=d, sigma=g)) for s, o, c, d, g in L['pull']]
T['knob'] = [dict(key=[s[:2]], sku=s, ok=bool(o), fails=[], metrics=dict(clearance=c)) for s, o, c in L['knob']]
for k in ('door', 'window'):
    T[k] = [dict(key=[s[:2]], sku=s, ok=bool(o), fails=[], metrics={}) for s, o in L[k]]
T['esc'] = [dict(key=[d], sku=d + '-E*', ok=bool(o), fails=[], metrics={}) for d, o in L['esc']]
json.dump(T, open(sys.argv[2], 'w'), ensure_ascii=False)
print('test_results', {k: len(T[k]) for k in ('pull', 'knob', 'door', 'window', 'esc')})
