"""Animatique Palantir (sans voix) : minutage estimé, à recaler sur la voix. DA « dossier classifié » (voir notes_da.md).
usage : python3 animatique.py png t1 t2 …  |  python3 animatique.py mp4 [fps]"""
import sys, os, math, subprocess, functools
import numpy as np, cairo, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from dossier import *
ROOT = os.path.abspath(f'{D}/../..'); sys.path.insert(0, f'{ROOT}/lib')
from logo import logo_symbol

# ---------- minutage estimé (≈ 27,5 s) ----------
S = dict(eye=0.0, thiel=4.0, cia=7.2, data=9.6, ia=11.8, money=13.6, multi=18.0, res=22.0, end=24.6, fin=27.6)
DUR = S['fin']
CAPS = [(0.0, "Cette entreprise ne te connaît pas…"), (1.9, "mais elle aide les États à tout savoir de toi."),
        (S['thiel'], "Palantir, cofondée par Peter Thiel,"), (S['cia'], "et financée à ses débuts par la CIA."),
        (S['data'], "Ses logiciels aident les armées, les polices et les hôpitaux"), (S['ia'], "Et avec l'IA, ses ventes explosent."),
        (S['money'], "1 000 € placés le jour de son entrée en bourse, en 2020,"), (16.0, "valent aujourd'hui environ 20 000 €."),
        (S['multi'], "Mais l'action vaut plus de 60 fois son chiffre d'affaires annuel."), (20.4, "Génie ou bulle ?"),
        (S['res'], "[phrase sur les résultats du 2 novembre]"), (S['end'], "Et toi, tu achèterais Palantir à ce prix-là ?")]
LAB = ("ACTIONS_BÉNÉFICES / DOSSIER PLTR", "REC  03.11.2026", "CONFIDENTIEL · NIVEAU 3", "TC ")

# ---------- l'œil (vidéo Gemini) ----------
EYE_SC, EPX, EPY = 1.9, 540, 700
@functools.lru_cache(maxsize=1)
def eye_frames():
    cap = cv2.VideoCapture(f'{D}/decors/oeil.mp4'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(f)
    return F
def eye(t, zoom=1.0):
    F = eye_frames(); f = F[min(len(F)-1, int(t*24))]
    sc = EYE_SC*zoom; f = cv2.resize(f, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    px, py = 180/360*f.shape[1], 316/640*f.shape[0]; x0, y0 = int(px-EPX), int(py-EPY)
    f = f[y0:y0+H, x0:x0+W]
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32); c = f.astype(np.float32)*.35+g[..., None]*.65
    c = np.clip((c-128)*1.25+118, 0, 255); bl = cv2.GaussianBlur(c, (0, 0), 2); c = np.clip(c*1.6-bl*.6, 0, 255)
    v = np.hypot(*np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))); c *= np.clip(1.15-.55*v, 0, 1)[..., None]
    return c[..., ::-1]

# ---------- scènes : chacune dessine sur le contexte cairo (fond compris) ----------
def sc_eye(c, t):
    k = t-S['eye']
    target(c, EPX, EPY, ease(k/1.6), 'dark', coords=("SUJET 0001", "ANALYSE…"))
    for y in range(0, H, 6): c.rectangle(0, y, W, 2); col(c, '000000', .10); c.fill()
    y = (k*700) % (H+200); g = cairo.LinearGradient(0, y-140, 0, y); g.add_color_stop_rgba(0, *rgb(RED), 0); g.add_color_stop_rgba(1, *rgb(RED), .28)
    c.set_source(g); c.rectangle(0, y-140, W, 140); c.fill()
    if k > 1.9: text(c, "TOUT SAVOIR", 540, 420, 'black', 118, WHITE, ease((k-1.9)/.2), 'c')
    if k > 2.3: text(c, "de toi.", 540, 520, 'serif', 96, RED, ease((k-2.3)/.2), 'c')
def sc_thiel(c, t):
    k = t-S['thiel']; background(c, 'paper', t)
    x0, w = text(c, scramble("PALANTIR", ease(k/1.0), 7), 540, 560, 'black', 180, INK)
    dims(c, x0, 470, x0+w, 650, ease((k-.9)/.8), ("PLTR · NYSE", "FONDÉE EN 2003"))
    if k > 1.2: text(c, "cofondée par", 540, 720, 'serif', 80, RED, ease((k-1.2)/.2))
    if k > 1.6:
        for i, wd in enumerate(("PETER", "THIEL")):
            kk = k-1.6-i*.22
            if kk > 0: text(c, wd, 540, 830+i*110, 'black', 110, INK, ease(kk/.15))
    dot(c, 540, 1080, 16*back(clamp((k-2.4)/.3)), glow=False)
