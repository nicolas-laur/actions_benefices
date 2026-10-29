"""Carrousel « GAFAM : le bulletin de notes » (résultats du 3e trimestre 2026 : Microsoft, Alphabet, Amazon).
DA de la vidéo PEA/CTO : fond sombre étoilé, panneaux de verre, grands chiffres lumineux ; Mister Coin classique change d'émotion à chaque diapo.
Chaque diapo est dessinée sur une toile 1080×1920 ; le contenu tient dans la bande y = 200…1500 (zone sûre TikTok),
la version Instagram 4:5 (1080×1350) est découpée dans cette même toile (y = 175…1525).
usage : python3 carrousel.py            → diapos 9:16 et 4:5 dans out/
        python3 carrousel.py planche    → planche de contrôle prev/planche.png"""
import sys, os, math, functools
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H
from logo import logo_symbol
from bglass import gpanel, place, glow_text, tilt_quad, surf, pil
NB = ' '
CY = '35D6FF'; CY2 = 'A8EEFF'; GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4D5E'; ICE = 'E8EEF8'; INK = '0B0E14'; WHITE = 'FFFFFF'
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
def fmt(v, d=1): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',').replace(' ', NB)

# ---------- données (sources dans sources.md) ----------
EURUSD = 1.12           # À CONFIRMER : taux de référence BCE du 30/10/2026
def eur(usd_md): return usd_md/EURUSD
# feux : 'v' vert, 'o' orange, 'r' rouge ; res = verdict sur les résultats, bourse = variation du cours le lendemain de l'annonce
DATA = {
    'MSFT': dict(nom="MICROSOFT", ca=92.3, ca_g=19, bn=36.6, bn_g=32, cloud="AZURE", cloud_g=48, capex=39.4, capex_x=2.0,
                 res='v', res_txt="SOLIDES", bourse=None, bfeu=None, pose='pouce', bulle="Le cloud porte tout !"),
    'GOOGL': dict(nom="ALPHABET", ca=127.6, ca_g=25, bn=26.5, bn_g=-24, cloud="GOOGLE CLOUD", cloud_g=103, capex=51.4, capex_x=2.1,
                  res='o', res_txt="MITIGÉS", bourse=None, bfeu=None, pose='choc', bulle="Ça coûte combien ?!"),
    'AMZN': dict(nom="AMAZON", ca=None, ca_g=None, bn=None, bn_g=None, cloud="AWS", cloud_g=None, capex=None, capex_x=None,
                 res=None, res_txt="?", bourse=None, bfeu=None, pose='joie', bulle="…"),
}
FEU = {'v': '3FE08A', 'o': 'FFA63D', 'r': 'FF4D5E'}

# ---------- fond : ciel étoilé + globe en points (rendu de la vidéo PEA/CTO), Amériques face à nous, qui tourne d'une diapo à l'autre ----------
GLOBE = ['0995', '1012', '1030', '1047', '1065', '1082', '1100']; GR_ = 514/600
@functools.lru_cache(maxsize=1)
def sky():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('04060B')); g.add_color_stop_rgb(.55, *rgb('070A12')); g.add_color_stop_rgb(1, *rgb('0B0F18')); c.set_source(g); c.paint()
    rng = np.random.default_rng(2)
    for x, y, r, a in zip(rng.uniform(0, W, 260), rng.uniform(0, H, 260), rng.uniform(.6, 1.7, 260), rng.uniform(.08, .35, 260)):
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a); c.fill()
    return to_img(s)
