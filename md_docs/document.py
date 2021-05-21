#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 99141802-ba36-11eb-b71c-5daaafeb5856
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-21
# -----------

"""
"""

# ------------
# System Modules - Included with Python

import logging

from pathlib import Path

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules

from md_docs.markdown import (
    find_all_atx_headers,
    extract_all_markdown_links,
)

from md_docs.pandoc import extract_yaml

# -------------
# Logging

log = logging.getLogger(__name__)
# -------------

def reverse_relative_links(md_files, root=None):
    """

    Takes a list of MarkdownDocument and constructs a relative link
    lookup dictionary.

    # Parameters

    md_files:list(MarkdownDocument)
        - The list of MarkdownDocument objects to create a reverse lookup
        list from.
        - The list well be keyed by the markdown file path and contain a
        list of internal links resolved to the proper path

    root:pathlib.Path
        - The root folder to make links relative to.

    # Return

    a dictionary

    """

    md_link_lookup = {}

    for md in md_files:

        key = md.filename

        if root:
            key = key.relative_to(root)

        md_link_lookup[key] = []

        for url in md.relative_links:

            p = md.filename.parent.joinpath(url[1]['md']).resolve()

            if root:
                p = p.relative_to(root)

            md_link_lookup[key].append(p)

    return md_link_lookup

class MarkdownDocument():
    """
    This class will represent a Markdown file in the system.

    # Attributes

    filename: pathlib.Path
        - The path to the Markdown file that the instance will represent.

    contents: list(str)
        - The contents of the markdown file line-by-line

    headers: dict
        - A dictionary keyed by the ATX header depth (1 to 6) with a list
        containing the line numbers where they exist in the document.

    yaml_block: dict
        - A dictionary representing the contents of all the YAML blocks
        within the document.

    links:list(tuple)
        - The list of all Markdown links contained within the file. The tuple:
            - line number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'text' - The text portion of the markdown link
                - 'link' - The URL portion of the markdown link

    absolute_links:list(tuple)
        - The list of all absolute Markdown links contained within the file. The tuple:
            - line_number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'text' - The text portion of the markdown link
                - 'link' - The URL portion of the markdown link

    relative_links:list(tuple)
        - The list of all relative Markdown links contained within the file. The tuple:
            - line_number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'text' - The text portion of the markdown link
                - 'link' - The URL portion of the markdown link
                - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
                - "md": result.group("md"),
                - "section_span": result.span("section"),
                - "section": section attribute i.e ../file.md#id <- the id portion,

    image_links:list(tuple)
        - The list of Markdown image links contained within the file. The
        tuple:
            - line number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'caption' - The image caption portion of the link -> ![image caption](URL)
                - 'image' - The url to the image
    """

    def __init__(self, filename):
        """
        """

        self.filename = filename

        # --------
        # Read the Contents

        with self.filename.open("r", encoding="utf-8") as fin:
            self.contents = fin.readlines()

        # --------
        # Extract the Headers

        # line number, header depth (1 to 6), header text
        # x, y, z

        headers = find_all_atx_headers(
            self.contents,
            include_line_numbers=True,
        )

        self.headers = {}
        for item in headers:

            line_number, depth, _ = item
            self.headers.setdefault(depth, []).append(line_number)

        # --------
        # Extract YAML Block(s)

        self.yaml_block = extract_yaml(md_lines=self.contents)

        # --------
        # Extract Links - all, absolute, relative and image

        self.links, self.absolute_links, self.relative_links, self.image_links = extract_all_markdown_links(self.contents)

        # --------
        # Create Reverse Lookup

        # Give a text string representing a line, return the line number within
        # the document

        self.reverse = {}

        # we could have duplicate lines, create a list of lines that match
        # the text
        for i, k in enumerate(self.contents):

            self.reverse.setdefault(k, []).append(i)

    def __eq__(self, other):
        return self.filename == other.filename

    def __hash__(self):
        return hash(self.filename)

    def __lt__(self, other):
         return self.filename < other.filename


class LSTDocument():
    """
    Represents an LST file in the system. It will resolve all the
    links relative to the current LST file to actual paths to Markdown
    files. Any nested LST will be resolved and added.

    It is assumed that links with the LST file are relative to the location
    of the current LST file.

    # Attributes

    filename: pathlib.Path
        - The path to the LST file that the instance will represent.
        - The path needs to be the full path to the LST file.

    contents: list(str)
        - The contents of the LST file line-by-line

    links: list(pathlib.Path)
        - The list of links contained with the file.
        - LST files will be resolved recursively and replaced with the
        Markdown links.


    # NOTE

    Only pathlib.Path are stored. They would have to be converted to
    MarkdownDocument objects in another process

    We are also not going to validate the Markdown file links within the
    process. That will be left to validation processes.
    """

    def __init__(self, filename):
        """
        """

        self.filename = filename

        # --------
        # Read the Contents

        with self.filename.open("r", encoding="utf-8") as fin:
            self.contents = fin.readlines()

        self.links = []

        for line in self.contents:

            row = line.strip().partition("#")

            # Is the line commented or empty?
            if len(row[0]) == 0:
                continue

            p = self.filename.parent.joinpath(row[0]).resolve()

            if p.suffix.lower() == ".md":

                self.links.append(p)

            if p.suffix.lower() == ".lst":

                lst = LSTDocument(p)

                self.links.extend(lst.links)


