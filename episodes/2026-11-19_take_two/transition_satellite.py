"""Transition « changement de personnage » façon GTA, v2 (17/11) : rythme, étalonnage et son calqués sur la capture de Nicolas
(references/transition_gta.mp4, vidéo YouTube « google maps gta zoom effect », mesurée image par image et au spectre).
Mesures de la référence (secondes depuis le début de l'effet) :
  départ 0,73 s (vue de dessus, froide) ; trois paliers de montée toutes les 0,60 s (coupe nette, flash +40 %, aberration
  chromatique sur les bords) ; glissement latéral rapide 0,47 s ; survol tenu 2,57 s (dérive lente, image froide désaturée) ;
  (référence) descente : palier 1 vert léger 2,63 s, palier 2 vert franc 2,60 s, palier 3 jaune chaud 1,10 s ; plongée en rotation 1,15 s.
  Son : coup sourd très grave à 45–47 Hz sur chaque palier (attaque nette, corps vers 330 Hz, queue 0,4 s en montée, ~1 s en
  descente), bourdon grave (45 et 66 Hz) pendant le survol, souffle d'air discret (250–800 Hz, −30 dB) entre les paliers de
  descente, grand souffle aigu au début de la plongée, grondement jusqu'à l'arrivée.
On recrée tout avec nos images (cartes Gemini) et nos sons fabriqués : rien n'est repris du jeu ni de la capture.
image(u, depart, arrivee) ; son(sr) → stéréo ; python3 transition_satellite.py → tmp/transition_seule.wav"""
import os, functools
import numpy as np, cv2
from scipy import signal
D = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920

# ---------- calage (mesuré sur la référence) ----------
# version validée le 17/11 : temps tenus raccourcis (survol 0,9 s au lieu de 2,57 ; paliers verts 1,0 s au lieu de 2,6), le reste au rythme de la référence
TENU_SURVOL, TENU_D1, TENU_D2 = 0.9, 1.0, 1.0
T_DEP = 0.73; T_UP = [0.73, 1.33, 1.93]; T_GLI = 2.56; T_TEN = 3.03
T_D1 = T_TEN+TENU_SURVOL; T_D2 = T_D1+TENU_D1; T_D3 = T_D2+TENU_D2; T_PLO = T_D3+1.10; DUREE = T_PLO+1.15

