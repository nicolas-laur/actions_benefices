"""Maquettes de l'épisode Take-Two / GTA 6 (19/11/2026) : images clés de chaque scène et des transitions, DA « façon GTA 6 »
(docs/formats/gta.md). Décors et plans d'origine (720×1280) agrandis simplement : l'affinage Real-ESRGAN n'est pas encore fini.
Calage provisoire sur la voix en trois morceaux + la phrase du montant (≈ 5 s, pas encore enregistrée).
usage : python3 maquettes.py            → tmp/maq/*.png, maquettes_take_two.jpg (planche) et tmp/maq/planche_bd.jpg (contrôle)"""
import os, sys, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); R = f'{D}/../..'
sys.path.insert(0, f'{R}/mister_coin'); sys.path.insert(0, f'{R}/lib')
W, H = 1080, 1920
F_TIT = f'{R}/fonts/InterDisplay-ExtraBold.otf'    # police maison (Inter Display, comme les carrousels) ; Big Shoulders réservée à la couverture (17/11)
F_SUB = f'{R}/fonts/InterDisplay-Bold.otf'; F_ANT = f'{R}/fonts/Anton-Regular.ttf'
CREME = (255, 244, 222)
F_MEN = f'{R}/fonts/InterDisplay-Bold.otf'
INK = (25, 8, 35); GOLD = (255, 214, 90); BORD = (38, 14, 58)

# ---------- calage provisoire (secondes) ----------
V1, V2, V3 = 8.28, 19.80, 28.53                      # durées des trois morceaux reçus le 17/11
# Découpage validé le 17/11 : plans Veo de 4 à 6 s, transition satellite d'environ 8 s sans voix (musique et bruitages).
# La voix est découpée en segments posés sur l'image : (fichier, début source, fin source, début dans la vidéo).
T_VEN, T_CAB, T_PIE = 1.5, 5.6, 9.8                    # mosaïque 0–1,5 s, puis Venice, cabriolet, jetée
TS = 14.8                                              # départ de la transition satellite (jetée de Los Angeles → rue de Miami)
import transition_satellite as TSAT
T_BIL = TS+TSAT.DUREE; T13 = T_BIL+6.0                 # Miami (pistolet à billets) puis la chambre de 2013
SEGS = [('voix_1_accroche', 0.00, 4.75, 0.00), ('voix_1_accroche', 4.75, 8.28, 5.65),
        ('voix_2', 0.00, 4.85, 9.90), ('voix_2', 4.85, 10.53, T_BIL+.30), ('voix_2', 10.53, 19.80, T13+.30)]
def pos(f, ts):
    """instant dans la vidéo d'un instant ts du fichier de voix f"""
    for (g, a, b, d) in SEGS:
        if g == f and a <= ts <= b: return d+ts-a
    raise ValueError((f, ts))
T2 = pos('voix_2', 0.0)
T_MINI = pos('voix_2', 19.80)+.25                      # mini-transition satellite 2013 → 2026 (1,5 s, sans voix)
TM = T_MINI+TSAT.MINI+.1; TMD = 6.95; T3 = TM+TMD+.3          # phrase du montant enregistrée le 17/11 (voix_montant, 6,9 s)
# Troisième morceau recomposé (17/11) : deux phrases remplacées par les nouvelles prises (voix_dix_millions, voix_ratio).
SEGS3 = [('voix_3', 0.00, 3.80, 0.00), ('voix_dix_millions', 0.00, 7.30, 4.05), ('voix_3', 9.60, 17.15, 11.55),
         ('voix_ratio', 0.00, 2.62, 19.40), ('voix_3', 19.45, 28.53, 22.25)]
V3N = 22.25+28.53-19.45
def p3(x):
    """instant (relatif à T3) de la nouvelle voix 3 correspondant à l'instant x de l'ancienne prise (calage d'origine des scènes)"""
    if x < 3.8: return x
    if x < 9.6: return 4.05+(x-3.8)*(7.30/5.8)
    if x < 17.15: return x+1.95
    if x < 19.45: return 19.40+(x-17.29)*(2.62/2.06) if x >= 17.29 else x+1.95
    return x+2.80
FIN = T3+V3N+2.7                                     # fin rallongée de 1,5 s (18/11)
OUTRO = 5.0; FIN_VID = FIN+OUTRO                   # outro « Abonne-toi » sur le pistolet à billets ralenti
# phrases (début, fin, texte, mot clé) — repérées sur les silences de chaque morceau
PH = [(0.00, 4.52, "GTA 6, le jeu le plus attendu de la décennie, sort aujourd'hui.", "aujourd'hui"),
      (pos('voix_1_accroche', 4.99), pos('voix_1_accroche', 7.94), "Savais-tu que l'entreprise derrière le jeu est cotée en bourse ?", "bourse"),
      (pos('voix_2', 0.0), pos('voix_2', 4.53), "Rockstar, le studio de GTA, appartient à Take-Two, cotée à New York.", "Take-Two"),
      (pos('voix_2', 5.17), pos('voix_2', 10.38), "Et si, en 2013, à la sortie de GTA 5, tu avais acheté l'action plutôt que le jeu ?", "l'action"),
      (pos('voix_2', 10.68), pos('voix_2', 14.6), "Ce jour-là, l'action vaut 17,70 $.", "17,70 $"),
      (pos('voix_2', 14.6), pos('voix_2', 19.8), "Le jeu pulvérise les records : 800 M$ de ventes en 24 h.", "800 M$"),
      (TM, TM+6.88, "Résultat : 1 000 € placés dans Take-Two ce jour-là valent aujourd'hui environ 14 100 €.", "14 100 €"),
      (T3+p3(0.00), T3+p3(3.66), "Pendant ce temps, ton vieux GTA 5 vaut quelques euros d'occasion.", "quelques euros"),
      (T3+4.05, T3+11.31, "Et GTA 6 démarre encore plus fort : plus de 10 millions de précommandes avant même la sortie.", "10 millions"),
      (T3+p3(9.78), T3+p3(12.68), "Alors, faut-il acheter l'action aujourd'hui ? Attention.", "Attention"),
      (T3+p3(12.98), T3+p3(16.84), "En 2013, Take-Two valait 1,4 fois ses ventes annuelles.", "1,4 fois"),
      (T3+19.40, T3+21.98, "Aujourd'hui, 5,8 fois.", "5,8 fois"),
      (T3+p3(19.62), T3+p3(21.42), "Le succès est déjà dans le prix :", "dans le prix"),
      (T3+p3(21.74), T3+p3(26.20), "GTA 6 peut tout casser… et l'action quand même décevoir.", "décevoir"),
      (T3+p3(26.67), T3+p3(28.28), "Et toi, tu as acheté GTA 6 ?", "GTA 6")]