def background(i, cx=540, cy=1240, size=1560, al=.55):
    cv = sky().copy()
    b = np.asarray(Image.open(f'{D}/globe/b_{GLOBE[i]}.png').convert('RGB'), np.float32); m = np.asarray(Image.open(f'{D}/globe/m_{GLOBE[i]}.png').convert('RGB'), np.float32)[..., :1]/255
    gl = b*(1-.5*m)+m*np.array(rgb(CY))*255*.75                      # terres en points teintées cyan, discrètes
    gl = Image.fromarray(np.clip(gl, 0, 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
    yy, xx = np.mgrid[0:size, 0:size]; r = np.hypot(xx-size/2+.5, yy-size/2+.5)/(size/2); A = np.clip((GR_-r)*size*.5, 0, 1)[..., None]*al
    arr = np.asarray(cv.convert('RGB'), np.float32); x0, y0 = cx-size//2, cy-size//2
    gx0, gy0 = max(0, -x0), max(0, -y0); gx1, gy1 = min(size, W-x0), min(size, H-y0)
    sub = arr[y0+gy0:y0+gy1, x0+gx0:x0+gx1]; G = np.asarray(gl, np.float32)[gy0:gy1, gx0:gx1]; AA = A[gy0:gy1, gx0:gx1]
    sub[:] = sub*(1-AA)+G*AA
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); R1 = size*GR_*.5*1.2; rg = cairo.RadialGradient(cx, cy, 0, cx, cy, R1)           # liseré d'atmosphère
    rg.add_color_stop_rgba(0, *rgb(CY), 0); rg.add_color_stop_rgba(.8, *rgb(CY), 0); rg.add_color_stop_rgba(.835, *rgb(CY), .30*al); rg.add_color_stop_rgba(1, *rgb(CY), 0)
    c.set_source(rg); c.arc(cx, cy, R1, 0, 2*math.pi); c.fill(); out.alpha_composite(to_img(s))
    s, c = surface(); g = cairo.LinearGradient(0, 0, 0, H)                                           # voile en haut : les titres restent sur fond calme
    g.add_color_stop_rgba(0, 0, 0, 0, .0); g.add_color_stop_rgba(.3, 0, 0, 0, .0); g.add_color_stop_rgba(1, 0, 0, 0, .25); c.set_source(g); c.paint(); out.alpha_composite(to_img(s))
    return out
def halos(cv, spots):
    s, c = surface()
    for (x, y, rad, colr, a) in spots:
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *rgb(colr), a); g.add_color_stop_rgba(1, *rgb(colr), 0)
        c.set_source(g); c.arc(x, y, rad, 0, 2*math.pi); c.fill()
    cv.alpha_composite(to_img(s))

# ---------- éléments ----------
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def gpill(c, s, x, y, colr, size=34, fg=INK, a=1):
    w = tw(c, s, 'xb', size, 2)+60; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2); return w
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def put_emoji(cv, ch, x, y, size):
    e = emoji(ch, size); cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
@functools.lru_cache(maxsize=16)
def coin_img(pose, h):
    im = Image.open(f'{D}/coin/{pose}.png').convert('RGBA'); return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
def coin(cv, pose, cx, feet, h=430, flip=False):
    """Mister Coin posé au sol, avec son ombre"""
    im = coin_img(pose, h)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    s, c = surface(); c.save(); c.translate(cx, feet); c.scale(im.width*.42, 18)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .65); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(feet-h+6)))
    return (cx-im.width/2, feet-h, cx+im.width/2, feet)
def bulle(c, s, x, y, tip, size=34):
    """bulle de BD blanche, pointe vers (tip) = la tête de Mister Coin"""
    w = tw(c, s, 'xb', size)+64; h = size*2.1; x0 = x-w/2; y0 = y-h/2
    tx, ty = tip; bx = min(max(tx, x0+50), x0+w-50); by = y0+h if ty > y else y0
    c.move_to(bx-22, by); c.line_to(tx, ty); c.line_to(bx+22, by); c.close_path(); col(c, WHITE); c.fill()
    rr(c, x0, y0, w, h, h/2); col(c, WHITE); c.fill()
    text(c, s, x, y, 'xb', size, INK, 'c')
def logo(cv, c, key, cx, cy, size=96):
    """logo fourni par Nicolas (logos/<KEY>.png) ; tant qu'il manque, un emplacement en pointillés"""
    f = f'{D}/logos/{key}.png'
    if os.path.exists(f):
        im = Image.open(f).convert('RGBA'); im = im.crop(im.getbbox()); k = size/max(im.size); im = im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.LANCZOS)
        cv.alpha_composite(im, (int(cx-im.width/2), int(cy-im.height/2)))
    else:
        c.set_dash([8, 8]); c.arc(cx, cy, size/2, 0, 2*math.pi); c.set_line_width(3); col(c, WHITE, .45); c.stroke(); c.set_dash([])
        text(c, "LOGO", cx, cy, 'xb', 18, WHITE, 'c', .5, 2)
