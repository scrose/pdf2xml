#!/usr/bin/env python3x

"""
===========================================
Metadata Document (ACM Proceedings Metadata)
===========================================
Assimilates CSV and PDF raw data into ACM DL XML metadata
"""

import os
import glob
import json
import utils
from tqdm import tqdm
import datetime
import lxml.etree as et
from params import params, Phases

class Meta:

    def __init__(self):
        self.patch = None
        self.section_data = None
        self.section_ch_data = None
        self.sections = self.init_data()

    # --------------------------------------
    # initialize section data to db
    def init_data(self):
        # get metadata files
        self.section_data = self.load(params.get_path('sessions', 'metadata'))
        self.section_ch_data = self.load(params.get_path('session_chairs', 'metadata'))

        # load base XML from template
        self.parser = et.XMLParser(remove_blank_text=True)
        self.root = et.parse(params.get_path('template'), self.parser).getroot()

        # initialize article sequence number and sort key
        seq_no = 1
        sort_key = 10
        display_no = 1
        # initialize section sequence number
        section_seq_no = 1
        cur_section = {} # current section

        # Get current date (format: month/day/year)
        now = datetime.datetime.now()
        current_date = f'{now.month:02}/{now.day:02}/{now.year}'

        # Get publication_date
        # extract publication date and add to articles
        publication_date = self.root.xpath('//proceeding/proceeding_rec/publication_date')[0].text

        # initialize merged data
        data = {}
        sections = {"section": []}
        # retrieve article metadata files
        for file in tqdm(params.get_paths('articles', 'metadata'), desc="Processing Metadata: "):
            # load article metadata file
            data = self.load(file)
            id = utils.get_id(file)
            print("Processing {} ... ".format(id))

            # retrieve data patch (if exists)
            patch_file = os.path.join(params.get_path('patches'), id + ".json")
            if os.path.isfile(patch_file):
                print("Using patch for file ID {} ... ".format(id))
                self.patch = self.load(patch_file)
            else:
                self.patch = None

            # add new section
            if len(cur_section) == 0 or cur_section['section_seq_no'] != data['section_seq_no']:
                data['sort_key'] = sort_key
                data['section_seq_no'] = str(section_seq_no)
                sections['section'].append(self._add_section(data))
                cur_section = sections['section'][-1]
                seq_no = 1
                sort_key += 10
                section_seq_no += 1
            # add article record
            data['sort_key'] = sort_key
            data['seq_no'] = seq_no
            # TODO: Load publication date from base XML
            data['article_publication_date'] = publication_date
            # a for article sequence, p for pagination
            data['display_label'] = 'a'
            # display number (if no pagination provided)
            data['display_no'] = display_no
            cur_section['article_rec'].append(self._add_article(data))
            seq_no += 1
            sort_key += 10
            display_no += 1

        return sections


    # --------------------------------------
    # Add section
    def _add_section(self, data):
        return {
    	   'section_id': '',
    		'sort_key': data['sort_key'],
			'section_seq_no': data['section_seq_no'],
			'section_type': self.section_data[data['section_seq_no']]['section_type'],
			'section_title': self.section_data[data['section_seq_no']]['section_title'].strip(),
			'section_abstract': {'par': ''},
            'section_page_from': self.section_data[data['section_seq_no']]['section_page_from'],
            'chair_editor': {'ch_ed': self._add_people(
                    self.section_ch_data[data['section_seq_no']],
                    self.section_ch_data[data['section_seq_no']]['role'])},
			'fulltext': '',
            'article_rec': []
        }

    # --------------------------------------
    # Add article record
    def _add_article(self, data):
        # use display number if no pagination provided
        if data['page_from'] and data['page_to']:
            params.empty_nodes += ['display_no']
            data['display_no'] = ''
        return {
            'article_id': '',
			'manuscript_tracking_id': '',
			'sort_key': data['sort_key'],
            'display_label': data['display_label'],
            'pages': data['pages'],
			'display_no': data['display_no'],
			'article_publication_date': data['article_publication_date'],
			'seq_no': data['seq_no'],
			'title': data['title'].strip(),
			'subtitle': '',
			'page_from': data['page_from'],
			'page_to': data['page_to'],
			'doi_number': self._add_doi(data['doi_number']),
			'url': '',
			'foreign_title': '',
			'foreign_subtitle': '',
			'language': '',
			'abstract': {'par': self._add_abstract(data['abstract'])},
            'keywords': {'kw': self._add_keywords(data['keywords'])},
            'categories': self._add_categories(data['categories']),
            'general_terms': {'gt': self._add_gts(data['general_terms'])},
            'authors': {'au': self._add_people(data['authors'], 'AUTHOR')},
            'references': {'ref': self._add_references(data['references'])},
            'fulltext': self._add_fulltext(data),
            'supplements': '',
            'qualifiers': '',
			'article_type': '',
			'best_paper_text': '',
			'production_history': '',
			'publisher_article_id': '',
			'article_sponsors': '',
			'topic': '',
			'ccc': self._add_copyright(data),
			'cited_by_list': self._add_citations(data),
			'print_on_demand': '',
			'editorial_comments': '',
            'reproducibility': '',
        }


    # --------------------------------------
    # add people to tree (authors, chairs, etc.)
    def _add_people(self, data, role):
        seq_no = 1
        people = []

        if role == 'AUTHOR':
            data = self._apply_patch('authors', data)
        if type(data) == dict:
            # check if required fields are empty
            if not data['last_name'] or not data['role'] or not data['section_seq_no']:
                return people
            else:
                data = [data]
        if data:
            for person in data:
                people.append({
                    'person_id': '',
                    'author_profile_id': '',
                    'orcid_id': '',
                    'seq_no': seq_no,
                    'first_name': person['first_name'].strip(),
                    'middle_name': person['middle_name'].strip(),
                    'last_name': person['last_name'].strip(),
                    'suffix': person['suffix'].strip(),
                    'affiliation': person['affiliation'].strip(),
                    'role': role,
                    'bio': '',
                    'email_address': '',
                })
                seq_no += 1
        return people

    # --------------------------------------
    # Add DOI number
    def _add_doi(self, data):
        data = self._apply_patch('doi_number', data)
        return data

    # --------------------------------------
    # Add article abstract
    def _add_abstract(self, data):
        data = self._apply_patch('abstract', data)
        return data

    # --------------------------------------
    # Add URL number
    def _add_url(self, data):
        data = self._apply_patch('url', data).replace("&", "%26")
        return data

    # --------------------------------------
    # Add references to build
    def _add_references(self, data):
        seq_no = 1;
        references = []
        data = self._apply_patch('references', data)
        if data:
            for reference in data:
                references.append({
                    'ref_obj_id': '',
                    'ref_obj_pid': '',
                    'ref_seq_no': reference['ref_seq_no'],
                    'ref_text': reference['ref_text'],
                })
                seq_no += 1


        return references


    # --------------------------------------
    # Add categories to build
    def _add_categories(self, data):
        categories = {'primary_category': {}, 'other_category': []} if len(data) > 1 else {}
        data = self._apply_patch('categories', data)
        for i, category in enumerate(data):
            if (i == 0):
                categories['primary_category'] = category
            else:
                categories['other_category'].append(category)

        return categories


    # --------------------------------------
    # Add CCS 2012 concepts to build
    def _add_concepts(self, data):
        concepts = []
        data = self._apply_patch('concepts', data)
        for concept in data:
            concepts({
                'concept_id': concept['concept_id'],
                'concept_desc': concept['concept_desc'],
                'concept_significance': concept['concept_significance'],
            })
        return concepts

    # --------------------------------------
    # Add keyword to db
    def _add_keywords(self, data):
        data = self._apply_patch('keywords', data)
        return data

    # --------------------------------------
    # Add general terms to db
    def _add_gts(self, data):
        data = self._apply_patch('general_terms', data)
        # code lookup table
        lookup_gt = {
            'Design': 'DES',
            'Documentation': 'DOC',
            'Economics': 'ECO',
            'Experimentation': 'EXP',
            'Human Factors': 'HUM',
            'Languages': 'LNG',
            'Legal Aspects': 'LEG',
            'Management': 'MGT',
            'Measurement': 'MEA',
            'Performance': 'PRF',
            'Reliability': 'REL',
            'Security': 'SEC',
            'Standardization': 'STD',
            'Theory': 'THR',
            'Verification': 'VER'
        }
        return [gt for gt in data if gt in lookup_gt]


    # --------------------------------------
    # Add fulltext metadata to build (articles)
    def _add_fulltext(self, data):
        url = self._add_url(data['url']) if data['url'] else ''
        return {
        'file': {
			'seq_no': '',
			'fname': '',
			'duration': '',
			'publisher_article_url': url,
			'description': '',
			'streaming': '',
			'hide': '',
            },
        'article_image': {
			'image': '',
			'caption': '',
		}
       }

    # --------------------------------------
    # Add article copyright information
    def _add_copyright(self, data):
        return {
        'copyright_holder': {
			'copyright_holder_name': '',
			'copyright_holder_year': '',
			'cms_conf_sort_no': '',
            }
       }

    # --------------------------------------
    # Add article citations
    def _add_citations(self, data):
        return {
        'cited_by_number': '',
        'cited_by': {
			'cited_by_object_id': '',
			'cited_by_text': '',
            }
       }

    # --------------------------------------
    # get metadata
    def load(self, path):
       data = None
       with open(path) as fp:
           data = json.load(fp)
       fp.close()
       return data

    # --------------------------------------
    # Apply patches to data object
    def _apply_patch(self, field, data):
        if (self.patch and field in self.patch):
            data = self.patch[field]
        return data



# -- end of MetaDoc class --
meta = Meta()