MONTANT = os.environ.get('MONTANT', '14 140')       # provisoire : clôture du 16/11 (213,47 $), à remplacer par la clôture du 17/11

# ---------- lecture des clips ----------
class _Lecteur:
    """lecture séquentielle d'un clip (une recherche par image coûte un décodage depuis l'image clé : trop lent pour le rendu)"""
    def __init__(self, path): self.cap = cv2.VideoCapture(path); self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)); self.i = -1; self.f = None
    def lire(self, i):
        if i == self.i: return self.f
        if not (self.i < i <= self.i+8): self.cap.set(cv2.CAP_PROP_POS_FRAMES, i); self.i = i-1
        while self.i < i: ok, f = self.cap.read(); self.i += 1; self.f = f if ok else self.f
        return self.f
_LECT = {}
@functools.lru_cache(maxsize=6)
def _image_clip(path, i):
    """image i du clip en 1080×1920 : version affinée Real-ESRGAN (decors/sr/<nom>/fNNNN.jpg) si elle existe, sinon agrandie"""
    nom = os.path.basename(path)[:-4]; sr = f'{D}/decors/sr/{nom}/f{i:04d}.jpg'
    if os.path.exists(sr): return cv2.cvtColor(cv2.imread(sr), cv2.COLOR_BGR2RGB).astype(np.float32)
    if path not in _LECT: _LECT[path] = _Lecteur(path)
    f = _LECT[path].lire(i)
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    return np.clip(g+.25*(g-cv2.GaussianBlur(g, (0, 0), 1.2)), 0, 255)
UTILISES = {}                                     # relevé des images de clip réellement utilisées (pour n'affiner qu'elles)
def frame(path, t, debut=0.0, vitesse=1.0):
    if path not in _LECT: _LECT[path] = _Lecteur(path)
    i = int(min(_LECT[path].n-1, max(0, (t-debut)*vitesse*24)))
    UTILISES.setdefault(path, set()).add(i)
    return _image_clip(path, i).copy()
def dec(n): return f'{D}/decors/{n}.mp4'
def pl(n): return f'{D}/plans/{n}.mp4'

# ---------- Mister Coin (clips classiques, détourés) ----------
@functools.lru_cache(maxsize=1)
def coin():
    """Mister Coin classique : il parle quand la voix parle (voix provisoire, trou de 5 s pour la phrase du montant)"""
    import veo_coin as VC
    return VC.VeoCoin([(T13, ['classique_parle_explique', 'classique_parle_enthousiaste'], 'voix'),
                       (TM, ['classique_danse_parle_billets', 'classique_parle_enthousiaste'], 'voix'),
                       (T3+p3(9.6), ['classique_parle_inquiet', 'classique_parle_confidence', 'classique_parle_explique'], 'voix')],
                      voix=f'{D}/voix/voice_provisoire.wav', x=540, pieds=1650, largeur_piece=230, duree=FIN, lisse=True)
def pose(img, clip, tl):
    rgb, a = coin().layer(T_ABS[0])
    return img*(1-a[..., None])+rgb*a[..., None]
T_ABS = [0.0]
REG = {'verres': [], 'objets': []}            # contrôle automatique : chaque texte ou graphique posé sur un verre doit rester dans son intérieur

# ---------- textes DA GTA ----------
@functools.lru_cache(maxsize=None)
def font(p, s): return ImageFont.truetype(p, s)
def texte(img, s, y, taille, police=F_TIT, coul=(255, 255, 255), contour=7, x=None, ombre=True, alpha=1.0):
    """texte centré (ou à partir de x), contour violet-noir et ombre portée floue"""
    if alpha <= 0: return img
    f = font(police, taille); bb = f.getbbox(s, stroke_width=contour); w = bb[2]-bb[0]
    X = (W-w)//2-bb[0] if x is None else x
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if ombre is True:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((X+6, y+9), s, font=f, fill=(10, 0, 20, 170), stroke_width=contour, stroke_fill=(10, 0, 20, 170))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(7))); d = ImageDraw.Draw(lay)
    d.text((X, y), s, font=f, fill=coul+(255,), stroke_width=contour, stroke_fill=INK+(255,))
    a = np.asarray(lay).astype(np.float32); m = a[..., 3:]/255*alpha
    bx = np.asarray(lay.getchannel('A')).nonzero()
    if len(bx[0]) and ombre is not None: REG['objets'].append((s, bx[1].min(), bx[0].min(), bx[1].max(), bx[0].max()))
    return img*(1-m)+a[..., :3]*m
def A(img, s, y, taille, coul=CREME, x=None):
    """gros mot façon carrousel (« BCE ») : Anton, crème ou or, sans contour, ombre douce"""
    return texte(img, s, y, taille, police=F_ANT, coul=coul, contour=0, x=x)
def I(img, s, y, taille, coul=(255, 255, 255), x=None):
    """phrase façon carrousel : Inter Display ExtraBold, sans contour, ombre douce"""
    return texte(img, s, y, taille, police=F_TIT, coul=coul, contour=0, x=x)
