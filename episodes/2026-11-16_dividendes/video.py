"""Vidéo « Combien investir pour toucher 2 000 € par mois de dividendes ? » (v1, ~96 s).
Scène de one man show (poursuite qui suit Mister Coin), argent Blender qui tombe au fond (flou) et parterre qui se constitue,
panneaux de verre épais animés, piles de pièces qui se forment pièce par pièce, courbes qui se dessinent.
usage : python3 video.py info | png t1 t2 … | seg out.mp4 f0 f1"""
import os, sys, math, functools, subprocess
import numpy as np, cv2, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import scenes as S
from scenes import text, surface, to_img, rr, col, tw, W, H, glow_text, tilt_quad, tplace, gpill, put_emoji, logo, caption, clamp, ease, rgb
from scenes import GD, GD2, GR, RD, OR, CY, ICE, INK, WHITE, CAP, BRUT, NB
from veo_coin import VeoCoin
FPS = 60; VOICE = f'{D}/voice_full.wav'; DUR = 96.6; S.DUR = DUR
def inout(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u

# ---------- parterre : 10 étapes Blender, fondu doux de l'une à l'autre ----------
@functools.lru_cache(maxsize=None)
def heap_stage(k):
    im = Image.open(f'{S.ASSETS}/heap_{k:02d}.png').convert('RGBA'); a = np.asarray(im).astype(np.float32); a[..., :3] *= .84
    prof = np.argmax(a[..., 3] > 120, axis=0).astype(np.float32); prof[(a[..., 3] > 120).sum(0) == 0] = im.height
    return a, prof
HY = H-400                                                                 # le bas du tas rendu passe sous le cadre
def heap(cv, t):
    s = 1+9*clamp((t-1)/(DUR-6))**.9; k0 = int(math.floor(s)); k1 = min(10, k0+1); u = inout(s-k0)
    a0, p0 = heap_stage(k0); a1, p1 = heap_stage(k1); a = a0*(1-u)+a1*u
    cv.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (0, HY))
    return HY+(p0*(1-u)+p1*u)
def money(cv, t):
    lay = Image.new('RGBA', (W, H), 0); prof = None
    for p in S._drops():
        dt = t-p['t0']
        if dt < 0: continue
        x, y, ang = S.fall(p, dt)
        if y > H-120: continue
        size = {'c': 80, 'b': 150, 's': 110}[p['kind']]*p['sz']
        fr = int(9+4*math.sin(p['w']*dt+p['rot'])) if p['kind'] == 'b' else int((dt*20+p['rot']*6)*(1 if p['spin'] > 0 else -1))
        im = S.sprite(p['kind'], fr, int(size))
        if ang: im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
        lay.alpha_composite(im, (int(x-im.width/2), int(y-im.height/2)))
    arr = cv2.GaussianBlur(np.asarray(lay), (0, 0), 2.6).astype(np.float32); arr[..., :3] *= .78
    cv.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))
    heap(cv, t)

# ---------- calage : plages de parole de la voix (timing.py) ----------
C = [(0.04, 3.16), (3.60, 7.82), (8.26, 11.60), (11.96, 13.96), (14.40, 17.54), (18.06, 23.26), (23.76, 26.98), (27.52, 28.64), (29.22, 30.04), (30.40, 33.02),
     (33.54, 36.88), (37.50, 40.02), (40.48, 44.02), (44.56, 46.36), (47.08, 49.84), (50.20, 51.44), (52.06, 53.26), (53.74, 59.64), (60.20, 62.66), (63.06, 63.72),
     (64.12, 66.14), (66.50, 69.28), (70.08, 70.74), (71.04, 73.86), (74.32, 77.72), (78.24, 81.34), (82.06, 82.74), (83.08, 90.08), (90.46, 92.56), (93.08, 94.18)]
