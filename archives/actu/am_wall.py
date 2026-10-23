"""Actu de la semaine : Netflix, Tesla, Meta. Plateau TV (vidéo générée, ralentie), mur d'écrans suivi en perspective
(vignettes de nos vidéos précédentes), cartes en verre au premier plan.
usage : python am.py png t1 t2 ... | python am.py seg out.mp4 f0 f1 | python am.py info"""
import sys, math, re, subprocess, os, functools
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/meta')
from bglass import *
FPS = 60; NB = ' '
RD = 'FF4057'; AMB = 'FFC24A'; GR = '3FE08A'; CY = '35D6FF'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage (voix 40,4 s) ----------
T = dict(intro=0.0, m5=3.5, trois=5.75, decu=7.9, hesite=8.8, rassure=9.9,
         nf=11.1, nf_ca=12.5, nf_pub=14.6, nf_job=16.45, nf_yr=17.85,
         ts=21.2, ts_ca=22.5, ts_ben=25.55, ts_cab=27.95,
         mt=31.25, mt_ca=32.55, mt_26=34.9, mt_up=36.75,
         toi=38.6, achete=39.25, end=41.6)
DUR = T['end']
CAPS = [(0.0, "Bonjour à toi et bienvenue dans l'actualité de la semaine !"), (T['m5'], "[Moins 5 %] pour Netflix."), (T['trois'], "Trois géants ont publié leurs résultats :"),
        (T['decu'], "un a [déçu],"), (T['hesite'], "un a [hésité],"), (T['rassure'], "un a [rassuré]."),
        (T['nf'], "Netflix [déçoit] :"), (T['nf_ca'], "chiffre d'affaires en hausse de [12 %],"), (T['nf_pub'], "mais [moins de publicité] que prévu"), (T['nf_job'], "et [1 000 postes] supprimés."),
        (T['nf_yr'], "L'action a perdu [près de la moitié] de sa valeur en un an."),
        (T['ts'], "Tesla [hésite] :"), (T['ts_ca'], "[28 milliards] de dollars de ventes, stables sur un an,"), (T['ts_ben'], "mais un bénéfice en chute de [43 %]."),
        (T['ts_cab'], "Tesla promet ses premiers [Cybercab] avant la fin de l'année."),
        (T['mt'], "Meta [rassure] :"), (T['mt_ca'], "[64,6 milliards] de dollars,"), (T['mt_26'], "[+26 %] en un an."), (T['mt_up'], "L'action a [grimpé] dès l'annonce."),
        (T['toi'], "Et toi,"), (T['achete'], "lequel tu [achètes] ?")]
HL = {T['m5']: RD, T['decu']: RD, T['hesite']: AMB, T['rassure']: GR, T['nf']: RD, T['nf_ca']: GR, T['nf_pub']: RD, T['nf_job']: RD, T['nf_yr']: RD,
      T['ts']: AMB, T['ts_ca']: AMB, T['ts_ben']: RD, T['ts_cab']: AMB, T['mt']: GR, T['mt_ca']: GR, T['mt_26']: GR, T['mt_up']: GR, T['achete']: GR}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1720, size=46, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 860: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK if hl in (GR, AMB, CY) else WHITE, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- plateau + mur d'écrans suivi ----------
D = '/home/claude/actu'
Q0 = np.float32([[252, 568], [700, 560], [700, 898], [252, 903]])      # panneau gauche du mur (image 0) : plan unique, suivi par ses jointures
POLY0 = np.float32([[200, 430], [1080, 360], [1080, 900], [200, 905]])
WW, WH = 1360, 1000
@functools.lru_cache(maxsize=1)
def Hs():
    p = f'{D}/wallH.npy'
    return np.load(p) if os.path.exists(p) else None
def nbg(): return len([f for f in os.listdir(f'{D}/bg30') if f.endswith('.jpg')])
@functools.lru_cache(maxsize=4)
def bg_img(i):
    return cv2.cvtColor(cv2.imread(f'{D}/bg30/{i:04d}.jpg'), cv2.COLOR_BGR2RGB)
