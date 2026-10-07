// NOOK FORM v5 — configurator combination test (headless Chrome). Usage: node test_config.js URL [uiSamples]
const {chromium}=require(process.env.PW||'playwright-core');
const URL=process.argv[2], NS=+(process.argv[3]||160);
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:1000}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto(URL,{waitUntil:'networkidle'});await p.waitForFunction(()=>window.NFCfg&&window.NFPhoto);
/* ---------- A. logic + geometry over ALL raw combinations ---------- */
const A=await p.evaluate(()=>{const C=NFCfg,K=C.KEYS,opts={};K.forEach(k=>opts[k]=C.options(k,true).map(o=>o[0]));
 const R={raw:0,valid:0,invalid:0,reasons:{},effective:0,skuDup:0,skuBad:0,sumBad:0,normBad:0,neighbor:{checked:0,fail:[]},naInvariance:{checked:0,fail:[]},previews:0,geomDistinct:0,geomCollide:[],buildErr:[],grpBad:0};
 const eff=new Map(), skus=new Map();
 const effKey=c=>K.filter(k=>!C.na(c,k,true)).map(k=>k+'='+c[k]).join('|');
 const geomCache=new Map();
 const ghash=S=>{const k=JSON.stringify(S);if(geomCache.has(k))return geomCache.get(k);let h;try{const G=NFPhoto.build(Object.assign({},S));G.updateMatrixWorld(true);const parts=[];
   G.traverse(o=>{if(!o.isMesh)return;const a=o.geometry.attributes.position.array,e=o.matrixWorld.elements;let s=0,t=0;for(let i=0;i<a.length;i+=3){const x=a[i]*e[0]+a[i+1]*e[4]+a[i+2]*e[8]+e[12],y=a[i]*e[1]+a[i+1]*e[5]+a[i+2]*e[9]+e[13],z=a[i]*e[2]+a[i+1]*e[6]+a[i+2]*e[10]+e[14];s+=x*1.3+y*1.7+z*2.9;t+=Math.abs(z)+x*x+y*y*1.1;}
   const m=o.material;parts.push(a.length+':'+s.toFixed(2)+':'+t.toFixed(2)+':'+(m.color?m.color.getHexString():'')+':'+(m.roughness||0).toFixed(3)+':'+(m.transmission||0)+':'+(m.opacity||1));});h=parts.join(';');}catch(e){R.buildErr.push(k+' '+e.message);h='ERR'}geomCache.set(k,h);return h;};
 const cart=(i,c)=>{if(i===K.length){test(Object.assign({},c));return;}for(const o of opts[K[i]]){c[K[i]]=o;cart(i+1,c);}};
 const test=c=>{R.raw++;const v=C.valid(c);
   // a raw combo is "invalid" only if an APPLICABLE key holds a disabled option; n/a keys are ignored (shown greyed out with reason)
   if(v){R.invalid++;const why=C.bad(c,v,c[v],true)||v;R.reasons[why]=(R.reasons[why]||0)+1;return;}
   R.valid++;const ek=effKey(c);if(eff.has(ek))return;eff.set(ek,1);R.effective++;
   const n=C.normalize(c);if(K.some(k=>!C.na(c,k,true)&&n[k]!==c[k]))R.normBad++;
   const s=C.sku(c);if(skus.has(s)&&skus.get(s)!==ek)R.skuDup++;skus.set(s,ek);
   const f=C.FORMS[c.form],seg=s.split('-');
   const exp=['NF',c.form,f.type==='knob'?c.size:c.mount+({A:96,B:128,C:160,D:224,E:320})[c.mount],f.insert?c.insert:'00',c.finish,C.na(c,'stem',true)?'00':c.stem,c.washer,f.ends?c.ending:'00',c.assembly,c.pack];
   if(seg.join()!==exp.join())R.skuBad++;
   const sm=C.summary(c,true).map(r=>r.v).join('|');const need=[c.form==='FRAME'?'FRAME':c.form.replace(/Q$/,' Q'),c.finish,c.assembly,c.pack,c.washer,'wycena'].concat(f.insert?[c.insert]:[]).concat(C.na(c,'stem',true)?[]:[c.stem.slice(0,2)]);
   if(need.some(x=>sm.indexOf(x)<0)||(C.mixed(c)!==(sm.indexOf('mieszane')>=0)))R.sumBad++;
   const g=C.groups(c,true);if(g.some(gr=>gr.options.some(o=>o.disabled&&!o.reason))||g.some(gr=>!gr.note&&gr.options.filter(o=>o.active).length!==1))R.grpBad++;
   // geometry: every applicable GEOM key change (to an enabled option) must change the built 3-D model, both assembled and exploded
   for(const xp of [false,true]){const S0=C.preview(c,xp),h0=ghash(S0);
    for(const k of C.GEOM){for(const o of opts[k]){if(o===c[k])continue;const c2=Object.assign({},c,{[k]:o});
      if(C.na(c,k,true)){R.naInvariance.checked++;if(C.sku(c2)!==s||JSON.stringify(C.preview(c2,xp))!==JSON.stringify(S0))R.naInvariance.fail.push(ek+' '+k+'>'+o);continue;}
      if(C.bad(c,k,o,true))continue; if(k==='form')continue; // form change = different product, checked via distinct count
      R.neighbor.checked++;if(ghash(C.preview(c2,xp))===h0)R.neighbor.fail.push(ek+(xp?' xp':'')+' '+k+'>'+o);}}}
 };
 cart(0,{});
 const hs=new Map();for(const [k,h] of geomCache){if(hs.has(h)&&R.geomCollide.length<10)R.geomCollide.push(k+' == '+hs.get(h));hs.set(h,k);}
 R.previews=geomCache.size;R.geomDistinct=hs.size;R.skuCount=skus.size;R.neighbor.fail=R.neighbor.fail.slice(0,20);R.naInvariance.fail=R.naInvariance.fail.slice(0,20);
 return R;});
