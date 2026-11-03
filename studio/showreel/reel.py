"""Showreel Actions_Benefices (30 s, 9:16) pour démarcher des entreprises : intro, 14 extraits des vidéos publiées, chacun avec
une étiquette qui nomme le savoir-faire, coupes rythmées (coup de zoom + éclair), conclusion avec contact.
usage : python3 reel.py info | png t1 t2 … | render"""
import sys, os, math, subprocess, functools
import numpy as np, cairo, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from bglass import glow_text
FPS = 60
EP = f'{ROOT}/episodes'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
GD = 'FFC24A'; ICE = 'E8EEF8'; INK = '0B0E14'; WHITE = 'FFFFFF'; CY = '35D6FF'
CLIPS = [  # (vidéo, début, durée, étiquette)
    ('2026-11-04_iphone_actions/out/2026-11-04_iphone_actions.mp4', 0.35, 2.0, "FAUSSE 3D, SANS LOGICIEL 3D"),
    ('2026-11-03_palantir/out/2026-11-03_palantir.mp4', 2.0, 1.6, "VIDÉO IA INTÉGRÉE AU MONTAGE"),
    ('2026-10-29_carburant/out/2026-10-29_carburant_v5.mp4', 4.0, 1.6, "OBJETS DU RÉEL ANIMÉS"),
    ('2026-11-03_palantir/out/2026-11-03_palantir.mp4', 14.6, 1.6, "TYPOGRAPHIE CINÉTIQUE"),
    ('2026-10-28_hermes/out/2026-10-28_hermes_v5.mp4', 27.0, 1.6, "DÉCORS SUR MESURE"),
    ('2026-11-02_etf_msci_world/out/2026-11-02_etf_msci_world.mp4', 5.4, 1.8, "DONNÉES RÉELLES, PAYS PAR PAYS"),
    ('2026-11-04_iphone_actions/out/2026-11-04_iphone_actions.mp4', 3.85, 1.6, "IMPACTS CALÉS SUR LA VOIX"),
    ('2026-11-03_palantir/out/2026-11-03_palantir.mp4', 20.6, 1.6, "RÉSULTATS PUBLIÉS LA VEILLE AU SOIR"),
    ('2026-10-27_kering/out/2026-10-27_kering_v4.mp4', 21.4, 1.6, "UNE MASCOTTE QUI VIT"),
    ('2026-11-02_etf_msci_world/out/2026-11-02_etf_msci_world.mp4', 22.4, 1.8, "GRAPHIQUES CHIFFRÉS ET SOURCÉS"),
    ('2026-11-04_iphone_actions/out/2026-11-04_iphone_actions.mp4', 6.75, 1.4, "UNE HISTOIRE EN 15 SECONDES"),
    ('2026-11-03_palantir/out/2026-11-03_palantir.mp4', 32.2, 1.7, "PANNEAU D'AÉROPORT"),
    ('2026-11-04_iphone_actions/out/2026-11-04_iphone_actions.mp4', 11.25, 2.2, "CAMÉRA EMBARQUÉE SUR LA COURBE"),
    ('2026-11-03_palantir/out/2026-11-03_palantir.mp4', 38.2, 1.6, "UNE FIN QUI FAIT COMMENTER"),
]
INTRO, OUTRO = 2.5, 3.8
STARTS = []; _t = INTRO
for cl in CLIPS: STARTS.append(_t); _t += cl[2]
DUR = _t+OUTRO
VOICE = None
def events():
    ev = [(0.0, 'whoosh'), (.35, 'impact'), (.9, 'swish'), (1.4, 'pop')]
    ev += [(s, 'impact' if i % 3 == 0 else 'swish') for i, s in enumerate(STARTS)]
    ev += [(STARTS[-1]+CLIPS[-1][2], 'whoosh'), (DUR-OUTRO+.25, 'impact'), (DUR-OUTRO+1.1, 'pop'), (DUR-OUTRO+1.8, 'glint')]
    return sorted(ev)

@functools.lru_cache(maxsize=1)
def bg():
    s, c = surface(); g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, .012, .016, .03); g.add_color_stop_rgb(1, .04, .05, .08); c.set_source(g); c.paint()
    r = cairo.RadialGradient(540, 760, 0, 540, 760, 900); r.add_color_stop_rgba(0, 1, .76, .29, .12); r.add_color_stop_rgba(1, 1, .76, .29, 0); c.set_source(r); c.paint()
    return to_img(s)
def card_intro(t):
    cv = bg().copy(); s, c = surface()
    c.push_group(); logo_symbol(c, 540, 560, 70*back(t/.5)); c.pop_group_to_source(); c.paint_with_alpha(ease(t/.2))
    text(c, "ACTIONS_BENEFICES", 540, 680, 'mono', 30, ICE, 'c', .8*ease((t-.3)/.3), 10)
    cv.alpha_composite(to_img(s)); s, c = surface()
    glow_text(cv, "VIDÉOS FINANCE", 540, 820, 112, top='FFFFFF', bottom='CFF4FF', glow=CY, ga=.55, a=ease((t-.35)/.12), scale=lerp(1.6, 1, back((t-.35)/.3, 1.6)), reflect=False)
    glow_text(cv, "EN MOTION DESIGN", 540, 950, 112, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=ease((t-.6)/.12), scale=lerp(1.6, 1, back((t-.6)/.3, 1.6)), reflect=False)
    for i, w in enumerate(("CHIFFRES RÉELS", "SOURCES VÉRIFIÉES", "FORMAT 9:16")):
        k = t-1.0-i*.18
        if k > 0:
            x = 540+(i-1)*300; wd = tw(c, w, 'xb', 24, 2)+40
            rr(c, x-wd/2, 1080-24, wd, 48, 24); col(c, GD if i == 1 else ICE, ease(k/.2)); c.fill(); text(c, w, x, 1080, 'xb', 24, INK, 'c', ease(k/.2), 2)
    cv.alpha_composite(to_img(s)); return cv
