"""Générateur du site actionsbenefices.com. Usage : python3 site/build.py  →  site/_site/ (publié par GitHub Pages).
Toutes les pages sont des dossiers avec index.html ; les liens sont relatifs (variable r)."""
import json, re, shutil, sys
from datetime import date
from html import escape
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ICI = Path(__file__).resolve().parent
sys.path[:0] = [str(ICI), str(ICI/'contenu')]
from composants import tuile, grille, lecture, carte, fr, coin_section
import fiche_nvidia
from news import NEWS
from pictos import PICTOS
from accueil_v2 import accueil_v2, flottants
from donnees import LEXIQUE, VIDEOS, QUIZ, SP_PEA as SP_PEA_, SP_PFU as SP_PFU_

SITE = dict(nom='Actions Bénéfices', url='https://actionsbenefices.com',
            menu=[('fiches/', 'Fiches entreprises'), ('news/', 'Les News'), ('lexique/', 'Lexique'), ('calculateurs/', 'Calculateurs'),
                  ('videos/', 'Vidéos')],
            tiktok='https://www.tiktok.com/@actions_bnfices', instagram='https://www.instagram.com/actions_benefices/',
            lettre_action=None)  # adresse du formulaire Brevo une fois le compte ouvert
# une entrée par entreprise : ses versions trimestrielles, la plus récente d'abord (versions archivées : site/outils/MAJ_FICHES.md)
ENTREPRISES = [[fiche_nvidia]]
FICHES = [v[0] for v in ENTREPRISES]      # versions à jour (liste des fiches, accueil)
MOIS_T = {1: 'janvier à mars', 2: 'avril à juin', 3: 'juillet à septembre', 4: 'octobre à décembre'}

def historique(versions, r, actuelle):
    """section « Historique des comptes » d'une fiche : une sous-section par année, un bloc par trimestre civil"""
    ans = {}
    for v in versions: ans.setdefault(v.META['annee'], []).append(v)
    blocs = ''
    for an in sorted(ans, reverse=True):
        lignes = ''
        for v in sorted(ans[an], key=lambda v: -v.META['trimestre']):
            m = v.META; ici = v is actuelle; a_jour = v is versions[0]
            lien = f'{r}fiches/{m["slug"]}/' + ('' if a_jour else f'{m["version"]}/')
            etat = '<span class="badge or">Version à jour</span>' if a_jour else '<span class="badge">Archivée</span>'
            titre = f'T{m["trimestre"]} {an}'
            lignes += (f'<li class="hist-t{" ici" if ici else ""}"><div><b>{titre}</b> {etat}{" <span class=\"gris petit\">(cette page)</span>" if ici else ""}</div>'
                       f'<span class="gris">Comptes du {m["comptes"]}, publiés le {m["comptes_publies"][8:10]}/{m["comptes_publies"][5:7]}/{m["comptes_publies"][:4]}</span>'
                       + ('' if ici else f'<a href="{lien}">Voir cette version →</a>') + '</li>')
        blocs += f'<div class="hist-an"><h4>{an}</h4><ul>{lignes}</ul></div>'
    return (f'<section class="section" id="historique"><h3 style="font-size:22px">Historique des comptes</h3>'
            f'<p class="gris" style="margin:0 0 14px">La fiche est mise à jour après chaque publication de résultats. Les trimestres sont ceux du calendrier '
            f'({", ".join(f"T{k} : {x}" for k, x in MOIS_T.items())}), quel que soit l\'exercice comptable de l\'entreprise. Chaque version passée reste consultable, avec ses chiffres et son cours de l\'époque.</p>'
            f'{blocs}</section>')

def page_fiche(versions, v):
    """corps d'une version de fiche : bandeau si archivée, contenu, historique"""
    def corps(r):
        m = v.META; tete = ''
        if v is not versions[0]:
            tete = (f'<p class="carte" style="padding:14px 20px;border-color:var(--filet-or)">Version archivée : comptes du T{m["trimestre"]} {m["annee"]} ({m["comptes"]}), '
                    f'cours figé au {v.CN["date"][8:10]}/{v.CN["date"][5:7]}/{v.CN["date"][:4]}. <a href="{r}fiches/{m["slug"]}/">Voir la fiche à jour →</a></p>')
        return tete + v.corps(r) + historique(versions, r, v)
    return corps
# rappel du processus trimestriel (site/outils/MAJ_FICHES.md) : la tâche du soir relaie ces alertes à Nicolas
import datetime as _dt
for _m in FICHES:
    _j = (_dt.date.fromisoformat(_m.META['prochains_resultats']) - _dt.date.today()).days
    if not _m.META.get('date_confirmee') and _j <= 60:
        print(f"RAPPEL fiche {_m.META['nom']} : date des prochains résultats à confirmer ({_m.META['prochains_txt']}), chercher l'annonce officielle")
    if 0 <= _j <= 7:
        print(f"RAPPEL fiche {_m.META['nom']} : résultats dans {_j} jour(s), le {_m.META['prochains_resultats'][8:10]}/{_m.META['prochains_resultats'][5:7]} ; prévoir la session de mise à jour")
    if _dt.date.today().isoformat() > _m.META['prochains_resultats']:
        print(f"ALERTE fiche {_m.META['nom']} : résultats attendus ({_m.META['prochains_txt']}) passés, comptes à mettre à jour (site/outils/MAJ_FICHES.md)")
