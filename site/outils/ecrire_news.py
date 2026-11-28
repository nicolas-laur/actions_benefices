import json, re, os, sys, pprint
from PIL import Image
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) + '/site/contenu')
from donnees import NEWS as OLD
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) + ''; EP = f'{REPO}/episodes'
r = json.load(open('/tmp/news.json'))
FIX = {'Amd': 'AMD', 'Walmart Et Home Depot': 'Walmart et Home Depot', 'Tech Et Ia': 'Tech et IA', 'Bourse De Paris': 'Bourse de Paris',
       'Inflation Aux États-Unis': 'Inflation aux États-Unis', 'Marchés': 'Wall Street et Paris', 'Droits De Douane': 'Droits de douane'}
def nom(u):
    h = re.sub(r'^www\.', '', u.split('/')[2])
    return {'sec.gov': 'SEC', 'cnbc.com': 'CNBC', 'forbes.com': 'Forbes', 'finance.yahoo.com': 'Yahoo Finance', 'kiplinger.com': 'Kiplinger', 'zonebourse.com': 'Zonebourse', 'tradingsat.com': 'BFM Bourse', 'euronews.com': 'Euronews', 'globenewswire.com': 'GlobeNewswire', 'techcrunch.com': 'TechCrunch', 'stocktitan.net': 'Stock Titan', 'newsroom.amd.com': 'AMD', 'corporate.mcdonalds.com': "McDonald's", 'tradingview.com': 'TradingView', 'ecb.europa.eu': 'BCE', 'nvidianews.nvidia.com': 'Nvidia'}.get(h, h)
def srcs(urls, n=4):
    vu, out = set(), []
    for u in urls:
        u = u.rstrip('.,;')
        if u in vu: continue
        vu.add(u); out.append((nom(u), u))
    return out[:n]
def phrase(s): return s[0].upper() + s[1:].lower() if s.isupper() else s
SEM = {
 '2026-11-27_les_news': dict(slug='2026-11-27', date_txt='27/11/2026', semaine='du 23 au 26 novembre 2026', titre='Le patron de Nvidia est de retour',
                             chapo="Retour de Jensen Huang chez Nvidia, droits de douane sur l'Europe, inflation qui chauffe, Anthropic sous son prix d'entrée : la semaine en 8 news.",
                             note="Chiffres à la clôture du 25/11/2026 pour Wall Street (fermé le 26/11) et du 26/11 pour Paris. Montants convertis au taux BCE du 26/11/2026 (1 € = 1,0975 $). Indices hors dividendes.",
                             sec=[[i] for i in range(8)]),
 '2026-11-20_les_news': dict(slug='2026-11-20', date_txt='20/11/2026', semaine='du 16 au 19 novembre 2026', titre=OLD[0]['titre'], chapo=OLD[0]['chapo'], note=OLD[0]['note'],
                             sec=[[0], [1], [2], [3], [4]]),
 '2026-11-13_les_news': dict(slug='2026-11-13', date_txt='13/11/2026', semaine='du 9 au 13 novembre 2026', titre='Le PDG de Nvidia démissionne',
                             chapo="Démission de Jensen Huang, inflation qui repart, Anthropic en route vers la bourse : la semaine en 6 news.",
                             note="Montants convertis au taux BCE du 12/11/2026 (1 € = 1,1081 $). Indices hors dividendes.", sec=[[0], [1, 5], [2], [3], [4], [6]]),
 '2026-11-06_les_news': dict(slug='2026-11-06', date_txt='06/11/2026', semaine='résultats publiés du 2 au 4 novembre 2026', titre='Résultats contre bourse',
                             chapo="Neuf grandes entreprises ont publié leurs comptes : leurs chiffres face à la réaction de la bourse. De bons chiffres font-ils une action qui monte ?",
                             note="Montants convertis au taux BCE du 04/11/2026 (1 € = 1,1267 $ et 7,4738 couronnes danoises). Résultats du trimestre de juillet à septembre 2026.",
                             sec=[[i] for i in range(10)],
                             bilan="La bourse réagit à la surprise et aux prévisions, pas au chiffre brut. Le paradoxe de la semaine : le chiffre d'affaires de Palantir bondit de 96 % et l'action recule de 1,7 % ; celui de Booking recule de 1 % et l'action prend 9,8 %. Palantir était attendu au sommet et coûte cher ; Booking avait perdu 29 % depuis janvier.")}
PAR = {'Paris tient bon': "Deux familles d'actions. Growth (la croissance) : tech et IA, on paie cher les bénéfices de demain, elles souffrent quand les taux montent. Value (la valeur) : luxe, banques, des bénéfices déjà là et des prix plus sages, elles résistent quand les taux montent."}
NEWS = []
K = 'https://kiplinger.com/investing/stocks/nasdaq-adds-400-points-after-coreweave-earnings-stock-market-today'
poses = set()
for d in ['2026-11-27_les_news', '2026-11-20_les_news', '2026-11-13_les_news', '2026-11-06_les_news']:
    m = SEM[d]; secs = list(r[d]['src'].values()); items = []
    for j, it in enumerate(r[d]['items']):
        urls = sum((secs[k] for k in m['sec'][j]), [])
        lect = it['lecture'] or "Taux en hausse : on quitte la croissance chère pour la valeur. C'est la rotation « growth » → « value »."
        detail = OLD[0]['items'][j][2] if d.startswith('2026-11-20') else PAR.get(phrase(it['titre']), '')
        if d.startswith('2026-11-13') and j in (3, 5): urls = urls + [K]   # Kiplinger du 11/11, cité dans les sources sans lien répété
        src = OLD[0]['items'][j][4] if d.startswith('2026-11-20') else srcs(urls)
        items.append(dict(sujet=FIX.get(it['sujet'], it['sujet']), titre=phrase(it['titre']), fait=it['fait'], detail=detail,
                          chiffres=[tuple(c) for c in it['chiffres']], lecture=lect, pose=it['pose'], bulle=it['bulle'], sources=src))
        poses.add((d, it['pose']))
    n = len(os.listdir(f'{REPO}/site/assets/news/{m["slug"]}'))
    NEWS.append(dict(slug=m['slug'], date=m['slug'], date_txt=m['date_txt'], semaine=m['semaine'], titre=m['titre'], chapo=m['chapo'], note=m['note'],
                     diapos=n, bilan=m.get('bilan', ''), items=items))
with open(f'{REPO}/site/contenu/news.py', 'w') as f:
    f.write('"""Les News du vendredi, générées par /home/claude/outils/ecrire_news.py à partir des carrousels (episodes/<date>_les_news/carrousel.py et sources.md) :\n'
            'mêmes titres, chiffres, phrases de lecture et poses que les diapos. Diapos : assets/news/<slug>/NN.webp. La plus récente en premier."""\n')
    f.write('NEWS = ' + pprint.pformat(NEWS, width=180, sort_dicts=False) + '\n')
# poses de Mister Coin utilisées
dst = f'{REPO}/site/assets/img'
for d, p in sorted(poses) + [('2026-11-20_les_news', 'lit_journal_v2_titre')]:
    out = f'{dst}/{p}.png'
    if os.path.exists(out) and p not in ('lit_journal_v2_titre',): continue
    im = Image.open(f'{EP}/{d}/coin/{p}.png').convert('RGBA'); im = im.crop(im.getbbox()); h = 360
    im.resize((int(im.width*h/im.height), h), Image.LANCZOS).save(out, optimize=True); print('pose', p)
