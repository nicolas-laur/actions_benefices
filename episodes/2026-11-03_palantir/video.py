"""Palantir (3/11/2026) : vidéo finale calée sur la voix de Thomas. DA « dossier classifié » (voir notes_da.md), Mister Coin classique.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, subprocess, functools
import numpy as np, cairo, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from dossier import *
ROOT = os.path.abspath(f'{D}/../..'); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from logo import logo_symbol

# ---------- minutage estimé (≈ 27,5 s) ----------
VOICE = f'{D}/voice_full.wav'
S = dict(eye=0.0, thiel=5.14, cia=7.53, data=9.98, ia=19.86, duel=24.09, money=28.98, multi=34.56, end=39.78, fin=42.6)
T = dict(b=2.03, cofondee=6.0, otan=11.66, foundry=14.46, aip=17.13, res2=20.70, comm=25.46, vingt=32.18, genie=38.22, etoi=40.11)
CARD_T = (S['data'], T['foundry'], T['aip'])
LINE_T = ((11.66, 12.55, 13.35), (15.3, 15.7, 16.1), (17.95, 18.45, 18.95))      # bandeaux qui se retirent au rythme de la voix
DUR = S['fin']
CAPS = [(0.0, "Cette entreprise ne te [connaît] pas…"), (T['b'], "mais elle aide les États à [tout savoir] de toi."),
        (S['thiel'], "[Palantir], cofondée par [Peter Thiel],"), (S['cia'], "et financée à ses débuts par [la CIA]."),
        (S['data'], "[Gotham], pour les armées :"), (T['otan'], "l'OTAN, l'armée américaine, [l'Ukraine]."),
        (T['foundry'], "[Foundry], pour les entreprises et les États."), (T['aip'], "Et [AIP], son intelligence artificielle."),
        (S['ia'], "Résultat :"), (T['res2'], "hier soir, son chiffre d'affaires a presque [doublé] en un an."),
        (S['duel'], "Et pour la [première fois],"), (T['comm'], "les entreprises américaines lui rapportent plus que [l'État américain]."),
        (S['money'], "1 000 € placés le jour de son entrée en bourse, en 2020,"), (T['vingt'], "valent aujourd'hui environ [20 000 €]."),
        (S['multi'], "Mais l'action vaut plus de [50 fois] son chiffre d'affaires annuel."), (T['genie'], "[Génie] ou [bulle] ?"),
        (S['end'], "Et toi, tu achèterais Palantir [à ce prix-là] ?")]
LAB = ("ACTIONS_BÉNÉFICES / DOSSIER PLTR", "REC  03.11.2026", "CONFIDENTIEL · NIVEAU 3", "TC ")

# ---------- l'œil (vidéo Gemini) ----------
EYE_SC, EPX, EPY = 1.9, 540, 700
@functools.lru_cache(maxsize=1)
def eye_frames():
    cap = cv2.VideoCapture(f'{D}/decors/oeil.mp4'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(f)
    return F
def eye(t, zoom=1.0):
    F = eye_frames(); f = F[min(len(F)-1, int(t*24))]
    sc = EYE_SC*zoom; f = cv2.resize(f, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    px, py = 180/360*f.shape[1], 316/640*f.shape[0]; x0, y0 = int(px-EPX), int(py-EPY)
    f = f[y0:y0+H, x0:x0+W]
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32); c = f.astype(np.float32)*.35+g[..., None]*.65
    c = np.clip((c-128)*1.25+118, 0, 255); bl = cv2.GaussianBlur(c, (0, 0), 2); c = np.clip(c*1.6-bl*.6, 0, 255)
    v = np.hypot(*np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))); c *= np.clip(1.15-.55*v, 0, 1)[..., None]
    return c[..., ::-1]

# ---------- scènes : chacune dessine sur le contexte cairo (fond compris) ----------
def sc_eye(c, t):
    k = t-S['eye']
    target(c, EPX, EPY, ease(k/1.6), 'dark', coords=("SUJET 0001", "ANALYSE…"))
    for y in range(0, H, 6): c.rectangle(0, y, W, 2); col(c, '000000', .10); c.fill()
    y = (k*700) % (H+200); g = cairo.LinearGradient(0, y-140, 0, y); g.add_color_stop_rgba(0, *rgb(RED), 0); g.add_color_stop_rgba(1, *rgb(RED), .28)
    c.set_source(g); c.rectangle(0, y-140, W, 140); c.fill()
    if k > 3.0: text(c, "TOUT SAVOIR", 540, 420, 'black', 118, WHITE, ease((k-3.0)/.2), 'c')
    if k > 3.9: text(c, "de toi.", 540, 520, 'serif', 96, RED, ease((k-3.9)/.2), 'c')
def sc_thiel(c, t):
    k = t-S['thiel']; background(c, 'paper', t)
    x0, w = text(c, scramble("PALANTIR", ease(k/1.0), 7), 540, 560, 'black', 180, INK)
    dims(c, x0, 470, x0+w, 650, ease((k-.9)/.8), ("PLTR · NYSE", "FONDÉE EN 2003"))
    if k > .85: text(c, "cofondée par", 540, 720, 'serif', 80, RED, ease((k-1.2)/.2))
    if k > 1.2:
        for i, wd in enumerate(("PETER", "THIEL")):
            kk = k-1.25-i*.22
            if kk > 0: text(c, wd, 540, 830+i*110, 'black', 110, INK, ease(kk/.15))
    dot(c, 540, 1080, 16*back(clamp((k-2.4)/.3)), glow=False)
def sc_cia(c, t):
    k = t-S['cia']; background(c, 'dark', t)
    dot(c, 540, 540, 18); target(c, 540, 540, ease(k/1.0), 'dark', coords=("38.95 N", "77.15 W"))
    if k > .5: text(c, "LANGLEY, VIRGINIE", 540, 330, 'mono', 26, WHITE, .7*ease((k-.5)/.3), 'c', .12)
    if k > .9: text(c, "financée à ses débuts par", 540, 770, 'serif', 70, RED, ease((k-.9)/.2))
    if k > 1.3:
        sc = lerp(1.35, 1, back((k-1.3)/.35)); c.save(); c.translate(540, 880); c.scale(sc, sc)
        text(c, "LA CIA", 0, 0, 'black', 170, WHITE, ease((k-1.3)/.12)); c.restore()
CARDS = [("01", "GOTHAM", "pour les armées et le renseignement", ["OTAN · SYSTÈME D'IA MAVEN (2025)", "US ARMY · JUSQU'À 10 MD$ SUR 10 ANS", "UKRAINE · DÉMINAGE, DÉFENSE AÉRIENNE"]),
         ("02", "FOUNDRY", "pour les entreprises et les États", ["AIRBUS · DONNÉES DE SES AVIONS", "NHS · 330 M£ SUR 7 ANS (2023)", "ICE · SUIVI DES MIGRANTS (ÉTATS-UNIS)"]),
         ("03", "AIP", "son intelligence artificielle (2023)", ["L'IA BRANCHÉE SUR LES DONNÉES DU CLIENT", "DES « BOOTCAMPS » DE 5 JOURS", "LE MOTEUR DE SA CROISSANCE"])]
def card(c, i, k, t):
    """fiche produit en papier qui glisse sur la pile ; les lignes noircies se dévoilent l'une après l'autre"""
    num, name, sub, lines = CARDS[i]
    u = ease(k/.35); x = lerp(1500, 540+(i-1)*14, u); y = 650+(i-1)*12; ang = lerp(.25, (-.04, .03, -.015)[i], u)
    c.save(); c.translate(x, y); c.rotate(ang)
    for j in range(6): rr_(c, -405+j*.5, -285+8+j, 810, 570, 10); col(c, '000000', .05); c.fill()
    rr_(c, -405, -285, 810, 570, 10); col(c, PAPER); c.fill()
    text(c, f"FICHE PRODUIT {num} / 03", -360, -240, 'mono', 22, INK, .7, 'l', .08)
    text(c, "PALANTIR TECHNOLOGIES", 360, -240, 'mono', 22, INK, .7, 'r', .08)
    c.move_to(-360, -215); c.line_to(360, -215); c.set_line_width(1.5); col(c, INK, .3); c.stroke()
    text(c, name, -360, -140, 'black', 120, INK, 1, 'l')
    text(c, sub, -360, -40, 'serif', 52, RED, ease((k-.25)/.2), 'l')
    for j, ln in enumerate(lines):
        yy = 40+j*68; kk = t-LINE_T[i][j]
        tw_ = tw(c, ln, 'monob', 26, .03)
        text(c, ln, -360, yy, 'monob', 26, INK, 1 if kk > 0 else 0, 'l', .03)
        cover = 1-ease(kk/.25) if kk > 0 else 1.0                      # bandeau noir qui se retire de gauche à droite
        if cover > 0: c.rectangle(-360+tw_*(1-cover), yy-20, tw_*cover+8, 40); col(c, INK); c.fill()
    if t > LINE_T[i][2]+.45:                                           # tampon rouge
        k = t-LINE_T[i][2]-.45+.9
        sc_ = lerp(1.6, 1, back((k-.9)/.25)); c.save(); c.translate(255, 238); c.rotate(-.12); c.scale(sc_*.85, sc_*.85)
        rr_(c, -130, -42, 260, 84, 8); c.set_line_width(5); col(c, RED, .85*ease((k-.9)/.1)); c.stroke()
        text(c, "CLASSIFIÉ", 0, 0, 'monob', 34, RED, .85*ease((k-.9)/.1), 'c', .12); c.restore()
    c.restore()
def sc_data(c, t):
    background(c, 'dark', t)
    def field(i, j, tt): return .5+.5*math.sin(i*.7+j*.5-tt*3)
    dot_grid(c, t, ease((t-S['data'])/.9)*.35, 'dark', cy=700, rows_=8, field=field)
    for i, t0 in enumerate(CARD_T):
        if t >= t0: card(c, i, t-t0, t)
def sc_ia(c, t):
    k = t-S['ia']; background(c, 'dark', t)
    def field(i, j, tt): return .5+.5*math.sin(i*.7+j*.5-tt*3)
    k2 = t-T['res2']
    dot_grid(c, t, 1.0, 'dark', cy=700, rows_=8, field=field, red_k=ease(k2/.8), square_k=ease((k2-.3)/.9), rot=max(0, k2)*1.6)
    text(c, "RÉSULTATS · 3E TRIMESTRE 2026", 540, 300, 'mono', 26, WHITE, .8*ease(k/.3), 'c', .1)
    if k2 > 0:
        sc = lerp(1.6, 1, back(k2/.35)); c.save(); c.translate(540, 620); c.scale(sc, sc)
        rr_(c, -340, -120, 680, 240, 18); col(c, INK, .92*ease(k2/.15)); c.fill()
        text(c, "+96 %", 0, -6, 'black', 190, WHITE, ease(k2/.12)); c.restore()
        rr_(c, 170, 790, 740, 110, 16); col(c, INK, .92*ease((k2-.5)/.2)); c.fill()
        text(c, "de chiffre d'affaires en un an", 540, 842, 'serif', 64, RED, ease((k2-.5)/.2))
def sc_duel(c, t):
    """les entreprises américaines dépassent l'État américain : deux barres en course, sur papier"""
    k = t-S['duel']; background(c, 'paper', t)
    text(c, scramble("POUR LA PREMIÈRE FOIS", ease(k/.9), 5), 540, 300, 'black', 64, INK, ease(k/.2))
    text(c, "chiffre d'affaires du trimestre aux États-Unis", 540, 380, 'serif', 46, RED, ease((k-.3)/.25))
    kb = t-T['comm']
    rows = (("ENTREPRISES", 984, RED), ("ÉTAT", 953, INK))
    for j, (lab, v, colr) in enumerate(rows):
        y = 520+j*170; u = ease(clamp(kb/1.6)) if kb > 0 else 0
        val = v*u; wmax = 600
        text(c, lab, 160, y-50, 'monob', 28, INK, .85*ease((k-.5)/.3), 'l', .08)
        rr_(c, 160, y-22, wmax, 64, 10); col(c, INK, .08*ease((k-.5)/.3)); c.fill()
        if val > 0: rr_(c, 160, y-22, max(20, wmax*val/1000), 64, 10); col(c, colr, .95); c.fill()
        text(c, f"{int(round(val))} M$", 160+max(20, wmax*val/1000)+18, y+10, 'black', 46, colr, ease((k-.5)/.3) if kb > 0 else 0, 'l')
    if kb > 1.7:
        sc_ = lerp(1.6, 1, back((kb-1.7)/.25)); c.save(); c.translate(760, 880); c.rotate(-.12); c.scale(sc_, sc_)
        rr_(c, -150, -42, 300, 84, 8); c.set_line_width(5); col(c, RED, .9*ease((kb-1.7)/.1)); c.stroke()
        text(c, "+148 % EN 1 AN", 0, 0, 'monob', 30, RED, .9*ease((kb-1.7)/.1), 'c', .06); c.restore()
