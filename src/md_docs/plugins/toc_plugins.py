#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   9804982c-c244-11eb-aa62-1beaed170423
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-05-31
# -----------

"""
Define the table of contents plugins for the build system to use.
"""

# ------------
# System Modules - Included with Python

import logging
from pathlib import Path

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules

from ..md_docs.common import relative_path

from ..md_docs.document import MarkdownDocument

from ..md_docs.markdown import (
    section_to_anchor,
    clean_atx_header_text,
)

from ..tools.plugins import TOCPlugin, register

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


@register(name="TOC")
class BasicTableOfContents(TOCPlugin):
    """
    This is the basic table of contents plugin.
    """

    def __call__(self, lst, depth=6, ignore=None):
        """
        Given a LST file, construct a table of contents to the Markdown
        files it points too.

        ```
        - [test](./test.md)
            - [header 1](./test.md#header-1)
                - [header 2](./test.md#header-2)
                - [Natural Numbers](./test.md#natural-numbers)
        ```

        # Parameters

        lst:LSTDocument
            - The list file we want to construct a table of contents for

        depth:int
            - How many headers to display, a number from 0 to 6. 0 would
              be a link to the markdown file, 1 to 6 would refer to the
              ATX headers within that file.
            - Default - 6

        ignore:set(Path)
            - A set of file Path objects that we do not want to add to
              the TOC.
            - Full path to the file to ignore.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - None


        # Return

        A list of strings representing the markdown table of contents

        # NOTE

        All links passed into the method should be relative to the
        document root
        """

        if depth < 0 or depth > 6:
            raise ValueError("depth has to be in the range [0, 6]...")

        if ignore is None:
            ignore = set()

        toc = []

        for path in lst.links:

            # Is the file in the ignore list?
            if path in ignore:
                continue

            md = MarkdownDocument(path)

            md_relative = relative_path(lst.filename.parent, path.parent)
            url = Path(md_relative).joinpath(path.name)

            # Try to construct a title name from the filename that we can
            # display as nice Markdown text in the TOC. We'll do some
            # simple things like remove dashes and underscores and set the
            # text to title case. This is the backup if the markdown
            # doesn't have a YAML block with a title variable defined We
            # could also potentially use the first ATX header at depth = 1
            # if it is available

            sanitized_file_name = url.stem.replace("_", " ")

            sanitized_file_name = sanitized_file_name.replace("-", " ")

            sanitized_file_name = sanitized_file_name.title()

            try:

                yb = md.yaml_block

            except Exception as e:
                log.error(f'YAML Block exception occurred in {md.filename}')
                raise Exception(f'Parsing YAML Block - {md.filename}') from e


            if yb and "title" in yb:
                sanitized_file_name = yb["title"]

            toc.append(f"- [{sanitized_file_name}]({url})" + "{.toc-file}")

            for atx_depth in md.headers:

                # do we skip the ATX header level?
                if atx_depth > depth:
                    continue

                for _, text in md.headers[atx_depth]:

                    anchor = section_to_anchor(text)

                    text = clean_atx_header_text(text).title()

                    # if the first header matches the file name, we'll skip it
                    if text == sanitized_file_name:
                        continue

                    # indent two spaces for every level we find.
                    indent = "  " * (atx_depth)

                    # can't have whitespace between the link and the attribute
                    toc.append(
                        f"{indent}- [{text}]({url}#{anchor})" + "{.toc-file-section}"
                    )

        # add line feed otherwise
        toc = [line + "\n" for line in toc]

        # Insert and append linefeed so we can be sure the list is generated
        # properly
        toc.insert(0, "\n")
        toc.append("\n")

        return toc
