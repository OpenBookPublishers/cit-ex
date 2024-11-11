from dataclasses import dataclass
import datetime
import re
import requests
from urllib.parse import urljoin

import backoff
from crossref.restful import Works, Etiquette


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
    edition: int = None
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
    def __init__(self, unstructured_citation: str, doi: str = None,
                 email: str = "no-email@offered.org") -> None:
        self.cit = Citation(unstructured_citation=unstructured_citation)

        self.work = None
        if doi is not None:
            try:
                self.work = self._get_work_by_doi(doi, email)
            except requests.exceptions.HTTPError:
                pass

    @staticmethod
    def find_doi_match(unstructured_citation: str) -> str:
        """Search the unstructured citation for a valid DOI and return it"""
        # Syntax of a DOI https://www.doi.org/doi_handbook/2_Numbering.html#2.2
        doi_regex = r"(10\.\d{3,6}\/\S*?)[,.;]?(?:\s|\Z)"
        result = re.search(doi_regex, unstructured_citation)
        if result is not None:
            return result.group(1)
        return None

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.HTTPError,
                          max_time=60, max_tries=3)
    def _get_work_by_doi(self, doi: str, email: str) -> dict:
        """This method queries Crossref and returns a dictionary with
           the result"""
        my_etiquette = Etiquette('cit-ex', '0.0.9', 'https://github.com/'
                                 'OpenBookPublishers/cit-ex', email)
        return Works(etiquette=my_etiquette).doi(doi)

    def _is_valid_doi(self) -> bool:
        """This method tests whether a DOI is valid/exists"""
        if self.work is not None:
            return True
        return False

    def get_issn(self) -> str:
        """Get ISSN from self.work"""
        try:
            return self.work.get("ISSN", [])[0]
        except IndexError:
            return None

    def get_series_title(self) -> str:
        """Get series title from self.work"""
        if self.cit.issn is not None:
            try:
                return self.work.get("container-title", [])[0]
            except IndexError:
                return None

    def get_isbn(self) -> str:
        """Get ISBN from self.work"""
        isbn = None
        for entry in self.work.get("isbn-type", []):
            if len(entry.get("value")) > 10:
                isbn = entry.get("value")

                # if isbn comes without hypens
                if len(isbn) == 13 and "-" not in isbn:
                    isbn_regex = r"(\d{3})(\d{1})(\d{3})(\d{5})(\d{1})"
                    isbn = re.sub(isbn_regex, '\\1-\\2-\\3-\\4-\\5', isbn)
                break

        return isbn

    def get_edition(self) -> int:
        """Get edition number from self.work"""
        edition = 0
        try:
            edition = int(self.work.get("edition-number"))
        except (TypeError, ValueError):
            pass

        return edition if edition > 0 else None

    def get_authors(self) -> str:
        """Get authors from self.work"""
        authors = []
        for author in self.work.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            authors.append(", ".join(filter(None, [family, given])))

        if len(authors) > 0:
            return "; ".join(authors)
        else:
            return None

    def get_url(self) -> str:
        """Get URL from self.work"""
        return self.work.get("resource", {}).get("primary", {}) \
                        .get("URL")

    def get_publication_date(self) -> str:
        """Get publication date from self.work"""
        try:
            date_parts = self.work.get("issued", {}).get("date-parts", [])[0]
            if date_parts[0] is None:
                return None
        except IndexError:
            return None
        else:
            # sometimes dates are incomplete, e.g. [1900] or [1900, 5]
            # and it is considered safe to default missing values to 1
            date_dict = {i: v for i, v in zip(["year", "month", "day"],
                                              date_parts)}
            date = datetime.datetime(date_dict.get("year"),
                                     date_dict.get("month", 1),
                                     date_dict.get("day", 1))
            return date.strftime("%Y-%m-%d")

    def get_title(self) -> str:
        """Get title from self.work. If a 'subtitle' is present, join
           that to the 'title' field."""
        title = None
        try:
            title = self.work.get("title", [])[0]
        except IndexError:
            pass

        if title is not None:
            try:
                title += ": " + self.work.get("subtitle", [])[0]
            except IndexError:
                pass

        return title

    def get_container_title(self) -> str:
        """Get name of the book or journal from self.work.
           Used for book chapters and journal articles."""
        try:
            return self.work.get("container-title", [])[-1]
        except IndexError:
            return None

    def get_first_page(self) -> str:
        """Get first page of a book chapters and journal articles
           from self.work."""
        page_range = self.work.get("page")
        if page_range is not None and \
           "-" in page_range:
            return page_range.split("-")[0]
        else:
            return None

    def get_volume_number(self) -> int:
        """Get volume number from self.work."""
        volume = self.work.get("volume")
        if isinstance(volume, str) and volume.isdigit():
            return volume
        elif isinstance(volume, int):
            return str(volume)
        else:
            return None

    def get_issue_number(self) -> str:
        """Get issue number from self.work."""
        issue = self.work.get("issue")
        if isinstance(issue, str) and issue.isdigit():
            return issue
        elif isinstance(issue, int):
            return str(issue)
        else:
            return None

    def process_crossref_data(self) -> None:
        """"This method parses the result of crossref query and feeds into
            the Citation object."""
        self.cit.process_doi(self.work.get("DOI"))
        self.cit.issn = self.get_issn()
        self.cit.isbn = self.get_isbn()
        self.cit.edition = self.get_edition()
        self.cit.author = self.get_authors()
        self.cit.url = self.get_url()
        self.cit.publication_date = self.get_publication_date()

        if self.work.get("type") in ["monograph", "edited-book"]:
            self.cit.volume_title = self.get_title()
            self.cit.series_title = self.get_series_title()

        elif self.work.get("type") == "book-chapter":
            self.cit.article_title = self.get_title()
            self.cit.volume_title = self.get_container_title()
            self.cit.first_page = self.get_first_page()
            self.cit.series_title = self.get_series_title()

        elif self.work.get("type") == "journal-article":
            self.cit.article_title = self.get_title()
            self.cit.journal_title = self.get_container_title()
            self.cit.first_page = self.get_first_page()
            self.cit.volume = self.get_volume_number()
            self.cit.issue = self.get_issue_number()

    def get_citation(self) -> Citation:
        """Return a Citation object with the data gathered"""
        return self.cit
