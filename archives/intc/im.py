"""Intel : 18 $ (plus bas depuis 2009) -> plus de 140 $ -> rechute. Processeur 3D générique + plongée dans les pistes (réseau).
usage : python im.py png t1 t2 ... | python im.py seg out.mp4 f0 f1 | python im.py info"""
import sys, math, re, random, subprocess, os, functools, csv, datetime
import numpy as np, cairo
from PIL import Image, ImageEnhance
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/meta')
from bglass import *
FPS = 60; NB = ' '
CY = '35D6FF'; CY2 = 'A8EEFF'; RD = 'FF4057'; GR = '3FE08A'; AMB = 'FFC24A'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage (provisoire, recalé sur la voix) ----------
T = dict(hook=0.0, miss=5.95, gov=10.1, nv=12.3, up=14.75, x8=17.3, fall=19.95, b37=21.7, eur=22.6, v=25.2, res=26.8, cta=29.6, buy=31.05, end=34.0)
DUR = T['end']
CAPS = [(0.0, "[18 dollars]."), (1.3, "C'est le prix d'Intel en avril 2025 :"), (4.0, "son plus bas depuis [16 ans]."),
        (T['miss'], "Le géant des processeurs avait raté le virage de l'[intelligence artificielle]."),
        (T['gov'], "Puis l'État américain entre au capital,"), (T['nv'], "Nvidia investit [5 milliards]…"),
        (T['up'], "et en 14 mois, l'action est multipliée [par 8],"), (18.0, "au-dessus de [140 dollars]."),
        (T['fall'], "Depuis l'été, elle a rechuté de [plus d'un tiers]."),
        (T['eur'], "1 000 euros placés il y a 5 ans valent aujourd'hui"), (T['v'], "[1 905 euros]."),
        (T['res'], "Le 29 octobre, Intel publie ses [résultats]."), (T['cta'], "Et toi,"), (T['buy'], "tu [achètes] ?")]
HL = {0.0: RD, 4.0: RD, T['miss']: RD, T['up']: GR, 18.0: GR, T['fall']: RD, T['v']: GR, T['buy']: GR}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1400, size=46, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 860: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK if hl in (GR, AMB, CY) else WHITE, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- fond 3D : processeur (orbite) puis plongée dans les pistes ----------
SEQ = {'cpu': '/home/claude/intc/seq2_cpu', 'net': '/home/claude/intc/seq2_net'}
@functools.lru_cache(maxsize=20)
def fr(shot, i):
    p = f'{SEQ[shot]}/f{i:04d}.png'
    if not os.path.exists(p):
        ks = sorted(k for k in os.listdir(SEQ[shot]) if k.endswith('.png')) if os.path.isdir(SEQ[shot]) else []
        p = f'{SEQ[shot]}/{ks[-1]}' if ks else f'/tmp/k08/i_{shot}.png'
    im = Image.open(p).convert('RGB')
    return im if im.size == (W, H) else im.resize((W, H), Image.LANCZOS)
SEQ30 = {'cpu': '/home/claude/intc/seq30_cpu', 'net': '/home/claude/intc/seq30_net'}
@functools.lru_cache(maxsize=8)
def fr30(shot, i):
    im = Image.open(f'{SEQ30[shot]}/{i:04d}.png').convert('RGB')
    return im if im.size == (W, H) else im.resize((W, H), Image.LANCZOS)
