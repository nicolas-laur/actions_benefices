"""Meta : 1 000 € placés au changement de nom, −76 %, ×8, résultats mercredi. Téléphone 3D (phone.py) + stories composées en 2D sur l'écran.
Aucun logo Meta / Facebook / Instagram : interface de stories neutre aux couleurs de la chaîne.
usage : python mm.py png t1 t2 ... | python mm.py seg out.mp4 f0 f1 | python mm.py info"""
import sys, math, re, random, subprocess, os, functools, json, csv, datetime
import numpy as np, cairo
from PIL import Image, ImageEnhance, ImageChops
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc')
from bglass import *
FPS = 60; NB = ' '
BL = '3D8BFF'; BL2 = '7FB8FF'; RD = 'FF4057'; GR = '3FE08A'; AMB = 'FFC24A'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage (provisoire, recalé sur la voix) ----------
T = dict(hook=0.0, s2=6.55, fb=8.15, meta=9.2, s3=9.8, s4=13.35, b76=15.05, s5=17.9, ia=20.3, s6=22.35, x8=23.6, s7=25.35, v=26.9, s8=29.25, s9=31.6, buy=32.2, end=34.1)
DUR = T['end']
STORIES = ['hook', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']
CAPS = [(0.0, "[328 euros]."), (1.4, "C'est tout ce qu'il restait de 1 000 euros placés dans Meta…"), (4.35, "un an après son changement de nom."),
        (T['s2'], "Octobre 2021 :"), (T['fb'], "Facebook devient [Meta],"), (T['s3'], "et Zuckerberg parie tout sur le [métavers]."),
        (T['s4'], "Résultat :"), (14.2, "l'action perd [76 %] depuis son record."), (T['s5'], "Puis Meta coupe dans ses coûts…"), (19.75, "et mise tout sur l'[intelligence artificielle]."),
        (T['s6'], "L'action est multipliée [par 8] depuis son plus bas."), (T['s7'], "Tes 1 000 euros valent aujourd'hui"), (T['v'], "[2 278 euros]."),
        (T['s8'], "Mercredi, Meta publie ses [résultats]."), (T['s9'], "Et toi,"), (T['buy'], "tu [achètes] ?")]
HL = {0.0: RD, 14.2: RD, T['s6']: GR, T['v']: GR, T['buy']: GR}
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
def caption(c, words, hl, y=1530, size=46, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK if hl in (GR, AMB, BL2) else WHITE, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- fond : téléphone 3D en boucle ----------
SEQ = '/home/claude/meta/seq_phone'
PROJ = {int(k): v for k, v in json.load(open('/home/claude/meta/proj.json')).items()}
@functools.lru_cache(maxsize=16)
def fr(i):
    p = f'{SEQ}/f{i:04d}.png'
    if not os.path.exists(p):
        ks = sorted(k for k in os.listdir(SEQ) if k.endswith('.png')) if os.path.isdir(SEQ) else []
        p = f'{SEQ}/{ks[0]}' if ks else '/tmp/k08/ph_t.png'
    return Image.open(p).convert('RGB').resize((W, H), Image.BICUBIC)
def phone_frame(t):
    f = (t*30) % 240; i = int(f//2)*2; u = (f-i)/2
    a = fr(i+1); b = fr((i+2) % 240+1)
    im = Image.blend(a, b, u) if u > .05 else a
    q0, q1 = PROJ[i+1], PROJ[(i+2) % 240+1]
    quad = [(lerp(p[0], r[0], u), lerp(p[1], r[1], u)) for p, r in zip(q0, q1)]
    return im, quad

# ---------- données ----------
PATH = []
with open('/home/claude/meta/path.csv') as f:
    for r in csv.DictReader(f):
        d = datetime.date.fromisoformat(r['date']); PATH.append((d.year+(d.timetuple().tm_yday-1)/365, float(r['price'])))
P0, PL, P1 = 323.57, 88.91, 709.33

# ---------- stories (dessinées à la taille de l'écran) ----------
SW, SH = 600, 1291
def story_bg(c, top, bot):
    g = cairo.LinearGradient(0, 0, SW*.3, SH); g.add_color_stop_rgb(0, *hx(top)[:3]); g.add_color_stop_rgb(1, *hx(bot)[:3]); c.set_source(g); c.paint()
def header(c, idx, prog):
    n = len(STORIES); gap = 8; w = (SW-40-gap*(n-1))/n
    for k in range(n):
        x = 20+k*(w+gap); rr(c, x, 26, w, 6, 3); col(c, WHITE, .3); c.fill()
        fill = 1 if k < idx else (prog if k == idx else 0)
        if fill > 0: rr(c, x, 26, max(6, w*fill), 6, 3); col(c, WHITE, .95); c.fill()
    # avatar neutre : pastille aux couleurs de la chaîne (pas l'anneau d'Instagram)
    c.arc(52, 76, 24, 0, 2*math.pi); col(c, '1A2333'); c.fill(); c.set_line_width(3); c.arc(52, 76, 26, 0, 2*math.pi); col(c, BL2); c.stroke()
    c.push_group(); logo_symbol(c, 40, 76, 24); c.pop_group_to_source(); c.paint()
    text(c, "actions_bnfices", 90, 70, 'xb', 22, WHITE, 'l'); text(c, "Meta · en 30 s", 90, 96, 'm', 18, ICE, 'l', .75)
def big(c, s, y, size, color=WHITE, a=1, sc=1.0):
    c.save(); c.translate(SW/2, y); c.scale(sc, sc); text(c, s, 0, 0, 'a', size, color, 'c', a); c.restore()
def chart(c, x0, y0, w, h, ymax, t0, t1, u, color, mark=None):
    def px(yr, v): return x0+(yr-t0)/(t1-t0)*w, y0+h-(v/ymax)*h
    pts = [p for p in PATH if t0 <= p[0] <= t1]; n = max(2, int(len(pts)*u)); pts = pts[:n]
    c.move_to(*px(*pts[0]))
    for q in pts[1:]: c.line_to(*px(*q))
    c.line_to(px(*pts[-1])[0], y0+h); c.line_to(px(*pts[0])[0], y0+h); c.close_path()
    g = cairo.LinearGradient(0, y0, 0, y0+h); g.add_color_stop_rgba(0, *hx(color, .35)); g.add_color_stop_rgba(1, *hx(color, 0)); c.set_source(g); c.fill()
    for a_, lw in ((.15, 18), (1, 6)):
        c.move_to(*px(*pts[0]))
        for q in pts[1:]: c.line_to(*px(*q))
        c.set_line_width(lw); c.set_line_join(1); col(c, color, a_); c.stroke()
    x, y = px(*pts[-1]); c.arc(x, y, 10, 0, 2*math.pi); col(c, WHITE); c.fill()
    return px

def st_hook(c, t, k):
    story_bg(c, '2A0A12', '0B0E14')
    big(c, "328 €", 560, 190, RD, sc=lerp(1.25, 1, back(k/.4)))
    text(c, "RESTANT DE TES 1 000 €", SW/2, 700, 'xb', 30, WHITE, 'c', ease((k-.4)/.3), 2)
    text(c, "PLACÉS DANS META EN 2021", SW/2, 745, 'xb', 30, WHITE, 'c', ease((k-.5)/.3), 2)
    e = ease((k-4.2)/.4)
    rr(c, SW/2-170, 830, 340, 70, 35); col(c, WHITE, .12*e); c.fill(); text(c, "UN AN PLUS TARD", SW/2, 865, 'xb', 28, AMB, 'c', e, 2)
def st_rename(c, t, k):
    story_bg(c, '0A1E44', '0B0E14')
    text(c, "28.10.2021", SW/2, 330, 'a', 80, WHITE, 'c', ease(k/.3))
    kf, km = t-T['fb'], t-T['meta']
    e = ease(kf/.3)
    text(c, "Facebook", SW/2, 560, 'xb', 76, WHITE, 'c', e*(1-.55*ease((km+.2)/.3)))
    if km > -.2:
        s = ease((km+.2)/.25); c.set_line_width(8); col(c, RD); c.move_to(SW/2-190, 560); c.line_to(SW/2-190+380*s, 560); c.stroke()
    text(c, "↓", SW/2, 680, 'xb', 70, BL2, 'c', ease(km/.3))
    big(c, "META", 820, 150, WHITE, ease(km/.3), lerp(1.3, 1, back(km/.4)))
def headset(c, cx, cy, s, a=1):
    """casque de réalité virtuelle générique (dessin original)"""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    rr(c, -170, -80, 340, 160, 70); g = cairo.LinearGradient(0, -80, 0, 80); g.add_color_stop_rgba(0, *hx('F2F4F8', a)); g.add_color_stop_rgba(1, *hx('9AA3B5', a)); c.set_source(g); c.fill()
    rr(c, -150, -55, 300, 110, 50); col(c, '0B0E14', a); c.fill()
    for sx in (-1, 1):
        c.arc(sx*70, 0, 34, 0, 2*math.pi); g = cairo.RadialGradient(sx*70-10, -10, 2, sx*70, 0, 34); g.add_color_stop_rgba(0, *hx(BL2, .9*a)); g.add_color_stop_rgba(1, *hx('1A3C80', .6*a)); c.set_source(g); c.fill()
    c.set_line_width(22); col(c, '3A4254', a); c.move_to(-170, -10); c.curve_to(-260, -10, -260, -150, -120, -170); c.stroke()
    c.restore()
def st_meta(c, t, k):
    story_bg(c, '151040', '0B0E14')
    rnd = random.Random(2)
    for i in range(40):   # grille du « monde virtuel »
        y = 900+i*14
        if y > SH: break
    c.set_line_width(2)
    for i in range(-8, 9):
        col(c, BL2, .25); c.move_to(SW/2+i*20, 760); c.line_to(SW/2+i*120, SH); c.stroke()
    for j in range(8):
        y = 760+(j/8)**1.8*(SH-760); col(c, BL2, .2); c.move_to(0, y); c.line_to(SW, y); c.stroke()
    headset(c, SW/2, 470+8*math.sin(t*2), lerp(.6, 1, back(k/.5)), ease(k/.3))
    text(c, "TOUT SUR LE MÉTAVERS", SW/2, 700, 'xb', 34, WHITE, 'c', ease((k-.4)/.3), 2)
def st_drop(c, t, k):
    story_bg(c, '2A0A12', '0B0E14')
    u = inout(k/1.6)
    px = chart(c, 40, 380, SW-80, 520, 400, 2021.6, 2022.95, u, RD)
    for yr, lab in ((2021.75, "2021"), (2022.5, "2022")): text(c, lab, px(yr, 0)[0], 935, 'm', 22, ICE, 'c', .7)
    if t >= T['b76']:
        s = back((t-T['b76'])/.35); c.save(); c.translate(SW/2, 250); c.scale(s, s); rr(c, -160, -60, 320, 120, 18); col(c, RD); c.fill(); text(c, "−76 %", 0, 0, 'a', 86, WHITE); c.restore()
        text(c, "DEPUIS SON RECORD", SW/2, 1010, 'xb', 28, WHITE, 'c', ease((t-T['b76']-.2)/.3), 2)
def chip(c, cx, cy, s, a=1, pulse=0):
    """puce « IA » générique"""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    for i in range(-3, 4):
        for sgn in (-1, 1):
            c.set_line_width(8); col(c, 'B9C4D8', a); c.move_to(i*36, sgn*130); c.line_to(i*36, sgn*170); c.stroke()
            c.move_to(sgn*130, i*36); c.line_to(sgn*170, i*36); c.stroke()
    rr(c, -135, -135, 270, 270, 26); g = cairo.LinearGradient(-135, -135, 135, 135); g.add_color_stop_rgba(0, *hx('2B3550', a)); g.add_color_stop_rgba(1, *hx('0F1422', a)); c.set_source(g); c.fill()
    rr(c, -135, -135, 270, 270, 26); c.set_line_width(4); col(c, BL2, (.6+.4*pulse)*a); c.stroke()
    text(c, "IA", 0, 0, 'a', 120, WHITE, 'c', a); c.restore()
def st_ai(c, t, k):
    story_bg(c, '0A1E44', '0B0E14')
    e = ease(k/.3)
    text(c, "2023", SW/2, 250, 'a', 70, WHITE, 'c', e); text(c, "« L'ANNÉE DE L'EFFICACITÉ »", SW/2, 320, 'xb', 28, AMB, 'c', e, 1)
    for i, (lab, v) in enumerate((("Postes supprimés", "−21 000"), ("Métavers", "freiné"))):
        y = 420+i*90; e2 = ease((k-.4-i*.25)/.3); rr(c, 60, y, SW-120, 70, 16); col(c, WHITE, .08*e2); c.fill()
        text(c, lab, 90, y+35, 'xb', 28, ICE, 'l', e2); text(c, v, SW-90, y+35, 'a', 38, RD, 'r', e2)
    k2 = t-T['ia']
    if k2 > 0: chip(c, SW/2, 900, lerp(.5, .95, back(k2/.5)), ease(k2/.3), .5+.5*math.sin(t*6))
def st_x8(c, t, k):
    story_bg(c, '082A1C', '0B0E14')
    u = inout(k/1.8)
    px = chart(c, 40, 400, SW-80, 560, 800, 2022.8, 2026.85, u, GR)
    for yr in (2023, 2024, 2025, 2026): text(c, str(yr), px(yr+.5, 0)[0], 995, 'm', 22, ICE, 'c', .7)
    kx = t-T['x8']
    big(c, "×8", 260, 170, GR, ease(kx/.3), lerp(1.3, 1, back(kx/.4)))
    text(c, "DEPUIS SON PLUS BAS", SW/2, 360, 'xb', 26, WHITE, 'c', ease((kx-.2)/.3), 2)
def st_today(c, t, k):
    story_bg(c, '082A1C', '0B0E14')
    text(c, "TES 1 000 € AUJOURD'HUI", SW/2, 380, 'xb', 32, WHITE, 'c', ease(k/.3), 2)
    kv = t-T['v']
    if kv > -0.6:
        v = int(2278*ease(clamp((kv+.6)/1.0)))
        big(c, f"{v:,} €".replace(',', ' '), 560, 150, GR if kv > 0 else WHITE, 1, lerp(1, 1.08, ease(kv/.2))*(1 if kv < .2 else lerp(1.08, 1, ease((kv-.2)/.3))))
    text(c, "+128 % EN 5 ANS", SW/2, 700, 'xb', 30, GR, 'c', ease((kv-.3)/.3), 2)
def st_wed(c, t, k):
    story_bg(c, '0A1E44', '0B0E14')
    e = back(k/.45); c.save(); c.translate(SW/2, 560); c.scale(e, e)
    rr(c, -200, -230, 400, 460, 36); col(c, WHITE); c.fill(); rr(c, -200, -230, 400, 110, 36); col(c, RD); c.fill(); c.rectangle(-200, -160, 400, 40); c.fill()
    text(c, "MERCREDI", 0, -168, 'xb', 40, WHITE, 'c', 1, 3); text(c, "21", 0, 30, 'a', 220, INK); text(c, "OCTOBRE", 0, 170, 'xb', 32, INK, 'c', 1, 3)
    c.restore()
    text(c, "RÉSULTATS T3 · APRÈS LA CLÔTURE", SW/2, 880, 'xb', 26, WHITE, 'c', ease((k-.5)/.3), 1)
def st_cta(c, t, k):
    story_bg(c, '0A1E44', '0B0E14')
    big(c, "ET TOI,", 380, 110, WHITE, ease(k/.3)); big(c, "TU ACHÈTES ?", 510, 110, GR, ease((t-T['buy'])/.3), lerp(1.2, 1, back((t-T['buy'])/.4)))
    e = ease((k-.8)/.35)   # sondage de story générique
    rr(c, 70, 640, SW-140, 260, 28); col(c, WHITE, .95*e); c.fill()
    for i, (lab, pct, cl) in enumerate((("J'ACHÈTE", .62, GR), ("J'ATTENDS", .38, AMB))):
        y = 680+i*105; rr(c, 100, y, SW-200, 80, 40); col(c, 'E9EDF4', e); c.fill()
        f = ease((k-1.4)/.6)*pct
        if f > 0: rr(c, 100, y, (SW-200)*f, 80, 40); col(c, cl, e); c.fill()
        text(c, lab, 140, y+40, 'xb', 30, INK, 'l', e)
    c.push_group(); logo_symbol(c, SW/2-120, 1080, 34); c.pop_group_to_source(); c.paint_with_alpha(ease((k-1.2)/.4))
    text(c, "Actions_Benefices", SW/2-95, 1080, 'b', 26, WHITE, 'l', ease((k-1.2)/.4))
FN = dict(hook=st_hook, s2=st_rename, s3=st_meta, s4=st_drop, s5=st_ai, s6=st_x8, s7=st_today, s8=st_wed, s9=st_cta)
NXT = {STORIES[i]: (T[STORIES[i+1]] if i+1 < len(STORIES) else DUR) for i in range(len(STORIES))}

EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'   # Noto Color Emoji (licence libre)
@functools.lru_cache(maxsize=64)
def emoji(ch, size):
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def paste_emoji(img, ch, x, y, size, k, rot=0.0, t=0.0):
    """pose un emoji avec un rebond d'apparition et une légère oscillation"""
    if k < 0: return
    s = back(k/.35, 2.2); 
    if s <= .02: return
    e = emoji(ch, size).rotate(rot+6*math.sin(t*3+x*.01), resample=Image.BICUBIC, expand=True)
    e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))), Image.BICUBIC)
    img.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
