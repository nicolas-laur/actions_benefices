"""Musique originale du spot (création Claude, libre de droits) : jazz hot années 1930, 128,7 BPM swing.
Mesures 1-4 (0 → 7,46 s) : ré mineur, discret, façon 78 tours. Mesure 5 = explosion de couleurs (7,46 s) : fa majeur, big band.
Fin : « shave and a haircut… two bits » (motif traditionnel) sur « Abonne-toi », « two bits » pendant le tour sur lui-même."""
import mido, os
D = os.path.dirname(os.path.abspath(__file__))
BPM = 128.7; TPB = 480
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def n(s):
    p = NOTE[s[0]]; i = 1
    while i < len(s) and s[i] in '#b': p += 1 if s[i] == '#' else -1; i += 1
    return p+12*(int(s[i:])+1)
def sw(b):   # swing : la croche de contretemps est retardée aux 2/3 du temps
    whole = int(b); f = b-whole
    return whole+(2/3 if abs(f-.5) < 1e-6 else f)
ev = []      # (beat, type, ch, a, b)
def note(ch, beat, dur, pitch, vel, swing=True):
    b0 = sw(beat) if swing else beat; b1 = sw(beat+dur) if swing else beat+dur
    ev.append((b0, 'on', ch, n(pitch) if isinstance(pitch, str) else pitch, vel)); ev.append((b1-.02, 'off', ch, n(pitch) if isinstance(pitch, str) else pitch, 0))
def line(ch, start, seq, vel):
    b = start
    for p, d in seq:
        if p != 'r': note(ch, b, d*.95, p, vel)
        b += d
def bend(ch, beat, v): ev.append((beat, 'bend', ch, v, 0))
def prog(ch, beat, p): ev.append((beat, 'prog', ch, p, 0))
def cc(ch, beat, c, v): ev.append((beat, 'cc', ch, c, v))
# canaux : 0 trompette (bouchée puis ouverte), 1 trombone, 2 clarinette, 3 banjo, 4 tuba, 5 piano, 9 batterie
for ch, p in ((0, 59), (1, 57), (2, 71), (3, 105), (4, 58), (5, 3)): prog(ch, 0, p)
for ch in range(6): cc(ch, 0, 91, 30)                          # un peu de réverbération
cc(1, 0, 101, 0); cc(1, 0, 100, 0); cc(1, 0, 6, 12)            # trombone : glissandos sur ±12 demi-tons
bar = lambda m: (m-1)*4
# ---------- A : ré mineur, mystérieux (mesures 1-4) ----------
A = [('D2', 'A2', ['D3', 'F3', 'A3']), ('D2', 'A2', ['D3', 'F3', 'A3']), ('G2', 'D3', ['G3', 'Bb3', 'D4']), ('A2', 'E3', ['G3', 'C#4', 'E4'])]
for m, (r, f, ch_) in enumerate(A, 1):
    note(4, bar(m), .8, r, 70, False); note(4, bar(m)+2, .8, f, 62, False)
    for bt in (1, 3):
        for p in ch_: note(5, bar(m)+bt, .35, p, 46, False)
line(0, bar(1)+2, [('D4', .5), ('F4', .5), ('A4', .5), ('G#4', .5)], 60)
line(0, bar(2), [('A4', 2), ('r', 1), ('F4', .5), ('E4', .5)], 58)
line(0, bar(3), [('D4', .5), ('E4', .5), ('F4', .5), ('G4', .5), ('Bb4', 1.5), ('r', .5)], 62)
line(0, bar(4), [('A4', 1), ('C#5', 1), ('E5', 1)], 72)
for m in range(1, 5):
    for bt in (1, 3): note(9, bar(m)+bt, .1, 44, 40, False)
for k in range(16): note(9, bar(4)+2+k/8, .06, 38, 30+k*5, False)    # roulement de caisse claire avant l'explosion
# ---------- B : fa majeur, big band (mesures 5-10) ----------
prog(0, bar(5)-.05, 56)                                         # la sourdine saute : trompette ouverte
B = [('F2', 'C3', ['F3', 'A3', 'C4']), ('D2', 'A2', ['D3', 'F#3', 'C4']), ('G2', 'D3', ['F3', 'B3', 'D4']), ('C2', 'G2', ['E3', 'Bb3', 'C4']), ('F2', 'C3', ['F3', 'A3', 'D4'])]
for m, (r, f, ch_) in enumerate(B, 5):
    note(4, bar(m), .9, r, 92, False); note(4, bar(m)+2, .9, f, 86, False)
    for bt in range(4):
        for p in ch_: note(3, bar(m)+bt, .25, p, 70 if bt % 2 else 58, False)
        note(5, bar(m)+bt, .3, ch_[0], 0, False)
    note(9, bar(m), .1, 36, 70, False); note(9, bar(m)+2, .1, 36, 62, False)
    for bt in (1, 3): note(9, bar(m)+bt, .1, 38, 64, False); note(9, bar(m)+bt, .1, 44, 60, False)
    for bt in (0, 1, 1.5, 2, 3, 3.5): note(9, bar(m)+bt, .1, 51, 58 if bt in (0, 2) else 46)