def loop(shot, t):
    """images intermédiaires calculées par flux optique (15 -> 30 i/s) : plus de fondu entre deux rendus, image nette"""
    if os.path.exists(f'{SEQ30[shot]}/0118.png'): return fr30(shot, min(118, int(t*30) % 120))
    f = (t*30) % 120; i = int(f//2)*2; u = (f-i)/2
    a = fr(shot, i+1); b = fr(shot, (i+2) % 120+1)
    return Image.blend(a, b, u) if u > .05 else a
DIVE, BACKC = T['gov']-.35, T['res']-.3
def rays(cv, cx, cy, a, color=(140, 230, 255), n=16, seed=3):
    """faisceaux de lumière volumétriques qui jaillissent du processeur"""
    if a <= .01: return
    s, c = surface(); rnd = random.Random(seed)
    for k in range(n):
        ang = -math.pi/2+rnd.uniform(-1.35, 1.35); w = rnd.uniform(.03, .09); L = rnd.uniform(700, 1500)
        g = cairo.RadialGradient(cx, cy, 0, cx, cy, L); g.add_color_stop_rgba(0, color[0]/255, color[1]/255, color[2]/255, .55*a*rnd.uniform(.5, 1)); g.add_color_stop_rgba(1, color[0]/255, color[1]/255, color[2]/255, 0)
        c.move_to(cx, cy); c.arc(cx, cy, L, ang-w, ang+w); c.close_path(); c.set_source(g); c.fill()
    im = lowblur(to_img(s), 18, 4); cv.alpha_composite(im)
    s, c = surface(); g = cairo.RadialGradient(cx, cy, 0, cx, cy, 260); g.add_color_stop_rgba(0, 1, 1, 1, .7*a); g.add_color_stop_rgba(1, color[0]/255, color[1]/255, color[2]/255, 0)
    c.set_source(g); c.paint(); cv.alpha_composite(to_img(s))

def background(t):
    if t < DIVE:
        im = loop('cpu', t); z = 1.02+.03*(t/DIVE)
        k = t-(DIVE-.6)
        if k > 0: z += 1.6*ease(k/.6)**2            # plongée dans le processeur
    elif t < BACKC:
        im = loop('net', t); k = t-DIVE; z = lerp(1.5, 1.0, ease(k/.6)) if k < .6 else 1.0
    else:
        im = loop('cpu', t); k = t-BACKC; z = lerp(1.35, 1.0, ease(k/.7))
    if t < .45: z += .15*(1-ease(t/.45))
    if abs(z-1) > .002:
        w, h = int(W*z), int(H*z); im = im.resize((w, h), Image.BILINEAR).crop(((w-W)//2, (h-H)//2, (w-W)//2+W, (h-H)//2+H))
    blur = 0
    if DIVE-.3 < t < DIVE+.4: blur = 14*(1-abs(t-DIVE)/.4)
    if blur > .5: im = lowblur(im, blur, 2)
    # bloom néon : les zones lumineuses diffusent un halo ; couleur des circuits selon l'histoire (cyan, or à la hausse, rouge à la rechute)
    arr = np.asarray(im, np.float32)
    tint = None
    if T['up'] <= t < T['fall']: tint, k_ = np.array([1.0, .72, .28]), ease((t-T['up'])/.6)
    elif T['fall'] <= t < T['eur']: tint, k_ = np.array([1.0, .25, .3]), ease((t-T['fall'])/.4)
    if tint is not None:
        lum = arr.max(axis=2, keepdims=True); cyan = np.clip((arr[..., 2:3]-arr[..., 0:1]-40)/80, 0, 1)   # pixels « néon cyan »
        arr = arr*(1-cyan*k_)+(lum*tint)*cyan*k_
    hi_ = np.clip(arr-185, 0, None)*1.4
    halo = np.asarray(lowblur(Image.fromarray(hi_.clip(0, 255).astype(np.uint8)), 22, 4), np.float32)
    im = Image.fromarray(np.clip(arr*.92+halo*.6, 0, 255).astype(np.uint8)).convert('RGBA')
    if abs(t-DIVE) < .18 or abs(t-BACKC) < .18:    # éclair de passage
        d = min(abs(t-DIVE), abs(t-BACKC)); s, c = surface(); c.set_source_rgba(.7, .95, 1, .55*(1-d/.18)); c.paint(); im.alpha_composite(to_img(s))
    return im

# ---------- données ----------
PATH = []
with open('/home/claude/intc/path.csv') as f:
    for r in csv.DictReader(f):
        d = datetime.date.fromisoformat(r['date']); PATH.append((d.year+(d.timetuple().tm_yday-1)/365, float(r['price'])))

# ---------- emojis (Noto, licence libre) ----------
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=64)
def emoji(ch, size):
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def pop_emoji(cv, ch, x, y, size, k, rot=0.0, t=0.0, a=1.0):
    if k < 0 or a <= 0: return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size).rotate(rot+6*math.sin(t*3+x*.01), resample=Image.BICUBIC, expand=True)
    e = with_alpha(e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))), Image.BICUBIC), a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
