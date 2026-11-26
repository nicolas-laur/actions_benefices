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
    """version 2 (26/11) : verre en vrai relief, transition à élément partagé, courbe nette ; idées 4 à 9 abandonnées ou reportées"""
    sp = _serie(MARCHES, 'sp500', 220)
    donnees = dict(sp=sp, perf=_perf10(MARCHES), expr=EXPR)
    data = json.dumps(donnees, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

    def bloc(num, titre, txt, corps, ident):
        return (f'<section class="section demo-bloc" id="{ident}"><div class="sec-tete"><div><div class="surtitre">{num}</div>'
                f'<h2>{titre}</h2><p class="gris" style="margin:6px 0 0;max-width:760px">{txt}</p></div></div>{corps}</section>')

    T = [('Capitalisation', 3628, ' Md€', '≈ 3 978 Md$', 0), ('PER au 23/11', 17.7, '', 'Broadcom 40,0 · AMD 99', 1), ('Marge nette', 56, ' %', 'exercice 2026', 0)]
    tuiles_plates = ''.join(f'<div class="tuile"><span class="lib">{l}</span><span class="val">{str(v).replace(".", ",")}{u}</span><span class="ctx">{c}</span></div>' for l, v, u, c, _ in T)
    tuiles_verre = ''.join(f'<div class="v3d"><div class="v-corps"><div class="v-face"><div class="v-reflet"></div></div>'
                           f'<div class="v-contenu"><span class="lib">{l}</span><span class="val compte" data-fin="{v}" data-dec="{d}" data-unite="{u}">{str(v).replace(".", ",")}{u}</span><span class="ctx">{c}</span></div></div></div>'
                           for l, v, u, c, d in T)
    sommaire = ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('verre', 'Verre épais'), ('transition', 'Transitions'), ('chiffres', 'Courbe qui se dessine'), ('jeu', 'Plus ou moins')])
    carte_fiche = (f'<a class="vt-carte" href="{r}demo/suite/"><img class="vt-logo" src="{r}assets/img/nvda.png" alt="">'
                   '<span><b class="vt-titre">NVIDIA</b><span class="petit gris">Les puces de l\'IA · fiche du 17/11</span></span>'
                   f'<img class="vt-coin" src="{r}assets/img/loupe.webp" alt=""></a>')
    c = (
        '<div class="hero tete"><div><div class="surtitre">Démonstration privée, non référencée · version 2</div><h1>LES IDÉES <em>EN VRAI</em></h1>'
        '<p class="chapo">Après tes retours du 26/11 : trois idées reprises de zéro, plus le jeu sur lequel tu ne t\'es pas encore prononcé.</p></div>'
        f'<img class="tete-coin" src="{r}assets/img/site_megaphone.webp" alt=""></div>'
        f'<nav class="sommaire">{sommaire}</nav>'
        + bloc('Idée 1 · version 2', 'LE <em>VERRE ÉPAIS</em>', "De vraies plaques en relief : une tranche dorée qui a de l'épaisseur, les chiffres qui flottent au-dessus du verre et une ombre portée au sol. Au repos elles respirent doucement ; survole-les pour les incliner.",
               f'<div class="demo-compare"><div><p class="petit gris">Aujourd\'hui</p><div class="tuiles demo-plates">{tuiles_plates}</div></div>'
               f'<div><p class="petit gris">Proposition</p><div class="demo-verres">{tuiles_verre}</div></div></div>', 'verre')
        + bloc('Idée 2 · version 2', 'DES <em>TRANSITIONS</em> ENTRE LES PAGES', "Clique sur la carte : le logo, le titre et Mister Coin glissent jusqu'à leur place dans l'en-tête de la fiche pendant que le reste se fond. L'en-tête et le pied du site ne bougent pas. Navigateurs récents (Chrome, Edge, Safari 18) ; ailleurs, la page s'ouvre normalement.",
               f'<div class="demo-transition">{carte_fiche}</div>', 'transition')
        + bloc('Idée 3 · version 2', 'UNE <em>COURBE</em> QUI SE DESSINE', "La courbe est tracée à la taille exacte de l'écran (nette sur téléphone comme sur grand écran) et se dessine une seule fois quand elle apparaît, avec le compteur et l'année qui suivent.",
               f'<div class="demo-courbe"><div class="courbe-val"><b class="compte-courbe">100</b><span class="petit gris">S&amp;P 500 en base 100 fin {sp[0][0][:4] if sp else ""}, en dollars, hors dividendes · <span class="courbe-an"></span></span></div>'
               '<svg class="courbe-svg" aria-label="S&amp;P 500 sur 10 ans, base 100"><defs><linearGradient id="cb-aire" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--or-lum)" stop-opacity=".28"/><stop offset="1" stop-color="var(--or-lum)" stop-opacity="0"/></linearGradient>'
               '<clipPath id="cb-clip"><rect class="cb-rect" x="0" y="-20" height="2000" width="0"/></clipPath></defs><g class="cb-grille"></g>'
               '<g clip-path="url(#cb-clip)"><path class="cb-aire" fill="url(#cb-aire)"/><path class="cb-halo"/><path class="cb-trait"/></g><circle class="cb-point" r="6"/></svg>'
               '<button class="bouton clair cb-rejouer" type="button">Rejouer</button></div>', 'chiffres')
        + bloc('Idée 10', 'LE JEU DU <em>PLUS OU MOINS</em>', "Deux valeurs, une question : laquelle a le plus progressé en 10 ans ? Mister Coin réagit, ta série est gardée. Données de notre comparateur (hors dividendes).",
               '<div class="demo-jeu"><div class="jeu-tete"><span class="badge or" id="jeu-serie">Série : 0</span><span class="badge" id="jeu-record">Record : 0</span></div>'
               '<p class="jeu-q">Laquelle a le plus monté en 10 ans ?</p><div class="jeu-duel"><button class="duel" type="button" data-c="0"></button><span class="vs">VS</span><button class="duel" type="button" data-c="1"></button></div>'
               f'<div class="jeu-bas"><img class="jeu-coin" src="{r}assets/img/expr/reflechit.webp" alt=""><p class="jeu-msg">Choisis !</p></div></div>', 'jeu')
        + f'<script type="application/json" id="demo-data">{data}</script><script src="{r}assets/js/demo.js" defer></script>'
    )
    return f'<link rel="stylesheet" href="{r}assets/css/demo.css">' + c


def demo_suite(r):
    return (f'<link rel="stylesheet" href="{r}assets/css/demo.css">'
            f'<p class="fil"><a href="{r}demo/#transition">Démonstration</a> › Nvidia</p>'
            f'<div class="hero vt-tete"><div><div class="surtitre">Fiche entreprise · comptes au 17/11</div>'
            f'<div class="vt-ligne"><img class="vt-logo grand" src="{r}assets/img/nvda.png" alt=""><h1 class="vt-titre">NVIDIA</h1></div>'
            '<p class="chapo">Le logo, le titre et Mister Coin ont glissé depuis la carte ; le reste de la page est apparu en fondu. '
            'Sur le site, ce serait le passage de la liste des fiches à une fiche, ou d\'une vidéo à sa page.</p>'
            f'<a class="bouton or" href="{r}demo/#transition">← Revenir à la démonstration</a></div>'
            f'<img class="vt-coin grand" src="{r}assets/img/loupe.webp" alt=""></div>')
