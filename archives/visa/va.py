"""Visa : le péage invisible. Carte métal 3D, studio bleu nuit et or, 60 i/s, ~63 s."""
import sys, math, re, subprocess, functools, random, os
import numpy as np, cairo
from PIL import Image, ImageEnhance, ImageOps
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/visa')
from vty import W, H, GOLD, GOLDG, WH, GR, GREEN, RED, hx, col, tw, text, gtext, rr, kicker, rule, pill
FPS = 60
B3D = '/home/claude/visa/b3d'
REDG = [(0, 'FF9A8A'), (.5, 'FF5A4E'), (1, 'B8261C')]

# ---------- chiffres vérifiés (11 octobre 2026) ----------
P0, FX0, P1, FX1 = 225.11, 1.1569, 385.45, 1.1177
DIVS = [.375]*4+[.45]*4+[.52]*4+[.59]*4+[.67]*4
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*sum(DIVS)/FX1; TOT = VAL+DIV
assert round(TOT, -1) == 1820 and round(VAL) == 1772 and round(DIV) == 48
TPS = 71.7e9/(91*86400)                  # transactions par seconde, avril-juin 2026
assert 9050 < TPS < 9150
assert round(385.45/(44/4)) == 35       # IPO 44 $ en 2008, division par 4 en 2015

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')

CAPS = [
 ("c01", "Chaque fois que tu paies par carte, quelqu'un [encaisse]."),
 ("c02", "Et ce n'est pas seulement ta banque : c'est [Visa]."),
 ("c03", "Et 1 000 € investis il y a 5 ans ? Réponse à la [fin]."),
 ("c04", "Visa ne prête [pas un centime]."),
 ("c05", "Son réseau relie ta banque à celle du commerçant… et prend sa [commission]."),
 ("c06", "Un [péage invisible] sur tes paiements."),
 ("c07", "Avril-juin 2026 : [72 milliards] de transactions."),
 ("c08", "Soit ≈ [9 100 par seconde]."),
 ("c09", "Plus de [4 000 milliards $] de paiements en 3 mois."),
 ("c10", "Revenus : [11,6 milliards $]. +14 % sur un an."),
 ("c11", "Sur 1 $ de revenus, ≈ [48 centimes] de bénéfice net."),
 ("c12", "[1958] : une banque envoie 65 000 cartes à Fresno, en Californie."),
 ("c13", "[2008] : en pleine crise, la plus grosse entrée en Bourse de l'époque."),
 ("c14", "Depuis son prix d'introduction : ≈ [×35]."),
 ("c15", "Le 9 octobre : [385 $], son plus haut sur un an."),
 ("c16", "Mais cet été : [2 600 postes] supprimés."),
 ("c17", "La justice américaine l'accuse de [monopole] sur le débit."),
 ("c18", "Et stablecoins et IA pourraient [rebattre les cartes]."),
 ("c19", "Tes 1 000 € ? ≈ [1 820 €], dividendes compris. ×1,82."),
 ("c20", "Péage éternel… ou [péage menacé] ?"),
 ("c21", "Et toi : tu achètes, tu vends ou tu [attends] ?"),
 ("c22", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '')
        d = max(3.1, len(clean)/20+1.15)        # rythme v3 : temps de lire titre, carte et sous-titre
        if cid in ('c05', 'c14', 'c18', 'c20'): d += 0.6
        if cid == 'c01': d = 4.2
        if cid == 'c19': d += 1.6
        if cid == 'c21': d += 0.8
        if cid == 'c22': d = 3.6
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.1
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def E(c): return TL[c][0]+TL[c][1]
NB = ' '
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]

