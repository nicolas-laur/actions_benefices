"""Rendu reprenable d'un épisode, par tranches de 120 images.
Chaque appel rend les tranches manquantes pendant au plus --budget secondes (3 workers en parallèle), puis s'arrête.
Quand toutes les tranches existent, il assemble la vidéo et produit out/<épisode>.mp4 et out/<épisode>_sans_musique.mp4.
usage : python3 render.py episodes/<dossier> [--budget 150] [--workers 3] [--fps 60]
(conçu pour les environnements qui limitent la durée d'une commande, comme le Mac de Nicolas via Claude : relancer jusqu'à « TERMINÉ »)"""
import os, sys, time, subprocess, argparse, glob, shutil
ap = argparse.ArgumentParser(); ap.add_argument('ep'); ap.add_argument('--budget', type=float, default=150)
ap.add_argument('--workers', type=int, default=3); ap.add_argument('--fps', type=int, default=60); ap.add_argument('--chunk', type=int, default=120)
A = ap.parse_args()
ROOT = os.path.dirname(os.path.abspath(__file__)); EP = os.path.abspath(A.ep); NAME = os.path.basename(EP)
os.environ['FPS'] = str(A.fps); T0 = time.time()
def sh(cmd, **kw): return subprocess.run(cmd, shell=True, check=True, cwd=EP, **kw)
os.makedirs(os.path.expanduser('~/.fonts'), exist_ok=True)
for f in glob.glob(f'{ROOT}/fonts/*'):
    d = os.path.expanduser(f'~/.fonts/{os.path.basename(f)}')
    if not os.path.exists(d): shutil.copy(f, d)
os.makedirs(f'{EP}/tmp/chunks', exist_ok=True); os.makedirs(f'{EP}/out', exist_ok=True)
if not os.path.exists(f'{EP}/voice_full.wav'): sh('ffmpeg -loglevel error -y -i voice.mp3 -ac 1 -ar 48000 voice_full.wav')
if not os.path.exists(f'{EP}/mix.wav'): sh('python3 mix.py')
dur = float(subprocess.check_output('python3 video.py info', shell=True, cwd=EP).decode().split()[-1])
tot = int(dur*A.fps); chunks = [(a, min(tot, a+A.chunk)) for a in range(0, tot, A.chunk)]
def path(a): return f'{EP}/tmp/chunks/c{a:06d}.mp4'
todo = [c for c in chunks if not os.path.exists(path(c[0]))]
print(f'{len(chunks)-len(todo)}/{len(chunks)} tranches déjà rendues', flush=True)
running = {}
avg = None
while (todo or running):
    for p, (a, b, t) in list(running.items()):
        if p.poll() is not None:
            del running[p]
            if p.returncode == 0: os.replace(path(a)+'.part.mp4', path(a)); dt = time.time()-t; avg = dt if avg is None else .7*avg+.3*dt
            else: print(f'échec tranche {a}', flush=True)
    left = A.budget-(time.time()-T0)
    while todo and len(running) < A.workers and left > (avg or 60)*1.1:
        a, b = todo.pop(0)
        p = subprocess.Popen(['python3', 'video.py', 'seg', path(a)+'.part.mp4', str(a), str(b)], cwd=EP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        running[p] = (a, b, time.time())
    if not running: break
    time.sleep(1)
done = sum(os.path.exists(path(c[0])) for c in chunks)
print(f'{done}/{len(chunks)} tranches rendues en {time.time()-T0:.0f} s', flush=True)
if done < len(chunks): print('À SUIVRE : relancer la même commande'); sys.exit(0)
with open(f'{EP}/tmp/list.txt', 'w') as f:
    for a, _ in chunks: f.write(f"file '{path(a)}'\n")
sh('ffmpeg -loglevel error -y -f concat -safe 0 -i tmp/list.txt -c copy tmp/video.mp4')
for m, suf in (('mix', ''), ('mix_sans_musique', '_sans_musique')):
    out = f'out/{NAME}{suf}.mp4'
    if not os.path.exists(out):
        sh(f'ffmpeg -loglevel error -y -i tmp/video.mp4 -i {m}.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -preset veryfast -crf 15 '
           f'-maxrate 16M -bufsize 32M -tune film -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart -f mp4 {out}.part')
        os.replace(f'{EP}/{out}.part', f'{EP}/{out}')
    if time.time()-T0 > A.budget: print('À SUIVRE : relancer pour la dernière version'); sys.exit(0)
print('TERMINÉ', f'{EP}/out')
