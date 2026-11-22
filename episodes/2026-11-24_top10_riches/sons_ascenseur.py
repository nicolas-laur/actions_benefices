"""Sons d'ascenseur originaux (synthèse) pour top10_riches : ding d'arrivée, grille en accordéon, moteur et câbles, arrêt.
python3 sons_ascenseur.py  ->  essai_ascenseur.wav (démo enchaînée) ; les fonctions sont importées par mix.py."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; rng = np.random.default_rng(24)
def tt(n): return np.arange(n)/SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def add(b, x, t0, g=1.0):
    i = int(round(t0*SR)); j = min(len(b), i+len(x)); b[i:j] += g*x[:j-i]

def ding(f=1046.5, g=.16, d=2.6):
    """Ding d'arrivée : timbre de carillon frappé (partiels de cloche tubulaire), attaque nette, longue résonance."""
    n = int(d*SR); t = tt(n)
    parts = ((1.0, 1.0, 1.6), (2.0, .42, 2.4), (2.76, .30, 3.6), (4.07, .16, 5.5), (5.40, .08, 8.0))
    x = sum(a*np.sin(2*np.pi*f*r*t+.3*r)*np.exp(-t*k) for r, a, k in parts)
    x *= 1+.04*np.sin(2*np.pi*5.2*t)*np.exp(-t*1.2)            # léger battement de la cloche
    clic = bp(rng.standard_normal(n), 2500, 7000)*np.exp(-t*900)*.25   # petit marteau
    return (x*np.minimum(1, t/.0015)+clic)*g

def grille(d=.9, g=.22):
    """Grille en accordéon qui se ferme : cliquetis métalliques rapides qui se resserrent, puis claquement."""
    s = np.zeros(int((d+.5)*SR)); tk = 0; k = 0
    while tk < d:
        n = int(.05*SR); t = tt(n); f = 2600+900*rng.random()
        x = bp(rng.standard_normal(n), f*.7, f*1.3)*np.exp(-t*160)*.5+np.sin(2*np.pi*f*.5*t)*np.exp(-t*70)*.15
        add(s, x*(.5+.5*rng.random()), tk); k += 1; tk += .055*(1-.55*tk/d)
    n = int(.4*SR); t = tt(n)
    add(s, (bp(rng.standard_normal(n), 900, 4000)*np.exp(-t*40)*.8+np.sin(2*np.pi*190*t)*np.exp(-t*18)*.4), d)
    return s*g

def moteur(d=3.0, g=.06):
    """Montée : ronronnement grave du moteur qui monte doucement, chuintement des câbles, fondu d'entrée et de sortie."""
    n = int(d*SR); t = tt(n)
    f = 58+10*np.minimum(1, t/1.2)
    hum = np.sin(2*np.pi*np.cumsum(f)/SR)+.5*np.sin(2*np.pi*np.cumsum(2*f)/SR)+.2*np.sin(2*np.pi*np.cumsum(3*f)/SR)
    whine = np.sin(2*np.pi*np.cumsum(420+120*np.minimum(1, t/1.5))/SR)*.06
    cable = lp(hp(rng.standard_normal(n), 300), 1400)*.25*(1+.3*np.sin(2*np.pi*1.7*t))
    env = np.minimum(1, t/.5)*np.clip((d-t)/.5, 0, 1)
    return lp(hum*.6+whine+cable, 2500)*env*g

def arret(g=.12):
    """Arrêt de la cabine : petit « clonc » amorti."""
    n = int(.5*SR); t = tt(n)
    return (np.sin(2*np.pi*np.cumsum(95+60*np.exp(-t*30))/SR)*np.exp(-t*12)+bp(rng.standard_normal(n), 200, 900)*np.exp(-t*35)*.4)*g

if __name__ == '__main__':
    b = np.zeros(int(14*SR))
    add(b, grille(), .2)
    add(b, moteur(3.2), 1.3); add(b, arret(), 4.4); add(b, ding(), 4.55)          # 1re montée, arrivée
    add(b, ding(1046.5), 7.6)                                                     # ding seul
    add(b, ding(1318.5), 9.6); add(b, ding(1046.5), 9.95)                         # variante deux tons
    pk = abs(b).max(); b = b*.8/pk
    wavfile.write('essai_ascenseur.wav', SR, (b*32767).astype(np.int16)); print('ok')
