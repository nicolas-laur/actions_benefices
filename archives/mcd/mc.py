"""McDonald's : test format court 30 s, promesse plein écran dès 0:00. Fond 3D pluie de frites, néon, borne, ticket."""
import sys, math, re, subprocess, os, functools
import numpy as np, cairo
from PIL import Image, ImageEnhance
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/mcd')
from mty2 import *
FPS = 60
P0, FX0, P1, FX1 = 242.65, 1.1555, 235.65, 1.1181
DIVS = [1.38]*4+[1.52]*4+[1.67]*4+[1.77]*4+[1.86]*4
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*sum(DIVS)/FX1; TOT = VAL+DIV
assert round(VAL) == 1004 and round(DIV) == 140 and round(TOT) == 1143
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
NB = ' '
SC = [("s1", 0.0, "5 ans de McDo en Bourse = [+4 €]."), ("s2", 4.6, "L'action a perdu [30 %] depuis février."),
      ("s3", 9.4, "Les clients modestes viennent [moins] depuis 2 ans."), ("s4", 14.0, "Ses ventes ne progressent plus que de [1,3 %]."),
      ("s5", 18.6, "Ce qui sauve tout : [140 €] de dividendes."), ("s6", 22.8, "Total : [≈ 1 143 €]. ×1,14 en 5 ans."),
      ("s7", 27.2, "Tu achètes, tu vends ou tu [attends] ?")]
DUR = 30.8
START = {k: a for k, a, _ in SC}; CAP = {k: c for k, _, c in SC}; ORDER = [k for k, _, _ in SC]
def cur(t):
    r = ORDER[0]
    for k in ORDER:
        if t >= START[k]: r = k
    return r
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]

@functools.lru_cache(maxsize=24)
def fry(i):
    p = f'/home/claude/mcd/seq_fries/f{i+1:04d}.png'
    if not os.path.exists(p): p = '/tmp/claude-0/fr1.png'
    return Image.open(p).convert('RGBA').resize((W, H), Image.BICUBIC)
def background(t, dim):
    f = (t*30) % 150; i = int(f); fr = f-i
    a = fry(i); im = Image.blend(a, fry((i+1) % 150), fr) if fr > 0.05 else a.copy()
    return ImageEnhance.Brightness(im).enhance(dim)
@functools.lru_cache(maxsize=4)
def neon_cached(key):
    if key == 'promise': return neon_text("1 004 €", 540, 860, 230, YEL, track=-4)
    if key == 'q': return neon_text("Toujours appétissant ?", 540, 470, 84, YEL)
    if key == 'frame': return glow_layer(lambda c: (rr(c, 70, 380, 940, 860, 40), c.set_line_width(5), col(c, YEL), c.stroke()), (22, 8), (1.6, 1.4))
@functools.lru_cache(maxsize=2)
def halo_cached():
    return glow_layer(lambda c: (rr(c, 190, 330, 700, 880, 6), col(c, 'FFB347', .3), c.fill()), (60, 30), (1.4, .8))
@functools.lru_cache(maxsize=64)
def receipt_cached(q): return receipt_img(q/60)
def darkspot(c, y, r=620, a=.55):
    g = cairo.RadialGradient(540, y, 0, 540, y, r); g.add_color_stop_rgba(0, 0, 0, 0, a); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.save(); c.translate(540, y); c.scale(1, .8); c.translate(-540, -y); c.set_source(g); c.paint(); c.restore()
def neon_alpha(t):
    """néon : allumé dès 0:00, deux micro-grésillements"""
    if 0.18 < t < 0.24 or 0.42 < t < 0.46: return 0.35
    return 1.0
ITEMS = [("s2", "L'ACTION", "depuis son plus haut de février", "−30 %", RED, 'down'), ("s3", "CLIENTS MODESTES", "ils viennent moins depuis 2 ans", "↓", RED, 'people'),
         ("s4", "VENTES COMPARABLES", "avril-juin 2026, au ralenti", "+1,3 %", WHITE, 'flat'), ("s5", "DIVIDENDES", "versés en 5 ans sur 1 000 €", "+140 €", GREEN, 'coin')]

