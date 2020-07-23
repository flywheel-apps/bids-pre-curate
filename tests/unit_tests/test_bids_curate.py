from utils.bids_pre_curate import data2csv
from utils.deep_dict import nested_get
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
                     'session': None,
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


def test_data2csv_normal_data():

    proj_label = 'test_proj'
    keep_keys = [['_id', 'label'],
                ['_id', ['parents', 'group'], 'label'],
                ['_id', ['parents', 'subject'], 'label']]
    column_renames = [['id', 'existing_acquisition_label'],
                    ['id', 'subject_label', 'existing_session_label'],
                    ['id', 'subject_label', 'existing_session_label']]
    prefixes = ['acq','sub','sess']
    user_columns = [[],['test'],['test1','test2']]
    for keep_key, column_rename, prefix, user_column in zip(keep_keys,column_renames, prefixes, user_columns):
        path,df = data2csv(test_data,proj_label,keep_key,prefix, column_rename,user_column, no_print=True)
        print(path)
        print(df)
        print('\n')

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

#def test_keep_specified_keys():
#   ['']
test_nested_get()
test_data2csv_normal_data()

