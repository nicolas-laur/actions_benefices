"""PEA ou compte-titres : globe 3D (continents en points) qui s'allume selon l'enveloppe, puis panneaux de verre (5 ans, taux, 10 000 €).
usage : python pm.py png t1 t2 ... | python pm.py seg out.mp4 f0 f1 | python pm.py info"""
import sys, math, re, subprocess, os, functools
import numpy as np, cairo
from PIL import Image
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/meta')
from bglass import *
FPS = 60; NB = ' '
CY = '35D6FF'; CY2 = 'A8EEFF'; GOLD = 'FFC24A'; GOLD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4057'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage calé sur la voix (35,6 s) ----------
T = dict(hook=0.0, offre=2.3, cto=4.85, plaf=7.05, pea=8.15, eur=8.85, etf=9.75, p150=11.85, regle=13.95, avant=14.75, clot=16.25, p314=17.3,
         apres=20.5, p186=21.5, s10k=25.7, gain=27.05, eu=29.95, dpea=31.1, us=32.05, dcto=33.35, toi=34.3, deux=34.9, end=36.9)
DUR = T['end']
CAPS = [(0.0, "[12,8 %] d'impôt en moins."), (T['offre'], "C'est ce que le PEA t'offre face au compte-titres."),
        (T['cto'], "Le compte-titres t'ouvre le [monde entier],"), (T['plaf'], "[sans plafond]."),
        (T['pea'], "Le PEA, c'est l'[Europe]…"), (T['etf'], "ou le monde via des [ETF éligibles],"), (T['p150'], "jusqu'à [150 000 euros] de versements."),
        (T['regle'], "Sa règle : [cinq ans]."), (T['avant'], "Si tu retires avant,"), (T['clot'], "le plan est [clôturé]"), (T['p314'], "et tu paies [31,4 %], comme au compte-titres."),
        (T['apres'], "Après cinq ans,"), (T['p186'], "il ne reste que [18,6 %] de prélèvements sociaux."),
        (T['s10k'], "Sur 10 000 euros de gains,"), (T['gain'], "ça fait [1 280 euros] de plus pour toi."),
        (T['eu'], "Tes actions européennes ?"), (T['dpea'], "Dans le [PEA]."), (T['us'], "Tes actions américaines ?"), (T['dcto'], "Au [compte-titres]."),
        (T['toi'], "Et toi,"), (T['deux'], "tu as [les deux] ?")]
