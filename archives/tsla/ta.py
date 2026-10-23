"""Tesla : le paradoxe. Vision de conduite autonome, cadres de détection qui verrouillent les chiffres. 2D net, 60 i/s."""
import sys, math, re, subprocess, os
import cairo
from PIL import Image
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/tsla')
from tdy import *
FPS = 60

# ---------- chiffres vérifiés (13 octobre 2026) ----------
P0, FX0, P1, FX1 = 270.36, 1.1555, 378.03, 1.1181
SH = 1000*FX0/P0; VAL = SH*P1/FX1
assert round(VAL) == 1445
assert round(480126/1.25, -3) == 384000 and round(398/0.43) == 926 and round(5.79/2.42, 1) == 2.4
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')
NB = ' '
ST = {'ok': (CYAN, "AUTOPILOTE · ACTIF", 118, None), 'warn': (RED, "ALERTE · RALENTISSEMENT", 52, '6A1A1A'), 'good': (GREEN, "VOIE LIBRE", 128, '1A5A3A'),
      'future': (CYAN, "MODE FUTUR · ACTIVÉ", 140, '2A4A8A'), 'end': (GREEN, "ARRIVÉE À DESTINATION", 30, '1A5A3A')}
SC = [
 ("c01", "Tesla gagne de moins en moins… mais vaut [1 490 milliards $].", 'ok'),
 ("c02", "Et 1 000 € investis il y a 5 ans ? Réponse à la [fin].", 'ok'),
 ("c03", "Côté voitures, ça roule : [480 000] livraisons au 2e trimestre. +25 %.", 'good'),
 ("c04", "Et [486 500] au 3e trimestre, mieux que prévu.", 'good'),
 ("c05", "Chiffre d'affaires : [28,2 milliards $] en 3 mois. +26 %.", 'good'),
 ("c06", "Mais sur 1 $ vendu, il ne garde que [1,4 centime] de résultat d'exploitation.", 'warn'),
 ("c07", "Son résultat d'exploitation : [−57 %] en un an.", 'warn'),
 ("c08", "Et son cash-flow libre passe [dans le rouge].", 'warn'),
 ("c09", "Pendant ce temps, BYD vend ≈ [276 000] électriques de plus que lui.", 'warn'),
 ("c10", "Sur 12 mois : [3,8 milliards $] de bénéfice. −35 %.", 'warn'),
 ("c11", "Pourtant, la Bourse le valorise [1 490 milliards $].", 'ok'),
 ("c12", "Soit ≈ [390 fois] ses bénéfices annuels.", 'warn'),
 ("c13", "Ce qu'on achète, c'est le [futur] : des robotaxis dans 7 villes américaines.", 'future'),
 ("c14", "[1,48 million] d'abonnés à sa conduite autonome supervisée.", 'future'),
 ("c15", "Le Cybercab entre en production. Le robot Optimus est [prévu] fin 2026.", 'future'),
 ("c16", "Tes 1 000 € il y a 5 ans ? ≈ [1 445 €]. ×1,45. Sans dividende.", 'end'),
 ("c17", "Génie visionnaire… ou [bulle] sur roues ?", 'warn'),
 ("c18", "Et toi : tu achètes, tu vends ou tu [attends] ?", 'end'),
 ("c19", "Abonne-toi, like, partage.", 'end'),
]
CAP = {s[0]: s[1] for s in SC}; STATE = {s[0]: s[2] for s in SC}; ORDER = [s[0] for s in SC]
LOCK = 0.35          # instant où le cadre verrouille l'objet (s)
def build():
    tl, t = {}, 0.0
    for cid in ORDER:
        clean = re.sub(r'[\[\]]', '', CAP[cid]); d = max(3.3, len(clean)/19+1.3)
        if cid == 'c01': d = 5.2
        if cid == 'c16': d += 1.4
        if cid == 'c18': d = 4.6
        if cid == 'c19': d = 3.6
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.05
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def cur_scene(t):
    cur = ORDER[0]
    for cid in ORDER:
        if t >= T(cid)-0.001: cur = cid
    return cur