SORTIE = ICI/'_site'
# relevé des marchés (Yahoo Finance), écrit chaque nuit par outils/marches.py ; absent : pas de bandeau ni de graphique
_M = ICI/'donnees'/'marches.json'
MARCHES = json.loads(_M.read_text()) if _M.exists() else None
env = Environment(loader=FileSystemLoader(ICI/'templates'), autoescape=True)
PAGES = []
# empreinte du contenu de chaque fichier de assets/ : ajoutée aux adresses (?v=…) pour que les navigateurs ne gardent pas une ancienne version en cache
import hashlib
def _empreinte(f): return hashlib.sha1(f.read_bytes()).hexdigest()[:8]
EMPREINTES = {str(f.relative_to(ICI)).replace('\\', '/'): _empreinte(f) for f in (ICI/'assets').rglob('*') if f.is_file()}
VERSION = hashlib.sha1(''.join(sorted(EMPREINTES.values())).encode()).hexdigest()[:8]
_RE_ASSET = re.compile(r'(assets/[\w./-]+\.(?:css|js|webp|png|jpg|svg|mp3|webm|json|woff2))(?=["\')\s])')
def versionne(html): return _RE_ASSET.sub(lambda m: m.group(1) + '?v=' + EMPREINTES.get(m.group(1), VERSION), html)

# racine absolue, utile seulement pour la page 404 (servie à n'importe quelle adresse)
RACINE = '/'
DOMAINE = 'actionsbenefices.com'
def page(chemin, titre, description, corps, rubrique=None, r=None, **kw):
    """chemin : '/' ou '/a/b/' ; corps : fonction(r) → HTML"""
    prof = chemin.strip('/').count('/') + 1 if chemin != '/' else 0
    r = r if r is not None else '../'*prof
    html = env.get_template('page.html').render(SITE=SITE, VERSION=VERSION, titre=titre, description=description, chemin=chemin, r=r,
                                                rubrique=rubrique, corps=corps(r), **kw)
    f = SORTIE/chemin.strip('/')/'index.html'; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(versionne(insecables(html)))
    PAGES.append(chemin)

def insecables(html):
    """espace insécable entre les milliers (« 50 000 »), dans le texte seulement, jamais dans les attributs ni les coordonnées SVG"""
    return re.sub(r'>[^<]+<', lambda m: re.sub(r'(\d) (?=\d{3}(?!\d))', '\\1\u00a0', m.group(0)), html)
def jj(d): return f'{d[8:]}/{d[5:7]}/{d[:4]}'
def entete(surtitre, h1, mot, chapo, pose=None, r=''):
    """en-tête de page façon couverture de l'accueil : halo doré, pièces peintes en parallaxe, titre qui monte, Mister Coin en léger décalage"""
    img = f'<img class="tete-coin mq-anim" style="--i:3" data-vitesse="0.12" src="{r}assets/img/{pose}.webp" alt="Mister Coin">' if pose else ''
    return (f'<div class="hero tete">' + flottants([(64, 84, 54, .35), (84, 90, 30, .08), (97, 32, 50, .25), (58, 94, 24, .05)], r, 1)
            + f'<div><div class="surtitre mq-anim">{surtitre}</div><h1><span class="mq-ligne"><span class="mq-mot" style="--i:1">{h1} <em>{mot}</em></span></span></h1>'
            f'<p class="chapo mq-anim" style="--i:2">{chapo}</p></div>{img}</div>')
def vignette(r, lien, badge, titre, texte, date_txt='', pose=None, logo=None):
    im = f'<img src="{r}assets/img/{logo}" alt="" style="height:32px;align-self:flex-start;margin:0">' if logo else ''
    pz = f'<img src="{r}assets/img/{pose}.webp" alt="">' if pose else ''
    return (f'<a class="vignette" href="{r}{lien}"><span class="badge">{badge}</span>{im}<h3>{titre}</h3>'
            f'<span class="gris">{texte}</span>{f"<span class=date>{date_txt}</span>" if date_txt else ""}{pz}</a>')
def liens(src): return ' · '.join(f'<a href="{u}">{escape(n)}</a>' for n, u in src)

# ---------- accueil ----------
def bandeau(r):
    if not MARCHES or not MARCHES.get('bandeau'): return ''
    b = MARCHES['bandeau']; d = next((x['date'] for x in b if x['id'] in ('cac40', 'sp500')), b[0]['date'])
    def it(x):
        sens = 'hausse' if x['var'] > 0 else 'baisse' if x['var'] < 0 else 'stable'
        fl = '▲' if x['var'] > 0 else '▼' if x['var'] < 0 else '■'
        return f'<li class="{sens}"><b>{escape(x["nom"])}</b> <span>{fl} {("+" if x["var"] > 0 else "−" if x["var"] < 0 else "")}{fr(abs(x["var"]), 2)} %</span></li>'
    items = ''.join(it(x) for x in b)
    return (f'<div class="bandeau" aria-label="Variation de la dernière séance"><span class="bandeau-titre">Dernière séance · {jj(d)}</span>'
            f'<div class="bandeau-fenetre"><ul class="bandeau-piste">{items}</ul><ul class="bandeau-piste" aria-hidden="true">{items}</ul></div>'
            f'<a class="bandeau-lien" href="{r}calculateurs/#performances">Comparer →</a></div>')
