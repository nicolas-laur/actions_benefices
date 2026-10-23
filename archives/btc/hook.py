# Bitcoin : 1 000 € il y a 5 ans (14 oct. 2021 -> 14 oct. 2026) et pizza de 2010
P0=57321.52   # clôture BTC 14 oct. 2021 (StatMuse / CoinMarketCap)
FX0=1.1602    # EUR/USD BCE 14 oct. 2021 (à reconfirmer)
P1=82709      # BTC 14 oct. 2026 (CoinGecko via cryptoticker)
FX1=82709/74239   # change implicite CoinGecko le même jour
btc=1000*FX0/P0; val=btc*P1/FX1
low=btc*15700/1.03; high=btc*126080/1.16
print(f"{btc:.5f} BTC -> {val:.0f} € (x{val/1000:.2f}) | creux nov. 2022 ~{low:.0f} € | sommet oct. 2025 ~{high:.0f} € | vs ATH {P1/126080-1:+.1%}")
print(f"pizza 10 000 BTC = {10000*P1/1e6:.0f} M$ ({10000*P1/FX1/1e6:.0f} M€)")
# plus loin dans le temps (EUR/USD BCE : 14 oct. 2016 1,1002 ; 14 oct. 2013 : 1,3564 (Banca d.Italia))
for y, p, fx in ((2016, 640.38, 1.1002), (2013, 140.52, 1.3564)):
    b = 1000*fx/p; v = b*P1/FX1
    print(f"{y}: {b:.3f} BTC -> {v:,.0f} € (x{v/1000:,.0f})".replace(',', ' '))