HL = {0.0: GR, T['plaf']: CY, T['cto']: CY, T['eur']: GOLD, T['pea']: GOLD, T['etf']: GOLD, T['p150']: GOLD, T['regle']: GOLD, T['clot']: RD, T['p314']: RD,
      T['p186']: GR, T['gain']: GR, T['dpea']: GOLD, T['dcto']: CY, T['deux']: GR}
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
def caption(c, words, hl, y=1560, size=46, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK if hl in (GR, GOLD, CY) else WHITE, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- globe ----------
D = '/home/claude/pea'; GR_ = 514/600     # rayon du disque dans l'image 1200 (normalisé)
@functools.lru_cache(maxsize=12)
def gimg(kind, t30):
    """image du globe à 30 i/s : tour rapide (4,8-8 s) rendu à 15 i/s, le reste à 7,5 i/s, interpolés par flux optique ; repli sur les rendus bruts"""
    cands = []
    if 144 <= t30 < 240: cands.append(f'{D}/g30s/{kind}/{t30-144:04d}.png')
    cands.append(f'{D}/g30/{kind}/{t30:04d}.png')
    f = int(round(t30/2)); cands += [f'{D}/gl/{kind}/{k:04d}.png' for k in (f, f-1, f+1, f-2, f+2, f-4, f+4)]
    cands.append(f'/tmp/k08/gtest/{kind}/0140.png')
    for p in cands:
        if os.path.exists(p):
            im = Image.open(p)
            if im.mode == 'RGBA': bg = Image.new('RGB', im.size, (0, 0, 0)); bg.paste(im, (0, 0), im); im = bg
            return im.convert('RGB')
@functools.lru_cache(maxsize=4)
def disk(size):
    yy, xx = np.mgrid[0:size, 0:size]; r = np.hypot(xx-size/2+.5, yy-size/2+.5)/(size/2)
    return np.clip((GR_-r)*size*.5, 0, 1).astype(np.float32)[..., None]
def glow_state(t):
    """intensités : monde (cyan), PEA (or), halo du reste du monde (or pâle)"""
    cto = ease((t-T['cto']-.2)/.6)*(1-ease((t-T['pea']+.1)/.4))
    pea = ease((t-T['eur'])/.4)*(1-ease((t-T['regle'])/.6))
    halo = .45*ease((t-T['etf'])/.6)*(1-ease((t-T['regle'])/.6))
    pea += ease((t-T['eu'])/.4)*(1-ease((t-T['us']+.1)/.4))
    cto += .9*ease((t-T['us']-.4)/.5)*(1-ease((t-T['toi'])/.6))
    return cto, pea, halo
def globe_layer(t):
    t30 = int(t*30)
    b = np.asarray(gimg('b', t30), np.float32); m = np.asarray(gimg('m', t30), np.float32)/255
    cto, pea, halo = glow_state(t)
    R, G = m[..., 0:1], m[..., 1:2]
    g = (R*cto*np.array(hx(CY)[:3])+G*pea*np.array(hx(GOLD)[:3])+np.clip(R-G, 0, 1)*halo*np.array(hx(GOLD2)[:3]))*255
    base = b*(1-.55*np.clip(R*cto+G*pea+(R-G).clip(0, 1)*halo, 0, 1))
    col_ = np.clip(base+g*1.1, 0, 255)
    gl = Image.fromarray(col_.astype(np.uint8))
    bloom = lowblur(Image.fromarray(np.clip(g*.9, 0, 255).astype(np.uint8)), 14, 3)
    return gl, bloom
def gplace(t):
    """position / taille / flou / opacité du globe selon la scène"""
    big = (540, 1060, 1180, 0.0, 1.0)
    low = (540, 1500, 1500, 9.0, .45)
    mid = (540, 1020, 1100, 0.0, 1.0)
    if t < T['regle']-.3: s = big;
    elif t < T['eu']-.6:
        u = inout((t-T['regle']+.3)/.8); s = tuple(lerp(a, b, u) for a, b in zip(big, low))
    else:
        u = inout((t-T['eu']+.6)/.8); s = tuple(lerp(a, b, u) for a, b in zip(low, mid))
    x, y, size, blur, al = s
    if t < .6: size *= lerp(1.15, 1, ease(t/.6))
    return x, y, size, blur, al
@functools.lru_cache(maxsize=1)
def bg_base():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('04060B')[:3]); g.add_color_stop_rgb(.55, *hx('070A12')[:3]); g.add_color_stop_rgb(1, *hx('0B0F18')[:3]); c.set_source(g); c.paint()
    rnd = np.random.default_rng(2)
    for k in range(260):   # poussière d'étoiles très discrète
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(.6, 1.6); c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, rnd.uniform(.08, .35)); c.fill()
    return to_img(s).convert('RGB')
