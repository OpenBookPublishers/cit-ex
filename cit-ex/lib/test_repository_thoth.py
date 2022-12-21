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

from repository import Thoth


def test_thoth_init():
    rep = Thoth("foo", "bar")
    assert rep.username == "foo"
    assert rep.password == "bar"


def test_thoth_init_connection(mocker):
    def mock_login(*args, **kwargs):
        return "Connection successful!"

    rep = Thoth()
    mocker.patch("repository.Thoth._validate_credentials", return_value=True)
    mocker.patch("repository.ThothClient.login", mock_login)
    rep.init_connection()

    assert rep.connection == "Connection successful!"


def test_thoth_init_connection_w_bad_credentials(mocker):
    rep = Thoth()
    mocker.patch("repository.Thoth._validate_credentials", return_value=False)

    assert rep.connection is None
