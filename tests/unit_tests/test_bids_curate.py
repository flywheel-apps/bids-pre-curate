from utils.bids_pre_curate import data2csv
from utils.deep_dict import nested_get
from utils.bids_pre_curate import keep_specified_keys
from tests.BIDS_popup_curation.acquisitions import acquistions_object
from tests.BIDS_popup_curation.sessions import session_object
import flywheel
import pandas as pd
import numpy as np

test_data = [{'age': None,
         'analyses': None,
         'code': 'sub-13',
         'cohort': None,
         'created': '',
         'ethnicity': None,
         'files': [],
         'firstname': None,
         '_id': '5db0845e69d4f3002d16ee05',
         'info': {},
         'info_exists': False,
         'label': 'sub-13',
         'lastname': None,
         'master_code': None,
         'modified': '',
         'notes': [],
         'parents': {'acquisition': None,
                     'analysis': None,
                     'group': 'scien',
                     'project': '5db0759469d4f3001f16e9c1',
                     'session': {
                         'session_no': 1,
                         'session_info': None
                     },
                     'subject': None},
         'permissions': {
             'perm-01': 'nate-has-access'
         },
         'project': '5db0759469d4f3001f16e9c1',
         'race': None,
         'revision': 17,
         'sex': None,
         'species': None,
         'strain': None,
         'tags': [],
         'type': None},
        {'age': None,
         'analyses': None,
         'code': 'sub-14',
         'cohort': None,
         'created': '',
         'ethnicity': None,
         'files': [],
         'firstname': None,
         '_id': '5db0845e69d4f3002d16ee05',
         'info': {},
         'info_exists': False,
         'label': 'sub-14',
         'lastname': 'hello',
         'master_code': None,
         'modified': '',
         'notes': [],
         'parents': {'acquisition': None,
                     'analysis': None,
                     'group': 'Nate',
                     'project': '5db0759469d4f3001f16e9c1',
                     'session': {
                         'session_no': None,
                         'session_info': None
                     },
                     'subject': None},
         'permissions': {},
         'project': '5db0759469d4f3001f16e9c1',
         'race': None,
         'revision': 17,
         'sex': None,
         'species': None,
         'strain': None,
         'tags': [],
         'type': None}]




def test_data2csv_dummy_data():

    proj_label = 'test_proj'
    keep_keys = [['label'],
                [['parents', 'group'], 'label'],
                [['parents', 'subject'], 'label']]
    column_renames = [['existing_acquisition_label'],
                    ['subject_group', 'existing_session_label'],
                    ['subject_label', 'existing_session_label']]
    prefixes = ['acq','sub','sess']
    user_columns = [[],['test'],['test1','test2']]
    for keep_key, column_rename, prefix, user_column in zip(keep_keys,column_renames, prefixes, user_columns):
        path,df = data2csv(test_data,proj_label,keep_key,prefix, column_rename,user_column, no_print=True)
        print(path)
        print(df)
        print('\n')

def test_data2csv_acq_duplicate(group='scien',project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    acqs = [acq.to_dict() for acq in fw.get_project_acquisitions(proj.id)]
    path,df = data2csv(acqs, project,
                        keep_keys=['label'],
                        prefix='acquisition_labels',
                        column_rename=['existing_acquisition_label'],
                        user_columns=['new_acquisition_label', 'modality', 'task', 'run', 'ignore'],
                        unique=['label'],no_print=True)
    supposedly_unique = np.sort(df['existing_acquisition_label'].values)
    unique = np.unique(pd.DataFrame.from_records(acquistions_object)['label'].values)
    comparison = unique == supposedly_unique
    assert comparison.all()
    assert (df.columns == ['existing_acquisition_label','new_acquisition_label', 'modality', 'task', 'run', 'ignore']).all()


def test_data2csv_ses_duplicate(group='scien',project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    sess = [ses.to_dict() for ses in fw.get_project_sessions(proj.id)]
    path, df = data2csv(sess, project,
                         keep_keys=['label'],
                         prefix='session_labels',
                         column_rename=['existing_session_label'],
                         user_columns=['new_session_label'],
                         unique=['label'],no_print=True)

    supposedly_unique = np.sort(df['existing_session_label'].values)
    unique = np.unique(pd.DataFrame.from_records(session_object)['label'].values)
    comparison = unique == supposedly_unique
    assert comparison.all()
    assert (df.columns == ['existing_session_label', 'new_session_label']).all()


def test_nested_get():
    lvl1 = {
        'test':'data'
    }
    lvl2 = {
        'test': {
            'test': 'data'
        }
    }
    lvl3 = {
        'test': {
            'test': {
                'test': 'data'
            }
        }
    }

    dicts = [lvl1,lvl2,lvl3]
    keys = [['test'],['test','test'],['test','test','test']]
    result = 'data'

    for dict,key in zip(dicts,keys):
        val = nested_get(dict,key)
        assert val == result
        print(f'expected: {result}, got: {val}, passed')

def test_keep_specified_keys():
    keep_keys = [['_id', 'label','lastname'],
                 ['_id', ['parents', 'group'], 'label'],
                 ['_id', ['permissions','perm-01'], 'label'],
                 [['parents','subject'],['parents','session','session_no'],
                    ['parents','session','session_info']]]
    expected = [[{'_id': '5db0845e69d4f3002d16ee05', 'label': 'sub-13', 'lastname': None},
                 {'_id': '5db0845e69d4f3002d16ee05', 'label': 'sub-14', 'lastname': 'hello'}],
                [{'_id': '5db0845e69d4f3002d16ee05', 'parents.group': 'scien', 'label': 'sub-13'},
                 {'_id': '5db0845e69d4f3002d16ee05', 'parents.group': 'Nate', 'label': 'sub-14'}],
                [{'_id': '5db0845e69d4f3002d16ee05', 'permissions.perm-01': 'nate-has-access', 'label': 'sub-13'},
                 {'_id': '5db0845e69d4f3002d16ee05', 'permissions.perm-01': None, 'label': 'sub-14'}],
                [{'parents.subject': None, 'parents.session.session_no': 1,
                    'parents.session.session_info': None},
                 {'parents.subject': None, 'parents.session.session_no': None,
                    'parents.session.session_info': None}]]

    for keys, expected in zip(keep_keys, expected):
        kept = keep_specified_keys(test_data, keys)
        for kept_dict,exp in zip(kept,expected):
            assert type(kept_dict) is dict
            assert kept_dict == exp


#def test_keep_specified_keys():
#   ['']

def run():
    test_data2csv_dummy_data()
    test_data2csv_acq_duplicate()
    test_nested_get()

    test_keep_specified_keys()

    test_data2csv_ses_duplicate()

if __name__ == '__main__':
    run()

