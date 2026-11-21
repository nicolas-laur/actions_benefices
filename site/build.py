"""Générateur du site actionsbenefices.com. Usage : python3 site/build.py  →  site/_site/ (publié par GitHub Pages).
Toutes les pages sont des dossiers avec index.html ; les liens sont relatifs (variable r)."""
import re, shutil, sys
from datetime import date
from html import escape
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ICI = Path(__file__).resolve().parent
sys.path[:0] = [str(ICI), str(ICI/'contenu')]
from composants import tuile, grille, lecture, carte, fr
import fiche_nvidia
from donnees import NEWS, LEXIQUE, VIDEOS, SP_PEA as SP_PEA_, SP_PFU as SP_PFU_

SITE = dict(nom='Actions_Bénéfices', url='https://actionsbenefices.com',
            menu=[('fiches/', 'Fiches entreprises'), ('news/', 'Les News'), ('lexique/', 'Lexique'), ('calculateurs/', 'Calculateurs'),
                  ('videos/', 'Vidéos'), ('produits/', 'Nos produits')],
            tiktok='https://www.tiktok.com/@actions_bnfices', instagram='https://www.instagram.com/actions_benefices/',
            lettre_action=None)  # adresse du formulaire Brevo une fois le compte ouvert
FICHES = [fiche_nvidia]
SORTIE = ICI/'_site'
env = Environment(loader=FileSystemLoader(ICI/'templates'), autoescape=True)
PAGES = []

# racine absolue, utile seulement pour la page 404 (servie à n'importe quelle adresse)
RACINE = '/'
DOMAINE = 'actionsbenefices.com'
def page(chemin, titre, description, corps, rubrique=None, r=None, **kw):
    """chemin : '/' ou '/a/b/' ; corps : fonction(r) → HTML"""
    prof = chemin.strip('/').count('/') + 1 if chemin != '/' else 0
    r = r if r is not None else '../'*prof
    html = env.get_template('page.html').render(SITE=SITE, titre=titre, description=description, chemin=chemin, r=r,
                                                rubrique=rubrique, corps=corps(r), **kw)
    f = SORTIE/chemin.strip('/')/'index.html'; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(insecables(html))
    PAGES.append(chemin)

def insecables(html):
    """espace insécable entre les milliers (« 50 000 »), dans le texte seulement, jamais dans les attributs ni les coordonnées SVG"""
    return re.sub(r'>[^<]+<', lambda m: re.sub(r'(\d) (?=\d{3}(?!\d))', '\\1\u00a0', m.group(0)), html)
def jj(d): return f'{d[8:]}/{d[5:7]}/{d[:4]}'
def entete(surtitre, h1, mot, chapo, pose=None, r=''):
    img = f'<img src="{r}assets/img/{pose}.png" alt="Mister Coin">' if pose else ''
    return (f'<div class="hero"><div><div class="surtitre">{surtitre}</div><h1>{h1} <em>{mot}</em></h1>'
            f'<p class="chapo">{chapo}</p></div>{img}</div>')
def vignette(r, lien, badge, titre, texte, date_txt='', pose=None, logo=None):
    im = f'<img src="{r}assets/img/{logo}" alt="" style="height:32px;align-self:flex-start;margin:0">' if logo else ''
    pz = f'<img src="{r}assets/img/{pose}.png" alt="">' if pose else ''
    return (f'<a class="vignette" href="{r}{lien}"><span class="badge">{badge}</span>{im}<h3>{titre}</h3>'
            f'<span class="gris">{texte}</span>{f"<span class=date>{date_txt}</span>" if date_txt else ""}{pz}</a>')
def liens(src): return ' · '.join(f'<a href="{u}">{escape(n)}</a>' for n, u in src)

