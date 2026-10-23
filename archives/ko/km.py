"""Coca-Cola : la société de Buffett touche 848 M$ de dividendes par an sur une mise de 1,3 Md$.
Fonds 3D : macro de bulles dans le cola (boucle) et verre droit générique qui se remplit (aucune forme ni marque déposée).
usage : python km.py png t1 t2 ... | python km.py seg out.mp4 f0 f1 | python km.py info"""
import sys, math, re, random, subprocess, os, functools
import numpy as np, cairo
from PIL import Image
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/meta')
from bglass import *
FPS = 60; NB = '\u00a0'
AMB = 'FFC24A'; CAR = 'FF9A4A'; CRM = 'FFF1DC'; GR = '3FE08A'; RD = 'FF4057'; INK = '120B06'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage calé sur la voix (Thomas, 35,1 s) ----------
T = dict(hook=0.0, buf=2.75, rien=5.7, y88=7.35, y94=8.8, buy=10.55, sh=11.15, cost=13.2, costn=13.55, never=14.75, auj=16.3, p65=19.05,
         chq=21.15, sec=22.15, streak=24.2, n64=26.2, stake=27.95, n37=29.5, ach=31.05, att=31.9, enc=32.8, cta=33.85, buy2=34.5, end=36.4)
DUR = T['end']
CAPS = [(0.0, "[848 millions] de dollars."), (T['buf'], "C'est ce que la société de Warren Buffett touche chaque année…"), (T['rien'], "[sans rien faire]."),
        (T['y88'], "Entre 1988 et 1994,"), (T['buy'], "elle achète [400 millions] d'actions Coca-Cola,"), (T['cost'], "pour [1,3 milliard] de dollars."),
        (T['never'], "Elle n'en a [jamais vendu] une seule."), (T['auj'], "Aujourd'hui, les dividendes lui rapportent"), (T['p65'], "[65 %] de sa mise…"),
        (T['chq'], "[chaque année]."), (T['sec'], "[27 dollars] par seconde."), (T['streak'], "Et Coca-Cola augmente son dividende depuis [64 ans] d'affilée."),
        (T['stake'], "Sa mise de départ vaut maintenant [37 milliards]."), (T['ach'], "Acheter, attendre, [encaisser]."), (T['cta'], "Et toi,"), (T['buy2'], "tu [achètes] ?")]
HL = {T['p65']: GR, T['chq']: GR, T['sec']: GR, T['stake']: GR, T['ach']: GR, T['buy2']: GR}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1440, size=46, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- fonds 3D ----------
D = '/home/claude/ko'
@functools.lru_cache(maxsize=10)
def img(p):
    im = Image.open(p).convert('RGB')
    return im if im.size == (W, H) else im.resize((W, H), Image.LANCZOS)
def last_png(d):
    ks = sorted(k for k in os.listdir(d) if k.endswith('.png')) if os.path.isdir(d) else []
    return f'{d}/{ks[-1]}' if ks else None
_yy, _xx = np.mgrid[0:H, 0:W]; VIG = np.clip(1-(((_xx-W/2)/(W*.75))**2+((_yy-H*.45)/(H*.62))**2), .08, 1)[..., None].astype(np.float32)
@functools.lru_cache(maxsize=10)
def graded(p):
    """étalonnage cola : rendu doré -> ambre profond, bords sombres"""
    a = np.asarray(img(p), np.float32)/255
    return Image.fromarray((np.clip(a**1.8*np.array([1.0, .6, .34], np.float32)*VIG*1.05, 0, 1)*255).astype(np.uint8))
def bub(t):
    """boucle de bulles : images intermédiaires par flux optique si disponibles"""
    if os.path.exists(f'{D}/seq30_bub/0118.png'): return graded(f'{D}/seq30_bub/{min(118, int(t*30) % 120):04d}.png')
    f = int((t*30) % 120)//2*2+1; p = f'{D}/seq_bub/f{f:04d}.png'
    return graded(p if os.path.exists(p) else (last_png(f'{D}/seq_bub') or '/tmp/k08/gb_1.png'))
F0, F1 = T['y88'], T['auj']     # le verre se remplit pendant l'achat puis reste plein (« jamais vendu une seule »)
def fill(t):
    d = f'{D}/seq30_fill'
    if os.path.isdir(d) and os.path.exists(f'{d}/done'):
        n = len([k for k in os.listdir(d) if k.endswith('.png')]); i = int(clamp((t-F0)/(F1-F0))*(n-1))
        return img(f'{d}/{i:04d}.png')
    f = int(clamp((t-F0)/(F1-F0))*47)*2+1; p = f'{D}/seq_fill/f{f:04d}.png'
    return img(p if os.path.exists(p) else (last_png(f'{D}/seq_fill') or '/tmp/k08/gt_60.png'))
