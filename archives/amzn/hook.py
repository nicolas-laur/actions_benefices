# Hook « 1 000 € il y a 5 ans » — Amazon (AMZN), sans dividende
P0=3288.62/20      # clôture 8 oct. 2021, ajustée du split 20:1 (juin 2022)
FX0=1.1569         # EUR/USD BCE, 8 oct. 2021
P1=262.43          # clôture 9 oct. 2026
FX1=1.1177         # EUR/USD, cours du 7 oct. 2026 (Banco de España / BCE)
sh=1000*FX0/P0; val=sh*P1/FX1; div=0.0
print(f"actions {sh:.3f}  valeur {val:.0f} €  x{val/1000:.2f}  perf USD {P1/P0-1:+.1%}  effet change {FX0/FX1-1:+.1%}")
assert 1600<val<1700
