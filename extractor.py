#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================
Metadata Extractor
===========================================

Created on Tue Mar 12 22:24:07 2019

@author: boutrous
 - Dependencies: tika, tqdm
"""
import os
import csv
import re
import json
import unicodedata as ud
import utils
import categories as ccs
from tqdm import tqdm
from tika import parser
from params import params, Phases


"""
===========================================
Metadata Extractor Class
===========================================
"""
class Extractor:

    def __init__(self, data=None):
        # initialize logging tool
        self._init_logger()
        # Maximum length of reference allowed
        self.max_ref_length = 600
        self.min_ref_length = 5
        # max number of pages for missing categories
        self.max_page_nocat = 2
        self.nonalpha_ascii = "~\`!?<>\.\,*_-/@#$&%^()\'\"=;:\{\}\[\] \t\n"
        # regex markers
        self.m1 = "--%%%start%%%--"
        self.m2 = "--%%%end%%%--"
        self.regex = {
                # ======== General =========
                # select non-alpha char used for superscripts
                "superscript": re.compile(r"([^a-zA-Z\s\v\n \.;:-|\\\[\]\(\)-~`\*@\#\$\%\^\&])"),
                # remove newline hyphenation
                "no_hyp": re.compile(r"((-\s+))"),
                # remove whitespace at top of page
                "ws_top": re.compile(r"^[\r\n\t ]+"),
                # match problematic whitespace
                "ws": re.compile(r"((\t|\x0b|\x0c|\r|\n)+)"),
                # match content after final period
                "end": re.compile(r"(\.)(?!.*\1)([\s\S]*)"),
                # select hyperlinks
                "hyperlinks": re.compile(r"(https?:\/\/).*?(?=[,])"),
                # remove whitespace between non-alphanumeric characters
                "no_hyperlink_ws": re.compile(r"(((?<=[/.:\?-@])\s)|(\s(?=[/.:\?-@])))"),

                # ======== Unicode/OCR =========
                # emoticons
                "emoticons": re.compile(u"[\u1f600-\u1f64f]+", re.UNICODE),
                #dingbats 2702 - 27B0
                "dingbats1": re.compile(u"[\u2702-\u27b0]+", re.UNICODE),
                #dingbats 2020
                "dingbats2": re.compile(u"[\u2020]+", re.UNICODE),
                # transport/map symbols
                "symbols1": re.compile(u"[\u1f680-\u1f6ff]+", re.UNICODE),
                # symbols & pics
                "symbols2": re.compile(u"[\u1f300-\u1f5ff]+", re.UNICODE),
                # diacritics (non-composing)
                "acute": re.compile(u"([\u00B4])([a-z])", re.UNICODE),
                "diaeresis": re.compile(u"([\u00a8])([a-z])", re.UNICODE),
                # Replace double/single quotes NOT in tags with HTML entity
                "dq": re.compile(r"(\")(?=[^>]*<)"),
                "sq": re.compile(r"(\")(?=[^>]*<)"),
                # OCR: Replace LATIN SMALL LIGATURE FI with "fi"
                "fi": re.compile(r"(&#64257;|\ufb01)"),
                # OCR: Replace LATIN SMALL LIGATURE FL with "fl"
                "fl": re.compile(r"(&#64258;|\ufb02)"),

                # ======== Abstracts =========
                # select text above abstract
                "above_abstract": re.compile(r"^((.|\n)*?)(?=abstract)", re.IGNORECASE),
                # select abstract
                "abstract": re.compile(r"(abstract)((.|\n)*?)(^\d|index terms:?|categories and subject descriptors|introduction|keywords:?|(the )?interview|motivation)", re.IGNORECASE),
                "rmv_num": re.compile(r"(\.[ ]\d)"),

                # ======== Keywords =========
                # select keywords
                "kws": re.compile(r"""(?<=keywords)(:?(.|\n)*?)(?=\.|index terms:?|introduction|[1])""", re.IGNORECASE),

                # ======== References =========
                # get content below 'References' title
                "ref_below": re.compile(r"(^\d?\d?\s?references\n?)([\s\S]*)", re.IGNORECASE|re.MULTILINE),
                # match [reference numbers]
                "ref_numbers": re.compile(r"(\[)([0-9]+)(\])"),
                # partition -> split reference string into references list
                "ref_part": re.compile(r"(^{})(\d\d?)({})([\s\S]*?)(?=^{}\d\d?{})".format(self.m1, self.m2, self.m1, self.m2), re.IGNORECASE|re.MULTILINE),
                "ref_split": re.compile(r"(?<=^{})([\s\S]*?)(?={})".format(self.m1, self.m2), re.IGNORECASE|re.MULTILINE),
                # truncate end reference content
                "ref_truc": re.compile(r"^([\s\S]*?)(\.$)", re.IGNORECASE|re.MULTILINE),
                # get last reference (NOTE: after partition and split)
                "ref_last": re.compile(r"(?<=^{})(\d\d?)({})([\s\S]*)(\.$)".format(self.m1, self.m2), re.IGNORECASE|re.MULTILINE),
                # match transposed text (ref numbers are above entries)
                #r_unnumbered = re.compile(r"(\])(\s+)(\[)" ) # find empty references
                #r_unnumbered = re.compile(r"((.|\n)*)(?!.*\1)(\.)") # find unnumbered references

                # ======== Categories =========
                # regex for categories
                "cats": re.compile(r"""(categories and subject descriptors|index terms:?)((.|\n)*?)(([1]\s*)?introduction|([1]\s*)?keywords)""", re.IGNORECASE),
                "cat_code": re.compile(r"([A-Z]\.[0-9a-zA-Z](\.[0-9]|\.[a-z])?)"),

                # ======== General Terms =========
                # match general terms
                "gts": re.compile(r"(general terms)((.|\n)*)(keywords)", re.IGNORECASE),

                # ======== CCS 2012 =========
                # match ACM CCS 2012 concepts
                "ccs_split": re.compile(r"""(-|\u2012|\u2013|\u2014|\u2015|\u2192|:|\n|\*)( ?)(?=[A-Z])"""),
                "ccs": re.compile(r"""(ccs concepts:?|index terms:?)((.|\n)*?)(([1]\s*)?introduction|([1]\s*)?keywords|([\*]\s*)?e-?mail)""", re.IGNORECASE),
        }



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
        data = None
        with open(file, "r", encoding="utf-8") as fp:
            data = fp.read()
        fp.close
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
    def merge(self, id, index_md, content):
        if id in index_md:
            get_data = lambda field: index_md[id][field] if field in index_md[id] else ""
        else:
            print("Article ID {} not found in metadata.".format(id))
            exit()
        metadata = {
            "id": id,
            "order": get_data("order"),
            "doi_number": get_data("doi_number"),
            "file_id": get_data("file_id"),
            "title": get_data("title"),
            "section_seq_no": get_data("section_seq_no"),
            "authors": self.authors(content, index_md[id]),
            "abstract": self.abst(content),
            "references": self.ref(content),
            "keywords": self.kws(content),
            "categories": self.cats(content),
            "ccs2012": self.ccs(content),
            "general_terms": self.gts(content),
            "url": get_data("url"),
            "page_from": get_data("page_from"),
            "page_to": get_data("page_to"),
            "pages": get_data("pages"),
        }
        # self.validate(metadata)
        return metadata


    # ==========================================
    # Field Handlers
    # ==========================================


    # ==========================================
    # Authors
    # extract title, author names and affiliations from file content
    def authors(self, content, csv_data):
        # Process raw PDF extracted data
        #---------
        # extract raw text of authors + affiliations
        header_raw = self.regex['above_abstract'].match(content)
        header = []
        if (header_raw):
            header_raw = header_raw.group(0).strip()
            # split text into fieldgroups by return and strip of empty tokens
            header = [self._clean_up(x) for x in re.split(r"(\\n|\n|\r)", header_raw) if x != '\n' and len(x) > 0]
        else:
            self.log("authors", "Empty header in PDF extraction")

        # CSV Data
        #---------
        # Tokenize individual authors w/ institutions
        get_data = lambda field: csv_data[field] if field in csv_data else ""
        author_data_csv_data = get_data("authors")
        affiliations_csv_data = get_data("affiliations")
        authors = []
        affiliations = []
        people = []

        # check for author data
        if author_data_csv_data:
            people = author_data_csv_data.split(",")

        else:
            self.log("authors", "<Author CSV data is empty")
            return
        # check for author affliation data
        if affiliations_csv_data:
            affiliations = affiliations_csv_data.split(",")
        #else:
            #self.log("authors", "Affiliation CSV data is empty>")
            #return

        # Tokenize author names and institution
        for i, person in enumerate(people):
            person = person.strip()
            prefixes = ["Al", "Dr."]
            suffixes = ["Jr.", "Sr.", "jr.", "sr."]
            affiliation = ""
            # Get author"s first/last/middle names
            names = [x.strip() for x in person.split() if len(x) > 0]
            # check for data
            if len(names) < 2:
                self.log("authors", "Invalid name", person)
            else:
                person_data = {
                    "first_name": "",
                    "last_name": "",
                    "middle_name": "",
                    "suffix": "",
                    "affiliation": "",
                    "email": ""
                }

                person_data["first_name"] = names[0]
                # check for middle names
                if (len(names) > 2):
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
                    person_data["affiliation"] = affiliations[i]
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
                    if (len(name_keys) > 0):
                        name_key = name_keys[0]
                        # reapply find for comma-delimited list of names
                        extracted_names = header[name_key].split(',')
                        name2_keys = [k for k, v in enumerate(extracted_names) if person_data["last_name"] in v]
                        extracted_name = extracted_names[name2_keys[0]].strip()
                        extracted_name = self.regex["ws"].sub('', extracted_name) # remove whitespace

                        # check for affiliation superscript
                        # -----------------------------------
                        # choose first superscript (either side of name) to corresponding affiliation
                        # characters are either numerals or non-alphabetic and non-ascii
                        superscripts = [s for s in extracted_name if not s.isalpha() and not s in self.nonalpha_ascii]

                        # superscript found
                        if (len(superscripts) > 0):
                            # use superscript to find corresponding affiliation
                            aff_keys = []
                            for s in superscripts:
                                aff_keys.extend([k for k, v in enumerate(header) if s in v and k > name_key])
                            # extract affiliation using last key
                            if (len(aff_keys) > 0):
                                affiliation = header[aff_keys[-1]]

                            # remove superscripts from name
                            if not '@' in affiliation:
                                affiliation = "".join([s for s in affiliation if s.isalpha() or s in self.nonalpha_ascii])
                            else:
                                affiliation = None

                        # select next header item (email addres -> go to next header item)
                        elif ( len(header) > name_keys[0]+1 and not '@' in header[name_keys[0]+1] ):
                            affiliation = header[name_keys[0]+1]
                        # select second next header item
                        elif ( len(header) > name_keys[0]+2 ):
                            affiliation = header[name_keys[0]+2]

                    else:
                        self.log("authors", "Name \'{}\' may not match in documents".format(person_data["last_name"]))

                    # assign affiliation if extracted
                    if affiliation:
                        # remove any superscripts from result
                        affiliation = self.regex["superscript"].sub('', affiliation)
                        person_data["affiliation"] = affiliation.strip()

                    else:
                        self.log("authors", "Affiliation for \'{}\' not found in header".format( \
                            person_data["last_name"]), header)

                # append author to list
                authors.append(person_data)
        return authors

    # ==========================================
    # extract abstracts from file content
    def abst(self, content):

        # normalize problematic whitespace
        abstract = self.regex["ws"].sub(" ", content)
        # extract raw abstract
        abstract = self.regex["abstract"].search(abstract)

        # get the abstract match group
        if (abstract):
            abstract = abstract.group(2).strip()
            # remove newline hyphenation
            abstract = self.regex["no_hyp"].sub("", abstract)
            # enumeration
            abstract = self.regex["rmv_num"].sub(".", abstract)
            # clean up
            abstract = self._clean_up(abstract)
        else:
            self.log("abstract", "Abstract is empty")

        return abstract

    # ==========================================
    # extract references from file content
    def ref(self, content):

        output = []
        i = 1
        # select everything after "References"
        references = self.regex["ref_below"].search(content)
        if references:
            references = references.group(2)
            # match and mark reference numbers
            references = self.regex["ref_numbers"].sub(r"{}\2{}".format(self.m1, self.m2), references)
            # match and mark reference text
            references = self.regex["ref_part"].sub(r"{}\2\t\4{}\n".format(self.m1, self.m2), references)
            # extract last reference to handle trailing content
            ref_last = self.regex["ref_last"].search(references)
            if ref_last is not None:
                ref_last = ref_last.group(0).replace(self.m2, "\t")
            # split references string into reference entries
            references = self.regex["ref_split"].findall(references)
            # append last reference to list
            if ref_last is not None:
                references.append(ref_last)
            else:
                self.log("references", "Last reference lost or invalid")
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
                    ref_text = self.regex["ref_truc"].sub(r"\1{}\2".format(self.m1), ref_text)
                    self.log("references", "Truncated very long reference", str(ref_text))

                # reformat hyperlinks
                hyperlink = self.regex["hyperlinks"].search(ref_text)
                if hyperlink is not None:
                    hyperlink = hyperlink.group()
                    hyperlink = self.regex["no_hyperlink_ws"].sub('', hyperlink)
                    hyperlink = re.sub(r"\s+", "_", hyperlink)
                # remove newline hyphenation
                ref_text = self.regex["no_hyp"].sub("", ref_text)
                # add back hyperline (if exists)
                if hyperlink is not None:
                    ref_text = self.regex["hyperlinks"].sub(hyperlink, ref_text)
                # remove problematic whitespace
                ref_text = self.regex["ws"].sub(" ", ref_text)

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
        # No references found
        else:
            self.log("references", "No references found>")



    # ----------------------------------------
    # extract categories of article
    def cats(self, content):
        categories = []
        rcats = self.regex["cats"].search(content)
        # Categories of form X.0.0
        if (rcats):
            # replace all whitespace with single space
            rcats = rcats.group(2)
            # remove newline hyphenation
            rcats = self.regex["no_hyp"].sub("", rcats)
            # remove whitespace
            rcats = self.regex["ws"].sub(" ", rcats)
            # extract category code
            rcats = self.regex["cat_code"].sub(r"\n\1\t", rcats)
            # separate categories
            for cat in rcats.split("\n"):
                if cat.strip():
                    cat = [c.strip().replace(";", "") for c in cat.split("\t")]
                    cat_desc = None
                    if len(cat)==2:
                        cat_node = cat[0]
                        cat_desc = ccs.get_category(cat_node, params.get_path("acm_taxonomy"))
                    # if verified category found add to categories list
                    if cat_desc:
                        categories.append({"cat_node": cat_node, "descriptor": cat_desc, "type": "S"})
                    else:
                        self.log("categories", "Invalid categories extracted", str(cat))
        return categories



    # ----------------------------------------
    # extract keywords of article
    def kws(self, content):
        kws = []
        r_kws = self.regex["kws"].search(content)

        if (r_kws):
            r_kws = r_kws.group(1)
            # remove newline hyphenation
            r_kws = self.regex["no_hyp"].sub('', r_kws)
            # fix newlines
            r_kws = r_kws.replace("\r"," ").replace("\n"," ")
            # separate keywords into list
            for kw in re.findall(r"[^,;]+", r_kws):
                if (kw.strip()):
                    kws.append(kw.strip())
                else:
                    self.log("keywords", "Invalid keywords", str(r_kws))

        return kws


    # ----------------------------------------
    # extract general terms of article
    def gts(self, content):
        gts = []
        r_getgts = self.regex["gts"].search(content)

        if (r_getgts):
            r_getgts = r_getgts.group(2)
            # remove newline hyphenation
            r_getgts = self.regex["no_hyp"].sub("", r_getgts)
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
        rccs = self.regex["ccs"].search(content)
        concepts = []
        # Categories of CCS 2012 format
        if (rccs):
            # replace all whitespace with single space
            rccs = self.regex["ws"].sub(" ", rccs.group(2))
            for concepts_raw in rccs.split(";"):
                concepts_raw = concepts_raw.strip()
                # split concepts at hyphen-Capital letter
                concepts_raw = self.regex["ccs_split"].sub("~", concepts_raw)
                concepts_raw = concepts_raw.split("~")
                concept_id, concept_desc, concept_significance = ccs.extract_concepts(
                        concepts_raw, params.get_path("CCS2012_taxonomy"))
                if concept_id and concept_desc:
                    concepts.append({
                            "concept_id": concept_id,
                            "concept_desc": concept_desc,
                            "concept_significance": concept_significance})
                else:
                    self.log("ccs2012", "Invalid CCS concepts", str(concepts_raw))
        return concepts

    # ----------------------------------------
    # save data to file
    def save(self, data, file):
        with open(file, 'w', encoding="utf-8") as fp:
            if (utils.get_filetype(file) == "json"):
                json.dump(data, fp, ensure_ascii=False, indent=4)
            else:
                fp.write(data)
        fp.close()


    # ----------------------------------------
    # clean up OCR and common miscellaneous errors/typos
    def _clean_up(self, content):
        clean_text = self.regex["ws_top"].sub("", content)
        clean_text = self.regex["dq"].sub("&#34;", clean_text)
        clean_text = self.regex["sq"].sub("&#39;", clean_text)
        # OCR: Replace LATIN SMALL LIGATURE FI with "fi"
        clean_text = self.regex["fi"].sub("fi", clean_text)
        # OCR: Replace LATIN SMALL LIGATURE FL with "fl"
        clean_text = self.regex["fl"].sub("fl", clean_text)
        clean_text = self.regex["dingbats1"].sub("", clean_text)
        clean_text = self.regex["dingbats2"].sub("", clean_text)
        # handle composing characters
        # Return the normal ‘NFKC’ form for the Unicode string
        # The normal form KC (NFKC) first applies the compatibility
        # decomposition, followed by the canonical composition.
        clean_text = ud.normalize("NFKC", clean_text)

        return clean_text

    # ----------------------------------------
    # validate metadata
    def validate(self, md):

        if (int(md["page_to"]) - int(md["page_from"]) > self.max_page_nocat):
            # CCS Categories
            if len(md["categories"]) == 0:
                self.log("categories",
                    "CCS concepts and keywords required for articles > 2 pages; optional for 1- or 2-page articles (or abstracts)"
                    )
            # Keywords
            elif len(md["keywords"]) == 0:
                self.log("categories",
                    "CCS concepts and keywords required for articles > 2 pages; optional for 1- or 2-page articles (or abstracts)"
                    )




    # ==========================================
    # Patch extracted data with manual corrections (patches)
    def generate_patch(self, md, content):
        patch_file = os.path.join(params.get_path("patches"), md["id"] + ".json")
        log_file = os.path.join(params.get_path("logs"), md["id"] + ".json")
        raw_file = os.path.join(params.get_path("raw"), md["id"] + ".txt")
        # count number of logged issues
        issues = [log for log in self.logger.values() if (len(log) > 0)]
        # Issues logged -> create log and patch files
        if len(issues) > 0:
            # save copy of metadata as patch if none exists
            # if not os.path.isfile(patch_file):
            #     self.save(self.logger, patch_file)
            # save extracted content as raw text patch if none exists
            if not os.path.isfile(raw_file):
                self.save(content, raw_file)
            # save copy as log
            self.save(self.logger, log_file)
        else:
            # delete log file
            if os.path.isfile(log_file):
                os.remove(log_file)
        # reset logger
        self._init_logger()


    # ----------------------------------------
    # initialize logger
    def _init_logger(self):
        self.logger = {
            "authors": [],
            "abstract": [],
            "references": [],
            "keywords": [],
            "categories": [],
            "ccs2012": [],
            "general_terms": [],
        }

    # ----------------------------------------
    # log issues
    def log(self, id, message, data=None):

        if data is not None:
            self.logger[id].append("<{}> ---- {}".format(message, data))
        else:
            self.logger[id].append("<{}>".format(message))


# instantiate Extractor
extractor = Extractor()