def sc_money(c, t):
    k = t-S['money']; background(c, 'dark', t)
    text(c, "1 000 € PLACÉS LE 30/09/2020", 540, 330, 'mono', 28, WHITE, .75*ease(k/.3), 'c', .1)
    flap_board(c, "1000€", 540, 470, 118, 168, clamp(k/1.2))
    kv = t-T['vingt']+.05
    if kv > -.4:
        text(c, "↓", 540, 588, 'black', 70, RED, ease((kv+.4)/.2))
        text(c, "AUJOURD'HUI", 540, 640, 'mono', 28, WHITE, .75*ease((kv+.4)/.3), 'c', .1)
    kv = t-T['vingt']+.05
    if kv > 0:
        flap_board(c, "19800€", 540, 800, 128, 182, clamp(kv/1.5), red_last=True)
        text(c, "≈", 100, 800, 'black', 90, RED, ease(kv/.3))
    if kv > 1.6:
        x0 = 540-6*(128+8)/2; x1 = x0+6*(128+8)
        dims(c, x0, 709, x1, 891, ease((kv-1.6)/.7), ("", "CLÔTURE DU 2/11"))
        text(c, "×20 EN 6 ANS · HORS DIVIDENDES", 540, 935, 'monob', 28, RED, ease((kv-1.8)/.3), 'c', .08)