def background(t):
    cv = bg_base().copy()
    x, y, size, blur, al = gplace(t); size = int(size)
    gl, bloom = globe_layer(t)
    gl = gl.resize((size, size), Image.BICUBIC); bloom = bloom.resize((size, size), Image.BICUBIC)
    a = disk(size)
    if blur > .5: gl = lowblur(gl, blur, 2)
    # halo d'atmosphère
    s, c = surface(); cto, pea, halo = glow_state(t)
    tint = np.array(hx(CY)[:3])*(.5+cto)+np.array(hx(GOLD)[:3])*pea*.8
    tint = tint/max(1e-6, tint.max())
    R1 = size*GR_*.5*1.2; rg = cairo.RadialGradient(x, y, 0, x, y, R1)
    rg.add_color_stop_rgba(0, *tint, 0); rg.add_color_stop_rgba(.8, *tint, 0); rg.add_color_stop_rgba(.835, *tint, .38*al); rg.add_color_stop_rgba(1, *tint, 0)
    c.set_source(rg); c.arc(x, y, R1, 0, 2*math.pi); c.fill()
    atm = to_img(s)
    arr = np.asarray(cv, np.float32); x0, y0 = int(x-size/2), int(y-size/2)
    gx0, gy0 = max(0, -x0), max(0, -y0); gx1, gy1 = min(size, W-x0), min(size, H-y0)
    if gx1 > gx0 and gy1 > gy0:
        sub = arr[y0+gy0:y0+gy1, x0+gx0:x0+gx1]
        G_ = np.asarray(gl, np.float32)[gy0:gy1, gx0:gx1]; B_ = np.asarray(bloom, np.float32)[gy0:gy1, gx0:gx1]; A_ = a[gy0:gy1, gx0:gx1]*al
        sub[:] = sub*(1-A_)+G_*A_+B_*.8*al
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA'); im.alpha_composite(atm)
    return im

# ---------- emojis ----------
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=64)
def emoji(ch, size):
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def pop_emoji(cv, ch, x, y, size, k, rot=0.0, t=0.0, a=1.0):
    if k < 0 or a <= 0: return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size).rotate(rot+6*math.sin(t*3+x*.01), resample=Image.BICUBIC, expand=True)
    e = with_alpha(e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))), Image.BICUBIC), a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
EMO = [(T['offre']+.4, '🤔', 900, 300, 110, -8, T['cto']), (T['cto']+.3, '🌍', 900, 300, 120, 8, T['pea']), (T['eur']+.1, '🇪🇺', 900, 300, 120, -6, T['regle']),
       (T['regle']+.2, '⏳', 880, 300, 120, 8, T['avant']), (T['clot']+.1, '🔒', 880, 300, 120, -8, T['apres']),
       (T['gain']+.25, '💶', 880, 400, 130, -8, T['eu']), (T['dpea']+.1, '🇪🇺', 900, 290, 110, -6, T['us']), (T['dcto']+.1, '🇺🇸', 900, 290, 110, 6, T['toi']),
       (T['deux']+.25, '😏', 540, 880, 120, -6, DUR+1)]

# ---------- éléments ----------
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def pill(c, s, x, y, colr, size=36, a=1, fg=INK):
    w = tw(c, s, 'xb', size, 2)+64; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
def sHook(cv, c, t, a):
    glow_text(cv, "−12,8 %", 540, 330, 210, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.75, a=a, scale=lerp(1.3, 1, back(t/.45, 1.3)))
    grp(c, a*ease((t-.9)/.3), lambda c: text(c, "D'IMPÔT", 540, 500, 'xb', 42, WHITE, 'c', 1, 4))
    k = t-T['offre']
    if k > 0:
        def vs(c):
            pill(c, "PEA", 330, 610, GOLD, 40); text(c, "VS", 540, 612, 'xb', 34, ICE, 'c', 1, 2); pill(c, "COMPTE-TITRES", 760, 610, CY, 32)
        grp(c, a*ease(k/.3), vs, 20*(1-ease(k/.3)))
def sCTO(cv, c, t, a):
    k = t-T['cto']
    grp(c, a*ease(k/.3), lambda c: pill(c, "COMPTE-TITRES", 540, 250, CY, 40), 20*(1-ease(k/.3)))
    grp(c, a*ease((k-.3)/.3), lambda c: text(c, "LE MONDE ENTIER", 540, 380, 'a', 96, WHITE, 'c'))
    kp = t-T['plaf']
    if kp > 0: grp(c, a*ease(kp/.3), lambda c: text(c, "SANS PLAFOND", 540, 470, 'xb', 40, CY2, 'c', 1, 4))