def background(t):
    if t < F0: im = bub(t); z = 1.03+.04*(t/F0)
    elif t < F1: im = fill(t); k = t-F0; z = lerp(1.25, 1.0, ease(k/.7))+.04*ease((t-T['never'])/1.5)
    else: im = bub(t); k = t-F1; z = lerp(1.3, 1.02, ease(k/.7))
    if t < .45: z += .15*(1-ease(t/.45))
    if abs(z-1) > .002:
        w, h = int(W*z), int(H*z); im = im.resize((w, h), Image.BICUBIC).crop(((w-W)//2, (h-H)//2, (w-W)//2+W, (h-H)//2+H))
    blur = 0
    for tc in (F0, F1):
        if tc-.25 < t < tc+.35: blur = max(blur, 16*(1-abs(t-tc)/.35))
    if blur > .5: im = lowblur(im, blur, 2)
    arr = np.asarray(im, np.float32)
    hi_ = np.clip(arr-190, 0, None)*1.4
    halo = np.asarray(lowblur(Image.fromarray(hi_.clip(0, 255).astype(np.uint8)), 22, 4), np.float32)
    im = Image.fromarray(np.clip(arr*.95+halo*.55, 0, 255).astype(np.uint8)).convert('RGBA')
    for tc in (F0, F1):
        if abs(t-tc) < .18:
            s, c = surface(); c.set_source_rgba(1, .85, .6, .5*(1-abs(t-tc)/.18)); c.paint(); im.alpha_composite(to_img(s))
    return im

# ---------- emojis (Noto, licence libre) ----------
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=64)
def emoji(ch, size):
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def pop_emoji(cv, ch, x, y, size, k, rot=0.0, t=0.0, a=1.0):
    if k < 0 or a <= 0: return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size).rotate(rot+6*math.sin(t*3+x*.01), resample=Image.BICUBIC, expand=True)
    e = with_alpha(e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))), Image.BICUBIC), a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
EMO = [(0.4, '🥤', 880, 300, 130, -10, T['buf']), (T['rien']+.1, '😴', 930, 660, 130, 8, T['y88']),
       (T['sh']+.2, '🛒', 545, 470, 100, -8, T['costn']-.3), (T['never']+.15, '🔒', 860, 330, 120, 8, T['auj']),
       (T['sec']+.2, '💸', 860, 360, 130, -8, T['streak']), (T['n64']+.1, '🎂', 860, 300, 130, 8, T['stake']),
       (T['n37']+.15, '👑', 880, 260, 130, -10, T['ach']), (T['buy2']+.25, '🤔', 540, 900, 120, -8, DUR+1)]

# ---------- éléments ----------
def gp(w, h, draw): return gpanel(w, h, draw, tint='FFE2C0', ta=.08, edge=.75)
def bubble(cv, x, y, r, draw, a=1.0):
    """grosse bulle de verre qui porte une information (reflets, liseré, intérieur légèrement éclairci)"""
    if a <= .01 or r < 4: return
    s, c = surface()
    g = cairo.RadialGradient(x-r*.25, y-r*.3, r*.1, x, y, r)
    g.add_color_stop_rgba(0, 1, .97, .9, .10*a); g.add_color_stop_rgba(.78, 1, .9, .75, .06*a); g.add_color_stop_rgba(.96, 1, .92, .82, .42*a); g.add_color_stop_rgba(1, 1, .95, .9, .0)
    c.arc(x, y, r, 0, 2*math.pi); c.set_source(g); c.fill()
    c.set_line_width(max(2, r*.025)); c.arc(x, y, r*.985, 0, 2*math.pi); c.set_source_rgba(1, .96, .9, .55*a); c.stroke()
    c.save(); c.translate(x-r*.42, y-r*.5); c.rotate(-.6); c.scale(r*.28, r*.12); c.arc(0, 0, 1, 0, 2*math.pi); c.restore()
    hg = cairo.RadialGradient(x-r*.42, y-r*.5, 0, x-r*.42, y-r*.5, r*.3); hg.add_color_stop_rgba(0, 1, 1, 1, .85*a); hg.add_color_stop_rgba(1, 1, 1, 1, 0); c.set_source(hg); c.fill()
    c.arc(x+r*.5, y+r*.55, r*.07, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, .5*a); c.fill()
    # verre dépoli : fond flouté sous la bulle
    box = (int(x-r), int(y-r), int(x+r), int(y+r)); cut = cv.crop(box); bl = lowblur(cut.convert('RGB'), 10, 2).convert('RGBA')
    m = Image.new('L', cut.size, 0); from PIL import ImageDraw; ImageDraw.Draw(m).ellipse([2, 2, cut.size[0]-3, cut.size[1]-3], fill=int(255*a)); cv.paste(bl, box[:2], m)
    cv.alpha_composite(to_img(s))
    s2, c2 = surface(); c2.push_group(); draw(c2); c2.pop_group_to_source(); c2.paint_with_alpha(a); cv.alpha_composite(to_img(s2))
