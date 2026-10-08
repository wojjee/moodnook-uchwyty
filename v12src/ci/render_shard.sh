#!/bin/bash
# render shard SH of N: product shots (specs_v12), family, mix and exploded (specs.py) with Blender/Cycles
set -e
SH=$1; N=$2; M=/workspace/moodnook; B=${BLENDER:-$HOME/blender/blender}
cd $M/v11/render
O=$M/v12/renders; mkdir -p $O $M/v11/renders/mix
python3 specs_v12.py $O ${SPP:-40} 100 > $O/list.txt
L=""; for k in $(cat $O/list.txt); do L="$L $O/spec/$k.json"; done
for D in OT PN OB OS KS; do python3 specs.py family $D 80 100 > /dev/null; L="$L $M/v11/renders/spec/family_$D.json"; done
python3 specs.py mix 64 > /dev/null; for f in $M/v11/renders/spec/MIX*.json; do L="$L $f"; done
python3 specs.py exploded 96 > /dev/null; L="$L $M/v11/renders/spec/exploded.json"
echo "$(echo $L | wc -w) renders total"
i=0
for f in $L; do
  if [ $((i % N)) -eq $SH ]; then
    t0=$(date +%s); n=$(basename $f .json)
    $B -b --factory-startup -P scene.py -- $f > /tmp/r_$n.log 2>&1 || { tail -40 /tmp/r_$n.log; exit 1; }
    echo "$n $(( $(date +%s) - t0 ))s"
  fi
  i=$((i + 1))
done
echo "shard $SH" > $O/shard_$SH.txt; echo "shard $SH" > $M/v11/renders/mix/shard_$SH.txt