def card_outro(t):
    cv = bg().copy(); s, c = surface()
    glow_text(cv, "UNE VIDÉO", 540, 640, 130, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.65, a=ease((t-.25)/.12), scale=lerp(1.6, 1, back((t-.25)/.3, 1.6)), reflect=False)
    glow_text(cv, "POUR VOTRE MARQUE ?", 540, 780, 92, top='FFFFFF', bottom='CFF4FF', glow=CY, ga=.55, a=ease((t-.5)/.12), scale=lerp(1.6, 1, back((t-.5)/.3, 1.6)), reflect=False)
    a = ease((t-1.1)/.3)
    text(c, "De la donnée brute à la vidéo publiée :", 540, 930, 'b', 36, ICE, 'c', .9*a)
    text(c, "recherche, script, motion design, son.", 540, 980, 'b', 36, ICE, 'c', .9*a)
    a2 = ease((t-1.8)/.3)
    c.push_group(); logo_symbol(c, 380, 1120, 46); c.pop_group_to_source(); c.paint_with_alpha(a2)
    text(c, "Nicolas Laur", 420, 1104, 'xb', 40, WHITE, 'l', a2)
    text(c, "@actions_bnfices · TikTok, YouTube, Instagram", 420, 1150, 'sb', 26, ICE, 'l', .75*a2)
    cv.alpha_composite(to_img(s)); return cv
def label(cv, s_, k, i):
    s, c = surface(); a = ease(k/.15)*(1-ease((k-1.25)/.2)) if k < 1.6 else 0
    if a <= 0: return
    n = int(len(s_)*clamp(k/.35)); txt = s_[:n]
    num = f"{i+1:02d}"; w = tw(c, num+"   "+s_, 'xb', 28, 2)+56; x0 = 540-w/2; y = 1800
    rr(c, x0, y-34, w, 68, 34); col(c, INK, .82*a); c.fill_preserve(); c.set_line_width(2); col(c, GD, .9*a); c.stroke()
    text(c, num, x0+28, y, 'xb', 28, GD, 'l', a, 2); text(c, txt, x0+28+tw(c, num+"   ", 'xb', 28, 2), y, 'xb', 28, WHITE, 'l', a, 2)
    cv.alpha_composite(to_img(s))
class Clip:
    def __init__(self, path, t0, d):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(t0), '-i', f'{EP}/{path}', '-t', str(d+.2), '-r', str(FPS), '-vf', f'scale={W}:{H}',
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE); self.last = None
    def next(self):
        b = self.p.stdout.read(W*H*3)
        if len(b) == W*H*3: self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        return self.last
    def close(self): self.p.kill()
def punch(img, z, blur=0):
    if abs(z-1) > 1e-3:
        M = cv2.getRotationMatrix2D((W/2, H/2), 0, z); img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if blur > 0: img = cv2.GaussianBlur(img, (0, 0), blur)
    return img
def clip_frame(fr, k, d, i):
    """coup de zoom à l'entrée, léger zoom avant + flou à la sortie, éclair sur la coupe"""
    z = lerp(1.14, 1.0, back(k/.22, 1.2)) if k < .22 else 1.0
    ko = d-k
    if ko < .12: z = lerp(1.0, 1.07, 1-ko/.12)
    img = punch(fr, z, 6*(1-ko/.12) if ko < .12 else 0).astype(np.float32)
    if k < .08: img = img*(1-.45*(1-k/.08))+255*.45*(1-k/.08)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
def frames():
    """générateur des images du showreel, dans l'ordre"""
    n_in = int(INTRO*FPS)
    for f in range(n_in): yield finish(card_intro(f/FPS), f/FPS, 2.0)
    for i, (path, t0, d, lab) in enumerate(CLIPS):
        cl = Clip(path, t0, d); n = int(round(d*FPS))
        for f in range(n):
            k = f/FPS; fr = cl.next(); im = clip_frame(fr, k, d, i); label(im, lab, k, i); yield im.convert('RGB')
        cl.close()
    for f in range(int(round(OUTRO*FPS))): yield finish(card_outro(f/FPS), f/FPS, 2.0)
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        want = [float(x) for x in sys.argv[2:]]; os.makedirs(f'{D}/prev', exist_ok=True)
        for idx, im in enumerate(frames()):
            t = idx/FPS
            for w_ in want:
                if abs(t-w_) < .5/FPS: im.convert('RGB').save(f'{D}/prev/p_{w_}.png')
            if t > max(want): break
        return
    tmp = f'{D}/reel_video.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for im in frames(): ff.stdin.write(im.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', f'{D}/mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', f'{D}/showreel_actions_benefices.mp4'], check=True)
    os.remove(tmp); print('ok', DUR)
if __name__ == '__main__': main()
