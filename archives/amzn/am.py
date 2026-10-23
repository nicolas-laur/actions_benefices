"""Amazon : le survivant. Entrepôt 3D + data center AWS, 60 i/s, ~62 s."""
import sys, math, re, subprocess, functools, random
import numpy as np, cairo
from PIL import Image, ImageEnhance
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/amzn')
from ty import W, H, OR, WH, GR, hx, col, tw, text, rr, label as ship_label
FPS = 60
B3D = '/home/claude/amzn/b3d'
NAVY = '0E141B'; BLUE = '9FD4FF'; RED = 'FF4D3D'; GREEN = '3DDC84'

# ---------- chiffres vérifiés (10 octobre 2026) ----------
P0, FX0, P1, FX1 = 3288.62/20, 1.1569, 262.43, 1.1177
SH = 1000*FX0/P0; VAL = SH*P1/FX1
assert round(VAL, -1) == 1650

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x): x = clamp(x); s = 1.7; return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')

CAPS = [
 ("c01", "Amazon a failli [disparaître]. Deux fois."),
 ("c02", "Aujourd'hui, elle pèse ≈ [2 800 milliards] de dollars."),
 ("c03", "Et tes 1 000 € d'il y a 5 ans ? Réponse à la [fin]."),
 ("c04", "[1994] : Jeff Bezos vend des livres en ligne, depuis un garage."),
 ("c05", "[1997] : entrée en Bourse."),
 ("c06", "2000 : la bulle internet [éclate]."),
 ("c07", "L'action s'effondre de plus de [90 %]."),
 ("c08", "Beaucoup la donnent pour [morte]."),
 ("c09", "Elle survit. [2005] : Prime et la livraison rapide."),
 ("c10", "[2006] : elle loue ses serveurs au monde entier. C'est AWS."),
 ("c11", "AWS : [42,2 milliards $] en 3 mois. +37 % sur un an."),
 ("c12", "Le cloud est devenu sa [machine à cash]."),
 ("c13", "[2022] : deuxième chute. Près de −50 % sur l'année."),
 ("c14", "Elle survit [encore]."),
 ("c15", "Avril-juin 2026 : [53 milliards $] de gain lié à Anthropic."),
 ("c16", "3 août : l'action touche un [record] à 284 $."),
 ("c17", "Mais elle prévoit [220 milliards $] d'investissements en 2026."),
 ("c18", "Résultat : son free cash flow passe [sous zéro]."),
 ("c19", "Et [16 000] postes de bureau supprimés cette année."),
 ("c20", "Tes 1 000 € il y a 5 ans ? ≈ [1 650 €]. ×1,65."),
 ("c21", "Survivante… ou [trop gourmande] en IA ?"),
 ("c22", "Et toi : tu achètes, tu vends ou tu [attends] ?"),
 ("c23", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '')
        d = max(2.0, len(clean)/23+0.6)
        if cid in ('c01', 'c07', 'c16'): d += 0.4
        if cid == 'c20': d += 0.9
        if cid == 'c22': d += 0.4
        if cid == 'c23': d = 3.2
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.1
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def E(c): return TL[c][0]+TL[c][1]
NB = ' '
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB).replace('− ', '−')
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]

# ---------- scènes : fond, mouvement de caméra 2D ----------
SCN = {'c01': 'belt', 'c02': 'belt', 'c03': 'belt', 'c04': 'garage', 'c05': 'garage', 'c06': 'crash', 'c07': 'crash', 'c08': 'crash',
       'c09': 'belt', 'c10': 'dc', 'c11': 'dc', 'c12': 'dc', 'c13': 'crash', 'c14': 'belt', 'c15': 'dc', 'c16': 'belt',
       'c17': 'dc', 'c18': 'dcdim', 'c19': 'crash', 'c20': 'stacks', 'c21': 'belt', 'c22': 'end', 'c23': 'end'}