# ---------- fonds : (séquence, mode, zoom départ, zoom fin, dx, dy, étalonnage) ----------
SCN = {
 'c01': ('tap', 'once', 1.00, 1.05, 0, 0, None), 'c02': ('spin', 'loop', 1.02, 1.08, 0, 0, None), 'c03': ('spin', 'loop', 1.10, 1.04, 0.02, 0, None),
 'c04': ('spin', 'loop', 1.18, 1.10, -0.03, 0.02, None), 'c05': ('tap', 'once', 1.06, 1.00, 0, 0, None), 'c06': ('stackend', 'hold', 1.02, 1.07, 0, 0, None),
 'c07': ('spin', 'loop', 1.04, 1.10, 0, 0, None), 'c08': ('spin', 'loop', 1.22, 1.14, 0.02, 0.03, None), 'c09': ('spin', 'loop', 1.06, 1.0, 0, 0, None),
 'c10': ('tapend', 'hold', 1.0, 1.06, 0, 0, None), 'c11': ('spin', 'loop', 1.12, 1.05, -0.02, 0, None),
 'c12': ('spin', 'loop', 1.05, 1.12, 0, 0, 'archive'), 'c13': ('spin', 'loop', 1.12, 1.05, 0, 0, 'archive'), 'c14': ('spin', 'loop', 1.0, 1.06, 0, 0, None),
 'c15': ('spin', 'loop', 1.08, 1.02, 0, 0, None), 'c16': ('dark', 'loop', 1.02, 1.08, 0, 0, None), 'c17': ('dark', 'loop', 1.12, 1.05, 0.02, 0, None),
 'c18': ('dark', 'loop', 1.05, 1.12, -0.02, 0, None), 'c19': ('stack', 'once', 1.0, 1.04, 0, 0, None), 'c20': ('spin', 'loop', 1.04, 1.10, 0, 0, None),
 'c21': ('end', None, 1, 1, 0, 0, None), 'c22': ('end', None, 1, 1, 0, 0, None)}
NSEQ = {'tap': 90, 'spin': 60, 'dark': 48, 'stack': 110}
KEYG = {'dark': REDG}

@functools.lru_cache(maxsize=40)
def src(name, i):
    p = f'{B3D}/seq_{name}/f{i+1:04d}.png'
    if not os.path.exists(p):    # aperçu provisoire
        p = {'tap': f'{B3D}/kf_k1.png', 'stack': f'{B3D}/kf_k3.png'}.get(name, f'{B3D}/kf_k2.png')
    return Image.open(p).convert('RGBA')
@functools.lru_cache(maxsize=2)
def end_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); col(c, '03050C'); c.paint()
    g = cairo.RadialGradient(540, 1400, 0, 540, 1400, 1300); g.add_color_stop_rgba(0, *hx('1A2C6B', .8)); g.add_color_stop_rgba(.5, *hx('0B1430', .6)); g.add_color_stop_rgba(1, *hx('000000', 0)); c.set_source(g); c.paint()
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
def kb(im, z, dx=0.0, dy=0.0):
    w, h = im.size; cw, ch = w/z, h/z
    x0 = min(max(0, (w-cw)/2+dx*w), w-cw); y0 = min(max(0, (h-ch)/2+dy*h), h-ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0+cw, y0+ch))
def seq_at(name, fpos, mode):
    n = NSEQ[name]
    if mode == 'loop': fpos = fpos % n; i = int(fpos); j = (i+1) % n
    else:
        if fpos > n-1:   # tenue finale en aller-retour lent sur les 24 dernières images
            k = (fpos-(n-1))*0.5; m = 24; ph = k % (2*m); fpos = n-1-(ph if ph < m else 2*m-ph)
        i = int(fpos); j = min(i+1, n-1)
    fr = fpos-int(fpos); a = src(name, i)
    return Image.blend(a, src(name, j), fr) if fr > 0.02 else a
def background(cid, t):
    name, mode, z0, z1, dx, dy, grade = SCN[cid]; a, d = TL[cid]; u = clamp((t-a)/(d+0.3))
    if name == 'end': return end_bg().copy()
    if name == 'tapend': base = seq_at('tap', 60+(t-a)*15, 'once')
    elif name == 'stackend': base = seq_at('stack', 85+(t-a)*15, 'once')
    elif mode == 'loop': base = seq_at(name, t*15, 'loop')          # boucles rendues à 15 i/s, fondues
    else: base = seq_at(name, (t-a)*30+(30 if name == 'stack' else 0), 'once')
    im = kb(base, lerp(z0, z1, inout(u)), dx, dy)
    sh = {'spin': 150, 'dark': 150, 'stack': 400, 'stackend': 400}.get(name, 0)
    if sh:     # descend la carte pour libérer la zone des titres
        top = im.crop((0, 0, W, 1)).resize((W, sh)); im2 = Image.new('RGBA', (W, H)); im2.paste(top, (0, 0)); im2.paste(im.crop((0, 0, W, H-sh)), (0, sh)); im = im2
    if grade == 'archive':
        g = ImageOps.grayscale(im.convert('RGB')); im = ImageOps.colorize(g, (8, 6, 4), (235, 205, 150)).convert('RGBA')
        im = ImageEnhance.Contrast(im).enhance(1.15)
    return im

