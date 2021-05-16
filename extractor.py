#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================
Metadata Extractor
===========================================

Created on Tue Mar 12 22:24:07 2019

@author: boutrous
 - Dependencies: tika
"""
import os
import csv
import re
import json
import unicodedata as ud
import utils
from categories import ccs
from tika import parser
from params import params
from regex import regex

"""
===========================================
Metadata Extractor Class
===========================================
"""


class Extractor:

    def __init__(self):
        # header labels
        self.csv_header = [
            'order',
            'id',
            'session',
            'title',
            'authors',
            'affiliations',
            'pages',
            'doi',
            'filename',
            'url',
            'from',
            'to'
        ]
        # get base metadata
        self.n_sessions = len(params.base['sessions'])
        # initialize logging tool
        self._init_logger()
        # Maximum length of reference allowed
        self.max_ref_length = 600
        self.min_ref_length = 5
        # max number of pages for missing categories
        self.max_page_nocat = 2

    # ----------------------------------------
    # Extract from CSV
    # ----------------------------------------
    # Extracts metadata from file(s)
    # Input:
    # - file: CSV file for extraction
    # - ref_id: index to value in data to use as key
    # Output:
    # - JSON data structured by fields
    # ----------------------------------------
    def csv(self, file, ref_id):
        data = {}
        try:
            # retrieve .csv file in input path
            with open(file, "r", encoding="utf-8") as csvfile:
                # extract file header
                reader = csv.reader(csvfile)
                header = [h.lower().replace(' ', '_') for h in next(reader) if h]
                # read in file data labeled by fields
                reader = csv.DictReader(csvfile, header)
                # extract entries
                for i, row in enumerate(reader):
                    entry = {k: self._clean_up(row[k]) for k in row.keys() & header}
                    data[entry[ref_id]] = entry

            csvfile.close()
            return data
        except Exception as e:
            print("CSV extraction error: ", e)

    # ----------------------------------------
    # Extract from Raw Text
    # ----------------------------------------
    # Extracts metadata from file(s)
    # Input:
    # - file: Text file for extraction
    # - ref_id: index to value in data to use as key
    # Output:
    # - JSON data structured by fields
    # ----------------------------------------
    def txt(self, file):
        with open(file, "r", encoding="utf-8") as fp:
            data = fp.read()
        return data

    # ----------------------------------------
    # Extracts metadata from PDF file
    # ----------------------------------------
    # - file: PDF filepath
    # - data: extracted CSV index metadata
    # - returns data structure
    # ----------------------------------------
    def pdf(self, file):
        raw = parser.from_file(file)
        return self._clean_up(raw["content"])

    # ----------------------------------------
    # Merges raw content with index metadata
    # ----------------------------------------
    # - file: PDF filepath
    # - data: extracted CSV index metadata
    # - returns data structure
    # ----------------------------------------
    def merge(self, file_id, index_md, content):

        # check that PDF file is indexed in index metadata
        if file_id not in index_md:
            print("Article ID \'{}\' not found in metadata.".format(file_id))
            exit()

        # get input data file path
        get_data = lambda field: index_md[file_id][field] if field in index_md[file_id] else ""
        file_path = os.path.join(params.get_path("articles", "input"), get_data("filename"))

        # extract ACM CCS concept metadata from raw text
        concepts_valid, concepts_invalid = self.ccs(content)

        metadata = {
            "id": file_id,
            "number": get_data("order"),
            "ref": file_id,
            "doi": get_data('doi'),
            "file_id": get_data("id"),
            "filename": get_data("filename"),
            "file_format": "application/pdf",
            "file_size": utils.get_filesize(file_path),
            "title": get_data("title"),
            "session": get_data("session"),
            "authors": self.authors(content, index_md[file_id]),
            "abstract": self.abst(content),
            "concepts": concepts_valid,
            "keywords": self.kws(content, concepts_invalid),
            "categories": self.cats(content),
            "general_terms": self.gts(content),
            "url": get_data("url"),
            "page_from": get_data("from"),
            "page_to": get_data("to"),
            "pages": get_data("pages"),
            "references": self.ref(content),
        }
        # self.validate(metadata)
        return metadata

    # ==========================================
    # Field Handlers
    # ==========================================

    # Authors
    # extract title, author names and affiliations from file content
    def authors(self, content, csv_data):
        # Process raw PDF extracted data
        # ---------
        # extract raw text of authors + affiliations
        header_raw = regex.above_abstract.match(content)
        header = []
        if header_raw:
            header_raw = header_raw.group(0).strip()
            # split text into fieldgroups by return and strip of empty tokens
            header = [self._clean_up(x) for x in re.split(r"(\\n|\n|\r)", header_raw) if x != '\n' and len(x) > 0]
        else:
            self.log("authors", "Empty header in PDF extraction")

        # CSV Data
        # ---------
        # Tokenize articles' authors and affiliations
        get_data = lambda field: csv_data[field] if field in csv_data else ""
        author_data_csv_data = get_data("authors")
        affiliations_csv_data = get_data("affiliations")

        # Tokenize indvidual authors (comma or semicolon delimited)
        authors = []
        affiliations = []
        if author_data_csv_data:
            people = author_data_csv_data.split(",")
        else:
            self.log("authors", "<Author CSV data is empty")
            return

        # Tokenize author affiliations (semicolon delimited only)
        if affiliations_csv_data:
            affiliations = affiliations_csv_data.split(";")
            if len(affiliations) != len(people):
                print("CSV ERROR: Number of affiliations must match the number of authors.")
                print("\tArticle: {}".format(csv_data['title']))
                print("\tFile: {}".format(csv_data['filename']))
                print("\tAuthors: {}".format(affiliations))
                print("\tAffiliations: {}".format(people))
                exit(1)
        else:
            self.log("authors", "Affiliation CSV data is empty>")
            return

        # Tokenize author names and institution
        # Assumes: [Prefix Firstname Middlename Lastname Suffix]
        for i, person in enumerate(people):
            person = person.strip()
            prefixes = ["Al", "Dr."]
            suffixes = ["Jr.", "Sr.", "jr.", "sr."]

            # Get author"s first/last/middle names
            names = [x.strip() for x in person.split() if len(x) > 0]

            # check that name has at least first and last names
            if len(names) < 2:
                self.log("authors", "Invalid name", person)
            else:
                # TODO: add prefix to author name data
                # Add first name to person data array
                person_data = {"seq_no": i + 1, "prefix": "", "first_name": names[0], "last_name": "",
                               "middle_name": "",
                               "suffix": "", "affiliation": "", "email": ""}

                # check for middle names
                if len(names) > 2:
                    # check for name suffixes
                    if any(s == names[-1] for s in suffixes):
                        person_data["suffix"] = names[-1]
                        person_data["last_name"] = names[-2]
                    # check for name prefixes
                    elif any(s == names[1] for s in prefixes):
                        person_data["last_name"] = " ".join(names[1:])
                    else:
                        person_data["middle_name"] = " ".join(names[1:-1])
                        person_data["last_name"] = names[-1]
                else:
                    person_data["last_name"] = names[-1]

                # check for CSV affiliation data
                if len(affiliations):
                    person_data["affiliation"] = affiliations[i].strip()
                # otherwise get affiliations from PDF data
                # PDF Data
                else:
                    affiliation = ""
                    # -----------------------------------
                    # CASE 1: affiliation below full name
                    # get index of item in header that contains the last name
                    name_keys = [k for k, v in enumerate(header) if person_data["last_name"] in v]
                    email_keys = [k for k, v in enumerate(header) if '@' in v]

                    # lastname found in header
                    if len(name_keys) > 0:
                        name_key = name_keys[0]
                        # reapply find for comma-delimited list of names
                        extracted_names = header[name_key].split(',')
                        name2_keys = [k for k, v in enumerate(extracted_names) if person_data["last_name"] in v]
                        extracted_name = extracted_names[name2_keys[0]].strip()
                        extracted_name = regex.ws.sub('', extracted_name)  # remove whitespace

                        # check for affiliation superscript
                        # -----------------------------------
                        # choose first superscript (either side of name) to corresponding affiliation
                        # characters are either numerals or non-alphabetic and non-ascii
                        superscripts = [s for s in extracted_name if not s.isalpha() and not s in regex.nonalpha_ascii]

                        # superscript found
                        if len(superscripts) > 0:
                            # use superscript to find corresponding affiliation
                            aff_keys = []
                            for s in superscripts:
                                aff_keys.extend([k for k, v in enumerate(header) if s in v and k > name_key])
                            # extract affiliation using last key
                            if len(aff_keys) > 0:
                                affiliation = header[aff_keys[-1]]

                            # remove superscripts from name
                            if '@' not in affiliation:
                                affiliation = "".join(
                                    [s for s in affiliation if s.isalpha() or s in regex.nonalpha_ascii])
                            else:
                                affiliation = None

                        # select next header item (email addres -> go to next header item)
                        elif len(header) > name_keys[0] + 1 and '@' not in header[name_keys[0] + 1]:
                            affiliation = header[name_keys[0] + 1]
                        # select second next header item
                        elif name_keys[0] + 2 < len(header):
                            affiliation = header[name_keys[0] + 2]

                    else:
                        self.log("authors", "Name \'{}\' may not match in documents".format(person_data["last_name"]))

                    # assign affiliation if extracted
                    if affiliation:
                        # remove any superscripts from result
                        affiliation = regex.superscript.sub('', affiliation)
                        person_data["affiliation"] = affiliation.strip()

                    else:
                        self.log(
                            "authors",
                            "Affiliation for \'{}\' not found in header".format(person_data["last_name"]),
                            header)

                # append author to list
                authors.append(person_data)
        return authors

    # ==========================================
    # extract abstracts from file content
    def abst(self, content):

        # extract text below abstract heading
        # OR split content by selection using markers
        abstract = regex.select_abstract.search(content)
        if abstract:
            abstract = abstract.group(2).strip()
            # split by double line breaks (if unlimited)
            # abstract = re.compile(r'([\r\n]{2})').split(abstract)[0]
            # normalize problematic whitespace
            abstract = regex.ws.sub(" ", abstract)
            # remove newline hyphenation
            abstract = regex.no_hyp.sub("", abstract)
            # enumeration
            abstract = regex.rmv_num.sub(".", abstract)
            # clean up
            abstract = self._clean_up(abstract)
            # check if abstract too short
            if len(abstract) < 200:
                self.log("abstract", "Abstract may have been truncated.")
            # check if extra content added to abstract
            if '@' in abstract or len(abstract) > 2000:
                self.log("abstract", "Abstract may contain extraneous text")
        else:
            self.log("abstract", "Abstract is empty")

        return abstract

    # ==========================================
    # extract references from file content
    def ref(self, content):

        output = []
        i = 1
        # select everything after "References"
        references = regex.ref_below.search(content)
        if references:
            references = references.group(2)
            # match and mark reference numbers
            references = regex.ref_numbers.sub(r"{}\2{}".format(regex.m1, regex.m2), references)
            # match and mark reference text
            references = regex.ref_part.sub(r"{}\2\t\4{}\n".format(regex.m1, regex.m2), references)
            # extract last reference to handle trailing content
            ref_last = regex.ref_last.search(references)
            if ref_last is not None:
                ref_last = ref_last.group(0).replace(regex.m2, "\t")
            # split references string into reference entries
            references = regex.ref_split.findall(references)
            # append last reference to list
            if ref_last is not None:
                references.append(ref_last)
            # else:
            #     self.log("references", "Last reference lost or invalid")
            # process references
            for ref in references:
                # split reference into number and text entry
                ref = ref.split('\t')
                # break if two items not extracted from reference string
                if len(ref) != 2: continue
                [ref_number, ref_text] = ref
                # Handle very long references
                if len(ref_text) > self.max_ref_length:
                    # insert marker for predicted end of reference
                    ref_text = regex.ref_truc.sub(r"\1{}\2".format(regex.m1), ref_text)
                    self.log("references", "Truncated very long reference", str(ref_text))

                # reformat hyperlinks
                hyperlink = regex.hyperlinks.search(ref_text)
                if hyperlink is not None:
                    hyperlink = hyperlink.group()
                    hyperlink = regex.no_hyperlink_ws.sub('', hyperlink)
                    hyperlink = re.sub(r"\s+", "_", hyperlink)
                # remove newline hyphenation
                ref_text = regex.no_hyp.sub("", ref_text)
                # add back hyperline (if exists)
                if hyperlink is not None:
                    ref_text = regex.hyperlinks.sub(hyperlink, ref_text)
                # remove problematic whitespace
                ref_text = regex.ws.sub(" ", ref_text)

                # verify correctness of reference
                # check if ref_text is empty
                if len(ref_text) < self.min_ref_length:
                    self.log("references", "Reference text is empty or cut-off")
                # check ref_numbers is an numeral and in the correct order
                elif not ref_number.isdigit() or int(ref_number) != i:
                    self.log("references", "Reference number {} is an invalid value.", ref_text)
                else:
                    # clean up entry
                    ref_text = self._clean_up(ref_text)
                    output.append({"ref_seq_no": ref_number, "ref_text": ref_text})
                i += 1
            return output
        else:
            self.log("references", "References not found")

    # ----------------------------------------
    # extract categories of article
    def cats(self, content):
        categories = []
        cat_node = None
        rcats = regex.cats.search(content)
        # Categories of form X.0.0
        if rcats:
            # replace all whitespace with single space
            rcats = rcats.group(2)
            # remove newline hyphenation
            rcats = regex.no_hyp.sub("", rcats)
            # remove whitespace
            rcats = regex.ws.sub(" ", rcats)
            # extract category code
            rcats = regex.cat_code.sub(r"\n\1\t", rcats)
            # separate categories
            for cat in rcats.split("\n"):
                if cat.strip():
                    cat = [c.strip().replace(";", "") for c in cat.split("\t")]
                    cat_desc = None
                    if len(cat) == 2:
                        cat_node = cat[0]
                        cat_desc = ccs.get_category(cat_node)
                    # if verified category found add to categories list
                    if cat_desc:
                        categories.append({"cat_node": cat_node, "descriptor": cat_desc, "type": "S"})
                    else:
                        self.log("categories", "Invalid categories extracted", str(cat))
        return categories

    # ----------------------------------------
    # extract keywords of article
    def kws(self, content, concepts_invalid):
        kws = []
        r_kws = regex.kws.search(content)
        if r_kws:
            r_kws = r_kws.group(1)
            # remove newline hyphenation
            r_kws = regex.no_hyp.sub('', r_kws)
            # fix newlines and colon starts
            r_kws = r_kws.replace("\r", " ").replace("\n", " ").replace(': ', '')
            # separate keywords into list
            for kw in re.findall(r"[^,;]+", r_kws):
                if kw.strip():
                    kws.append(kw.strip())
                else:
                    self.log("keywords", "Invalid keywords", str(r_kws))
        if concepts_invalid:
            kws += concepts_invalid
        return kws

    # ----------------------------------------
    # extract general terms of article
    def gts(self, content):
        gts = []
        r_getgts = regex.gts.search(content)

        if (r_getgts):
            r_getgts = r_getgts.group(2)
            # remove newline hyphenation
            r_getgts = regex.no_hyp.sub("", r_getgts)
            # remove whitespace
            r_getgts = re.sub(r"(\n|\.|\s)+", "", r_getgts)
            # separate into list
            for gt in r_getgts.split(","):
                if gt.strip():
                    gts.append(gt.strip())
                else:
                    self.log("general_terms", "Invalid general terms", str(gt))

        return gts

    # ----------------------------------------
    # extract ACM CCS 2012 taxonomies
    def ccs(self, content):
        rccs = regex.ccs.search(content)
        concepts_valid = []
        concepts_invalid = []
        # Categories of CCS 2012 format
        if rccs:
            # replace all whitespace with single space
            rccs = regex.ws.sub(" ", rccs.group(2))
            # split concept groups
            for concepts_raw in re.split('-; |—; |; |, |\u2022', rccs):
                concepts_raw = concepts_raw.strip().replace('  ', ' ')
                # remove hyphenation
                concepts_raw = regex.no_hyp.sub("", concepts_raw)
                # split concepts at em-dash
                concepts_raw = regex.ccs_concept_split.sub("~", concepts_raw)
                concepts = concepts_raw.split("~")
                concepts = [regex.ws.sub(" ", c).strip().replace('.', '') for c in concepts if c != '']
                concept_id, concept_desc, concept_significance, log_data = ccs.lookup(concepts)
                # confirm valid concepts extracted
                if concept_id and concept_desc:
                    concepts_valid.append({
                        "id": concept_id,
                        "description": concept_desc,
                        "significance": concept_significance})
                else:
                    concepts_invalid += concepts
                    for log_entry in log_data:
                        self.log("concepts", log_entry[0], log_entry[1])
        return concepts_valid, concepts_invalid

    # ----------------------------------------
    # save data to file
    def save(self, data, file):
        with open(file, 'w', encoding="utf-8") as fp:
            if utils.get_filetype(file) == "json":
                json.dump(data, fp, ensure_ascii=False, indent=4)
            else:
                fp.write(data)

    # ----------------------------------------
    # clean up OCR and common miscellaneous errors/typos
    def _clean_up(self, content):
        clean_text = regex.ws_top.sub("", content)
        clean_text = regex.dq.sub("&#34;", clean_text)
        clean_text = regex.sq.sub("&#39;", clean_text)
        # OCR: Replace LATIN SMALL LIGATURE FI with "fi"
        clean_text = regex.fi.sub("fi", clean_text)
        # OCR: Replace LATIN SMALL LIGATURE FL with "fl"
        clean_text = regex.fl.sub("fl", clean_text)
        clean_text = regex.dingbats1.sub("", clean_text)
        clean_text = regex.dingbats2.sub("", clean_text)
        # handle composing characters
        # Return the normal ‘NFKC’ form for the Unicode string
        # The normal form KC (NFKC) first applies the compatibility
        # decomposition, followed by the canonical composition.
        clean_text = ud.normalize("NFKC", clean_text)

        return clean_text

    # ----------------------------------------
    # validate metadata
    def validate(self, md):

        if int(md["page_to"]) - int(md["page_from"]) > self.max_page_nocat:
            # CCS Categories / Keywords
            if len(md["categories"]) == 0 or len(md["keywords"]) == 0:
                self.log("categories",
                         "CCS concepts and keywords required for articles > 2 pages; optional for under 2-page articles"
                         )

    # ==========================================
    # Patch extracted data with manual corrections (patches)
    def generate_patch(self, md, content):
        # patch_file = os.path.join(params.get_path("patches"), md["id"] + "_patch.json")
        log_file = os.path.join(params.get_path("logs", "output"), md["id"] + "-log.json")
        txt_file = os.path.join(params.get_path("txt", "output"), md["id"] + ".txt")
        # count number of logged issues
        issues = [log for log in self.logger.values() if (len(log) > 0)]
        # Issues logged -> create log and patch files
        if len(issues) > 0:
            # save copy of metadata as patch if none exists
            # if not os.path.isfile(patch_file):
            #     self.save(self.logger, patch_file)
            # save extracted content as raw text patch if none exists
            if not os.path.isfile(txt_file):
                self.save(content, txt_file)
            # save copy as log
            self.save(self.logger, log_file)
        else:
            # delete log file
            if os.path.isfile(log_file):
                os.remove(log_file)
        # reset logger
        self._init_logger()

        # return number of issues found
        return len(issues)

    # ----------------------------------------
    # initialize logger
    def _init_logger(self):
        self.logger = {
            "authors": [],
            "abstract": [],
            "references": [],
            "keywords": [],
            "categories": [],
            "concepts": [],
            "general_terms": [],
        }

    # ----------------------------------------
    # log issues
    def log(self, ref_id, message, data=None):

        if data is not None:
            self.logger[ref_id].append("<{}> ---- {}".format(message, data))
        else:
            self.logger[ref_id].append("<{}>".format(message))


# instantiate Extractor
extractor = Extractor()
