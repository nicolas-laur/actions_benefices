"""Ton iPhone ou des actions Apple ? v2 « Keynote 2007 → courbe » (format court, accroche question).
Motion design : téléphone générique en fausse 3D (lacet, roulis, perspective) dont l'écran s'allume, typographie cinétique,
caméra continue (poussées, panoramiques, secousses aux impacts), tiroir qui claque, retour en arrière, tuile Apple qui sort du
tiroir dans la lumière, puis caméra embarquée sur la vraie courbe de l'action (clôtures annuelles 2007 → 2026, hors dividendes)
avec le compteur en euros accroché à la tête de la courbe, pluie de pièces, duel final. Mister Coin classique (3 clips).
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from bglass import gpanel, place, glow_text, tilt_quad, with_alpha
FPS = int(os.environ.get('FPS', 60)); NB = ' '
NAVY = '1E2A44'; WHITE = 'FFFFFF'; GOLD = 'F5B400'; BLUE = '3A86FF'; PINK = 'FF5DA2'
CY = '35D6FF'; CY2 = 'A8EEFF'; GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4057'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def ease5(x): x = clamp(x); return 1-(1-x)**5
def inout(x): x = clamp(x); return x*x*(3-2*x)
def inq(x): x = clamp(x); return x*x*x
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def spring(x, f=3.2, d=5.0): x = max(0, x); return 1-math.exp(-d*x)*math.cos(f*2*math.pi*x)
def lerp(a, b, u): return a+(b-a)*u
def rgb(h, k=1.0, w=0.0):
    h = h.lstrip('#'); v = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]; return [min(1, x*k*(1-w)+w) for x in v]
def fmt(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
def win(t, a, b, fi=.2, fo=.2): return min(ease((t-a)/fi) if fi > 0 else float(t >= a), 1-ease((t-b)/fo) if fo > 0 else float(t < b))

# ---------- minutage (voix Thomas 15,12 s) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(q=0.0, sorti=1.87, prix=3.83, auj=6.09, tiroir=6.83, etsi=8.59, apple=9.83, place=10.07, aurais=11.21, num=11.90, etoi=13.49, choisi=14.13, fin=15.12)
DUR = 15.9
CAPS = [(T['q'], "Tu te souviens du [premier iPhone] ?"), (T['sorti'], "Sorti en France en 2007, à [399 €]…"),
        (T['auj'], "Aujourd'hui, il traîne au fond d'un [tiroir]."), (T['etsi'], "Et si tu avais acheté des [actions Apple] à la place ?"),
        (T['aurais'], "Tu aurais environ [27 000 €]."), (T['etoi'], "Et toi, tu aurais [choisi quoi] ?")]
HL = {T['q']: BLUE, T['sorti']: GOLD, T['auj']: PINK, T['etsi']: BLUE, T['aurais']: GOLD, T['etoi']: GOLD}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    out = []
    for tok in s.split(' '):
        if '[' in tok:                                                   # la ponctuation collée reste hors du surlignage
            pre, rest = tok.split('[', 1); mid, post = rest.split(']', 1)
            if pre: out.append((pre, False, True))
            out.append((mid, True, bool(post)));
            if post: out.append((post, False, False))
        else: out.append((tok, False, False))
    return out
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1060, size=44, a=1):
    """mots du sous-titre ; un mot suivi de sa ponctuation collée (glue) n'a pas d'espace après lui"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k, g in words]
    gaps = [0 if g else sp for w, k, g in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(gaps[i-1] if cur else 0)
        if cur and cw+need > 760 and not (i > 0 and words[i-1][2]): lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, INK, .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for j, i in enumerate(idx):
            w, k, g = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, NAVY if hl == GOLD else WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+gaps[i]

# ---------- outils ----------
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def put_emoji(cv, ch, x, y, size, k, a=1.0):
    if k <= 0 or a <= 0: return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    if a < 1: e = with_alpha(e, a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def gpill(c, s, x, y, colr, size=34, a=1, fg=INK):
    w = tw(c, s, 'xb', size, 2)+60; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&@"
def scramble(s, u, seed=3):
    """décodage : les lettres se figent de gauche à droite, les autres changent à chaque image"""
    n = len(s); k = int(u*n*1.0001); rng = np.random.default_rng(seed+int(u*40))
    return ''.join(ch if (i < k or ch == ' ') else GLYPHS[rng.integers(len(GLYPHS))] for i, ch in enumerate(s))
def slam(cv, s, x, y, size, t0, t, stagger=.07, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=1.0):
    """chaque caractère tombe à son tour (×2,4 → ×1) avec un petit rebond"""
    c0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); widths = [tw(c0, ch, 'a', size) for ch in s]; tot = sum(widths)
    xx = x-tot/2
    for i, ch in enumerate(s):
        k = t-(t0+i*stagger)
        if k > 0 and ch != ' ':
            sc = lerp(2.4, 1, back(k/.22, 2.0)); al = a*ease(k/.08)
            glow_text(cv, ch, xx+widths[i]/2, y, size, top=top, bottom=bottom, glow=glow, ga=ga, a=al, scale=sc, reflect=False)
        xx += widths[i]

# ---------- fond : scène de keynote (noir profond, faisceau de lumière, poussière en suspension) ----------
@functools.lru_cache(maxsize=1)
def bg_base():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('030407')); g.add_color_stop_rgb(.6, *rgb('06080D')); g.add_color_stop_rgb(1, *rgb('0A0D14')); c.set_source(g); c.paint()
    return to_img(s)
@functools.lru_cache(maxsize=1)
def motes():
    rng = np.random.default_rng(3); return rng.uniform(0, W, 140), rng.uniform(0, H, 140), rng.uniform(.8, 2.2, 140), rng.uniform(.05, .3, 140), rng.uniform(0, 6.3, 140)