# vitesse continue (lissée) et distance parcourue intégrée → la route défile en cohérence avec le compteur
import numpy as np
_ts = np.arange(0, DUR+1, 1/FPS)
_tgt = np.array([ST[STATE[cur_scene(x)]][2] for x in _ts], float)
_k = int(0.8*FPS); _sp = np.convolve(np.pad(_tgt, (_k, _k), mode='edge'), np.ones(2*_k+1)/(2*_k+1), 'valid')
_dist = np.cumsum(_sp/118*16)/FPS
def speed_at(t): return float(np.interp(t, _ts, _sp))
def dist_at(t): return float(np.interp(t, _ts, _dist))
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]

# ---------- détection ----------
def lock_box(c, s, t0, x, y, w, h, color, label, ink='05070A'):
    """le cadre arrive large et se resserre sur l'objet, puis l'étiquette apparaît"""
    u = ease((s-t0)/LOCK)
    if u <= 0: return False
    k = lerp(1.35, 1.0, u); cx, cy = x+w/2, y+h/2; ww, hh = w*k, h*k
    bracket(c, cx-ww/2, cy-hh/2, ww, hh, color, clamp(u*1.6), lw=4 if w < 600 else 5)
    if s > t0+LOCK*0.8:
        a = clamp((s-t0-LOCK*0.8)/0.15); c.push_group(); tag(c, label, x, y-20, color, 24, ink); c.pop_group_to_source(); c.paint_with_alpha(a)
    # balayage de scan
    if 0 < s-t0 < LOCK+0.25:
        v = (s-t0)/(LOCK+0.25); yy = y+h*v; c.rectangle(x, yy-2, w, 4); col(c, color, .5*(1-v)); c.fill()
    return s > t0+LOCK*0.6
def appear(c, s, t0, draw, d=0.3):
    u = ease((s-t0)/d)
    if u <= 0: return
    c.push_group(); draw(c); c.pop_group_to_source(); c.paint_with_alpha(u)
def count(s, t0, v0, v1, d=1.0): return lerp(v0, v1, ease((s-t0)/d))
def chip(c, sv, x, y, color, size=34, ink='05070A'):
    w = tw(c, sv, 'xb', size)+40; c.rectangle(x-w/2, y-size*0.8, w, size*1.6); col(c, color); c.fill(); text(c, sv, x, y, 'xb', size, ink)
def hbar(c, x, y, w, frac, color, h=26):
    c.rectangle(x, y, w, h); col(c, 'FFFFFF', .1); c.fill(); c.rectangle(x, y, w*frac, h); col(c, color); c.fill()

