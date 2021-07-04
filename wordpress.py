#!/usr/bin/env python3x

import requests

"""
===========================================
Wordpress
===========================================
Generates WordPress XML metadata

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
            wp_export_xml = utils.parse(
                "/Users/boutrous/Workspace/Metadata/GI/2020/input/index/WP_media_uploads.xml").getroot()
            wp_index = {'post_parent': wp_export_xml.xpath('//wp:post_parent',
                                                           namespaces={'wp': 'http://wordpress.org/export/1.2/'})[
                0].text}
            wp_posts = wp_export_xml.xpath('//item')
            for wp_post in wp_posts:
                wp_post_name = wp_post.xpath('wp:post_name', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
                wp_post_id = wp_post.xpath('wp:post_id', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
                wp_index[wp_post_name[0].text] = wp_post_id[0].text

            # Include WP metadata
            # -- deepcopy before data manipulation
            md_base_indexed = deepcopy(md_base)
            md_base_indexed['wp_post_parent'] = wp_index['post_parent']
            for j, md_session in enumerate(md_base['sessions']):
                for k, md_article in enumerate(md_session['articles']):
                    article_id = 'gi2020-' + md_article['number']
                    md_base_indexed['sessions'][j]['articles'][k]['wp_post_id'] = wp_index[article_id]
                    md_base_indexed['sessions'][j]['articles'][k]['wp_post_name'] = article_id

            # convert json metadata -> xml
            print("\n\nGenerating WordPress XML ... ")
            if not 'wordpress' in params.paths['templates']:
                print('Wordpress template is missing.')
                exit(1)
            xml_base = builder.transform(builder.build(md_base_indexed), params.paths['templates']['wordpress'])
            # Remove empty tags
            xml_base = builder.remove_empty(xml_base)
            utils.save(builder.build(md_base_indexed), '/Users/boutrous/Workspace/Metadata/GI/2020/build/test.xml')

            builder.validate(xml_base)
            utils.save(xml_base, os.path.join(output_path, output_id, output_id + ".xml"))

"""

def main():

    datacite_file = '/Users/boutrous/Workspace/Metadata/GI/2020/build/datacite/gi2020-01.xml'
    output_dir = '/Users/boutrous/Workspace/Metadata/GI/2020/build/datacite'
    with open(datacite_file) as fp:
       datacite_xml = fp.read()
    fp.close()

    url = "https://api.test.datacite.org/dois/id"

    headers = {"content-type": "application/vnd.api+json"}

    response = requests.request("PUT", url, headers=headers)

    print(response.text)


# Encapsulate in main()
if __name__ == "__main__":
    main()
    
    
# -- end of DataCite class --   