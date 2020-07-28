#!/bin/bash
# Pull project creation script
GROUP='scien'
PROJECT='Nate-BIDS-pre-curate'
git submodule update

GEAR_DIR=/tmp/gear
# Create requirements
pipenv run pip freeze > tests/integration_tests/requirements.txt
# Remove local requirements
sed -i '/^-e/d' tests/integration_tests/requirements.txt
# Install requirements
pip install --user -r tests/integration_tests/requirements.txt

sudo rm -rf $GEAR_DIR
cp -r . $GEAR_DIR
function build_container {
  # Create gear directory and copy resources to dir

  #
  cd $GEAR_DIR
  mkdir -p $GEAR_DIR/flywheel/v0
  cp {setup.py,run.py,Pipfile,Pipfile.lock} flywheel/v0
  cp -r utils flywheel/v0

  cd flywheel/v0

  if [[ "$2" == "--test" ]]; then
    cp $GEAR_DIR/tests/integration_tests/test_run.py test_run.py
    chmod +x test_run.py
    cp $GEAR_DIR/tests/integration_tests/manifest.json manifest.json
    cp $GEAR_DIR/tests/integration_tests/Dockerfile Dockerfile
    cp $GEAR_DIR/tests/integration_tests/requirements.txt requirements.txt
    docker build -t flywheel/bids-pre-curate:$1  ./
  else
    cp $GEAR_DIR/Dockerfile Dockerfile
    cp $GEAR_DIR/manifest.json manifest.json
    cp $GEAR_DIR/requirements.txt requirements.txt
    docker build -t flywheel/bids-pre-curate:$1 ./
  fi
}

##################### Unit Testing
python -m pytest tests/unit_tests/test_bids_curate.py

## Pre stage 1, clean and make new project

yes y | python tests/integration_tests/delete_project.py --group "$GROUP" --project "$PROJECT" --data-only
python tests/BIDS_popup_curation/makesession.py --group "$GROUP" --project "$PROJECT" --subjects IVA_202,IVA_202-1,IVA_202-2

##################### Stage 1 integration testing
# Build container as production
build_container $1
cd $GEAR_DIR/flywheel/v0
# Run local csv generation stage of gear
fw gear local
# Outputs are
cd $GEAR_DIR
mkdir input
cp flywheel/v0/output/* input/
python tests/integration_tests/populate_csv.py --sub-name IVA_202  \
  --acquisitions input/acquisition_labels_$PROJECT.csv \
  --subjects input/subject_codes_$PROJECT.csv \
  --sessions input/session_labels_$PROJECT.csv

##################### Stage 2 integration testing
build_container $1 --test
cd $GEAR_DIR/flywheel/v0

fw gear local --acquisition_table ../../input/acquisition_labels_$PROJECT.csv \
  --session_table ../../input/session_labels_$PROJECT.csv \
  --subject_table ../../input/subject_codes_$PROJECT.csv

