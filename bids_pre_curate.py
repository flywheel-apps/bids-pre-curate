import flywheel
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.deep_dict import nested_get
import logging
import pandas as pd

log = logging.getLogger(__name__)


def build_csv(group, proj_name):
    log.debug(f'Starting client connection')
    fw = flywheel.Client()

    project = fw.projects.find_one(f'group={group},label={proj_name}')
    log.info(f'Building CSV for {project.label}')
    proj_label = make_file_name_safe(project.label)

    # Acquisitions
    acqs = fw.get_project_acquisitions(project.id)
    acq_csv(acqs, proj_label)

    # Subjects
    subjs = fw.get_project_subjects(project.id)
    subj_csv(subjs, proj_label)

    # Sessions
    sess = fw.get_project_sessions(project.id)
    ses_csv(sess, proj_label)


def acq_csv(acqs, proj_label):
    # Only need to keep keys from the returned acquisitions that are important for the csv
    keep_keys = ['_id', 'label']  # Can be expanded later if needed
    acquisitions = [{key: acq[key] for key in keep_keys} for acq in acqs]
    # Convert to dataframe for writing csv
    acq_df = pd.DataFrame(acquisitions)
    # Rename _id to id
    acq_df.columns = ['id', 'label']
    acq_df = acq_df.reindex(columns=acq_df.columns.tolist() + ['modality', 'task', 'run', 'ignore'])

    acq_df = acq_df.drop_duplicates(subset=['label'])
    csv_file = f'/tmp/acquisition_labels_{proj_label}.csv'
    acq_df.to_csv(csv_file)


def subj_csv(subjs, proj_label):
    # Only need to keep keys from the returned subjects that are important for the csv
    keep_keys = ['_id', 'code']
    subjects = [{key: subj[key] for key in keep_keys} for subj in subjs]
    # Convert to dataframe for writing csv
    subj_df = pd.DataFrame(subjects)
    # Rename column names for readability
    subj_df.columns = ['id', 'existing_subj_label']
    subj_df['new_subject_labels'] = ''
    csv_file = f'/tmp/subject_codes_{proj_label}.csv'
    subj_df.to_csv(csv_file)


def ses_csv(sess, proj_label):
    # Only need to keep keys from the returned sessions that are important for the csv
    # sessions are a little more complicated because we need a nested label subject.label.
    keep_keys = ['_id', 'label', ['subject', 'label']]
    sessions = [
        {(key if type(key) is str else '_'.join(key)):
             (nested_get(ses, key) if type(key) is list else nested_get(ses, [key]))
         for key in keep_keys} for ses in sess
    ]
    ses_df = pd.DataFrame(sessions)
    # Rename columns
    ses_df.columns = ['id', 'existing_session_label', 'subject_label']
    ses_df['new_session_labels'] = ''
    csv_file = f'/tmp/sesect_codes_{proj_label}.csv'
    ses_df.to_csv(csv_file)