def frame(t):
    k = cur(t); s = t-START[k]
    if k == 's1': base = background(t, 0.75)
    else: base = background(t, 0.42)
    S, c = surface()
    if k == 's1':
        darkspot(c, 760, 700, .6)
        layer_neon = neon_cached('promise')
    elif k in ('s2', 's3', 's4', 's5'):
        layer_neon = neon_cached('frame')
    elif k == 's6': layer_neon = halo_cached()
    else: darkspot(c, 700, 700, .55); layer_neon = neon_cached('q')
    darkspot(c, 1370, 560, .55)   # zone des sous-titres plus calme
    # --- calque UI
    if k == 's1':
        text(c, "1 000 € DANS MCDO IL Y A 5 ANS", 540, 420, 'sb', 34, YEL, 'c', 1, 4)
        text(c, "1 000 €", 540, 560, 'k', 104, WHITE, 'c', .6)
        c.set_line_width(8); col(c, YEL, .9); c.move_to(540, 640); c.line_to(540, 715); c.stroke(); c.move_to(508, 688); c.line_to(540, 722); c.line_to(572, 688); c.stroke()
        a = clamp((t-0.5)/0.3); text(c, "5 ans pour gagner… 4 €", 540, 1035, 'xb', 52, WHITE, 'c', a)
        a = ease((t-1.1)/0.3)
        if a > 0:
            c.save(); sc_ = lerp(1.3, 1, a); c.translate(540, 1178); c.scale(sc_, sc_); c.translate(-540, -1178)
            w = tw(c, "Tu achètes ? Réponds 1, 2 ou 3", 'xb', 34)+70; rr(c, 540-w/2, 1140, w, 76, 38); col(c, RED, a); c.fill(); text(c, "Tu achètes ? Réponds 1, 2 ou 3", 540, 1178, 'xb', 34, WHITE, 'c', a); c.restore()
    elif k in ('s2', 's3', 's4', 's5'):
        e = ease((t-START['s2'])/0.35); dy = 60*(1-e)
        c.save(); c.translate(0, dy); c.push_group()
        glass_panel(c, 70, 380, 940, 860, 40, '2A0C08', .6)
        text(c, "TA COMMANDE · 5 ANS", 120, 440, 'xb', 40, YEL, 'l')
        for j, (sid, ti, de, pr, cc, ic) in enumerate(ITEMS):
            ts = START[sid]+0.25
            if t < ts: continue
            u = ease((t-ts)/0.35); y = 510+j*170
            c.save(); c.translate(80*(1-u), 0); kiosk_row(c, y, ti, de, pr, cc, ic, u)
            if t-ts < 0.5:   # surbrillance de l'article ajouté
                rr(c, 110, y, 860, 150, 26); c.set_line_width(4); col(c, YEL, 1-(t-ts)/0.5); c.stroke()
            c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(e); c.restore()
    elif k == 's7':
        for j, (lab, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", YEL))):
            a = ease((s-0.25-j*0.15)/0.3)
            if a <= 0: continue
            y = 620+j*140; c.push_group(); glass_panel(c, 250, y, 580, 108, 54, '2A0C08', .6); rr(c, 250, y, 580, 108, 54); c.set_line_width(3); col(c, cc); c.stroke()
            text(c, f"{j+1}", 310, y+54, 'k', 42, cc); text(c, lab, 560, y+54, 'xb', 50, WHITE); c.pop_group_to_source(); c.paint_with_alpha(a)
        a = ease((s-0.9)/0.4)
        if a > 0:
            c.save(); c.translate(540, 1090); c.scale(.5, .5); c.translate(-540, -1090); c.push_group(); logo_symbol(c, 540, 1090, 190); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
            text(c, "Actions_Benefices", 540, 1175, 'b', 30, WHITE, 'c', a)
    progress(c, clamp(t/DUR))
    items = parse(CAP[k]); ka = 1.0 if k == 's1' else clamp(s/0.2)
    if ka > 0: c.push_group(); caption(c, items, 1352, 46); c.pop_group_to_source(); c.paint_with_alpha(ka)
    if k in ('s6', 's7'): text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1470, 'm', 22, SUB, 'c', .9)
    ui = to_img(S)
    out = base
    if k == 's1':
        n = neon_cached('promise').copy()
        if neon_alpha(t) < 1: n.putalpha(n.getchannel('A').point(lambda v: int(v*neon_alpha(t))))
        dark = Image.new('RGBA', (W, H)); out.alpha_composite(ui); out.alpha_composite(n)
    elif k == 's6':
        q = int(clamp((s-0.15)/2.2)*60); hl = halo_cached().copy(); hh = int(330+(880+20)*q/60)
        m = np.zeros((H, W), np.uint8); m[:hh+30, :] = 255; hl.putalpha(Image.fromarray(np.minimum(np.asarray(hl.getchannel('A')), m)))
        out.alpha_composite(hl); out.alpha_composite(receipt_cached(q)); out.alpha_composite(ui)
        if s > 2.5:   # le total « tamponné »
            pass
    elif k == 's7':
        n = neon_cached('q').copy(); a = ease(s/0.3); n.putalpha(n.getchannel('A').point(lambda v: int(v*a))); out.alpha_composite(ui); out.alpha_composite(n)
    else:
        e = ease((t-START['s2'])/0.35); n = neon_cached('frame').copy()
        if e < 1: n.putalpha(n.getchannel('A').point(lambda v: int(v*e)))
        n = n.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -60*(1-e))) if e < 1 else n
        out.alpha_composite(n); out.alpha_composite(ui)
    # transitions : flash bref entre scènes (sauf dans la borne), fondu final
    i = ORDER.index(k)
    if i > 0 and k in ('s2', 's6', 's7') and s < 0.12:
        out = Image.blend(out, Image.new('RGBA', (W, H), (255, 214, 120, 255)), 0.35*(1-s/0.12))
    if t > DUR-0.35: out = Image.blend(out, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t-(DUR-0.35))/0.35))
    return out
def events():
    ev = [(0.0, 'neon'), (0.0, 'impact'), (1.1, 'pop'), (START['s2'], 'swish')]
    for sid, *_ in ITEMS: ev.append((START[sid]+0.25, 'kiosk'))
    ev += [(START['s5']+0.3, 'glint'), (START['s6'], 'swish'), (START['s6']+0.15, 'printer'), (START['s6']+2.4, 'impact'), (START['s6']+2.4, 'glint'),
           (START['s7'], 'neon'), (START['s7']+0.25, 'pop'), (START['s7']+0.4, 'pop'), (START['s7']+0.55, 'pop')]
    return ev
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/mcd/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'/home/claude/mcd/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGBA').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