# ---------- accueil ----------
def accueil(r):
    f = FICHES[0].META; n = NEWS[0]
    return (f'<div class="hero"><div><div class="surtitre">La bourse sans jargon</div><h1>COMPRENDRE LA BOURSE <em>AVEC MISTER COIN</em></h1>'
            '<p class="chapo">Des fiches entreprises épurées, les News de la semaine, un lexique et des calculateurs. Chiffres exacts, sources en lien, jamais de conseil.</p>'
            f'<div class="pastilles"><a class="bouton" href="{r}fiches/{f["slug"]}/">Lire la fiche {f["nom"]}</a><a class="bouton or" href="{r}lettre/">La lettre du dimanche</a></div></div>'
            f'<img src="{r}assets/img/salut.png" alt="Mister Coin salue"></div>'
            '<section class="section"><h2>À LA <em>UNE</em></h2>'
            + grille(vignette(r, f'fiches/{f["slug"]}/', 'Fiche entreprise', f['titre'], f['accroche'], 'Chiffres au ' + f['chiffres_au'], logo=f['logo']),
                     vignette(r, f'news/{n["slug"]}/', 'Les News', n['titre'], n['chapo'], n['date_txt'], 'journal'),
                     vignette(r, 'calculateurs/', 'Calculateur', 'Combien pour vivre de tes dividendes ?', 'Le capital nécessaire selon le rendement et ton enveloppe (PEA ou CTO).', pose='reflechit'), mn=300)
            + '</section><section class="section"><h2>LE PETIT <em>LEXIQUE</em></h2><div class="pastilles">'
            + ''.join(f'<a class="bouton" style="background:#E9EEF4;color:var(--marine)" href="{r}lexique/{s}/">{sig}</a>' for s, sig, *_ in LEXIQUE)
            + '</div></section>')

# ---------- fiches ----------
def fiches(r):
    return (entete('Une entreprise, ses chiffres', 'FICHES', 'ENTREPRISES', "Croissance, rentabilité, solidité, dividende et rivaux : les comptes remis à plat, en euros, sources en lien. Aucun verdict, aucun objectif de cours.", 'loupe', r)
            + grille(*[vignette(r, f'fiches/{m.META["slug"]}/', 'Fiche n°' + str(i+1), m.META['titre'], m.META['accroche'], 'Chiffres au ' + m.META['chiffres_au'], logo=m.META['logo'])
                       for i, m in enumerate(FICHES)], mn=320))

# ---------- news ----------
def news_liste(r):
    return (entete('Chaque vendredi', 'LES', 'NEWS', "La semaine en bourse en 5 actus : ce qui s'est passé, et comment la bourse a réagi.", 'journal', r)
            + grille(*[vignette(r, f'news/{n["slug"]}/', 'Semaine du ' + n['date_txt'], n['titre'], n['chapo']) for n in NEWS], mn=320))
def news_page(n):
    def c(r):
        it = ''.join(f'<section class="section" id="n{i}"><div class="surtitre">{i:02d} · {escape(s)}</div><h2>{escape(t)}</h2>'
                     + lecture(r, escape(x), p) + f'<p class="source">Sources : {liens(src)}</p></section>' for i, (s, t, x, p, src) in enumerate(n['items'], 1))
        return (f'<p class="fil"><a href="{r}news/">Les News</a> › {n["date_txt"]}</p>'
                + entete(f'Les News du {n["date_txt"]}', n['titre'].upper(), '', n['chapo'], 'journal', r)
                + f'<p class="gris petit">{n["note"]}</p>' + it)
    return c

# ---------- lexique ----------
def lex_liste(r):
    return (entete('Les sigles de la bourse', 'LE', 'LEXIQUE', "Dix mots pour comprendre ce qu'on raconte, dont un piège.", 'doigt_leve', r)
            + grille(*[f'<a class="vignette" href="{r}lexique/{s}/"><span class="terme">{sig}</span><b>{escape(dev)}</b><span class="gris">{escape(ex)}</span></a>'
                       for s, sig, dev, ex, *_ in LEXIQUE], mn=260))
