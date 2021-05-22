#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 9de6d1d4-bb0e-11eb-8e16-a1c71b5bec55
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       =  2021-05-22
# -----------

"""

"""

# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# Custom Modules

from .common import relative_path

from .document import (
    MarkdownDocument,
)

from .markdown import (
    section_to_anchor,
    clean_atx_header_text,
)


def create_table_of_contents(
    lst=None,
    include_sections=False,
    **kwargs,
):
    """

    Given a LST file, construct a table of contents to the Markdown files
    it points too.

    ```
    - [test](./test.md)
        - [header 1](./test.md#header-1)
            - [header 2](./test.md#header-2)
            - [Natural Numbers](./test.md#natural-numbers)
    ```

    # Parameters

    lst:LSTDocument
        - The list file we want to construct a table of contents for

    include_sections:bool
        - include markdown document sections as part of the table of contents
        - default - False

    # Parameters (kwargs)

    depth:int
        - How many headers to display, a number from 0 to 6. 0 would be a link to the markdown file, 1 to 6 would
        refer to the ATX headers within that file.
        - Default - 6 - include all headers

    ignore:set(str)
        - a set of files that we do not want to add to the TOC.
        - Should be a set for efficient membership testing, but could be a list or tuple.
        - Default - empty set - set()

    # Return

    A list of strings representing the markdown table of contents

    # NOTE

    All links passed into the method should be relative to the document root

    """

    depth = kwargs["depth"] if "depth" in kwargs else 6

    if depth < 0 or depth > 6:
        raise ValueError("depth has to be in the range [0, 6]...")

    # If ignore is not in kwargs or it is None, default it to an empty set
    ignore = kwargs["ignore"] if "ignore" in kwargs and kwargs["ignore"] else set()

    toc = []

    for path in lst.links:

        # Is the file in the ignore list?
        if str(path) in ignore:
            continue

        md = MarkdownDocument(path)

        md_relative = relative_path(lst.filename.parent, path.parent)
        url = Path(md_relative).joinpath(path.name)

        sanitized_file_name = (
            url.stem.replace("-", " ").replace("_", " ").title().strip()
        )

        yb = md.yaml_block

        if yb and "title" in yb:
            sanitized_file_name = yb["title"]

        toc.append(f"- [{sanitized_file_name}]({url})" + "{.toc-file}")

        if not include_sections:
            continue

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
    toc = [l + "\n" for l in toc]

    # Insert and append linefeed so we can be sure the list is generated properly
    toc.insert(0, "\n")
    toc.append("\n")

    return toc

    # # ---------------
    # # ---------------
    # # We need the full path to the list file in order to correctly resolve the relative links
    # lst_full_path = document_root.joinpath(lst).resolve()

    # # Recursively resolve all markdown links within the LST file
    # # NOTE: The links within the LST should be relative to the LST file

    # lst_md_links = find_lst_links(lst, lst_links)

    # for md in lst_md_links:

    #     key = str(md.link)

    #     # Is the file in the ignore list?
    #     if key in ignore:
    #         continue

    #     md_full = document_root.joinpath(md.link).resolve()

    #     md_relative = relative_path(lst_full_path.parent, md_full.parent)
    #     url = Path(md_relative).joinpath(md_full.name)

    #     sanitized_file_name = (
    #         url.stem.replace("-", " ").replace("_", " ").title().strip()
    #     )

    #     # See if we can extract the title from the YAML block. If we can
    #     # we'll use that to name the link.
    #     yb = extract_yaml(md_file_contents[key])

    #     if yb and "title" in yb:
    #         sanitized_file_name = yb["title"]

    #     toc.append(f"- [{sanitized_file_name}]({url})" + "{.toc-file}")

    #     if not include_sections:
    #         continue

    #     if key in md_file_contents:

    #         headers = find_all_atx_headers(md_file_contents[key])

    #         for level, text in headers:

    #             if level > depth:
    #                 continue

    #             anchor = section_to_anchor(text)

    #             text = clean_atx_header_text(text).title()

    #             # if the first header matches the file name, we'll skip it
    #             if text == sanitized_file_name:
    #                 continue

    #             # indent two spaces for every level we find.
    #             indent = "  " * (level)

    #             # can't have whitespace between the link and the attribute
    #             toc.append(
    #                 f"{indent}- [{text}]({url}#{anchor})" + "{.toc-file-section}"
    #             )

    # # add line feed otherwise
    # toc = [l + "\n" for l in toc]

    # # Insert and append linefeed so we can be sure the list is generated properly
    # toc.insert(0, "\n")
    # toc.append("\n")

    # return toc


def create_blog_toc(
    lst=None,
    **kwargs,
):
    """
    Take the files and generate a blog table of contents. It creates a list
    with the article date and article title:

    ```
    - yyyy-mm-dd - [article title](article_title.md)
    ```

    # Parameters

    lst:LSTDocument
        - The dictionary key for the list file that we want to construct

    lst_links:dict[str:pathlib.Path]
        - a dictionary containing the links within the LST files

    md_file_contents:dict(str:list(str))
        - A dictionary keyed by the path string of the file. It contains the
        contents of each md file in the system. The idea is to look up the
        contents of each file in md_files in this dictionary.

    # Parameters (kwargs)

    ignore:set(str)
        - a set of files that we do not want to add to the TOC.
        - Should be a set for efficient membership testing, but could be a list or tuple.
        - Default - empty set - set()

    # Return

    The markdown contents representing the index.

    # NOTE

    The markdown files must contain a YAML block and it is looking for
    the kwargs - "date" and "title"

    All paths should be relative to a common root.

    It will add attributes to the elements so they can be styled by css
    if applicable

    The list itself is wrapped in a div tag i.e. `:::` and the .index-file-lst
    attribute is added to it.

    The date gets `.index-file-date`

    The title gets `.index-file-link`

    """

    # If ignore is not in kwargs or it is None, default it to an empty set
    ignore = kwargs["ignore"] if "ignore" in kwargs and kwargs["ignore"] else set()

    # https://pandoc.org/MANUAL.html#divs-and-spans Creates a div without resorting to native html
    contents = ["::: {.index-file-lst}\n"]

    for path in lst.links:

        # Is the file in the ignore list?
        if str(path) in ignore:
            continue

        md = MarkdownDocument(path)

        yb = md.yaml_block

        if yb and "date" in yb and "title" in yb:
            contents.append(
                f"- [{yb['date']}]{{.index-file-date}} - [{yb['title']}]({mds}){{.index-file-link}}\n"
            )

    # for md in [l.link for l in find_lst_links(lst, lst_links)]:

    #     mds = str(md)

    #     # Is the file in the ignore list?
    #     if mds in ignore:
    #         continue

    #     if mds in md_file_contents:

    #         yb = extract_yaml(md_file_contents[mds])

    #         if yb and "date" in yb and "title" in yb:
    #             contents.append(
    #                 f"- [{yb['date']}]{{.index-file-date}} - [{yb['title']}]({mds}){{.index-file-link}}\n"
    #             )

    contents.append(":::\n")

    return contents