def pill(img, s, y, taille=40):
    """pastille jaune des carrousels (« Banque centrale européenne ») : texte encre sur fond or arrondi"""
    w = largeur(s, taille, F_TIT, 0)+64; x0 = (W-w)//2; hh = int(taille*1.7)
    m = np.zeros((H, W), np.uint8); cv2.rectangle(m, (x0+hh//2, y), (x0+w-hh//2, y+hh), 255, -1)
    cv2.circle(m, (x0+hh//2, y+hh//2), hh//2, 255, -1, cv2.LINE_AA); cv2.circle(m, (x0+w-hh//2, y+hh//2), hh//2, 255, -1, cv2.LINE_AA)
    a = m[..., None]/255; img = img*(1-a)+np.array((255, 196, 74), np.float32)*a
    return texte(img, s, y+int(hh*.16), taille, police=F_TIT, coul=INK, contour=0, ombre=False)
def emoji_(img, ch, cx, cy, taille):
    """émoji Noto (fonts/NotoColorEmoji.ttf, comme les carrousels)"""
    f = ImageFont.truetype(f'{R}/fonts/NotoColorEmoji.ttf', 109); e = Image.new('RGBA', (180, 180), 0)    # même rendu que lib/carrousel.py
    ImageDraw.Draw(e).text((10, 10), ch, font=f, embedded_color=True); e = e.crop(e.getbbox()); e = e.resize((taille, int(taille*e.height/e.width)), Image.LANCZOS)
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    cv.alpha_composite(e, (int(cx-e.width/2), int(cy-e.height/2))); REG['objets'].append((ch, int(cx-e.width/2), int(cy-e.height/2), int(cx+e.width/2), int(cy+e.height/2)))
    return np.asarray(cv.convert('RGB')).astype(np.float32)
@functools.lru_cache(maxsize=None)
def _tuile(nom, taille):
    im = Image.open(f'{D}/logos/{nom}.png').convert('RGBA').resize((taille, taille), Image.LANCZOS); return im
def tuile(img, nom, x, y, taille):
    """tuile logo façon icône d'appli (logos/, tirée des favicons via Simple Icons), ombre douce"""
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA'); t = _tuile(nom, taille)
    sh = Image.new('RGBA', cv.size, 0); sh.paste((10, 0, 20, 150), (x+4, y+6, x+taille+4, y+taille+6), t.getchannel('A'))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); cv.alpha_composite(t, (x, y))
    REG['objets'].append((nom, x, y, x+taille, y+taille)); return np.asarray(cv.convert('RGB')).astype(np.float32)
def fleche_simple(img, cx, y0, y1, coul=(255, 255, 255)):
    """flèche fine et sobre vers le bas : un trait et deux branches, bouts arrondis, ombre douce (18/11)"""
    pts = [((cx, y0), (cx, y1)), ((cx-20, y1-20), (cx, y1)), ((cx+20, y1-20), (cx, y1))]
    sh = np.zeros((H, W), np.float32)
    for a_, b_ in pts: cv2.line(sh, (a_[0], a_[1]+4), (b_[0], b_[1]+4), 1.0, 10, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), 5)*.5; img = img*(1-sh[..., None])+np.array((10, 0, 20), np.float32)*sh[..., None]
    for a_, b_ in pts: cv2.line(img, a_, b_, coul, 6, cv2.LINE_AA)
    REG['objets'].append(('flèche', cx-26, y0, cx+26, y1+6)); return img
def tendance(img, cx, cy, monte, k=1.0):
    """flèche de tendance épaisse, verte qui monte ou rouge qui descend, qui se trace de gauche à droite"""
    c = (90, 220, 120) if monte else (240, 80, 80); L = 150; d = -1 if monte else 1
    x0, y0 = cx-L//2, cy-d*45; x1, y1 = int(x0+L*k), int(y0+d*90*k)
    cv2.line(img, (x0, y0), (x1, y1), INK, 30, cv2.LINE_AA); cv2.line(img, (x0, y0), (x1, y1), c, 18, cv2.LINE_AA)
    if k > .6:
        ang = np.arctan2(y1-y0, x1-x0); p = np.array([(x1+30*np.cos(ang), y1+30*np.sin(ang)), (x1+26*np.cos(ang+2.4), y1+26*np.sin(ang+2.4)), (x1+26*np.cos(ang-2.4), y1+26*np.sin(ang-2.4))], np.int32)
        cv2.fillPoly(img, [p], c, cv2.LINE_AA)
    REG['objets'].append(('tendance', x0-15, min(y0, y1)-20, x0+L+30, max(y0, y1)+20)); return img
def largeur(s, taille, police=F_TIT, contour=7): bb = font(police, taille).getbbox(s, stroke_width=contour); return bb[2]-bb[0]
def fleche(img, cx, cy, l=70, e=34, bas=False):
    q = [(-l/2, -e*.32), (l*.12, -e*.32), (l*.12, -e*.62), (l/2, 0), (l*.12, e*.62), (l*.12, e*.32), (-l/2, e*.32)]
    p = np.array([(cx-v, cy+u) if bas else (cx+u, cy+v) for (u, v) in q], np.int32)
    m = np.zeros((H, W), np.uint8); cv2.polylines(m, [p], True, 255, 14, cv2.LINE_AA); cv2.fillPoly(m, [p], 255)
    f = np.zeros((H, W), np.uint8); cv2.fillPoly(f, [p], 255, cv2.LINE_AA)
    img = img*(1-m[..., None]/255)+np.array(INK, np.float32)*(m[..., None]/255)
    return img*(1-f[..., None]/255)+np.array(GOLD, np.float32)*(f[..., None]/255)
def plaque(img, x0, y0, x1, y1, a=.55):
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (x0, y0), (x1, y1), 1, -1); m = cv2.GaussianBlur(m, (0, 0), 3)*a
    return img*(1-m[..., None])+np.array(INK, np.float32)*m[..., None]

def verre(img, x, y, w, h, mood='or'):
    """panneau de verre épais translucide (lib/verre_epais.py) : le décor se réfracte dans le biseau, lumière qui traverse"""
    from verre_epais import thick_panel, MOODS
    cv = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    thick_panel(cv, x, y, w, h, r=46, bevel=40, frost=22, dim=.55, **MOODS[mood]); REG['verres'].append((x, y, x+w, y+h))
    return np.asarray(cv.convert('RGB')).astype(np.float32)

# ---------- sous-titres mot à mot (ligne de 760 px max, y ≈ 1040, mot clé en jaune) ----------
def _rr(img, x0, y0, x1, y1, r, coul, a):
    """rectangle arrondi plein, fondu dans l'image"""
    m = np.zeros((H, W), np.uint8); x0, y0, x1, y1, r = map(int, (x0, y0, x1, y1, r))
    cv2.rectangle(m, (x0+r, y0), (x1-r, y1), 255, -1); cv2.rectangle(m, (x0, y0+r), (x1, y1-r), 255, -1)
    for cx, cy in ((x0+r, y0+r), (x1-r, y0+r), (x0+r, y1-r), (x1-r, y1-r)): cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    m = m[..., None]/255*a; return img*(1-m)+np.array(coul, np.float32)*m
def sous_titre(img, t):
    """sous-titres comme les épisodes précédents (loto) : la ligne entière toujours centrée sur x = 540, sur une plaque arrondie ;
    mot à mot = les mots déjà dits en blanc plein, les suivants estompés ; mot clé sur une pastille or une fois dit"""
    ph = next((p for p in PH if p[0] <= t < p[1]+.15), None)
    if ph is None: return img
    a, b, s, cle = ph; mots = s.split(' '); T = 46; PAD = 18
    cles = set(cle.split(' '))
    bruts = [(m, m.strip(',.:?…') in cles) for m in mots]
    mots, est_cle = [], []                                                      # mots clés consécutifs regroupés dans une seule pastille (18/11)
    for m, c in bruts:
        if c and est_cle and est_cle[-1]: mots[-1] += ' '+m
        else: mots.append(m); est_cle.append(c)
    k = max(1, min(len(mots), int((t-a)/max(.1, b-a)*len(mots))+1))         # mot courant (réparti à la longueur, en attendant un calage fin)
    wd = [largeur(m, T, F_SUB, 0)+(2*PAD if c else 0) for m, c in zip(mots, est_cle)]; sp = largeur(' ', T, F_SUB, 0)+4
    lignes, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 760: lignes.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lignes.append((cur, cw))
    li = next(j for j, (idx, _) in enumerate(lignes) if k-1 in idx)                # une seule ligne à l'écran : celle du mot courant
    idx, lw = lignes[li]; x = 540-lw/2; y = 1020
    img = _rr(img, x-30, y-14, x+lw+30, y+T+30, 26, INK, .72)
    for i in idx:
        dit = i < k
        if est_cle[i] and dit:
            img = _rr(img, x, y-8, x+wd[i], y+T+22, 14, (255, 196, 74), 1.0)
            img = texte(img, mots[i], y-2, T, police=F_SUB, coul=INK, contour=0, x=int(x+PAD), ombre=None)
        else:
            img = texte(img, mots[i], y-2, T, police=F_SUB, coul=(255, 255, 255), contour=0, x=int(x+(PAD if est_cle[i] else 0)), ombre=None, alpha=1.0 if dit else .42)
        x += wd[i]+sp
    return img

# ---------- cadre façon écran de chargement ----------
def cadre(img, ep=16):
    m = np.ones((H, W), np.float32); m[ep:H-ep, ep:W-ep] = 0
    return img*(1-m[..., None])+np.array(BORD, np.float32)*m[..., None]
def grille(cases, t):
    """écran de chargement : 3 cases de BD inclinées sur fond violet"""
    img = np.zeros((H, W, 3), np.float32)+np.array(BORD, np.float32)
    zones = [((24, 24), (1056, 700)), ((24, 724), (620, 1300)), ((644, 724), (1056, 1896)), ((24, 1324), (620, 1896))]
    for (src, tt), ((x0, y0), (x1, y1)) in zip(cases, zones):
        f = frame(src, tt); w, h = x1-x0, y1-y0; s = max(w/W, h/H); g = cv2.resize(f, (int(W*s)+1, int(H*s)+1))
        oy = (g.shape[0]-h)//2; ox = (g.shape[1]-w)//2; img[y0:y1, x0:x1] = g[oy:oy+h, ox:ox+w]
    return img
CASES = [((0, 0), (1080, 0), (1080, 610), (0, 690)), ((0, 690), (560, 648), (500, 1333), (0, 1360)),
         ((560, 648), (1080, 610), (1080, 1300), (500, 1333)), ((0, 1360), (1080, 1300), (1080, 1920), (0, 1920))]
def mosaique(t, plans=('mc_venice', 'mc_cabriolet', 'mc_billets', 'mc_poursuite'), tps=(1.0, 3.0, 2.5, 4.0)):
    """écran de chargement façon GTA : quatre cases de BD aux séparations obliques et bords violet foncé, nos propres plans"""
    img = np.zeros((H, W, 3), np.float32)+np.array(BORD, np.float32)
    for poly, nm, t0 in zip(CASES, plans, tps):
        pts = np.array(poly, np.int32); x0, y0 = pts.min(0); x1, y1 = pts.max(0); w, h = x1-x0, y1-y0
        f = frame(pl(nm), t0+t*.8); sc = max(w/W, h/H)*(1.06-.04*min(1, t)); g = cv2.resize(f, (int(W*sc)+2, int(H*sc)+2))
        oy, ox = (g.shape[0]-h)//2, (g.shape[1]-w)//2; m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [pts], 1.0, cv2.LINE_AA)
        tile = np.zeros_like(img); tile[y0:y1, x0:x1] = g[oy:oy+h, ox:ox+w]; img = img*(1-m[..., None])+tile*m[..., None]
    for a, b in (((0, 690), (1080, 610)), ((560, 648), (500, 1333)), ((0, 1360), (1080, 1300))):
        cv2.line(img, a, b, BORD, 26, cv2.LINE_AA)
    return img                                   # néons colorés annulés par Nicolas (17/11) : séparations violet foncé de la DA
ROSE, CYAN = (255, 60, 190), (40, 210, 255)
NEONS = [(((0, 690), (1080, 610)), ROSE, 0.0), (((560, 648), (500, 1333)), CYAN, .35), (((0, 1360), (1080, 1300)), ROSE, .7),
         (((16, 16), (1064, 16)), CYAN, .15), (((1064, 16), (1064, 1904)), ROSE, .5), (((1064, 1904), (16, 1904)), CYAN, .85), (((16, 1904), (16, 16)), ROSE, .3)]
def _screen(img, add):
    """fusion « écran » : la lumière s'ajoute sans brûler les couleurs"""
    a = np.clip(img, 0, 255)/255; b = np.clip(add, 0, 255)/255; return (1-(1-a)*(1-b))*255
def _eclat(lum, x, y, r, c, k):
    """étoile à quatre branches (reflet d'objectif) blanche, teintée de la couleur du tube"""
    for (dx, dy, L) in ((1, 0, r*2.6), (0, 1, r*2.6), (.7, .7, r*1.1), (.7, -.7, r*1.1)):
        p0 = (int(x-dx*L), int(y-dy*L)); p1 = (int(x+dx*L), int(y+dy*L))
        cv2.line(lum, p0, p1, tuple(float(min(255, 255*.75+v*.25))*k for v in c), 3, cv2.LINE_AA)
    cv2.circle(lum, (int(x), int(y)), int(r*.5), (255*k, 255*k, 255*k), -1, cv2.LINE_AA)
def neons(img, t, vitesse=.55, n=64):
    """séparations et cadre en tubes néon rose et bleu (DA de GTA 6), version lumineuse (17/11) :
    cœur blanc incandescent, gaine colorée, trois halos (serré, moyen, large) en fusion écran, lumière qui déborde sur les cases,
    éclats blancs qui glissent le long des tubes avec un reflet en étoile, léger scintillement"""
    gaine = np.zeros((H, W, 3), np.float32); coeur = np.zeros((H, W, 3), np.float32); etoiles = np.zeros((H, W, 3), np.float32)
    rng = np.random.default_rng(int(t*30))
    for j, ((a, b), c, ph) in enumerate(NEONS):
        a, b = np.array(a, np.float32), np.array(b, np.float32); fl = .93+.07*np.sin(t*23+j*1.7)       # scintillement très léger
        for i in range(n):
            u0, u1 = i/n, (i+1)/n; um = (u0+u1)/2
            d1 = (um-(t*vitesse+ph)) % 1.0; d1 = min(d1, 1-d1); d2 = (um-(t*vitesse*.6+ph+.5)) % 1.0; d2 = min(d2, 1-d2)
            k = fl*(.75+.9*np.exp(-(d1/.06)**2)+.5*np.exp(-(d2/.045)**2))
            p0 = tuple(int(v) for v in a+(b-a)*u0); p1 = tuple(int(v) for v in a+(b-a)*u1)
            cv2.line(gaine, p0, p1, tuple(float(v)*min(1.4, k) for v in c), 14, cv2.LINE_AA)
            w = min(1, k); cv2.line(coeur, p0, p1, (255*w, 255*w, 255*w), 4 if k < 1.1 else 6, cv2.LINE_AA)
        for (ph2, sp) in ((ph, vitesse), (ph+.5, vitesse*.6)):              # tête des éclats : reflet en étoile
            u = (t*sp+ph2) % 1.0; x, y = a+(b-a)*u
            if 8 < x < W-8 and 8 < y < H-8: _eclat(etoiles, x, y, 14, c, .95)
    halo = cv2.GaussianBlur(gaine, (0, 0), 5)*1.3+cv2.GaussianBlur(gaine, (0, 0), 16)*1.4+cv2.GaussianBlur(gaine, (0, 0), 42)*1.3
    etoiles = cv2.GaussianBlur(etoiles, (0, 0), 1.2)+cv2.GaussianBlur(etoiles, (0, 0), 7)*.8
    out = _screen(img, halo)                                                   # la lumière déborde sur les cases
    out = _screen(out, gaine*.9); out = _screen(out, coeur); return _screen(out, etoiles)

@functools.lru_cache(maxsize=1)
def cours():
    """cours mensuels réels (donnees/ttwo_mensuel.csv) : départ 17,70 $ le 17/09/2013, arrivée = dernière clôture (COURS_FIN)"""
    L = [l.split(',') for l in open(f'{D}/donnees/ttwo_mensuel.csv') if l[0].isdigit()]
    x = [2013+8.55/12]+[int(m[:4])+(int(m[5:7])-.5)/12 for m, _ in L]+[2026+10.55/12]
    y = [17.70]+[float(v) for _, v in L]+[COURS_FIN]
    return np.array(x), np.array(y)
COURS_FIN = float(os.environ.get('COURS_FIN', '205.93'))     # clôture du 17/11 (Yahoo Finance)
RATIO = 5.8                                                    # capitalisation ÷ ventes sur douze mois au 17/11 (38,6 Md$ ÷ 6,7 Md$ = 5,76)
def courbe(img, x0, y0, x1, y1, prog=1.0):
    """courbe réelle du cours, tracée de gauche à droite (prog de 0 à 1), axe des prix linéaire de 0 au plus haut"""
    xs, ys = cours(); n = max(2, int(len(xs)*prog))
    X = x0+(xs-xs[0])/(xs[-1]-xs[0])*(x1-x0); Y = y1-ys/ys.max()*(y1-y0)
    pts = np.stack([X[:n], Y[:n]], 1).astype(np.int32)
    poly = np.vstack([pts, [[pts[-1][0], y1], [pts[0][0], y1]]]); m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [poly], .22)
    img = img*(1-m[..., None])+np.array(GOLD, np.float32)*m[..., None]
    cv2.polylines(img, [pts], False, GOLD, 6, cv2.LINE_AA); cv2.circle(img, tuple(pts[-1]), 11, GOLD, -1, cv2.LINE_AA)
    REG['objets'].append(('courbe', x0, y0, x1, y1)); return img, pts[-1]
