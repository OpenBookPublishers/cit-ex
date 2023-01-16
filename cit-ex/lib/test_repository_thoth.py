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
from urllib.parse import urljoin

from refine import Citation
from repository import Thoth


def test_thoth_init():
    rep = Thoth("foo", "bar")
    assert rep.username == "foo"
    assert rep.password == "bar"


def test_thoth_init_connection(mocker):
    rep = Thoth()
    login = mocker.patch("repository.ThothClient.login")
    rep.init_connection()

    login.assert_called_once()


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


@pytest.mark.parametrize("uuid", [["a28326e3-e86b-4e6c-8538-4ed0306d4259"],
                                  {}])
def test_resolve_identifier_w_invalid_uuid(uuid):
    with pytest.raises(TypeError):
        rep = Thoth()
        rep.resolve_identifier(uuid)


def test_resolve_identifier_w_empty_input():
    with pytest.raises(ValueError):
        rep = Thoth()
        rep.resolve_identifier("")


@pytest.mark.parametrize("work_id, reference_ordinal, doi, "
                         "unstructured_citation",
                         [["1234", 1, "10.11647/OBP.0322", "Foo Bar"]])
def test_write_record(work_id, reference_ordinal,
                      doi, unstructured_citation):
    class MockClient:
        def create_reference(self, reference):
            self.reference = reference

    rep = Thoth()
    rep.identifier = work_id
    rep.client = MockClient()
    c = Citation(unstructured_citation=unstructured_citation,
                 doi=doi, doi_url=urljoin("https://doi.org/", doi))
    rep.write_record(c, reference_ordinal)

    assert rep.client.reference["workId"] == work_id
    assert rep.client.reference["referenceOrdinal"] == reference_ordinal
    assert rep.client.reference["doi"] == urljoin("https://doi.org/", doi)
    assert rep.client.reference["unstructuredCitation"] \
        is unstructured_citation
    assert rep.client.reference["issn"] is None
    assert rep.client.reference["isbn"] is None
    assert rep.client.reference["journalTitle"] is None
    assert rep.client.reference["articleTitle"] is None
    assert rep.client.reference["seriesTitle"] is None
    assert rep.client.reference["volumeTitle"] is None
    assert rep.client.reference["edition"] is None
    assert rep.client.reference["author"] is None
    assert rep.client.reference["volume"] is None
    assert rep.client.reference["issue"] is None
    assert rep.client.reference["firstPage"] is None
    assert rep.client.reference["componentNumber"] is None
    assert rep.client.reference["standardDesignator"] is None
    assert rep.client.reference["standardsBodyName"] is None
    assert rep.client.reference["standardsBodyAcronym"] is None
    assert rep.client.reference["url"] is None
    assert rep.client.reference["publicationDate"] is None
    assert rep.client.reference["retrievalDate"] is None


@pytest.mark.parametrize("work_id, reference_ordinal, citation",
                         [["1234", 1, [Citation()]],
                          ["1234", 1, {"citation": Citation()}]])
def test_write_record_type_error(work_id, reference_ordinal, citation):
    class MockClient:
        def create_reference(self, reference):
            self.reference = reference

    with pytest.raises(TypeError):
        rep = Thoth()
        rep.identifier = work_id
        rep.client = MockClient()
        rep.write_record(citation, reference_ordinal)
