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

import pytest

from repository import Repository, Thoth


def test_repository_attributes():
    rep = Repository()
    assert hasattr(rep, "username")
    assert hasattr(rep, "password")


def test_repository_default_values():
    rep = Repository()
    assert rep.username is None
    assert rep.password is None


def test_repository_arguments():
    rep = Repository("foo", "bar")
    assert rep.username == "foo"
    assert rep.password == "bar"


def test_repository_named_arguments():
    rep = Repository(password="bar", username="foo")
    assert rep.username == "foo"
    assert rep.password == "bar"


def test_repository_init_connection():
    with pytest.raises(NotImplementedError):
        _ = Repository.init_connection("foobar")


def test_thoth_init():
    rep = Thoth("foo", "bar")
    assert rep.username == "foo"
    assert rep.password == "bar"
