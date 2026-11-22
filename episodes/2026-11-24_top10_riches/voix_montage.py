"""Montage de la voix : voix/voice_orig.wav (ElevenLabs, 48 kHz mono) -> voice_full.wav.
Silences ajoutés (temps de la voix d'origine, durée) : trajets d'ascenseur (grille, moteur, ding) avant chaque étage,
réactions de Mister Coin après la médiane et après le top 1 %, petite respiration avant la question finale."""
import wave, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
CUTS = [(7.07, .6), (14.31, 1.5), (20.55, 1.9), (21.82, 1.0), (29.32, 1.0), (38.62, 2.2), (45.47, .5)]
def shift(t): return t+sum(d for (c, d) in CUTS if t > c)
if __name__ == '__main__':
    w = wave.open(f'{D}/voix/voice_orig.wav'); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).copy()
    out = []; p = 0
    for c, d in CUTS: out += [x[p:int(c*sr)], np.zeros(int(d*sr), np.int16)]; p = int(c*sr)
    out.append(x[p:]); y = np.concatenate(out)
    o = wave.open(f'{D}/voice_full.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(y.tobytes()); o.close()
    print(len(y)/sr)
