#!/bin/bash
set -e
cd "$(dirname "$0")/growth"
CREAM=0xFFF6E4
WALNUT=0x5E3B22
GOLD=0xE2B04A
ENC="-c:v libx264 -preset medium -crf 24 -maxrate 14M -bufsize 28M -pix_fmt yuv420p -r 30"
mkdir -p txt
t() {
  local id="$1" a="$2" b="$3" size="$4" y="$5" txt="$6"
  printf '%s' "$txt" > "txt/$id.txt"
  local al="min(1,max(0,(t-$a)/0.3))*min(1,max(0,($b-t)/0.3))"
  local sl="(1-pow(1-min(1,max(0,(t-$a)/0.45)),3))"
  echo "drawtext=fontfile=lato.ttf:textfile=txt/$id.txt:fontsize=$size:fontcolor=${CREAM}:borderw=3:bordercolor=${WALNUT}:shadowcolor=${WALNUT}@0.6:shadowx=6:shadowy=6:x='120-80*(1-$sl)':y=$y:alpha='$al':enable='between(t,$a,$b)'"
}
bar() {
  local a="$1" b="$2" y="$3" w="$4"
  local sl="(1-pow(1-min(1,max(0,(t-$a-0.1)/0.4)),3))"
  echo "drawbox=x=120:y=$y:w='$w*$sl':h=12:color=${GOLD}@1:t=fill:enable='between(t,$a+0.1,$b-0.1)'"
}
VF="scale=1920:1080"
VF="$VF,$(t intro1 0.3 2.9 150 380 'MoriMonchis')"
VF="$VF,$(t intro2 0.6 2.9 64 560 'Así crece tu tienda')"
VF="$VF,$(bar 0.3 2.9 540 640)"
VF="$VF,$(t e1 3.0 6.4 96 820 'Etapa 1 · El puestito'),$(bar 3.0 6.4 940 820)"
VF="$VF,$(t e1b 12.0 14.8 80 840 'Mejoras · nivel 2 y 3'),$(bar 12.0 14.8 940 760)"
VF="$VF,$(t e2 17.0 20.4 96 820 'Etapa 2 · Tienda del barrio'),$(bar 17.0 20.4 940 1040)"
VF="$VF,$(t e3 26.0 29.4 96 820 'Etapa 3 · Tienda famosa'),$(bar 26.0 29.4 940 900)"
VF="$VF,$(t e4 35.0 38.4 96 820 'Etapa 4 · Emporio MoriMonchi'),$(bar 35.0 38.4 940 1140)"
VF="$VF,$(t end1 43.6 48.0 150 380 'MoriMonchis'),$(t end2 44.0 48.0 64 560 '16 zonas · 3 niveles cada una'),$(bar 43.6 48.0 540 640)"
VF="$VF,fade=in:st=0:d=0.5,fade=out:st=47.3:d=0.7"
ffmpeg -v error -y -framerate 30 -i frames/f_%04d.jpg -i growth_music.wav -i growth_pops.wav \
  -filter_complex "[0:v]$VF[v];[1:a][2:a]amix=inputs=2:weights='1 0.55':normalize=0,afade=t=out:st=47:d=1[a]" \
  -map "[v]" -map "[a]" $ENC -c:a aac -b:a 192k -shortest MoriMonchis_crecimiento.mp4
echo done