def sc_cia(c, t):
    k = t-S['cia']; background(c, 'dark', t)
    dot(c, 540, 540, 18); target(c, 540, 540, ease(k/1.0), 'dark', coords=("38.95 N", "77.15 W"))
    if k > .5: text(c, "LANGLEY, VIRGINIE", 540, 330, 'mono', 26, WHITE, .7*ease((k-.5)/.3), 'c', .12)
    if k > .9: text(c, "financée à ses débuts par", 540, 770, 'serif', 70, RED, ease((k-.9)/.2))
    if k > 1.3:
        sc = lerp(1.35, 1, back((k-1.3)/.35)); c.save(); c.translate(540, 880); c.scale(sc, sc)
        text(c, "LA CIA", 0, 0, 'black', 170, WHITE, ease((k-1.3)/.12)); c.restore()
def sc_data(c, t):
    k = t-S['data']; background(c, 'dark', t)
    def field(i, j, tt): return .5+.5*math.sin(i*.7+j*.5-tt*3)
    dot_grid(c, t, ease(k/.9), 'dark', cy=700, rows_=8, field=field, red_k=0)
    tags = ("ARMÉES", "POLICES", "HÔPITAUX")
    for i, tg in enumerate(tags):
        kk = k-.3-i*.35
        if kk > 0:
            x = 540+(i-1)*305
            w = tw(c, tg, 'monob', 34, .08)+40; rr_(c, x-w/2, 290, w, 64, 8); col(c, INK, .85*ease(kk/.15)); c.fill()
            c.set_line_width(2); rr_(c, x-w/2, 290, w, 64, 8); col(c, RED, ease(kk/.15)); c.stroke()
            text(c, tg, x, 322, 'monob', 34, WHITE, ease(kk/.15), 'c', .08)
def sc_ia(c, t):
    k = t-S['ia']; background(c, 'dark', t)
    def field(i, j, tt): return .5+.5*math.sin(i*.7+j*.5-tt*3)
    dot_grid(c, t, 1.0, 'dark', cy=700, rows_=8, field=field, red_k=ease(k/.8), square_k=ease((k-.3)/.9), rot=k*1.6)
    sc = lerp(1.6, 1, back(k/.35)); c.save(); c.translate(540, 640); c.scale(sc, sc)
    rr_(c, -330, -110, 660, 220, 18); col(c, INK, .9*ease(k/.15)); c.fill()
    text(c, "+ IA", 0, -10, 'black', 150, WHITE, ease(k/.12)); c.restore()
    if k > .5:
        rr_(c, 200, 780, 680, 110, 16); col(c, INK, .92*ease((k-.5)/.2)); c.fill()
        text(c, "ses ventes explosent", 540, 832, 'serif', 76, RED, ease((k-.5)/.2))
def sc_money(c, t):
    k = t-S['money']; background(c, 'dark', t)
    text(c, "1 000 € PLACÉS LE 30/09/2020", 540, 330, 'mono', 28, WHITE, .75*ease(k/.3), 'c', .1)
    flap_board(c, "1000€", 540, 470, 118, 168, clamp(k/1.2))
    if k > 1.4:
        text(c, "↓", 540, 600, 'black', 70, RED, ease((k-1.4)/.2))
        text(c, "AUJOURD'HUI", 540, 670, 'mono', 28, WHITE, .75*ease((k-1.4)/.3), 'c', .1)
    if k > 1.9:
        flap_board(c, "20386€", 540, 800, 128, 182, clamp((k-1.9)/1.6), red_last=True)
    if k > 3.4:
        x0 = 540-6*(128+8)/2; x1 = x0+6*(128+8)
        dims(c, x0, 709, x1, 891, ease((k-3.4)/.7), ("×20 EN 6 ANS", "HORS DIVIDENDES"))
def sc_multi(c, t):
    k = t-S['multi']; background(c, 'dark', t)
    word_rows(c, ["GÉNIE", "BULLE"], t, ease((k-2.2)/.4), size=150, cy=760)
    a = 1-ease((k-2.2)/.3)
    if a > 0:
        sc = lerp(1.4, 1, back(k/.4)); c.save(); c.translate(540, 600); c.scale(sc, sc)
        x0, w = text(c, "61×", 0, 0, 'black', 260, WHITE, a*ease(k/.12)); c.restore()
        if k > .5: text(c, "son chiffre d'affaires", 540, 800, 'serif', 78, RED, a*ease((k-.5)/.2))
        if k > .8: dims(c, 540-w/2, 490, 540+w/2, 710, ease((k-.8)/.6)*a, ("VALORISATION", "ESTIMATION 2026"))
    if k > 2.4:
        rr_(c, 290, 700, 500, 130, 14); col(c, INK, .92*ease((k-2.4)/.2)); c.fill()
        text(c, "GÉNIE OU BULLE ?", 540, 765, 'black', 58, WHITE, ease((k-2.4)/.2))