# ---------- fiches ----------
def fiches(r):
    return (entete('Une entreprise, ses chiffres', 'FICHES', 'ENTREPRISES', "Croissance, rentabilité, solidité, dividende et rivaux : les comptes remis à plat, en euros, sources en lien. Aucun verdict, aucun objectif de cours.", 'loupe', r)
            + grille(*[vignette(r, f'fiches/{m.META["slug"]}/', 'Fiche n°' + str(i+1), m.META['titre'], m.META['accroche'], 'Comptes du ' + m.META['comptes'] + ' · cours et PER du soir', logo=m.META['logo'])
                       for i, m in enumerate(FICHES)], mn=320))

# ---------- news ----------
SIGLES = ('US', 'IA', 'PDG', 'CAC', 'S&P', 'BCE', 'ETF', 'EBITDA', 'FTC', 'ANT', 'GTA', 'DKK', 'TV')
def phrase_(t):
    """« RACHAT D'ACTIONS EN PLUS » → « Rachat d'actions en plus », en gardant les sigles"""
    m = t[0] + t[1:].lower() if t.isupper() else t
    for sg in SIGLES: m = re.sub(rf'\b{re.escape(sg.lower())}\b', sg, m, flags=re.I) if sg != 'ANT' else m
    for a, b in (('états-unis', 'États-Unis'), ('nasdaq', 'Nasdaq'), ('coreweave', 'CoreWeave'), ('walmart', 'Walmart'), ('home depot', 'Home Depot'),
                 ('dow jones', 'Dow Jones'), ('fed', 'Fed'), ('total /', 'Total /'), ('sanofi', 'Sanofi'), ('lvmh', 'LVMH'), ('brent', 'Brent'),
                 ('ftc', 'FTC'), ('ebitda', 'EBITDA'), ('noël', 'Noël'), ('iphone', 'iPhone'), ('wegovy', 'Wegovy')):
        m = re.sub(rf'\b{a}\b', b, m, flags=re.I)
    return m
def diapo(n, i): return f'assets/news/{n["slug"]}/{i:02d}.webp'
def galerie(r, n):
    ims = ''.join(f'<button class="gal-diapo" type="button" data-i="{i-1}" aria-label="Agrandir la diapo {i} sur {n["diapos"]}">'
                  f'<img src="{r}{diapo(n, i)}" alt="Diapo {i} du carrousel Les News du {n["date_txt"]}" loading="lazy" width="720" height="1280"></button>' for i in range(1, n['diapos']+1))
    return (f'<div class="galerie" data-galerie><button class="gal-fleche prec" type="button" aria-label="Diapos précédentes">‹</button>'
            f'<div class="gal-piste" tabindex="0" aria-label="Diapos du carrousel">{ims}</div>'
            f'<button class="gal-fleche suiv" type="button" aria-label="Diapos suivantes">›</button></div>')
def coin_bulle(r, pose, bulle):
    return (f'<figure class="coin"><span class="bulle">{escape(bulle)}</span><img src="{r}assets/img/{pose}.webp" alt="Mister Coin" loading="lazy"></figure>')
def news_liste(r):
    cartes = ''.join(f'<a class="vignette news" href="{r}news/{n["slug"]}/"><img class="couv" src="{r}{diapo(n, 1)}" alt="Couverture des News du {n["date_txt"]}" loading="lazy">'
                     f'<div class="pile" style="gap:8px"><span class="badge">Semaine {escape(n["semaine"])}</span><h3>{escape(n["titre"])}</h3>'
                     f'<span class="gris">{escape(n["chapo"])}</span><span class="date">Les News du {n["date_txt"]} · {len(n["items"])} sujets · {n["diapos"]} diapos</span></div></a>' for n in NEWS)
    return (entete('Chaque vendredi', 'LES', 'NEWS', "La semaine en bourse : ce qui s'est passé, les chiffres, et comment la bourse a réagi. Le carrousel complet et tous les détails.", 'lit_journal_v2_titre', r)
            + f'<div class="grille" style="--min:330px">{cartes}</div>')
