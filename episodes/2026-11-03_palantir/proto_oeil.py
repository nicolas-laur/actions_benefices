import sys, numpy as np, cairo, cv2
from PIL import Image
sys.path.insert(0, '.')
from dossier import *
SC, PX, PY = 1.9, 540, 700
def eye_frame(t):
    cap = cv2.VideoCapture('decors/oeil.mp4'); cap.set(1, int(t*24)); ok, f = cap.read()
    f = cv2.resize(f, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
    ox, oy = int(684*SC/1.9*1.0 - PX + 0), 0
    px, py = 180/360*f.shape[1], 316/640*f.shape[0]; x0, y0 = int(px-PX), int(py-PY)
    f = f[y0:y0+H, x0:x0+W]
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32); c = f.astype(np.float32)
    c = c*.35+g[..., None]*.65                                      # presque noir et blanc
    c = np.clip((c-128)*1.25+118, 0, 255)
    bl = cv2.GaussianBlur(c, (0, 0), 2); c = np.clip(c*1.6-bl*.6, 0, 255)  # netteté après agrandissement
    return c[..., ::-1]
t = 1.5
base = eye_frame(t)
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
target(c, PX, PY, .8, 'dark', coords=("POINT 01", "CIBLE"))
for k in range(0, H, 6): c.rectangle(0, k, W, 2); col(c, '000000', .10); c.fill()
y = (t*900) % H; g = cairo.LinearGradient(0, y-120, 0, y); g.add_color_stop_rgba(0, *rgb(RED), 0); g.add_color_stop_rgba(1, *rgb(RED), .25); c.set_source(g); c.rectangle(0, y-120, W, 120); c.fill()
hud(c, t, 'dark', ("ACTIONS_BÉNÉFICES / DOSSIER PLTR", "REC  03.11.2026", "CONFIDENTIEL · NIVEAU 3", "TC "))
s.flush(); ov = np.asarray(Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1)).astype(np.float32)
a = ov[..., 3:]/255; out = base*(1-a)+ov[..., :3]*a
v = (np.hypot(*np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H)))); out *= np.clip(1.15-.55*v, 0, 1)[..., None]
Image.fromarray(grain_layer(out, t, 9).astype(np.uint8)).save('prev/oeil_proto.png')
Image.open('prev/oeil_proto.png').resize((540, 960)).save('prev/oeil_proto_s.png')
