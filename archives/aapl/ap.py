"""Apple : 50 ans, un nouveau patron, un record. DA keynote, studios 3D blanc / béton, 60 i/s, ~85 s."""
import sys, math, re, subprocess, functools
import numpy as np, cairo
from PIL import Image, ImageFilter
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
from kn import W, H, hx, col, tw, text, gtext, rr, path_text, SUNSET, OCEAN, TITAN, REDG, GREENG
FPS = 60
DARKG = [(0, '1D1D1F'), (1, '5A5A60')]
B3D = '/home/claude/aapl/b3d'

# ---------- chiffres vérifiés (9 octobre 2026) ----------
FX0, FX1, P0, P1 = 1.1569, 1/0.8927, 142.96, 336.64
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*4.90/FX1; TOT = VAL+DIV
assert round(TOT, -1) == 2470 and round(VAL) == 2432 and round(DIV) == 35

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')

CAPS = [
 ("c01", "Apple vaut près de [5 000 milliards] de dollars."),
 ("c02", "Pourtant, elle a failli [disparaître]."),
 ("c03", "Et 1 000 € investis il y a 5 ans ? Réponse à la [fin]."),
 ("c04", "[1976] : Steve Jobs et Steve Wozniak lancent Apple dans un garage."),
 ("c05", "[1984] : le Macintosh popularise la souris."),
 ("c06", "[1985] : Jobs est poussé vers la sortie."),
 ("c07", "[1997] : Apple frôle la faillite. Jobs revient."),
 ("c08", "[2001] : l'iPod met 1 000 chansons dans la poche."),
 ("c09", "[2007] : l'iPhone. Tout change."),
 ("c10", "[2011] : Tim Cook prend la relève."),
 ("c11", "[2018] : première entreprise américaine à 1 000 milliards."),
 ("c12", "Aujourd'hui, l'iPhone pèse [la moitié] des ventes."),
 ("c13", "Et les Services rapportent [30 milliards] par trimestre."),
 ("c14", "Avril-juin 2026 : [109 milliards] de ventes, un record."),
 ("c15", "2026, ce sont aussi les [50 ans] d'Apple."),
 ("c16", "Et un nouveau patron : [John Ternus]."),
 ("c17", "Le 25 septembre, l'action signe un [record] : 341 $."),
 ("c18", "Mais le Siri dopé à l'IA a [un an de retard]."),
 ("c19", "Selon Nikkei, les commandes d'iPhone 18 Pro [baissent]."),
 ("c20", "Et l'action se paie [plus de 35 fois] ses bénéfices."),
 ("c21", "Tes 1 000 € ? ≈ [2 470 €]. ×2,5 en 5 ans."),
 ("c22", "Et toi : tu achètes, tu vends ou tu [attends] ?"),
 ("c23", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '')
        d = max(2.6, len(clean)/19+0.85)
        if cid in ('c01', 'c07', 'c17', 'c21'): d += 0.6
        if cid in ('c22',): d += 0.6
        if cid == 'c23': d = 3.4
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.15
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

# ---------- scènes : (studio, rendu 3D ou None, couleur du mot clé) ----------
SCN = {
 'c01': ('light', 'hook', SUNSET), 'c02': ('dark', None, REDG), 'c03': ('dark', None, TITAN), 'c04': ('dark', None, SUNSET),
 'c05': ('light', 'retro', SUNSET), 'c06': ('dark', None, TITAN), 'c07': ('dark', None, REDG), 'c08': ('light', 'player', OCEAN),
 'c09': ('light', 'phone07', SUNSET), 'c10': ('light', None, DARKG), 'c11': ('light', None, OCEAN), 'c12': ('light', None, OCEAN),
 'c13': ('light', None, OCEAN), 'c14': ('light', None, OCEAN), 'c15': ('light', None, SUNSET), 'c16': ('light', None, DARKG),
 'c17': ('light', None, OCEAN), 'c18': ('dark', 'siri', REDG), 'c19': ('dark', None, REDG), 'c20': ('dark', None, TITAN),
 'c21': ('light', None, SUNSET), 'c22': ('black', None, TITAN), 'c23': ('black', None, TITAN)}
NSEQ = {'hook': 84, 'retro': 64, 'player': 64, 'phone07': 64, 'siri': 76}

@functools.lru_cache(maxsize=4)
def static_bg(style):
    if style == 'black':
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); col(c, '000000'); c.paint()
        g = cairo.RadialGradient(540, 900, 0, 540, 900, 1100); g.add_color_stop_rgba(0, *hx('16181D', .9)); g.add_color_stop_rgba(1, *hx('000000', 0)); c.set_source(g); c.paint()
        s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRA', s.get_stride(), 1).copy()
    return Image.open(f'{B3D}/st_{style}/0000.png').convert('RGBA').resize((W, H), Image.LANCZOS)
