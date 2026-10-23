"""Alphabet : « L'IA devait le tuer ». Barre de recherche, curseur souris, cartes de résultats. 2D net, 60 i/s."""
import sys, math, re, subprocess, os, random
import cairo
from PIL import Image
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/googl')
from gty import *
FPS = 60

# ---------- chiffres vérifiés (12 octobre 2026) ----------
P0, FX0, P1, FX1 = 136.45, 1.1569, 351.66, 1.1177
DIVS = [.20]*4+[.21]*4+[.22]*2
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*sum(DIVS)/FX1; TOT = VAL+DIV
assert round(TOT, -1) == 2680 and round(VAL) == 2668 and round(DIV) == 16
assert round(119.8/1.24, 1) == 96.6 and round(24.8/1.82, 1) == 13.6 and round(63.3/119.8*100) == 53
assert round(514/(24.8*4), 1) == 5.2

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x): x = clamp(x); s = 1.6; return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')
NB = ' '

# (id, sous-titre, requête tapée, couleur d'accent)
SC = [
 ("c01", "En 2023, l'IA devait [tuer] Google.", "google est-il fini face à chatgpt", RED),
 ("c02", "ChatGPT cartonne. Chez Google, c'est le [code rouge].", "google code rouge chatgpt", RED),
 ("c03", "Février 2023 : sa première IA se trompe en pleine démo. ≈ [100 milliards $] partent en fumée.", "démo ia google erreur bourse", RED),
 ("c04", "Et 1 000 € investis il y a 5 ans ? Réponse à la [fin].", "1000 € dans alphabet en 2021", YELLOW),
 ("c05", "Trois ans plus tard : [119,8 milliards $] de ventes en 3 mois.", "résultats alphabet avril-juin 2026", BLUE),
 ("c06", "La recherche ? Pas morte du tout : [+17 %] sur un an.", "revenus recherche google 2026", BLUE),
 ("c07", "Le cloud explose : [+82 %], et 514 milliards $ de contrats déjà signés.", "croissance google cloud 2026", GREEN),
 ("c09", "Son IA Gemini : [950 millions] d'utilisateurs par mois.", "utilisateurs gemini par mois", BLUE),
 ("c10", "Résultat : Alphabet vaut ≈ [4 300 milliards $] en Bourse.", "valeur en bourse alphabet", YELLOW),
 ("c12", "Mais pour rester devant, il prévoit jusqu'à [205 milliards $] d'investissements en 2026.", "investissements alphabet 2026", RED),
 ("c13", "Au dernier trimestre, son cash-flow libre passe [dans le rouge].", "free cash flow alphabet t2 2026", RED),
 ("c14", "Et son bénéfice record ? Gonflé par [98 milliards $] de gains sur le papier.", "bénéfice alphabet t2 2026", YELLOW),
 ("c15", "En justice : ni Chrome ni sa régie pub [vendus de force]. Bruxelles enquête encore.", "procès antitrust google verdict", GREEN),
 ("c17", "Tes 1 000 € il y a 5 ans ? ≈ [2 680 €]. ×2,68.", "1000 € dans alphabet il y a 5 ans", YELLOW),
 ("c18", "L'IA devait le tuer… et si elle l'avait [rendu plus fort] ?", "", BLUE),
 ("c19", "Et toi : tu achètes, tu vends ou tu [attends] ?", "", GREEN),
 ("c20", "Abonne-toi, like, partage.", "", BLUE),
]
CAP = {s[0]: s[1] for s in SC}; QRY = {s[0]: s[2] for s in SC}; ACC = {s[0]: s[3] for s in SC}
ORDER = [s[0] for s in SC]
def tline(cid):
    """repères internes d'une scène : fin de frappe, clic, arrivée de la carte"""
    q = QRY[cid]
    if not q: return 0, 0.15, 0.25
    cps = max(32, len(q)/0.8); te = 0.15+len(q)/cps
    tc = te+0.2; return te, tc, tc+0.12
def build():
    tl, t = {}, 0.0
    for cid in ORDER:
        clean = re.sub(r'[\[\]]', '', CAP[cid]); te, tc, tk = tline(cid)
        d = tk+max(2.4, len(clean)/22+0.7)
        if cid == 'c01': d = 5.0
        if cid == 'c17': d += 1.6
        if cid == 'c19': d = 4.6
        if cid == 'c20': d = 3.6
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.05
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]

