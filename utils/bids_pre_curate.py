import logging
import pprint
import re
import sys

import flywheel_gear_toolkit
import pandas as pd
from flywheel.models.info_update_input import InfoUpdateInput

from utils.deep_dict import nested_get
from utils.delete_empty import delete_empty_subject
from utils.fly.make_file_name_safe import make_file_name_safe

log = logging.getLogger(__name__)


def build_csv(acqs, subs, sess, proj_label,suggest=True,allows='_-'):
    """Wrapper for building CSVs for project

        Subjects, sessions and acquisitions are passed in in the form of lists of
        dicts.  They are then passed to data2csv with options set to be converted
        to csv format.
    Args:
        acqs (list):  list of dicts containing acquisitions for the project.
        subs (list):  list of dicts containing subjects for the project.
        sess (list):  list of dicts containing sessions for the project
        proj_label (str):  project name (label)
        suggest (bool): Whether or not to suggest a new label by removing spaces and special characters

    Returns:
        file_names (tuple): Tuple of filenames (full filepath) for all three csv files
    """
    log.info(f'Starting client connection')

    # Compile the user given regex.  Hyphen needs to not be between characters
    #   otherwise it will be taken as a range, we need it to be taken literally
    #   so we add it at the end if it is in the allows string.
    # if the replacement is not a string or not safe, set replace_str to x
    regex = r"[^A-Za-z0-9"
    hyphen_in = '-' in allows
    for char in allows:
        if hyphen_in and char == '-':
            continue
        regex += char
    regex += r"-]+" if hyphen_in else r"]+"
    try:
        safe_patt = re.compile(regex)
    except re.error:
        sys.exit(1)
    log.info(f"Regex to use: {regex}")
    # proj_label = make_file_name_safe(proj_label)
    log.info(f'Building CSV for {proj_label}')

    # Acquisitions
    log.info('Building acquisitions CSV...')
    acq_file = data2csv(acqs, proj_label,
                        keep_keys=['label'],
                        prefix='acquisition_labels',
                        regex=safe_patt,
                        column_rename=['existing_acquisition_label'],
                        user_columns=['new_acquisition_label', 'modality', 'task', 'run', 'ignore'],
                        unique=['label'],
                        old_new_index=[0,1],
                        suggest=suggest)

    # Sessions
    log.info('Building session CSV...')
    sess_file = data2csv(sess, proj_label,
                         keep_keys=['label'],
                         prefix='session_labels',
                         regex=safe_patt,
                         column_rename=['existing_session_label'],
                         user_columns=['new_session_label'],
                         unique=['label'],
                         old_new_index=[0,1],
                         suggest=suggest)

    # Subjects
    log.info('Building subject CSV...')
    sub_file = data2csv(subs, proj_label,
                        keep_keys=['id', 'label'],
                        prefix='subject_codes',
                        regex=safe_patt,
                        column_rename=['id', 'existing_subject_label'],
                        user_columns=['new_subject_label'],
                        old_new_index=[1,2],
                        suggest=suggest)
    file_names = (acq_file[0], sess_file[0], sub_file[0])
    return file_names


def data2csv(data, proj_label, keep_keys, prefix, regex, column_rename=[], user_columns=[],
             unique=[], old_new_index=[0, 1], suggest=True,no_print=False):
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
        regex (compiled regex): Characters to allow in filename, passed into
            make_file_name_safe
        column_rename (list, optional): optional list of column titles in
            the same order as keep_keys to be displayed on the CSV.
        user_columns (list, optional): optional list of column titles
            to add to the csv
        unique (list,optional): If specified, find unique entries on the
            given indices.
        old_new_index (list): Mapping for columns of the existig to new names,
            ex. if the columns of a df are ['existing_session_label',
                'new_session_label','custom_data_1'], then
            old_new_index would be [0,1] since it maps column 0 to column 1.
        suggest (boolean): whether or not to suggest new name by removing spaces
            and special characters
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
        data_df.drop_duplicates(subset=unique, inplace=True)
    # Rename _id to id
    if column_rename:
        # Assuming the user can't modify this, we don't need to catch this error
        #      if len(column_rename) != len(keep_keys)
        #          log.error(f'column_rename ({column_rename}) must be same length as keep_keys ({keep_keys}). Exiting')
        #          os.sys.exit(1)
        data_df.columns = column_rename

    if user_columns:
        data_df = data_df.reindex(columns=data_df.columns.tolist() + user_columns)
    if suggest:
        data_df.iloc[:, old_new_index[1]] = data_df.apply(
            lambda row: suggest_new_name(row[old_new_index[0]],regex), axis=1)
    csv_file = f'/tmp/{prefix}_{proj_label}.csv'
    if no_print:
        return (csv_file, data_df)
    data_df.to_csv(csv_file, index_label=False, index=False)
    return (csv_file,)


def suggest_new_name(existing_label,regex):
    if make_file_name_safe(existing_label, regex, '') != existing_label:
        return make_file_name_safe(existing_label, regex, '')
    else:
        return ''




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
    acq_df.fillna('',inplace=True)
    ses_df.fillna('',inplace=True)
    subj_df.fillna('',inplace=True)
    handle_acquisitions(acq_df, fw, project, dry_run)
    handle_sessions(ses_df, fw, project, dry_run)
    handle_subjects(subj_df, fw, project, dry_run)


