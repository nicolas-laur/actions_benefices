"""Monte la voix finale : accroche (voix/accroche.mp3, « Peut-on vraiment devenir riche en jouant au Loto ? ») + 0,35 s + voix d'origine
(voix/voice_orig.wav). Sans accroche reçue : 2,6 s de silence à la place (pour les maquettes). Sortie : voice_full.wav, 48 kHz mono."""
import os, subprocess, numpy as np
from scipy.io import wavfile
D = os.path.dirname(os.path.abspath(__file__)); SR = 48000
sr, v = wavfile.read(f'{D}/voix/voice_orig.wav'); v = v.astype(np.float32)
src = f'{D}/voix/accroche.mp3'
if os.path.exists(src):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', str(SR), f'{D}/voix/accroche.wav'], check=True)
    _, h = wavfile.read(f'{D}/voix/accroche.wav'); h = h.astype(np.float32)
    e = np.abs(h) > np.abs(h).max()*.02; i0, i1 = np.argmax(e), len(e)-np.argmax(e[::-1])     # silences de début et de fin retirés
    h = h[max(0, i0-int(.04*SR)):min(len(h), i1+int(.06*SR))]
    pk = np.abs(v).max(); h *= np.sqrt((v**2).mean()/max(1e-9, (h**2).mean()))                # même niveau que la voix d'origine
    h = np.clip(h, -pk, pk)
else:
    h = np.zeros(int(2.25*SR), np.float32)
out = np.concatenate([np.zeros(int(.12*SR)), h, np.zeros(int(.35*SR)), v])
wavfile.write(f'{D}/voice_full.wav', SR, np.clip(out, -32767, 32767).astype(np.int16))
print('accroche', round((len(out)-len(v))/SR, 3), 's')
