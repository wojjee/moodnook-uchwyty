/* NOOK FORM site v12 — modular system v11 (main line). Vanilla JS, hash routes, three r128 live configurator. */
(function(){
'use strict';
var N=window.NF12, LS=window.localStorage, L='pl';
try{L=LS.getItem('nf12-lang')||(/^en/i.test(navigator.language)?'pl':'pl');}catch(e){}
function T(pl,en){return L==='en'?en:pl;}
function E(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return [].slice.call((r||document).querySelectorAll(s));}
var MAIL='trade@nookform.studio'; /* PLACEHOLDER address used across the site — owner to confirm */
var DIRS=['OT','PN','OB','OS','KS'];
var NAME={OT:'OTOCZAK',PN:'PION',OB:'OBRĄCZKA',OS:'OSIKA',KS:'KASKADA'};
var SUB={OT:['organiczny otoczak','organic pebble'],PN:['architektoniczny pion','architectural fin'],OB:['biżuteryjna obrączka','jewellery ring'],OS:['mosiądz i drewno','brass and timber'],KS:['minimalne art déco','minimal Art Deco']};
var DESC={
OT:['Organiczny, wygładzony przez wodę kształt. Chwyt-otoczak to jeden odlew z kroplowymi czopami; nóżki wymienia się w najwęższym miejscu – w talii Ø7,2, 19 mm pod chwytem – więc złącze jest niewidoczne, a system pozostaje modułowy.','An organic, water-smoothed form. The pebble grip is one casting with drop-shaped stubs; the posts are swapped at the narrowest point – the Ø7.2 waist 19 mm below the grip – so the joint stays invisible and the system stays modular.'],
PN:['Architektoniczny, pionowy przekrój jak płetwa. Czyste płaszczyzny, mikrofazy 0,25–0,35 mm i kwadratowe słupki z kołkiem ustalającym – wszystko w osi pionu.','Architectural: an upright, fin-like section. Clean planes, 0.25–0.35 mm micro-chamfers and square posts with a locating pin – everything on the vertical axis.'],
OB:['Biżuteria mebla: matowy pręt i cienkie, polerowane obrączki. Obrączka jest jednocześnie złączem – ma płaską bazę i przelot M4, dzięki czemu pręt staje się modułowy, a obrączki można przenieść na inne kierunki.','Jewellery for furniture: a matte rod and slim polished rings. The ring is the joint itself – a flat land with an M4 passage – so the rod becomes modular and the rings can move to other directions.'],
OS:['Skandynawskie ciepło: mosiężny rdzeń w tulei z dębu lub jesionu, satynowe tulejki w miejscu nóżek. Drewno jest dzielone na segmenty dokładnie pod tulejkami, więc nigdzie nie widać czoła drewna.','Scandinavian warmth: a brass core in an oak or ash sleeve, with satin ferrules where the posts meet. The timber is split exactly under the ferrules, so no end grain is ever visible.'],
KS:['Minimalne art déco: schodki w przekroju, w nóżkach, w rozetach i w gałce. Ten sam rytm stopni powtarza się w każdym elemencie rodziny.','Minimal Art Deco: steps in the section, the posts, the roses and the knob. The same rhythm of tiers repeats in every piece of the family.']};
var SPEC={
OT:[['superelipsa 14,6 × 8,5 mm (224/320: 16 × 9,4)','superellipse 14.6 × 8.5 mm (224/320: 16 × 9.4)'],['OTD-12 (kropla Ø8,4 → Ø7,2) + WD14','OTD-12 (drop Ø8.4 → Ø7.2) + WD14'],['owalna głowica S/M/L na trzonie OTD-12','oval head S/M/L on the OTD-12 stem'],['ramię-otoczak 18 × 11, rozeta kopułkowa Ø52','pebble arm 18 × 11, domed rose Ø52'],['ramię 110 mm, rozeta 29 × 72','110 mm arm, 29 × 72 rose']],
PN:[['FIN 7 × 12 mm (320: 8 × 14)','FIN 7 × 12 mm (320: 8 × 14)'],['SQ7-30 + WS11, kołek ustalający Ø1','SQ7-30 + WS11, Ø1 locating pin'],['T-bar 26/32/40 mm na SQ7-K24','T-bar 26/32/40 mm on SQ7-K24'],['FIN 8 × 16, szyjka □18, rozeta □50','FIN 8 × 16, □18 neck, □50 rose'],['FIN, rozeta 29 × 72, faza 0,6','FIN, 29 × 72 rose, 0.6 chamfer']],
OB:[['pręt Ø8 mm (320: Ø10), mat, kopułkowe końce','Ø8 mm rod (320: Ø10), matte, domed ends'],['SR7-30 (224/320: SR8-30) + WR12 + obrączka CR','SR7-30 (224/320: SR8-30) + WR12 + CR ring'],['tarcza Ø24/28/34 z polerowanym bezelem','Ø24/28/34 disc with a polished bezel'],['pręt Ø16 + pierścień PB, rozeta Ø52 z obrzeżem PB','Ø16 rod + PB ring, Ø52 rose with PB rim'],['rozeta z polerowanym pierścieniem','rose with a polished inlay ring']],
OS:[['rdzeń Ø8 + dąb/jesion Ø12 (224: 13, 320: 10 + 15)','Ø8 core + oak/ash Ø12 (224: 13, 320: 10 + 15)'],['SR8-30 + WR13 + tulejka CF','SR8-30 + WR13 + CF ferrule'],['dębowa kopułka Ø25/30/35 na mosiężnej bazie','oak dome Ø25/30/35 on a brass base'],['rdzeń Ø12 + dąb Ø20, rozeta z dębowym pierścieniem','Ø12 core + Ø20 oak, rose with an oak ring'],['rozeta 29 × 72, faza 0,3','29 × 72 rose, 0.3 chamfer']],
KS:[['dwa stopnie 11 × 3,5 + 6,6 × 3,5 (320: wzmocniony S320L)','two tiers 11 × 3.5 + 6.6 × 3.5 (320: reinforced S320L)'],['SK8-30 ze schodkową stopą, bez podkładki','SK8-30 with an integral stepped foot, no washer'],['trzy stopnie D / 0,84D / 0,68D','three tiers D / 0.84D / 0.68D'],['dwa stopnie 14 + 9, rozeta Ø52/44/36','two tiers 14 + 9, Ø52/44/36 rose'],['rozeta trzystopniowa','three-tier rose']]};
var FIN={SB:['satynowy','satin','#C8A56C'],PB:['polerowany','polished','#DDBB76'],AB:['postarzany','aged','#8E6C40'],MB:['czarny mat (powłoka)','matte black (coated)','#2A2826'],WH:['ciepła biel (powłoka)','warm white (coated)','#EEE8DC'],NK:['nikiel szczotkowany (powłoka)','brushed nickel (plated)','#B9B7B1']};
var FINS=['SB','PB','AB','SB.PB','AB.PB','MB','WH','NK'];
var MIXTXT={MIX1:['KASKADA na słupkach PION','KASKADA on PION posts'],MIX2:['Obrączki PB na dębowej OSICE','PB rings on oak OSIKA'],MIX3:['PION na schodkowych słupkach KASKADY','PION on stepped KASKADA posts'],MIX4:['OBRĄCZKA na słupkach KASKADY','OBRĄCZKA on KASKADA posts'],MIX5:['OTOCZAK na słupkach SR8 z podkładką PB','OTOCZAK on SR8 posts with a PB washer'],MIX6:['OSIKA jesion na słupkach KASKADY','Ash OSIKA on KASKADA posts'],MIX7:['PION na okrągłych słupkach z podkładką schodkową','PION on round posts with a stepped washer'],MIX8:['Gałka KASKADA na trzonie OBRĄCZKI','KASKADA knob on an OBRĄCZKA stem'],MIX9:['Gałka OBRĄCZKA na trzonie KASKADY','OBRĄCZKA knob on a KASKADA stem']};
var PRODS={};N.products.forEach(function(p){PRODS[p.id]=p;});
var IMGS={};(N.images||[]).forEach(function(i){IMGS[i]=1;});
function fmt(x,d){return (+x).toFixed(d==null?1:d).replace(/\.0+$/,'').replace('.',L==='en'?'.':',');}
function img(name,cls,alt,eager){return '<div class="ph '+(cls||'r43')+'"><img src="v12/img/'+name+'-1200.webp" srcset="v12/img/'+name+'-640.webp 640w, v12/img/'+name+'-1200.webp 1200w" sizes="(max-width:860px) 100vw, 50vw" alt="'+E(alt||'')+'" '+(eager?'':'loading="lazy" ')+'decoding="async" data-img="'+name+'"></div>';}
function kindName(p){var n=NAME[p.dir];
 if(p.kind==='pull')return T('Uchwyt ','Pull ')+n+(p.species==='JS'?T(' jesion',' ash'):(p.dir==='OS'?T(' dąb',' oak'):''))+' '+p.cc;
 if(p.kind==='knob')return T('Gałka ','Knob ')+n;
 if(p.kind==='door')return T('Klamka drzwiowa ','Door lever ')+n;
 return T('Klamka okienna ','Window handle ')+n;}
function pcard(p){return '<a class="card" href="#/produkt/'+p.id+'">'+img(p.img[0],'r43',kindName(p))+'<div class="tx"><h3>'+E(kindName(p))+'</h3><div class="sku">'+E(p.sku)+'</div></div></a>';}
/* ---------------- inquiry list ---------------- */
function inq(){try{return JSON.parse(LS.getItem('nf12-inq')||'[]');}catch(e){return [];}}
function inqSave(a){try{LS.setItem('nf12-inq',JSON.stringify(a));}catch(e){} badge();}
function inqAdd(sku,name){var a=inq(),f=a.filter(function(x){return x.sku===sku;})[0]; if(f)f.qty++; else a.push({sku:sku,name:name,qty:1}); inqSave(a); toast(T('Dodano do zapytania: ','Added to your inquiry: ')+sku);}
function badge(){var n=inq().reduce(function(s,x){return s+x.qty;},0); $$('.cnt').forEach(function(b){b.textContent=n; b.style.display=n?'':'none';});}
var tt;function toast(m){var t=$('.toast'); t.textContent=m; t.classList.add('on'); clearTimeout(tt); tt=setTimeout(function(){t.classList.remove('on');},2600);}
/* ---------------- layout ---------------- */
function header(){return '<header class="hd"><div class="wrap"><a class="logo" href="#/">NOOK FORM<small>MOOD NOOK · '+T('SYSTEM MODUŁOWY','MODULAR SYSTEM')+'</small></a>'+
 '<button class="burger" aria-label="Menu"><i></i><i></i><i></i></button><nav class="nav">'+
 '<a href="#/kolekcje" data-r="kolekcj">'+T('Kolekcje','Collections')+'</a><a href="#/konfigurator" data-r="konfigurator">'+T('Konfigurator','Configurator')+'</a>'+
 '<a href="#/mix" data-r="mix">Mix &amp; match</a><a href="#/system" data-r="system">System</a><a href="klasyczna.html">'+T('Kolekcja klasyczna','Classic collection')+'</a>'+
 '<a href="#/zapytanie" data-r="zapytanie">'+T('Zapytanie','Inquiry')+'<span class="cnt"></span></a><button class="lang" type="button">'+(L==='en'?'PL':'EN')+'</button></nav></div></header>';}
function footer(){return '<footer class="ft"><div class="wrap"><div class="cols"><div><div class="logo" style="margin-bottom:14px">NOOK FORM</div><p>'+T('Uchwyty, gałki i klamki z litego, bezołowiowego mosiądzu CW724R. Jeden system złączy M4 dla pięciu kierunków formy.','Pulls, knobs and levers in solid, lead-free CW724R brass. One M4 joint system for five form directions.')+'</p><p class="note">[PLACEHOLDER — '+T('nazwa firmy, adres, NIP','company name, address, VAT ID')+']</p></div>'+
 '<div><h4>'+T('System v11','System v11')+'</h4>'+DIRS.map(function(d){return '<a href="#/kolekcja/'+d+'">'+NAME[d]+'</a>';}).join('')+'<a href="#/konfigurator">'+T('Konfigurator','Configurator')+'</a><a href="#/mix">Mix &amp; match</a><a href="#/system">'+T('Jak to działa','How it works')+'</a><a href="'+N.pdf+'" download>'+T('Katalog PDF','PDF catalogue')+'</a></div>'+
 '<div><h4>'+T('Kolekcja klasyczna','Classic collection')+'</h4><a href="klasyczna.html">Fine Line · RILL · GRID</a><a href="klasyczna.html#probki">'+T('Próbki','Samples')+'</a><a href="klasyczna.html#montaz">'+T('Montaż i szablon','Installation')+'</a><a href="klasyczna.html#pielegnacja">'+T('Pielęgnacja','Care')+'</a><a href="klasyczna.html#faq">FAQ</a></div>'+
 '<div><h4>'+T('Informacje','Information')+'</h4><a href="#/zapytanie">'+T('Zapytanie ofertowe','Quote request')+'</a><a href="klasyczna.html#dostawa">'+T('Dostawa','Shipping')+'</a><a href="klasyczna.html#zwroty">'+T('Zwroty','Returns')+'</a><a href="klasyczna.html#gwarancja">'+T('Gwarancja','Warranty')+'</a><a href="klasyczna.html#rodo">'+T('Prywatność (RODO)','Privacy (GDPR)')+'</a><a href="klasyczna.html#kontakt">'+T('Kontakt','Contact')+'</a></div></div>'+
 '<div class="legal">© Mood Nook · NOOK FORM. '+T('Wizualizacje generowane z modeli CAD; ceny na zapytanie.','Images rendered from the CAD models; prices on request.')+'</div></div></footer><div class="toast" role="status"></div>';}
/* ---------------- pages ---------------- */
function countAll(){var c=N.counts;return c.pull.total+c.knob.total+c.door.total+c.window.total+c.esc.total;}
function pHome(){
 var c=N.counts;
 return '<section class="wrap hero"><div><div class="k">NOOK FORM · '+T('system modułowy','modular system')+'</div><h1>'+T('Jeden system.<br>Pięć języków formy.','One system.<br>Five languages of form.')+'</h1>'+
 '<p class="lead">'+T('Uchwyty, gałki i klamki z litego, bezołowiowego mosiądzu CW724R. Każdy moduł łączy się z każdym tym samym złączem M4 – chwyt jednego kierunku stanie na słupkach drugiego.','Pulls, knobs and levers in solid, lead-free CW724R brass. Every module meets every other through the same M4 joint – a grip from one direction stands on the posts of another.')+'</p>'+
 '<div class="ctas"><a class="btn" href="#/konfigurator">'+T('Złóż swój uchwyt','Build your handle')+'</a><a class="btn o" href="#/kolekcje">'+T('Zobacz kolekcje','See the collections')+'</a></div>'+
 '<div class="facts"><div><b>5</b><span>'+T('kierunków formy','form directions')+'</span></div><div><b>'+countAll()+'</b><span>'+T('sprawdzonych kombinacji','verified combinations')+'</span></div><div><b>M4</b><span>'+T('jedno złącze','one joint')+'</span></div></div></div>'+
 img('family_OB','r43',NAME.OB,true)+'</section>'+
 '<section class="sec alt" id="kolekcje"><div class="wrap"><div class="hdr"><div><div class="k">'+T('Kolekcje','Collections')+'</div><h2>'+T('Pięć kierunków, wspólne moduły','Five directions, shared modules')+'</h2></div><p class="mut">'+T('Każdy kierunek to rodzina: uchwyty w pięciu rozstawach, gałki S/M/L, klamka drzwiowa z rozetą i szyldami oraz klamka okienna.','Each direction is a family: pulls in five spacings, S/M/L knobs, a door lever with rose and escutcheons, and a window handle.')+'</p></div>'+
 '<div class="g5">'+DIRS.map(function(d){return '<a class="card coll" href="#/kolekcja/'+d+'">'+img('family_'+d,'r1',NAME[d])+'<div class="tx"><h3>'+NAME[d]+'</h3><div class="sub">'+T(SUB[d][0],SUB[d][1])+'</div></div></a>';}).join('')+'</div></div></section>'+
 '<section class="sec"><div class="wrap"><div class="hdr"><div><div class="k">Mix &amp; match</div><h2>'+T('Moduły bez granic kierunków','Modules across directions')+'</h2></div><a class="lnk" href="#/mix">'+T('Wszystkie zestawienia','All combinations')+'</a></div>'+
 '<div class="g3">'+N.mix.slice(0,3).map(mixCard).join('')+'</div></div></section>'+
 '<section class="sec alt"><div class="wrap g2"><div>'+img('exploded_OB-R128_annotated','r43',T('Rozstrzelony widok modułów','Exploded view of the modules'))+'</div><div><div class="k">'+T('Jak to działa','How it works')+'</div><h2>'+T('Jedno złącze w każdym miejscu','One joint everywhere')+'</h2>'+
 '<p>'+T('Chwyt, obrączka, słupek i podkładka łączą się zawsze tak samo: gwint wewnętrzny M4, trzpień ISO 4026 i czop Ø5,0 podkładki w kieszeni stopy. Dlatego każdy moduł jest też częścią zamienną – wygląd można zmienić po latach.','Grip, ring, post and washer always meet the same way: a female M4 thread, an ISO 4026 stud and the Ø5.0 washer spigot in the foot counterbore. That makes every module a spare part too – the look can change years later.')+'</p>'+
 '<p class="mut">'+T('Test systemu: ','System test: ')+c.pull.total+T(' uchwytów, ',' pulls, ')+c.knob.total+T(' gałek, ',' knobs, ')+c.door.total+T(' klamek × rozet, ',' lever × rose sets, ')+c.window.total+T(' klamek okiennych – wszystkie złożone i sprawdzone geometrycznie.',' window sets – all assembled and checked geometrically.')+'</p>'+
 '<a class="lnk" href="#/system">'+T('Szczegóły systemu','System details')+'</a></div></div></section>'+
 '<section class="sec"><div class="wrap"><div class="classic"><div class="ph" style="min-height:280px"><img src="v8/p/og.jpg" alt="Fine Line · RILL · GRID" loading="lazy" style="height:100%;object-fit:cover"></div><div class="tx"><div class="k">'+T('Kolekcja klasyczna','Classic collection')+'</div><h2>Fine Line · RILL · GRID</h2><p>'+T('Gałki i uchwyty z toczonego mosiądzu: gładkie linie, delikatne żłobienia i siatka pierścieni – z wkładkami z kamienia i bursztynu w polerowanej oprawie.','Turned brass knobs and pulls: smooth lines, fine flutes and a ring lattice – with stone and amber inserts in a polished bezel.')+'</p><a class="btn o" href="klasyczna.html">'+T('Przejdź do kolekcji','Open the collection')+'</a></div></div></div></section>';}
function mixCard(m){var k=m.id.split('_')[0],t=MIXTXT[k]||['',''];return '<div class="card mixt">'+img(m.id,'r43',T(t[0],t[1]))+'<div class="tx"><h3>'+E(T(t[0],t[1]))+'</h3><div class="sku">'+E(m.sku)+'</div><div style="margin-top:12px"><a class="lnk" href="#/konfigurator/'+encodeURIComponent(m.sku)+'">'+T('Otwórz w konfiguratorze','Open in the configurator')+'</a></div></div></div>';}
function pCollections(){return '<section class="wrap" style="padding:48px 0 80px"><div class="k">'+T('Kolekcje','Collections')+'</div><h1>'+T('System v11','System v11')+'</h1><p class="mut" style="max-width:40em">'+T('Pięć kierunków formy w jednym systemie modułów M4. Wybierz rodzinę albo złóż własne zestawienie w konfiguratorze.','Five form directions in one M4 module system. Pick a family, or build your own mix in the configurator.')+'</p>'+
 '<div class="g3" style="margin-top:36px">'+DIRS.map(function(d){return '<a class="card coll" href="#/kolekcja/'+d+'">'+img('family_'+d,'r43',NAME[d])+'<div class="tx"><h3>'+NAME[d]+'</h3><div class="sub">'+T(SUB[d][0],SUB[d][1])+'</div></div></a>';}).join('')+
 '<a class="card coll" href="klasyczna.html"><div class="ph r43"><img src="v8/p/og.jpg" alt="" loading="lazy" style="height:100%;object-fit:cover"></div><div class="tx"><h3>'+T('KLASYCZNA','CLASSIC')+'</h3><div class="sub">Fine Line · RILL · GRID</div></div></a></div></section>';}
function pCollection(d){
 if(!NAME[d])return pHome();
 var ps=N.products.filter(function(p){return p.dir===d;}),sp=SPEC[d];
 var rows=[[T('Przekrój chwytu','Grip section'),sp[0]],[T('Słupki','Posts'),sp[1]],[T('Gałka','Knob'),sp[2]],[T('Klamka drzwiowa','Door lever'),sp[3]],[T('Klamka okienna','Window handle'),sp[4]],[T('Materiał','Material'),[T('mosiądz bezołowiowy CW724R','lead-free brass CW724R'),'']]];
 function grp(t,f){var a=ps.filter(f);return a.length?'<div class="grp"><h3>'+t+'</h3><div class="g4">'+a.map(pcard).join('')+'</div></div>':'';}
 return '<section class="wrap chero"><div><div class="crumb"><a href="#/kolekcje">'+T('Kolekcje','Collections')+'</a> / '+NAME[d]+'</div><div class="k" style="margin-top:22px">'+T(SUB[d][0],SUB[d][1])+' · '+d+'</div><h1>'+NAME[d]+'</h1><p>'+T(DESC[d][0],DESC[d][1])+'</p>'+
 '<table class="tbl">'+rows.map(function(r){return '<tr><th>'+r[0]+'</th><td>'+E(typeof r[1]==='string'?r[1]:T(r[1][0],r[1][1]||r[1][0]))+'</td></tr>';}).join('')+'</table>'+
 '<div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn s" href="#/konfigurator/'+encodeURIComponent(PRODS[d+'-pull-128'].sku)+'">'+T('Konfiguruj','Configure')+'</a><a class="btn o s" href="#/mix">Mix &amp; match</a></div>'+
 '<div class="dirnav" style="margin-top:26px">'+DIRS.map(function(x){return '<a class="'+(x===d?'on':'')+'" href="#/kolekcja/'+x+'">'+NAME[x]+'</a>';}).join('')+'</div></div>'+img('family_'+d,'r43',NAME[d],true)+'</section>'+
 '<section class="wrap" style="padding-bottom:80px">'+grp(T('Uchwyty meblowe','Cabinet pulls'),function(p){return p.kind==='pull'&&!p.species;})+(d==='OS'?grp(T('Uchwyty – jesion','Pulls – ash'),function(p){return p.species==='JS';}):'')+
 grp(T('Gałki, klamki drzwiowe i okienne','Knobs, door levers and window handles'),function(p){return p.kind!=='pull';})+'</section>';}
var VLAB={front:['przód','front'],detail:['detal','detail'],top:['góra','top'],SML:['S · M · L','S · M · L'],BB:['szyld BB','BB escutcheon'],'WC-in':['szyld WC','WC escutcheon'],PZ:['szyld PZ','PZ escutcheon'],M:['M','M']};
function vlab(n,i){if(i===0)return T('widok główny','main view');var k=n.split('-').slice(-1)[0];if(/WC-in$/.test(n))k='WC-in';var v=VLAB[k];return v?T(v[0],v[1]):n;}
function pProduct(id){
 var p=PRODS[id]; if(!p)return pHome();
 var m=p.meta||{},rows=[];
 if(p.kind==='pull'){var fl=N.flex[m.bar]||{};rows=[[T('Rozstaw otworów','Hole spacing'),p.cc+' mm'],[T('Długość','Length'),fmt(p.bbox[0])+' mm'],[T('Wysokość od frontu','Projection'),fmt(p.bbox[2])+' mm'],[T('Masa kompletu','Set weight'),fmt(p.mass_g,0)+' g'],[T('Chwyt','Grip'),m.bar],[T('Słupki','Posts'),m.post+' × 2'],[T('Podkładki','Washers'),(m.washer==='W0'?T('brak (stopa zintegrowana)','none (integral foot)'):m.washer+' × 2')]];
  if(m.collar)rows.push([T('Obrączki / tulejki','Rings / ferrules'),m.collar+' × 2']); if(fl.delta!=null)rows.push([T('Ugięcie przy 100 N','Deflection at 100 N'),fmt(fl.delta,3)+' mm']);}
 else if(p.kind==='knob'){rows=[['S / M / L',['S','M','L'].map(function(s){var b=p.sizes[s].bbox;return s+' '+fmt(b[0])+'×'+fmt(b[1]);}).join(' · ')+' mm'],[T('Wysokość (M)','Height (M)'),fmt(p.bbox[2])+' mm'],[T('Masa (M)','Weight (M)'),fmt(p.mass_g,0)+' g'],[T('Trzon','Stem'),m.stem],[T('Podkładka','Washer'),m.washer]];}
 else if(p.kind==='door'){rows=[[T('Ramię','Arm'),'132 mm'],[T('Trzpień','Spindle'),'□8 mm'],[T('Szyld','Escutcheon'),T('PZ 72 mm · BB 72 mm · WC 78 mm','PZ 72 mm · BB 72 mm · WC 78 mm')],[T('Masa klamki / rozety','Lever / rose weight'),fmt(p.lever,0)+' g / '+fmt(p.rose,0)+' g'],[T('Norma docelowa','Target standard'),'EN 1906 ('+T('wymaga badań','testing pending')+')']];}
 else{rows=[[T('Ramię','Arm'),'110 mm'],[T('Trzpień','Spindle'),'□7 × 38 mm'],[T('Mocowanie','Fixing'),'2 × M5, 43 mm'],[T('Masa kompletu','Set weight'),fmt(p.mass_g,0)+' g'],[T('Norma docelowa','Target standard'),'EN 13126-3 ('+T('wymaga badań','testing pending')+')']];}
 rows.push([T('Materiał','Material'),T('mosiądz bezołowiowy CW724R','lead-free brass CW724R')+(p.dir==='OS'?(p.species==='JS'?T(' + jesion olejowany',' + oiled ash'):T(' + dąb olejowany',' + oiled oak')):'')]);
 var fd=p.sku.split('/').pop();
 rows.push([T('Wykończenie domyślne','Default finish'),fd+' · '+finName(fd)]);
 var th=p.img.map(function(n,i){return '<button type="button" class="'+(i?'':'on')+'" data-i="'+n+'" title="'+E(vlab(n,i))+'"><img src="v12/img/'+n+'-640.webp" alt="'+E(vlab(n,i))+'" loading="lazy"></button>';}).join('')+'<button type="button" data-3d="1">3D</button>';
 var sizes=p.kind==='knob'?'<div class="step" style="margin-top:18px"><label>'+T('Rozmiar','Size')+'</label><div class="chips" id="ksz">'+['S','M','L'].map(function(s){return '<button type="button" data-s="'+s+'" class="'+(s==='M'?'on':'')+'">'+s+'</button>';}).join('')+'</div></div>':'';
 return '<section class="wrap"><div class="crumb"><a href="#/kolekcje">'+T('Kolekcje','Collections')+'</a> / <a href="#/kolekcja/'+p.dir+'">'+NAME[p.dir]+'</a> / '+E(kindName(p))+'</div></section>'+
 '<section class="wrap pg"><div><div id="pmain">'+img(p.img[0],'r43',kindName(p),true)+'</div><div class="thumbs">'+th+'</div><p class="note" style="margin-top:10px">'+(p.kind==='pull'&&!p.species&&p.img.length>1?T('Widoki przód / detal / góra pokazują rozstaw 128.','Front / detail / top views show the 128 spacing.')+' ':'')+T('Przycisk 3D składa model na żywo z modułów CAD.','The 3D button assembles the model live from the CAD modules.')+'</p></div>'+
 '<div><div class="k">'+NAME[p.dir]+' · '+T(SUB[p.dir][0],SUB[p.dir][1])+'</div><h1 style="font-size:clamp(32px,3.6vw,48px)">'+E(kindName(p))+'</h1><div class="skuline" id="psku">'+E(p.sku)+'</div>'+sizes+
 '<table class="tbl">'+rows.map(function(r){return '<tr><th>'+r[0]+'</th><td>'+E(r[1])+'</td></tr>';}).join('')+'</table>'+
 '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px"><button class="btn" type="button" id="padd">'+T('Dodaj do zapytania','Add to inquiry')+'</button><a class="btn o" id="pcfg" href="#/konfigurator/'+encodeURIComponent(p.sku)+'">'+T('Zmień moduły','Change the modules')+'</a></div>'+
 '<p class="note" style="margin-top:18px">'+T('Ceny na zapytanie. Każdy moduł jest też dostępny osobno jako część zamienna.','Prices on request. Every module is also available separately as a spare part.')+'</p></div></section>';}
function finName(f){var a=f.split('.'),b=FIN[a[0]];if(!b)return f;return T(b[0],b[1])+(a[1]?T(', akcenty ',', accents ')+T(FIN[a[1]][0],FIN[a[1]][1]):'');}
function pMix(){return '<section class="wrap" style="padding:48px 0 80px"><div class="k">Mix &amp; match</div><h1>'+T('Zestawienia między kierunkami','Mixing the directions')+'</h1><p style="max-width:44em">'+T('Wszystkie kierunki dzielą te same interfejsy: chwyty F stają na słupkach SR7, SR8, SQ7 lub SK8, pręty okrągłe przechodzą przez obrączkę lub tulejkę dopasowaną do średnicy, a głowice gałek pasują do każdego trzonu M4. Poniższe zestawienia zostały złożone i sprawdzone w teście systemu – każde można otworzyć w konfiguratorze 3D.','All directions share the same interfaces: F grips stand on SR7, SR8, SQ7 or SK8 posts, round rods pass through a ring or ferrule sized to their diameter, and knob heads fit every M4 stem. The combinations below were assembled and checked in the system test – open any of them in the 3D configurator.')+'</p>'+
 '<div class="g3" style="margin-top:34px">'+N.mix.map(mixCard).join('')+'</div>'+
 '<div class="g2" style="margin-top:70px;align-items:start"><div><h2>'+T('Zasady łączenia','Mixing rules')+'</h2><ul class="rules">'+RULES().map(function(r){return '<li>'+r+'</li>';}).join('')+'</ul></div><div>'+img('mix_and_match_sheet','r43','Mix & match')+'</div></div></section>';}
function RULES(){return [T('Chwyty płaskie (PION, KASKADA) stają na słupkach H30: SR7, SR8, SQ7 lub SK8.','Flat-seat grips (PION, KASKADA) take H30 posts: SR7, SR8, SQ7 or SK8.'),
 T('Pręty okrągłe (OBRĄCZKA, OSIKA) przechodzą przez obrączkę R lub tulejkę F o tej samej średnicy; słupek kwadratowy SQ7 nie jest tu dozwolony.','Round rods (OBRĄCZKA, OSIKA) pass through an R ring or F ferrule of matching diameter; the square SQ7 post is not allowed here.'),
 T('OTOCZAK stoi na słupkach H12; kroplowy słupek OTD tylko pod OTOCZAKIEM.','OTOCZAK stands on H12 posts; the OTD drop post is used only under OTOCZAK.'),
 T('SQ7 przyjmuje podkładkę WS11 lub żadnej; SK8 ma stopę zintegrowaną, bez podkładki.','SQ7 takes the WS11 washer or none; SK8 has an integral foot and no washer.'),
 T('Gałka T kierunku PION wymaga trzonu z kołkiem SQ7-K24; okrągłe głowice pasują do każdego trzonu.','The PION T-knob needs the pinned SQ7-K24 stem; round heads fit every stem.'),
 T('Każda klamka na każdej rozecie; szyld zawsze w obrysie rozety.','Any lever on any rose; the escutcheon always follows the rose outline.'),
 T('Wykończenia z powłoką (MB, WH, NK) tylko jako cały komplet.','Coated finishes (MB, WH, NK) only as a complete set.')];}
function pSystem(){var c=N.counts;
 return '<section class="wrap" style="padding:48px 0 30px"><div class="k">System v11</div><h1>'+T('Jak zbudowany jest uchwyt','How a handle is built')+'</h1></section>'+
 '<section class="wrap g2" style="align-items:start;padding-bottom:60px"><div>'+img('exploded_OB-R128_annotated','r43',T('Widok rozstrzelony: OBRĄCZKA 128','Exploded view: OBRĄCZKA 128'),true)+'<p class="note" style="margin-top:10px">'+T('Widok rozstrzelony: OBRĄCZKA 128 na słupkach SR7 z obrączkami CR8-8 i podkładkami WR12.','Exploded view: OBRĄCZKA 128 on SR7 posts with CR8-8 rings and WR12 washers (labels in Polish).')+'</p></div>'+
 '<div class="steps4"><div><h3>'+T('Chwyt','Grip')+'</h3><p>'+T('Pręt, płetwa, otoczak lub chwyt schodkowy – z gwintem wewnętrznym M4 od spodu (pręty: gwint promieniowy, min. Ø8).','Rod, fin, pebble or stepped grip – with a female M4 thread from below (rods: radial thread, min. Ø8).')+'</p></div>'+
 '<div><h3>'+T('Obrączka / tulejka','Ring / ferrule')+'</h3><p>'+T('Dla prętów okrągłych: płaska baza ≥ 5,6 mm i przelot Ø4,3. Styl R (polerowany) lub F (satynowy) jest dowolny.','For round rods: a flat land ≥ 5.6 mm and a Ø4.3 passage. The R (polished) or F (satin) style is free.')+'</p></div>'+
 '<div><h3>'+T('Słupek','Post')+'</h3><p>'+T('SR7, SR8, SQ7, SK8 lub OTD; M4 na górze i w stopie, trzpień ISO 4026 z Loctite 243.','SR7, SR8, SQ7, SK8 or OTD; M4 at the top and in the foot, ISO 4026 stud with Loctite 243.')+'</p></div>'+
 '<div><h3>'+T('Podkładka','Washer')+'</h3><p>'+T('Czop Ø5,0 × 1,0 w kieszeni Ø5,1 stopy – podkładka zawsze się centruje. Wkręt M4 od tyłu frontu.','A Ø5.0 × 1.0 spigot in the Ø5.1 foot counterbore – the washer always centres. M4 screw from the back of the front.')+'</p></div></div></section>'+
 '<section class="sec alt"><div class="wrap g2" style="align-items:start"><div><div class="k">'+T('Testy','Tests')+'</div><h2>'+T('Każda kombinacja złożona i sprawdzona','Every combination assembled and checked')+'</h2>'+
 '<table class="tbl"><tr><th>'+T('Uchwyty','Pulls')+'</th><td>'+c.pull.passed+' / '+c.pull.total+'</td></tr><tr><th>'+T('Gałki','Knobs')+'</th><td>'+c.knob.passed+' / '+c.knob.total+'</td></tr><tr><th>'+T('Klamki × rozety','Levers × roses')+'</th><td>'+c.door.passed+' / '+c.door.total+'</td></tr><tr><th>'+T('Klamki okienne × rozety','Window handles × roses')+'</th><td>'+c.window.passed+' / '+c.window.total+'</td></tr><tr><th>'+T('Szyldy','Escutcheons')+'</th><td>'+c.esc.passed+' / '+c.esc.total+'</td></tr><tr><th>'+T('Testy negatywne (wykryte błędy)','Negative tests (caught)')+'</th><td>'+c.negative.caught+' / '+c.negative.total+'</td></tr></table>'+
 '<p class="note" style="margin-top:12px">'+T('Sprawdzane geometrycznie na modelu B-rep: brak kolizji, styk powierzchni nośnych ≥ 10 mm², współosiowość M4, ścianka gwintu, prześwit pod chwytem ≥ 30 mm (gałki ≥ 15 mm), ugięcie przy 100 N ≤ 0,5 mm. To kontrola konstrukcyjna – nie zastępuje badań normowych.','Checked geometrically on the B-rep model: no interference, bearing contact ≥ 10 mm², co-axial M4, thread wall, finger clearance ≥ 30 mm (knobs ≥ 15 mm), deflection at 100 N ≤ 0.5 mm. This is a design check – it does not replace standard testing.')+'</p></div>'+
 '<div><div class="k">'+T('Katalog','Catalogue')+'</div><h2>'+T('Katalog modułowy v11','Modular catalogue v11')+'</h2><p>'+T('Wszystkie moduły, macierze zgodności, schemat SKU, klamki EU i wyniki testów w jednym pliku PDF (język polski).','All modules, compatibility matrices, the SKU scheme, EU levers and the test results in one PDF (in Polish).')+'</p><a class="btn" href="'+N.pdf+'" download>'+T('Pobierz katalog PDF','Download the PDF catalogue')+'</a>'+
 '<h3 style="margin-top:40px">'+T('Schemat SKU','SKU scheme')+'</h3><div class="skuline">{KIER}-{typ}{cc} / {słupek}-{H} / {podkładka} [/ {obrączka}] / {wykończenie}</div><p class="note">'+T('Np. ','E.g. ')+'<code>PN-F128/SQ7-30/WS11/SB</code> · <code>OS-DB128/SR8-30/WR12/CR8-12/SB.PB</code></p></div></div></section>'+
 '<section class="sec"><div class="wrap"><div class="k">'+T('Materiał i wykończenia','Material and finishes')+'</div><h2>CW724R</h2><div class="g2" style="align-items:start"><p>'+T('Mosiądz bezołowiowy CuZn21Si3P (≤ 0,10 % Pb), zgodny z RoHS/REACH i listą 4MS. Wykończenia bez powłoki – satynowe SB, polerowane PB i postarzane AB – patynują naturalnie.','Lead-free CuZn21Si3P brass (≤ 0.10 % Pb), RoHS/REACH compliant and on the 4MS list. The uncoated finishes – satin SB, polished PB and aged AB – patinate naturally.')+'</p>'+
 '<p class="note">'+T('Stopy miedzi bez powłoki mogą wykazywać właściwości przeciwdrobnoustrojowe; deklarację opublikujemy po badaniu naszych próbek SB/PB/AB (ISO 22196) i weryfikacji prawnej. Wykończenia MB, WH i NK mają powłokę i tej właściwości nie dotyczą.','Uncoated copper alloys may show antimicrobial properties; we will publish a claim only after testing our own SB/PB/AB samples (ISO 22196) and a legal review. The coated MB, WH and NK finishes are not covered.')+'</p></div></div></section>';}
function pInquiry(){var a=inq();
 return '<section class="wrap" style="padding:48px 0 80px;max-width:900px"><div class="k">'+T('Zapytanie ofertowe','Quote request')+'</div><h1>'+T('Twoja lista','Your list')+'</h1>'+
 (a.length?'<ul class="inq" style="list-style:none;padding:0">'+a.map(function(x,i){return '<li><code>'+E(x.sku)+'</code><span class="mut" style="font-size:13px">'+E(x.name||'')+'</span><input type="number" min="1" value="'+x.qty+'" data-q="'+i+'" aria-label="qty"><button class="btn o s" type="button" data-del="'+i+'">'+T('Usuń','Remove')+'</button></li>';}).join('')+'</ul>':'<p class="mut">'+T('Lista jest pusta. Dodaj produkty z kolekcji albo z konfiguratora.','The list is empty. Add products from the collections or the configurator.')+'</p>')+
 '<div style="margin-top:28px;display:grid;gap:12px"><input type="text" id="iqn" placeholder="'+T('Imię i nazwisko / firma','Name / company')+'"><textarea id="iqt" rows="4" placeholder="'+T('Uwagi: ilości, termin, wykończenie, adres dostawy','Notes: quantities, timing, finish, delivery address')+'"></textarea></div>'+
 '<div style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn" id="iqm" href="#">'+T('Wyślij zapytanie e-mailem','Send the inquiry by e-mail')+'</a><a class="btn o" href="#/konfigurator">'+T('Konfigurator','Configurator')+'</a></div>'+
 '<p class="note" style="margin-top:16px">'+T('Otworzy się Twój program pocztowy z gotową wiadomością do ','Your e-mail app opens with a ready message to ')+MAIL+' [PLACEHOLDER — '+T('adres do potwierdzenia przez właściciela','address to be confirmed by the owner')+']. '+T('Dane przetwarzamy wyłącznie w celu przygotowania oferty.','We use your data only to prepare the quote.')+'</p></section>';}
/* ---------------- configurator logic ---------------- */
var CF={kind:'pull'};
function parsePull(s){var a=s.split('/'),pm=/^(.+)-(\d+)$/.exec(a[1]);return {bar:a[0],post:pm[1],H:+pm[2],washer:a[2],collar:a[3]||null};}
function parseKnob(s){var a=s.split('/');return {head:a[0],stem:a[1],washer:a[2]};}
var PULLS=N.combos.pull.map(function(s){var o=parsePull(s);o.s=s;return o;}), KNOBS=N.combos.knob.map(function(s){var o=parseKnob(s);o.s=s;return o;});
var BARS=[];DIRS.forEach(function(d){(d==='OS'?['DB','JS']:[null]).forEach(function(sp){BARS.push({d:d,sp:sp,key:d+(sp?'-'+sp:'')});});});
function barCode(key,cc){var d=key.slice(0,2),sp=key.split('-')[1];var m=N.modules;for(var c in m){var x=m[c];if(x.kind==='bar'&&x.dir===d&&x.meta.cc===cc&&(d!=='OS'||c.indexOf('-'+sp)===2))return c;}return null;}
function barKey(code){var d=code.slice(0,2);return d==='OS'?(code.indexOf('-JS')===2?'OS-JS':'OS-DB'):d;}
function setFromSku(sku){var a=sku.split('/'),fin=a.pop(),core=a.join('/');
 if(N.combos.pull.indexOf(core)>=0){var o=parsePull(core),b=N.modules[o.bar];CF={kind:'pull',bk:barKey(o.bar),cc:b.meta.cc,post:o.post,washer:o.washer,cst:o.collar?o.collar[1]:null,fin:fin};return true;}
 if(N.combos.knob.indexOf(core)>=0){var k=parseKnob(core);CF={kind:'knob',hd:k.head.slice(0,2),size:k.head.slice(-1),stem:k.stem,washer:k.washer,fin:fin};return true;}
 var dm=/^([A-Z]{2})-L\/([A-Z]{2})-R(?:\/[A-Z]{2}-E(\w+))?$/.exec(core);if(dm){CF={kind:'door',lv:dm[1],rs:dm[2],esc:dm[3]||'none',fin:fin};return true;}
 var wm=/^([A-Z]{2})-O\/([A-Z]{2})-RO$/.exec(core);if(wm){CF={kind:'window',lv:wm[1],rs:wm[2],fin:fin};return true;}
 return false;}
function defaults(kind){var p;if(kind==='pull'){setFromSku(PRODS['OB-pull-128'].sku);}else if(kind==='knob'){setFromSku(PRODS['KS-knob'].sku);}else if(kind==='door'){CF={kind:'door',lv:'OS',rs:'KS',esc:'PZ',fin:'SB'};}else{CF={kind:'window',lv:'PN',rs:'PN',fin:'SB'};}}
function resolve(){/* clamp the state to an allowed combination; returns {sku, opts} */
 var o={};
 if(CF.kind==='pull'){var bc=barCode(CF.bk,CF.cc);if(!bc){CF.cc=128;bc=barCode(CF.bk,128);}
  var c=PULLS.filter(function(x){return x.bar===bc;}),def=parsePull(PRODS[(CF.bk==='OS-JS'?'OSJS':CF.bk.slice(0,2))+'-pull-'+CF.cc].sku.split('/').slice(0,-1).join('/'));
  o.posts=uniq(c.map(function(x){return x.post;}));if(o.posts.indexOf(CF.post)<0)CF.post=o.posts.indexOf(def.post)>=0?def.post:o.posts[0];
  c=c.filter(function(x){return x.post===CF.post;});o.washers=uniq(c.map(function(x){return x.washer;}));if(o.washers.indexOf(CF.washer)<0)CF.washer=o.washers.indexOf(def.washer)>=0?def.washer:o.washers[0];
  c=c.filter(function(x){return x.washer===CF.washer;});o.cst=uniq(c.map(function(x){return x.collar?x.collar[1]:null;}));if(o.cst.indexOf(CF.cst)<0)CF.cst=o.cst[0];
  c=c.filter(function(x){return (x.collar?x.collar[1]:null)===CF.cst;});o.combo=c[0];o.core=c[0].s;o.bar=bc;}
 else if(CF.kind==='knob'){var hc=CF.hd+'-K'+CF.size,k=KNOBS.filter(function(x){return x.head===hc;});
  o.stems=uniq(k.map(function(x){return x.stem;}));if(o.stems.indexOf(CF.stem)<0)CF.stem=o.stems.indexOf(N.knob_default[CF.hd][0])>=0?N.knob_default[CF.hd][0]:o.stems[0];
  k=k.filter(function(x){return x.stem===CF.stem;});o.washers=uniq(k.map(function(x){return x.washer;}));if(o.washers.indexOf(CF.washer)<0)CF.washer=o.washers.indexOf(N.knob_default[CF.hd][1]||'W0')>=0?(N.knob_default[CF.hd][1]||'W0'):o.washers[0];
  o.core=k.filter(function(x){return x.washer===CF.washer;})[0].s;}
 else if(CF.kind==='door'){o.core=CF.lv+'-L/'+CF.rs+'-R';if(N.combos.door.indexOf(o.core)<0)throw new Error('door combo');if(CF.esc!=='none'&&N.combos.esc.indexOf(CF.rs)>=0)o.core+='/'+CF.rs+'-E'+CF.esc;}
 else{o.core=CF.lv+'-O/'+CF.rs+'-RO';if(N.combos.window.indexOf(o.core)<0)throw new Error('window combo');}
 if(FINS.indexOf(CF.fin)<0)CF.fin='SB';
 o.sku=o.core+'/'+CF.fin;return o;}
function uniq(a){var r=[];a.forEach(function(x){if(r.indexOf(x)<0)r.push(x);});return r;}
var WNAME={W0:['bez podkładki','no washer'],WR12:['okrągła PB Ø12','round PB Ø12'],WR13:['okrągła Ø13','round Ø13'],WD14:['kopułka Ø14','dome Ø14'],WS11:['kwadrat □11','square □11'],WT17:['schodkowa Ø17','stepped Ø17']};
var PNAME={SR7:['okrągły Ø7','round Ø7'],SR8:['okrągły Ø8','round Ø8'],SQ7:['kwadrat □7','square □7'],SK8:['schodkowy','stepped'],OTD:['kropla','drop']};
function chip(attr,val,on,label,dis){return '<button type="button" data-'+attr+'="'+E(val)+'" class="'+(on?'on':'')+'"'+(dis?' disabled':'')+'>'+label+'</button>';}
function pConfig(arg){
 if(arg){try{if(!setFromSku(decodeURIComponent(arg)))defaults('pull');}catch(e){defaults('pull');}} else if(!CF.fin)defaults('pull');
 return '<section class="wrap"><div class="crumb">'+T('Konfigurator 3D · system v11','3D configurator · system v11')+'</div></section><section class="wrap cf"><div class="stage"><div class="v3" id="v3"><div class="hint">'+T('przeciągnij, aby obrócić · kółko / dwa palce: zoom','drag to rotate · wheel / pinch: zoom')+'</div><div class="ld" id="v3ld"></div></div>'+
 '<div class="skuline" id="csku"></div><div style="display:flex;gap:12px;flex-wrap:wrap"><button class="btn" type="button" id="cadd">'+T('Dodaj do zapytania','Add to inquiry')+'</button><a class="btn o" id="cprod" href="#/kolekcje">'+T('Kolekcja','Collection')+'</a></div></div>'+
 '<div><div class="tabs">'+[['pull',T('Uchwyt','Pull')],['knob',T('Gałka','Knob')],['door',T('Klamka drzwiowa','Door lever')],['window',T('Klamka okienna','Window handle')]].map(function(t){return chip('kind',t[0],CF.kind===t[0],t[1]);}).join('')+'</div><div id="cfo"></div></div></section>';}
function cfOptions(){
 var o=resolve(),h='';
 function step(lab,inner,note){h+='<div class="step"><label>'+lab+'</label><div class="chips">'+inner+'</div>'+(note?'<p class="note" style="margin:8px 0 0">'+note+'</p>':'')+'</div>';}
 if(CF.kind==='pull'){
  step(T('Chwyt (kierunek)','Grip (direction)'),BARS.map(function(b){return chip('bk',b.key,CF.bk===b.key,NAME[b.d]+(b.sp?(b.sp==='DB'?T(' dąb',' oak'):T(' jesion',' ash')):''));}).join(''));
  step(T('Rozstaw','Spacing'),N.combos&&[96,128,160,224,320].map(function(c){return chip('cc',c,CF.cc===c,c+' mm');}).join(''));
  step(T('Słupki','Posts'),['OTD','SR7','SR8','SQ7','SK8'].map(function(p){return chip('post',p,CF.post===p,p+' · '+T(PNAME[p][0],PNAME[p][1]),o.posts.indexOf(p)<0);}).join(''),T('Dostępne tylko dozwolone i przetestowane połączenia.','Only allowed, tested combinations are selectable.'));
  step(T('Podkładki','Washers'),['W0','WR12','WR13','WD14','WS11','WT17'].map(function(w){return chip('washer',w,CF.washer===w,(w==='W0'?'':w+' · ')+T(WNAME[w][0],WNAME[w][1]),o.washers.indexOf(w)<0);}).join(''));
  if(o.cst[0])step(T('Obrączka / tulejka','Ring / ferrule'),['R','F'].map(function(s){return chip('cst',s,CF.cst===s,s==='R'?T('obrączka R (OBRĄCZKA)','R ring (OBRĄCZKA)'):T('tulejka F (OSIKA)','F ferrule (OSIKA)'),o.cst.indexOf(s)<0);}).join(''));}
 else if(CF.kind==='knob'){
  step(T('Głowica (kierunek)','Head (direction)'),DIRS.map(function(d){return chip('hd',d,CF.hd===d,NAME[d]);}).join(''));
  step(T('Rozmiar','Size'),['S','M','L'].map(function(s){return chip('size',s,CF.size===s,s);}).join(''));
  step(T('Trzon','Stem'),['OTD-12','SR8-12','SR7-K21','SR8-K16','SK8-K18.5','SQ7-K24'].map(function(s){return chip('stem',s,CF.stem===s,s,o.stems.indexOf(s)<0);}).join(''));
  step(T('Podkładka','Washer'),['W0','WR12','WR13','WD14','WS11','WT17'].map(function(w){return chip('washer',w,CF.washer===w,(w==='W0'?'':w+' · ')+T(WNAME[w][0],WNAME[w][1]),o.washers.indexOf(w)<0);}).join(''));}
 else{
  step(CF.kind==='door'?T('Klamka (kierunek)','Lever (direction)'):T('Klamka okienna (kierunek)','Handle (direction)'),DIRS.map(function(d){return chip('lv',d,CF.lv===d,NAME[d]);}).join(''));
  step(T('Rozeta (kierunek)','Rose (direction)'),DIRS.map(function(d){return chip('rs',d,CF.rs===d,NAME[d]);}).join(''),T('Każda klamka pasuje do każdej rozety (wspólny czop Ø15).','Every lever fits every rose (shared Ø15 spigot).'));
  if(CF.kind==='door')step(T('Szyld (w obrysie rozety)','Escutcheon (rose outline)'),[['PZ',T('wkładka PZ · 72 mm','PZ cylinder · 72 mm')],['BB',T('klucz BB · 72 mm','BB key · 72 mm')],['WCi',T('WC zasuwka · 78 mm','WC thumbturn · 78 mm')],['WCo',T('WC zwolnienie · 78 mm','WC release · 78 mm')],['none',T('bez szyldu','none')]].map(function(e){return chip('esc',e[0],CF.esc===e[0],e[1]);}).join(''));}
 step(T('Wykończenie','Finish'),FINS.map(function(f){var a=f.split('.');return chip('fin',f,CF.fin===f,'<span class="sw" style="background:'+FIN[a[0]][2]+(a[1]?';box-shadow:inset -6px 0 0 '+FIN[a[1]][2]:'')+'"></span>'+f);}).join(''),finName(CF.fin)+'. '+T('Powłoki MB / WH / NK tylko dla całego kompletu.','MB / WH / NK coatings for the whole set only.'));
 var bom=bomOf(o);
 h+='<div class="step"><label>'+T('Moduły w komplecie','Modules in the set')+'</label><ul class="bom">'+bom.map(function(b){var m=N.modules[b[0]];return '<li><span><code>'+E(b[0])+'</code> <span class="mut">'+(m?(m.dir==='SYS'?T('moduł wspólny','shared module'):NAME[m.dir]):'')+'</span></span><span>× '+b[1]+'</span></li>';}).join('')+'</ul><p class="note ok" style="margin-top:10px">✓ '+T('Kombinacja jest w zestawie '+countAll()+' sprawdzonych w teście systemu.','This combination is among the '+countAll()+' verified in the system test.')+'</p></div>';
 $('#cfo').innerHTML=h; $('#csku').textContent=o.sku;
 var dirs=uniq(bom.map(function(b){var m=N.modules[b[0]];return m&&m.dir!=='SYS'?m.dir:null;}).filter(Boolean));
 $('#cprod').textContent=dirs.length>1?'Mix & match':T('Kolekcja ','Collection ')+NAME[dirs[0]||'OB']; $('#cprod').href=dirs.length>1?'#/mix':'#/kolekcja/'+(dirs[0]||'OB');
 V3.show(assemblyOf(o),CF.fin);
 try{history.replaceState(null,'','#/konfigurator/'+encodeURIComponent(o.sku));}catch(e){}
 return o;}
function bomOf(o){
 if(CF.kind==='pull'){var c=o.combo,r=[[c.bar,1],[c.post+'-'+c.H,2]];if(c.washer!=='W0')r.push([c.washer,2]);if(c.collar)r.push([c.collar,2]);return r;}
 if(CF.kind==='knob'){var k=parseKnob(o.core),r2=[[k.head,1],[k.stem,1]];if(k.washer!=='W0')r2.push([k.washer,1]);return r2;}
 if(CF.kind==='door'){var r3=[[CF.lv+'-L',1],[CF.rs+'-R',1]];if(CF.esc!=='none')r3.push([CF.rs+'-E'+CF.esc,1]);return r3;}
 return [[CF.lv+'-O',1],[CF.rs+'-RO',1]];}
/* assembly description in model mm (Z = away from the mounting face), mirrors nookcad assemble_* */
function assemblyOf(o){var M=N.modules,it=[];
 if(CF.kind==='pull'){var c=o.combo,b=M[c.bar],p=M[c.post+'-'+c.H],w=c.washer!=='W0'?M[c.washer]:null,cl=c.collar?M[c.collar]:null,t=w?w.meta.t:0,H=p.meta.H,cc=b.meta.cc,pins=p.meta.pins&&p.meta.pins.length;
  [-cc/2,cc/2].forEach(function(x){if(w)it.push([c.washer,x,0,0,0]);it.push([c.post+'-'+c.H,x,0,t,(x>0&&pins)?90:0]);if(cl)it.push([c.collar,x,0,t+H,0]);});
  it.push([c.bar,0,0,t+H+(cl?cl.meta.f:0),0]);return {up:'z',items:it};}
 if(CF.kind==='knob'){var k=parseKnob(o.core),kw=k.washer!=='W0'?M[k.washer]:null,kt=kw?kw.meta.t:0;if(kw)it.push([k.washer,0,0,0,0]);it.push([k.stem,0,0,kt,0]);it.push([k.head,0,0,kt+M[k.stem].meta.H,0]);return {up:'z',items:it};}
 if(CF.kind==='door'){it=[[CF.rs+'-R',0,0,0,0],[CF.lv+'-L',0,0,0,0]];if(CF.esc!=='none'){var e=M[CF.rs+'-E'+CF.esc],dist=/^WC/.test(CF.esc)?78:72;it.push([CF.rs+'-E'+CF.esc,0,-dist-e.meta.axis,0,0]);}return {up:'y',items:it,panel:-9};}
 return {up:'y',items:[[CF.rs+'-RO',0,0,0,0],[CF.lv+'-O',0,0,0,0]],panel:-12};}
/* ---------------- three.js viewer ---------------- */
var V3=(function(){
 var CDN='https://cdn.jsdelivr.net/npm/three@0.128.0/',ready=null,R,S,C,CT,G,el,tpl={},want=null,raf=0,ground,panel;
 function load(src){return new Promise(function(ok,ko){var s=document.createElement('script');s.src=src;s.crossOrigin='anonymous';s.onload=ok;s.onerror=function(){ko(new Error(src));};document.head.appendChild(s);});}
 function three(){if(!ready)ready=(window.THREE?Promise.resolve():load(CDN+'build/three.min.js')).then(function(){return Promise.all([THREE.GLTFLoader?0:load(CDN+'examples/js/loaders/GLTFLoader.js'),THREE.OrbitControls?0:load(CDN+'examples/js/controls/OrbitControls.js')]);});return ready;}
 function col(h){return new THREE.Color(h).convertSRGBToLinear();}
 var MATS={};
 function mat(key){if(MATS[key])return MATS[key];var P={SB:['#C9A66D',1,.36],PB:['#E2C27F',1,.12],AB:['#8A683D',1,.48],SBm:['#C4A169',1,.52],PBm:['#D9B877',1,.3],ABm:['#86653B',1,.58],MB:['#232220',.35,.5],WH:['#EEE9DF',0,.42],NK:['#BDBBB5',1,.3],steel:['#6E6E6C',1,.35]}[key];
  var m;if(key==='oak'||key==='ash')m=new THREE.MeshStandardMaterial({map:wood(key),roughness:.62,metalness:0});else m=new THREE.MeshStandardMaterial({color:col(P[0]),metalness:P[1],roughness:P[2]});
  return MATS[key]=m;}
 function wood(k){var c=document.createElement('canvas');c.width=512;c.height=64;var x=c.getContext('2d'),base=k==='oak'?'#9C7550':'#D2BE9C',dk=k==='oak'?'rgba(80,45,18,':'rgba(120,90,50,';x.fillStyle=base;x.fillRect(0,0,512,64);
  for(var i=0;i<70;i++){x.strokeStyle=dk+(0.08+Math.random()*0.22)+')';x.lineWidth=0.5+Math.random()*1.6;var y=Math.random()*64;x.beginPath();x.moveTo(0,y);for(var u=0;u<=512;u+=32)x.lineTo(u,y+Math.sin(u/90+i)*2.2);x.stroke();}
  var t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.wrapS=t.wrapT=THREE.RepeatWrapping;return t;}
 function pick(name,fin){var pre=String(name).split('_')[0].toLowerCase(),a=fin.split('.'),body=a[0],acc=a[1]||body,coated=/^(MB|WH|NK)$/.test(body);
  if(pre==='oak'||pre==='ash')return mat(pre);if(pre==='steel')return mat('steel');
  if(coated)return mat(body);if(pre==='pol')return mat(acc);if(pre==='matte')return mat(body+'m');return mat(body);}
 function env(){var pm=new THREE.PMREMGenerator(R),es=new THREE.Scene();
  es.add(new THREE.Mesh(new THREE.BoxGeometry(12,8,12),new THREE.MeshBasicMaterial({color:col('#9C9284'),side:THREE.BackSide})));
  function lp(w,h,x,y,z,i){var m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(i,i*.96,i*.9),side:THREE.DoubleSide}));m.position.set(x,y,z);m.lookAt(0,0,0);es.add(m);}
  lp(5,3,-3,3.5,2,5);lp(1.2,6,4,2,-1,7);lp(6,2,0,-1,5,1.6);lp(8,8,0,3.9,0,1.4);
  var t=pm.fromScene(es,.03).texture;pm.dispose();return t;}
 function init(host){el=host;R=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});R.setPixelRatio(Math.min(window.devicePixelRatio||1,2));R.outputEncoding=THREE.sRGBEncoding;R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=1.05;R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;
  host.appendChild(R.domElement);S=new THREE.Scene();S.background=new THREE.Color('#EEE9E1');S.environment=env();
  S.add(new THREE.HemisphereLight(0xfff6ea,0xd9d0c3,.35));var dl=new THREE.DirectionalLight(0xfff0dc,1.25);dl.position.set(-.25,.5,.3);dl.castShadow=true;dl.shadow.mapSize.set(2048,2048);var sc=dl.shadow.camera;sc.left=sc.bottom=-.3;sc.right=sc.top=.3;sc.near=.05;sc.far=2;dl.shadow.radius=6;dl.shadow.bias=-.0004;S.add(dl);S.add(dl.target);
  ground=new THREE.Mesh(new THREE.PlaneGeometry(4,4),new THREE.ShadowMaterial({opacity:.16}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;S.add(ground);
  panel=new THREE.Mesh(new THREE.PlaneGeometry(1.2,1.2),new THREE.MeshStandardMaterial({color:col('#E3DCD0'),roughness:.8,metalness:0}));panel.receiveShadow=true;S.add(panel);
  C=new THREE.PerspectiveCamera(28,4/3,.005,10);CT=new THREE.OrbitControls(C,R.domElement);CT.enableDamping=true;CT.dampingFactor=.12;CT.enablePan=false;CT.addEventListener('change',draw);
  window.addEventListener('resize',size);size();}
 function size(){if(!el||!R)return;var w=el.clientWidth,h=el.clientHeight||w*.75;R.setSize(w,h,false);C.aspect=w/h;C.updateProjectionMatrix();draw();}
 function draw(){if(raf)return;raf=requestAnimationFrame(function(){raf=0;if(CT)CT.update();R.render(S,C);});}
 function glb(code){if(!tpl[code])tpl[code]=new Promise(function(ok,ko){new THREE.GLTFLoader().load(N.modules[code].file.replace(/^mod\//,'v12/mod/'),function(g){var r=g.scene;r.traverse(function(o){if(o!==r&&o.parent===r)o.quaternion.set(0,0,0,1);});ok(r);},undefined,ko);});return tpl[code];}
 var seq=0,lastKind='';
 function show(asm,fin){want=[asm,fin];var host=$('#v3');if(!host)return;var my=++seq,ld=$('#v3ld');if(ld)ld.textContent=T('ładowanie modułów…','loading modules…');
  three().then(function(){if(!R||!document.body.contains(R.domElement))init(host);else if(R.domElement.parentNode!==host){host.appendChild(R.domElement);el=host;size();}
   return Promise.all(asm.items.map(function(i){return glb(i[0]);}));}).then(function(ts){if(my!==seq)return;
   if(G)S.remove(G);G=new THREE.Group();var inner=new THREE.Group();G.add(inner);
   asm.items.forEach(function(i,n){var h=new THREE.Group(),m=ts[n].clone(true);m.traverse(function(o){if(o.isMesh){o.material=pick(o.name||(o.parent&&o.parent.name)||'',fin);o.castShadow=true;o.receiveShadow=true;}});h.add(m);h.position.set(i[1]/1000,i[2]/1000,i[3]/1000);h.rotation.z=i[4]*Math.PI/180;inner.add(h);});
   if(asm.up==='z'){inner.rotation.x=-Math.PI/2;ground.visible=true;panel.visible=false;}else{ground.visible=false;panel.visible=true;panel.position.set(0,0,asm.panel/1000);}
   S.add(G);G.updateMatrixWorld(true);var bb=new THREE.Box3().setFromObject(G),cs=bb.getCenter(new THREE.Vector3()),sz=bb.getSize(new THREE.Vector3());
   if(asm.up!=='z'){panel.position.x=cs.x;panel.position.y=cs.y;}
   var r=Math.max(sz.x,sz.y,sz.z,.05)*.5,d=r/Math.tan(C.fov*Math.PI/360)*(C.aspect<1?1.9:1.32);
   var kind=asm.up+asm.items.length+(asm.items[0]||[''])[0].slice(0,2);
   if(kind!==lastKind||!CT.target.lengthSq()){CT.target.copy(cs);if(asm.up==='z')C.position.set(cs.x+d*.42,cs.y+d*.52,cs.z+d*.74);else C.position.set(cs.x+d*.38,cs.y+d*.12,cs.z+d*.92);lastKind=kind;}else CT.target.copy(cs);
   CT.minDistance=d*.35;CT.maxDistance=d*2.5;CT.maxPolarAngle=asm.up==='z'?Math.PI*.49:Math.PI;C.near=d/100;C.far=d*20;C.updateProjectionMatrix();
   var ld2=$('#v3ld');if(ld2)ld2.textContent='';draw();window.__nf3dReady=(window.__nf3dReady||0)+1;}).catch(function(e){var ld3=$('#v3ld');if(ld3)ld3.textContent=T('3D niedostępne','3D unavailable');console.warn('nf3d',e);});}
 return {show:show,draw:draw};})();
window.NF12app={resolve:resolve,setFromSku:setFromSku,assemblyOf:assemblyOf,CF:function(){return CF;},V3:V3};
/* ---------------- router ---------------- */
function route(){
 var h=(location.hash||'').replace(/^#\/?/,''),seg=h.split('/'),app=$('#app'),html,after=null;
 if(!seg[0])html=pHome();
 else if(seg[0]==='kolekcje')html=pCollections();
 else if(seg[0]==='kolekcja')html=pCollection(seg[1]);
 else if(seg[0]==='produkt')html=pProduct(seg[1]),after=wireProduct.bind(null,seg[1]);
 else if(seg[0]==='konfigurator')html=pConfig(seg.slice(1).join('/')),after=wireConfig;
 else if(seg[0]==='mix')html=pMix();
 else if(seg[0]==='system')html=pSystem();
 else if(seg[0]==='zapytanie')html=pInquiry(),after=wireInq;
 else html=pHome();
 app.innerHTML=html;$$('.nav a').forEach(function(a){var r=a.getAttribute('data-r');a.classList.toggle('on',!!r&&seg[0].indexOf(r)===0);});
 $('.nav').classList.remove('open');if(after)after();badge();
 if(!/^konfigurator/.test(seg[0])||!route.cfg)window.scrollTo(0,0);route.cfg=/^konfigurator/.test(seg[0]);
 document.title=(seg[0]?(NAME[seg[1]]||(PRODS[seg[1]]?kindName(PRODS[seg[1]]):'')||({kolekcje:T('Kolekcje','Collections'),konfigurator:T('Konfigurator','Configurator'),mix:'Mix & match',system:'System',zapytanie:T('Zapytanie','Inquiry')}[seg[0]]||''))+' · ':'')+'NOOK FORM — '+T('system modułowy z mosiądzu','modular brass system');}
function wireProduct(id){var p=PRODS[id],cur=p.sku;
 $$('.thumbs button').forEach(function(b){b.addEventListener('click',function(){$$('.thumbs button').forEach(function(x){x.classList.remove('on');});b.classList.add('on');
  if(b.getAttribute('data-3d')){$('#pmain').innerHTML='<div class="v3" id="v3"><div class="hint">'+T('przeciągnij, aby obrócić','drag to rotate')+'</div><div class="ld" id="v3ld"></div></div>';var keep=CF;setFromSku(cur);var o=resolve();V3.show(assemblyOf(o),CF.fin);CF=keep;}
  else $('#pmain').innerHTML=img(b.getAttribute('data-i'),'r43',kindName(p),true);});});
 $$('#ksz button').forEach(function(b){b.addEventListener('click',function(){$$('#ksz button').forEach(function(x){x.classList.remove('on');});b.classList.add('on');cur=p.sizes[b.getAttribute('data-s')].sku;$('#psku').textContent=cur;$('#pcfg').href='#/konfigurator/'+encodeURIComponent(cur);});});
 $('#padd').addEventListener('click',function(){inqAdd(cur,kindName(p));});}
function wireConfig(){cfOptions();
 $('.cf').addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b||b.disabled)return;var ds=b.dataset;
  if(ds.kind){if(ds.kind!==CF.kind){defaults(ds.kind);$$('.tabs button').forEach(function(x){x.classList.toggle('on',x.dataset.kind===ds.kind);});}}
  else if(ds.bk)CF.bk=ds.bk;else if(ds.cc)CF.cc=+ds.cc;else if(ds.post)CF.post=ds.post;else if(ds.washer)CF.washer=ds.washer;else if(ds.cst)CF.cst=ds.cst;else if(ds.hd)CF.hd=ds.hd;else if(ds.size)CF.size=ds.size;else if(ds.stem)CF.stem=ds.stem;else if(ds.lv)CF.lv=ds.lv;else if(ds.rs)CF.rs=ds.rs;else if(ds.esc)CF.esc=ds.esc;else if(ds.fin)CF.fin=ds.fin;
  else if(b.id==='cadd'){inqAdd($('#csku').textContent,T('Konfiguracja','Configuration'));return;}else return;
  cfOptions();});}
function wireInq(){function upd(){var a=inq(),n=($('#iqn')||{}).value||'',t=($('#iqt')||{}).value||'';var body=T('Dzień dobry,\nproszę o ofertę na:\n','Hello,\nplease quote for:\n')+a.map(function(x){return '- '+x.sku+' × '+x.qty+(x.name?' ('+x.name+')':'');}).join('\n')+'\n\n'+t+'\n\n'+n;$('#iqm').href='mailto:'+MAIL+'?subject='+encodeURIComponent(T('Zapytanie NOOK FORM','NOOK FORM inquiry'))+'&body='+encodeURIComponent(body);}
 $$('[data-q]').forEach(function(i){i.addEventListener('change',function(){var a=inq();a[+i.dataset.q].qty=Math.max(1,+i.value||1);inqSave(a);upd();});});
 $$('[data-del]').forEach(function(b){b.addEventListener('click',function(){var a=inq();a.splice(+b.dataset.del,1);inqSave(a);route();});});
 ['#iqn','#iqt'].forEach(function(s){$(s).addEventListener('input',upd);});upd();}
function boot(){document.body.innerHTML=header()+'<main id="app"></main>'+footer();document.documentElement.lang=L;route();}
document.addEventListener('click',function(ev){var t=ev.target;if(!t.closest)return;if(t.closest('.lang')){L=L==='en'?'pl':'en';try{LS.setItem('nf12-lang',L);}catch(e){}boot();return;}if(t.closest('.burger'))$('.nav').classList.toggle('open');});
var booted=false;window.addEventListener('hashchange',route);
function start(){if(booted){return;}booted=true;boot();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
