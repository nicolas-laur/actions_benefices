from gty import *
NB = ' '
def k1(c):
    background(c, 0); progress(c, .05)
    kicker(c, "2023 · TOUT LE MONDE EN ÉTAIT SÛR")
    searchbar(c, "google est-il fini face à chatgpt", 470)
    # suggestions façon autocomplétion
    for j, s in enumerate(("google est-il fini", "google va-t-il disparaître", "la fin de la recherche en ligne")):
        y = 590+j*78; magnifier(c, 170, y, 26, '9AA3B5'); text(c, s, 210, y, 'm', 34, SUB, 'l')
    text(c, "L'IA DEVAIT", 540, 900, 'k', 110, INK)
    text(c, "LE TUER.", 540, 1030, 'k', 150, RED)
    caption(c, [("En", 0), ("2023,", 0), ("l'IA", 0), ("devait", 0), ("tuer", 0), ("Google.", 0), ("Trois", 0), ("ans", 0), ("plus", 0), ("tard" + NB + "?", 1)], accent=RED)
def k2(c):
    background(c, 2); progress(c, .45)
    searchbar(c, "croissance google cloud 2026", 400, focus=.4)
    card(c, 110, 520, 860, 640, "Google Cloud · chiffre d'affaires")
    text(c, "+82" + NB + "%", 540, 780, 'k', 190, GREEN)
    text(c, "sur un an", 540, 880, 'sb', 32, SUB)
    # barres T2 2025 vs T2 2026
    for i, (v, lab, cc) in enumerate(((13.6, "T2 2025", 'C9D2E3'), (24.8, "T2 2026", GREEN))):
        x = 250+i*330; hh = 140*v/24.8; rr(c, x, 1110-hh, 250, hh, 16); col(c, cc); c.fill()
        text(c, f"{v:.1f} Md$".replace('.', ','), x+125, 1110-hh-30, 'xb', 34, INK); text(c, lab, x+125, 1140, 'm', 26, SUB)
    caption(c, [("Le", 0), ("cloud", 0), ("de", 0), ("Google", 0), ("+82" + NB + "%", 1), ("en", 0), ("un", 0), ("an.", 0)], accent=GREEN)
def k3(c):
    background(c, 4); progress(c, .88)
    searchbar(c, "1000 € dans alphabet il y a 5 ans", 400, focus=.4)
    card(c, 110, 520, 860, 640, None, "résultat · calcul au 9 octobre 2026")
    w1 = tw(c, "≈ ", 'xb', 90); w2 = tw(c, "2" + NB + "680" + NB + "€", 'k', 170); x0 = 540-(w1+w2)/2
    text(c, "≈", x0, 700, 'xb', 90, INK, 'l'); text(c, "2" + NB + "680" + NB + "€", x0+w1, 700, 'k', 170, BLUE, 'l')
    text(c, "2 668 € d'action  +  16 € de dividendes", 540, 830, 'm', 32, INK)
    text(c, "change €/$ inclus · avant impôts et frais", 540, 880, 'l', 26, SUB)
    # mini courbe
    pts = [0, .1, .05, .3, .2, .45, .62, .55, .8, 1.0, .9]
    c.set_line_width(6); c.set_line_join(1)
    for i, v in enumerate(pts): (c.move_to if i == 0 else c.line_to)(200+i*68, 1100-v*150)
    col(c, BLUE); c.stroke()
    chip(c, "×2,68", 540, 1215, GREEN, 40)
    caption(c, [("Tes", 0), ("1" + NB + "000" + NB + "€" + NB + "?", 0), ("≈" + NB + "2" + NB + "680" + NB + "€", 1), ("aujourd'hui.", 0)], y=1380, accent=YELLOW)
for f, n in ((k1, 'g_da_k1_ia'), (k2, 'g_da_k2_cloud'), (k3, 'g_da_k3_reveal')):
    s, c = surface(); f(c); to_img(s).convert('RGB').save(f'{n}.png')
ims = [Image.open(f'{n}.png') for n in ('g_da_k1_ia', 'g_da_k2_cloud', 'g_da_k3_reveal')]
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('sheet.png')
