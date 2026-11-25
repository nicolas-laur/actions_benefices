"""Affinage Real-ESRGAN de tous les décors de l'épisode (240 images chacun), reprenable."""
import os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import sr_tout as T
for n in (sys.argv[1:] or ['preteur', 'garage', 'bibliotheque', 'cinema']): T.job(n, 241)
