"""Visa v2 : intro terminal en 3D, puis carte flottante nette qui porte les infographies."""
import sys, math, subprocess, functools, json, os
import numpy as np, cairo
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
_a = sys.argv; sys.argv = ['x', 'info']
import va as V
sys.argv = _a
from va import (W, H, FPS, clamp, ease, inout, lerp, fmt, CAPS, TL, DUR, T, E, parse, reveal, zoomin, shine, approx_big,
                end_bg, TOT, VAL, DIV, REDG, logo_symbol)
from vty import GOLD, GOLDG, WH, GR, GREEN, RED, hx, col, tw, text, gtext, rr, kicker, rule, pill
import cardui
B3D = '/home/claude/visa/b3d'

# ---------- scènes : (pose de carte, contenu de la carte, étalonnage) ----------
SCN = {'c01': ('tap', None, None), 'c02': ('A', 'feed', None), 'c03': ('B', 'hook', None), 'c04': ('A', 'credit', None), 'c05': ('B', 'flow', None),
       'c06': ('A', 'toll', None), 'c07': ('B', 'tx', None), 'c08': ('A', 'tps', None), 'c09': ('B', 'volume', None), 'c10': ('A', 'rev', None),
       'c11': ('B', 'margin', None), 'c12': ('A', 'fresno', 'archive'), 'c13': ('B', 'ipo', 'archive'), 'c14': ('A', 'curve', None),
       'c15': ('B', 'range', None), 'c16': ('darkA', 'jobs', None), 'c17': ('darkA', 'doj', None), 'c18': ('darkA', 'rivals', None),
       'c19': ('A', 'reveal', None), 'c20': ('B', 'verdict', None), 'c21': ('end', None, None), 'c22': ('end', None, None)}
DARK = ('c16', 'c17', 'c18')
# titres au-dessus de la carte : (sur-titre, grand texte, dégradé ou None)
HEAD = {'c02': ("ET CE N'EST PAS SEULEMENT TA BANQUE", "VISA", GOLDG), 'c03': ("1 000 € INVESTIS EN OCTOBRE 2021", "COMBIEN ?", GOLDG),
        'c04': ("ARGENT PRÊTÉ PAR VISA", "0 €", GOLDG), 'c05': ("COMMENT ÇA MARCHE", "LE RÉSEAU", None), 'c06': ("LE MODÈLE", "PÉAGE INVISIBLE", GOLDG),
        'c07': ("AVRIL-JUIN 2026", "72 MILLIARDS", None), 'c08': ("TRANSACTIONS PAR SECONDE", "≈ 9 100", GOLDG), 'c09': ("PAIEMENTS EN 3 MOIS", "4 000 MD$", None),
        'c10': ("REVENUS · AVRIL-JUIN 2026", "11,6 MD$", None), 'c11': ("BÉNÉFICE NET", "48 %", GOLDG), 'c12': ("AUX ORIGINES", "1958", None),
        'c13': ("EN PLEINE CRISE FINANCIÈRE", "2008", None), 'c14': ("DEPUIS L'INTRODUCTION", "×35", GOLDG), 'c15': ("CLÔTURE DU 9 OCTOBRE", "385 $", GOLDG),
        'c16': ("CET ÉTÉ", "2 600 POSTES", None), 'c17': ("LA JUSTICE AMÉRICAINE", "MONOPOLE ?", REDG), 'c18': ("LES NOUVEAUX RIVAUX ?", "STABLECOINS + IA", None),
        'c19': ("TES 1 000 € IL Y A 5 ANS", None, None), 'c20': ("LA QUESTION", "PÉAGE MENACÉ ?", REDG)}

@functools.lru_cache(maxsize=8)
def still(name):
    return Image.open(f'{B3D}/st_{name}.png').convert('RGBA')
@functools.lru_cache(maxsize=4)
def quad(pose):
    return json.load(open(f'{B3D}/card_{pose}.json'))
@functools.lru_cache(maxsize=40)
def tap_src(i):
    p = f'{B3D}/seq_tap/f{i+1:04d}.png'
    if not os.path.exists(p): p = f'{B3D}/seq_tap_lowres/f{i+1:04d}.png'
    return Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS)
def persp_coeffs(dst, src):
    """coefficients PIL PERSPECTIVE : point de sortie (dst) → point d'entrée (src)"""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()
def content_layer(pose, key, u, t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, cardui.CW, cardui.CH); c = cairo.Context(s)
    cardui.draw(c, key, u, t); s.flush()
    im = Image.frombuffer('RGBA', (cardui.CW, cardui.CH), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)
    q = quad(pose); src = [(0, 0), (cardui.CW, 0), (cardui.CW, cardui.CH), (0, cardui.CH)]
    return im.transform((W, H), Image.PERSPECTIVE, persp_coeffs(q, src), Image.BICUBIC)