CAPS_SRC = [(0, "Combien il te faut pour toucher [2 000 € par mois] sans travailler ?", GD), (1, "Pour te situer : le [SMIC], c'est environ 1 480 € nets par mois.", CY),
    (2, "Et le [salaire médian] dans le privé, celui qui coupe les salariés en deux moitiés,", GD), (3, "est de [2 190 € nets].", GD),
    (4, "Sur un an, 2 000 € par mois, ça fait [24 000 €].", GD), (5, "Mais même dans un PEA de plus de cinq ans, l'État prélève [18,6 %] de prélèvements sociaux.", RD),
    (6, "Il te faut donc près de [30 000 €] de dividendes avant prélèvements.", GD), (7, "Combien de capital pour ça ?", GD), (8, "Tout dépend du [rendement] :", GD),
    (9, "c'est ce qu'une action te verse chaque année, rapporté à son prix.", GD), (10, "À [3 %], 100 € placés te rapportent [3 €] par an.", GD),
    (11, "Un ETF monde ne verse qu'[1,5 %] :", GD), (12, "les géants de la tech préfèrent réinvestir leurs bénéfices plutôt que de les distribuer.", GD),
    (13, "Il te faudrait près de [2 millions d'euros].", GD), (14, "Un ETF à dividendes élevés verse environ [3 %] :", GD), (15, "il te faut près d'[un million].", GD),
    (16, "Et les actions à [gros dividendes] ?", GD), (17, "Crédit Agricole, BNP Paribas, Engie, AXA ou Orange versent entre [5 et 7,5 %].", GR),
    (18, "À [5 %], il te faut environ [600 000 €].", GD), (19, "Mais attention :", RD), (20, "un dividende peut être [coupé du jour au lendemain].", RD),
    (21, "[Stellantis] n'a plus rien versé depuis avril 2025.", RD), (22, "Autre piège :", OR), (23, "le PEA est plafonné à [150 000 €] de versements.", GD),
    (24, "Au-delà, c'est le compte-titres, taxé à [31,4 %].", OR), (25, "Il te faudrait alors près d'[1,2 million] à 3 %.", OR), (26, "La [bonne nouvelle] :", GR),
    (27, "en remplissant ton PEA avec [1 000 € par mois] pendant 12 ans et demi, puis en le laissant grossir à 7 % par an, ce qui n'est jamais garanti,", GR),
    (28, "tu atteins le [million] en [33 ans] environ.", GR), (29, "Et toi, tu en es où ?", GD)]
def _split(txt, a, b, maxc=56):
    """phrase trop longue → morceaux de ≤ 2 lignes, durée au prorata des caractères"""
    words = txt.split(' '); parts = []; cur = ''
    for w in words:
        if len((cur+' '+w).replace('[', '').replace(']', '')) > maxc and cur and cur.count('[') == cur.count(']'): parts.append(cur); cur = w
        else: cur = (cur+' '+w).strip()
    parts.append(cur); L = [len(p) for p in parts]; tot = sum(L); out = []; t = a
    for p, l in zip(parts, L): d = (b-a)*l/tot; out.append((t, t+d, p)); t += d
    return out
CAPS = []
for i, txt, hl in CAPS_SRC:
    a, b = C[i]
    for (x0, x1, p) in _split(txt, a, b): CAPS.append((x0, x1, p, hl))
def cap_layer(c, t):
    for k, (a, b, s_, hl) in enumerate(CAPS):
        nxt = CAPS[k+1][0] if k+1 < len(CAPS) else DUR
        end = min(nxt, b+.45)
        if a-.05 <= t < end:
            al = ease((t-a+.05)/.12)*(1-ease((t-(end-.12))/.12) if end-b > .1 or k+1 >= len(CAPS) else 1)
            caption(c, s_, hl=hl, a=al); return

# ---------- Mister Coin : clips de danse, il parle quand la voix parle ----------
SW, CO, BI, PR, JO = 'classique_danse_parle_swing', 'classique_danse_parle_compte', 'classique_danse_parle_billets', 'classique_danse_parle_prudent', 'classique_danse_joie_silence'
FEET = 1660
MC = VeoCoin([(0.0, SW, 'voix'), (3.4, CO, 'voix'), (27.2, BI, 'voix'), (51.8, PR, 'voix'), (70.0, CO, 'voix'), (82.0, BI, 'voix'), (92.6, JO, 'une'), (94.6, SW, 'voix')],
             voix=VOICE, duree=DUR, x=540, pieds=FEET, largeur_piece=200, lisse=True)
