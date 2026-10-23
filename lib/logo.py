"""Logo Actions_Bénéfices : courbe montante blanche dans une pastille turquoise (logo officiel, ne pas modifier)."""
import math, cairo
TEAL = (0x14/255, 0xA3/255, 0x8B/255, 1.0)
def logo_symbol(k, x, y, size):
    k.save(); k.translate(x-size/2, y-size/2); k.scale(size/200, size/200)
    k.new_path(); k.arc(100, 100, 100, 0, 2*math.pi); k.set_source_rgba(*TEAL); k.fill()
    k.move_to(36, 138); k.curve_to(56, 136, 64, 112, 84, 114); k.curve_to(104, 116, 112, 128, 128, 98); k.curve_to(144, 68, 146, 62, 160, 56)
    k.set_source_rgba(1, 1, 1, 1); k.set_line_width(13); k.set_line_cap(cairo.LINE_CAP_ROUND); k.stroke()
    k.new_path(); k.arc(160, 56, 11, 0, 2*math.pi); k.fill(); k.restore()