def sPEA(cv, c, t, a):
    k = t-T['pea']
    grp(c, a*ease(k/.3), lambda c: pill(c, "PEA", 540, 250, GOLD, 44), 20*(1-ease(k/.3)))
    ke = t-T['eur']
    if ke > 0: glow_text(cv, "L'EUROPE", 540, 400, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=a*ease(ke/.3)*(1-.4*ease((t-T['etf'])/.4)), scale=lerp(1.25, 1, back(ke/.4)))
    kt = t-T['etf']
    if kt > 0:
        def d(c):
            text(c, "UE + ISLANDE, NORVÈGE, LIECHTENSTEIN", 540, 480, 'xb', 26, GOLD2, 'c', 1, 2)
            text(c, "+ LE MONDE VIA DES ETF ÉLIGIBLES", 540, 530, 'xb', 30, WHITE, 'c', 1, 2)
        grp(c, a*ease(kt/.3), d)
    kp = t-T['p150']
    if kp > 0:
        def d2(c):
            w = 560; rr(c, 540-w/2, 575, w, 66, 33); col(c, '000000', .5); c.fill(); text(c, "PLAFOND : 150 000 € VERSÉS", 540, 609, 'xb', 32, GOLD, 'c', 1, 2)
        grp(c, a*ease(kp/.3), d2)
def sRule(cv, c, t, a):
    k = t-T['regle']
    def d(kk, w, h):
        text(kk, "PEA · LA RÈGLE DES 5 ANS", w/2, 64, 'sb', 26, GOLD, 'c', 1, 3)
        X0, X1, Y = 70, w-70, 190; seg = (X1-X0)/5
        prog = clamp((t-T['regle']-.2)/1.2)*5
        if t >= T['avant']: prog = min(prog, 2.6)
        for i in range(5):
            x = X0+i*seg+6; ww = seg-12; f = clamp(prog-i)
            rr(kk, x, Y-22, ww, 44, 10); col(kk, 'FFFFFF', .10); kk.fill()
            if f > 0: rr(kk, x, Y-22, ww*f, 44, 10); col(kk, RD if t >= T['clot'] else GOLD, .95); kk.fill()
            text(kk, f"AN {i+1}", x+ww/2, Y+56, 'xb', 22, ICE, 'c', .8, 2)
        if t >= T['avant']:
            ka = t-T['avant']; xm = X0+2.6*seg
            kk.set_line_width(4); col(kk, WHITE, ease(ka/.3)); kk.move_to(xm, Y-60); kk.line_to(xm, Y+30); kk.stroke()
            text(kk, "RETRAIT", xm, Y-80, 'xb', 24, WHITE, 'c', ease(ka/.3), 2)
        if t >= T['clot']:
            kc = t-T['clot']; s_ = lerp(1.4, 1, back(kc/.35))
            kk.save(); kk.translate(w/2, 380); kk.rotate(-.08); kk.scale(s_, s_)
            ww = 440; kk.set_line_width(6); col(kk, RD, ease(kc/.2)); rr(kk, -ww/2, -46, ww, 92, 14); kk.stroke()
            text(kk, "PLAN CLÔTURÉ", 0, 2, 'a', 64, RD, 'c', ease(kc/.2)); kk.restore()
    e = ease(k/.45)
    place(cv, gp(860, 500, d, 'FFE9C0'), tilt_quad(540, 560+50*(1-e), 860, 500, ry=-.12-.3*(1-e), rx=.06), a*e, 14, .55)
    kp = t-T['p314']
    if kp > 0:
        glow_text(cv, "31,4 %", 540, 1000, 200, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.7, a=a*ease(kp/.25), scale=lerp(1.35, 1, back(kp/.4)))
        grp(c, a*ease((kp-1.9)/.3), lambda c: text(c, "COMME AU COMPTE-TITRES", 540, 1140, 'xb', 34, WHITE, 'c', 1, 3))
