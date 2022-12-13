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

from ebooklib import epub, ITEM_DOCUMENT


class Extractor:
    """Class to extract unstructured citations from an EPUB file"""

    def __init__(self, epub_path: str) -> None:
        self.book = self._get_book(epub_path)
        self.docs = self._get_docs()

    def _get_book(self, epub_path: str) -> epub.EpubBook:
        """Return an EpubBook object of the input file (path) epub_path"""
        try:
            book = epub.read_epub(epub_path)
        except FileNotFoundError as e:
            print(f"The filepath '{epub_path}' is invalid. \n\nSee: \n{e}")
            raise
        except epub.EpubException as e:
            print(f"Invalid input type {type(epub_path)}. \n\nSee: \n{e}")
            raise

        return book

    def _get_docs(self) -> list:
        """Return a list of the book ITEM_DOCUMENT items (i.e. chapters)"""
        return list(self.book.get_items_of_type(ITEM_DOCUMENT))