def news_page(n):
    def c(r):
        som = ''.join(f'<a href="#n{i}">{escape(it["sujet"])}</a>' for i, it in enumerate(n['items'], 1))
        it_html = ''
        for i, it in enumerate(n['items'], 1):
            tu = grille(*[tuile(e, escape(phrase_(l)), escape(v), escape(x)) for l, v, x, e in it["chiffres"]], mn=200)
            it_html += (f'<section class="section" id="n{i}"><div><div class="surtitre">{i:02d} · {escape(it["sujet"])}</div><h2>{escape(it["titre"].upper())}</h2></div>'
                        f'<p class="fait">{escape(it["fait"])}</p>{tu}'
                        + (f'<p class="texte" style="margin:0">{escape(it["detail"])}</p>' if it['detail'] else '')
                        + f'<div class="lecture">{coin_bulle(r, it["pose"], it["bulle"])}<p><span aria-hidden="true">💡 </span>{escape(it["lecture"])}</p></div>'
                        + (f'<p class="source">Sources : {liens(it["sources"])}</p>' if it['sources'] else '') + '</section>')
        bilan = (f'<section class="section"><div><div class="surtitre">À retenir</div><h2>LE MATCH DE <em>LA SEMAINE</em></h2></div>'
                 + carte(f'<p style="margin:0;font-size:18px">{escape(n["bilan"])}</p>') + '</section>') if n['bilan'] else ''
        return (f'<p class="fil"><a href="{r}news/">Les News</a> › {n["date_txt"]}</p>'
                f'<div class="hero news-hero"><div><div class="surtitre">Les News du {n["date_txt"]} · {escape(n["semaine"])}</div>'
                f'<h1>{escape(n["titre"].upper())}</h1><p class="chapo">{escape(n["chapo"])}</p>'
                f'<nav class="sommaire" aria-label="Les sujets">{som}</nav><p class="gris petit" style="margin:0">{escape(n["note"])}</p></div>'
                f'<button class="kiosque gal-ouvre" type="button" data-i="0" aria-label="Ouvrir le carrousel"><img src="{r}{diapo(n, 1)}" alt="Couverture : le kiosque des News"><span>Voir les {n["diapos"]} diapos</span></button></div>'
                f'<section class="section" id="carrousel"><div><div class="surtitre">Tel que publié sur TikTok et Instagram</div><h2>LE <em>CARROUSEL</em></h2></div>{galerie(r, n)}</section>'
                + it_html + bilan
                + f'<p class="gris petit">Contenu pédagogique, pas un conseil en investissement. Les performances passées ne préjugent pas des performances futures.</p>'
                + f'<script src="{r}assets/js/galerie.js" defer></script>')
    return c

# ---------- lexique ----------
def lex_voir(r, voir, pop=False):
    out = []
    for x in voir:
        if x == 'interets-composes':
            out.append(f'<a class="bouton clair" href="{r}calculateurs/#composes">Intérêts composés</a>')
        else:
            sig = next(l[1] for l in LEXIQUE if l[0] == x)
            out.append(f'<a class="bouton clair" href="{r}lexique/{x}/"{f" data-terme={chr(34)}{x}{chr(34)}" if pop else ""}>{sig}</a>')
    return ''.join(out)
def lex_contenu(r, e, pop=False):
    """corps d'une définition : utilisé dans la pop-up de la liste et dans la page du terme"""
    s_, sig, dev, expl, exemple, src, voir = e
    return (f'<p class="lex-expl">{escape(expl)}</p>'
            f'<div class="exemple"><div class="surtitre">Exemple concret</div><p>{escape(exemple)}</p></div>'
            + (f'<p class="source">Source : {liens(src)}</p>' if src else '')
            + (f'<div><div class="surtitre" style="margin-bottom:10px">Voir aussi</div><div class="pastilles">{lex_voir(r, voir, pop)}</div></div>' if voir else ''))
def quiz(r):
    data = json.dumps([dict(q=q, c=c, b=b, e=e, p=p) for q, c, b, e, p in QUIZ], ensure_ascii=False).replace('</', '<\\/')
    return (f'<section class="section" id="quiz"><div><div class="surtitre">Teste-toi</div><h2>TESTE TES <em>CONNAISSANCES !</em></h2>'
            f'<p class="gris" style="margin:6px 0 0">{len(QUIZ)} questions sur les mots de la bourse. Réponds, Mister Coin te corrige.</p></div>'
            f'<div class="carte quiz" data-quiz data-r="{r}"><noscript>Le quiz a besoin de JavaScript.</noscript></div>'
            f'<script type="application/json" id="quiz-donnees">{data}</script></section>')
def lex_liste(r):
    cartes = ''.join(f'<a class="vignette terme-carte" href="{r}lexique/{e[0]}/" data-terme="{e[0]}"><span class="terme">{e[1]}</span><b>{escape(e[2])}</b>'
                     f'<span class="gris">{escape(e[3])}</span><span class="date">Voir la définition et un exemple →</span></a>' for e in LEXIQUE)
    tpl = ''.join(f'<template id="t-{e[0]}"><div class="surtitre">Lexique</div><h2 class="lex-sigle">{e[1]}</h2><p class="lex-dev">{escape(e[2])}</p>{lex_contenu(r, e, True)}</template>' for e in LEXIQUE)
    return (entete('Les sigles de la bourse', 'LE', 'LEXIQUE', "Dix mots pour comprendre ce qu'on raconte, dont un piège. Clique sur un sigle pour sa définition et un exemple concret, puis teste-toi avec le quiz.", 'site_dictionnaire', r)
            + f'<div class="pastilles" style="margin-bottom:18px"><a class="bouton or" href="#quiz">Teste tes connaissances !</a></div>'
            + f'<div class="grille" style="--min:250px">{cartes}</div>' + tpl
            + f'<dialog class="fiche-terme" aria-label="Définition"><button class="v-fermer sombre" type="button" aria-label="Fermer">×</button><div class="fiche-corps"></div>'
              f'<img src="{r}assets/img/montre.webp" alt="" class="fiche-coin"></dialog>'
            + quiz(r) + f'<script src="{r}assets/js/lexique.js" defer></script>')
