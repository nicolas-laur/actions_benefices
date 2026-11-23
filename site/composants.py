"""Briques HTML du site (thème sombre et or) : tuiles à pastilles, barres de pourcentage, encadré de lecture avec Mister Coin,
sections numérotées et graphiques SVG (barres empilées, flux du compte de résultat, barres avec courbe). Chaque fonction renvoie une chaîne HTML.
Les chemins d'images sont relatifs : R (« ../ » répété selon la profondeur de la page) est fourni par build.py."""
from html import escape

# palette du thème sombre et or (mêmes teintes que les carrousels, lib/carrousel.py) ; *_R : rubans translucides des flux
INK = '#F2F5FA'; GREY = '#9AA6B8'; LINE = 'rgba(255,255,255,.12)'; NAVY = '#35D6FF'; GOLD = '#FFC24A'; NUIT = '#0B0E14'
TEAL = '#35D6FF'; TEAL_R = 'rgba(53,214,255,.30)'; LIME = '#FFC24A'; LIME_R = 'rgba(255,194,74,.30)'; GREEN = '#3FE08A'; GREEN_R = 'rgba(63,224,138,.30)'
RED = '#FF4D5E'; RED_R = 'rgba(255,77,94,.30)'; GOLD_R = 'rgba(255,194,74,.30)'
F = 'font-family:Inter,system-ui,sans-serif'

def fr(v, d=1):
    """nombre à la française : espace fine pour les milliers, virgule décimale"""
    return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')

# ---------- blocs ----------
def tuile(etat, lib, val, ctx=''):
    """tuile d'indicateur : pastille ✓ (ok), ✗ (ko) ou – (neutre), libellé, valeur, contexte"""
    c = {'ok': GREEN, 'ko': RED}.get(etat, '#8A8A90')
    sym = {'ok': '<path d="M7 12.5l3.5 3.5L17 9"/>', 'ko': '<path d="M8 8l8 8M16 8l-8 8"/>'}.get(etat, '<path d="M7 12h10"/>')
    nom = {'ok': 'point fort', 'ko': 'point faible'}.get(etat, 'neutre')
    return (f'<div class="tuile"><svg width="34" height="34" viewBox="0 0 24 24" role="img" aria-label="{nom}"><circle cx="12" cy="12" r="12" fill="{c}" opacity=".14"/>'
            f'<g fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{sym}</g></svg>'
            f'<div><div class="lib">{lib}</div><div><span class="val">{val}</span>{f"<span class=ctx>{ctx}</span>" if ctx else ""}</div></div></div>')

def grille(*items, mn=230):
    return f'<div class="grille" style="--min:{mn}px">' + ''.join(items) + '</div>'

def pbar(lab, p, c):
    return (f'<div class="pbar"><div><span style="font-weight:600">{lab}</span><span style="font-weight:800;color:{c}">{fr(p)} %</span></div>'
            f'<div class="rail"><i style="width:{max(p, 1.2)}%;background:{c}"></i></div></div>')

def lecture(R, texte, pose=None, alt='Mister Coin'):
    img = f'<img src="{R}assets/img/{pose}.webp" alt="{alt}" loading="lazy">' if pose else ''
    return f'<div class="lecture">{img}<p>{texte}</p></div>'

def coin_section(R, coin):
    """Mister Coin illustré (poses « site_* ») à droite du titre d'une section"""
    return f'<img class="sec-coin" data-vitesse="0.06" src="{R}assets/img/{coin}.webp" alt="" loading="lazy">' if coin else ''

def section(num, titre, mot, sous, corps, R='', pose=None, texte=None, source=None, ident=None, coin=None):
    return (f'<section class="section" id="{ident or f"s{num}"}"><div class="sec-tete"><div><div class="surtitre">{num:02d}</div>'
            f'<h2>{titre} <em>{mot}</em></h2><p class="gris" style="margin:6px 0 0">{sous}</p></div>{coin_section(R, coin)}</div>{corps}'
            + (lecture(R, texte, pose) if texte else '') + (f'<p class="source">{source}</p>' if source else '') + '</section>')

def carte(html, style=''):
    return f'<div class="carte" style="{style}">{html}</div>'

# ---------- graphiques ----------
# Interactivité : chaque élément portant data-tip (lignes séparées par « \n », la 1re est le titre) affiche une infobulle
# au survol, au focus clavier ou au toucher (assets/js/infobulles.js) ; le SVG porte la classe « interactif ».
from pictos import PICTOS

def _t(x, y, s, sz=14, c=INK, w=600, a='middle', halo=False):
    h = ' stroke="#0E131D" stroke-width="5" stroke-linejoin="round" paint-order="stroke"' if halo else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{c}" font-weight="{w}" text-anchor="{a}"{h} style="{F}">{escape(str(s))}</text>'

