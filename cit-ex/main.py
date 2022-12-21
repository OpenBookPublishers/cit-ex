#!/usr/bin/env python3
'''
cit-ex - A tool to extract citation data from EPUBs and upload it to a
metadata repository.
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
from os import getenv

from lib.extractor import Extractor
from lib.parser import Parser
from lib.repository import Thoth


def main():
    parser = argparse.ArgumentParser(
                 prog="cit-ex",
                 description="A tool to extract citation data from "
                             "EPUBs and upload it to a metadata repository.",
                 epilog="This program is licensed GPL v3."
    )
    parser.add_argument("epub", type=argparse.FileType("r"),
                        help="File path of the EPUB to parse.")
    parser.add_argument("-c", "--classes", type=str, nargs="+", default="",
                        help="HTML class(es) of the citation nodes. "
                             "This parameter accepts multiple values.")
    parser.add_argument("-r", "--repository", type=str, default="thoth",
                        help="Name of the metadata repository.")
    parser.add_argument("-d", "--dry-run", action='store_true',
                        help="Perform a dry run: no data would be sent to "
                             "metadata repositories.")
    args = parser.parse_args()

    # Extract unstructured citations from EPUB
    ex = Extractor(args.epub.name)
    unstr_citations = []
    for class_ in args.classes:
        unstr_citations.extend(ex.exctract_cit(class_))

    # Parse the unstructured citations and return Citation objects
    citations = []
    for c in unstr_citations:
        citations.append(Parser(c).get_citation())

    # If dry run, simply show citation data
    if args.dry_run:
        for c in citations:
            print(c)
    # If not dry run, write data to repository
    else:
        if args.repository == "thoth":
            rep = Thoth(username=getenv('THOTH_EMAIL'),
                        password=getenv('THOTH_PWD'))
        else:
            raise ValueError(f"The repository name '{args.repository}' "
                             "is invalid or not implemented yet.")

        rep.init_connection()


if __name__ == "__main__":  # pragma: no cover
    main()
