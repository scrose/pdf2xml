#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 21:43:26 2019

@author: boutrous
"""

import lxml.etree as et

def extract_concepts(concepts, acm_ccs_file):
    
    # get ACM classification categories
    ccs2012 = et.parse(acm_ccs_file).getroot()
    nsmap = {'skos':'http://www.w3.org/2004/02/skos/core#', 'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
             
    print("Adding CCS 2012 Concepts: ", concepts)

    concept_id = ''
    concept_desc = ''
    concept_significance = 500
    concept_id_array = []
    
    concepts = [c.strip() for c in concepts]
    concept_desc = '~'.join(concepts)
    bottom_concepts = []
    
    top_concept_candidates = [concepts[0], concepts[0].replace('-',' ').lower()]
    bottom_concept_candidates = [concepts[-1], concepts[-1].replace('-',' ').lower()]
    
    # test possible variations of top concept
    for top_cpt_candidate in top_concept_candidates:
        top_concept = ccs2012.xpath('.//skos:prefLabel[text()="' + top_cpt_candidate +'"]/..', namespaces=nsmap)
        top_concept_alt = ccs2012.xpath('.//skos:altLabel[text()="' + top_cpt_candidate +'"]/..', namespaces=nsmap)
        if top_concept:
            top_concept_id = get_concept_id(top_concept[0], nsmap)
            break
        elif top_concept_alt:
            top_concept_id = get_concept_id(top_concept_alt[0], nsmap)
            break
    
    # test possible variations of bottom concept
    for bottom_cpt_candidate in bottom_concept_candidates:
        # Retrieve broadest and narrowes concepts
        bottom_concept = ccs2012.xpath('.//skos:prefLabel[text()="' + bottom_cpt_candidate +'"]/..', namespaces=nsmap)
        bottom_concept_alt = ccs2012.xpath('.//skos:altLabel[text()="' + bottom_cpt_candidate +'"]/..', namespaces=nsmap)
        if bottom_concept:
            bottom_concepts += bottom_concept
        if bottom_concept_alt:
            bottom_concepts += bottom_concept_alt

    if top_concept and len(bottom_concepts):
        for bottom_concept in bottom_concepts:
            concept_id_array=[]
            if (get_concepts(ccs2012, nsmap, bottom_concept, top_concept_id, concept_id_array)):
                print("Confirmed: Valid path")
                concept_id_array.append(get_concept_id(bottom_concept, nsmap))
                concept_id = '.'.join(concept_id_array).replace('#','')
                print(concept_id, concept_desc, concept_significance)
                return concept_id, concept_desc, concept_significance
            else:
                print("Abort: Not a valid skos path")
                return None, None, None

    else:
        print('Inputed CCS 2012 concepts are not valid.')
    return None, None, None

# --------------------------------------------
def get_concepts(root, nsmap, current_concept, top_concept_id, concept_id_array):

    nsmap = {'skos':'http://www.w3.org/2004/02/skos/core#', 'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
    current_concept_id = get_concept_id(current_concept, nsmap)
    broader_concept_ids = get_broader_ids(current_concept, nsmap)

    #print("Top: ", top_concept_id, "Current: ", current_concept_id, "Broader: ", broader_concept_ids)

    # at top of concept taxonomy
    if (len(broader_concept_ids) == 0):
        return current_concept_id == top_concept_id

    # recursion on broader concepts
    else:
        for c_id in broader_concept_ids:
            resource = get_concept(c_id, root, nsmap)
            if (get_concepts(root, nsmap, resource, top_concept_id, concept_id_array)):
                concept_id_array.append(c_id)
                return True

# --------------------------------------------
def get_concept_id(concept, nsmap):
    concepts = concept.xpath('@rdf:about', namespaces=nsmap)
    return concepts[0] if concepts else None

# --------------------------------------------
def get_concept(concept_id, root, nsmap):
    concept = root.xpath('.//skos:Concept[@rdf:about="' + concept_id + '"]', namespaces=nsmap)
    return concept[0] if (concept) else None

# --------------------------------------------
def get_broader_ids(concept, nsmap):
    concept_ids = []
    broader_concepts = concept.xpath('skos:broader/@rdf:resource', namespaces=nsmap)
    for c_id in broader_concepts:
        concept_ids.append(c_id)
    return concept_ids

# --------------------------------------------
def get_category(cat_node, acm_cat_file):
    
    cat_index = et.parse(acm_cat_file).getroot()
    return cat_index.xpath('/categories/category[cat_node="' + cat_node + '"]/name/text()')[0]