def background(t, cam):
    cv = bg_base().copy(); s, c = surface()
    warm = ease((t-T['etsi']-.2)/1.2)                                    # la lumière passe du froid (2007) au doré (les actions)
    cool = np.array(rgb('9FC8FF')); gold = np.array(rgb(GD)); tint = cool*(1-warm)+gold*warm
    sx = 540+(cam[0]-540)*.15                                            # le faisceau suit la caméra en parallaxe
    g = cairo.LinearGradient(sx, 0, sx, 1000)
    g.add_color_stop_rgba(0, *tint, .16); g.add_color_stop_rgba(1, *tint, 0)
    c.move_to(sx-90, 0); c.line_to(sx+90, 0); c.line_to(sx+520, 1000); c.line_to(sx-520, 1000); c.close_path(); c.set_source(g); c.fill()
    r = cairo.RadialGradient(sx, 620, 0, sx, 620, 620); r.add_color_stop_rgba(0, *tint, .10); r.add_color_stop_rgba(1, *tint, 0); c.set_source(r); c.paint()
    X, Y, R, A, P = motes()
    for x, y, rr_, a_, p in zip(X, Y, R, A, P):                          # poussière dans la lumière, lente
        xx = (x+12*math.sin(t*.4+p)-(cam[0]-540)*.3) % W; yy = (y-t*14-(cam[1]-700)*.3) % H
        c.arc(xx, yy, rr_, 0, 2*math.pi); c.set_source_rgba(*tint, a_*(.6+.4*math.sin(t*1.1+p))); c.fill()
    cv.alpha_composite(to_img(s)); return cv

# ---------- téléphone générique 2007 en fausse 3D ----------
PW, PH, PS = 300, 560, 2                                                  # dimensions logiques ; face rendue en ×2
ICONS = ['3FE08A', '35D6FF', 'FFC24A', 'FF5DA2', 'FF8A3D', '8E7CFF', 'E8EEF8', '3A86FF', 'FF4057', '2DB36F', 'FFD34D', '9AA7BD', '35D6FF', 'FF8A3D', '3FE08A', 'FFC24A']
def face(t, mode):
    """face avant : verre noir, écran (éteint → glisser pour déverrouiller → icônes → extinction), bouton rond"""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, PW*PS, PH*PS); c = cairo.Context(s); c.scale(PS, PS); c.translate(PW/2, PH/2)
    w, h = PW, PH
    rr(c, -w/2, -h/2, w, h, 46); col(c, '0A0B0E'); c.fill()
    g = cairo.LinearGradient(-w/2, -h/2, w/2, h/2)                                  # liseré chromé vu de face
    for u, k in ((0, 'D9DEE6'), (.3, 'FFFFFF'), (.55, '8E95A2'), (1, 'E6E9EF')): g.add_color_stop_rgb(u, *rgb(k))
    rr(c, -w/2, -h/2, w, h, 46); rr(c, -w/2+8, -h/2+8, w-16, h-16, 40); c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source(g); c.fill(); c.set_fill_rule(cairo.FILL_RULE_WINDING)
    sx0, sy0, sw, sh = -118, -190, 236, 352
    on = mode.get('on', 0.0); dim = mode.get('grey', 0.0)
    rr(c, sx0, sy0, sw, sh, 4); col(c, '050608'); c.fill()
    if on > 0:
        c.save(); rr(c, sx0, sy0, sw, sh, 4); c.clip()
        crt = mode.get('crt', 0.0)                                                   # extinction façon tube cathodique
        if crt > 0:
            hh = sh*(1-inout(crt/.6)); ww = sw*(1-inout((crt-.5)/.4)) if crt > .5 else sw
            c.rectangle(-ww/2, -14-hh/2, ww, max(2, hh)); col(c, 'CFE0FF', .7*(1-clamp((crt-.85)/.15))); c.fill(); c.restore()
        else:
            gs = cairo.LinearGradient(0, sy0, 0, sy0+sh); gs.add_color_stop_rgb(0, *rgb('1B3A6B', 1-.6*dim)); gs.add_color_stop_rgb(1, *rgb('0D1A33', 1-.6*dim))
            c.set_source(gs); c.paint_with_alpha(on); c.new_path()
            text(c, "9:41", 0, sy0+18, 'b', 15, WHITE, 'c', .9*on)
            ku = mode.get('unlock', -1)
            if ku >= 0 and ku < 1.15:                                                    # barre « glisser pour déverrouiller »
                al = on*(1-ease((ku-.95)/.2))
                rr(c, sx0+14, sy0+sh-62, sw-28, 46, 12); c.set_source_rgba(0, 0, 0, .45*al); c.fill()
                shx = sx0+20+(t*260 % 260)
                gsh = cairo.LinearGradient(shx-40, 0, shx+40, 0); gsh.add_color_stop_rgba(0, 1, 1, 1, .35); gsh.add_color_stop_rgba(.5, 1, 1, 1, 1); gsh.add_color_stop_rgba(1, 1, 1, 1, .35)
                c.save(); c.select_font_face('Inter Display', 0, 0); c.set_font_size(13); c.move_to(sx0+70, sy0+sh-34); c.text_path("glisser pour déverrouiller")
                c.set_source(gsh); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(al); c.restore()
                kx = sx0+20+(sw-80)*inout(clamp((ku-.15)/.55))
                rr(c, kx, sy0+sh-58, 44, 38, 9); g2 = cairo.LinearGradient(0, sy0+sh-58, 0, sy0+sh-20); g2.add_color_stop_rgb(0, *rgb('F4F6FA')); g2.add_color_stop_rgb(1, *rgb('A9B0BC'))
                c.set_source(g2); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(al)
                c.move_to(kx+16, sy0+sh-47); c.line_to(kx+28, sy0+sh-39); c.line_to(kx+16, sy0+sh-31); c.set_line_width(3); col(c, '6B7280', al); c.stroke()
            ki = mode.get('icons', -1)
            for i, colr in enumerate(ICONS):                                             # icônes qui jaillissent en cascade
                k = ki-i*.035
                if k <= 0: continue
                r_, k_ = divmod(i, 4); ix = -90+k_*60; iy = -128+r_*72
                sc = spring(k/.55, 1.6, 6.0)
                c.save(); c.translate(ix, iy); c.scale(sc, sc)
                gi = cairo.LinearGradient(0, -22, 0, 22); gi.add_color_stop_rgb(0, *rgb(colr, 1-.6*dim, .25*(1-dim))); gi.add_color_stop_rgb(1, *rgb(colr, .8*(1-.6*dim)))
                rr(c, -22, -22, 44, 44, 10); c.set_source(gi); c.fill(); rr(c, -22, -22, 44, 20, 10); c.set_source_rgba(1, 1, 1, .18); c.fill(); c.restore()
            if ki > .6:
                for k_ in range(4):
                    ix = -90+k_*60; rr(c, ix-22, 118, 44, 44, 10); col(c, ICONS[k_*3+1], .9*ease((ki-.6)/.2)*(1-.6*dim)); c.fill()
            c.restore()
    c.move_to(sx0, sy0); c.line_to(sx0+sw, sy0); c.line_to(sx0+sw, sy0+150); c.curve_to(40, -80, -40, -120, sx0, -60); c.close_path()
    c.set_source_rgba(1, 1, 1, .06); c.fill()
    sweep = mode.get('sweep', None)                                                      # reflet qui balaie le verre
    if sweep is not None:
        xs = lerp(-260, 260, sweep); gl = cairo.LinearGradient(xs-60, -h/2, xs+60, h/2)
        gl.add_color_stop_rgba(0, 1, 1, 1, 0); gl.add_color_stop_rgba(.5, 1, 1, 1, .22); gl.add_color_stop_rgba(1, 1, 1, 1, 0)
        rr(c, -w/2+8, -h/2+8, w-16, h-16, 40); c.set_source(gl); c.fill()
    c.arc(0, 224, 24, 0, 2*math.pi); col(c, '1A1C22'); c.fill_preserve(); c.set_line_width(2); col(c, '5A606B'); c.stroke()
    rr(c, -8, 216, 16, 16, 3); c.set_line_width(2); col(c, '8A909B'); c.stroke()
    rr(c, -26, -238, 52, 7, 3.5); col(c, '2A2D35'); c.fill()
    s.flush(); return np.asarray(Image.frombuffer('RGBA', (PW*PS, PH*PS), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1))
