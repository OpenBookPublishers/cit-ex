import re


class Parser():
    """Class to parse unstructured citations

       Note: this class makes little sense in the present state
             (i.e. cold be replaced by a Citation method), but it is
             meant to be extended in the feature to allow retrival of
             additional (meta)data fields."""
    def __init__(self, unstr_citation: str = None) -> None:
        self.unstr_citation = unstr_citation
        self.doi = self._search_doi()

    def _search_doi(self) -> str:
        """Search the unstructured citation for a valid DOI and return it"""
        # Syntax of a DOI https://www.doi.org/doi_handbook/2_Numbering.html#2.2
        doi_regex = r"(10\.\d{3,6}\/\S*)"
        result = re.search(doi_regex, self.unstr_citation)
        if result:
            return result.group()
        return None
