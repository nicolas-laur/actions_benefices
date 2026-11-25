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
    vmax = max(a+b for a, b in vals); pas = 25 if vmax <= 125 else 50 if vmax <= 250 else 100   # graduations adaptées à l'échelle
    for g in range(pas, int(vmax)+pas, pas):
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
    s.append('</svg>')
    return _double(''.join(s), _hb_empilees(vals, groupes, premier, tips))

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
    s.append('</svg>')
    return _double(''.join(s), _flux_mobile(''.join(s), nodes, links, vals, labels, tips, noms), mobile_seul=False)

def barres(vals, labels, fmt_, color, aria, courbe=None, H=360, hach=None, ident='h', tips=None, nom_courbe='Marge nette', nom_barres='Résultat net (Md€)'):
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
    s.append('</svg>')
    return _double(''.join(s), _hb_simples(vals, labels, fmt_, color, courbe, hach, tips, nom_courbe, nom_barres))


# ---------------------------------------------------------------------------------------------------------------------------
# Versions téléphone des graphiques (chantier mobile du 25/11) : sous 760 px de large, chaque graphique SVG est remplacé par une
# version en barres horizontales, lisible sans défilement (valeur au bout de chaque barre, détail au toucher via data-tip).
# Sur ordinateur, rien ne change : la version SVG reste affichée (classes g-bureau / g-mobile, assets/css/mobile.css).

def _double(svg, mobile, mobile_seul=True):
    return f'<div class="g-bureau">{svg}</div><div class="g-mobile">{mobile}</div>'

def _ligne(etiq, largeur, segments, valeur, tip, coul_val=None, cache=False, extra='', classe=''):
    """une barre horizontale : étiquette, segments [(part en %, couleur, motif)], valeur au bout"""
    segs = ''.join(f'<i style="width:{p:.2f}%;background:{c}"{" class=hach" if h else ""}></i>' for p, c, h in segments)
    st = f' style="color:{coul_val}"' if coul_val else ''
    return (f'<div class="hb-l{" " + classe if classe else ""}"{" hidden" if cache else ""} {_tip(tip) if tip else ""}>'
            f'<span class="hb-q">{escape(etiq)}</span><span class="hb-piste"><span class="hb-b" style="width:{max(largeur, .8):.2f}%">{segs}</span></span>'
            f'<b class="hb-v"{st}>{valeur}</b>{extra}</div>')

def _plus(n, nom):
    return f'<button class="hb-plus" type="button" aria-expanded="false"><span class="ouvrir">Voir les {n} {nom}</span><span class="fermer">Voir moins</span></button>'

def _hb_empilees(vals, groupes, premier, tips, visibles=8):
    """barres empilées → barres horizontales ; trimestres regroupés par exercice ; les « visibles » dernières affichées, le reste au bouton"""
    n = len(vals); vmax = max(a+b for a, b in vals); h = ['<div class="hb">']
    # au moins « visibles » − 3 barres, en commençant au début d'un exercice (pas de trimestre isolé sous son titre)
    debut = 0 if n <= visibles else (((n-visibles)//groupes + 1)*groupes if groupes > 1 else n-visibles)
    for i, (a, b) in enumerate(vals):
        cache = i < debut; tot = a+b
        if groupes > 1 and (i % groupes == 0 or i == debut):
            h.append(f'<p class="hb-an"{" hidden" if cache else ""}>Exercice {premier+i//groupes}</p>')
        etiq = f'T{i % groupes + 1}' if groupes > 1 else str(premier+i)
        h.append(_ligne(etiq, 100*tot/vmax, [(100*a/tot, TEAL, False), (100*b/tot, LIME, False)], fr(tot), tips[i] if tips else None, cache=cache))
    if debut: h.append(_plus(n, 'trimestres' if groupes > 1 else 'années'))
    return ''.join(h+['</div>'])

def _hb_simples(vals, labels, fmt_, color, courbe, hach, tips, nom_courbe, nom_barres):
    """barres (et courbe éventuelle) → une ligne par période : barre, valeur, puis la valeur de la courbe en pastille"""
    vmax = max(abs(v) for v in vals) or 1; h = ['<div class="hb">']
    if courbe: h.append(f'<p class="hb-leg"><span><i style="background:{color}"></i>{escape(nom_barres)}</span><span class="hb-c">{escape(nom_courbe)}</span></p>')
    for i, (v, lb) in enumerate(zip(vals, labels)):
        c = color if v >= 0 else RED
        extra = f'<span class="hb-c">{fr(courbe[i], 0)} %</span>' if courbe else ''
        h.append(_ligne(lb, 100*abs(v)/vmax, [(100, c, hach == i)], fmt_(v), tips[i] if tips else None, None if v >= 0 else RED, extra=extra,
                        classe='avec-c' if courbe else ''))
    return ''.join(h+['</div>'])

def _flux_mobile(svg, nodes, links, vals, labels, tips, noms):
    """flux → aperçu du graphique entier (un appui l'ouvre en grand) + deux barres empilées : d'où vient l'argent, où il va"""
    entrees = {b for a, b, v, c in links}; sorties = {a for a, b, v, c in links}
    nom = lambda n: (noms or {}).get(n) or labels.get(n, ('', [(n, 'n')]))[1][0][0]
    ca = next((n for n in nodes if labels.get(n, ('', [('', '')]))[1][0][0].lower().startswith("chiffre d")), None)
    import re
    svg = re.sub(r' data-tip="[^"]*" tabindex="0" role="img" aria-label="[^"]*"', '', svg)   # l'aperçu n'est qu'une vignette : le détail est dans la vue en grand
    if ca is None: return f'<button class="flux-apercu" type="button">{svg}</button>'
    xca = nodes[ca][0]; total = vals[ca]
    src = [n for n in nodes if n not in entrees and nodes[n][0] < xca]
    puits = [n for n in nodes if n not in sorties and nodes[n][0] > xca]
    rn = next((p for p in puits if 'sultat net' in nom(p)), None)
    puits.sort(key=lambda n: (n == rn, -nodes[n][1]))   # les charges du plus gros au plus petit, le résultat net en dernier
    def pile(titre, ids):
        segs = ''.join(f'<i style="width:{100*vals[n]/sum(vals[x] for x in ids):.2f}%;background:{nodes[n][2]}" {_tip(tips[n]) if tips and n in tips else ""}></i>' for n in ids)
        lig = ''.join(f'<li {_tip(tips[n]) if tips and n in tips else ""}><i style="background:{nodes[n][2]}"></i><span>{escape(nom(n))}</span>'
                      f'<b>{fr(vals[n])}</b><em>{fr(100*vals[n]/total, 0)} %</em></li>' for n in ids)
        return f'<div class="pile-act"><p class="hb-titre">{titre}</p><div class="pile-barre">{segs}</div><ul>{lig}</ul></div>'
    return (f'<button class="flux-apercu" type="button" aria-label="Afficher le graphique en grand">{svg}<span class="flux-ouvrir">Toucher pour l\'afficher en entier</span></button>'
            + pile(f"D'où viennent les {fr(total)} Md€ de ventes", src)
            + pile("Où va chaque euro de ventes", puits)
            + '<p class="hb-note">Pourcentages du chiffre d\'affaires.</p>')
