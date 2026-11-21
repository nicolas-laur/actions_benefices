"""Briques HTML du site (thème clair des fiches entreprise) : tuiles à pastilles, barres de pourcentage, encadré de lecture avec Mister Coin,
sections numérotées et graphiques SVG (barres empilées, flux du compte de résultat, barres avec courbe). Chaque fonction renvoie une chaîne HTML.
Les chemins d'images sont relatifs : R (« ../ » répété selon la profondeur de la page) est fourni par build.py."""
from html import escape

INK = '#111418'; GREY = '#5F5F66'; LINE = '#E2DFD8'; NAVY = '#17375E'; GOLD = '#B8860B'
TEAL = '#0B7A5F'; TEAL_R = '#A9CDC3'; LIME = '#6FA823'; LIME_R = '#CFE6B4'; GREEN = '#2E8C38'; GREEN_R = '#B2DBA8'
RED = '#C9161D'; RED_R = '#EAA7A4'; GOLD_R = '#EBD9A6'
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
    img = f'<img src="{R}assets/img/{pose}.png" alt="{alt}" loading="lazy">' if pose else ''
    return f'<div class="lecture">{img}<p>{texte}</p></div>'

def section(num, titre, mot, sous, corps, R='', pose=None, texte=None, source=None, ident=None):
    return (f'<section class="section" id="{ident or f"s{num}"}"><div><div class="surtitre">{num:02d}</div>'
            f'<h2>{titre} <em>{mot}</em></h2><p class="gris" style="margin:6px 0 0">{sous}</p></div>{corps}'
            + (lecture(R, texte, pose) if texte else '') + (f'<p class="source">{source}</p>' if source else '') + '</section>')

def carte(html, style=''):
    return f'<div class="carte" style="{style}">{html}</div>'

# ---------- graphiques ----------
def _t(x, y, s, sz=14, c=INK, w=600, a='middle'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{c}" font-weight="{w}" text-anchor="{a}" style="{F}">{escape(str(s))}</text>'

def barres_empilees(data, aria, groupes=4, premier=2022, conv=1.0, etiq=None):
    """barres empilées (2 séries, bas = data[i][0]) ; groupes de 4 trimestres étiquetés « Ex. AAAA » ; valeurs divisées par conv"""
    W, H = 1000, 400; x0, base, top = 40, 340, 40; n = len(data); st = (W-x0-10)/n; bw = st*.72
    vals = [(a/conv, b/conv) for a, b in data]; k = (base-top)/max(a+b for a, b in vals)
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{escape(aria)}">']
    for g in (25, 50, 75, 100):
        y = base-g*k
        if y > top-10: s += [f'<line x1="{x0}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}"/>', _t(x0-6, y+4, g, 11, GREY, 500, 'end')]
    for i, (a, b) in enumerate(vals):
        x = x0+i*st+(st-bw)/2; ha, hb = a*k, b*k
        s.append(f'<rect x="{x:.1f}" y="{base-ha:.1f}" width="{bw:.1f}" height="{ha:.1f}" rx="3" fill="{TEAL}"/>')
        s.append(f'<rect x="{x:.1f}" y="{base-ha-hb-2:.1f}" width="{bw:.1f}" height="{hb:.1f}" rx="3" fill="{LIME}"/>')
        if (etiq or (lambda i: i % groupes == groupes-1 or i >= n-4))(i): s.append(_t(x+bw/2, base-ha-hb-9, fr(a+b), 11, INK, 700))
        if i % groupes == 0:
            s.append(f'<line x1="{x0+i*st:.1f}" x2="{x0+i*st:.1f}" y1="{base+6}" y2="{base+32}" stroke="{LINE}"/>')
            s.append(_t(x0+(i+min(groupes, n-i)/2)*st, base+24, f'Ex. {premier+i//groupes}', 12, GREY, 500))
    return ''.join(s+['</svg>'])

def flux(nodes, links, vals, k, labels, aria, W=1100, H=600, nw=18):
    """compte de résultat en rubans, mise en page inspirée de App Economy Insights (How They Make Money).
    nodes : {id: (x, y, couleur)} (y = haut du nœud) ; links : (source, cible, valeur, couleur du ruban) dans l'ordre haut → bas ;
    vals : {id: valeur} ; labels : {id: (côté 't'/'b'/'l'/'r', [(texte, 'n' nom | 'v' valeur | 's' grisé), …])}"""
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{escape(aria)}">']
    out = {n: 0 for n in nodes}; inn = {n: 0 for n in nodes}
    for a, b, v, c in links:
        xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]; h = v*k; m = (xa+nw+xb)/2; y0 = ya+out[a]; y1 = yb+inn[b]
        s.append(f'<path d="M{xa+nw},{y0:.1f} C{m},{y0:.1f} {m},{y1:.1f} {xb},{y1:.1f} L{xb},{y1+h:.1f} C{m},{y1+h:.1f} {m},{y0+h:.1f} {xa+nw},{y0+h:.1f} Z" fill="{c}"/>')
        out[a] += h; inn[b] += h
    for n, (x, y, c) in nodes.items(): s.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{max(vals[n]*k, 3):.1f}" fill="{c}"/>')
    for n, (side, lines) in labels.items():
        x, y, c = nodes[n]; h = vals[n]*k; lh = 17; m = len(lines)
        if side == 't': ty, tx, a = y-10-lh*(m-1), x+nw/2, 'middle'
        elif side == 'b': ty, tx, a = y+h+20, x+nw/2, 'middle'
        elif side == 'l': ty, tx, a = y+h/2-lh*(m-1)/2+5, x-10, 'end'
        else: ty, tx, a = y+h/2-lh*(m-1)/2+5, x+nw+10, 'start'
        for j, (txt, kind) in enumerate(lines):
            sz, w, cc = {'n': (15, 700, c), 'v': (17, 800, c), 's': (12, 500, GREY)}[kind]
            s.append(_t(tx, ty+j*lh, txt, sz, cc, w, a))
    return ''.join(s+['</svg>'])

