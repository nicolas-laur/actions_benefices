"""Montant de la phrase « mille euros placés dans Take-Two ce jour-là valent aujourd'hui environ … euros » (règle du projet : taux BCE).
usage : python3 calcul_montant.py <clôture TTWO du 17/11 en $> <taux BCE USD du 17/11>
Take-Two ne verse pas de dividende et n'a pas divisé son action depuis 2013 : le cours suffit."""
import sys
EUR_2013 = 1000.0
BCE_2013 = 1.3356        # taux de référence BCE du 17/09/2013 (USD pour 1 €)
COURS_2013 = 17.70       # ouverture du 17/09/2013, jour de sortie de GTA V (Benzinga)
def montant(cours, bce):
    usd = EUR_2013*BCE_2013; n = usd/COURS_2013; v = n*cours
    return usd, n, v, v/bce
if __name__ == '__main__':
    cours, bce = float(sys.argv[1]), float(sys.argv[2])
    usd, n, v, eur = montant(cours, bce)
    print(f'1 000 € → {usd:,.2f} $ → {n:.3f} actions × {cours:.2f} $ = {v:,.0f} $ → {eur:,.0f} € (taux {bce}) ; × {cours/COURS_2013:.1f} en dollars, × {eur/EUR_2013:.1f} en euros')