# ---------- animation ----------
def reveal(c, t, t0, draw, d=0.45, rise=26):
    u = ease((t-t0)/d)
    if u <= 0: return
    c.save(); c.translate(0, rise*(1-u)); c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(u); c.restore()
def zoomin(c, t, t0, x, y, draw, d=0.35, s0=1.5):
    u = clamp((t-t0)/d)
    if u <= 0: return
    s = lerp(s0, 1, ease(u)); c.save(); c.translate(x, y); c.scale(s, s); c.translate(-x, -y); c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(clamp(u*2.5)); c.restore()
def shine(c, t, t0, y, size):
    """reflet qui balaie un texte or (appliqué en ATOP sur le groupe courant)"""
    u = (t-t0-0.3)/1.0
    if 0 < u < 1:
        c.set_operator(cairo.OPERATOR_ATOP); g = cairo.LinearGradient(80+920*u-160, y-size, 80+920*u+160, y+size)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(.5, 1, .97, .9, .6); g.add_color_stop_rgba(1, 1, 1, 1, 0); c.set_source(g); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
def big(c, s, y, size, stops=None, t=None, t0=None, color=WH):
    while tw(c, s, 'k', size) > 900: size -= 6
    c.push_group()
    if stops: gtext(c, s, 540, y, 'k', size, stops)
    else: text(c, s, 540, y, 'k', size, color)
    if stops and t is not None: shine(c, t, t0, y, size)
    c.pop_group_to_source(); c.paint()
def approx_big(c, s, y, size, stops=GOLDG):
    w1 = tw(c, "≈ ", 'xb', size*0.5); w2 = tw(c, s, 'k', size); x0 = 540-(w1+w2)/2
    text(c, "≈", x0, y, 'xb', size*0.5, WH, 'l'); gtext(c, s, x0+w1, y, 'k', size, stops, 'l')
def sub(c, s, y, color=GR, size=32, f='sb', track=3): text(c, s, 540, y, f, size, color, 'c', 1, track, False)

def draw_caption(c, t, cid):
    a, d = TL[cid]; b = a+d; size = 46; kst = KEYG.get(SCN[cid][0], GOLDG)
    items = parse(dict(CAPS)[cid]); sp = tw(c, ' ', 'p', size); wd = [tw(c, w, 'p', size) for w, _ in items]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 790: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = 1352-(len(lines)-1)*36
    # voile de lisibilité
    vg = cairo.RadialGradient(540, y0+36, 0, 540, y0+36, 560); vg.add_color_stop_rgba(0, 0, 0, .02, .55); vg.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.save(); c.scale(1, 0.32); c.translate(0, (y0+36)*(1/0.32-1)); c.set_source(vg); c.paint(); c.restore()
    fo = 1-clamp((t-(b-0.15))/0.15); n_ = 0
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; y = y0+li*72
        for i in idx:
            w, k = items[i]; ti = a+n_*0.04; n_ += 1; u = ease((t-ti)/0.3); al = clamp((t-ti)/0.18)*fo
            if al > 0:
                c.push_group(); yy = y+12*(1-u)
                if k: gtext(c, w, x, yy, 'p', size, kst, 'l')
                else: text(c, w, x, yy, 'p', size, WH, 'l')
                c.pop_group_to_source(); c.paint_with_alpha(al)
            x += wd[i]+sp