# scènes : (début, fin, fonction, position de Mister Coin)
def scene_list():
    return [(0.0, 3.4, sc_hook, 540), (3.4, 14.2, sc_reperes, 430), (14.2, 27.2, sc_impot, 650), (27.2, 37.2, sc_rendement, 540), (37.2, 51.8, sc_piles, 540),
            (51.8, 60.0, sc_actions, 420), (60.0, 70.0, sc_piles2, 540), (70.0, 82.0, sc_plafond, 640), (82.0, 92.8, sc_courbe, 540), (92.8, DUR, sc_fin, 540)]
def coin_x(t):
    L = scene_list(); i = max(j for j, sc in enumerate(L) if t >= sc[0] or j == 0)
    prev = L[i-1][3] if i > 0 else L[0][3]
    return lerp(prev, L[i][3], inout((t-L[i][0])/.9))
def coin_layer(cv, t, X):
    Y = FEET+MC.hop_dy(t); rgb_, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx = MC.feet_x(al, Y)
    if fx is not None:
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (95, 15), 0, 0, 360, .55, -1); a *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    a = a*(1-al[..., None])+rgb_*al[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')

# ---------- outils d'animation ----------
def ent(k, d=.45): return ease(k/d)                    # entrée d'un panneau
def tilt(k): return .05+.25*(1-ent(k))
def count_to(v, u): return v*ease(u)
def title(c, s_, k, y=240):
    text(c, s_, 540, y, 'sb', 30, GD2, 'c', .85*ent(k, .35), 6)
def tp(cv, w, h, draw, cx, cy, mood, k, ry=0.0, bev=30):
    S.tp(cv, w, h, draw, cx, cy+40*(1-ent(k)), mood, rx=tilt(k), ry=ry, bev=bev)
# pile de pièces qui se forme pièce par pièce (les pièces tombent du haut et se posent)
@functools.lru_cache(maxsize=4)
def stack_scaled(w):
    st = S.stack_img(); k = w/st.width; full = st.resize((w, int(st.height*k)), Image.LANCZOS)
    a = np.asarray(full)[..., 3] > 100; rows = np.where(a.any(1))[0]; face = int(w*.30)
    pitch = (full.height-face)/95
    return full, face, pitch
def pile_anim(cv, c, cx, base, n_target, t, t0, t1, tint=None, crack=0.0, w=170):
    full, face, pitch = stack_scaled(w)
    u = clamp((t-t0)/(t1-t0)); n = int(round(n_target*(u**1.15)))
    if t >= t1: n = n_target
    if n <= 0: return base, 0
    hh = int(face+n*pitch); im = full.crop((0, 0, w, min(full.height, hh)))
    if tint is not None:
        a = np.asarray(im).astype(np.float32); a[..., :3] *= np.array(tint, np.float32); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    s2, k = surface(); k.save(); k.translate(cx, base); k.scale(w*.7, 18); g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .7); g.add_color_stop_rgba(1, 0, 0, 0, 0); k.set_source(g); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    cv.alpha_composite(to_img(s2)); top = base-im.height; cv.alpha_composite(im, (int(cx-w/2), int(top)))
    if t0 < t < t1:                                                          # la pièce suivante tombe sur la pile
        dt_c = (t1-t0)/max(1, n_target); ph = ((t-t0) % dt_c)/dt_c
        coin_im = full.crop((0, 0, w, int(face+pitch*1.2)))
        if tint is not None:
            a = np.asarray(coin_im).astype(np.float32); a[..., :3] *= np.array(tint, np.float32); coin_im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        y = top-pitch-260*(1-ph)**2
        cv.alpha_composite(coin_im, (int(cx-w/2), int(y)))
    if crack > 0:
        s3, kk = surface(); y = top+face*.5; kk.move_to(cx+6, y); pts = [(cx-14, y+50), (cx+18, y+110), (cx-8, y+180), (cx+14, y+260)]
        for (x2, y2) in pts[:max(1, int(len(pts)*crack))]: kk.line_to(x2, min(y2, base-12))
        kk.set_line_width(5); kk.set_source_rgba(.06, .02, 0, .95); kk.stroke_preserve(); kk.set_line_width(1.5); kk.set_source_rgba(1, .8, .4, .5); kk.stroke(); cv.alpha_composite(to_img(s3))
    return top, n
