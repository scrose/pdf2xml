"""
===========================================
Parameters Object Class
===========================================
"""

import os
import glob
import json
import sys
import datetime
import utils
from enum import Enum


# Phase enumeration constants
class Phases(Enum):
    EXTRACT = 0
    UPDATE = 2
    BUILD = 1


# XML Schema enumeration constants
class Schema(Enum):
    BITS = 0
    DATACITE = 1
    WORDPRESS = 2


class Parameters:

    def __init__(self):

        # date timestamp
        now = datetime.datetime.now()
        self.datestamp = "{}{}{}".format(now.year, now.month, now.day)
        # Timestamp FORMAT: YYYY-MM-DD HH:MM:SS
        self.postdate = "{}-{:02d}-{:02d} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute,
                                                           now.second)
        # Timestamp FORMAT: Mon, 20 May 2019 05:50:45 +0000
        self.timestamp = now.strftime("%a, %d %b %Y %H:%M:%S %z")
        self.phase = None
        self.schema = None
        self.empty_nodes = ['self-uri']
        self.element_name = 'element'

        try:

            # --------- parse command line input ---------
            if len(sys.argv) > 2:
                # get resource paths from json file
                if sys.argv[1]:
                    with open(sys.argv[1]) as fp:
                        print('Parsing paths file:', sys.argv[1])
                        self.paths = json.load(fp)
                        # load base settings file
                        self.base = utils.load_json(self.get_path('base', 'metadata'))
                    # create directories for output files if does not exist
                    if not os.path.isdir(self.paths['metadata']['articles']):
                        os.mkdir(self.paths['metadata']['articles'])
                    for path in self.paths['output'].values():
                        if not os.path.isdir(path):
                            print("Creating new directory at {}".format(path))
                            os.mkdir(path)
                else:
                    print("Path file (paths.json) is not specified.")
                    exit(1)

                # extraction phase
                if sys.argv[2] == "-extract":
                    self.phase = Phases.EXTRACT
                    self.ext = "*.pdf"
                # option to use existing raw text (.txt) instead of PDF files (.pdf)
                elif sys.argv[2] == "-update":
                    self.phase = Phases.UPDATE
                    self.ext = "*.txt"
                # xml build phase
                elif sys.argv[2] == "-build":
                    self.phase = Phases.BUILD
                    self.ext = "*.json"
                    # set schema for XML transformation
                    if len(sys.argv) > 3:
                        if sys.argv[3] == "-bits":
                            self.schema = Schema.BITS
                        elif sys.argv[3] == "-datacite":
                            self.schema = Schema.DATACITE
                        elif sys.argv[3] == "-wordpress":
                            self.schema = Schema.WORDPRESS
                        else:
                            print("Schema requested is missing or invalid.")
                            exit(1)
                    else:
                        print("Schema not specified.")
                        exit(1)
                else:
                    print("Processing phase requested is not valid.")
                    exit(1)
            else:
                print("Missing arguments.")
                exit(1)

        except StopIteration as err:
            print(err)
            exit(1)

    # --------------------------------------
    # Get file or directory path
    def get_path(self, sub_dir, parent_dir=None):
        if sub_dir in self.paths or parent_dir is not None and parent_dir not in self.paths:
            print("Path keys {} {} not found. Please check paths.json.".format(sub_dir, parent_dir))
            return
        else:
            return self.paths[parent_dir][sub_dir] if parent_dir is not None else self.paths[sub_dir]

    # --------------------------------------
    # Get multiple files from
    def get_files(self, subdir, parent_dir=None):
        if parent_dir is None:
            return sorted(glob.glob(os.path.join(self.get_path(subdir), self.ext)))
        else:
            return sorted(glob.glob(os.path.join(self.get_path(subdir, parent_dir), self.ext)))


# instantiate paths
params = Parameters()