EMO = [(0.35, '📉', 860, 330, 130, -10, T['miss']), (2.2, '😵', 220, 760, 120, 10, T['miss']),
       (T['miss']+.9, '🤦', 880, 900, 130, -8, T['gov']), (7.4, '🤖', 200, 900, 110, 10, T['gov']),
       (T['gov']+.3, '🏛️', 880, 400, 110, -8, T['up']), (T['nv']+.3, '💵', 200, 1060, 110, 10, T['up']),
       (T['x8']+.1, '🚀', 900, 190, 130, -12, T['fall']), (T['b37']+.1, '🎢', 900, 180, 130, 8, T['eur']),
       (T['v']+.2, '💶', 880, 560, 120, -10, T['res']), (T['res']+.5, '⏳', 860, 560, 110, 10, T['cta']), (T['buy']+.2, '🤔', 540, 880, 120, -8, DUR+1)]

# ---------- scènes ----------
def gp(w, h, draw): return gpanel(w, h, draw, tint='CFF4FF', ta=.08, edge=.75)
def sHook(cv, c, t, a):
    glow_text(cv, "18 $", 540, 520, 260, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.75, a=a, scale=lerp(1.3, 1, back(t/.45, 1.3)))
    grp(c, a*ease((t-1.3)/.3), lambda c: text(c, "INTEL · AVRIL 2025", 540, 720, 'xb', 40, WHITE, 'c', 1, 3))
    def badge(c):
        w = tw(c, "PLUS BAS DEPUIS 2009", 'xb', 32, 2)+60; rr(c, 540-w/2, 770, w, 64, 32); col(c, RD); c.fill(); text(c, "PLUS BAS DEPUIS 2009", 540, 802, 'xb', 32, WHITE, 'c', 1, 2)
    grp(c, a*ease((t-4.0)/.3), badge)
def sMiss(cv, c, t, a):
    k = t-T['miss']; e = ease(k/.4)
    def d(k_, w, h):
        text(k_, "LE GÉANT DES PROCESSEURS", w/2, 70, 'sb', 26, CY2, 'c', 1, 3)
        text(k_, "A RATÉ", w/2, 165, 'a', 96, WHITE, 'c'); text(k_, "LE VIRAGE DE L'IA", w/2, 270, 'a', 70, RD, 'c')
    place(cv, gp(820, 340, d), tilt_quad(540, 640+50*(1-e), 820, 340, ry=-.18*(1-e)-.06, rx=.08), a*e, 14, .5)
def node(title, val, sub, accent):
    def d(k, w, h):
        k.arc(52, 60, 12, 0, 2*math.pi); col(k, accent); k.fill(); k.arc(52, 60, 22, 0, 2*math.pi); k.set_line_width(2); col(k, accent, .5); k.stroke()
        text(k, title, 86, 60, 'sb', 26, ICE, 'l', 1, 2); text(k, val, w/2, 150, 'a', 84, WHITE, 'c'); text(k, sub, w/2, 222, 'sb', 24, accent, 'c', 1, 2)
    return gp(600, 260, d)
def sNodes(cv, c, t, a):
    # deux nœuds du réseau reliés par une piste lumineuse
    k1, k2 = t-T['gov'], t-T['nv']
    s, cc = surface()
    if k2 > 0:
        u = ease(k2/.5); cc.set_line_width(6); col(cc, CY, .9*a); cc.move_to(400, 620); cc.line_to(400, 620+(830-620)*u); cc.line_to(400+(680-400)*clamp(u*1.5-.5), 830); cc.stroke()
    cv.alpha_composite(to_img(s))
    e1 = ease(k1/.4); place(cv, node("ÉTAT AMÉRICAIN", "AU CAPITAL", "AOÛT 2025", AMB), tilt_quad(400, 520+40*(1-e1), 600, 260, ry=.22, rx=.08), a*e1, 14, .5)
    if k2 > 0:
        e2 = ease(k2/.4); place(cv, node("NVIDIA", "5 MD$", "INVESTIS · SEPT. 2025", GR), tilt_quad(680, 900+40*(1-e2), 600, 260, ry=-.22, rx=.08), a*e2, 14, .5)