def sc_res(c, t):
    k = t-S['res']; background(c, 'paper', t)
    text(c, "RÉSULTATS · 2 NOVEMBRE 2026", 540, 330, 'mono', 28, INK, .75*ease(k/.3), 'c', .1)
    text(c, scramble("CHIFFRE D'AFFAIRES", ease(k/.8), 3), 540, 470, 'black', 70, INK, ease(k/.2))
    text(c, "+ XX %", 540, 620, 'black', 200, '9A958C', ease((k-.4)/.2))
    text(c, "chiffres de ce soir", 540, 780, 'serif', 70, RED, ease((k-.7)/.2))
    dot(c, 540, 900, 14, glow=False)
def sc_end(c, t):
    k = t-S['end']; background(c, 'dark', t)
    text(c, "Et toi,", 540, 360, 'serif', 110, RED, ease(k/.2))
    for i, wd in enumerate(("TU ACHÈTERAIS", "PALANTIR", "À CE PRIX-LÀ ?")):
        kk = k-.35-i*.3
        if kk > 0:
            sc = lerp(1.3, 1, back(kk/.3)); c.save(); c.translate(540, 490+i*125); c.scale(sc, sc)
            text(c, wd, 0, 0, 'black', 104 if i != 1 else 130, WHITE if i != 1 else RED, ease(kk/.12)); c.restore()
    if k > 1.6:
        a = ease((k-1.6)/.4); c.push_group(); logo_symbol(c, 395, 880, 44); c.pop_group_to_source(); c.paint_with_alpha(a)
        text(c, "Actions_Benefices", 430, 880, 'xb', 30, WHITE, a, 'l')
        text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 945, 'mono', 19, WHITE, .5*a, 'c')
ORDER = [('eye', sc_eye), ('thiel', sc_thiel), ('cia', sc_cia), ('data', sc_data), ('ia', sc_ia), ('money', sc_money), ('multi', sc_multi), ('res', sc_res), ('end', sc_end)]
KEYS = list(S)
def scene_at(t):
    cur = ORDER[0]
    for nm, fn in ORDER:
        if t >= S[nm]: cur = (nm, fn)
    return cur
def caption(c, t, mode):
    k = None
    for i, (t0, _) in enumerate(CAPS):
        if t >= t0: k = i
    if k is None or t > DUR-.4: return
    s_ = CAPS[k][1]; size = 40
    font(c, 'xb', size); words = s_.split(' '); lines, cur = [], ''
    for w_ in words:
        tt_ = (cur+' '+w_).strip()
        if cur and tw(c, tt_, 'xb', size) > 760: lines.append(cur); cur = w_
        else: cur = tt_
    lines.append(cur); y0 = 1060-(len(lines)-1)*30
    bw = max(tw(c, l, 'xb', size) for l in lines)+56; bh = len(lines)*60+30
    rr_(c, 540-bw/2, y0-45, bw, bh, 18); col(c, INK if mode == 'dark' else 'FFFFFF', .78); c.fill()
    for i, l in enumerate(lines): text(c, l, 540, y0+i*60, 'xb', size, WHITE if mode == 'dark' else INK, 1)
def frame(t):
    nm, fn = scene_at(t); mode = 'paper' if nm in ('thiel', 'res') else 'dark'
    s, c = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H), None; c = cairo.Context(s)
    if nm == 'eye':
        zoom = 1+3.5*ease((t-(S['thiel']-.55))/.55)**2 if t > S['thiel']-.55 else 1+.02*t
        base = eye(t, zoom)
        fn(c, t)
    else:
        base = None; fn(c, t)
    hud(c, t, mode, LAB)
    # flash rouge du raccord : le point rouge grossit et remplit l'écran à la fin de l'œil
    if nm == 'eye' and t > S['thiel']-.3:
        r = 30+1600*ease((t-(S['thiel']-.3))/.3)**2; c.arc(EPX, EPY, r, 0, 2*math.pi); col(c, RED, 1); c.fill()
    caption(c, t, mode)
    s.flush(); ov = np.asarray(Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)).astype(np.float32)
    if base is not None:
        a = ov[..., 3:]/255; out = base*(1-a)+ov[..., :3]*a
    else: out = ov[..., :3]
    # coupe sur le temps fort : léger flash blanc d'une image à chaque changement de scène
    for k in KEYS[1:-1]:
        if 0 <= t-S[k] < 1/30: out = out*.6+255*.4
    # zone de Mister Coin (repère pour l'animatique)
    return Image.fromarray(grain_layer(out, t, 8).astype(np.uint8))
def main():
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]: frame(float(ts)).save(f'{D}/prev/a_{ts}.png')
        return
    fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    out = f'{D}/out/animatique_palantir.mp4'; os.makedirs(f'{D}/out', exist_ok=True)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(DUR*fps)): ff.stdin.write(frame(i/fps).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('ok', out)
if __name__ == '__main__': main()
