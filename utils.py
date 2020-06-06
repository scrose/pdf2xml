#!/usr/bin/env python3x

"""
===========================================
Utilities
===========================================
"""

import os
import glob
import json
import sys
from params import params, Phases


# --------------------------------------
# Extract ID from filename
def get_id(file):
    return os.path.splitext(os.path.basename(file))[0]

# --------------------------------------
# Extract ID from filename
def get_filetype(file):
    return os.path.splitext(os.path.basename(file))[1].replace('.','')


# -- end of Utilities --