def project_phone(cx, cy, sc, yaw, roll, depth=16):
    """coins avant et arrière projetés (perspective, focale 1700)"""
    f = 1700; out = {}
    for zname, z0 in (('f', 0), ('b', -depth)):
        pts = []
        for (x, y) in ((-PW/2, -PH/2), (PW/2, -PH/2), (PW/2, PH/2), (-PW/2, PH/2)):
            xr = x*math.cos(yaw)+z0*math.sin(yaw); zr = -x*math.sin(yaw)+z0*math.cos(yaw)
            k = f/(f-zr*sc); px, py = xr*sc*k, y*sc*k
            qx = px*math.cos(roll)-py*math.sin(roll); qy = px*math.sin(roll)+py*math.cos(roll)
            pts.append((cx+qx, cy+qy))
        out[zname] = pts
    return out
def draw_phone(cv, t, cx, cy, sc, yaw, roll, mode, a=1.0, shadow=True, clip_y=None):
    if a <= 0 or sc <= .01: return
    P = project_phone(cx, cy, sc, yaw, roll)
    lay = Image.new('RGBA', (W, H), 0); s, c = surface()
    if shadow:
        c.save(); c.translate(cx+20*sc, cy+PH/2*sc+30*sc); c.scale(1, .16); c.arc(0, 0, PW*.7*sc, 0, 2*math.pi); c.restore()
        c.set_source_rgba(0, 0, 0, .35*a); c.fill()
    side = 1 if math.sin(yaw) > 0 else 3                                                  # tranche visible : gauche ou droite
    i0, i1 = (0, 3) if side == 1 else (1, 2)
    q = [P['f'][i0], P['f'][i1], P['b'][i1], P['b'][i0]]
    g = cairo.LinearGradient(q[0][0], 0, q[3][0], 0)
    for u, k in ((0, 'F2F4F8'), (.5, '9AA1AE'), (1, '5E6470')): g.add_color_stop_rgb(u, *rgb(k))
    c.move_to(*q[0]); [c.line_to(*p) for p in q[1:]]; c.close_path(); c.set_source(g); c.fill()
    lay.alpha_composite(to_img(s))
    fimg = face(t, mode)
    src = np.float32([[0, 0], [PW*PS, 0], [PW*PS, PH*PS], [0, PH*PS]]); dst = np.float32(P['f'])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(fimg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    lay.alpha_composite(Image.fromarray(warped, 'RGBA'))
    if clip_y is not None:
        arr = np.asarray(lay).copy(); y0, y1 = clip_y; arr[:max(0, int(y0))] = 0; arr[int(y1):] = 0; lay = Image.fromarray(arr, 'RGBA')
    cv.alpha_composite(with_alpha(lay, a) if a < 1 else lay)
    return P
def phone_state(t):
    """pose du téléphone 0 → 8,1 s"""
    k0 = ease5(t/1.25)
    yaw = lerp(-1.45, 0, k0)+.10*math.sin(t*1.3)*k0; roll = lerp(-.25, 0, k0)+.03*math.sin(t*.9)
    x, y, sc = 540, 690, lerp(.75, 1.0, k0)
    mode = dict(on=0.0, sweep=clamp((t-.5)/1.0) if t < 1.6 else None)
    ku = t-T['sorti']
    if ku > 0: mode.update(on=ease(ku/.15), unlock=ku);
    if ku > .75: mode['icons'] = ku-.75
    kp = t-T['prix']
    if kp > 0:                                                                                 # « à 399 € » : il pivote et laisse la place au prix
        u = back(kp/.45, 1.2); x = lerp(540, 330, u); yaw += .42*ease(kp/.45); sc = lerp(sc, .82, ease(kp/.45)); y = lerp(690, 680, u)
    ka = t-T['auj']
    if ka > 0:
        mode['crt'] = ka-.05; mode['grey'] = 1.0; u = ease(ka/.6); x = lerp(x, 540, u); yaw = lerp(yaw, .15, u); sc = lerp(sc, .7, u); y = lerp(y, 560, u)
    kt = t-(T['tiroir']+.05)
    if kt > 0:                                                                                 # chute qui accélère, roulis, il bascule à plat
        u = inq(clamp(kt/.62)); y = lerp(560, 800, u); roll = lerp(roll, 1.45, inout(kt/.62)); sc = lerp(.7, .55, u); yaw = lerp(yaw, .55, u)
    return x, y, sc, yaw, roll, mode

# ---------- tiroir ----------
DX, DY, DW = 540, 735, 660
def drawer_geom(t):
    """ouverture (0→1), décalage vertical d'entrée, et réouverture lumineuse au « Et si… »"""
    enter = ease5((t-(T['tiroir']-.25))/.45); rise = 520*(1-enter)
    o = ease((t-(T['tiroir']-.05))/.35)*(1-inout((t-(T['tiroir']+.68))/.16))              # se referme d'un coup
    o2 = ease((t-(T['etsi']+.25))/.45)                                                     # se rouvre sur la lumière
    leave = ease((t-(T['place']+.15))/.45)
    return max(o, o2), rise+leave*620, enter
def drawer(c, t, a, part):
    o, dy, _ = drawer_geom(t); depth = 160*o; y = DY+dy
    glow = ease((t-(T['etsi']+.3))/.5)
    if part == 'back':
        c.move_to(DX-DW/2, y); c.line_to(DX-DW/2+55, y-depth); c.line_to(DX+DW/2-55, y-depth); c.line_to(DX+DW/2, y); c.close_path()
        g = cairo.LinearGradient(0, y-depth, 0, y); g.add_color_stop_rgb(0, *rgb('1C120C')); g.add_color_stop_rgb(1, *rgb('3A271A'))
        c.set_source(g); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
        if glow > 0 and depth > 4:                                                         # lumière dorée qui sort du tiroir
            c.move_to(DX-DW/2+30, y-4); c.line_to(DX-DW/2+60, y-depth); c.line_to(DX+DW/2-60, y-depth); c.line_to(DX+DW/2-30, y-4); c.close_path()
            c.set_source_rgba(*rgb(GD2), .85*glow*a); c.fill()
            for j in range(9):
                ang = -math.pi/2+(j-4)*.17+.03*math.sin(t*2+j); L = 900*glow
                xs = DX+(j-4)*50
                gb = cairo.LinearGradient(xs, y-depth, xs+L*math.cos(ang), y-depth+L*math.sin(ang)); gb.add_color_stop_rgba(0, *rgb(GD2), .30*glow*a); gb.add_color_stop_rgba(1, *rgb(GD), 0)
                c.move_to(xs-18, y-depth); c.line_to(xs+18, y-depth); c.line_to(xs+L*math.cos(ang)+70, y-depth+L*math.sin(ang)); c.line_to(xs+L*math.cos(ang)-70, y-depth+L*math.sin(ang)); c.close_path()
                c.set_source(gb); c.fill()
    else:
        fh = 200
        g = cairo.LinearGradient(0, y, 0, y+fh)
        for u, k in ((0, '7A5638'), (.08, '5E412B'), (1, '3E2A1B')): g.add_color_stop_rgb(u, *rgb(k))
        rr(c, DX-DW/2+8, y+14, DW, fh, 14); c.set_source_rgba(0, 0, 0, .45*a); c.fill()
        rr(c, DX-DW/2, y, DW, fh, 14); c.set_source(g); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
        for j in range(7):
            yy = y+26+j*25; c.move_to(DX-DW/2+30, yy)
            for xx in range(0, DW-60, 40): c.line_to(DX-DW/2+30+xx, yy+4*math.sin(xx*.03+j))
            c.set_line_width(1.5); c.set_source_rgba(0, 0, 0, .12*a); c.stroke()
        rr(c, DX-95, y+fh/2-15, 190, 30, 15)
        gh = cairo.LinearGradient(0, y+fh/2-15, 0, y+fh/2+15); gh.add_color_stop_rgb(0, *rgb('FFE3A0')); gh.add_color_stop_rgb(1, *rgb('B8842E'))
        c.set_source(gh); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
        if glow > 0: rr(c, DX-DW/2, y, DW, 6, 3); c.set_source_rgba(*rgb(GD2), .9*glow*a); c.fill()
DUST = [(float(np.random.default_rng(i).uniform(-300, 300)), float(np.random.default_rng(i+9).uniform(.5, 1.3)), float(np.random.default_rng(i+50).uniform(-1, 1))) for i in range(22)]
def dust(c, t, a):
    k = t-(T['tiroir']+.84)
    if not 0 < k < 1.3: return
    for dx, sp, d in DUST:
        x = DX+dx+d*120*ease(k/1.3); y = DY-6-90*ease(k/1.3)*sp; r = 8+34*ease(k/1.3)
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(.85, .8, .72, .20*a*(1-k/1.3)); c.fill()

# ---------- la courbe : clôtures annuelles d'Apple, en dollars, ajustées des divisions (hors dividendes) ----------
YRS = [2007.91, 2008.99, 2009.99, 2010.99, 2011.99, 2012.99, 2013.99, 2014.99, 2015.99, 2016.99, 2017.99, 2018.99, 2019.99, 2020.99, 2021.99, 2022.99, 2023.99, 2024.99, 2025.99, 2026.84]
PRX = [6.58, 3.05, 7.53, 11.52, 14.46, 19.01, 20.04, 27.59, 26.32, 28.96, 42.31, 39.44, 73.41, 132.69, 177.57, 129.93, 192.53, 250.42, 271.9, 339.11]
SHARES = 399*1.4738/6.58                                                                  # 89,4 actions
def fx(yr): return lerp(1.4738, 1.1172, clamp((yr-2007.91)/(2026.84-2007.91)))              # dollar/euro interpolé, juste aux deux bouts
def eur(yr, p): return SHARES*p/fx(yr)
CX0, CX1, CY0, CY1 = 150, 930, 890, 440                                                   # repère de la courbe (écran, avant caméra)
def gx(yr): return lerp(CX0, CX1, (yr-YRS[0])/(YRS[-1]-YRS[0]))
def gy(p): return lerp(CY0, CY1, p/360)
@functools.lru_cache(maxsize=1)
def curve_pts():
    """points denses : interpolation de Hermite monotone entre les clôtures annuelles (pas de bosse inventée)"""
    xs = np.array(YRS); ys = np.array(PRX); n = len(xs); d = np.diff(ys)/np.diff(xs); m = np.zeros(n)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n-1): m[i] = 0 if d[i-1]*d[i] <= 0 else 2/(1/d[i-1]+1/d[i])
    out = []
    for i in range(n-1):
        h = xs[i+1]-xs[i]
        for u in np.linspace(0, 1, 40, endpoint=False):
            h00 = 2*u**3-3*u**2+1; h10 = u**3-2*u**2+u; h01 = -2*u**3+3*u**2; h11 = u**3-u**2
            out.append((xs[i]+u*h, h00*ys[i]+h10*h*m[i]+h01*ys[i+1]+h11*h*m[i+1]))
    out.append((xs[-1], ys[-1])); return np.array(out)
