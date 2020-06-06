#!/usr/bin/env python3

'''
===========================================
Converts PDF documents to XML metadata
 * Applies ACM DL XML Schema
 * Dependencies:
   - lxml XML toolkit
   - Tika (Apache)
===========================================
'''

import os
import json
import params
import utils
from tqdm import tqdm
from extractor import extractor
from params import params, Phases
from meta import meta
from builder import builder


"""
===========================================
Main Metadata Processer
===========================================
"""
def main():

    # EXTTRACTION or UPDATE phases
    # ===============================================
    if (params.phase == Phases.EXTRACT or params.phase == Phases.UPDATE):
        input_source = "articles" if params.phase == Phases.EXTRACT else "raw"

        # original extraction of index data
        if (params.phase == Phases.EXTRACT):
            # extract metadata from CSV index files
            session_md = extractor.csv(params.get_path("sessions", "index"), "section_seq_no")
            extractor.save(session_md, params.get_path("sessions", "metadata"))
            session_chair_md = extractor.csv(params.get_path("session_chairs", "index"), "section_seq_no")
            extractor.save(session_chair_md, params.get_path("session_chairs", "metadata"))

        # extract metadata from PDF articles (Tika) / Raw text
        submission_md = extractor.csv(params.get_path("articles", "index"), "file_id")

        for file in tqdm(params.get_paths(input_source), desc="Data {}:".format(params.phase.name)):
            # get reference ID from CSV filename
            id = utils.get_id(file)
            # extract raw text from PDF file or use existing raw text
            content = extractor.pdf(file) if params.phase == Phases.EXTRACT else extractor.txt(file)
            md = extractor.merge(id, submission_md, content)

            # save processed metadata to file
            extractor.save(md, os.path.join(params.get_path("articles", "metadata"), id + ".json"))
            extractor.generate_patch(md, content);


    # ===============================================
    # BUILD phase
    # ===============================================
    elif (params.phase == Phases.BUILD or params.phase == Phases.PATCH):
        # build XML from metadata
        builder.build(meta.sections)
        builder.root.append(builder.tree)
        # Remove empty tags
        builder.remove_empty()
        # write output tree to file
        output = builder.save()




# Encapsulate in main()
if __name__ == "__main__":
    main()
