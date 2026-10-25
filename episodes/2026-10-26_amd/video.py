"""AMD : 1 000 € il y a 5 ans = 4 481 €. Ville-circuit, usine en crise (2015), renaissance (Ryzen), centre de données (IA), écran (trop tard ?).
Mister Coin traverse les décors, brandit une puce, et part à la vitesse de la lumière après les 1 000 milliards (cri « façon Wilhelm » de synthèse).
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from mister_coin import MisterCoin
FPS = int(os.environ.get('FPS', 60)); NB = '\u202f'
INK = '15090A'; RED = 'E8322E'; RED2 = 'FF8A7A'; GREEN = '2DB36F'; WHITE = 'FFFFFF'; PAPER = 'FBF7F6'; GOLD = 'E2A72E'; DARK = '1A0B0C'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 71,2 s + 0,9 s de silence insérés à 50,35 s pour le gag) ----------
VOICE = f'{D}/voice_full.wav'
G = 1.2   # silence inséré à 10,6 s (après « de très loin ») pour le gag de la ville
def S(x): return x+G if x > 10.6 else x
_T = dict(intro=0.0, mille=1.22, valent=4.66, prog=7.27, puce=8.53, gag=10.34, y2015=11.0, tombe=13.92, morte=16.28, patronne=18.43, lisa=20.33,
          mise=22.18, ryzen=23.95, pari=26.28, grignote=27.12, abord=29.9, serveurs=31.36, ia=32.92, oct=35.22, signe=39.42, annee=43.73,
          milliards=46.97, record=50.63, recule=52.75, alors=54.7, ventes=56.19, mais2=59.66, sept=62.51, verdict=65.76, toi=68.92, achet=69.59, end=72.6)
T = {k: S(v) for k, v in _T.items()}
if os.path.exists(f'{D}/timing.json'): T.update(json.load(open(f'{D}/timing.json')))
DUR = T['end']
CAPS = [(T['intro'], "Bonjour à tous !"), (T['mille'], "Mille euros placés dans AMD il y a cinq ans"), (T['valent'], "valent aujourd'hui [4 481 euros]."),
        (T['prog'], "Aujourd'hui au programme :"), (T['puce'], "la puce qui revient [de très loin]."), (T['gag']+.02, ""),
        (T['y2015'], "En 2015, AMD est [au bord du gouffre]."), (T['tombe'], "Son action tombe à [1,62 dollar],"),
        (T['morte'], "et beaucoup la donnent déjà [pour morte]."), (T['patronne'], "Mais une nouvelle patronne vient d'arriver :"),
        (T['lisa'], "[Lisa Su], une ingénieure."), (T['mise'], "Elle mise tout sur une nouvelle puce, [Ryzen], lancée en 2017."),
        (T['pari'], "[Pari gagné] :"), (T['grignote'], "AMD grignote [Intel], son rival historique,"),
        (T['abord'], "d'abord dans les ordinateurs, puis dans [les serveurs]."), (S(32.15), ""), (T['ia'], "Puis arrive [l'intelligence artificielle]."),
        (T['oct'], "En octobre 2025, [OpenAI], le créateur de ChatGPT,"), (T['signe'], "signe [un accord géant] pour équiper ses centres de données avec les puces d'AMD."),
        (T['annee'], "Cette année, l'action a grimpé jusqu'à [+200 %],"), (T['milliards'], "et AMD a dépassé [les 1 000 milliards] de dollars en Bourse."),
        (T['record'], "Mais depuis son record du 6 octobre,"), (T['recule'], "elle a déjà reculé de [20 %]."),
        (T['alors'], "Alors, [trop tard] ?"), (T['ventes'], "Ses ventes dans les centres de données ont [plus que doublé] en un an."),
        (T['mais2'], "Mais l'action vaut près de [22 fois] ses ventes annuelles,"), (T['sept'], "[7 fois plus] que la moyenne des grandes entreprises américaines."),
        (T['verdict'], "Le verdict tombera [le 3 novembre], avec ses résultats."), (T['toi'], "Et toi,"), (T['achet'], "tu [achèterais] AMD à ce prix-là ?")]
HL = {T['valent']: GREEN, T['puce']: RED, T['y2015']: RED, T['tombe']: RED, T['morte']: RED, T['lisa']: RED, T['mise']: RED, T['pari']: GREEN,
      T['grignote']: RED, T['abord']: GREEN, T['ia']: RED, T['oct']: RED, T['signe']: GREEN, T['annee']: GREEN, T['milliards']: GREEN,
      T['recule']: RED, T['alors']: RED, T['ventes']: GREEN, T['mais2']: RED, T['sept']: RED, T['verdict']: RED, T['achet']: RED}
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

# ---------- décors animés ----------
CROP = {'ecran': (2300, 329, 380)}          # écran remonté au-dessus des sous-titres : (hauteur de mise à l'échelle, x, y du recadrage)
@functools.lru_cache(maxsize=8)
def base(name):
    im = Image.open(f'{D}/decors/{name}.jpg').convert('RGB')
    if name in CROP:
        hh, x, y = CROP[name]; im = im.resize((int(im.width*hh/im.height), hh), Image.LANCZOS); im = im.crop((x, y, x+W, y+H))
    else:
        im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS); x = (im.width-W)//2; im = im.crop((x, 0, x+W, H))
    return np.asarray(im).astype(np.float32)
@functools.lru_cache(maxsize=8)
def lights(name):
    """masque des zones lumineuses (néons, pistes, voyants) et carte de phase pour les faire vivre"""
    a = base(name); R, G, B = a[..., 0], a[..., 1], a[..., 2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if name in ('ville', 'renaissance'):          # pistes lumineuses : la lumière circule
        m = np.clip((R-150)/80, 0, 1)*np.clip((R-B-40)/60, 0, 1); ph = (xx*.9+yy*1.3)/70
    elif name == 'crise':                         # tubes blancs qui grésillent
        m = np.clip((R+G+B-600)/120, 0, 1); ph = np.floor(xx/240)*1.7+np.floor(yy/200)*2.3
    else:                                         # voyants rouges des serveurs qui clignotent
        m = np.clip((R-170)/60, 0, 1)*np.clip((R-G-70)/60, 0, 1); rng = np.random.default_rng(2)
        cells = rng.uniform(0, 6.28, (H//18+1, W//18+1)).astype(np.float32); ph = cells[(yy//18).astype(int), (xx//18).astype(int)]
        side = ((xx < 300) | (xx > 790)) if name == 'datacenter' else ((xx < 90) | (xx > 990))
        m = m*side*(yy < (1250 if name == 'datacenter' else 1150))
    return m.astype(np.float32), ph.astype(np.float32)
def decor(name, t):
    a = base(name); m, ph = lights(name)
    if name in ('ville', 'renaissance'): k = .35*np.sin(ph-t*5.0)+1.3*np.maximum(0, np.sin(ph*.5-t*3.2))**10   # paquets de lumière qui filent
    elif name == 'crise':
        fl = (np.sin(ph*13+t*31) > .45).astype(np.float32)*(math.sin(t*2.3) > -.4); k = -.7*fl
    else: k = .75*np.sin(ph+t*(3.0+ph*.4))
    out = a*(1+(m*k)[..., None])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
# ---------- éléments animés bien visibles (ajoutés sur le décor, avant le travelling) ----------
def _h(pts): return [(x*2, y*2) for x, y in pts]          # tracés relevés sur la grille demi-taille
PATHS = {'ville': [_h([(265, 235), (262, 160), (270, 100), (295, 70), (340, 50), (420, 25), (470, 5)]),
                   _h([(240, 960), (212, 860), (207, 760), (240, 675), (330, 600), (420, 540), (500, 470), (540, 440)]),
                   _h([(540, 250), (470, 290), (420, 330), (380, 365)]),
                   _h([(0, 775), (70, 720), (130, 660), (170, 590), (165, 530), (200, 490), (250, 465)])]}
def _along(pts, u):
    d = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]; L = sum(d); s = (u % 1)*L
    for i, di in enumerate(d):
        if s <= di: f = s/di; return pts[i][0]+(pts[i+1][0]-pts[i][0])*f, pts[i][1]+(pts[i+1][1]-pts[i][1])*f
        s -= di
    return pts[-1]
CARS = {k: [(pi, np.random.default_rng(i+7*pi).uniform(0, 1), np.random.default_rng(99+i+7*pi).uniform(.10, .22)*(1 if (i+pi) % 3 else -1))
            for pi in range(len(v)) for i in range(5)] for k, v in PATHS.items()}
SMOKE = {'ville': [(200, 270), (195, 370), (780, 470), (1010, 170)], 'renaissance': [(880, 560), (760, 520)], 'crise': [(900, 760), (160, 900)]}
SPARKS = {'crise': [(860, 610), (300, 280)]}
@functools.lru_cache(maxsize=2)
def fog_tex(seed):
    rng = np.random.default_rng(seed); n = rng.standard_normal((48, 96)).astype(np.float32)
    im = Image.fromarray(((n-n.min())/(n.max()-n.min())*255).astype(np.uint8)).resize((2160, 1080), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    return np.asarray(im).astype(np.float32)/255
def overlay(name, t):
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
    for pi, u0, sp in CARS.get(name, []):                         # petites lumières qui roulent sur les routes
        pts = PATHS[name][pi]; L = sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)); u = u0+t*sp*700/L
        for k in range(10):
            x, y = _along(pts, u-k*.012*(1 if sp > 0 else -1)*700/L)
            r = 13-k*1.0; a = int(240*(1-k/10)); d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 210-k*12, 150-k*12, a))
    for i, (x0, y0) in enumerate(SMOKE.get(name, [])):           # fumée qui monte en volutes
        for k in range(7):
            ph = ((t*.35+k/7+i*.13) % 1); x = x0+40*math.sin(ph*5+i)+ph*60; y = y0-ph*260; r = 25+ph*90
            d.ellipse((x-r, y-r, x+r, y+r), fill=(225, 210, 210, int(70*math.sin(math.pi*ph))))
    for i, (x0, y0) in enumerate(SPARKS.get(name, [])):          # gerbes d'étincelles par saccades
        burst = (math.sin(t*2.1+i*2) > .3)
        if not burst: continue
        rng = np.random.default_rng(int(t*30)+i*1000)
        for k in range(16):
            ph = rng.uniform(0, .6); vx = rng.uniform(-160, 160); x = x0+vx*ph; y = y0+rng.uniform(-60, 40)*ph+500*ph*ph
            d.line((x, y, x-vx*.04, y-12), fill=(255, 230, 160, 230), width=3)
    lay = lay.filter(ImageFilter.GaussianBlur(2.2))
    if name == 'renaissance':                                     # reflet lumineux qui balaie la plaquette de silicium
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((540-195, 910-125, 540+195, 910+125), fill=255)
        sw = Image.new('L', (W, H), 0); xs = 300+((t*.45) % 1.4)*700
        ImageDraw.Draw(sw).polygon([(xs, 700), (xs+70, 700), (xs-80, 1120), (xs-150, 1120)], fill=200)
        sw = Image.composite(sw.filter(ImageFilter.GaussianBlur(18)), Image.new('L', (W, H), 0), m)
        shine = Image.new('RGBA', (W, H), (255, 240, 225, 0)); shine.putalpha(sw); lay.alpha_composite(shine)
    if name in ('datacenter', 'ecran'):                           # brume qui roule au sol
        tex = fog_tex(1); off = int(t*60) % 1080; band = np.roll(tex, -off, axis=1)[:, :W]
        y0 = 1050 if name == 'datacenter' else 1150; hgt = min(H-y0, band.shape[0])
        al = np.zeros((H, W), np.float32); prof = np.sin(np.linspace(0, math.pi, hgt))[:, None]
        al[y0:y0+hgt] = band[:hgt]*prof*120
        fog = Image.new('RGBA', (W, H), (230, 150, 150, 0)); fog.putalpha(Image.fromarray(np.clip(al, 0, 255).astype(np.uint8))); lay.alpha_composite(fog)
    return lay
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
        d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 190, 180, int(rng.uniform(30, 90))))
    im = im.convert('RGBA'); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.8))); return im
def reflection(char_layer, floor_y, a=.16):
    r = char_layer.transpose(Image.FLIP_TOP_BOTTOM)
    r = r.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, (H-2*floor_y)), Image.BICUBIC)
    al = np.asarray(r.getchannel('A')).astype(np.float32)
    fade = np.clip(1-(np.arange(H)-floor_y)/240, 0, 1)[:, None]; al *= fade*a; al[:int(floor_y)] = 0
    r.putalpha(Image.fromarray(al.astype(np.uint8))); return r.filter(ImageFilter.GaussianBlur(2.5))

# ---------- écran (décor « ecran » recadré : dalle noire) ----------
SX0, SY0, SX1, SY1 = 95, 505, 985, 985
def screen_bg(c, a):
    rr(c, SX0, SY0, SX1-SX0, SY1-SY0, 8); col(c, '0D0506', .85*a); c.fill()
    c.set_line_width(1); col(c, RED2, .08*a)
    for x in range(SX0+40, SX1, 60): c.move_to(x, SY0+8); c.line_to(x, SY1-8); c.stroke()
    for y in range(SY0+30, SY1, 50): c.move_to(SX0+8, y); c.line_to(SX1-8, y); c.stroke()
def scanlines(c, t, a):
    y = SY0+((t*140) % (SY1-SY0)); g = cairo.LinearGradient(0, y-40, 0, y+4)
    g.add_color_stop_rgba(0, 1, .4, .35, 0); g.add_color_stop_rgba(1, 1, .4, .35, .10*a); c.rectangle(SX0, y-40, SX1-SX0, 44); c.set_source(g); c.fill()
def bars(c, t, a, t0, rows, vmax, title, fmt):
    """barres horizontales qui poussent : rows = [(libellé, valeur, couleur, délai)]"""
    text(c, title, SX0+40, SY0+44, 'xb', 22, RED2, 'l', .9*a, 2)
    for i, (lab, v, cl, dl) in enumerate(rows):
        u = inout((t-t0-dl)/.7)
        if u <= 0: continue
        y = SY0+120+i*105; x0 = SX0+300; w = (SX1-90-x0)*v/vmax*u
        text(c, lab, SX0+40, y, 'xb', 24, WHITE, 'l', .9*ease((t-t0-dl)/.3), 1)
        rr(c, x0, y-26, max(4, w), 52, 10); col(c, cl, a); c.fill()
        text(c, fmt(v*u), x0+w+14, y, 'a', 40, WHITE, 'l', a*ease((t-t0-dl)/.3))
def sScreen(c, cv, t):
    a = ease((t-T['record'])/.4); screen_bg(c, a); scanlines(c, t, a)
    if t < T['ventes']-.1:
        rows = [("1ER JANV. 2026", 214.16, '7A2A2A', 0), ("RECORD · 6 OCT.", 649.42, GREEN, .5), ("23 OCT. 2026", 516.79, RED, 1.6)]
        bars(c, t, a, T['record']+.1, rows, 649.42, "AMD · ACTION EN DOLLARS (CLÔTURES)", lambda v: f"{v:,.0f} $".replace(',', NB))
        k = t-T['recule']-.3
        if k > 0: big(c, "−20 %", 820, SY1-75, 96, RED, ease(k/.25), lerp(1.35, 1, back(k/.45)), .04)
        return
    if t < T['mais2']-.1:
        k = t-T['ventes']
        text(c, "AMD · VENTES DES CENTRES DE DONNÉES", SX0+40, SY0+44, 'xb', 22, RED2, 'l', .9*a, 2)
        big(c, "+107 %", 540, SY0+215, 150, GREEN, ease(k/.25), lerp(1.3, 1, back(k/.45)))
        text(c, "EN UN AN (2E TRIMESTRE 2026 : 6,7 MILLIARDS $)", 540, SY0+345, 'xb', 26, WHITE, 'c', ease((k-.4)/.3), 1)
        return
    if t < T['verdict']-.1:
        rows = [("AMD", 21.8, RED, 0), ("S&P 500", 3.1, '8C8C8C', 3.0)]
        bars(c, t, a, T['mais2']+.2, rows, 21.8, "PRIX DE L'ACTION / VENTES ANNUELLES", lambda v: f"× {v:.1f}".replace('.', ','))
        k = t-T['sept']
        if k > 0: big(c, "7 FOIS PLUS CHER", 540, SY1-80, 70, RED2, ease(k/.25), lerp(1.3, 1, back(k/.4)))
        return
    if t < T['toi']-.1:
        k = t-T['verdict']
        text(c, "LE VERDICT", 540, SY0+130, 'xb', 34, RED2, 'c', ease(k/.3), 4)
        big(c, "3 NOVEMBRE", 540, SY0+250, 120, WHITE, ease((k-.4)/.25), lerp(1.3, 1, back((k-.4)/.4)), edge=RED)
        text(c, "RÉSULTATS DU 3E TRIMESTRE", 540, SY0+370, 'xb', 28, WHITE, 'c', ease((k-.9)/.3), 2)
        put_emoji(cv, '⏳', 870, SY0+130, 70, k-.6)
        return
    k = t-T['toi']
    big(c, "ET TOI,", 540, SY0+105, 92, WHITE, ease(k/.3), edge=RED)
    kb = t-T['achet']
    big(c, "TU ACHÈTERAIS", 540, SY0+220, 82, RED2, ease(kb/.3), lerp(1.25, 1, back(kb/.4)))
    big(c, "À CE PRIX-LÀ ?", 540, SY0+325, 82, RED2, ease((kb-.15)/.3), lerp(1.25, 1, back((kb-.15)/.4)))
    if t > T['achet']+.4:
        al = ease((t-T['achet']-.4)/.4)
        c.push_group(); logo_symbol(c, 410, SY1-45, 40); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 440, SY1-45, 'b', 26, WHITE, 'l', al)

# ---------- scènes ----------
SCN = [(0, 'ville'), (T['y2015'], 'crise'), (T['mise'], 'renaissance'), (T['ia'], 'datacenter'), (T['record'], 'ecran')]
def room_at(t):
    r = 'ville'
    for a, p in SCN:
        if t >= a: r = p
    return r
def room_start(r): return dict((p, a) for a, p in SCN)[r]
def room_end(r):
    starts = [a for a, _ in SCN]+[DUR]; i = [p for _, p in SCN].index(r); return starts[i+1]
def sVille(c, cv, t):
    if t < T['prog']-.15:
        big(c, "4 481 €", 540, 520, 210, GREEN, 1.0, (1+.1*math.exp(-max(0, t-T['valent'])*8)*(t > T['valent'])))      # chiffre choc dès l'image 0
        card(c, 540, 715, 800, 110, 1.0, GREEN, .012)
        text(c, "1 000 € PLACÉS DANS AMD IL Y A 5 ANS", 540, 717, 'xb', 34, INK, 'c', 1.0, 1)
        tag(c, "+348 %", 540, 330, GREEN, ease((t-T['valent'])/.3), 34)
        return
    k = t-T['prog']; card(c, 540, 420, 880, 300, ease(k/.3))
    text(c, "AUJOURD'HUI AU PROGRAMME", 540, 330, 'xb', 28, RED, 'c', ease(k/.3), 3)
    k2 = t-T['puce']
    for i, l in enumerate(("LA PUCE QUI REVIENT", "DE TRÈS LOIN")):
        text(c, l, 540, 410+i*82, 'a', 76, INK, 'c', ease((k2-i*.15)/.3))
def sCrise(c, cv, t):
    k = t-T['y2015']
    if t < T['patronne']-.1:
        card(c, 540, 330, 860, 200, ease(k/.3), RED)
        text(c, "2015", 540, 285, 'a', 80, RED, 'c', ease(k/.3))
        text(c, "AU BORD DU GOUFFRE", 540, 375, 'xb', 36, INK, 'c', ease((k-.6)/.3), 2)
        kt = t-T['tombe']-.6
        if kt > 0: big(c, "1,62 $", 540, 620, 170, RED, ease(kt/.25), lerp(1.35, 1, back(kt/.45)), -.03)
        km = t-T['morte']-.9
        if km > 0:
            c.save(); c.translate(560, 820); c.rotate(-.1); s_ = lerp(1.5, 1, back(km/.35)); c.scale(s_, s_)
            c.set_line_width(7); col(c, RED, ease(km/.2)); rr(c, -260, -52, 520, 104, 16); c.stroke()
            text(c, "DONNÉE POUR MORTE", 0, 2, 'a', 62, RED, 'c', ease(km/.2)); c.restore()
        return
    kl = t-T['lisa']
    card(c, 540, 380, 860, 250, ease((t-T['patronne'])/.3), RED)
    text(c, "UNE NOUVELLE PATRONNE", 540, 320, 'xb', 30, RED, 'c', ease((t-T['patronne'])/.3), 3)
    text(c, "LISA SU", 540, 405, 'a', 100, INK, 'c', ease(kl/.3))
    text(c, "INGÉNIEURE · PDG DEPUIS OCTOBRE 2014", 540, 475, 'xb', 26, INK, 'c', ease((kl-.6)/.3), 1)
    put_emoji(cv, '🔬', 880, 250, 74, kl-.3)
def sRenai(c, cv, t):
    k = t-T['mise']
    if t < T['pari']-.1:
        card(c, 540, 330, 820, 210, ease(k/.3), RED)
        text(c, "NOUVELLE PUCE", 540, 280, 'xb', 30, RED, 'c', ease(k/.3), 3)
        kr = t-T['ryzen']
        text(c, "RYZEN · 2017", 540, 370, 'a', 92, INK, 'c', ease(kr/.3))
        return
    big(c, "PARI GAGNÉ", 540, 300, 130, GREEN, ease((t-T['pari'])/.25), lerp(1.3, 1, back((t-T['pari'])/.4)))
    kg = t-T['grignote']
    if kg > 0:
        card(c, 540, 500, 800, 110, ease(kg/.3), RED, -.012)
        text(c, "AMD GRIGNOTE INTEL", 540, 502, 'xb', 40, INK, 'c', ease(kg/.3), 2)
    ka = t-T['abord']
    if ka > 0:
        for i, (em, lab, dl) in enumerate((('💻', "ORDINATEURS", 0), ('🗄️', "SERVEURS", T['serveurs']-T['abord']))):
            u = ease((ka-dl)/.3)
            if u <= 0: continue
            x = 330+i*420; card(c, x, 715, 340, 150, u, GREEN)
            text(c, lab, x, 760, 'xb', 28, INK, 'c', u, 2); put_emoji(cv, em, x, 690, 64, ka-dl)
def sData(c, cv, t):
    k = t-T['ia']
    if t < T['annee']-.1:
        if t < T['signe']-.1:
            big(c, "L'IA", 540, 330, 190, RED, ease(k/.25), lerp(1.35, 1, back(k/.45)))
            ko = t-T['oct']
            if ko > 0:
                card(c, 540, 560, 820, 170, ease(ko/.3), RED)
                text(c, "OCTOBRE 2025", 540, 520, 'xb', 30, RED, 'c', ease(ko/.3), 3)
                text(c, "OPENAI (CHATGPT)", 540, 590, 'a', 64, INK, 'c', ease((ko-.3)/.3))
            return
        ks = t-T['signe']
        card(c, 540, 380, 880, 260, ease(ks/.3), GREEN)
        text(c, "ACCORD AVEC OPENAI", 540, 310, 'xb', 32, GREEN, 'c', ease(ks/.3), 3)
        text(c, "6 GIGAWATTS", 540, 395, 'a', 96, INK, 'c', ease((ks-.2)/.3))
        text(c, "DE PUCES AMD (1ERS ENVOIS FIN 2026)", 540, 470, 'xb', 26, INK, 'c', ease((ks-.8)/.3), 1)
        put_emoji(cv, '🤝', 540, 650, 110, ks-1.2)
        return
    ka = t-T['annee']
    big(c, "+203 %", 540, 330, 180, GREEN, ease(ka/.25), lerp(1.35, 1, back(ka/.45)))
    text(c, "DEPUIS JANVIER, AU RECORD DU 6 OCTOBRE", 540, 470, 'xb', 28, WHITE, 'c', ease((ka-.5)/.3), 1)
    km = t-T['milliards']
    if km > 0:
        card(c, 540, 650, 860, 170, ease(km/.3), GREEN, -.01)
        text(c, "1 000 MILLIARDS $", 540, 630, 'a', 84, INK, 'c', ease(km/.3))
        text(c, "EN BOURSE · 21 SEPTEMBRE 2026", 540, 700, 'xb', 26, INK, 'c', ease((km-.6)/.3), 1)
SCENE = {'ville': sVille, 'crise': sCrise, 'renaissance': sRenai, 'datacenter': sData, 'ecran': sScreen}

# ---------- Mister Coin ----------
PLACES = {'ville': (540, 1650, .28), 'crise': (330, 1655, .28), 'renaissance': (740, 1655, .28, True), 'datacenter': (330, 1665, .28),
          'ecran': (760, 1665, .28, True)}
ACTIONS = [(a if a < 10.6 else S(a), S(b), p) for a, b, p in [
           (6.68, 7.27, 'ravi'), (9.0, 10.3, 'point'), (10.34, 11.6, 'projete'), (11.6, 13.6, 'souci'),
           (13.61, 13.92, 'inquiet'), (13.92, 17.9, 'souci'),
           (17.91, 18.43, 'abattu'), (20.33, 21.6, 'point'), (21.8, 22.18, 'ravi'), (26.28, 27.4, 'thumb'), (32.18, 32.95, 'puce'),
           (35.3, 36.6, 'point'), (43.19, 43.73, 'billets'), (46.79, 46.97, 'ravi'), (50.1, 50.63, 'joie'),
           (53.65, 54.3, 'souci'), (55.6, 56.19, 'inquiet'), (59.24, 59.66, 'ravi'),
           (61.0, 62.27, 'souci'), (65.27, 65.76, 'inquiet'), (68.39, 68.92, 'ravi'), (69.59, 71.0, 'point')]]
ROAD = [(540, 1650), (560, 1450), (600, 1250), (585, 1050), (545, 880), (540, 760)]   # l'autoroute lumineuse jusqu'au processeur central
def road(v):
    v = clamp(v)*(len(ROAD)-1); i = min(int(v), len(ROAD)-2); f = v-i
    return lerp(ROAD[i][0], ROAD[i+1][0], f), lerp(ROAD[i][1], ROAD[i+1][1], f)
GAG0 = T['gag']+.03; GAG1 = GAG0+.25; GAG2 = GAG1+.9; LAND0 = T['y2015']+.05; LAND1 = T['y2015']+.5
def trajet(t):
    """gag de la ville : il vibre, puis il est propulsé sur l'autoroute lumineuse jusqu'au processeur central (il rapetisse au loin),
    et il retombe du ciel dans l'usine de 2015"""
    if GAG0 <= t < GAG1:
        x, y = PLACES['ville'][:2]; return (x+12*math.sin((t-GAG0)*95), y, .28, False, 0, 0.0)
    if GAG1 <= t < GAG2:
        v = ((t-GAG1)/(GAG2-GAG1))**1.6; x, y = road(v); z = .28*(1-v)+.012*v
        return (x, y, z, False, -78, 0.0)
    if GAG2 <= t < LAND0: return (-2000, -2000, .01, False, 0, 0.0)
    if LAND0 <= t < LAND1:
        v = (t-LAND0)/(LAND1-LAND0); x, y = PLACES['crise'][:2]; return (x, lerp(-200, y, v*v), .28, False, 0, 0.0)
    return None
