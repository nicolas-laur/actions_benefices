"""Intel : du plus bas depuis 2009 au record, puis la rechute."""
P0 = 49.00          # clôture fin oct. 2021 (digrin, prix réel)
PL = 18.13          # plus bas de clôture depuis juillet 2009 (Seeking Alpha, mardi 8 avril 2025)
PH = 142.35         # plus haut sur 52 semaines (juin 2026)
P1 = 89.85          # clôture du 16/10/2026 (StockAnalysis)
FX0, FX1 = 1.1645, 1.1208
n = 1000*FX0/P0
print(f"actions : {n:.3f} | aujourd'hui : {n*P1/FX1:.0f} € | depuis oct. 2021 au plus bas : {PL/P0-1:+.1%}")
print(f"plus bas -> record : x{PH/PL:.2f} | record -> aujourd'hui : {P1/PH-1:+.1%} | plus bas -> aujourd'hui : x{P1/PL:.2f}")
