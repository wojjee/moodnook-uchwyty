# publication check: python3 grep_check.py SITE_DIR  (new site outputs: html/js/css/json, decoded classic page, PDF text)
import os, re, sys, glob, gzip, base64, subprocess, codecs
site = sys.argv[1]; fails = []
R = lambda ws: [codecs.decode(w, 'rot13') for w in ws]  # word lists kept rot13 so the names are not published in clear text
CI = re.compile('|'.join(w.replace(' ', r'\s*') for w in R(['ohfgre', 'chapu', 'oo fjrqra', 'orfynt', 'abgngxn jrja', 'abgngxn-jrjargeman'])), re.I)
CS = re.compile(r'\b(' + '|'.join(R(['Pebff', 'Yvarne'])) + r')\b')
def check(name, text):
    for rx in (CI, CS):
        for m in rx.finditer(text):
            fails.append('%s: %r ...%s...' % (name, m.group(0), text[max(0, m.start() - 40):m.end() + 40].replace('\n', ' ')))
files = [os.path.join(site, f) for f in ('index.html', 'klasyczna.html', '404.html', 'sitemap.xml', 'robots.txt')]
files += glob.glob(os.path.join(site, 'v12', '*.*')) + glob.glob(os.path.join(site, 'v8', 'p', '*.js'))
for f in files:
    if os.path.isfile(f) and f.endswith(('.html', '.js', '.css', '.json', '.xml', '.txt')):
        check(os.path.relpath(f, site), open(f, encoding='utf-8', errors='replace').read())
b64 = ''.join(open(f).read() for f in sorted(glob.glob(os.path.join(site, 'v8', '0*.b64'))))
check('classic page (v8/*.b64)', gzip.decompress(base64.b64decode(b64)).decode())
pdf = os.path.join(site, 'v12', 'katalog-modulowy-v11.pdf')
check('katalog PDF', subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True, check=True).stdout)
for p in ['spec'] + [w + '.md' for w in R(['abgngxn-jrjargeman-i8', 'abgngxn-jrjargeman-i9'])]:
    if os.path.exists(os.path.join(site, p)): fails.append('internal file published: ' + p)
print('\n'.join(fails) if fails else 'GREP CHECK PASSED (%d files + classic page + PDF)' % len(files))
sys.exit(1 if fails else 0)
