"""Séquence test du rig v2 (8 s) : entrée en marchant, coucou, il pointe un chiffre en haut, pouce levé, il ramasse une étiquette.
usage : python3 test_rig2.py sortie.mp4 [fps]"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import rig2_proto as rig2
W, H = 1080, 1920; Z = .28
FEET = np.array([1000., rig2.FEET_Y])
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x*x*(3-2*x)
def lerp(a, b, u): return a+(b-a)*u
BG = Image.open(f'{D}/../episodes/2026-10-27_kering/decors/boutique.jpg').convert('RGB')
BG = BG.resize((int(BG.width*1920/BG.height), 1920), Image.LANCZOS); BG = BG.crop(((BG.width-W)//2, 0, (BG.width-W)//2+W, H))
X0, X1, T_WALK = -250., 520., 2.4                   # position écran du centre des pieds
def root_x(t):
    if t < T_WALK: return lerp(X0, X1, t/T_WALK)
    return X1
def mouth_at(t):
    if 2.6 < t < 7.4: return int(abs(math.sin(t*9.3))*2.99+(math.sin(t*3.1) > .6))%4 if math.sin(t*1.7) > -.7 else 0
    return None
def pose(t):
    p = {'bouche': mouth_at(t), 'cligne': (t % 3.1) < .1}
    rest_L, rest_R = rig2.REST['jambes']['G'], rig2.REST['jambes']['D']
    if t < T_WALK+.15:                               # marche : pieds posés au sol pendant l'appui, levés pendant le pas
        v = (X1-X0)/T_WALK/Z; f = 1.9; Lh = v/f/2*.5      # vitesse en px de toile, foulée
        ph = t*f; bob = -18*abs(math.sin(math.pi*2*ph)); legs = {}
        for side, off, base in (('G', 0, rest_L), ('D', .5, rest_R)):
            u = (ph+off) % 1
            if u < .5: dx = lerp(Lh, -Lh, u/.5); lift = 0
            else: w = (u-.5)/.5; dx = lerp(-Lh, Lh, ease(w)); lift = 70*math.sin(math.pi*w)
            k = 1-ease((t-T_WALK)/.15) if t > T_WALK else 1
            legs[side] = (base[0]+dx*k, base[1]-lift*k, (-12*math.sin(math.pi*2*u))*k, 1)
        p['jambes'] = legs; p['corps'] = (0, bob, 3*math.sin(2*math.pi*ph))
        sw = math.sin(2*math.pi*ph)                   # bras qui balancent à l'opposé des jambes
        p['bras'] = {'G': (520-110*sw, 2000, 'poing', None, .45), 'D': (1420+110*sw, 1990, 'poing', None, -.45)}
        return p
    tt = t-T_WALK
    legs = {'G': rest_L, 'D': rest_R}; p['jambes'] = legs
    br = {'G': rig2.REST['bras']['G'], 'D': rig2.REST['bras']['D']}
    if tt < 1.3:                                      # coucou de la main droite
        u = ease(tt/.3); wave = math.sin(tt*14)*120*u
        br['D'] = (lerp(1520, 1600, u)+wave*.4, lerp(1990, 1220, u), 'ouvert', lerp(0, 15, u)+wave*.08, -.35)
    elif tt < 3.0:                                    # il pointe le chiffre en haut à droite
        u = ease((tt-1.3)/.35)
        br['D'] = (lerp(1520, 1700, u), lerp(1990, 1050, u), 'index', None, -.25)
        p['corps'] = (0, 0, -4*u)
    elif tt < 4.0:                                    # pouce levé
        u = ease((tt-3.0)/.25)
        br['D'] = (lerp(1700, 1560, u), lerp(1050, 1600, u), 'pouce', 0, -.5)
        br['G'] = (lerp(430, 560, u), lerp(2010, 2050, u), 'poing', None, .4)
    else:                                             # il se penche, ramasse l'étiquette au sol, puis la brandit
        u = ease((tt-4.0)/.6); up = ease((tt-4.9)/.6)
        p['corps'] = (lerp(0, 40, u)*(1-up), lerp(0, 110, u)*(1-up), lerp(0, 9, u)*(1-up))
        hx = lerp(1520, 1430, u)+lerp(0, 120, up); hy = lerp(1990, 2330, u)*(1-up)+1330*up
        ang = lerp(0, 180, u)*(1-up)                   # gant tourné vers le sol pour saisir, puis redressé
        br['D'] = (hx, hy, 'tenir', ang, -.3)
        a = math.radians(ang); ox, oy = 0, -190         # ouverture du C par rapport au poignet
        grip = (hx+ox*math.cos(a)-oy*math.sin(a), hy+ox*math.sin(a)+oy*math.cos(a))
        p['tag'] = grip if tt > 4.55 else None
    p['bras'] = br
    return p
def tag_img():
    im = Image.new('RGBA', (300, 170), 0); d = ImageDraw.Draw(im)  # agrandie ensuite
    d.rounded_rectangle((0, 0, 299, 169), 26, fill=(200, 55, 45, 255)); d.ellipse((24, 70, 54, 100), fill=(255, 255, 255, 255))
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 78) if os.path.exists('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf') else None
    d.text((80, 30), "−16 %", font=f, fill=(255, 255, 255, 255)); return im
TAG = tag_img().resize((540, 306), Image.LANCZOS)
def frame(t):
    p = pose(t); cv = rig2.draw(p)
    tg = p.pop('tag', None) if 'tag' in p else None
    if tg is not None: cv.alpha_composite(TAG, (int(tg[0]-60), int(tg[1]-TAG.height/2)))
    elif t-T_WALK > 3.9 and t-T_WALK <= 4.55: cv.alpha_composite(TAG, (1370, 2520-TAG.height//2))   # l'étiquette au sol avant qu'il la prenne
    sx = root_x(t); sy = 1665
    ch = cv.resize((int(cv.width*Z), int(cv.height*Z)), Image.LANCZOS)
    out = BG.copy().convert('RGBA'); out.alpha_composite(ch, (int(sx-FEET[0]*Z), int(sy-FEET[1]*Z))) if sx-FEET[0]*Z >= 0 else out.paste(ch, (int(sx-FEET[0]*Z), int(sy-FEET[1]*Z)), ch)
    return out.convert('RGB')
if __name__ == '__main__':
    out = sys.argv[1]; fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(8*fps)): ff.stdin.write(frame(i/fps).tobytes())
    ff.stdin.close(); ff.wait()