def lex_page(e):
    s_, sig, dev, expl, exemple, src, voir = e
    def c(r):
        return (f'<p class="fil"><a href="{r}lexique/">Lexique</a> › {sig}</p><div class="hero"><div><div class="surtitre">Lexique</div><h1>{sig}</h1>'
                f'<p class="chapo"><b>{escape(dev)}</b></p></div><img src="{r}assets/img/montre.webp" alt="Mister Coin montre la définition"></div>'
                f'<div class="pile texte">{lex_contenu(r, e)}<p><a class="bouton or" href="{r}lexique/#quiz">Teste tes connaissances !</a></p></div>')
    return c

# ---------- calculateurs ----------
def calculateurs(r):
    def bloc(ident, titre, mot, sous, champs, sortie, note, coin=None):
        ch = ''.join(f'<div><label for="{i}">{l}</label><input id="{i}" type="number" inputmode="decimal" value="{v}" min="0" step="{st}"></div>' if typ == 'n'
                     else f'<div><label for="{i}">{l}</label><select id="{i}">{v}</select></div>' for i, l, v, st, typ in champs)
        return (f'<section class="section" id="{ident}"><div class="sec-tete"><div><h2>{titre} <em>{mot}</em></h2><p class="gris" style="margin:6px 0 0">{sous}</p></div>{coin_section(r, coin)}</div>'
                + carte(f'<div class="pile"><div class="champs">{ch}</div><div aria-live="polite">{sortie}</div></div>') + f'<p class="source">{note}</p></section>')
    env_opt = '<option value="pea">PEA de plus de 5 ans (18,6 %)</option><option value="cto">Compte-titres (PFU 31,4 %)</option>'
    return (entete('Fais tes calculs', 'LES', 'CALCULATEURS', "Quatre outils simples pour te faire une idée. Ce sont des simulations : aucun rendement n'est garanti.", 'site_calculatrice', r)
            + bloc('composes', 'LES INTÉRÊTS', 'COMPOSÉS', "Ce que devient une épargne placée chaque mois",
                   [('c-init', 'Départ (€)', 1000, 100, 'n'), ('c-mois', 'Chaque mois (€)', 100, 10, 'n'), ('c-taux', 'Rendement par an (%)', 7, .1, 'n'), ('c-ans', 'Durée (ans)', 30, 1, 'n')],
                   '<div class="surtitre">Capital à la fin</div><div class="resultat" id="c-res">–</div><p class="gris" id="c-det" style="margin:4px 0 0"></p>'
                   '<figure class="graph-composes"><div id="c-graph"></div><figcaption class="legende"><span><i style="background:#3FE08A"></i>Ton capital</span>'
                   '<span><i style="background:#35D6FF"></i>Ce que tu as versé</span><span class="gris">Passe la souris (ou le doigt) sur la courbe pour le détail de chaque année.</span></figcaption></figure>',
                   "Calcul mensuel, rendement constant, avant impôts et frais. 7 % par an est une hypothèse, pas une promesse : les actions ont des années de baisse.", 'site_arrosoir')
            + bloc('dividendes', 'VIVRE DE SES', 'DIVIDENDES', "Le capital nécessaire pour un revenu mensuel après impôts",
                   [('d-rev', 'Revenu voulu par mois (€)', 2000, 100, 'n'), ('d-rdt', 'Rendement du dividende (%)', 4, .1, 'n'), ('d-env', 'Enveloppe', env_opt, 0, 's')],
                   '<div class="surtitre">Capital nécessaire</div><div class="resultat" id="d-res">–</div><p class="gris" id="d-det" style="margin:4px 0 0"></p>',
                   "Fiscalité 2026 : prélèvements sociaux de 18,6 % sur un PEA de plus de 5 ans, PFU de 31,4 % sur un compte-titres. Le PEA est plafonné à 150 000 € de versements. "
                   "Le dividende peut baisser ou disparaître.")
            + pea_cto(r) + performances(r)
            + f'<script src="{r}assets/js/calculateurs.js" defer></script>')
