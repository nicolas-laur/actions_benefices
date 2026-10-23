# Hook « 1 000 € il y a 5 ans » — Netflix (NFLX), aucun dividende
P0=63.38    # cours au 13 oct. 2021, ajusté du split 10:1 (MarketBeat, « il y a 5 ans » au 13 oct. 2026)
FX0=1.1562  # EUR/USD BCE 13 oct. 2021
P1=70.46    # clôture 13 oct. 2026
FX1=1.1188  # EUR/USD BCE 13 oct. 2026
sh=1000*FX0/P0; val=sh*P1/FX1
print(f"actions {sh:.3f} | valeur {val:.0f} € x{val/1000:.2f} | perf $ {P1/P0-1:+.1%} | depuis plus haut 52 sem. {70.46/124.86-1:+.1%}")