def sc_multi(c, t):
    k = t-S['multi']; background(c, 'dark', t)
    kg = t-T['genie']+2.2
    word_rows(c, ["GÉNIE", "BULLE"], t, ease((kg-2.2)/.4), size=150, cy=760)
    a = 1-ease((kg-2.2)/.3)
    if a > 0:
        sc = lerp(1.4, 1, back(k/.4)); c.save(); c.translate(540, 600); c.scale(sc, sc)
        x0, w = text(c, "50×", 0, 0, 'black', 260, WHITE, a*ease(k/.12)); c.restore()
        if k > .5: text(c, "son chiffre d'affaires", 540, 800, 'serif', 78, RED, a*ease((k-.5)/.2))
        if k > .8: dims(c, 540-w/2, 490, 540+w/2, 710, ease((k-.8)/.6)*a, ("≈ 450 MD$ EN BOURSE", "CA 2026 PRÉVU"))
    if kg > 2.4:
        rr_(c, 290, 700, 500, 130, 14); col(c, INK, .92*ease((kg-2.4)/.2)); c.fill()
        text(c, "GÉNIE OU BULLE ?", 540, 765, 'black', 58, WHITE, ease((kg-2.4)/.2))
def sc_res(c, t):
    k = t-S['res']; background(c, 'paper', t)
    text(c, "RÉSULTATS · 2 NOVEMBRE 2026", 540, 330, 'mono', 28, INK, .75*ease(k/.3), 'c', .1)
    text(c, scramble("CHIFFRE D'AFFAIRES", ease(k/.8), 3), 540, 470, 'black', 70, INK, ease(k/.2))
    text(c, "+ XX %", 540, 620, 'black', 200, '9A958C', ease((k-.4)/.2))
    text(c, "chiffres de ce soir", 540, 780, 'serif', 70, RED, ease((k-.7)/.2))
    dot(c, 540, 900, 14, glow=False)
