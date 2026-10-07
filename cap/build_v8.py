# Rebuilds the v8 page from the deployed v6 chunks + cap/v8patch.*.txt (text-only deploy path), verifies SHA-1, writes v8/00..05.b64 (+ optional v9 text edits)
# patch format: "@ start end n\n" + n chars of replacement text + "\n", offsets into the decoded v6 page
import sys,glob,base64,gzip,hashlib,os,re
src,dst=sys.argv[1],sys.argv[2]; here=os.path.dirname(os.path.abspath(__file__))
A=gzip.decompress(base64.b64decode(''.join(open(f).read() for f in sorted(glob.glob(src+'/v6/*.b64'))).replace('\n','').replace(' ',''))).decode()
ops=[]
for f in sorted(glob.glob(here+'/v8patch.*.txt'),key=lambda x:int(x.split('.')[-2])):
  T=open(f,encoding='utf-8').read();i=0
  while i<len(T):
    m=re.compile(r'@ (\d+) (\d+) (\d+)\n').match(T,i); assert m,'bad patch header in %s at %d'%(f,i)
    n=int(m.group(3)); t=T[m.end():m.end()+n]; assert T[m.end()+n]=='\n'; ops.append((int(m.group(1)),int(m.group(2)),t)); i=m.end()+n+1
ops.sort();r=[];p=0
for s,e,t in ops: assert s>=p; r.append(A[p:s]);r.append(t);p=e
r.append(A[p:]);B=''.join(r).encode()
want=open(here+'/v8patch.sha1').read().strip()
assert hashlib.sha1(B).hexdigest()==want,'patched page SHA-1 mismatch %s'%hashlib.sha1(B).hexdigest()
# v9: exact-match text edits applied on top of the SHA-verified v8 page (cap/v9edits.json then cap/v9bedits.json: [[old,new,count],...]), verified by cap/v9.sha1
import json
if os.path.exists(here+'/v9edits.json'):
  T=B.decode()
  for o,nw,c in [x for f in ('v9edits.json','v9bedits.json') if os.path.exists(here+'/'+f) for x in json.load(open(here+'/'+f,encoding='utf-8'))]:
    assert T.count(o)==c,'v9 edit expects %d match(es), found %d: %r'%(c,T.count(o),o[:80]); T=T.replace(o,nw)
  B=T.encode(); want9=open(here+'/v9.sha1').read().strip() if os.path.exists(here+'/v9.sha1') else ''
  assert want9 in('',hashlib.sha1(B).hexdigest()),'v9 page SHA-1 mismatch %s'%hashlib.sha1(B).hexdigest()
  if os.environ.get('NF_DUMP'): open(os.environ['NF_DUMP'],'wb').write(B)
z=base64.b64encode(gzip.compress(B,9,mtime=0)).decode();n=6;k=-(-len(z)//n)
os.makedirs(dst+'/v8',exist_ok=True)
for i in range(n): open('%s/v8/%02d.b64'%(dst,i),'w').write(z[i*k:(i+1)*k])
print('v8 ok',len(ops),len(B),len(z))