def content(c, cid, s):
    st = STATE[cid]; acc = ST[st][0]; t0 = 0.25; L = t0+LOCK
    X, Y, Wd, Hd = 140, 470, 800, 400
    if cid == 'c01':
        appear(c, s, 0.1, lambda k: text(k, "LE PARADOXE", 540, 450, 'k', 96, INK))
        appear(c, s, 0.4, lambda k: text(k, "TESLA", 540, 560, 'k', 150, RED, glow=1))
        if lock_box(c, s, 1.2, 120, 720, 470, 200, CYAN, "VALORISATION"):
            text(c, f"{fmt(count(s, 1.45, 0, 1490, 0.9))} MD$", 355, 820, 'k', 76, INK)
        if lock_box(c, s, 2.4, 640, 860, 330, 150, RED, "BÉNÉFICE 12 MOIS", 'FFFFFF'):
            text(c, f"{count(s, 2.65, 0, 3.8, 0.7):.1f} MD$".replace('.', ','), 805, 935, 'k', 58, INK)
        return
    if cid == 'c17':
        if lock_box(c, s, 0.3, 120, 480, 400, 260, GREEN, "SCÉNARIO A"): text(c, "GÉNIE", 320, 610, 'k', 84, GREEN, glow=1)
        if lock_box(c, s, 1.1, 560, 620, 400, 260, RED, "SCÉNARIO B", 'FFFFFF'): text(c, "BULLE ?", 760, 750, 'k', 84, RED, glow=1)
        return
    if cid in ('c18', 'c19'):
        return
    labels = {'c02': "TON INVESTISSEMENT", 'c03': "LIVRAISONS · T2 2026", 'c04': "LIVRAISONS · T3 2026", 'c05': "CHIFFRE D'AFFAIRES · T2 2026",
              'c06': "MARGE D'EXPLOITATION · T2 2026", 'c07': "RÉSULTAT D'EXPLOITATION · T2", 'c08': "FREE CASH FLOW · T2 2026", 'c09': "BYD VS TESLA · T3 2026",
              'c10': "BÉNÉFICE NET · 12 MOIS", 'c11': "VALORISATION · 13 OCT. 2026", 'c12': "OBSTACLE DÉTECTÉ", 'c13': "ROBOTAXI · ÉTATS-UNIS",
              'c14': "CONDUITE AUTONOME (SUPERVISÉE)", 'c15': "NOUVEAUX PRODUITS", 'c16': "VALEUR ESTIMÉE"}
    ink = 'FFFFFF' if acc == RED else '05070A'
    if cid == 'c16': appear(c, s, 0.05, lambda k: text(k, "TES 1 000 € IL Y A 5 ANS", 540, 395, 'mono', 26, SUB, 'c', 1, 4))
    if not lock_box(c, s, t0, X, Y, Wd, Hd, acc, labels[cid], ink): return
    cx = X+Wd/2
    def big(sv, y=Y+150, size=130, color=INK):
        while tw(c, sv, 'k', size) > Wd-60: size -= 6
        text(c, sv, cx, y, 'k', size, color, glow=1)
    if cid == 'c02':
        text(c, "OCT. 2021", X+180, Y+110, 'mono', 24, SUB); text(c, "1 000 €", X+180, Y+200, 'k', 84, INK)
        text(c, "OCT. 2026", X+Wd-170, Y+110, 'mono', 24, SUB); text(c, "?", X+Wd-170, Y+210, 'k', 140, CYAN, glow=1)
        c.set_line_width(4); col(c, CYAN); c.move_to(X+340, Y+190); c.line_to(X+340+200*ease((s-L)/0.8), Y+190); c.stroke()
        text(c, "réponse à la fin de la vidéo", cx, Y+330, 'mono', 22, SUB)
    elif cid == 'c03':
        big(fmt(round(count(s, L, 0, 480126), -3))); chip(c, "+25 %", cx, Y+260, GREEN, 34)
        text(c, "environ 384 000 un an plus tôt", cx, Y+340, 'mono', 22, SUB)
    elif cid == 'c04':
        big(fmt(round(count(s, L, 0, 486532), -2)))
        x0, w = X+80, Wd-160; hbar(c, x0, Y+270, w, ease((s-L)/1.0)*486532/500000, GREEN)
        xc = x0+w*461974/500000; c.set_dash([8, 6]); c.set_line_width(3); col(c, INK); c.move_to(xc, Y+250); c.line_to(xc, Y+320); c.stroke(); c.set_dash([])
        text(c, "consensus 461 974", xc, Y+350, 'mono', 22, SUB)
    elif cid == 'c05':
        big(f"{count(s, L, 0, 28.24):.1f} MD$".replace('.', ','), Y+140, 120); chip(c, "+26 %", cx, Y+240, GREEN, 32)
        x0, w = X+60, Wd-120; u = ease((s-L-0.3)/1.0); xx = x0
        for v, lab, cc in ((20.52, "AUTO", CYAN), (3.14, "ÉNERGIE", GREEN), (4.58, "SERVICES", AMBER)):
            ww = w*v/28.24*u; c.rectangle(xx, Y+300, ww, 26); col(c, cc); c.fill()
            if u > .9: text(c, lab, xx+ww/2, Y+355, 'mono', 20, cc)
            xx += ww
    elif cid == 'c06':
        big(f"{count(s, L, 0, 1.4):.1f} %".replace('.', ','), Y+140, 140, RED)
        text(c, "1 $ VENDU", X+60, Y+265, 'mono', 22, SUB, 'l'); hbar(c, X+60, Y+285, Wd-120, 1.0, 'FFFFFF', 22)
        text(c, "1,4 CENTIME GARDÉ", X+60, Y+335, 'mono', 22, RED, 'l'); hbar(c, X+60, Y+355, Wd-120, 0.014*ease((s-L)/0.6)+0.004, RED, 22)
    elif cid == 'c07':
        big(f"−{int(count(s, L, 0, 57))} %", Y+130, 140, RED)
        for i, (v, lab) in enumerate(((926, "T2 2025 · ≈ 926 M$"), (398, "T2 2026 · 398 M$"))):
            y = Y+250+i*70; text(c, lab, X+60, y, 'mono', 22, SUB if i == 0 else RED, 'l'); hbar(c, X+60, y+18, Wd-120, v/926*ease((s-L-i*0.2)/0.8), 'FFFFFF' if i == 0 else RED, 20)
    elif cid == 'c08':
        big(f"−{count(s, L, 0, 1.09):.1f} MD$".replace('.', ','), Y+140, 130, RED)
        text(c, "investissements ×2,4 en un an (5,8 Md$)", cx, Y+260, 'm', 30, INK)
        text(c, "+146 M$ un an plus tôt", cx, Y+320, 'mono', 22, SUB)
    elif cid == 'c09':
        big(f"+{fmt(round(count(s, L, 0, 276000), -3))}", Y+140, 130, RED)
        text(c, "véhicules électriques vendus en plus par BYD", cx, Y+260, 'm', 30, INK)
        text(c, "sur le trimestre · selon Electrek", cx, Y+320, 'mono', 22, SUB)
    elif cid == 'c10':
        big(f"{count(s, L, 0, 3.81):.1f} MD$".replace('.', ','), Y+150, 130, INK); chip(c, "−35 %", cx, Y+275, RED, 34, 'FFFFFF')
    elif cid == 'c11':
        big(f"{fmt(count(s, L, 0, 1490))} MD$", Y+150, 120, CYAN); text(c, "capitalisation boursière", cx, Y+270, 'mono', 24, SUB)
    elif cid == 'c12':
        warn(c, cx, Y+90, 80); big("PER ≈ 390", Y+230, 130)
        text(c, "il faudrait ≈ 390 ans de bénéfices actuels pour « rembourser » son prix", cx, Y+340, 'm', 24, SUB)
    elif cid == 'c13':
        big(f"{int(count(s, L, 0, 7, 0.7))} VILLES", Y+140, 130, CYAN)
        for k in range(7):
            x = X+110+k*95; a = clamp((s-L-k*0.12)/0.2); c.arc(x, Y+290, 16, 0, 2*math.pi); col(c, CYAN, a); c.fill()
            c.arc(x, Y+290, 16+14*((s*1.5+k*0.3) % 1), 0, 2*math.pi); c.set_line_width(2); col(c, CYAN, .5*a*(1-((s*1.5+k*0.3) % 1))); c.stroke()
        text(c, "service de robotaxi en place", cx, Y+350, 'mono', 22, SUB)
    elif cid == 'c14':
        big(f"{count(s, L, 0, 1.48):.2f} M".replace('.', ','), Y+150, 130, CYAN); chip(c, "+56 % sur un an", cx, Y+275, GREEN, 30)
    elif cid == 'c15':
        for k, (name, stt, cc) in enumerate((("CYBERCAB", "EN PRODUCTION · TEXAS", GREEN), ("OPTIMUS", "PRÉVU FIN 2026 · FREMONT", AMBER))):
            a = clamp((s-L-k*0.5)/0.3); y = Y+120+k*150
            c.push_group(); text(c, name, X+60, y, 'k', 76, INK, 'l'); tag(c, stt, X+60, y+70, cc, 22); c.pop_group_to_source(); c.paint_with_alpha(a)
    elif cid == 'c16':
        v = count(s, L, 1000, VAL, 1.3); sv = fmt(round(v, -1) if v < VAL-8 else 1445)+" €"
        w1 = tw(c, "≈ ", 'xb', 76); w2 = tw(c, sv, 'k', 150); x0 = cx-(w1+w2)/2
        text(c, "≈", x0, Y+150, 'xb', 76, INK, 'l'); text(c, sv, x0+w1, Y+150, 'k', 150, INK, 'l', glow=1)
        text(c, "sans dividende · change €/$ inclus · avant frais", cx, Y+260, 'mono', 20, SUB)
        if s > L+1.5:
            u = ease((s-L-1.5)/0.3); c.save(); c.translate(cx, Y+330); sc_ = lerp(1.6, 1, u); c.scale(sc_, sc_); c.push_group(); chip(c, "×1,45", 0, 0, GREEN, 40); c.pop_group_to_source(); c.paint_with_alpha(clamp(u*2)); c.restore()

