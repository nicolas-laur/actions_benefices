"""Récupère les cours chez Yahoo Finance (via yfinance) pour le bandeau de l'accueil et le graphique des performances historiques.
Lancé chaque nuit par le workflow .github/workflows/site.yml avant la construction du site ; écrit site/donnees/marches.json.
Cours de clôture ajustés des divisions d'actions mais PAS des dividendes (performances « hors dividendes »), en devise locale.
Le site n'affiche que des variations et des performances calculées (base 100), pas de flux de cours brut."""
import json, math, os, sys, datetime as dt
import pandas as pd
import yfinance as yf

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, '..', 'donnees', 'marches.json')

# id interne : (ticker Yahoo, nom affiché, groupe, devise)
SERIES = {
    'sp500':   ('^GSPC', 'S&P 500', 'Indices', 'USD'),
    'nasdaq':  ('^NDX', 'Nasdaq 100', 'Indices', 'USD'),
    'dow':     ('^DJI', 'Dow Jones', 'Indices', 'USD'),
    'cac40':   ('^FCHI', 'CAC 40', 'Indices', 'EUR'),
    'dax':     ('^GDAXI', 'DAX', 'Indices', 'EUR'),
    'stoxx50': ('^STOXX50E', 'Euro Stoxx 50', 'Indices', 'EUR'),
    'ftse':    ('^FTSE', 'FTSE 100', 'Indices', 'GBP'),
    'nikkei':  ('^N225', 'Nikkei 225', 'Indices', 'JPY'),
    'aapl': ('AAPL', 'Apple', 'Actions américaines', 'USD'),
    'msft': ('MSFT', 'Microsoft', 'Actions américaines', 'USD'),
    'nvda': ('NVDA', 'Nvidia', 'Actions américaines', 'USD'),
    'amzn': ('AMZN', 'Amazon', 'Actions américaines', 'USD'),
    'googl': ('GOOGL', 'Alphabet', 'Actions américaines', 'USD'),
    'meta': ('META', 'Meta', 'Actions américaines', 'USD'),
    'tsla': ('TSLA', 'Tesla', 'Actions américaines', 'USD'),
    'nflx': ('NFLX', 'Netflix', 'Actions américaines', 'USD'),
    'amd':  ('AMD', 'AMD', 'Actions américaines', 'USD'),
    'pltr': ('PLTR', 'Palantir', 'Actions américaines', 'USD'),
    'ko':   ('KO', 'Coca-Cola', 'Actions américaines', 'USD'),
    'ttwo': ('TTWO', 'Take-Two', 'Actions américaines', 'USD'),
    'mc':   ('MC.PA', 'LVMH', 'Actions européennes', 'EUR'),
    'rms':  ('RMS.PA', 'Hermès', 'Actions européennes', 'EUR'),
    'or':   ('OR.PA', "L'Oréal", 'Actions européennes', 'EUR'),
    'tte':  ('TTE.PA', 'TotalEnergies', 'Actions européennes', 'EUR'),
    'air':  ('AIR.PA', 'Airbus', 'Actions européennes', 'EUR'),
    'kering': ('KER.PA', 'Kering', 'Actions européennes', 'EUR'),
    'ubi':  ('UBI.PA', 'Ubisoft', 'Actions européennes', 'EUR'),
    'asml': ('ASML.AS', 'ASML', 'Actions européennes', 'EUR'),
    'novo': ('NOVO-B.CO', 'Novo Nordisk', 'Actions européennes', 'DKK'),
    'gold': ('GC=F', "L'or (once)", 'Autres', 'USD'),
    'btc':  ('BTC-USD', 'Bitcoin', 'Autres', 'USD'),
    'eurusd': ('EURUSD=X', 'Euro / dollar', 'Autres', ''),
}
BANDEAU = ['cac40', 'sp500', 'nasdaq', 'dow', 'dax', 'stoxx50', 'nikkei', 'eurusd', 'gold', 'btc',
           'nvda', 'aapl', 'msft', 'amzn', 'googl', 'meta', 'tsla', 'mc', 'rms', 'tte', 'air', 'asml', 'novo']

def arrondi(x):
    if x is None or (isinstance(x, float) and math.isnan(x)): return None
    return float(f'{x:.5g}')

def main():
    tickers = [v[0] for v in SERIES.values()]
    # historique hebdomadaire depuis 1990 (clôtures du vendredi)
    h = yf.download(tickers, start='1990-01-01', interval='1d', auto_adjust=False, progress=False, threads=True)['Close']
    h.index = pd.to_datetime(h.index).tz_localize(None)
    hebdo = h.resample('W-FRI').last()
    # semaines où la majorité des marchés ont coté (le bitcoin cote aussi le week-end : pas de fausse semaine en cours)
    hebdo = hebdo.loc[hebdo.notna().sum(axis=1) >= hebdo.shape[1] / 2]
    dates = [d.strftime('%Y-%m-%d') for d in hebdo.index]
    series = {}
    for k, (t, nom, grp, dev) in SERIES.items():
        if t not in hebdo: print('absent :', t, file=sys.stderr); continue
        col = hebdo[t].ffill(limit=2)                     # trous ponctuels (jours fériés)
        first = col.first_valid_index()
        if first is None: print('vide :', t, file=sys.stderr); continue
        series[k] = dict(nom=nom, groupe=grp, devise=dev, ticker=t, debut=first.strftime('%Y-%m-%d'),
                         v=[arrondi(x) for x in col.tolist()])
    # bandeau : variation de la dernière séance (clôtures quotidiennes)
    band = []
    for k in BANDEAU:
        t = SERIES[k][0]
        if t not in h: continue
        c = h[t].dropna()
        if len(c) < 2: continue
        band.append(dict(id=k, nom=SERIES[k][1], var=round(100 * (c.iloc[-1] / c.iloc[-2] - 1), 2), date=c.index[-1].strftime('%Y-%m-%d')))
    out = dict(maj=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), source='Yahoo Finance', dates=dates, series=series, bandeau=band)
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(series)} séries, {len(dates)} semaines, bandeau de {len(band)} valeurs, {os.path.getsize(SORTIE)//1024} Ko')

if __name__ == '__main__':
    main()
