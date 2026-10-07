/* NOOK FORM v4–v8: pre-rendered static WebP product photos. Inserts the image into each photo slot before
   the in-browser three.js renderer reaches it (it skips slots that already hold an <img>); unknown keys
   (e.g. configurator variants) still render live. The 3D viewer is untouched. MAP is filled by CI. */
(function(){var M=/*MAP*/{}/*END*/,D='v8/p/';if(/[?&]nfcap/.test(location.search))return;
function show(el,im){var ok=function(){setTimeout(function(){im.classList.add('nfp-in');var s=el.querySelector(':scope>svg');if(s)s.style.opacity='0';},20);};
if(im.complete&&im.naturalWidth)ok();else im.addEventListener('load',ok);}
function put(el,k,cls){if(!M[k])return;var ex=el.querySelector('img');
if(ex){if(!ex.classList.contains('nfp-in')&&ex.src.indexOf(M[k])>=0)show(el,ex);return;}/* markup re-rendered from a copy: re-attach the fade-in */
var im=new Image();im.className=cls;im.alt=el.getAttribute('data-alt')||'';im.decoding='async';if(cls==='nfs-img')im.loading='lazy';im.src=D+M[k];el.appendChild(im);show(el,im);}
function one(n){if(n.matches('.nfp[data-k]'))put(n,n.getAttribute('data-k'),'nfp-img');else if(n.matches('[data-nf-scene]'))put(n,'scene:'+n.getAttribute('data-nf-scene'),'nfs-img');}
function scan(r){if(r.nodeType!==1)return;one(r);var a=r.querySelectorAll('.nfp[data-k],[data-nf-scene]');for(var i=0;i<a.length;i++)one(a[i]);}
new MutationObserver(function(ms){for(var i=0;i<ms.length;i++)for(var j=0;j<ms[i].addedNodes.length;j++)scan(ms[i].addedNodes[j]);}).observe(document,{childList:true,subtree:true});})();
