import re, subprocess, math
txt = """Sept mille sept cent soixante-quatre euros. | C'est ce que valent aujourd'hui mille euros placés dans le S and P cinq cents | la veille de la faillite de Lehman Brothers. |
Vendredi douze septembre deux mille huit. | Tu places mille euros dans le CAC quarante, | et mille dans le S and P cinq cents. |
Lundi, | Lehman Brothers s'effondre. |
En six mois, | le CAC perd quarante-deux pour cent. | Le S and P, | quarante-six. |
Le S and P retrouve son niveau | en deux ans et trois mois. | Le CAC, | lui… | cinq ans et cinq mois. |
Et aujourd'hui ? | Ton CAC vaut mille huit cent trente et un euros. | Ton S and P : | sept mille sept cent soixante-quatre. |
Même krach, | même mise. | Quatre fois plus. |
Au prochain krach… | et toi, | tu achètes ?"""
ph = [p.strip() for p in txt.replace('\n', ' ').split('|') if p.strip()]
def syl(s):
    s = s.lower().replace("'", ' ')
    n = 0
    for w in re.findall(r"[a-zàâéèêëîïôûùüç]+", s):
        v = re.findall(r"[aeiouyàâéèêëîïôûùü]+", w)
        k = len(v)
        if w.endswith('e') and k > 1 and not w.endswith('ée'): k -= 1
        if w.endswith('es') and k > 1 and w not in ('les', 'des', 'mes', 'tes', 'ses', 'ces'): k -= 1
        n += max(1, k)
    return n
S = [syl(p) for p in ph]
out = subprocess.run(['ffmpeg', '-i', 'voice.mp3', '-af', 'silencedetect=noise=-34dB:d=0.07', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
lead = en[0]; pauses = list(zip(st[1:], en[1:]))
end = pauses[-1][0]; pauses = pauses[:-1]
# DP : chaque frontière de phrase (n-1) assignée à une pause distincte, croissante ; coût = écart du débit
import functools
N = len(ph); P = len(pauses); tot = sum(S); rate = tot/(end-lead-sum(b-a for a, b in pauses))
@functools.lru_cache(None)
def f(i, j, t0):
    # phrase i commence à t0 ; frontières restantes i..N-2 ; pause candidate >= j
    if i == N-1:
        d = end-t0; return ((S[i]/rate-d)**2/(S[i]/rate+.3), ())
    best = (1e9, ())
    for k in range(j, P):
        a, b = pauses[k]; d = a-t0
        if d <= 0: continue
        c = (S[i]/rate-d)**2/(S[i]/rate+.3)
        if c > 25: 
            if d > S[i]/rate*2.5: break
            continue
        r = f(i+1, k+1, b)
        if c+r[0] < best[0]: best = (c+r[0], ((t0, a),)+r[1])
    return best
c, segs = f(0, 0, lead)
segs = list(segs)+[(segs[-1][1] if False else None, end)]
segs = list(f(0, 0, lead)[1])
print('lead', lead, 'rate', round(rate, 2), 'cost', round(c, 2))
for i, p in enumerate(ph):
    a = segs[i][0]-lead if i < len(segs) else segs[-1][1]
    print(f"{a:6.2f}  {S[i]:3d}  {p}")
