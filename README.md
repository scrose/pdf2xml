# PDF Metadata Converter

Tool to extract and convert PDF document data into XML metadata that can be restructured using XSL templates.

## Overview

Use this tool to extract unstructured text data from standard IEEE formatted conference papers (PDF files) to be filtered and exported to different formats, such as BITS or WordPress XML data. Metadata extraction from PDF documents is stored in intermediate JSON and XML files that can be exported to defined schemas using XSL templates. Extraction requires index files that map raw text scraped from the PDF files to known metadata.

## Input Index Files

In addition to the PDF documents to be extracted, three different input index files are required to use this tool. Example index files can be found in the `input` folder.

1. `paths.json`: Provides paths to the PDF articles, the output paths, as well as `base.json` and `articles.csv`. Use the template provided in the source root.
2. `base.json`: Base Metadata (JSON) to provide general information about the conference proceeding and sessions.
3. `articles.csv`: Articles Metadata (CSV) to provide an index of articles, authors and affiliations in the proceeding.


## Extractor Tool

Using the Tika library, the extractor module (`extractor.py`) extracts text from the PDF documents and maps them
using the index data to any useful data extracted from the PDF files and writes the data to intermediate JSON files.
All input and output paths are defined in the `paths.json` index file.

The following folders are generated for saved output. The output paths are defined in `paths.json` configuration file.

1. Extraction
   - `articles`: JSON metadata files generated for each PDF article.
   - `xml`: XML metadata files generated for each PDF article.
   - `logs`: Error logs for issues found during extraction.
   - `patches`: Overwrite the generated metadata by making updated copies of JSON metadata files here.
   - `txt`: The raw text generated from the PDF extraction.

### Usage

`python main.py [FILEPATH paths.json] -extract`

## Updater Tool

Raw extracted data can be edited and updated by running the update tool. Edit the raw text directly and run the updater to regenerate the JSON metadata files. Alternatively, edit the

### Usage

```
python main.py [FILEPATH paths.json] -update
```

## Builder Tool

Data in intermediate metadata files generated through extraction can be exported to XML using the builder module (`build.py`). This module has three defined schema options.

### Available Schemas

The following schemas are available, however this package can be extended to include other schemas using an XSL stylesheet and a valid XSD schema definition for validation.

1.  [BITS - Book Interchange Tag Set: JATS Extension] (https://jats.nlm.nih.gov/extensions/bits/) Generates XML metadata for the ACM proceeding Digital Library using BITS schema.. The intent of the BITS is to provide a common format in which publishers and archives can exchange book content, including book parts such as chapters. The Suite provides a set of XML schema modules that define elements and attributes for describing the textual and graphical content of books and book components as well as a package for book part interchange.
2.  [DataCite - Metadata for DOIs] (https://schema.datacite.org/) Generates DataCite metadata XML files for each article. The DataCite Metadata Schema is a list of core metadata properties chosen for an accurate and consistent identification of a resource for citation and retrieval purposes, along with recommended use instructions.
2.  [WordPress - Importer XML Schema] (https://wordpress.org/support/article/importing-content/) Generates WordPress import XML from extracted data. Using the WordPress Import tool, you can import content into your site using this schema option.

### Usage

```
python main.py <path to paths.json> -build -bits
python main.py <path to paths.json> -build -datacite
python main.py <path to paths.json> -build -wordpress
```