def performances(r):
    if not MARCHES: return ''
    per = ''.join(f'<button type="button" class="bouton clair" data-periode="{v}">{t}</button>' for v, t in (('1', '1 an'), ('5', '5 ans'), ('10', '10 ans'), ('20', '20 ans'), ('30', '30 ans'), ('max', 'Max')))
    return (f'<section class="section" id="performances"><div class="sec-tete"><div><h2>LES PERFORMANCES <em>HISTORIQUES</em></h2><p class="gris" style="margin:6px 0 0">'
            "Compare les grandes places boursières et les actions les plus connues : ce qu'est devenue une même somme placée au départ.</p></div>" + coin_section(r, 'site_graphique') + "</div>"
            + carte(f'<div class="pile" id="perf" data-src="{r}assets/data/marches.json"><div class="perf-choix"></div>'
                    f'<div class="pastilles perf-periodes">{per}</div><div class="perf-res"></div>'
                    '<div class="perf-zone"><div class="perf-graph" aria-live="polite">Chargement…</div><div class="perf-bulle" hidden></div></div>'
                    '<p class="gris petit perf-note" style="margin:0"></p></div>')
            + f'<p class="source">Base 100 au début de la période. Cours de clôture hebdomadaires, ajustés des divisions d\'actions, hors dividendes et chacun dans sa devise (dollar, euro, livre, yen…) : '
              f'le change n\'est pas compté. Jusqu\'à 5 courbes à la fois. Données Yahoo Finance, mises à jour chaque nuit (dernier relevé : {jj(MARCHES["dates"][-1])}). '
              'Les performances passées ne préjugent pas des performances futures.</p>'
            + f'<script src="{r}assets/js/perf.js" defer></script></section>')

def pea_cto(r):
    sel = lambda i, lab, opts: f'<div><label for="{i}">{lab}</label><select id="{i}">' + ''.join(f'<option value="{v}"{" selected" if k == 0 else ""}>{t}</option>' for k, (v, t) in enumerate(opts)) + '</select></div>'
    champs = ('<div class="champs">'
              f'<div><label for="p-gain">Montant du gain (€)</label><input id="p-gain" type="number" inputmode="decimal" value="1000" min="0" step="100"></div>'
              + sel('p-nature', 'Type de gain', [('pv', 'Plus-value à la revente'), ('div', 'Dividende')])
              + sel('p-origine', 'Actions', [('eu', 'Européennes (éligibles au PEA)'), ('us', 'Américaines')])
              + sel('p-duree', 'Détention (titres ou plan)', [('8p', 'Plus de 8 ans'), ('5-8', 'De 5 à 8 ans'), ('2-5', 'De 2 à 5 ans'), ('m2', 'Moins de 2 ans')])
              + sel('p-tmi', "Ta tranche d'impôt (TMI)", [('30', '30 %'), ('0', '0 %'), ('11', '11 %'), ('41', '41 %'), ('45', '45 %')])
              + '<div id="p-ligne-2018" class="case"><input id="p-2018" type="checkbox"><label for="p-2018">Titres achetés avant le 1er janvier 2018</label></div>'
              + '</div>')
    sortie = ('<div class="grille" style="--min:260px">'
              '<div class="colonne"><div class="surtitre">PEA</div><div class="resultat" id="p-pea">–</div><p class="net" id="p-pea-net"></p><p class="gris petit" id="p-pea-txt"></p></div>'
              '<div class="colonne"><div class="surtitre">Compte-titres (meilleure option)</div><div class="resultat" id="p-cto" style="color:var(--rouge)">–</div><p class="net" id="p-cto-net"></p>'
              '<div class="choix-impot"><div id="p-ch-pfu"><span>Flat tax (31,4 %)</span><b id="p-cto-pfu">–</b></div><div id="p-ch-bar"><span>Barème + prélèvements sociaux</span><b id="p-cto-bar">–</b></div></div></div>'
              '</div><p class="gris" id="p-det" style="margin:0"></p>')
    note = ("Barème 2026 : prélèvements sociaux de 18,6 % ; flat tax (PFU) de 31,4 % (12,8 % d'impôt et 18,6 % de prélèvements sociaux). "
            "Abattement pour durée de détention (50 % de 2 à 8 ans, 65 % au-delà) réservé aux titres achetés avant 2018, et seulement si tu choisis le barème. "
            "Dividendes américains : retenue de 15 % aux États-Unis, compensée par un crédit d'impôt (simulation simplifiée : il efface au plus l'impôt français). "
            "Le choix du barème vaut pour tous tes revenus de placement de l'année ; la CSG déductible n'est pas comptée. Simulation pédagogique, pas un conseil fiscal. "
            f'Sources : {liens([SP_PFU_, ("impots.gouv.fr, abattement pour durée de détention", "https://www.impots.gouv.fr/particulier/questions/jai-realise-des-plus-values-ai-je-droit-un-abattement-pour-duree-de-detention"), ("service-public.gouv.fr, revenus de placement 2026", "https://www.service-public.gouv.fr/particuliers/vosdroits/F34913"), ("BOFiP, convention France–États-Unis", "https://bofip.impots.gouv.fr/bofip/3042-PGP.html")])}.')
    return (f'<section class="section" id="pea-cto"><div class="sec-tete"><div><h2>PEA OU <em>CTO ?</em></h2><p class="gris" style="margin:6px 0 0">Ce que l\'État prend sur ton gain, selon ton compte, tes actions et depuis quand tu les as</p></div>' + coin_section(r, 'site_tirelire') + '</div>'
            + carte(f'<div class="pile">{champs}<div aria-live="polite" class="pile" style="gap:14px">{sortie}</div></div>') + f'<p class="source">{note}</p></section>')

