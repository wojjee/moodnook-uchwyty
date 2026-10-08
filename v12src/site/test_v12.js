// v12 site tests (browser): node test_v12.js BASE_URL
//  exhaustive configurator walk: every chip combination resolves to an allowed combo (subset of test_results via data.js),
//  allowed choices are kept, cross-direction mixes assemble in the live 3D viewer; every product page image loads.
const {chromium}=require(process.env.PW||'playwright-core');const BASE=process.argv[2];
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--use-gl=swiftshader','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1280,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(BASE+'#/konfigurator',{waitUntil:'networkidle'});await p.waitForFunction(()=>window.NF12app&&window.NF12,null,{timeout:60000});
const R=await p.evaluate(()=>{const A=NF12app,N=NF12,f=[],C={pull:new Set(N.combos.pull),knob:new Set(N.combos.knob),door:new Set(N.combos.door),window:new Set(N.combos.window)};let n=0,kept=0;
 const chk=(kind,o,want)=>{n++;let core=o.core;if(kind==='door')core=core.replace(/\/[A-Z]{2}-E\w+$/,'');if(!C[kind].has(core))f.push(kind+' not allowed '+o.sku);
  for(const [k,v,list] of want){if(list&&list.indexOf(v)>=0){if(A.CF()[k]!==v)f.push(kind+' dropped allowed '+k+'='+v+' '+o.sku);else kept++;}}};
 const FINS=['SB','PB','AB','SB.PB','AB.PB','MB','WH','NK'];
 for(const bk of ['OT','PN','OB','OS-DB','OS-JS','KS'])for(const cc of [96,128,160,224,320])for(const post of ['OTD','SR7','SR8','SQ7','SK8'])for(const washer of ['W0','WR12','WR13','WD14','WS11','WT17'])for(const cst of ['R','F',null]){
  A.setFromSku(N.products.find(x=>x.id==='OB-pull-128').sku);const cf=A.CF();Object.assign(cf,{kind:'pull',bk,cc,post,washer,cst,fin:FINS[n%FINS.length]});let o;try{o=A.resolve()}catch(e){f.push('pull throw '+bk+cc+post+washer+e.message);continue}
  chk('pull',o,[['post',post,o.posts]]);}
 for(const hd of ['OT','PN','OB','OS','KS'])for(const size of ['S','M','L'])for(const stem of ['OTD-12','SR8-12','SR7-K21','SR8-K16','SK8-K18.5','SQ7-K24'])for(const washer of ['W0','WR12','WR13','WD14','WS11','WT17']){
  A.setFromSku(N.products.find(x=>x.id==='KS-knob').sku);Object.assign(A.CF(),{kind:'knob',hd,size,stem,washer});let o;try{o=A.resolve()}catch(e){f.push('knob throw '+hd+size+stem+e.message);continue}chk('knob',o,[['stem',stem,o.stems]]);}
 const D=['OT','PN','OB','OS','KS'];for(const lv of D)for(const rs of D){for(const esc of ['PZ','BB','WCi','WCo','none']){A.setFromSku('OS-L/KS-R/SB');Object.assign(A.CF(),{kind:'door',lv,rs,esc});chk('door',A.resolve(),[]);}
  A.setFromSku('PN-O/PN-RO/SB');Object.assign(A.CF(),{kind:'window',lv,rs});chk('window',A.resolve(),[]);}
 return {n,kept,f:f.slice(0,20),nf:f.length};});
// cross-direction mixes in the live viewer
const mixes=['KS-S128/PN-SQ7-30/WS11/SB'.replace('PN-SQ7-30','SQ7-30'),'OS-L/KS-R/KS-EPZ/SB','PN-O/OB-RO/AB'];const V=[];
for(const sku of mixes.concat((await p.evaluate(()=>NF12.mix.map(m=>m.sku))).slice(0,3))){const before=await p.evaluate(()=>window.__nf3dReady||0);
 await p.goto(BASE+'#/konfigurator/'+encodeURIComponent(sku));await p.waitForTimeout(300);
 const ok=await p.waitForFunction(b=>(window.__nf3dReady||0)>b,before,{timeout:60000}).then(()=>true,()=>false);
 const shown=await p.evaluate(()=>(document.getElementById('csku')||{}).textContent||'');V.push({sku,ok,shown:shown.slice(0,80)});}
// product pages: all images load
const ids=await p.evaluate(()=>NF12.products.map(x=>x.id));const P=[];
for(const id of ids){await p.goto(BASE+'#/produkt/'+id);await p.waitForTimeout(150);
 const r=await p.evaluate(async()=>{const im=[...document.querySelectorAll('main img, #app img, img')].filter(i=>/v12\/img\//.test(i.src));for(const i of im){i.loading='eager';if(!i.complete)await new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,8000)});}
  return {n:im.length,bad:im.filter(i=>!i.naturalWidth).map(i=>i.src.split('/').pop())};});if(!r.n||r.bad.length)P.push(id+' '+JSON.stringify(r));}
const fails=[].concat(R.f,V.filter(v=>!v.ok).map(v=>'viewer '+v.sku),P,errs.map(e=>'pageerror '+e));
console.log(JSON.stringify({walk:{states:R.n,keptChecks:R.kept,fails:R.nf},viewer:V,products:ids.length,productFails:P},null,1));
console.log(fails.length?'V12 BROWSER TEST FAILED '+fails.length+'\n'+fails.join('\n'):'V12 BROWSER TEST PASSED ('+R.n+' configurator states, '+V.length+' live 3D mixes, '+ids.length+' product pages)');
await b.close();process.exit(fails.length?1:0);})();