@functools.lru_cache(maxsize=2)
def shadow():
    im = Image.new('L', (W, H), 0); s = cairo.ImageSurface(cairo.FORMAT_A8, W, H); c = cairo.Context(s)
    c.save(); c.translate(540, 1560); c.scale(420, 46); c.arc(0, 0, 1, 0, 2*math.pi); c.restore(); c.set_source_rgba(0, 0, 0, .55); c.fill(); s.flush()
    a = Image.frombuffer('L', (s.get_stride(), H), bytes(s.get_data()), 'raw', 'L', 0, 1).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(28))
    sh = Image.new('RGBA', (W, H), (0, 0, 5, 255)); sh.putalpha(a); return sh
def card_frame(cid, t):
    pose, key, grade = SCN[cid]; a, d = TL[cid]
    bg = still('bg').copy()
    z = lerp(1.0, 1.04, inout(clamp((t-a)/(d+0.3)))); w2, h2 = W/z, H/z
    bg = bg.resize((W, H), Image.BICUBIC, box=((W-w2)/2, (H-h2)/2, (W+w2)/2, (H+h2)/2))
    if cid in DARK:
        bg = ImageEnhance.Brightness(bg).enhance(0.6); bg = Image.blend(bg, Image.new('RGBA', (W, H), (60, 6, 4, 255)), 0.18)
    # carte + contenu, puis flottaison (légère translation, rotation, échelle) appliquée ensemble
    layer = still(pose).copy()
    u = clamp((t-a-0.35)/2.0)
    layer.alpha_composite(content_layer(pose, key, u, t-a))
    dy = 12*math.sin(2*math.pi*t/3.6); rot = math.radians(0.55*math.sin(2*math.pi*t/5.2)); sc = 1+0.01*math.sin(2*math.pi*t/4.4)
    cx, cy, dx = 540, 1020, -38; sc *= 0.9          # carte réduite et décalée : hors de la zone des boutons TikTok
    ca, sa = math.cos(rot)/sc, math.sin(rot)/sc
    ox, oy = cx+dx, cy+dy
    coeffs = (ca, sa, cx-ca*ox-sa*oy, -sa, ca, cy+sa*ox-ca*oy)
    layer = layer.transform((W, H), Image.AFFINE, coeffs, Image.BICUBIC)
    shd = shadow().copy(); shd.putalpha(shd.getchannel('A').point(lambda v: int(v*(1-dy/60))))
    bg.alpha_composite(shd); bg.alpha_composite(layer)
    if grade == 'archive':
        g = ImageOps.grayscale(bg.convert('RGB')); bg = ImageEnhance.Contrast(ImageOps.colorize(g, (8, 6, 4), (235, 205, 150))).enhance(1.15).convert('RGBA')
    return bg
def background(cid, t):
    pose = SCN[cid][0]
    if pose == 'end': return end_bg().copy()
    if pose == 'tap':
        f = (t-T(cid))*30; n = 90
        if f > n-1: k = (f-(n-1))*0.5; m = 24; ph = k % (2*m); f = n-1-(ph if ph < m else 2*m-ph)
        i = int(f); j = min(i+1, n-1); fr = f-i; a = tap_src(i)
        return Image.blend(a, tap_src(j), fr) if fr > 0.02 else a.copy()
    return card_frame(cid, t)