def handle_acquisitions(acq_df, fw, project, dry_run=False):
    # Acquisitions
    for index, row in acq_df.iterrows():
        # Since len(rows) != len(project.acquisitions), need to find all acquisitions
        #   in the project for each row in the acquisition dataframe.
        #If names are numeric, the value has to be wrapped in double quotes
        find_string = 'parents.project='+project.id+',label="' \
            +row['existing_acquisition_label']+'"'
        acquisitions_for_row = fw.acquisitions.find(find_string)
        # print(row['existing_acquisition_label'],len(acquisitions_for_row))

        for acquisition in acquisitions_for_row:

            # If acquisition name should change
            if row.get('new_acquisition_label'):
                new_acq_name = row['new_acquisition_label']
            else:
                new_acq_name = row['existing_acquisition_label']
            # Warn for bad labels
            if make_file_name_safe(row['new_acquisition_label'], '') != row['new_acquisition_label']:
                log.warning(f"New acquisition label f{row['new_acquisition_label']} may not be BIDS compliant")

            if row.get('ignore') and str(row['ignore']).lower() in ['true', 'yes']:
                new_acq_name += '_ignore-BIDS'

            if new_acq_name == row['existing_acquisition_label']:
                log.info(f"Acquisition {row['existing_acquisition_label']} did not change, not updating")

            else:
                if dry_run:
                    log.info(f"Dry Run: NOT updating acquisition label from {acquisition.label} to {new_acq_name}")
                else:
                    log.info(f"updating acquisition label from {acquisition.label} to {new_acq_name}")
                    acquisition.update({'label': new_acq_name})



def handle_sessions(ses_df, fw, project, dry_run=False):
    # Sessions
    for index, row in ses_df.iterrows():
        # Since len(rows) != len(project.sessions), need to find all sessions
        #   in the project for each row in the session dataframe.
        find_string = 'parents.project='+project.id+',label="' \
            +row['existing_session_label']+'"'
        sessions_for_row = fw.sessions.find(find_string)
        for session in sessions_for_row:
            # If session name should change
            if row.get('new_session_label'):
                new_ses_name = row['new_session_label']
            else:
                new_ses_name = row['existing_session_label']

            # Warn for bad labels
            if row['new_session_label'] != make_file_name_safe(row['new_session_label'], ''):
                log.warning(f"New session label f{row['new_session_label']} may not be BIDS compliant")

            if row['existing_session_label'] == new_ses_name:
                log.info(f"Session {row['existing_session_label']} did not change, not updating")
            else:
                if dry_run:
                    log.info(f"Dry Run: NOT updating session label from {session.label} to {new_ses_name}")
                else:
                    log.info(f"updating session label from {session.label} to {new_ses_name}")
                    session.update({'label': new_ses_name})


def handle_subjects(subj_df, fw, project, dry_run=False):
    subj_df.loc[subj_df['new_subject_label'] == '', 'new_subject_label'] = subj_df['existing_subject_label']
    # new_subject_label column should be all unique subjects
    unique_subjs = pd.unique(subj_df['new_subject_label'])
    for unique_subj in unique_subjs:
        if make_file_name_safe(unique_subj, '') != unique_subj:
            log.warning(f"Subject label f{unique_subj} may not be BIDS compliant")
        existing_subj = project.subjects.find_first(f'label="{unique_subj}"')
        # Iterate over existing subjects that are supposed to have the same new_subject_label
        #   These are sessions that were misnamed and entered as subjects.
        #   All of these *subjects*  need to be converted to sessions under the new_subject_label subject
        subjects_to_be_moved = subj_df[subj_df['new_subject_label'] == unique_subj]
        for index, subject_to_be_moved in subjects_to_be_moved.iterrows():
            # If label is the same, we can skip.
            if subject_to_be_moved['new_subject_label'] == subject_to_be_moved['existing_subject_label']:
                continue
            # If subject doesn't exist, update this subject to have the new label and code
            # otherwise, update sessions below it to point to this
            new_subj = fw.get_subject(subject_to_be_moved['id'])
            if not existing_subj:
                if dry_run:
                    log.info(f'Dry Run: NOT updating subject {new_subj.label} with new label, code of {unique_subj}')
                else:
                    log.info(f'updating new subject {new_subj.label} with new label, code of {unique_subj}')
                    new_subj.update({
                        'label': unique_subj,
                        'code': unique_subj
                    })
                # Update existing subject
                existing_subj = new_subj
            else:
                for session in new_subj.sessions.iter():
                    existing_session = existing_subj.sessions.find_first(
                            f'label={session.label}'
                    )
                    # Check for a session with the same name in the destination
                    # this would cause a 409 error if we try to update the
                    # parent session, and lead to FLYW-8972
                    if existing_session:
                        log.warning(
                            f'Refusing to move session {session.label} as it '
                            f'would duplicate a session in {existing_subj.label}'
                        )
                        continue
                    # Change all sessions to point to the existing subject
                    to_update = {
                        'subject': {
                            '_id': existing_subj.id
                        }
                    }

                    if dry_run:
                        # Originally had '...to subject {existing_subj.label}' but this hasn't been updated yet
                        #   Locally, the two options are to cal fw.reload(), or use the name it was updated to
                        #   Since the latter is much more efficient, that's what I'll do.
                        log.info(f'Dry Run: NOT moving session {session.label} to subject {unique_subj}')
                    else:
                        log.info(f'moving session {session.label} to subject {unique_subj}')
                        session.update(to_update)

                # Once all sessions have been moved, delete this subject
                if delete_empty_subject(new_subj.id, dry_run, fw):
                    if dry_run:
                        log.info(f'Dry Run: NOT deleting Subject {new_subj.label}.')
                    else:
                        log.info(f'Subject {new_subj.label} deleted')
                else:
                    log.info(f'Subject {new_subj.label} NOT deleted.  Check to make sure it is empty. Exiting')
                    sys.exit(1)