N_COINS = {r_: int(round(400*CAP[r_]/CAP[1.5]/stack_scaled(170)[2])) for r_ in CAP}
def euro(v):
    if v >= 1e6: return f"{v/1e6:.2f}".replace('.', ',')+" M€"
    return f"{int(round(v, -3)):,}".replace(',', NB)+" €"

# ================= scènes animées (k = temps depuis le début de la scène) =================
def sc_hook(cv, c, t, k):
    text(c, "LES DIVIDENDES", 540, 250, 'sb', 30, GD2, 'c', .85*ent(k, .3), 8)
    u = ent(k, .5); glow_text(cv, "2 000 €", 540, 430+30*(1-u), 230, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.75, a=u)
    u2 = ent(k-.5, .4); glow_text(cv, "PAR MOIS", 540, 600, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.5, reflect=False, a=u2)
    if k > 1.4: gpill(c, "SANS TRAVAILLER ?", 540, 745, GD, 44, a=ent(k-1.4, .3))
    if k > 2.0: put_emoji(cv, '🤔', 800, 250, int(70*ent(k-2.0, .3))+1)
def sc_reperes(cv, c, t, k):
    title(c, "POUR TE SITUER", k)
    def d(kk, w, h):
        x0, x1 = 70, w-70; lo, hi = 1000, 2600; X = lambda v: x0+(v-lo)/(hi-lo)*(x1-x0); y = 300
        g = cairo.LinearGradient(x0, 0, x1, 0); g.add_color_stop_rgb(0, *rgb('3A6B8C')); g.add_color_stop_rgb(1, *rgb('FFC24A'))
        rr(kk, x0, y-9, (x1-x0)*ent(k, .6), 18, 9); kk.set_source(g); kk.fill()
        for v in range(1000, 2601, 250):
            kk.move_to(X(v), y+16); kk.line_to(X(v), y+30); kk.set_line_width(2); col(kk, WHITE, .4*ent(k, .6)); kk.stroke()
        marks = [(SMIC_T, S.SMIC, "SMIC", "1 478 €", CY, True), (MED_T, S.MEDIAN, "SALAIRE MÉDIAN", "2 190 €", WHITE, True), (OBJ_T, S.NET_MOIS, "TON OBJECTIF", "2 000 €", GD, False)]
        for (t0, v, lab, sub, colr, up) in marks:
            a = ent(t-t0, .35)
            if a <= 0: continue
            x = X(v); kk.arc(x, y, (17 if colr == GD else 12)*a, 0, 2*math.pi); col(kk, colr); kk.fill()
            yy = y-150 if up else y+120
            kk.move_to(x, y+(-20 if up else 20)); kk.line_to(x, lerp(y, yy+(48 if up else -48), a)); kk.set_line_width(2.5); col(kk, colr, .8); kk.stroke()
            text(kk, lab, x, yy-24, 'xb', 26, colr, 'c', a, 2); text(kk, sub, x, yy+20, 'a', 52, colr, 'c', a)
        text(kk, "net par mois, temps plein (SMIC au 1er juin 2026, médian du privé 2024)", w/2, h-36, 'sb', 21, ICE, 'c', .7*ent(k, .6))
    tp(cv, 920, 560, d, 540, 640, 'or', k)