def draw_u(t):
    """avancement de la courbe : vitesse régulière, départ et arrivée en douceur"""
    u = clamp((t-(T['aurais']+.1))/1.75); return u*u*(3-2*u)*.35+u*.65
def head(t):
    P = curve_pts(); u = draw_u(t); i = u*(len(P)-1); i0 = int(i); fr = i-i0; i1 = min(i0+1, len(P)-1)
    yr = lerp(P[i0][0], P[i1][0], fr); p = lerp(P[i0][1], P[i1][1], fr); return yr, p, u
def chart(cv, c, t, a):
    if a <= 0: return
    P = curve_pts(); yr, p, u = head(t); n = max(2, int(u*(len(P)-1))+1)
    pts = [(gx(x), gy(y)) for x, y in P[:n]]+[(gx(yr), gy(p))]
    for yv in (100, 200, 300):                                                                 # grille discrète
        c.move_to(CX0, gy(yv)); c.line_to(CX1, gy(yv)); c.set_line_width(1.5); c.set_source_rgba(1, 1, 1, .07*a); c.stroke()
        text(c, f"{yv} $", CX0-14, gy(yv), 'sb', 20, ICE, 'r', .45*a)
    c.move_to(CX0, CY0); c.line_to(CX1, CY0); c.set_line_width(2); c.set_source_rgba(1, 1, 1, .25*a); c.stroke()
    text(c, "COURS DE L'ACTION APPLE · CLÔTURES ANNUELLES, HORS DIVIDENDES", CX0-40, CY1-36, 'sb', 19, ICE, 'l', .55*a, 1)
    for yy in (2008, 2011, 2014, 2017, 2020, 2023, 2026):
        if yr >= yy-.4: text(c, str(yy), gx(yy), CY0+34, 'sb', 22, ICE, 'c', .7*a*ease((yr-yy+.4)/.6))
    c.move_to(pts[0][0], CY0)                                                                  # aire dorée sous la courbe
    for x, y in pts: c.line_to(x, y)
    c.line_to(pts[-1][0], CY0); c.close_path()
    g = cairo.LinearGradient(0, CY1, 0, CY0); g.add_color_stop_rgba(0, *rgb(GD), .38*a); g.add_color_stop_rgba(1, *rgb(GD), .02*a); c.set_source(g); c.fill()
    for lw, al in ((22, .10), (12, .22), (5, 1.0)):                                            # ligne lumineuse
        c.move_to(*pts[0]); [c.line_to(x, y) for x, y in pts[1:]]
        c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_source_rgba(*rgb(GD2 if lw == 5 else GD), al*a); c.stroke()
    for yy, lab in ((2008.99, "CRISE DE 2008"), (2020.2, "COVID")):                            # repères qui passent
        if yr > yy+.15:
            P_ = P[np.argmin(abs(P[:, 0]-yy))]; x, y = gx(P_[0]), gy(P_[1]); k = ease((yr-yy-.15)/.8)*(1-ease((t-(T['num']+1.1))/.3))
            c.move_to(x, y+14); c.line_to(x, y+52); c.set_line_width(2); c.set_source_rgba(1, 1, 1, .5*k*a); c.stroke()
            text(c, lab, x, y+70, 'xb', 18, ICE, 'c', .8*k*a, 2)
    hx_, hy_ = gx(yr), gy(p)                                                                   # tête de la courbe : point brillant + compteur
    rg = cairo.RadialGradient(hx_, hy_, 0, hx_, hy_, 60); rg.add_color_stop_rgba(0, 1, .95, .8, .9*a); rg.add_color_stop_rgba(1, 1, .8, .3, 0)
    c.set_source(rg); c.arc(hx_, hy_, 60, 0, 2*math.pi); c.fill(); c.arc(hx_, hy_, 9, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a); c.fill()
    return hx_, hy_, yr, p
