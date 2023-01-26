import pytest

from refine import Citation, Refine


def test_refine_no_argument():
    with pytest.raises(TypeError):
        _ = Refine()


def test_refine_has_attributes():
    p = Refine("FooBar")
    assert hasattr(p, "cit")


@pytest.mark.parametrize("unstructured_citation",
                         ["https://doi.org/10.11647/OBP.0288",
                          "http://dx.doi.org/10.11647/OBP.0288",
                          "https://doi.org/10.11647/OBP.0288 FooBar",
                          "FooBar https://doi.org/10.11647/OBP.0288",
                          "https://doi.org/10.11647/OBP.0288. FooBar",
                          "https://doi.org/10.11647/OBP.0288, FooBar",
                          "https://doi.org/10.11647/OBP.0288; FooBar",
                          "https://doi.org/10.11647/OBP.0288."])
def test_search_doi_w_good_input(unstructured_citation, mocker):
    mocker.patch("refine.Refine.get_doi", return_value="10.11647/OBP.0288")
    p = Refine(unstructured_citation)
    assert p.cit.doi == "10.11647/OBP.0288"


@pytest.mark.parametrize("unstructured_citation",
                         ["",
                          "FooBar",
                          "https://doi.org/",
                          "https://doi.org/10.1/OBP.0288",
                          ])
def test_search_doi_w_empty_or_insufficient_input(unstructured_citation):
    p = Refine(unstructured_citation)
    assert p.cit.doi is None


# Examples sourced from https://www.doi.org/demos.html
@pytest.mark.parametrize("unstructured_citation, expected_result",
                         [["doi:10.1038/nphys1170",
                           "10.1038/nphys1170"],
                          ["doi:10.1002/0470841559.ch1",
                           "10.1002/0470841559.ch1"],
                          ["doi:10.1594/PANGAEA.726855",
                           "10.1594/PANGAEA.726855"],
                          ["doi:10.1594/GFZ.GEOFON.gfz2009kciu",
                           "10.1594/GFZ.GEOFON.gfz2009kciu"],
                          ["doi:10.11467/isss2003.7.1_11",
                           "10.11467/isss2003.7.1_11"]
                          ])
def test_search_doi_regex_efficacy(unstructured_citation,
                                   expected_result, mocker):
    mocker.patch("refine.Refine.get_doi", return_value=expected_result)
    p = Refine(unstructured_citation)
    assert p.cit.doi == expected_result


def test_get_doi(mocker):
    mocker.patch("refine.Refine._search_doi", return_value="10.11647/OBP.0288")
    mocker.patch("refine.Refine._is_valid_doi", return_value=True)

    p = Refine("dummy_unstructured_citation")
    assert p.cit.doi == "10.11647/OBP.0288"


def test_get_doi_doi_not_present_in_unstructured_citation(mocker):
    mocker.patch("refine.Refine._search_doi", return_value=None)
    mocker.patch("refine.Refine._is_valid_doi", return_value=False)

    p = Refine("dummy_unstructured_citation")
    assert p.cit.doi is None


def test_get_doi_doi_present_in_unstructured_citation_but_invalid(mocker):
    mocker.patch("refine.Refine._search_doi", return_value="dummy_doi")
    mocker.patch("refine.Refine._is_valid_doi", return_value=False)

    p = Refine("dummy_unstructured_citation")
    assert p.cit.doi is None


def test_is_valid_doi(mocker):
    class MockGet:
        status_code = 200

    mocker.patch("refine.Refine.get_doi", return_value="dummy_doi")
    mocker.patch("refine.urljoin", return_value="dummy_doi_url")
    mocker.patch("refine.requests.get", return_value=MockGet())

    p = Refine("dummy_unstructured_citation")
    assert p._is_valid_doi("dummy_doi") is True


def test_is_valid_doi_invalid_doi(mocker):
    class MockGet:
        status_code = 404

    mocker.patch("refine.Refine.get_doi", return_value="dummy_doi")
    mocker.patch("refine.urljoin", return_value="dummy_doi_url")
    mocker.patch("refine.requests.get", return_value=MockGet())

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
