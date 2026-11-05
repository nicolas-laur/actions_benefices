"""Découpage de la voix (silences) et calage des phrases du texte, au prorata des caractères dans les plages de parole."""
import numpy as np
from scipy.io import wavfile
SENT = [
 "Combien il te faut pour toucher deux mille euros par mois sans travailler ?",
 "Pour te situer : le SMIC, c'est environ mille quatre cent quatre-vingts euros nets par mois.",
 "Et le salaire médian dans le privé, celui qui coupe les salariés en deux moitiés, est de deux mille cent quatre-vingt-dix euros nets.",
 "Sur un an, deux mille euros par mois, ça fait vingt-quatre mille euros.",
 "Mais même dans un PEA de plus de cinq ans, l'État prélève dix-huit virgule six pour cent de prélèvements sociaux.",
 "Il te faut donc près de trente mille euros de dividendes avant prélèvements.",
 "Combien de capital pour ça ? Tout dépend du rendement : c'est ce qu'une action te verse chaque année, rapporté à son prix.",
 "À trois pour cent, cent euros placés te rapportent trois euros par an.",
 "Un ETF monde ne verse qu'un virgule cinq pour cent : les géants de la tech préfèrent réinvestir leurs bénéfices plutôt que de les distribuer.",
 "Il te faudrait près de deux millions d'euros.",
 "Un ETF à dividendes élevés verse environ trois pour cent : il te faut près d'un million.",
 "Et les actions à gros dividendes ? Crédit Agricole, BNP Paribas, Engie, AXA ou Orange versent entre cinq et sept et demi pour cent.",
 "À cinq pour cent, il te faut environ six cent mille euros.",
 "Mais attention : un dividende peut être coupé du jour au lendemain. Stellantis n'a plus rien versé depuis avril deux mille vingt-cinq.",
 "Autre piège : le PEA est plafonné à cent cinquante mille euros de versements. Au-delà, c'est le compte-titres, taxé à trente et un virgule quatre pour cent.",
 "Il te faudrait alors près d'un million deux cent mille euros à trois pour cent.",
 "La bonne nouvelle : en remplissant ton PEA avec mille euros par mois pendant douze ans et demi, puis en le laissant grossir à sept pour cent par an, ce qui n'est jamais garanti, tu atteins le million en trente-trois ans environ.",
 "Et toi, tu en es où ?"]
def chunks(path='voice_full.wav', th=.012, gap=.30):
    sr, x = wavfile.read(path); x = x.astype(float)/32768; w = int(.02*sr)
    e = np.sqrt(np.convolve(x**2, np.ones(w)/w, 'same'))[::w]; sp = e >= th; out = []; i = 0
    while i < len(sp):
        if sp[i]:
            j = i
            while j < len(sp) and (sp[j] or (j+int(gap/.02) < len(sp) and sp[j:j+int(gap/.02)].any())): j += 1
            out.append((i*.02, j*.02)); i = j
        else: i += 1
    return out
if __name__ == '__main__':
    C = chunks(); print(len(C), 'plages')
    for a, b in C: print(f'{a:6.2f} {b:6.2f} {b-a:5.2f}')
