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

from thothlibrary import ThothClient


class Repository():
    """Base Repository class to derive specialised classes from to interface
       with metadata repositories."""
    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username
        self.password = password
        self.connection = None

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


class Thoth(Repository):
    """Class to interface with Thoth repository"""
    def init_connection(self) -> None:
        if self._validate_credentials():
            client = ThothClient()
            self.connection = client.login(self.username, self.password)
