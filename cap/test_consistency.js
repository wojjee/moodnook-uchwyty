// single-source consistency test (blocks deploy): every catalogue model must match across collections, catalogue, product page, configurator, renders and spec tables. Usage: node test_consistency.js URL
const {chromium}=require(process.env.PW||'playwright-core');
const URL=process.argv[2];
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||'/usr/bin/google-chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:1000}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(URL,{waitUntil:'networkidle'});await p.waitForFunction(()=>window.NFCfg&&window.NFPhoto&&window.NF_CATALOG);
const F=[];const fail=(area,code,msg)=>F.push(area+' · '+code+' · '+msg);
const C=await p.evaluate(()=>NF_CATALOG.models);const codes=C.map(m=>m.code);
/* 1. logic layer: configurator, spec tables, renders */
const L=await p.evaluate(()=>{const out=[];const C=NF_CATALOG.models,G=NFCfg;
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 if(!eq(G.ORDER,C.map(m=>m.code))) out.push(['config','*','form list ≠ catalogue']);
 const sk=Object.keys(window.NF_SPEC||{}).sort(), ck=C.map(m=>m.code).sort(); if(!eq(sk,ck)) out.push(['spec-table','*','NF_SPEC keys ≠ catalogue: '+sk.filter(x=>ck.indexOf(x)<0).concat(ck.filter(x=>sk.indexOf(x)<0)).join(',')]);
 C.forEach(m=>{const c=G.normalize({form:m.code}),F=G.FORMS[m.code];
  if(!F||F.name!==m.name) out.push(['config',m.code,'name']);
  if(c.coll!==m.coll||c.cat!==m.cat) out.push(['config',m.code,'collection/category']);
  const op=k=>G.options(k,true,c).map(o=>o[0]);
  if(m.sizes&&!eq(op('size'),m.sizes.map(s=>s[0]))) out.push(['config',m.code,'sizes']);
  if(m.ctc&&!eq(op('mount'),m.ctc)) out.push(['config',m.code,'CTC']);
  if(!!m.sizes===!!G.na(c,'size',true)) out.push(['config',m.code,'size applicability']);
  if(!eq(op('finish'),m.finishes)) out.push(['config',m.code,'finishes']);
  const en=k=>G.options(k,true,c).filter(o=>!G.bad(c,k,o[0],true)).map(o=>o[0]);
  if(!!m.modules.stem===!!G.na(c,'stem',true)) out.push(['config',m.code,'stem module']);
  if(!!m.modules.insert===!!G.na(c,'insert',true)) out.push(['config',m.code,'insert module']);
  if(m.modules.stems&&!eq(en('stem').sort(),m.modules.stems.slice().sort())) out.push(['config',m.code,'stem options']);
  if(m.modules.washer&&!eq(en('washer').sort(),m.modules.washer.slice().sort())) out.push(['config',m.code,'washer options']);
  if(m.modules.ends&&!eq(en('ending').sort(),m.modules.ends.slice().sort())) out.push(['config',m.code,'ending options']);
  if(m.eu){['rose','esc','spindle','plate'].forEach(k=>{if(m.eu[k]&&!eq(en(k).sort(),m.eu[k].slice().sort())) out.push(['config',m.code,k+' options']);});}
  if(G.sku(c).split('-')[1]!==m.code.replace(/-/g,'')) out.push(['config',m.code,'SKU code']);
  if(G.summary(c,true).map(r=>r.v).join('|').indexOf(m.name)<0) out.push(['config',m.code,'summary name']);
  try{const S=G.preview(c,false);if(S.form!==m.code) out.push(['render',m.code,'preview form']);const g=NFPhoto.build(S);let n=0;g.traverse(o=>{if(o.isMesh)n++;});if(n<1) out.push(['render',m.code,'empty model']);
   const x=NFPhoto.build(G.preview(c,true));if(!x) out.push(['render',m.code,'exploded']);}catch(e){out.push(['render',m.code,'build error '+e.message]);}
 });return out;});
L.forEach(x=>fail(...x));
/* 2. UI layer */
const nav=async l=>{await p.locator('header nav button',{hasText:new RegExp('^('+l+')$')}).first().click();await p.waitForTimeout(600);};
const texts=async sel=>p.evaluate(s=>[...document.querySelectorAll(s)].map(e=>e.textContent.trim()),sel);
// collections page: every card title per section
await nav('Kolekcje');
const coll=await p.evaluate(()=>{const sec=[...document.querySelectorAll('section h2')].filter(h=>/^(Fine Line|RILL|GRID|System)$/.test(h.textContent.trim()));
 return sec.map(h=>{let box=h.closest('div[style*="margin-top:72px"],div[style*="margin-top:28px"]')||h.parentNode.parentNode;return {c:h.textContent.trim(),names:[...box.querySelectorAll('div[style*="Cormorant"]')].map(d=>d.textContent.trim()).filter(t=>t&&t!==h.textContent.trim())};});});