def barres(vals, labels, fmt_, color, aria, courbe=None, H=360, hach=None, ident='h'):
    """barres avec valeur au-dessus (négatifs en rouge sous l'axe), courbe secondaire facultative dans sa propre bande sous les barres,
    hachure sur la barre d'indice hach (période en cours)"""
    W = 1000; x0 = 20; base = H-(110 if courbe else 40); top = 40; n = len(vals); st = (W-2*x0)/n; bw = st*.5
    vmax = max(max(vals), 0); vmin = min(min(vals), 0); k = (base-top)/((vmax-vmin) or 1); y0 = base+vmin*k
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{escape(aria)}">',
         f'<defs><pattern id="{ident}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="{color}"/>'
         f'<line x1="0" y1="0" x2="0" y2="10" stroke="#fff" stroke-width="4" opacity=".45"/></pattern></defs>',
         f'<line x1="{x0}" x2="{W-x0}" y1="{y0:.1f}" y2="{y0:.1f}" stroke="{LINE}" stroke-width="2"/>']
    for i, (v, lb) in enumerate(zip(vals, labels)):
        cx = x0+st*(i+.5); h = abs(v)*k; y = y0-h if v >= 0 else y0
        fill = f'url(#{ident})' if hach == i else (color if v >= 0 else RED)
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h, 2):.1f}" rx="5" fill="{fill}"/>')
        s.append(_t(cx, (y-10) if v >= 0 else (y+h+20), fmt_(v), 16, INK if v >= 0 else RED, 800))
        s.append(_t(cx, base+24, lb, 14, GREY, 500))
    if courbe:
        cb = H-14; ct = base+50; mn, mx = min(courbe), max(courbe); kc = (cb-ct)/((mx-mn) or 1)
        pts = [(x0+st*(i+.5), cb-(c-mn)*kc) for i, c in enumerate(courbe)]
        s.append(f'<polyline fill="none" stroke="{TEAL}" stroke-width="3" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '"/>')
        for (x, y), c in zip(pts, courbe):
            s += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="{TEAL}" stroke-width="3"/>', _t(x+30, y+5, fr(c, 0)+' %', 13, TEAL, 700)]
        s.append(_t(x0, base+48, 'Marge nette', 13, TEAL, 700, 'start'))
    return ''.join(s+['</svg>'])
