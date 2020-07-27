import sys

import flywheel_gear_toolkit
from flywheel.models.info_update_input import InfoUpdateInput
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.delete_empty import delete_empty_subject
from utils.deep_dict import nested_get
import logging
import pandas as pd
import pprint

log = logging.getLogger(__name__)


def build_csv(acqs, subs, sess, proj_label):
    """Wrapper for building CSVs for project

        Subjects, sessions and acquisitions are passed in in the form of lists of
        dicts.  They are then passed to data2csv with options set to be converted
        to csv format.
    Args:
        acqs (list):  list of dicts containing acquisitions for the project.
        subs (list):  list of dicts containing subjects for the project.
        sess (list):  list of dicts containing sessions for the project
        proj_label (str):  project name (label)

    Returns:
        file_names (tuple): Tuple of filenames (full filepath) for all three csv files
    """
    log.info(f'Starting client connection')

    proj_label = make_file_name_safe(proj_label)
    log.info(f'Building CSV for {proj_label}')

    # Acquisitions
    log.info('Building acquisitions CSV...')
    acq_file = data2csv(acqs, proj_label,
                        keep_keys=['id', 'label'],
                        prefix='acquisition_labels',
                        column_rename=['id', 'existing_acquisition_label'],
                        user_columns=['new_acquisition_label', 'modality', 'task', 'run', 'ignore'],
                        unique=['label'])

    # Sessions
    log.info('Building session CSV...')
    sess_file = data2csv(sess, proj_label,
                         keep_keys=['id', ['subject', 'label'], 'label'],
                         prefix='session_labels',
                         column_rename=['id', 'subject_label', 'existing_session_label'],
                         user_columns=['new_session_label'])

    # Subjects
    log.info('Building subject CSV...')
    sub_file = data2csv(subs, proj_label,
                        keep_keys=['id', 'label'],
                        prefix='subject_codes',
                        column_rename=['id', 'existing_subject_label'],
                        user_columns=['new_subject_label'])
    file_names = (acq_file[0], sess_file[0], sub_file[0])
    return file_names


def data2csv(data, proj_label, keep_keys, prefix, column_rename=[], user_columns=[],
             unique=[], no_print=False):
    """Creates a CSV on passed in data

    Create a CSV of passed in data while specifying which keys should be kept,
        how the columns should be named, what columns should be added, and whether
        or not to only use unique values

    Args:
        data (list): list of dicts containing data
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
        no_print (boolean): If true, don't print output csv's, just print
            dataframe

    Returns:
        tuple: if no_print,returns tuple of (csv_file,dataframe).  Otherwise
            file path is returned in a 1-length tuple

    """
    # Only need to keep keys from the returned acquisitions that are important for the csv
    kept_data = keep_specified_keys(data, keep_keys)
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

    csv_file = f'/tmp/{prefix}_{proj_label}.csv'
    if no_print:
        return (csv_file, data_df)
    data_df.to_csv(csv_file, index_label=False, index=False)
    return (csv_file,)


def keep_specified_keys(data, keep_keys):
    kept_data = []
    for datum in data:
        #        print(keep_keys)
        kept_data.append({
            (key if type(key) is str else '.'.join(key)):
                (nested_get(datum, [key]) if type(key) is str else nested_get(datum, key))
            for key in keep_keys
        })
    return kept_data


def read_from_csv(acq_df, subj_df, ses_df, project, dry_run=False):
    context = flywheel_gear_toolkit.GearToolkitContext()
    fw = context.client
    # TODO: Need to do some validation to make sure the CSV file is in the correct format
    #   this should be at the row level, otherwise if they put columns in wrong, it may really
    #   mess up their whole project
    # Subjects and Sessions
    move_and_delete_subjects(subj_df, ses_df, project, fw, dry_run)
    handle_acquisitions(acq_df, fw, dry_run)


def handle_acquisitions(acq_df, fw, dry_run=False):
    # Acquisitions
    for index, row in acq_df.iterrows():
        acquisition = fw.get_acquisition(row['id'])
        if row.get('new_acquisition_label'):
            if dry_run:
                log.info(f"NOT updating acquisition label from {acquisition.label} to {row['new_acquisition_label']}")
            else:
                log.info(f"updating acquisition label from {acquisition.label} to {row['new_acquisition_label']}")
                acquisition.update({'label': row['new_acquisition_label']})

        for file in acquisition.files:
            to_update = {
                'BIDS': {}
            }
            if row.get('modality'): to_update['BIDS']['Modality'] = row['modality']
            if row.get('task'): to_update['BIDS']['Task'] = row['task']
            if row.get('run'): to_update['BIDS']['Run'] = row['run']
            if row.get('ignore'): to_update['BIDS']['Ignore'] = row['ignore']
            # Only update file information if there is any new information
            if not to_update.get('BIDS'):
                continue
            to_update_data = InfoUpdateInput(set=to_update)
            if dry_run:
                log.info(f'NOT updating file information for {file.label}')
            else:
                log.info(f'updating file information for {file.label}')
                resp = fw.modify_acquisition_file_info(acquisition.id, file.name, to_update_data)


def move_and_delete_subjects(subj_df, ses_df, project, fw, dry_run=False):
    unique_subjs = pd.unique(subj_df['new_subject_label'])
    for unique_subj in unique_subjs:
        # dataframe of subjects that are supposed to be sessions
        subjects = subj_df[subj_df['new_subject_label'] == unique_subj]
        for subject in subjects.iterrows():
            # If subject doesn't exist, update this subject to have the new label and code
            # otherwise, update sessions below it to point to this
            existing_subj = project.subjects.find_first(f'label={unique_subj}')
            new_subj = fw.get_subject(subject['id'])
            if not existing_subj:
                if dry_run:
                    log.info(f'NOT updating subject {new_subj} with new label, code of {unique_subj}')
                else:
                    log.info(f'updating subject {new_subj} with new label, code of {unique_subj}')
                    new_subj.update({
                        'label': unique_subj,
                        'code': unique_subj
                    })
            else:
                for session in new_subj.sessions.iter():
                    to_update = {
                        'subject': new_subj,
                    }
                    if ses_df[ses_df['id'] == session.id]['new_session_label']:
                        to_update['label'] = ses_df[ses_df['id'] == session.id]['new_session_label']
                    if dry_run:
                        log.info(f'NOT moving session {session.label} to subject {new_subj.label}')
                    else:
                        if delete_empty_subject(new_subj.id, dry_run):
                            log.info('Subjects deleted')
                        else:
                            log.info('Subjects not deleted.  Check Subjects empty. Exiting')
                            sys.exit(1)

                        log.info(f'moving session {session.label} to subject {new_subj.label}')
                        session.update(to_update)
