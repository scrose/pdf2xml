#!/usr/bin/env python3
import os
from copy import deepcopy
from shutil import copyfile

import params
import utils
from tqdm import tqdm
from extractor import extractor
from params import params, Phases, Schema
from builder import builder

"""
===========================================
Metadata Processor
===========================================
Converts PDF documents to XML metadata
 * Applies ACM DL XML Schema
 * Dependencies:
   - lxml XML toolkit
   - Tika (Apache)

===========================================
"""


def main():
    # ===============================================
    # EXTRACTION or UPDATE phases
    # ===============================================
    if params.phase == Phases.EXTRACT or params.phase == Phases.UPDATE:
        # select input source (unprocessed or preprocessed)
        if params.phase == Phases.EXTRACT:
            input_source = params.get_files("articles", "input")
        else:
            input_source = params.get_files("txt", "output")

        # extract metadata from articles index CSV
        articles_md = extractor.csv(params.get_path("articles", "index"), "id")

        # extract metadata from PDF articles (Tika) / Raw text
        issues = 0
        for file in tqdm(input_source, desc="Data {}:".format(params.phase.name)):
            # get reference ID from CSV filename
            file_id = utils.get_id(file)
            # extract raw text from PDF file or use existing raw text
            content = extractor.pdf(file) if params.phase == Phases.EXTRACT else extractor.txt(file)
            data = extractor.merge(file_id, articles_md, content)

            # save processed metadata to file
            extractor.save(data, os.path.join(params.get_path("articles", "metadata"), file_id + ".json"))
            issues += extractor.generate_patch(data, content)

        print('\nParsing errors/issues found: {}'.format(issues))

    # ===============================================
    # BUILD phase
    # ===============================================
    elif params.phase == Phases.BUILD or params.phase == Phases.PATCH:

        # get article metadata
        article_files = params.get_files('articles', 'metadata')

        # collate metadata from extractor
        md_base = utils.collate(
            params.get_path('base', 'metadata'),
            article_files,
            params.get_path('patches', 'output')
        )

        # utils.save(builder.build(md_base), '/Users/boutrous/Workspace/Metadata/GI/2020/build/test.xml')
        # Apply ACM schema (BITS format)
        if params.schema == Schema.BITS:
            # get ACM object ID
            base_id = md_base['publication']['acm_id']
            # Format: acmotherconferences_objectID_yyyymmdd (zipped)
            # root_dir = "{}_{}_V{}".format(md_base['conference']['code'], base_id, params.datestamp)
            root_dir = "acmotherconferences_{}_{}".format(base_id, params.datestamp)
            base_dir = base_id
            output_path = params.get_path("build", "output")
            # create root directory
            utils.mk_dir(output_path, root_dir)
            # create manifest
            print("\n====\nGenerating manifest ... ")
            xml_manifest = builder.transform(builder.build(md_base), params.get_path("manifest", "templates"))
            utils.save(xml_manifest, os.path.join(output_path, root_dir, "manifest.xml"))
            # build base XML from metadata and apply XSLT
            print("\n====\nGenerating base XML ... ")
            utils.mk_dir(output_path, root_dir, base_dir)
            utils.mk_dir(output_path, root_dir, base_dir, base_dir)
            xml_base = builder.transform(builder.build(md_base), params.get_path("base", "templates"))
            # Remove empty tags
            xml_base = builder.remove_empty(xml_base)
            builder.validate(xml_base)
            utils.save(xml_base, os.path.join(output_path, root_dir, base_dir, base_dir, base_id + ".xml"))
            # Copy front-matter (if provided) to base directory
            fm_src_path = params.get_path("front-matter", "input")
            if fm_src_path:
                fm_filename = md_base['publication']['front_matter']['uri']
                fm_dst_path = os.path.join(output_path, root_dir, base_dir, base_dir, fm_filename)
                copyfile(fm_src_path, fm_dst_path)
            # Generate article xml documents and validate
            for md_session in md_base['sessions']:
                for md_article in md_session['articles']:
                    print("\n====\nGenerating article {} ... ".format(md_article['doi']))
                    article_doi = "{}.{}".format(base_id, md_article['doi'])
                    # create article directory
                    utils.mk_dir(output_path, root_dir, base_dir, article_doi)
                    # attach base metadata fields to metadata
                    md_article['conference'] = md_base['conference']
                    md_article['publication'] = md_base['publication']
                    # convert article metadata to XML
                    xml_article = builder.transform(builder.build(md_article), params.get_path("article", "templates"))
                    # Remove empty tags
                    xml_article = builder.remove_empty(xml_article)
                    # validate against schema
                    builder.validate(xml_article)
                    # save article output
                    utils.save(xml_article,
                               os.path.join(output_path, root_dir, base_dir, article_doi, article_doi + ".xml"))
                    # save raw xml generated
                    utils.save(builder.build(md_article), os.path.join(params.get_path("xml", "output"), article_doi + ".xml"))
                    # DEBUG: create intermediate XML metadata file
                    # xml_external = builder.transform(builder.build(md_base), params.get_path("external", "templates"))
                    # utils.save(xml_external, os.path.join(params.get_path("output"), root_dir, article_doi + ".xml"))

        # Apply DataCite schema
        elif params.schema == Schema.DATACITE:
            # Format: datacite_[conference series slug]_[datestamp]
            base_id = md_base['conference']['series'].replace(' ', '_')
            root_dir = "datacite_{}_{}".format(base_id, params.datestamp)
            output_path = params.get_path("build", "output")
            patches_path = params.get_path('patches', 'output')
            # create root directory
            utils.mk_dir(output_path, root_dir)
            # Generate article xml documents and validate
            for md_article_file in params.get_files('articles', 'metadata'):
                # Apply patch (if exists)
                md_article = utils.apply_patch(md_article_file, patches_path)
                article_id = md_article['id']
                print("\n====\nGenerating article {} ... ".format(article_id))
                # attach base metadata fields to metadata
                md_article['conference'] = md_base['conference']
                md_article['publication'] = md_base['publication']
                md_article['publisher'] = md_base['publisher']
                # convert article metadata to XML
                xml_article = builder.transform(builder.build(md_article), params.get_path("datacite", "templates"))
                # Remove empty tags
                xml_article = builder.remove_empty(xml_article)
                # validate against schema
                builder.validate(xml_article)
                # save article output
                utils.save(xml_article, os.path.join(output_path, root_dir, article_id + ".xml"))
                # save raw xml generated
                utils.save(builder.build(md_article),
                           os.path.join(params.get_path("xml", "output"), article_id + ".xml"))

        # Apply WordPress RSS schema
        elif params.schema == Schema.WORDPRESS:
            # Format: wp_[conference series slug]_[datestamp]
            base_id = md_base['conference']['series'].replace(' ', '_')
            output_id = "wp_{}_{}".format(base_id, params.datestamp)
            output_path = params.get_path("build", "output")
            # create root directory
            utils.mk_dir(output_path, output_id)
            # set timestamp in metadata
            md_base['timestamp'] = params.timestamp
            md_base['post_date'] = params.postdate

            # load Wordpress XML Export data
            wp_export_xml = utils.parse("/Users/boutrous/Workspace/Metadata/GI/2020/input/index/WP_media_uploads.xml").getroot()
            wp_index = {'post_parent': wp_export_xml.xpath('//wp:post_parent', namespaces={'wp': 'http://wordpress.org/export/1.2/'})[0].text}
            wp_posts = wp_export_xml.xpath('//item')
            for wp_post in wp_posts:
                wp_post_name = wp_post.xpath('wp:post_name', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
                wp_post_id = wp_post.xpath('wp:post_id', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
                wp_index[wp_post_name[0].text] = wp_post_id[0].text

            # Include WP metadata
            # deepcopy before data manipulation
            md_base_indexed = deepcopy(md_base)
            md_base_indexed['wp_post_parent'] = wp_index['post_parent']
            for j, md_session in enumerate(md_base['sessions']):
                for k, md_article in enumerate(md_session['articles']):
                    article_id = 'gi2020-' + md_article['number']
                    md_base_indexed['sessions'][j]['articles'][k]['wp_post_id'] = wp_index[article_id]
                    md_base_indexed['sessions'][j]['articles'][k]['wp_post_name'] = article_id

            # convert json metadata -> xml
            print("\n====\nGenerating WordPress XML ... ")
            xml_base = builder.transform(builder.build(md_base_indexed), params.get_path("wordpress", "templates"))
            # Remove empty tags
            xml_base = builder.remove_empty(xml_base)
            utils.save(builder.build(md_base_indexed), '/Users/boutrous/Workspace/Metadata/GI/2020/build/test.xml')

            builder.validate(xml_base)
            utils.save(xml_base, os.path.join(output_path, output_id, output_id + ".xml"))

        else:
            print('Schema {} not found or enabled.'.format(params.schema))
            exit(1)

        print('Build completed.')


# Encapsulate in main()
if __name__ == "__main__":
    main()
