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
    data2csv(acqs, proj_label,
             keep_keys=['_id', 'label'],
             prefix='acquisition_labels',
             column_rename=['id', 'label'],
             user_columns=['modality', 'task', 'run', 'ignore'],
             unique=['label'])

    # Sessions
    sess = fw.get_project_sessions(project.id)
    data2csv(sess, proj_label,
             keep_keys=['_id', ['subject', 'label'], 'label'],
             prefix='session_labels',
             column_rename=['id', 'subject_label', 'existing_session_label'],
             user_columns=['new_session_label'])

    # Subjects
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
