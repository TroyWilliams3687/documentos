#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   f3c90404-f156-11eb-92de-2350ce5a509d
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-07-30
# -----------

"""
Define the JSON Document plugins...
"""

# ------------
# System Modules - Included with Python

import json

from pathlib import Path

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules

from ..documentos.common import relative_path

from ..documentos.document import MarkdownDocument

from ..documentos.markdown import (
    section_to_anchor,
    clean_atx_header_text,
)

from ..tools.plugins import JSONDocumentPlugin, register


# -------------


@register(name="JSON Minimum")
class JSONMinimum(JSONDocumentPlugin):
    """
    Iterate through all of the Markdown Documents and construct a list
    of dictionaries with the following keys:

    - file - The path to the file relative to the root path
    - contents - The body of the document

    The list of dictionaries will be converted to valid JSON and
    returned
    """

    @property
    def filename(self):
        """
        The name of the file to use to store the JSON string in, for
        example: `documents.json`.

        """

        return "basic_document.json"

    def __call__(self, documents=None, root=None, ignore=None):
        """

        Iterate through all of the Markdown Documents and construct a
        list of dictionaries with the following keys:

        - file - The path to the file relative to the root path
        - contents - The body of the document

        The list of dictionaries will be converted to valid JSON and
        returned

        # Parameters

        documents:list(MarkdownDocuments)
            - The list file we want to construct the JSON document from.

        root:Path
            - The path to the root folder of the documents.

        ignore:set(Path)
            - A set of file Path objects that we do not want to add to
              the JSON document.
            - Full path to the file to ignore.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - None

        # Return

        A valid JSON string representing the contents of the documents.

        # NOTE

        All links passed into the method should be relative to the
        document root
        """

        if ignore is None:
            ignore = set()

        docs = []

        for md in documents:

            # Is the file in the ignore list?
            if md in ignore:
                continue

            docs.append(
                {
                    'file':str(md.filename.relative_to(root)),
                    'contents':'\n'.join(md.contents),
                }
            )

        return json.dumps(docs)