def flow(c, t, a):
    """schéma : toi → ta banque → réseau → banque du commerçant → commerçant, avec une impulsion dorée"""
    nodes = [("TOI", 180), ("TA BANQUE", 360), ("RÉSEAU", 540), ("SA BANQUE", 720), ("COMMERÇANT", 900)]
    y = 600; u = clamp((t-a-0.3)/1.6)
    rr(c, 110, y-150, 860, 260, 28); col(c, '060A18', .78); c.fill(); rr(c, 110, y-150, 860, 260, 28); col(c, GOLD, .25); c.set_line_width(1.5); c.stroke()
    c.set_line_width(3); col(c, 'FFFFFF', .22); c.move_to(180, y); c.line_to(900, y); c.stroke()
    col(c, GOLD); c.move_to(180, y); c.line_to(180+720*u, y); c.stroke()
    for j, (lab, x) in enumerate(nodes):
        on = u*720 >= x-180-1; r = 26 if lab == "RÉSEAU" else 18
        c.arc(x, y, r, 0, 2*math.pi); col(c, '0A1228'); c.fill_preserve(); col(c, GOLD if on else 'FFFFFF', 1 if on else .35); c.set_line_width(3); c.stroke()
        text(c, lab, x, y+(55 if j % 2 == 0 else 92), 'sb', 22 if lab != "COMMERÇANT" else 20, GOLD if lab == "RÉSEAU" else WH, 'c', 1, 2, False)
    # la commission tombe dans « RÉSEAU »
    if t > a+0.3+0.8:
        v = clamp((t-a-1.1)/0.5); c.save(); c.translate(540, y-100*(1-ease(v))-112); c.push_group(); pill(c, "+ commission", 0, 0, 26); c.pop_group_to_source(); c.paint_with_alpha(v); c.restore()

