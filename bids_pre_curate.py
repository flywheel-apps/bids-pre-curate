
import flywheel
import logging
import pandas as pd

log = logging.getLogger(__name__)

def build_csv(group,project,outfiles):
    log.debug(f'Starting client connection')
    fw = flywheel.Client()
    log.info(f'Building CSV for {project.label}')

    project = fw.projects().find_one(f'group={group},label={project}')
    subjects = fw.get_project_subjects(project.id)
    sessions = fw.get_project_sessions(project.id)

    acq_keys = ['id','label','parents.subject','parents.session']
    acquisitions = [{} for acq fw.get_project_acquisitions(project.id)]

    #TODO: Ask if make_file_name_safe is appropriate for this, or if I should write my own
    #   acq renamer
    unique_acqs = set([make_file_name_safe(acq.label) for acq in acquisitions])