line(0, bar(5), [('C5', 1), ('A4', .5), ('C5', .5), ('F5', 1.5), ('r', .5)], 100)
line(0, bar(6), [('D5', .5), ('E5', .5), ('F#5', 1), ('A5', 1.5), ('r', .5)], 100)
line(0, bar(7), [('G5', 1), ('F5', .5), ('D5', .5), ('B4', 1), ('G4', 1)], 96)
line(0, bar(8), [('Bb4', .5), ('C5', .5), ('D5', .5), ('E5', .5), ('G5', 1), ('Bb5', 1)], 102)
# trombone : glissade de l'explosion puis contrechant à glissandos
bend(1, bar(5)-.6, 0); note(1, bar(5)-.6, 1.2, 'F3', 100, False)
for i in range(13): bend(1, bar(5)-.6+i*.05, int(-8192+8192*i/12))
for m, (a_, b_) in enumerate((('A3', 'C4'), ('F#3', 'A3'), ('F3', 'B3'), ('E3', 'Bb3')), 5):
    note(1, bar(m)+.5, 1.4, a_, 84, False); note(1, bar(m)+2.2, 1.6, b_, 88, False)
    bend(1, bar(m)+2.2, -1365)
    for i in range(7): bend(1, bar(m)+2.2+i*.05, int(-1365+1365*i/6))
for m in (5, 6, 7, 8):                                          # clarinette : petites fusées en fin de mesure
    for i, p in enumerate(('C5', 'E5', 'G5', 'C6') if m % 2 else ('A5', 'F5', 'D5', 'A4')): note(2, bar(m)+3+i*.22, .2, p, 74, False)
# « shave and a haircut » (mesure 9) sur « Abonne-toi »… silence… « two bits » pendant le tour
line(0, bar(9), [('F5', 1), ('C5', .5), ('C5', .5), ('D5', 1), ('C5', 1)], 104)
line(1, bar(9), [('A3', 1), ('A3', .5), ('A3', .5), ('Bb3', 1), ('A3', 1)], 84)
for p, b_ in ((('E5', 'G4', 'Bb3', 'C3'), bar(10)+1), (('F5', 'A4', 'C4', 'F2'), bar(10)+2)):
    note(0, b_, 1.9 if b_ > bar(10)+1.5 else .7, p[0], 112, False); note(2, b_, 1.9 if b_ > bar(10)+1.5 else .7, p[1], 90, False)
    note(1, b_, 1.9 if b_ > bar(10)+1.5 else .7, p[2], 96, False); note(4, b_, 1.9 if b_ > bar(10)+1.5 else .7, p[3], 100, False)
    note(9, b_, .1, 38, 100, False); note(9, b_, .1, 36, 100, False)
note(9, bar(5), .1, 49, 110, False); note(9, bar(10)+2, .1, 49, 116, False)
# ---------- écriture ----------
mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM)))
ev.sort(key=lambda e: (e[0], 0 if e[1] in ('prog', 'cc', 'bend', 'off') else 1)); last = 0
for b, k, ch, a, v in ev:
    t = max(0, int(round(b*TPB))); dt = t-last; last = t
    if k == 'on': tr.append(mido.Message('note_on', channel=ch, note=a, velocity=v, time=dt))
    elif k == 'off': tr.append(mido.Message('note_off', channel=ch, note=a, velocity=0, time=dt))
    elif k == 'prog': tr.append(mido.Message('program_change', channel=ch, program=a, time=dt))
    elif k == 'cc': tr.append(mido.Message('control_change', channel=ch, control=a, value=v, time=dt))
    elif k == 'bend': tr.append(mido.Message('pitchwheel', channel=ch, pitch=max(-8192, min(8191, a)), time=dt))
mid.save(f'{D}/spot.mid'); print('beat', 60/BPM, 'mesure 5 à', 16*60/BPM)
