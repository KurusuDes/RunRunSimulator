#!/bin/bash
set -e
SRC="${1:-/e/GitHub/RunRunSimulator/Recordings/promo}"
cd "$SRC"
mkdir -p seg
ENC="-c:v libx264 -preset medium -crf 15 -pix_fmt yuv420p -r 30"

lens() {
  echo "split[la][lb];[lb]gblur=sigma=14[lbb];[la][lbb]blend=all_expr='A+(B-A)*clip((hypot(X-W/2,(Y-H*0.52)*1.5)/(W*0.5)-0.32)/0.42,0,1)'"
}

punch() {
  echo "scale=w='1920*(1+0.08*pow(max(0,1-t/0.3),2))':h=-2:eval=frame,crop=1920:1080"
}

flash() {
  echo "fade=in:st=0:d=0.2:color=white"
}

pop() {
  echo "eq=contrast=1.12:saturation=1.28:gamma=0.97"
}

clip() {
  local shot="$1" start="$2" frames="$3" out="$4" vf="$5" speed="${6:-1}"
  ffmpeg -v error -y -framerate 30 -start_number "$start" -i "$shot/f_%04d.jpg" \
    -vf "trim=end_frame=$frames,setpts=(PTS-STARTPTS)/$speed,fps=30,scale=1920:1080,$vf" $ENC "seg/$out.mp4"
}

clip egg_top       0   60 c01 "$(pop),$(lens),fade=in:st=0:d=0.5"
clip egg_dolly     40  60 c02 "$(pop),$(punch),$(flash),$(lens)"
clip slime_orbit   30  60 c03 "$(pop),$(punch),$(flash),$(lens)"
clip pair_orbit    40  60 c04 "$(pop),$(punch),$(flash),$(lens)"
clip line_track    40  60 c05 "$(pop),$(lens)"
clip life_track    20  60 c06 "$(pop),$(punch),$(lens)"
clip arena_aerial  70  30 c07 "$(pop),$(flash)"
clip arena_clash1  15  45 c08 "$(pop),$(punch)"
clip arena_clash1  95  30 c09 "$(pop),$(punch),$(flash)"
clip arena_clash3  20  45 c10 "$(pop),$(punch)"
clip arena_clash2  150 45 c11 "$(pop),$(punch),$(flash)"
clip arena_clash3  165 60 c12 "$(pop),$(punch)"
clip arena_clash1  135 45 c13 "$(pop),$(punch),$(flash)"

i=0
for spec in "egg_dolly 100 8" "line_track 75 7" "pair_orbit 80 8" "arena_clash1 120 7"; do
  set -- $spec
  ffmpeg -v error -y -loop 1 -framerate 30 -i "$1/f_$(printf %04d $2).jpg" \
    -vf "scale=1920:1080,eq=contrast=1.35:saturation=1.5,$(punch)" -frames:v $3 $ENC "seg/s$i.mp4"
  i=$((i+1))
done
printf "file 's%d.mp4'\n" 0 1 2 3 > seg/strobe.txt
ffmpeg -v error -y -f concat -safe 0 -i seg/strobe.txt -c copy seg/c14.mp4
ffmpeg -v error -y -f lavfi -i color=black:s=1920x1080:r=30 -frames:v 30 $ENC seg/c15.mp4

ffmpeg -v error -y -framerate 30 -start_number 0 -i line_push/f_%04d.jpg -framerate 30 -start_number 1 -i logo/logo_%04d.png \
  -filter_complex "[0]trim=end_frame=120,setpts=1.5*(PTS-STARTPTS),fps=30,scale=1920:1080,gblur=sigma=26,eq=brightness=-0.2:saturation=0.85[bg];[1]format=rgba,tpad=stop_mode=clone:stop_duration=2[lg];[bg][lg]overlay=0:-40:format=auto,fade=in:st=0:d=0.2:color=white,fade=out:st=5.4:d=0.6" \
  -frames:v 180 $ENC seg/c16.mp4

: > seg/list.txt
for k in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16; do echo "file 'c$k.mp4'" >> seg/list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i seg/list.txt -c copy seg/cut.mp4
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 seg/cut.mp4

ffmpeg -v error -y -i seg/cut.mp4 -framerate 30 -start_number 0 -i gfx/g_%04d.png -i music.wav \
  -filter_complex "[0]eq=contrast=1.05:saturation=1.08:gamma=0.98,colorbalance=rs=0.02:bs=-0.03:rh=0.04:bh=-0.03,rgbashift=rh=-2:bh=2,vignette=angle=PI/5,noise=alls=4:allf=t[base];[1]format=rgba[g];[base][g]overlay=0:0:format=auto,drawbox=x=0:y=0:w=iw:h=103:color=black:t=fill,drawbox=x=0:y=ih-103:w=iw:h=103:color=black:t=fill,format=yuv420p[v];[2]afade=t=out:st=28.8:d=1.2,loudnorm=I=-14:TP=-1.0:LRA=11[a]" \
  -map "[v]" -map "[a]" -t 30 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart MoriMonchis_promo_EN.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 MoriMonchis_promo_EN.mp4