def lampes(k, x, y, etat, r=15, gap=40):
    """trois lampes rouge / orange / vert, seule celle de l'état est allumée (halo)"""
    for j, e in enumerate('rov'):
        xx = x+(j-1)*gap; on = (e == etat)
        if on:
            g = cairo.RadialGradient(xx, y, 0, xx, y, r*3); g.add_color_stop_rgba(0, *rgb(FEU[e]), .55); g.add_color_stop_rgba(1, *rgb(FEU[e]), 0); k.set_source(g); k.arc(xx, y, r*3, 0, 2*math.pi); k.fill()
        k.arc(xx, y, r, 0, 2*math.pi); col(k, FEU[e], 1 if on else .16); k.fill_preserve(); k.set_line_width(2); col(k, WHITE if on else FEU[e], .7 if on else .35); k.stroke()
def feu_panel(titre, etat, valeur, w=410, h=200):
    def dr(k, w, h):
        text(k, titre, w/2, 44, 'xb', 24, ICE, 'c', .85, 3)
        lampes(k, w/2, 98, etat)
        text(k, valeur, w/2, 158, 'a', 50, FEU[etat] if etat else WHITE, 'c')
    return gp(w, h, dr, FEU[etat] if etat else 'CFE8FF')
def kpi_panel(rows, w=860, h=600, tint='CFE8FF', vcol={}):
    """tableau de verre : libellé, valeur en euros, évolution sur un an"""
    def dr(k, w, h):
        n = len(rows); rh = (h-40)/n
        for i, (lab, val, sub, dv, dcol) in enumerate(rows):
            y = 20+rh*i+rh/2
            if i: k.move_to(40, 20+rh*i); k.line_to(w-40, 20+rh*i); k.set_line_width(1.5); col(k, WHITE, .12); k.stroke()
            text(k, lab, 46, y-22, 'xb', 26, ICE, 'l', .8, 2)
            text(k, val, 46, y+24, 'a', 56, vcol.get(i, WHITE), 'l')
            if sub: text(k, sub, 46+tw(k, val, 'a', 56)+18, y+30, 'sb', 24, ICE, 'l', .6)
            if dv:
                pw = tw(k, dv, 'xb', 34)+44; rr(k, w-46-pw, y-30, pw, 60, 30); col(k, dcol, .16); k.fill_preserve(); k.set_line_width(2.5); col(k, dcol, .9); k.stroke()
                text(k, dv, w-46-pw/2, y, 'xb', 34, dcol, 'c')
    return gp(w, h, dr, tint)
def sgn(v, unit=' %'): return ("+" if v > 0 else "−")+fmt(abs(v), 0)+unit.replace(' ', NB)
def pagination(c, i, n=7):
    for k in range(n):
        x = 540+(k-(n-1)/2)*26; c.arc(x, 1470, 6 if k == i else 4.5, 0, 2*math.pi); col(c, WHITE, .95 if k == i else .3); c.fill()

# ---------- diapos ----------
def s1(cv, c):
    """couverture : la question qui accroche + les trois copies"""
    text(c, "RÉSULTATS DU 3E TRIMESTRE 2026", 540, 250, 'sb', 28, ICE, 'c', .8, 4)
    glow_text(cv, "GAFAM", 540, 390, 200, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "RÉSULTATS VS BOURSE", 540, 545, GD, 40)
    text(c, "De bons chiffres = une action qui monte ?", 540, 640, 'xb', 36, WHITE, 'c')
    for i, (k, colr) in enumerate((('MSFT', CY), ('GOOGL', GD), ('AMZN', GR))):
        x = 220+i*320
        def dr(kk, w, h, k=k, colr=colr):
            text(kk, DATA[k]['nom'], w/2, 150, 'xb', 26, colr, 'c', 1, 2)
            lampes(kk, w/2, 210, None, 13, 34)
        place(cv, gp(270, 260, dr), tilt_quad(x, 870, 270, 260, ry=(.18, 0, -.18)[i], rx=.06), 1, 14, .5)
        s_, k_ = surface(); logo(cv, k_, k, x, 800, 80); cv.alpha_composite(to_img(s_))
    coin(cv, 'montre', 330, 1460, 400)
    bulle(c, "Pas toujours…", 700, 1120, (440, 1140), 34)
    text(c, "SWIPE", 880, 1330, 'xb', 30, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 930, 1328, 54)
