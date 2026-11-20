"""Affinage Real-ESRGAN des décors (notaire à part : en attente de la nouvelle version 9:16). coffres : passage de 5,5 s, 150 images suffisent."""
import sr_decors as S
for d, n in (('coffres', 150), ('manoir', 240), ('guichet', 240), ('krach', 240), ('hemicycle', 240), ('salon', 240)): S.job(d, n)
