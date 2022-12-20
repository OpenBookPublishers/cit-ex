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


class Repository():
    """Base Repository class to derive specialised classes from to interface
       with metadata repositories."""
    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username
        self.password = password

    def init_connection(self) -> None:
        """Init repository object"""
        raise NotImplementedError


class Thoth(Repository):
    pass
