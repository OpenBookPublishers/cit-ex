import pytest

from refine import Citation, Refine


def test_refine_no_argument():
    with pytest.raises(TypeError):
        _ = Refine()


def test_refine_w_doi(mocker):
    mocker.patch("refine.Refine._get_work_by_doi", return_value=True)
    p = Refine("FooBar", "dummy_doi")
    assert p.work is True


def test_refine_w_doi_HTTP_error(mocker):
    mocker.patch("refine.Refine._get_work_by_doi",
                 side_effect=Exception('HTTPError'))
    with pytest.raises(Exception):
        p = Refine("FooBar", "dummy_doi")
        assert p.work is None


def test_get_work_by_doi(mocker):
    class MockWorks:
        def doi(self, doi):
            return {"DummyDoi": True}

    class MockEtiquette:
        pass

    mocker.patch("refine.Works", return_value=MockWorks())
    mocker.patch("refine.Etiquette", return_value=MockEtiquette())
    p = Refine("FooBar", "dummy_doi")
    assert p.work is not None


def test_refine_no_doi():
    p = Refine("FooBar")
    assert p.work is None


def test_refine_has_attributes():
    p = Refine("FooBar")
    assert hasattr(p, "cit")
    assert hasattr(p, "work")


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
    doi = Refine.find_doi_match(unstructured_citation)
    assert doi == expected_result


def test_is_valid_doi(mocker):
    mocker.patch("refine.Refine._get_work_by_doi", return_value=True)
    p = Refine("dummy_unstructured_citation", "dummy_doi")
    assert p._is_valid_doi() is True


def test_is_valid_doi_invalid_doi(mocker):
    class MockWorkss:
        def doi(self, doi):
            return None

    mocker.patch("refine.Works", return_value=MockWorkss())

    p = Refine("dummy_unstructured_citation")
    assert p._is_valid_doi() is False


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"DOI": "10.123/123"}, "10.123/123"],
                          [{}, None]])
def test_process_crossref_data_doi(input_data, expected_result, mocker):
    p = Refine("Foo Bar")
    p.work = input_data

    def mock_process(*args):
        p.cit.doi = expected_result

    mocker.patch("refine.Citation.process_doi", mock_process)

    p.process_crossref_data()
    assert p.cit.doi == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"URL": "http://10.123/123"}, "http://10.123/123"],
                          [{}, None]])
def test_process_crossref_data_doi_url(input_data, expected_result, mocker):
    p = Refine("Foo Bar")
    p.work = input_data

    def mock_process(*args):
        p.cit.doi_url = expected_result

    mocker.patch("refine.Citation.process_doi", mock_process)

    p.process_crossref_data()
    assert p.cit.doi_url == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"ISSN": ["123-123"]}, "123-123"],
                          [{"ISSN": []}, None],
                          [{}, None]])
def test_get_issn(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_issn() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"ISSN": "123-123",
                            "container-title": ["Dummy Series"]},
                           "Dummy Series"],
                          [{"ISSN": "123-123",
                            "container-title": ["Dummy Series", "Dummy Book"]},
                           "Dummy Series"],
                          [{"ISSN": "123-123", "container-title": []},
                           None],
                          [{"ISSN": "123-123"}, None],
                          [{"container-title": ["Foo Bar"]}, None],
                          [{}, None]])
def test_get_series_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.cit.issn = input_data.get("ISSN")
    assert p.get_series_title() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"isbn-type": [{"value": "123-1-231-23123-1"}]},
                           "123-1-231-23123-1"],
                          [{"isbn-type": [{"value": "1231231231231"}]},
                           "123-1-231-23123-1"],
                          [{"isbn-type": [{"value": "123-1-231-23123-1"},
                                          {"value2": "123-1-231-23123-2"}]},
                           "123-1-231-23123-1"],
                          [{"isbn-type": []}, None],
                          [{"isbn-type": [{"value": "123-1"}]}, None],
                          [{}, None]])
def test_get_isbn(input_data, expected_result, mocker):
    mocker.patch("refine.re.sub", return_value=expected_result)
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_isbn() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"edition-number": "3"}, 3],
                          [{"edition-number": "0"}, None],
                          [{"edition-number": "-1"}, None],
                          [{}, None]])
def test_get_edition(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_edition() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"author": [{"given": "a", "family": "b"}]}, "a b"],
                          [{"author": [{"given": "a"}]}, "a"],
                          [{"author": [{"family": "b"}]}, "b"],
                          [{"author": [{"given": "a", "family": "b"},
                                       {"given": "c", "family": "d"}]},
                           "a b; c d"],
                          [{"author": []}, None],
                          [{}, None]])
def test_get_authors(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_authors() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"resource": {"primary": {"URL": "http"}}}, "http"],
                          [{"resource": {"primary": {}}}, None],
                          [{"resource": {}}, None],
                          [{}, None]])
def test_get_url(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_url() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"issued": {"date-parts": [[1, 2, 3]]}}, "dummy"],
                          [{"issued": {"date-parts": []}}, None],
                          [{"issued": {}}, None],
                          [{}, None]])
def test_get_publication_date(input_data, expected_result, mocker):
    class MockDatetime():
        def strftime(self, args):
            return "dummy"

    mocker.patch("refine.datetime.datetime", return_value=MockDatetime())
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_publication_date() == expected_result


@pytest.mark.parametrize("input_data",
                         [{"issued": {"date-parts": [[1900, 1, 1]]}},
                          {"issued": {"date-parts": [[1900, 1]]}},
                          {"issued": {"date-parts": [[1900]]}}
                          ])
