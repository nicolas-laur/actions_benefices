# Hook « 1 000 € il y a 5 ans » — Alphabet (GOOGL)
P0=136.45   # cours d'il y a 5 ans, ajusté du split 20:1 de 2022 (MarketBeat)
FX0=1.1569  # EUR/USD BCE 8 oct. 2021
P1=351.66   # clôture 9 oct. 2026
FX1=1.1177  # EUR/USD 7 oct. 2026
divs=[.20]*4+[.21]*4+[.22]*2   # ex-dates juin 2024 → sept. 2026
sh=1000*FX0/P0; val=sh*P1/FX1; div=sh*sum(divs)/FX1; tot=val+div
print(f"actions {sh:.3f} | valeur {val:.0f} € | dividendes {div:.0f} € | total {tot:.0f} € x{tot/1000:.2f} | perf $ {P1/P0-1:+.1%}")
assert 2650<tot<2700
