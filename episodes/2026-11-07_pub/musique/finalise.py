"""Post-production de la musique et mixage final : partie A en « 78 tours » (bande étroite, mono, craquements, léger pleurage),
passage net en haute fidélité à l'explosion (7,46 s), musique baissée sous la voix, puis ajout au mixage voix + bruitages."""
import numpy as np, os
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
D = os.path.dirname(os.path.abspath(__file__)); E = os.path.dirname(D)
SR = 48000; DUR = 19.2; BURST = 16*60/128.7
sr, m = wavfile.read(f'{D}/spot_raw.wav'); m = m.astype(np.float32)/32768; assert sr == SR
m = m[:int(DUR*SR)]; N = len(m); t = np.arange(N)/SR; rng = np.random.default_rng(3)
def bp(x, lo, hi): return sosfilt(butter(3, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)
mono = m.mean(1)
# 78 tours : bande 280-3200 Hz, pleurage de 0,4 %, craquements et souffle
wow = (np.arange(N)+0.004*SR/(2*np.pi*.55)*np.sin(2*np.pi*.55*t)).clip(0, N-1)
old = np.interp(wow, np.arange(N), mono); old = bp(old, 280, 3200)*1.6
crack = np.zeros(N); idx = rng.integers(0, N, 900); crack[idx] = rng.uniform(-.25, .25, len(idx)); crack = bp(crack, 1500, 7000)
hiss = bp(rng.standard_normal(N)*.012, 2000, 8000)
old = old+crack*.5+hiss
a = np.clip((t-(BURST-.03))/.06, 0, 1)                      # bascule franche sur le temps de l'explosion
L = old*(1-a)+m[:, 0]*a; R = old*(1-a)+m[:, 1]*a
fade = np.clip((DUR-t)/.45, 0, 1); L *= fade; R *= fade
mus = np.stack([L, R], 1)
# mixage : voix + bruitages déjà prêts, musique baissée quand la voix parle
sr2, vx = wavfile.read(f'{E}/mix_sans_musique.wav'); vx = vx.astype(np.float32)/32768; vx = vx[:N]
sr3, vo = wavfile.read(f'{E}/voice_full.wav'); vo = vo.astype(np.float32)/32768
vo = np.pad(vo, (0, max(0, N-len(vo))))[:N]
env = np.convolve(np.abs(vo), np.ones(int(.05*SR))/int(.05*SR), 'same'); env = np.clip(env/(np.percentile(env, 95)+1e-6), 0, 1)
sm = np.zeros(N); acc = 0.0; a_, r_ = 1-np.exp(-1/(.03*SR)), 1-np.exp(-1/(.30*SR))
for i in range(0, N, 64): e = env[i]; acc += (a_ if e > acc else r_)*64*(e-acc); sm[i:i+64] = acc
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4]**2))
g = .30*rms(vo)/rms(mus.mean(1))                             # musique ~ -10 dB sous la voix hors parole
duck = (1-.55*sm)*np.where(t < BURST, .8, 1.0)
out = vx+mus*(g*duck)[:, None]
out = np.tanh(out*1.05)/np.tanh(1.05); out *= .9/np.abs(out).max()
wavfile.write(f'{D}/musique_seule.wav', SR, (mus/np.abs(mus).max()*.9*32767).astype(np.int16))
wavfile.write(f'{E}/mix_avec_musique.wav', SR, (out*32767).astype(np.int16)); print('ok', round(g, 3))
