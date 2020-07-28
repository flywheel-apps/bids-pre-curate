#!/usr/bin/env python3
"""
"""

import os
from pathlib import Path
import shutil
import logging
import json
from pprint import pprint

import flywheel_gear_toolkit
import pandas as pd


import run
import utils.bids_pre_curate

gtk_context = flywheel_gear_toolkit.GearToolkitContext()
gtk_context.init_logging()

log = gtk_context.log
log.info('Test')

project = gtk_context.client.lookup('scien/Nate-BIDS-pre-curate')
inputs = run.validate_inputs(gtk_context)
log.info('Validated inputs')

acq_df = pd.read_csv(inputs[0]).fillna('')
ses_df = pd.read_csv(inputs[1]).fillna('')
sub_df = pd.read_csv(inputs[2]).fillna('')


log.info('Finished loading data')
#print(acq_df)
#print(ses_df)
#print(sub_df)


def test():
    #test_bids_curate.run()
    utils.bids_pre_curate.handle_acquisitions(acq_df,gtk_context.client,dry_run=True)
    log.info('Finished handle_acquisitions')
    utils.bids_pre_curate.move_and_delete_subjects(sub_df,ses_df,project,gtk_context.client,dry_run=True)
    log.info('Finished move_and_delete_subjects')
    utils.bids_pre_curate.read_from_csv(acq_df,sub_df,ses_df,project)
    log.info('Finished read_from_csv')
test()