# ---------- vidéos ----------
POSES_VID = ['salut', 'court', 'etoiles', 'reflechit', 'joie', 'loupe', 'rire', 'pouce', 'montre', 'question']
def logo(n): return f'<svg class="logo-reseau" viewBox="0 0 24 24" aria-hidden="true"><path d="{PICTOS[n]}"/></svg>'
def videos(r):
    cartes = []
    for k, (d, t, ty, tk, ig, vig) in enumerate(VIDEOS):
        visu = (f'<img src="{r}assets/videos/{vig}" alt="" loading="lazy" width="720" height="1280">' if vig else
                f'<div class="sans-vig"><span>{escape(t)}</span><img src="{r}assets/img/{POSES_VID[k % len(POSES_VID)]}.webp" alt="" loading="lazy"></div>')
        data = f' data-titre="{escape(t, quote=True)}"' + (f' data-tiktok="{tk}"' if tk else '') + (f' data-insta="{ig}"' if ig else '')
        bt = ''.join(x for x in (
            f'<button class="bouton lecteur tiktok" type="button" data-plateforme="tiktok">{logo("tiktok")}TikTok</button>' if tk else '',
            f'<button class="bouton lecteur insta" type="button" data-plateforme="insta">{logo("instagram")}Instagram</button>' if ig else ''))
        cartes.append(f'<article class="video" data-type="{"carrousel" if ty == "Carrousel" else "video"}"{data}>'
                      f'<button class="ecran" type="button" aria-label="Regarder : {escape(t, quote=True)}">{visu}<span class="badge{" or" if ty == "Carrousel" else ""}">{ty}</span><span class="lire" aria-hidden="true">▶</span></button>'
                      f'<div class="pile" style="gap:8px;padding:14px 16px 16px"><span class="date">{jj(d)}</span><h3>{escape(t)}</h3><div class="choix-lecteur">{bt}</div></div></article>')
    filtres = ('<div class="pastilles filtres" role="group" aria-label="Filtrer"><button class="bouton clair actif" data-filtre="tout">Tout</button>'
               '<button class="bouton clair" data-filtre="video">Vidéos</button><button class="bouton clair" data-filtre="carrousel">Carrousels</button></div>')
    lecteur = ('<dialog class="lecteur-pop" aria-label="Lecteur vidéo"><div class="lp-tete"><h3 class="lp-titre"></h3>'
               '<button class="v-fermer sombre" type="button" aria-label="Fermer">×</button></div>'
               f'<div class="lp-onglets" role="tablist"><button type="button" role="tab" class="lp-onglet tiktok" data-plateforme="tiktok">{logo("tiktok")}TikTok</button>'
               f'<button type="button" role="tab" class="lp-onglet insta" data-plateforme="insta">{logo("instagram")}Instagram</button></div>'
               '<div class="lp-ecran"></div><p class="lp-pied"><a class="lp-ouvrir" target="_blank" rel="noopener" href="#">Ouvrir dans l\'appli ↗</a></p></dialog>')
    return (entete('TikTok et Instagram', 'NOS', 'VIDÉOS', f"{len(VIDEOS)} vidéos et carrousels depuis le 15/10/2026. Clique sur une vignette pour la regarder ici, sur TikTok ou sur Instagram.", 'site_clap', r)
            + f'<div class="pastilles" style="margin-bottom:14px"><a class="bouton tiktok" href="{SITE["tiktok"]}">{logo("tiktok")}Nous suivre sur TikTok</a><a class="bouton insta" href="{SITE["instagram"]}">{logo("instagram")}Nous suivre sur Instagram</a></div>'
            + filtres + f'<p class="gris petit">Le lecteur TikTok ou Instagram ne se charge que quand tu ouvres une vidéo : ce service peut alors déposer ses propres cookies.</p>'
            + f'<div class="grille videos" style="--min:240px">{"".join(cartes)}</div>{lecteur}<script src="{r}assets/js/videos.js" defer></script>')

# ---------- lettre, mentions (page Produits retirée le 22/11 tant que rien n'est proposé) ----------
def lettre(r):
    return (entete('Chaque dimanche matin', 'LA LETTRE', 'DU DIMANCHE', "Les News de la semaine, la prochaine fiche entreprise et un mot du lexique, en 5 minutes de lecture. Gratuite, sans publicité, désinscription en un clic.", 'site_enveloppe', r)
            + carte('<div class="pile" style="gap:10px"><span class="badge or">En cours de préparation</span><h3>La lettre n\'est pas encore ouverte</h3>'
                    '<p style="margin:0">On y travaille et elle arrive bientôt. En attendant, toutes nos publications sont sur TikTok et Instagram, et les News de chaque vendredi sont sur ce site.</p>'
                    f'<div class="pastilles"><a class="bouton" href="{r}news/">Lire les News</a><a class="bouton clair" href="{SITE["tiktok"]}">TikTok</a><a class="bouton clair" href="{SITE["instagram"]}">Instagram</a></div></div>'))
