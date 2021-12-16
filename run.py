#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""

import os
import pprint
import shutil
import sys

import flywheel_gear_toolkit
import pandas as pd
from flywheel.rest import ApiException

from utils import bids_pre_curate
from utils.bids.run_level import get_run_level_and_hierarchy


def parse_config(context):
    conf_dict = {}
    config = context.config
    conf_dict['dry_run'] = config.get('dry_run', False)
    conf_dict['suggest'] = config.get('suggest',True)
    conf_dict['allows'] = config.get('allows','_-')


    return conf_dict


def validate_inputs(context):
    acq = context.get_input_path('acquisition_table')
    ses = context.get_input_path('session_table')
    sub = context.get_input_path('subject_table')

    if acq and ses and sub:
        return (acq, ses, sub)
    elif not (acq or ses or sub):
        return ()
    else:
        context.log.error('None or all inputs must be provided. Exiting')
        sys.exit(1)


def main(gtk_context):
    log = gtk_context.log
    dest = gtk_context.client.get_analysis(gtk_context.destination['id'])
    run_level = dest.parent['type']
    if run_level not in ['project', 'subject']:
        raise RuntimeError(
            'Cannot run at %s level, please run at'
            ' subject or project level', run_level
        )
    hierarchy = dest.parents
    if hierarchy['group'] and hierarchy['project']:
        group = hierarchy['group']
        project = hierarchy['project']
    else:
        log.exception('Unable to determine run level and hierarchy, exiting')
        sys.exit(1)
        #group = 'scien'
        #project_label = 'Nate-BIDS-pre-curate'

    msg = 'a single subject' if run_level == 'subject' else 'the whole project'
    log.info(f"Running on {msg}")

    config = parse_config(gtk_context)
    inputs = validate_inputs(gtk_context)

    project = gtk_context.client.get_project(hierarchy['project'])
    log.info(f'Found project {group}/{project.label}')
    if inputs:
        # Make the id column the index for the dataframe
        acq_df = pd.read_csv(inputs[0], dtype=str)
        ses_df = pd.read_csv(inputs[1], dtype=str)
        sub_df = pd.read_csv(inputs[2], dtype=str)
        bids_pre_curate.read_from_csv(
            acq_df,
            sub_df,
            ses_df,
            run_level,
            hierarchy,
            config['dry_run'],
        )
    else:
        fw = gtk_context.client
        acqs = [acq.to_dict() for acq in fw.get_project_acquisitions(project.id)]
        sess = [ses.to_dict() for ses in fw.get_project_sessions(project.id)]
        subs = [sub.to_dict() for sub in fw.get_project_subjects(project.id)]

        file_names = bids_pre_curate.build_csv(acqs, subs, sess, project.label,
                                               suggest=config['suggest'],
                                               allows=config['allows'])
        if not os.path.exists(gtk_context.output_dir):
            try:
                os.mkdir(gtk_context.output_dir)
            except FileNotFoundError as e:
                gtk_context.log.error()
                sys.exit(1)
        # Move tmp files to output
        for filename in file_names:
            output = os.path.join(gtk_context.output_dir, os.path.basename(filename))
            shutil.move(filename, output)


if __name__ == "__main__":
    gtk_context = flywheel_gear_toolkit.GearToolkitContext()
    pprint.pprint(os.environ)

    # Setup basic logging and log the configuration for this job
    gtk_context.init_logging()
    gtk_context.log_config()

    main(gtk_context)
    gtk_context.log.info(f'BIDS-pre-curate is done.')

    sys.exit(0)
