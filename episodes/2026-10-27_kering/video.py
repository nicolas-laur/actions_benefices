"""Kering (Gucci) : boutique de luxe pleine, défilé, galerie déserte à Shanghai, boutique vide, bureau de direction.
Mister Coin commence en tenue normale, sort du champ à la fin de la boutique et revient en bling-bling au défilé (surprise).
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from mister_coin import MisterCoin, silences
FPS = int(os.environ.get('FPS', 60)); NB = ' '
INK = '1E160C'; RED = 'C8372D'; RED2 = 'FF9A8A'; GREEN = '2DB36F'; WHITE = 'FFFFFF'; PAPER = 'FFFCF6'; GOLD = 'B8892E'; GOLD2 = 'F2D28B'; DARK = '17120B'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 77,0 s) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(intro=0.0, mille=1.19, valent=6.05, prog=8.68, luxe=9.96, y2015=12.36, michele=14.2, logos=17.47, monde=20.51, stars=21.91,
         y2021=23.95, record=27.31, mais=28.86, chine=32.28, discret=33.71, ventes=36.57, md10=38.37, md6=40.67, plus40=42.79,
         change=44.92, demeo=46.18, demna=49.09, oct23=52.08, gucci6=54.85, chute16=57.54, resultat=60.71, alors=64.12, promet=67.23,
         instant=71.1, toi=74.19, parier=74.86, end=78.4)
DUR = T['end']
CAPS = [(T['intro'], "Bonjour à tous !"), (T['mille'], "Mille euros placés dans Kering, la maison mère de Gucci, au sommet d'août 2021,"),
        (T['valent'], "n'en valent plus que [215] aujourd'hui."), (T['prog'], "Aujourd'hui au programme :"), (T['luxe'], "le luxe qui [ne fait plus rêver]."),
        (T['y2015'], "Retour en [2015]."), (T['michele'], "Gucci confie ses collections à [Alessandro Michele]."),
        (T['logos'], "[Logos géants], couleurs, excentricité :"), (T['monde'], "tout le monde veut du Gucci,"), (T['stars'], "des stars [aux réseaux sociaux]."),
        (T['y2021'], "En août 2021, l'action Kering atteint son record :"), (T['record'], "[827 euros]."),
        (T['mais'], "Mais à force d'être partout, Gucci finit [par lasser]."), (T['chine'], "Les clients chinois [freinent],"),
        (T['discret'], "et la mode passe au [luxe discret], sans logo."), (T['ventes'], "Les ventes de Gucci [s'effondrent] :"),
        (T['md10'], "[10 milliards et demi] d'euros en 2022,"), (T['md6'], "[6 milliards] en 2025."), (T['plus40'], "Plus de [40 %] envolés."),
        (T['change'], "Kering [change tout] :"), (T['demeo'], "un nouveau patron, [Luca de Meo], venu de Renault,"),
        (T['demna'], "et un nouveau directeur artistique chez Gucci, [Demna]."), (T['oct23'], "Mais le 23 octobre, [nouvelle déception] :"),
        (T['gucci6'], "les ventes de Gucci reculent encore de [6 %],"), (T['chute16'], "et l'action chute de [16 %] en une seule journée."),
        (T['resultat'], "Résultat : [−78 %] depuis le sommet."), (T['alors'], "Alors, [affaire en or] ou [piège à touristes] ?"),
        (T['promet'], "Le nouveau patron promet de [doubler la rentabilité] d'ici la fin de la décennie."),
        (T['instant'], "Mais pour l'instant, Gucci [n'a pas retrouvé son éclat]."), (T['toi'], "Et toi,"),
        (T['parier'], "tu [parierais] sur le retour de Gucci à ce prix-là ?")]
HL = {T['valent']: RED, T['luxe']: RED, T['y2015']: GOLD, T['michele']: GOLD, T['logos']: GOLD, T['stars']: GOLD, T['record']: GREEN,
      T['mais']: RED, T['chine']: RED, T['discret']: GOLD, T['ventes']: RED, T['md10']: GOLD, T['md6']: RED, T['plus40']: RED, T['change']: GOLD,
      T['demeo']: GOLD, T['demna']: GOLD, T['oct23']: RED, T['gucci6']: RED, T['chute16']: RED, T['resultat']: RED, T['alors']: GOLD,
      T['promet']: GREEN, T['instant']: RED, T['parier']: GOLD}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1060, size=44, a=1):
    """zone sûre Réels / TikTok / Shorts : au-dessus de l'interface du bas (≥ 1500 px) et loin des icônes de droite (x > 950)"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '120607', .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- éléments graphiques ----------
def card(c, x, y, w, h, a=1, accent=RED, tilt=0.0, dark=False):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt)
    rr(c, -w/2+6, -h/2+10, w, h, 22); col(c, '000000', .3*a); c.fill()
    rr(c, -w/2, -h/2, w, h, 22); col(c, DARK if dark else PAPER, .95*a); c.fill()
    rr(c, -w/2, -h/2, 12, h, 6); col(c, accent, a); c.fill()
    c.restore()