CX0, CX1 = 2025.2, 2026.85
def _smooth(path, n=900):
    """Catmull-Rom (centripète simplifiée) rééchantillonnée finement : la courbe se dessine sans à-coups"""
    P = [p for p in path if p[0] >= CX0-.1]; out = []
    for i in range(len(P)-1):
        p0, p1, p2, p3 = P[max(0, i-1)], P[i], P[i+1], P[min(len(P)-1, i+2)]
        for k in range(12):
            u = k/12; u2, u3 = u*u, u*u*u
            f = lambda a, b, c, d: .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u2+(-a+3*b-3*c+d)*u3)
            out.append((f(p0[0], p1[0], p2[0], p3[0]), max(5.0, f(p0[1], p1[1], p2[1], p3[1]))))
    out.append(P[-1]); return out
SM = _smooth(PATH)
def reveal(xr):
    pts = [p for p in SM if p[0] <= xr]
    j = len(pts)
    if 0 < j < len(SM):
        a, b = SM[j-1], SM[j]; f = (xr-a[0])/max(1e-9, b[0]-a[0]); pts.append((xr, a[1]+(b[1]-a[1])*f))
    return pts if len(pts) >= 2 else SM[:2]
def sChart(cv, c, t, a):
    k = t-T['up']
    if t < T['fall']: u = inout(k/2.2); xr = 2026.5
    else: u = 1.0; xr = 2026.5+(CX1-2026.5)*inout((t-T['fall'])/1.4)
    X0, X1, YT, YB = 60, 820, 120, 470
    def px(yr, v): return X0+(yr-CX0)/(CX1-CX0)*(X1-X0), YB-v/150*(YB-YT)
    pts = reveal(CX0+(xr-CX0)*u if t < T['fall'] else xr)
    def d(kk, w, h):
        text(kk, "COURS DE L'ACTION ($)", 40, 50, 'sb', 24, CY2, 'l', 1, 2)
        for yy in (2025.5, 2026.0, 2026.5):
            text(kk, {2025.5: "JUIL. 25", 2026.0: "JANV. 26", 2026.5: "JUIL. 26"}[yy], px(yy, 0)[0], h-34, 'm', 22, SUB)
        grow = t < T['fall']
        colr = GR if grow else RD
        kk.move_to(*px(*pts[0]))
        for q in pts[1:]: kk.line_to(*px(*q))
        kk.line_to(px(*pts[-1])[0], YB); kk.line_to(px(*pts[0])[0], YB); kk.close_path()
        g = cairo.LinearGradient(0, YT, 0, YB); g.add_color_stop_rgba(0, *hx(colr, .35)); g.add_color_stop_rgba(1, *hx(colr, 0)); kk.set_source(g); kk.fill()
        for a_, lw in ((.12, 22), (.25, 11), (1, 5)):
            kk.move_to(*px(*pts[0]))
            for q in pts[1:]: kk.line_to(*px(*q))
            kk.set_line_width(lw); kk.set_line_join(1); col(kk, colr, a_); kk.stroke()
        x, y = px(*pts[-1]); kk.arc(x, y, 10, 0, 2*math.pi); col(kk, WHITE); kk.fill()
        text(kk, f"{pts[-1][1]:.0f} $", min(x+16, w-120), y-28, 'xb', 32, WHITE, 'l')
        lx, ly = px(2025.27, 18.13); text(kk, "18 $", lx+10, ly+30, 'xb', 26, RD, 'l')
    e = ease(k/.45)
    place(cv, gp(880, 560, d), tilt_quad(540, 780+50*(1-e), 880, 560, ry=-.14-.3*(1-e), rx=.06), a*e, 14, .55)
    if t < T['fall']:
        kx = t-T['x8']
        if kx > 0: glow_text(cv, "×7,8", 540, 330, 200, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kx/.25), scale=lerp(1.35, 1, back(kx/.4)))
    else:
        kb = t-T['b37']
        if kb > 0: glow_text(cv, "−37 %", 540, 330, 200, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.7, a=a*ease(kb/.25), scale=lerp(1.35, 1, back(kb/.4)))
        grp(c, a*ease((kb-.3)/.3), lambda c: text(c, "DEPUIS LE SOMMET DE JUIN", 540, 470, 'xb', 32, WHITE, 'c', 1, 2))
