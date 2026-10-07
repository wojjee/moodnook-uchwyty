// Fails (exit 1) if any product photo slot (.nfp / scene) is missing, broken or blank (pixel-variance check) on:
// home, collections, catalogue (every collection filter, PL + EN), all product pages, configurator (every form).
// Also checks that all catalogue models are covered in each place. --static: every photo must be a pre-rendered WebP
// (no in-browser fallback). --shots=PREFIX saves PREFIX-catalog-<filter>.png per collection filter.
const {chromium}=require(process.env.PW||'playwright-core');
const URL=process.argv[2]||'http://localhost:8774/';const STATIC=process.argv.includes('--static');
const SHOTS=(process.argv.find(a=>a.startsWith('--shots='))||'').slice(8);const WAIT=STATIC?20000:150000;
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||'/usr/bin/google-chrome',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1440,height:900}});const fails=[],perr=[];
p.on('pageerror',e=>perr.push(e.message));p.on('console',m=>{if(m.type()==='error')perr.push(m.text())});
const nav=async l=>{await p.locator('header nav button',{hasText:new RegExp('^('+l+')$')}).first().click();await p.waitForTimeout(500);};
const check=async(view)=>{const t0=Date.now();let r;
 while(true){r=await p.evaluate(async()=>{const out=[];const slots=[...document.querySelectorAll('.nfp[data-k]')].map(e=>({e,k:e.getAttribute('data-k')})).concat([...document.querySelectorAll('[data-nf-scene]')].map(e=>({e,k:'scene:'+e.getAttribute('data-nf-scene')})));
  for(const {e,k} of slots){const im=e.querySelector('img');const o={k,form:(k.match(/form:([^,}]+)/)||[])[1]||null,vis:!!e.offsetParent};
   if(!im){o.err='no image';out.push(o);continue;}o.src=im.src;
   if(!im.complete){o.err='loading';out.push(o);continue;}if(!im.naturalWidth){o.err='broken image';out.push(o);continue;}
   /* blank check: composite on white, 96x96; background = median colour of the border; the product must cover >=0.5% of the
      pixels with a colour distance >24 from it (catches empty/transparent renders and an empty panel/backdrop) */
   const S=96,c=document.createElement('canvas');c.width=c.height=S;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,S,S);g.drawImage(im,0,0,S,S);
   const d=g.getImageData(0,0,S,S).data,B=[[],[],[]];for(let y=0;y<S;y++)for(let x=0;x<S;x++)if(x<2||y<2||x>=S-2||y>=S-2){const i=(y*S+x)*4;B[0].push(d[i]);B[1].push(d[i+1]);B[2].push(d[i+2]);}
   const bg=B.map(a=>a.sort((u,v)=>u-v)[a.length>>1]);let fg=0,s=0,s2=0;const n=S*S;
   for(let i=0;i<d.length;i+=4){const l=.3*d[i]+.59*d[i+1]+.11*d[i+2];s+=l;s2+=l*l;if(Math.hypot(d[i]-bg[0],d[i+1]-bg[1],d[i+2]-bg[2])>24)fg++;}
   o.var=Math.round(s2/n-(s/n)**2);o.fg=fg/n;if(o.fg<0.005)o.err='blank image (fg '+o.fg.toFixed(4)+', var '+o.var+')';out.push(o);}return out;});
  const pend=r.filter(o=>o.err==='no image'||o.err==='loading');if(!pend.length||Date.now()-t0>WAIT)break;await p.waitForTimeout(500);}
 for(const o of r){if(o.err)fails.push(view+' | '+o.k+' | '+o.err);else if(STATIC&&!/\/v8\/p\/[0-9a-f]{12}\.webp$/.test(o.src))fails.push(view+' | '+o.k+' | not pre-rendered ('+o.src.slice(0,30)+')');}
 return r.filter(o=>!o.err).map(o=>o.form);};
