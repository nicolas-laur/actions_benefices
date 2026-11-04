"""Ubisoft (5/11/2026), vidéo finale : orbe et présages → clocher, marche, plongeon, spirale → spirale sur fond noir et texte →
souterrain, brèche → argumentaire sur panneaux de verre (argument.py) ; voix Thomas en 5 fichiers, Mister Coin revient dans le
souterrain. Musique : posée par Nicolas dans Edits (la vidéo est livrée avec voix et bruitages, sans musique).
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import os, sys, math, re, subprocess
os.environ.setdefault('TXT', '0'); os.environ.setdefault('AMB', '0')
import numpy as np, cv2, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..')); sys.path.insert(0, D)
import assemble as A
import argument as G
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from veo_coin import VeoCoin
FPS = int(os.environ.get('FPS', 60)); NB = ' '
VOICE = f'{D}/voice_full.wav'
OFF = {1: 4.35, 2: 10.9, 3: 15.25, 4: 18.45, 5: G.V5}
A5 = G.V5
DUR = A5+69.49+2.0
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)

# ---------- l'argumentaire remplace le panneau d'essai derrière la brèche ----------
B = A.B
def room_arg(bt):
    t = bt-A.B_SKIP+A.T_B
    cv = B.room_base().copy(); s, c = surface(); rng = np.random.default_rng(4)
    for k in range(70):                                                      # poussière qui retombe
        x = (rng.uniform(0, W)+12*math.sin(t*.5+k)) % W; y = (rng.uniform(0, H)+t*25) % H; r = rng.uniform(.8, 2.4)
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(.85, .9, 1, rng.uniform(.05, .2)); c.fill()
    cv.alpha_composite(to_img(s))
    G.draw(cv, t-A5)
    return cv
B.room = room_arg
A.DUR = DUR

# ---------- sous-titres (mot clé surligné ; ponctuation collée hors surlignage) ----------
BLUE, GOLD, PINK, NAVY, INK = '3A86FF', 'F5B400', 'FF5DA2', '1E2A44', '0B0E14'
def spans(o, parts):
    """répartit des morceaux de phrase sur une plage de voix, au prorata du nombre de lettres"""
    a, b = parts[0]; chunks = parts[1:]; L = [len(re.sub(r'[\[\]]', '', s)) for s, _ in chunks]; tot = sum(L); out = []; t = a
    for (s, hl), l in zip(chunks, L): out.append((o+t, s, hl)); t += (b-a)*l/tot
    return out
V5 = A5
CAPS = [(OFF[1], "Cette entreprise a sûrement [bercé ton enfance].", BLUE), (OFF[1]+2.95, "", BLUE),
        (OFF[2], "Mais depuis son record de [juillet 2018]…", GOLD), (OFF[2]+2.7, "", BLUE),
        (OFF[3], "…son action a perdu [plus de 95 %].", PINK), (OFF[3]+3.1, "", BLUE),
        (OFF[4], "[Ubisoft].", BLUE), (OFF[4]+1.3, "", BLUE)]
CAPS += [(V5+0.0, "Ubisoft, c'est une histoire [bretonne] :", BLUE)]
CAPS += spans(V5, [(2.4, 10.43), ("fondée en [1986] par les [cinq frères Guillemot],", GOLD), ("elle a donné naissance à [Rayman], [Assassin's Creed],", BLUE), ("[Far Cry] ou [Rainbow Six].", BLUE)])
CAPS += [(V5+11.04, "Mais depuis deux ans, ses ventes [s'effondrent] :", PINK)]
CAPS += spans(V5, [(13.69, 18.49), ("[2,3 milliards d'euros] en 2023,", GOLD), ("à peine [1,5 milliard] l'an dernier.", PINK)])
CAPS += [(V5+18.97, "[-34 %].", PINK)]
CAPS += spans(V5, [(20.67, 28.91), ("[Star Wars Outlaws] s'est vendu [moins que prévu],", PINK), ("et même [Assassin's Creed Shadows], avec [3 millions de joueurs] en une semaine,", BLUE), ("n'a pas [inversé la tendance].", PINK)])
CAPS += spans(V5, [(29.43, 39.85), ("Pendant ce temps, l'argent dépensé [dans les jeux],", BLUE), ("objets, extensions, abonnements, [grimpe] :", GOLD), ("[plus de 900 millions d'euros] l'an dernier,", GOLD), ("soit [6 euros sur 10] encaissés par Ubisoft.", GOLD)])
CAPS += spans(V5, [(40.24, 46.1), ("Ajoute des jeux [en retard ou annulés]", PINK), ("et des [polémiques à répétition], jusqu'au héros d'[Assassin's Creed Shadows].", PINK)])
CAPS += spans(V5, [(46.66, 51.9), ("En janvier, Ubisoft [arrête six jeux],", PINK), ("et l'action perd [près de 40 %] en une seule journée.", PINK)])
CAPS += [(V5+52.48, "L'an dernier : [plus d'un milliard d'euros] de pertes.", PINK)]
CAPS += spans(V5, [(55.6, 59.87), ("Résultat : [1 000 €] placés au sommet", GOLD), ("valent aujourd'hui [moins de 50 €].", PINK)])
CAPS += spans(V5, [(60.27, 65.71), ("Mais [Tencent] vient de miser [plus d'un milliard]", BLUE), ("sur Assassin's Creed, Far Cry et Rainbow Six.", BLUE)])
CAPS += [(V5+66.22, "[Game over]…", PINK), (V5+67.3, "ou [nouvelle partie] ?", GOLD), (V5+69.4, "", BLUE)]
CAPS = [c if len(c) == 3 else (c[0], c[1], BLUE) for c in CAPS]
CAPS.sort(key=lambda c: c[0])
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    out = []
    for tok in s.split(' '):
        while '[' in tok:
            pre, rest = tok.split('[', 1); mid, post = rest.split(']', 1)
            if pre: out.append((pre, False, True))
            out.append((mid, True, bool(post))); tok = post
        if tok: out.append((tok, False, False))
    return out
def caption(c, words, hl, y=1060, size=44, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k, g in words]; gaps = [0 if g else sp for w, k, g in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(gaps[i-1] if cur else 0)
        if cur and cw+need > 760 and not words[i-1][2]: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(l for _, l in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, INK, .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k, g = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, NAVY if hl == GOLD else 'FFFFFF', 'l', a)
            else: text(c, w, x, yy, 'b', size, 'FFFFFF', 'l', a)
            x += wd[i]+gaps[i]
def cap_layer(cv, t):
    k = None
    for i, cc in enumerate(CAPS):
        if t >= cc[0]: k = i
    if k is None or not CAPS[k][1]: return
    st0, s_, hl = CAPS[k]; a = ease((t-st0)/.12)
    nxt = CAPS[k+1][0] if k+1 < len(CAPS) else DUR
    if k+1 >= len(CAPS) or not CAPS[k+1][1]: a *= 1-ease((t-(nxt-.15))/.15)
    s, c = surface(); caption(c, parse(s_), hl, a=a); cv.alpha_composite(to_img(s))

# ---------- Mister Coin revient dans le souterrain (classique, de face), en bondissant depuis le bas ----------
EXP, INQ, CONF, TRI, ENT, QUES = 'classique_parle_explique', 'classique_parle_inquiet', 'classique_parle_confidence', 'classique_parle_triste', 'classique_parle_enthousiaste', 'classique_parle_question'
T_MC = 29.9
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(T_MC, EXP, 'voix'), (V5+10.6, INQ, 'voix'), (V5+29.0, CONF, 'voix'), (V5+46.2, TRI, 'voix'), (V5+59.9, ENT, 'voix'), (V5+65.8, QUES, 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin(cv, t):
    if t < T_MC: return cv
    k = t-T_MC; jump = 0.0
    if k < .55: u = k/.55; jump = 520*(1-u)-260*math.sin(math.pi*u)              # il bondit dans le cadre depuis le bas
    X, Y = CX_COIN, FEET+MC.hop_dy(t)+jump
    rgb_, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx = (MC.feet_x(al, Y) if Y > FEET-30 else X) if (k > .5 and Y < H-30) else None
    if fx is not None:
        kk = 1/(1+max(0, FEET-Y)/150); m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (int(100*kk)+1, int(15*kk)+1), 0, 0, 360, .55*kk, -1)
        a *= (1-cv2.GaussianBlur(m, (0, 0), 9)[..., None])
    a = a*(1-al[..., None])+rgb_*al[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')

def frame(t):
    cv = A.frame(t).convert('RGBA')
    cv = coin(cv, t)
    cap_layer(cv, t)
    return finish(cv, t, 2.0) if t > A.T_B else cv
def events():
    ev = [(A.DARK, 'impact'), (A.DARK+.02, 'glint'), (A.DARK+I_T, 'whoosh'), (A.DARK+I_T+1.1, 'glint'), (A.T_TXT, 'key'), (A.T_TXT+.4, 'key')]
    ev += G.events(A5)
    ev += [(T_MC+.1, 'hop')] + [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops) if h > T_MC+1]
    return sorted(ev)
I_T = A.I.T_JUMP
def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/f_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
