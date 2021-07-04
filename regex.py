#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 21:43:26 2019

@author: boutrous
"""

import re


class Regex:

    def __init__(self):
        # ======== General =========
        self.nonalpha_ascii = "~\`!?<>\.\,*_-/@#$&%^()\'\"=;:\{\}\[\] \t\n"
        # regex markers
        self.m1 = "--%%%start%%%--"
        self.m2 = "--%%%end%%%--"
        # select non-alpha char used for superscripts
        self.superscript = re.compile(r"([^a-zA-Z\s\v\n \.;:-|\\\[\]\(\)-~`\*@\#\$\%\^\&])")
        # remove newline hyphenation
        self.no_hyp = re.compile(r"((-\s+))")
        # remove whitespace at top of page
        self.ws_top = re.compile(r"^[\r\n\t ]+")
        # match problematic whitespace
        self.ws = re.compile(r"((\t|\x0b|\x0c|\r|\n)+)")
        # match content after final period
        self.end = re.compile(r"(\.)(?!.*\1)([\s\S]*)")
        # select hyperlinks
        self.hyperlinks = re.compile(r"(https?:\/\/).*?(?=[,])")
        # remove whitespace between non-alphanumeric characters
        self.no_hyperlink_ws = re.compile(r"(((?<=[/.:\?-@])\s)|(\s(?=[/.:\?-@])))")
        # ======== Unicode/OCR =========
        # emoticons
        self.emoticons = re.compile(u"[\u1f600-\u1f64f]+", re.UNICODE)
        # dingbats 2702 - 27B0
        self.dingbats1 = re.compile(u"[\u2702-\u27b0]+", re.UNICODE)
        # dingbats 2020
        self.dingbats2 = re.compile(u"[\u2020]+", re.UNICODE)
        # transport/map symbols
        self.symbols1 = re.compile(u"[\u1f680-\u1f6ff]+", re.UNICODE)
        # symbols & pics
        self.symbols2 = re.compile(u"[\u1f300-\u1f5ff]+", re.UNICODE)
        # diacritics (non-composing)
        self.acute = re.compile(u"([\u00B4])([a-z])", re.UNICODE)
        self.diaeresis = re.compile(u"([\u00a8])([a-z])", re.UNICODE)
        # Replace double/single quotes NOT in tags with HTML entity
        self.dq = re.compile(r"(\")(?=[^>]*<)")
        self.sq = re.compile(r"(\")(?=[^>]*<)")
        # OCR: Replace LATIN SMALL LIGATURE FI with "fi"
        self.fi = re.compile(r"(&#64257;|\ufb01)")
        # OCR: Replace LATIN SMALL LIGATURE FL with "fl"
        self.fl = re.compile(r"(&#64258;|\ufb02)")

        # ======== Abstracts =========
        # select text above abstract
        self.above_abstract = re.compile(r"^((.|\n)*?)(?=^abstract)", re.IGNORECASE | re.MULTILINE)
        # select text below abstract
        self.below_abstract = re.compile(r"(^\s?======abstract-start======\n?)([\s\S]*)", re.IGNORECASE | re.MULTILINE)
        # abstract between strings
        self.select_abstract = re.compile(r"(^\s?======abstract-start======\n)([\s\S]*?)(?=^\s======abstract-end======\n)", re.IGNORECASE | re.MULTILINE)
        # remove numeration
        self.rmv_num = re.compile(r"(\.[ ]\d)")

        # ======== Keywords =========
        # select keywords
        self.kws = re.compile(r"(^\s?======keywords-start======\n?)([\s\S]*)(?=^\s?======keywords-end======\n)", re.IGNORECASE | re.MULTILINE)

        # ======== References =========
        # get content below 'References' title
        self.ref_below = re.compile(r"(^\s?======references-start======\n?)([\s\S]*)", re.IGNORECASE | re.MULTILINE)
        # match [reference numbers]
        self.ref_numbers = re.compile(r"(\[)([0-9]+)(\])")
        # partition -> split reference string into references list
        self.ref_part = re.compile(r"(^{})(\d\d?)({})([\s\S]*?)(?=^{}\d\d?{})".format(self.m1, self.m2, self.m1, self.m2), re.IGNORECASE | re.MULTILINE)
        self.ref_split = re.compile(r"(?<=^{})([\s\S]*?)(?={})".format(self.m1, self.m2), re.IGNORECASE | re.MULTILINE)
        # truncate end reference content
        self.ref_truc = re.compile(r"^([\s\S]*?)(\.$)", re.IGNORECASE | re.MULTILINE)
        # get last reference (NOTE: after partition and split)
        self.ref_last = re.compile(r"(?<=^{})(\d\d?)({})([\s\S]*)(\.$)".format(self.m1, self.m2), re.IGNORECASE | re.MULTILINE)
        # match transposed text (ref numbers are above entries)
        # r_unnumbered = re.compile(r"(\])(\s+)(\[)" ) # find empty references
        # r_unnumbered = re.compile(r"((.|\n)*)(?!.*\1)(\.)") # find unnumbered references

        # ======== Categories =========
        # regex for categories
        self.cats = re.compile(r"""(categories and subject descriptors?)((.|\n)*?)(([1]\s*)?introduction|([1]\s*)?keywords)""", re.IGNORECASE)
        self.cat_code = re.compile(r"([A-Z]\.[0-9a-zA-Z](\.[0-9]|\.[a-z])?)")
        # ======== General Terms =========
        # match general terms
        self.gts = re.compile(r"(general terms)((.|\n)*)(keywords)", re.IGNORECASE)

        # ======== CCS 2012 =========
        # match ACM CCS 2012 concepts
        self.ccs_group_split = re.compile(r"""(, |; |\u2022)""")
        self.ccs_concept_split = re.compile(r"""(—|\u2012|\u2013|\u2014|\u2015|\u2192|:|\n|\*)( ?)(?=[A-Za-z])""")
        self.ccs = re.compile(r"""(^\s?======index-start======)([\s\S]*?)(?=^\s======index-end======)""", re.IGNORECASE | re.MULTILINE)


# instantiate paths
regex = Regex()
