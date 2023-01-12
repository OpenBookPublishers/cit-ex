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

from parser import Citation


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

    def write_record(self, citation: Citation = None,
                     ordinal: int = None) -> None:
        """Write a citation record"""
        raise NotImplementedError


class Thoth(Repository):
    """Class to interface with Thoth repository"""
    def init_connection(self) -> None:
        if self._validate_credentials():
            self.client = ThothClient()
            self.client.login(self.username, self.password)

    def resolve_identifier(self, identifier: str = None) -> None:
        """User would input either a DOI or a UUID from the CLI. This method
           figures out which one was given, in the case of DOI resolves it and
           finally stores the corresponding UUID in self.identifier.

           Accepted formats are:
            - DOI:
                + https://doi.org/10.11647/obp.0288
                + 10.11647/obp.0288
            - UUID:
                + cedb58f1-b88f-476c-b7c8-bc5869a2a6ba"""
        if identifier is None:
            raise ValueError("Empty value supplied for identifier")
        elif type(identifier) != str:
            raise TypeError(f"Invalid identifier type. '{type(identifier)}' "
                            "supplied, expected a string.")

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

    def write_record(self, citation: Citation, ordinal: int) -> None:
        """Create the reference object and write it to the repository"""
        args = [("citation", citation, Citation), ("ordinal", ordinal, int)]
        for element, value, value_type in args:
            if value is None:
                raise ValueError(f"Please provide a {element}, none given.")
            if not isinstance(value, value_type):
                raise TypeError(f"Please provide a valid {element}. "
                                f"'{type(value)}' offered, expected "
                                f"{value_type}.")

        reference = {
            "workId":               self.identifier,
            "referenceOrdinal":     ordinal,
            "doi":                  urljoin("https://doi.org/", citation.doi),
            "unstructuredCitation": citation.unstr_citation,
            "issn":                 None,
            "isbn":                 None,
            "journalTitle":         None,
            "articleTitle":         None,
            "seriesTitle":          None,
            "volumeTitle":          None,
            "edition":              None,
            "author":               None,
            "volume":               None,
            "issue":                None,
            "firstPage":            None,
            "componentNumber":      None,
            "standardDesignator":   None,
            "standardsBodyName":    None,
            "standardsBodyAcronym": None,
            "url":                  None,
            "publicationDate":      None,
            "retrievalDate":        None
            }

        self.client.create_reference(reference)