def entreprise(key, idx):
    def s(cv, c):
        d = DATA[key]; tint = {'MSFT': 'CFE8FF', 'GOOGL': 'FFE9C0', 'AMZN': 'D4FFE6'}[key]
        text(c, "RÉSULTATS · JUILLET À SEPTEMBRE 2026", 540, 240, 'sb', 24, ICE, 'c', .7, 3)
        nw = tw(c, d['nom'], 'a', 112); x0 = 540-(nw+120)/2
        logo(cv, c, key, x0+48, 340, 96); glow_text(cv, d['nom'], x0+120+nw/2, 340, 112, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.4)
        b = d['bourse']
        place(cv, feu_panel("LES RÉSULTATS", d['res'], d['res_txt']), tilt_quad(305, 530, 410, 200, ry=.12, rx=.04), 1, 16, .45)
        place(cv, feu_panel("LA BOURSE", d['bfeu'], sgn(b, ' %').replace('+', '+') if b is not None else "?"), tilt_quad(775, 530, 410, 200, ry=-.12, rx=.04), 1, 16, .45)
        rows = [("CHIFFRE D'AFFAIRES", f"{fmt(eur(d['ca']))} Md€" if d['ca'] else "?", None, sgn(d['ca_g']) if d['ca_g'] is not None else None, GR),
                ("BÉNÉFICE NET", f"{fmt(eur(d['bn']))} Md€" if d['bn'] else "?", None, sgn(d['bn_g']) if d['bn_g'] is not None else None, GR if (d['bn_g'] or 0) > 0 else RD),
                (f"CROISSANCE DU CLOUD ({d['cloud']})", sgn(d['cloud_g']) if d['cloud_g'] is not None else "?", "sur un an", None, GR),
                ("INVESTISSEMENTS DU TRIMESTRE", f"{fmt(eur(d['capex']))} Md€" if d['capex'] else "?", None, (f"×{fmt(d['capex_x'])}".replace(',0', '')) if d['capex_x'] else None, GD)]
        place(cv, kpi_panel(rows, 860, 500, tint, vcol={2: GR}), tilt_quad(540, 905, 860, 500, rx=.05), 1, 18, .5)
        coin(cv, d['pose'], 260, 1480, 330)
        bulle(c, d['bulle'], 680, 1300, (350, 1210), 34)
        pagination(c, idx)
    return s
def s5(cv, c):
    """le cœur du carrousel : résultats vs réaction de la bourse"""
    text(c, "LE MATCH", 540, 250, 'sb', 28, ICE, 'c', .8, 4)
    glow_text(cv, "RÉSULTATS VS BOURSE", 540, 350, 92, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.45)
    keys = ('MSFT', 'GOOGL', 'AMZN')
    def dr(k, w, h):
        text(k, "RÉSULTATS", 470, 50, 'xb', 24, ICE, 'c', .85, 3); text(k, "BOURSE", 730, 50, 'xb', 24, ICE, 'c', .85, 3)
        for j, kk in enumerate(keys):
            d = DATA[kk]; y = 150+j*165
            if j: k.move_to(30, y-82); k.line_to(w-30, y-82); k.set_line_width(1.5); col(k, WHITE, .12); k.stroke()
            text(k, d['nom'], 150, y, 'xb', 30, (CY, GD, GR)[j], 'l', 1, 1)
            lampes(k, 470, y-26, d['res'], 13, 34); text(k, d['res_txt'], 470, y+30, 'a', 40, FEU[d['res']] if d['res'] else WHITE, 'c')
            b = d['bourse']; lampes(k, 730, y-26, d['bfeu'], 13, 34); text(k, sgn(b, ' %') if b is not None else "?", 730, y+30, 'a', 40, FEU[d['bfeu']] if d['bfeu'] else WHITE, 'c')
    place(cv, gp(880, 560, dr), tilt_quad(540, 760, 880, 560, rx=.05), 1, 18, .5)
    for j, kk in enumerate(keys):
        s_, k_ = surface(); logo(cv, k_, kk, 165, 760-280+150+j*165, 64); cv.alpha_composite(to_img(s_))
    coin(cv, 'question', 300, 1460, 360)
    bulle(c, "Pas le même verdict !", 710, 1250, (420, 1170), 34)
    pagination(c, 4)
