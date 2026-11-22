"""Maquette de la nouvelle page d'accueil, inspirée de More Nutrition (docs/references/more_nutrition.md).
Publiée à /maquette-accueil/ (non référencée) pour validation par Nicolas avant de remplacer l'accueil.
Réutilise les données et composants du site ; styles dans assets/css/maquette.css, animations dans assets/js/maquette.js."""
from html import escape

def maquette_accueil(r, NEWS, FICHES, VIDEOS, LEXIQUE, MARCHES, bandeau, phrase_):
    n = NEWS[0]; f = FICHES[0].META
    nb_marches = len(MARCHES['series']) if MARCHES else 0
    vids = [v for v in VIDEOS if v[5]][:5]

    # 1. Couverture : fond marine plein, titre géant ligne à ligne, Mister Coin cliquable entouré de pastilles de chiffres
    def ligne(t, i, cls=''):
        return f'<span class="mq-ligne"><span class="mq-mot {cls}" style="--i:{i}">{t}</span></span>'
    pastilles = [(len(VIDEOS), 'vidéos et carrousels'), (len(LEXIQUE), 'mots du lexique'), (nb_marches, 'marchés suivis')]
    couverture = (
        '<section class="mq-plein mq-couverture hero">'
        '<div class="mq-dedans mq-couv-grille">'
        '<div class="mq-couv-texte">'
        '<p class="mq-surtitre mq-anim" style="--i:0">La bourse sans jargon</p>'
        f'<h1 class="mq-titre">{ligne("LA BOURSE,", 1)}{ligne("ENFIN CLAIRE.", 2)}{ligne("AVEC MISTER COIN", 3, "or")}</h1>'
        '<p class="mq-chapo mq-anim" style="--i:4">Les News de chaque vendredi, des fiches entreprises, un lexique avec son quiz et des calculateurs. '
        'Chiffres exacts, sources en lien, jamais de conseil.</p>'
        f'<div class="mq-boutons mq-anim" style="--i:5"><a class="bouton or" href="{r}news/{n["slug"]}/">Les News du {n["date_txt"][:5]}</a>'
        f'<a class="bouton contour" href="{r}fiches/{f["slug"]}/">La fiche {f["nom"]}</a></div>'
        '</div>'
        f'<div class="coin-scene mq-scene" data-r="{r}"><span class="coin-bulle" aria-live="polite"></span>'
        '<svg class="mq-arc" viewBox="0 0 400 400" aria-hidden="true"><circle cx="200" cy="200" r="182" pathLength="1"/></svg>'
        + ''.join(f'<span class="mq-pastille p{k}" style="--i:{k + 2}"><b>{v}</b>{escape(t)}</span>' for k, (v, t) in enumerate(pastilles))
        + f'<img class="coin-anim" src="{r}assets/img/salut.webp" alt="Mister Coin salue : clique sur lui" tabindex="0" role="button">'
        '<button class="coin-son" type="button" aria-label="Activer le son">🔇</button>'
        '<span class="mq-note n1" aria-hidden="true">Clique-moi !'
        '<svg viewBox="0 0 120 70"><path class="mq-trait" pathLength="1" d="M8 10 C 40 4, 80 18, 96 52 M84 44 L97 54 L104 40"/></svg></span>'
        '</div></div></section>'
        f'<script src="{r}assets/js/coin.js" defer></script>')

    # 2. Récit épinglé : Mister Coin reste au centre et change de pose pendant que défilent les rubriques
    etapes = [
        ('lit_journal_v2_titre', 'Chaque vendredi', 'LES NEWS', "La semaine en bourse en un carrousel : ce qui s'est passé, les chiffres et la réaction des marchés.",
         f'{r}news/{n["slug"]}/', f'Lire « {phrase_(n["titre"])} »', f'<img class="mq-visuel incline" src="{r}assets/news/{n["slug"]}/01.webp" alt="Couverture des News" loading="lazy">',
         'Nouveau chaque vendredi'),
        ('loupe', 'Fiches entreprises', 'LES FICHES', "Une entreprise passée à la loupe : ce qu'elle vend, ce qu'elle gagne, ce qui l'attend. Graphiques à explorer.",
         f'{r}fiches/{f["slug"]}/', f'Que vaut {f["nom"]} ?', f'<div class="mq-visuel carte-logo"><img src="{r}assets/img/{f["logo"]}" alt="{f["nom"]}"><span>Chiffres au {f["chiffres_au"]}</span></div>',
         'Survole les graphiques'),
        ('question', 'Lexique et quiz', 'LE LEXIQUE', "PEA, ETF, PFU, DCA… chaque sigle expliqué avec un exemple concret, puis un quiz pour vérifier.",
         f'{r}lexique/#quiz', 'Teste tes connaissances !', '<div class="mq-visuel sigles">' + ''.join(f'<span>{e[1]}</span>' for e in LEXIQUE[:9]) + '</div>',
         '10 questions'),
        ('reflechit', 'Calculateurs', 'LES CALCULS', "Intérêts composés, dividendes, PEA ou CTO, et les performances des grandes places boursières depuis 1990.",
         f'{r}calculateurs/', 'Faire mes calculs',
         '<svg class="mq-visuel courbe" viewBox="0 0 300 160" aria-hidden="true"><path class="mq-trait" pathLength="1" d="M10 150 C 80 145, 120 130, 160 105 S 240 40, 290 10"/>'
         '<path class="mq-trait pointille" pathLength="1" d="M10 150 L 290 95"/></svg>', 'Ta courbe, année par année'),
    ]
    recit = (
        '<section class="mq-recit" aria-label="Ce que tu trouveras ici">'
        '<div class="mq-collant">'
        '<div class="mq-coin-centre">' + ''.join(f'<img class="mq-pose{" actif" if k == 0 else ""}" data-k="{k}" src="{r}assets/img/{e[0]}.webp" alt="" loading="lazy">' for k, e in enumerate(etapes)) + '</div>'
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
                    f'<a class="mq-vcarte mq-anim" style="--i:{k};--r:{(k - 2) * 6}deg;--y:{abs(k - 2) * 18}px" href="{r}videos/">'
                    f'<img src="{r}assets/videos/{vig}" alt="" loading="lazy"><b>{escape(t)}</b></a>'
                    for k, (d, t, ty, tk, ig, vig) in enumerate(vids)) + '</div>'
                f'<p class="mq-centre"><a class="bouton" href="{r}videos/">Toutes les vidéos</a></p></section>')

    # 4. Nos règles, coches qui apparaissent une à une, sur fond or clair
    regles = [('Des chiffres exacts', 'Vérifiés et sourcés, en lien sous chaque graphique.'), ('Jamais de conseil', "On explique, tu décides. Rien ici n'est une recommandation."),
              ('En euros', 'Montants convertis au taux de la BCE du jour retenu.'), ('Avec le sourire', 'Mister Coin est là pour rendre la bourse moins austère.')]
    regles_html = ('<section class="mq-plein mq-regles"><div class="mq-dedans">'
                   '<h2 class="mq-grand mq-anim">NOS <em>RÈGLES</em></h2><ul class="mq-liste">'
                   + ''.join(f'<li class="mq-anim" style="--i:{k + 1}"><span class="mq-coche" aria-hidden="true">✓</span><div><b>{escape(a)}</b><p>{escape(b)}</p></div></li>' for k, (a, b) in enumerate(regles))
                   + f'</ul><img class="mq-anim mq-coin-regles" style="--i:5" src="{r}assets/img/pouce.webp" alt="" loading="lazy"></div></section>')

    # 5. Fin : rendez-vous vendredi, sur fond marine
    fin = ('<section class="mq-plein mq-fin"><div class="mq-dedans mq-fin-grille">'
           f'<img class="mq-anim" src="{r}assets/img/rire.webp" alt="Mister Coin rit" loading="lazy">'
           '<div><h2 class="mq-grand mq-anim" style="--i:1">RENDEZ-VOUS <em>VENDREDI</em></h2>'
           '<p class="mq-anim" style="--i:2">Les News de la semaine arrivent chaque vendredi sur TikTok, Instagram et ici. La lettre du dimanche est en préparation.</p>'
           f'<div class="mq-boutons mq-anim" style="--i:3"><a class="bouton or" href="{r}news/">Toutes les News</a><a class="bouton contour" href="{r}videos/">Nos vidéos</a></div>'
           '</div></div></section>')

    return (f'<link rel="stylesheet" href="{r}assets/css/maquette.css">'
            '<p class="mq-bandeau-maquette">Maquette de la future page d\'accueil, pour validation. Fais défiler la page : les animations font partie de la proposition.</p>'
            + couverture + bandeau(r) + recit + trace + eventail + regles_html + fin
            + f'<script src="{r}assets/js/maquette.js" defer></script>')
