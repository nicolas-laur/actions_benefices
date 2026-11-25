"""Démonstrations d'idées graphiques et d'effets pour Nicolas (25/11/2026), à valider avant intégration au site.
Publiées à /demo/ et /demo/suite/ (non référencées, hors plan du site). Styles : assets/css/demo.css ; scripts : assets/js/demo.js."""
import json, datetime as dt
from html import escape


def _serie(MARCHES, k, n=160):
    """série hebdomadaire base 100 sur 10 ans, échantillonnée à n points"""
    s = MARCHES['series'][k]['v']; d = MARCHES['dates']
    i0 = max(0, len(d) - 522)
    pts = [(d[i], v) for i, v in list(zip(range(len(d)), s))[i0:] if v]
    if not pts: return []
    pas = max(1, len(pts) // n); pts = pts[::pas] + [pts[-1]]
    b = pts[0][1]
    return [[p[0], round(100 * p[1] / b, 1)] for p in pts]


def _perf10(MARCHES):
    """performance sur 10 ans (dernière valeur / valeur d'il y a 10 ans), pour le jeu du plus ou moins"""
    d = MARCHES['dates']; out = {}
    for k, s in MARCHES['series'].items():
        if k == 'eurusd': continue
        v = s['v']; i0 = max(0, len(d) - 522)
        a = next((x for x in v[i0:i0 + 8] if x), None); b = next((x for x in reversed(v) if x), None)
        if a and b and s['groupe'].split('|')[0] in ('Actions américaines', 'Actions européennes', 'Indices', 'Matières premières'):
            out[k] = dict(nom=s['nom'], p=round(100 * (b / a - 1)), g=s['groupe'].replace('|', ' · '))
    return out


def demo(r, MARCHES, LEXIQUE, QUIZ, EXPR, FICHES, depuis):
    sp = _serie(MARCHES, 'sp500')
    semaine = dt.date.today().isocalendar()[1]
    sigles = [e for e in LEXIQUE if e[1].isupper() or len(e[1]) <= 6]
    mot = sigles[semaine % len(sigles)]
    q = next((x for x in QUIZ if mot[1].split()[0].lower() in x[0].lower()), None)
    bandeau = [b for b in MARCHES['bandeau'] if b.get('var') is not None][:8]
    donnees = dict(sp=sp, perf=_perf10(MARCHES), expr=EXPR, bandeau=bandeau, mot=dict(sigle=mot[1], nom=mot[2], q=q and dict(q=q[0], c=q[1], b=q[2], e=q[3])))
    data = json.dumps(donnees, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    yeux = json.load(open(depuis / 'assets' / 'img' / 'demo' / 'yeux.json'))

    def bloc(num, titre, txt, corps, ident):
        return (f'<section class="section demo-bloc" id="{ident}"><div class="sec-tete"><div><div class="surtitre">Idée {num}</div>'
                f'<h2>{titre}</h2><p class="gris" style="margin:6px 0 0;max-width:760px">{txt}</p></div></div>{corps}</section>')

    T = [('Capitalisation', 3628, ' Md€', '≈ 3 978 Md$', 0), ('PER au 23/11', 17.7, '', 'Broadcom 40,0 · AMD 99', 1), ('Marge nette', 56, ' %', 'exercice 2026', 0)]
    tuiles_plates = ''.join(f'<div class="tuile"><span class="lib">{l}</span><span class="val">{str(v).replace(".", ",")}{u}</span><span class="ctx">{c}</span></div>' for l, v, u, c, _ in T)
    tuiles_verre = ''.join(f'<div class="verre-epais"><span class="lib">{l}</span><span class="val compte" data-fin="{v}" data-dec="{d}" data-unite="{u}">0</span><span class="ctx">{c}</span></div>' for l, v, u, c, d in T)

    sommaire = ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('verre', 'Verre épais'), ('transition', 'Transitions'), ('chiffres', 'Chiffres qui comptent'), ('mot', 'Mot de la semaine'),
                                                             ('portrait', 'Portrait de Mister Coin'), ('yeux', 'Yeux qui suivent'), ('pluie', 'Pluie de pièces'), ('palettes', 'Tableau à palettes'),
                                                             ('dossier', 'Fiche feuilletée'), ('jeu', 'Plus ou moins')])
    yeux_svg = ''.join(f'<ellipse class="oeil" data-i="{i}" cx="{e["cx"]:.1f}" cy="{e["cy"]:.1f}" rx="{e["rx"] * .62:.1f}" ry="{e["ry"] * .66:.1f}" fill="#2A1712"/>'
                       f'<ellipse class="reflet" data-i="{i}" cx="{e["cx"]:.1f}" cy="{e["cy"]:.1f}" rx="{e["rx"] * .16:.1f}" ry="{e["ry"] * .14:.1f}" fill="#FFF6E6"/>' for i, e in enumerate(yeux['yeux']))
    yeux_js = json.dumps(yeux)

    portrait_expr = ['salut', 'etoiles', 'rire', 'sceptique', 'choc', 'reflechit', 'site_trophee', 'site_dort']
    c = (
        '<div class="hero tete"><div><div class="surtitre">Démonstration privée, non référencée</div><h1>LES IDÉES <em>EN VRAI</em></h1>'
        '<p class="chapo">Dix pistes à essayer sur cette page avant de les intégrer au site. Fais défiler, survole, clique : tout est fonctionnel.</p></div>'
        f'<img class="tete-coin" src="{r}assets/img/site_megaphone.webp" alt=""></div>'
        f'<nav class="sommaire">{sommaire}</nav>'
        + bloc(1, 'LE <em>VERRE ÉPAIS</em>', "Ta signature des vidéos sur les tuiles de chiffres : épaisseur, tranche dorée, reflet qui suit la souris. À gauche, les tuiles actuelles.",
               f'<div class="demo-compare"><div><p class="petit gris">Aujourd\'hui</p><div class="tuiles demo-plates">{tuiles_plates}</div></div>'
               f'<div><p class="petit gris">Proposition</p><div class="demo-verres">{tuiles_verre}</div></div></div>', 'verre')
        + bloc(2, 'DES <em>TRANSITIONS</em> ENTRE LES PAGES', "Plus d'écran blanc entre deux pages : la nouvelle glisse et Mister Coin reste à sa place, comme s'il t'accompagnait. Clique pour voir (navigateurs récents : Chrome, Edge, Safari 18).",
               f'<div class="demo-transition"><img class="vt-coin" src="{r}assets/img/expr/salut.webp" alt=""><a class="bouton or" href="{r}demo/suite/">Aller à la page suivante →</a></div>', 'transition')
        + bloc(3, 'DES <em>CHIFFRES</em> QUI COMPTENT', "Les grands chiffres défilent jusqu'à leur valeur quand ils apparaissent, et la courbe se dessine au rythme du défilement. Ici, le S&P 500 sur 10 ans (base 100, hors dividendes).",
               '<div class="demo-courbe"><svg viewBox="0 0 1000 360" preserveAspectRatio="none" aria-label="S&amp;P 500 sur 10 ans"><path class="grille" d="M0 90H1000M0 180H1000M0 270H1000"/>'
               '<path class="trace" pathLength="1"/><circle class="point" r="7"/></svg><div class="courbe-val"><b class="compte-courbe">100</b><span>valeur de 100 € placés il y a 10 ans</span></div></div>', 'chiffres')
        + bloc(4, 'LE <em>MOT</em> DE LA SEMAINE', "Un terme du lexique mis en avant sur l'accueil, changé chaque lundi automatiquement, avec sa mini-question.",
               '<div class="demo-mot"><div class="mot-carte"><span class="surtitre">Mot de la semaine</span><b class="mot-sigle"></b><span class="mot-nom"></span>'
               '<div class="mot-q"></div></div>' f'<img src="{r}assets/img/expr/question.webp" alt="" class="mot-coin"></div>', 'mot')
        + bloc(5, 'LE <em>PORTRAIT</em> DE MISTER COIN', "Une page à lui, comme une fiche de personnage : son identité, ses expressions, ses répliques, ses coulisses. Les répliques sont des propositions à réécrire avec toi.",
               '<div class="demo-portrait"><div class="carte-id"><span class="tampon">Fiche d\'identité</span><b>MISTER COIN</b>'
               '<dl><dt>Né</dt><dd>en octobre 2026, à Toulouse</dd><dt>Métier</dt><dd>rendre la bourse claire</dd><dt>Signes particuliers</dt><dd>chapeau haut-de-forme, nœud papillon, ne donne jamais de conseil</dd>'
               '<dt>Peur bleue</dt><dd>les frais cachés</dd><dt>Plat préféré</dt><dd>les intérêts composés</dd></dl></div>'
               '<div class="portrait-droite"><div class="galerie-expr">' + ''.join(f'<img src="{r}assets/img/expr/{n}.webp" alt="" loading="lazy">' for n in portrait_expr) + '</div>'
               '<ul class="repliques"><li>« Pas de stress ma poule, on remet les chiffres à plat. »</li><li>« Un PER de 99 ? Je m\'assois deux minutes. »</li><li>« Je ne te dis pas quoi acheter : je te montre comment lire. »</li></ul>'
               '<p class="petit gris">Coulisses : décors peints puis animés, voix enregistrée, chiffres vérifiés un par un, sources en commentaire.</p></div></div>', 'portrait')
        + bloc(6, 'DES <em>YEUX</em> QUI TE SUIVENT', "Ses pupilles suivent ta souris (ou ton doigt). Survole un chiffre en hausse ou en baisse : il réagit.",
               f'<div class="demo-yeux"><div class="yeux-scene" data-yeux=\'{yeux_js}\'><img class="yeux-base" src="{r}assets/img/demo/salut_sans_pupilles.webp" alt="Mister Coin">'
               f'<svg class="yeux-svg" viewBox="0 0 {yeux["w"]} {yeux["h"]}">{yeux_svg}</svg><img class="yeux-reaction" alt=""></div>'
               '<div class="yeux-chips"><span class="chip hausse" data-expr="site_saut_joie">Nvidia +31,5 %</span><span class="chip baisse" data-expr="sueur">Nasdaq −2,0 %</span>'
               '<span class="chip" data-expr="sceptique">PER de 99</span></div></div>', 'yeux')
        + bloc(7, 'LA <em>PLUIE</em> DE PIÈCES', "Le calculateur d'intérêts composés en version physique : chaque colonne est une tranche de 5 ans, sa hauteur suit le capital. La part dorée vient des intérêts.",
               '<div class="demo-pluie"><div class="pluie-reglages"><label>Chaque mois <input type="number" id="pl-m" value="100" min="10" step="10"> €</label>'
               '<label>Rendement <input type="number" id="pl-t" value="7" min="0" max="15" step="0.5"> %/an</label><label>Durée <input type="number" id="pl-d" value="30" min="5" max="40" step="5"> ans</label>'
               '<button class="bouton or" type="button" id="pl-go">Lancer la pluie</button></div><canvas id="pluie-cv" height="420"></canvas>'
               '<p class="pluie-res petit gris">Calcul mensuel, rendement constant, avant impôts et frais : une hypothèse, pas une promesse.</p></div>', 'pluie')
        + bloc(8, 'LE <em>TABLEAU</em> À PALETTES', "À la place du bandeau défilant de l'accueil : un vrai tableau de gare des années 1930, dont les lettres se retournent à chaque mise à jour (son mécanique si le son est activé).",
               '<div class="demo-palettes"><div class="palettes" id="pal-tab"></div><div class="palettes-bas"><button class="bouton clair" type="button" id="pal-go">Rejouer</button>'
               '<button class="bouton clair" type="button" id="pal-son">🔇 Son</button><span class="petit gris">Variations de la dernière séance</span></div></div>', 'palettes')
        + bloc(9, 'LA FICHE <em>FEUILLETÉE</em>', "La fiche s'ouvre comme un dossier d'archive : on tourne les pages, le tampon atteste les comptes vérifiés. Clique sur le dossier ou utilise les flèches.",
               '<div class="demo-dossier"><div class="dossier" id="dos-box" tabindex="0">'
               '<div class="feuille couv"><span class="tampon rouge">Comptes vérifiés · 17/11/2026</span><b>DOSSIER N° 2</b><span class="titre-dossier">NVIDIA</span><span class="petit">Ouvrir →</span></div>'
               '<div class="feuille"><span class="surtitre">Pièce 1 · Identité</span><b>Les puces de l\'IA</b><p>Processeurs graphiques pour centres de données, jeux vidéo et voitures. En bourse depuis 1999 (Nasdaq).</p><p class="gros">≈ 3 628 Md€</p><p class="petit">capitalisation au 23/11</p></div>'
               '<div class="feuille"><span class="surtitre">Pièce 2 · Croissance</span><b>329 Md€ de ventes</b><p>sur les 12 derniers mois, +103 % au dernier trimestre sur un an.</p><p class="gros">+68 %/an</p><p class="petit">sur 4 ans, 2022 → 2026</p></div>'
               '<div class="feuille"><span class="surtitre">Pièce 3 · Rentabilité</span><b>56 % de marge nette</b><p>Sur 100 € de ventes, 56 € de bénéfice. Trésorerie nette : +19,2 Md€.</p><p class="gros">PER 17,7</p><p class="petit">au 23/11</p></div>'
               '<div class="feuille fin"><span class="surtitre">Fin du dossier</span><b>La fiche complète</b>' f'<a class="bouton or" href="{r}fiches/nvidia/">Ouvrir la fiche Nvidia</a></div>'
               '</div><div class="dossier-nav"><button class="bouton clair" type="button" id="dos-prec">←</button><span id="dos-num">1 / 5</span><button class="bouton clair" type="button" id="dos-suiv">→</button></div></div>', 'dossier')
        + bloc(10, 'LE JEU DU <em>PLUS OU MOINS</em>', "Deux valeurs, une question : laquelle a le plus progressé en 10 ans ? Mister Coin réagit, ta série est gardée. Données de notre comparateur (hors dividendes).",
               '<div class="demo-jeu"><div class="jeu-tete"><span class="badge or" id="jeu-serie">Série : 0</span><span class="badge" id="jeu-record">Record : 0</span></div>'
               '<p class="jeu-q">Laquelle a le plus monté en 10 ans ?</p><div class="jeu-duel"><button class="duel" type="button" data-c="0"></button><span class="vs">VS</span><button class="duel" type="button" data-c="1"></button></div>'
               f'<div class="jeu-bas"><img class="jeu-coin" src="{r}assets/img/expr/reflechit.webp" alt=""><p class="jeu-msg">Choisis !</p></div></div>', 'jeu')
        + f'<script type="application/json" id="demo-data">{data}</script><script src="{r}assets/js/demo.js" defer></script>'
    )
    return f'<link rel="stylesheet" href="{r}assets/css/demo.css">' + c


def demo_suite(r):
    return (f'<link rel="stylesheet" href="{r}assets/css/demo.css">'
            '<div class="hero tete"><div><div class="surtitre">Démonstration · transition</div><h1>TU AS <em>CHANGÉ</em> DE PAGE</h1>'
            '<p class="chapo">La page a glissé et Mister Coin est resté en place. Sur le site, ce serait le cas entre toutes les rubriques.</p>'
            f'<a class="bouton or" href="{r}demo/#transition">← Revenir à la démonstration</a></div></div>'
            f'<div class="demo-transition suite"><img class="vt-coin" src="{r}assets/img/expr/salut.webp" alt=""></div>')