await p.goto(URL,{waitUntil:'networkidle'});await p.waitForTimeout(2000);
const models=await p.evaluate(()=>NF_CATALOG.models.map(m=>({code:m.code,name:m.name,coll:m.coll})));
const cover={catalog:new Set(),collections:new Set(),product:new Set(),configurator:new Set()};
await p.evaluate(()=>scrollTo(0,0));(await check('home'));
await nav('Kolekcje');(await check('collections')).forEach(f=>cover.collections.add(f));
for(const L of ['PL','EN']){
 await p.locator('header button',{hasText:new RegExp('^'+L+'$')}).first().click();await p.waitForTimeout(600);
 await nav(L=='PL'?'Produkt':'Product');
 const filters=await p.evaluate(()=>{const lab=[...document.querySelectorAll('div')].find(d=>/^(kolekcja|collection)$/i.test(d.textContent.trim())&&d.nextElementSibling&&d.nextElementSibling.querySelector('button'));return lab?[...lab.nextElementSibling.querySelectorAll('button')].map(b=>b.textContent.trim()):[]});
 if(filters.length<5)fails.push('catalog '+L+' | collection filter buttons not found: '+JSON.stringify(filters));
 for(const f of filters){await p.locator('button',{hasText:f}).filter({hasText:new RegExp('^'+f.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'$')}).first().click();await p.waitForTimeout(600);
  const got=await check('catalog '+L+' ['+f+']');if(L=='PL')got.forEach(x=>cover.catalog.add(x));
  const cards=await p.evaluate(()=>document.querySelectorAll('.nfp[data-k]').length);if(!cards)fails.push('catalog '+L+' ['+f+'] | no cards');
  console.log('catalog',L,f,'cards',cards);
  if(SHOTS&&L=='PL'){await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(400);await p.screenshot({path:SHOTS+'-catalog-'+f.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'.png',fullPage:true});}}
 if(filters.length)await p.locator('button',{hasText:filters[0]}).first().click();
}
await p.locator('header button',{hasText:/^PL$/}).first().click();await p.waitForTimeout(600);
for(const m of models){await nav('Produkt');await p.getByText(m.name,{exact:true}).first().click();await p.waitForTimeout(400);
 const got=await check('product '+m.name);if(got.includes(m.code))cover.product.add(m.code);else fails.push('product '+m.name+' | no valid photo of '+m.code);}
await nav('Konfigurator');
const grp=async lab=>p.evaluate(lab=>{const l=[...document.querySelectorAll('div')].find(d=>d.textContent.trim().toLowerCase()==lab&&d.nextElementSibling&&d.nextElementSibling.querySelector('button'));return l?[...l.nextElementSibling.querySelectorAll('button')].map(b=>({t:b.textContent.trim(),dis:b.disabled||getComputedStyle(b).opacity<0.6})):[]},lab);
const pick=async(lab,t)=>p.evaluate(([lab,t])=>{const l=[...document.querySelectorAll('div')].find(d=>d.textContent.trim().toLowerCase()==lab&&d.nextElementSibling&&d.nextElementSibling.querySelector('button'));const bt=[...l.nextElementSibling.querySelectorAll('button')].find(b=>b.textContent.trim()==t);bt.click();},[lab,t]);
for(const c of await grp('kolekcja')){await pick('kolekcja',c.t);await p.waitForTimeout(300);
 for(const k of await grp('kategoria')){if(k.dis)continue;await pick('kategoria',k.t);await p.waitForTimeout(300);
  for(const f of await grp('forma · wersja')){if(f.dis)continue;await pick('forma · wersja',f.t);await p.waitForTimeout(400);
   const got=await check('configurator '+c.t+' / '+k.t+' / '+f.t);got.forEach(x=>cover.configurator.add(x));}}}
for(const [w,s] of Object.entries(cover)){const miss=models.filter(m=>!s.has(m.code)).map(m=>m.name);if(miss.length)fails.push(w+' | models without a valid photo: '+miss.join(', '));console.log(w,'covered',models.length-miss.length+'/'+models.length);}
perr.forEach(e=>fails.push('page error | '+e));
console.log(fails.length?'THUMB TEST FAILED '+fails.length+'\n'+fails.join('\n'):'THUMB TEST PASSED ('+models.length+' models'+(STATIC?', all pre-rendered':'')+')');
await b.close();process.exit(fails.length?1:0);})();
