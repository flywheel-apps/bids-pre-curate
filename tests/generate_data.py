import json
import os

import flywheel

fw = flywheel.Client()
group = 'scien'
project_label = 'BIDS-Sample'
json_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proj_data.json')


def gen_project_data():
    project = fw.lookup(f'{group}/{project_label}')

    subjects = [subj.to_dict() for subj in fw.get_project_subjects(project.id)]
    sessions = [ses.to_dict for ses in fw.get_project_sessions(project.id)]
    acquisitions = [acq.to_dict() for acq in fw.get_project_acquisitions(project.id)]

    with open(json_out, 'w') as outfile:
        data = {
            'subjects': subjects,
            'sessions': sessions,
            'acquisitions': acquisitions
        }
        json.dump(data, outfile, default=str)


if __name__ == '__main__':
    gen_project_data()
