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
        run.main(gtk_context)

#        if gtk_context.config:

if __name__ == '__main__':
    gtk_context = flywheel_gear_toolkit.GearToolkitContext()
    run.main(gtk_context)