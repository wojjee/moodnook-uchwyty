# Classic line v9 (Fine Line / RILL / GRID) for klasyczna.html.
# Usage: python3 build_classic.py SRC DST CAPDIR
#   SRC: dir with v6/*.b64 (deployed chunks); CAPDIR: dir with build_v8.py + v8patch/v9edits (SHA-verified v9b page)
#   writes DST/v8/00..05.b64 (gzip+base64 of the v9 page) and DST/classic_v9.sha1
import os, sys, json, gzip, base64, hashlib, subprocess, tempfile
src, dst, cap = sys.argv[1], sys.argv[2], sys.argv[3]
here = os.path.dirname(os.path.abspath(__file__))
tmp = tempfile.mkdtemp()
dump = os.path.join(tmp, 'v9b.html')
os.makedirs(tmp + '/v8', exist_ok=True)
subprocess.check_call([sys.executable, os.path.join(cap, 'build_v8.py'), src, tmp], env=dict(os.environ, NF_DUMP=dump))
P = open(dump, encoding='utf-8').read()
assert hashlib.sha1(P.encode()).hexdigest() == open(os.path.join(cap, 'v9.sha1')).read().strip()
D = json.load(open(os.path.join(here, 'classic_v9_delta.json'), encoding='utf-8'))

def sub_json(P, start, endmark, fn, **dumpkw):
    i = P.index(start) + len(start); j = P.index(endmark, i)
    obj = json.loads(P[i:j]); assert json.dumps(obj, ensure_ascii=False, **dumpkw) == P[i:j]
    obj = fn(obj)
    return P[:i] + json.dumps(obj, ensure_ascii=False, **dumpkw) + P[j:]

# (a) NF_CATALOG -> v9
CAB = ('DISC', 'DISCQ', 'DRUM', 'AXIS-D', 'DIAL-M', 'DIAL-E', 'STUD', 'STUD-E', 'GATE-D')  # spec v9: cabochon option (ST/AM) where the core sits in a rolled bezel
def cat(c):
    c['version'] = D['version']; c['source'] = D['source']
    out = []
    for m in c['models']:
        k = m['code']
        if k not in D['abr_excl']:
            for f in ('finishes', 'living'):
                if 'AB-R' not in m[f]:
                    m[f].insert(m[f].index('AB') + 1, 'AB-R')
        if k in D['intro_pl']: m['intro']['pl'] = D['intro_pl'][k]
        ins = (m.get('modules') or {}).get('insert')
        if ins and k in CAB:
            if 'AM' in ins and 'AC' not in ins: ins.append('AC')
            if 'ST' in ins and 'SC' not in ins: ins.append('SC')
        out.append(m)
        if k == 'ORB': out.append(D['orbf'])
    c['models'] = out
    assert len(out) == 31
    return c
P = sub_json(P, 'window.NF_CATALOG=', ';</script>', cat, separators=(',', ':'))

# (b) NF_SPEC -> AB-R in finishes rows, ORB-F entry
def spec(s):
    for k, rows in s.items():
        for r in rows:
            if r[0] == 'Wykończenia / Finishes' and k not in D['abr_excl'] and 'AB-R' not in r[1]:
                r[1] = r[1].replace('SB · PB · AB', 'SB · PB · AB · AB-R')
    n = {}
    for k, v in s.items():
        n[k] = v
        if k == 'ORB':
            rows = json.loads(json.dumps(v))
            for r in rows:
                if r[0].startswith('Masa'): r[1] = '≈ 38–242 g'
            rows.insert(1, ['Fasety / Facets', '8 · 12 · 16 (h 0,80 · 0,58 · 0,53 mm)'])
            n['ORB-F'] = rows
    return n
i = P.index('window.NF_SPEC=') + len('window.NF_SPEC='); j = P.index(';', P.index(']]}', i))
P = sub_json(P, 'window.NF_SPEC=', P[j:j+1] + P[j+1:j+2], spec) if False else P[:i] + json.dumps(spec(json.loads(P[i:j])), ensure_ascii=False) + P[j:]

