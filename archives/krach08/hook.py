"""Krachs ép. 1 : 2008. 1 000 € placés la veille de Lehman (vendredi 12 sept. 2008), CAC 40 vs S&P 500, indices de prix (hors dividendes)."""
import pandas as pd
CAC0, SPX0 = 4332.66, 1251.70        # clôtures 12/09/2008 (Yahoo via smqf ; tradingsat confirme 4 332)
CAC1, SPX1 = 7934.70, 7744.06        # clôtures 15/10/2026 (BFM Bourse, TheStreet)
FX0, FX1 = 1.4066, 1.1208            # EUR/USD BCE 12/09/2008 et 15/10/2026
for n, a in (('cac', CAC0), ('spx', SPX0)):
    s = pd.read_csv(f'{n}.csv', index_col=0, parse_dates=True)['close']; post = s['2008-09-12':]
    lo = post[:'2010'].idxmin(); rec = post[(post.index > lo) & (post >= a)].index[0]
    yrs = (rec - pd.Timestamp('2008-09-12')).days/365.25
    print(f"{n}: creux {lo.date()} {post[lo]:.0f} ({post[lo]/a-1:+.1%}) -> 1 000 € = {1000*post[lo]/a:.0f} € | retour {rec.date()} ({yrs:.1f} ans) | dernier passage sous le niveau {post[post<a].index[-1].date()}")
print(f"CAC aujourd'hui : 1 000 € -> {1000*CAC1/CAC0:.0f} €")
print(f"S&P en euros aujourd'hui : 1 000 € -> {1000*FX0/SPX0*SPX1/FX1:.0f} € (en dollars : x{SPX1/SPX0:.2f})")
