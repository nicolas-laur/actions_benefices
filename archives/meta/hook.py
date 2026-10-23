"""Meta : 1 000 € placés fin octobre 2021 (le lendemain du changement de nom), le plongeon de 2022, et aujourd'hui."""
P0, D0 = 323.57, '29/10/2021'      # clôture fin oct. 2021 (digrin, prix réel)
PH = 382.18                         # record de clôture 07/09/2021 (≈ 382,05 selon SmartAsset)
PL, DL = 88.91, '03/11/2022'        # plus bas de clôture (SmartAsset / Convextrade)
P1, D1 = 709.33, '16/10/2026'       # clôture (StockAnalysis)
FX0, FXL, FX1 = 1.1645, 0.9753, 1.1208   # EUR/USD BCE 29/10/2021, 03/11/2022, 15/10/2026 (dernier consulté)
n = 1000*FX0/P0
print(f"actions : {n:.3f}")
print(f"au plus bas {DL} : {n*PL/FXL:.0f} € ({PL/P0-1:+.1%} en $)  | depuis le record : {PL/PH-1:+.1%}")
print(f"aujourd'hui {D1} : {n*P1/FX1:.0f} € ({P1/P0-1:+.1%} en $) | x{P1/PL:.1f} depuis le plus bas")
