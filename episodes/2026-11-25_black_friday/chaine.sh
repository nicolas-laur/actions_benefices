#!/bin/bash
# affinage -> interpolation -> rendu, reprenable (chaque étape saute ce qui est déjà fait)
cd "$(dirname "$0")"
while pgrep -f sr_lance.py >/dev/null; do sleep 20; done
python3 sr_lance.py hall rayon enquete vitrine rue >> sr.log 2>&1
python3 hd_lance.py >> hd.log 2>&1
python3 rendu.py >> rendu.log 2>&1
echo FIN >> rendu.log
