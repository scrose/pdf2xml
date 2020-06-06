#!/usr/bin/env python3x

"""
===========================================
DOI Metadata Document (DataCite)
===========================================
Generates DataCite DOI Metadata files for REST API
"""


def main():

   datacite_file = '/Users/boutrous/Workspace/Metadata/GI/2019/DataCite/doi_metadata_gi2019.xml'
   output_dir = '/Users/boutrous/Workspace/Metadata/GI/2019/DataCite/'
   with open(datacite_file) as fp:
       datacite_xml = fp.read()
   fp.close()
   
   datacite_xml = datacite_xml.split('---BREAK---')
   i = 0
   for file_data in datacite_xml:
       print('Writing file {}'.format(i))
       # write xml to file 
       outfile = str(output_dir + 'GI2019-' + str(i).zfill(2) + '.xml')
       with open(outfile, 'w', encoding="utf-8") as fp:
           fp.write(file_data)
       fp.close()
       i += 1
            
# Encapsulate in main()
if __name__ == "__main__":
    main()
    
    
# -- end of DataCite class --   