@functools.lru_cache(maxsize=10)
def seq_frame(name, i):
    return Image.open(f'{B3D}/{name}/{i:04d}.png').convert('RGBA').resize((W, H), Image.LANCZOS)
def background(cid, t):
    style, seq, _ = SCN[cid]
    if seq is None: return static_bg(style).copy()
    a, d = TL[cid]; n = NSEQ[seq]; f = clamp((t-a)/(d+0.4))*(n-1); i = int(f); fr = f-i
    im = seq_frame(seq, i)
    if fr > 0.02 and i+1 < n: im = Image.blend(im, seq_frame(seq, i+1), fr)
    return im.copy()

# ---------- typographie ----------
def ink(style): return '1D1D1F' if style == 'light' else 'F5F5F7'
def sub_ink(style): return '6E6E73' if style == 'light' else 'A1A1A6'
def reveal(c, t, t0, draw, d=0.6, rise=30):
    u = ease((t-t0)/d)
    if u <= 0: return
    c.save(); c.translate(0, rise*(1-u)); c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(u); c.restore()
def sweep_text(c, s, x, y, w_, size, stops, t, t0, track=-6):
    """texte en dégradé + balayage de lumière"""
    c.push_group(); gtext(c, s, x, y, w_, size, stops, track=track)
    u = (t-t0-0.25)/1.1
    if 0 < u < 1:
        c.set_operator(cairo.OPERATOR_ATOP); g = cairo.LinearGradient(80+920*u-140, y-size, 80+920*u+140, y+size)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(.5, 1, 1, 1, .55); g.add_color_stop_rgba(1, 1, 1, 1, 0); c.set_source(g); c.paint()
    c.pop_group_to_source(); c.paint()
def draw_caption(c, t, cid):
    a, d = TL[cid]; b = a+d; style, _, kst = SCN[cid]; size = 46
    items = parse(dict(CAPS)[cid]); sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size) for w, _ in items]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 790: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = 1360-(len(lines)-1)*35
    # voile de lisibilité
    vg = cairo.RadialGradient(540, y0+35, 0, 540, y0+35, 520)
    vcol = 'FFFFFF' if style == 'light' else '000000'; va = .55 if style == 'light' else .55
    vg.add_color_stop_rgba(0, *hx(vcol, va)); vg.add_color_stop_rgba(1, *hx(vcol, 0))
    c.save(); c.translate(0, 0); c.scale(1, 0.35); c.translate(0, (y0+35)*(1/0.35-1)); c.set_source(vg); c.paint(); c.restore()
    fo = 1-clamp((t-(b-0.2))/0.2); n_ = 0
    kst2 = kst if style == 'light' or kst is not DARKG else TITAN
    if style != 'light' and kst is SUNSET: kst2 = [(0, 'FFB340'), (.5, 'FF5C7A'), (1, 'D18BFF')]
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; y = y0+li*70
        for i in idx:
            w, k = items[i]; ti = a+n_*0.045; n_ += 1; u = ease((t-ti)/0.35); al = clamp((t-ti)/0.2)*fo
            if al > 0:
                c.push_group(); yy = y+12*(1-u)
                if k: gtext(c, w, x, yy, 'b', size, kst2, 'l')
                else: text(c, w, x, yy, 'b', size, ink(style), 'l')
                c.pop_group_to_source(); c.paint_with_alpha(al)
            x += wd[i]+sp

