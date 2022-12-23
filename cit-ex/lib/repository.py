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
        self.connection = None
        self.identifier = None

    def init_connection(self) -> None:
        """Init repository object"""
        raise NotImplementedError

    def _validate_credentials(self) -> None:
        """Method to check if the log in credentials are valid.
           Specifically, this method checks that username and password
           are (1) not None (default value assigned by Reposotory())
           and (2) strings"""
        if self.username is None or type(self.username) != str:
            raise ValueError(f"Please provide a valid username. "
                             f"'{type(self.username)}' offered, expected str.")
        if self.password is None or type(self.password) != str:
            raise ValueError(f"Please provide a valid password. "
                             f"'{type(self.password)}' offered, expected str.")
        return True

    def write_record(self, citation: Citation = None, id: str = None) -> None:
        """Write a citation record at the specified identifier"""
        raise NotImplementedError


class Thoth(Repository):
    """Class to interface with Thoth repository"""
    def init_connection(self) -> None:
        if self._validate_credentials():
            self.client = ThothClient()
            self.connection = self.client.login(self.username, self.password)

    def resolve_identifier(self, identifier: str = None) -> None:
        """User would input either a DOI or a UUID from the CLI. This method
           firures out which one was given, in the case of DOI resolves it and
           finally stores the corresponding UUID in self.identifier.

           Accepted formats are:
            - DOI:
                + https://doi.org/10.11647/obp.0288
                + 10.11647/obp.0288
            - UUID:
                + cedb58f1-b88f-476c-b7c8-bc5869a2a6ba"""
        doi_regex = re.compile(r"(10\.\d{3,6}\/\S*)")
        uuid_regex = re.compile(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-"
                                r"[a-f0-9]{4}-[a-f0-9]{12})")

        if identifier is None or type(identifier) != str:
            raise TypeError(f"Invalid identifier type. '{type(identifier)}' "
                            "supplied, expected a string.")
        elif doi_regex.search(identifier):
            doi = doi_regex.search(identifier).group()
            work = self.client.work_by_doi(urljoin("https://doi.org/", doi))
            self.identifier = work.workId

        elif uuid_regex.search(identifier):
            self.identifier = uuid_regex.search(identifier).group()
        else:
            raise ValueError(f"Identifier not well formatted: '{identifier}'. "
                             "Expected a DOI or UUID")
