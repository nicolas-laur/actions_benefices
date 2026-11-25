# Contrôle mobile de toutes les pages (390/360, clair/sombre) : textes qui débordent, textes sous 12 px, images sous 2x. Site servi sur le port 8765.
import asyncio, json
from playwright.async_api import async_playwright
PAGES=['','fiches/','fiches/nvidia/','fiches/alphabet/','news/','news/2026-11-20/','videos/','lexique/','lexique/pea/','calculateurs/','lettre/','mentions-legales/']
JS='''() => {
 const W=innerWidth, out={over:[],small:[],flou:[]};
 for (const el of document.querySelectorAll('main *, header *, footer *')) {
   const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden') continue;
   if(el.closest('.g-bureau,.gal-piste,.bandeau-piste,.mq-videos,svg,.flux-grand,[hidden]')) continue;
   const r=el.getBoundingClientRect(); if(!r.width||!r.height) continue;
   if(el.classList.contains('mq-flottant')||el.closest('.mq-flottant')) continue;
   const t=[...el.childNodes].some(n=>n.nodeType==3&&n.textContent.trim().length>1);
   if(t && (r.right>W+1||r.left<-1)) out.over.push(el.tagName+'.'+el.className.toString().slice(0,30)+' «'+el.textContent.trim().slice(0,25)+'» '+Math.round(r.left)+'..'+Math.round(r.right));
   if(t && parseFloat(cs.fontSize)<12) out.small.push(el.tagName+'.'+el.className.toString().slice(0,30)+' '+cs.fontSize+' «'+el.textContent.trim().slice(0,25)+'»');
   if(el.tagName==='IMG' && el.complete && el.naturalWidth && r.width>40 && el.naturalWidth < r.width*2*0.95) out.flou.push(el.getAttribute('src').slice(0,50)+' '+el.naturalWidth+' pour '+Math.round(r.width));
 }
 for(const k in out) out[k]=[...new Set(out[k])].slice(0,8); out.hscroll=document.documentElement.scrollWidth>W; return out;}'''
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for w,s in ((390,'dark'),(360,'light'),(390,'light'),(360,'dark')):
      c=await b.new_context(viewport={'width':w,'height':800},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme=s); pg=await c.new_page()
      for u in PAGES:
        await pg.goto('http://localhost:8765/'+u, wait_until='networkidle')
        h=await pg.evaluate('document.documentElement.scrollHeight')
        for y in range(0,h,900): await pg.evaluate(f'scrollTo(0,{y})'); await pg.wait_for_timeout(40)
        await pg.wait_for_timeout(400)
        r=await pg.evaluate(JS)
        if any(r[k] for k in ('over','small','flou')) or r['hscroll']: print(w,s,u or '/',json.dumps(r,ensure_ascii=False))
      await c.close()
    await b.close()
asyncio.run(main())