def sRates(cv, c, t, a):
    k = t-T['apres']
    def card(name, colr, tint, ir, ps, sub, kk_t):
        def d(kk, w, h):
            text(kk, name, w/2, 62, 'xb', 32, colr, 'c', 1, 3)
            YB, HB = 600, 440; X = w/2-70; WB = 140
            u = ease((t-kk_t)/.9)
            hps = HB*ps/31.4*u; hir = HB*ir/31.4*u
            rr(kk, X, YB-hps, WB, hps, 10); col(kk, CY2 if colr == CY else GOLD2, .85); kk.fill()
            if ir > 0: rr(kk, X, YB-hps-hir, WB, hir, 10); col(kk, RD, .9); kk.fill()
            tot = (ir+ps)*u
            text(kk, f"{tot:.1f} %".replace('.', ','), w/2, YB-hps-hir-40, 'a', 70, WHITE, 'c')
            text(kk, sub, w/2, h-80, 'xb', 22, ICE, 'c', .85, 1)
            text(kk, "■ PRÉL. SOCIAUX 18,6 %" if ir == 0 else "■ IMPÔT 12,8 % + PS 18,6 %", w/2, h-40, 'xb', 20, GOLD2 if ir == 0 else RD, 'c', .9, 1)
        return gp(440, 760, d, tint)
    e1 = ease(k/.45); e2 = ease((t-T['p186']+.3)/.45)
    place(cv, card("COMPTE-TITRES", CY, 'CFE8FF', 12.8, 18.6, "CHAQUE ANNÉE, SANS CONDITION", T['apres']+.1), tilt_quad(290, 760+50*(1-e1), 440, 760, ry=.16+.3*(1-e1), rx=.05), a*e1, 14, .55)
    if t > T['p186']-.3:
        place(cv, card("PEA · APRÈS 5 ANS", GOLD, 'FFE9C0', 0.0, 18.6, "0 % D'IMPÔT SUR LE REVENU", T['p186']+.2), tilt_quad(790, 760+50*(1-e2), 440, 760, ry=-.16-.3*(1-e2), rx=.05), a*e2, 14, .55)
    kd = t-T['p186']-1.6
    if kd > 0:
        def dd(c):
            w = 420; rr(c, 540-w/2, 1210, w, 76, 38); col(c, GR, a); c.fill(); text(c, "−12,8 POINTS", 540, 1249, 'xb', 40, INK, 'c', 1, 2)
        grp(c, a*ease(kd/.3), dd, 20*(1-ease(kd/.3)))
def sGain(cv, c, t, a):
    k = t-T['s10k']
    def d(kk, w, h):
        text(kk, "10 000 € DE PLUS-VALUES", w/2, 70, 'xb', 34, WHITE, 'c', 1, 3)
        for i, (name, colr, tax, net) in enumerate((("COMPTE-TITRES", CY, 3140, 6860), ("PEA (+5 ANS)", GOLD, 1860, 8140))):
            y = 190+i*150; u = ease((t-T['s10k']-.4-i*.35)/.6)
            text(kk, name, 50, y, 'xb', 28, colr, 'l', u, 2)
            text(kk, f"IMPÔTS  −{int(tax*u):,} €".replace(',', ' '), w-50, y, 'xb', 28, RD, 'r', u, 1)
            text(kk, f"TU GARDES  {int(net*u):,} €".replace(',', ' '), w-50, y+52, 'xb', 28, WHITE, 'r', u, 1)
    e = ease(k/.45)
    place(cv, gp(860, 470, d), tilt_quad(540, 520+50*(1-e), 860, 470, ry=.12+.3*(1-e), rx=.06), a*e, 14, .55)
    kg = t-T['gain']
    if kg > -.4:
        v = int(1280*ease(clamp((kg+.4)/.8)))
        glow_text(cv, f"+{v:,} €".replace(',', ' '), 540, 960, 200, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.75, a=a*ease((kg+.4)/.25), scale=lerp(1, 1.08, ease(kg/.2)) if 0 < kg < .2 else (lerp(1.08, 1, ease((kg-.2)/.3)) if kg >= .2 else 1))
        grp(c, a*ease((kg-.3)/.3), lambda c: text(c, "DANS TA POCHE", 540, 1100, 'xb', 36, WHITE, 'c', 1, 4))
