#!/bin/bash
# Pull project creation script
GROUP='scien'
PROJECT='Nate-BIDS-pre-curate'
git submodule update

GEAR_DIR=/tmp/gear
if [[ ! -a tests/integration_tests/requirements.txt ]]; then
  # Create requirements
  pipenv run pip freeze > tests/integration_tests/requirements.txt
  # Remove local requirements
  sed -i '/^-e/d' tests/integration_tests/requirements.txt
  # Install requirements
  pip install --user -r tests/integration_tests/requirements.txt
fi

sudo rm -rf $GEAR_DIR
cp -r . $GEAR_DIR
function build_container {
  # Create gear directory and copy resources to dir
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

function unit_test {
  ##################### Unit Testing
  python -m pytest tests/unit_tests/test_bids_curate.py
}
function pre_stage_1 {
  ## Pre stage 1, clean and make new project
  yes y | python tests/integration_tests/delete_project.py --group "$GROUP" --project "$PROJECT" --data-only
  python tests/BIDS_popup_curation/makesession.py --group "$GROUP" --project "$PROJECT" --subjects IVA_202,IVA_202-1,IVA_202-2
}
function stage_1 {
  ##################### Stage 1 integration testing
  # Build container as production
  build_container $1
  cd $GEAR_DIR/flywheel/v0
  # Run local csv generation stage of gear
  echo "Allow string: $2"
  fw gear local --allows "$2"
}

function populate_csv {
  # Outputs are
  cd $GEAR_DIR
  mkdir input
  cp flywheel/v0/output/* input/
  python tests/integration_tests/populate_csv.py --sub-name IVA_202  \
    --acquisitions input/acquisition_labels_$PROJECT.csv \
    --subjects input/subject_codes_$PROJECT.csv \
    --sessions input/session_labels_$PROJECT.csv
}

function stage_2 {
  ##################### Stage 2 integration testing
  build_container $1 --test
  cd $GEAR_DIR/flywheel/v0

  fw gear local --acquisition_table ../../input/acquisition_labels_$PROJECT.csv \
    --session_table ../../input/session_labels_$PROJECT.csv \
    --subject_table ../../input/subject_codes_$PROJECT.csv
}
function help {
  __usage="
  Usage: $(basename $0) <version> <to_run> [allows]

  <version>: Version to tag docker images with (required)
  [allows]: Optional string of characters to add to the allow regex.

  to_run:
    -a, --all         Run all tasks
    -c, --clean       Clean project and populate with new data
    -h, --help        Print this message
    -o, --stage-one   Run stage 1 test
    -s, --csv         Populate csv for stage 2
    -t. --stage-two   Run stage 2 test
    -u, --unit-test   Run unit tests
  "
  echo "$__usage"
}

if [[ $# -gt 2 ]]; then
    allows="$3"
else
    allows=""
fi
echo "Allows: $allows"

case "$2" in
  "-h" | "--help")
    help
    ;;
  "-a" | "--all")
    unit_test
    pre_stage_1
    stage_1 $1 $allows
    populate_csv
    stage_2 $1
    ;;
  "-c" | "--clean")
    pre_stage_1
    ;;
  "-o" | "--stage-one")
    stage_1 $1 $allows
    ;;
  "-s" | "--csv")
    populate_csv
    ;;
  "-t" | "--stage-two")
    stage_2 $1
    ;;
  "-u" | "--unit-test")
    unit_test
    ;;
  *)
    help
    ;;
esac
