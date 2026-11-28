"""Extrait le contenu des carrousels News (titres, fait, chiffres, lecture, pose, bulle) et les diapos, pour le site."""
import sys, os, re, json, importlib.util
from PIL import Image
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) + ''; EP = f'{REPO}/episodes'
def charge(d):
    sys.argv = ['x']; spec = importlib.util.spec_from_file_location(f'c_{d[:10].replace("-","")}', f'{EP}/{d}/carrousel.py')
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m); return m
def etat(colr):
    return {'3FE08A': 'ok', 'FF4D5E': 'ko'}.get(str(colr).upper().lstrip('#'), 'neutre')
def sources(d):
    sec, out = None, {}
    for l in open(f'{EP}/{d}/sources.md'):
        if l.startswith('## '): sec = l[3:].strip(); out[sec] = []
        elif sec: out[sec] += re.findall(r'https?://[^\s)]+', l)
    return out
def nom_site(u):
    h = re.sub(r'^www\.', '', u.split('/')[2]); return h
res = {}
# --- 27/11, 20/11 et 13/11 : on enregistre les appels à sujet()
for d in ['2026-11-27_les_news', '2026-11-20_les_news', '2026-11-13_les_news']:
    m = charge(d); rec = []
    def sujet(cv, c, i, num, nom, titre, fait, rows, mood, lect, pose, bul, **kw):
        rec.append(dict(sujet=nom.title() if nom.isupper() else nom, titre=titre, fait=fait, lecture=lect, pose=pose, bulle=bul,
                        chiffres=[(r[0], r[1], r[2] or '', etat(r[4])) for r in rows], extra=bool(kw.get('extra'))))
    m.sujet = sujet
    for s in m.SLIDES[1:]:
        if s.__name__ in ('s_cover', 's_fin', 's_ret'): continue
        try: s(None, None)
        except Exception as e: print('!!', d, s.__name__, e)
    res[d] = dict(items=rec, top=getattr(m, 'TOP', None), src=sources(d))
# --- 06/11 : neuf entreprises + Anthropic
m = charge('2026-11-06_les_news'); rec = []
SEC = list(sources('2026-11-06_les_news').keys())
def pub(i):
    t = re.search(r'publié le ([^)]*)', SEC[i]); return t.group(1) if t else ''
FAIT = {k: f"Comptes du trimestre de juillet à septembre 2026, publiés le {pub(i)}. Verdict des chiffres : {m.DATA[k]['res_txt'].lower()} ; réaction de la bourse : {('+' if m.DATA[k]['bourse'] > 0 else '−') + m.fmt(abs(m.DATA[k]['bourse']), 1)} % ({m.DATA[k]['bnote']})."
        for i, k in enumerate(m.KEYS)}
def sg(v, d=1): return ('+' if v > 0 else '−') + m.fmt(abs(v), d) + ' %'
for k in m.KEYS:
    dd = m.DATA[k]
    ch = [("Chiffre d'affaires", m.md(dd['ca']), sg(dd['ca_g'], 0) + ' sur un an', 'ok' if dd['ca_g'] > 0 else 'ko'),
          ('Bénéfice net', m.md(dd['bn']), (sg(dd['bn_g'], 0) + ' sur un an') if dd['bn_g'] is not None else dd.get('bn_sub', ''), 'ok' if (dd['bn_g'] or 1) > 0 else 'ko')]
    for kk in ('k3', 'k4'):
        lab, val, sub, dv, colr = dd[kk]; ch.append((lab.capitalize(), val, ' '.join(x for x in (dv, sub) if x and x not in '↑↓'), etat(colr)))
    ch.append(('La bourse', sg(dd['bourse'], 1), dd['bnote'], {'v': 'ok', 'r': 'ko'}.get(dd['bfeu'], 'neutre')))
    rec.append(dict(sujet=dd['nom'].title().replace("Mcdonald'S", "McDonald's"), titre=f"Résultats {dd['res_txt'].lower()}, bourse {sg(dd['bourse'], 1)}",
                    fait=FAIT[k], lecture=m.LECTURE[k], pose=dd['pose'], bulle=dd['bulle'], chiffres=ch, cle=k))
rec.append(dict(sujet='Anthropic', titre='Bonus : à surveiller', fait="Pas encore en bourse : son entrée au Nasdaq est attendue ce mois-ci.",
                lecture=m.LECTURE['ANTH'], pose='montre', bulle='Prochaine star de la bourse ?',
                chiffres=[("Chiffre d'affaires du trimestre", m.md(m.usd(16.96)), "≈ 17 Md$, +47 % sur le trimestre d'avant", 'ok'),
                          ('Perte nette du trimestre', '−' + m.md(m.usd(23.29)), 'surtout comptable', 'ko'),
                          ("Perte d'exploitation", '−' + m.md(m.usd(0.567)), "contre un bénéfice au trimestre d'avant", 'neutre'),
                          ('Puissance de calcul déjà promise', m.md(m.usd(895.4)), '≈ 895 Md$', 'neutre')]))
res['2026-11-06_les_news'] = dict(items=rec, src=sources('2026-11-06_les_news'))
json.dump(res, open('/tmp/news.json', 'w'), ensure_ascii=False, indent=1)
# --- diapos en webp pour le site
for d in res:
    if not os.path.isdir(f'{EP}/{d}/out'): print(d, 'pas de out/ : diapos déjà publiées conservées'); continue
    o = f'{REPO}/site/assets/news/{d[:10]}'; os.makedirs(o, exist_ok=True)
    pre = 'instagram_' if os.path.exists(f'{EP}/{d}/out/instagram_1.png') else 'tiktok_'   # format unique 4:5 depuis le 26/11
    n = len([f for f in os.listdir(f'{EP}/{d}/out') if f.startswith(pre)])
    for i in range(1, n+1):
        im = Image.open(f'{EP}/{d}/out/{pre}{i}.png').convert('RGB')
        if abs(im.width/im.height - 9/16) > .01:   # 4:5 : centré sur la couleur de fond de la diapo, sans déformation (comme videos.py)
            fond = Image.new('RGB', (720, 1280), im.getpixel((5, 5))); h = round(720*im.height/im.width)
            fond.paste(im.resize((720, h), Image.LANCZOS), (0, (1280-h)//2)); im = fond
        im.resize((720, 1280), Image.LANCZOS).save(f'{o}/{i:02d}.webp', quality=82, method=6)
    print(d, n, 'diapos')
