#!/bin/bash
# Pull project creation script
GROUP='scien'
PROJECT='Nate-BIDS-pre-curate'
git submodule update

cwd=$(pwd)

GEAR=/tmp/gear/flywheel/v0
if [[ ! -a tests/integration_tests/requirements.txt ]]; then
  # Create requirements
  pipenv run pip freeze > tests/integration_tests/requirements.txt
  # Remove local requirements
  sed -i '/^-e/d' tests/integration_tests/requirements.txt
  # Install requirements
  pip install --user -r tests/integration_tests/requirements.txt
fi

VERSION=$(grep "version" manifest.json | sed "s/[^-0-9._]//g")
function build_container {
  echo "$(pwd)"

  if [[ ! -d $GEAR ]]; then
    mkdir -p $GEAR
  fi
  # Create gear directory and copy resources to dir
  cp -r {setup.py,run.py,Pipfile*,tests,utils} $GEAR/

  cd $GEAR

  mv tests/integration_tests/Dockerfile .

  if [[ ! -z "$1"  && "$1" == '--hide-build' ]]; then
    docker build -t flywheel/bids-pre-curate:$VERSION ./ > /dev/null 2>&1
  else
    docker build -t flywheel/bids-pre-curate:$VERSION ./
  fi
  if [[ ! -d inputs ]]; then
    mkdir inputs
  fi
  if [[ ! -d outputs ]]; then
    mkdir outputs
  fi
}
function run_container {

  cd $GEAR
  container=$(docker container ls -a | grep bids-pre-curate)
  if [[ ! -z $container ]]; then
    docker container rm bids-pre-curate
  fi

  echo "Running command inside container: $1"
  # If config file supplied run the container as a gear
  if [[ -f "$2" ]]; then
    docker run -it --rm --name bids-pre-curate \
      -v $GEAR/inputs:/flywheel/v0/input \
      -v $GEAR/outputs:/flywheel/v0/output \
      -v "$GEAR/$2":/flywheel/v0/config.json \
      -v ~/.config/flywheel/user.json:/root/.config/flywheel/user.json \
      flywheel/bids-pre-curate:$VERSION "$1" 2>&1
  else
    #Otherwise, run as just an image
    docker run -it --rm --name bids-pre-curate \
      -v $GEAR/inputs:/flywheel/v0/input \
      -v $GEAR/outputs:/flywheel/v0/output \
      -v ~/.config/flywheel/user.json:/root/.config/flywheel/user.json \
      flywheel/bids-pre-curate:$VERSION "$1" 2>&1
  fi
}

function unit_test {
  ##################### Unit Testing
  run_cmd="pipenv run python -m pytest tests/unit_tests/test_bids_pre_curate.py"
  run_container "$run_cmd"
}
function pre_stage_1 {
  ## Pre stage 1, clean and make new project
  run_cmd="yes y | pipenv run python3 tests/integration_tests/delete_project.py \
                      --group $GROUP --project $PROJECT --data-only \
                   && pipenv run python3 tests/BIDS_popup_curation/makesession.py \
                      --group $GROUP --project $PROJECT --subjects IVA_202,IVA_202-1,IVA_202-2"
  run_container "$run_cmd"
}
function stage_1 {
  ##################### Stage 1 integration testing
  # Build container as production
  cd "$cwd"
#  run="python3 -m pdb tests/integration_tests/test_run.py"
  run_container "$1" tests/assets/config-stage1.json
}

function populate_csv {
  # Outputs are
  cd "$GEAR"
  mv -f outputs/* inputs
  run_cmd="pipenv run python3 tests/integration_tests/populate_csv.py --sub-name IVA_202 \
    --acquisitions input/acquisition_labels_$PROJECT.csv \
    --subjects input/subject_codes_$PROJECT.csv \
    --sessions input/session_labels_$PROJECT.csv"
  run_container "$run_cmd"

}

function stage_2 {
  ##################### Stage 2 integration testing

  cd $cwd
#  run="python3 -m pdb tests/integration_tests/test_run.py"
  run_container "$1" tests/assets/config-stage2.json
}
__test_usage="
  ... test {unit_test,stage1,stage2,all} [opts]
    Use pytest to perform integration test on stage 1, stage 2 or full.

  opts:
    -d, --with-debug  Run pytest and drop to pdb on error
    -c. --with-cov    Run pytest and print coverage report
"
test(){
  if [[ "$2" == "-c" ]] || [[ "$2" == "--with-cov" ]]; then
    cmd="pipenv run python -m pytest --cov run tests/integration_tests/test_run.py"
  elif [[ "$2" == "-d" ]] || [[ "$2" == "--with-debug" ]]; then
    cmd="pipenv run python -m pytest --pdb tests/integration_tests/test_run.py"
  else
    cmd="pipenv run python -m pytest tests/integration_tests/test_run.py"
  fi

  case $1 in
    "unit_test")
      unit_test
      ;;
    "stage1")
      stage_1 "$cmd"
      ;;
    "stage2")
      stage_2 "$cmd"
      ;;
    "all")
      unit_test
      pre_stage_1
      stage_1 "$cmd"
      populate_csv
      stage_2 "$cmd"
      ;;
    *)
      echo "$__test_usage"
      exit
      ;;
  esac
}
__shell_usage="
  ... shell
    Enter bash shell in container
"
shell(){
  run_container "/bin/bash"
}
__run_usage="
  ... run {full,pdb} [opts]
    Run with either full run or drop into PDB

  opts:
    -a, --all         Run all tasks
    -c, --clean       Clean project and populate with new data
    -o, --stage-one   Run stage 1 test
    -s, --csv         Populate csv for stage 2
    -t. --stage-two   Run stage 2 test
"
run(){
  run_cmd="pipenv run python3 tests/integration_tests/test_run.py"
  pdb_cmd="pipenv run python3 -m pdb tests/integration_tests/test_run.py"
  if [[ $1 == 'pdb' ]]; then
    cmd=$pdb_cmd
    shift
  elif [[ $1 == 'full' ]]; then
    cmd="$run_cmd"
    shift
  else
    echo "$__run_usage"
  fi
  case "$1" in
    "-a" | "--all")
      unit_test
      pre_stage_1
      stage_1 "$cmd"
      populate_csv
      stage_2 "$cmd"
      ;;
    "-c" | "--clean")
      pre_stage_1
      ;;
    "-o" | "--stage-one")
      stage_1 "$cmd"
      ;;
    "-s" | "--csv")
      populate_csv
      ;;
    "-t" | "--stage-two")
      stage_2 "$cmd"
      ;;
    *)
      echo "$__run_usage"
      ;;
  esac
}
__usage="
  Usage: $(basename $0) {run,shell,test}

  -h, --help    Print this message

  -------------------------------------------------
  "$__run_usage"

  -------------------------------------------------
  "$__test_usage"

  -------------------------------------------------
  "$__shell_usage"
  "
main() {
  build_container
  while [ $# -gt 0 ]; do
    case "$1" in
      "run")
        shift
        run "$@"
        break
        ;;
      "test")
        shift
        test "$@"
        break
        ;;
      "shell")
        shift
        shell
        break
        ;;
      "-h" | "--help")
        echo "$__usage"
        break
        ;;
      *)
        echo "$__usage"
        break
        ;;
    esac
  done
}
main "$@"