@functools.lru_cache(maxsize=None)
def carte(nom):
    return cv2.cvtColor(cv2.imread(f'{D}/cartes/{nom}.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
def vue(nom, z=1.0, dx=0.0, dy=0.0, rot=0.0):
    """cadre 1080×1920 dans la carte : z = grossissement (1 = toute la largeur), dx/dy en fraction, rot en degrés"""
    c = carte(nom); h, w = c.shape[:2]; cw = w/z; s = W/cw
    cx, cy = w/2+dx*w, h/2+dy*h
    M = cv2.getRotationMatrix2D((cx, cy), rot, s); M[0, 2] += W/2-cx; M[1, 2] += H/2-cy
    return cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def ease(x): x = min(1, max(0, x)); return x*x*(3-2*x)

# ---------- étalonnage ----------
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_R = np.sqrt(((_xx-W/2)/(W/2))**2+((_yy-H/2)/(H/2))**2)
_VIG = np.clip(1-.30*_R**2, .45, 1)[..., None]
def grade(im, mode, k=1.0):
    g = im.mean(2, keepdims=True)
    if mode == 'froid':   o = (g+(im-g)*.30)*np.array((.96, 1.02, 1.04), np.float32)                 # gris bleuté désaturé
    elif mode == 'vert1': o = (g+(im-g)*.55)*np.array((1.00, 1.12, .82), np.float32)                 # vert-jaune léger
    elif mode == 'vert2': o = ((g+(im-g)*.6)*np.array((.98, 1.22, .70), np.float32)-128)*1.12+128     # vert franc, contraste
    elif mode == 'chaud': o = (g+(im-g)*.75)*np.array((1.12, 1.08, .74), np.float32)+10              # jaune chaud, lumière de jour
    else: o = im
    return im*(1-k)+o*k
def aberration(im, a):
    """décalage radial du rouge et du bleu (bords irisés), a ≈ 0,01"""
    if a < 1e-3: return im
    out = im.copy()
    for ch, s in ((0, 1+a), (2, 1-a)):
        M = cv2.getRotationMatrix2D((W/2, H/2), 0, s); out[..., ch] = cv2.warpAffine(im[..., ch], M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out
def finition(im, u, onsets, flash=.40):
    """à chaque palier : flash bref (+40 %) et aberration forte qui retombent en 0,3 s ; aberration légère permanente ; vignette ; grain"""
    k = max([0.0]+[np.exp(-(u-t)/.10) for t in onsets if u >= t])
    im = aberration(im, .004+.016*k)
    im = im*(1+flash*k)
    rng = np.random.default_rng(int(u*1000)); im = im+rng.normal(0, 4, (H//2, W//2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    return np.clip(im*_VIG, 0, 255)
def flou_dir(im, dx):
    """flou de bougé horizontal (glissement)"""
    n = int(abs(dx))
    if n < 2: return im
    k = np.zeros((1, n), np.float32); k[:] = 1/n; return cv2.filter2D(im, -1, k)

def image(u, depart, arrivee):
    ON = [T_DEP]+T_UP[1:]+[T_D1, T_D2, T_D3]
    if u < T_DEP:                                                   # départ : la scène vire au froid et recule
        k = ease(u/T_DEP); im = depart(u)
        M = cv2.getRotationMatrix2D((W/2, H/2), 0, 1-.08*k); im = cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        return finition(grade(im, 'froid', min(1, u/.25)), u, [0.0], flash=.25)
    if u < T_UP[1]: im = grade(vue('carte_rue', 1.30-.10*(u-T_UP[0])/.6), 'froid')
    elif u < T_UP[2]: im = grade(vue('carte_quartier', 1.25-.10*(u-T_UP[1])/.6), 'froid')
    elif u < T_GLI: im = grade(vue('carte_ville_v2_oblique_midi', 1.20-.06*(u-T_UP[2])/.63, dx=-.08), 'froid')
    elif u < T_TEN:                                                 # glissement latéral rapide, flou de bougé
        g = ease((u-T_GLI)/(T_TEN-T_GLI)); v = np.sin(np.pi*g)
        im = flou_dir(grade(vue('carte_ville_v2_oblique_midi', 1.14, dx=-.08+.16*g), 'froid'), 90*v)
    elif u < T_D1: im = grade(vue('carte_ville_v2_oblique_midi', 1.14+.05*(u-T_TEN)/(T_D1-T_TEN), dx=.08, dy=-.01*(u-T_TEN)), 'froid')
    elif u < T_D2: im = grade(vue('carte_quartier_marina', 1.00+.05*(u-T_D1)/(T_D2-T_D1), dy=.02), 'vert1')
    elif u < T_D3: im = grade(vue('carte_quartier_marina', 1.90+.08*(u-T_D2)/(T_D3-T_D2), dx=.04, dy=.05), 'vert2')
    elif u < T_PLO: im = grade(vue('carte_rue', 1.05+.06*(u-T_D3)/(T_PLO-T_D3)), 'chaud')             # carte de la rue : la plus détaillée, reste nette de près
    else:                                                           # plongée : zoom et rotation dans la carte, la scène arrive en tournant
        k = ease((u-T_PLO)/(DUREE-T_PLO))
        m = grade(vue('carte_rue', 1.11*(1+1.6*k**1.5), rot=-38*k), 'chaud')
        sc = arrivee(u); M = cv2.getRotationMatrix2D((W/2, H/2), 22*(1-k), 1+.7*(1-k))
        sc = cv2.warpAffine(sc, M, (W, H), borderMode=cv2.BORDER_REFLECT); sc = grade(sc, 'chaud', .5*(1-k))
        a = ease((k-.35)/.5); im = m*(1-a)+sc*a
        out = finition(im, u, ON); fin = ease((k-.75)/.25)       # l'image se « nettoie » (vignette et grain retirés) à l'arrivée
        return out*(1-fin)+np.clip(sc, 0, 255)*fin
    return finition(im, u, ON)

# ---------- son (fabriqué) ----------
def _bp(x, sr, lo, hi, o=4): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=sr, output='sos'), x)
def _lp(x, sr, f, o=4): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=sr, output='sos'), x)
def _hp(x, sr, f, o=4): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=sr, output='sos'), x)
def coup(sr, queue=.45, gain=1.0, rng=None, punch=0.0, brillance=.18):
    """coup sourd du palier : sous-grave 46 Hz (léger glissement de 62 à 46 Hz à l'attaque), harmonique, corps à 330 Hz, attaque claire"""
    rng = rng or np.random.default_rng(1); d = queue*4+.2; n = int(d*sr); t = np.arange(n)/sr
    f = 46+16*np.exp(-t/.035); ph = 2*np.pi*np.cumsum(f)/sr
    env = (1-np.exp(-t/.004))*np.exp(-t/queue)
    sub = np.tanh(1.6*(np.sin(ph)+.28*np.sin(2*ph+.4)))*env
    corps = _bp(rng.standard_normal(n), sr, 220, 480)*np.exp(-t/(queue*.45)); corps /= np.abs(corps).max()+1e-9
    clic = _hp(rng.standard_normal(n), sr, 1800)*np.exp(-t/.010); clic /= np.abs(clic).max()+1e-9
    mid = _bp(rng.standard_normal(n), sr, 600, 2200)*np.exp(-t/(queue*.6)); mid /= np.abs(mid).max()+1e-9    # grain médium du coup
    p = np.sin(2*np.pi*np.cumsum(88+30*np.exp(-t/.02))/sr)*(1-np.exp(-t/.003))*np.exp(-t/.09)   # « punch » vers 88 Hz (paliers de descente)
    return (sub*.95+corps*.10*(1-np.exp(-t/.003))+clic*brillance+p*punch+mid*.06)*gain