NSEQ = {'belt': 96, 'dc': 75}
KEYC = {'belt': OR, 'garage': OR, 'crash': RED, 'dc': BLUE, 'dcdim': RED, 'stacks': OR, 'end': OR}

@functools.lru_cache(maxsize=4)
def static_src(name):
    if name == 'end':
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); col(c, '05070A'); c.paint()
        g = cairo.RadialGradient(540, 1500, 0, 540, 1500, 1300); g.add_color_stop_rgba(0, *hx('3A2306', .9)); g.add_color_stop_rgba(.5, *hx('101820', .7)); g.add_color_stop_rgba(1, *hx('000000', 0)); c.set_source(g); c.paint()
        s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
    import os
    p = f'{B3D}/st_{name}.png'
    if not os.path.exists(p): p = {'stacks': f'{B3D}/kf_stacks.png'}.get(name, f'/tmp/claude-0/t_{name}.png')   # aperçu provisoire
    return Image.open(p).convert('RGBA')
@functools.lru_cache(maxsize=24)
def seq_src(name, i):
    import os
    p = f'{B3D}/seq_{name}/f{i+1:04d}.png'
    if not os.path.exists(p): p = f'{B3D}/seq_belt/f0001.png' if name == 'belt' else '/tmp/claude-0/t_dc.png'
    return Image.open(p).convert('RGBA')
def kb(im, z, dx=0.0, dy=0.0):
    """recadrage Ken Burns : zoom z>=1, décalage relatif"""
    w, h = im.size; cw, ch = w/z, h/z
    x0 = min(max(0, (w-cw)/2+dx*w), w-cw); y0 = min(max(0, (h-ch)/2+dy*h), h-ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0+cw, y0+ch))
def background(cid, t):
    nm = SCN[cid]; a, d = TL[cid]; u = clamp((t-a)/(d+0.3))
    if nm in ('belt', 'dc', 'dcdim'):
        sq = 'dc' if nm == 'dcdim' else nm
        i = int(t*30) % NSEQ[sq]       # 30 i/s rendus, chaque image tenue 2 trames (flou de mouvement Cycles)
        im = kb(seq_src(sq, i), lerp(1.04, 1.10, inout(u)))
        if nm == 'dcdim':
            im = ImageEnhance.Brightness(im).enhance(0.55)
            r = Image.new('RGBA', (W, H), (120, 10, 5, 255)); im = Image.blend(im, r, 0.18)
        return im
    if nm == 'stacks': return kb(static_src(nm), lerp(1.02, 1.08, inout(u)), 0, 0.01)
    if nm == "garage": return kb(static_src(nm), lerp(1.22, 1.13, inout(u)), 0, 0.05)
    if nm == 'crash':
        im = kb(static_src(nm), lerp(1.0, 1.08, inout(u)), 0, 0)
        rnd = random.Random(int(t*12)); fl = 0.82+0.18*rnd.random() if rnd.random() < 0.35 else 1.0
        return ImageEnhance.Brightness(im).enhance(fl) if fl < 1 else im
    return static_src('end').copy()

# ---------- éléments graphiques ----------
def reveal(c, t, t0, draw, d=0.45, rise=26):
    u = ease((t-t0)/d)
    if u <= 0: return
    c.save(); c.translate(0, rise*(1-u)); c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(u); c.restore()
def pop(c, t, t0, x, y, draw, d=0.35, s0=1.5, rot=0.0):
    """tampon : arrive grand puis s'écrase sur le carton"""
    u = clamp((t-t0)/d)
    if u <= 0: return
    s = lerp(s0, 1.0, ease(u)); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(clamp(u*2.5)); c.restore()
def stamp(c, s, color, size=56, pad=26):
    w = tw(c, s, "Archivo Black", size)+2*pad; h = size+2*pad*0.8
    c.set_line_width(7); rr(c, -w/2, -h/2, w, h, 12); col(c, color, .95); c.stroke()
    c.set_line_width(2.5); rr(c, -w/2+12, -h/2+12, w-24, h-24, 6); c.stroke()
    text(c, s, 0, 0, "Archivo Black", size, color, False, 'c', .95, 0, False)
