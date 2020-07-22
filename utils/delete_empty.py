import flywheel
import logging
fw = flywheel.Client('', root=True)

log = logging.getLogger(__name__)

log.info(fw.get_config().site.api_url)

def delete_empty_acqusition(acquisition, dry_run=False):
    log.info(f'    Checking if acquisition "{acquisition.label}" is empty')
    num_files = len(acquisition.files)
    log.info(f'    Found {num_files} files')
    acquisition_has_no_files = num_files == 0
    if acquisition_has_no_files:
        if dry_run:
            log.info(f'    NOT Deleting acquisition "{acquisition.label}"')
        else:
            log.info(f'    Deleting acquisition "{acquisition.label}"')
            log.info(fw.delete_acquisition(acquisition.id))
    return acquisition_has_no_files

def delete_empty_acqusitions(session, dry_run=False):
    acquisitions = session.acquisitions()
    num_acquisitions = len(acquisitions)
    num_deleted = 0
    log.info(f'Found {num_acquisitions} acquisitions')
    for acquisition in acquisitions:
        if delete_empty_acqusition(acquisition, dry_run):
            num_deleted += 1
    msg = 'Almost ' if dry_run else ""
    log.info(f'{msg}Deleted {num_deleted}/{num_acquisitions} sessions')
    return num_deleted == num_acquisitions

 def delete_empty_session(session, dry_run=False):
    print(f'  Checking if session "{session.label}" is empty')
    num_files = len(session.files)
    print(f'  Found {num_files} files')
    session_has_no_files = num_files == 0
    all_acqusition_empty = delete_empty_acqusitions(session, dry_run)
    session_empty = all_acqusition_empty and session_has_no_files
    if session_empty:
        if dry_run:
            print(f'  NOT Deleting session "{session.label}"')
        else:
            print(f'  Deleting session "{session.label}"')
            print(fw.delete_session(session.id))
    return session_empty

 def delete_empty_sessions(subject, dry_run=False):
    sessions = subject.sessions()
    num_sessions = len(sessions)
    num_deleted = 0
    print(f'Found {num_sessions} sessions')
    for session in sessions:
        if delete_empty_session(session, dry_run):
            num_deleted += 1
    msg = 'Almost ' if dry_run else ""
    print(f'{msg}Deleted {num_deleted}/{num_sessions} sessions')
    return num_deleted == num_sessions

 def delete_empty_subject(subject, dry_run=False):
    print(f'Checking if subject "{subject.label}" is empty')
    num_files = len(subject.files)
    print(f'Found {num_files} files')
    subject_has_no_files = num_files == 0
    all_sessions_empty = delete_empty_sessions(subject, dry_run)
    subject_empty = all_sessions_empty and subject_has_no_files
    if subject_empty:
        if dry_run:
            print(f'NOT Deleting subject "{subject.label}"')
        else:
            print(f'Deleting subject "{subject.label}"')
            print(fw.delete_subject(subject.id))
    return subject_empty

 def delete_empty_subjects(project, dry_run=False):
    print(f'Deleting empty subjects for project "{project.label}"')
    subjects = project.subjects()
    num_subjects = len(subjects)
    num_deleted = 0
    print(f'Found {len(subjects)} subjects')
    for ii, subject in enumerate(subjects):
        print(f'Subject # {ii:3d} ---------------------------------')
        if delete_empty_subject(subject, dry_run):
            num_deleted += 1
    msg = 'Almost ' if dry_run else ""
    print(f'{msg}Deleted {num_deleted}/{num_subjects} subjects')
    return num_deleted == num_subjects