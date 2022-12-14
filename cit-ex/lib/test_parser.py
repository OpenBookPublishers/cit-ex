import pytest

from parser import Citation, Parser


def test_parser_has_attributes():
    p = Parser("FooBar")
    assert hasattr(p, "unstr_citation")
    assert hasattr(p, "doi")


@pytest.mark.parametrize("unstr_citation",
                         ["https://doi.org/10.11647/OBP.0288",
                          "http://dx.doi.org/10.11647/OBP.0288",
                          "https://doi.org/10.11647/OBP.0288 FooBar",
                          "FooBar https://doi.org/10.11647/OBP.0288"])
def test_search_doi_w_good_input(unstr_citation):
    p = Parser(unstr_citation)
    assert p.doi == "10.11647/OBP.0288"


@pytest.mark.parametrize("unstr_citation",
                         ["",
                          "FooBar",
                          "https://doi.org/",
                          "https://doi.org/10.1/OBP.0288",
                          ])
def test_search_doi_w_empty_or_insufficient_input(unstr_citation):
    p = Parser(unstr_citation)
    assert p.doi is None


# Examples sourced from https://www.doi.org/demos.html
@pytest.mark.parametrize("unstr_citation, expected_result",
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
def test_search_doi_regex_efficacy(unstr_citation, expected_result):
    p = Parser(unstr_citation)
    assert p.doi == expected_result


class DummyParser():
    def __init__(self, unstr_citation):
        self.unstr_citation = unstr_citation
        self.doi = None


def test_get_citation():
    p = DummyParser(None)
    assert Parser.get_citation(p) == Citation()


def test_citation_init():
    c = Citation("FooBar 10.123/123", "10.123/123")
    assert c.unstr_citation == "FooBar 10.123/123"
    assert c.doi == "10.123/123"


def test_citation_named_init():
    c = Citation(unstr_citation="FooBar 10.123/123", doi="10.123/123")
    assert c.unstr_citation == "FooBar 10.123/123"
    assert c.doi == "10.123/123"


def test_citation_init_no_args():
    c = Citation()
    assert c.unstr_citation is None
    assert c.doi is None