# ---------- éléments animés ----------
def _arrow(c):
    c.move_to(0, 0); c.line_to(0, 34); c.line_to(8, 26); c.line_to(14, 40); c.line_to(20, 37); c.line_to(14, 24); c.line_to(25, 24); c.close_path()
def pointer(c, x, y, press=0.0, a=1.0):
    """curseur flèche générique (ombre + corps blanc cerné)"""
    if a <= 0: return
    s = 1.5*(1-0.12*press)
    c.save(); c.translate(x+3, y+5); c.scale(s, s); _arrow(c); col(c, '000000', .2*a); c.fill(); c.restore()
    c.save(); c.translate(x, y); c.scale(s, s); _arrow(c); col(c, 'FFFFFF', a); c.fill_preserve(); c.set_line_width(1.6); c.set_line_join(1); col(c, INK, a); c.stroke(); c.restore()
def ripple(c, x, y, u, color):
    if 0 < u < 1:
        c.arc(x, y, 18+60*ease(u), 0, 2*math.pi); c.set_line_width(4*(1-u)); col(c, color, .8*(1-u)); c.stroke()
def typed(q, s):
    if not q: return ""
    te, tc, tk = tline_q(q); n = int(clamp((s-0.15)/(te-0.15)) * len(q)) if te > 0.15 else len(q)
    return q[:n]
def tline_q(q):
    cps = max(32, len(q)/0.8); te = 0.15+len(q)/cps; return te, te+0.2, te+0.32
def key_times(cid):
    q = QRY[cid]
    if not q: return []
    te, tc, tk = tline(cid); n = len(q); return [T(cid)+0.15+(te-0.15)*(i+1)/n for i in range(n) if q[i] != ' ']

def bars(c, x0, base, vals, labs, cols_, u, maxh=170, w=230, gap=90, fmtv=None):
    vmax = max(vals)
    for i, v in enumerate(vals):
        x = x0+i*(w+gap); hh = maxh*v/vmax*ease(clamp(u*1.3-i*0.25))
        if hh > 1: rr(c, x, base-hh, w, hh, 14); col(c, cols_[i]); c.fill()
        text(c, labs[i], x+w/2, base+30, 'm', 26, SUB)
        if hh > 6: text(c, fmtv(v) if fmtv else str(v), x+w/2, base-hh-30, 'xb', 34, INK)
def donut(c, cx, cy, r, frac, u, color, w=40):
    c.set_line_width(w); c.arc(cx, cy, r, 0, 2*math.pi); col(c, LINE); c.stroke()
    c.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*frac*ease(u)); col(c, color); c.stroke()

