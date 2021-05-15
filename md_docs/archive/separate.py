#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = 2e5f894a-3322-11eb-8fed-60f262a5770a
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-11-30
# -----------

"""
This module will take a set of separate markdown files defined in a .lst file, copy them
to a tmp folder maintaining their relative folder structure. During the copy process, the
markdown files will be altered to support conversion into separate files. Typically, this
use case will only be used to convert the markdown to html. The only thing that needs to be
adjusted is the markdown relative links that point to other markdown files. They will need
to be renamed to point to the new file extension.

It should start with a single .lst file.

The main operation of these methods is via a *.lst file. The .lst file contains
references to the markdown files in the order to be merged. It can contain comments and
relative paths to files. Think of a .lst file like the table of contents describing how
the various bits of information are ordered to form a coherent set of document. It can also
include other .lst files. Ideally these methods should work from one, and only one .lst file
at the top of the hierarchy.

Here is an example .lst file:

```
# This is a comment and will be ignored
# each line is the path to markdown file
# The path is relative to the location of the .lst file
# Each file will be merged, in order, forming one large file
# You can add other .lst files and they will be read
# .lst files can be located anywhere in the document structure

# NOTE: The path is relative to the location of the .lst file
./documents/index.md
./documents/ch0_0_preamble.md
./documents/ch0_1_images.md
./documents/ch0_2_equations.md

# You can include other .lst files within the list
./documents/test.lst
```

From the .lst file example, there are a number of documents that will be copied to a temporary
stagging area. During the process, the markdown intra-documents links (and possible other things) will be
modified so that they point to the correct file after the conversion process is completed.

The methods in this module are designed to work with the standard python logging system.
Some information is relegated to debug, but most is set for the info level.


"""

# System Modules
import re
import logging
from pathlib import Path

# Custom Modules
from .markdown_classifiers import MarkdownLinkRule, AbsoluteURLRule, RelativeMarkdownURLRule, MarkdownImageRule
from .markdown import adjust_markdown_links

# Module level logging
log = logging.getLogger(__name__)

# def adjust_markdown_links(line, md_file, **kwargs):
#     """

#     Given a line, check to see if it contains a markdown link. If it contains
#     a markdown link we need to check for intra document links and adjust them.

#     A markdown link is of the form: [text](url)

#     1. Does the line contain a markdown link?
#     2. Is the url portion absolute (http://www.iring.ca)?
#     3. Is the url relative (../file.md#section_title)?

#     - If it is not a markdown link the line is returned unaltered.
#     - If the url is absolute, the line is returned unaltered.

#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     md_file:pathlib.Path
#         - The full path to the markdown file that the line is from.

#     # Return

#     The line object with modifications to any markdown links as required.

#     # Note

#     The line classifier rules perform memoization and should be instantiated above
#     the loop that calls this method. I don't expect many duplicate lines so this
#     optimization is not necessary. Mostly it is about the match and the extract
#     data

#     """

#     md_link_rule = MarkdownLinkRule()

#      # Contains a valid markdown link?
#     if md_link_rule.match(line.strip()):

#         absolute_url_rule = AbsoluteURLRule()
#         relative_md_url_rule = RelativeMarkdownURLRule()

#         results = md_link_rule.extract_data(line.strip())

#         # can be multiple links in the line...
#         for r in results:

#             url = r['link']

#             # Is absolute url?
#             if absolute_url_rule.match(url):
#                 pass # we can ignore this

#             # Is relative reference to a markdown file?
#             elif relative_md_url_rule.match(url):
#                 results = relative_md_url_rule.extract_data(url)

#                 if results['md']:
#                     # we have a relative path to the markdown file, we need to remove it from the line.

#                     log.debug(f'Replacing .md extension with .html: "{line}"  ')
#                     line = line.replace('.md', '.html')

#             else:

#                 log.debug(f'Warning - Unrecognized link -> {md_file.name} - "{line}"')

#     return line

def copy_adjust(files=None, tmp=None, documents=None, **kwargs):
    """

    Read the contents of the .lst file (start). Copy the files, maintaining
    the relative folder path) to a temporary folder. The copied files will
    have markdown intra-document links adjusted to point to .html instead of
    the .md files.

    # Parameters

    files:list(pathlib.Path)
        - The list of markdown files to copy and adjust to a temporary folder.

    tmp:pathlib.Path
        - The path to the temporary folder to copy the markdown files too.

    documents:pathlib.Path
        - The path to the root of the documents folder. All markdown should be stored nested under here.

    # Return

    A tuple, containing the path to the tmp folder and a list of Path objects pointing
    to the copied markdown files.

    """

    tmp_files = []

    for md in files:
        log.info(f'Reading {md.name}...')

        # Construct the relative path to the md file in the tmp folder
        tmp_path = tmp.joinpath(md.relative_to(documents))
        tmp_path.parent.mkdir(parents=True, exist_ok=True)

        log.debug(f'Writing {tmp_path.name}...')
        with tmp_path.open("w", encoding="utf-8") as fo:

            with md.open("r", encoding="utf-8") as fin:
                for line in fin.readlines():

                    line = adjust_markdown_links(line, md, replace_md_extension=True, **kwargs)

                    fo.write(line)

        tmp_files.append(tmp_path)

    return tmp_files




