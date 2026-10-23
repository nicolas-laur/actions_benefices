"""DA McDonald's : borne de commande générique (rouge et jaune), panier qui se remplit, ticket qui s'imprime. Aucun logo ni produit de la marque."""
import math, cairo
from PIL import Image
W, H = 1080, 1920
RED = 'DA291C'; DRED = 'A3150B'; YEL = 'FFC72C'; INK = '1D1D1B'; SUB = '6B6B6B'; WHITE = 'FFFFFF'; CREAM = 'FFF8E7'; GREEN = '1E9E5A'
def hx(h, a=1): return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def col(c, h, a=1): c.set_source_rgba(*hx(h, a))
FAM = {'k': ('Inter Display Black', 0), 'xb': ('Inter Display ExtraBold', 0), 'b': ('Inter Display', 1), 'sb': ('Inter Display SemiBold', 0),
       'm': ('Inter Display Medium', 0), 'mono': ('JetBrains Mono', 1)}
def font(c, f, size):
    fam, bold = FAM[f]; c.select_font_face(fam, 0, cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c, s, f, size, track=0):
    font(c, f, size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def _path(c, s, x0, yy, f, size, track):
    font(c, f, size); xx = x0
    for ch in s: c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track
def text(c, s, x, y, f, size, color=INK, align='c', a=1, track=0, shadow=False):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    if shadow: col(c, '000000', .25*a); _path(c, s, x0+4, yy+6, f, size, track); c.fill()
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2); c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()
def shadow(c, x, y, w, h, r, a=.18):
    for k in range(6, 0, -1):
        e = 5*k; rr(c, x-e/2, y-e/2+e*.6, w+e, h+e, r+e/2); col(c, '000000', a/6*(1-k/7)); c.fill()

def bg(c, t=0.0):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('E8341F')[:3]); g.add_color_stop_rgb(1, *hx('B81C0F')[:3]); c.set_source(g); c.paint()
    # motif de pastilles jaunes très discret qui glisse
    col(c, YEL, .07); off = (t*20) % 120
    for j in range(-1, 18):
        for i in range(-1, 10):
            x = i*120+(60 if j % 2 else 0)+off; y = j*120+off*.5
            c.arc(x, y, 14, 0, 2*math.pi); c.fill()
def promise(c, a=1.0, v=1004, sub=True):
    """promesse plein écran : 1 000 € → 1 004 €"""
    text(c, "1 000 € DANS MCDO IL Y A 5 ANS", 540, 420, 'sb', 36, YEL, 'c', a, 3)
    text(c, "1 000 €", 540, 560, 'k', 110, WHITE, 'c', a*.75)
    c.set_line_width(10); col(c, YEL, a); c.move_to(540, 640); c.line_to(540, 720); c.stroke()
    c.move_to(505, 690); c.line_to(540, 730); c.line_to(575, 690); c.stroke()
    s = f"{int(v):,}".replace(',', ' ')+" €"
    text(c, s, 540, 880, 'k', 230, YEL, 'c', a, -4, shadow=True)
    if sub: text(c, "5 ans pour gagner… 4 €", 540, 1040, 'xb', 52, WHITE, 'c', a)
def kiosk_panel(c, y0=380, h=860):
    shadow(c, 70, y0, 940, h, 40); rr(c, 70, y0, 940, h, 40); col(c, CREAM); c.fill()
    c.save(); rr(c, 70, y0, 940, h, 40); c.clip(); c.rectangle(70, y0, 940, 110); col(c, YEL); c.fill(); c.restore()
    text(c, "TA COMMANDE · 5 ANS", 120, y0+56, 'xb', 40, INK, 'l')
