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
DATA = {
    'MSFT': dict(nom="MICROSOFT", trimestre="JUILLET À SEPTEMBRE 2026", ca=92.3, ca_g=19, bn=36.6, bn_g=32, cloud="AZURE", cloud_g=48, capex=39.4, capex_x=2.0,
                 bourse=None, note='A', ncol=GR, pose='pouce', bulle="Le cloud porte tout !"),
    'GOOGL': dict(nom="ALPHABET", trimestre="JUILLET À SEPTEMBRE 2026", ca=127.6, ca_g=25, bn=26.5, bn_g=-24, cloud="GOOGLE CLOUD", cloud_g=103, capex=51.4, capex_x=2.1,
                  bourse=None, note='C', ncol=RD, pose='choc', bulle="Ça coûte combien ?!"),
    'AMZN': dict(nom="AMAZON", trimestre="JUILLET À SEPTEMBRE 2026", ca=None, ca_g=None, bn=None, bn_g=None, cloud="AWS", cloud_g=None, capex=None, capex_x=None,
                 bourse=None, note='?', ncol=GD, pose='joie', bulle="…"),
}

# ---------- fond ----------
@functools.lru_cache(maxsize=1)
def background():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('04060B')); g.add_color_stop_rgb(.55, *rgb('070A12')); g.add_color_stop_rgb(1, *rgb('0B0F18')); c.set_source(g); c.paint()
    rng = np.random.default_rng(2)
    for x, y, r, a in zip(rng.uniform(0, W, 260), rng.uniform(0, H, 260), rng.uniform(.6, 1.7, 260), rng.uniform(.08, .35, 260)):
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a); c.fill()
    return to_img(s)
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
def note_badge(cv, lettre, colr, cx, cy, r=96):
    """pastille de note façon bulletin : disque de verre teinté, lettre lumineuse"""
    def d(k, w, h):
        k.arc(w/2, h/2, r-3, 0, 2*math.pi); g = cairo.RadialGradient(w/2, h*.35, 0, w/2, h/2, r); g.add_color_stop_rgba(0, *rgb(colr), .35); g.add_color_stop_rgba(1, *rgb(colr), .08)
        k.set_source(g); k.fill_preserve(); k.set_line_width(5); col(k, colr, .95); k.stroke()
    s, k = surf(2*r, 2*r); d(k, 2*r, 2*r); cv.alpha_composite(pil(s), (int(cx-r), int(cy-r)))
    glow_text(cv, lettre, cx, cy+4, int(r*1.25), top='FFFFFF', bottom=colr, glow=colr, ga=.8, reflect=False)
def entete(cv, c, d):
    text(c, "RÉSULTATS · " + d['trimestre'], 90, 250, 'sb', 26, ICE, 'l', .75, 3)
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
    """couverture : le chiffre choc + les trois copies à noter"""
    halos(cv, [(300, 520, 520, GD, .10), (820, 1100, 560, CY, .10)])
    text(c, "RÉSULTATS DU 3E TRIMESTRE 2026", 540, 250, 'sb', 28, ICE, 'c', .8, 4)
    glow_text(cv, "GAFAM", 540, 400, 210, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "LE BULLETIN DE NOTES", 540, 560, GD, 40)
    for i, (k, colr) in enumerate((('MSFT', CY), ('GOOGL', GD), ('AMZN', GR))):
        x = 220+i*320
        def dr(kk, w, h, k=k, colr=colr):
            text(kk, DATA[k]['nom'], w/2, 52, 'xb', 26, colr, 'c', 1, 2)
            text(kk, "?", w/2, 170, 'a', 120, WHITE, 'c', .9)
        place(cv, gp(270, 270, dr), tilt_quad(x, 790, 270, 270, ry=(.18, 0, -.18)[i], rx=.06), 1, 14, .5)
    coin(cv, 'montre', 360, 1440, 440)
    bulle(c, "Qui a eu la meilleure note ?", 720, 1080, (470, 1110), 32)
    text(c, "SWIPE", 880, 1300, 'xb', 30, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 930, 1298, 54)
