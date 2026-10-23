#!/usr/bin/env bash
# Rendu complet d'un épisode : ./render.sh episodes/<dossier> [nb_segments] [fps]
# Chaque épisode contient : video.py (CLI info | png t… | seg out f0 f1), mix.py, voice.mp3, timing.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; EP="$(cd "$1" && pwd)"; N="${2:-4}"; export FPS="${3:-60}"
mkdir -p "$HOME/.fonts" && cp -n "$ROOT"/fonts/* "$HOME/.fonts/" 2>/dev/null || true; fc-cache -f >/dev/null 2>&1 || true
cd "$EP"; mkdir -p out tmp
[ -f voice_full.wav ] || ffmpeg -loglevel error -y -i voice.mp3 -ac 1 -ar 48000 voice_full.wav
python3 mix.py
DUR=$(python3 video.py info); TOT=$(python3 -c "print(int($DUR*$FPS))"); STEP=$(( (TOT+N-1)/N ))
: > tmp/list.txt
for i in $(seq 0 $((N-1))); do
  python3 video.py seg tmp/seg$i.mp4 $((i*STEP)) $(((i+1)*STEP)) > tmp/seg$i.log 2>&1 &
  echo "file '$EP/tmp/seg$i.mp4'" >> tmp/list.txt
done
wait
ffmpeg -loglevel error -y -f concat -safe 0 -i tmp/list.txt -c copy tmp/video.mp4
NAME="$(basename "$EP")"
for m in mix mix_sans_musique; do
  ffmpeg -loglevel error -y -i tmp/video.mp4 -i $m.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -preset medium -crf 15 -maxrate 16M -bufsize 32M \
    -tune film -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "out/${NAME}${m#mix}.mp4"
done
echo "OK : $EP/out"
