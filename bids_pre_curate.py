
import flywheel
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.deep_dict import nested_get
import logging
import pandas as pd

log = logging.getLogger(__name__)

def build_csv(group,proj_name):
    log.debug(f'Starting client connection')
    fw = flywheel.Client()

    project = fw.projects.find_one(f'group={group},label={proj_name}')
    log.info(f'Building CSV for {project.label}')
    proj_label = make_file_name_safe(project.label)
    sessions = fw.get_project_sessions(project.id)

    id_remap = {'_id': 'id'}

    #Acquisitions
    # Only keep the following keys when getting project acquisitions
    keep_keys_acq = ['_id', 'label']# Can be expanded later
    acquisitions = [{key: acq[key] for key in keep_keys_acq} for acq in fw.get_project_acquisitions(project.id)]
    acq_df = pd.DataFrame(acquisitions)
    # Rename _id to id
    acq_df.rename(columns=id_remap)
    acq_df = acq_df.reindex(columns=acq_df.columns.tolist() + ['modality', 'task', 'run', 'ignore'])
    acq_df = acq_df.drop_duplicates(subset=['label'])
    acq_csv = f'/tmp/acquisition_labels_{proj_label}.csv'
    acq_df.to_csv(acq_csv)

    # Subjects
    keep_keys_subj = ['_id', 'code']
    subjects = [{key: subj[key] for key in keep_keys_subj} for subj in fw.get_project_subjects(project.id)]
    subj_df = pd.DataFrame(subjects)
    # Rename _id to id
    subj_df.columns = ['id','existing_subj_label']
    subj_df['new_subject_labels'] = ''
    subj_csv = f'/tmp/subject_codes_{proj_label}.csv'
    subj_df.to_csv(subj_csv)

    #Sessions
    keep_keys_ses = ['_id', 'label',['subject','label']]
    sessions = [
        {(key if type(key) is str else '_'.join(key)):
            (nested_get(ses,key) if type(key) is list else nested_get(ses,[key]))
            for key in keep_keys_ses } for ses in fw.get_project_sessions(project.id)
    ]
    ses_df = pd.DataFrame(sessions)
    # Rename _id to id
    ses_df.columns = ['id','existing_session_label','subject_label']
    ses_df['new_session_labels'] = ''
    ses_csv = f'/tmp/session_labels_{proj_label}.csv'
    subj_df = pd.DataFrame(subjects)
    # Rename _id to id
    subj_df.columns = ['id','existing_subj_label']
    subj_df['new_subject_labels'] = ''
    subj_csv = f'/tmp/subject_codes_{proj_label}.csv'
    subj_df.to_csv(subj_csv)







