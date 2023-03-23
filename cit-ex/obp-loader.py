#!/usr/bin/env python3
'''
This file is part of cit-ex

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import requests
import json
import subprocess
import tempfile
from urllib.parse import urljoin

from ebooklib import epub


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("doi", type=str,
                        help="Work DOI")
    parser.add_argument("--dry-run", action='store_true',
                        help="Perform a dry run: no data would be sent to "
                             "metadata repositories.")
    args = parser.parse_args()

    # get chapter data
    query = query_thoth(urljoin("https://doi.org/", args.doi))
    chapters = get_chapters(query)

    # add bibliography section (if any) to chapter list
    try:
        bib_url = urljoin(chapters[0].get("html_page"), "bibliography.xhtml")
    except IndexError:
        pass
    else:
        r = requests.get(bib_url)
        if r.status_code == 200:
            chapters.append({"doi": args.doi, "html_page": bib_url})

    # create an epub for each chapter and run it through cit-ex
    for chapter in chapters:
        with tempfile.NamedTemporaryFile() as epub_file:
            create_epub(chapter.get("html_page"), epub_file.name)

            cmd = f"python3 main.py {epub_file.name} " \
                  f"-c bibliography-first-para bibliography-other-para " \
                  f"-i {chapter.get('doi')}"
            print(f"Executing: `{cmd}`")
            if not args.dry_run:
                subprocess.check_output(cmd.split())


def query_thoth(book_doi: str) -> str:
    """This method queries Thoth to get the landingPage URLs of the HTML
       edition of each chapter of the book"""
    url = 'https://api.thoth.pub/graphql'
    query = {"query": "{ workByDoi (doi: \"%s\") { \
                           relations (relationTypes: HAS_CHILD) { \
                              relatedWork { \
                                doi \
                                publications (publicationTypes: HTML) { \
                                  locations { \
                                    landingPage \
                                  } \
                                } \
                              } \
                           } \
                         } \
                        }" % book_doi}

    # handle connection issues
    try:
        r = requests.post(url, json=query)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return json.loads(r.text)


def get_chapters(thoth_data: str) -> list:
    """This method extracts data from a Thoth query
       and returns a list of dictionaries with landingPage and DOI
       of each chapter"""
    try:
        relations = thoth_data["data"]["workByDoi"]["relations"]
    except TypeError:
        print('The graphql query did not produce a valid response.',
              'thoth_data["data"]["workByDoi"]["relations"] not found.')
        raise

    chapters = []
    for relation in relations:
        doi = relation.get("relatedWork", {}).get("doi", None)

        try:
            html = relation.get("relatedWork", {}).get("publications", {})[0] \
                           .get("locations", {})[0].get("landingPage", None)
        except IndexError:
            raise IndexError(f"No html data for relation {relation}.")

        if (doi is not None) and (html is not None):
            chapters.append({"doi": doi, "html_page": html})

    return chapters


def create_epub(url: str, epub_file_path: str) -> None:
    """This method creates an EPUB with the HTML page (URL) specified in the
       argument"""
    r = requests.get(url)

    book = epub.EpubBook()

    chapter = epub.EpubHtml(title="Chapter", file_name="chapter.xhtml",
                            lang="en-gb")
    chapter.content = r.text.encode()
    book.add_item(chapter)

    book.toc = (epub.Link("chapter.xhtml", "Chapter", "ch"),
                (epub.Section("Book"),
                (chapter, ))
                )

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(epub_file_path, book, {})


if __name__ == "__main__":  # pragma: no cover
    main()
