import flywheel_gear_toolkit
import logging

context = flywheel_gear_toolkit.GearToolkitContext()
fw = context.client

log = logging.getLogger(__name__)

log.info(fw.get_config().site.api_url)


def delete_empty_subject(subject_id, dry_run):
    """Deletes a subject after confirming its empty.

    A subject will be empty if it has no sessions attached to it,
    this function checks whether the given subject has any children
    sessions.  If it doesn't, it deletes the subject and returns
    true, if it does, it returns false and logs a warning

    Args:
        subject_id (str): the subject id

    Returns:
       boolean: whether the subject was deleted or not

    """
    subject = fw.get_subject(subject_id)
    sessions = subject.sessions
    if len(sessions.find()):
        log.warning('Subject not empty: sessions still attached. Not deleting')
        return False
    elif len(subject.files) > 0:
        log.warning('Subject not empty: files still attached.  Not deleting')
        return False
    else:
        fw.delete_subject(subject.id)
        return True
