"""Séquence test du moteur v2 (Coin2) sur les 14 premières secondes de la voix Kering. usage : python3 test_coin2.py sortie.mp4 [fps]"""
import sys, os, subprocess
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from PIL import Image, ImageDraw, ImageFont
from coin2 import Coin2
E = f'{D}/../episodes/2026-10-27_kering'
BG = Image.open(f'{E}/decors/boutique.jpg').convert('RGB'); BG = BG.resize((int(BG.width*1920/BG.height), 1920), Image.LANCZOS); BG = BG.crop(((BG.width-1080)//2, 0, (BG.width-1080)//2+1080, 1920))
TAG = Image.new('RGBA', (300, 170), 0); d = ImageDraw.Draw(TAG); d.rounded_rectangle((0, 0, 299, 169), 26, fill=(200, 55, 45, 255))
d.text((150, 85), "−16 %", font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 80), fill='white', anchor='mm')
places = {'dehors': (-250, 1660, .28), 'centre': (560, 1660, .28), 'droite': (800, 1660, .28, True)}
mc = Coin2(f'{E}/voice_full.wav', places, 'dehors', duree=14,
           sauts_de_place=[(0.0, 'centre', 'marche', 2.2), (9.6, 'droite')],
           coucous=[(2.3, 3.6)],
           actions=[(4.0, 5.6, 'point', (540, 470)), (6.05, 7.2, 'souci'), (7.3, 8.05, 'inquiet'), (8.1, 9.2, 'ravi'), (11.0, 12.36, 'thumb'), (12.4, 14, 'abattu')],
           gestes_mots=[3.7], objets=[(10.3, 11.0, TAG, 'D', 2.0)])
def frame(t):
    out = BG.copy().convert('RGBA'); dr = ImageDraw.Draw(out)
    if 4.0 <= t < 6.0: dr.rounded_rectangle((330, 420, 750, 520), 20, fill=(255, 252, 246, 240)); dr.text((540, 470), "215 €", font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 70), fill=(200, 55, 45), anchor='mm')
    out.alpha_composite(mc.layer(t)); return out.convert('RGB')
if __name__ == '__main__':
    out = sys.argv[1]; fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                           '-ss', '0', '-t', '14', '-i', f'{E}/voice_full.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], stdin=subprocess.PIPE)
    for i in range(int(14*fps)): ff.stdin.write(frame(i/fps).tobytes())
    ff.stdin.close(); ff.wait()