def sEur(cv, c, t, a):
    k = t-T['eur']; e = ease(k/.4)
    grp(c, a*e, lambda c: (text(c, "1 000 € PLACÉS EN OCTOBRE 2021", 540, 420, 'xb', 38, WHITE, 'c', 1, 2), text(c, "VALENT AUJOURD'HUI", 540, 480, 'xb', 38, CY2, 'c', 1, 2)))
    kv = t-T['v']
    if kv > -.6:
        v = int(1905*ease(clamp((kv+.6)/1.0)))
        glow_text(cv, f"{v:,} €".replace(',', ' '), 540, 700, 200, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a, scale=lerp(1, 1.08, ease(kv/.2)) if kv < .2 else lerp(1.08, 1, ease((kv-.2)/.3)))
    grp(c, a*ease((kv-.4)/.3), lambda c: text(c, "+90 % EN 5 ANS… APRÈS −63 % EN CHEMIN", 540, 880, 'xb', 30, AMB, 'c', 1, 1))
def sRes(cv, c, t, a):
    k = t-T['res']; e = back(k/.45)
    def d(kk, w, h):
        rr(kk, 0, 0, w, 110, 0); col(kk, RD); kk.fill()
        text(kk, "JEUDI", w/2, 58, 'xb', 44, WHITE, 'c', 1, 4); text(kk, "29", w/2, 260, 'a', 230, WHITE); text(kk, "OCTOBRE", w/2, 420, 'xb', 36, ICE, 'c', 1, 4)
    place(cv, gp(420, 480, d), tilt_quad(540, 700, 420*e, 480*e, ry=-.12, rx=.06), a*clamp(k/.2), 22, .5)
    grp(c, a*ease((k-.5)/.3), lambda c: text(c, "RÉSULTATS T3 · APRÈS LA CLÔTURE", 540, 1010, 'xb', 32, WHITE, 'c', 1, 2))
def sCta(cv, c, t, a):
    k = t-T['cta']
    glow_text(cv, "ET TOI,", 540, 520, 130, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.3))
    kb = t-T['buy']
    glow_text(cv, "TU ACHÈTES ?", 540, 680, 130, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kb/.3), scale=lerp(1.3, 1, back(kb/.4)))
    al = ease((kb-.3)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 1135, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 1135, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)

SCENES = [(sHook, 0.0, T['miss']), (sMiss, T['miss']-.1, T['gov']), (sNodes, T['gov']-.1, T['up']), (sChart, T['up']-.1, T['eur']),
          (sEur, T['eur']-.1, T['res']), (sRes, T['res']-.1, T['cta']), (sCta, T['cta']-.1, DUR+1)]
SHAKES = [(0.0, 14), (DIVE, 18), (T['x8'], 12), (T['b37'], 14), (T['v'], 14)]
def frame(t):
    cv = background(t)
    if t < 1.2: rays(cv, 540, 1010, (1-ease(t/1.2))*1.0)                    # éclair d'ouverture
    if DIVE-.9 < t < DIVE+.25: rays(cv, 540, 1010, clamp((t-(DIVE-.9))/.9)*clamp((DIVE+.25-t)/.25)*1.2, n=22, seed=5)   # le processeur s'illumine avant la plongée
    if T['x8'] <= t < T['x8']+.9: rays(cv, 540, 900, (1-ease((t-T['x8'])/.9))*.9, color=(255, 200, 110), n=18, seed=8)
    darkspot(cv, 540, 700, 700, 720, .3); darken_band(cv, 1290, 1520, .6)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    kk = cap_at(t)
    if kk is not None and t < DUR:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, CY)), 14*(1-al))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(6, 6, 8, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'impact'), (0.0, 'low'), (T['miss'], 'swish'), (DIVE-.8, 'riser'), (DIVE, 'boom'), (T['nv'], 'pop'), (T['up'], 'swish'),
          (T['x8']-.6, 'tick'), (T['x8'], 'impact'), (T['fall'], 'crash'), (T['b37'], 'impact'), (T['eur'], 'swish'), (T['v']-.6, 'tick'),
          (T['v'], 'boom'), (T['v'], 'coins'), (BACKC, 'swish'), (T['res'], 'pop'), (T['buy'], 'pop'), (T['buy']+.3, 'click')]
    ev += [(e[0], 'pop') for e in EMO if e[0] > .1]
    return ev

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/intc/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'/home/claude/intc/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
