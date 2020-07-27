#!/bin/bash
GEAR_DIR=/tmp/gear

if [ ! -d "$GEAR_DIR" ]; then
  mkdir /tmp/gear
fi
rm -rf /tmp/gear
cp -r ../../ /tmp/gear


cd /tmp/gear
mkdir -p /tmp/gear/flywheel/v0
mv {run.py,utils,Pipfile,Pipfile.lock} flywheel/v0
mv input/ output/
cd flywheel/v0
if [[ "$2" == "--test" ]]; then
  echo   "docker build -t flywheel/bids-pre-curate:$1 -f tests/integration_tests/Dockerfile ./"
  mv $GEAR_DIR/tests/integration_tests/test_run.py .
  chmod +x test_run.py
  mv $GEAR_DIR/tests/integration_tests/manifest.json manifest.json
  mv $GEAR_DIR/tests/integration_tests/Dockerfile Dockerfile
  docker build -t flywheel/bids-pre-curate:$1  ./
else
  mv $GEAR_DIR/Dockerfile Dockerfile
  mv $GEAR_DIR/manifest.json manifest.json
  docker build -t flywheel/bids-pre-curate:$1 ./
fi

shift
shift

fw gear local --acquisition_table $GEAR_DIR/output/acquisition_labels_Nate-BIDS-pre-curate.csv \
  --session_table $GEAR_DIR/output/session_labels_Nate-BIDS-pre-curate.csv \
  --subject_table $GEAR_DIR/output/subject_codes_Nate-BIDS-pre-curate.csv