def sEnd(cv, c, t, a):
    ke = t-T['eu']
    def tags(c):
        if t < T['us']-.15:
            u = ease(ke/.3); text(c, "ACTIONS EUROPÉENNES", 540, 300, 'a', 76, WHITE, 'c', u)
            if t > T['dpea']: pill(c, "→ PEA", 540, 420, GOLD, 44, ease((t-T['dpea'])/.25))
        else:
            u = ease((t-T['us'])/.3)*(1-ease((t-T['toi']+.15)/.25)); text(c, "ACTIONS AMÉRICAINES", 540, 300, 'a', 76, WHITE, 'c', u)
            if t > T['dcto']: pill(c, "→ COMPTE-TITRES", 540, 420, CY, 40, ease((t-T['dcto'])/.25)*(1-ease((t-T['toi']+.15)/.25)))
    grp(c, a, tags)
def sCta(cv, c, t, a):
    k = t-T['toi']
    glow_text(cv, "ET TOI,", 540, 330, 130, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.3))
    kb = t-T['deux']
    glow_text(cv, "TU AS LES DEUX ?", 540, 490, 120, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kb/.3), scale=lerp(1.3, 1, back(kb/.4)))
    al = ease((kb-.3)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 640, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 640, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)

SCENES = [(sHook, 0.0, T['cto']), (sCTO, T['cto']-.1, T['pea']), (sPEA, T['pea']-.1, T['regle']), (sRule, T['regle']-.1, T['apres']),
          (sRates, T['apres']-.1, T['s10k']), (sGain, T['s10k']-.1, T['eu']), (sEnd, T['eu']-.1, T['toi']), (sCta, T['toi']-.1, DUR+1)]
SHAKES = [(0.0, 14), (T['clot'], 12), (T['p314'], 14), (T['gain'], 14)]
def frame(t):
    cv = background(t)
    darkspot(cv, 540, 420, 760, 420, .35); darken_band(cv, 1450, 1680, .55)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    kk = cap_at(t)
    if kk is not None and t < DUR-1.3:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, GOLD)), 14*(1-al))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(4, 6, 11, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'impact'), (0.0, 'low'), (T['offre'], 'swish'), (T['cto'], 'swish'), (T['cto']+.2, 'riser'), (T['plaf'], 'pop'), (T['pea'], 'swish'), (T['eur'], 'glint'),
          (T['etf'], 'pop'), (T['p150'], 'pop'), (T['regle'], 'swish'), (T['regle']+.2, 'tick'), (T['avant'], 'click'), (T['clot'], 'thud'), (T['p314'], 'impact'),
          (T['apres'], 'swish'), (T['p186']-.1, 'tick'), (T['p186']+1.6, 'glint'), (T['s10k'], 'swish'), (T['gain']-.4, 'tick'), (T['gain'], 'boom'), (T['gain'], 'coins'),
          (T['eu'], 'swish'), (T['dpea'], 'pop'), (T['us'], 'swish'), (T['dcto'], 'pop'), (T['toi'], 'swish'), (T['deux'], 'pop'), (T['deux']+.3, 'click')]
    ev += [(e[0], 'pop') for e in EMO if e[0] > .1]
    return ev

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
