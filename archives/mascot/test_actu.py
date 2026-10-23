"""Test : Mister Coin présente la voix de l'actu (Netflix / Tesla / Meta) devant le studio flouté."""
import sys, subprocess, math
sys.path.insert(0, '/home/claude/mascot')
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import puppet as P
A = '/home/claude/actu'; FPS = 30; DUR = 40.6; W, H = 1080, 1920
actions = [(3.5, 4.5, 'inquiet'),      # « Moins cinq pour cent pour Netflix »
           (11.1, 12.3, 'point'),      # carte Netflix
           (16.45, 17.5, 'inquiet'),   # suppressions de postes
           (21.2, 22.4, 'point'),      # carte Tesla
           (25.55, 26.7, 'inquiet'),   # bénéfice −43 %
           (31.25, 32.4, 'point'),     # carte Meta
           (36.75, 38.2, 'thumb'),     # l'action grimpe
           (39.25, 40.6, 'ravi')]      # « Et toi, lequel tu achètes ? »
pup = P.Puppet(f'{A}/voice_full.wav', actions)
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', f'{A}/amix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                       '-c:a', 'aac', '-b:a', '192k', '-shortest', '/home/claude/mascot/test_mister_coin.mp4'], stdin=subprocess.PIPE)
for f in range(int(DUR*FPS)):
    t = f/FPS
    bg = Image.open(f'{A}/bg30/{min(f, 1264):04d}.jpg').convert('RGB').resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(6))).enhance(.7).convert('RGBA')
    im, bob, (dw, dh) = pup.frame(t)
    # entrée : petit saut depuis le bas pendant les 0,5 premières secondes
    hop = 0 if t > .5 else (1-t/.5)**2*700
    x = W//2-im.width//2+60; y = H-im.height+40+int(bob+hop)
    # ombre au sol
    sh = Image.new('RGBA', (W, H), 0); from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse((x+im.width*.28, H-120, x+im.width*.78, H-70), fill=(0, 0, 0, 110))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    bg.alpha_composite(im, (x, y))
    ff.stdin.write(bg.convert('RGB').tobytes())
    if f % 150 == 0: print(f, flush=True)
ff.stdin.close(); ff.wait(); print('ok')
