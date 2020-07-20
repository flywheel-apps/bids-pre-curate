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