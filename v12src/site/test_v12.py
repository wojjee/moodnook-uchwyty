# v12 site tests (static): python3 test_v12.py SITE_DIR TEST_RESULTS_JSON
#  1. configurator combos (pull/knob/door/window/esc) are a subset of the passing combos in test_results.json
#  2. every product (and mix / family / exploded image) has its WebP files (640 + 1200), every module GLB exists
#  3. SKUs are unique (products, combos), product SKUs are allowed combos, inquiry/PDF assets present
import json, os, re, sys
site, trp = sys.argv[1], sys.argv[2]
s = open(os.path.join(site, 'v12/data.js'), encoding='utf-8').read()
N = json.loads(s[s.index('=') + 1:].strip().rstrip(';'))
TR = json.load(open(trp))
fails = []; checks = 0
def ok(c, msg):
    global checks; checks += 1
    if not c: fails.append(msg)
ok(TR.get('allok') is True, 'test_results allok is not true')
for kind in ('pull', 'knob', 'door', 'window'):
    passing = {re.sub(r'/[A-Z.]+$', '', e['sku']) for e in TR[kind] if e['ok']}
    combos = N['combos'][kind]
    ok(len(combos) == len(set(combos)), kind + ': duplicate combos')
    extra = sorted(set(combos) - passing)
    ok(not extra, '%s: %d configurator combos not in passing test results, e.g. %s' % (kind, len(extra), extra[:3]))
    ok(len(combos) == TR['counts'][kind]['passed'], '%s: %d combos vs %s passed in test counts' % (kind, len(combos), TR['counts'][kind]))
    ok(not [e for e in TR[kind] if not e['ok'] and re.sub(r'/[A-Z.]+$', '', e['sku']) in combos], kind + ': failing combo offered')
esc_ok = {e['key'][0] for e in TR['esc'] if e['ok']}
ok(set(N['combos']['esc']) <= esc_ok, 'esc dirs not all passing')
img = os.path.join(site, 'v12/img')
def has(name):
    return all(os.path.getsize(os.path.join(img, '%s-%d.webp' % (name, w))) > 2000 if os.path.exists(os.path.join(img, '%s-%d.webp' % (name, w))) else False for w in (640, 1200))
skus = [p['sku'] for p in N['products']]
ok(len(skus) == len(set(skus)), 'duplicate product SKUs: %s' % sorted({x for x in skus if skus.count(x) > 1}))
ok(len({p['id'] for p in N['products']}) == len(N['products']), 'duplicate product ids')
allc = {k: set(v) for k, v in N['combos'].items()}
for p in N['products']:
    ok(len(p.get('img') or []) >= 1, p['id'] + ': no image listed')
    for n in p.get('img') or []: ok(has(n), p['id'] + ': missing image ' + n)
    core = p['sku'].rsplit('/', 1)[0]
    if p['kind'] == 'door': core = re.sub(r'/[A-Z]{2}-E\w+$', '', core)
    ok(core in allc[p['kind']], p['id'] + ': product SKU not an allowed combo ' + p['sku'])
for m in N['mix']:
    ok(has(m['id']), 'mix image missing ' + m['id'])
    core = m['sku'].rsplit('/', 1)[0]
    ok(core in allc['pull'] or core in allc['knob'], 'mix SKU not allowed ' + m['sku'])
for d in ('OT', 'PN', 'OB', 'OS', 'KS'):
    ok(has('family_' + d), 'family image missing ' + d)
    ok(len([p for p in N['products'] if p['dir'] == d]) >= 4, d + ': fewer than 4 products')
for n in N['images']: ok(has(n), 'listed image missing ' + n)
for code, m in N['modules'].items():
    ok(os.path.exists(os.path.join(site, 'v12', m['file'])), 'module GLB missing ' + code)
ok(os.path.getsize(os.path.join(site, N['pdf'])) > 100000, 'PDF missing/small')
print(json.dumps({'checks': checks, 'products': len(N['products']), 'combos': {k: len(v) for k, v in N['combos'].items()}, 'failures': fails[:30]}, indent=1, ensure_ascii=False))
print('V12 STATIC TEST ' + ('FAILED %d' % len(fails) if fails else 'PASSED (%d checks)' % checks))
sys.exit(1 if fails else 0)