# ---------- titres ----------
def head(c, cid, t):
    a, d = TL[cid]; TAP = 34/30
    if cid == 'c01':
        reveal(c, t, a, lambda k: (kicker(k, "CHAQUE FOIS QUE TU PAIES"), rule(k)))
        reveal(c, t, a+TAP-0.1, lambda k: text(k, "QUELQU'UN", 540, 500, 'k', 120, WH))
        zoomin(c, t, a+TAP+0.15, 540, 640, lambda k: V.big(k, "ENCAISSE", 640, 130, GOLDG, t, a+TAP+0.15))
        return
    if cid == 'c21':
        reveal(c, t, a, lambda k: V.big(k, "Et toi ?", 470, 170))
        for j, (lab, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", GOLD))):
            def btn(k, j=j, lab=lab, cc=cc):
                y = 680+j*150; rr(k, 250, y, 580, 112, 56); col(k, 'FFFFFF', .06); k.fill_preserve(); col(k, cc, .9); k.set_line_width(2.5); k.stroke()
                text(k, f"{j+1}", 312, y+56, 'k', 44, cc, 'c', 1, 0, False); text(k, lab, 560, y+56, 'xb', 54, WH, 'c', 1, 0, False)
            reveal(c, t, a+0.3+j*0.18, btn)
        return
    if cid == 'c22':
        def hd(k):
            s_ = lerp(0.8, 1, ease((t-a)/0.5)); k.save(); k.translate(540, 470); k.scale(s_, s_); k.translate(-540, -470); logo_symbol(k, 540, 470, 190); k.restore()
            text(k, "Actions_Benefices", 540, 630, 'b', 46, WH)
        reveal(c, t, a, hd)
        for j, lab in enumerate(("Abonne-toi", "Like", "Partage")):
            reveal(c, t, a+0.35+j*0.25, lambda k, j=j, lab=lab: (rr(k, 290, 730+j*135, 500, 100, 50), col(k, 'FFFFFF', .08), k.fill(), text(k, lab, 540, 780+j*135, 'xb', 48, WH, 'c', 1, 0, False)))
        return
    kc = 'FF8A7E' if cid in DARK or cid == 'c20' else GOLD
    kick, big_, st = HEAD[cid]
    reveal(c, t, a, lambda k: (kicker(k, kick, 330, kc, 24 if len(kick) > 28 else 26), rule(k, 372)))
    if cid == 'c19':
        v = lerp(1000, TOT, ease((t-a-0.2)/1.3)); s_ = fmt(round(v, -1) if v < TOT-10 else 1820)+" €"
        reveal(c, t, a+0.1, lambda k: approx_big(k, s_, 480, 160))
        zoomin(c, t, a+1.6, 540, 615, lambda k: pill(k, "×1,82", 540, 615, 46), s0=1.7)
        return
    if big_.startswith('≈ '):
        reveal(c, t, a+0.1, lambda k: approx_big(k, big_[2:], 480, 160)); return
    size = 170 if len(big_) <= 8 else (130 if len(big_) <= 12 else 104)
    if st: zoomin(c, t, a+0.1, 540, 480, lambda k: V.big(k, big_, 480, size, st, t, a+0.1), s0=1.35)
    else: reveal(c, t, a+0.1, lambda k: text(k, big_, 540, 480, 'k', size, WH))

def draw_caption(c, t, cid):
    a, d = TL[cid]; b = a+d; size = 46; kst = REDG if cid in DARK else GOLDG
    items = parse(dict(CAPS)[cid]); sp = tw(c, ' ', 'p', size); wd = [tw(c, w, 'p', size) for w, _ in items]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 790: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = 1440-(len(lines)-1)*36
    vg = cairo.RadialGradient(540, y0+36, 0, 540, y0+36, 560); vg.add_color_stop_rgba(0, 0, 0, .02, .6); vg.add_color_stop_rgba(1, 0, 0, 0, 0)
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

def vignette(c, end=False):
    g = cairo.LinearGradient(0, 0, 0, H); top = 0 if end else .5
    g.add_color_stop_rgba(0, 0, 0, .02, top+.25); g.add_color_stop_rgba(.2, 0, 0, .02, top); g.add_color_stop_rgba(.34, 0, 0, 0, 0); g.add_color_stop_rgba(.7, 0, 0, 0, 0)
    g.add_color_stop_rgba(.82, 0, 0, .02, .5); g.add_color_stop_rgba(1, 0, 0, .02, .8); c.set_source(g); c.paint()
def scene(cid, t):
    im = background(cid, t)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    vignette(c, SCN[cid][0] == 'end'); head(c, cid, t); draw_caption(c, t, cid)
    if cid in ('c10', 'c11', 'c14', 'c15', 'c19', 'c20', 'c21'):
        text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1545, 'm', 22, GR, 'c', .85, 0, False)
    col(c, 'FFFFFF', .15); rr(c, 140, 260, 800, 5, 2.5); c.fill(); col(c, GOLD); rr(c, 140, 260, max(5, 800*clamp(t/DUR)), 5, 2.5); c.fill()
    s.flush(); ov = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)
    im.alpha_composite(ov); return im
ORDER = [cid for cid, _ in CAPS]
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
    ev = []
    for cid in ORDER[1:]:
        a = T(cid)
        ev.append((a, 'swish'))                          # entrée de scène
        if cid in ('c21', 'c22'): continue
        ev.append((a+0.12, 'impact'))
        if cid in ('c07', 'c08', 'c09', 'c10', 'c11', 'c14', 'c15', 'c19'): ev.append((a+0.35, 'tick'))   # compteur / graphique qui se remplit
        if cid in ('c02', 'c04', 'c06', 'c11', 'c14', 'c15', 'c19'): ev.append((a+0.12, 'glint'))           # chiffre doré
    ev += [(T('c01')+34/30, 'paid'), (T('c01')+34/30+0.15, 'impact'), (T('c12'), 'whoosh'), (T('c16'), 'low'), (T('c17')+0.1, 'low'),
           (T('c19')-1.3, 'riser'), (T('c19')+1.6, 'impact'), (T('c19')+1.6, 'glint'), (T('c21'), 'impact')]
    return ev
def main():
    if sys.argv[1] == 'info': print(round(DUR, 2)); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/visa/prev', exist_ok=True)
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/visa/prev/q_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
