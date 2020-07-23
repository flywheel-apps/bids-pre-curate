#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""

import sys
import pandas as pd

import flywheel_gear_toolkit
from utils import bids_pre_curate
from utils.bids.run_level import get_run_level_and_hierarchy


def parse_config(context):
    conf_dict = {}
    config = context.config
    if not config:
        return
    if config.sessions_per_subject:
        conf_dict['ses_per_sub'] = config.sessions_per_subject
    else:
        gtk_context.log.error('sessions_per_subject required.  Exiting')
        sys.exit(1)

    if config.infer_bids:
        conf_dict['infer_bids'] = True
    else:
        conf_dict['infer_bids'] = False
    if config.reset_bids_info:
        conf_dict['reset_info'] = True
    else:
        conf_dict['reset_info'] = False
    if config.reset_bids_ignore:
        conf_dict['reset_ignore'] = True
    else:
        conf_dict['reset_ignore'] = False

    return conf_dict


def validate_inputs(context):
    acq = context.get_input_path('acquisition_table')
    ses = context.get_input_path('session_table')
    sub = context.get_input_path('subject_table')

    if acq and ses and sub:
        return (acq, ses, sub)
    elif not (acq and ses and sub):
        return ()
    else:
        context.log.error('None or all inputs must be provided. Exiting')
        sys.exit(1)


def main(gtk_context):
    #    hierarchy = get_run_level_and_hierarchy(
    #        gtk_context.client, gtk_context.destination["id"]
    #    )
    group = "scien"  # hierarchy.group
    project_label = "Nate"  # hierarchy.project_label

    config = parse_config(gtk_context)
    inputs = validate_inputs(gtk_context)

    project = gtk_context.client.lookup(f'{group}/{project_label}')
    if inputs:
        acq_df = pd.read_csv(inputs[0])
        ses_df = pd.read_csv(inputs[1])
        sub_df = pd.read_csv(inputs[2])
        bids_pre_curate.read_from_csv(acq_df, sub_df, ses_df, project)  # ,config.dry_run)
    else:
        fw = gtk_context.client
        acqs = [acq.to_dict() for acq in fw.get_project_acquisitions(project.id)]
        sess = [ses.to_dict() for ses in fw.get_project_sessions(project.id)]
        subs = [sub.to_dict() for sub in fw.get_project_subjects(project.id)]
        bids_pre_curate.build_csv(acqs, subs, sess, project.label)


if __name__ == "__main__":
    gtk_context = flywheel_gear_toolkit.GearToolkitContext()

    # Setup basic logging and log the configuration for this job
    gtk_context.init_logging()
    gtk_context.log_config()

    main(gtk_context)
    gtk_context.log.info(f'BIDS-pre-curate is done.')

    sys.exit(0)