def test_get_publication_date_missing_parts(input_data, mocker):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_publication_date() == "1900-01-01"


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"title": ["dummy-title"]}, "dummy-title"],
                          [{"title": ["dummy-title"],
                            "subtitle": ["dummy-subtitle"]},
                           "dummy-title: dummy-subtitle"],
                          [{"subtitle": ["dummy-subtitle"]}, None],
                          [{"title": [],
                            "subtitle": ["dummy-subtitle"]}, None],
                          [{"title": ["dummy-title"],
                            "subtitle": []},
                           "dummy-title"],
                          [{}, None]])
def test_get_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_title() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"container-title": ["dummy"]}, "dummy"],
                          [{"container-title": []}, None],
                          [{}, None]])
def test_get_container_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_container_title() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"page": "1-2"}, "1"],
                          [{"page": ""}, None],
                          [{}, None]])
def test_get_first_page(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_first_page() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"volume": "1"}, "1"],
                          [{"volume": 1}, "1"],
                          [{}, None]])
def test_get_volume_number(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_volume_number() == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"issue": "1"}, "1"],
                          [{"issue": 1}, "1"],
                          [{}, None]])
def test_get_issue_number(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    assert p.get_issue_number() == expected_result


def test_process_crossref_data_monograph(mocker):
    get_issn = mocker.patch("refine.Refine.get_issn")
    get_isbn = mocker.patch("refine.Refine.get_isbn")
    get_edition = mocker.patch("refine.Refine.get_edition")
    get_authors = mocker.patch("refine.Refine.get_authors")
    get_url = mocker.patch("refine.Refine.get_url")
    get_publication_date = mocker.patch("refine.Refine.get_publication_date")
    get_title = mocker.patch("refine.Refine.get_title")
    get_series_title = mocker.patch("refine.Refine.get_series_title")

    p = Refine("Foo Bar")
    p.work = {"type": "monograph"}
    p.process_crossref_data()

    get_issn.assert_called_once()
    get_isbn.assert_called_once()
    get_edition.assert_called_once()
    get_authors.assert_called_once()
    get_url.assert_called_once()
    get_publication_date.assert_called_once()
    get_title.assert_called_once()
    get_series_title.assert_called_once()


def test_process_crossref_data_edited_book(mocker):
    get_issn = mocker.patch("refine.Refine.get_issn")
    get_isbn = mocker.patch("refine.Refine.get_isbn")
    get_edition = mocker.patch("refine.Refine.get_edition")
    get_authors = mocker.patch("refine.Refine.get_authors")
    get_url = mocker.patch("refine.Refine.get_url")
    get_publication_date = mocker.patch("refine.Refine.get_publication_date")
    get_title = mocker.patch("refine.Refine.get_title")
    get_series_title = mocker.patch("refine.Refine.get_series_title")

    p = Refine("Foo Bar")
    p.work = {"type": "edited-book"}
    p.process_crossref_data()

    get_issn.assert_called_once()
    get_isbn.assert_called_once()
    get_edition.assert_called_once()
    get_authors.assert_called_once()
    get_url.assert_called_once()
    get_publication_date.assert_called_once()
    get_title.assert_called_once()
    get_series_title.assert_called_once()


def test_process_crossref_data_book_chapter(mocker):
    get_issn = mocker.patch("refine.Refine.get_issn")
    get_isbn = mocker.patch("refine.Refine.get_isbn")
    get_edition = mocker.patch("refine.Refine.get_edition")
    get_authors = mocker.patch("refine.Refine.get_authors")
    get_url = mocker.patch("refine.Refine.get_url")
    get_publication_date = mocker.patch("refine.Refine.get_publication_date")
    get_title = mocker.patch("refine.Refine.get_title")
    get_container_title = mocker.patch("refine.Refine.get_container_title")
    get_first_page = mocker.patch("refine.Refine.get_first_page")
    get_series_title = mocker.patch("refine.Refine.get_series_title")

    p = Refine("Foo Bar")
    p.work = {"type": "book-chapter"}
    p.process_crossref_data()

    get_issn.assert_called_once()
    get_isbn.assert_called_once()
    get_edition.assert_called_once()
    get_authors.assert_called_once()
    get_url.assert_called_once()
    get_publication_date.assert_called_once()
    get_title.assert_called_once()
    get_container_title.assert_called_once()
    get_first_page.assert_called_once()
    get_series_title.assert_called_once()


def test_process_crossref_data_journal_article(mocker):
    get_issn = mocker.patch("refine.Refine.get_issn")
    get_isbn = mocker.patch("refine.Refine.get_isbn")
    get_edition = mocker.patch("refine.Refine.get_edition")
    get_authors = mocker.patch("refine.Refine.get_authors")
    get_url = mocker.patch("refine.Refine.get_url")
    get_publication_date = mocker.patch("refine.Refine.get_publication_date")
    get_title = mocker.patch("refine.Refine.get_title")
    get_container_title = mocker.patch("refine.Refine.get_container_title")
    get_first_page = mocker.patch("refine.Refine.get_first_page")
    get_volume_number = mocker.patch("refine.Refine.get_volume_number")
    get_issue_number = mocker.patch("refine.Refine.get_issue_number")

    p = Refine("Foo Bar")
    p.work = {"type": "journal-article"}
    p.process_crossref_data()

    get_issn.assert_called_once()
    get_isbn.assert_called_once()
    get_edition.assert_called_once()
    get_authors.assert_called_once()
    get_url.assert_called_once()
    get_publication_date.assert_called_once()
    get_title.assert_called_once()
    get_container_title.assert_called_once()
    get_first_page.assert_called_once()
    get_volume_number.assert_called_once()
    get_issue_number.assert_called_once()


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