def controle(t):
    """renvoie les objets qui débordent de l'intérieur d'un verre (marge 30 px) ou qui le chevauchent sans y être"""
    pb = []
    for (s_, a, b, c, d) in REG['objets']:
        for (x0, y0, x1, y1) in REG['verres']:
            chev = a < x1 and c > x0 and b < y1 and d > y0
            if chev and not (a >= x0+30 and c <= x1-30 and b >= y0+30 and d <= y1-30): pb.append(f'{t:5.2f}s « {s_} » ({a},{b})-({c},{d}) hors du verre ({x0},{y0})-({x1},{y1})')
    return pb
CASES2 = [((0, 690), (560, 648), (500, 1333), (0, 1360)), ((560, 648), (1080, 610), (1080, 1300), (500, 1333)),
          ((0, 1360), (1080, 1300), (1080, 1920), (0, 1920))]
def mosaique2(t):
    """proposition du 17/11 : la case du haut devient une case titre (dégradé coucher de soleil rose-orange vers violet de la DA),
    trois cases de plans dessous ; le titre ne passe plus sur un visage, les sous-titres sont sur la bande centrale"""
    img = mosaique(t, plans=('mc_venice', 'mc_venice', 'mc_cabriolet', 'mc_billets'), tps=(1.0, 3.0, 3.0, 2.5))
    y = np.linspace(0, 1, 690, dtype=np.float32)[:, None, None]
    grad = np.array((255, 150, 110), np.float32)*(1-y)+np.array((90, 40, 140), np.float32)*y
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [np.array(CASES[0], np.int32)], 1.0, cv2.LINE_AA)
    g = np.zeros_like(img); g[:690] = grad; img = img*(1-m[..., None])+g*m[..., None]
    cv2.line(img, (0, 690), (1080, 610), BORD, 26, cv2.LINE_AA)
    img = texte(img, 'GTA 6', 150, 260, police=F_ANT, coul=CREME, contour=0)
    img = texte(img, "sort aujourd'hui", 445, 74, police=F_TIT, coul=(255, 255, 255), contour=0)
    return img