def rise(t, t0, y1, y0=1700, d=.8):
    """une bulle monte depuis le bas et se pose en flottant"""
    k = t-t0; u = ease(k/d)
    return lerp(y0, y1, u)+(6*math.sin(k*2.2) if k > d else 0), u

# ---------- scènes ----------
def sHook(cv, c, t, a):
    sc = lerp(1.3, 1, back(t/.45, 1.3))
    glow_text(cv, "848 M$", 540, 560, 230, top='FFFFFF', bottom='FFD79A', glow='FF9A3C', ga=.75, a=a, scale=sc)
    grp(c, a*ease((t-.9)/.3), lambda c: text(c, "DE DIVIDENDES PAR AN", 540, 760, 'xb', 40, WHITE, 'c', 1, 3))
    def badge(c):
        s_ = "LA SOCIÉTÉ DE WARREN BUFFETT"; w = tw(c, s_, 'xb', 30, 2)+60; rr(c, 540-w/2, 816, w, 60, 30); col(c, AMB); c.fill(); text(c, s_, 540, 846, 'xb', 30, INK, 'c', 1, 2)
    grp(c, a*ease((t-T['buf']-.6)/.3), badge)
    kr = t-T['rien']
    if kr > 0: glow_text(cv, "SANS RIEN FAIRE", 540, 1000, 92, top='FFFFFF', bottom='FFE9C8', glow='FFB25A', ga=.5, a=a*ease(kr/.3), scale=lerp(1.2, 1, back(kr/.4)))
def sBuy(cv, c, t, a):
    k = t-T['y88']
    yr = 1988 if t < T['y94'] else 1988+round(6*ease((t-T['y94'])/1.0))
    def years(c):
        text(c, "ACHATS", 540, 170, 'xb', 32, AMB, 'c', 1, 6)
        text(c, "1988", 300, 300, 'a', 120, WHITE, 'c'); text(c, "→", 540, 288, 'xb', 70, CRM, 'c', ease((t-T['y94']+.2)/.3))
        text(c, str(yr), 780, 300, 'a', 120, WHITE if t >= T['y94'] else '777777', 'c', ease((t-T['y94']+.2)/.3))
    grp(c, a*ease(k/.35), years, 30*(1-ease(k/.35)))
    if t > T['sh']-.2:
        y, u = rise(t, T['sh']-.2, 490)
        def d1(c):
            text(c, "400 M", 290, y+16, 'a', 80, WHITE, 'c', a); text(c, "D'ACTIONS", 290, y+70, 'xb', 24, CRM, 'c', a, 3)
        bubble(cv, 290, y, 150*lerp(.6, 1, u), d1, a*u)
    if t > T['costn']-.25:
        y, u = rise(t, T['costn']-.25, 490)
        def d2(c):
            text(c, "1,3 MD$", 795, y+16, 'a', 70, AMB, 'c', a); text(c, "INVESTIS", 795, y+66, 'xb', 24, CRM, 'c', a, 3)
        bubble(cv, 795, y, 150*lerp(.6, 1, u), d2, a*u)
def sNever(cv, c, t, a):
    k = t-T['never']; sc = lerp(1.6, 1, back(k/.35, 1.6))
    glow_text(cv, "0", 540, 430, 300, top='FFFFFF', bottom='FFD79A', glow='FF9A3C', ga=.7, a=a*ease(k/.2), scale=sc)
    grp(c, a*ease((k-.25)/.3), lambda c: text(c, "ACTION VENDUE DEPUIS 1988", 540, 600, 'xb', 40, WHITE, 'c', 1, 3))
