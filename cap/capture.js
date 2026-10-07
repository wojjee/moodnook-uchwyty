// Pre-renders the site's three.js product "photos" into static WebP files + nfstatic.js (key -> file map)
const {chromium}=require(process.env.PW||'playwright-core');const fs=require('fs'),crypto=require('crypto');
const URL=process.argv[2], OUT=process.argv[3];
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1440,height:900}});p.on('pageerror',e=>console.log('pageerror',e));
const settle=async ms=>{const t=Date.now();while(Date.now()-t<ms){const n=await p.evaluate(()=>[document.querySelectorAll('.nfp').length,document.querySelectorAll('.nfp-img.nfp-in').length]);if(n[1]>=n[0])return n;await p.waitForTimeout(400);}};
const got={};const grab=async()=>Object.assign(got,await p.evaluate(()=>{const o={};document.querySelectorAll('.nfp[data-k]>img.nfp-img').forEach(i=>{if(i.src.startsWith('blob:'))o[i.parentNode.getAttribute('data-k')]=i.src});document.querySelectorAll('[data-nf-scene]>img.nfs-img').forEach(i=>{if(i.src.startsWith('blob:'))o['scene:'+i.parentNode.getAttribute('data-nf-scene')]=i.src});return o;}));
const nav=async l=>{await p.locator('header nav button',{hasText:new RegExp('^'+l+'$')}).first().click();await p.waitForTimeout(700);};
await p.goto(URL+(URL.includes('?')?'&':'?')+'nfcap',{waitUntil:'networkidle'});await settle(90000);
fs.mkdirSync(OUT,{recursive:true});await p.setViewportSize({width:1200,height:630});await p.waitForTimeout(1500);await p.screenshot({path:OUT+'/og.jpg',type:'jpeg',quality:84});await p.setViewportSize({width:1440,height:900});await p.waitForTimeout(800);
await p.evaluate(()=>document.querySelector('.nf-insitu')&&document.querySelector('.nf-insitu').scrollIntoView());
await grab();let t=Date.now();while(Date.now()-t<90000&&await p.evaluate(()=>document.querySelectorAll('[data-nf-scene]').length>document.querySelectorAll('[data-nf-scene]>img.nfs-img').length))await p.waitForTimeout(500);await grab();
await nav('Kolekcje');await settle(180000);await grab();
const models=await p.evaluate(()=>(window.NF_CATALOG||{models:[]}).models.map(m=>m.name));console.log('models',models.join(','));
await nav('Produkt');await settle(180000);await grab();console.log('catalog cards',await p.evaluate(()=>document.querySelectorAll('.nfp[data-k]>img.nfp-img').length));/* catalogue grid cards (aspect 1.65) */
await nav('Konfigurator');await settle(60000);await grab();
const grp=lab=>p.evaluate(lab=>{const l=[...document.querySelectorAll('div')].find(d=>d.textContent.trim().toLowerCase()==lab&&d.nextElementSibling&&d.nextElementSibling.querySelector('button'));return l?[...l.nextElementSibling.querySelectorAll('button')].filter(b=>!b.disabled&&getComputedStyle(b).opacity>=0.6).map(b=>b.textContent.trim()):[]},lab);
const pick=(lab,t)=>p.evaluate(([lab,t])=>{const l=[...document.querySelectorAll('div')].find(d=>d.textContent.trim().toLowerCase()==lab&&d.nextElementSibling&&d.nextElementSibling.querySelector('button'));[...l.nextElementSibling.querySelectorAll('button')].find(b=>b.textContent.trim()==t).click();},[lab,t]);
for(const c of await grp('kolekcja')){await pick('kolekcja',c);await p.waitForTimeout(250);for(const k of await grp('kategoria')){await pick('kategoria',k);await p.waitForTimeout(250);for(const f of await grp('forma · wersja')){await pick('forma · wersja',f);await p.waitForTimeout(300);await settle(60000);await grab();}}}/* every configurator form */
console.log('after configurator',Object.keys(got).length);
for(const m of models){await nav('Produkt');const l=p.getByText(m,{exact:true}).first();if(await l.count()){await l.click();await p.waitForTimeout(500);await settle(60000);await grab();}}
const res=await p.evaluate(async(G)=>{const o={};for(const [k,u] of Object.entries(G)){if(!u||!u.startsWith('blob:'))continue;const im=new Image();im.src=u;await im.decode();const sc=k.startsWith('scene:')?1200:800;const r=Math.min(1,sc/Math.max(im.width,im.height));const c=document.createElement('canvas');c.width=Math.round(im.width*r);c.height=Math.round(im.height*r);c.getContext('2d').drawImage(im,0,0,c.width,c.height);o[k]=c.toDataURL('image/webp',0.8).split(',')[1];}return o;},got);
fs.mkdirSync(OUT,{recursive:true});const map={};let tot=0;
for(const [k,d] of Object.entries(res)){const f=crypto.createHash('sha1').update(k).digest('hex').slice(0,12)+'.webp';const buf=Buffer.from(d,'base64');fs.writeFileSync(OUT+'/'+f,buf);map[k]=f;tot+=buf.length;}
fs.writeFileSync(OUT+'/nfstatic.js',fs.readFileSync(__dirname+'/nfstatic.js','utf8').replace('/*MAP*/{}/*END*/','/*MAP*/'+JSON.stringify(map)+'/*END*/'));console.log('images',Object.keys(map).length,'bytes',tot);await b.close();})();