@functools.lru_cache(maxsize=200)
def clip(name, k):
    fs = sorted(os.listdir(f'{D}/clips/{name}')); f = fs[k % len(fs)]
    return Image.open(f'{D}/clips/{name}/{f}').convert('RGB')
def wall_quad(i):
    H = Hs()
    if H is None: return Q0
    return cv2.perspectiveTransform(Q0[None], H[min(i, len(H)-1)])[0]
CO = {'NETFLIX': ('netflix', RD, "DÉÇOIT", "14 OCT."), 'TESLA': ('tesla', AMB, "HÉSITE", "13 OCT."), 'META': ('meta', GR, "RASSURE", "19 OCT.")}
def wall_content(t):
    s, c = surf(WW, WH)
    def pill_(c, s_, x, y, colr, size, a):
        w = tw(c, s_, 'xb', size, 2)+56; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s_, x, y, 'xb', size, INK, 'c', a, 2)
    def tile(name, x, y, w, h, a, verdict_on, num=None):
        key, colr, verdict, _ = CO[name]
        rr(c, x, y, w, h, 26); col(c, '000000', .5*a); c.fill(); rr(c, x, y, w, h, 26); c.set_line_width(5); col(c, colr if verdict_on else 'FFFFFF', .85*a); c.stroke()
        text(c, name, x+w/2, y+h*.45, 'a', 88, WHITE, 'c', a)
        if verdict_on: pill_(c, verdict, x+w/2, y+h*.72, colr, 38, a)
        if num: text(c, num, x+40, y+70, 'a', 70, AMB, 'c', a)
    if t < T['m5']-.2:
        a = ease((t-.2)/.5)
        text(c, "L'ACTU", WW/2, 330, 'a', 220, WHITE, 'c', a); text(c, "DE LA SEMAINE", WW/2, 500, 'a', 130, WHITE, 'c', a)
        text(c, "RÉSULTATS DU 3E TRIMESTRE 2026", WW/2, 620, 'xb', 44, CY, 'c', a, 4)
        c.push_group(); logo_symbol(c, WW/2-200, 760, 50); c.pop_group_to_source(); c.paint_with_alpha(a); text(c, "Actions_Benefices", WW/2-160, 760, 'b', 46, WHITE, 'l', a)
    elif t < T['nf']-.2 or t >= T['toi']-.2:
        cta = t >= T['toi']-.2
        for j, (name, k_) in enumerate((('NETFLIX', 'decu'), ('TESLA', 'hesite'), ('META', 'rassure'))):
            a = ease((t-T['m5']-.1-j*.15)/.4) if not cta else ease((t-T['toi']+.2-j*.1)/.4)
            tile(name, 30+j*440, 150, 420, 560, a, t >= T[k_], str(j+1) if cta else None)
        if cta: text(c, "RÉPONDS 1, 2 OU 3", WW/2, 830, 'a', 90, WHITE, 'c', ease((t-T['achete'])/.4))
        else: text(c, "3 GÉANTS · 3 RÉSULTATS", WW/2, 830, 'a', 80, WHITE, 'c', ease((t-T['trois'])/.4))
    else:
        name = 'NETFLIX' if t < T['ts']-.2 else ('TESLA' if t < T['mt']-.2 else 'META')
        key, colr, verdict, date = CO[name]
        t0 = {'NETFLIX': T['nf'], 'TESLA': T['ts'], 'META': T['mt']}[name]; a = ease((t-t0+.2)/.4)
        k = int(max(0, t-t0)*15); im = clip(key, k).resize((450, 800), Image.BICUBIC)
        arr = np.asarray(im.convert('RGBA'), np.uint8).copy(); arr[..., [0, 2]] = arr[..., [2, 0]]
        isurf = cairo.ImageSurface.create_for_data(bytearray(arr.tobytes()), cairo.FORMAT_ARGB32, 450, 800)
        c.save(); rr(c, 50, 100, 450, 800, 26); c.clip(); c.set_source_surface(isurf, 50, 100); c.paint_with_alpha(a); c.restore()
        rr(c, 50, 100, 450, 800, 26); c.set_line_width(5); col(c, colr, a); c.stroke()
        text(c, "DÉJÀ SUR", 560, 200, 'xb', 44, ICE, 'l', a, 3); text(c, f"LA CHAÎNE · {date}", 560, 260, 'xb', 44, ICE, 'l', a, 3)
        text(c, name, 560, 470, 'a', 170 if name != 'NETFLIX' else 150, WHITE, 'l', a)
        w = tw(c, verdict, 'xb', 58, 2)+80; rr(c, 560, 560, w, 104, 52); col(c, colr, a); c.fill(); text(c, verdict, 560+w/2, 613, 'xb', 58, INK, 'c', a, 2)
        if name == 'META':
            u = a*ease((t-T['mt_up'])/.4); text(c, "LUNDI, ON TE", 560, 760, 'xb', 40, ICE, 'l', u, 2); text(c, "DEMANDAIT : TU ACHÈTES ?", 560, 812, 'xb', 40, ICE, 'l', u, 2)
    return pil(s)