# (c) renderer + UI literal edits [old, new, count]
HELP = r'''function nfBQ(s,le,z,ins,l){if(!ins||"NO"===ins)return;var o=le/2+.4,q=le/2-.25,Sh=new e.Shape;Sh.moveTo(-o,-o),Sh.lineTo(o,-o),Sh.lineTo(o,o),Sh.lineTo(-o,o),Sh.lineTo(-o,-o);var Hh=new e.Path;Hh.moveTo(-q,-q),Hh.lineTo(-q,q),Hh.lineTo(q,q),Hh.lineTo(q,-q),Hh.lineTo(-q,-q),Sh.holes.push(Hh);var G=new e.ExtrudeGeometry(Sh,{depth:.5,bevelEnabled:!0,bevelThickness:.1,bevelSize:.1,bevelSegments:1,curveSegments:1});G.translate(0,0,z-.1),s.add(S(G,nfBM(l)));if("AC"===ins||"SC"===ins){var ww=le-.5,P=new e.PlaneGeometry(ww,ww,40,40),A=P.attributes.position,h=.16*ww;for(var k=0;k<A.count;k++){var x=2*A.getX(k)/ww,yy=2*A.getY(k)/ww;A.setZ(k,h*(1-Math.pow(Math.abs(x),4))*(1-Math.pow(Math.abs(yy),4)))}P.computeVertexNormals(),P.translate(0,0,z+.1),s.add(S(P,y(ins)))}}function nfBM(l){return/^(MB|WH|NK)$/.test(l)?M(l):M("PB")}function nfBZ(s,r,z,ins,l,ax,tx,ty,tz){if(!ins||"NO"===ins)return;var G=g([[r-.25,z-.7],[r+.55,z-.7],[r+.55,z-.05],[r+.4,z+.5],[r-.05,z+.5],[r-.25,z+.3],[r-.25,z-.7]],128);ax&&G.rotateY(Math.PI/2),G.translate(tx||0,ty||0,tz||0),s.add(S(G,nfBM(l)));if("AC"===ins||"SC"===ins){for(var q=r-.2,h=.3*q,Q=[[0,z-.3],[q,z-.3],[q,z]],k=15;k>=0;k--){var a=k/16*Math.PI/2;Q.push([q*Math.sin(a),z+h*Math.cos(a)])}var C=g(Q,96);ax&&C.rotateY(Math.PI/2),C.translate(tx||0,ty||0,tz||0),s.add(S(C,y(ins)))}}function nfSP(s,r0,r1,T,z,l){if(!(T>0)||r1<=r0+.5)return;for(var P=[],N=Math.round(120*T),k=0;k<=N;k++){var a=k/N*T*2*Math.PI,rr=r0+(r1-r0)*k/N;P.push(new e.Vector3(rr*Math.cos(a),rr*Math.sin(a),z))}var G=new e.TubeGeometry(new e.CatmullRomCurve3(P),N,Math.min(.11,(r1-r0)/T*.24),6,!1),m=M(l);m.color.multiplyScalar(/^(MB|WH|NK)$/.test(l)?.8:.45),m.roughness=Math.min(1,m.roughness+.25),s.add(S(G,m))}function nfFL(R,n,dp,len,fd,ch){var tear=fd<0;fd=Math.max(.01,Math.min(Math.abs(fd),len/2)),ch=ch||0;var A=Math.max(96,Math.min(1440,12*n)),K=Math.max(24,Math.min(360,Math.ceil(len/.4))),V=[],I=[],i,j;function rad(z,t){var b=R-(ch>0?Math.max(0,ch-Math.min(z,len-z)):0),f=tear?Math.max(0,1-z/len):Math.max(0,Math.min(1,Math.min(z-ch,len-ch-z)/fd)),q=Math.sin(n*t/2);return b-dp*q*q*f}for(i=0;i<=K;i++){var z=len*i/K;for(j=0;j<=A;j++){var t=2*Math.PI*j/A,r=rad(z,t);V.push(r*Math.cos(t),r*Math.sin(t),z)}}for(i=0;i<K;i++)for(j=0;j<A;j++){var a=i*(A+1)+j,b=a+A+1;I.push(a,a+1,b,a+1,b+1,b)}[0,len].forEach((function(z,w){var c=V.length/3;V.push(0,0,z);for(j=0;j<=A;j++){var t=2*Math.PI*j/A,r=rad(z,t);V.push(r*Math.cos(t),r*Math.sin(t),z)}for(j=0;j<A;j++)w?I.push(c,c+1+j,c+2+j):I.push(c,c+2+j,c+1+j)}));var G=new e.BufferGeometry;return G.setAttribute("position",new e.Float32BufferAttribute(V,3)),G.setIndex(I),G.computeVertexNormals(),G}function nfFLX(R,n,dp,len,fd,ch){var G=nfFL(R,n,dp,len,fd,ch);return G.translate(0,0,-len/2),G.rotateY(Math.PI/2),G}function nfFAC(G,R,n){var P=G.attributes.position,L=R*Math.cos(Math.PI/n)+1e-4,v=new e.Vector3,on=new Uint8Array(P.count);for(var k=0;k<P.count;k++){v.fromBufferAttribute(P,k);for(var j=0;j<n;j++){var a=2*Math.PI*j/n,cx=Math.cos(a),cy=Math.sin(a),dd=v.x*cx+v.y*cy;dd>L&&(v.x-=(dd-L)*cx,v.y-=(dd-L)*cy,on[k]=1)}P.setXYZ(k,v.x,v.y,v.z)}P.needsUpdate=!0;var X=G.index.array,F=[],O=[];for(k=0;k<X.length;k+=3)(on[X[k]]&&on[X[k+1]]&&on[X[k+2]]?F:O).push(X[k],X[k+1],X[k+2]);G.computeVertexNormals();var G2=G.clone();return G.setIndex(O),G2.setIndex(F),G2}'''
E = [
 # helpers (module scope of the 3D renderer, before O())
 ['function O(n){var o=t[n.form]||null,i=o?o.texture:"smooth"', HELP + 'function O(n){var o=t[n.form]||null,i=o?o.texture:"smooth"', 1],
 # AB-R finish material (patinated, relief polished)
 ['AB:[8021832,.36,1,0,1],MB:[855051', 'AB:[8021832,.36,1,0,1],"AB-R":[9271888,.32,1,0,1],MB:[855051', 1],
 ['o.color.multiplyScalar(.78),o}', 'o.color.multiplyScalar(.78),"AB-R"===a&&(o.map=i,o.color.setHex(13414770).convertSRGBToLinear(),o.roughness=.3),o}', 1],
 ['return r.bumpMap=o,r.bumpScale=.06,r}function', 'return r.bumpMap=o,r.bumpScale=.06,"AB-R"===e&&(r.map=o,r.color.setHex(12687976).convertSRGBToLinear()),r}function', 1],
 # cabochon codes map to amber / stone materials
 ['function y(a){var t={AM:', 'function y(a){a={AC:"AM",SC:"ST"}[a]||a;var t={AM:', 1],
 # NF_DIM for ORB-F
 ['ORBQ:{d:[13,21,34]}', 'ORBQ:{d:[13,21,34]},"ORB-F":{d:[34,55,89]}', 1],
 # ORB-F case: ORB sphere, smooth, with n equator facets (PB on SB)
 ['break;case"ORBQ":j(Fe=(de=v(m.d))/.62', 'break;case"ORB-F":var nfF;H=(Fe=v(m.d))/2,X=.19*Fe+.44*Fe,j(Fe,ze=.19*Fe+1),q="FL"===w?Math.asin(.49):0,W=Math.PI-Math.acos(.88),($e=new e.SphereGeometry(H,192,128,0,2*Math.PI,q,W-q)).rotateX(Math.PI/2),nfF=nfFAC($e,H,[8,12,16][Math.min(f,2)]),$e.translate(0,0,X),nfF.translate(0,0,X),s.add(S($e,c)),s.add(S(nfF,"SB"===l?M("PB"):c)),"FL"===w&&(u=3,_=.49*H,$=X+H*Math.cos(q),s.add(S(g([[0,$-.3],[_,$-.3],[_,$],[_-.2,$+.15],[0,$+.15]],96),c)),u=2);break;case"ORBQ":j(Fe=(de=v(m.d))/.62', 1],
 # DISC: core 0.6D on the two larger sizes, filler face, rolled PB bezel, face spiral (8 / 15 turns, none on the smallest)
 ['te=H-J-.6,ne=ie+ee-.5', 'te=f>=1&&"RD"!==w&&"NO"!==n.insert?.3*Fe:H-J-.6,ne=ie+ee-.5', 1],
 ['s.add(S(oe,ae||M("PB"===l?"SB":l))),u=2;break;case"DISCQ"', 's.add(S(oe,ae||M("PB"===l?"SB":l))),"RD"!==w&&"NO"!==n.insert&&(te<H-J-1&&s.add(S(g([[te,ie+ee-.9],[H-J-.3,ie+ee-.9],[H-J-.3,ie+ee-.25],[te,ie+ee-.25]],160),c)),nfBZ(s,te,ie+ee-.25,n.insert||"BR",l),te<H-J-1&&nfSP(s,te+1.1,H-J-.9,[0,8,15][Math.min(f,2)],ie+ee-.24,l)),u=2;break;case"DISCQ"', 1],
 # DISCQ: square rolled bezel (+ cushion cabochon)
 ['ie+ee-("NO"===n.insert?.9:.88)),ae||M("PB"===l?"SB":l))),u=2;break;case"RAIL"', 'ie+ee-("NO"===n.insert?.9:.88)),ae||M("PB"===l?"SB":l))),"NO"!==n.insert&&nfBQ(s,le,ie+ee,n.insert||"BR",l),u=2;break;case"RAIL"', 1],
 # DRUM: fading flutes + bezel
 ['(fe=new e.ExtrudeGeometry(T(nfR,Math.round(Math.PI*Pe/2.44),.4),{depth:.6*nfH,bevelEnabled:!1,curveSegments:8})).translate(0,0,ze+.2*nfH)', '(fe=nfFL(nfR,Math.round(Math.PI*Pe/2.44),.4,.6*nfH,0===f?4:6,0)).translate(0,0,ze+.2*nfH)', 1],
 ['[te,ne+("BR"===n.insert?.25:.05)],[0,ne+("BR"===n.insert?.25:.05)]],96),ke)),u=2);break;', '[te,ne+("BR"===n.insert?.25:.05)],[0,ne+("BR"===n.insert?.25:.05)]],96),ke)),nfBZ(s,te,ne,n.insert,l),u=2);break;', 1],
 # RD endings: cabochon codes get a bezel + dome on the domed face
 ['[0,ze+Ie+.05*Fe]],96),"NO"!==n.insert?y(n.insert||"GL")||M("PB"===l?"SB":l):c)),u=2)', '[0,ze+Ie+.05*Fe]],96),"NO"!==n.insert?y(n.insert||"GL")||M("PB"===l?"SB":l):c)),/^(AC|SC)$/.test(n.insert)&&nfBZ(s,.3*Fe,ze+Ie+.03*Fe-.2,n.insert,l),u=2)', 1],
 ['s.add(S(re,ke||c)),u=2)', 's.add(S(re,ke||c)),/^(AC|SC)$/.test(n.insert)&&nfBZ(s,.3*Pe,ze+.44*Pe+.03*Pe-.2,n.insert,l),u=2)', 1],
 # STUD: bezel
 ['[te,ze+Ie+.05],[0,ze+Ie+.05]],96),y(n.insert||"GL")||M("PB"===l?"SB":l))),u=2)', '[te,ze+Ie+.05],[0,ze+Ie+.05]],96),y(n.insert||"GL")||M("PB"===l?"SB":l))),nfBZ(s,te,ze+Ie,n.insert||"GL",l),u=2)', 1],
 # DIAL band flutes: teardrop fade over the band height
 ['var f=new e.ExtrudeGeometry(T(l,Math.round(Math.PI*o/1.6),.4),{depth:.4*s,bevelEnabled:!1,curveSegments:8});return f.translate(0,0,i)', 'var f=nfFL(l,Math.round(Math.PI*o/1.6),.4,.4*s,-1,0);return f.translate(0,0,i)', 1],
 # bars (AXIS/VANE/door levers) flutes: 6 mm fade at the zone ends
 ['(f=E(T(m,Math.max(10,Math.round(1.6*s)),.07*s),i-o,Math.min(.5,h))).translate((o+i)/2,l,c)', '(f=nfFLX(m,Math.max(10,Math.round(1.6*s)),.07*s,i-o,6,Math.min(.5,h))).translate((o+i)/2,l,c)', 1],
 # STAVE
 ['var o=E(r?T(t/2,r,.07*t):T(t/2,0),a,"RD"===w?0:.8);', 'var o=r?nfFLX(t/2,r,.07*t,a,6,"RD"===w?0:.8):E(T(t/2,0),a,"RD"===w?0:.8);', 1],
 # DIAL: index mark only without a core
 ['var Ne=new e.BoxGeometry(.6,.2*Fe,.3);Ne.translate(0,.28*Fe,ze+Ie),u=2,s.add(S(Ne,new e.MeshBasicMaterial({color:1709068})));', 'var Ne=new e.BoxGeometry(.6,.2*Fe,.3);Ne.translate(0,.28*Fe,ze+Ie),u=2,n.insert&&"NO"!==n.insert||s.add(S(Ne,new e.MeshBasicMaterial({color:1709068})));', 1],
 # door lever end insert (GATE-D / AXIS-D): bezel around the X axis
 ['_e.translate(Ue+("BR"===n.insert?.3:0),0,Ke),s.add(S(_e,y(n.insert)||M("PB"===l?"SB":l))),u=2)', '_e.translate(Ue+("BR"===n.insert?.3:0),0,Ke),s.add(S(_e,y(n.insert)||M("PB"===l?"SB":l))),nfBZ(s,.32*Ze,0,n.insert,l,1,Ue-.1,0,Ke),u=2)', 2],
]
# DIAL / DIAL-E core: explicit face position, bezel + spiral
i = P.index('if(("DIAL"===d||"EDIAL"===d)&&n.insert&&"NO"!==n.insert){var Ma=null')
j = P.index('if(n.xp){', i)
P = P[:i] + 'if(("DIAL"===d||"EDIAL"===d)&&n.insert&&"NO"!==n.insert){var nfE="EDIAL"===d,nfZ=nfE?ra+3.3+13.6:ze+Ie+("RD"===w?.045*Fe:0),nfD=nfE?34:Fe,nfR=.3*nfD,nfG="BR"===n.insert?.3:.08;u=3,s.add(S(g([[0,nfZ-.9],[nfR,nfZ-.9],[nfR,nfZ+nfG],[0,nfZ+nfG]],96),y(n.insert)||M("PB"===l?"SB":l))),"RD"!==w?(nfBZ(s,nfR,nfZ,n.insert,l),nfSP(s,nfR+1.1,nfD/2-1.4,nfE?8:[0,8,15][Math.min(f,2)],nfZ+.01,l)):/^(AC|SC)$/.test(n.insert)&&nfBZ(s,nfR,nfZ,n.insert,l),u=2}' + P[j:]
UI = [
 # finish tables (3D photo + SVG + React)
 ['AB:{name:"Aged brass",t:{dp:"#110c08",dk:"#271d15",md:"#4a3a2a",lt:"#6b5640",hi:"#8c745a",wh:"#ad977c",rim:"#7f6a53"},sharp:!1,rough:.62,brush:.05,spun:.04,sw:"#6F5B45",patina:!0}',
  'AB:{name:"Aged brass",t:{dp:"#110c08",dk:"#271d15",md:"#4a3a2a",lt:"#6b5640",hi:"#8c745a",wh:"#ad977c",rim:"#7f6a53"},sharp:!1,rough:.62,brush:.05,spun:.04,sw:"#6F5B45",patina:!0},"AB-R":{name:"Aged brass, relief polished",t:{dp:"#16100a",dk:"#33271a",md:"#6a5436",lt:"#a08550",hi:"#cdb276",wh:"#eedcae",rim:"#b39a63"},sharp:!1,rough:.4,brush:.04,spun:.04,sw:"#8D7550",patina:!0}', 1],
 ['ST:{name:"Travertine",type:"stone",sw:"#E0DACB"}}', 'ST:{name:"Travertine",type:"stone",sw:"#E0DACB"},AC:{name:"Amber cabochon",type:"glow",sw:"#D7901F"},SC:{name:"Travertine cabochon",type:"stone",sw:"#E0DACB"}}', 1],
 ['window.NF_FORMS=i,window.NF_FIN=a,window.NF_INS=r', 'window.NF_FORMS=i,window.NF_FIN=a,window.NF_INS=r,i["ORB-F"]||(i["ORB-F"]=i.ORB)', 1],
 ['finishHex(e){return{SB:11045210,PB:13216106,AB:9205057,', 'finishHex(e){return{SB:11045210,PB:13216106,AB:9205057,"AB-R":10520912,', 1],
 ['insertHex(e){return{AM:', 'insertHex(e){return e={AC:"AM",SC:"ST"}[e]||e,{AM:', 1],
 ['metalSpec(e){return{SB:[13806955,.34,1,0],PB:[15319408,.1,1,.5],AB:[9268287,.46,1,0],', 'metalSpec(e){return{SB:[13806955,.34,1,0],PB:[15319408,.1,1,.5],AB:[9268287,.46,1,0],"AB-R":[10520912,.34,1,0],', 1],
 ['coreTex(e){', 'coreTex(e){e={AC:"AM",SC:"ST"}[e]||e;', 1],
 ['AB:{pl:"Aged · żywe",en:"Aged · living"},', 'AB:{pl:"Aged · żywe",en:"Aged · living"},"AB-R":{pl:"Aged relief · żywe",en:"Aged relief · living"},', 1],
 ['M=["SB","PB","AB","MB","WH","NK"].map(', 'M=["SB","PB","AB","AB-R","MB","WH","NK"].map(', 1],
 ['E=["SB","PB","AB"].includes(this.state.finish)', 'E=["SB","PB","AB","AB-R"].includes(this.state.finish)', 1],
 ['AB:{pl:"Postarzany · patynuje",en:"Aged · patinates"},', 'AB:{pl:"Postarzany · patynuje",en:"Aged · patinates"},"AB-R":{pl:"Postarzany, relief polerowany · patynuje",en:"Aged, relief polished · patinates"},', 1],
 ['x={SB:"Satin",PB:"Polished",AB:"Aged",', 'x={SB:"Satin",PB:"Polished",AB:"Aged","AB-R":"Aged relief",', 1],
 ['L=["SB","PB","AB"].map(A)', 'L=["SB","PB","AB","AB-R"].map(A)', 1],
 ['case"finish":return(u?u.finishes:["SB","PB","AB","MB","WH","NK"])', 'case"finish":return(u?u.finishes:["SB","PB","AB","AB-R","MB","WH","NK"])', 1],
 ['["ST","ST · "+i(r,"kamień","stone")]]', '["ST","ST · "+i(r,"kamień","stone")],["AC","AC · "+i(r,"kaboszon bursztyn","amber cabochon")],["SC","SC · "+i(r,"kaboszon trawertyn","travertine cabochon")]]', 1],
 ['knurl:e?"krata pierścieniowa":"ring-lattice"}[Z.texture]', 'knurl:e?"krata pierścieniowa":"ring-lattice",facets:e?"pas płaskich faset na równiku":"band of flat equator facets"}[Z.texture]', 1],
 # antibacterial / living-finish wording incl. AB-R (softened wording kept)
 ['(SB / PB / AB)', '(SB / PB / AB / AB-R)', 2],
 ['(SB, PB, AB)', '(SB, PB, AB, AB-R)', None],
 ['właściwości antybakteryjne*: SB · PB · AB"', 'właściwości antybakteryjne*: SB · PB · AB · AB-R"', 1],
 ['antibacterial properties*: SB · PB · AB"', 'antibacterial properties*: SB · PB · AB · AB-R"', 1],
]
for o, nw, c in E + UI:
    k = P.count(o)
    assert k >= 1 and (c is None or k == c), ('edit count', k, c, o[:80])
    P = P.replace(o, nw)
B = P.encode()
h = hashlib.sha1(B).hexdigest()
if os.environ.get('NF_DUMP'): open(os.environ['NF_DUMP'], 'wb').write(B)
os.makedirs(dst + '/v8', exist_ok=True)
z = base64.b64encode(gzip.compress(B, 9, mtime=0)).decode(); n = 6; k = -(-len(z) // n)
for i in range(n): open('%s/v8/%02d.b64' % (dst, i), 'w').write(z[i*k:(i+1)*k])
open(dst + '/classic_v9.sha1', 'w').write(h + '\n')
print('classic v9 page', len(B), 'bytes sha1', h)