# stickers posés sur les stories : (story, apparition, emoji, x, y, taille, rotation)
STICK = [('hook', .45, '😱', 470, 390, 120, -10), ('hook', 4.55, '⏳', 110, 960, 100, 12),
         ('s2', T['meta']+.35, '🤔', 480, 690, 110, -8),
         ('s3', 10.5, '😬', 110, 300, 120, 10), ('s3', 11.3, '😂', 490, 300, 120, -12), ('s3', 11.7, '😂', 300, 1040, 90, 8),
         ('s4', 14.3, '📉', 490, 1090, 110, -6), ('s4', T['b76']+.3, '💀', 110, 1090, 110, 10),
         ('s5', 18.4, '✂️', 490, 720, 90, -12), ('s5', T['ia']+.3, '🤖', 480, 1080, 120, -8),
         ('s6', T['x8']+.2, '🚀', 480, 220, 120, 12), ('s6', 24.2, '📈', 110, 1080, 100, -8),
         ('s7', T['v']+.25, '🤑', 480, 300, 120, -10), ('s7', T['v']+.55, '💰', 120, 860, 110, 10),
         ('s8', T['s8']+.6, '👀', 490, 230, 110, -8), ('s8', T['s8']+1.0, '🍿', 110, 1040, 110, 10),
         ('s9', T['buy']+.15, '👇', 505, 625, 80, -6)]
