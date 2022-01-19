import os
from pathlib import Path

import flywheel
import numpy as np
import pandas as pd
import pytest
import sys
sys.path.append(str(Path(__file__).parents[2].resolve()))
from tests.BIDS_popup_curation.acquisitions import acquistions_object
from tests.BIDS_popup_curation.sessions import session_object
from utils.bids_pre_curate import (data2csv, generalize_find_str,
                                   handle_acquisitions,
                                   handle_sessions, handle_subjects,
                                   keep_specified_keys)
from utils.deep_dict import nested_get

test_data = [
    {
        'code': 'sub-13 test',
        'firstname': None,
        '_id': '5db0845e69d4f3002d16ee05',
        'label': 'sub-13 test',
        'lastname': None,
        'parents': {
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
    },
    {
        'code': 'sub-14',
        'firstname': None,
        '_id': '5db0845e69d4f3002d16ee05',
        'label': 'sub-14',
        'lastname': 'hello',
        'parents': {
            'group': 'Nate',
            'project': '5db0759469d4f3001f16e9c1',
            'session': {
                'session_no': None,
                'session_info': None
            },
            'subject': None
        },
        'permissions': {}
    }
]


def test_data2csv_rename():
    proj_label = 'test_proj'
    keep_keys = ['label']
    column_renames = ['existing_subject_label']
    user_columns = ['new_subject_label']
    remap = [0, 1]
    allows = ['.-_', '._-', '._ -', '', '.', '-', '_']

    expected = [['sub-13test', 'sub-14'],
                ['sub-13 test', 'sub-14'],
                ['sub-13 test', 'sub-14'],
                ['sub13test', 'sub14'],
                ['sub-13test', 'sub-14'],
                ['sub13test', 'sub14']]

    def test_invalid_regex():
        with pytest.raises(SystemExit):
            path, df = data2csv(test_data,
                                proj_label,
                                keep_keys, 'sub', column_renames,
                                user_columns,
                                old_new_index=remap,
                                no_print=True,
                                allows=allows[0])

    def test_valid_regex():
        for allow, exp in zip(allows[1:], expected):
            path, df = data2csv(test_data,
                                proj_label,
                                keep_keys, 'sub', column_renames,
                                user_columns,
                                old_new_index=remap,
                                no_print=True,
                                allows=allow)
            assert df.columns == ['existing_subject_label', 'new_subject_label']
            assert df.iloc[0,1] == expected[0]
            assert df.iloc[1,1] == expected[1]


def test_data2csv_dummy_data():
    proj_label = 'test_proj'
    keep_keys = [['label'],
                 ['label', ['parents', 'group']],
                 ['label', ['parents', 'subject'], 'label']]
    column_renames = [['existing_acquisition_label'],
                      ['existing_session_label', 'subject_group'],
                      ['existing_session_label', 'subject_label']]
    remap = [[0, 1], [0, 2], [0, 2]]
    prefixes = ['acq', 'sub', 'sess']
    user_columns = [['new_session_label'], ['new_session_label'], ['new_session_label', 'test2']]
    for keep_key, column_rename, prefix, user_column, remap in zip(keep_keys, column_renames, prefixes, user_columns,
                                                                   remap):
        path, df = data2csv(test_data, proj_label, keep_key, prefix, '[^A-Za-z0-9]', column_rename, user_column, old_new_index=remap,
                            no_print=True)
        assert (df.columns == [*column_rename, *user_column]).all()
        assert df['new_session_label'][0] == 'sub13test'
        assert df['new_session_label'][1] == 'sub14'


def test_data2csv_acq_duplicate(group='scien', project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    acqs = [acq.to_dict() for acq in fw.get_project_acquisitions(proj.id)]
    path, df = data2csv(acqs, project,
                        keep_keys=['label'],
                        prefix='acquisition_labels',
                        regex='[^A-Za-z0-9]',
                        column_rename=['existing_acquisition_label'],
                        user_columns=['new_acquisition_label', 'modality', 'task', 'run', 'ignore'],
                        unique=['label'], no_print=True)
    supposedly_unique = np.sort(df['existing_acquisition_label'].values)
    unique = np.unique(pd.DataFrame.from_records(acquistions_object)['label'].values)
  #  assert unique.shape == supposedly_unique.shape
    assert (df.columns == ['existing_acquisition_label', 'new_acquisition_label', 'modality', 'task', 'run',
                           'ignore']).all()


def test_data2csv_ses_duplicate(group='scien', project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    sess = [ses.to_dict() for ses in fw.get_project_sessions(proj.id)]
    path, df = data2csv(sess, project,
                        keep_keys=['label'],
                        prefix='session_labels',
                        regex='[^A-Za-z0-9]',
                        column_rename=['existing_session_label'],
                        user_columns=['new_session_label'],
                        unique=['label'], no_print=True)
    print(df.values)
    supposedly_unique = df.index.values
    unique = np.unique(pd.DataFrame.from_records(session_object)['label'].values)
    #assert set(unique) == set(supposedly_unique)
    assert (set(df.columns) == set(['existing_session_label', 'new_session_label']))

@pytest.mark.parametrize('mock_str, expected_outcome',
                         [('elmtree','elmtree'),
                          ('34-elmtree', 'elmtree'),
                          ('70 elmtree', 'elmtree'),
                          ('-- tigger', 'tigger'),
                          ('.tigger', 'tigger'),
                          ('12345', '12345')
                         ])
def test_generalize_find_str(mock_str, expected_outcome):
    test_str = generalize_find_str(mock_str)
    assert test_str == expected_outcome

def test_nested_get():
    lvl1 = {
        'test': 'data'
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

    dicts = [lvl1, lvl2, lvl3]
    keys = [['test'], ['test', 'test'], ['test', 'test', 'test']]
    result = 'data'

    for dict, key in zip(dicts, keys):
        val = nested_get(dict, key)
        assert val == result
        print(f'expected: {result}, got: {val}, passed')


def test_keep_specified_keys():
    keep_keys = [['_id', 'label', 'lastname'],
                 ['_id', ['parents', 'group'], 'label'],
                 ['_id', ['permissions', 'perm-01'], 'label'],
                 [['parents', 'subject'], ['parents', 'session', 'session_no'],
                  ['parents', 'session', 'session_info'], 'label']]
    expected = [['_id', 'label', 'lastname'],
                ['_id', 'parents.group', 'label'],
                ['_id', 'permissions.perm-01', 'label'],
                ['parents.subject', 'parents.session.session_no',
                 'parents.session.session_info', 'label']]

    for keys, exp in zip(keep_keys, expected):
        kept = keep_specified_keys(test_data, keys)
        for kept_dict in kept:
            print(kept_dict)
            print(exp)
            assert type(kept_dict) is dict
            assert set(kept_dict.keys()) == set(exp)
            if 'parents.session.session_info' in kept_dict:
                assert kept_dict['parents.session.session_info'] == None


def test_handle_acquisitions_no_changes(group='scien', project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    path = Path(__file__).parents[1] / 'assets/project/acquisition_labels_Nate-BIDS-pre-curate.csv'
    acq_df = pd.read_csv(path.resolve())
    handle_acquisitions(acq_df, fw, proj, dry_run=True)
    # This test only checks for errors, so if we get here, we can assert True
    # Integration testing checks for functionality
    assert True


def test_handle_sessions_no_changes(group='scien', project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    path = Path(__file__).parents[1] / 'assets/project/session_labels_Nate-BIDS-pre-curate.csv'
    ses_df = pd.read_csv(path.resolve())
    handle_sessions(ses_df, fw, proj, dry_run=True)
    # This test only checks for errors, so if we get here, we can assert True
    # Integration testing checks for functionality
    assert True


def test_handle_subjects_no_changes(group='scien', project='Nate-BIDS-pre-curate'):
    fw = flywheel.Client()
    proj = fw.lookup(f'{group}/{project}')
    path = Path(__file__).parents[1] / 'assets/project/subject_codes_Nate-BIDS-pre-curate.csv'
    sub_df = pd.read_csv(path.resolve())
    with pytest.raises(flywheel.rest.ApiException) as api_info:
        handle_subjects(sub_df, fw, proj, dry_run=True)
        # This test only checks for errors, so if we get here, we can assert True
        # Integration testing checks for functionality
        # Subject id is stale so it won't find
        assert "not found" in api_info


# def test_keep_specified_keys():
#   ['']

def run():
    test_data2csv_dummy_data()
    test_data2csv_acq_duplicate()
    test_nested_get()

    test_keep_specified_keys()

    test_data2csv_ses_duplicate()
    test_handle_acquisitions_no_changes()
    test_handle_sessions_no_changes()
    test_handle_subjects_no_changes()


if __name__ == '__main__':
    run()