def head_label(c, t, hx_, hy_, yr, p, a):
    v = eur(yr, p); s_ = fmt(v)+" €"; done = t > T['num']+.95
    if done: return
    w = tw(c, s_, 'xb', 34)+40; x0 = min(max(hx_-w/2, 40), W-40-w); y0 = hy_-86
    rr(c, x0, y0, w, 56, 14); c.set_source_rgba(*rgb(INK), .85*a); c.fill_preserve(); c.set_line_width(2); c.set_source_rgba(*rgb(GD), .9*a); c.stroke()
    text(c, s_, x0+w/2, y0+28, 'xb', 34, GD2, 'c', a)
    text(c, str(int(yr)), x0+w/2, y0+76, 'sb', 18, ICE, 'c', .0)

# ---------- pièces ----------
COINS = []
_r = np.random.default_rng(11)
for i in range(34): COINS.append((float(_r.uniform(-1, 1)), float(_r.uniform(.6, 1.4)), float(_r.uniform(0, 6.3)), float(_r.uniform(.0, .25)), float(_r.uniform(18, 34))))
def coins(c, t, x0, y0, a):
    k0 = t-(T['num']+.95)
    if k0 <= 0 or k0 > 2.2: return
    for vx, vy, ph, dl, r in COINS:
        k = k0-dl
        if k <= 0: continue
        x = x0+vx*680*k-220*k; y = y0-vy*1050*k+2300*k*k; spin = abs(math.cos(ph+k*9))
        if y > 1000: continue
        c.save(); c.translate(x, y); c.scale(max(.15, spin), 1)
        g = cairo.RadialGradient(-r*.3, -r*.3, 1, 0, 0, r); g.add_color_stop_rgb(0, *rgb('FFF1B8')); g.add_color_stop_rgb(.6, *rgb('F5B400')); g.add_color_stop_rgb(1, *rgb('A86E00'))
        c.arc(0, 0, r, 0, 2*math.pi); c.set_source(g); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a*(1-clamp((k0-1.6)/.6)))
        c.arc(0, 0, r*.68, 0, 2*math.pi); c.set_line_width(2); c.set_source_rgba(.55, .35, 0, .5*a); c.stroke(); c.restore()

