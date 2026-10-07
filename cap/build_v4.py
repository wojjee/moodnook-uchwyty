# Rebuilds the v4 page from the deployed v3 chunks + v4patch.json (text-only deploy path), verifies SHA-1, writes v4/00..05.b64
import sys,glob,base64,gzip,json,hashlib,os
src,dst=sys.argv[1],sys.argv[2]; here=os.path.dirname(os.path.abspath(__file__))
A=gzip.decompress(base64.b64decode(''.join(open(f).read() for f in sorted(glob.glob(src+'/v3/*.b64'))).replace('\n','').replace(' ',''))).decode()
P=json.load(open(here+'/v4patch.json'));r=[];p=0
for s,e in P['ranges']: r.append(A[p:s]);r.append(P['text']);p=e
r.append(A[p:]);B=''.join(r).encode()
assert hashlib.sha1(B).hexdigest()==P['sha1'],'patched page SHA-1 mismatch'
z=base64.b64encode(gzip.compress(B,9,mtime=0)).decode();n=6;k=-(-len(z)//n)
os.makedirs(dst+'/v4',exist_ok=True)
for i in range(n): open('%s/v4/%02d.b64'%(dst,i),'w').write(z[i*k:(i+1)*k])
print('v4 ok',len(B),len(z))