def sc_end(c, t):
    k = t-S['end']; background(c, 'dark', t)
    text(c, "Et toi,", 540, 360, 'serif', 110, RED, ease(k/.2))
    for i, wd in enumerate(("TU ACHÈTERAIS", "PALANTIR", "À CE PRIX-LÀ ?")):
        kk = k-.35-i*.3
        if kk > 0:
            sc = lerp(1.3, 1, back(kk/.3)); c.save(); c.translate(540, 490+i*125); c.scale(sc, sc)
            text(c, wd, 0, 0, 'black', 104 if i != 1 else 130, WHITE if i != 1 else RED, ease(kk/.12)); c.restore()
    if k > 1.6:
        a = ease((k-1.6)/.4); c.push_group(); logo_symbol(c, 395, 880, 44); c.pop_group_to_source(); c.paint_with_alpha(a)
        text(c, "Actions_Benefices", 430, 880, 'xb', 30, WHITE, a, 'l')
        text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 945, 'mono', 19, WHITE, .5*a, 'c')
ORDER = [('eye', sc_eye), ('thiel', sc_thiel), ('cia', sc_cia), ('data', sc_data), ('ia', sc_ia), ('duel', sc_duel), ('money', sc_money), ('multi', sc_multi), ('end', sc_end)]
KEYS = list(S)
def scene_at(t):
    cur = ORDER[0]
    for nm, fn in ORDER:
        if t >= S[nm]: cur = (nm, fn)
    return cur
