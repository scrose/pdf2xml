"""
===========================================
Paths Object Class
===========================================
"""

import os
import glob
import json
import sys
from tqdm import tqdm
import datetime
from enum import Enum

# Phase enumeration constants
class Phases(Enum):
    EXTRACT = 0
    UPDATE = 2
    BUILD = 1


class Parameters:

    def __init__(self):

        # date timestamp
        now = datetime.datetime.now()
        self.datestamp = "{}{}{}".format(now.month, now.day, now.year)
        self.phase = None
        self.empty_nodes = []

        # --------- parse command line input ---------
        if (len(sys.argv) > 2):
            # get resource paths from json file
            if (sys.argv[1] is not None):
                with open(sys.argv[1]) as fp:
                    self.paths = json.load(fp)
                fp.close()
            else:
                print("Path file not specified.")
                exit(1)

            # extraction phase
            if (sys.argv[2] == "-extract"):
                self.phase = Phases.EXTRACT
                self.ext = "*.pdf"
            # xml build phase
            elif (sys.argv[2] == "-update"):
                self.phase = Phases.UPDATE
                self.ext = "*.txt"
            # xml build phase
            elif (sys.argv[2] == "-build"):
                self.phase = Phases.BUILD
                self.ext = "*.json"
                self.outfile = os.path.join(self.paths["output"], "{}_databuild.xml".format(self.datestamp))
            else:
                print("Processing phase is not valid.")
                exit(1)
        else:
            print("Missing arguments.")
            exit(1)

        # option to use existing raw text (.txt) instead of PDF files (.pdf)


    # --------------------------------------
    # Get single file or directory from filename
    def get_path(self, dir, parent_dir=None):
        if parent_dir is None:
            return self.paths[dir]
        else:
            return self.paths[parent_dir][dir]

    # --------------------------------------
    # Get multiple files or directories in
    def get_paths(self, dir, parent_dir=None):
        if parent_dir is None:
            return sorted(glob.glob(os.path.join(self.get_path(dir), self.ext)))
        else:
            return sorted(glob.glob(os.path.join(self.get_path(dir, parent_dir), self.ext)))



# instantiate paths
params = Parameters()