def entreprise(key, idx):
    def s(cv, c):
        d = DATA[key]; tint = {'MSFT': 'CFE8FF', 'GOOGL': 'FFE9C0', 'AMZN': 'D4FFE6'}[key]
        halos(cv, [(820, 420, 520, d['ncol'], .12), (260, 1200, 520, CY, .08)])
        text(c, "RÉSULTATS · JUILLET À SEPTEMBRE 2026", 90, 245, 'sb', 24, ICE, 'l', .7, 3)
        glow_text(cv, d['nom'], 90+tw(c, d['nom'], 'a', 120)/2, 340, 120, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.4)
        note_badge(cv, d['note'], d['ncol'], 900, 320, 92)
        b = d['bourse']
        rows = [("CHIFFRE D'AFFAIRES", f"{fmt(eur(d['ca']))} Md€" if d['ca'] else "?", None, sgn(d['ca_g']) if d['ca_g'] is not None else None, GR),
                ("BÉNÉFICE NET", f"{fmt(eur(d['bn']))} Md€" if d['bn'] else "?", None, sgn(d['bn_g']) if d['bn_g'] is not None else None, GR if (d['bn_g'] or 0) > 0 else RD),
                (f"CROISSANCE DU CLOUD ({d['cloud']})", sgn(d['cloud_g']) if d['cloud_g'] is not None else "?", "sur un an", None, GR),
                ("INVESTISSEMENTS DU TRIMESTRE", f"{fmt(eur(d['capex']))} Md€" if d['capex'] else "?", None, (f"×{fmt(d['capex_x'])}".replace(',0', '')) if d['capex_x'] else None, GD),
                ("BOURSE LE LENDEMAIN", sgn(b, ' %') if b is not None else "?", None, None, GR)]
        place(cv, kpi_panel(rows, 860, 700, tint, vcol={2: GR, 4: (GR if (b or 0) > 0 else RD) if b is not None else WHITE}), tilt_quad(520, 770, 860, 700, ry=0, rx=.05), 1, 18, .5)
        coin(cv, d['pose'], 270, 1480, 360)
        bulle(c, d['bulle'], 680, 1300, (370, 1200), 34)
        pagination(c, idx)
    return s
def s5(cv, c):
    """comparatif"""
    halos(cv, [(540, 700, 640, CY, .09)])
    text(c, "LE COMPARATIF", 540, 250, 'sb', 28, ICE, 'c', .8, 4)
    glow_text(cv, "QUI FAIT QUOI ?", 540, 350, 104, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.45)
    keys = ('MSFT', 'GOOGL', 'AMZN'); colw = 190; x0 = 300
    def dr(k, w, h):
        for j, kk in enumerate(keys):
            text(k, DATA[kk]['nom'], x0+colw*j+colw/2, 60, 'xb', 26, (CY, GD, GR)[j], 'c', 1, 1)
        lab = ["CHIFFRE D'AFF.", "CROISSANCE", "CLOUD", "INVESTIS.", "BOURSE"]
        for i, l in enumerate(lab):
            y = 150+i*100
            k.move_to(30, y-50); k.line_to(w-30, y-50); k.set_line_width(1.5); col(k, WHITE, .12); k.stroke()
            text(k, l, 40, y, 'xb', 26, ICE, 'l', .85, 1)
            for j, kk in enumerate(keys):
                d = DATA[kk]
                v = [f"{fmt(eur(d['ca']), 0)} Md€" if d['ca'] else "?", sgn(d['ca_g']) if d['ca_g'] is not None else "?", sgn(d['cloud_g']) if d['cloud_g'] is not None else "?",
                     f"{fmt(eur(d['capex']), 0)} Md€" if d['capex'] else "?", sgn(d['bourse']) if d['bourse'] is not None else "?"][i]
                cc = WHITE if i in (0, 3) else (GR if not v.startswith('−') else RD)
                if v == "?": cc = ICE
                text(k, v, x0+colw*j+colw/2, y, 'a', 46, cc, 'c')
    place(cv, gp(880, 640, dr), tilt_quad(520, 800, 880, 640, rx=.05), 1, 18, .5)
    coin(cv, 'question', 300, 1460, 380)
    bulle(c, "Pas le même bulletin !", 720, 1260, (430, 1200), 32)
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
    cv = background().copy(); s, c = surface()
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