def big(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0, edge=WHITE):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s)
    c.move_to(-ext.x_advance/2+5, size*.36+7); c.text_path(s); col(c, '000000', .35*a); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(12); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, edge, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def tag(c, s, x, y, color, a=1, size=30, fg=WHITE):
    if a <= 0: return
    w = tw(c, s, 'xb', size, 2)+56; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, color, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=16)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
EMO = []
def put_emoji(cv, ch, x, y, size, k, out=None):
    if k > 0: EMO.append((ch, x, y, size, k, out))
def draw_emoji(cv, ch, x, y, size, k, out=None):
    if k <= 0 or not os.path.exists(EMOJI_FONT): return
    s = back(k/.35, 2.2)
    if out is not None: s *= 1-ease((out)/.25) if out > 0 else 1
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))

# ---------- décors ----------
@functools.lru_cache(maxsize=8)
def base(name):
    im = Image.open(f'{D}/decors/{name}.jpg').convert('RGB')
    im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS); x = (im.width-W)//2
    return im.crop((x, 0, x+W, H))
def rng_at(t, k): return np.random.default_rng(int(t*FPS)*7919+k)
BAGS = [(270, 648), (432, 670), (567, 707), (270, 810), (553, 850), (430, 905)]
SPOTS = [(135, 490), (365, 495), (470, 495), (580, 495), (700, 495), (790, 490), (1000, 490)]
EIFFEL = []
AUDIENCE = [(x, y) for y in range(930, 1420, 70) for x in list(np.linspace(40-y*.0, 380-(y-930)*.25, 5))+list(np.linspace(700+(y-930)*.25, 1050, 5))]
def sparkle(d, x, y, r, a):
    d.line((x-r, y, x+r, y), fill=(255, 255, 240, a), width=3); d.line((x, y-r, x, y+r), fill=(255, 255, 240, a), width=3)
    d.ellipse((x-r*.25, y-r*.25, x+r*.25, y+r*.25), fill=(255, 255, 255, a))