SMIC_T, MED_T, OBJ_T = 4.6, 12.0, 12.9
def sc_impot(cv, c, t, k):
    title(c, "DANS UN PEA DE PLUS DE 5 ANS", k)
    def d(kk, w, h):
        a1 = ent(t-14.4, .4); text(kk, "2 000 € × 12 MOIS", w/2, 52, 'xb', 30, ICE, 'c', .9*a1, 2)
        text(kk, f"{int(count_to(24000, (t-15.6)/1.2)):,} € / an".replace(',', NB), w/2, 120, 'a', 74, GD, 'c', a1)
        x0, x1, y = 70, w-70, 260; xn = x0+(x1-x0)*S.NET_AN/BRUT
        g1 = ent(t-16.6, .5); rr(kk, x0, y-40, (xn-x0)*g1, 80, 18); col(kk, GD); kk.fill()
        if g1 > .6: text(kk, "CE QUE TU TOUCHES", (x0+xn)/2, y, 'xb', 24, INK, 'c', ent(g1-.6, .3), 2)
        g2 = ent(t-20.9, .45)
        if g2 > 0:
            rr(kk, xn+6, y-40, (x1-xn-6)*g2, 80, 18); col(kk, RD); kk.fill(); text(kk, "18,6 %", (xn+x1)/2+3, y, 'xb', 28, WHITE, 'c', g2); text(kk, "prélèvements sociaux", (xn+x1)/2+3, y+66, 'sb', 22, RD, 'c', g2)
        g3 = ent(t-24.4, .4)
        if g3 > 0:
            text(kk, "IL TE FAUT", w/2, 370, 'xb', 26, ICE, 'c', .85*g3, 3)
            text(kk, f"{int(count_to(BRUT, (t-24.5)/1.4)):,} €".replace(',', NB), w/2, 440, 'a', 90, WHITE, 'c', g3); text(kk, "de dividendes par an", w/2, 510, 'sb', 26, ICE, 'c', .8*g3)
    tp(cv, 900, 560, d, 540, 640, 'orange', k, ry=.04)
def sc_rendement(cv, c, t, k):
    title(c, "LE RENDEMENT", k)
    def d(kk, w, h):
        a1 = ent(t-29.3, .4); text(kk, "ce qu'une action te verse chaque année,", w/2, 56, 'sb', 30, ICE, 'c', .9*a1); text(kk, "rapporté à son prix", w/2, 100, 'sb', 30, ICE, 'c', .9*a1)
        a2 = ent(t-33.6, .35); text(kk, "100 €", 200, 270, 'a', 110, WHITE, 'c', a2); text(kk, "placés", 200, 350, 'sb', 28, ICE, 'c', .8*a2)
        a3 = ent(t-34.6, .45)
        if a3 > 0:
            xe = lerp(350, 540, a3); kk.move_to(350, 270); kk.line_to(xe, 270); kk.set_line_width(6); col(kk, GD); kk.stroke(); kk.move_to(xe, 270); kk.line_to(xe-25, 252); kk.line_to(xe-25, 288); kk.close_path(); kk.fill()
            text(kk, "3 %", 445, 236, 'xb', 34, GD, 'c', a3)
        a4 = ent(t-35.6, .35); text(kk, "3 €", 680, 270, 'a', 110, GD, 'c', a4); text(kk, "chaque année", 680, 350, 'sb', 28, GD2, 'c', .9*a4)
    tp(cv, 900, 430, d, 540, 600, 'or', k)