def lex_page(e):
    s, sig, dev, expl, exemple, src, voir = e
    def c(r):
        v = ''.join(f'<a class="bouton" style="background:#E9EEF4;color:var(--marine)" href="{r}lexique/{x}/">{next(l[1] for l in LEXIQUE if l[0] == x)}</a>' if x != 'interets-composes'
                    else f'<a class="bouton" style="background:#E9EEF4;color:var(--marine)" href="{r}calculateurs/#composes">Intérêts composés</a>' for x in voir)
        return (f'<p class="fil"><a href="{r}lexique/">Lexique</a> › {sig}</p><div class="hero"><div><div class="surtitre">Lexique</div><h1>{sig}</h1>'
                f'<p class="chapo"><b>{escape(dev)}</b></p></div></div><div class="pile texte">'
                + carte(f'<p style="margin:0">{escape(expl)}</p>') + lecture(r, 'Exemple : ' + escape(exemple), 'doigt_leve')
                + (f'<p class="source">Source : {liens(src)}</p>' if src else '')
                + (f'<div><div class="surtitre" style="margin-bottom:10px">Voir aussi</div><div class="pastilles">{v}</div></div>' if v else '') + '</div>')
    return c

# ---------- calculateurs ----------
def calculateurs(r):
    def bloc(ident, titre, mot, sous, champs, sortie, note):
        ch = ''.join(f'<div><label for="{i}">{l}</label><input id="{i}" type="number" inputmode="decimal" value="{v}" min="0" step="{st}"></div>' if typ == 'n'
                     else f'<div><label for="{i}">{l}</label><select id="{i}">{v}</select></div>' for i, l, v, st, typ in champs)
        return (f'<section class="section" id="{ident}"><div><h2>{titre} <em>{mot}</em></h2><p class="gris" style="margin:6px 0 0">{sous}</p></div>'
                + carte(f'<div class="pile"><div class="champs">{ch}</div><div aria-live="polite">{sortie}</div></div>') + f'<p class="source">{note}</p></section>')
    env_opt = '<option value="pea">PEA de plus de 5 ans (18,6 %)</option><option value="cto">Compte-titres (PFU 31,4 %)</option>'
    return (entete('Fais tes calculs', 'LES', 'CALCULATEURS', "Trois outils simples pour te faire une idée. Ce sont des simulations : aucun rendement n'est garanti.", 'reflechit', r)
            + bloc('composes', 'LES INTÉRÊTS', 'COMPOSÉS', "Ce que devient une épargne placée chaque mois",
                   [('c-init', 'Départ (€)', 1000, 100, 'n'), ('c-mois', 'Chaque mois (€)', 100, 10, 'n'), ('c-taux', 'Rendement par an (%)', 7, .1, 'n'), ('c-ans', 'Durée (ans)', 30, 1, 'n')],
                   '<div class="surtitre">Capital à la fin</div><div class="resultat" id="c-res">–</div><p class="gris" id="c-det" style="margin:4px 0 0"></p>',
                   "Calcul mensuel, rendement constant, avant impôts et frais. 7 % par an est une hypothèse, pas une promesse : les actions ont des années de baisse.")
            + bloc('dividendes', 'VIVRE DE SES', 'DIVIDENDES', "Le capital nécessaire pour un revenu mensuel après impôts",
                   [('d-rev', 'Revenu voulu par mois (€)', 2000, 100, 'n'), ('d-rdt', 'Rendement du dividende (%)', 4, .1, 'n'), ('d-env', 'Enveloppe', env_opt, 0, 's')],
                   '<div class="surtitre">Capital nécessaire</div><div class="resultat" id="d-res">–</div><p class="gris" id="d-det" style="margin:4px 0 0"></p>',
                   "Fiscalité 2026 : prélèvements sociaux de 18,6 % sur un PEA de plus de 5 ans, PFU de 31,4 % sur un compte-titres. Le PEA est plafonné à 150 000 € de versements. "
                   "Le dividende peut baisser ou disparaître.")
            + bloc('pea-cto', 'PEA OU', 'CTO ?', "Ce que l'État prend sur une plus-value",
                   [('p-gain', 'Plus-value (€)', 1000, 100, 'n')],
                   '<div class="grille" style="--min:220px"><div><div class="surtitre">PEA de plus de 5 ans</div><div class="resultat" id="p-pea">–</div></div>'
                   '<div><div class="surtitre">Compte-titres</div><div class="resultat" id="p-cto" style="color:var(--rouge)">–</div></div></div><p class="gris" id="p-det" style="margin:4px 0 0"></p>',
                   "Barème 2026 : PEA de plus de 5 ans, 18,6 % de prélèvements sociaux ; compte-titres, PFU de 31,4 % (12,8 % d'impôt et 18,6 % de prélèvements sociaux). "
                   f'Sources : {liens([SP_PEA_, SP_PFU_])}.')
            + f'<script src="{r}assets/js/calculateurs.js" defer></script>')