# ---------- tuile Apple ----------
@functools.lru_cache(maxsize=48)
def logo_tile(size):
    im = Image.open(f'{D}/logos/AAPL.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size+60, size+60), 0); m = Image.new('L', (size+60, size+60), 0)
    ImageDraw.Draw(m).rounded_rectangle((30, 40, 30+size, 40+size), radius=size*.22, fill=150)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(12))); sh.alpha_composite(im, (30, 30)); return sh
def tile_state(t):
    """sort du tiroir dans la lumière, se pose, puis file se poser au départ de la courbe"""
    k = t-T['apple']+.12
    if k <= 0: return None
    u = back(k/.5, 1.4); _, dy, _ = drawer_geom(t)
    x = 540; y = lerp(DY+dy-40, 430, u); sz = lerp(60, 230, ease(k/.45)); rot = lerp(-.6, 0, back(k/.5))
    kf = t-(T['aurais']-.15)
    if kf > 0:
        v = inout(kf/.42); x = lerp(540, gx(YRS[0]), v); y = lerp(430, gy(PRX[0]), v)-120*math.sin(math.pi*v); sz = lerp(230, 18, v); rot = lerp(0, 1.2, v)
        if kf > .42: return None
    return x, y, sz, rot

# ---------- scènes (coordonnées écran ; la caméra s'applique à tout le calque ensuite) ----------
def hud(t):
    """éléments fixes à l'écran, hors caméra : le résultat final"""
    cv = Image.new('RGBA', (W, H), 0); s, c = surface()
    a_c = win(t, T['aurais']-.05, T['etoi'], .2, .3); kd = t-(T['num']+.95)
    if kd > 0 and a_c > 0:
        glow_text(cv, "27 100 €", 570, 235, 150, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.85, a=a_c*ease(kd/.08), scale=lerp(1.8, 1, back(kd/.3, 1.8)), reflect=False)
        grp(c, a_c*ease(kd/.1), lambda c: text(c, "≈", 190, 233, 'xb', 100, GD2, 'c', 1))
        grp(c, a_c*ease((kd-.25)/.2), lambda c: gpill(c, "×68 EN 19 ANS", 540, 345, GR, 30), dy=10*(1-ease((kd-.25)/.3)))
        cv.alpha_composite(to_img(s)); s, c = surface()
        put_emoji(cv, '🤑', 945, 225, 64, kd-.2, a_c)
    cv.alpha_composite(to_img(s)); return cv
