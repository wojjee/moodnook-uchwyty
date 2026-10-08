#!/bin/bash
# recreate the build tree the generators expect (/workspace/moodnook/...) from v12src
set -e
S=$(cd "$(dirname "$0")/.." && pwd); M=/workspace/moodnook
sudo mkdir -p /workspace && sudo chown "$USER" /workspace
mkdir -p $M/ai-design $M/v11/render $M/v11/layout $M/v11/renders/spec $M/v11/renders/mix $M/v12/src $M/v12/renders
cp $S/cad/nookcad.py $M/ai-design/
cp $S/cad/build_v11.py $M/v11/
cp $S/cad/export_modules.py $M/v12/src/
cp $S/cad/build_exploded.py $S/render/*.py $M/v11/render/
cp $S/layout/build_pdf.py $M/v11/layout/
cp $S/site/*.py $S/site/*.js $M/v12/src/
python3 $S/site/expand_tr.py $S/site/tr_lite.json $M/v11/test_results.json
