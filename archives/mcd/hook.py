# Hook « 1 000 € il y a 5 ans » — McDonald's (MCD)
P0=242.65   # cours au 12 oct. 2021 (MarketBeat, « il y a 5 ans » au 12 oct. 2026)
FX0=1.1555  # EUR/USD BCE 12 oct. 2021
P1=235.65   # clôture 12 oct. 2026
FX1=1.1181  # EUR/USD BCE 12 oct. 2026
divs=[1.38]*4+[1.52]*4+[1.67]*4+[1.77]*4+[1.86]*4   # ex-dates nov. 2021 → sept. 2026
sh=1000*FX0/P0; val=sh*P1/FX1; div=sh*sum(divs)/FX1; tot=val+div
print(f"actions {sh:.3f} | action {val:.0f} € | dividendes {div:.0f} € (Σ {sum(divs):.2f} $) | total {tot:.0f} € x{tot/1000:.2f} | perf $ {P1/P0-1:+.1%}")