def card_content(c, cid, u, s, X, Y, Wd, Hd):
    acc = ACC[cid]; cx = X+Wd/2
    def big(sv, y=Y+250, size=150, color=acc):
        while tw(c, sv, 'k', size) > Wd-80: size -= 6
        text(c, sv, cx, y, 'k', size, color)
    if cid == 'c02':
        text(c, "« Code rouge »", cx, Y+230, 'k', 104, RED)
        text(c, "décembre 2022 · selon le New York Times", cx, Y+330, 'm', 30, SUB)
        text(c, "Google réorganise ses équipes face à ChatGPT", cx, Y+420, 'sb', 32, INK)
        for k in range(3):
            a = clamp(u*3-k); c.arc(cx-60+k*60, Y+520, 14, 0, 2*math.pi); col(c, RED, .25+.75*a*(0.5+0.5*math.sin(s*6+k))); c.fill()
    elif cid == 'c03':
        v = 100*ease(u); big(f"−{int(v)} MD$", Y+240, 150, RED)
        text(c, "de valeur en Bourse en une journée", cx, Y+340, 'sb', 32, INK)
        text(c, "8 février 2023 · erreur de son chatbot dans une publicité", cx, Y+395, 'm', 26, SUB)
        pts = [0, .02, -.01, .03, .02, -.35, -.33, -.36]
        c.set_line_width(6); c.set_line_join(1)
        k = ease(u)*(len(pts)-1)
        for i in range(int(k)+1): (c.move_to if i == 0 else c.line_to)(X+120+i*90, Y+520-pts[i]*260)
        col(c, RED); c.stroke()
    elif cid == 'c04':
        text(c, "OCT. 2021", X+220, Y+190, 'sb', 30, SUB); text(c, "1 000 €", X+220, Y+290, 'k', 96, INK)
        text(c, "OCT. 2026", X+Wd-200, Y+190, 'sb', 30, SUB); text(c, "?", X+Wd-200, Y+300, 'k', 160, YELLOW)
        c.set_line_width(5); col(c, YELLOW); c.move_to(X+400, Y+280); c.line_to(X+400+180*ease(u), Y+280); c.stroke()
        text(c, "réponse à la fin de la vidéo", cx, Y+470, 'm', 30, SUB)
    elif cid == 'c05':
        big(f"{119.8*ease(u):.1f}".replace('.', ',')+" MD$", Y+220, 130, BLUE)
        chip(c, "+24 % sur un an", cx, Y+330, GREEN, 30)
        bars(c, X+180, Y+600, [96.6, 119.8], ["avr-juin 2025", "avr-juin 2026"], ['C6CBD3', BLUE], u, maxh=170, fmtv=lambda v: f"{v:.1f} Md$".replace('.', ','))
    elif cid == 'c06':
        donut(c, X+230, Y+380, 150, 63.3/119.8, u, BLUE)
        text(c, "53 %", X+230, Y+385, 'k', 64, INK)
        text(c, "RECHERCHE", X+440, Y+250, 'xb', 40, BLUE, 'l'); text(c, "63,3 Md$ en 3 mois", X+440, Y+310, 'm', 32, INK, 'l')
        chip(c, "+17 %", X+530, Y+390, GREEN, 34)
        text(c, "plus de la moitié des ventes", X+440, Y+470, 'm', 28, SUB, 'l')
    elif cid == 'c07':
        big(f"+{int(82*ease(u))} %", Y+220, 160, GREEN); text(c, "sur un an · 514 Md$ de contrats déjà signés", cx, Y+320, 'sb', 28, SUB)
        bars(c, X+180, Y+600, [13.6, 24.8], ["avr-juin 2025", "avr-juin 2026"], ['C6CBD3', GREEN], u, maxh=150, fmtv=lambda v: f"{v:.1f} Md$".replace('.', ','))
    elif cid == 'c08':
        big(f"{int(514*ease(u))} MD$", Y+230, 150, GREEN)
        text(c, "de contrats cloud déjà signés", cx, Y+330, 'sb', 32, INK)
        for k in range(5):     # ≈ 5 ans de ventes du cloud au rythme actuel
            x = X+130+k*125; a = clamp(u*5-k)
            rr(c, x, Y+420, 100, 100, 18); col(c, GREEN, .15+.85*a); c.fill(); text(c, f"an {k+1}", x+50, Y+470, 'sb', 24, 'FFFFFF' if a > .5 else SUB)
        text(c, "≈ 5 ans de ventes du cloud au rythme actuel", cx, Y+565, 'm', 26, SUB)
    elif cid == 'c09':
        big(f"{int(950*ease(u))} M", Y+220, 150, BLUE)
        text(c, "d'utilisateurs par mois · application Gemini", cx, Y+320, 'sb', 30, INK)
        x0, x1, y = X+90, X+Wd-90, Y+430
        rr(c, x0, y, x1-x0, 30, 15); col(c, LINE); c.fill(); rr(c, x0, y, (x1-x0)*0.95*ease(u), 30, 15); col(c, BLUE); c.fill()
        text(c, "1 milliard", x1, y+70, 'sb', 26, SUB, 'r')
        text(c, "et 90 % des 100 plus grandes entreprises US utilisent son offre pro", cx, Y+570, 'm', 24, SUB)
    elif cid == 'c10':
        big("≈ 4 300 MD$", Y+220, 120, YELLOW)
        text(c, "capitalisation boursière · 9 octobre 2026", cx, Y+310, 'sb', 28, SUB)
        x0, x1, y = X+90, X+Wd-90, Y+430; lo, hi, v = 235.84, 408.61, 351.66
        rr(c, x0, y, x1-x0, 24, 12); col(c, LINE); c.fill()
        xm = x0+(x1-x0)*(v-lo)/(hi-lo)*ease(u); rr(c, x0, y, xm-x0, 24, 12); col(c, YELLOW); c.fill()
        c.arc(xm, y+12, 22, 0, 2*math.pi); col(c, 'FFFFFF'); c.fill_preserve(); col(c, INK); c.set_line_width(4); c.stroke()
        text(c, "236 $", x0, y+70, 'sb', 28, SUB, 'l'); text(c, "409 $", x1, y+70, 'sb', 28, SUB, 'r'); text(c, "352 $", xm, y-46, 'xb', 32, INK)
        text(c, "fourchette sur 52 semaines", cx, Y+575, 'm', 26, SUB)
    elif cid == 'c11':
        for k, (lab, v) in enumerate((("Data centers", .9), ("Puces maison (TPU)", .7), ("Serveurs IA", .8))):
            y = Y+200+k*120; text(c, lab, X+70, y, 'sb', 36, INK, 'l')
            rr(c, X+70, y+34, Wd-140, 22, 11); col(c, LINE); c.fill(); rr(c, X+70, y+34, (Wd-140)*v*ease(clamp(u*1.5-k*0.2)), 22, 11); col(c, RED); c.fill()
        text(c, "les postes qui avalent les milliards", cx, Y+580, 'm', 26, SUB)
    elif cid == 'c12':
        big(f"{int(205*ease(u))} MD$", Y+210, 150, RED); text(c, "d'investissements prévus en 2026 (haut de fourchette)", cx, Y+305, 'sb', 26, SUB)
        bars(c, X+90, Y+600, [22.45, 35.67, 44.9], ["T2 2025", "T1 2026", "T2 2026"], ['C6CBD3', 'F6AEA9', RED], u, maxh=150, w=200, gap=60, fmtv=lambda v: f"{v:.0f} Md$")
    elif cid == 'c13':
        big("−5,9 MD$", Y+230, 150, RED); text(c, "cash-flow libre · avril-juin 2026", cx, Y+330, 'sb', 30, SUB)
        text(c, "l'argent produit ne suffit plus à payer les investissements", cx, Y+430, 'm', 28, INK)
        c.set_line_width(4); col(c, LINE); c.move_to(X+90, Y+530); c.line_to(X+Wd-90, Y+530); c.stroke()
        c.move_to(X+90, Y+500);
        for i in range(8): c.line_to(X+90+i*(Wd-180)/7, Y+500-60*math.sin(i*0.5)+i*14*ease(u))
        col(c, RED); c.set_line_width(5); c.stroke()
    elif cid == 'c14':
        donut(c, X+230, Y+380, 150, 98/112.2, u, YELLOW)
        text(c, "112 Md$", X+230, Y+385, 'k', 50, INK)
        text(c, "BÉNÉFICE NET T2", X+440, Y+230, 'xb', 36, INK, 'l')
        rr(c, X+440, Y+290, 28, 28, 6); col(c, YELLOW); c.fill(); text(c, "98 Md$ de gains sur", X+485, Y+304, 'm', 30, INK, 'l'); text(c, "des participations", X+485, Y+344, 'm', 30, INK, 'l')
        rr(c, X+440, Y+410, 28, 28, 6); col(c, LINE); c.fill(); text(c, "≈ 14 Md$ le reste", X+485, Y+424, 'm', 30, INK, 'l')
        text(c, "des gains « sur le papier », pas du cash encaissé", cx, Y+575, 'm', 26, SUB)
    elif cid == 'c15':
        for k, (yr, lab, cc) in enumerate((("SEPT. 2025 · ÉTATS-UNIS", "Chrome : pas de vente forcée", GREEN), ("SEPT. 2026 · ÉTATS-UNIS", "Régie AdX : pas de vente forcée", GREEN), ("EN COURS · UNION EUROPÉENNE", "Enquête sur l'auto-favoritisme", RED))):
            y = Y+190+k*140; a = clamp(u*2.6-k*0.7)
            c.arc(X+110, y, 34, 0, 2*math.pi); col(c, cc, a); c.fill()
            c.set_line_width(6); col(c, 'FFFFFF', a)
            if cc == GREEN: c.move_to(X+94, y); c.line_to(X+106, y+12); c.line_to(X+128, y-12); c.stroke()
            else: c.move_to(X+110, y-16); c.line_to(X+110, y+4); c.stroke(); c.arc(X+110, y+15, 4, 0, 2*math.pi); c.fill()
            text(c, yr, X+170, y-26, 'sb', 26, SUB, 'l', a); text(c, lab, X+170, y+18, 'xb', 34, INK, 'l', a)
        text(c, "des mesures restent imposées sur ses pratiques", cx, Y+585, 'm', 26, SUB)
    elif cid == 'c16':
        text(c, "UNION EUROPÉENNE", cx, Y+200, 'sb', 32, SUB, 'c', 1, 4)
        text(c, "Digital Markets Act", cx, Y+290, 'k', 72, INK)
        chip(c, "auto-favoritisme dans la recherche", cx, Y+400, RED, 32)
        text(c, "risque : amendes", cx, Y+500, 'm', 30, SUB)
    elif cid == 'c17':
        v = lerp(1000, TOT, ease(u*1.1)); sv = fmt(round(v, -1) if v < TOT-10 else 2680)+" €"
        w1 = tw(c, "≈ ", 'xb', 80); w2 = tw(c, sv, 'k', 150); x0 = cx-(w1+w2)/2
        text(c, "≈", x0, Y+230, 'xb', 80, INK, 'l'); text(c, sv, x0+w1, Y+230, 'k', 150, BLUE, 'l')
        text(c, f"{fmt(VAL)} € d'action  +  {round(DIV)} € de dividendes", cx, Y+345, 'm', 30, INK)
        text(c, "change €/$ inclus · avant impôts et frais", cx, Y+395, 'l', 26, SUB)
        bars(c, X+180, Y+600, [1000, TOT], ["oct. 2021", "oct. 2026"], ["C6CBD3", BLUE], clamp(u*1.4), maxh=130, fmtv=lambda v: fmt(round(v, -1))+" €")

