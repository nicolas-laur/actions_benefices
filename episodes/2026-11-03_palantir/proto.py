import sys, numpy as np, cairo
from PIL import Image
sys.path.insert(0, '.')
from dossier import *
LAB = ("ACTIONS_BÉNÉFICES / DOSSIER PLTR", "REC  03.11.2026", "CONFIDENTIEL · NIVEAU 3", "TC ")
def shot(fn, t, mode, name):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    background(c, mode, t); fn(c, t); hud(c, t, mode, LAB)
    s.flush(); im = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).convert('RGB')
    a = grain_layer(np.asarray(im).astype(np.float32), t, 8); Image.fromarray(a.astype(np.uint8)).save(f'prev/{name}.png')
def p1(c, t):   # chiffre choc
    x0, w = text(c, "20 400 €", 540, 620, 'black', 210, WHITE)
    dims(c, x0, 520, x0+w, 720, 1.0, ("×20 DEPUIS 2020", "1 000 € PLACÉS"))
    text(c, "pour 1 000 € placés en", 540, 800, 'serif', 64, RED)
    text(c, "2020", 540, 880, 'black', 64, WHITE)
def p2(c, t):   # décodage
    text(c, scramble("PALANTIR", .55, 4), 540, 560, 'black', 170, INK)
    text(c, "fondée par", 540, 690, 'serif', 72, RED)
    text(c, "PETER THIEL", 540, 790, 'black', 96, INK)
    dot(c, 540, 930, 16)
def p3(c, t):   # cible
    dot(c, 540, 650, 18); target(c, 540, 650, .85, 'dark')
    text(c, "financée par", 540, 880, 'serif', 72, RED); text(c, "LA CIA", 540, 980, 'black', 150, WHITE)
def p4(c, t):   # panneau
    text(c, "COURS DE L'ACTION", 540, 430, 'mono', 30, WHITE, .7, 'c', .1)
    flap_board(c, "$9,50", 540, 560, 120, 170, 1.0); text(c, "↓", 540, 700, 'black', 70, RED)
    flap_board(c, "$184", 540, 840, 140, 190, .7, red_last=True)
def p5(c, t): word_rows(c, ["GÉNIE", "BULLE"], t, 1.0, size=150, cy=820)
def p6(c, t): dot_grid(c, t, 1.0, 'dark', red_k=.6, square_k=.5, rot=.8)
for fn, t, mode, nm in ((p1, 1.0, 'dark', 'a'), (p2, 2.0, 'paper', 'b'), (p3, 3.0, 'dark', 'c'), (p4, 4.0, 'dark', 'd'), (p5, 5.0, 'dark', 'e'), (p6, 6.0, 'dark', 'f')):
    shot(fn, t, mode, nm)
ims = [Image.open(f'prev/{n}.png').resize((360, 640)) for n in 'abcdef']
P = Image.new('RGB', (360*6, 640)); [P.paste(m, (k*360, 0)) for k, m in enumerate(ims)]; P.save('prev/proto.png')
