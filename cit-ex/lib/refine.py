from dataclasses import dataclass
import re


@dataclass
class Citation:
    unstructured_citation: str = None
    doi: str = None
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


class Refine():
    """Class to process unstructured citations.
       The method get_citation returns a Citation object to (hopefully) ease
       further processing via dependency injection.

       Note: this class makes little sense in the present state
             (i.e. could be replaced with a Citation method), but it is
             meant to be extended in the feature to allow retrival of
             additional (meta)data fields."""
    def __init__(self, unstructured_citation: str = None) -> None:
        self.unstructured_citation = unstructured_citation
        self.doi = self._search_doi()

    def _search_doi(self) -> str:
        """Search the unstructured citation for a valid DOI and return it"""
        # Syntax of a DOI https://www.doi.org/doi_handbook/2_Numbering.html#2.2
        doi_regex = r"(10\.\d{3,6}\/\S*)"
        result = re.search(doi_regex, self.unstructured_citation)
        if result:
            return result.group()
        return None

    def get_citation(self) -> Citation:
        """Return a Citation object with the data gathered with the Refine"""
        return Citation(unstructured_citation=self.unstructured_citation,
                        doi=self.doi)
