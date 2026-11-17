"""Story Instagram du 17/11 : « bonne semaine » + emplacement libre au centre pour la publication du carrousel (autocollant à poser dans l'appli).
usage : python3 story.py  → out/story.png"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *
cv = fond('banque').copy(); s, c = surface()
glow_text(cv, "BONNE SEMAINE", 540, 330, 118, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
glow_text(cv, "À TOUS !", 540, 455, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
text(c, "Nouveau carrousel : 9 sigles de la bourse… et un piège", 540, 560, 'sb', 32, ICE, 'c', .95)
put_emoji(cv, '👇', 540, 620, 48)
bb = coin(cv, 'joie', 250, 1640, 330); bulle_pres(c, "On révise|ensemble ?", bb, 36, .25)
cv.alpha_composite(to_img(s)); os.makedirs(f'{D}/out', exist_ok=True); cv.convert('RGB').save(f'{D}/out/story.png'); print('ok')
