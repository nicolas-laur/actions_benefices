# SpaceX (SPCX) : 1 000 € au plus haut du 16 juin 2026 -> clôture du 15 oct. 2026 ; pas de dividende
IPO = 135.0; OPEN1 = 160.0; ATH = 225.64; LOWJUL = 113.5; LOW = 104.83; P1 = 148.62
FX0 = 1.1594   # EUR/USD BCE 16 juin 2026
FX1 = 1.1195   # EUR/USD BCE 14 oct. 2026 (dernier publié consulté)
v = 1000*FX0/ATH*P1/FX1
print(f"1 000 € au plus haut -> {v:.0f} €  | +{ATH/IPO-1:.0%} IPO->ATH en 4 jours | ATH->fin juillet {LOWJUL/ATH-1:+.0%} | ATH->plus bas {LOW/ATH-1:+.0%}")
print(f"1 000 € à l'ouverture du 12 juin -> {1000*FX0/OPEN1*P1/FX1:.0f} € (change approx.) | P/S ≈ {2020/23.04:.0f}x")
# actionnaires (nombre d'actions publiés après l'IPO, Yahoo Finance / Fool) valorisés au cours du 15 oct. 2026
for n, sh in (("Alphabet (Google)", 551.2), ("Fidelity", 302.6), ("Gigafund", 171.8), ("Fonds souverain saoudien (PIF)", 154.1), ("Nvidia", 122.8)):
    print(f"{n:32s} {sh:6.1f} M actions -> {sh*P1/1000:5.1f} Md$")
print(f"Musk ~42 % de {2020} Md$ -> ~{.42*2020:.0f} Md$ ; Google : 0,9 Md$ investis en 2015 -> x{551.2*P1/1000/0.9:.0f}")