@functools.lru_cache(maxsize=1)
def paris_lights():
    a = np.asarray(base('bureau')).astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; yy, xx = np.mgrid[0:H, 0:W]
    win = (((xx > 28) & (xx < 228)) | ((xx > 862) & (xx < 1080))) & (yy > 880) & (yy < 1130)
    m = (np.clip((R-150)/60, 0, 1)*np.clip((R-B)/40, 0, 1)*win).astype(np.float32)
    rng = np.random.default_rng(8); cells = rng.uniform(0, 6.28, (H//6+1, W//6+1)).astype(np.float32)
    return m, cells[(yy//6).astype(int), (xx//6).astype(int)]
def _eiffel():
    a = np.asarray(base('bureau')).astype(np.int32); pts = []
    rng = np.random.default_rng(11)
    for _ in range(4000):
        y = rng.uniform(752, 935); half = 3+(y-752)/183*44; x = rng.uniform(941-half, 941+half)
        R, G, B = a[int(y), int(x)]
        if R > 150 and R-B > 50: pts.append((x, y))
        if len(pts) >= 140: break
    return pts
eiffel_pts = functools.lru_cache(maxsize=1)(_eiffel)
def decor(name, t):
    im = base(name).copy().convert('RGBA'); lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
    if name == 'boutique':
        # rayon de soleil qui glisse sur le marbre
        x0 = 1000-((t*90) % 900); sun = Image.new('L', (W, H), 0)
        ImageDraw.Draw(sun).polygon([(x0, 1150), (x0+260, 1150), (x0-60, 1920), (x0-420, 1920)], fill=70); lay.paste((255, 240, 205, 255), (0, 0), sun.filter(ImageFilter.GaussianBlur(40)))
        for i, (x, y) in enumerate(BAGS):                      # éclats sur les sacs
            ph = (t*.7+i*.37) % 1
            if ph < .25: sparkle(d, x+30, y-20, 24*math.sin(math.pi*ph/.25), int(230*math.sin(math.pi*ph/.25)))
    elif name == 'defile':
        for k, (x, y) in enumerate(SPOTS):                      # projecteurs qui balaient
            ang = .35*math.sin(t*.9+k*1.3); L = 1350; w = 170
            p = [(x, y), (x+math.sin(ang)*L-w, y+math.cos(ang)*L), (x+math.sin(ang)*L+w, y+math.cos(ang)*L)]
            beam = Image.new('L', (W, H), 0); ImageDraw.Draw(beam).polygon(p, fill=40); lay.paste((255, 230, 180, 255), (0, 0), beam.filter(ImageFilter.GaussianBlur(25)))
        rng = rng_at(t, 1)                                      # flashs photo qui crépitent
        for k in range(len(AUDIENCE)):
            if rng.random() < .012:
                x, y = AUDIENCE[k]; x += rng.uniform(-30, 30); r = rng.uniform(14, 24); g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((x-r, y-60-r, x+r, y-60+r), fill=150)
                lay.paste((255, 250, 235, 255), (0, 0), g.filter(ImageFilter.GaussianBlur(r*.5))); sparkle(d, x, y-60, r*.6, 170)
        rng2 = np.random.default_rng(5)                         # paillettes dorées qui tombent
        for k in range(70):
            x0, y0, v = rng2.uniform(0, W), rng2.uniform(0, H), rng2.uniform(60, 140); x = x0+25*math.sin(t*2+k); y = (y0+v*t) % H
            d.rectangle((x-3, y-3, x+3, y+3), fill=(255, 220, 140, int(170+80*math.sin(t*9+k))))
    elif name == 'shanghai':
        f = 1-.38*inout((t-T['mais']-.8)/5.5)                  # la galerie s'assombrit à mesure que les clients disparaissent
        im = ImageEnhance.Brightness(im.convert('RGB')).enhance(f).convert('RGBA'); d = ImageDraw.Draw(lay)
        for x0 in (378, 620):                                   # marches d'escalator qui défilent
            for i in range(12):
                y = 1110-((i*28+t*45) % 330); xx = x0+(1110-y)*.0; d.line((xx+8, y, xx+74, y), fill=(255, 245, 225, 70), width=2)
        rng = np.random.default_rng(9)                          # lumières de la ville qui scintillent derrière la verrière
        for k in range(40):
            x, y = rng.uniform(390, 690), rng.uniform(560, 800)
            if math.sin(t*rng.uniform(2, 6)+k) > .6: d.ellipse((x-3, y-3, x+3, y+3), fill=(255, 220, 160, 200))
    elif name == 'boutique_vide':
        f = 1-.22*clamp((t-T['ventes'])/6); im = ImageEnhance.Brightness(im.convert('RGB')).enhance(f).convert('RGBA')
        for k in range(26):                                     # pluie sur la vitre
            x = 1000+((k*37) % 80); y = ((k*211+t*420) % 900)+420; d.line((x, y, x+2, y+26), fill=(210, 220, 235, 110), width=2)
        ang = .45*math.sin(t*2.2); px, py = 480, 905; L = 70           # étiquette de prix qui se balance seule
        ex, ey = px+L*math.sin(ang), py+L*math.cos(ang); d.line((px, py, ex, ey), fill=(90, 70, 40, 255), width=3)
        tagp = Image.new('RGBA', (110, 60), 0); dt = ImageDraw.Draw(tagp); dt.rounded_rectangle((0, 0, 109, 59), 10, fill=(250, 244, 230, 255), outline=(150, 120, 60, 255), width=3)
        dt.line((22, 30, 88, 30), fill=(200, 60, 50, 255), width=5)
        tg = tagp.rotate(math.degrees(-ang), expand=True, resample=Image.BICUBIC); lay.alpha_composite(tg, (int(ex-tg.width/2), int(ey)))
        g = clamp((t-T['ventes']-2)/1.5)                         # le réverbère s'allume dehors
        if g > 0:
            lamp = Image.new('L', (W, H), 0); ImageDraw.Draw(lamp).ellipse((1010, 690, 1090, 770), fill=int(200*g)); lay.paste((255, 210, 140, 255), (0, 0), lamp.filter(ImageFilter.GaussianBlur(20)))
    elif name == 'bureau':
        m, tw_ = paris_lights()                                 # fenêtres de Paris qui s'allument et s'éteignent
        a = np.asarray(im).astype(np.float32); k = np.sin(tw_+t*(1.5+tw_*.35))
        a[..., :3] *= (1+m*(.55*np.clip(k, 0, 1)-.35*np.clip(-k, 0, 1)))[..., None]
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(lay)
        g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((140, 800, 225, 900), fill=int(90+60*math.sin(t*1.3)))   # Sacré-Cœur qui rayonne
        lay.paste((255, 235, 200, 255), (0, 0), g.filter(ImageFilter.GaussianBlur(22)))
        clip = Image.new('L', (W, H), 0); ImageDraw.Draw(clip).rectangle((862, 600, 1080, 1195), fill=255)   # phare de la tour Eiffel qui tourne
        beam = Image.new('L', (W, H), 0); db = ImageDraw.Draw(beam)
        for off in (0, math.pi):
            ang = t*1.1+off; L = 900; w = .045
            if math.cos(ang) > -.2:
                db.polygon([(941, 748), (941+L*math.sin(ang-w), 748-L*.18*math.cos(ang)), (941+L*math.sin(ang+w), 748-L*.18*math.cos(ang)+40)], fill=int(70*max(0, math.cos(ang))))
        beam = Image.composite(beam.filter(ImageFilter.GaussianBlur(6)), Image.new('L', (W, H), 0), clip); lay.paste((255, 245, 215, 255), (0, 0), beam)
        rng = rng_at(t, 3)                                      # scintillement de la tour Eiffel
        for (x, y) in eiffel_pts():
            if rng.random() < .3:
                r = rng.uniform(1.5, 3.2); d.ellipse((x-r*2, y-r*2, x+r*2, y+r*2), fill=(255, 255, 255, 60)); d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 250, 255))
        for k in range(5):
            u = ((t*.25+k/5) % 1); x = lerp(1075, 1010, u); y = lerp(1195, 1110, u); d.ellipse((x-4, y-3, x+4, y+3), fill=(255, 240, 200, 230))
    im = im.convert('RGBA'); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)) if name != 'defile' else lay)
    return im.convert('RGB')