def overlay(c, cid, t):
    a, d = TL[cid]; style = SCN[cid][0]; I = ink(style); S = sub_ink(style)
    big = DARKG if style == 'light' else TITAN
    if cid == 'c01':
        reveal(c, t, a, lambda k: sweep_text(k, "5 000", 540, 375, 'black', 165, SUNSET, t, a))
        reveal(c, t, a+0.25, lambda k: text(k, "milliards de dollars.", 540, 492, 'xb', 50, I, track=-1))
    elif cid == 'c02':
        reveal(c, t, a, lambda k: text(k, "Pourtant, elle a failli", 540, 500, 'sb', 56, S))
        reveal(c, t, a+0.35, lambda k: sweep_text(k, "disparaître.", 540, 660, 'black', 150, REDG, t, a+0.35, -4))
    elif cid == 'c03':
        reveal(c, t, a, lambda k: text(k, "1 000 €", 540, 520, 'black', 200, I, track=-6))
        reveal(c, t, a+0.3, lambda k: text(k, "investis il y a 5 ans", 540, 680, 'sb', 46, S))
        def q(k):
            p = inout((t-a-0.6)/2.2)*0.8; rr(k, 290, 800, 500, 10, 5); col(k, 'FFFFFF', .15); k.fill(); rr(k, 290, 800, max(10, 500*p), 10, 5); col(k, 'F5F5F7'); k.fill()
            text(k, "aujourd'hui ? ? ?", 540, 870, 'm', 38, S)
        reveal(c, t, a+0.6, q)
    elif cid in ('c04', 'c06', 'c07', 'c10', 'c11', 'c15'):
        spec = {'c04': ("Los Altos, Californie", "1976.", SUNSET, "Un garage. Deux Steve."),
                'c06': ("Le fondateur évincé", "1985.", TITAN, "Jobs quitte Apple."),
                'c07': ("Au bord de la faillite", "1997.", REDG, None),
                'c10': ("Un nouveau PDG", "2011.", DARKG, "Tim Cook."),
                'c11': ("Première entreprise américaine", "2018.", OCEAN, "1 000 milliards."),
                'c15': ("1976 – 2026", "50 ans.", SUNSET, "Un anniversaire historique.")}[cid]
        eb, yr, st, sub = spec
        reveal(c, t, a, lambda k: text(k, eb, 540, 400, 'sb', 34, S))
        reveal(c, t, a+0.15, lambda k: sweep_text(k, yr, 540, 560, 'black', 220, st, t, a+0.15))
        if sub:
            szs = 96 if cid in ('c10', 'c11') else 58
            if cid == 'c11': reveal(c, t, a+0.6, lambda k: sweep_text(k, sub, 540, 740, 'black', szs, OCEAN, t, a+0.6, -3))
            else: reveal(c, t, a+0.6, lambda k: text(k, sub, 540, 740, 'xb' if szs > 60 else 'sb', szs, I, track=-2))
        if cid == 'c07':
            reveal(c, t, a+1.9, lambda k: sweep_text(k, "Jobs revient.", 540, 750, 'black', 100, [(0, 'FFB340'), (.5, 'FF5C7A'), (1, 'D18BFF')], t, a+1.9, -3))
    elif cid in ('c05', 'c08', 'c09'):
        yr, st = {'c05': ("1984.", SUNSET), 'c08': ("2001.", OCEAN), 'c09': ("2007.", SUNSET)}[cid]
        reveal(c, t, a, lambda k: sweep_text(k, yr, 540, 400, 'black', 160, st, t, a))
    elif cid in ('c12', 'c13'):
        items = [("iPhone", 54.3, "54,3 Md$"), ("Services", 30.7, "30,7 Md$"), ("Mac", 10.4, "10,4 Md$"), ("Wearables", 7.9, "7,9 Md$"), ("iPad", 6.2, "6,2 Md$")]
        hl = 0 if cid == 'c12' else 1; a0 = T('c12')
        reveal(c, t, a0, lambda k: text(k, "Ventes · avril-juin 2026", 540, 360, 'sb', 34, S))
        for i, (lab, v, s) in enumerate(items):
            y = 440+i*104; g = ease((t-a0-0.15-i*0.08)/0.7); w = 520*v/54.3*g
            text(c, lab, 180, y, 'sb', 28, S, 'l', clamp((t-a0-i*0.08)/0.3))
            if w > 2:
                rr(c, 180, y+26, max(48, w), 48, 24)
                if i == hl:
                    gr = cairo.LinearGradient(180, 0, 180+w, 0)
                    for o, h_ in OCEAN: gr.add_color_stop_rgb(o, *hx(h_)[:3])
                    c.set_source(gr)
                else: col(c, 'D2D2D7')
                c.fill()
                text(c, s, 180+max(48, w)+18, y+50, 'b', 30, I if i == hl else S, 'l', g)
    elif cid == 'c14':
        reveal(c, t, a, lambda k: text(k, "Chiffre d'affaires · avril-juin 2026", 540, 400, 'sb', 34, S))
        v = 109.4*ease((t-a-0.1)/1.0)
        reveal(c, t, a+0.1, lambda k: gtext(k, f"{v:.1f}".replace('.', ',')+" Md$", 540, 580, 'black', 160, OCEAN, track=-5))
        reveal(c, t, a+0.7, lambda k: text(k, "+16 % · record pour un trimestre de juin", 540, 740, 'sb', 40, I))
    elif cid == 'c16':
        reveal(c, t, a, lambda k: text(k, "Nouveau PDG · 1er septembre 2026", 540, 380, 'sb', 34, S))
        reveal(c, t, a+0.2, lambda k: text(k, "John", 540, 540, 'black', 170, I, track=-6))
        reveal(c, t, a+0.4, lambda k: text(k, "Ternus.", 540, 700, 'black', 170, I, track=-6))
        reveal(c, t, a+0.9, lambda k: text(k, "Tim Cook devient président exécutif.", 540, 850, 'm', 34, S))
    elif cid == 'c17':
        reveal(c, t, a, lambda k: text(k, "Record · 25 septembre 2026", 540, 360, 'sb', 34, S))
        reveal(c, t, a+0.1, lambda k: sweep_text(k, "341 $", 540, 500, 'black', 150, OCEAN, t, a+0.1, -5))
        pts = [(0, 143), (.08, 170), (.2, 135), (.3, 165), (.45, 195), (.55, 230), (.62, 222), (.7, 255), (.78, 200), (.86, 245), (.9, 253), (.97, 341), (1, 337)]
        u = inout((t-a-0.3)/1.8); X = lambda q: 160+q*760; Y = lambda v: 960-(v-120)/(360-120)*300
        n = 80; qs = [u*i/n for i in range(n+1)]; vs = np.interp(qs, [p[0] for p in pts], [p[1] for p in pts])
        if u > 0:
            c.new_path(); c.move_to(X(0), Y(vs[0])); [c.line_to(X(q), Y(v)) for q, v in zip(qs, vs)]
            gr = cairo.LinearGradient(160, 0, 920, 0)
            for o, h_ in OCEAN: gr.add_color_stop_rgb(o, *hx(h_)[:3])
            c.set_source(gr); c.set_line_width(7); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
            if u > 0.97: c.new_path(); c.arc(X(.97), Y(341), 11, 0, 2*math.pi); col(c, '0A84FF'); c.fill()
            text(c, "oct. 2021", 160, 1000, 'm', 26, S, 'l'); text(c, "oct. 2026", 920, 1000, 'm', 26, S, 'r')
    elif cid == 'c18':
        reveal(c, t, a, lambda k: sweep_text(k, "1 an de retard.", 540, 420, 'black', 100, REDG, t, a, -3))
    elif cid == 'c19':
        reveal(c, t, a, lambda k: text(k, "Commandes d'iPhone 18 Pro", 540, 420, 'sb', 40, S))
        reveal(c, t, a+0.15, lambda k: sweep_text(k, "−15 %", 540, 600, 'black', 220, REDG, t, a+0.15))
        reveal(c, t, a+0.6, lambda k: text(k, "Selon Nikkei · non confirmé par Apple", 540, 770, 'm', 32, S))
    elif cid == 'c20':
        reveal(c, t, a, lambda k: text(k, "Valorisation", 540, 420, 'sb', 40, S))
        reveal(c, t, a+0.15, lambda k: sweep_text(k, "35×", 540, 600, 'black', 240, TITAN, t, a+0.15))
        reveal(c, t, a+0.5, lambda k: text(k, "ses bénéfices annuels, et plus.", 540, 780, 'sb', 44, I))
    elif cid == 'c21':
        reveal(c, t, a, lambda k: text(k, "1 000 € investis il y a 5 ans", 540, 380, 'sb', 36, S))
        v = 1000+(TOT-1000)*ease((t-a-0.3)/1.1)
        s_ = fmt(round(v, -1) if v < TOT-15 else 2470)+" €"
        def big(k):
            w1 = tw(k, "≈ ", 'xb', 90); w2 = tw(k, s_, 'black', 170, -5); x0 = 540-(w1+w2)/2
            text(k, "≈", x0, 560, 'xb', 90, '1D1D1F', 'l'); gtext(k, s_, x0+w1, 560, 'black', 170, SUNSET, 'l', -5)
        reveal(c, t, a+0.2, big)
        reveal(c, t, a+0.9, lambda k: text(k, f"actions ≈ {fmt(VAL)} € · dividendes ≈ {round(DIV)} €", 540, 720, 'sb', 36, I))
        reveal(c, t, a+1.1, lambda k: text(k, "change €/$ inclus · avant impôts et frais", 540, 780, 'm', 28, S))
        if t > a+1.5:
            sc = lerp(1.6, 1, ease((t-a-1.5)/0.35))
            c.save(); c.translate(540, 900); c.scale(sc, sc); c.push_group(); gtext(c, "×2,5", 0, 0, 'black', 90, DARKG); c.pop_group_to_source(); c.paint_with_alpha(clamp((t-a-1.5)/0.15)); c.restore()
    elif cid == 'c22':
        reveal(c, t, a, lambda k: sweep_text(k, "Et toi ?", 540, 470, 'black', 170, TITAN, t, a))
        for j, (lab, st) in enumerate((("J'achète", GREENG), ("Je vends", REDG), ("J'attends", OCEAN))):
            def btn(k, j=j, lab=lab, st=st):
                y = 680+j*150; rr(k, 250, y, 580, 112, 56); col(k, 'FFFFFF', .08); k.fill_preserve(); col(k, 'FFFFFF', .25); k.set_line_width(2); k.stroke()
                gtext(k, lab, 540, y+56, 'xb', 56, st, track=-1)
            reveal(c, t, a+0.35+j*0.18, btn)
    elif cid == 'c23':
        def head(k):
            sc = lerp(0.8, 1, ease((t-a)/0.5)); k.save(); k.translate(540, 470); k.scale(sc, sc); k.translate(-540, -470); logo_symbol(k, 540, 470, 190); k.restore()
            text(k, "Actions_Benefices", 540, 630, 'b', 46, 'F5F5F7')
        reveal(c, t, a, head)
        for j, lab in enumerate(("Abonne-toi", "Like", "Partage")):
            reveal(c, t, a+0.35+j*0.25, lambda k, j=j, lab=lab: (rr(k, 290, 730+j*135, 500, 100, 50), col(k, 'FFFFFF', .1), k.fill(), text(k, lab, 540, 780+j*135, 'xb', 50, 'F5F5F7')))
        reveal(c, t, a+1.3, lambda k: text(k, "Contenu pédagogique, pas un conseil en investissement", 540, 1180, 'm', 26, 'A1A1A6'))