def s6(cv, c):
    """la leçon : le cloud explose, les dépenses aussi"""
    halos(cv, [(540, 620, 620, RD, .08), (540, 900, 520, GD, .07)])
    text(c, "CE QU'IL FAUT RETENIR", 540, 250, 'sb', 28, ICE, 'c', .8, 4)
    tot = sum(eur(DATA[k]['capex']) for k in DATA if DATA[k]['capex'])
    glow_text(cv, f"{fmt(tot, 0)} Md€", 540, 420, 160, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "INVESTIS EN UN SEUL TRIMESTRE", 540, 545, 'xb', 36, WHITE, 'c', 1, 3)
    text(c, "surtout des data centers et des puces pour l'IA", 540, 600, 'sb', 30, ICE, 'c', .75)
    def dr(k, w, h):
        text(k, "La bourse ne récompense pas", w/2, 90, 'xb', 38, WHITE, 'c')
        text(k, "la croissance à n'importe quel prix.", w/2, 145, 'xb', 38, WHITE, 'c')
        text(k, "Elle regarde ce que l'IA coûte", w/2, 235, 'sb', 34, GD2, 'c')
        text(k, "et quand elle rapportera.", w/2, 285, 'sb', 34, GD2, 'c')
    place(cv, gp(840, 370, dr, 'FFE9C0'), tilt_quad(520, 860, 840, 370, rx=.05), 1, 18, .5)
    coin(cv, 'inquiet', 330, 1460, 400)
    bulle(c, "L'addition est salée…", 700, 1230, (420, 1130), 32)
    pagination(c, 5)
def s7(cv, c):
    """question finale (pas de blague), logo"""
    halos(cv, [(540, 600, 640, CY, .10), (540, 900, 500, GD, .08)])
    glow_text(cv, "ET TOI,", 540, 340, 130, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5)
    glow_text(cv, "LEQUEL", 540, 500, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "TU GARDES ?", 540, 650, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 790, 'sb', 34, ICE, 'c', .85); put_emoji(cv, '👇', 540, 860, 60)
    coin(cv, 'question', 540, 1330, 380)
    c.push_group(); logo_symbol(c, 395, 1405, 40); c.pop_group_to_source(); c.paint()
    text(c, "Actions_Benefices", 428, 1405, 'b', 28, WHITE, 'l')
    text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 1475, 'sb', 20, ICE, 'c', .55)
SLIDES = [s1, entreprise('MSFT', 1), entreprise('GOOGL', 2), entreprise('AMZN', 3), s5, s6, s7]

def render(i):
    cv = background(i); s, c = surface()
    # couche texte (cairo) posée après les panneaux : on dessine d'abord les panneaux (PIL) dans la fonction, puis le texte cairo
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__':
    os.makedirs(f'{D}/out', exist_ok=True); os.makedirs(f'{D}/prev', exist_ok=True)
    ims = [render(i) for i in range(len(SLIDES))]
    for i, im in enumerate(ims):
        im.save(f'{D}/out/tiktok_{i+1}.png'); im.crop((0, 175, W, 1525)).save(f'{D}/out/instagram_{i+1}.png')
    if 'planche' in sys.argv:
        th = [im.resize((360, 640)) for im in ims]; P = Image.new('RGB', (360*len(th), 640)); [P.paste(t, (k*360, 0)) for k, t in enumerate(th)]; P.save(f'{D}/prev/planche.png')
    print('ok')
