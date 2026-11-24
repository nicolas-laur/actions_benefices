"""Page d'accueil (validée le 22/11/2026), inspirée de More Nutrition (docs/references/more_nutrition.md).
Réutilise les données et composants du site ; styles dans assets/css/theme.css, animations dans assets/js/theme.js."""
from html import escape

DECOR = ['piece1', 'eclat', 'piece_etoile', 'piece3', 'eclat', 'piece2', 'grappe', 'eclat', 'piece4']
ETINCELLE = ('<svg viewBox="-50 -50 100 100" aria-hidden="true"><defs><radialGradient id="ge" r="1"><stop offset="0" stop-color="#fff"/>'
             '<stop offset=".35" stop-color="#FFF1B8"/><stop offset="1" stop-color="#FFC24A"/></radialGradient></defs>'
             '<g class="rayons"><path d="M0-50V50M-50 0H50" /><path d="M-30-30L30 30M30-30L-30 30" class="fins"/></g>'
             '<path class="etoile" fill="url(#ge)" d="M0-44C3-14 14-3 44 0 14 3 3 14 0 44-3 14-14 3-44 0-14-3-3-14 0-44Z"/></svg>')
def deco(k, r, cls, style, extra=''):
    """élément de décor : pièce peinte (accessoires des épisodes) ou étincelle vectorielle qui rayonne"""
    nom = DECOR[k % len(DECOR)]
    if nom.startswith('eclat'):
        return f'<span class="mq-flottant mq-etincelle {cls}" aria-hidden="true" {extra} style="{style};--tw:{1.6 + (k % 5) * .35}s;--dl:-{(k * .37) % 2:.2f}s">{ETINCELLE}</span>'
    return (f'<img class="mq-flottant {cls}" src="{r}assets/deco/{nom}.webp" alt="" aria-hidden="true" '
            f'loading="lazy" {extra} style="{style}">')
def flottants(liste, r, decal=0):
    """pièces d'or peintes (accessoires des épisodes) qui défilent à des vitesses différentes : parallaxe ; les petites, floues, sont « loin »"""
    return ''.join(deco(k + decal, r, "loin" if v < 0.15 else "", f'left:{x}%;top:{y}%;width:{t}px;--rot:{(k * 37) % 70 - 35}deg;--duree:{5 + k % 4}s', f'data-vitesse="{v}"')
                   for k, (x, y, t, v) in enumerate(liste))

