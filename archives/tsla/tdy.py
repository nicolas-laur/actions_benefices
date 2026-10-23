"""DA Tesla : vision d'une voiture autonome. Route de nuit en perspective, HUD, cadres de détection. Aucun logo ni design Tesla."""
import math, cairo, random
from PIL import Image
W, H = 1080, 1920
INK = 'F2F4F7'; SUB = '9AA3B0'; RED = 'E82127'; CYAN = '3FD0FF'; AMBER = 'FFB020'; GREEN = '35D07F'; BG0 = '05070A'
VX, VY = 540, 1010          # point de fuite
def hx(h, a=1): return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def col(c, h, a=1): c.set_source_rgba(*hx(h, a))
FAM = {'k': ('Inter Display Black', 0), 'xb': ('Inter Display ExtraBold', 0), 'b': ('Inter Display', 1), 'sb': ('Inter Display SemiBold', 0),
       'm': ('Inter Display Medium', 0), 'l': ('Inter Display Light', 0), 'mono': ('JetBrains Mono', 1)}
def font(c, f, size):
    fam, bold = FAM[f]; c.select_font_face(fam, 0, cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c, s, f, size, track=0):
    font(c, f, size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def _path(c, s, x0, yy, f, size, track):
    font(c, f, size); xx = x0
    for ch in s: c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track
def text(c, s, x, y, f, size, color=INK, align='c', a=1, track=0, glow=0):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    if glow:
        for k in (10, 6, 3):
            c.set_line_width(k); _path(c, s, x0, yy, f, size, track); col(c, color, .06*glow*a); c.stroke()
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2); c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()

def road(c, t=0.0, speed=1.0, tint=None, dist=None):
    """route de nuit : ciel dégradé, halo d'horizon, voies qui défilent, bas-côtés, lampadaires"""
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('020305')[:3]); g.add_color_stop_rgb(.45, *hx('0B1220')[:3])
    g.add_color_stop_rgb(.53, *hx('141C2C')[:3]); g.add_color_stop_rgb(.56, *hx('07090D')[:3]); g.add_color_stop_rgb(1, *hx('030405')[:3]); c.set_source(g); c.paint()
    hz = cairo.RadialGradient(VX, VY, 0, VX, VY, 700); hz.add_color_stop_rgba(0, *hx(tint or '3A6EA8', .35)); hz.add_color_stop_rgba(1, *hx('000000', 0))
    c.save(); c.translate(VX, VY); c.scale(1.6, 0.35); c.translate(-VX, -VY); c.set_source(hz); c.paint(); c.restore()
    # chaussée (trapèze)
    c.move_to(VX-30, VY); c.line_to(VX+30, VY); c.line_to(W+700, H); c.line_to(-700, H); c.close_path()
    rg = cairo.LinearGradient(0, VY, 0, H); rg.add_color_stop_rgb(0, *hx('0E1219')[:3]); rg.add_color_stop_rgb(1, *hx('07090C')[:3]); c.set_source(rg); c.fill()
    def proj(xw, z):          # xw : position latérale (m), z : distance (m)
        s = 1/(z+0.6); return VX+xw*s*620, VY+s*1180
    # bas-côtés lumineux
    for xw, cc, a in ((-6.0, INK, .5), (6.0, INK, .5)):
        c.move_to(*proj(xw, 80)); [c.line_to(*proj(xw, z)) for z in (40, 20, 10, 5, 2, 0.4)]; c.set_line_width(4); col(c, cc, a); c.stroke()
    # tirets centraux qui défilent
    D = dist if dist is not None else t*speed*14
    off = D % 6
    for k in range(30):
        z0 = 0.2+k*6-off; z1 = z0+3
        if z1 < 0.25 or z0 > 90: continue
        z0 = max(z0, 0.25); (x0, y0), (x1, y1) = proj(-0.08, z0), proj(-0.08, z1); (x2, y2), (x3, y3) = proj(0.08, z1), proj(0.08, z0)
        c.move_to(x0, y0); c.line_to(x1, y1); c.line_to(x2, y2); c.line_to(x3, y3); c.close_path(); col(c, INK, .75*min(1, 3/(z0+0.5))*min(1, max(0, (z0-0.3)/3.0))); c.fill()
    # lampadaires lointains qui défilent
    off2 = D % 18
    for k in range(8):
        z = 2+k*18-off2
        if z < 1 or z > 140: continue
        for side in (-1, 1):
            x, y = proj(side*9, z); hgt = 900/(z+0.6); a = min(1, 6/(z+1))
            c.set_line_width(max(1, 8/(z+0.6))); col(c, '8090A0', .5*a); c.move_to(x, y); c.line_to(x, y-hgt); c.stroke()
            gl = cairo.RadialGradient(x, y-hgt, 0, x, y-hgt, 60*a+8); gl.add_color_stop_rgba(0, *hx('FFD9A0', .9*a)); gl.add_color_stop_rgba(1, *hx('FFD9A0', 0)); c.set_source(gl); c.paint()
    return proj

