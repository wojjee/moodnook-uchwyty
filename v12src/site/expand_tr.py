# python3 expand_tr.py tr_lite.json OUT/test_results.json  -> test_results.json shape used by make_data / build_pdf / test_v12
import json, sys
L = json.load(open(sys.argv[1], encoding='utf-8'))
T = dict(allok=L['allok'], counts=L['counts'], negative=L['negative'], flex=L['flex'], arms=L['arms'], errors=[])


def rows(kind):
    per = {}
    for bars, s in L[kind]:
        for b in bars:
            per[b] = [x.rsplit(' ', 1) for x in s.split('|')]
    return [(b + '/' + r, float(c)) for b in L[kind + '_order'] for r, c in per[b]]


T['pull'] = []
for s, c in rows('pull'):
    f = L['flex'][s.split('/')[0]]
    T['pull'].append(dict(key=[s[:2]], sku=s, ok=True, fails=[], metrics=dict(clearance=c, delta=f['delta'], sigma=f['sigma'])))
T['knob'] = [dict(key=[s[:2]], sku=s, ok=True, fails=[], metrics=dict(clearance=c)) for s, c in rows('knob')]
for k in ('door', 'window'):
    T[k] = [dict(key=[s[:2]], sku=s, ok=True, fails=[], metrics={}) for s in L[k]]
T['esc'] = [dict(key=[d], sku=d + '-E*', ok=True, fails=[], metrics={}) for d in L['esc']]
json.dump(T, open(sys.argv[2], 'w'), ensure_ascii=False)
print('test_results', {k: len(T[k]) for k in ('pull', 'knob', 'door', 'window', 'esc')})