def camera(im, t, t0, t1, z0=1.0, z1=1.05, cx=540, cy=900):
    u = clamp((t-t0)/max(.1, t1-t0)); u = u*u*(3-2*u); z = z0+(z1-z0)*u
    w, h = W/z, H/z; box = (cx-w*cx/W, cy-h*cy/H, cx-w*cx/W+w, cy-h*cy/H+h)
    return im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
def atmosphere(im, t, seed=3):
    k = 1+.018*math.sin(t*1.7)+.008*math.sin(t*5.3)
    im = ImageEnhance.Brightness(im).enhance(k)
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay); rng = np.random.default_rng(seed)
    for i in range(60):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H*.75), rng.uniform(6, 18)
        x = (x0+sp*t+12*math.sin(t*.6+i)) % W; y = (y0+6*math.sin(t*.9+i*1.3)) % H; r = rng.uniform(1, 2.4)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 238, 205, int(rng.uniform(30, 90))))
    im = im.convert('RGBA'); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.8))); return im
def reflection(char_layer, floor_y, a=.16):
    r = char_layer.transpose(Image.FLIP_TOP_BOTTOM)
    r = r.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, (H-2*floor_y)), Image.BICUBIC)
    al = np.asarray(r.getchannel('A')).astype(np.float32)
    fade = np.clip(1-(np.arange(H)-floor_y)/240, 0, 1)[:, None]; al *= fade*a; al[:int(floor_y)] = 0
    r.putalpha(Image.fromarray(al.astype(np.uint8))); return r.filter(ImageFilter.GaussianBlur(2.5))

# ---------- écran du bureau : habillage façon chaîne d'info financière ----------
SX0, SY0, SX1, SY1 = 268, 618, 800, 950
CX = (SX0+SX1)/2
def screen_bg(c, t, a, ticker=True):
    g = cairo.LinearGradient(0, SY0, 0, SY1); g.add_color_stop_rgba(0, .09, .07, .05, .97*a); g.add_color_stop_rgba(1, .02, .02, .02, .97*a)
    rr(c, SX0, SY0, SX1-SX0, SY1-SY0, 6); c.set_source(g); c.fill()
    c.set_line_width(1); col(c, GOLD2, .06*a)
    for x in range(SX0+30, SX1, 38): c.move_to(x, SY0+44); c.line_to(x, SY1-36); c.stroke()
    rr(c, SX0, SY0, SX1-SX0, 40, 6); col(c, '2A2014', a); c.fill()                       # bandeau du haut
    text(c, "KERING · EURONEXT PARIS", SX0+18, SY0+21, 'xb', 17, GOLD2, 'l', a, 2)
    on = (t*1.6) % 1 < .6; c.arc(SX1-108, SY0+20, 6, 0, 6.3); col(c, RED, a*(1 if on else .3)); c.fill()
    text(c, "EN DIRECT", SX1-96, SY0+21, 'xb', 16, WHITE, 'l', a, 1)
    if not ticker: return
    rr(c, SX0, SY1-34, SX1-SX0, 34, 6); col(c, RED, .9*a); c.fill()                          # bandeau défilant du bas
    msg = "   KERING −16,6 % SUR LA SÉANCE DU 23 OCTOBRE   ·   GUCCI −6 % AU 3E TRIMESTRE   ·   −78 % DEPUIS LE RECORD DE 2021   ·"
    c.save(); c.rectangle(SX0, SY1-34, SX1-SX0, 34); c.clip()
    w = tw(c, msg, 'xb', 17, 1); x = SX1-((t*90) % (w+SX1-SX0))
    for k in (0, 1): text(c, msg, x+k*w, SY1-16, 'xb', 17, WHITE, 'l', a, 1)
    c.restore()
def arrow_down(c, x, y, s, a, color=RED):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-14, -30); c.line_to(14, -30); c.line_to(14, 2); c.line_to(30, 2); c.line_to(0, 34); c.line_to(-30, 2); c.line_to(-14, 2); c.close_path()
    col(c, color, a); c.fill(); c.restore()