def _tip(texte):
    """attributs d'un élément interactif : infobulle, focus clavier, libellé pour les lecteurs d'écran"""
    t = escape(texte, quote=True)
    return f'data-tip="{t}" tabindex="0" role="img" aria-label="{t.replace(chr(10), " · ")}"'

def _picto(nom, cx, cy, taille, coul):
    k = taille/24
    return f'<path d="{PICTOS[nom]}" fill="{coul}" transform="translate({cx-taille/2:.1f},{cy-taille/2:.1f}) scale({k:.3f})"/>'

def _svg(W, H, aria):
    return f'<svg class="interactif" viewBox="0 0 {W} {H}" width="100%" role="group" aria-label="{escape(aria)}">'

def barres_empilees(data, aria, groupes=4, premier=2022, conv=1.0, etiq=None, tips=None):
    """barres empilées (2 séries, bas = data[i][0]) ; groupes de 4 trimestres étiquetés « Ex. AAAA » ; valeurs divisées par conv ;
    tips : un texte d'infobulle par barre"""
    W, H = 1000, 400; x0, base, top = 40, 340, 40; n = len(data); st = (W-x0-10)/n; bw = st*.72
    vals = [(a/conv, b/conv) for a, b in data]; k = (base-top)/max(a+b for a, b in vals)
    s = [_svg(W, H, aria)]
    for g in (25, 50, 75, 100):
        y = base-g*k
        if y > top-10: s += [f'<line x1="{x0}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}"/>', _t(x0-6, y+4, g, 11, GREY, 500, 'end')]
    for i, (a, b) in enumerate(vals):
        if i % groupes == 0:
            s.append(f'<line x1="{x0+i*st:.1f}" x2="{x0+i*st:.1f}" y1="{base+6}" y2="{base+32}" stroke="{LINE}"/>')
            s.append(_t(x0+(i+min(groupes, n-i)/2)*st, base+24, f'Ex. {premier+i//groupes}', 12, GREY, 500))
    for i, (a, b) in enumerate(vals):
        x = x0+i*st+(st-bw)/2; ha, hb = a*k, b*k
        s.append(f'<g {_tip(tips[i])}>' if tips else '<g>')
        s.append(f'<rect class="zone" x="{x0+i*st:.1f}" y="{top-20}" width="{st:.1f}" height="{base-top+20}"/>')
        s.append(f'<rect x="{x:.1f}" y="{base-ha:.1f}" width="{bw:.1f}" height="{ha:.1f}" rx="3" fill="{TEAL}"/>')
        s.append(f'<rect x="{x:.1f}" y="{base-ha-hb-2:.1f}" width="{bw:.1f}" height="{hb:.1f}" rx="3" fill="{LIME}"/>')
        if (etiq or (lambda i: i % groupes == groupes-1 or i >= n-4))(i): s.append(_t(x+bw/2, base-ha-hb-9, fr(a+b), 11, INK, 700))
        s.append('</g>')
    return ''.join(s+['</svg>'])

