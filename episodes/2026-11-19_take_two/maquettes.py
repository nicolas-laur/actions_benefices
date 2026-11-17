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
F_TIT = f'{R}/fonts/ArchivoBlack-Regular.ttf'      # titres et chiffres dans la vidéo (Big Shoulders réservée à la couverture, retour du 17/11)
F_MEN = f'{R}/fonts/InterDisplay-Bold.otf'
INK = (25, 8, 35); GOLD = (255, 214, 90); BORD = (38, 14, 58)

# ---------- calage provisoire (secondes) ----------
V1, V2, V3 = 8.28, 19.80, 28.53                      # durées des trois morceaux reçus le 17/11
T2 = V1+.35; TM = T2+V2+.25; TMD = 5.0; T3 = TM+TMD+.3; FIN = T3+V3+1.2
# phrases (début, fin, texte, mot clé) — repérées sur les silences de chaque morceau
PH = [(0.00, 4.52, "GTA 6, le jeu le plus attendu de la décennie, sort aujourd'hui.", "aujourd'hui"),
      (4.99, 7.94, "Savais-tu que l'entreprise derrière le jeu est cotée en bourse ?", "bourse"),
      (T2+0.00, T2+4.53, "Rockstar, le studio de GTA, appartient à Take-Two, cotée à New York.", "Take-Two"),
      (T2+5.17, T2+10.38, "Et si, en 2013, à la sortie de GTA 5, tu avais acheté l'action plutôt que le jeu ?", "l'action"),
      (T2+10.68, T2+14.6, "Ce jour-là, l'action vaut 17,70 $.", "17,70 $"),
      (T2+14.6, T2+19.8, "Le jeu pulvérise les records : 800 M$ de ventes en 24 h.", "800 M$"),
      (TM, TM+TMD, "Résultat : 1 000 € placés dans Take-Two ce jour-là valent aujourd'hui environ … €.", "aujourd'hui"),
      (T3+0.00, T3+3.66, "Pendant ce temps, ton vieux GTA 5 vaut quelques euros d'occasion.", "quelques euros"),
      (T3+3.94, T3+9.39, "Et GTA 6 démarre encore plus fort : près de 10 millions de précommandes avant même la sortie.", "10 millions"),
      (T3+9.78, T3+12.68, "Alors, faut-il acheter l'action aujourd'hui ? Attention.", "Attention"),
      (T3+12.98, T3+16.84, "En 2013, Take-Two valait 1,4 fois ses ventes annuelles.", "1,4 fois"),
      (T3+17.29, T3+19.35, "Aujourd'hui, 5,7 fois.", "5,7 fois"),
      (T3+19.62, T3+21.42, "Le succès est déjà dans le prix :", "dans le prix"),
      (T3+21.74, T3+26.20, "GTA 6 peut tout casser… et l'action quand même décevoir.", "décevoir"),
      (T3+26.67, T3+28.28, "Et toi, tu as acheté GTA 6 ?", "GTA 6")]
MONTANT = os.environ.get('MONTANT', '14 500')       # provisoire : clôture du 16/11 (213,47 $), à remplacer par la clôture du 17/11

# ---------- lecture des clips ----------
def frame(path, t, debut=0.0, vitesse=1.0):
    cap = cv2.VideoCapture(path); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(min(n-1, max(0, (t-debut)*vitesse*24)))); ok, f = cap.read(); cap.release()
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    return np.clip(g+.25*(g-cv2.GaussianBlur(g, (0, 0), 1.2)), 0, 255)
def dec(n): return f'{D}/decors/{n}.mp4'
def pl(n): return f'{D}/plans/{n}.mp4'

# ---------- Mister Coin (clips classiques, détourés) ----------
@functools.lru_cache(maxsize=1)
def coin():
    """Mister Coin classique : il parle quand la voix parle (voix provisoire, trou de 5 s pour la phrase du montant)"""
    import veo_coin as VC
    return VC.VeoCoin([(T2, ['classique_parle_explique', 'classique_parle_enthousiaste'], 'voix'),
                       (T2+5.0, ['classique_parle_question', 'classique_parle_enthousiaste'], 'voix'),
                       (TM, ['classique_danse_parle_billets', 'classique_parle_enthousiaste'], 'voix'),
                       (T3+9.6, ['classique_parle_inquiet', 'classique_parle_confidence', 'classique_parle_explique'], 'voix')],
                      voix=f'{D}/voix/voice_provisoire.wav', x=540, pieds=1650, largeur_piece=230, duree=FIN, lisse=True)
