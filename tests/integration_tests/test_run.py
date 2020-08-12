#!/usr/bin/env python3
"""
"""

import json
import logging
import os
import shutil
import sys
from pathlib import Path
from pprint import pprint
import pytest

sys.path.append(str(Path(__file__).parents[2].resolve()))

import flywheel_gear_toolkit
import pandas as pd

import run
import utils.bids_pre_curate










@pytest.fixture
def gtk_context():
    return flywheel_gear_toolkit.GearToolkitContext()

class TestWetRun:
    def test_wet_run(self, gtk_context):
        acq = gtk_context.get_input_path('acquisition_table')
        ses = gtk_context.get_input_path('session_table')
        sub = gtk_context.get_input_path('subject_table')
        if acq and ses and sub:
            # All inputs provided, there should be no outputs
            run.main(gtk_context)
            outdir = Path(gtk_context.output_dir)
            assert len(os.listdir(outdir)) == 0
        elif not (acq or ses or sub):
            # No inputs provided, there should be three outputs
            run.main(gtk_context)
            outdir = Path(gtk_context.output_dir)
            outfiles = os.listdir(outdir)
            assert len(outfiles) == 3
        else:
            # Raise system exit when not all three or none are provided
            with pytest.raises(SystemExit):
                run.main(gtk_context)
                assert True

#        if gtk_context.config:

if __name__ == '__main__':
    gtk_context = flywheel_gear_toolkit.GearToolkitContext()
    run.main(gtk_context)