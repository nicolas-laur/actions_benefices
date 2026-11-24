"""Audit de lisibilité : liste, page par page et en mode clair puis sombre, les textes sous le seuil de contraste WCAG AA (4,5, ou 3 pour les grands textes).
À lancer avec le site servi en local sur le port 8765 ; les boutons à fond dégradé (or, Instagram) sortent en faux positifs."""
import asyncio, json
from playwright.async_api import async_playwright
PAGES=['','fiches/','fiches/nvidia/','news/','lexique/','calculateurs/','videos/','lettre/','mentions-legales/','404.html']
JS='''() => {
 function rgb(s){const m=s.match(/[\\d.]+/g);return m?m.map(Number):null}
 function lum(c){const a=c.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]}
 function fond(el){while(el){const c=rgb(getComputedStyle(el).backgroundColor);if(c&&(c[3]===undefined||c[3]>.5))return c;el=el.parentElement}return [246,240,227]}
 const out=[];const vu=new Set();
 document.querySelectorAll('main *, footer *, header *').forEach(el=>{
   const t=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim().length>2).map(n=>n.textContent.trim()).join(' ');
   if(!t)return; const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0)return;
   if(el.closest('.ecran,.vignette-img,svg,.mq-vcarte,.kiosque,template,dialog:not([open])'))return;
   const c=rgb(cs.color), f=fond(el); if(!c)return;
   const a=c[3]===undefined?1:c[3]; const cc=c.slice(0,3).map((v,i)=>v*a+f[i]*(1-a));
   const L1=lum(cc),L2=lum(f), r=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
   const big=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.6&&+cs.fontWeight>=700);
   if(r<(big?3:4.5)){const k=el.className+'|'+t.slice(0,30); if(!vu.has(k)){vu.add(k);out.push([Math.round(r*10)/10, el.tagName.toLowerCase()+'.'+String(el.className).slice(0,40), t.slice(0,50)])}}
 });return out}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for sch in ['light','dark']:
            ctx=await b.new_context(viewport={'width':1440,'height':900},color_scheme=sch); pg=await ctx.new_page()
            print('=====',sch)
            for u in PAGES:
                await pg.goto('http://localhost:8765/'+u); await pg.wait_for_timeout(400)
                await pg.evaluate("document.querySelectorAll('.mq-anim,.mq-mot,.mq-pastille,.mq-note').forEach(e=>e.classList.add('vu'))")
                r=await pg.evaluate(JS)
                for x in r: print(u or '/', x)
        await b.close()
asyncio.run(main())