def sScreen(c, cv, t):
    a = ease((t-T['oct23'])/.4)
    if a <= 0: return
    screen_bg(c, t, a, t < T['toi']-.1)
    if t < T['resultat']-.1:
        text(c, "23 OCTOBRE 2026", CX, SY0+72, 'a', 38, WHITE, 'c', a)
        kg = t-T['gucci6']
        if kg > 0:
            rr(c, SX0+24, SY0+102, 230, 120, 12); col(c, '241A10', ease(kg/.3)); c.fill()
            text(c, "VENTES GUCCI", SX0+139, SY0+126, 'xb', 18, GOLD2, 'c', ease(kg/.3), 2); text(c, "3E TRIMESTRE", SX0+139, SY0+146, 'b', 15, WHITE, 'c', ease(kg/.3))
            text(c, "−6 %", SX0+139, SY0+188, 'a', 52, RED2, 'c', ease((kg-.2)/.3))
        kc = t-T['chute16']
        if kc > 0:
            u = ease(kc/.3); rr(c, SX0+268, SY0+102, 240, 120, 12); col(c, '3A0E0A', u); c.fill()
            text(c, "ACTION KERING", SX0+388, SY0+126, 'xb', 18, GOLD2, 'c', u, 2); text(c, "EN UNE SÉANCE", SX0+388, SY0+146, 'b', 15, WHITE, 'c', u)
            text(c, "−16,6 %", SX0+388, SY0+188, 'a', 52, RED2, 'c', ease((kc-.3)/.3))
            text(c, "213,50 €  →  178,12 €", CX, SY0+255, 'xb', 24, WHITE, 'c', ease((kc-1)/.3), 1)
        return
    if t < T['alors']-.1:
        k = t-T['resultat']
        text(c, "DEPUIS LE RECORD", SX0+30, SY0+72, 'xb', 20, GOLD2, 'l', a, 2)
        h1 = 140*inout(k/.8); h2 = 140*178.12/826.72*inout((k-.6)/.8); base_y = SY1-62
        for x, h, cl, lab, val in ((SX0+60, h1, GOLD, "13 AOÛT 2021", "826,72 €"), (SX0+200, h2, RED, "23 OCT. 2026", "178,12 €")):
            if h <= 1: continue
            rr(c, x, base_y-h, 100, h, 8); col(c, cl, a); c.fill()
            text(c, val, x+50, base_y-h-16, 'a', 26, WHITE, 'c', a); text(c, lab, x+50, base_y+14, 'xb', 13, GOLD2, 'c', a, 1)
        kb = k-1.2
        if kb > 0: big(c, "−78 %", SX0+405, SY0+150, 84, RED, ease(kb/.25), lerp(1.4, 1, back(kb/.45)))
        if kb > .5: text(c, "1 000 € → 215 €", SX0+405, SY0+225, 'xb', 22, WHITE, 'c', ease((kb-.5)/.3), 1)
        return
    if t < T['toi']-.1:
        k = t-T['alors']
        rr(c, SX0+24, SY0+56, 235, 70, 12); col(c, '2A2010', ease(k/.3)); c.fill(); text(c, "AFFAIRE EN OR ?", SX0+141, SY0+92, 'a', 30, GOLD2, 'c', ease(k/.3))
        rr(c, SX0+273, SY0+56, 235, 70, 12); col(c, '3A0E0A', ease((k-.6)/.3)); c.fill(); text(c, "PIÈGE ?", SX0+390, SY0+92, 'a', 30, RED2, 'c', ease((k-.6)/.3))
        kp = t-T['promet']
        if kp > 0:
            text(c, "OBJECTIF DU NOUVEAU PATRON", SX0+30, SY0+160, 'xb', 18, GOLD2, 'l', ease(kp/.3), 2)
            text(c, "MARGE", SX0+30, SY0+215, 'a', 46, WHITE, 'l', ease((kp-.2)/.3)); big(c, "× 2", SX0+215, SY0+212, 64, GOLD2, ease((kp-.5)/.25), lerp(1.3, 1, back((kp-.5)/.4)), edge=DARK)
            text(c, "D'ICI 2030", SX0+290, SY0+215, 'a', 46, WHITE, 'l', ease((kp-.2)/.3))
        ki = t-T['instant']
        if ki > 0: text(c, "EN ATTENDANT : GUCCI −6 % AU T3", CX, SY0+262, 'xb', 20, RED2, 'c', ease(ki/.3), 1)
        return
    k = t-T['toi']
    big(c, "ET TOI,", CX, SY0+90, 66, WHITE, ease(k/.3), edge=GOLD)
    kb = t-T['parier']
    big(c, "TU PARIERAIS SUR", CX, SY0+165, 48, GOLD2, ease(kb/.3), lerp(1.25, 1, back(kb/.4)), edge=DARK)
    big(c, "LE RETOUR DE GUCCI ?", CX, SY0+228, 48, GOLD2, ease((kb-.15)/.3), lerp(1.25, 1, back((kb-.15)/.4)), edge=DARK)
    if t > T['parier']+.6:
        al = ease((t-T['parier']-.6)/.4)
        c.push_group(); logo_symbol(c, CX-120, SY1-24, 30); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", CX-98, SY1-24, 'b', 22, WHITE, 'l', al)

