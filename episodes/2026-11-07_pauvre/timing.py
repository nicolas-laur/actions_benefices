"""Découpage de la voix (silences) et calage des phrases du texte, au prorata des caractères dans les plages de parole."""
import numpy as np
from scipy.io import wavfile
SENT = [
 'Pourquoi tu restes pauvre ?',
 "Spoiler : ce n'est pas qu'une question de salaire.",
 'En France, un Français sur quatre est à découvert presque tous les mois.',
 'En moyenne, dès le dix-huit.',
 'Erreur numéro un : tu épargnes ce qui reste à la fin du mois.',
 "Sauf qu'il ne reste jamais rien.",
 "Les riches font l'inverse : ils se paient en premier.",
 'Un virement automatique le jour de la paie, et tu vis avec le reste.',
 'Erreur numéro deux : ton loyer.',
 "Le repère, c'est un tiers de ton salaire maximum.",
 'Avec deux mille euros nets, ça fait six cent soixante-sept euros.',
 'Au-delà, chaque mois commence déjà dans le rouge.',
 'Erreur numéro trois : les petites dépenses.',
 "Les Français paient en moyenne soixante-douze euros par mois d'abonnements loisirs.",
 'Placés à sept pour cent pendant trente ans, ça fait près de quatre-vingt-huit mille euros.',
 "La règle simple, c'est cinquante, trente, vingt.",
 "Cinquante pour cent pour l'essentiel, trente pour tes envies, vingt pour ton avenir.",
 'Sur deux mille euros, ça fait quatre cents euros par mois.',
 'En trente ans, près de quatre cent quatre-vingt-dix mille euros.',
 "Et si ton salaire ne couvre même pas l'essentiel, le problème ne vient pas de toi.",
 'Commence par dix euros.',
 "Ce qui compte, c'est l'habitude.",
 'Et toi, tu te paies en premier ?']
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
