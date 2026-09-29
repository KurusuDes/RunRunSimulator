#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p seg
FONT=lato.ttf
CREAM=0xF4E3CE
CORAL=0xC24428
GOLD=0xF5B948
ENC="-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -r 30"

title() {
  local txt="$1" dur="$2" size="${3:-124}"
  local e="(1-pow(1-min(1,max(0,(t-0.12)/0.32)),3))"
  local a="min(1,max(0,(t-0.12)/0.14))*min(1,max(0,($dur-t)/0.14))"
  echo "drawbox=x=150:y=ih-103-118:w='${size}*3.2*$e':h=10:color=${GOLD}@1:t=fill:enable='gte(t,0.12)',drawtext=fontfile=$FONT:text='$txt':fontsize=$size:fontcolor=${CREAM}:shadowcolor=${CORAL}:shadowx=7:shadowy=7:x='150-90*(1-$e)':y=h-103-150-${size}:alpha='$a'"
}

lens() {
  echo "split[la][lb];[lb]gblur=sigma=16[lbb];[la][lbb]blend=all_expr='A+(B-A)*clip((hypot(X-W/2,(Y-H*0.52)*1.5)/(W*0.5)-0.28)/0.42,0,1)'"
}

punch() {
  echo "scale=w='1920*(1+0.09*pow(max(0,1-t/0.28),2))':h=-2:eval=frame,crop=1920:1080"
}

seq() {
  local dir="$1" start="$2" frames="$3" speed="$4" out="$5" vf="$6"
  ffmpeg -v error -y -framerate 60 -start_number "$start" -i "$dir/f_%04d.jpg" \
    -vf "trim=end_frame=$frames,setpts=(PTS-STARTPTS)/$speed,fps=30,scale=1920:1080,$vf" $ENC "seg/$out.mp4"
}

seq G 12 120 1 s1 "$(title 'INCUBA' 2.0),fade=in:st=0:d=0.45"
seq C 294 90 1 s2 "$(punch),fade=in:st=0:d=0.22:color=white,$(title 'EXPLORA' 1.5)"
seq D 240 180 3 s3 "null"
seq C 132 90 1 s4 "null"
seq B 441 150 1 s5 "$(punch),fade=in:st=0:d=0.22:color=white,$(title 'EVOLUCIONA' 2.5 118)"
seq E 108 90 1 s6 "$(lens),$(title 'CRÍA' 1.5)"
seq E 360 60 1 s7 "$(punch),$(lens)"
seq F1 150 90 1 s8 "$(lens),$(title 'CADA UNO ES ÚNICO' 1.5 96)"

rm -f seg/strobe_*.png
i=0
for spec in "G 100" "C 360" "B 560" "F1 230"; do
  set -- $spec
  ffmpeg -v error -y -i "$1/f_$(printf %04d $2).jpg" -vf "scale=1920:1080,eq=contrast=1.25:saturation=1.35" "seg/strobe_$i.png"
  i=$((i+1))
done
ffmpeg -v error -y \
  -loop 1 -t 0.134 -i seg/strobe_0.png -loop 1 -t 0.133 -i seg/strobe_1.png \
  -loop 1 -t 0.133 -i seg/strobe_2.png -loop 1 -t 0.1 -i seg/strobe_3.png \
  -filter_complex "[0]fps=30[a];[1]fps=30[b];[2]fps=30[c];[3]fps=30[d];[a][b][c][d]concat=n=4:v=1:a=0" $ENC seg/s9.mp4

ffmpeg -v error -y -i B/f_0590.jpg -framerate 30 -start_number 1 -i logo/logo_%04d.png \
  -filter_complex "[0]scale=1920:1080,gblur=sigma=28,eq=brightness=-0.22:saturation=0.8,loop=loop=60:size=1:start=0,fps=30,setpts=N/30/TB[bg];[1]format=rgba[lg];[bg][lg]overlay=0:0:format=auto,fade=in:st=0:d=0.18:color=white,fade=out:st=1.75:d=0.25" \
  -t 2.0 $ENC seg/s10.mp4

printf "file 's%d.mp4'\n" 1 2 3 4 5 6 7 8 9 10 > seg/list.txt
ffmpeg -v error -y -f concat -safe 0 -i seg/list.txt -c copy seg/cut.mp4

ffmpeg -v error -y -i seg/cut.mp4 -i music.wav \
  -filter_complex "[0]eq=contrast=1.07:saturation=1.12:gamma=0.98,colorbalance=rs=-0.03:bs=0.05:rh=0.05:bh=-0.04,vignette=angle=PI/5,noise=alls=5:allf=t,drawbox=x=0:y=0:w=iw:h=103:color=black:t=fill,drawbox=x=0:y=ih-103:w=iw:h=103:color=black:t=fill[v];[1]afade=t=out:st=14.6:d=0.4,loudnorm=I=-14:TP=-1.0:LRA=11[a]" \
  -map "[v]" -map "[a]" -t 15 -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart MoriMonchis_trailer_test.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 MoriMonchis_trailer_test.mp4