PILES = [(220, 1.5, "ETF MONDE", None, WHITE, 37.6, 44.6), (540, 3, "ETF DIVIDENDES", None, GD, 47.1, 51.4), (860, 5, "ACTIONS À GROS DIVIDENDES", (1.0, .78, .6), OR, 60.3, 62.7)]
def _piles(cv, c, t, k, show3, crack=0.0):
    title(c, "POUR 2 000 € NETS PAR MOIS", k); base = 930
    for i, (x, r_, lab, tint, vc, t0, t1) in enumerate(PILES):
        if i == 2 and not show3: continue
        if t < t0-.4:
            continue
        al = ent(t-(t0-.4), .3)
        top, n = pile_anim(cv, c, x, base, N_COINS[r_], t, t0, t1, tint, crack if i == 2 else 0)
        v = CAP[r_]*min(1, n/N_COINS[r_])
        text(c, euro(v) if v >= 1e6 else f"{int(round(v, -3)):,} €".replace(',', NB), x, min(top, base-20)-60, 'a', 60 if r_ == 1.5 else 54, vc, 'c', al)
        text(c, f"{str(r_).replace('.', ',')} %", x, min(top, base-20)-120, 'xb', 32, ICE, 'c', .9*al)
        text(c, lab, x, base+50, 'xb', 22 if r_ != 5 else 19, ICE, 'c', .85*al, 1)
def sc_piles(cv, c, t, k): _piles(cv, c, t, k, False)
def sc_piles2(cv, c, t, k):
    _piles(cv, c, t, 9, True, crack=ent(t-64.6, 1.0))
    a = ent(t-66.6, .4)
    if a > 0:
        def d(kk, w, h):
            text(kk, "STELLANTIS", 110, 40, 'xb', 28, WHITE, 'l', 1, 1); text(kk, "plus rien depuis avril 2025", 110, 78, 'sb', 22, ICE, 'l', .85); text(kk, "0 €", w-40, 58, 'a', 52, RD, 'r')
        S.tp(cv, 520, 116, d, 760, 330+30*(1-a), 'rouge', rx=.05, ry=-.08, bev=22); logo(cv, 'STLA', 760-260+12+50, 330+30*(1-a), 56, cross=True)
ACT = [('CA', "CRÉDIT AGRICOLE", "7,5 %", 53.8), ('BNP', "BNP PARIBAS", "6,0 %", 55.0), ('ENGIE', "ENGIE", "5,8 %", 55.9), ('AXA', "AXA", "5,4 %", 56.6), ('ORANGE', "ORANGE", "5,2 %", 57.3)]
def sc_actions(cv, c, t, k):
    title(c, "LES GROS DIVIDENDES DU CAC 40", k)
    def d(kk, w, h):
        for i, (key, nom, r_, t0) in enumerate(ACT):
            a = ent(t-t0, .3); y = 60+i*96
            if i: kk.move_to(40, y-48); kk.line_to(w-40, y-48); kk.set_line_width(1.2); col(kk, WHITE, .12); kk.stroke()
            text(kk, nom, 150+30*(1-a), y, 'xb', 30, WHITE, 'l', a, 1); text(kk, r_, w-60, y, 'a', 52, GR, 'r', ent(t-58.2-i*.12, .3))
        text(kk, "rendement sur le dividende 2025, cours au 1er novembre 2026", w/2, h-28, 'sb', 20, ICE, 'c', .65*ent(k, .5))
    tp(cv, 860, 560, d, 540, 600, 'orange', k, ry=-.04)
    for i, (key, _, _, t0) in enumerate(ACT):
        a = ent(t-t0, .3)
        if a > 0: logo(cv, key, 540-430+20+80, 600+40*(1-ent(k))-280+20+60+i*96, int(60*a)+1)
