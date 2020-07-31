# bids-pre-curation
The bids pre-curation gear will help in the renaming of acquisitions and classification
of data based on user-input on a bulk scale.

### Workflow
Users will run pre-curate on their project data, this will generate csv files that will be populated with a unique list of container labels and the information we have about the files within, as well as slots for the information that we need (classification, task, etc.). 

The user will then download and modify this csv-file (outside of Flywheel) to provide the missing/corrected information.

The corrected csv file will then be uploaded to the project and provided as input to a run of this gear to do on-the-fly mappings to properly update metadata. 

### Inputs
* 3 CSV files

    1. session_table
    2. subject_table
    3. acquisition_table

All three inputs would be optional, however if one is provided they should all be provided

### Outputs
* CSV files that will be populated with a unique list of container labels and the information we have about the files within, as well as slots for the information that we need (classification, task, etc. for acquisitions)

* These files will be attached to the project by the customer after the customer fills them out if providing input.

### Config
* sessions_per_subject (int)  = number of sessions that will be collected per subject. If 0, sessions will be excluded from bids.
required

* infer_bids (boolean) - will try to infer bids fields from classification and acquisition label (SeriesDescription) and pre-populate the output csv files with these values 

* reset_bids_info (boolean)

* reset_bids_ignore (boolean)

## Testing
### Full integration testing
From the root directory of the project run `./tests/integration_tests/test.sh <version> --all`.  This script will do the following:
1. Generate (if needed) and install requirements with pipenv
2. Copy the project directory to `/tmp/gear`
3. Run unit tests
4. Remove and re-populate the project '$GROUP/$PROJECT' with dummy data in need of pre-curation
5. Build the docker image and run phase 1 to export CSV
6. Edit the CSVs to rename files trivially
7. Build the docker container for the integration test and run phase 2 (renaming the files and updating metadata) 

After running the script, '$GROUP/$PROJECT' should be named correctly and have metadata uploaded.

### Fine grained testing
The `test.sh` script has a number of options for running, its full usage is as follows:
```
  Usage: test.sh <version> <to_run>

  <version>: Version to tag docker images with (required)

  to_run:
    -a, --all         Run all tasks
    -c, --clean       Clean project and populate with new data
    -h, --help        Print this message
    -o, --stage-one   Run stage 1 test
    -s, --csv         Populate csv for stage 2
    -t. --stage-two   Run stage 2 test
    -u, --unit-test   Run unit tests
  "
```
