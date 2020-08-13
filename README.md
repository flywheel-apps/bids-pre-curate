# bids-pre-curation
The bids pre-curation gear will help in the renaming of acquisitions and classification
of data based on user-input on a bulk scale.

### Workflow

This gear can run at the project, subject or session level.
It should initially be run at the project level to prepare the whole project for BIDS curation.  After that, changes can be made to specific subjects or sessions by running at the 
[subject level](https://docs.flywheel.io/hc/en-us/articles/360038261213-Run-an-analysis-gear-on-a-subject) or
[session level](https://docs.flywheel.io/hc/en-us/articles/360015505453-Analysis-Gears).
To run at the project level, select the "Analyses" tab (at the top, between "Information" and "Data Views") then click on the "Run Analysis Gear" button and in the drop-down menu, look for the "BIDS Apps" section and select "BIDS Pre-Curate".  If you are looking at the project sessions there will be another "Analyses" tab and if you select that, there will also be a "Run Analysis Gear" button.  If you click that one, you will be running at the session level.  Similarly, if you are looking at the project sessions but have selected the Subject View button, there will another analysis tab that will show the button to run at the subject level.  See the links above for more information on running at those levels.

Users will run pre-curate on their project data, this will generate csv files that will be populated with a unique list of container labels and the information we have about the files within, as well as slots for the information that we need (classification, task, etc.). 

> This will be known as __Stage 1__, in Stage 1, suggested names _can_ be  automatically populated in the new_[type]_label field by selecting the 'suggest' configuration option.  These suggested names come from the allows set in the configuration.

The user will then download and modify this csv-file (outside of Flywheel) to provide the missing/corrected information.

The corrected csv file will then be uploaded to the project and provided as input to a run of this gear to do on-the-fly mappings to properly update metadata. 

> This will be known as __Stage 2__.  In Stage 2, three CSV inputs will be provided (see __Inputs__ section)

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
First install dependencies, from the root dir after pipenv is installed (`python3 -m pip install pipenv`), run `pipenv install`.

From the root directory of the project run `./tests/integration_tests/test.sh run full --all`.  This script will do the following:
1. Copy the project directory to `/tmp/gear`
2. Run unit tests
3. Remove and re-populate the project '$GROUP/$PROJECT' with dummy data in need of pre-curation
4. Build the docker image and run stage 1 to export CSV
5. Edit the CSVs to rename files trivially
6. Build the docker container for the integration test and run stage 2 (renaming the files and updating metadata) 

After running the script, '$GROUP/$PROJECT' should be named correctly and have metadata uploaded.

### Fine grained testing
The `test.sh` script has a number of options for running, its full usage is as follows:
```
   Usage: test.sh {run,shell,test}

  -h, --help    Print this message

  -------------------------------------------------
  ... run {full,pdb} [opts]
    Run with either full run or drop into PDB

  opts:
    -a, --all         Run all tasks
    -c, --clean       Clean project and populate with new data
    -o, --stage-one   Run stage 1 test
    -s, --csv         Populate csv for stage 2
    -t. --stage-two   Run stage 2 test

  -------------------------------------------------
  ... test {unit_test,stage1,stage2,all} [opts]
    Use pytest to perform integration test on stage 1, stage 2 or full.

  opts:
    -d, --with-debug  Run pytest and drop to pdb on error
    -c. --with-cov    Run pytest and print coverage report

  -------------------------------------------------
  ... shell
    Enter bash shell in container
```

In general, running stage2 without having first run clean will lead to an API error, since the subjects will have already
been moved.  The recommended workflow is to run either `./tests/integration_tests/test.sh run full -a` or running in order
1. `./tests/integration_tests/test.sh run full -c`
2. `./tests/integration_tests/test.sh run full -o`
3. `./tests/integration_tests/test.sh run full -s`
4. `./tests/integration_tests/test.sh run full -t`

And similarly for testing instead of running, either test all, or run clean and then test stage 1, then run csv and then stage 2
