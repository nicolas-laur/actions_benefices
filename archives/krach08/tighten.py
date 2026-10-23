"""Resserre les pauses de la voix (≤ 0,22 s, 0,30 s sur les effets) puis accélère légèrement : objectif ≈ 34 s.
Écrit voice_tight.wav et timing.json (début/fin de chaque phrase dans le nouveau temps)."""
import json, numpy as np, scipy.io.wavfile as w, subprocess
A = json.load(open('align.json')); lead = A['lead']
ph = [(a+lead, b+lead, p) for a, b, p in A['ph']]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'voice.mp3', '-ac', '1', '-ar', '44100', 'v44.wav'])
sr, x = w.read('v44.wav'); x = x.astype(np.float32)
KEEP = {"cinq ans et cinq mois.": .32, "Quatre fois plus.": .32, "tu achètes ?": .3, "Lehman Brothers s'effondre.": .3}
out = []; tm = []; cur = 0.0; pad = .04
for i, (a, b, p) in enumerate(ph):
    a0 = max(0, a-pad); b0 = min(len(x)/sr, b+pad)
    if i: 
        g = a0-(ph[i-1][1]+pad); g2 = min(max(g, 0), KEEP.get(p, .2))
        out.append(np.zeros(int(g2*sr), np.float32)); cur += g2
    seg = x[int(a0*sr):int(b0*sr)].copy(); f = int(.01*sr); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    tm.append((cur+(a-a0), p)); out.append(seg); cur += len(seg)/sr
y = np.concatenate(out); w.write('v_cut.wav', sr, y.astype(np.int16))
TEMPO = float(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 1.07
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'v_cut.wav', '-af', f'atempo={TEMPO}', 'voice_tight.wav'])
d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice_tight.wav'], capture_output=True, text=True).stdout)
tm = [(round(t/TEMPO, 2), p) for t, p in tm]
json.dump({'dur': d, 'tempo': TEMPO, 'ph': tm}, open('timing.json', 'w'), ensure_ascii=False)
print('cut', round(len(y)/sr, 2), '-> final', round(d, 2))
for t, p in tm: print(f'{t:6.2f}  {p}')