def scene(cid, t):
    im = background(cid, t)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    overlay(c, cid, t); draw_caption(c, t, cid)
    style = SCN[cid][0]
    if cid in ('c17', 'c19', 'c20'):
        text(c, "Courbe simplifiée · Pas un conseil en investissement" if cid == 'c17' else "Pas un conseil en investissement", 540, 1462, 'm', 22, sub_ink(style), 'c', .9)
    # barre de progression
    pc = '1D1D1F' if style == 'light' else 'FFFFFF'
    col(c, pc, .15); rr(c, 140, 260, 800, 5, 2.5); c.fill(); rr(c, 140, 260, max(5, 800*clamp(t/DUR)), 5, 2.5); col(c, pc, .85); c.fill()
    s.flush(); ov = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)
    im.alpha_composite(ov); return im
ORDER = [cid for cid, _ in CAPS]
def frame(t):
    cur = ORDER[0]
    for cid in ORDER:
        if t >= T(cid)-0.001: cur = cid
    im = scene(cur, t)
    i = ORDER.index(cur)
    if i > 0 and t-T(cur) < 0.3:     # fondu enchaîné depuis la scène précédente
        prev = scene(ORDER[i-1], t); im = Image.blend(prev, im, inout((t-T(cur))/0.3))
    if t > DUR-0.4: im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t-(DUR-0.4))/0.4))
    return im

def events():
    ev = []
    for cid in ORDER:
        st = SCN[cid][0]; ev.append((T(cid), 'swell' if cid in ('c01', 'c05', 'c08', 'c09', 'c15') else 'trans'))
    ev += [(T('c01')+0.25, 'hit'), (T('c02')+0.35, 'low'), (T('c03')+0.6, 'tick'), (T('c07')+1.9, 'hit'), (T('c11')+0.6, 'hit'),
           (T('c14')+0.1, 'hit'), (T('c17')+0.1, 'hit'), (T('c18'), 'low'), (T('c19')+0.15, 'low'), (T('c21')+0.3, 'count'), (T('c21')+1.5, 'hit')]
    return ev

def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/aapl/prev_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
