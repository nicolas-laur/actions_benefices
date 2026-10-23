# Hook « 1 000 € il y a 5 ans » — Tesla (TSLA), aucun dividende
P0=270.36   # cours au 12 oct. 2021, ajusté du split 3:1 de 2022 (MarketBeat, « il y a 5 ans » au 12 oct. 2026)
FX0=1.1555  # EUR/USD BCE 12 oct. 2021
P1=378.03   # clôture 12 oct. 2026
FX1=1.1181  # EUR/USD BCE 12 oct. 2026
sh=1000*FX0/P0; val=sh*P1/FX1
print(f"actions {sh:.3f} | valeur {val:.0f} € x{val/1000:.2f} | perf $ {P1/P0-1:+.1%}")
assert 1430<val<1460