def mentions(r):
    return ('<div class="pile texte" style="padding:28px 0"><h1>MENTIONS <em>LÉGALES</em></h1>'
            '<h3>Éditeur</h3><p>Nicolas LAUR, Toulouse. Contact : [À COMPLÉTER].</p>'
            '<h3>Hébergement</h3><p>GitHub Pages, GitHub Inc., 88 Colin P Kelly Jr Street, San Francisco, CA 94107, États-Unis.</p>'
            '<h3>Contenu</h3><p>Les contenus d\'Actions Bénéfices sont pédagogiques. Ils ne constituent pas un conseil en investissement ni une recommandation d\'achat ou de vente. '
            'Investir comporte un risque de perte en capital ; les performances passées ne préjugent pas des performances futures. Quand l\'auteur détient un titre présenté, la fiche le précise.</p>'
            '<h3>Données personnelles et cookies</h3><p>Ce site ne dépose aucun cookie et n\'utilise aucun outil de mesure d\'audience. Les polices sont hébergées sur le site. '
            'Sur la page Vidéos, les lecteurs TikTok et Instagram ne se chargent que si tu cliques sur leur bouton : ces services peuvent alors déposer leurs propres cookies, selon leurs règles. '
            'L\'adresse e-mail donnée pour la lettre du dimanche sert uniquement à l\'envoyer ; tu peux te désinscrire à tout moment depuis chaque lettre.</p>'
            '<h3>Marques</h3><p>Les logos d\'entreprises appartiennent à leurs propriétaires et servent uniquement à illustrer les fiches. Mister Coin et le nom Actions Bénéfices appartiennent à l\'éditeur.</p></div>')

# ---------- assemblage ----------
def construire():
    if SORTIE.exists(): shutil.rmtree(SORTIE)
    shutil.copytree(ICI/'assets', SORTIE/'assets')
    shutil.move(SORTIE/'assets'/'favicon.ico', SORTIE/'favicon.ico')  # les navigateurs le cherchent à la racine
    if MARCHES: (SORTIE/'assets'/'data').mkdir(exist_ok=True); shutil.copy(_M, SORTIE/'assets'/'data'/'marches.json')
    page('/', SITE['nom'], "Comprendre la bourse sans jargon avec Mister Coin : fiches entreprises, News de la semaine, lexique et calculateurs. Contenu pédagogique.",
         lambda r: accueil_v2(r, NEWS, FICHES, VIDEOS, LEXIQUE, MARCHES, bandeau, phrase_), sans_lettre=True)
    page('/fiches/', 'Fiches entreprises', "Les comptes des grandes entreprises remis à plat, en euros, sources en lien.", fiches, 'fiches/')
    for vs in ENTREPRISES:
        for m in vs:
            chemin = f'/fiches/{m.META["slug"]}/' + ('' if m is vs[0] else f'{m.META["version"]}/')
            page(chemin, m.META['titre'] + ('' if m is vs[0] else f' (T{m.META["trimestre"]} {m.META["annee"]})'), m.META['description'], page_fiche(vs, m), 'fiches/',
                 image_og=m.META['logo'], **({} if m is vs[0] else dict(noindex=True)))
    page('/news/', 'Les News', "La semaine en bourse en 5 actus, chaque vendredi.", news_liste, 'news/')
    for n in NEWS: page(f'/news/{n["slug"]}/', f'Les News du {n["date_txt"]} : {n["titre"]}', n['chapo'], news_page(n), 'news/', image_og=f'../news/{n["slug"]}/01.webp')
    page('/lexique/', 'Lexique de la bourse', "PEA, CTO, ETF, PFU, PER… les sigles de la bourse expliqués simplement.", lex_liste, 'lexique/')
    for e in LEXIQUE: page(f'/lexique/{e[0]}/', f'{e[1]} : {e[2]}', e[3], lex_page(e), 'lexique/')
    page('/calculateurs/', 'Calculateurs', "Intérêts composés, vivre de ses dividendes, PEA ou CTO : trois simulateurs simples.", calculateurs, 'calculateurs/')
    page('/videos/', 'Nos vidéos', "Toutes les vidéos et carrousels d'Actions Bénéfices sur TikTok et Instagram.", videos, 'videos/')
    page('/lettre/', 'La lettre du dimanche', "Les News, la prochaine fiche et un mot du lexique, chaque dimanche.", lettre)
    page('/mentions-legales/', 'Mentions légales', "Mentions légales du site Actions Bénéfices.", mentions, sans_lettre=True)
    # 404, plan du site, robots
    page('/404/', 'Page introuvable', "Cette page n'existe pas.", lambda r: entete('Erreur 404', 'PAGE', 'INTROUVABLE', f'Retour à <a href="{r}">l\'accueil</a>.', 'site_carte_perdu', r), sans_lettre=True, r=RACINE)
    shutil.move(SORTIE/'404'/'index.html', SORTIE/'404.html'); (SORTIE/'404').rmdir(); PAGES.remove('/404/')
    auj = date.today().isoformat()
    (SORTIE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + ''.join(f'  <url><loc>{SITE["url"]}{p}</loc><lastmod>{auj}</lastmod></url>\n' for p in PAGES) + '</urlset>\n')
    (SORTIE/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n')
    (SORTIE/'.nojekyll').write_text('')
    (SORTIE/'CNAME').write_text(DOMAINE + '\n')
    print(f'{len(PAGES)} pages dans {SORTIE}')

if __name__ == '__main__': construire()