def scene(cid, t):
    a, d = TL[cid]; s = t-a; acc = ACC[cid]
    S, c = surface(); background(c, t)
    q = QRY[cid]; te, tc, tk = tline(cid)
    if cid == 'c01':
        bar_y = 470; searchbar(c, typed(q, s), bar_y, cursor=(int(s*2.2) % 2 == 0) or s < te, focus=1)
        for j, sg in enumerate(("google est-il fini", "google va-t-il disparaître", "la fin de la recherche en ligne")):
            al = clamp((s-te-0.1-j*0.12)/0.25)
            if al > 0:
                y = 590+j*78; c.push_group(); magnifier(c, 170, y, 26, '9AA3B5'); text(c, sg, 210, y, 'm', 34, SUB, 'l'); c.pop_group_to_source(); c.paint_with_alpha(al)
        u1 = ease((s-1.9)/0.4); u2 = clamp((s-2.4)/0.35)
        if u1 > 0: c.push_group(); text(c, "L'IA DEVAIT", 540, 900+20*(1-u1), 'k', 110, INK); c.pop_group_to_source(); c.paint_with_alpha(u1)
        if u2 > 0:
            sc_ = lerp(1.5, 1, ease(u2)); c.save(); c.translate(540, 1030); c.scale(sc_, sc_); c.push_group(); text(c, "LE TUER.", 0, 0, 'k', 150, RED); c.pop_group_to_source(); c.paint_with_alpha(clamp(u2*2)); c.restore()
    elif cid in ('c18', 'c19', 'c20'):
        if cid == 'c18':
            for k, (lab, v, cc) in enumerate((("L'IA DEVAIT LE TUER", "2023", RED), ("ELLE L'A RENDU PLUS FORT ?", "2026", GREEN))):
                al = ease((s-0.2-k*0.9)/0.4)
                if al <= 0: continue
                y = 560+k*330; c.push_group(); card(c, 110, y-140, 860, 260, None, v)
                text(c, lab, 540, y+20, 'k', 58 if k else 64, cc); c.pop_group_to_source(); c.paint_with_alpha(al)
        elif cid == 'c19':
            al = ease(s/0.4); c.push_group(); text(c, "Et toi ?", 540, 470, 'k', 170, INK); c.pop_group_to_source(); c.paint_with_alpha(al)
            for j, (lab, cc) in enumerate((("J'achète", GREEN), ("Je vends", RED), ("J'attends", YELLOW))):
                al = ease((s-0.3-j*0.18)/0.4)
                if al <= 0: continue
                y = 680+j*150; c.push_group(); soft_shadow(c, 250, y, 580, 112, 56, .1); rr(c, 250, y, 580, 112, 56); col(c, 'FFFFFF'); c.fill_preserve(); col(c, cc); c.set_line_width(4); c.stroke()
                text(c, f"{j+1}", 312, y+56, 'k', 44, cc); text(c, lab, 560, y+56, 'xb', 54, INK); c.pop_group_to_source(); c.paint_with_alpha(al)
            # le curseur vient cliquer « J'attends »
            px, py = lerp(940, 690, ease((s-1.4)/0.8)), lerp(1500, 1000, ease((s-1.4)/0.8))
            if s > 1.4: ripple(c, 690, 1000, (s-2.3)/0.5, YELLOW); pointer(c, px, py, 1 if 2.3 < s < 2.42 else 0)
        else:
            sc_ = lerp(0.8, 1, ease(s/0.5)); c.save(); c.translate(540, 470); c.scale(sc_, sc_); c.translate(-540, -470); logo_symbol(c, 540, 470, 190); c.restore()
            text(c, "Actions_Benefices", 540, 630, 'b', 46, INK)
            for j, lab in enumerate(("Abonne-toi", "Like", "Partage")):
                al = ease((s-0.35-j*0.25)/0.4)
                if al <= 0: continue
                y = 730+j*135; c.push_group(); rr(c, 290, y, 500, 100, 50); col(c, GCOLS[j]); c.fill(); text(c, lab, 540, y+50, 'xb', 46, 'FFFFFF'); c.pop_group_to_source(); c.paint_with_alpha(al)
    else:
        bar_y = 400; searchbar(c, typed(q, s), bar_y, cursor=s < tc+0.1, focus=1 if s < tc+0.2 else .4)
        # carte résultat
        ku = ease((s-tk)/0.4)
        if ku > 0:
            X, Y, Wd, Hd = 110, 520+50*(1-ku), 860, 640
            c.push_group(); card(c, X, Y, Wd, Hd, None, "résultat"); card_content(c, cid, clamp((s-tk-0.2)/1.8), s, X, Y, Wd, Hd); c.pop_group_to_source(); c.paint_with_alpha(ku)
        # curseur : vient de bas-droite, clique sur la loupe, repart
        tgt = (164, 404)
        if s < tc+0.7:
            m = ease((s-0.05)/(tc-0.05)); px, py = lerp(960, tgt[0], m), lerp(1560, tgt[1], m)
            al = clamp(s/0.2)*(1-clamp((s-tc-0.4)/0.3))
            if s > tc: px, py = tgt[0]+90*ease((s-tc-0.15)/0.5), tgt[1]+60*ease((s-tc-0.15)/0.5)
            ripple(c, tgt[0], tgt[1], (s-tc)/0.45, acc); pointer(c, px, py, 1 if tc <= s < tc+0.12 else 0, al)
    # sous-titre
    items = parse(CAP[cid]); fo = 1-clamp((s-(d-0.15))/0.15)
    c0 = 0.15 if cid in ('c01', 'c18', 'c19', 'c20') else tc
    k = clamp((s-c0)/0.25)*fo
    if k > 0:
        c.push_group(); caption(c, items, 1352, 46, acc); c.pop_group_to_source(); c.paint_with_alpha(k)
    if cid in ('c10', 'c12', 'c13', 'c14', 'c17', 'c18', 'c19'):
        text(c, "Contenu pédagogique, pas un conseil en investissement", 540, 1470, 'm', 22, SUB, 'c', .9)
    progress(c, clamp(t/DUR))
    return to_img(S)