def sDiv(cv, c, t, a):
    k = t-T['auj']
    if t < T['sec']:
        kp = t-T['p65']; v = 65*ease(clamp(kp/1.1)) if kp > 0 else 0
        def d(kk, w, h):
            text(kk, "DIVIDENDES / MISE DE DÉPART", w/2, 60, 'sb', 24, CAR, 'c', 1, 2)
            cx, cy, R = w/2, 330, 190
            kk.set_line_width(34); kk.arc(cx, cy, R, 0, 2*math.pi); col(kk, 'FFFFFF', .10); kk.stroke()
            if v > 0:
                kk.set_line_cap(cairo.LINE_CAP_ROUND)
                for lw, al in ((60, .15), (34, 1)):
                    kk.set_line_width(lw); kk.arc(cx, cy, R, -math.pi/2, -math.pi/2+2*math.pi*v/100); col(kk, GR, al); kk.stroke()
            text(kk, f"{v:.0f} %", cx, cy+40, 'a', 130, WHITE, 'c')
            text(kk, "CHAQUE ANNÉE", cx, h-56, 'xb', 32, GR if t >= T['chq'] else '777777', 'c', 1, 3)
        e = ease(k/.45); place(cv, gp(620, 640, d), tilt_quad(540, 560+50*(1-e), 620, 640, ry=-.14-.3*(1-e), rx=.06), a*e, 14, .55)
        if t > T['chq']:
            kc = t-T['chq']
            grp(c, a*ease(kc/.3), lambda c: text(c, "MISE REMBOURSÉE TOUS LES 18 MOIS", 540, 1000, 'xb', 32, AMB, 'c', 1, 2))
    else:
        ks = t-T['sec']; sc = lerp(1.35, 1, back(ks/.4))
        glow_text(cv, "27 $", 540, 470, 240, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(ks/.25), scale=sc)
        grp(c, a*ease((ks-.2)/.3), lambda c: text(c, "PAR SECONDE", 540, 650, 'xb', 44, WHITE, 'c', 1, 4))
        tot = int(27*max(0, ks-.4))
        def ctr(c):
            s_ = f"+{tot} $ DEPUIS LE DÉBUT DE CETTE PHRASE".replace('+0 ', '+0 '); w = tw(c, s_, 'xb', 28, 1)+56
            rr(c, 540-w/2, 712, w, 58, 29); col(c, '000000', .45); c.fill(); text(c, s_, 540, 741, 'xb', 28, GR, 'c', 1, 1)
        grp(c, a*ease((ks-.5)/.3), ctr)
def sStreak(cv, c, t, a):
    k = t-T['streak']; n = int(64*inout(clamp((k-.2)/2.0)))
    def d(kk, w, h):
        text(kk, "DIVIDENDE ANNUEL : UNE HAUSSE PAR AN", w/2, 56, 'sb', 22, CAR, 'c', 1, 2)
        X0, X1, YB, YT = 50, w-50, h-60, 120; bw = (X1-X0)/64
        for i in range(n):
            v = (1.07**i-1)/(1.07**63-1); y = YB-(YB-YT)*(.04+.96*v)
            g = cairo.LinearGradient(0, y, 0, YB); g.add_color_stop_rgba(0, *hx(GR if i == n-1 else AMB, 1)); g.add_color_stop_rgba(1, *hx(AMB, .25))
            kk.rectangle(X0+i*bw+1, y, bw-2, YB-y); kk.set_source(g); kk.fill()
        text(kk, "1963", X0+20, h-24, 'm', 22, SUB, 'l'); text(kk, "2026", X1-20, h-24, 'm', 22, SUB, 'r')
    e = ease(k/.45); place(cv, gp(860, 520, d), tilt_quad(540, 700+50*(1-e), 860, 520, ry=.14+.3*(1-e), rx=.06), a*e, 14, .55)
    kn = t-T['n64']
    if kn > -.3: glow_text(cv, "64 ANS", 540, 320, 170, top='FFFFFF', bottom='FFD79A', glow='FF9A3C', ga=.7, a=a*ease((kn+.3)/.25), scale=lerp(1.35, 1, back((kn+.3)/.4)))
    grp(c, a*ease((kn)/.3), lambda c: text(c, "DE HAUSSES D'AFFILÉE", 540, 440, 'xb', 36, WHITE, 'c', 1, 3))