# réactions qui montent à côté du téléphone (comme des réactions en direct)
FLOAT = [(0.3, '😱', 905), (11.3, '😂', 905), (11.55, '😂', 950), (11.8, '😂', 880), (T['b76']+.2, '💀', 170), (T['x8']+.1, '🚀', 910),
         (T['v']+.2, '💰', 175), (T['v']+.4, '🤑', 905)]
def floats(cv, t):
    for t0, ch, x in FLOAT:
        k = t-t0
        if 0 <= k < 1.8:
            y = 1150-k*520; a = clamp(k/.15)*clamp((1.8-k)/.5); sz = int(110*(.8+.25*math.sin(k*3)))
            e = with_alpha(emoji(ch, sz).rotate(10*math.sin(k*4+x), resample=Image.BICUBIC, expand=True), a)
            cv.alpha_composite(e, (int(x+30*math.sin(k*3+x)-e.width/2), int(y-e.height/2)))

def story_img(t):
    cur = [s for s in STORIES if T[s] <= t][-1]; idx = STORIES.index(cur)
    def draw(name, tt):
        s, c = surf(SW, SH); FN[name](c, tt, tt-T[name]); i = STORIES.index(name)
        header(c, i, clamp((tt-T[name])/(NXT[name]-T[name]))); im_ = pil(s)
        for st_, t0, ch, x, y, sz, rot in STICK:
            if st_ == name: paste_emoji(im_, ch, x, y, sz, tt-t0, rot, tt)
        return im_
    im = draw(cur, t)
    # transition « glisser » entre stories (0,28 s)
    k = t-T[cur]
    if idx > 0 and k < .28:
        u = inout(k/.28); prev = draw(STORIES[idx-1], T[cur]-.001)
        out = Image.new('RGBA', (SW, SH), (0, 0, 0, 255)); out.alpha_composite(prev, (int(-SW*u), 0)); out.alpha_composite(im, (int(SW*(1-u)), 0)); im = out
    return im
