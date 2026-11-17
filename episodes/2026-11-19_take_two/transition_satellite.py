"""Transition « changement de personnage » façon GTA, recréée avec nos images (prompts_gemini.md, 16/11) :
la scène part vers le haut, trois paliers de carte de plus en plus haut (rue, quartier, ville), un court survol,
puis trois paliers de descente vers la scène suivante. Voile vert-gris et grille de carte sur les vues satellite.
Images : cartes/carte_rue, carte_quartier, carte_ville_v2_oblique_midi, carte_quartier_marina (Gemini, 1438×2576).
image(u, depart, arrivee) : u en secondes depuis le début de la transition (durée DUREE), depart/arrivee = fonctions u → image 1080×1920.
son(sr) : bruitages fabriqués (aucun son du jeu) : whoosh montant, impacts sourds à chaque palier, souffle du survol, whoosh descendants.
python3 transition_satellite.py → tmp/transition_seule.wav (écoute du son seul)"""
import os, functools
import numpy as np, cv2
D = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
DUREE = 2.2
# paliers (u de début) : montée, rue, quartier, ville + survol, marina, marina ×2, plongée vers la scène
P_RUE, P_QUA, P_VIL, P_MAR, P_MA2, P_PLO = .35, .60, .85, 1.35, 1.60, 1.85

