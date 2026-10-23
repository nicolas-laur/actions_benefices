from tdy import *
NB = ' '
def k1(c):
    proj = road(c, 0.3); trajectory(c, proj); progress(c, .05); hud(c, 0.3)
    text(c, "LE PARADOXE", 540, 450, 'k', 96, INK)
    text(c, "TESLA", 540, 560, 'k', 150, RED, glow=1)
    # deux « objets » détectés sur la route
    bracket(c, 120, 720, 470, 200, CYAN); tag(c, "VALORISATION 99 %", 120, 700, CYAN)
    text(c, "1 490 MD$", 355, 820, 'k', 76, INK)
    bracket(c, 640, 860, 330, 150, RED); tag(c, "BÉNÉFICE 12 MOIS", 640, 840, RED, ink='FFFFFF')
    text(c, "3,8 MD$", 805, 935, 'k', 58, INK)
    scanlines(c)
    caption(c, [("Tesla", 0), ("gagne", 0), ("de", 0), ("moins", 0), ("en", 0), ("moins…", 0), ("et", 0), ("vaut", 0), ("1" + NB + "490" + NB + "milliards" + NB + "$.", 1)])
def k2(c):
    proj = road(c, 1.1, tint='6A1A1A'); trajectory(c, proj, RED, .5, curve=-0.6); progress(c, .45); hud(c, 1.1, 46, label="ALERTE · RALENTISSEMENT", color=RED)
    bracket(c, 150, 470, 780, 420, RED, lw=5)
    tag(c, "OBSTACLE DÉTECTÉ", 150, 450, RED, ink='FFFFFF')
    warn(c, 540, 560, 80)
    text(c, "PER ≈ 390", 540, 710, 'k', 140, INK, glow=1)
    text(c, "390 ans de bénéfices actuels pour rembourser son prix", 540, 820, 'm', 28, SUB)
    scanlines(c)
    caption(c, [("Son", 0), ("action", 0), ("coûte", 0), ("≈" + NB + "390" + NB + "fois", 1), ("ses", 0), ("bénéfices.", 0)])
def k3(c):
    proj = road(c, 2.0); trajectory(c, proj, CYAN, .7, curve=0.4); progress(c, .88); hud(c, 2.0, 112, label="ARRIVÉE À DESTINATION", color=GREEN)
    text(c, "TES 1 000 € IL Y A 5 ANS", 540, 395, 'mono', 26, SUB, 'c', 1, 4)
    bracket(c, 140, 490, 800, 300, GREEN, lw=5); tag(c, "VALEUR ESTIMÉE", 140, 470, GREEN)
    w1 = tw(c, "≈ ", 'xb', 80); w2 = tw(c, "1" + NB + "445" + NB + "€", 'k', 160); x0 = 540-(w1+w2)/2
    text(c, "≈", x0, 630, 'xb', 80, INK, 'l'); text(c, "1" + NB + "445" + NB + "€", x0+w1, 630, 'k', 160, INK, 'l', glow=1)
    text(c, "sans dividende · change €/$ inclus · avant frais", 540, 740, 'mono', 20, SUB)
    tag(c, "×1,45", 540+70, 860, GREEN, 40, align='r')
    scanlines(c)
    caption(c, [("Tes", 0), ("1" + NB + "000" + NB + "€" + NB + "?", 0), ("≈" + NB + "1" + NB + "445" + NB + "€.", 1), ("Le", 0), ("rêve", 0), ("coûte", 0), ("cher.", 0)], accent=GREEN)
for f, n in ((k1, 't_da_k1_paradoxe'), (k2, 't_da_k2_per'), (k3, 't_da_k3_reveal')):
    s, c = surface(); f(c); to_img(s).convert('RGB').save(f'{n}.png')
ims = [Image.open(f'{n}.png') for n in ('t_da_k1_paradoxe', 't_da_k2_per', 't_da_k3_reveal')]
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('sheet.png')