def check(c, x, y, s, color):
    c.set_line_width(s*0.22); c.set_line_cap(1); c.set_line_join(1); col(c, color)
    c.move_to(x-s*0.5, y); c.line_to(x-s*0.12, y+s*0.38); c.line_to(x+s*0.55, y-s*0.42); c.stroke()
def kicker(c, s, y=350, color=GR, size=26):
    text(c, s, 540, y, "JetBrains Mono", size, color, True, 'c', 1, 4)
def bignum(c, s, y=505, size=200, color=WH, approx=False):
    if approx:
        w1 = tw(c, "≈ ", "Poppins", size*0.45, True); w2 = tw(c, s, "Archivo Black", size); x0 = 540-(w1+w2)/2
        text(c, "≈", x0, y, "Poppins", size*0.45, color, True, 'l'); text(c, s, x0+w1, y, "Archivo Black", size, color, False, 'l')
    else:
        while tw(c, s, "Archivo Black", size) > 860: size -= 6
        text(c, s, 540, y, "Archivo Black", size, color)
def tape_box(c, s, x, y, color=OR, size=52, ink='111111', rot=-0.02):
    w = tw(c, s, "Archivo Black", size)+56
    c.save(); c.translate(x, y); c.rotate(rot); c.rectangle(-w/2, -size*0.72, w, size*1.44); col(c, color); c.fill()
    text(c, s, 0, 0, "Archivo Black", size, ink, False, 'c', 1, 0, False); c.restore()
def count_up(t, t0, d, v0, v1):
    return lerp(v0, v1, ease((t-t0)/d))

def draw_caption(c, t, cid):
    a, d = TL[cid]; b = a+d; size = 46; kc = KEYC[SCN[cid]]
    items = parse(dict(CAPS)[cid]); sp = tw(c, ' ', "Poppins", size, True)
    wd = [tw(c, w, "Poppins", size, True)+(24 if k else 0) for w, k in items]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 790: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = 1352-(len(lines)-1)*36
    fo = 1-clamp((t-(b-0.15))/0.15); n_ = 0
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; y = y0+li*72
        for i in idx:
            w, k = items[i]; ti = a+n_*0.04; n_ += 1; u = ease((t-ti)/0.3); al = clamp((t-ti)/0.18)*fo
            if al > 0:
                c.push_group(); yy = y+12*(1-u)
                if k:   # mot clé sur ruban adhésif qui se déroule
                    tu = ease((t-ti-0.05)/0.28)
                    c.save(); c.translate(x+wd[i]/2, yy); c.rotate(-0.02); c.rectangle(-wd[i]/2, -32, wd[i]*tu, 62); col(c, kc); c.fill(); c.restore()
                    text(c, w, x+12, yy, "Poppins", size, '111111' if kc != RED else 'FFFFFF', True, 'l', 1, 0, False)
                else: text(c, w, x, yy, "Poppins", size, WH, True, 'l')
                c.pop_group_to_source(); c.paint_with_alpha(al)
            x += wd[i]+sp

