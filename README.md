# PDF Metadata Converter

##Overview
Simple tool to convert PDF document data into XML metadata for the ACM Digital Library

##Workflow

### Preprocessing PDF data

#### Add PDF article files


#### Create index CSV files to combine with PDF extraction
Initial index files will map already existing metadata to raw text extracted from
the PDF files using the Tika library. The header row of the CSV should contain the field names
to go in the final metadata. The extractor (*extractor.py*) merges the CSV metadata with
any useful data extracted from the PDF files and writes the data to files in *metadata* directory.

For the ACM metadata, there are three index files to create:
- Articles (*articles.csv*) TODO: (EndNote XML: *articles.xmk*)

- Sessions (*sessions.csv*)
-- Format:
--- section_seq_no
--- section_type
--- section_title
--- section_page_from

- Session Chairs (*session_chairs.csv*)
-- Format:
--- section_seq_no
--- person_id
--- author_profile_id
--- orcid_id
--- first_name
--- middle_name
--- last_name
--- suffix
--- affiliation
--- role

#### Complete file path index and base XML metadata template
- File paths index (*paths.json*)
- General conference metadata XML template (*base.xml*)

#### Process Session index files
1. Session index (*sessions.csv*)


2. Session Chair index (*session_chairs.csv*)


#### Complete Article index files
1. Article index (*articles.csv*)

#### Extract and compile article and session index Data
1. Run extractor '''python extractor.py [path to paths.json]'''


#### Run XML builder to convert and merge JSON extraction files
- Run *main.py* with the full path to *paths.json*.



2. **Dataset**

## Proceedings Articles



## Requirements

 - tqdm 4.31.1


## Usage

```
python main.py -h # prints usage help and configuration options
```

1. Data Extractor Preprocessing

```
python extractor.py <PATH file> # preprocess CSV and PDF data; converts to JSON metadata

```

2. Data Extractor Preprocessing

```
python main.py <PATH file> # preprocess CSV and PDF data; converts to JSON metadata
```

3. Metadata Converter

```
python main.py --mode train
python main.py -h # to view configuration options

```

4. Test model

```
python main.py --mode test
python main.py -h # to view configuration options
```

## Parameters

```
python main.py -h # prints usage help and configuration options
```

See Also: params.py for list of hyperparameters.

## References

[1] Du, Xinya, Junru Shao, and Claire Cardie. "Learning to ask: Neural question generation for reading comprehension." arXiv preprint arXiv:1705.00106 (2017).

### ACM Reference Format

<Index Terms>
	Categories/CCS 2012 Classification
</Index Terms>
<General Terms>...</General Terms>
<Keywords>...<.Keywords>
<References>
[1] ...
[2] ...
...
[n] ...
</References>

Example:

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