# ---------- scènes ----------
SCN = [(0, 'boutique'), (T['y2015'], 'defile'), (T['mais'], 'shanghai'), (T['ventes'], 'boutique_vide'), (T['change'], 'bureau')]
def room_at(t):
    r = 'boutique'
    for a, p in SCN:
        if t >= a: r = p
    return r
def room_start(r): return dict((p, a) for a, p in SCN)[r]
def room_end(r):
    starts = [a for a, _ in SCN]+[DUR]; i = [p for _, p in SCN].index(r); return starts[i+1]
def sBoutique(c, cv, t):
    if t < T['prog']-.15:
        big(c, "215 €", 540, 470, 220, RED, 1.0, (1+.1*math.exp(-max(0, t-T['valent'])*8)*(t > T['valent'])))        # chiffre choc dès l'image 0
        card(c, 540, 670, 860, 130, 1.0, GOLD, .01)
        text(c, "1 000 € PLACÉS DANS KERING (GUCCI)", 540, 650, 'xb', 32, INK, 'c', 1.0, 1)
        text(c, "AU SOMMET D'AOÛT 2021", 540, 698, 'xb', 26, RED, 'c', 1.0, 2)
        tag(c, "−78 %", 540, 285, RED, 1.0, 34)
        return
    k = t-T['prog']; card(c, 540, 420, 880, 300, ease(k/.3), GOLD)
    text(c, "AUJOURD'HUI AU PROGRAMME", 540, 330, 'xb', 28, GOLD, 'c', ease(k/.3), 3)
    k2 = t-T['luxe']
    for i, l in enumerate(("LE LUXE QUI NE", "FAIT PLUS RÊVER")):
        text(c, l, 540, 410+i*82, 'a', 76, INK, 'c', ease((k2-i*.15)/.3))
def sDefile(c, cv, t):
    k = t-T['y2015']
    if t < T['y2021']-.1:
        card(c, 540, 290, 860, 210, ease(k/.3), GOLD)
        text(c, "2015", 540, 245, 'a', 76, GOLD, 'c', ease(k/.3))
        km = t-T['michele']
        text(c, "ALESSANDRO MICHELE PREND LA CRÉATION", 540, 335, 'xb', 28, INK, 'c', ease(km/.3), 1)
        kl = t-T['logos']
        for i, (w, dl) in enumerate((("LOGOS GÉANTS", 0), ("COULEURS", .9), ("EXCENTRICITÉ", 1.7))):
            u = kl-dl
            if u > 0: tag(c, w, [300, 760, 540][i], [480, 480, 570][i], [GOLD, RED, '6A4BC4'][i], ease(u/.25), 32)
        ks = t-T['stars']
        if ks > 0:
            card(c, 540, 700, 760, 110, ease(ks/.3), RED, -.012)
            text(c, "TOUT LE MONDE VEUT DU GUCCI", 540, 702, 'xb', 36, INK, 'c', ease(ks/.3), 1)
            put_emoji(cv, '⭐', 200, 640, 70, ks-.3); put_emoji(cv, '📸', 880, 640, 70, ks-.6)
        return
    k = t-T['y2021']
    card(c, 540, 330, 860, 260, ease(k/.3), GREEN)
    text(c, "AOÛT 2021 · RECORD", 540, 260, 'xb', 32, GREEN, 'c', ease(k/.3), 3)
    kr = t-T['record']
    big(c, "826,72 €", 540, 365, 130, GREEN, ease(kr/.25), lerp(1.35, 1, back(kr/.45)))
    text(c, "PLUS HAUTE CLÔTURE DE L'ACTION KERING", 540, 440, 'xb', 22, INK, 'c', ease(k/.3), 1)
def sShanghai(c, cv, t):
    k = t-T['mais']
    card(c, 540, 300, 860, 150, ease(k/.3), RED)
    text(c, "GUCCI PARTOUT…", 540, 280, 'a', 64, INK, 'c', ease(k/.3))
    text(c, "ET ÇA FINIT PAR LASSER", 540, 340, 'xb', 28, RED, 'c', ease((k-1.5)/.3), 2)
    kc = t-T['chine']
    if kc > 0:
        card(c, 540, 500, 760, 110, ease(kc/.3), RED, .012); text(c, "LES CLIENTS CHINOIS FREINENT", 540, 502, 'xb', 34, INK, 'c', ease(kc/.3), 1)
        put_emoji(cv, '🇨🇳', 140, 500, 70, kc-.2)
    kd = t-T['discret']
    if kd > 0:
        card(c, 540, 650, 760, 110, ease(kd/.3), GOLD, -.01); text(c, "MODE : LUXE DISCRET, SANS LOGO", 540, 652, 'xb', 32, INK, 'c', ease(kd/.3), 1)