def bourdon(sr, d, rng=None):
    rng = rng or np.random.default_rng(2); n = int(d*sr); t = np.arange(n)/sr
    x = np.sin(2*np.pi*45.5*t)+.8*np.sin(2*np.pi*66*t+1)+.45*np.sin(2*np.pi*132*t+2)+.35*_lp(rng.standard_normal(n), sr, 160)*3
    am = .75+.25*np.sin(2*np.pi*.7*t); env = np.minimum(1, t/.4)*np.minimum(1, np.maximum(0, d-t)/.5)
    return np.tanh(x*.8)*am*env*.45
def air(sr, d, rng=None):
    rng = rng or np.random.default_rng(3); n = int(d*sr); t = np.arange(n)/sr
    x = _bp(rng.standard_normal(n), sr, 220, 850); x /= np.abs(x).max()+1e-9
    env = np.minimum(1, t/.8)*np.minimum(1, np.maximum(0, d-t)/.3)*(.8+.2*np.sin(2*np.pi*.35*t))
    return x*env*.075
def souffle(sr, d, rng=None, lo=1500, hi=12000):
    """souffle (glissement, début de plongée) : bruit filtré qui enfle puis retombe"""
    rng = rng or np.random.default_rng(4); n = int(d*sr); t = np.linspace(0, 1, n)
    x = _bp(rng.standard_normal(n), sr, lo, hi); x /= np.abs(x).max()+1e-9
    return x*np.sin(np.pi*t)**2*.5
def reverbe(x, sr, d=1.6, mix=.22, seed=5):
    """réverbération synthétique (bruit à décroissance exponentielle, assombri), stéréo décorrélée"""
    rng = np.random.default_rng(seed); n = int(d*sr); t = np.arange(n)/sr; outs = []
    for ch in range(2):
        ir = _lp(rng.standard_normal(n), sr, 3500)*np.exp(-t/(d/6.9)); ir /= np.sqrt((ir**2).sum())
        outs.append(signal.fftconvolve(x, ir)[:len(x)])
    return np.stack([x*(1-mix)+outs[0]*mix*3, x*(1-mix)+outs[1]*mix*3], 1)
def son(sr=48000):
    rng = np.random.default_rng(11); L = int((DUREE+1.5)*sr); out = np.zeros(L, np.float64)
    def pose(x, t, g=1.0):
        a = int(t*sr); b = min(L, a+len(x)); out[a:b] += x[:b-a]*g
    pose(coup(sr, .35, .8, rng), 0.0)                                    # départ
    for t in T_UP: pose(coup(sr, .30, 1.0, rng), t)                       # trois paliers de montée
    pose(souffle(sr, T_TEN-T_GLI+.15, rng, 400, 6000), T_GLI-.05, .7); pose(coup(sr, .30, .55, rng), T_GLI+.15)
    pose(bourdon(sr, T_D1-T_GLI+.3, rng), T_GLI)                          # survol
    for t, nxt in ((T_D1, T_D2), (T_D2, T_D3)):                           # paliers de descente : coup long puis souffle d'air
        pose(coup(sr, .30, 1.0, rng, punch=.7, brillance=.45), t); pose(air(sr, nxt-t-.5, rng), t+.5)
    pose(coup(sr, .35, 1.0, rng, punch=.5, brillance=.3), T_D3); pose(souffle(sr, .45, rng, 600, 7000), T_D3+.08, .9)
    pose(bourdon(sr, DUREE-T_D3+.4, rng)*.8, T_D3+.3)                    # grondement jusqu'à l'arrivée
    pose(souffle(sr, DUREE-T_PLO+.2, rng, 300, 3000), T_PLO, .18); pose(coup(sr, .5, .7, rng), DUREE)
    st = reverbe(out, sr); return st/np.abs(st).max()*10**(-1/20)

