# Krachs, ép. 1 : 2008 — sources et calculs

## Chiffres de la vidéo
- Clôture du 12/09/2008 (vendredi avant la faillite) : CAC 40 4 332,66 pts ; S&P 500 1 251,70 pts.
- Creux du 09/03/2009 : CAC 40 2 519,29 (−41,9 %) ; S&P 500 676,53 (−46,0 %).
- Retour au niveau du 12/09/2008 (indices de prix, hors dividendes) : S&P 500 le 21/12/2010 (2 ans et 3 mois) ; CAC 40 le 14/02/2014 (5 ans et 5 mois), avec un dernier passage sous ce niveau le 15/01/2015.
- Clôtures du 15/10/2026 : CAC 40 7 934,70 ; S&P 500 7 744,06.
- 1 000 € au 12/09/2008 → aujourd'hui : CAC 40 = 1 000 × 7 934,70 / 4 332,66 = 1 831 € ; S&P 500 en euros = 1 000 × 1,4066 / 1 251,70 × 7 744,06 / 1,1208 = 7 764 € (rapport 4,24).
- Hors dividendes réinvestis : avec dividendes, les deux montants seraient plus élevés et l'écart resterait du même ordre.

## Sources
- Séries quotidiennes CAC 40 et S&P 500 (Yahoo Finance, jusqu'au 31/12/2015) : paquet R smqf, miroir CRAN — https://github.com/cran/smqf
- Clôture du CAC 40 le 12/09/2008 (4 332 pts) : BFM Bourse / Tradingsat — https://www.tradingsat.com/cac-40-FR0003500008/conseils/cac-40-lehman-brothers-en-faillite-187337.html
- Clôture du CAC 40 le 15/10/2026 : BFM Bourse — https://www.tradingsat.com/cac-40-FR0003500008/actualites/cac-40-malgre-le-repli-des-valeurs-liees-a-l-ia-l-oreal-et-hermes-soutiennent-le-cac-40-qui-gagne-pres-de-08-1171850.html
- Clôture du S&P 500 le 15/10/2026 : TheStreet — https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-15-2026
- EUR/USD de référence BCE le 12/09/2008 (1,4066) : https://www.poundsterlinglive.com/bank-of-england-spot/historical-spot-exchange-rates/eur/EUR-to-USD-2008
- EUR/USD de référence BCE le 15/10/2026 (1,1208), publié par la Banca d'Italia : https://www.bancaditalia.it/compiti/operazioni-cambi/cambio/cambi_rif_20261015
- Lehman Brothers, 4e banque d'affaires américaine à sa faillite : HISTORY — https://www.history.com/this-day-in-history/september-15/lehman-brothers-collapses
- Faillite du 15/09/2008 : Bloomberg — https://www.bloomberg.com/news/articles/2008-09-15/lehman-files-for-biggest-bankruptcy-in-u-s-after-suitors-balk

## Calculs
Fichiers joints : hook.py (calcul), load.py (extraction des séries), cac.csv, spx.csv, path.csv (courbes de la vidéo, base 1 000 €).
