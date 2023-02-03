import pytest

from refine import Citation, Refine


def test_refine_no_argument():
    with pytest.raises(TypeError):
        _ = Refine()


def test_refine_w_doi(mocker):
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
    class MockWorks:
        def doi(self, doi):
            return {"DummyDoi": True}

    mocker.patch("refine.Works", return_value=MockWorks())

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
def test_process_crossref_data_issn(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.issn == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"ISSN": "123-123", "container-title": ["Foo Bar"]},
                           "Foo Bar"],
                          [{"ISSN": "123-123", "container-title": []},
                           None],
                          [{"ISSN": "123-123"}, None],
                          [{"container-title": ["Foo Bar"]}, None],
                          [{}, None]])
def test_process_crossref_series_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.series_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"isbn-type": [{"value": "123-1-231-23123-1"}]},
                           "123-1-231-23123-1"],
                          [{"isbn-type": [{"value": "1231231231231"}]},
                           "123-1-231-23123-1"],
                          [{"isbn-type": []}, None],
                          [{"isbn-type": [{"value": "123-123"},
                                          {"value2": "456-456"}]}, "123-123"],
                          [{}, None]])
def test_process_crossref_isbn(input_data, expected_result, mocker):
    mocker.patch("refine.re.sub", return_value=expected_result)
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.isbn == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"edition-number": "3"}, 3],
                          [{}, None]])
def test_process_crossref_edition_number(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.edition == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"author": [{"given": "a", "family": "b"}]}, "a b"],
                          [{"author": [{"given": "a"}]}, "a"],
                          [{"author": [{"family": "b"}]}, "b"],
                          [{"author": [{"given": "a", "family": "b"},
                                       {"given": "c", "family": "d"}]},
                           "a b; c d"],
                          [{"author": []}, None],
                          [{}, None]])
def test_process_crossref_author(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.author == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"resource": {"primary": {"URL": "http"}}}, "http"],
                          [{"resource": {"primary": {}}}, None],
                          [{"resource": {}}, None],
                          [{}, None]])
def test_process_crossref_url(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.url == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"issued": {"date-parts": [[1, 2, 3]]}}, "dummy"],
                          [{"issued": {"date-parts": []}}, None],
                          [{"issued": {}}, None],
                          [{}, None]])
def test_process_publication_date(input_data, expected_result, mocker):
    class MockDatetime():
        def strftime(self, args):
            return "dummy"

    mocker.patch("refine.datetime.datetime", return_value=MockDatetime())
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.publication_date == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "monograph", "title": ["dummy"]}, "dummy"],
                          [{"type": "edited-book", "title": ["dummy"]},
                           "dummy"],
                          [{"type": "monograph"}, None],
                          [{"title": ["dummy"]}, None],
                          [{}, None]])
def test_process_book_volume_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.volume_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "book-chapter", "title": ["dummy"]},
                          "dummy"],
                          [{"type": "book-chapter", "title": []}, None],
                          [{"type": "book-chapter"}, None],
                          [{"title": []}, None],
                          [{}, None]])
def test_process_chapter_article_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.article_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "book-chapter",
                            "container-title": ["dummy"]}, "dummy"],
                          [{"type": "book-chapter",
                            "container-title": ["", "dummy"]}, "dummy"],
                          [{"type": "book-chapter",
                            "container-title": []}, None],
                          [{"type": "book-chapter"}, None],
                          [{"container-title": ["dummy"]}, None],
                          [{}, None]])
def test_process_chapter_volume_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.volume_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "book-chapter", "page": "1-2"}, "1"],
                          [{"type": "book-chapter"}, None],
                          [{"page": "1-2"}, None],
                          [{}, None]])
def test_process_chapter_first_page(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.first_page == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "journal-article",
                            "container-title": ["dummy"]}, "dummy"],
                          [{"type": "journal-article"}, None],
                          [{"container-title": "dummy"}, None],
                          [{}, None]])
def test_process_journal_journal_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.journal_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "journal-article",
                            "title": ["dummy"]}, "dummy"],
                          [{"type": "journal-article"}, None],
                          [{"title": "dummy"}, None],
                          [{}, None]])
def test_process_journal_article_title(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.article_title == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "journal-article",
                            "volume": "1"}, "1"],
                          [{"type": "journal-article"}, None],
                          [{"volume": "1"}, None],
                          [{}, None]])
def test_process_journal_volume(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.volume == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "journal-article",
                            "issue": "1"}, "1"],
                          [{"type": "journal-article"}, None],
                          [{"issue": "1"}, None],
                          [{}, None]])
def test_process_journal_issue(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.issue == expected_result


@pytest.mark.parametrize("input_data, expected_result",
                         [[{"type": "journal-article", "page": "1-2"}, "1"],
                          [{"type": "journal-article"}, None],
                          [{"page": "1-2"}, None],
                          [{}, None]])
def test_process_journal_first_page(input_data, expected_result):
    p = Refine("Foo Bar")
    p.work = input_data
    p.process_crossref_data()
    assert p.cit.first_page == expected_result


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
