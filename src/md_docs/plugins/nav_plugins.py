#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   52b7bf58-ceb3-11eb-9734-2d229bf17d60
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-06-16
# -----------

"""
Define the default Navigation plugins included with the system.
"""

# ------------
# System Modules - Included with Python

import logging
import csv

from pathlib import Path

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules

from ..md_docs.common import relative_path
from ..md_docs.document import MarkdownDocument

from ..tools.plugins import HTMLNavigationPlugin, register

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


@register(name="CSV Navigation")
class BasicCSV(HTMLNavigationPlugin):
    """

    This plugin will take all of the MarkdownDocument objects and
    allow the build system to construct a CSV file from it:

    ```
    UUID, Title, Path
    03bd16cc-ceb9-11eb-9734-2d229bf17d60, "How to load a wireframe from DXF", designer/import/dxf.html
    1a6b59ec-ceb9-11eb-9734-2d229bf17d60, "Isosurface from Stope", designer/issurface/stope.html
    ```

    The components will be extracted from the document YAML block and
    the file path.

    """

    def __call__(
        self,
        document_root=None,
        output=None,
        documents=None,
        **kwargs,
    ):
        """

        Given the root path and a list of MarkdownDocument objects,
        construct a CSV file containing the UUID, the document title
        and relative path to the HTML file

        # Parameters

        document_root:Path
            - The valid path to the root of the MarkdownDocument folder
            - It can be used to create relative paths from full paths

        output:Path
            - The valid path to the location that file should be written.
            - This is the folder where the plugin will write the navigation file too

        documents:iterable(MarkdownDocument)
            - The list of MarkdownDocument objects that will be used to
              construct the navigation document.

        # Return

        None - The file will be written by the plugin to the root
        folder.

        """

        log.debug("Entering `BasicCSV`")

        csv_file = ouput / 'url_map.csv'

        log.debug(f"{csv_file=}")

        headers = ['uuid', 'title', 'path']

        with csv_file.open("w", encoding="utf-8") as fo:
            writer = csv.DictWriter(fo, fieldnames=headers)
            writer.writeheader()

            for md in documents:


                row = {
                    "uuid":md.yaml_block['UUID'],
                    'title':md.yaml_block['title']
                    'path':relative_path(md.filename.parent, document_root) / f'{md.filename.stem}.html'
                }

                log.debug(f"Writing: {md.filename}")
                writer.writerow(row)

        log.debug("BasicCSV - Completed.")
