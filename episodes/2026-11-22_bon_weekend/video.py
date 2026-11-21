"""Mini vidéo « Bon week-end » (15 s, sans voix) : le résumé de la semaine du 16 au 21/11 sur le décor du salon (Buy, borrow, die),
Mister Coin qui se balance dans son rocking chair, les contenus de la semaine qui apparaissent un par un sur un panneau de verre, un mystère pour la suite.
Décor : decors/salon_hd.mp4 (decor_salon de buy_borrow_die agrandi en 1080×1920, ralenti ×1,55 et interpolé en 30 i/s, commande dans README ci-dessous).
usage : python3 video.py [apercu]   (apercu : images clés dans prev/)"""
import sys, os, math, subprocess
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

FPS, DUR = 30, 15.0
ROWS = [('💰', "Vivre de ses dividendes", "600 k€ à 2 M€"),
        ('🎟️', "Le Loto toute ta vie", "14 k€ joués"),
        ('📖', "Le lexique de la bourse", "9 sigles"),
        ('🎮', "GTA 6 ou Take-Two ?", "×13 depuis 2013"),
        ('📰', "Les News de la semaine", "Dow −6,2" + NB + "%"),
        ('🔍', "Que vaut Nvidia ?", "PER 13,5"),
        ('🤫', "Bientôt…", "un secret de milliardaires")]
T_ROW = [1.0+1.2*i for i in range(len(ROWS))]           # apparition de chaque ligne
PW, RH = 820, 88; PH = RH*len(ROWS)+30; PCX, PY0 = 540, 430; PCY = PY0+PH/2

def assombrir(a):
    y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 200, 520, 1100, 1450, H], [.55, .45, .40, .40, .45, .55])
    return (a.astype(np.float32)*(1-dark)).astype(np.uint8)

