# cit-ex 
A tool to extract citation data from EPUBs and upload it to a metadata repository.

_cit-ex_ parses EPUB files looking for all the bibliographic references that match the html class(es) defined at prompt. 
These, in turn, get parsed for more granular results and then uploaded to a metadata of choice.

As of v.0.0.1, the unstructured citations are parsed to find only DOI data and the only metadata repository supported is [Thoth](https://thoth.pub/)

## Installation

Firstly, you need to initialise a virtual envieronment:

$ `cd path/to/the/cit-ex/folder/`

$ `python3 -m venv .env`

Then, install the required dependencies:

(.env) $ `python3 -m pip install -r requirements.txt`


## Usage example

Given that your epub file is stored at _~/file.epub_ and the bibliographic references are marked with an HTML class _biblio_ in the EPUB:

(.env) $ `python3 cit-ex/main.py ~/file.epub -c biblio --dry-run`

If your references are marked either as _biblio_ and _biblio2_

(.env) $ `python3 cit-ex/main.py ~/file.epub -c biblio biblio2 --dry-run`

### Usage example with Thoth

Make sure your login credentials are stored in the environment variables "THOTH_EMAIL" and "THOTH_PWD". 
You also need to know the identifier (either its DOI or UUID) of the work you with to append the citation data to.

Given that these pre-requisites are satisfied and your identifier is _10.11647/OBP.0288_, you can run the command:

(.env) $ `python3 cit-ex/main.py ~/file.epub -c biblio biblio2 -i 10.11647/OBP.0288 -r thoth`

## Development setup

On top of the steps listed in "Installation", install the dev dependencies with:

(.env) $ `python -m pip install -r requirements-dev.txt`

## Extra packages

### OBP loader
The file `cit-ex/obp-loader.py` is an OBP-specific wrapper to load chapter-level citations to the repository (Thoth).

It relies on each book chapter to report the URL of their HTML edition. This file is downloaded, embedded into an EPUB and finally run through _cit-ex_.

The wrapper runs with:

(.env) $ `python3 obp-loader.py 10.11647/obp.0085`

where "10.11647/obp.0085" is the DOI of the book to be parsed.

#### Run OBP loader with Docker

Clone the repository and build the image with:

$ `docker build . -f Dockerfile-obp-loader -t openbookpublishers/cit-ex-obp-loader`

Deploy a container with:

```
docker run --rm \
           -e THOTH_EMAIL=$THOTH_EMAIL \
           -e THOTH_PWD=$THOTH_PWD \
           openbookpublishers/cit-ex-obp-loader \
           obp-loader.py 10.11647/obp.0337

```

Where `$THOTH_EMAIL` and `$THOTH_PWD` are your thoth credentials and 10.11647/obp.0337 is the book-level DOI you wish to process.