def sStake(cv, c, t, a):
    k = t-T['stake']
    grp(c, a*ease(k/.3), lambda c: (text(c, "MISE DE DÉPART", 540, 300, 'xb', 32, CRM, 'c', 1, 3), text(c, "1,3 MD$", 540, 420, 'a', 110, WHITE, 'c')))
    grp(c, a*ease((k-.6)/.3), lambda c: text(c, "↓", 540, 540, 'xb', 80, AMB, 'c'))
    kv = t-T['n37']
    if kv > -.7:
        v = 37.6*ease(clamp((kv+.7)/.9))
        glow_text(cv, f"{v:.1f} MD$".replace('.', ','), 540, 720, 180, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease((kv+.7)/.25), scale=lerp(1.0, 1.08, ease(kv/.2)) if 0 < kv < .2 else (lerp(1.08, 1, ease((kv-.2)/.3)) if kv >= .2 else 1))
    if kv > .3:
        y, u = rise(t, T['n37']+.3, 960, 1600, .6)
        bubble(cv, 540, y, 135*lerp(.6, 1, u), lambda c_: text(c_, "×29", 540, y+36, 'a', 110, GR, 'c', a), a*u)
def sMotto(cv, c, t, a):
    for i, (key, word, colr) in enumerate((('ach', "ACHETER", WHITE), ('att', "ATTENDRE", WHITE), ('enc', "ENCAISSER", AMB))):
        kw = t-T[key]
        if kw > 0:
            y = 420+i*170
            if colr == AMB: glow_text(cv, word, 540, y, 130, top='FFFFFF', bottom='FFD79A', glow='FF9A3C', ga=.7, a=a*ease(kw/.25), scale=lerp(1.3, 1, back(kw/.4)))
            else: grp(c, a*ease(kw/.25), lambda c, w=word, y=y, kw=kw: text(c, w, 540, y+40*(1-ease(kw/.3)), 'a', 120, colr, 'c'))
def sCta(cv, c, t, a):
    k = t-T['cta']
    glow_text(cv, "ET TOI,", 540, 520, 130, top='FFFFFF', bottom='FFE9C8', glow='FFB25A', ga=.5, a=a*ease(k/.3))
    kb = t-T['buy2']
    glow_text(cv, "TU ACHÈTES ?", 540, 680, 130, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kb/.3), scale=lerp(1.3, 1, back(kb/.4)))
    al = ease((kb-.3)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 1135, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 1135, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)

SCENES = [(sHook, 0.0, T['y88']), (sBuy, T['y88']-.1, T['never']), (sNever, T['never']-.1, T['auj']), (sDiv, T['auj']-.1, T['streak']),
          (sStreak, T['streak']-.1, T['stake']), (sStake, T['stake']-.1, T['ach']), (sMotto, T['ach']-.1, T['cta']), (sCta, T['cta']-.1, DUR+1)]
SHAKES = [(0.0, 14), (T['never'], 14), (T['p65'], 8), (T['sec'], 14), (T['n64'], 10), (T['n37'], 14), (T['enc'], 10)]
def sdiv_swap(t):   # bascule douce entre la jauge et « 27 $ par seconde »
    return None
def frame(t):
    cv = background(t)
    darkspot(cv, 540, 640, 720, 700, .32); darken_band(cv, 1330, 1560, .6)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if fn is sDiv and T['sec']-.2 < t < T['sec']+.05: al *= clamp(abs(t-(T['sec']-.075))/.125)
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    kk = cap_at(t)
    if kk is not None and t < DUR-1.2:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, AMB)), 14*(1-al))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(6, 4, 3, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'impact'), (0.0, 'low'), (T['buf']+.6, 'swish'), (T['rien'], 'pop'), (F0-.8, 'riser'), (F0, 'swish'), (T['y94'], 'tick'),
          (T['sh']-.2, 'pop'), (T['costn']-.25, 'pop'), (T['costn'], 'glint'), (T['never'], 'impact'), (F1, 'swish'), (T['p65']-.1, 'tick'),
          (T['p65']+1.0, 'glint'), (T['chq'], 'coin'), (T['sec'], 'boom'), (T['sec']+.5, 'coins'), (T['streak'], 'swish'), (T['n64'], 'impact'),
          (T['stake'], 'swish'), (T['n37']-.7, 'tick'), (T['n37'], 'boom'), (T['n37'], 'coins'), (T['n37']+.3, 'pop'),
          (T['ach'], 'thud'), (T['att'], 'thud'), (T['enc'], 'impact'), (T['enc'], 'coin'), (T['cta'], 'swish'), (T['buy2'], 'pop'), (T['buy2']+.3, 'click')]
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