def sc_plafond(cv, c, t, k):
    title(c, "LE PIÈGE DU PLAFOND", k)
    def d(kk, w, h):
        x0, x1, y0, y1 = 110, w-50, h-150, 80; T = 27; V = 340000; X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/V
        for v in (100000, 200000, 300000):
            kk.move_to(x0, Y(v)); kk.line_to(x1, Y(v)); kk.set_line_width(1); col(kk, WHITE, .1); kk.stroke(); text(kk, f"{v//1000} k€", x0-14, Y(v), 'sb', 20, ICE, 'r', .6)
        for yr in (0, 10, 20): text(kk, f"{yr} ans", X(yr), y0+30, 'sb', 20, ICE, 'c', .6)
        xc = X(12.5); u1 = inout((t-71.2)/2.4)                               # versements jusqu'au plafond
        if u1 > 0:
            kk.move_to(X(0), Y(0)); kk.line_to(X(12.5*u1), Y(150000*u1)); kk.set_line_width(6); col(kk, GD); kk.stroke()
            text(kk, "versements de 1 000 €/mois", X(9), Y(40000), 'sb', 21, ICE, 'c', .75*ent(u1-.3, .3))
        if t > 73.7: kk.arc(xc, Y(150000), 11, 0, 2*math.pi); col(kk, WHITE); kk.fill(); text(kk, "PLAFOND DU PEA : 150 000 €", X(19.5), Y(150000)+34, 'xb', 24, GD, 'c', ent(t-73.7, .3), 1)
        u2 = inout((t-74.4)/3.0)
        if u2 > 0:
            xe = 12.5+(T-12.5)*u2
            kk.move_to(xc, Y(150000)); kk.line_to(X(xe), Y(1000*12*xe)); kk.line_to(X(xe), Y(150000)); kk.close_path(); col(kk, OR, .28); kk.fill()
            kk.move_to(xc, Y(150000)); kk.line_to(X(xe), Y(150000)); kk.set_line_width(6); col(kk, GD); kk.stroke()
            kk.move_to(xc, Y(150000)); kk.line_to(X(xe), Y(1000*12*xe)); kk.set_dash([10, 8]); kk.set_line_width(4); col(kk, OR); kk.stroke(); kk.set_dash([])
            text(kk, "COMPTE-TITRES", X(21), Y(220000), 'xb', 24, OR, 'c', ent(u2-.4, .3), 1); text(kk, "31,4 % de flat tax", X(21), Y(220000)+32, 'sb', 22, OR, 'c', .9*ent(u2-.4, .3))
        a3 = ent(t-78.4, .4)
        if a3 > 0:
            rr(kk, 60, h-104, w-120, 76, 22); col(kk, OR, .14*a3); kk.fill()
            text(kk, "Tout en compte-titres, à 3 % :", w/2-110, h-66, 'sb', 26, WHITE, 'c', a3); text(kk, euro(count_to(S.CTO3, (t-78.5)/1.5)), w/2+200, h-66, 'a', 46, OR, 'c', a3)
    tp(cv, 920, 640, d, 540, 620, 'orange', k, ry=-.04)
    if t > 73.7: put_emoji(cv, '🔒', 540-460+20+110+(920-160)*12.5/27, 620-320+20+80+(640-230)*(1-150000/340000)-72, int(46*ent(t-73.7, .25))+1)
def sc_courbe(cv, c, t, k):
    title(c, "LA BONNE NOUVELLE", k)
    def d(kk, w, h):
        x0, x1, y0, y1 = 110, w-50, h-90, 70; T = 34; V = 1100000; X = lambda yr: x0+(x1-x0)*yr/T; Y = lambda v: y0-(y0-y1)*v/V
        for v in (250000, 500000, 750000, 1000000):
            kk.move_to(x0, Y(v)); kk.line_to(x1, Y(v)); kk.set_line_width(1); col(kk, WHITE, .1); kk.stroke(); text(kk, f"{v//1000} k€" if v < 1e6 else "1 M€", x0-14, Y(v), 'sb', 20, ICE, 'r', .6)
        for yr in (0, 10, 20, 30): text(kk, f"{yr} ans", X(yr), y0+30, 'sb', 20, ICE, 'c', .6)
        u = inout((t-83.2)/8.2); Mmax = int(T*12*u)
        r = .07/12; pts = []; pv = []; val = 0
        for m in range(0, Mmax+1):
            if m > 0: val = val*(1+r)+(1000 if m <= 150 else 0)
            pts.append((X(m/12), Y(val))); pv.append((X(m/12), Y(min(150000, 1000*m))))
        if len(pts) > 1:
            kk.move_to(*pv[0]); [kk.line_to(*p) for p in pv]; kk.set_line_width(4); col(kk, CY, .9); kk.stroke()
            kk.move_to(*pts[0]); [kk.line_to(*p) for p in pts]; kk.line_to(pts[-1][0], y0); kk.line_to(x0, y0); kk.close_path()
            g = cairo.LinearGradient(0, y1, 0, y0); g.add_color_stop_rgba(0, 1, .76, .29, .45); g.add_color_stop_rgba(1, 1, .76, .29, 0); kk.set_source(g); kk.fill()
            kk.move_to(*pts[0]); [kk.line_to(*p) for p in pts]; kk.set_line_width(6); col(kk, GD); kk.stroke()
            kk.arc(*pts[-1], 9, 0, 2*math.pi); col(kk, WHITE); kk.fill()
            text(kk, euro(val) if val < 1e6 else euro(val), pts[-1][0]-14, pts[-1][1]-36, 'a', 40, GD, 'r', ent(u*10, .3))
        a1 = ent(t-84.0, .4); text(kk, "1 000 €/mois pendant 12 ans et demi, puis plus rien", X(17), Y(150000)-30, 'sb', 22, CY, 'c', a1)
        if t > 86.0: text(kk, "150 000 € versés", X(28), Y(150000)+30, 'xb', 22, CY, 'c', ent(t-86, .3))
        if t > 91.4: text(kk, "en 33 ans", X(32.8)-14, Y(982800)+8, 'sb', 24, GD2, 'r', ent(t-91.4, .3))
        text(kk, "hypothèse : 7 % par an, jamais garanti", w/2, h-34, 'sb', 21, ICE, 'c', .75*ent(k, .5))
    tp(cv, 920, 620, d, 540, 620, 'vert', k)
