#!/usr/bin/env python3x

"""
===========================================
Utilities
===========================================
"""
import os
import re
import json
import lxml.etree as et
from tqdm import tqdm


# ----------------------------------------
# process terminal node text values
def process(val, node):
    if val:
        # Encode/escape urls
        if node.tag == 'publisher_article_url' \
                or node.tag == 'publisher_url' \
                or node.tag == 'conference_url' \
                or node.tag == 'url':
            node.text = val.replace("&", "%26")
            return
        node.text = str(val)
    return


# ----------------------------------------
# write XML tree to file (params.path)
def save(xml_data, outfile):
    # get doctype metadata
    # - public_id
    # - sysurl
    # - doctype (full declaration)
    if hasattr(xml_data, 'docinfo'):
        docinfo = xml_data.docinfo
        doctype = docinfo.doctype
    else:
        doctype = '<!DOCTYPE root SYSTEM "proceeding.dtd">'

    try:
        with open(outfile, "w", encoding="utf-8") as fp:
            print("Processing character corrections ... ", end='')
            content = clean(et.tostring(xml_data,
                                        encoding='ascii',
                                        xml_declaration=True,
                                        pretty_print=True,
                                        doctype=doctype).decode())
            print("done.")

            print("Saving XML to file {} ... ".format(outfile), end='')
            fp.write(content)
            print("done.")

    except Exception as e:
        print("Error: Problem with output file {}:\n{}".format(outfile, e))


# ----------------------------------------
# clean up OCR, special char entities, and various errors/typos
def clean(content):

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


def collate(md_base_path, md_articles_path, md_patches_path):

    # load metadata
    data = load_json(md_base_path)
    n_sessions = len(data['sessions'])
    # validate metadata has sessions stub
    assert 'sessions' in data and type(data['sessions']) is list, 'Invalid base metadata.'

    # collate article/session metadata in common data node
    for md_file in tqdm(md_articles_path, desc="Collating Metadata: "):
        # load article metadata / apply patch fix (if exists)
        md_article_data = apply_patch(md_file, md_patches_path)
        # get session sequence number
        session_idx = int(md_article_data['session']) - 1
        assert session_idx < n_sessions, 'Invalid session sequence number: {}'.format(session_idx)
        # add articles list to session, if needed
        if 'articles' not in data['sessions'][session_idx]:
            data['sessions'][session_idx]['articles'] = []
        # add article metadata to corresponding session
        data['sessions'][session_idx]['articles'] += [md_article_data]

    return data


# --------------------------------------
# Apply patches to data object
def apply_patch(md_file, patches_path=None):
    # load metadata
    md_data = load_json(md_file)
    # apply patch (if exists)
    if patches_path:
        file_id = get_id(md_file)
        patch_file = os.path.join(patches_path, file_id + ".json")
        if os.path.isfile(patch_file):
            print("Using patch for file ID {} ... ".format(file_id))
            patch = load_json(patch_file)
            for field in patch.keys():
                if field in md_data:
                    md_data[field] = patch[field]
    return md_data


# --------------------------------------
# Extract ID from filename
def get_id(file):
    return os.path.splitext(os.path.basename(file))[0]


# --------------------------------------
# Extract ID from filename
def get_filetype(file):
    return os.path.splitext(os.path.basename(file))[1].replace('.', '')


# --------------------------------------
# Extract filesize from file path [kB]
def get_filesize(file_path):
    return int(os.path.getsize(file_path) / 1000)


# --------------------------------------
# Create subdirectory in path
def mk_dir(path, *subdir):
    path = os.path.join(path, *subdir)
    if not os.path.isdir(path):
        os.mkdir(path)


# --------------------------------------
# get metadata
def load_json(path):
    with open(path) as fp:
        return json.load(fp)


# ----------------------------------------
# parse XML file -> etree object
def parse(xml_path):
    return et.parse(xml_path)


# --------------------------------------
# print node tree to stdout
def print_tree(root):
    print(et.tostring(root, pretty_print=True))

# -- end of Utilities --