def flux(nodes, links, vals, k, labels, aria, W=1100, H=600, nw=18, tips=None, noms=None, pictos=None):
    """compte de résultat en rubans, mise en page inspirée de App Economy Insights (How They Make Money).
    nodes : {id: (x, y, couleur)} (y = haut du nœud) ; links : (source, cible, valeur, couleur du ruban) dans l'ordre haut → bas ;
    vals : {id: valeur} ; labels : {id: (côté 't'/'b'/'l'/'r', [(texte, 'n' nom | 'v' valeur | 's' grisé), …])} ;
    tips : {id: infobulle du nœud} ; noms : {id: nom court} pour les infobulles des rubans ;
    pictos : {id: [noms de pictogrammes]}, posés au-dessus de l'étiquette (en dessous pour le côté 'b')"""
    s = [_svg(W, H, aria)]
    out = {n: 0 for n in nodes}; inn = {n: 0 for n in nodes}
    for a, b, v, c in links:
        xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]; h = v*k; m = (xa+nw+xb)/2; y0 = ya+out[a]; y1 = yb+inn[b]
        t = f' {_tip(f"{noms[a]} → {noms[b]}" + chr(10) + f"{fr(v)} Md€" + chr(10) + f"soit {fr(100*v/vals[a], 0)} % de « {noms[a]} »")}' if noms else ''
        s.append(f'<path{t} d="M{xa+nw},{y0:.1f} C{m},{y0:.1f} {m},{y1:.1f} {xb},{y1:.1f} L{xb},{y1+h:.1f} C{m},{y1+h:.1f} {m},{y0+h:.1f} {xa+nw},{y0+h:.1f} Z" fill="{c}"/>')
        out[a] += h; inn[b] += h
    for n, (x, y, c) in nodes.items():
        side, lines = labels.get(n, ('r', []))
        h = vals[n]*k; lh = 17; m = len(lines)
        if side == 't': ty, tx, a = y-10-lh*(m-1), x+nw/2, 'middle'
        elif side == 'b': ty, tx, a = y+h+20, x+nw/2, 'middle'
        elif side == 'l': ty, tx, a = y+h/2-lh*(m-1)/2+5, x-10, 'end'
        else: ty, tx, a = y+h/2-lh*(m-1)/2+5, x+nw+10, 'start'
        g = [f'<g {_tip(tips[n])}>' if tips and n in tips else '<g>',
             f'<rect class="zone" x="{x-6}" y="{y-6}" width="{nw+12}" height="{max(h, 3)+12:.1f}"/>',
             f'<rect x="{x}" y="{y}" width="{nw}" height="{max(h, 3):.1f}" fill="{c}"/>']
        for j, (txt, kind) in enumerate(lines):
            sz, w, cc = {'n': (15, 700, c), 'v': (17, 800, c), 's': (12, 500, GREY)}[kind]
            g.append(_t(tx, ty+j*lh, txt, sz, cc, w, a))
        if pictos and n in pictos:
            noms_p = pictos[n]; ps = 26; pas = 30; larg = pas*(len(noms_p)-1)
            py = ty+(m-1)*lh+12+ps/2 if side == 'b' else ty-17-ps/2
            px0 = {'middle': tx-larg/2, 'end': tx-ps/2-larg, 'start': tx+ps/2}[a]
            g += [_picto(p, px0+j*pas, py, ps, c) for j, p in enumerate(noms_p)]
        s.append(''.join(g) + '</g>')
    return ''.join(s+['</svg>'])

def barres(vals, labels, fmt_, color, aria, courbe=None, H=360, hach=None, ident='h', tips=None, nom_courbe='Marge nette'):
    """barres avec valeur au-dessus (négatifs en rouge sous l'axe), courbe secondaire facultative dans sa propre bande sous les barres,
    hachure sur la barre d'indice hach (période en cours) ; tips : un texte d'infobulle par barre (colonne entière, courbe comprise)"""
    W = 1000; x0 = 20; base = H-(110 if courbe else 40); top = 40; n = len(vals); st = (W-2*x0)/n; bw = st*.5
    vmax = max(max(vals), 0); vmin = min(min(vals), 0); k = (base-top)/((vmax-vmin) or 1); y0 = base+vmin*k
    s = [_svg(W, H, aria),
         f'<defs><pattern id="{ident}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="{color}"/>'
         f'<line x1="0" y1="0" x2="0" y2="10" stroke="#0B0E14" stroke-width="4" opacity=".45"/></pattern></defs>',
         f'<line x1="{x0}" x2="{W-x0}" y1="{y0:.1f}" y2="{y0:.1f}" stroke="{LINE}" stroke-width="2"/>']
    pts = []
    if courbe:
        cb = H-22; ct = base+56; mn, mx = min(courbe), max(courbe); kc = (cb-ct)/((mx-mn) or 1)
        pts = [(x0+st*(i+.5), cb-(c-mn)*kc) for i, c in enumerate(courbe)]
        s.append(f'<polyline fill="none" stroke="{TEAL}" stroke-width="3" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '"/>')
        s.append(_t(x0, base+44, nom_courbe, 13, TEAL, 700, 'start'))
    for i, (v, lb) in enumerate(zip(vals, labels)):
        cx = x0+st*(i+.5); h = abs(v)*k; y = y0-h if v >= 0 else y0
        fill = f'url(#{ident})' if hach == i else (color if v >= 0 else RED)
        g = [f'<g {_tip(tips[i])}>' if tips else '<g>', f'<rect class="zone" x="{x0+st*i:.1f}" y="{top-30}" width="{st:.1f}" height="{H-top+30-4}"/>',
             f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h, 2):.1f}" rx="5" fill="{fill}"/>',
             _t(cx, (y-10) if v >= 0 else (y+h+20), fmt_(v), 16, INK if v >= 0 else RED, 800), _t(cx, base+24, lb, 14, GREY, 500)]
        if courbe:
            (px, py), c = pts[i], courbe[i]
            # valeur au-dessus du point, avec un halo blanc : elle ne se mêle plus à la courbe
            g += [f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#0E131D" stroke="{TEAL}" stroke-width="3"/>', _t(px, py-13, fr(c, 0)+' %', 13, TEAL, 700, halo=True)]
        s.append(''.join(g) + '</g>')
    return ''.join(s+['</svg>'])
