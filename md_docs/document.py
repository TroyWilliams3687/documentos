#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 99141802-ba36-11eb-b71c-5daaafeb5856
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-05-21
-----------
"""

# ------------
# System Modules - Included with Python

from functools import cached_property


# ------------
# 3rd Party - From pip

# ------------
# Custom Modules

from .markdown import (
    find_all_atx_headers,
    extract_all_markdown_links,
)

from .pandoc import extract_yaml


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

        for url in md.relative_links():

            p = md.filename.parent.joinpath(url[1]["md"]).resolve()

            if root:
                p = p.relative_to(root)

            md_link_lookup[key].append(p)

    return md_link_lookup


class MarkdownDocument:
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
                - "section": section attribute i.e ../file.md#id <- the id portion

    image_links:list(tuple)
        - The list of Markdown image links contained within the file. The
        tuple:
            - line number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'caption' - The image caption portion of the link -> ![image caption](URL)
                - 'image' - The url to the image

    # NOTE

    How to clear the cache:
    - https://stackoverflow.com/questions/59899732/python-cached-property-how-to-delete

    ```
    def _clear_cache(self):
        for cache_item in [
            'contents',
            'headers',
            'yaml_block',
            'links',
            'line_look_up ',
        ]:
            if cache_item in self.__dict__:
                del self.__dict__[cache_item]
    ```
    """

    def __init__(self, filename, **kwargs):
        """

        # Parameters

        filename:pathlib.Path
            - The path to the Markdown file

        """

        self.filename = filename

    def __eq__(self, other):
        return self.filename == other.filename

    def __hash__(self):
        return hash(self.filename)

    def __lt__(self, other):
        return self.filename < other.filename

    @cached_property
    def contents(self):
        """
        Return a list representing the contents of the markdown file.
        """

        with self.filename.open("r", encoding="utf-8") as fin:
            return fin.readlines()

    @cached_property
    def headers(self):
        """
        Extract the ATX header information from the Markdown.

        # Return

        A dictionary keyed by header depth (1 to 6) with
        a list of tuples containing line numbers containing the ATX header at that depth and
        the text of the header
        (23, "[hello World](./en.md) ")

        """

        items = find_all_atx_headers(
            self.contents,
            include_line_numbers=True,
        )

        headers = {}
        for item in items:

            # (x, y, z) <- basic format
            # x - line number
            # y - header depth (1 to 6)
            # z - header text

            line_number, depth, text = item
            headers.setdefault(depth, []).append((line_number, text))

        return headers

    @cached_property
    def yaml_block(self):
        """
        Extract the YAML blocks from the Markdown.

        # Return

        A dictionary containing the YAML variables.

        # NOTE

        If the file contains
        multiple YAML blocks and duplicate variables, the variables from
        subsequent YAML blocks will overwrite those from earlier blocks.
        """

        return extract_yaml(md_lines=self.contents)

    @cached_property
    def links(self):
        """
        Extract all Markdown links:
        - all links (absolute and relative)
        - absolute links
        - relative links
        - image links - links formatted to display images

        # Return

        a tuple containing:

        0. all_links
        1. absolute_links
        2. relative_links
        3. image_links

        each of these is a list of tuples:

        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'text' - The text portion of the markdown link
            - 'link' - The URL portion of the markdown link

        relative_links:
        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'text' - The text portion of the markdown link
            - 'link' - The URL portion of the markdown link
            - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
            - "md": result.group("md"),
            - "section_span": result.span("section"),
            - "section": section attribute i.e ../file.md#id <- the id portion,

        image_links:
        - line number (0 based)
        - dict
            - 'full' - The full regex match - [text](link)
            - 'caption' - The image caption portion of the link -> ![image caption](URL)
            - 'image' - The url to the image

        """

        return extract_all_markdown_links(self.contents)

    def all_links(self):
        return self.links[0]

    def absolute_links(self):
        return self.links[1]

    def relative_links(self):
        return self.links[2]

    def image_links(self):
        return self.links[3]

    @cached_property
    def line_look_up(self):
        """
        Give a text string representing a line, return the line number within
        the document.

        # Return

        A dictionary keyed by a string with a list of integers representing
        the line numbers.

        """

        reverse = {}

        # we could have duplicate lines, create a list of lines that match
        # the text
        for i, k in enumerate(self.contents):

            reverse.setdefault(k, []).append(i)

        return reverse


class LSTDocument:
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

    def __init__(self, filename, **kwargs):
        """ """

        self.filename = filename

    @cached_property
    def contents(self):
        """
        Return a list representing the contents of the LST file.
        """

        with self.filename.open("r", encoding="utf-8") as fin:
            return fin.readlines()

    @cached_property
    def links(self):
        """
        This property references the Path objects to
        all the markdown files within the document.
        """

        links = []

        for line in self.contents:

            left, _, _ = line.strip().partition("#")

            # Is the line commented or empty?
            if len(left) == 0:
                continue

            f = self.filename.parent.joinpath(left).resolve()

            if f.suffix.lower() == ".md":
                links.append(f)

            if f.suffix.lower() == ".lst":
                lst = LSTDocument(f)
                links.extend(lst.links)

        return links


def search(root=None, extension=".md", document=MarkdownDocument):
    """
    Search for all of the files starting from the root folder that
    match the file extension. Create a document object from it and
    add it to the list.

    # Parameters

    root:pathlib.Path
        - The root folder to search recursively

    extension:str
        - The file extension to search for
        - Default - .md
        - Note: it has to be dotted i.e. .md and not md

    document:Document
        - A method required to create the new objects from
        - Default - MarkdownDocument

    """

    files = []

    for f in root.rglob("*.*"):

        if f.suffix.lower() == extension:

            files.append(document(f))

    return files