console.log('A',JSON.stringify(A,null,1));
/* ---------- B. UI click-through: real buttons, real render ---------- */
await p.locator('header nav button',{hasText:/^Konfigurator$/}).first().click();await p.waitForTimeout(1500);
const img=async()=>{const t=Date.now();let last='';while(Date.now()-t<20000){const s=await p.evaluate(()=>{const i=document.querySelector('.nf-cfg-preview img.nfp-img');return i&&i.complete&&i.naturalWidth?i.src.length+':'+i.src.slice(-80):''});if(s&&s===last)return s;last=s;await p.waitForTimeout(350);}return last;};
const U={clicks:0,renders:0,changed:0,same:[],disabledClicks:0,disabledOk:0,noTitle:0,skuMismatch:0,errBefore:errs.length};
const click=async(k,c)=>{const bt=p.locator(`[data-cfg-key="${k}"][data-cfg-code="${c}"]`).first();const dis=await bt.getAttribute('aria-disabled')==='true';const before=await p.locator('.nf-sku').first().innerText();
 if(dis){U.disabledClicks++;if(!(await bt.getAttribute('title')))U.noTitle++;await bt.click({force:true});await p.waitForTimeout(150);if(await p.locator('.nf-sku').first().innerText()===before)U.disabledOk++;return false;}
 await bt.click();U.clicks++;return true;};
// deterministic plan: for each form, cycle every option of every key; then random mixes
const plan=[];const keys=['form','size','insert','stem','ending','washer','finish','mount','assembly','pack'];
const opts=await p.evaluate(()=>{const o={};NFCfg.KEYS.forEach(k=>o[k]=NFCfg.options(k,true).map(x=>x[0]));return o;});
for(const f of opts.form){plan.push(['form',f]);for(const k of ['size','insert','stem','ending','washer','finish','mount'])for(const c of opts[k])plan.push([k,c]);}
let seed=7;const rnd=n=>{seed=(seed*16807)%2147483647;return seed%n;};
for(let i=0;i<NS;i++){const k=keys[rnd(keys.length)];plan.push([k,opts[k][rnd(opts[k].length)]]);}
let prevImg=await img(),prevSku=await p.locator('.nf-sku').first().innerText();
for(const [k,c] of plan){const ok=await click(k,c);if(!ok)continue;const sku=await p.locator('.nf-sku').first().innerText();
 const geomChange=sku!==prevSku&&!['assembly','pack'].includes(k);const im=await img();U.renders++;
 if(geomChange){if(im!==prevImg)U.changed++;else U.same.push(prevSku+' -> '+sku);}
 // UI SKU must equal NFCfg.sku of the pressed buttons
 const st=await p.evaluate(()=>{const o={};document.querySelectorAll('[data-cfg-key]').forEach(e=>{if(e.getAttribute('aria-pressed')==='true')o[e.dataset.cfgKey]=e.dataset.cfgCode});return o;});
 if(Object.keys(st).length&&(await p.evaluate(s=>NFCfg.sku(s),st))!==sku)U.skuMismatch++;
 prevImg=im;prevSku=sku;}
// exploded toggle
const ex=p.locator('button',{hasText:/^(Moduły|Modules)$/i}).first();let exOK=false;if(await ex.count()){const a=await img();await ex.click();await p.waitForTimeout(400);const bimg=await img();exOK=a!==bimg;}
U.explodeChanges=exOK;U.errors=errs.slice(0,10);U.errCount=errs.length;U.same=U.same.slice(0,10);
console.log('B',JSON.stringify(U,null,1));await b.close();
const bad=A.skuDup+A.skuBad+A.sumBad+A.normBad+A.grpBad+A.neighbor.fail.length+A.naInvariance.fail.length+A.buildErr.length+U.same.length+U.skuMismatch+U.noTitle+(U.disabledClicks-U.disabledOk)+U.errCount+(U.explodeChanges?0:1)+(A.geomDistinct===A.previews?0:1);
console.log(bad?'CONFIG TEST FAILED':'CONFIG TEST PASSED',bad);process.exit(bad?1:0);})();
