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

import re
from urllib.parse import urljoin

from thothlibrary import ThothClient


class Repository():
    """Base Repository class to derive specialised classes from to interface
       with metadata repositories."""
    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username
        self.password = password
        self.client = None
        self.identifier = None

    def init_connection(self) -> None:
        """Init repository object"""
        raise NotImplementedError

    def _validate_credentials(self) -> None:
        """Method to check if the log in credentials are valid.
           Specifically, this method checks that username and password
           are (1) not None (default value assigned by Reposotory())
           and (2) strings"""
        credentials = [("username", self.username),
                       ("password", self.password)]

        for element, value in credentials:
            if value is None:
                raise ValueError(f"Please provide a {element}, none given.")
            if type(value) != str:
                raise TypeError(f"Please provide a valid {element}. "
                                f"'{type(value)}' offered, expected str.")
        else:
            return True

    def write_record(self, citation: any, ordinal: int) -> None:
        """Write a citation record"""
        raise NotImplementedError


class Thoth(Repository):
    """Class to interface with Thoth repository"""
    def init_connection(self) -> None:
        if self._validate_credentials():
            self.client = ThothClient()
            self.client.login(self.username, self.password)

    def resolve_identifier(self, identifier: str) -> None:
        """User would input either a DOI or a UUID from the CLI. This method
           figures out which one was given, in the case of DOI resolves it and
           finally stores the corresponding UUID in self.identifier.

           Accepted formats are:
            - DOI:
                + https://doi.org/10.11647/obp.0288
                + 10.11647/obp.0288
            - UUID:
                + cedb58f1-b88f-476c-b7c8-bc5869a2a6ba"""
        doi_regex = re.compile(r"(10\.\d{3,6}\/\S*)")
        uuid_regex = re.compile(r"([a-f0-9]{8}-(?:[a-f0-9]{4}-){3}"
                                r"[a-f0-9]{12})")

        if doi_regex.search(identifier):
            doi = doi_regex.search(identifier).group()
            work = self.client.work_by_doi(urljoin("https://doi.org/", doi))
            self.identifier = work.workId
        elif uuid_regex.search(identifier):
            self.identifier = uuid_regex.search(identifier).group()
        else:
            raise ValueError(f"Identifier not well formatted: '{identifier}'. "
                             "Expected a DOI or UUID")

    def write_record(self, citation: any, ordinal: int) -> None:
        """Create the reference object and write it to the repository"""
        try:
            reference = {
                "workId":               self.identifier,
                "referenceOrdinal":     ordinal,
                "doi":                  citation.doi_url,
                "unstructuredCitation": citation.unstructured_citation,
                "issn":                 citation.issn,
                "isbn":                 citation.isbn,
                "journalTitle":         citation.journal_title,
                "articleTitle":         citation.article_title,
                "seriesTitle":          citation.series_title,
                "volumeTitle":          citation.volume_title,
                "edition":              citation.edition,
                "author":               citation.author,
                "volume":               citation.volume,
                "issue":                citation.issue,
                "firstPage":            citation.first_page,
                "componentNumber":      citation.component_number,
                "standardDesignator":   citation.standard_designator,
                "standardsBodyName":    citation.standards_body_name,
                "standardsBodyAcronym": citation.standards_body_acronym,
                "url":                  citation.url,
                "publicationDate":      citation.publication_date,
                "retrievalDate":        citation.retrieval_date
                }
        except AttributeError as e:
            raise TypeError(f"Please, provide a valid Citation object, "
                            f"see:\n\n{e}")
        else:
            self.client.create_reference(reference)