def background(t):
    n = nbg(); i = min(n-1, int(t*30)) if n else 0
    base = bg_img(i).astype(np.float32)
    # mur : contenu projeté en perspective, mélangé en « écran » (lumière ajoutée)
    wc = np.asarray(wall_content(t), np.float32)
    q = wall_quad(i); M = cv2.getPerspectiveTransform(np.float32([[0, 0], [WW, 0], [WW, WH], [0, WH]]), q.astype(np.float32))
    warped = cv2.warpPerspective(wc, M, (W, H), flags=cv2.INTER_LINEAR)
    al = warped[..., 3:4]/255; rgb = warped[..., :3]
    dim = 1-.55*cv2.warpPerspective(np.full((WH, WW), 1, np.float32), M, (W, H))[..., None]   # le mur s'assombrit sous le contenu
    base = base*dim
    base = base*(1-al)+rgb*al
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(1.1))     # légère profondeur de champ : le décor recule derrière les cartes
    return im.convert('RGBA')

# ---------- emojis ----------
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=64)
def emoji(ch, size):
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def pop_emoji(cv, ch, x, y, size, k, rot=0.0, t=0.0, a=1.0):
    if k < 0 or a <= 0: return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size).rotate(rot+6*math.sin(t*3+x*.01), resample=Image.BICUBIC, expand=True)
    e = with_alpha(e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))), Image.BICUBIC), a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
EMO = [(0.3, '👋', 900, 300, 120, -8, T['m5']), (T['m5']+.1, '📉', 900, 300, 120, 8, T['trois']), (T['nf']+.3, '😬', 920, 1150, 120, -8, T['ts']),
       (T['ts']+.3, '🤷', 920, 1150, 120, 8, T['mt']), (T['mt']+.3, '🚀', 920, 1150, 130, -10, T['toi']), (T['achete']+.25, '🤔', 900, 300, 120, -6, DUR+1)]

# ---------- premier plan ----------
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def sIntro(cv, c, t, a):
    grp(c, a*ease((t-.4)/.4), lambda c: text(c, "BIENVENUE", 540, 260, 'a', 110, WHITE, 'c'))
def sHook(cv, c, t, a):
    k = t-T['m5']
    glow_text(cv, "−5 %", 540, 250, 200, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.75, a=a*ease(k/.25), scale=lerp(1.35, 1, back(k/.4)))
    grp(c, a*ease((k-.3)/.3), lambda c: text(c, "NETFLIX APRÈS SES RÉSULTATS", 540, 380, 'xb', 36, WHITE, 'c', 1, 3))
def card(name, colr, rows, t, tint):
    def d(kk, w, h):
        text(kk, name, 48, 70, 'a', 66, WHITE, 'l');
        y = 150
        for (t0, label, val, vc) in rows:
            u = ease((t-t0)/.35)
            if u <= 0: continue
            text(kk, label, 48, y, 'xb', 26, ICE, 'l', u*.85, 2); text(kk, val, w-48, y, 'a', 54, vc, 'r', u)
            kk.set_line_width(1.5); col(kk, 'FFFFFF', .12*u); kk.move_to(48, y+30); kk.line_to(w-48, y+30); kk.stroke()
            y += 92
    return gp(900, 150+92*len(rows), d, tint)
