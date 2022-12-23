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

from munch import Munch
import pytest

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


def test_resolve_identifier_w_valid_doi():
    class MockClient():
        def work_by_doi(self, *args, **kwargs):
            work = Munch()
            work.workId = "dummy-workId"
            return work

    rep = Thoth()
    rep.client = MockClient()
    rep.resolve_identifier("10.11647/obp.0288")

    assert rep.identifier == "dummy-workId"


def test_resolve_identifier_w_valid_uuid():
    rep = Thoth()
    rep.resolve_identifier("a28326e3-e86b-4e6c-8538-4ed0306d4259")

    assert rep.identifier == "a28326e3-e86b-4e6c-8538-4ed0306d4259"


@pytest.mark.parametrize("uuid", ["a28326-e86b-4e6c-8538-4ed0306d4259",
                                  "a28326e3-e8-4e6c-8538-4ed0306d4259",
                                  "a28326e3-e86b-4e-8538-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-85-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-8538-4ed0306d42"])
def test_resolve_identifier_w_invalid_uuid_clusters_too_short(uuid):
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


@pytest.mark.parametrize("uuid", ["a28326e3e86b-4e6c-8538-4ed0306d4259",
                                  "a28326e3-e86b4e6c-8538-4ed0306d4259",
                                  "a28326e3-e86b-4e6c8538-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-85384ed0306d4259"])
def test_resolve_identifier_w_invalid_uuid_missing_separators(uuid):
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


@pytest.mark.parametrize("uuid", ["Aa28326e-e86b-4e6c-8538-4ed0306d4259",
                                  "a28326e3-Ae86-4e6c-8538-4ed0306d4259",
                                  "a28326e3-e86b-A4e6-8538-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-A853-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-8538-A4ed0306d425"])
def test_resolve_identifier_w_invalid_uuid_uppercase_letter(uuid):
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


@pytest.mark.parametrize("uuid", ["za28326e-e86b-4e6c-8538-4ed0306d4259",
                                  "a28326e3-ze86-4e6c-8538-4ed0306d4259",
                                  "a28326e3-e86b-z4e6-8538-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-z853-4ed0306d4259",
                                  "a28326e3-e86b-4e6c-8538-z4ed0306d425"])
def test_resolve_identifier_w_invalid_uuid_not_hex_digit_clusters(uuid):
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


@pytest.mark.parametrize("uuid", [None, {}])
def test_resolve_identifier_w_invalid_uuid(uuid):
    with pytest.raises(TypeError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


def test_resolve_identifier_w_empty_input():
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier("")
