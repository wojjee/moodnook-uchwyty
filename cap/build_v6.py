# Rebuilds the v6 page from the deployed v5 chunks + cap/v6patch.*.txt (text-only deploy path), verifies SHA-1, writes v6/00..05.b64
# patch format: "@ start end n\n" + n chars of replacement text + "\n", offsets into the decoded v5 page
import sys,glob,base64,gzip,hashlib,os,re
src,dst=sys.argv[1],sys.argv[2]; here=os.path.dirname(os.path.abspath(__file__))
A=gzip.decompress(base64.b64decode(''.join(open(f).read() for f in sorted(glob.glob(src+'/v5/*.b64'))).replace('\n','').replace(' ',''))).decode()
ops=[]
for f in sorted(glob.glob(here+'/v6patch.*.txt'),key=lambda x:int(x.split('.')[-2])):
  T=open(f,encoding='utf-8').read();i=0
  while i<len(T):
    m=re.compile(r'@ (\d+) (\d+) (\d+)\n').match(T,i); assert m,'bad patch header in %s at %d'%(f,i)
    n=int(m.group(3)); t=T[m.end():m.end()+n]; assert T[m.end()+n]=='\n'; ops.append((int(m.group(1)),int(m.group(2)),t)); i=m.end()+n+1
ops.sort();r=[];p=0
for s,e,t in ops: assert s>=p; r.append(A[p:s]);r.append(t);p=e
r.append(A[p:]);B=''.join(r).encode()
want=open(here+'/v6patch.sha1').read().strip()
assert hashlib.sha1(B).hexdigest()==want,'patched page SHA-1 mismatch %s'%hashlib.sha1(B).hexdigest()
z=base64.b64encode(gzip.compress(B,9,mtime=0)).decode();n=6;k=-(-len(z)//n)
os.makedirs(dst+'/v6',exist_ok=True)
for i in range(n): open('%s/v6/%02d.b64'%(dst,i),'w').write(z[i*k:(i+1)*k])
print('v6 ok',len(ops),len(B),len(z))
