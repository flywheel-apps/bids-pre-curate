from flywheel.models.session import Session
sess_keys = ['operator', 'label', 'info', 'project', 'uid', 'timestamp',
             'timezone', 'subject', 'age', 'weight', 'id', 'info_exists',
              'created', 'modified', 'revision',
             'group', 'project_has_template', 'satisfies_template',
             'files', 'notes', 'tags', 'analyses']


def subj_to_sess(to_conv,parent):
    sess = {}
    for key in sess_keys:
        if key == 'id':
            sess[key] = to_conv['_id']
        if key in to_conv:
            sess[key] = to_conv[key]
    sess['subject'] = parent
    ses = Session(**sess)
    return ses