def frame(t):
    cur = ORDER[0]
    for cid in ORDER:
        if t >= T(cid)-0.001: cur = cid
    im = scene(cur, t); i = ORDER.index(cur)
    if i > 0 and t-T(cur) < 0.22:
        im = Image.blend(scene(ORDER[i-1], t), im, inout((t-T(cur))/0.22))
    if t < 0.25: im = Image.blend(Image.new('RGBA', (W, H), (248, 249, 250, 255)), im, clamp(t/0.25))
    if t > DUR-0.4: im = Image.blend(im, Image.new('RGBA', (W, H), (248, 249, 250, 255)), clamp((t-(DUR-0.4))/0.4))
    return im

def events():
    ev = []
    for cid in ORDER:
        a = T(cid); te, tc, tk = tline(cid)
        for kt in key_times(cid): ev.append((kt, 'key'))
        if QRY[cid] and cid != 'c01':
            ev += [(a+tc, 'click'), (a+tk+0.15, 'impact')]
            if cid in ('c03', 'c05', 'c07', 'c08', 'c09', 'c12', 'c17'): ev.append((a+tk+0.3, 'tick'))
        if cid != 'c01': ev.append((a, 'swish'))
    ev += [(T('c01')+2.4, 'impact'), (T('c03')+tline('c03')[2]+0.4, 'low'), (T('c13'), 'low'), (T('c17')-1.2, 'riser'),
           (T('c17')+tline('c17')[2]+1.8, 'impact'), (T('c17')+tline('c17')[2]+1.8, 'glint'), (T('c19')+2.3, 'click'), (T('c19'), 'impact')]
    return ev

def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 1) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/googl/prev', exist_ok=True)
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/googl/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
