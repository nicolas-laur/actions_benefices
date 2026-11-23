"""Cours du jour pour les fiches entreprises : le workflow relance site/outils/marches.py chaque nuit (mardi à samedi, après la clôture
de Wall Street), puis le site est reconstruit. Le cours, la capitalisation, le PER et le rendement des fiches sont donc recalculés chaque soir
à partir du dernier cours de clôture ; les comptes (BPA, dividende, nombre d'actions), eux, changent à chaque trimestre (site/outils/MAJ_FICHES.md).
Si les données manquent (Yahoo ou BCE muets), on retombe sur les valeurs figées de la fiche, avec leur date."""
import json, os, datetime as dt
from composants import fr

_F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'donnees', 'marches.json')
try: _D = json.load(open(_F))
except Exception: _D = {}

def jj_mm(iso): return dt.date.fromisoformat(iso).strftime('%d/%m')
def jj_mm_aaaa(iso): return dt.date.fromisoformat(iso).strftime('%d/%m/%Y')

def taux(defaut, date_defaut):
    """(1 € = x $, date ISO) : BCE du dernier jour publié, sinon la valeur figée de la fiche"""
    b = _D.get('bce')
    return (b['usd'], b['date']) if b and b.get('usd') else (defaut, date_defaut)

def cours(ident, defaut, date_defaut, var_defaut=None):
    """dict(c=cours en $, date ISO, var=% de la dernière séance) : dernier cours de clôture, sinon la valeur figée"""
    c = _D.get('cours', {}).get(ident)
    if c and c.get('c') and c.get('date', '') >= date_defaut: return c
    return dict(c=defaut, date=date_defaut, var=var_defaut)

def per(c, bpa12):
    """PER = cours ÷ bénéfice par action des 12 derniers mois publiés ; None si les bénéfices sont nuls ou négatifs"""
    return c / bpa12 if bpa12 > 0 else None

def fr_per(x): return '—' if x is None else fr(x, 0 if x >= 50 else 1)
def fr_var(v): return '' if v is None else f"{'+' if v >= 0 else '−'}{fr(abs(v), 1)} % sur la séance"