const CN={'01':'Fine Line','02':'RILL','03':'GRID','00':'System'};
for(const k of ['01','02','03','00']){const want=C.filter(m=>m.coll===k).map(m=>m.name).sort();const got=((coll.find(x=>x.c===CN[k])||{}).names||[]).sort();
 if(JSON.stringify(want)!==JSON.stringify(got)) fail('collections',CN[k],'cards '+JSON.stringify(got)+' ≠ '+JSON.stringify(want));}
// catalogue page
await nav('Produkt|Produkty|Katalog');
const cat=await p.evaluate(()=>[...document.querySelectorAll('div')].filter(d=>d.getAttribute('style')&&/Cormorant/.test(d.getAttribute('style'))&&d.nextElementSibling&&/IBM Plex Mono/.test(d.parentNode.innerHTML)).map(d=>d.textContent.trim()));
const catSet=new Set(cat);C.forEach(m=>{if(!catSet.has(m.name)) fail('catalogue',m.code,'card missing');});
// product page for each model (via app state, same path as a card click)
for(const m of C){await p.evaluate(code=>{const el=[...document.querySelectorAll('div')].find(d=>d.textContent.trim()===NF_CATALOG.models.find(x=>x.code===code).name&&d.closest('[style*="cursor"]'));el.closest('[style*="cursor"]').click();},m.code).catch(()=>fail('catalogue',m.code,'card not clickable'));
 await p.waitForTimeout(350);
 const r=await p.evaluate(m=>{const h=[...document.querySelectorAll('h1')].map(x=>x.textContent.trim());const hero=document.querySelector('.nf-prod-hero .nfp[data-k]');const st=hero&&NFPhoto.state(hero.getAttribute('data-k'));
  const body=document.body.innerText;const sp=(NF_SPEC[m.code]||[])[0];return {h, heroForm:st&&st.form, spec:!sp||body.indexOf(sp[1])>=0, coll:body.indexOf({'01':'01 Fine Line','02':'02 RILL','03':'03 GRID','00':'System'}[m.coll])>=0};},m);
 if(r.h.indexOf(m.name)<0) fail('product',m.code,'heading '+r.h.join('|'));
 if(r.heroForm!==m.code) fail('product',m.code,'hero render form '+r.heroForm);
 if(!r.spec) fail('product',m.code,'spec table'); if(!r.coll) fail('product',m.code,'collection label');
 await nav('Produkt|Produkty|Katalog');}
// configurator UI: reach every model through collection → category → form buttons
await nav('Konfigurator');
for(const m of C){const clk=async(k,v)=>{const bt=p.locator(`[data-cfg-key="${k}"][data-cfg-code="${v}"]`).first();if(!(await bt.count())){fail('config-ui',m.code,'no button '+k+'='+v);return;}if(await bt.getAttribute('aria-pressed')!=='true'){await bt.click();await p.waitForTimeout(120);}};
 await clk('coll',m.coll);await clk('cat',m.cat);await clk('form',m.code);
 const r=await p.evaluate(()=>{const s=(document.querySelector('.nf-sku')||{}).textContent||'';const pv=document.querySelector('.nf-cfg-preview .nfp[data-k]');const st=pv&&NFPhoto.state(pv.getAttribute('data-k'));
  const sz=[...document.querySelectorAll('[data-cfg-key="size"]')].filter(e=>e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.cfgCode);return {s,form:st&&st.form,sz};});
 if(r.s.split('-')[1]!==m.code.replace(/-/g,'')) fail('config-ui',m.code,'SKU '+r.s);
 if(r.form!==m.code) fail('config-ui',m.code,'preview form '+r.form);
 if(m.sizes&&JSON.stringify(r.sz)!==JSON.stringify(m.sizes.map(s=>s[0]))) fail('config-ui',m.code,'size buttons '+r.sz);}
const formBtns=await p.evaluate(()=>NFCfg.ORDER.length);if(formBtns!==C.length) fail('config-ui','*','form count');
if(errs.length) fail('page','*','errors: '+errs.slice(0,3).join(' | '));
console.log(JSON.stringify({models:C.length,collections:{fl:C.filter(m=>m.coll==='01').length,rill:C.filter(m=>m.coll==='02').length,grid:C.filter(m=>m.coll==='03').length},categories:[...new Set(C.map(m=>m.cat))],checks:'collections · catalogue · product (heading, hero render, spec table, collection) · configurator logic + UI (name, coll/cat, sizes, CTC, modules, finishes, EU options, SKU, summary) · renders (assembled + exploded)',failures:F},null,1));
await b.close();console.log(F.length?'CONSISTENCY TEST FAILED '+F.length:'CONSISTENCY TEST PASSED');process.exit(F.length?1:0);})();