@functools.lru_cache(maxsize=None)
def carte(nom):
    return cv2.cvtColor(cv2.imread(f'{D}/cartes/{nom}.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
def vue(nom, z=1.0, dx=0.0, dy=0.0, flou=0.0):
    """cadre 1080×1920 dans la carte : z = grossissement (1 = toute la largeur), dx/dy = décalage en fraction de largeur/hauteur"""
    c = carte(nom); h, w = c.shape[:2]; cw, ch = w/z, w/z*H/W
    cx, cy = w/2+dx*w, h/2+dy*h
    M = np.float32([[W/cw, 0, -(cx-cw/2)*W/cw], [0, W/cw, -(cy-ch/2)*W/cw]])
    im = cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if flou > .3: im = cv2.GaussianBlur(im, (0, 0), flou)
    return im
def voile(im, force=1.0):
    """voile vert-gris et grille de carte (vue satellite du jeu, recréée)"""
    g = im.mean(2, keepdims=True); v = im*.5+g*.5; v = v*.78+np.array((92, 118, 104), np.float32)*.22
    grille = np.zeros((H, W), np.float32)
    for x in range(30, W, 120): grille[:, x:x+2] = 1
    for y in range(0, H, 120): grille[y:y+2] = 1
    v = v*(1-.18*grille[..., None])+235*.18*grille[..., None]
    yy, xx = np.mgrid[0:H, 0:W]; vig = 1-.35*(((xx-W/2)/(W*.75))**2+((yy-H/2)/(H*.75))**2)
    v = v*vig[..., None]
    return im*(1-force)+v*force
def zoom_img(im, s, flou=0.0):
    """agrandit (s > 1) ou rapetisse (s < 1) une image plein cadre autour du centre"""
    M = cv2.getRotationMatrix2D((W/2, H/2), 0, s)
    o = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.GaussianBlur(o, (0, 0), flou) if flou > .3 else o
def ease(x): x = min(1, max(0, x)); return 1-(1-x)**3
def flash(im, u, t0, d=.07, a=.35):
    """bref voile clair à l'arrivée d'un palier (ressenti d'impact)"""
    k = max(0, 1-(u-t0)/d) if u >= t0 else 0
    return im*(1-a*k)+255*a*k
def image(u, depart, arrivee):
    if u < P_RUE:                                   # la scène s'envole : zoom arrière rapide puis fondu vers la rue vue d'en haut
        k = ease(u/P_RUE); s_ = 1-.55*k                # la scène rapetisse et s'enfonce dans la carte (pas de bords en miroir)
        M = cv2.getRotationMatrix2D((W/2, H/2), 0, s_)
        sc = cv2.warpAffine(depart(u), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        m = cv2.warpAffine(np.ones((H, W), np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if k > .05: sc = cv2.GaussianBlur(sc, (0, 0), 5*k); m = cv2.GaussianBlur(m, (0, 0), 3)
        rue = voile(vue('carte_rue', 1.5-.25*k, flou=4*(1-k)))
        a = m*(1-min(1, max(0, (u-.2)/.15)))
        return sc*a[..., None]+rue*(1-a[..., None])
    if u < P_QUA: im = voile(vue('carte_rue', 1.12-.12*ease((u-P_RUE)/.12))); return flash(im, u, P_RUE)
    if u < P_VIL: im = voile(vue('carte_quartier', 1.12-.12*ease((u-P_QUA)/.12))); return flash(im, u, P_QUA)
    if u < P_MAR:                                   # sommet : la ville, brève, floutée par le mouvement, avec un glissement latéral
        g = (u-P_VIL)/(P_MAR-P_VIL); im = voile(vue('carte_ville_v2_oblique_midi', 1.08-.08*ease(g*3), dx=-.06+.12*g, flou=2.5))
        return flash(im, u, P_VIL)
    if u < P_MA2: im = voile(vue('carte_quartier_marina', 1.0+.12*ease((u-P_MAR)/.25))); return flash(im, u, P_MAR)
    if u < P_PLO: im = voile(vue('carte_quartier_marina', 1.9+.15*ease((u-P_MA2)/.25), dy=.05)); return flash(im, u, P_MA2)
    k = ease((u-P_PLO)/(DUREE-P_PLO))               # plongée : zoom avant dans la carte, fondu vers la scène d'arrivée qui se pose
    m = voile(vue('carte_quartier_marina', 2.05+2.5*k, dy=.05, flou=5*k), 1-k)
    sc = zoom_img(arrivee(u), 1.6-.6*k, flou=5*(1-k))
    a = min(1, max(0, (k-.35)/.5)); return m*(1-a)+sc*a

# ---------- son ----------
def _bruit(n, rng): return rng.standard_normal(n).astype(np.float32)
def _passe_bande(x, sr, f_lo, f_hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/sr); X[(f < f_lo) | (f > f_hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def whoosh(sr, d, monte=True, rng=None):
    rng = rng or np.random.default_rng(1); n = int(d*sr); x = _bruit(n, rng); out = np.zeros(n, np.float32); B = 8
    for i in range(B):                              # balayage de bande : bruit filtré dont la fréquence monte (ou descend)
        a, b = i*n//B, (i+1)*n//B; k = i/(B-1) if monte else 1-i/(B-1); fc = 250*(14**k)
        out[a:b] = _passe_bande(x, sr, fc*.6, fc*1.6)[a:b]
    t = np.linspace(0, 1, n); env = np.sin(np.pi*t)**1.5 if monte else (1-t)**1.2*np.minimum(1, t*12)
    return out*env/ (np.abs(out).max()+1e-6)
def impact(sr, fort=1.0, rng=None):
    rng = rng or np.random.default_rng(2); d = .38 if fort > 1 else .26; n = int(d*sr); t = np.arange(n)/sr
    f = 95*np.exp(-t*9)+38; ph = 2*np.pi*np.cumsum(f)/sr; boum = np.sin(ph)*np.exp(-t*(9 if fort > 1 else 14))
    clic = _passe_bande(_bruit(n, rng), sr, 600, 5000)*np.exp(-t*90)*.5
    return (boum+clic)*.9*fort
def survol(sr, d, rng=None):
    rng = rng or np.random.default_rng(3); n = int(d*sr); x = _passe_bande(_bruit(n, rng), sr, 120, 900)
    t = np.linspace(0, 1, n); return x/np.abs(x).max()*np.sin(np.pi*t)*.45
def son(sr=48000):
    rng = np.random.default_rng(7); out = np.zeros(int((DUREE+.6)*sr), np.float32)
    def pose(x, t, g=1.0):
        a = int(t*sr); b = min(len(out), a+len(x)); out[a:b] += x[:b-a]*g
    pose(whoosh(sr, .42, True, rng), 0, .55)
    for p in (P_RUE, P_QUA, P_VIL): pose(impact(sr, 1.0, rng), p, .55)
    pose(survol(sr, P_MAR-P_VIL+.1, rng), P_VIL, .5)
    for p in (P_MAR, P_MA2): pose(whoosh(sr, .22, False, rng), p-.05, .35); pose(impact(sr, 1.0, rng), p, .5)
    pose(whoosh(sr, DUREE-P_PLO, False, rng), P_PLO, .45); pose(impact(sr, 1.4, rng), DUREE, .7)
    return out
if __name__ == '__main__':
    import wave
    s = son(); s = s/max(1e-6, np.abs(s).max())*10**(-1/20)
    os.makedirs(f'{D}/tmp', exist_ok=True)
    with wave.open(f'{D}/tmp/transition_seule.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes((s*32767).astype(np.int16).tobytes())
    print('ok', len(s)/48000, 's')