def scene(cid, t):
    a, d = TL[cid]; s = t-a; st = STATE[cid]; acc, lab, spd, tint = ST[st]
    S, c = surface()
    proj = road(c, dist=dist_at(t), tint=tint)
    if cid not in ('c18', 'c19'): trajectory(c, proj, acc, .6, curve=-0.5 if st == 'warn' else (0.4 if st in ('good', 'future') else 0.0))
    else: c.rectangle(0, 0, W, H); col(c, '000000', .55); c.fill()
    progress(c, clamp(t/DUR)); hud(c, t, speed_at(t), label=lab, color=acc)
    content(c, cid, s)
    if cid == 'c18':
        appear(c, s, 0, lambda k: text(k, "Et toi ?", 540, 470, 'k', 170, INK, glow=1))
        for j, (lb, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", CYAN))):
            def btn(k, j=j, lb=lb, cc=cc):
                y = 680+j*150; bracket(k, 250, y, 580, 112, cc, 1, 26, 4); c2 = k
                text(c2, f"{j+1}", 300, y+56, 'mono', 34, cc); text(c2, lb, 560, y+56, 'xb', 54, INK)
            appear(c, s, 0.3+j*0.18, btn)
    if cid == 'c19':
        def hd(k):
            sc_ = lerp(0.8, 1, ease(s/0.5)); k.save(); k.translate(540, 470); k.scale(sc_, sc_); k.translate(-540, -470); logo_symbol(k, 540, 470, 190); k.restore()
            text(k, "Actions_Benefices", 540, 630, 'b', 46, INK)
        appear(c, s, 0, hd)
        for j, lb in enumerate(("Abonne-toi", "Like", "Partage")):
            appear(c, s, 0.35+j*0.25, lambda k, j=j, lb=lb: (bracket(k, 290, 730+j*135, 500, 100, GREEN, 1, 22, 3), text(k, lb, 540, 780+j*135, 'xb', 46, INK)))
    scanlines(c, .04)
    items = parse(CAP[cid]); fo = 1-clamp((s-(d-0.15))/0.15); k = clamp((s-0.2)/0.25)*fo
    if k > 0:
        c.push_group(); caption(c, items, 1352, 46, acc); c.pop_group_to_source(); c.paint_with_alpha(k)
    if cid in ('c11', 'c12', 'c16', 'c17', 'c18'):
        text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1470, 'm', 22, SUB, 'c', .9)
    return to_img(S)