# ---------- vidéos ----------
def videos(r):
    rows = ''.join(f'<tr><td class="gris" style="white-space:nowrap">{jj(d)}</td><td><b>{escape(t)}</b></td><td><span class="badge{" or" if ty == "Carrousel" else ""}">{ty}</span></td></tr>'
                   for d, t, ty in VIDEOS)
    return (entete('TikTok et Instagram', 'NOS', 'VIDÉOS', f"{len(VIDEOS)} vidéos et carrousels depuis le 17/10/2026. Toutes sont à voir sur nos comptes.", 'rocking', r)
            + f'<div class="pastilles" style="margin-bottom:20px"><a class="bouton" href="{SITE["tiktok"]}">Voir sur TikTok</a><a class="bouton" href="{SITE["instagram"]}">Voir sur Instagram</a></div>'
            + carte(f'<div class="tableau"><table><thead><tr><th scope="col">Date</th><th scope="col">Sujet</th><th scope="col">Format</th></tr></thead><tbody>{rows}</tbody></table></div>'))

# ---------- produits, lettre, mentions ----------
def produits(r):
    p = [('Le guide des premiers pas', "Ouvrir son PEA, choisir un ETF, mettre en place un versement mensuel : le pas à pas, sans jargon.", 'doigt_leve'),
         ('Les fiches entreprises en PDF', "Toutes les fiches, mises à jour à chaque trimestre, à garder et à imprimer.", 'loupe'),
         ('Le tableau de suivi', "Un tableau pour suivre tes versements, tes dividendes et tes frais, mois après mois.", 'reflechit')]
    return (entete('Bientôt', 'NOS', 'PRODUITS', "Des outils pour passer à l'action, en préparation. Abonne-toi à la lettre du dimanche pour être prévenu de leur sortie.", 'applaudit', r)
            + grille(*[carte(f'<div class="pile" style="gap:10px"><span class="badge or">En préparation</span><h3>{t}</h3><p class="gris" style="margin:0">{x}</p>'
                             f'<img src="{r}assets/img/{po}.png" alt="" style="height:110px;width:auto;align-self:flex-end"></div>') for t, x, po in p], mn=280))
def lettre(r):
    return entete('Chaque dimanche matin', 'LA LETTRE', 'DU DIMANCHE', "Les News de la semaine, la prochaine fiche entreprise et un mot du lexique, en 5 minutes de lecture. Gratuit, sans publicité, désinscription en un clic.", 'journal', r)