MC = MisterCoin(VOICE, PLACES, 'ville', actions=ACTIONS, trajet=trajet,
                sauts_de_place=[(T['gag']+.1, 'crise'), (T['mise']-.25, 'renaissance'), (T['ia']-.25, 'datacenter'), (T['record']-.25, 'ecran')],
                coucous=[(.1, 1.0)], petits_sauts=[T['pari']+.05, T['milliards']+.6, LAND1-.02],
                bulles=[(T['morte']+.1, T['morte']+1.6, "Même pas mort !", 'droite'),
                        (T['grignote']+.15, T['grignote']+2.0, "Miam, du silicium !", 'gauche'),
                        (T['signe']+.2, T['signe']+2.0, "Je signe où ?", 'droite'),
                        (T['sept']+.2, T['sept']+2.1, "Ça pique un peu…", 'gauche')])

def room_frame(r, t):
    cy = 760 if r == 'ecran' else 950
    im = decor(r, t).convert('RGBA'); im.alpha_composite(overlay(r, t))
    return camera(im.convert('RGB'), t, room_start(r), room_end(r), 1.0, 1.07, 540, cy)
def frame(t):
    r = room_at(t); ts = room_start(r)
    bg = room_frame(r, t)
    if r != 'ville' and t-ts < .5:                  # glissement latéral d'une salle à l'autre
        prev = [p for a, p in SCN if a < ts][-1]; u = inout((t-ts)/.5)
        old = room_frame(prev, t); cv = Image.new('RGB', (W, H)); cv.paste(old, (int(-W*u), 0)); cv.paste(bg, (int(W*(1-u)), 0)); bg = cv
    cv = bg.convert('RGBA')
    EMO.clear(); s, c = surface(); SCENE[r](c, cv, t); cv.alpha_composite(to_img(s))
    for e in EMO: draw_emoji(cv, *e)
    ch = MC.layer(t)
    if r in ('datacenter', 'ecran') and not (GAG0 <= t < LAND1): cv.alpha_composite(reflection(ch, 1665))
    if GAG1 <= t < GAG2+.35:                        # traînée de lumière derrière lui sur l'autoroute
        lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
        v1 = clamp(((t-GAG1)/(GAG2-GAG1)))**1.6; v0 = max(0, v1-.35); fade_ = 1-clamp((t-GAG2)/.35)
        pts = [road(v0+(v1-v0)*i/24) for i in range(25)]
        for i in range(24):
            w_ = 10+90*(1-(v0+(v1-v0)*i/24))*(i/24)**.7
            d.line([pts[i], pts[i+1]], fill=(255, 225, 170, int(235*fade_*(i/24)**.6)), width=max(2, int(w_)))
        cv.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))
    cv.alpha_composite(ch)
    cv = atmosphere(cv, t)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, RED), a=al)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'swish'), (T['valent'], 'impact'), (T['prog'], 'swish'), (T['y2015'], 'swish'), (T['tombe']+.6, 'crash'), (T['morte']+.9, 'thud'),
          (T['patronne'], 'neon'), (T['lisa'], 'pop'), (T['mise'], 'swish'), (T['ryzen'], 'glint'), (T['pari'], 'impact'), (T['grignote'], 'pop'),
          (T['abord'], 'pop'), (T['serveurs'], 'pop'), (T['ia'], 'swish'), (T['ia'], 'riser'), (T['oct'], 'pop'), (T['signe'], 'paid'),
          (T['annee'], 'boom'), (T['milliards'], 'coins'), (GAG1-.05, 'scream'), (GAG1, 'zoom'), (LAND1-.05, 'thud'),
          (T['record'], 'swish'), (T['recule']+.3, 'impact'), (T['recule'], 'low'), (T['ventes'], 'tick'), (T['mais2'], 'tick'), (T['sept'], 'thud'),
          (T['verdict'], 'swish'), (T['toi'], 'swish'), (T['achet'], 'pop'), (T['achet']+.4, 'click')]
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
