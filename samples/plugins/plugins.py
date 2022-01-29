#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   dfc210f8-c2db-11eb-9b1d-dbcf63dc8c1c
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-06-01
# -----------

"""
This is a sample file demonstrating how to construct various types of
plugins the system recognizes.

"""

# ------------
# System Modules - Included with Python

import logging
from pathlib import Path

# ------------
# Custom Modules

from documentos.documentos.common import relative_path

from documentos.documentos.document import MarkdownDocument

from documentos.documentos.markdown import (
    section_to_anchor,
    clean_atx_header_text,
)

from documentos.tools.plugins import TOCPlugin, register

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------

@register(name="Blog TOC")
class BlogTableOfContents(TOCPlugin):
    def __call__(self, lst, depth=6, ignore=None):
        """
        Take the files and generate a blog table of contents. It creates
        a list with the article date and article title:

        ```
        - yyyy-mm-dd - [article title](article_title.md)
        ```

        # Parameters

        lst:LSTDocument
            - The list file we want to construct a table of contents for

        depth:int
            - How many headers to display, a number from 0 to 6. 0 would
              be a link to the markdown file, 1 to 6 would refer to the
              ATX headers within that file.
            - Default - 6

        ignore:set(str)
            - a set of files that we do not want to add to the TOC.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - set()


        # Return

        The markdown contents representing the index.

        # NOTE

        The markdown files must contain a YAML block and it is looking
        for the kwargs - "date" and "title"

        All paths should be relative to a common root.

        It will add attributes to the elements so they can be styled by
        css if applicable

        The list itself is wrapped in a div tag i.e. `:::` and
        the .index-file-lst attribute is added to it.

        The date gets `.index-file-date`

        The title gets `.index-file-link`

        """

        if depth < 0 or depth > 6:
            raise ValueError("depth has to be in the range [0, 6]...")

        if ignore is None:
            ignore = set()

        # https://pandoc.org/MANUAL.html#divs-and-spans Creates a div
        # without resorting to native HTML
        contents = ["::: {.index-file-lst}\n"]

        for path in lst.links:

            # Is the file in the ignore list?
            if str(path) in ignore:
                continue

            md = MarkdownDocument(path)

            md_relative = relative_path(lst.filename.parent, path.parent)
            url = Path(md_relative).joinpath(path.name)

            yb = md.yaml_block

            if yb and "date" in yb and "title" in yb:
                contents.append(
                    f"- [{yb['date']}]{{.index-file-date}} - [{yb['title']}]({url}){{.index-file-link}}\n"
                )

        contents.append(":::\n")

        return contents
