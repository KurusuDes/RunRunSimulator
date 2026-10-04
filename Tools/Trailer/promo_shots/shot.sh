#!/bin/bash
# usage: shot.sh NAME FRAMES WARM "C# param lines"
cd "$(dirname "$0")"
NAME=$1; FRAMES=$2; WARM=$3; PARAMS=$4
OUT=/e/GitHub/RunRunSimulator/Recordings/promo/_gen_$NAME.cs
mkdir -p /e/GitHub/RunRunSimulator/Recordings/promo
py - "$NAME" "$FRAMES" "$WARM" "$PARAMS" "$OUT" <<'PY'
import sys
name, frames, warm, params, out = sys.argv[1:]
src = open('_shot_template.cs', encoding='utf-8').read()
src = src.replace('//PARAMS', params).replace('SHOT', '"%s"' % name).replace('WARM', warm).replace('FRAMES', frames)
open(out, 'w', encoding='utf-8').write(src)
PY
unity command eval_file --no-banner --caller plugin --skill unity-cli --file "$OUT" --timeout 20 | tail -1 | cut -c1-400
