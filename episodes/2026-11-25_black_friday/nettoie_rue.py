"""Efface les pseudo-lettres des enseignes du décor de la rue (Gemini), en suivant le travelling avant de la caméra.
Zones définies sur l'image 0 (720×1280), reportées sur chaque image par homographie (points ORB de la façade, voitures exclues),
puis lettres claires détectées dans chaque zone et effacées par inpainting (l'enseigne garde sa forme et sa couleur).
python3 nettoie_rue.py   (decors/decor_rue_src.mp4 -> decors/decor_rue.mp4)"""
import os, subprocess, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f'{D}/decors/decor_rue_src.mp4', f'{D}/decors/decor_rue.mp4'
# (x0, y0, x1, y1, seuil de clarté au-dessus de la médiane locale)
ZONES = [(612, 300, 720, 560, -1),      # enseigne verticale bordeaux (en saillie : parallaxe, zone large, lettres repérées par leur fond bordeaux)
         (548, 580, 656, 634, 22),      # panneau au-dessus de la vitrine droite
         (108, 578, 192, 630, 22),      # panneau au-dessus de la vitrine gauche
         (668, 598, 720, 630, 14),      # enseigne pâle de l'immeuble de droite
         (0, 584, 34, 612, 14)]         # enseigne pâle de l'immeuble de gauche
orb = cv2.ORB_create(3000)
def feats(g):
    m = np.zeros_like(g); m[:760] = 255; return orb.detectAndCompute(g, m)
def main():
    if not os.path.exists(SRC): os.replace(OUT, SRC)
    cap = cv2.VideoCapture(SRC); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    k0, d0 = feats(cv2.cvtColor(fr[0], cv2.COLOR_BGR2GRAY)); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '720x1280', '-r', '24', '-i', '-',
                           '-c:v', 'libx264', '-crf', '10', '-preset', 'slow', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
    Hp = np.eye(3)
    for i, f in enumerate(fr):
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        if i:
            k1, d1 = feats(g); m = sorted(bf.match(d0, d1), key=lambda x: x.distance)[:600]
            if len(m) > 20:
                Hn, _ = cv2.findHomography(np.float32([k0[x.queryIdx].pt for x in m]), np.float32([k1[x.trainIdx].pt for x in m]), cv2.RANSAC, 3.0)
                if Hn is not None: Hp = Hn
        mask = np.zeros(g.shape, np.uint8)
        for (x0, y0, x1, y1, thr) in ZONES:
            poly = cv2.perspectiveTransform(np.float32([[[x0, y0]], [[x1, y0]], [[x1, y1]], [[x0, y1]]]), Hp).astype(np.int32)
            zm = np.zeros(g.shape, np.uint8); cv2.fillConvexPoly(zm, poly, 255)
            if zm.sum() == 0: continue
            if thr < 0:
                b, gg, r = [f[..., j].astype(np.int16) for j in range(3)]
                maroon = ((r-gg > 28) & (r < 115) & (b < r)).astype(np.uint8); near = cv2.dilate(maroon, np.ones((9, 9), np.uint8)) > 0
                mask |= ((r > 120) & (r < 205) & near & (zm > 0)).astype(np.uint8)*255; continue
            med = np.median(g[zm > 0]); mask |= ((g.astype(np.int16) > med+thr) & (zm > 0)).astype(np.uint8)*255
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
        out = cv2.inpaint(f, mask, 5, cv2.INPAINT_TELEA) if mask.any() else f
        ff.stdin.write(out.tobytes())
    ff.stdin.close(); ff.wait(); print('ok', len(fr))
if __name__ == '__main__': main()
