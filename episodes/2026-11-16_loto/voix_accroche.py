"""Monte la voix finale : nouvelle accroche de Nicolas (voix/accroche.mp3 : « S'enrichir en jouant au Loto ? Vraiment ? Jouer au Loto toute ta vie,
ou bien placer le même montant chaque semaine en bourse. Qui finit le plus riche ? ») à la place de la 1re phrase d'origine, puis la voix d'origine
à partir de 4,9 s (« Une grille coûte… »). Écrit voice_full.wav (48 kHz mono) et voix/accroche.json : A = fin de « Vraiment ? »
(fin de l'ouverture sur la foule), B = début de la voix d'origine dans la vidéo."""
import os, json, subprocess, numpy as np
from scipy.io import wavfile
D = os.path.dirname(os.path.abspath(__file__)); SR = 48000; CUT = 4.9; VRAIMENT = 2.72
sr, v = wavfile.read(f'{D}/voix/voice_orig.wav'); v = v.astype(np.float32)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/voix/accroche.mp3', '-ac', '1', '-ar', str(SR), f'{D}/voix/accroche.wav'], check=True)
_, h = wavfile.read(f'{D}/voix/accroche.wav'); h = h.astype(np.float32)
e = np.abs(h) > np.abs(h).max()*.02; i0, i1 = max(0, np.argmax(e)-int(.04*SR)), min(len(h), len(e)-np.argmax(e[::-1])+int(.06*SR))
h = h[i0:i1]; h *= np.sqrt((v**2).mean()/max(1e-9, (h**2).mean())); h = np.clip(h, -np.abs(v).max(), np.abs(v).max())
lead, gap = .08, .3
out = np.concatenate([np.zeros(int(lead*SR)), h, np.zeros(int(gap*SR)), v[int(CUT*SR):]])
wavfile.write(f'{D}/voice_full.wav', SR, np.clip(out, -32767, 32767).astype(np.int16))
A = lead+VRAIMENT-i0/SR+.1; B = lead+len(h)/SR+gap
json.dump({'A': round(A, 3), 'B': round(B, 3), 'CUT': CUT}, open(f'{D}/voix/accroche.json', 'w')); print('A', round(A, 2), 'B', round(B, 2), 'durée', round(len(out)/SR, 2))
