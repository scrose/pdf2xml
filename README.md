# PDF Metadata Converter
Simple tool to convert PDF document data into XML metadata using XSL templates.

##Overview
Use this tool to extract unstructured text data from standard IEEE formatted papers (PDF files) to be filtered and exported to different formats, such as XML. Metadata extraction from PDF documents is stored in intermediate JSON files that can be exported to defined schemas using XSL templates. Extraction requires index files that map raw text scraped from the PDF files to known metadata.

## Required Index Files

1. Base Metadata (JSON)
   - Template: `base.json`
   - General information about the conference proceeding.
   - Sessions information
2. Articles Metadata (CSV)
   - Template: `articles.csv`
   - CSV index of articles in the proceeding.
3. File paths (JSON)
   - Template: `paths.json`
      
## Extraction

Using the Tika library, the extractor module (`extractor.py`) extracts text from the PDF documents and maps them 
using the index data to any useful data extracted from the PDF files and writes the data to intermediate JSON files. 
All input and output paths are defined in the `paths.json` index file.

#### Usage

`python main.py [FILEPATH paths.json] -[PHASE extract|update]`


## Build

Data in intermediate metadata files can be exported to XML using the builder module (`build.py`)
- Run *main.py* with the full path to *paths.json*.

#### Usage

`python main.py  -[PHASE build]`



# Requirements

 - tqdm 4.31.1


## Usage

1. Print help and configuration options
    ```
    python main.py -h # prints usage 
    ```

2. Extract data from sources

    ```
    python main.py [FILEPATH paths.json] -build -bits -extract
    ```

3. Build bridge metadata XML

    ```
    python main.py [FILEPATH paths.json] -update 
    ```

4. Generate XML from templates

    ```
    python main.py <path to paths.json> -build -bits
    python main.py <path to paths.json> -build -datacite
    python main.py <path to paths.json> -build -wordpress
    ```


### Metadata format

#### Example

C.2.1. Wireless communication; C.2.0. [General]: Security and protection General Terms
Security, Design
Internet of things,  link layer security,  key management, denial-of-service, denial-of-sleep
[1] E. C. Alexander, C.-C. Chang, M. Shimabukuro, S. Franconeri, C. Collins, and M. Gleicher. Perceptual biases in font size as a data encoding. IEEE Trans. Vis. Comput. Graphics, 2017.
[2] S. Bateman, C. Gutwin, and M. Nacenta. Seeing things in the clouds: The effect of visual features on tag cloud selections. In 19th ACM Conf. on Hypertext and Hypermedia, HT '08, pp. 193-202. ACM, 2008.
[3] M. Bostock, V. Ogievetsky, and J. Heer. D3 data-driven documents. IEEE Trans. Vis. Comput. Graph., 17(12):2301-2309, 2011.


## NOTES

- CCS Concepts and user-defined keywords are required for all articles over two pages in length, and optional for one- and two-page articles (or abstracts).
- The ACM Reference Format text is required for all articles over one page in length, and optional for one-page articles (abstracts).
- Ensure to populate the <publisher_article_url> to include external links to articles.
- Include front matter PDF and cover with the metadata file.
- PUB4613 should be entered as the <publisher_id>, not the <publisher_code>. Here’s how that section looks in the corrected .xml:
- The <article_publication_date> format is MM/DD/YYYY
- The <concept_id> of 10010147.1001037 was an invalid CCS path. I believe the correct one is 10010147.10010371
- The <fm_text> tag should not exceed the character limit.
- The <page_from> and <page_to> tags need to be populated even if the proceedings is not paginated (e.g. for a paper with 5 pages, I simply entered ‘1’ in <page_from> and ‘5’ in <page_to>; for a paper with 9 pages I went with 1-9)
- The <display_no> tag important if using article numbers (instead of page numbers). The <display_no> tag should be populated by ‘1’ for the first article, by ‘2’ for the second article, and so on.   
