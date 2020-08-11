#!/usr/bin/env python3
"""
"""

import json
import logging
import os
import shutil
from pathlib import Path
from pprint import pprint
import pytest


import flywheel_gear_toolkit
import pandas as pd

import run
import utils.bids_pre_curate






def test():
    #test_bids_curate.run()
    utils.bids_pre_curate.handle_acquisitions(acq_df,gtk_context.client,project,dry_run=True)
    log.info('Finished handle_acquisitions')
    utils.bids_pre_curate.handle_sessions(ses_df, gtk_context.client, project, dry_run=True)
    log.info('Finished handle_sessions')
    utils.bids_pre_curate.handle_subjects(sub_df, gtk_context.client, project, dry_run=True)
    log.info('Finished handle_subjects')

    utils.bids_pre_curate.read_from_csv(acq_df,sub_df,ses_df,project)
    log.info('Finished read_from_csv')
test()



@pytest.fixture
def gtk_context():
    return flywheel_gear_toolkit.GearToolkitContext()

class TestWetRun:
    def test_wet_run(self, gtk_context):
        run.main(gtk_context)

        if gtk_context.config