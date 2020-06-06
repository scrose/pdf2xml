#!/usr/bin/env python3x

"""
===========================================
XML data builder
===========================================
Assimilates CSV and PDF raw data into ACM DL XML metadata
"""

import glob
import json
import re
import lxml.etree as et
from params import params, Phases

class XMLBuilder:

    def __init__(self):
        self.parser = et.XMLParser(remove_blank_text=True)

        # create base XML from template
        self.root = et.parse(params.get_path('template'), self.parser).getroot()

        # initialize tree
        self.tree = None

    # ----------------------------------------
    # Recursively build using JSON object as DOM tree
    def build(self, data):
        tree = et.Element('content')
        self._build_node(data, tree)
        self.tree = tree
    # ----------------------------------------
    # Build XML node
    def _build_node(self, data, tree):
        # list subtree
        if data and type(data) == list:
            # check if descendents
            # copy parent tagname then remove parent element
            tag_name = tree.tag
            tree_parent = tree.getparent()
            tree_parent.remove(tree)
            tree = tree_parent
            for e in data:
                if e:
                    node = et.SubElement(tree, tag_name)
                    # text or empty value
                    if type(e) == str:
                        self.process_value(e, node)
                    # node value
                    else:
                        self._build_node(e, node)
        # dict subtree
        elif data and type(data) == dict:
            for k, e in data.items():
                # include selected empty nodes
                if k in params.empty_nodes:
                    et.SubElement(tree, str(k))
                # non-empty nodes
                elif e:
                    node = et.SubElement(tree, str(k))
                    # text or empty value
                    if type(e) == str or type(e) == int:
                        self.process_value(e, node)
                    # node value
                    else:
                        self._build_node(e, node)


    # ----------------------------------------
    # process terminal node text values
    def process_value(self, val, node):
        if (val):
            # val = h.unescape(val)
            if (node.tag=='article_type'):
                node.set('art_type', "regular_article")
                return
            # encode uris
            elif (node.tag =='publisher_article_url' or \
                node.tag == 'publisher_url' or node.tag == 'conference_url' or node.tag == 'url'):
                node.text = val.replace("&", "%26")
                return
            # elif ( node.tag =='display_no' ):
            #     node.text = ''
            #     return
            elif (node.tag=='qualifiers'):
                node.getparent().set(node.tag,val)
                return
            node.text = str(val)
        return


    # ----------------------------------------
    # remove empty nodes from output tree
    def remove_empty(self):
        # nodes that are recursively empty
        context = et.iterwalk(self.root)
        for action, node in context:
            parent = node.getparent()
            if self.recursively_empty(node):
                parent.remove(node)
    # ----------------------------------------
    def recursively_empty(self, node):
        if node.text or node.tag in params.empty_nodes:
            return False
        return all((self.recursively_empty(c) for c in node.iterchildren()))


    # ----------------------------------------
    # validate document against DTD provided
    def validate(self):
        dtd = et.DTD(params.get_path('dtd'))
        result = 'VALID' if dtd.validate(self.root) else 'NOT VALID'
        print("\n\nDTD Validation Result: {}\n-------------------".format(result))
        if (len(dtd.error_log.filter_from_errors())):
            print(dtd.error_log.filter_from_errors()[0])


    # ----------------------------------------
    # print xml to stdout
    def print(self):
        print(et.tostring(self.root, xml_declaration=True, pretty_print=True, doctype='<!DOCTYPE proceeding SYSTEM "proceeding.dtd">'))



    # ----------------------------------------
    # write XML tree to file (params.path)
    def save(self):
        outfile = params.outfile
        print("Writing XML tree to outpath file path: {}".format(outfile))
        try:
            with open(outfile, "w", encoding="utf-8") as fp:
                print("Processing character corrections ... ", end='')
                content = self.clean_up(et.tostring(self.root,
                                           encoding='ascii',
                                           xml_declaration=False,
                                           pretty_print=True,
                                           doctype='<!DOCTYPE proceeding SYSTEM "proceeding.dtd">').decode())
                print("done.")

                print("Saving to file {} ... ".format(outfile), end='')
                fp.write(content)
                fp.close()
                print("done.")

                # validate xml against dtd
                builder.validate()
                print("Completed.")

        except Exception as e:
            print ( "Error: Problem with output file {}:\n{}".format(outfile, e) )



    # ----------------------------------------
    # clean up OCR, special char entities, and various errors/typos
    def clean_up(self, content):

        # Replace double/single quotes NOT in tags with HTML entity
        regex1a = re.compile(r"(\")(?=[^>]*<)")
        regex1b = re.compile(r"(\')(?=[^>]*<)")

        # OCR: Replace LATIN SMALL LIGATURE FI with "fi"
        regex2 = re.compile(r"(&#64257;)")

        # OCR: Replace LATIN SMALL LIGATURE FL with "fl"
        regex3 = re.compile(r"(&#64258;)")

        # clean up xml text
        content = regex1a.sub("&#34;", content)
        content = regex1b.sub("&#39;", content)
        content = regex2.sub("fi", content)
        content = regex3.sub("fl", content)

        # replace special unicode entities
        content = content.replace("&#8216;", "&#39;")
        content = content.replace("&#8217;", "&#39;")
        content = content.replace("&#8220;", "&#34;")
        content = content.replace("&#8221;", "&#34;")
        content = content.replace("&#8211;", "-")
        content = content.replace("&#8212;", "-")
        content = content.replace("&#9632;", "")
        content = content.replace("&#8226;", "-")

        return content


# -- end of MetaDoc class --
builder = XMLBuilder()
