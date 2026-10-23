import re, numpy as np, scipy.io.wavfile as w, functools
exec(open('align.py').read().split('S = [syl(p)')[0])   # ph, syl
S = [syl(p) for p in ph]
sr, x = w.read('voice16.wav'); x = x.astype(float)/32768
hop = int(.01*sr); n = len(x)//hop; r = np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(1)); db = 20*np.log10(r+1e-6); db -= db.max()
db = np.convolve(db, np.ones(3)/3, 'same')
low = db < -30
# zones basses ≥ 40 ms
dips = []; i = 0
while i < n:
    if low[i]:
        j = i
        while j < n and low[j]: j += 1
        if (j-i) >= 4: dips.append((i/100, j/100))
        i = j
    else: i += 1
lead = dips[0][1]; end = [d for d in dips if d[0] > 38][-1][0] if dips[-1][1] >= n/100-.05 else n/100
dips = [d for d in dips if lead < d[0] < end-.05 and d[1] < end]
speech = end-lead-sum(b-a for a, b in dips); rate = sum(S)/speech
print('lead', lead, 'end', end, 'rate', round(rate, 2), 'dips', len(dips))
N, P = len(ph), len(dips)
def cost(s, d): e = s/rate; return ((e-d)/(.25+.18*e))**2
@functools.lru_cache(None)
def f(i, j, t0):
    if i == N-1: return (cost(S[i], end-t0), ())
    best = (1e18, ())
    skipped = 0.0
    for k in range(j, P):
        a, b = dips[k]; d = a-t0
        if d > 0:
            c = cost(S[i], d) + 3*skipped
            if c < 60:
                rr = f(i+1, k+1, b)
                if c+rr[0] < best[0]: best = (c+rr[0], ((t0, a, b),)+rr[1])
            if d > S[i]/rate*2.2+1: break
        skipped += max(0, (b-a)-.15)*10   # une longue pause non utilisée coûte
    return best
c, segs = f(0, 0, lead)
print('cost', round(c, 1))
res = []
for i, p in enumerate(ph):
    t0 = segs[i][0] if i < len(segs) else segs[-1][2]
    t1 = segs[i][1] if i < len(segs) else end
    res.append((round(t0-lead, 2), round(t1-lead, 2), p)); print(f"{t0-lead:6.2f} {t1-lead:6.2f} {S[i]:3d}  {p}")
import json; json.dump({'lead': lead, 'end': end, 'ph': res}, open('align.json', 'w'), ensure_ascii=False)