def overlay(c, cid, t):
    a, d = TL[cid]
    if cid == 'c01':
        reveal(c, t, a, lambda k: kicker(k, "AMAZON · DE 1994 À 2026"))
        reveal(c, t, a+0.15, lambda k: bignum(k, "SURVIVANT", 500, 150))
        pop(c, t, a+0.9, 560, 700, lambda k: stamp(k, "FRAGILE", OR, 60), rot=-0.08)
    elif cid == 'c02':
        reveal(c, t, a, lambda k: kicker(k, "VALEUR EN BOURSE · OCT. 2026"))
        v = count_up(t, a+0.1, 1.0, 0, 2800)
        reveal(c, t, a+0.1, lambda k: bignum(k, fmt(round(v, -1)), 505, 210, approx=True))
        reveal(c, t, a+0.4, lambda k: text(k, "MILLIARDS DE DOLLARS", 540, 650, "JetBrains Mono", 34, OR, True, 'c', 1, 6))
    elif cid == 'c03':
        reveal(c, t, a, lambda k: kicker(k, "TON COLIS EST EN ROUTE"))
        pop(c, t, a+0.2, 540, 620, lambda k: ship_label(k, 0, 0, ["COLIS N° 2021-10", "CONTENU : 1 000 €", "LIVRAISON : FIN DE VIDÉO"], 470, 0), s0=1.25, rot=-0.04)
    elif cid == 'c04':
        reveal(c, t, a, lambda k: kicker(k, "CHAPITRE 1 · LE GARAGE"))
        reveal(c, t, a+0.1, lambda k: bignum(k, "1994", 500, 230))
        pop(c, t, a+0.6, 560, 720, lambda k: ship_label(k, 0, 0, ["EXPÉDITEUR : UN GARAGE", "CONTENU : LIVRES"], 440, 0), s0=1.3, rot=0.05)
    elif cid == 'c05':
        reveal(c, t, a, lambda k: kicker(k, "INTRODUCTION EN BOURSE"))
        reveal(c, t, a+0.1, lambda k: bignum(k, "1997", 500, 230))
        reveal(c, t, a+0.4, lambda k: text(k, "NASDAQ", 540, 650, "JetBrains Mono", 36, OR, True, 'c', 1, 8))
    elif cid == 'c06':
        reveal(c, t, a, lambda k: kicker(k, "CHAPITRE 2 · LA CHUTE", 350, RED))
        reveal(c, t, a+0.1, lambda k: bignum(k, "2000", 500, 230))
        reveal(c, t, a+0.4, lambda k: text(k, "BULLE INTERNET", 540, 650, "JetBrains Mono", 36, RED, True, 'c', 1, 8))
    elif cid == 'c07':
        reveal(c, t, a, lambda k: kicker(k, "DE DÉC. 1999 À SEPT. 2001", 350, GR))
        sh = (6*math.sin(t*70)*(1-clamp((t-a-0.25)/0.4))) if t > a+0.25 else 0
        c.save(); c.translate(sh, 0); reveal(c, t, a+0.1, lambda k: bignum(k, "−90 %", 500, 220, RED)); c.restore()
        pop(c, t, a+0.8, 560, 720, lambda k: ship_label(k, 0, 0, ["COLIS N° 2001", "ÉTAT : ENDOMMAGÉ"], 380), s0=1.3, rot=0.06)
    elif cid == 'c08':
        reveal(c, t, a, lambda k: kicker(k, "WALL STREET, 2001", 350, GR))
        pop(c, t, a+0.3, 540, 560, lambda k: stamp(k, "RETOUR À L'EXPÉDITEUR", RED, 50), rot=-0.07)
    elif cid == 'c09':
        reveal(c, t, a, lambda k: kicker(k, "CHAPITRE 3 · LA REVANCHE", 350, OR))
        reveal(c, t, a+0.1, lambda k: bignum(k, "2005", 500, 230))
        reveal(c, t, a+0.4, lambda k: text(k, "PRIME · LIVRAISON EN 2 JOURS", 540, 650, "JetBrains Mono", 32, OR, True, 'c', 1, 4))
    elif cid == 'c10':
        reveal(c, t, a, lambda k: kicker(k, "AMAZON WEB SERVICES", 350, BLUE))
        reveal(c, t, a+0.1, lambda k: bignum(k, "2006", 500, 230))
        reveal(c, t, a+0.4, lambda k: text(k, "LE CLOUD D'AMAZON", 540, 650, "JetBrains Mono", 34, BLUE, True, 'c', 1, 6))
    elif cid == 'c11':
        reveal(c, t, a, lambda k: kicker(k, "AWS · AVRIL-JUIN 2026", 350, BLUE))
        v = count_up(t, a+0.1, 0.9, 0, 42.2)
        reveal(c, t, a+0.1, lambda k: bignum(k, f"{v:.1f}".replace('.', ',')+" MD$", 500, 190))
        pop(c, t, a+0.8, 540, 670, lambda k: tape_box(k, "+37 %", 0, 0, OR, 56))
    elif cid == 'c12':
        reveal(c, t, a, lambda k: kicker(k, "POIDS D'AWS · T2 2026", 350, BLUE))
        # barre : AWS = 21 % des ventes
        def bar(k):
            u = ease((t-a-0.2)/0.9); rr(k, 140, 470, 800, 80, 14); col(k, 'FFFFFF', .12); k.fill()
            rr(k, 140, 470, max(28, 800*0.21*u), 80, 14); col(k, BLUE); k.fill()
            text(k, "AWS", 140+800*0.21*u/2, 510, "Archivo Black", 34, '0A1420', False, 'c', 1, 0, False)
            text(k, "21 % DES VENTES", 540, 620, "Archivo Black", 64, WH)
            text(k, "42,2 MD$ SUR 200,6 MD$", 540, 700, "JetBrains Mono", 30, GR, True, 'c', 1, 3)
        reveal(c, t, a+0.1, bar)
    elif cid == 'c13':
        reveal(c, t, a, lambda k: kicker(k, "CHAPITRE 4 · DEUXIÈME CHUTE", 350, RED))
        reveal(c, t, a+0.1, lambda k: bignum(k, "2022", 500, 230))
        pop(c, t, a+0.7, 560, 720, lambda k: ship_label(k, 0, 0, ["COLIS N° 2022", "ÉTAT : ÉCRASÉ"], 380, 0, "−50 %"), s0=1.3, rot=0.05)
    elif cid == 'c14':
        def ok(k):
            stamp(k, "LIVRÉ     ", GREEN, 70); w = tw(k, "LIVRÉ     ", "Archivo Black", 70); check(k, w/2-44, -2, 46, GREEN)
        pop(c, t, a+0.2, 540, 540, ok, rot=-0.06)
    elif cid == 'c15':
        reveal(c, t, a, lambda k: kicker(k, "GAIN LIÉ À ANTHROPIC · T2 2026", 350, BLUE, 24))
        v = count_up(t, a+0.1, 1.0, 0, 53.4)
        reveal(c, t, a+0.1, lambda k: bignum(k, f"{v:.1f}".replace('.', ',')+" MD$", 500, 190))
        reveal(c, t, a+0.5, lambda k: text(k, "plus-value sur sa participation, pas du cash", 540, 640, "Poppins", 32, GR, True))
    elif cid == 'c16':
        reveal(c, t, a, lambda k: kicker(k, "RECORD HISTORIQUE · 3 AOÛT 2026", 350, OR, 24))
        v = count_up(t, a+0.1, 1.0, 165, 284.02)
        reveal(c, t, a+0.1, lambda k: bignum(k, f"{int(v)} $", 500, 220))
        reveal(c, t, a+0.5, lambda k: text(k, f"≈ 164 $ IL Y A 5 ANS · {P1:.0f} $ LE 9 OCT.", 540, 650, "Poppins", 30, GR, True))
    elif cid == 'c17':
        reveal(c, t, a, lambda k: kicker(k, "INVESTISSEMENTS PRÉVUS EN 2026", 350, BLUE, 24))
        v = count_up(t, a+0.1, 1.0, 0, 220)
        reveal(c, t, a+0.1, lambda k: bignum(k, f"{int(v)} MD$", 500, 210))
        reveal(c, t, a+0.5, lambda k: text(k, "DATA CENTERS · PUCES · IA", 540, 650, "JetBrains Mono", 32, BLUE, True, 'c', 1, 4))
    elif cid == 'c18':
        reveal(c, t, a, lambda k: kicker(k, "FREE CASH FLOW · 12 MOIS", 350, RED))
        reveal(c, t, a+0.1, lambda k: bignum(k, "−7,6 MD$", 500, 190, RED))
        reveal(c, t, a+0.5, lambda k: text(k, "les dépenses mangent le cash produit", 540, 640, "Poppins", 32, GR, True))
    elif cid == 'c19':
        reveal(c, t, a, lambda k: kicker(k, "SUPPRESSIONS DE POSTES · 2026", 350, RED, 24))
        v = count_up(t, a+0.1, 0.9, 0, 16000)
        reveal(c, t, a+0.1, lambda k: bignum(k, fmt(round(v, -2)), 500, 220))
        reveal(c, t, a+0.5, lambda k: text(k, "SURTOUT DANS LA TECH ET LE MANAGEMENT", 540, 650, "JetBrains Mono", 26, GR, True, 'c', 1, 2))
    elif cid == 'c20':
        reveal(c, t, a, lambda k: kicker(k, "TES 1 000 € IL Y A 5 ANS", 350, GR, 28))
        v = count_up(t, a+0.2, 1.2, 1000, VAL); s_ = fmt(round(v, -1) if v < VAL-12 else 1650)+" €"
        reveal(c, t, a+0.1, lambda k: bignum(k, s_, 490, 150, approx=True))
        reveal(c, t, a+0.6, lambda k: text(k, "SANS DIVIDENDE · CHANGE €/$ INCLUS · AVANT FRAIS", 540, 600, "JetBrains Mono", 22, GR, True, 'c', 1, 1))
        pop(c, t, a+0.9, 330, 790, lambda k: ship_label(k, 0, 0, ["OCT. 2021", "10 CARTONS"], 300, 0, "1 000 €"), s0=1.3, rot=-0.05)
        pop(c, t, a+1.4, 760, 740, lambda k: ship_label(k, 0, 0, ["OCT. 2026", "16,5 CARTONS"], 310, 0, "1 650 €"), s0=1.3, rot=0.05)
        if t > a+1.9:
            s = lerp(1.6, 1, ease((t-a-1.9)/0.3)); c.save(); c.translate(540, 1010); c.scale(s, s)
            c.push_group(); tape_box(c, "×1,65", 0, 0, OR, 60, rot=0); c.pop_group_to_source(); c.paint_with_alpha(clamp((t-a-1.9)/0.12)); c.restore()
    elif cid == 'c21':
        reveal(c, t, a, lambda k: kicker(k, "LA QUESTION", 350, OR))
        reveal(c, t, a+0.1, lambda k: bignum(k, "SURVIVANTE", 480, 140))
        reveal(c, t, a+0.35, lambda k: text(k, "ou", 540, 590, "Poppins", 50, GR, True))
        reveal(c, t, a+0.55, lambda k: bignum(k, "GOURMANDE ?", 700, 140, OR))
    elif cid == 'c22':
        reveal(c, t, a, lambda k: bignum(k, "Et toi ?", 470, 170))
        for j, (lab, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", OR))):
            def btn(k, j=j, lab=lab, cc=cc):
                y = 680+j*150; rr(k, 250, y, 580, 112, 18); col(k, 'FFFFFF', .07); k.fill_preserve(); col(k, cc, .9); k.set_line_width(3); k.stroke()
                text(k, f"{j+1}", 300, y+56, "Archivo Black", 44, cc, False, 'c', 1, 0, False)
                text(k, lab, 560, y+56, "Archivo Black", 52, WH, False, 'c', 1, 0, False)
            reveal(c, t, a+0.3+j*0.18, btn)
    elif cid == 'c23':
        def head(k):
            sc = lerp(0.8, 1, ease((t-a)/0.5)); k.save(); k.translate(540, 470); k.scale(sc, sc); k.translate(-540, -470); logo_symbol(k, 540, 470, 190); k.restore()
            text(k, "Actions_Benefices", 540, 630, "Poppins", 46, WH, True)
        reveal(c, t, a, head)
        for j, lab in enumerate(("Abonne-toi", "Like", "Partage")):
            reveal(c, t, a+0.35+j*0.25, lambda k, j=j, lab=lab: (rr(k, 290, 730+j*135, 500, 100, 18), col(k, 'FFFFFF', .08), k.fill(), text(k, lab, 540, 780+j*135, "Archivo Black", 48, WH, False, 'c', 1, 0, False)))

def vignette(c, nm):
    g = cairo.LinearGradient(0, 0, 0, H)
    top = .55 if nm != 'end' else 0
    g.add_color_stop_rgba(0, 0, 0, 0, top+.2); g.add_color_stop_rgba(.2, 0, 0, 0, top); g.add_color_stop_rgba(.42, 0, 0, 0, top*.25); g.add_color_stop_rgba(.58, 0, 0, 0, 0)
    g.add_color_stop_rgba(.66, 0, 0, 0, .25); g.add_color_stop_rgba(.78, 0, 0, 0, .62); g.add_color_stop_rgba(1, 0, 0, 0, .7); c.set_source(g); c.paint()

def scene(cid, t):
    im = background(cid, t); nm = SCN[cid]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    vignette(c, nm); overlay(c, cid, t); draw_caption(c, t, cid)
    if cid in ('c11', 'c15', 'c16', 'c17', 'c18', 'c20', 'c21', 'c22'):
        text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1458, "Poppins", 22, GR, False, 'c', .85, 0, False)
    col(c, 'FFFFFF', .18); rr(c, 140, 260, 800, 6, 3); c.fill(); rr(c, 140, 260, max(6, 800*clamp(t/DUR)), 6, 3); col(c, OR); c.fill()
    s.flush(); ov = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)
    im.alpha_composite(ov); return im