def content(t):
    cv = Image.new('RGBA', (W, H), 0); s, c = surface()
    info = {}
    # --- titre et date ---
    a_t = win(t, 0, T['sorti']-.05, .01, .2)
    if a_t > 0:
        grp(c, a_t*ease((t-.25)/.2), lambda c: text(c, scramble("LE PREMIER", ease((t-.25)/.5)), 540, 222, 'mono', 34, ICE, 'c', .9, 8))
        if t > .55: glow_text(cv, "iPHONE", 540, 318, 120, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.6, a=a_t*ease((t-.55)/.1), scale=lerp(1.7, 1, back((t-.55)/.3, 1.8)), reflect=False)
        put_emoji(cv, '🤔', 860, 280, 66, t-1.0, a_t)
    a_d = win(t, T['sorti'], T['auj'], .2, .25)
    if a_d > 0:
        k = t-T['sorti']
        grp(c, a_d, lambda c: text(c, scramble("SORTIE EN FRANCE", ease(k/.45), 5), 540, 210, 'mono', 32, ICE, 'c', .9, 6))
        grp(c, a_d, lambda c: text(c, scramble("29.11.2007", ease((k-.15)/.6), 9), 540, 285, 'k', 96, WHITE, 'c', 1, 6))
        put_emoji(cv, '🇫🇷', 905, 285, 58, k-.7, a_d)
    # --- le prix ---
    kp = t-T['prix']; a_p = win(t, T['prix'], T['auj']+.1, .0, .3)
    if kp > 0 and a_p > 0:
        sc_out = 1+.6*ease((t-T['auj'])/.3)
        if t < T['auj']: slam(cv, "399 €", 760, 640, 150, T['prix']+.12, t, .09, a=a_p)
        else: glow_text(cv, "399 €", 760, 640, 150, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a_p, scale=sc_out, reflect=False)
        grp(c, a_p*ease((kp-.7)/.25), lambda c: gpill(c, "8 GO · CHEZ ORANGE", 760, 760, 'E8EEF8', 26), dy=10*(1-ease((kp-.7)/.3)))
    # --- 19 ans plus tard ---
    a_l = win(t, T['auj'], T['etsi'], .15, .2)
    if a_l > 0:
        k = t-T['auj']
        grp(c, a_l, lambda c: text(c, scramble("19 ANS PLUS TARD", ease(k/.5), 13), 540, 250, 'k', 64, WHITE, 'c', 1, 4))
        def yrs(c, k=k):
            text(c, "2007", 440, 330, 'mono', 30, ICE, 'c', .7, 4); text(c, "2026", 640, 330, 'mono', 30, ICE, 'c', .7, 4)
            u = ease((k-.5)/.5); c.move_to(490, 330); c.line_to(490+80*u, 330); c.set_line_width(3); c.set_source_rgba(1, 1, 1, .7); c.stroke()
            if u > .9: c.move_to(574, 322); c.line_to(586, 330); c.line_to(574, 338); c.stroke()
        grp(c, a_l*ease((k-.4)/.3), yrs)
    # --- tiroir + téléphone ---
    on_drawer = T['tiroir']-.3 < t < T['place']+.65
    a_dr = 1-ease((t-(T['place']+.2))/.4)
    if on_drawer: drawer(c, t, a_dr, 'back')
    cv.alpha_composite(to_img(s)); s, c = surface()
    if t < T['tiroir']+.75:
        x, y, sc, yaw, roll, mode = phone_state(t)
        clip = None
        if t > T['tiroir']+.05:
            o, dy, _ = drawer_geom(t); top = DY+dy-160*o; kd = clamp((t-(T['tiroir']+.05))/.4)
            clip = (lerp(-2000, top, kd), DY+dy)
        draw_phone(cv, t, x, y, sc, yaw, roll, mode, 1.0, shadow=t < T['tiroir'], clip_y=clip)
    if on_drawer: drawer(c, t, a_dr, 'front'); dust(c, t, 1.0)
    # --- et si… (retour en arrière) ---
    a_e = win(t, T['etsi'], T['aurais']-.1, .1, .25)
    if a_e > 0:
        k = t-T['etsi']
        def rew(c):
            for j in range(2):
                x0 = 400+j*64-30*math.sin(k*10)*ease(1-k/.8)
                c.move_to(x0+56, 222); c.line_to(x0, 252); c.line_to(x0+56, 282); c.close_path(); c.set_source_rgba(1, 1, 1, .9); c.fill()
            text(c, "2007", 640, 252, 'k', 64, WHITE, 'l', 1, 4)
        grp(c, a_e*(1-ease((t-T['apple'])/.25)), rew)
        if t > T['apple']-.1:
            grp(c, a_e, lambda c: text(c, "ACTIONS APPLE", 540, 252, 'k', 64, WHITE, 'c', ease((t-T['apple']+.1)/.15), 4))
    cv.alpha_composite(to_img(s)); s, c = surface()
    ts = tile_state(t)
    if ts:
        x, y, sz, rot = ts; im = logo_tile(max(8, int(sz))).rotate(math.degrees(-rot), resample=Image.BICUBIC, expand=True)
        cv.alpha_composite(im, (int(x-im.width/2), int(y-im.height/2)))
    kq = t-(T['place']+.25)
    if kq > 0 and t < T['aurais']:
        grp(c, ease(kq/.2)*(1-ease((t-T['aurais']+.25)/.2)), lambda c: gpill(c, "399 € = 89 ACTIONS", 540, 640, GD, 36), dy=14*(1-ease(kq/.3)))
        grp(c, ease((kq-.15)/.3)*(1-ease((t-T['aurais']+.25)/.2)), lambda c: text(c, "le 29/11/2007, divisions d'actions comprises", 540, 712, 'sb', 24, ICE, 'c', .75))
    # --- la courbe ---
    a_c = win(t, T['aurais']-.05, T['etoi'], .2, .3)
    if a_c > 0:
        hx_, hy_, yr, p = chart(cv, c, t, a_c); info['head'] = (hx_, hy_)
        head_label(c, t, hx_, hy_, yr, p, a_c)
        coins(c, t, hx_, hy_, a_c)
    # --- duel final ---
    a_f = win(t, T['etoi']-.05, DUR+1, .2, 0)
    if a_f > 0:
        k = t-T['etoi']
        glow_text(cv, "ET TOI ?", 540, 235, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a_f*ease(k/.15), scale=lerp(1.6, 1, back(k/.35, 1.6)), reflect=False)
        for j in range(2):
            kk = k-.18-j*.12
            if kk <= 0: continue
            cx = 540+(-225 if j == 0 else 225); cy = 545+28*(1-ease(kk/.35)); u = ease(kk/.35)
            pulse = 1+.06*math.exp(-max(0, t-T['choisi']-j*.16)*5)*math.sin(max(0, t-T['choisi']-j*.16)*16) if t > T['choisi']+j*.16 else 1
            def d(kq, w, h, j=j):
                text(kq, ("L'IPHONE" if j == 0 else "LES ACTIONS"), w/2, h-86, 'xb', 32, WHITE, 'c', 1, 2)
                text(kq, ("399 €" if j == 0 else "≈ 27 100 €"), w/2, h-40, 'xb', 34, (ICE if j == 0 else GD2), 'c', .95)
            place(cv, gp(350, 330, d, 'CFE8FF' if j == 0 else 'FFE9C0'), tilt_quad(cx, cy, 350*pulse, 330*pulse, ry=(.2 if j == 0 else -.2)*(1-u)), a_f*ease(kk/.25), 18, .5)
            if j == 0:
                draw_phone(cv, t, cx, cy-60, .26*pulse, .25+.08*math.sin(t*1.5), 0, dict(on=1, icons=2, grey=.0), a_f*ease(kk/.25), shadow=False)
            else:
                ss, cc = surface()
                P = curve_pts()[::6]; cc.move_to(cx-110, cy-10)
                for x, y in P: cc.line_to(cx-110+(x-YRS[0])/(YRS[-1]-YRS[0])*220, cy-10-y/360*130*ease(kk/.5))
                cc.set_line_width(6); cc.set_line_cap(cairo.LINE_CAP_ROUND); cc.set_line_join(cairo.LINE_JOIN_ROUND); cc.set_source_rgba(*rgb(GD2), a_f); cc.stroke()
                cv.alpha_composite(to_img(ss))
        def ou(c):
            kk = k-.45; sc = back(kk/.3, 2.0); c.save(); c.translate(540, 545); c.scale(sc, sc); c.rotate(.6*(1-ease(kk/.4)))
            c.arc(0, 0, 46, 0, 2*math.pi); col(c, GD); c.fill(); text(c, "OU", 0, 0, 'k', 34, INK, 'c', 1, 1); c.restore()
        if k > .45: grp(c, a_f, ou)
        al = ease((t-T['choisi']-.45)/.35)
        def lg(c):
            text(c, "Dis-le en commentaire 👇".replace(' 👇', ''), 540, 772, 'xb', 36, WHITE, 'c', 1)
            c.push_group(); logo_symbol(c, 410, 845, 38); c.pop_group_to_source(); c.paint_with_alpha(1)
            text(c, "Actions_Benefices", 441, 845, 'b', 27, WHITE, 'l', 1)
            text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 900, 'sb', 20, ICE, 'c', .65)
            text(c, "Les performances passées ne préjugent pas des performances futures.", 540, 928, 'sb', 20, ICE, 'c', .65)
        grp(c, a_f*al, lg)
    cv.alpha_composite(to_img(s))
    return cv, info

