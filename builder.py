#!/usr/bin/env python3x

"""
===========================================
XML builder
===========================================
Converts JSON metadata to schematized XML
"""
import lxml
import lxml.etree as et
from params import params, Schema
import utils


class XMLBuilder:

    def __init__(self):
        self.parser = et.XMLParser(remove_blank_text=True)
        # initialize schema
        if params.schema:
            print('Initializing builder schema...'.format(params.schema), end='')
            if params.schema == Schema.BITS:
                self.schema = lxml.etree.XMLSchema(et.parse(params.get_path("bits", "schema")))
            elif params.schema == Schema.DATACITE:
                self.schema = lxml.etree.XMLSchema(et.parse(params.get_path("datacite", "schema")))
            elif params.schema == Schema.WORDPRESS:
                self.schema = lxml.etree.XMLSchema(et.parse(params.get_path("wordpress", "schema")))
            print('done.')

    # ----------------------------------------
    # Build XML from metadata (JSON-format)
    def build(self, data):
        root = et.Element('root')
        # convert JSON metadata -> XML
        self._build_node(data, root)
        return root

    # ----------------------------------------
    # Build XML node (helper function)
    def _build_node(self, data, tree):
        # list subtree
        if data and type(data) == list:
            for e in data:
                if e:
                    # create new element to contain sub-elements
                    node = et.SubElement(tree, params.element_name)
                    # text or empty value
                    if type(e) == str:
                        utils.process(e, node)
                    # node value
                    else:
                        self._build_node(e, node)
        # dict subtree
        elif data and type(data) == dict:
            for k, e in data.items():
                # empty nodes
                if not e:
                    # include selected empty nodes
                    if type(params.empty_nodes) == list:
                        if k in params.empty_nodes:
                            et.SubElement(tree, str(k))
                    # include all empty nodes
                    elif params.empty_nodes == 'any':
                        et.SubElement(tree, str(k))
                    else:
                        continue
                # non-empty nodes
                else:
                    node = et.SubElement(tree, str(k))
                    # text or empty value
                    if type(e) == str or type(e) == int:
                        utils.process(e, node)
                    # node value
                    else:
                        self._build_node(e, node)

    # ----------------------------------------
    # remove empty nodes from output tree
    def remove_empty(self, tree):
        # nodes that are recursively empty
        context = et.iterwalk(tree)
        for action, node in context:
            parent = node.getparent()
            if self._recursively_empty(node):
                parent.remove(node)
        return tree

    # ----------------------------------------
    # Remove empty nodes from node tree (helper function)
    def _recursively_empty(self, node):
        if node.text or node.tag in params.empty_nodes:
            return False
        return all((self._recursively_empty(c) for c in node.iterchildren()))

    # --------------------------------------
    # Apply input XSLT template (see paths.json)
    def transform(self, xml_data, xslt_path):
        # load configured XSLT stylesheet
        xslt_root = et.parse(xslt_path)
        _transform_ = et.XSLT(xslt_root)
        # xml = et.parse(xml_data, parser=self.parser).getroot()
        result = None
        try:
            result = _transform_(xml_data)
        except:
            for error in _transform_.error_log:
                print(error.message, error.line)

        return result

    # ----------------------------------------
    # validate document against XSD schema (see paths.json)
    def validate(self, xml_data):
        validation = self.schema.validate(xml_data)
        msg = 'VALID' if validation else 'NOT VALID'
        print("XSD Validation: {}".format(msg))
        # show validation errors
        if len(self.schema.error_log):
            print('\n-------------------\nERROR LOGS:')
            print(self.schema.error_log.last_error)
            print()


# -- end of Builder class --
builder = XMLBuilder()