def sCo(cv, c, t, a, name, t0, rows, colr, tint):
    k = t-t0; e = ease(k/.45); p = card(name, colr, rows, t, tint)
    h = 150+92*len(rows)
    place(cv, p, tilt_quad(540, 1420+40*(1-e), 900, h, ry=-.1-.3*(1-e), rx=.06), a*e, 14, .55)
def sNF(cv, c, t, a):
    sCo(cv, c, t, a, "NETFLIX", T['nf'], [(T['nf_ca'], "CHIFFRE D'AFFAIRES T3", "+11,8 %", GR), (T['nf_pub'], "PUB 2026 ATTENDUE", "2,7 MD$ (VS 3)", RD),
                                             (T['nf_job'], "POSTES SUPPRIMÉS", "ENVIRON 1 000", RD), (T['nf_yr'], "ACTION SUR UN AN", "PRÈS DE −50 %", RD)], RD, 'FFD0D6')
def sTS(cv, c, t, a):
    sCo(cv, c, t, a, "TESLA", T['ts'], [(T['ts_ca'], "VENTES T3", "28,05 MD$ (=)", AMB), (T['ts_ben'], "BÉNÉFICE NET", "−43 %", RD),
                                          (T['ts_cab'], "CYBERCAB", "AVANT FIN 2026", AMB)], AMB, 'FFE9C0')
def sMT(cv, c, t, a):
    sCo(cv, c, t, a, "META", T['mt'], [(T['mt_ca'], "CHIFFRE D'AFFAIRES T3", "64,6 MD$", GR), (T['mt_26'], "SUR UN AN", "+26 %", GR),
                                         (T['mt_up'], "ACTION APRÈS L'ANNONCE", "EN HAUSSE", GR)], GR, 'D0FFE4')
def sCta(cv, c, t, a):
    k = t-T['toi']
    glow_text(cv, "ET TOI,", 540, 1250, 120, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.3))
    kb = t-T['achete']
    glow_text(cv, "LEQUEL TU ACHÈTES ?", 540, 1400, 104, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kb/.3), scale=lerp(1.3, 1, back(kb/.4)))
    al = ease((kb-.3)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 1530, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 1530, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)

SCENES = [(sIntro, 0.0, T['m5']), (sHook, T['m5']-.1, T['nf']), (sNF, T['nf']-.1, T['ts']), (sTS, T['ts']-.1, T['mt']), (sMT, T['mt']-.1, T['toi']), (sCta, T['toi']-.1, DUR+1)]
SHAKES = [(T['m5'], 14), (T['nf_yr'], 8), (T['ts_ben'], 10), (T['mt_26'], 10)]
def frame(t):
    cv = background(t)
    darken_band(cv, 1180, 1920, .5)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    kk = cap_at(t)
    if kk is not None and t < DUR-1.3:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, CY)), 14*(1-al))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(6, 6, 8, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'swish'), (T['m5'], 'impact'), (T['m5'], 'low'), (T['trois'], 'swish'), (T['decu'], 'pop'), (T['hesite'], 'pop'), (T['rassure'], 'pop'),
          (T['nf'], 'swish'), (T['nf_ca'], 'tick'), (T['nf_pub'], 'pop'), (T['nf_job'], 'thud'), (T['nf_yr'], 'crash'),
          (T['ts'], 'swish'), (T['ts_ca'], 'tick'), (T['ts_ben'], 'impact'), (T['ts_cab'], 'pop'),
          (T['mt'], 'swish'), (T['mt_ca'], 'tick'), (T['mt_26'], 'boom'), (T['mt_26'], 'coins'), (T['mt_up'], 'glint'),
          (T['toi'], 'swish'), (T['achete'], 'pop'), (T['achete']+.3, 'click')]
    ev += [(e[0], 'pop') for e in EMO if e[0] > .1]
    return ev

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