def mentions(r):
    return ('<div class="pile texte" style="padding:28px 0"><h1>MENTIONS <em>LÉGALES</em></h1>'
            '<h3>Éditeur</h3><p>Nicolas LAUR, Toulouse. Contact : [À COMPLÉTER].</p>'
            '<h3>Hébergement</h3><p>GitHub Pages, GitHub Inc., 88 Colin P Kelly Jr Street, San Francisco, CA 94107, États-Unis.</p>'
            '<h3>Contenu</h3><p>Les contenus d\'Actions_Bénéfices sont pédagogiques. Ils ne constituent pas un conseil en investissement ni une recommandation d\'achat ou de vente. '
            'Investir comporte un risque de perte en capital ; les performances passées ne préjugent pas des performances futures. Quand l\'auteur détient un titre présenté, la fiche le précise.</p>'
            '<h3>Données personnelles et cookies</h3><p>Ce site ne dépose aucun cookie et n\'utilise aucun outil de mesure d\'audience. Les polices sont hébergées sur le site. '
            'L\'adresse e-mail donnée pour la lettre du dimanche sert uniquement à l\'envoyer ; tu peux te désinscrire à tout moment depuis chaque lettre.</p>'
            '<h3>Marques</h3><p>Les logos d\'entreprises appartiennent à leurs propriétaires et servent uniquement à illustrer les fiches. Mister Coin et le nom Actions_Bénéfices appartiennent à l\'éditeur.</p></div>')

# ---------- assemblage ----------
def construire():
    if SORTIE.exists(): shutil.rmtree(SORTIE)
    shutil.copytree(ICI/'assets', SORTIE/'assets')
    page('/', SITE['nom'], "Comprendre la bourse sans jargon avec Mister Coin : fiches entreprises, News de la semaine, lexique et calculateurs. Contenu pédagogique.", accueil)
    page('/fiches/', 'Fiches entreprises', "Les comptes des grandes entreprises remis à plat, en euros, sources en lien.", fiches, 'fiches/')
    for m in FICHES:
        page(f'/fiches/{m.META["slug"]}/', m.META['titre'], m.META['description'], m.corps, 'fiches/', image_og=m.META['logo'])
    page('/news/', 'Les News', "La semaine en bourse en 5 actus, chaque vendredi.", news_liste, 'news/')
    for n in NEWS: page(f'/news/{n["slug"]}/', f'Les News du {n["date_txt"]} : {n["titre"]}', n['chapo'], news_page(n), 'news/', image_og='journal.png')
    page('/lexique/', 'Lexique de la bourse', "PEA, CTO, ETF, PFU, PER… les sigles de la bourse expliqués simplement.", lex_liste, 'lexique/')
    for e in LEXIQUE: page(f'/lexique/{e[0]}/', f'{e[1]} : {e[2]}', e[3], lex_page(e), 'lexique/')
    page('/calculateurs/', 'Calculateurs', "Intérêts composés, vivre de ses dividendes, PEA ou CTO : trois simulateurs simples.", calculateurs, 'calculateurs/')
    page('/videos/', 'Nos vidéos', "Toutes les vidéos et carrousels d'Actions_Bénéfices sur TikTok et Instagram.", videos, 'videos/')
    page('/produits/', 'Nos produits', "Guide des premiers pas, fiches en PDF, tableau de suivi : bientôt disponibles.", produits, 'produits/')
    page('/lettre/', 'La lettre du dimanche', "Les News, la prochaine fiche et un mot du lexique, chaque dimanche.", lettre)
    page('/mentions-legales/', 'Mentions légales', "Mentions légales du site Actions_Bénéfices.", mentions, sans_lettre=True)
    # 404, plan du site, robots
    page('/404/', 'Page introuvable', "Cette page n'existe pas.", lambda r: entete('Erreur 404', 'PAGE', 'INTROUVABLE', f'Retour à <a href="{r}">l\'accueil</a>.', 'reflechit', r), sans_lettre=True, r=RACINE)
    shutil.move(SORTIE/'404'/'index.html', SORTIE/'404.html'); (SORTIE/'404').rmdir(); PAGES.remove('/404/')
    auj = date.today().isoformat()
    (SORTIE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + ''.join(f'  <url><loc>{SITE["url"]}{p}</loc><lastmod>{auj}</lastmod></url>\n' for p in PAGES) + '</urlset>\n')
    (SORTIE/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n')
    (SORTIE/'.nojekyll').write_text('')
    (SORTIE/'CNAME').write_text(DOMAINE + '\n')
    print(f'{len(PAGES)} pages dans {SORTIE}')

if __name__ == '__main__': construire()
