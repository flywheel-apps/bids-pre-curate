# bids-pre-curation
The bids pre-curation gear will help in the renaming of acquisitions and classification
of data based on user-input on a bulk scale.

### Workflow

This gear can run at the project, subject or session level.
It should initially be run at the project level to prepare the whole project for BIDS curation.  After that, changes can be made to specific subjects or sessions by running at the 
[subject level](https://docs.flywheel.io/hc/en-us/articles/360038261213-Run-an-analysis-gear-on-a-subject) or
[session level](https://docs.flywheel.io/hc/en-us/articles/360015505453-Analysis-Gears).
To run at the project level, select the "Analyses" tab (at the top, between "Information" and "Data Views") then click on the "Run Analysis Gear" button and in the drop-down menut, look for the "BIDS Apps" section and select "BIDS Pre-Curate".  If you are looking at the project sessions there will be another "Analyses" tab and if you select that, there will also be a "Run Analysis Gear" button.  If you click that one, you will be running at the session level.  Similarly, if you are looking at the project sessions but have selected the Subject View button, there will another analysis tab that will show the button to run at the subject level.  See the links above for more information on running at those levels.

Users will run pre-curate on their project data, this will generate csv files that will be populated with a unique list of container labels and the information we have about the files within, as well as slots for the information that we need (classification, task, etc.). 

> This will be known as _Stage 1_, in Stage 1, suggested names are automatically populated in the new_[type]_label field.  These suggested names come from the allows set in the configuration.

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
* dry_run (boolean): __default: false__, Perform a dry-run for stage 2.  Instead of actually renaming the sessions, subjects, and acquisitions, log what they would be renamed to.

* allows (string): __default: ''__, String of additional characters to allow.  By default, A-Z, a-z, and 0-9 are allowed, common allows are hyphens '-', underscores '_' and periods '.'. 

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
  Usage: test.sh <version> <to_run> [allows]

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
```