def sVide(c, cv, t):
    k = t-T['ventes']
    text(c, "GUCCI · VENTES ANNUELLES", 540, 250, 'xb', 30, WHITE, 'c', ease(k/.3), 3)
    rows = [(T['md10'], "2022", 10.487, "10,5 MD€", GOLD), (T['md6'], "2025", 6.0, "6,0 MD€", RED)]
    for i, (t0, yr, v, lab, cl) in enumerate(rows):
        u = inout((t-t0)/.8)
        if u <= 0: continue
        y = 360+i*140; x0 = 230; w = 600*v/10.487*u
        card(c, 540, y, 920, 110, ease((t-t0)/.3), cl)
        text(c, yr, 120, y+2, 'a', 50, INK, 'l', ease((t-t0)/.3))
        rr(c, x0, y-24, max(4, w), 48, 10); col(c, cl, 1); c.fill(); text(c, lab, x0+w+14, y+2, 'a', 40, INK, 'l', ease((t-t0)/.3))
    kp = t-T['plus40']
    if kp > 0: big(c, "−43 %", 540, 700, 150, RED, ease(kp/.25), lerp(1.35, 1, back(kp/.45)), .04)
def sBureau(c, cv, t):
    k = t-T['change']
    if t < T['oct23']-.1:
        card(c, 540, 240, 860, 120, ease(k/.3), GOLD); text(c, "KERING CHANGE TOUT", 540, 242, 'a', 64, INK, 'c', ease(k/.3))
        for i, (t0, h, s_) in enumerate(((T['demeo'], "LUCA DE MEO", "DIRECTEUR GÉNÉRAL (EX-RENAULT)"), (T['demna'], "DEMNA", "DIRECTEUR ARTISTIQUE DE GUCCI"))):
            u = ease((t-t0)/.3)
            if u <= 0: continue
            y = 400+i*165; card(c, 540, y, 760, 140, u, GOLD)
            text(c, h, 540, y-18, 'a', 58, INK, 'c', u); text(c, s_, 540, y+42, 'xb', 24, GOLD, 'c', u, 1)
        return
    sScreen(c, cv, t)
SCENE = {'boutique': sBoutique, 'defile': sDefile, 'shanghai': sShanghai, 'boutique_vide': sVide, 'bureau': sBureau}

# ---------- Mister Coin ----------
PLACES = {'boutique': (560, 1650, .28), 'defile': (540, 1665, .28), 'shanghai': (360, 1665, .28), 'boutique_vide': (720, 1655, .28, True),
          'bureau': (760, 1665, .28, True)}
# changements de tenue en sortie de champ : classique → bling-bling (défilé → Shanghai), bling-bling → classique (boutique vide → bureau)
EXA0, EXA1, ENA0, ENA1 = 28.33, 28.86, 29.0, 30.0
EXB0, EXB1, ENB0, ENB1 = 44.35, 44.92, 45.05, 46.1
BONK = T['resultat']-.45             # gag : l'étiquette « −16 % » lui tombe sur la casquette
def trajet(t):
    if EXA0 <= t < EXA1: u = (t-EXA0)/(EXA1-EXA0); return (lerp(540, 1350, u*u), 1665, .28, False, 0, 1.0)
    if EXA1 <= t < ENA0 or EXB1 <= t < ENB0: return (-2000, 1650, .28, False, 0, 0.0)
    if ENA0 <= t < ENA1: u = ease((t-ENA0)/(ENA1-ENA0)); return (lerp(-300, 360, u), 1665, .28, False, 0, 1.0-u*.6)
    if EXB0 <= t < EXB1: u = (t-EXB0)/(EXB1-EXB0); return (lerp(720, -350, u*u), 1655, .28, True, 0, 1.0)
    if ENB0 <= t < ENB1: u = ease((t-ENB0)/(ENB1-ENB0)); return (lerp(1380, 760, u), 1665, .28, True, 0, 1.0-u*.6)
    return None
SIL = [(a, b) for a, b in silences(VOICE, min_s=.25)]
def bling_actions(t0, t1):
    """bouche greffée qui parle ; dans les silences, les dessins d'origine (frime, puis dépité)"""
    acts = [(t0, t0+.9, 'bling_salut')]; cur = t0+.9
    for a, b in SIL:
        if a < cur or a >= t1: continue
        b = min(b, t1); p = 'bling_frime' if a < T['chine'] else 'bling_depite'
        if a > cur: acts.append((cur, a, 'bling_salut_parle' if cur < T['ventes'] else 'bling_depite_parle'))
        acts.append((a, b, p)); cur = b
    if cur < t1: acts.append((cur, t1, 'bling_depite_parle'))
    return acts
