# Captures d écran mobiles d une page (vues successives) : python3 vue.py <chemin> <nom> <largeur> <dark|light> ; site servi sur le port 8765. Sortie dans /home/claude/audit.
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
BASE='http://localhost:8765/'
async def main(url, nom, w, scheme, nmax=40):
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    ctx=await b.new_context(viewport={'width':w,'height':780}, device_scale_factor=2, is_mobile=True, has_touch=True, color_scheme=scheme)
    pg=await ctx.new_page(); await pg.goto(BASE+url, wait_until='networkidle'); await pg.wait_for_timeout(800)
    h=await pg.evaluate('document.documentElement.scrollHeight'); ims=[]
    for i,y in enumerate(range(0,h,700)):
      if i>=nmax: break
      await pg.evaluate(f'window.scrollTo(0,{y})'); await pg.wait_for_timeout(900)
      f=f'/tmp/v_{nom}_{w}_{scheme}_{i}.png'; await pg.screenshot(path=f); ims.append(Image.open(f))
    await b.close()
  sc=0.5; cw=int(ims[0].width*sc); ch=int(ims[0].height*sc); per=8
  for k in range(0,len(ims),per):
    grp=ims[k:k+per]; out=Image.new('RGB',(len(grp)*(cw+10),ch),(255,0,255))
    for i,im in enumerate(grp): out.paste(im.resize((cw,ch)),(i*(cw+10),0))
    out.save(f'/home/claude/audit/v_{nom}_{w}_{scheme}_{k//per}.png')
  print(nom, w, 'vues', len(ims), 'hauteur', h)
u,n,w,s=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
asyncio.run(main(u,n,w,s))
