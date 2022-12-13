#!/usr/bin/env python3
'''
cit-ex - A tool to extract citation data from EPUBs and upload it to a
metadata manager.
Copyright (C) 2022 Luca Baffa

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

import argparse

from lib.extractor import Extractor


def main():
    parser = argparse.ArgumentParser(
                 prog="cit-ex",
                 description="A tool to extract citation data from "
                             "EPUBs and upload it to a metadata manager.",
                 epilog="This program is licensed GPL v3."
    )
    parser.add_argument("epub", type=argparse.FileType("r"),
                        help="File path of the EPUB to parse.")
    parser.add_argument("-c", "--classes", type=str, nargs="+", default="",
                        help="HTML class(es) of the citation nodes. "
                             "This parameter accepts multiple values.")
    args = parser.parse_args()

    ex = Extractor(args.epub.name)
    unstr_citations = []
    for class_ in args.classes:
        unstr_citations.extend(ex.exctract_cit(class_))
    print(unstr_citations)


if __name__ == "__main__":  # pragma: no cover
    main()
