"""PEA/CTO avec Mister Coin (kit /home/claude/mister_coin) : il se tient en bas à gauche et illustre le propos,
puis saute au centre pour la question finale."""
import sys, os, subprocess
_argv = sys.argv; sys.argv = ['x', 'info']
from pm import *
import pm
sys.argv = _argv
sys.path.insert(0, '/home/claude/mister_coin')
from mister_coin import MisterCoin
MC = MisterCoin('/home/claude/pea/voice_full.wav',
                places={'ciel': (840, -300, .2, True), 'bd': (840, 1450, .2, True), 'bg': (240, 1450, .2),
                        'regle_g': (250, 316, .16), 'regle_m': (470, 316, .16), 'chiffre': (865, 850, .2, True),
                        'carte_g': (260, 1430, .2), 'carte_d': (830, 1430, .2, True), 'poche': (830, 1490, .2, True), 'centre': (540, 1500, .27)},
                debut='ciel',
                moments=[(2.4, 'montre'), (7.05, 'pouce'), (8.6, 'montre'), (14.75, 'negatif'), (16.3, 'negatif'), (20.9, 'montre'),
                         (25.0, 'positif'), (27.05, 'positif'), (31.1, 'montre'), (33.35, 'montre'), (34.9, 'positif')],
                sauts_de_place=[(0.05, 'bd'), (8.0, 'bg'), (13.75, 'regle_g'), (14.1, 'regle_m', 'marche', .65), (17.2, 'chiffre'),
                                (20.35, 'carte_g'), (21.45, 'carte_d'), (25.6, 'poche'), (29.9, 'bg'), (32.0, 'bd'), (34.2, 'centre')],
                petits_sauts=[T['clot']], marches=[(4.9, 6.9)], assis=[(17.8, 20.3)], danses=[(27.1, 29.3)],
                coucous=[(35.6, 36.9)],
                bulles=[(5.1, 6.8, "J'ai pas pris mon passeport !"), (9.1, 10.7, "Bonjour, hallo, ciao !"), (16.45, 17.5, "Aïe… ça pique.", 'droite'),
                        (18.0, 19.5, "Je peux m'asseoir ?"), (21.95, 23.0, "Ah, là on respire !", 'gauche'), (27.4, 28.9, "Nouveau chapeau !", 'gauche')])
# cartes des taux remontées de 40 px et pastille « −12,8 points » décalée à droite : rien de caché par Mister Coin
import inspect as _insp
_src = _insp.getsource(pm.sRates).replace("760+50*(1-e1)", "640+50*(1-e1)").replace("760+50*(1-e2)", "640+50*(1-e2)")
_src = _src.replace("rr(c, 540-w/2, 1210, w, 76, 38)", "rr(c, 610-w/2, 1170, w, 76, 38)").replace("text(c, \"−12,8 POINTS\", 540, 1249", "text(c, \"−12,8 POINTS\", 610, 1209")
exec(_src, pm.__dict__); sRates = pm.sRates
_src2 = _insp.getsource(pm.sRule).replace('"31,4 %", 540, 1000', '"31,4 %", 540, 915').replace('"COMME AU COMPTE-TITRES", 540, 1140', '"COMME AU COMPTE-TITRES", 540, 1025')
exec(_src2, pm.__dict__); sRule = pm.sRule
SCENES = [({'sRates': sRates, 'sRule': sRule}.get(f.__name__, f), a, b) for f, a, b in SCENES]
# émojis : on garde les émojis thématiques, les réactions passent par Mister Coin
EMO = [e for e in pm.EMO if e[1] not in ('🤔', '😏')]
def frame(t):
    cv = background(t)
    darkspot(cv, 540, 420, 760, 420, .35); darken_band(cv, 1450, 1680, .55)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    s2, c2 = surface()
    kk = cap_at(t)
    if kk is not None and t < DUR-1.3:
        st0 = CAPS[kk][0]; al = 1.0 if st0 == 0 else ease((t-st0)/.12)
        grp(c2, al, lambda c: caption(c, parse(CAPS[kk][1]), HL.get(st0, GOLD)), 14*(1-al))
    cv.alpha_composite(to_img(s))           # textes des scènes
    cv.alpha_composite(MC.layer(t))         # Mister Coin devant tout le décor et les textes…
    cv.alpha_composite(to_img(s2))          # …sauf les sous-titres
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(4, 6, 11, 255))
    return finish(cv, t, 4.0)
def events():
    drop = {e[0] for e in pm.EMO if e[1] in ('🤔', '😏')}
    ev = [e for e in pm.events() if not (e[1] == 'pop' and e[0] in drop)]
    ev += [(m[0]+.05, 'swish') for m in MC.moves if m[4] == 'saut' and m[0] > .5]       # chaque saut de Mister Coin
    ev += [(b[0], 'pop') for b in MC.bulles]                                          # chaque bulle
    return ev
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/mc_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
