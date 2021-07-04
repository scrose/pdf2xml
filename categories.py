#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 21:43:26 2019

@author: boutrous
"""

import lxml.etree as et
from params import params


class CCS:

    def __init__(self):
        # load ACM classification categories
        self.skos = et.parse(params.paths['taxonomy']['CCS2012']).getroot()
        # CCS2012 taxonomy namespace mapping
        self.nsmap = {
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        }
        # get list of top concepts
        self.valid_top_concepts = \
            self.skos.xpath('//skos:ConceptScheme/skos:hasTopConcept/@rdf:resource', namespaces=self.nsmap)
        self.cat_index = et.parse(params.paths['taxonomy']['acm']).getroot()
        self.logger = []

    def lookup(self, concepts):

        # clear logs
        self.clear_logs()

        if len(concepts) == 0:
            return None, None, None, self.logger

        # initialize
        top_concept_id = None
        bottom_concepts = []
        concept_significance = 500  # default weight

        # clean raw concept text extraction
        concept_desc = '~'.join(concepts)

        # list alternates of top and bottom concepts
        top_concept_candidates = [concepts[0], concepts[0].lower(), concepts[0].lower().capitalize()]
        bottom_concept_candidates = [concepts[-1], concepts[-1].lower(), concepts[-1].lower().capitalize()]

        self.log("Top concept candidates", top_concept_candidates)
        self.log("Bottom concept candidates", bottom_concept_candidates)

        # test possible variations of top concept
        for top_cpt_candidate in top_concept_candidates:
            top_concepts = \
                self.skos.xpath('//*[contains(text(), "' + top_cpt_candidate + '")]/..', namespaces=self.nsmap)
            for top_concept in top_concepts:
                if self.get_concept_id(top_concept) in self.valid_top_concepts:
                    top_concept_id = self.get_concept_id(top_concept)
                    break
            if top_concept_id:
                break

        if not top_concept_id:
            self.log('Top concept invalid')
            return None, None, None, self.logger
        else:
            self.log("Top concept validated", top_concept_id)

        # test variations of bottom concept
        for bottom_cpt_candidate in bottom_concept_candidates:
            # Retrieve broadest and narrows concepts
            bottom_concepts += \
                self.skos.xpath('//*[contains(text(), "' + bottom_cpt_candidate + '")]/..', namespaces=self.nsmap)

        if not bottom_concepts:
            self.log('Bottom concepts invalid')
            return None, None, None, self.logger
        else:
            bottom_concept_ids = [self.get_concept_id(c) for c in bottom_concepts]
            self.log("Bottom concepts validated", bottom_concept_ids)

        # Find possible node paths from bottom to top concepts
        for bottom_concept_id in bottom_concept_ids:
            concept_path = self.get_concept_path(top_concept_id, [bottom_concept_id])
            if concept_path:
                # Get path description
                concept_path_desc = []
                for concept_id in concept_path:
                    concept_path_desc += [self.get_concept_desc(concept_id)]
                concept_desc = "~".join(concept_path_desc)
                concept_id = '.'.join(concept_path).replace('#', '')
                return concept_id, concept_desc, concept_significance, self.logger
        self.log("Abort: Not a valid CSS concept path")
        return None, None, None, self.logger

    # --------------------------------------------
    # DFS concept paths from current concept to top concept
    def get_concept_path(self, top_concept_id, concept_path):
        if concept_path is None or len(concept_path) == 0:
            return None
        # front item is current ID
        current_concept_id = concept_path[0]
        # concepts up the tree
        broader_concept_ids = self.get_broader_ids(self.get_concept(current_concept_id))
        self.log("Top: {}, Current: {}, Broader: {}, Path: {}".format(
            top_concept_id, current_concept_id, broader_concept_ids, concept_path))

        # found top concept ID
        if current_concept_id == top_concept_id:
            return concept_path

        # recursively test broader concepts
        for broader_concept_id in broader_concept_ids:
            test_path = [broader_concept_id] + concept_path
            self.log("Testing path: {}".format(test_path))
            test_result = self.get_concept_path(top_concept_id, test_path)
            self.log("Result: {}".format(test_result))
            if test_result:
                return test_result

        # concept path not found
        return None

    # --------------------------------------------
    def get_concept_id(self, concept):
        concept_id = concept.xpath('@rdf:about', namespaces=self.nsmap)
        return concept_id[0] if id else None

    # --------------------------------------------
    def get_concept(self, concept_id):
        concept = self.skos.xpath('.//skos:Concept[@rdf:about="' + concept_id + '"]', namespaces=self.nsmap)
        return concept[0] if concept else None

    # --------------------------------------------
    def get_broader_ids(self, concept):
        return concept.xpath('.//skos:broader/@rdf:resource', namespaces=self.nsmap)

    # --------------------------------------------
    def get_concept_desc(self, concept_id):
        concept = self.get_concept(concept_id)
        concept_desc = concept.xpath('.//skos:prefLabel/text()', namespaces=self.nsmap)[0]
        return concept_desc if concept_desc else None

    # --------------------------------------------
    def get_category(self, cat_node):
        cat = self.cat_index.xpath('/categories/category[cat_node="' + cat_node + '"]/name/text()')
        if len(cat) > 0:
            return cat[0]
        else:
            return ''

    # ----------------------------------------
    # log issues
    def log(self, message, data=None):
        self.logger.append((message, data))

    # ----------------------------------------
    # clear log records
    def clear_logs(self):
        self.logger = []


ccs = CCS()
