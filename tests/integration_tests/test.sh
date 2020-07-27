#!/bin/bash

GEAR_DIR=/tmp/gear

rm -rf $GEAR_DIR
cp -r ../../ $GEAR_DIR
function build_container {
  # Create gear directory and copy resources to dir

  #
  cd $GEAR_DIR
  mkdir -p $GEAR_DIR/flywheel/v0
  mv {run.py,utils,Pipfile,Pipfile.lock} flywheel/v0

  cd flywheel/v0

  if [[ "$2" == "--test" ]]; then
    mv $GEAR_DIR/tests/integration_tests/test_run.py test_run.py
    chmod +x test_run.py
    mv $GEAR_DIR/tests/integration_tests/manifest.json manifest.json
    mv $GEAR_DIR/tests/integration_tests/Dockerfile Dockerfile
    docker build -t flywheel/bids-pre-curate:$1  ./
  else
    mv $GEAR_DIR/Dockerfile Dockerfile
    mv $GEAR_DIR/manifest.json manifest.json
    docker build -t flywheel/bids-pre-curate:$1 ./
  fi
}

##################### Unit Testing
pipenv run python ../unit_tests/test_bids_curate.py

## Pre stage 1, clean and make new project
yes y | pipenv run python delete_project.py --group scien --project Nate-BIDS-pre-curation --data-only
pipenv run python ../BIDS_popup_curation/makesession.py --group scien --project Nate-BIDS-pre-curate --subjects IVA_202,IVA_202-1,IVA_202-2

##################### Stage 1 integration testing
# Build container as production
build_container $1
cd $GEAR_DIR/flywheel/v0
pipenv install pandas
# Run local csv generation stage of gear
fw gear local
# Outputs are
pipenv run python ../../tests/integration_tests/populate_csv.py --sub-name IVA_202  \
  --acquisitions output/acquisition_labels_Nate-BIDS-pre-curate.csv \
  --subjects output/subject_codes_Nate-BIDS-pre-curate.csv \
  --sessions output/session_labels_Nate-BIDS-pre-curate.csv



##################### Stage 2 integration testing
build_container $1 --test
cd $GEAR_DIR/flywheel/v0

fw gear local --acquisition_table $GEAR_DIR/output/acquisition_labels_Nate-BIDS-pre-curate.csv \
  --session_table $GEAR_DIR/output/session_labels_Nate-BIDS-pre-curate.csv \
  --subject_table $GEAR_DIR/output/subject_codes_Nate-BIDS-pre-curate.csv

