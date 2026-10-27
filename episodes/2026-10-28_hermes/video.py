"""Hermès : atelier 1837, avion 1984 (Birkin), salon privé, bibliothèque (famille contre LVMH), salon de Bourse (la chute).
Mister Coin aristocrate en clips Veo (Gemini) détourés.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
FPS = int(os.environ.get('FPS', 60)); NB = ' '
INK = '1E160C'; RED = 'C8372D'; RED2 = 'FF9A8A'; GREEN = '2DB36F'; WHITE = 'FFFFFF'; PAPER = 'FFFCF6'; GOLD = 'B8892E'; GOLD2 = 'F2D28B'; DARK = '17120B'
ORANGE = 'D9772B'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 83,9 s, phrases calées sur les silences) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(intro=0.0, mille=1.22, valent=5.63, prog=7.71, luxe=9.07, y1837=11.76, harnais=14.85, y1984=17.87, patron=20.88, explique=25.3,
         dessine=28.43, birkin=30.25, convoite=31.31, attendre=34.75, envole=37.63, y2010=39.77, quart=42.97, famille=45.75, renonce=49.56,
         record=52.82, trois=56.04, chine=57.61, oct22=59.41, resultat=63.67, alors=67.24, pasvite=69.06, sacs=70.07, chere=74.24,
         trente=76.51, contre=78.73, toi=81.7, achet=82.36, end=84.9)
if os.path.exists(f'{D}/timing.json'): T.update(json.load(open(f'{D}/timing.json')))
DUR = T['end']
CAPS = [(T['intro'], "Bonjour à tous !"), (T['mille'], "Mille euros placés dans Hermès à son sommet de février 2025"),
        (T['valent'], "n'en valent plus que [432] aujourd'hui."), (T['prog'], "Aujourd'hui au programme :"),
        (T['luxe'], "le luxe qu'on croyait [intouchable]."), (T['y1837'], "Tout commence en [1837], à Paris."),
        (T['harnais'], "Thierry Hermès fabrique [des harnais] pour les chevaux."), (T['y1984'], "Un siècle et demi plus tard, en [1984],"),
        (T['patron'], "le patron d'Hermès est assis dans un avion à côté de l'actrice [Jane Birkin]."),
        (T['explique'], "Elle lui explique qu'elle ne trouve [aucun sac] à son goût."), (T['dessine'], "Il lui en dessine un [sur place] :"),
        (T['birkin'], "le sac [Birkin] est né."), (T['convoite'], "Il devient l'objet [le plus convoité] du luxe :"),
        (T['attendre'], "il faut parfois attendre [des années] pour en obtenir un."), (T['envole'], "Et l'action Hermès [s'envole]."),
        (T['y2010'], "En 2010, [LVMH], le géant du luxe,"), (T['quart'], "achète en secret [près d'un quart] de l'entreprise."),
        (T['famille'], "Mais la famille Hermès, qui en détient environ [les deux tiers], fait bloc,"),
        (T['renonce'], "et en 2014, LVMH [doit renoncer]."), (T['record'], "En février 2025, l'action atteint son [record] :"),
        (T['trois'], "près de [3 000 euros]."), (T['chine'], "Puis la Chine [ralentit]."),
        (T['oct22'], "Le 22 octobre, Hermès annonce sa [plus faible croissance] depuis 2020."),
        (T['resultat'], "Résultat : [−57 %] depuis le sommet."), (T['alors'], "Alors, [la fin d'un mythe] ?"), (T['pasvite'], "[Pas si vite]."),
        (T['sacs'], "Ses sacs se vendent toujours très bien : [+10 %] au dernier trimestre."),
        (T['chere'], "Et l'action est devenue [bien moins chère] :"), (T['trente'], "elle vaut aujourd'hui [30 ans] de bénéfices,"),
        (T['contre'], "contre [44] en moyenne depuis 2017."), (T['toi'], "Et toi,"), (T['achet'], "tu [achèterais] Hermès à ce prix-là ?")]
HL = {T['valent']: RED, T['luxe']: GOLD, T['y1837']: GOLD, T['harnais']: ORANGE, T['y1984']: GOLD, T['patron']: GOLD, T['explique']: ORANGE,
      T['dessine']: ORANGE, T['birkin']: ORANGE, T['convoite']: GOLD, T['attendre']: ORANGE, T['envole']: GREEN, T['y2010']: RED, T['quart']: RED,
      T['famille']: GOLD, T['renonce']: GREEN, T['record']: GREEN, T['trois']: GREEN, T['chine']: RED, T['oct22']: RED, T['resultat']: RED,
      T['alors']: GOLD, T['pasvite']: GREEN, T['sacs']: GREEN, T['chere']: GREEN, T['trente']: GOLD, T['contre']: GOLD, T['achet']: ORANGE}
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
def glow(lay, rgb, mask):
    """ajoute une lueur colorée (alpha = masque) en mélange normal, sans assombrir"""
    g = Image.new('RGBA', (W, H), rgb+(0,)); g.putalpha(mask); lay.alpha_composite(g)
def sparkle(d, x, y, r, a):
    d.line((x-r, y, x+r, y), fill=(255, 255, 240, a), width=3); d.line((x, y-r, x, y+r), fill=(255, 255, 240, a), width=3)
    d.ellipse((x-r*.25, y-r*.25, x+r*.25, y+r*.25), fill=(255, 255, 255, a))
def flame(lay, x, y, r, t, k=1.0, seed=0):
    f = .75+.15*math.sin(t*13+seed)+.1*math.sin(t*29+seed*2)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((x-r*f, y-r*f, x+r*f, y+r*f), fill=int(120*k*f))
    glow(lay, (255, 170, 80), m.filter(ImageFilter.GaussianBlur(r*.45)))
@functools.lru_cache(maxsize=1)
def eiffel_pts():
    a = np.asarray(base('bourse')).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = np.zeros(R.shape, bool); m[684:850, 197:262] = True
    m &= (R > 170) & (R-B > 45)
    ys, xs = np.where(m); return list(zip(xs, ys))
def decor(name, t):
    im = base(name).copy().convert('RGBA'); lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
    if name == 'atelier':
        flame(lay, 494, 1015, 260, t)                                       # la lampe à huile vacille
        beam = Image.new('L', (W, H), 0)                                   # rayon de soleil depuis la fenêtre, qui respire
        ImageDraw.Draw(beam).polygon([(20, 500), (260, 480), (760, 1700), (300, 1850)], fill=int(48+16*math.sin(t*.8)))
        glow(lay, (255, 225, 170), beam.filter(ImageFilter.GaussianBlur(50)))
        rng = np.random.default_rng(3)                                    # poussière dans le rayon
        for k in range(55):
            u, v = rng.uniform(0, 1), rng.uniform(0, 1); x = lerp(lerp(30, 250, u), lerp(320, 740, u), v); y = lerp(lerp(500, 480, u), lerp(1840, 1700, u), v)
            x += 20*math.sin(t*.5+k); y = (y-14*t-k*7) % 1400+480
            r = rng.uniform(1.5, 3.5); d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 240, 200, int(rng.uniform(90, 200))))
    elif name == 'avion':
        rng = np.random.default_rng(6)                                    # nuages qui défilent derrière les hublots
        for k, (x0, y0) in enumerate([(30, 760), (95, 760), (150, 755), (205, 750)]):
            for j in range(3):
                cx_ = x0+((t*55+j*40+k*13) % 90)-45; m = Image.new('L', (W, H), 0)
                ImageDraw.Draw(m).ellipse((cx_-22, y0-10+j*12, cx_+22, y0+8+j*12), fill=150)
                glow(lay, (255, 255, 255), m.filter(ImageFilter.GaussianBlur(6)))
        ph = (t*.18) % 1                                                  # bande de soleil qui glisse le long de la cabine
        sw = Image.new('L', (W, H), 0); yy = lerp(1900, 700, ph)
        ImageDraw.Draw(sw).polygon([(0, yy), (1080, yy-120), (1080, yy-40), (0, yy+80)], fill=40); glow(lay, (255, 230, 180), sw.filter(ImageFilter.GaussianBlur(30)))
    elif name == 'salon':
        ph = (t*.45) % 1.6                                                # éclat qui balaie la vitrine et le sac
        if ph < 1:
            xs = lerp(470, 640, ph); sw = Image.new('L', (W, H), 0)
            ImageDraw.Draw(sw).polygon([(xs, 560), (xs+28, 560), (xs-40, 1060), (xs-68, 1060)], fill=110)
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle((440, 560, 660, 1060), fill=255)
            glow(lay, (255, 250, 235), Image.composite(sw.filter(ImageFilter.GaussianBlur(6)), Image.new('L', (W, H), 0), m))
        for k, (x, y) in enumerate([(505, 785), (600, 800), (548, 760)]):
            p = (t*.8+k*.33) % 1
            if p < .22: sparkle(d, x, y, 22*math.sin(math.pi*p/.22), int(240*math.sin(math.pi*p/.22)))
    elif name == 'bibliotheque':
        flame(lay, 81, 1270, 330, t, 1.2, 1)                               # le feu crépite dans la cheminée
        rng = rng_at(t, 2)
        for k in range(6):                                                # étincelles qui montent
            ph = ((t*.9+k/6) % 1); x = 70+30*math.sin(k*2+t)+rng.uniform(-3, 3); y = 1290-ph*170
            d.ellipse((x-3, y-3, x+3, y+3), fill=(255, 190, 90, int(230*(1-ph))))
        for k, (x, y) in enumerate([(915, 470), (950, 455), (985, 470), (950, 500)]):
            p = (t*.6+k*.27) % 1
            if p < .2: sparkle(d, x, y, 16*math.sin(math.pi*p/.2), int(220*math.sin(math.pi*p/.2)))
    elif name == 'bourse':
        pts = eiffel_pts(); rng = rng_at(t, 3)                             # la tour Eiffel scintille (sur la tour seulement), le lustre brille
        for k in rng.choice(len(pts), 14, replace=False):
            x, y = pts[k]; r = rng.uniform(1.4, 2.6)
            d.ellipse((x-r*2, y-r*2, x+r*2, y+r*2), fill=(255, 255, 255, 60)); d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 250, 255))
        for k, (x, y) in enumerate([(470, 250), (540, 300), (610, 250), (540, 200), (500, 330), (580, 330)]):
            p = (t*.7+k*.19) % 1
            if p < .18: sparkle(d, x, y, 20*math.sin(math.pi*p/.18), int(230*math.sin(math.pi*p/.18)))
    im.alpha_composite(lay)
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
# ---------- écran (salon de Bourse) ----------
SX0, SY0, SX1, SY1 = 351, 707, 734, 931
CX = (SX0+SX1)/2
def screen(c, t):
    a = ease((t-T['record'])/.4)
    if a <= 0: return
    rr(c, SX0, SY0, SX1-SX0, SY1-SY0, 4); col(c, '0B0906', .95*a); c.fill()
    rr(c, SX0, SY0, SX1-SX0, 30, 4); col(c, '2A2014', a); c.fill(); text(c, "HERMÈS · EURONEXT PARIS", SX0+12, SY0+16, 'xb', 13, GOLD2, 'l', a, 2)
    if t < T['resultat']:
        text(c, "RECORD · 14 FÉV. 2025", CX, SY0+70, 'xb', 18, GOLD2, 'c', a, 2)
        text(c, "2 957 €", CX, SY0+128, 'a', 58, GREEN, 'c', ease((t-T['trois'])/.3))
        if t > T['oct22']: text(c, "T3 2026 : +4,3 %", CX, SY0+185, 'xb', 22, RED2, 'c', ease((t-T['oct22'])/.3), 1)
    elif t < T['toi']:
        text(c, "DEPUIS LE RECORD", CX, SY0+62, 'xb', 18, GOLD2, 'c', a, 2)
        text(c, "−57 %", CX, SY0+125, 'a', 70, RED, 'c', ease((t-T['resultat'])/.3))
        text(c, "2 957 € → 1 278,50 €", CX, SY0+185, 'xb', 20, WHITE, 'c', ease((t-T['resultat']-.6)/.3), 1)
    else:
        text(c, "ET TOI ?", CX, SY0+95, 'a', 56, WHITE, 'c', ease((t-T['toi'])/.3))
        al = ease((t-T['achet']-.4)/.4)
        c.push_group(); logo_symbol(c, CX-95, SY0+165, 26); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", CX-77, SY0+165, 'b', 19, WHITE, 'l', al)

# ---------- scènes ----------
SCN = [(0, 'atelier'), (T['y1984'], 'avion'), (T['convoite'], 'salon'), (T['y2010'], 'bibliotheque'), (T['record'], 'bourse')]
def room_at(t):
    r = 'atelier'
    for a, p in SCN:
        if t >= a: r = p
    return r
def room_start(r): return dict((p, a) for a, p in SCN)[r]
def room_end(r):
    starts = [a for a, _ in SCN]+[DUR]; i = [p for _, p in SCN].index(r); return starts[i+1]
def two(c, l1, l2, y, k, accent=GOLD, s1=64, s2=28, w=880, c2=None):
    h = 190 if l2 else 120; card(c, 540, y, w, h, ease(k/.3), accent)
    text(c, l1, 540, y-(22 if l2 else 0), 'a', s1, INK, 'c', ease(k/.3))
    if l2: text(c, l2, 540, y+50, 'xb', s2, c2 or accent, 'c', ease((k-.25)/.3), 1)
def sAtelier(c, cv, t):
    if t < T['prog']-.15:
        big(c, "432 €", 540, 470, 220, RED, 1.0, (1+.1*math.exp(-max(0, t-T['valent'])*8)*(t > T['valent'])))     # chiffre choc dès l'image 0
        card(c, 540, 670, 880, 130, 1.0, GOLD, .01)
        text(c, "1 000 € PLACÉS DANS HERMÈS", 540, 650, 'xb', 32, INK, 'c', 1.0, 1)
        text(c, "AU SOMMET DE FÉVRIER 2025", 540, 698, 'xb', 26, RED, 'c', 1.0, 2)
        tag(c, "−57 %", 540, 285, RED, 1.0, 34)
        return
    if t < T['y1837']-.15:
        k = t-T['prog']; card(c, 540, 420, 880, 300, ease(k/.3), GOLD)
        text(c, "AUJOURD'HUI AU PROGRAMME", 540, 330, 'xb', 28, GOLD, 'c', ease(k/.3), 3)
        for i, l in enumerate(("LE LUXE QU'ON CROYAIT", "INTOUCHABLE")):
            text(c, l, 540, 410+i*82, 'a', 72, INK, 'c', ease((t-T['luxe']-i*.15)/.3))
        return
    two(c, "1837 · PARIS", None, 300, t-T['y1837'])
    kh = t-T['harnais']
    if kh > 0: two(c, "THIERRY HERMÈS", "HARNACHEUR : HARNAIS ET SELLES POUR CHEVAUX", 500, kh, ORANGE, 56, 24); put_emoji(cv, '🐎', 900, 380, 90, kh-.3)
def sAvion(c, cv, t):
    k = t-T['y1984']
    two(c, "1984", "UN VOL PARIS → LONDRES", 280, k, GOLD, 80, 26)
    kp = t-T['patron']
    if kp > 0 and t < T['birkin']-.1:
        two(c, "JANE BIRKIN", "ACTRICE ET CHANTEUSE", 500, kp, ORANGE, 60, 24)
        ke = t-T['explique']
        if ke > 0: put_emoji(cv, '👜', 830, 470, 90, ke)
    kb = t-T['birkin']
    if kb > 0: big(c, "LE BIRKIN EST NÉ", 540, 520, 96, ORANGE, ease(kb/.25), lerp(1.3, 1, back(kb/.45)))
def sSalon(c, cv, t):
    k = t-T['convoite']
    two(c, "L'OBJET LE PLUS", "CONVOITÉ DU LUXE", 260, k, GOLD, 58, 34, c2=INK)
    ka = t-T['attendre']
    if ka > 0 and t < T['envole']-.1: tag(c, "DES ANNÉES D'ATTENTE", 540, 450, ORANGE, ease(ka/.3), 32); put_emoji(cv, '⏳', 830, 450, 70, ka-.2)
    ke = t-T['envole']
    if ke > 0: big(c, "L'ACTION S'ENVOLE", 540, 470, 92, GREEN, ease(ke/.25), lerp(1.3, 1, back(ke/.45))); put_emoji(cv, '📈', 540, 600, 90, ke-.3)
def pie3d(c, cx, cy, R, parts, tilt=.45, depth=55, a=1.):
    """camembert en 3D : parts = [(fraction, couleur, décollement)] dans le sens horaire depuis le haut"""
    r = R*tilt; ang = -math.pi/2; sl = []
    for f, colr, ex in parts:
        if f <= 0.001: continue
        a0, a1 = ang, ang+f*2*math.pi; mid = (a0+a1)/2; dx, dy = math.cos(mid)*ex, math.sin(mid)*ex*tilt
        sl.append((a0, a1, colr, dx, dy)); ang = a1
    def P(t_, ox, oy, z=0): return cx+ox+R*math.cos(t_), cy+oy+r*math.sin(t_)+z
    def shade(colr, k): h = colr.lstrip('#'); rgb = [int(h[i:i+2], 16)/255*k for i in (0, 2, 4)]; return rgb
    for a0, a1, colr, dx, dy in sorted(sl, key=lambda s_: -abs(math.cos((s_[0]+s_[1])/2+math.pi/2))):      # côtés (seulement la partie avant)
        lo, hi = max(a0, 0), min(a1, math.pi)
        for off in (0, 2*math.pi):
            l2, h2 = max(a0, off), min(a1, off+math.pi)
            if h2 <= l2: continue
            n = 24; pts = [P(l2+(h2-l2)*i/n, dx, dy) for i in range(n+1)]
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; [c.line_to(p[0], p[1]+depth) for p in pts[::-1]]; c.close_path()
            c.set_source_rgba(*shade(colr, .7), a); c.fill()
        for e in (a0, a1):                                             # faces de coupe visibles quand la part est décollée
            if dx or dy:
                p1 = (cx+dx, cy+dy); p2 = P(e, dx, dy)
                c.move_to(*p1); c.line_to(*p2); c.line_to(p2[0], p2[1]+depth); c.line_to(p1[0], p1[1]+depth); c.close_path()
                c.set_source_rgba(*shade(colr, .55), a); c.fill()
    for a0, a1, colr, dx, dy in sl:                                    # dessus
        c.move_to(cx+dx, cy+dy); n = 40
        for i in range(n+1): c.line_to(*P(a0+(a1-a0)*i/n, dx, dy))
        c.close_path(); c.set_source_rgba(*shade(colr, 1), a); c.fill_preserve()
        c.set_source_rgba(1, 1, 1, .55*a); c.set_line_width(3); c.stroke()
def sBiblio(c, cv, t):
    k = t-T['y2010']; kq = t-T['quart']; kf = t-T['famille']; kr = t-T['renonce']
    lv = .23*inout(kq/.9)*(1-inout(kr/.9)) if kq > 0 else 0          # part de LVMH : monte à 23 %, puis disparaît en 2014
    ex = 46*inout(kq/.6)*(1-inout(kr/.6)) if kq > 0 else 0
    fam_ex = 14*math.sin(min(1, max(0, kf)/.5)*math.pi) if 0 < kf < .5 else 0
    pa = ease(k/.4)
    if pa > 0:
        pie3d(c, 540, 620, 250, [(lv, '#C8372D', ex), (.34-lv, '#8C8577', 0), (.66, '#B8892E', fam_ex)], a=pa)
        big(c, "FAMILLE HERMÈS", 430, 610, 40, WHITE, pa, edge=DARK); big(c, "ENVIRON 2/3", 430, 660, 46, GOLD2, pa, edge=DARK)
        if lv > .01: big(c, f"LVMH : {round(lv*100)} %", 800, 470, 54, 'FF6B5E', ease(kq/.3)*(1-ease(kr/.4)), edge=DARK)
    if t < T['famille']-.1:
        two(c, "2010 · LVMH", "LE GÉANT DU LUXE ACHÈTE EN SECRET", 250, k, RED, 66, 26)
        return
    if t < T['renonce']-.1: two(c, "LA FAMILLE FAIT BLOC", None, 250, kf, GOLD, 58); put_emoji(cv, '🛡️', 880, 160, 70, kf-.6)
    else: two(c, "2014 · LVMH RENONCE", None, 250, kr, GREEN, 58)
def _old_sBiblio(c, cv, t):
    k = t-T['y2010']
    if t < T['famille']-.1:
        two(c, "2010 · LVMH", "LE GÉANT DU LUXE ACHÈTE EN SECRET", 280, k, RED, 70, 26)
        kq = t-T['quart']
        if kq > 0: big(c, "PRÈS D'UN QUART", 540, 500, 96, RED, ease(kq/.25), lerp(1.3, 1, back(kq/.45)))
        return
    kf = t-T['famille']
    two(c, "LA FAMILLE HERMÈS", "ENVIRON LES DEUX TIERS DU CAPITAL", 280, kf, GOLD, 60, 26)
    if kf > 1.2: put_emoji(cv, '🛡️', 880, 200, 80, kf-1.2)
    kr = t-T['renonce']
    if kr > 0: two(c, "2014 · LVMH RENONCE", None, 470, kr, GREEN, 54)
def sBourse(c, cv, t):
    screen(c, t)
    if t < T['chine']-.1:
        two(c, "FÉVRIER 2025", "RECORD HISTORIQUE", 260, t-T['record'], GREEN, 70, 30)
        kt = t-T['trois']
        if kt > 0: big(c, "PRÈS DE 3 000 €", 540, 470, 100, GREEN, ease(kt/.25), lerp(1.3, 1, back(kt/.45)))
        return
    if t < T['resultat']-.1:
        tag(c, "LA CHINE RALENTIT", 540, 230, RED, ease((t-T['chine'])/.3), 34); put_emoji(cv, '🇨🇳', 820, 230, 64, t-T['chine']-.2)
        ko = t-T['oct22']
        if ko > 0: two(c, "22 OCT. 2026", "PLUS FAIBLE CROISSANCE DEPUIS 2020", 430, ko, RED, 64, 26)
        return
    if t < T['alors']-.1:
        kr = t-T['resultat']; big(c, "−57 %", 540, 380, 200, RED, ease(kr/.25), lerp(1.35, 1, back(kr/.45)), .03)
        text(c, "1 000 € AU SOMMET → 432 €", 540, 545, 'xb', 32, WHITE, 'c', ease((kr-.6)/.3), 1)
        return
    if t < T['sacs']-.1:
        ka = t-T['alors']; big(c, "LA FIN D'UN MYTHE ?", 540, 330, 84, GOLD2, ease(ka/.25), lerp(1.3, 1, back(ka/.45)), edge=DARK)
        kp = t-T['pasvite']
        if kp > 0: tag(c, "PAS SI VITE", 540, 470, GREEN, ease(kp/.25), 36)
        return
    if t < T['chere']-.1:
        two(c, "MAROQUINERIE", "+10,8 % AU 3E TRIMESTRE 2026", 300, t-T['sacs'], GREEN, 60, 28); put_emoji(cv, '👜', 880, 210, 70, t-T['sacs']-.3)
        return
    if t < T['toi']-.1:
        k = t-T['chere']; card(c, 540, 380, 900, 360, ease(k/.3), GOLD)
        text(c, "PRIX DE L'ACTION = X ANS DE BÉNÉFICES", 540, 245, 'xb', 26, GOLD, 'c', ease(k/.3), 1)
        for i, (t0, lab, v, cl) in enumerate(((T['trente'], "AUJOURD'HUI", 30, GREEN), (T['contre'], "MOYENNE DEPUIS 2017", 44, '8C8C8C'))):
            u = inout((t-t0)/.7)
            if u <= 0: continue
            y = 330+i*110; w = 420*v/44*u
            text(c, lab, 130, y, 'xb', 24, INK, 'l', ease((t-t0)/.3), 1)
            rr(c, 130, y+22, max(4, w), 46, 10); col(c, cl, 1); c.fill(); text(c, f"{v} ANS", 130+w+16, y+46, 'a', 40, INK, 'l', ease((t-t0)/.3))
        return
    big(c, "ET TOI,", 540, 260, 92, WHITE, ease((t-T['toi'])/.3), edge=GOLD)
    kb = t-T['achet']
    big(c, "TU ACHÈTERAIS", 540, 380, 78, GOLD2, ease(kb/.3), lerp(1.25, 1, back(kb/.4)), edge=DARK)
    big(c, "À CE PRIX-LÀ ?", 540, 475, 78, GOLD2, ease((kb-.15)/.3), lerp(1.25, 1, back((kb-.15)/.4)), edge=DARK)
SCENE = {'atelier': sAtelier, 'avion': sAvion, 'salon': sSalon, 'bibliotheque': sBiblio, 'bourse': sBourse}

# ---------- Mister Coin (clips Veo) ----------
# le clip « enthousiaste » coupe ses mains au bord de l'image : non utilisé (à régénérer avec plus de marge)
N_, E_ = 'aristo_parle_neutre', 'aristo_parle_enthousiaste_16x9'     # deux clips qui alternent, changement en plein saut
MC = VeoCoin([(0.0, N_, 'voix'), (T['y1984']+.15, E_, 'voix'), (T['convoite']+.15, N_, 'voix'), (T['y2010']+.15, E_, 'voix'),
              (T['record']+.15, N_, 'voix'), (T['alors'], E_, 'voix')], voix=VOICE, duree=DUR, x=500, pieds=1725, largeur_piece=220)
PLACE = {'atelier': 500, 'avion': 560, 'salon': 830, 'bibliotheque': 640, 'bourse': 500}     # salon : à côté du piédestal, pas dessus
def coin_pos(t):
    """(x, y des pieds, écrasement) : il saute d'une scène à l'autre en arc, avec élan et réception"""
    x = PLACE['atelier']; y = 1725.
    for i, (ts, r) in enumerate(SCN[1:], 1):
        prev = SCN[i-1][1]; t0 = ts-.12; d = .62
        if t < t0-.15: break
        if t < t0: return PLACE[prev], y+18*math.sin(math.pi/2*(t-t0+.15)/.15)          # il se tasse avant de sauter
        if t < t0+d:
            u = (t-t0)/d; return lerp(PLACE[prev], PLACE[r], inout(u)), y-300*math.sin(math.pi*u)
        if t < t0+d+.2: return PLACE[r], y+14*math.sin(math.pi*(t-t0-d)/.2)            # réception
        x = PLACE[r]
    return x, y

def room_frame(r, t):
    cy = 820 if r == 'bourse' else 950
    return camera(decor(r, t), t, room_start(r), room_end(r), 1.0, 1.06, 540, cy)
def frame(t):
    r = room_at(t); ts = room_start(r)
    bg = room_frame(r, t)
    if r != 'atelier' and t-ts < .5:
        prev = [p for a, p in SCN if a < ts][-1]; u = inout((t-ts)/.5)
        old = room_frame(prev, t); cv = Image.new('RGB', (W, H)); cv.paste(old, (int(-W*u), 0)); cv.paste(bg, (int(W*(1-u)), 0)); bg = cv
    cv = bg.convert('RGBA')
    EMO.clear(); s, c = surface(); SCENE[r](c, cv, t); cv.alpha_composite(to_img(s))
    for e in EMO: draw_emoji(cv, *e)
    X, Y = coin_pos(t); rgb, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx = MC.feet_x(al, Y) if Y > 1700 else X
    if fx is not None:                                                    # ombre douce au sol (plus petite quand il est en l'air)
        import cv2
        k = 1/(1+max(0, 1725-Y)/150)
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), 1722), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .42*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
        a *= (1-m[..., None])
    a = a*(1-al[..., None])+rgb*al[..., None]
    cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    cv = atmosphere(cv, t)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(a-.12, 'whoosh') for a, _ in SCN[1:]]+[(0.0, 'swish'), (T['valent'], 'impact'), (T['prog'], 'swish'), (T['y1837'], 'swish'), (T['harnais'], 'pop'), (T['y1984'], 'swish'),
          (T['patron'], 'pop'), (T['explique'], 'pop'), (T['birkin'], 'glint'), (T['convoite'], 'swish'), (T['attendre'], 'tick'), (T['envole'], 'coins'),
          (T['y2010'], 'swish'), (T['quart'], 'thud'), (T['quart']+.6, 'pop'), (T['renonce']+.3, 'whoosh'), (T['famille'], 'pop'), (T['renonce'], 'glint'), (T['record'], 'swish'), (T['trois'], 'coins'),
          (T['chine'], 'thud'), (T['oct22'], 'pop'), (T['resultat']+.0, 'impact'), (T['resultat'], 'low'), (T['alors'], 'swish'), (T['pasvite'], 'pop'),
          (T['sacs'], 'glint'), (T['chere'], 'swish'), (T['trente'], 'tick'), (T['contre'], 'tick'), (T['toi'], 'swish'), (T['achet'], 'pop'), (T['achet']+.4, 'click')]
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