def accueil_v2(r, NEWS, FICHES, VIDEOS, LEXIQUE, MARCHES, bandeau, phrase_):
    n = NEWS[0]; f = FICHES[0].META
    nb_marches = len(MARCHES['series']) if MARCHES else 0
    vids = [v for v in VIDEOS if v[5]][:5]

    # 1. Couverture : fond marine plein, titre géant ligne à ligne, Mister Coin cliquable entouré de pastilles de chiffres
    def ligne(t, i, cls=''):
        return f'<span class="mq-ligne"><span class="mq-mot {cls}" style="--i:{i}">{t}</span></span>'
    pastilles = [(len(VIDEOS), 'vidéos et carrousels'), (len(LEXIQUE), 'mots du lexique'), (nb_marches, 'marchés suivis')]
    couverture = (
        '<section class="mq-plein mq-couverture hero">'
        + flottants([(47, 4, 110, .55), (22, 96, 34, .1), (36, 94, 26, .06), (52, 88, 120, .42), (57, 20, 22, .05), (93, 10, 96, .4), (88, 74, 30, .12), (70, 92, 80, .6)], r, 3)
        + '<div class="mq-dedans mq-couv-grille">'
        '<div class="mq-couv-texte" data-vitesse="0.12">'
        '<p class="mq-surtitre mq-anim" style="--i:0">La bourse sans jargon</p>'
        f'<h1 class="mq-titre">{ligne("LA BOURSE,", 1)}{ligne("ENFIN CLAIRE.", 2)}{ligne("AVEC MISTER COIN", 3, "or")}</h1>'
        '<p class="mq-chapo mq-anim" style="--i:4">Les News de chaque vendredi, des fiches entreprises, un lexique avec son quiz et des calculateurs. '
        'Chiffres exacts, sources en lien, jamais de conseil.</p>'
        f'<div class="mq-boutons mq-anim" style="--i:5"><a class="bouton or" href="{r}news/{n["slug"]}/">Les News du {n["date_txt"][:5]}</a>'
        f'<a class="bouton contour" href="{r}fiches/{f["slug"]}/">La fiche {f["nom"]}</a></div>'
        '</div>'
        f'<div class="coin-scene mq-scene" data-r="{r}" data-vitesse="-0.1"><span class="coin-bulle" aria-live="polite"></span>'
        '<svg class="mq-arc" viewBox="0 0 400 400" aria-hidden="true"><circle cx="200" cy="200" r="182" pathLength="1"/></svg>'
        + ''.join(f'<span class="mq-pastille p{k}" data-vitesse="{(0.14, -0.1, 0.22)[k]}" style="--i:{k + 2}"><b>{v}</b>{escape(t)}</span>' for k, (v, t) in enumerate(pastilles))
        + ''.join(deco(1, r, 'autour', f'left:{x}%;top:{y}%;width:{t}px') for x, y, t in ((14, 30, 34), (82, 22, 26), (88, 78, 38), (24, 86, 22)))
        + f'<img class="coin-anim" src="{r}assets/img/salut.webp" alt="Mister Coin salue : clique sur lui" tabindex="0" role="button">'
        '<button class="coin-son" type="button" aria-label="Activer le son">🔇</button>'
        '<span class="mq-note n1" aria-hidden="true"><svg viewBox="0 0 110 80"><path class="mq-trait" pathLength="1" d="M104 8 C 84 6, 52 14, 36 40 C 28 52, 22 62, 14 70 M12 52 L13 71 L31 67"/></svg>'
        '<span>Clique-moi !</span></span>'
        '</div></div></section>'
        f'<script src="{r}assets/js/coin.js" defer></script>')

    # 2. Récit épinglé : Mister Coin reste au centre et change de pose pendant que défilent les rubriques
    etapes = [
        ('lit_journal_v2_titre', 'Chaque vendredi', 'LES NEWS', "La semaine en bourse en un carrousel : ce qui s'est passé, les chiffres et la réaction des marchés.",
         f'{r}news/{n["slug"]}/', f'Lire « {phrase_(n["titre"])} »', f'<img class="mq-visuel incline" src="{r}assets/news/{n["slug"]}/01.webp" alt="Couverture des News" loading="lazy">',
         'Nouveau chaque vendredi'),
        ('loupe', 'Fiches entreprises', 'LES FICHES', "Une entreprise passée à la loupe : ce qu'elle vend, ce qu'elle gagne, ce qui l'attend. Graphiques à explorer.",
         f'{r}fiches/{f["slug"]}/', f'Que vaut {f["nom"]} ?', f'<div class="mq-visuel carte-logo"><img src="{r}assets/img/{f["logo"]}" alt="{f["nom"]}"><span>Cours et PER mis à jour chaque soir</span></div>',
         'Survole les graphiques'),
        ('question', 'Lexique et quiz', 'LE LEXIQUE', "Du livret A à l'option de vente, chaque mot expliqué avec un exemple concret, puis un quiz débutant, initié ou expert.",
         f'{r}lexique/#quiz', 'Teste tes connaissances !', '<div class="mq-visuel sigles">' + ''.join(f'<span>{e[1]}</span>' for e in [x for x in LEXIQUE if x[1].isupper()][:9]) + '</div>',
         '10 questions'),
        ('reflechit', 'Calculateurs', 'LES CALCULS', "Intérêts composés, dividendes, PEA ou CTO, et les performances des grandes places boursières depuis 1990.",
         f'{r}calculateurs/', 'Faire mes calculs',
         '<svg class="mq-visuel courbe" viewBox="0 0 300 160" aria-hidden="true"><path class="mq-trait" pathLength="1" d="M10 150 C 80 145, 120 130, 160 105 S 240 40, 290 10"/>'
         '<path class="mq-trait pointille" pathLength="1" d="M10 150 L 290 95"/></svg>', 'Ta courbe, année par année'),
    ]
    recit = (
        '<section class="mq-recit mq-plein" aria-label="Ce que tu trouveras ici">'
        '<div class="mq-collant">'
        + ''.join(deco(k + 2, r, "recit" + (" loin" if d < 1 else ""), f'left:{x}%;top:{y}%;width:{t}px;--d:{d};--rot:{k * 23}deg')
                  for k, (x, y, t, d) in enumerate([(-3, 74, 110, 1.6), (46, 2, 40, .6), (50, 90, 70, 1.1), (95, 4, 120, 1.8), (97, 58, 40, .5), (-1, 22, 32, .4), (58, 96, 56, .8)]))
        + '<div class="mq-coin-centre">' + ''.join(f'<img class="mq-pose{" actif" if k == 0 else ""}" data-k="{k}" src="{r}assets/img/{e[0]}.webp" alt="" loading="lazy">' for k, e in enumerate(etapes)) + '</div>'
        + ''.join(f'<article class="mq-etape{" actif" if k == 0 else ""} {"gauche" if k % 2 == 0 else "droite"}" data-k="{k}">'
                  f'<p class="mq-surtitre">{escape(st)}</p><h2 class="mq-grand">{h}</h2><p>{escape(tx)}</p><a class="bouton" href="{lien}">{escape(lab)}</a></article>'
                  f'<div class="mq-cote{" actif" if k == 0 else ""} {"droite" if k % 2 == 0 else "gauche"}" data-k="{k}">{vis}<span class="mq-note">{escape(note)}</span></div>'
                  for k, (po, st, h, tx, lien, lab, vis, note) in enumerate(etapes))
        + '<ol class="mq-points" aria-hidden="true">' + ''.join(f'<li data-k="{k}"{" class=actif" if k == 0 else ""}></li>' for k in range(len(etapes))) + '</ol>'
        '</div>' + ''.join(f'<div class="mq-repere" data-k="{k}"></div>' for k in range(len(etapes))) + '</section>')

    # 3. Tracé doré qui se dessine au défilement, puis les vidéos en éventail
    trace = ('<div class="mq-plein mq-trace-zone" aria-hidden="true"><svg viewBox="0 0 1440 220" preserveAspectRatio="none">'
             '<path class="mq-trace" pathLength="1" d="M-20 60 C 240 220, 420 -40, 720 110 S 1180 220, 1460 40"/></svg></div>')
    eventail = ('<section class="mq-dedans mq-videos"><p class="mq-surtitre mq-anim">TikTok et Instagram</p>'
                '<h2 class="mq-grand mq-anim" style="--i:1">NOS DERNIÈRES <em>VIDÉOS</em></h2>'
                '<div class="mq-eventail">' + ''.join(
                    f'<a class="mq-vcarte mq-anim" data-vitesse="{(0.06, 0.16, 0.26, 0.16, 0.06)[k]}" style="--i:{k};--r:{(k - 2) * 6}deg;--y:{abs(k - 2) * 18}px" href="{r}videos/">'
                    f'<img src="{r}assets/videos/{vig}" alt="" loading="lazy"><b>{escape(t)}</b></a>'
                    for k, (d, t, ty, tk, ig, vig) in enumerate(vids)) + '</div>'
                f'<p class="mq-centre"><a class="bouton" href="{r}videos/">Toutes les vidéos</a></p></section>')

    # 4. Nos règles, coches qui apparaissent une à une, sur fond or clair
    regles = [('Des chiffres exacts', 'Vérifiés et sourcés, en lien sous chaque graphique.'), ('Jamais de conseil', "On explique, tu décides. Rien ici n'est une recommandation."),
              ('En euros', 'Montants convertis au taux de la BCE du jour retenu.'), ('Avec le sourire', 'Mister Coin est là pour rendre la bourse moins austère.')]
    regles_html = ('<section class="mq-plein mq-regles">' + flottants([(3, 16, 100, .45), (48, 6, 26, .06), (93, 70, 90, .35), (60, 90, 22, .05)], r, 4) + '<div class="mq-dedans">'
                   '<h2 class="mq-grand mq-anim">NOS <em>RÈGLES</em></h2><ul class="mq-liste">'
                   + ''.join(f'<li class="mq-anim" style="--i:{k + 1}"><span class="mq-coche" aria-hidden="true">✓</span><div><b>{escape(a)}</b><p>{escape(b)}</p></div></li>' for k, (a, b) in enumerate(regles))
                   + f'</ul><img class="mq-anim mq-coin-regles" data-vitesse="0.22" style="--i:5" src="{r}assets/img/pouce.webp" alt="" loading="lazy"></div></section>')

    # 5. Fin : rendez-vous vendredi, sur fond marine
    fin = ('<section class="mq-plein mq-fin">' + flottants([(6, 12, 90, .4), (40, 80, 26, .06), (78, 8, 120, .5), (92, 66, 30, .1)], r, 2) + '<div class="mq-dedans mq-fin-grille">'
           f'<img class="mq-anim" data-vitesse="0.2" src="{r}assets/img/rire.webp" alt="Mister Coin rit" loading="lazy">'
           '<div><h2 class="mq-grand mq-anim" style="--i:1">RENDEZ-VOUS <em>VENDREDI</em></h2>'
           '<p class="mq-anim" style="--i:2">Les News de la semaine arrivent chaque vendredi sur TikTok, Instagram et ici. La lettre du dimanche est en préparation.</p>'
           f'<div class="mq-boutons mq-anim" style="--i:3"><a class="bouton or" href="{r}news/">Toutes les News</a><a class="bouton contour" href="{r}videos/">Nos vidéos</a></div>'
           '</div></div></section>')

    return (couverture + bandeau(r) + recit + trace + eventail + regles_html + fin
            )