def carte(t):
    """transition « changement de personnage » : vue de dessus, voile vert-gris, grille de carte"""
    c = cv2.cvtColor(cv2.imread(f'{D}/cartes/carte_quartier.jpg'), cv2.COLOR_BGR2RGB); c = cv2.resize(c, (W, H)).astype(np.float32)
    g = c.mean(2, keepdims=True); c = c*.45+g*.55; c = c*.75+np.array((90, 120, 100), np.float32)*.25
    for x in range(0, W, 90): c[:, x:x+2] = c[:, x:x+2]*.6+200*.4
    for y in range(0, H, 90): c[y:y+2] = c[y:y+2]*.6+200*.4
    return cv2.GaussianBlur(c, (0, 0), 1.5)

# ---------- scènes ----------
def ease_(x): x = min(1, max(0, x)); return x*x*(3-2*x)
def outro(u):
    """outro de 5 s (18/11) : le pistolet à billets de Miami ralenti presque à l'arrêt (0,1×, fondu entre images voisines, léger
    zoom avant), puis le bloc « ABONNE-TOI » des carrousels (lib/carrousel.py, logos/PROFIL.png) en haut, au-dessus de Mister Coin"""
    sys.path.insert(0, f'{R}/lib'); import carrousel as CR; CR.D = D
    x = (3.0+u*.1)*24; i0 = int(x); f = x-i0
    a = frame(pl('mc_billets'), i0/24, 0, 1.0); b = frame(pl('mc_billets'), (i0+1)/24, 0, 1.0); im = a*(1-f)+b*f
    M = cv2.getRotationMatrix2D((W/2, H*.42), 0, 1+.05*u/OUTRO); im = cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    k = ease_((u-.3)/.6)
    cv = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).convert('RGBA'); s_, c_ = CR.surface()
    CR.bloc_abonne(cv, c_, cy=340); cv.alpha_composite(CR.to_img(s_))
    out = np.asarray(cv.convert('RGB')).astype(np.float32)
    return cadre(im*(1-k)+out*k)
