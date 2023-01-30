import pytest

from refine import Citation, Refine


def test_refine_no_argument():
    with pytest.raises(TypeError):
        _ = Refine()


def test_refine_has_attributes():
    p = Refine("FooBar")
    assert hasattr(p, "cit")


@pytest.mark.parametrize("unstructured_citation, expected_result",
                         [["https://doi.org/10.11647/OBP.0288",
                           "10.11647/OBP.0288"],
                          ["http://dx.doi.org/10.11647/OBP.0288",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288 FooBar",
                           "10.11647/OBP.0288"],
                          ["doi:10.11647/OBP.0288",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288. FooBar",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288. FooBar",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288, FooBar",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288; FooBar",
                           "10.11647/OBP.0288"],
                          ["https://doi.org/10.11647/OBP.0288.",
                           "10.11647/OBP.0288"],
                          ["http://dx.doi.org/10.2990/1471-5457(2005)24"
                           "[2:tmpwac]2.0.co;2",
                           "10.2990/1471-5457(2005)24[2:tmpwac]2.0.co;2"],
                          ["", None],
                          ["Foo Bar", None],
                          ])
def test_find_doi_match(unstructured_citation, expected_result):
    doi = Refine.find_doi_match("", unstructured_citation)
    assert doi == expected_result


def test_is_valid_doi(mocker):
    class MockWorks:
        def doi(self, doi):
            return {"DummyDoi": True}

    mocker.patch("refine.Works", return_value=MockWorks())

    p = Refine("dummy_unstructured_citation")
    assert p._is_valid_doi("dummy_doi") is True


def test_is_valid_doi_invalid_doi(mocker):
    class MockWorkss:
        def doi(self, doi):
            return None

    mocker.patch("refine.Works", return_value=MockWorkss())

    p = Refine("dummy_unstructured_citation")
    assert p._is_valid_doi("dummy_doi") is False


def test_get_citation():
    p = Refine("Foo Bar")
    assert p.get_citation() == Citation("Foo Bar")


def test_citation_init():
    c = Citation("FooBar 10.123/123", "10.123/123")
    assert c.unstructured_citation == "FooBar 10.123/123"
    assert c.doi == "10.123/123"


def test_citation_named_init():
    c = Citation(unstructured_citation="FooBar 10.123/123", doi="10.123/123")
    assert c.unstructured_citation == "FooBar 10.123/123"
    assert c.doi == "10.123/123"


def test_citation_init_no_args():
    c = Citation()
    assert c.unstructured_citation is None
    assert c.doi is None
    assert c.reference_id is None
    assert c.work_id is None
    assert c.reference_ordinal is None
    assert c.issn is None
    assert c.isbn is None
    assert c.journal_title is None
    assert c.article_title is None
    assert c.series_title is None
    assert c.volume_title is None
    assert c.edition is None
    assert c.author is None
    assert c.volume is None
    assert c.issue is None
    assert c.first_page is None
    assert c.component_number is None
    assert c.standard_designator is None
    assert c.standards_body_name is None
    assert c.standards_body_acronym is None
    assert c.url is None
    assert c.publication_date is None
    assert c.retrieval_date is None


def test_citation_process_doi():
    c = Citation()
    c.process_doi("10.123/123")

    assert c.doi == "10.123/123"
    assert c.doi_url == "https://doi.org/10.123/123"


def test_citation_process_doi_none_input():
    c = Citation()
    c.process_doi(None)

    assert c.doi is None
    assert c.doi_url is None


def test_citation_process_doi_no_input():
    with pytest.raises(TypeError):
        c = Citation()
        c.process_doi()
