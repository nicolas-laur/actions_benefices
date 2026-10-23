"""Infographies affichées sur le dos de la carte (canevas 1560×670, plaqué ensuite en perspective)."""
import math, cairo
from vty import GOLD, GOLDG, WH, GR, GREEN, RED, hx, col, tw, text, gtext, rr
CW, CH = 1560, 670
REDS = 'FF6B5E'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')
def T(c, s, x, y, f, size, color=WH, align='c', a=1, track=0): text(c, s, x, y, f, size, color, align, a, track, False)
def label(c, s, x=60, y=58, color=GOLD, size=40): T(c, s, x, y, 'sb', size, color, 'l', 1, 5)

def donut(c, cx, cy, r, frac, u, color=GOLD, w=46, bg=.12):
    c.set_line_width(w); c.set_line_cap(0)
    c.arc(cx, cy, r, 0, 2*math.pi); col(c, 'FFFFFF', bg); c.stroke()
    a0 = -math.pi/2; c.arc(cx, cy, r, a0, a0+2*math.pi*frac*ease(u)); col(c, color); c.stroke()
def bars(c, vals, labels, u, x0=140, base=600, top=170, w=230, gap=170, colors=None, fmtv=None, vmax=None):
    vmax = vmax or max(vals)
    for i, v in enumerate(vals):
        x = x0+i*(w+gap); hh = (base-top)*v/vmax*ease(clamp(u*1.2-i*0.2))
        rr(c, x, base-hh, w, hh, 14); col(c, (colors or ['FFFFFF', GOLD])[i % 2], .3 if (colors or ['FFFFFF', GOLD])[i % 2] == 'FFFFFF' else 1); c.fill()
        T(c, labels[i], x+w/2, base+40, 'sb', 36, GR)
        if hh > 4: T(c, fmtv(v) if fmtv else str(v), x+w/2, base-hh-36, 'k', 50, WH)