def trajectory(c, proj, color=CYAN, a=.6, curve=0.0):
    """trajectoire prévue (bande translucide au sol)"""
    pts_l, pts_r = [], []
    for k in range(40):
        z = 0.3+k*1.2; dx = curve*(z/40)**2*6
        pts_l.append(proj(dx-1.2, z)); pts_r.append(proj(dx+1.2, z))
    c.move_to(*pts_l[0]); [c.line_to(*p) for p in pts_l]; [c.line_to(*p) for p in reversed(pts_r)]; c.close_path()
    g = cairo.LinearGradient(0, VY, 0, H); g.add_color_stop_rgba(0, *hx(color, 0)); g.add_color_stop_rgba(1, *hx(color, .35*a)); c.set_source(g); c.fill()
    for pts in (pts_l, pts_r):
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts]; c.set_line_width(3); g2 = cairo.LinearGradient(0, VY, 0, H); g2.add_color_stop_rgba(0, *hx(color, 0)); g2.add_color_stop_rgba(1, *hx(color, a)); c.set_source(g2); c.stroke()

def bracket(c, x, y, w, h, color=CYAN, a=1.0, L=34, lw=4):
    """cadre de détection : coins en équerre"""
    c.set_line_width(lw); col(c, color, a); c.set_line_cap(0)
    for (px, py, dx, dy) in ((x, y, 1, 1), (x+w, y, -1, 1), (x, y+h, 1, -1), (x+w, y+h, -1, -1)):
        c.move_to(px+dx*L, py); c.line_to(px, py); c.line_to(px, py+dy*L); c.stroke()
    rr(c, x, y, w, h, 4); col(c, color, .06*a); c.fill()
def tag(c, s, x, y, color=CYAN, size=24, ink='05070A', align='l'):
    w = tw(c, s, 'mono', size)+26; x0 = x if align == 'l' else x-w
    c.rectangle(x0, y-size*0.85, w, size*1.7); col(c, color); c.fill(); text(c, s, x0+13, y, 'mono', size, ink, 'l')
def warn(c, x, y, s, color=RED):
    c.move_to(x, y-s*0.55); c.line_to(x+s*0.6, y+s*0.5); c.line_to(x-s*0.6, y+s*0.5); c.close_path(); col(c, color); c.fill()
    c.set_line_width(s*0.1); col(c, '05070A'); c.move_to(x, y-s*0.2); c.line_to(x, y+s*0.18); c.stroke(); c.arc(x, y+s*0.33, s*0.06, 0, 2*math.pi); c.fill()
def hud(c, t=0.0, speed_kmh=88, u=0.0, label="AUTOPILOTE · ACTIF", color=CYAN):
    """bandeau HUD en haut : statut, vitesse, horloge"""
    y = 330
    c.arc(150, y, 9, 0, 2*math.pi); col(c, color, .6+.4*math.sin(t*4)); c.fill()
    text(c, label, 172, y, 'mono', 22, color, 'l')
    text(c, f"{int(speed_kmh)}", 930, y-4, 'xb', 44, INK, 'r'); text(c, "km/h", 940, y+4, 'mono', 18, SUB, 'l')
def scanlines(c, a=.05):
    col(c, '000000', a)
    for y in range(0, H, 4): c.rectangle(0, y, W, 1); c.fill()
def caption(c, words, y=1352, size=46, accent=RED):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 800: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    vg = cairo.LinearGradient(0, y0-90, 0, y0+len(lines)*72+40); vg.add_color_stop_rgba(0, 0, 0, 0, 0); vg.add_color_stop_rgba(.3, 0, 0, 0, .55); vg.add_color_stop_rgba(.8, 0, 0, 0, .55); vg.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.rectangle(0, y0-90, W, len(lines)*72+130); c.set_source(vg); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: c.rectangle(x, yy-34, wd[i], 66); col(c, accent); c.fill(); text(c, w, x+10, yy, 'b', size, '05070A' if accent in (CYAN, AMBER, GREEN) else 'FFFFFF', 'l')
            else: text(c, w, x, yy, 'b', size, INK, 'l')
            x += wd[i]+sp
def progress(c, u, color=RED):
    col(c, 'FFFFFF', .12); c.rectangle(140, 262, 800, 4); c.fill(); col(c, color); c.rectangle(140, 262, max(4, 800*u), 4); c.fill()
def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)
def to_img(s):
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