def item(c, y, title, detail, price, color=RED, icon='down', a=1.0):
    c.push_group()
    rr(c, 110, y, 860, 150, 26); col(c, WHITE); c.fill()
    c.arc(190, y+75, 46, 0, 2*math.pi); col(c, color, .14); c.fill()
    c.set_line_width(8); c.set_line_cap(1); c.set_line_join(1); col(c, color)
    if icon == 'down': c.move_to(160, y+55); c.line_to(185, y+80); c.line_to(200, y+68); c.line_to(222, y+95); c.stroke(); c.move_to(206, y+97); c.line_to(222, y+95); c.line_to(220, y+79); c.stroke()
    elif icon == 'people':
        for dx in (-16, 16): c.arc(190+dx, y+62, 10, 0, 2*math.pi); c.fill(); c.arc(190+dx, y+102, 18, math.pi, 2*math.pi); c.fill()
    elif icon == 'flat': c.move_to(158, y+80); c.line_to(222, y+76); c.stroke()
    elif icon == 'coin': c.arc(190, y+75, 26, 0, 2*math.pi); c.stroke(); text(c, "€", 190, y+77, 'k', 34, color)
    text(c, title, 265, y+52, 'xb', 36, INK, 'l'); text(c, detail, 265, y+102, 'm', 28, SUB, 'l')
    text(c, price, 935, y+75, 'k', 46, color, 'r')
    c.pop_group_to_source(); c.paint_with_alpha(a)
def receipt(c, u=1.0, x=190, w=700, top=330):
    """ticket qui s'imprime (u : 0 → 1)"""
    hmax = 880; h = hmax*u
    c.save(); c.rectangle(x-20, top, w+40, h+40); c.clip()
    shadow(c, x, top, w, hmax, 6, .2); c.rectangle(x, top, w, hmax); col(c, 'FFFDF8'); c.fill()
    # bord dentelé en bas
    for i in range(0, w, 28): c.move_to(x+i, top+hmax); c.line_to(x+i+14, top+hmax+16); c.line_to(x+i+28, top+hmax); col(c, 'FFFDF8'); c.fill()
    y = top+70
    text(c, "TICKET · 5 ANS DE BOURSE", x+w/2, y, 'mono', 26, INK); y += 50
    c.set_dash([6, 6]); c.set_line_width(2); col(c, INK, .5); c.move_to(x+40, y); c.line_to(x+w-40, y); c.stroke(); c.set_dash([]); y += 60
    for lab, val, cc in (("Mise de départ", "1 000 €", INK), ("Action (5 ans)", "+4 €", INK), ("Dividendes reçus", "+140 €", GREEN)):
        text(c, lab, x+50, y, 'mono', 28, INK, 'l'); text(c, val, x+w-50, y, 'mono', 30, cc, 'r'); y += 62
    c.set_dash([6, 6]); col(c, INK, .5); c.move_to(x+40, y); c.line_to(x+w-40, y); c.stroke(); c.set_dash([]); y += 80
    text(c, "TOTAL", x+50, y, 'k', 44, INK, 'l'); text(c, "≈ 1 143 €", x+w-50, y, 'k', 60, RED, 'r'); y += 80
    text(c, "×1,14 en 5 ans", x+w/2, y, 'xb', 36, INK); y += 70
    text(c, "change €/$ inclus · dividendes bruts", x+w/2, y, 'mono', 20, SUB); y += 34
    text(c, "avant impôts et frais", x+w/2, y, 'mono', 20, SUB); y += 70
    for i in range(46): bw = [3, 6, 2, 4][i*7 % 4]; c.rectangle(x+120+i*10, y, bw, 70); col(c, INK); c.fill()
    c.restore()
def caption(c, words, y=1352, size=46, accent=YEL):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 800: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, accent); c.fill(); text(c, w, x+10, yy, 'b', size, INK, 'l')
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', 1, 0, True)
            x += wd[i]+sp
def question_pill(c, a=1.0, y=1180):
    c.push_group(); s = "Tu achètes ? Réponds 1, 2 ou 3 👇".replace(" 👇", "")
    w = tw(c, s, 'xb', 36)+70; rr(c, 540-w/2, y-40, w, 80, 40); col(c, WHITE); c.fill(); text(c, s, 540, y, 'xb', 36, RED)
    c.pop_group_to_source(); c.paint_with_alpha(a)
def progress(c, u):
    col(c, WHITE, .25); rr(c, 140, 260, 800, 8, 4); c.fill(); col(c, YEL); rr(c, 140, 260, max(8, 800*u), 8, 4); c.fill()
def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)
def to_img(s):
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
