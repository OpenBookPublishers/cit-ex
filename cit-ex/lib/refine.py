from dataclasses import dataclass
import re
from urllib.parse import urljoin


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
        if doi is None:
            self.doi_url = None
        else:
            self.doi_url = urljoin("https://doi.org/", doi)


class Refine():
    """Class to process unstructured citations.
       The method get_citation returns a Citation object to (hopefully) ease
       further processing via dependency injection.

       Note: this class makes little sense in the present state
             (i.e. could be replaced with a Citation method), but it is
             meant to be extended in the feature to allow retrival of
             additional (meta)data fields."""
    def __init__(self, unstructured_citation: str) -> None:
        self.cit = Citation()
        self.cit.unstructured_citation = unstructured_citation
        self.cit.process_doi(self._search_doi(unstructured_citation))

    def _search_doi(self, unstructured_citation: str) -> str:
        """Search the unstructured citation for a valid DOI and return it"""
        # Syntax of a DOI https://www.doi.org/doi_handbook/2_Numbering.html#2.2
        doi_regex = r"(10\.\d{3,6}\/\S*)"
        result = re.search(doi_regex, unstructured_citation)
        if result:
            return result.group()
        return None

    def get_citation(self) -> Citation:
        """Return a Citation object with the data gathered"""
        return self.cit
