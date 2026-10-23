"""Actu du 23 octobre, version avec Mister Coin présent tout du long (pas de gros plans : il illustre et réagit).
Mise en page : intro / tuiles en haut, Mister Coin en bas ; pour chaque entreprise, il se tient à gauche et désigne
un panneau compact à droite (extrait de la vidéo précédente + verdict), au-dessus de la carte des chiffres."""
import sys, os, subprocess
_argv = sys.argv; sys.argv = ['x', 'info']
from am import *
import am
sys.argv = _argv
sys.path.insert(0, '/home/claude/mascot')
import mc_actu
mc_actu.CFG = mc_actu.build(T)

def sIntro(cv, c, t, a):
    e = ease((t-.2)/.5)
    def d(kk, w, h):
        text(kk, "L'ACTU", w/2, 170, 'a', 150, WHITE, 'c'); text(kk, "DE LA SEMAINE", w/2, 290, 'a', 96, WHITE, 'c')
        text(kk, "RÉSULTATS DU 3E TRIMESTRE 2026", w/2, 380, 'xb', 30, CY, 'c', 1, 3)
        kk.push_group(); logo_symbol(kk, w/2-150, 470, 36); kk.pop_group_to_source(); kk.paint(); text(kk, "Actions_Benefices", w/2-118, 470, 'b', 34, WHITE, 'l')
    place(cv, gp(860, 560, d), tilt_quad(540, 590+40*(1-e), 860, 560, ry=-.12-.3*(1-e), rx=.05), a*e, 14, .55)

def name_panel(name, t, t0):
    key, colr, verdict, date = CO[name]
    def d(kk, w, h):
        k = int(max(0, t-t0)*15); im = clip(key, k).resize((200, 356), Image.BICUBIC)
        arr = np.asarray(im.convert('RGBA'), np.uint8).copy(); arr[..., [0, 2]] = arr[..., [2, 0]]
        isurf = cairo.ImageSurface.create_for_data(bytearray(arr.tobytes()), cairo.FORMAT_ARGB32, 200, 356)
        x0 = w-232
        kk.save(); rr(kk, x0, 32, 200, 356, 20); kk.clip(); kk.set_source_surface(isurf, x0, 32); kk.paint(); kk.restore()
        rr(kk, x0, 32, 200, 356, 20); kk.set_line_width(4); col(kk, colr); kk.stroke()
        text(kk, "DÉJÀ SUR", 34, 84, 'xb', 26, ICE, 'l', .9, 3); text(kk, "LA CHAÎNE", 34, 122, 'xb', 26, ICE, 'l', .9, 3)
        text(kk, date, 34, 166, 'xb', 26, colr, 'l', 1, 3)
        if name == 'META':
            u = ease((t-T['mt_up'])/.4)
            text(kk, "LUNDI, ON TE", 34, 262, 'xb', 22, ICE, 'l', u, 1); text(kk, "DEMANDAIT :", 34, 296, 'xb', 22, ICE, 'l', u, 1)
            text(kk, "« TU ACHÈTES ? »", 34, 336, 'xb', 24, GR, 'l', u, 1)
        text(kk, name, w/2, 500, 'a', 108 if name == 'NETFLIX' else 120, WHITE, 'c')
        ww = tw(kk, verdict, 'xb', 42, 2)+64; rr(kk, w/2-ww/2, 538, ww, 78, 39); col(kk, colr); kk.fill(); text(kk, verdict, w/2, 578, 'xb', 42, INK, 'c', 1, 2)
    return gp(540, 650, d, {'NETFLIX': 'FFD0D6', 'TESLA': 'FFE9C0', 'META': 'D0FFE4'}[name])

def sCo(cv, c, t, a, name, t0, rows, colr, tint):
    k = t-t0; e = ease((k-.25)/.45); p = card(name, colr, rows, t, tint)
    place(cv, name_panel(name, t, t0), tilt_quad(788, 690+40*(1-e), 540, 650, ry=-.08-.3*(1-e), rx=.05), a*e, 14, .55)
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
def sTilesUp(cv, c, t, a, cta=False):
    """tuiles un peu plus haut pour laisser la place à Mister Coin"""
    for j, (name, k_) in enumerate((('NETFLIX', 'decu'), ('TESLA', 'hesite'), ('META', 'rassure'))):
        key, colr, verdict, _ = CO[name]
        t0 = (T['toi']+.35+j*.12) if cta else (T['trois']+j*.15); e = ease((t-t0)/.4)
        on = t >= T[k_]
        def d(kk, w, h, name=name, colr=colr, verdict=verdict, on=on, j=j):
            if cta: text(kk, str(j+1), w/2, 70, 'a', 70, AMB, 'c')
            text(kk, name, w/2, 210, 'a', 62 if name == 'NETFLIX' else 72, WHITE, 'c')
            if on:
                ww = tw(kk, verdict, 'xb', 26, 1)+40; rr(kk, w/2-ww/2, 262, ww, 52, 26); col(kk, colr); kk.fill(); text(kk, verdict, w/2, 289, 'xb', 26, INK, 'c', 1, 1)
        yc = 520 if cta else 640
        place(cv, gp(300, 360, d, {'NETFLIX': 'FFD0D6', 'TESLA': 'FFE9C0', 'META': 'D0FFE4'}[name]), tilt_quad(190+j*350, yc+40*(1-e), 300, 360, ry=(j-1)*.18, rx=.05), a*e, 14, .55)
def sHook(cv, c, t, a):
    k = t-T['m5']
    glow_text(cv, "−5 %", 540, 250, 200, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.75, a=a*ease(k/.25), scale=lerp(1.35, 1, back(k/.4)))
    grp(c, a*ease((k-.3)/.3), lambda c: text(c, "NETFLIX APRÈS SES RÉSULTATS", 540, 380, 'xb', 36, WHITE, 'c', 1, 3))
    if t >= T['trois']-.1: sTilesUp(cv, c, t, a)
def sCta(cv, c, t, a):
    sTilesUp(cv, c, t, a, cta=True)
    k = t-T['toi']
    glow_text(cv, "ET TOI,", 540, 850, 110, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.3))
    kb = t-T['achete']
    glow_text(cv, "LEQUEL TU ACHÈTES ?", 540, 990, 98, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease(kb/.3), scale=lerp(1.3, 1, back(kb/.4)))

SCENES = [(sIntro, 0.0, T['m5']), (sHook, T['m5']-.1, T['nf']), (sNF, T['nf']-.1, T['ts']), (sTS, T['ts']-.1, T['mt']), (sMT, T['mt']-.1, T['toi']), (sCta, T['toi']-.1, DUR+1)]
EMO = [(T['m5']+.1, '📉', 900, 300, 120, 8, T['trois'])]          # les réactions passent désormais par Mister Coin
am.EMO = EMO
def frame(t):
    cv = background(t)
    darken_band(cv, 1180, 1920, .5)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    for t0, ch, x, y, sz, rot, t1 in EMO:
        if t0 <= t < t1: pop_emoji(cv, ch, x, y, sz, t-t0, rot, t, clamp((t1-t)/.2))
    cv.alpha_composite(mc_actu.layer(t))
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
    ev = [e for e in am.events() if not (e[1] == 'pop' and any(abs(e[0]-x[0]) < 1e-6 for x in am.EMO if x[0] > .1) and e[0] not in (T['decu'], T['hesite'], T['rassure'], T['nf_pub'], T['ts_cab'], T['achete']))]
    ev += [(T['nf']-.05, 'swish'), (T['toi']-.05, 'swish')]                   # grands sauts de Mister Coin
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
