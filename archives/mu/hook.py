# Micron : 1 000 € le 14 oct. 2021 -> 14 oct. 2026
P0 = 67.68     # cours « il y a 5 ans » (MarketBeat)
FX0 = 1.1602   # EUR/USD BCE 14 oct. 2021
P1 = 914.13    # clôture 14 oct. 2026
FX1 = 1.1195   # EUR/USD BCE 14 oct. 2026
DIVS = [.10, .10]+[.115]*14+[.15, .15]   # ex-dates déc. 2021 -> juil. 2026 (celui du 14 oct. 2026, payé le 29, exclu)
sh = 1000*FX0/P0; val = sh*P1/FX1; div = sh*sum(DIVS)/FX1
print(f"{sh:.3f} actions -> {val:,.0f} € (x{val/1000:.1f}) + dividendes ≈ {div:.0f} € -> total ≈ {val+div:,.0f} €".replace(',', ' '))
hi = sh*1255/1.17; print(f"au plus haut (1 255 $) ≈ {hi:,.0f} € ; plus bas 2022 (49 $) ≈ {sh*49.14/0.98:,.0f} €".replace(',', ' '))
print(f"depuis le plus haut : {P1/1255-1:+.1%}")
