"""Test : clips Veo (Gemini) détourés et intégrés dans la boutique Kering, avec la voix. usage : python3 test_veo.py sortie.mp4"""
import sys, os, subprocess, numpy as np, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); E = f'{D}/../../episodes/2026-10-27_kering'
W, H, FPS = 1080, 1920, 24
BG = Image.open(f'{E}/decors/boutique.jpg').convert('RGB'); BG = BG.resize((int(BG.width*1920/BG.height), 1920), Image.LANCZOS)
BG = np.asarray(BG.crop(((BG.width-W)//2, 0, (BG.width-W)//2+W, H))).astype(np.float32)
def frames(f, w, h):
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', f, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w*h*3)
        if len(b) < w*h*3: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
def key(a):
    a = a.astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = 1-np.clip((ks-30)/60, 0, 1); al = cv2.GaussianBlur(al, (0, 0), .7)
    sp = ks > 0; a[..., 1] = np.where(sp, np.minimum(G, R*.75+B*.25), G); a[..., 2] = np.where(sp, np.minimum(B, R), B)   # débordement vert neutralisé (sans liseré violet)
    dk = (a.sum(2) < 330) & (a[..., 2] > a[..., 0]*.8)                       # traits sombres teintés de bleu : ramenés au brun
    a[..., 2] = np.where(dk, a[..., 0]*.55, a[..., 2]); a[..., 1] = np.where(dk, np.minimum(a[..., 1], a[..., 0]*.75), a[..., 1])
    return a, al
def place(a, al, s, cx, feet, X, Y):
    """met l'image détourée à l'échelle s, son point (cx, feet) sur (X, Y) de l'écran"""
    M = np.float32([[s, 0, X-cx*s], [0, s, Y-feet*s]])
    fg = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_CUBIC); m = cv2.warpAffine(al, M, (W, H), flags=cv2.INTER_LINEAR)
    return fg, np.clip(m, 0, 1)
def shadow(X, Y, k=1.):
    m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(X), int(Y)), (95, 14), 0, 0, 360, .45*k, -1); return cv2.GaussianBlur(m, (0, 0), 9)
out = sys.argv[1]
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-itsoffset', '5.6', '-i', f'{E}/voice_full.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p',
                       '-c:a', 'aac', '-shortest', out], stdin=subprocess.PIPE)
GY = 1660; sB, sA = 234/307, 234/255
B = list(frames(f'{D}/clip_b.mp4', 720, 1280))[:144]
A = frames(f'{D}/clip_a.mp4', 1280, 720)
def comp(fg, m, X):
    sh = shadow(X, GY)
    bg = BG*(1-sh[..., None]); return np.clip(bg*(1-m[..., None])+fg*m[..., None], 0, 255).astype(np.uint8)
last = None
for i, f in enumerate(B):                                    # il entre en marchant et s'arrête au centre
    a, al = key(f); fg, m = place(a, al, sB, 367, 1001, 540, GY); last = (fg, m); ff.stdin.write(comp(fg, m, 540).tobytes())
for j, f in enumerate(A):                                    # puis il parle (fondu de 0,3 s entre les deux clips)
    a, al = key(f); fg, m = place(a, al, sA, 637, 631, 540, GY)
    if j < 7:
        u = j/7; fg = last[0]*(1-u)+fg*u; m = last[1]*(1-u)+m*u
    ff.stdin.write(comp(fg, m, 540).tobytes())
ff.stdin.close(); ff.wait()