def overlay(c, cid, t):
    a, d = TL[cid]; TAP = 34/30
    if cid == 'c01':
        reveal(c, t, a, lambda k: (kicker(k, "CHAQUE FOIS QUE TU PAIES"), rule(k)))
        reveal(c, t, a+TAP-0.1, lambda k: text(k, "QUELQU'UN", 540, 500, 'k', 120, WH))
        zoomin(c, t, a+TAP+0.15, 540, 640, lambda k: big(k, "ENCAISSE", 640, 130, GOLDG, t, a+TAP+0.15))
    elif cid == 'c02':
        reveal(c, t, a, lambda k: (kicker(k, "ET CE N'EST PAS SEULEMENT TA BANQUE"), rule(k)))
        zoomin(c, t, a+0.6, 540, 520, lambda k: big(k, "VISA", 520, 230, GOLDG, t, a+0.6))
    elif cid == 'c03':
        reveal(c, t, a, lambda k: (kicker(k, "1 000 € INVESTIS EN OCTOBRE 2021"), rule(k)))
        reveal(c, t, a+0.2, lambda k: big(k, "1 000 €", 500, 180))
        reveal(c, t, a+0.6, lambda k: big(k, "?", 680, 160, GOLDG))
    elif cid == 'c04':
        reveal(c, t, a, lambda k: (kicker(k, "ARGENT PRÊTÉ PAR VISA"), rule(k)))
        zoomin(c, t, a+0.15, 540, 520, lambda k: big(k, "0 €", 520, 240, GOLDG, t, a+0.15))
        reveal(c, t, a+0.6, lambda k: sub(k, "AUCUN CRÉDIT · AUCUN RISQUE D'IMPAYÉ", 680))
    elif cid == 'c05':
        reveal(c, t, a, lambda k: (kicker(k, "COMMENT ÇA MARCHE"), rule(k)))
        reveal(c, t, a+0.1, lambda k: flow(k, t, a))
    elif cid == 'c06':
        reveal(c, t, a, lambda k: (kicker(k, "LE MODÈLE"), rule(k)))
        reveal(c, t, a+0.1, lambda k: text(k, "PÉAGE", 540, 500, 'k', 170, WH))
        zoomin(c, t, a+0.45, 540, 650, lambda k: big(k, "INVISIBLE", 650, 120, GOLDG, t, a+0.45))
    elif cid == 'c07':
        reveal(c, t, a, lambda k: (kicker(k, "AVRIL-JUIN 2026"), rule(k)))
        v = lerp(0, 72, ease((t-a-0.1)/1.1))
        reveal(c, t, a+0.1, lambda k: text(k, f"{int(round(v))}", 540, 520, 'k', 250, WH))
        reveal(c, t, a+0.3, lambda k: big(k, "MILLIARDS", 690, 104, GOLDG, t, a+0.3))
        reveal(c, t, a+0.5, lambda k: sub(k, "DE TRANSACTIONS EN 3 MOIS", 780))
    elif cid == 'c08':
        reveal(c, t, a, lambda k: (kicker(k, "TRANSACTIONS TRAITÉES PAR VISA"), rule(k)))
        reveal(c, t, a+0.1, lambda k: approx_big(k, "9 100", 510, 200))
        reveal(c, t, a+0.3, lambda k: sub(k, "PAR SECONDE", 650, WH, 40, 'xb', 6))
        n = TPS*max(0, t-a-0.4)
        reveal(c, t, a+0.5, lambda k: (sub(k, "DEPUIS LE DÉBUT DE CETTE PHRASE", 1060, GR, 24), text(k, "+ "+fmt(n), 540, 1120, 'k', 64, GOLD, 'c', 1, 0, False)))
    elif cid == 'c09':
        reveal(c, t, a, lambda k: (kicker(k, "VOLUME DE PAIEMENTS · 3 MOIS"), rule(k)))
        v = lerp(0, 4000, ease((t-a-0.1)/1.1))
        reveal(c, t, a+0.1, lambda k: big(k, fmt(round(v, -1)), 510, 210))
        reveal(c, t, a+0.3, lambda k: big(k, "MILLIARDS $", 670, 96, GOLDG, t, a+0.3))
        reveal(c, t, a+0.6, lambda k: sub(k, "UNE PREMIÈRE DANS SON HISTOIRE", 760))
    elif cid == 'c10':
        reveal(c, t, a, lambda k: (kicker(k, "REVENUS · AVRIL-JUIN 2026"), rule(k)))
        v = lerp(0, 11.6, ease((t-a-0.1)/1.0))
        reveal(c, t, a+0.1, lambda k: big(k, f"{v:.1f}".replace('.', ',')+" MD$", 510, 190))
        zoomin(c, t, a+0.9, 540, 670, lambda k: pill(k, "+14 %", 540, 670, 50))
    elif cid == 'c11':
        reveal(c, t, a, lambda k: (kicker(k, "BÉNÉFICE NET · AVRIL-JUIN 2026"), rule(k)))
        def bars(k):
            u = ease((t-a-0.3)/1.0)
            text(k, "1 $ DE REVENUS", 140, 470, 'sb', 28, GR, 'l', 1, 2, False); rr(k, 140, 500, 800, 56, 12); col(k, 'FFFFFF', .14); k.fill()
            text(k, "BÉNÉFICE NET", 140, 610, 'sb', 28, GOLD, 'l', 1, 2, False); rr(k, 140, 640, max(24, 800*0.48*u), 56, 12); col(k, GOLD); k.fill()
            text(k, f"≈ {int(round(48*u))} ¢", 140+800*0.48*u+24, 668, 'k', 52, WH, 'l')
            sub(k, "5,6 MD$ DE BÉNÉFICE POUR 11,6 MD$ DE REVENUS", 760, GR, 24)
        reveal(c, t, a+0.1, bars)
    elif cid == 'c12':
        reveal(c, t, a, lambda k: (kicker(k, "AUX ORIGINES"), rule(k)))
        reveal(c, t, a+0.1, lambda k: big(k, "1958", 510, 230))
        reveal(c, t, a+0.45, lambda k: sub(k, "65 000 CARTES ENVOYÉES PAR LA POSTE", 660, WH, 30))
        reveal(c, t, a+0.6, lambda k: sub(k, "FRESNO, CALIFORNIE", 710, GOLD, 26, 'sb', 6))
    elif cid == 'c13':
        reveal(c, t, a, lambda k: (kicker(k, "INTRODUCTION EN BOURSE"), rule(k)))
        reveal(c, t, a+0.1, lambda k: big(k, "2008", 510, 230))
        reveal(c, t, a+0.45, lambda k: sub(k, "≈ 19 MILLIARDS $ LEVÉS", 660, WH, 32))
        reveal(c, t, a+0.6, lambda k: sub(k, "EN PLEINE CRISE FINANCIÈRE", 710, GOLD, 26, 'sb', 6))
    elif cid == 'c14':
        reveal(c, t, a, lambda k: (kicker(k, "DEPUIS 2008"), rule(k)))
        zoomin(c, t, a+0.15, 540, 520, lambda k: big(k, "×35", 520, 240, GOLDG, t, a+0.15), s0=1.8)
        reveal(c, t, a+0.6, lambda k: sub(k, "11 $  ·  385 $ PAR ACTION", 690, WH, 32))
        reveal(c, t, a+0.7, lambda k: sub(k, "prix d'introduction ajusté de la division par 4 de 2015", 740, GR, 22, 'm', 0))
    elif cid == 'c15':
        reveal(c, t, a, lambda k: (kicker(k, "CLÔTURE DU 9 OCTOBRE 2026"), rule(k)))
        v = lerp(300, 385.45, ease((t-a-0.1)/1.0))
        reveal(c, t, a+0.1, lambda k: big(k, f"{int(v)} $", 510, 220, GOLDG if t > a+1.1 else None, t, a+1.1))
        reveal(c, t, a+0.6, lambda k: sub(k, "PLUS HAUT SUR 52 SEMAINES", 670, WH, 30))
    elif cid == 'c16':
        reveal(c, t, a, lambda k: (kicker(k, "SUPPRESSIONS DE POSTES · ÉTÉ 2026", 350, 'FF8A7E'), rule(k)))
        reveal(c, t, a+0.1, lambda k: big(k, "2 600", 510, 230))
        reveal(c, t, a+0.5, lambda k: sub(k, "≈ 7 % DES EFFECTIFS · 563 M$ D'INDEMNITÉS", 670, WH, 26))
    elif cid == 'c17':
        reveal(c, t, a, lambda k: (kicker(k, "DÉPARTEMENT DE LA JUSTICE DES ÉTATS-UNIS", 350, 'FF8A7E', 22), rule(k)))
        zoomin(c, t, a+0.15, 540, 510, lambda k: big(k, "MONOPOLE ?", 510, 150, REDG))
        reveal(c, t, a+0.6, lambda k: sub(k, "VISA CONTESTE · PROCÈS ATTENDU VERS 2028", 650, WH, 26))
    elif cid == 'c18':
        reveal(c, t, a, lambda k: (kicker(k, "LES NOUVEAUX RIVAUX ?", 350, 'FF8A7E'), rule(k)))
        reveal(c, t, a+0.1, lambda k: text(k, "STABLECOINS", 540, 480, 'k', 110, WH))
        reveal(c, t, a+0.3, lambda k: text(k, "+ AGENTS IA", 540, 600, 'k', 96, 'FF8A7E'))
        reveal(c, t, a+0.7, lambda k: sub(k, "Visa y voit plutôt des relais de croissance", 700, GR, 28, 'm', 0))
    elif cid == 'c19':
        reveal(c, t, a, lambda k: (kicker(k, "TES 1 000 € IL Y A 5 ANS", 350, GOLD, 28), rule(k)))
        v = lerp(1000, TOT, ease((t-a-0.2)/1.3)); s_ = fmt(round(v, -1) if v < TOT-10 else 1820)+" €"
        reveal(c, t, a+0.1, lambda k: approx_big(k, s_, 490, 170))
        reveal(c, t, a+0.9, lambda k: text(k, f"{fmt(VAL)} € d'action  +  {round(DIV)} € de dividendes", 540, 610, 'm', 34, WH, 'c', 1, 0, False))
        reveal(c, t, a+1.1, lambda k: text(k, "change €/$ inclus · avant impôts et frais", 540, 660, 'l', 28, GR, 'c', 1, 0, False))
        zoomin(c, t, a+1.6, 540, 740, lambda k: pill(k, "×1,82", 540, 740, 52), s0=1.7)
    elif cid == 'c20':
        reveal(c, t, a, lambda k: (kicker(k, "LA QUESTION"), rule(k)))
        reveal(c, t, a+0.1, lambda k: big(k, "PÉAGE ÉTERNEL", 490, 120, GOLDG, t, a+0.1))
        reveal(c, t, a+0.4, lambda k: text(k, "ou", 540, 600, 'm', 48, GR))
        reveal(c, t, a+0.6, lambda k: big(k, "PÉAGE MENACÉ ?", 710, 120, REDG))
    elif cid == 'c21':
        reveal(c, t, a, lambda k: big(k, "Et toi ?", 470, 170))
        for j, (lab, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", GOLD))):
            def btn(k, j=j, lab=lab, cc=cc):
                y = 680+j*150; rr(k, 250, y, 580, 112, 56); col(k, 'FFFFFF', .06); k.fill_preserve(); col(k, cc, .9); k.set_line_width(2.5); k.stroke()
                text(k, f"{j+1}", 312, y+56, 'k', 44, cc, 'c', 1, 0, False); text(k, lab, 560, y+56, 'xb', 54, WH, 'c', 1, 0, False)
            reveal(c, t, a+0.3+j*0.18, btn)
    elif cid == 'c22':
        def head(k):
            sc = lerp(0.8, 1, ease((t-a)/0.5)); k.save(); k.translate(540, 470); k.scale(sc, sc); k.translate(-540, -470); logo_symbol(k, 540, 470, 190); k.restore()
            text(k, "Actions_Benefices", 540, 630, 'b', 46, WH)
        reveal(c, t, a, head)
        for j, lab in enumerate(("Abonne-toi", "Like", "Partage")):
            reveal(c, t, a+0.35+j*0.25, lambda k, j=j, lab=lab: (rr(k, 290, 730+j*135, 500, 100, 50), col(k, 'FFFFFF', .08), k.fill(), text(k, lab, 540, 780+j*135, 'xb', 48, WH, 'c', 1, 0, False)))

def vignette(c, end=False):
    g = cairo.LinearGradient(0, 0, 0, H); top = 0 if end else .5
    g.add_color_stop_rgba(0, 0, 0, .02, top+.25); g.add_color_stop_rgba(.22, 0, 0, .02, top); g.add_color_stop_rgba(.42, 0, 0, 0, top*.2); g.add_color_stop_rgba(.6, 0, 0, 0, 0)
    g.add_color_stop_rgba(.78, 0, 0, .02, .55); g.add_color_stop_rgba(1, 0, 0, .02, .75); c.set_source(g); c.paint()
    if not end:   # ombre douce derrière le bloc de titres
        c.save(); c.translate(540, 560); c.scale(1, 0.55); r = cairo.RadialGradient(0, 0, 0, 0, 0, 560)
        r.add_color_stop_rgba(0, 0, 0, .02, .5); r.add_color_stop_rgba(.6, 0, 0, .02, .3); r.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(r); c.paint(); c.restore()
def scene(cid, t):
    im = background(cid, t)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    vignette(c, SCN[cid][0] == 'end'); overlay(c, cid, t); draw_caption(c, t, cid)
    if cid in ('c10', 'c11', 'c14', 'c15', 'c19', 'c20', 'c21'):
        text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1458, 'm', 22, GR, 'c', .85, 0, False)
    col(c, 'FFFFFF', .15); rr(c, 140, 260, 800, 5, 2.5); c.fill(); col(c, GOLD); rr(c, 140, 260, max(5, 800*clamp(t/DUR)), 5, 2.5); c.fill()
    s.flush(); ov = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)
    im.alpha_composite(ov); return im
