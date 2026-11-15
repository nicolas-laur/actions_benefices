"""Affinage Real-ESRGAN de toutes les images des 4 décors (toutes sont utilisées : chaque scène dure plus de 10 s)."""
import sr_decors as S
for d in ('tabac', 'tirage', 'machine', 'verger'): S.job(d, 240)