ACTIONS = ([(6.05, 8.05, 'souci'), (8.05, 8.68, 'inquiet'), (8.9, 9.9, 'point'), (17.03, 17.47, 'ravi'), (20.6, 21.6, 'thumb'), (23.41, 23.95, 'ravi'),
            (27.05, 27.31, 'joie')] + bling_actions(ENA0, EXB1) +
           [(51.61, 52.08, 'inquiet'), (52.08, 60.27, 'souci'), (60.27, 60.71, 'abattu'), (60.71, 63.6, 'souci'), (63.61, 64.12, 'abattu'),
            (67.4, 68.6, 'point'), (70.67, 71.1, 'inquiet'), (71.1, 73.6, 'souci'), (74.9, 76.4, 'point')])
MC = MisterCoin(VOICE, PLACES, 'boutique', actions=ACTIONS, trajet=trajet,
                sauts_de_place=[(T['y2015']-.25, 'defile'), (EXA1+.02, 'shanghai'), (T['ventes']-.25, 'boutique_vide'), (EXB1+.02, 'bureau')],
                coucous=[(.1, 1.0), (ENB1-.2, ENB1+.8)], petits_sauts=[T['record']+.1],
                bulles=[(T['stars']+.1, T['stars']+1.6, "Je suis une star !", 'droite'),
                        (T['discret']+.2, T['discret']+1.9, "Discret, moi ?", 'droite'),
                        (T['demna']+.15, T['demna']+1.9, "Retour au classique !", 'gauche'),
                        (BONK+.45, BONK+1.9, "Aïe !", 'gauche')])

def room_frame(r, t):
    cy = 780 if r == 'bureau' else 950
    return camera(decor(r, t), t, room_start(r), room_end(r), 1.0, 1.07, 540, cy)
def bonk_tag(cv, t):
    """étiquette de prix rouge « −16 % » qui tombe du plafond et rebondit sur Mister Coin"""
    u = t-BONK
    if not (-.05 < u < 1.6): return
    x, fy = PLACES['bureau'][:2]; top = fy-560
    if u < .35: y = lerp(-150, top, (u/.35)**2); ang = 0
    else: v = u-.35; y = top-260*v+600*v*v; x = x-260*v; ang = -v*3
    if y > H: return
    s, c = surface(); c.save(); c.translate(x, y); c.rotate(ang)
    rr(c, -110, -50, 220, 100, 18); col(c, RED, 1); c.fill(); c.arc(-80, 0, 10, 0, 6.3); col(c, WHITE, 1); c.fill()
    text(c, "−16 %", 15, 4, 'a', 56, WHITE, 'c', 1); c.restore(); cv.alpha_composite(to_img(s))
def frame(t):
    r = room_at(t); ts = room_start(r)
    bg = room_frame(r, t)
    if r != 'boutique' and t-ts < .5:
        prev = [p for a, p in SCN if a < ts][-1]; u = inout((t-ts)/.5)
        old = room_frame(prev, t); cv = Image.new('RGB', (W, H)); cv.paste(old, (int(-W*u), 0)); cv.paste(bg, (int(W*(1-u)), 0)); bg = cv
    cv = bg.convert('RGBA')
    EMO.clear(); s, c = surface(); SCENE[r](c, cv, t); cv.alpha_composite(to_img(s))
    for e in EMO: draw_emoji(cv, *e)
    ch = MC.layer(t)
    if r in ('boutique', 'shanghai', 'boutique_vide', 'bureau'): cv.alpha_composite(reflection(ch, PLACES[r][1], .14))
    cv.alpha_composite(ch)
    bonk_tag(cv, t)
    cv = atmosphere(cv, t)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

FLASH_T = []
def events():
    ev = [(0.0, 'swish'), (T['valent'], 'impact'), (T['prog'], 'swish'), (EXA0, 'whoosh'), (ENA0+.1, 'tadaa'), (EXB0, 'whoosh'), (T['y2015'], 'swish'),
          (T['logos'], 'pop'), (T['logos']+.9, 'pop'), (T['logos']+1.7, 'pop'), (T['stars'], 'glint'), (T['y2021'], 'swish'), (T['record'], 'coins'),
          (T['mais'], 'swish'), (T['mais']+1.0, 'thud'), (T['chine'], 'pop'), (T['chine']+.3, 'thud'), (T['discret'], 'pop'), (T['ventes'], 'trans'),
          (T['md10'], 'tick'), (T['md6'], 'crash'), (T['plus40'], 'impact'), (T['change'], 'swish'), (T['demeo'], 'pop'), (T['demna'], 'pop'),
          (T['oct23'], 'neon'), (T['gucci6'], 'pop'), (T['chute16']+.3, 'crash'), (BONK+.35, 'bonk'), (T['resultat']+.4, 'impact'), (T['resultat'], 'low'),
          (T['alors'], 'swish'), (T['promet'], 'glint'), (T['toi'], 'swish'), (T['parier'], 'pop'), (T['parier']+.6, 'click')]
    ev += [(b[0], 'pop') for b in MC.bulles]
    return sorted(ev)

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
