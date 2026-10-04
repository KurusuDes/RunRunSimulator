#!/bin/bash
# look.sh NAME "x,y,z" "lx,ly,lz" fov
./shot.sh "$1" 1 4 "rig.Mode = MoriMonchiSimulator.TrailerCameraRig.Move.Dolly; rig.From = new UnityEngine.Vector3($2); rig.To = rig.From; rig.FixedPoint = new UnityEngine.Vector3($3); rig.LookOffset = UnityEngine.Vector3.zero; rig.Duration = 1f; rig.FovStart = $4; rig.FovEnd = $4;" > /dev/null
until [ -f /e/GitHub/RunRunSimulator/Recordings/promo/$1/done.txt ]; do sleep 1; done