def decor_frames():
    cap = cv2.VideoCapture(f'{D}/decors/salon_hd.mp4'); out = []
    while True:
        ok, f = cap.read()
        if not ok: break
        out.append(assombrir(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    return out

def panneau(base, k):
    """panneau de verre avec les k premières lignes, rendu sur l'image de décor base (RGB)"""
    cv = Image.fromarray(base).convert('RGBA')
    def dr(c, w, h):
        for j, (_, t, v) in enumerate(ROWS[:k]):
            y = 15+RH*j+RH/2; myst = j == len(ROWS)-1
            if j: c.move_to(30, 15+RH*j); c.line_to(w-30, 15+RH*j); c.set_line_width(1.2); col(c, WHITE, .12); c.stroke()
            text(c, t, 100, y, 'xb', 31, GD2 if myst else WHITE, 'l', .97)
            text(c, v, w-34, y, 'sb' if myst else 'xb', 27 if myst else 29, GD2 if myst else GD, 'r', .95)
    tp(cv, PW, PH, dr, PCX, PCY, 'or', rx=.04, frost=16, dim=.55)
    for j, (e, _, _) in enumerate(ROWS[:k]): put_emoji(cv, e, PCX-PW/2+58, PY0+15+RH*j+RH/2, 46)
    return np.asarray(cv.convert('RGB'))

def calque(fn):
    im = Image.new('RGBA', (W, H), 0); s, c = surface(); fn(im, c); im2 = to_img(s); im2.alpha_composite(im); return im2

def titre(im, c):
    glow_text(im, "BON WEEK-END !", 540, 255, 118, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, reflect=False)
    text(c, "Ta semaine sur Actions_Bénéfices", 540, 365, 'sb', 32, ICE, 'c', .92)
def abonne(im, c):
    w = gpill(c, "ABONNE-TOI POUR LA SUITE", 540, 1150, GD, 30); put_emoji(im, '🔔', 540+w/2+30, 1148, 40)

def main(apercu=False):
    frames = decor_frames(); n = int(FPS*DUR); F0 = frames[0]
    R = [panneau(F0, k) for k in range(len(ROWS)+1)]
    diff = np.abs(R[-1].astype(int)-F0.astype(int)).max(2) > 6
    m = cv2.morphologyEx(diff.astype(np.uint8)*255, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    ys, xs = np.nonzero(m); box = (xs.min(), ys.min(), xs.max(), ys.max())
    mask = np.zeros((H, W), np.float32); mask[box[1]:box[3]+1, box[0]:box[2]+1] = cv2.dilate(m, np.ones((5, 5), np.uint8))[box[1]:box[3]+1, box[0]:box[2]+1]/255
    mask = cv2.GaussianBlur(mask, (5, 5), 0)[..., None]
    L_titre = np.asarray(calque(titre), np.float32)/255; L_ab = np.asarray(calque(abonne), np.float32)/255
    coin_im = Image.open(f'{D}/coin/rocking_chair.png').convert('RGBA'); ch = 300; coin_im = coin_im.resize((int(coin_im.width*ch/coin_im.height), ch), Image.LANCZOS)
    def bulle_l(t):
        s, c = surface(); bulle_pres(c, "Bon week-end !", (60, 1500-ch, 60+coin_im.width, 1500), 34, .28); return np.asarray(to_img(s), np.float32)/255
    L_bul = bulle_l(0)
    ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else x*x*(3-2*x)
    def over(img, L, a):
        if a <= 0: return img
        al = L[..., 3:4]*a; return img*(1-al)+L[..., :3]*255*al
    def frame(i):
        t = i/FPS; d = frames[min(i, len(frames)-1)].astype(np.float32)
        k = sum(1 for tr in T_ROW if t >= tr); f = ease((t-T_ROW[k-1])/.35) if k else 0
        pan = R[k].astype(np.float32) if k == 0 else R[k-1]*(1-f)+R[k]*f
        a_pan = ease((t-.5)/.4)
        img = d*(1-mask*a_pan)+pan*mask*a_pan
        img = over(img, L_titre, ease(t/.4))
        img = over(img, L_ab, ease((t-9.8)/.4))
        pil_ = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert('RGBA')
        ang = 3.2*math.sin(2*math.pi*t/2.4)                              # balancement lent du rocking chair
        r = coin_im.rotate(ang, resample=Image.BICUBIC, expand=True, center=(coin_im.width*.5, coin_im.height*.98))
        sh = surface(); c = sh[1]; c.save(); c.translate(60+coin_im.width/2, 1496); c.scale(coin_im.width*.45, 16)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .6); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore()
        pil_.alpha_composite(to_img(sh[0])); pil_.alpha_composite(r, (int(60+coin_im.width/2-r.width/2), int(1500-ch-(r.height-ch)/2)))
        img = np.asarray(pil_.convert('RGB'), np.float32)
        img = over(img, L_bul, ease((t-11.0)/.35))
        img *= min(1, (DUR-t)/.4) if t > DUR-.4 else 1
        return img.clip(0, 255).astype(np.uint8)
    os.makedirs(f'{D}/prev', exist_ok=True); os.makedirs(f'{D}/out', exist_ok=True)
    if apercu:
        ims = [Image.fromarray(frame(int(t*FPS))).resize((360, 640)) for t in (0.3, 2.5, 5.0, 8.0, 9.9, 11.5, 13.5, 14.9)]
        P = Image.new('RGB', (360*4, 640*2)); [P.paste(im, ((j % 4)*360, (j//4)*640)) for j, im in enumerate(ims)]; P.save(f'{D}/prev/images_cles.png'); print('ok'); return
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest', '-c:v', 'libx264', '-crf', '15', '-maxrate', '16M', '-bufsize', '32M',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', f'{D}/out/bon_weekend.mp4'], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); Image.fromarray(frame(int(12.5*FPS))).save(f'{D}/out/couverture.png'); print('ok')

if __name__ == '__main__': main('apercu' in sys.argv)