def frame(t):
    cur = cur_scene(t); im = scene(cur, t); i = ORDER.index(cur)
    if i > 0 and t-T(cur) < 0.22: im = Image.blend(scene(ORDER[i-1], t), im, inout((t-T(cur))/0.22))
    if t < 0.3: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, clamp(t/0.3))
    if t > DUR-0.4: im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t-(DUR-0.4))/0.4))
    return im
def events():
    ev = []
    for cid in ORDER:
        a = T(cid); st = STATE[cid]
        if cid != 'c01': ev.append((a, 'pass'))
        if cid in ('c18', 'c19'): continue
        if cid == 'c01': ev += [(a+1.2, 'lock'), (a+1.45, 'impact'), (a+2.4, 'lock'), (a+2.65, 'warn')]; continue
        if cid == 'c17': ev += [(a+0.3, 'lock'), (a+1.1, 'lock'), (a+1.2, 'warn')]; continue
        ev += [(a+0.25, 'lock'), (a+0.25+LOCK, 'impact')]
        if st == 'warn': ev.append((a+0.25+LOCK+0.05, 'warn'))
        if cid in ('c03', 'c04', 'c05', 'c07', 'c09', 'c10', 'c11', 'c14', 'c16'): ev.append((a+0.25+LOCK+0.1, 'tick'))
    ev += [(T('c16')-1.2, 'riser'), (T('c16')+0.6+1.5, 'impact'), (T('c16')+0.6+1.5, 'glint'), (T('c18'), 'impact')]
    return ev
def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 1) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/tsla/prev', exist_ok=True)
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/tsla/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
