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


inputs = run.validate_inputs(gtk_context)

acq_df = pd.read_csv(inputs[0], index_col=0)
ses_df = pd.read_csv(inputs[1], index_col=0)
sub_df = pd.read_csv(inputs[2], index_col=0)

print(acq_df)
print(ses_df)
print(sub_df)