ORDER = [cid for cid, _ in CAPS]
CHAPTERS = ('c04', 'c06', 'c09', 'c10', 'c13', 'c20')
def frame(t):
    cur = ORDER[0]
    for cid in ORDER:
        if t >= T(cid)-0.001: cur = cid
    im = scene(cur, t); i = ORDER.index(cur)
    if i > 0 and t-T(cur) < 0.25 and cur not in CHAPTERS:
        prev = scene(ORDER[i-1], t); im = Image.blend(prev, im, inout((t-T(cur))/0.25))
    if cur in CHAPTERS and t-T(cur) < 0.18:      # coupe franche + flash
        fl = 1-clamp((t-T(cur))/0.18); im = Image.blend(im, Image.new('RGBA', (W, H), (255, 245, 230, 255)), 0.55*fl)
    if t < 0.25: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, clamp(t/0.25))
    if t > DUR-0.4: im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t-(DUR-0.4))/0.4))
    return im

def events():
    ev = []
    for cid in ORDER:
        ev.append((T(cid), 'whoosh' if cid in CHAPTERS else 'trans'))
    ev += [(T('c01')+0.15, 'hit'), (T('c01')+0.9, 'thud'), (T('c02')+0.1, 'count'), (T('c03')+0.2, 'thud'), (T('c04')+0.6, 'thud'),
           (T('c06'), 'low'), (T('c07')+0.25, 'crash'), (T('c07')+0.8, 'thud'), (T('c08')+0.3, 'thud'), (T('c09'), 'hit'),
           (T('c10'), 'hit'), (T('c11')+0.1, 'count'), (T('c11')+0.8, 'thud'), (T('c13'), 'low'), (T('c13')+0.7, 'thud'),
           (T('c14')+0.2, 'thud'), (T('c15')+0.1, 'count'), (T('c16')+0.1, 'count'), (T('c16')+1.1, 'hit'), (T('c17')+0.1, 'count'),
           (T('c18')+0.1, 'low'), (T('c19')+0.1, 'count'), (T('c20')+0.2, 'count'), (T('c20')+0.9, 'thud'), (T('c20')+1.4, 'thud'),
           (T('c20')+1.9, 'hit'), (T('c22'), 'hit')]
    return ev

def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/amzn/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