def pose(img, clip, tl):
    rgb, a = coin().layer(T_ABS[0])
    return img*(1-a[..., None])+rgb*a[..., None]
T_ABS = [0.0]

# ---------- textes DA GTA ----------
@functools.lru_cache(maxsize=None)
def font(p, s): return ImageFont.truetype(p, s)
def texte(img, s, y, taille, police=F_TIT, coul=(255, 255, 255), contour=7, x=None, ombre=True, alpha=1.0):
    """texte centré (ou à partir de x), contour violet-noir et ombre portée floue"""
    if alpha <= 0: return img
    f = font(police, taille); bb = f.getbbox(s, stroke_width=contour); w = bb[2]-bb[0]
    X = (W-w)//2-bb[0] if x is None else x
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if ombre:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((X+6, y+9), s, font=f, fill=(10, 0, 20, 170), stroke_width=contour, stroke_fill=(10, 0, 20, 170))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(7))); d = ImageDraw.Draw(lay)
    d.text((X, y), s, font=f, fill=coul+(255,), stroke_width=contour, stroke_fill=INK+(255,))
    a = np.asarray(lay).astype(np.float32); m = a[..., 3:]/255*alpha
    return img*(1-m)+a[..., :3]*m
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
    thick_panel(cv, x, y, w, h, r=46, bevel=40, frost=22, dim=.55, **MOODS[mood])
    return np.asarray(cv.convert('RGB')).astype(np.float32)

# ---------- sous-titres mot à mot (ligne de 760 px max, y ≈ 1040, mot clé en jaune) ----------
def sous_titre(img, t):
    ph = next((p for p in PH if p[0] <= t < p[1]+.15), None)
    if ph is None: return img
    a, b, s, cle = ph; mots = s.split(' ')
    k = max(1, min(len(mots), int((t-a)/max(.1, b-a)*len(mots))+1))         # mot courant (réparti à la longueur, en attendant un calage fin)
    # groupe de mots tenant sur une ligne autour du mot courant
    lignes, cur = [], []
    for m in mots:
        if cur and largeur(' '.join(cur+[m]), 50) > 760: lignes.append(cur); cur = []
        cur.append(m)
    lignes.append(cur); i = 0
    for L in lignes:
        if k <= i+len(L): break
        i += len(L)
    vis = L[:k-i]; X = (W-largeur(' '.join(L), 50))//2
    img = plaque(img, X-24, 1012, X+largeur(' '.join(L), 50)+24, 1098, .45)
    for m in vis:
        c = GOLD if any(w in cle.split(' ') for w in [m.strip(',.:?…')]) or m.strip(',.:?…') in cle.split(' ') else (255, 255, 255)
        img = texte(img, m, 1022, 50, coul=c, contour=5, x=X, ombre=False); X += largeur(m+' ', 50)
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
def carte(t):
    """transition « changement de personnage » : vue de dessus, voile vert-gris, grille de carte"""
    c = cv2.cvtColor(cv2.imread(f'{D}/cartes/carte_quartier.jpg'), cv2.COLOR_BGR2RGB); c = cv2.resize(c, (W, H)).astype(np.float32)
    g = c.mean(2, keepdims=True); c = c*.45+g*.55; c = c*.75+np.array((90, 120, 100), np.float32)*.25
    for x in range(0, W, 90): c[:, x:x+2] = c[:, x:x+2]*.6+200*.4
    for y in range(0, H, 90): c[y:y+2] = c[y:y+2]*.6+200*.4
    return cv2.GaussianBlur(c, (0, 0), 1.5)