# ---------- Mister Coin ----------
from veo_coin import VeoCoin
from nty import finish
INQ, EXP, ENT, CONF, QUES = 'classique_parle_inquiet', 'classique_parle_explique', 'classique_parle_enthousiaste', 'classique_parle_confidence', 'classique_parle_question'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, INQ, 'voix'), (9.8, EXP, 'voix'), (19.7, ENT, 'voix'), (34.4, CONF, 'voix'), (39.6, QUES, 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def caption(c, t, mode):
    """sous-titres : phrase en cours, mot clé [entre crochets] surligné en rouge"""
    k = None
    for i, (t0, _) in enumerate(CAPS):
        if t >= t0: k = i
    if k is None or t > DUR-.35: return
    raw = CAPS[k][1]; size = 42
    toks = []; inb = False; cur = ''
    for ch in raw:
        if ch == '[': inb = True; continue
        if ch == ']': inb = False; continue
        if ch == ' ' and not inb: toks.append(cur); cur = ''; continue
        cur += ('\u00a0' if ch == ' ' else ch)
    toks.append(cur)
    hl = []; inb = False; idx = 0; word = ''
    for w_ in raw.replace('] ', ']\x00').split(' '): pass
    marks = set(); pos = 0
    for part in __import__('re').finditer(r'\[([^\]]+)\]', raw): marks.add(part.group(1).replace(' ', '\u00a0'))
    words = [(w_.replace('\u00a0', ' '), any(m in w_ for m in marks)) for w_ in toks]
    sp = tw(c, ' ', 'xb', size); wd = [tw(c, w_, 'xb', size)+(18 if h else 0) for w_, h in words]
    lines, cur_, cw = [], [], 0
    for i, w_ in enumerate(wd):
        need = w_+(sp if cur_ else 0)
        if cur_ and cw+need > 760: lines.append((cur_, cw)); cur_, cw = [], 0; need = w_
        cur_.append(i); cw += need
    lines.append((cur_, cw)); y0 = 1060-(len(lines)-1)*32
    al = ease((t-CAPS[k][0])/.1)
    bw = max(l for _, l in lines)+56; bh = len(lines)*64+28
    rr_(c, 540-bw/2, y0-46, bw, bh, 16); col(c, INK if mode == 'dark' else 'FFFFFF', .82*al); c.fill()
    fg = WHITE if mode == 'dark' else INK
    for li, (ids, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*64
        for i in ids:
            w_, h = words[i]
            if h:
                rr_(c, x, yy-31, wd[i], 60, 10); col(c, RED, al); c.fill(); text(c, w_, x+9, yy, 'xb', size, WHITE, al, 'l')
            else: text(c, w_, x, yy, 'xb', size, fg, al, 'l')
            x += wd[i]+sp
def frame(t):
    nm, fn = scene_at(t); mode = 'paper' if nm in ('thiel', 'duel') else 'dark'
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    if nm == 'eye':
        zoom = 1+3.5*ease((t-(S['thiel']-.4))/.4)**2 if t > S['thiel']-.4 else 1+.02*t
        base = eye(t, zoom)
    else: base = None
    fn(c, t)
    hud(c, t, mode, LAB)
    if nm == 'eye' and t > S['thiel']-.25:
        r = 30+1600*ease((t-(S['thiel']-.25))/.25)**2; c.arc(EPX, EPY, r, 0, 2*math.pi); col(c, RED, 1); c.fill()
    s.flush(); ov = np.asarray(Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)).astype(np.float32)
    if base is not None: a = ov[..., 3:]/255; out = base*(1-a)+ov[..., :3]*a
    else: out = ov[..., :3]
    for k in KEYS[1:-1]:
        if 0 <= t-S[k] < 1/24: out = out*.65+255*.35                        # coupe franche + éclair d'une image, comme la référence
    # Mister Coin (au-dessus du décor, sous les sous-titres)
    X, Y = CX_COIN, FEET+MC.hop_dy(t); rgb_, al = MC.layer(t, X, Y)
    fx = MC.feet_x(al, Y) if Y > FEET-30 else X
    if fx is not None:
        kk = 1/(1+max(0, FEET-Y)/150); m = np.zeros((H, W), np.float32)
        cv2.ellipse(m, (int(fx), FEET-3), (int(100*kk)+1, int(15*kk)+1), 0, 0, 360, .5*kk, -1); out *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    out = out*(1-al[..., None])+rgb_*al[..., None]
    s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c2 = cairo.Context(s2); caption(c2, t, mode); s2.flush()
    ov2 = np.asarray(Image.frombuffer('RGBA', (W, H), bytes(s2.get_data()), 'raw', 'BGRa', s2.get_stride(), 1)).astype(np.float32)
    a2 = ov2[..., 3:]/255; out = out*(1-a2)+ov2[..., :3]*a2
    return Image.fromarray(grain_layer(out, t, 7).astype(np.uint8))
def events():
    ev = [(0.0, 'impact'), (S['thiel']-.25, 'whoosh'), (S['thiel'], 'impact'), (S['cia'], 'thud'), (S['cia']+1.3, 'impact'),
          (S['data'], 'swish'), (T['foundry'], 'swish'), (T['aip'], 'swish'), (S['ia'], 'swish'), (T['res2'], 'impact'), (S['duel'], 'swish'),
          (T['comm']+1.6, 'glint'), (T['comm']+1.7, 'thud'), (S['money'], 'swish'), (T['vingt']+1.5, 'impact'), (T['vingt']+1.55, 'coins'),
          (S['multi'], 'impact'), (T['genie'], 'whoosh'), (S['end'], 'swish')]
    ev += [(LINE_T[i][j], 'key') for i in range(3) for j in range(3)]
    ev += [(LINE_T[i][2]+.45, 'thud') for i in range(3)]
    ev += [(S['money']+x*.06, 'flap') for x in range(0, 20)] + [(T['vingt']+x*.06, 'flap') for x in range(0, 25)]
    ev += [(S['thiel']+x*.08, 'tick1') for x in range(12)] + [(S['duel']+x*.08, 'tick1') for x in range(11)]
    ev += [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]: frame(float(ts)).save(f'{D}/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); FPS = int(os.environ.get('FPS', 60))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done')
if __name__ == '__main__': main()
