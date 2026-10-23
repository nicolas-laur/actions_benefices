"""Coca-Cola : la mise de Berkshire (Buffett) et les dividendes."""
SH = 400e6; COST = 1.299e9; DIV = 2.12; P1 = 93.90   # actions, coût 1988-1994, dividende annuel 2026 (4 x 0,53 $), clôture 16/10/2026
print(f"dividendes/an : {SH*DIV/1e6:.0f} M$ = {SH*DIV/COST:.0%} de la mise | mise remboursée en {COST/(SH*DIV)*12:.0f} mois")
print(f"valeur de la ligne : {SH*P1/1e9:.1f} Md$ = x{SH*P1/COST:.0f} | par seconde : {SH*DIV/365/86400:.0f} $")