# ---------- scènes ----------
def image(t):
    T_ABS[0] = t
    if t < 1.6: img = frame(pl('mc_venice'), t, 0, 1.4)
    elif t < 3.2: img = frame(pl('mc_cabriolet'), t, 1.6, 1.6)
    elif t < 4.5: img = frame(pl('mc_pier'), t, 3.2, 1.8)
    elif t < 5.6: img = carte(t)
    elif t < T2: img = frame(pl('mc_billets'), t, 5.6-1.5, 1.0)
    elif t < T2+5.0:                                                            # Rockstar → Take-Two
        img = pose(frame(dec('decor_boulevard'), t, T2, .9), 'classique_parle_explique', t-T2)
    elif t < TM:                                                                # 2013
        img = pose(frame(dec('decor_2013'), t, T2+5, .5), 'classique_parle_question' if t < T2+10.5 else 'classique_parle_enthousiaste', t-T2)
    elif t < T3+3.8:                                                            # le résultat, la tour
        img = pose(frame(dec('decor_tour'), t, TM, .9), 'classique_danse_parle_billets', t-TM)
    elif t < T3+9.6: img = frame(pl('mc_poursuite'), t, T3+3.8-1.0, 1.2)      # GTA 6, précommandes
    elif t < T3+26.4:                                                           # le piège
        img = pose(frame(dec('decor_plage_nuit'), t, T3+9.6, .55), 'classique_parle_inquiet' if t < T3+19.5 else 'classique_parle_confidence', t-T3)
    else: img = frame(pl('mc_yacht'), t, T3+26.4-5.5, 1.0)
    # ---- textes par scène : titres nus sur l'action, informations sur des panneaux de verre épais ----
    if 4.5 <= t < 5.6: pass
    elif t < 4.5: img = texte(img, 'gta 6', 230, 150); img = texte(img, "sort aujourd'hui", 400, 86)
    elif t < T2: img = texte(img, 'cotée en', 250, 96); img = texte(img, 'bourse ?', 370, 140, coul=GOLD)
    elif t < T2+5.0:
        img = verre(img, 170, 220, 740, 500, 'bleu')
        img = texte(img, 'rockstar', 260, 84); img = fleche(img, 540, 420, 76, 56, bas=True); img = texte(img, 'take-two', 470, 100)
        img = texte(img, 'nasdaq · new york', 625, 46, coul=GOLD, contour=5)
    elif t < TM:
        img = verre(img, 150, 200, 780, 330 if t < T2+10.6 else (530 if t < T2+14.6 else 740), 'or')
        img = texte(img, '2013', 225, 130, coul=GOLD)
        if t < T2+10.6: img = texte(img, "l'action ou le jeu ?", 400, 62)
        else:
            img = texte(img, "l'action take-two", 400, 52); img = texte(img, '17,70 $', 470, 120, coul=GOLD)
            if t >= T2+14.6: img = texte(img, 'gta 5 : 800 m$', 650, 72, coul=GOLD); img = texte(img, 'en 24 h', 750, 56)
    elif t < T3:
        img = verre(img, 110, 205, 860, 760, 'vert')
        img = texte(img, "l'action take-two", 235, 50)
        img = texte(img, '2013', 520, 34, x=150, contour=4); img = texte(img, '2026', 520, 34, x=W-150-largeur('2026', 34, contour=4), contour=4)
        xs = np.linspace(170, 910, 60); u = (xs-170)/740; ys = 505-180*(u**2.2)          # courbe stylisée (à remplacer par les vrais cours annuels)
        pts = np.stack([xs, ys], 1).astype(np.int32); cv2.polylines(img, [pts], False, INK, 16, cv2.LINE_AA); cv2.polylines(img, [pts], False, GOLD, 8, cv2.LINE_AA)
        img = texte(img, '1 000 €', 585, 70)
        img = fleche(img, 540, 715, 70, 52, bas=True)
        cnt = 1000+(float(MONTANT.replace(' ', ''))-1000)*min(1, max(0, (t-TM-2.2)/2.3))
        img = texte(img, f"{int(round(cnt/10)*10):,} €".replace(',', ' '), 765, 120, coul=GOLD)
    elif t < T3+3.8:
        img = verre(img, 170, 250, 740, 300, 'rouge')
        img = texte(img, 'ton gta 5', 290, 90); img = texte(img, "quelques € d'occasion", 420, 56, coul=GOLD)
    elif t < T3+9.6:
        img = texte(img, '10 millions', 240, 112, coul=GOLD); img = texte(img, 'de précommandes', 400, 70)
    elif t < T3+26.4:
        if t < T3+12.9: img = texte(img, 'attention', 300, 120, coul=GOLD)
        elif t < T3+19.6:
            img = verre(img, 120, 200, 840, 700, 'orange')
            img = texte(img, 'valeur en bourse', 225, 44, contour=5); img = texte(img, 'pour 1 € de ventes', 280, 44, contour=5)
            for i, (lab, v, an, t0) in enumerate((('2013', 1.4, '1,4 ×', T3+12.98), ('2026', 5.7, '5,7 ×', T3+17.29))):
                if t < t0: continue
                x0 = 260+i*340; hh = int(380*v/5.7*min(1, (t-t0)/.8)); y1 = 830
                cv2.rectangle(img, (x0-6, y1-hh-6), (x0+176, y1+6), INK, -1)
                cv2.rectangle(img, (x0, y1-hh), (x0+170, y1), GOLD if i else (255, 150, 110), -1)
                img = texte(img, an, y1-hh-90, 66, coul=GOLD, x=x0+85-largeur(an, 66)//2)
                img = texte(img, lab, y1+10, 44, x=x0+85-largeur(lab, 44)//2, contour=5)
        else:
            img = verre(img, 140, 240, 800, 280, 'orange')
            img = texte(img, 'le succès est', 265, 84); img = texte(img, 'déjà dans le prix', 380, 84, coul=GOLD)
        img = plaque(img, 170, 930, 910, 1000, .55)                              # mention (Inter : Archivo n'a pas le signe ≠)
        img = texte(img, 'performances passées ≠ performances futures', 936, 28, police=F_MEN, contour=0, ombre=False)
        img = texte(img, 'pas un conseil en investissement', 968, 28, police=F_MEN, contour=0, ombre=False)
    else:
        img = texte(img, 'et toi, tu as', 250, 100); img = texte(img, 'acheté gta 6 ?', 380, 116, coul=GOLD)
    img = sous_titre(img, t)
    return cadre(img)

CLES = [(0.0, 'accroche · image 0'), (2.4, 'accroche · cabriolet'), (3.9, 'accroche · jetée'), (5.0, 'transition carte'),
        (7.2, 'cotée en bourse ?'), (T2+2.6, 'rockstar → take-two'), (T2+8.0, '2013'), (T2+12.5, '17,70 $'),
        (T2+17.5, '800 m$ en 24 h'), (TM+4.6, 'le résultat'), (T3+2.0, "gta 5 d'occasion"), (T3+6.5, 'précommandes'),
        (T3+11.5, 'attention'), (T3+18.4, '1,4 × contre 5,7 ×'), (T3+23.5, 'déjà dans le prix'), (T3+27.6, 'question finale')]
TRANS = [T2-.05, T2+5.0, TM+.05, T3+3.82, T3+9.62, T3+26.42]          # contrôle des coupes (texte sur texte)
if __name__ == '__main__':
    out = f'{D}/tmp/maq'; os.makedirs(out, exist_ok=True); vign = []
    for i, (t, lab) in enumerate(CLES):
        im = np.clip(image(t), 0, 255).astype(np.uint8); cv2.imwrite(f'{out}/{i:02d}.png', im[..., ::-1])
        v = cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA)[..., ::-1].copy()
        cv2.rectangle(v, (0, 600), (360, 640), (35, 8, 25), -1); cv2.putText(v, f'{t:4.1f}s  {lab}', (8, 628), cv2.FONT_HERSHEY_SIMPLEX, .55, (255, 255, 255), 1, cv2.LINE_AA)
        vign.append(v); print(i, round(t, 2), lab, flush=True)
    while len(vign) % 4: vign.append(np.zeros_like(vign[0]))
    pl_ = np.vstack([np.hstack(vign[i:i+4]) for i in range(0, len(vign), 4)])
    cv2.imwrite(f'{D}/maquettes_take_two.jpg', pl_, [cv2.IMWRITE_JPEG_QUALITY, 88])
    cv2.imwrite(f'{out}/planche_bd.jpg', cv2.resize(pl_, None, fx=.5, fy=.5), [cv2.IMWRITE_JPEG_QUALITY, 75])
    tr = [cv2.resize(np.clip(image(t), 0, 255).astype(np.uint8), (270, 480))[..., ::-1] for t in TRANS]
    cv2.imwrite(f'{out}/transitions_bd.jpg', np.hstack(tr), [cv2.IMWRITE_JPEG_QUALITY, 75])
    print('durée totale estimée', round(FIN, 1), 's')