_yy, _xx = np.mgrid[0:H, 0:W]
VIG = (0.42+0.5*np.clip(1-np.sqrt(((_xx-540)/760.)**2+((_yy-880)/980.)**2), 0, 1)**0.8)[..., None].astype(np.float32)   # décor plus sombre, téléphone mis en valeur
@functools.lru_cache(maxsize=1)
def screen_mask():
    s, c = surf(SW, SH); rr(c, 0, 0, SW, SH, 86); col(c, WHITE); c.fill(); return pil(s).split()[3]

GLOW = {'hook': ("328 €", RD), 's2': ("DE FACEBOOK À META", BL2), 's3': ("MÉTAVERS", BL2), 's4': ("−76 %", RD), 's5': ("CAP SUR L'IA", BL2),
        's6': ("×8", GR), 's7': ("2 278 €", GR), 's8': ("RÉSULTATS MERCREDI", AMB), 's9': ("TU ACHÈTES ?", GR)}
GC = {RD: ('FFFFFF', 'FF9AA6', 'FF4057'), GR: ('FFFFFF', '9DFFC6', '2FD27A'), BL2: ('FFFFFF', 'BFD8FF', '3D8BFF'), AMB: ('FFFFFF', 'FFD98A', 'FFB020')}
SHAKES = [(0.0, 12), (T['meta'], 8), (T['b76'], 14), (T['x8'], 10), (T['v'], 14)]