if __name__ == '__main__':
    import wave
    os.makedirs(f'{D}/tmp', exist_ok=True); s = son()
    with wave.open(f'{D}/tmp/transition_seule.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((s*32767).astype(np.int16).tobytes())
    print('son ok', round(len(s)/48000, 2), 's')

def demo(avant=1.5, apres=2.5, fps=30, nom='demo_transition'):
    """démo de la transition seule (bruitages seuls) : la jetée de Los Angeles, la transition, la rue de Miami"""
    import subprocess, wave
    def plan(n, t0):
        cap = cv2.VideoCapture(f'{D}/plans/{n}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, int(t0*24)); ok, f = cap.read(); cap.release()
        return cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    dep = lambda u: plan('mc_pier', 2.0+u); arr = lambda u: plan('mc_billets', 1.0+(u-DUREE))
    sr = 48000; s = son(sr); tot = avant+DUREE+apres; a = np.zeros((int(tot*sr), 2)); k = int(avant*sr); n = min(len(s), len(a)-k); a[k:k+n] = s[:n]
    with wave.open(f'{D}/tmp/{nom}.wav', 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a*32767).astype(np.int16).tobytes())
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                           '-i', f'{D}/tmp/{nom}.wav', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', f'{D}/{nom}.mp4'], stdin=subprocess.PIPE)
    for i in range(int(tot*fps)):
        t = i/fps; u = t-avant
        im = dep(u) if u < 0 else (image(u, dep, arr) if u < DUREE else arr(u))
        ff.stdin.write(np.clip(im, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('démo ok', nom)
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'demo': demo()

# ---------- mini-transition « retour en 2026 » (17/11) : deux paliers en 1,5 s, même langage que la grande ----------
MINI = 1.5; M_UP = [0.30, 0.72]; M_PLO = 1.05
def mini_image(u, depart, arrivee):
    if u < M_UP[0]:
        k = ease(u/M_UP[0]); im = depart(u); M = cv2.getRotationMatrix2D((W/2, H/2), 0, 1-.08*k)
        return finition(grade(cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT), 'froid', k), u, [0.0], flash=.25)
    if u < M_UP[1]: im = grade(vue('carte_quartier', 1.22-.08*(u-M_UP[0])/.42), 'froid')
    elif u < M_PLO: im = grade(vue('carte_ville_v2_oblique_midi', 1.16-.05*(u-M_UP[1])/.33, dx=.04), 'vert1')
    else:
        k = ease((u-M_PLO)/(MINI-M_PLO)); m = grade(vue('carte_ville_v2_oblique_midi', 1.11*(1+1.8*k**1.5), dx=.04, rot=-30*k), 'chaud')
        sc = arrivee(u); M = cv2.getRotationMatrix2D((W/2, H/2), 18*(1-k), 1+.6*(1-k)); sc = cv2.warpAffine(sc, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        a = ease((k-.3)/.5); out = finition(m*(1-a)+sc*a, u, M_UP); fin = ease((k-.7)/.3)
        return out*(1-fin)+np.clip(sc, 0, 255)*fin
    return finition(im, u, M_UP)
def mini_son(sr=48000):
    rng = np.random.default_rng(21); L = int((MINI+1.2)*sr); out = np.zeros(L)
    def pose(x, t, g=1.0):
        a = int(t*sr); b = min(L, a+len(x)); out[a:b] += x[:b-a]*g
    pose(coup(sr, .30, .7, rng), 0.0)
    for t in M_UP: pose(coup(sr, .30, 1.0, rng), t)
    pose(souffle(sr, MINI-M_PLO+.15, rng, 500, 6000), M_PLO-.05, .6); pose(coup(sr, .45, .75, rng, punch=.4), MINI)
    st = reverbe(out, sr); return st/np.abs(st).max()*10**(-1/20)