def image(t):
    T_ABS[0] = t
    if t >= FIN: return outro(t-FIN)
    REG['verres'].clear(); REG['objets'].clear()
    if t < 1.2: img = mosaique(t)
    elif t < T_VEN:                                                             # la case du haut s'ouvre en plein écran
        k = (t-1.2)/(T_VEN-1.2); img = mosaique(t)*(1-k)+frame(pl('mc_venice'), t, 1.2, 1.0)*k
    elif t < T_CAB: img = frame(pl('mc_venice'), t, 1.2, 1.0)                   # 4,1 s
    elif t < T_PIE: img = frame(pl('mc_cabriolet'), t, T_CAB-.5, 1.0)           # 4,2 s
    elif t < TS: img = frame(pl('mc_pier'), t, T_PIE-.6, 1.0)                    # 5,0 s
    elif t < T_BIL: img = TSAT.image(t-TS, lambda u: frame(pl('mc_pier'), TS+u, T_PIE-.6, 1.0), lambda u: frame(pl('mc_billets'), TS+u, T_BIL-.4, 1.0))
    elif t < T13: img = frame(pl('mc_billets'), t, T_BIL-.4, 1.0)              # 6,0 s
    elif t < T_MINI:                                                            # 2013
        img = pose(frame(dec('decor_2013'), t, T13, .5), '', t)
    elif t < TM:                                                                # retour en 2026 : mini-transition satellite
        dep = lambda u: pose(frame(dec('decor_2013'), T_MINI+u, T13, .5), '', T_MINI+u)
        arr = lambda u: pose(frame(dec('decor_tour'), TM, TM, .9), '', TM)
        img = TSAT.mini_image(t-T_MINI, dep, arr)
    elif t < T3+p3(3.8):                                                            # le résultat, la tour
        img = pose(frame(dec('decor_tour'), t, TM, .9), '', t)
    elif t < T3+p3(3.8):                                                            # le résultat, la tour
        img = pose(frame(dec('decor_tour'), t, TM, .9), 'classique_danse_parle_billets', t-TM)
    elif t < T3+p3(9.6): img = frame(pl('mc_poursuite'), t, T3+p3(3.8)-.2, 1.0)      # GTA 6, précommandes
    elif t < T3+p3(19.6):                                                           # le piège, 1 : le boulevard (attention, les barres)
        img = pose(frame(dec('decor_boulevard'), t, T3+p3(9.6), .7), '', t)
    elif t < T3+p3(26.4):                                                           # le piège, 2 : la plage de nuit (déjà dans le prix)
        img = pose(frame(dec('decor_plage_nuit'), t, T3+p3(19.6), .7), '', t)
    else: img = frame(pl('mc_yacht'), t, T3+p3(26.4)-2.5, 1.0)
    # ---- textes par scène, style des carrousels : gros mots en Anton, phrases en Inter Display, sans contour, ombre douce ----
    if TS <= t < T_BIL: pass                                                   # transition : image seule
    elif t < T_VEN: img = A(img, 'GTA 6', 215, 190); img = I(img, "sort aujourd'hui", 440, 72)     # mosaïque : titre en grand
    elif t < T_CAB:                                                             # Venice : titre sur une ligne, au-dessus du chapeau
        wa = largeur('GTA 6', 104, F_ANT, 0); wb = largeur("sort aujourd'hui", 58, F_TIT, 0); x0 = (W-(wa+28+wb))//2
        img = A(img, 'GTA 6', 190, 104, x=x0); img = I(img, "sort aujourd'hui", 222, 58, x=x0+wa+28)
    elif t < T_PIE: img = I(img, 'Cotée en', 250, 80); img = A(img, 'BOURSE ?', 345, 170, GOLD)
    elif t < TS:
        if t >= T2-.1:
            img = verre(img, 80, 190, 920, 225, 'bleu')                       # bandeau bas de hauteur : Mister Coin reste dégagé
            wr = largeur('Rockstar', 50, F_TIT, 0); wt = largeur('TAKE-TWO', 84, F_ANT, 0); x0 = (W-(64+16+wr+100+64+16+wt))//2
            img = tuile(img, 'ROCKSTAR', x0, 230, 64); x = x0+80
            img = I(img, 'Rockstar', 230, 50, x=x); x += wr+50; img = fleche(img, x, 262, 70, 50); x += 50
            img = tuile(img, 'TTWO', x, 230, 64); img = A(img, 'TAKE-TWO', 210, 84, x=x+80)
            img = pill(img, 'Nasdaq · New York', 328, 32)
    elif t < T13:
        if t >= pos('voix_2', 5.0):
            img = verre(img, 150, 200, 780, 350, 'or'); img = A(img, '2013', 215, 150, GOLD); img = I(img, "L'action ou le jeu ?", 410, 58)
    elif T_MINI <= t < TM: pass                                                # mini-transition : image seule
    elif t < TM:
        img = verre(img, 150, 200, 780, 530 if t < pos('voix_2', 14.6) else 740, 'or')
        img = A(img, '2013', 215, 150, GOLD)
        img = I(img, "L'action Take-Two", 400, 48); img = A(img, '17,70 $', 460, 130, GOLD)
        if t >= pos('voix_2', 14.6): img = A(img, 'GTA 5 : 800 M$', 640, 96, GOLD); img = I(img, 'de ventes en 24 h', 765, 48)
    elif t < T3:
        img = verre(img, 110, 205, 860, 780, 'vert')
        wl = largeur("L'action Take-Two", 46, F_TIT, 0); img = tuile(img, 'TTWO', (W-wl)//2-62, 236, 48); img = I(img, "L'action Take-Two", 235, 46)
        img = I(img, '2013', 520, 30, x=150); img = I(img, '2026', 520, 30, x=W-175-largeur('2026', 30, F_TIT, 0))
        img, fin = courbe(img, 200, 330, 880, 505, prog=min(1, max(.02, (t-TM)/2.2)))
        img = I(img, '17,70 $', 438, 30, x=200)
        if t-TM >= 2.2: img = I(img, f"{COURS_FIN:.0f} $".replace('.', ','), 290, 30, x=880-largeur(f"{COURS_FIN:.0f} $", 30, F_TIT, 0))
        img = A(img, '1 000 €', 555, 90)
        img = fleche_simple(img, 540, 688, 742)
        cnt = 1000+(float(MONTANT.replace(' ', ''))-1000)*min(1, max(0, (t-TM-2.2)/2.3))
        img = A(img, f"{int(round(cnt/10)*10):,} €".replace(',', ' '), 768, 135, GOLD)
    elif t < T3+p3(3.8):
        img = verre(img, 170, 250, 740, 300, 'rouge')
        img = I(img, 'Ton GTA 5', 302, 76); img = pill(img, "d'occasion : dès 13,90 €", 425)
        img = emoji_(img, '💿', 262, 348, 76)
    elif t < T3+p3(9.6):
        img = A(img, '10 MILLIONS', 225, 150, GOLD); img = I(img, 'de précommandes', 420, 64)
    elif t < T3+p3(26.4):
        if t < T3+p3(12.9): img = A(img, 'ATTENTION', 280, 170, GOLD)
        elif t < T3+p3(19.6):
            img = verre(img, 120, 200, 840, 700, 'orange')
            img = I(img, 'Valeur en bourse', 238, 40); img = I(img, 'pour 1 € de ventes', 290, 40)
            for i, (lab, v, an, t0) in enumerate((('2013', 1.4, '1,4 ×', T3+p3(12.98)), ('2026', RATIO, f'{RATIO:.1f} ×'.replace('.', ','), T3+p3(17.29)))):
                if t < t0: continue
                x0 = 260+i*340; hh = int(330*v/RATIO*min(1, (t-t0)/.8)); y1 = 790
                cv2.rectangle(img, (x0, y1-hh), (x0+170, y1), GOLD if i else (255, 150, 110), -1)
                img = A(img, an, y1-hh-100, 84, GOLD, x=x0+85-largeur(an, 84, F_ANT, 0)//2)
                img = I(img, lab, y1+10, 40, x=x0+85-largeur(lab, 40, F_TIT, 0)//2)
        else:
            if t < T3+p3(21.7):
                img = verre(img, 140, 240, 800, 300, 'orange')
                img = I(img, 'Le succès est', 270, 76); img = I(img, 'déjà dans le prix', 380, 76, GOLD)
            else:                                                               # en deux temps : le jeu monte… l'action peut baisser
                img = verre(img, 140, 220, 800, 360 if t >= T3+p3(23.6) else 200, 'orange')
                img = A(img, 'GTA 6', 245, 96, x=250); img = emoji_(img, '📈', 740, 312, 96)
                if t >= T3+p3(23.6): img = A(img, "L'ACTION", 405, 96, x=250); img = emoji_(img, '📉', 740, 470, 96)
        img = plaque(img, 170, 930, 910, 1000, .55)
        img = texte(img, 'performances passées ≠ performances futures', 936, 28, police=F_MEN, contour=0, ombre=False)
        img = texte(img, 'pas un conseil en investissement', 968, 28, police=F_MEN, contour=0, ombre=False)
    else:
        img = I(img, 'Et toi, tu as', 250, 84); img = A(img, 'ACHETÉ GTA 6 ?', 360, 140, GOLD)
    img = sous_titre(img, t)
    return cadre(img)

CLES = [(0.0, 'image 0 · mosaïque'), (3.5, 'venice'), (7.5, 'cabriolet · bourse ?'), (12.0, 'jetée · rockstar'),
        (TS+.4, 'transition · départ'), (TS+1.5, 'transition · montée'), (TS+3.5, 'transition · survol'), (TS+4.4, 'transition · vert'),
        (TS+6.5, 'transition · jaune'), (TS+7.6, 'transition · plongée'), (T_BIL+2.0, "miami · l'action ou le jeu ?"), (T13+3.0, '2013 · 17,70 $'),
        (T13+7.5, '800 m$ en 24 h'), (T_MINI+.5, 'mini-transition 2013 → 2026'), (TM+1.1, 'le résultat · courbe'), (TM+4.6, 'le résultat · montant'), (T3+p3(2.0), "ton gta 5"),
        (T3+p3(6.5), 'précommandes'), (T3+p3(11.5), 'attention'), (T3+p3(15.5), '1,4 ×'), (T3+p3(18.4), '1,4 × contre 5,8 ×'),
        (T3+p3(20.5), 'le succès…'), (T3+p3(22.6), 'GTA 6 ↗'), (T3+p3(25.5), "l'action ↘"), (T3+p3(27.6), 'question finale')]
TRANS = [T_CAB+.02, T_PIE+.02, TS-.02, T_BIL+.02, T13+.02, TM+.05, T3+p3(3.82), T3+p3(9.62), T3+p3(26.42)]          # contrôle des coupes (texte sur texte)
def ambiance(sr, t0, t1, niveau=-30.0, baisse_voix=8.0):
    """son d'ambiance des vidéos générées (Veo et décors), très bas : chaque extrait ramené à niveau dBFS efficaces,
    baissé de baisse_voix dB quand la voix parle, fondus de 0,4 s aux coupes ; la musique de Nicolas passe par-dessus"""
    import subprocess, wave
    TAB = [('plans/mc_venice', 1.2, T_CAB, 1.2), ('plans/mc_cabriolet', T_CAB, T_PIE, T_CAB-.5), ('plans/mc_pier', T_PIE, TS+1.0, T_PIE-.6),
           ('plans/mc_billets', T_BIL-.8, T13, T_BIL-.4), ('decors/decor_2013', T13, T_MINI+.3, T13), ('decors/decor_tour', TM-.3, T3+p3(3.8), TM),
           ('plans/mc_poursuite', T3+p3(3.8), T3+p3(9.6), T3+p3(3.8)-.2), ('decors/decor_boulevard', T3+p3(9.6), T3+p3(19.6), T3+p3(9.6)), ('decors/decor_plage_nuit', T3+p3(19.6), T3+p3(26.4), T3+p3(19.6)), ('plans/mc_yacht', T3+p3(26.4), FIN, T3+p3(26.4)-2.5), ('plans/mc_billets', FIN, FIN_VID, FIN-3.0)]
    out = np.zeros((int((t1-t0)*sr), 2), np.float32)
    for (f, a, b, deb) in TAB:
        a, b = max(a, t0), min(b, t1)
        if b <= a: continue
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{D}/{f}.mp4', '-f', 's16le', '-ac', '2', '-ar', str(sr), '-'], capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32)/32768
        x = x/max(1e-6, np.sqrt((x**2).mean()))*10**(niveau/20)
        n = int((b-a)*sr); i0 = int(max(0, a-deb)*sr)
        idx = (i0+np.arange(n)) % len(x); seg = x[idx]                       # boucle si l'extrait dépasse les 8 s du clip
        fd = min(int(.4*sr), n//2); env = np.ones(n, np.float32); env[:fd] = np.linspace(0, 1, fd); env[-fd:] = np.linspace(1, 0, fd)
        k = int((a-t0)*sr); out[k:k+n] += seg*env[:, None]
    import wave as _w
    v = np.frombuffer(_w.open(f'{D}/voix/voice_provisoire.wav').readframes(10**9), np.int16).astype(np.float32)/32768
    v = v[int(t0*sr):int(t0*sr)+len(out)]; v = np.pad(v, (0, len(out)-len(v)))
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    parle = uniform_filter1d(maximum_filter1d((np.abs(v) > .02).astype(np.float32), int(.25*sr)), int(.15*sr))
    return out*(10**(-baisse_voix*parle/20))[:, None]
def assembler_voix():
    """voix provisoire : segments posés selon SEGS, trou de TMD pour la phrase du montant, troisième morceau à T3"""
    import wave
    sr = 48000; out = np.zeros(int((FIN+.5)*sr), np.float32)
    def lire(f): return np.frombuffer(wave.open(f'{D}/voix/{f}.wav').readframes(10**9), np.int16).astype(np.float32)/32768
    for (f, a, b, d) in SEGS+[('voix_montant', 0.0, 6.95, TM)]+[(f_, a_, b_, T3+d_) for (f_, a_, b_, d_) in SEGS3]:
        x = lire(f)[int(a*sr):int(b*sr)]; k = int(d*sr); out[k:k+len(x)] += x
    with wave.open(f'{D}/voix/voice_provisoire.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(out, -1, 1)*32767).astype(np.int16).tobytes())
def demo(t0=0.0, t1=None, fps=30, nom='demo_accroche'):
    """démo vidéo (voix provisoire + bruitages de la transition) : python3 maquettes.py demo"""
    import subprocess, wave
    t1 = t1 or T13+1.0; out = f'{D}/tmp/{nom}'; assembler_voix()
    sr = 48000; v = np.frombuffer(wave.open(f'{D}/voix/voice_provisoire.wav').readframes(10**9), np.int16).astype(np.float32)/32768
    a = np.stack([v[int(t0*sr):int(t1*sr)]]*2, 1); a += ambiance(sr, t0, t1)[:len(a)]
    fm = TSAT.mini_son(sr); km = int((T_MINI-t0)*sr)
    if 0 <= km < len(a): nm = min(len(a)-km, len(fm)); a[km:km+nm] += fm[:nm]*.8
    fx = TSAT.son(sr); k = int((TS-t0)*sr); n = min(len(a)-k, len(fx)); a[k:k+n] += fx[:n]*.8
    a = a/max(1, np.abs(a).max()/10**(-1/20))
    with wave.open(out+'.wav', 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a*32767).astype(np.int16).tobytes())
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                           '-i', out+'.wav', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', f'{D}/{nom}.mp4'], stdin=subprocess.PIPE)
    for i in range(int((t1-t0)*fps)): ff.stdin.write(np.clip(image(t0+i/fps), 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('ok', f'{D}/{nom}.mp4')
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'demo': demo(); sys.exit()
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'controle':
    assembler_voix()
    pb = []
    for t in np.arange(0, FIN, .1): image(t); pb += controle(t)
    print('\n'.join(pb) or 'aucun débordement'); sys.exit()
if __name__ == '__main__':
    assembler_voix()
    out = f'{D}/tmp/maq'; os.makedirs(out, exist_ok=True); vign = []
    for i, (t, lab) in enumerate(CLES):
        im = np.clip(image(t), 0, 255).astype(np.uint8); cv2.imwrite(f'{out}/{i:02d}.png', im[..., ::-1])
        v = cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA)[..., ::-1].copy()
        cv2.rectangle(v, (0, 600), (360, 640), (35, 8, 25), -1); cv2.putText(v, f'{t:4.1f}s  {lab}', (8, 628), cv2.FONT_HERSHEY_SIMPLEX, .55, (255, 255, 255), 1, cv2.LINE_AA)
        vign.append(v); print(i, round(t, 2), lab, flush=True)
    while len(vign) % 6: vign.append(np.zeros_like(vign[0]))
    pl_ = np.vstack([np.hstack(vign[i:i+6]) for i in range(0, len(vign), 6)])
    cv2.imwrite(f'{D}/maquettes_take_two_{os.environ.get("VERSION", "v")}.jpg', pl_, [cv2.IMWRITE_JPEG_QUALITY, 88])
    cv2.imwrite(f'{out}/planche_bd.jpg', cv2.resize(pl_, None, fx=.5, fy=.5), [cv2.IMWRITE_JPEG_QUALITY, 75])
    tr = [cv2.resize(np.clip(image(t), 0, 255).astype(np.uint8), (270, 480))[..., ::-1] for t in TRANS]
    cv2.imwrite(f'{out}/transitions_bd.jpg', np.hstack(tr), [cv2.IMWRITE_JPEG_QUALITY, 75])
    print('durée totale estimée', round(FIN, 1), 's')
