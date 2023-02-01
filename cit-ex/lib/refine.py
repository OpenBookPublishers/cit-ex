from dataclasses import dataclass
import datetime
import re
from urllib.parse import urljoin

from crossref.restful import Works


@dataclass
class Citation:
    unstructured_citation: str = None
    doi: str = None
    doi_url: str = None
    reference_id: str = None
    work_id: str = None
    reference_ordinal: int = None
    issn: str = None
    isbn: str = None
    journal_title: str = None
    article_title: str = None
    series_title: str = None
    volume_title: str = None
    edition: str = None
    author: str = None
    volume: str = None
    issue: str = None
    first_page: str = None
    component_number: str = None
    standard_designator: str = None
    standards_body_name: str = None
    standards_body_acronym: str = None
    url: str = None
    publication_date: str = None
    retrieval_date: str = None

    def process_doi(self, doi):
        """Assign a value to self.doi and populate the self.doi_url field"""
        self.doi = doi
        if doi is not None:
            self.doi_url = urljoin("https://doi.org/", doi)


class Refine():
    """Class to process unstructured citations.
       The method get_citation returns a Citation object to (hopefully) ease
       further processing via dependency injection."""
    def __init__(self, unstructured_citation: str) -> None:
        self.cit = Citation(unstructured_citation=unstructured_citation)
        self.work = None

    def find_doi_match(self, unstructured_citation: str) -> str:
        """Search the unstructured citation for a valid DOI and return it"""
        # Syntax of a DOI https://www.doi.org/doi_handbook/2_Numbering.html#2.2
        doi_regex = r"(10\.\d{3,6}\/\S*?)[,.;]?(?:\s|\Z)"
        result = re.search(doi_regex, unstructured_citation)
        if result is not None:
            return result.group(1)
        return None

    def _is_valid_doi(self, doi: str) -> bool:
        """This method tests whether a DOI is valid/exists"""
        self.work = Works().doi(doi)
        if self.work is not None:
            return True
        return False

    def process_crossref_data(self) -> None:
        """"This method parses the result of crossref query and feeds into
            the Citation object."""

        # DOI
        self.cit.doi = self.work.get("DOI")
        self.cit.doi_url = self.work.get("URL")

        # ISSN
        try:
            self.cit.issn = self.work.get("ISSN", [])[0]
        except IndexError:
            pass
        else:  # if part of a series
            # Series name
            try:
                self.cit.series_title = self.work.get("container-title", [])[0]
            except IndexError:
                pass

        # ISBN
        try:
            self.cit.isbn = self.work.get("isbn-type", [])[0].get("value")
        except IndexError:
            pass

        # Edition
        self.cit.edition = self.work.get("edition-number")

        # Authors
        authors = []
        for author in self.work.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            authors.append(" ".join(filter(None, [given, family])))
        if len(authors) > 0:
            self.cit.author = "; ".join(authors)

        # URL
        self.cit.url = self.work.get("resource", {}).get("primary", {}) \
                                .get("URL")

        # Publication Date
        try:
            date_parts = self.work.get("issued", {}).get("date-parts", [])[0]
        except IndexError:
            pass
        else:
            date = datetime.datetime(*date_parts)
            self.cit.publication_date = date.strftime("%Y-%m-%d %H:%M:%S")

        # If book
        if self.work.get("type") in ["monograph", "edited-book"]:
            try:
                self.cit.volume_title = self.work.get("title", [])[0]
            except IndexError:
                pass

        # If book chapter
        elif self.work.get("type") == "book-chapter":
            # Chapter title
            try:
                self.cit.article_title = self.work.get("title", [])[0]
            except IndexError:
                pass

            # Book (container) title
            try:
                self.cit.volume_title = self.work.get(
                                               "container-title", [])[-1]
            except IndexError:
                pass

            # First page
            try:
                self.cit.first_page = self.work.get("page").split("-")[0]
            except AttributeError:
                pass

        # if journal
        elif self.work.get("type") == "journal-article":
            # Journal title
            try:
                self.cit.journal_title = self.work.get(
                                               "container-title", [])[-1]
            except IndexError:
                pass

            # Article title
            try:
                self.cit.article_title = self.work.get("title", [])[0]
            except IndexError:
                pass

            # Volume number
            self.cit.volume = self.work.get("volume")

            # Issue
            self.cit.issue = self.work.get("issue")

            # First page
            try:
                self.cit.first_page = self.work.get("page").split("-")[0]
            except AttributeError:
                pass

    def get_citation(self) -> Citation:
        """Return a Citation object with the data gathered"""
        return self.cit
