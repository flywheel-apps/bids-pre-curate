import sys

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
    log.info('Building acquisitions CSV...')
    acqs = fw.get_project_acquisitions(project.id)
    data2csv(acqs, proj_label,
             keep_keys=['_id', 'label'],
             prefix='acquisition_labels',
             column_rename=['id', 'existing_acquisition_label'],
             user_columns=['new_acquisition_label','modality', 'task', 'run', 'ignore'],
             unique=['label'])

    # Sessions
    log.info('Building session CSV...')
    sess = fw.get_project_sessions(project.id)
    data2csv(sess, proj_label,
             keep_keys=['_id', ['subject', 'label'], 'label'],
             prefix='session_labels',
             column_rename=['id', 'subject_label', 'existing_session_label'],
             user_columns=['new_session_label'])

    # Subjects
    log.info('Building subject CSV...')
    subj = fw.get_project_subjects(project.id)
    data2csv(subj, proj_label,
             keep_keys=['_id', 'label'],
             prefix='subject_codes',
             column_rename=['id', 'existing_subject_label'],
             user_columns=['new_subject_label'])


def data2csv(data, proj_label, keep_keys, prefix, column_rename=[], user_columns=[], unique=[]):
    """Creates a CSV on passed in data

    Create a CSV of passed in data while specifying which keys should be kept,
        how the columns should be named, what columns should be added, and whether
        or not to only use unique values

    Args:
        data (list): list of dicts containting data
        proj_label (str): project label
        keep_keys (list): list of strings or list of lists, or combination.
            This list keeps track of the keys from the acquisitions that
            will be included in the csv.  A string in the list will be
            treated as a top level key, whereas a list of strings in the
            list will be treated as nested keys.  A nested key will be
            relabeled with periods '.' denoting nesting.
        prefix (str): prefix under which to save file
        column_rename (list, optional): optional list of column titles in
            the same order as keep_keys to be displayed on the CSV.
        user_columns (list, optional): optional list of column titles
            to add to the csv
        unique (list,optional): If specified, find unique entries on the
            given indices.

    Returns:
        n/a

    """
    # Only need to keep keys from the returned acquisitions that are important for the csv
    kept_data = []
    for datum in data:
        kept_data.append({
            (key if type(key) is str else '.'.join(key)):
                (nested_get(datum, [key]) if type(key) is str else nested_get(datum, key))
            for key in keep_keys
        })
    # Convert to dataframe for writing csv
    data_df = pd.DataFrame(kept_data)

    if unique:
        data_df.drop_duplicates(subset=unique)
    # Rename _id to id
    if column_rename:
        # Assuming the user can't modify this, we don't need to catch this error
        #      if len(column_rename) != len(keep_keys)
        #          log.error(f'column_rename ({column_rename}) must be same length as keep_keys ({keep_keys}). Exiting')
        #          os.sys.exit(1)
        data_df.columns = column_rename

    if user_columns:
        data_df = data_df.reindex(columns=data_df.columns.tolist() + user_columns)

    data_df = data_df.drop_duplicates(subset=['label'])
    csv_file = f'/tmp/{prefix}_{proj_label}.csv'
    data_df.to_csv(csv_file)

def read_from_csv(csv_file, type='aqc', project):
    fw = flywheel.Client()
    conf = fw.get_config().site.api_url
    # TODO: Need to do some validation to make sure the CSV file is in the correct format
    #   this should be at the row level, otherwise if they put columns in wrong, it may really
    #   mess up their whole project
    data = pd.read_csv(csv_file)

    if type == 'subj':
        unique_subjs = pd.unique(data['new_subject_label'])
        for unique_subj in unique_subjs:
            subjects = data[data['new_subject_label'] == unique_subj]
            for subject in subjects.iterrows():
                # If subject doesn't exist, update this subject to have the new label and code
                # otherwise, update sessions below it to point to this
                existing_subj = project.subjects.find_first(f'label={unique_subj}')
                new_subject = fw.get_subject(subject['id'])
                if not existing_subj:
                    new_subject.update({
                        'label': unique_subj,
                        'code': unique_subj
                    })
                else:
                    for session in new_subject.sessions.iter():
                        session.update({
                            # TODO: Join with the sessions csv to update new label at the same time
                            #   if applicable
                            'subject': new_subject
                        })




    elif type == 'ses':
            for index, row in data.iterrows():
                session = fw.get_session(row['id'])
                if row['new_session_label']:
                    session.update(label=row['new_session_label'])

    elif type == 'acq':
        for index, row in data.iterrows():
            acquisition = fw.get_acquisition(row['id'])
            to_update = {}
            if row['new_acquisition_label']: to_update['label'] = row['new_acquisition_label']
            if row['modality']: to_update['files.info.BIDS.Modality'] = row['modality']
            if row['task']: to_update['files.info.BIDS.Task'] = row['task']
            if row['run']: to_update['files.info.BIDS.Run'] = row['run']
            if row['ignore']: to_update['files.info.BIDS.Ignore'] = row['ignore']

            if to_update:
                acquisition.update(to_update)

    else:
        log.error(f'Invalid CSV type: {type}.  Exiting')
        sys.exit(1)


