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

from ebooklib import epub
import pytest

from extractor import Extractor


@pytest.fixture
def dummy_epub(tmp_path):
    book = epub.EpubBook()

    ch1 = epub.EpubHtml(title="Intro", file_name="ch1.xhtml", lang="en-gb")
    ch1.content = "<h1>Heading</h1><p>First paragraph.</p>" + \
                  "<p class='citation'>This citation</p>"
    book.add_item(ch1)

    book.toc = (epub.Link("ch1.xhtml", "Introduction", "intro"),
                (epub.Section("Test book"),
                (ch1, ))
                )

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    file_path = tmp_path / "file.epub"
    epub.write_epub(file_path, book, {})

    yield file_path


def test_extractor_has_attributes(dummy_epub):
    ex = Extractor(dummy_epub)
    assert hasattr(ex, "book")
    assert hasattr(ex, "docs")


def test_get_book_w_good_input(dummy_epub):
    ex = Extractor(dummy_epub)
    assert type(ex.book).__name__ == "EpubBook"


def test_get_book_w_empty_input():
    with pytest.raises(FileNotFoundError):
        _ = Extractor("")


def test_get_book_w_nonexistent_input():
    with pytest.raises(FileNotFoundError):
        _ = Extractor("/foo/bar.epub")


def test_get_book_w_bad_input(dummy_epub):
    with pytest.raises(epub.EpubException):
        _ = Extractor(open(dummy_epub))


def test_get_docs(dummy_epub):
    book = Extractor(dummy_epub)
    chapters = Extractor._get_docs(book)
    assert chapters[0].get_name() == "ch1.xhtml"


@pytest.fixture
def dummy_chapter():
    book = epub.EpubBook()

    ch1 = epub.EpubHtml(title="Intro", file_name="ch1.xhtml", lang="en-gb")
    ch1.content = "<h1>Heading</h1><p>First paragraph.</p>" + \
                  "<p class='citation'>This citation</p>"
    book.add_item(ch1)
    yield ch1


class MockExtractor:
    def __init__(self, *dummy_chapter):
        self.docs = list(dummy_chapter)


def test_exctract_cit_w_good_input(dummy_chapter):
    book = MockExtractor(dummy_chapter)
    assert Extractor.exctract_cit(book, "citation") == ["This citation"]


def test_exctract_cit_w_empty_input(dummy_chapter):
    book = MockExtractor(dummy_chapter)
    assert Extractor.exctract_cit(book, "") == []


def test_exctract_cit_w_non_matching_input(dummy_chapter):
    book = MockExtractor(dummy_chapter)
    assert Extractor.exctract_cit(book, "FooBar") == []
