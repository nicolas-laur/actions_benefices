# Hook « 1 000 € il y a 5 ans » — Visa (V)
P0=225.11   # clôture ~8 oct. 2021 (MarketBeat : « 225,11 $ il y a cinq ans »)
FX0=1.1569  # EUR/USD BCE 8 oct. 2021
P1=385.45   # clôture 9 oct. 2026
FX1=1.1177  # EUR/USD 7 oct. 2026
divs=[.375]*4+[.45]*4+[.52]*4+[.59]*4+[.67]*4   # ex-dates nov. 2021 → août 2026
sh=1000*FX0/P0; val=sh*P1/FX1; div=sh*sum(divs)/FX1; tot=val+div
print(f"actions {sh:.3f} | valeur {val:.0f} € | dividendes bruts {div:.0f} € (Σ {sum(divs):.2f} $) | total {tot:.0f} € x{tot/1000:.2f} | perf $ {P1/P0-1:+.1%}")
assert 1800<tot<1850