ORDER = [cid for cid, _ in CAPS]
CHAPTERS = ('c04', 'c07', 'c12', 'c16', 'c19')
def frame(t):
    cur = ORDER[0]
    for cid in ORDER:
        if t >= T(cid)-0.001: cur = cid
    im = scene(cur, t); i = ORDER.index(cur)
    if i > 0 and t-T(cur) < 0.3:
        prev = scene(ORDER[i-1], t); im = Image.blend(prev, im, inout((t-T(cur))/0.3))
    if t < 0.3: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, clamp(t/0.3))
    if t > DUR-0.4: im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t-(DUR-0.4))/0.4))
    return im

def events():
    ev = [(T(cid), 'whoosh' if cid in CHAPTERS else 'trans') for cid in ORDER]
    ev += [(T('c01')+34/30, 'beep'), (T('c01')+34/30+0.15, 'hit'), (T('c02')+0.6, 'hit'), (T('c04')+0.15, 'hit'), (T('c05')+34/30, 'beep'),
           (T('c05')+1.1, 'coin'), (T('c06')+0.45, 'hit'), (T('c07')+0.1, 'count'), (T('c08')+0.5, 'count'), (T('c09')+0.1, 'count'),
           (T('c10')+0.1, 'count'), (T('c10')+0.9, 'coin'), (T('c11')+0.3, 'count'), (T('c14')+0.15, 'hit'), (T('c15')+0.1, 'count'),
           (T('c16'), 'low'), (T('c17')+0.15, 'low'), (T('c19')+0.2, 'count'), (T('c19')+1.6, 'hit'), (T('c19')+1.6, 'coin'), (T('c21'), 'hit')]
    return ev

def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/visa/prev', exist_ok=True)
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/visa/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
