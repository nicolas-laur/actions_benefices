"""Imprime un journal crédible sur la pose lit_journal (titre « ACTIONS BÉNÉFICES », gros titre, colonnes) -> poses/lit_journal_titre.png.
Chaque page est dessinée à plat puis déformée en perspective sur la page du dessin (coins relevés sur la pose 705×900)."""
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
H0 = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H0, '..', 'fonts')
INK = (52, 36, 28)
def font(n, s): return ImageFont.truetype(f'{F}/{n}', s)
def page(w, h, droite):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); m = 44; ml, mr = (m, 190) if droite else (170, m)   # marges élargies côté gants
    def ctext(t, y, f): b = d.textbbox((0, 0), t, font=f); d.text(((ml+w-mr-(b[2]-b[0]))/2-b[0], y-b[1]), t, font=f, fill=INK)
    def colonnes(y0, y1, x0, x1, n):
        cw = (x1-x0-(n-1)*22)/n
        for k in range(n):
            for y in range(int(y0), int(y1), 26):
                L = cw*(.6 if (y-y0) % 182 == 156 else 1)
                d.line([(x0+k*(cw+22), y), (x0+k*(cw+22)+L, y)], fill=INK+(110,), width=7)
    if droite:                                                  # la une : titre du journal
        ctext("ACTIONS", 40, font('AlfaSlabOne-Regular.ttf', 112)); ctext("BÉNÉFICES", 170, font('AlfaSlabOne-Regular.ttf', 84))
        d.line([(ml, 300), (w-mr, 300)], fill=INK, width=6); d.line([(ml, 312), (w-mr, 312)], fill=INK, width=2)
        ctext("SPÉCIAL MARCHÉS", 336, font('InterDisplay-Black.otf', 50))
        colonnes(430, h-40, ml, w-mr, 3)
    else:                                                       # page de gauche : un graphique et des colonnes
        ctext("LA BOURSE", 46, font('AlfaSlabOne-Regular.ttf', 84))
        d.line([(ml, 160), (w-mr, 160)], fill=INK, width=4)
        x0, y0, x1, y1 = ml+10, 200, (ml+w-mr)//2+10, 430
        d.rectangle([x0, y0, x1, y1], outline=INK, width=4)
        pts = [(x0+12+i*(x1-x0-24)/7, y1-30-v*(y1-y0-60)) for i, v in enumerate([.2, .35, .3, .55, .45, .7, .6, .9])]
        d.line(pts, fill=(200, 60, 50), width=9, joint='curve')
        colonnes(200, 430, (ml+w-mr)//2+40, w-mr, 1); colonnes(470, h-40, ml, w-mr, 2)
    return im
def warp(cv, pg, quad):
    h, w = pg.shape[:2]; M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    return cv2.warpPerspective(pg, M, (cv.shape[1], cv.shape[0]), flags=cv2.INTER_AREA)
POSES = {   # pose source : (sortie, page de droite = la une, page de gauche), coins dans l'ordre haut gauche, haut droit, bas droit, bas gauche
 'lit_journal':    ('lit_journal_titre',    [(360, 432), (690, 330), (628, 645), (350, 722)], [(22, 318), (334, 432), (338, 722), (78, 632)]),
 'lit_journal_v2': ('lit_journal_v2_titre', [(268, 418), (608, 338), (612, 664), (282, 718)], [(20, 300), (244, 416), (262, 712), (74, 624)]),
}
def imprime(src, dst, R, L, mr_left=170):
    im = np.asarray(Image.open(f'{H0}/poses/{src}.png').convert('RGBA')).astype(np.float32)
    paper = ((im[..., 0] > 200) & (im[..., 1] > 190) & (im[..., 2] > 180) & (im[..., 3] > 200)).astype(np.float32)
    paper = cv2.erode(paper, np.ones((9, 9), np.uint8))       # rester à distance du trait de contour et du pli
    out = im.copy()
    for quad, droite in ((R, True), (L, False)):
        pg = np.asarray(page(1000, 900, droite)).astype(np.float32)
        wp = warp(im, pg, quad); a = wp[..., 3:4]/255*paper[..., None]
        out[..., :3] = out[..., :3]*(1-a)+wp[..., :3]*a
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(f'{H0}/poses/{dst}.png'); print(dst)
if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or POSES): imprime(k, *POSES[k])