# ---------- caméra : poussées, panoramiques, embarquée sur la courbe, secousses aux impacts ----------
SHAKES = [(T['prix']+.12, 10), (T['prix']+.48, 8), (T['tiroir']+.7, 16), (T['apple']-.1, 10), (T['num']+.95, 14), (T['etoi'], 6)]
def camera(t):
    """renvoie (cx, cy, zoom, rot) : le point (cx, cy) du calque est placé au centre visuel (540, 620)"""
    cx, cy, z, r = 540, 620, 1.0, 0.0
    z = lerp(1.18, 1.0, ease5(t/1.6))                                                            # ouverture : on recule
    if t > T['sorti']: z = lerp(z, 1.05, inout((t-T['sorti'])/1.8))
    if t > T['prix']: z = lerp(z, 1.0, ease((t-T['prix'])/.5)); cx = lerp(540, 560, ease((t-T['prix'])/.5))
    if t > T['auj']: cx = lerp(cx, 540, ease((t-T['auj'])/.6)); z = lerp(z, 1.04, ease((t-T['auj'])/1.2))
    if t > T['tiroir']: cy = lerp(620, 690, inout((t-T['tiroir'])/.8)); z = lerp(z, 1.10, inout((t-T['tiroir'])/.8))
    if t > T['etsi']:
        u = inout((t-T['etsi'])/1.0); cy = lerp(cy, 560, u); z = lerp(z, 1.0, u)
        r = .035*math.sin(clamp((t-T['etsi'])/.6)*math.pi)                                       # petit roulis du retour en arrière
    if t > T['aurais']-.1:                                                                        # caméra embarquée sur la tête de la courbe
        yr, p, u = head(t); hx_, hy_ = gx(yr), gy(p)
        kin = inout((t-(T['aurais']-.1))/.35); kout = inout((t-(T['num']+.75))/.5)
        tz = lerp(1.55, 1.0, kout); tx = lerp(hx_, 540, kout); ty = lerp(hy_, 620, kout)
        cx, cy, z = lerp(cx, tx, kin), lerp(cy, ty, kin), lerp(z, tz, kin)
    if t > T['etoi']-.1:
        u = inout((t-(T['etoi']-.1))/.4); cx, cy, z = lerp(cx, 540, u), lerp(cy, 600, u), lerp(z, 1.0, u)
        z = lerp(z, 1.03, inout((t-T['etoi'])/2.2))
    sx = sy = 0.0
    for t0, amp in SHAKES:                                                                        # secousse amortie
        k = t-t0
        if 0 < k < .45: e = amp*math.exp(-k*9); sx += e*math.sin(k*70); sy += e*math.cos(k*57)
    return cx+sx, cy+sy, z, r
def apply_cam(img, cam, anchor=(540, 620)):
    cx, cy, z, r = cam
    M = cv2.getRotationMatrix2D((cx, cy), math.degrees(r), z); M[0, 2] += anchor[0]-cx; M[1, 2] += anchor[1]-cy
    arr = cv2.warpAffine(np.asarray(img), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return Image.fromarray(arr, 'RGBA')
def flash(t):
    v = 0.0
    for t0, a in ((T['prix']+.12, .25), (T['tiroir']+.7, .18), (T['apple']-.1, .45), (T['num']+.95, .2)):
        k = t-t0
        if 0 <= k < .25: v = max(v, a*(1-k/.25)**2)
    return v

# ---------- Mister Coin (3 clips ; changements pendant les silences 8,07-8,59 et 13,02-13,49) ----------
QUES, ENT = 'classique_parle_question', 'classique_parle_enthousiaste'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, QUES, 'voix'), (8.25, ENT, 'voix'), (13.2, QUES, 'voix')], voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    cam = camera(t)
    cv = background(t, cam)
    lay, info = content(t)
    lay = apply_cam(lay, cam)
    kr = t-T['etsi']                                                                               # retour en arrière : décalage chromatique + lignes
    if 0 < kr < .55:
        e = math.sin(kr/.55*math.pi); arr = np.asarray(lay).copy(); sh = int(10*e)
        if sh: arr[..., 0] = np.roll(arr[..., 0], sh, 1); arr[..., 2] = np.roll(arr[..., 2], -sh, 1)
        arr[::6, :, 3] = (arr[::6, :, 3]*(1-.5*e)).astype(np.uint8); lay = Image.fromarray(arr, 'RGBA')
    cv.alpha_composite(lay); cv.alpha_composite(hud(t))
    fl = flash(t)
    if fl > 0: cv = Image.blend(cv, Image.new('RGBA', (W, H), (255, 244, 220, 255)), fl)
    X, Y = coin_pos(t); rgb_, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx_ = MC.feet_x(al, Y) if Y > FEET-30 else X
    if fx_ is not None:
        k = 1/(1+max(0, FEET-Y)/150)
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx_), FEET-3), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .55*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
        a *= (1-m[..., None])
    a = a*(1-al[..., None])+rgb_*al[..., None]
    cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < T['fin']+.35:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        al_ *= 1-ease((t-T['fin'])/.3)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'whoosh'), (.55, 'impact'), (.6, 'glint'), (T['sorti'], 'click'), (T['sorti']+.15, 'riser'), (T['sorti']+.7, 'swish')]
    ev += [(T['sorti']+.75+i*.035*3, 'pop') for i in range(0, 16, 3)]                               # icônes en cascade (un pop sur trois)
    ev += [(T['prix'], 'whoosh')] + [(T['prix']+.12+i*.09, 'thud') for i in (0, 1, 2, 4)] + [(T['prix']+.75, 'pop')]
    ev += [(T['auj'], 'trans'), (T['auj']+.1, 'beep'), (T['tiroir']-.25, 'swish'), (T['tiroir']+.1, 'whoosh'), (T['tiroir']+.7, 'crash'), (T['tiroir']+.72, 'thud')]
    ev += [(T['etsi'], 'zoom'), (T['etsi']+.3, 'riser'), (T['apple']-.1, 'impact'), (T['apple']-.05, 'glint'), (T['place']+.25, 'pop')]
    ev += [(T['aurais']-.15, 'whoosh'), (T['aurais']+.1, 'count'), (T['num']+.95, 'boom'), (T['num']+.97, 'coins'), (T['num']+1.0, 'paid'), (T['num']+1.2, 'pop')]
    ev += [(T['etoi'], 'swish'), (T['etoi']+.18, 'pop'), (T['etoi']+.3, 'pop'), (T['etoi']+.45, 'impact'), (T['choisi'], 'tick'), (T['choisi']+.16, 'tick'), (T['choisi']+.45, 'glint')]
    ev += [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)]
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