def draw(c, key, u, t=0.0):
    """u : avancement 0→1 de l'animation du contenu ; t : temps écoulé dans la scène (s)"""
    if key == 'feed':     # flux de paiements validés
        label(c, "PAIEMENTS EN COURS")
        rows = [("Boulangerie", "3,20 €"), ("Train", "45,00 €"), ("Supermarché", "62,80 €"), ("Streaming", "13,49 €"), ("Café", "2,10 €"), ("Pharmacie", "8,90 €"), ("Carburant", "71,30 €")]
        off = (t*1.6) % 1; k0 = int(t*1.6)
        for j in range(5):
            name, amt = rows[(k0+j) % len(rows)]; y = 150+j*105-off*105
            a = clamp(min((y-90)/60, (640-y)/60))
            if a <= 0: continue
            T(c, name, 60, y, 'm', 40, WH, 'l', a); T(c, amt, 1240, y, 'xb', 42, WH, 'r', a)
            c.arc(1330, y, 22, 0, 2*math.pi); col(c, GREEN, .9*a); c.set_line_width(5); c.stroke()
            c.move_to(1318, y); c.line_to(1327, y+9); c.line_to(1343, y-9); c.stroke()
            col(c, 'FFFFFF', .08*a); c.rectangle(60, y+42, 1440, 2); c.fill()
    elif key == 'hook':
        label(c, "TON INVESTISSEMENT")
        T(c, "OCT. 2021", 300, 250, 'sb', 34, GR); T(c, "1 000 €", 300, 380, 'k', 110, WH)
        T(c, "OCT. 2026", 1180, 250, 'sb', 34, GR); gtext(c, "?", 1180, 390, 'k', 170, GOLDG)
        c.set_line_width(4); col(c, GOLD, .8); c.move_to(560, 360); c.line_to(560+380*ease(u), 360); c.stroke()
        if u > .9: c.move_to(925, 340); c.line_to(950, 360); c.line_to(925, 380); c.stroke()
        T(c, "réponse à la fin de la vidéo", 780, 560, 'm', 38, GR)
    elif key == 'credit':
        label(c, "CE QUE VISA PRÊTE")
        for j, (lab, val) in enumerate((("CRÉDIT ACCORDÉ", "0 €"), ("RISQUE D'IMPAYÉ", "0"))):
            y = 230+j*190; T(c, lab, 60, y, 'sb', 34, WH, 'l', 1, 3)
            rr(c, 60, y+40, 1100, 40, 20); col(c, 'FFFFFF', .12); c.fill()
            gtext(c, val, 1360, y+60, 'k', 90, GOLDG)
        T(c, "les cartes sont émises par les banques, qui portent le crédit", 780, 620, 'm', 34, GR)
    elif key == 'flow':
        label(c, "LE CIRCUIT D'UN PAIEMENT")
        nodes = [("TOI", 150), ("TA BANQUE", 465), ("VISA", 780), ("SA BANQUE", 1095), ("COMMERÇANT", 1410)]
        y = 360; p = clamp(u*1.15)
        c.set_line_width(6); col(c, 'FFFFFF', .2); c.move_to(150, y); c.line_to(1410, y); c.stroke()
        col(c, GOLD); c.move_to(150, y); c.line_to(150+1260*ease(p), y); c.stroke()
        for j, (lab, x) in enumerate(nodes):
            on = 150+1260*ease(p) >= x-1; r = 48 if lab == "VISA" else 30
            c.arc(x, y, r, 0, 2*math.pi); col(c, '0B1020'); c.fill_preserve(); col(c, GOLD if on else 'FFFFFF', 1 if on else .35); c.set_line_width(6); c.stroke()
            T(c, lab, x, y+(100 if lab != "VISA" else 115), 'xb' if lab == "VISA" else 'sb', 40 if lab == "VISA" else 32, GOLD if lab == "VISA" else WH)
        if u > .7:
            v = ease((u-.7)/.3); c.save(); c.translate(780, y-130-50*(1-v)); c.push_group()
            w = tw(c, "+ commission", 'xb', 40)+60; rr(c, -w/2, -34, w, 68, 34); col(c, GOLD); c.fill(); T(c, "+ commission", 0, 0, 'xb', 40, '0A1020')
            c.pop_group_to_source(); c.paint_with_alpha(v); c.restore()
    elif key == 'toll':
        label(c, "SUR CHAQUE PAIEMENT")
        rr(c, 60, 260, 1440, 120, 22); col(c, 'FFFFFF', .14); c.fill()
        T(c, "TON PAIEMENT", 120, 320, 'xb', 44, WH, 'l')
        w = 70*ease(u); rr(c, 1500-w, 260, w, 120, 22); col(c, GOLD); c.fill()
        c.set_line_width(3); col(c, GOLD, .9); c.move_to(1465, 400); c.line_to(1465, 470); c.stroke()
        T(c, "une petite fraction pour le réseau", 1465, 510, 'sb', 32, GOLD, 'r')
        T(c, "× des milliards de fois par trimestre", 780, 610, 'm', 38, GR)
    elif key == 'tx':
        label(c, "TRANSACTIONS TRAITÉES · 3 MOIS")
        bars(c, [65.2, 71.7], ["AVR-JUIN 2025", "AVR-JUIN 2026"], u, x0=300, w=330, gap=300, fmtv=lambda v: f"{v:.0f} MD".replace('.', ','))
        if u > .8: c.save(); c.translate(1340, 260); w = tw(c, "+10 %", 'xb', 46)+50; rr(c, -w/2, -36, w, 72, 36); col(c, GOLD); c.fill(); T(c, "+10 %", 0, 0, 'xb', 46, '0A1020'); c.restore()
    elif key == 'tps':
        label(c, "COMPTEUR EN DIRECT")
        n = 9119*max(0, t-0.3)
        T(c, "+ "+fmt(n), 780, 300, 'k', 150, WH)
        T(c, "transactions depuis le début de cette phrase", 780, 430, 'm', 34, GR)
        for k in range(48):     # grille qui s'allume en rythme
            x = 120+(k % 24)*55; y = 540+(k//24)*55; on = (k+int(t*30)) % 7 == 0
            c.arc(x, y, 12, 0, 2*math.pi); col(c, GOLD if on else 'FFFFFF', .95 if on else .12); c.fill()
    elif key == 'volume':
        label(c, "VOLUME DE PAIEMENTS · 3 MOIS")
        x0, x1, y = 80, 1480, 330; v = ease(u)*1.04
        rr(c, x0, y, x1-x0, 70, 35); col(c, 'FFFFFF', .12); c.fill()
        rr(c, x0, y, (x1-x0)*v/1.1, 70, 35); col(c, GOLD); c.fill()
        xm = x0+(x1-x0)/1.1; c.set_dash([14, 10]); c.set_line_width(4); col(c, WH, .9); c.move_to(xm, y-60); c.line_to(xm, y+130); c.stroke(); c.set_dash([])
        T(c, "4 000 MD$", xm, y-95, 'xb', 40, WH)
        T(c, "seuil franchi pour la première fois", 780, 560, 'm', 34, GR)
    elif key == 'rev':
        label(c, "REVENUS · 3 MOIS")
        bars(c, [10.2, 11.6], ["AVR-JUIN 2025", "AVR-JUIN 2026"], u, x0=300, w=330, gap=300, fmtv=lambda v: f"{v:.1f} MD$".replace('.', ','))
        if u > .8: c.save(); c.translate(1340, 260); w = tw(c, "+14 %", 'xb', 46)+50; rr(c, -w/2, -36, w, 72, 36); col(c, GOLD); c.fill(); T(c, "+14 %", 0, 0, 'xb', 46, '0A1020'); c.restore()
    elif key == 'margin':
        label(c, "SUR 1 $ DE REVENUS")
        donut(c, 380, 380, 190, 0.48, u)
        gtext(c, f"{int(round(48*ease(u)))} ¢", 380, 390, 'k', 96, GOLDG)
        T(c, "BÉNÉFICE NET", 760, 280, 'xb', 50, GOLD, 'l'); T(c, "5,6 MD$ sur 11,6 MD$ de revenus", 760, 350, 'm', 34, WH, 'l')
        T(c, "LE RESTE", 760, 470, 'xb', 50, GR, 'l'); T(c, "charges, impôts, litiges", 760, 540, 'm', 34, GR, 'l')
    elif key == 'fresno':
        label(c, "FRESNO, CALIFORNIE · 1958")
        n = int(65*ease(u))
        for k in range(65):
            x = 90+(k % 13)*108; y = 140+(k//13)*92
            rr(c, x, y, 84, 54, 8); col(c, GOLD if k < n else 'FFFFFF', .9 if k < n else .1); c.fill()
        T(c, "1 carte = 1 000 cartes envoyées par la poste", 780, 625, 'm', 36, GR)
    elif key == 'ipo':
        label(c, "INTRODUCTION EN BOURSE · MARS 2008")
        for j, (v, lab) in enumerate((("44 $", "PRIX PAR ACTION"), ("406 M", "ACTIONS VENDUES"), ("≈ 19 MD$", "LEVÉS AU TOTAL"))):
            x = 280+j*500; gtext(c, v, x, 320, 'k', 96, GOLDG) if j == 2 else T(c, v, x, 320, 'k', 96, WH); T(c, lab, x, 420, 'sb', 30, GR, 'c', 1, 2)
        T(c, "la plus grosse introduction américaine de l'époque", 780, 580, 'm', 38, GR)
    elif key == 'curve':
        label(c, "COURS DE L'ACTION · 2008 → 2026")
        pts = [(2008.2, 11), (2009, 19.7), (2010, 16.0), (2011, 23.2), (2012, 34.9), (2013, 51.7), (2014, 61.3), (2015, 73.1), (2016, 74.1), (2017, 109), (2018, 127),
               (2019, 182), (2020, 213), (2021, 212), (2022, 205), (2023, 259), (2024, 306), (2026.8, 385.45)]
        X = lambda yr: 90+(yr-2008)/(2026.8-2008)*1300; Y = lambda v: 590-v/400*470
        k = ease(u)*(len(pts)-1); n = int(k); fr = k-n
        c.set_line_width(7); c.set_line_join(1); col(c, GOLD)
        c.move_to(X(pts[0][0]), Y(pts[0][1]))
        for i in range(1, n+1): c.line_to(X(pts[i][0]), Y(pts[i][1]))
        if n+1 < len(pts):
            a, b = pts[n], pts[n+1]; c.line_to(X(a[0]+(b[0]-a[0])*fr), Y(a[1]+(b[1]-a[1])*fr))
        path = c.copy_path(); c.stroke()
        T(c, "11 $", X(2008.2)+10, Y(11)-40, 'xb', 36, WH, 'l')
        if u > .95: T(c, "385 $", X(2026.8)-10, Y(385.45)-40, 'xb', 44, GOLD, 'r')
        T(c, "courbe simplifiée · clôtures annuelles ajustées", 780, 645, 'm', 30, GR)
    elif key == 'range':
        label(c, "FOURCHETTE SUR 52 SEMAINES")
        x0, x1, y = 120, 1440, 330; lo, hi, v = 293.89, 386.84, 385.45
        rr(c, x0, y, x1-x0, 26, 13); col(c, 'FFFFFF', .14); c.fill()
        g = cairo.LinearGradient(x0, 0, x1, 0); g.add_color_stop_rgba(0, *hx('FFFFFF', .2)); g.add_color_stop_rgba(1, *hx(GOLD)); rr(c, x0, y, (x1-x0)*ease(u), 26, 13); c.set_source(g); c.fill()
        xm = x0+(x1-x0)*(v-lo)/(hi-lo)*ease(u); c.arc(xm, y+13, 30, 0, 2*math.pi); col(c, GOLD); c.fill()
        T(c, "294 $", x0, y+90, 'xb', 40, GR, 'l'); T(c, "387 $", x1, y+90, 'xb', 40, GR, 'r')
        T(c, "CLÔTURE 9 OCT. : 385 $", 780, 560, 'xb', 44, WH)
    elif key == 'jobs':
        label(c, "EFFECTIFS · ÉTÉ 2026", color=REDS)
        donut(c, 380, 380, 190, 0.07, u, REDS)
        T(c, "≈ 7 %", 380, 385, 'k', 90, WH)
        T(c, "≈ 2 600 POSTES", 760, 290, 'xb', 54, REDS, 'l'); T(c, "surtout tech et produit", 760, 360, 'm', 34, WH, 'l')
        T(c, "563 M$", 760, 470, 'xb', 54, WH, 'l'); T(c, "d'indemnités de départ", 760, 540, 'm', 34, GR, 'l')
    elif key == 'doj':
        label(c, "ÉTATS-UNIS CONTRE VISA · DÉBIT", color=REDS)
        steps = [("2024", "plainte du DOJ"), ("2026", "procédure en cours"), ("≈ 2028", "procès attendu")]
        y = 340; c.set_line_width(6); col(c, 'FFFFFF', .2); c.move_to(220, y); c.line_to(1340, y); c.stroke()
        col(c, REDS); c.move_to(220, y); c.line_to(220+560*ease(u), y); c.stroke()
        for j, (yr, lab) in enumerate(steps):
            x = 220+j*560; on = 220+560*ease(u)*2 >= x-1
            c.arc(x, y, 30, 0, 2*math.pi); col(c, '0B1020'); c.fill_preserve(); col(c, REDS if j < 2 else 'FFFFFF', 1 if j < 2 else .6); c.stroke()
            T(c, yr, x, y-90, 'k', 54, WH); T(c, lab, x, y+90, 'm', 38, GR)
        T(c, "Visa conteste toute pratique illégale", 780, 600, 'm', 36, GR)
    elif key == 'rivals':
        label(c, "MENACE OU RELAIS ?", color=REDS)
        for j, (name, desc) in enumerate((("STABLECOINS", "paiements en cryptos adossées au dollar"), ("AGENTS IA", "l'IA qui paie à ta place"))):
            y = 220+j*210; T(c, name, 60, y, 'k', 66, WH, 'l'); T(c, desc, 60, y+70, 'm', 32, GR, 'l')
            for k, (tag, cc) in enumerate((("MENACE", REDS), ("RELAIS", GOLD))):
                x = 1080+k*230; on = (int(t*1.2)+j+k) % 2 == 0
                rr(c, x, y-36, 200, 72, 36); col(c, cc, .95 if on else .15); c.fill(); T(c, tag, x+100, y, 'xb', 30, '0A1020' if on else WH)
    elif key == 'reveal':
        label(c, "TES 1 000 € D'OCTOBRE 2021")
        base, top = 600, 140; vmax = 1900
        def bar(x, segs, lab):
            yy = base
            for v, cc, a in segs:
                hh = (base-top)*v/vmax*ease(u); rr(c, x, yy-hh, 300, hh, 12); col(c, cc, a); c.fill(); yy -= hh
            T(c, lab, x+150, base+40, 'sb', 36, GR)
            return yy
        bar(260, [(1000, 'FFFFFF', .35)], "OCT. 2021"); T(c, "1 000 €", 410, base-(base-top)*1000/vmax*ease(u)-40, 'k', 50, WH)
        yy = bar(1000, [(1772, GOLD, 1), (48, 'FFE7B0', 1)], "OCT. 2026")
        if u > .6: gtext(c, "≈ 1 820 €", 1150, yy-46, 'k', 56, GOLDG)
    elif key == 'verdict':
        label(c, "LE BILAN")
        for j, (title, items, cc) in enumerate((("POUR", ["72 Md de transactions", "48 ¢ de bénéfice / 1 $", "aucun risque de crédit"], GREEN),
                                                ("CONTRE", ["procès antitrust", "stablecoins et IA", "2 600 postes supprimés"], REDS))):
            x = 60+j*760; T(c, title, x, 150, 'k', 54, cc, 'l')
            for k, it in enumerate(items):
                a = clamp(u*3-k*0.5-j*0.3); T(c, it, x, 260+k*110, 'm', 40, WH, 'l', a)
