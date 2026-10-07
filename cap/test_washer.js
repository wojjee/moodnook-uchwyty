// Washer geometry + visual test: every form × size/CTC × washer RP/SP/NP × assembled/exploded, through NFCfg.preview → NFPhoto.build/shot
const {chromium}=require(process.env.PW||'playwright-core');
const URL=process.argv[2], OUT=process.argv[3]||'';
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--use-gl=swiftshader','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1200,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(URL,{waitUntil:'networkidle'});await p.waitForFunction(()=>window.NFPhoto&&window.NFCfg,null,{timeout:60000});
const r=await p.evaluate(()=>{const T=THREE,F=NFCfg.FORMS,fails=[],stat={cases:0,visual:0};
 const box=(G,q)=>{const bb=new T.Box3();let n=0;G.updateMatrixWorld(true);G.traverse(o=>{if(o.isMesh&&(o.userData.p||0)===q){bb.expandByObject(o);n++;}});return n?bb:null;};
 const px=(S)=>{const cv=NFPhoto.shot(S,160,160);const c=document.createElement('canvas');c.width=c.height=160;const x=c.getContext('2d');x.drawImage(cv,0,0);return x.getImageData(0,0,160,160).data;};
 for(const f of Object.keys(F)){const knob=F[f].type==='knob';const vals=knob?NFCfg.options('size',true).map(o=>o[0]):NFCfg.options('mount',true).map(o=>o[0]);
  for(const v of vals){const pix={};
   for(const w of ['RP','SP','NP']){let c=NFCfg.select(NFCfg.select(Object.assign({},NFCfg.DEF),'form',f),knob?'size':'mount',v);c=NFCfg.select(c,'washer',w);
    if(NFCfg.na(c,'washer',true)){continue;} if(c.washer!==w){fails.push([f,v,w,'select did not apply washer']);continue;}
    for(const xp of [false,true]){stat.cases++;const S=NFCfg.preview(c,xp),G=NFPhoto.build(S),wb=box(G,0),sb=box(G,1)||box(G,2);/* ARC/FRAME legs are part of the body */
     if(!xp&&v===vals[Math.floor(vals.length/2)]) pix[w]=px(S);const id=[f,v,w,xp?'xp':'asm'].join('/');
     if(w==='NP'){ if(wb) fails.push([id,'NP still has a washer']); continue; }
     if(!wb){fails.push([id,'washer missing']);continue;} if(!sb){fails.push([id,'stem missing']);continue;}
     const ws=wb.getSize(new T.Vector3()), ss=sb.getSize(new T.Vector3());
     if(ws.z<.8||ws.z>4) fails.push([id,'washer thickness '+ws.z.toFixed(2)]);
     if(!xp&&Math.abs(wb.min.z)>.05) fails.push([id,'washer not on surface z='+wb.min.z.toFixed(2)]);
     if(!xp&&Math.abs(sb.min.z-wb.max.z)>.06) fails.push([id,'stem not seated on washer gap='+(sb.min.z-wb.max.z).toFixed(2)]);
     if(xp&&!(wb.min.z>.2&&wb.max.z<sb.min.z)) fails.push([id,'exploded order surface→washer→stem broken']);
     const perStem=knob?1:2; if(ws.x/perStem<ss.x/perStem*1.15&&knob) fails.push([id,'washer not wider than stem']);
     if(knob&&(Math.abs((wb.min.x+wb.max.x)/2)>.05||Math.abs((wb.min.y+wb.max.y)/2)>.05)) fails.push([id,'washer off-axis']);
     if(w==='SP'&&knob&&Math.abs(ws.x-ws.y)>.05) fails.push([id,'square washer not square']);
     G.traverse(o=>{if(o.geometry)o.geometry.dispose();});}}
   if(pix.RP&&pix.NP){ const d=(a,b2)=>{let n=0;for(let i=0;i<a.length;i+=4){if(Math.abs(a[i]-b2[i])+Math.abs(a[i+1]-b2[i+1])+Math.abs(a[i+2]-b2[i+2])>24)n++;}return n/(a.length/4);};
     const dr=d(pix.RP,pix.NP), ds=pix.SP?d(pix.SP,pix.NP):1, drs=pix.SP?d(pix.RP,pix.SP):1; stat.visual++;
     if(dr<.002) fails.push([f,v,'RP washer not visible in preview (diff '+(dr*100).toFixed(2)+'%)']);
     if(ds<.002) fails.push([f,v,'SP washer not visible in preview (diff '+(ds*100).toFixed(2)+'%)']);
     if(drs<.0008) fails.push([f,v,'RP and SP look identical (diff '+(drs*100).toFixed(3)+'%)']); }}}
 return {stat,fails};});
console.log(JSON.stringify(r.stat),'fails',r.fails.length);r.fails.slice(0,40).forEach(x=>console.log(' ',x.join(' | ')));console.log('errs',errs.length,errs.slice(0,3));
await b.close();if(r.fails.length||errs.length){console.log('WASHER TEST FAILED');process.exit(1);}console.log('WASHER TEST PASSED');})();