def sc_fin(cv, c, t, k):
    glow_text(cv, "ET TOI,", 540, 420, 140, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=ent(k, .4))
    glow_text(cv, "TU EN ES OÙ ?", 540, 590, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=ent(k-.3, .4))
    if k > .9: text(c, "Dis-le en commentaire", 540, 740, 'sb', 36, ICE, 'c', .85*ent(k-.9, .3)); put_emoji(cv, '👇', 540, 810+8*math.sin(k*5), 56)

# ---------- image complète ----------
FADE = .35
def frame(t):
    X = coin_x(t)
    cv = S.stage().copy(); money(cv, t); S.spotlight(cv, X, FEET)
    for (a, b, f, cx) in scene_list():
        if a-FADE <= t < b+FADE:
            al = ent(t-a, FADE)*(1-ent(t-b, FADE)) if a > 0 else 1-ent(t-b, FADE)
            if al <= .01: continue
            lay = cv.copy(); s, c = surface(); f(lay, c, t, max(0.0, t-a)); lay.alpha_composite(to_img(s))
            cv = Image.blend(cv, lay, al) if al < .999 else lay
    cv = coin_layer(cv, t, X)
    s, c = surface(); cap_layer(c, t); cv.alpha_composite(to_img(s))
    return cv
def events():
    ev = [(a, 'swish') for (a, b, f, cx) in scene_list()[1:]]
    ev += [(.6, 'impact'), (1.4, 'pop'), (SMIC_T, 'pop'), (MED_T, 'pop'), (OBJ_T, 'glint'), (15.6, 'tick'), (20.9, 'thud'), (24.5, 'tick'), (25.9, 'glint'), (33.6, 'pop'), (35.6, 'coin')]
    for (x, r_, lab, tint, vc, t0, t1) in PILES:                              # chaque pièce qui se pose : petit tintement (une sur trois)
        n = N_COINS[r_]
        for i in range(0, n, 3): ev.append((t0+(t1-t0)*((i+1)/n)**(1/1.15), 'coin'))
        ev.append((t1+.05, 'glint'))
    ev += [(t0, 'pop') for (_, _, _, t0) in ACT] + [(64.6, 'shatter'), (66.6, 'thud'), (73.7, 'clack'), (74.4, 'whoosh'), (78.5, 'tick'), (83.2, 'riser'), (91.4, 'paid'), (93.0, 'hop'), (94.9, 'impact')]
    ev += [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)]
    return sorted(ev)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/f_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
