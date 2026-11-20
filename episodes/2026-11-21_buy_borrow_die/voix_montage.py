"""Montage de la voix : voix/voice_orig.wav (ElevenLabs, 48 kHz mono) -> voice_full.wav.
Le bruit non verbal entre « 3,4 % » et « Leur méthode » (20,0-20,75 s) est remplacé par du silence, puis deux silences sont allongés
pour les réactions de Mister Coin : +1,85 s après « 3,4 % » (19,6 s), +2,34 s après « effacée » (52,8 s) : environ 2,6 s de silence chacun."""
import wave, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
CUTS = [(19.6, 1.85), (52.8, 2.34)]
def shift(t): return t+sum(d for (c, d) in CUTS if t > c)
if __name__ == '__main__':
    w = wave.open(f'{D}/voix/voice_orig.wav'); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).copy()
    a, b = int(20.0*sr), int(20.75*sr); x[a:b] = 0
    out = []; p = 0
    for c, d in CUTS: out += [x[p:int(c*sr)], np.zeros(int(d*sr), np.int16)]; p = int(c*sr)
    out.append(x[p:]); y = np.concatenate(out)
    o = wave.open(f'{D}/voice_full.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(y.tobytes()); o.close()
    print(len(y)/sr)