def frame(t):
    bgim, quad = phone_frame(t)
    # zoom d'ouverture + respiration lente
    z = 1.0+.03*math.sin(t*.4)+(.12*(1-ease(t/.5)) if t < .5 else 0)
    if abs(z-1) > .002:
        w, h = int(W*z), int(H*z); bgim = bgim.resize((w, h), Image.BILINEAR).crop(((w-W)//2, (h-H)//2, (w-W)//2+W, (h-H)//2+H))
        quad = [((x-540)*z+540, (y-960)*z+960) for x, y in quad]
    bgim = Image.fromarray((np.asarray(bgim, np.float32)*VIG).clip(0, 255).astype(np.uint8))
    cv = bgim.convert('RGBA')
    # écran : contenu de la story en perspective, puis reflets du verre ajoutés par-dessus
    st = story_img(t); st.putalpha(screen_mask())
    cf = coeffs(quad, [(0, 0), (SW, 0), (SW, SH), (0, SH)])
    warped = st.transform((W, H), Image.PERSPECTIVE, cf, Image.BICUBIC)
    refl = np.asarray(bgim, np.float32); m = np.asarray(warped.split()[3], np.float32)[..., None]/255
    base = np.asarray(cv, np.float32)[..., :3]; content = np.asarray(warped, np.float32)[..., :3]
    lum = refl.max(axis=2, keepdims=True); hi = np.clip((lum-40)/215, 0, 1)*refl*.9    # reflets : seulement les zones claires du verre
    out = base*(1-m)+content*m          # écran parfaitement lisible : aucun reflet sur la dalle (les reflets restent sur le cadre)
    cv = Image.fromarray(out.astype(np.uint8)).convert('RGBA')
    floats(cv, t)
    darken_band(cv, 1440, 1640, .55)
    s, c = surface()
    cur = [n for n in STORIES if T[n] <= t][-1]; k = t-T[cur]
    lab, cl = GLOW[cur]; top, bot, glw = GC[cl]
    g0 = {'s2': T['meta'], 's4': T['b76'], 's6': T['x8'], 's7': T['v']}.get(cur, T[cur]); k = t-g0
    a = 1.0 if (cur == 'hook' and t < 1) else ease(k/.25)*(k >= 0)
    a *= clamp((NXT[cur]-t)/.2) if cur != 's9' else 1
    if cur != 's9': glow_text(cv, lab, 540, 190, 108 if len(lab) < 9 else 78, top=top, bottom=bot, glow=glw, ga=.6, a=a, scale=lerp(1.25, 1, back(k/.4)) if cur != 'hook' else lerp(1.25, 1, back(t/.45)), reflect=False)
    kk = cap_at(t)
    if kk is not None and t < DUR:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, BL2)), 14*(1-al))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(6, 6, 8, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'impact'), (0.0, 'low')]
    for n in STORIES[1:]: ev.append((T[n], 'swish'))
    ev += [(T['meta']-.2, 'click'), (T['meta'], 'pop'), (T['b76']-.9, 'riser'), (T['b76'], 'crash'), (T['b76'], 'impact'), (T['s5']+.4, 'tick'), (T['ia'], 'glint'),
           (T['x8'], 'impact'), (T['v']-.6, 'tick'), (T['v'], 'boom'), (T['v'], 'coins'), (T['s8'], 'pop'), (T['buy'], 'pop'), (T['s9']+1.4, 'click')]
    ev += [(t0, 'pop') for _, t0, *_ in STICK if t0 > .1]
    return ev

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/meta/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'/home/claude/meta/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
