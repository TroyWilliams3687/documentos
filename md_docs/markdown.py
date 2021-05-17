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
This module will house code that performs operations on markdown files. Usually the files
will be represented by lists of strings.


We will try to stick to commonmark as muck as possible. However, pandoc has specific syntax:

- https://spec.commonmark.org/0.29/
- https://pandoc.org/MANUAL.html#pandocs-markdown

"""

# System Modules
import re
import logging

from pathlib import Path

# Custom Modules
from .common import read_lst, find_lst_links, relative_path

from .markdown_classifiers import (
    ATXHeaderRule,
    MarkdownLinkRule,
    MarkdownAttributeSyntax,
    CodeFenceClassifier,
    RelativeMarkdownURLRule,
    MarkdownImageRule,
    YamlBlockClassifier,
)

from .pandoc import extract_yaml

# Module level logging
log = logging.getLogger(__name__)


# define the rules outside so they can take advantage of memoization (if any headers repeat - probably unlikely)
atx_rules = [
    ATXHeaderRule(key="Rule 1", count=1),
    ATXHeaderRule(key="Rule 2", count=2),
    ATXHeaderRule(key="Rule 3", count=3),
    ATXHeaderRule(key="Rule 4", count=4),
    ATXHeaderRule(key="Rule 5", count=5),
    ATXHeaderRule(key="Rule 6", count=6),
]

md_link_rule = MarkdownLinkRule()
md_attribute_syntax_rule = MarkdownAttributeSyntax()


class MDFence():
    """
    A simple object to wrap up tests to see if we are in code blocks
    or YAML blocks. We can't be in both at the same time.
    """

    def __init__(self):
        """ """
        self.code_rule = CodeFenceClassifier()
        self.yaml_rule = YamlBlockClassifier()

        self.in_block_type = {
            "code": False,
            "yaml": False,
        }

    def in_block(self, line):
        """ """

        if self.in_block_type["code"]:

            # Are we at the end?
            if self.code_rule.match(line):
                self.in_block_type["code"] = False

            # We are at the last line of the code block, but caller
            # would consider this line is still in the block. We
            # return True, but we have set the flag to false
            return True

        if self.in_block_type["yaml"]:

            # Are we at the end?
            if self.yaml_rule.match(line):
                self.in_block_type["yaml"] = False

            # We are at the last line of the code block, but caller
            # would consider this line is still in the block. We
            # return True, but we have set the flag to false
            return True

        # If we made it this far, we are not in a code block. Check to see if we are entering one

        # Have we entered a code block?
        if self.code_rule.match(line):

            self.in_block_type["code"] = True

            return True

        # Have we entered a YAML block?
        if self.yaml_rule.match(line):

            self.in_block_type["yaml"] = True

            return True

        return False


def find_atx_header(line, **kwargs):
    """

    Determine if the line is an ATX header or not. If it is an ATX header it will
    return a tuple containing the header number (1 - 6) and the text of the header.

    # Parameters

    line:str
        - The string to check for an ATX header.

    # Return

    a tuple containing the heading level (1-6) and the string of the header (not the ATX header syntax).

    # Note

    We do not consider more than 6 indentation levels to be an ATX header.
    (https://spec.commonmark.org/0.24/#atx-headings).

    """

    for rule in atx_rules:
        if rule.match(line):
            return rule.atx_count, rule.extract_data(line)

    return None


def find_all_atx_headers(contents, **kwargs):
    """
    Given a list of strings representing the contents of a markdown
    file, return a list of section headers.

    # Parameters

    contents:list(str)
        - The list of strings representing the contents of a markdown file.

    # Parameters (kwargs)

    include_line_numbers:bool
        - Add the line number in the contents where it found the contents

    # Return

    A list of tuples representing the header level (1 to 6) and the header text

    """

    include_line_numbers = (
        kwargs["include_line_numbers"] if "include_line_numbers" in kwargs else False
    )

    headers = []

    ignore_block = MDFence()


    for i, line in enumerate(contents):

        if ignore_block.in_block(line):
            continue

        result = find_atx_header(line)

        if result:

            if include_line_numbers:

                result = (i, *result)

            headers.append(result)

    return headers


def find_attribute_syntax(s):
    """

    Given a string, find the markdown attribute syntax it may contain.

    Examples of the attribute syntax:

    ```
    # Header 1 {#header_1 .sidebar}

    ## Header 2 {#header_2 .topbar}

    ![image](./path/to/image.png) {#image_1 .image_link}

    ![image](./path/to/image.png) {.image_link #image_1}

    # Header 1 { #header_1 .sidebar}

    ## Header 2 {        #header_2 .topbar}

    ![image](./path/to/image.png) {xxx     #image_1 .image_link}

    ```

    # Parameters

    s:str
        - The string we want to search for markdown attributes

    # Return

    A list of dictionaries containing discovered attribute syntax. The dictionaries
    are keyed with:
    - 'full' - The full attribute syntax
    - 'id'   - The id portion of the syntax. This generally is used for the anchor references in a hyperlink

    """

    # Is there header attribute syntax?

    # https://pandoc.org/MANUAL.html#extension-fenced_code_attributes
    # 'Equations {#sec:ch0_2_equations-1}' <- handle this case with "header attribute syntax"
    # We are looking for {#sec:ch0_2} the hashtag identifier that denotes a section name, just return this if it is found...
    # NOTE: There should only be one match, so we return the first match

    if md_attribute_syntax_rule.match(s):

        return md_attribute_syntax_rule.extract_data(s)

    else:

        return []


def section_to_anchor(s):
    """
    Given the text of an ATX header, construct a valid anchor from it. NOTE: it
    is expecting the text of the ATX header and not the syntax defining the ATX header
    i.e. it shouldn't contain leading #.

    From [Pandoc](https://pandoc.org/MANUAL.html#extension-auto_identifiers):
    ```
    The default algorithm used to derive the identifier from the heading text is:

    - Remove all formatting, links, etc.
    - Remove all footnotes.
    - Remove all non-alphanumeric characters, except underscores, hyphens, and periods.
    - Replace all spaces and newlines with hyphens.
    - Convert all alphabetic characters to lowercase.
    - Remove everything up to the first letter (identifiers may not begin with a number or punctuation mark).
    - If nothing is left after this, use the identifier section.

    Thus, for example,
    Heading                         Identifier
    Heading identifiers in HTML     heading-identifiers-in-html
    Maître d'hôtel                  maître-dhôtel
    *Dogs*?--in *my* house?         dogs--in-my-house
    [HTML], [S5], or [RTF]?         html-s5-or-rtf
    3. Applications                 applications
    33                              section

    Preamble {#sec:ch0_0_preamble-1}  sec:ch0_0_preamble-1
    ```

    These anchors can be used in links:
    ```
    See the section on
    [heading identifiers](#heading-identifiers-in-html-latex-and-context).
    ```

    # NOTE

    Pandoc Extension: gfm_auto_identifiers

    Changes the algorithm used by auto_identifiers to conform to GitHub’s
    method. Spaces are converted to dashes (-), uppercase characters to
    lowercase characters, and punctuation characters other than - and _ are
    removed.

    We'll stick with the basics (for now).

    Reference:

    - https://stackoverflow.com/questions/1007481/how-do-i-replace-whitespaces-with-underscore

    Could use some slugify methods:

    - https://github.com/un33k/python-slugify

    """

    # Is there header attribute syntax?

    # https://pandoc.org/MANUAL.html#extension-fenced_code_attributes
    # 'Equations {#sec:ch0_2_equations-1}' <- handle this case with "header attribute syntax"
    # We are looking for {#sec:ch0_2} the hashtag identifier that denotes a section name, just return this if it is found...
    # NOTE: There should only be one match, so we return the first match

    if md_attribute_syntax_rule.match(s):
        for r in md_attribute_syntax_rule.extract_data(s):
            return r["id"]

    # Do we have markdown links?
    # [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) Usage

    if md_link_rule.match(s):
        for r in md_link_rule.extract_data(s):
            s = s.replace(r["full"], r["text"])

    # Convert all alphabetic characters to lowercase.
    s = s.lower()

    # Replace all spaces and newlines with hyphens.
    s = re.sub(r"\s+", "-", s)

    # Remove all non-alphanumeric characters, except underscores, hyphens, and periods.
    s = re.sub(r"[^\w_\-.]", "", s)

    # we could probably do more, but let's leave it here for now....

    return s


def create_file_toc(lines=None, path=None, **kwargs):
    """
    Given a list of lines in a markdown file, generate a table of contents
    for the file. It will examine each line in the file for a valid ATX
    header and use that to construct a markdown link. It will return a list
    of all of the links which construct a toc for the file.

    ```
    - [test](./test.md)
        - [header 1](./test.md#header-1)
            - [header 2](./test.md#header-2)
            - [Natural Numbers](./test.md#natural-numbers)
    ```

    # Parameters

    lines:list(str)
        - The list of lines that makeup the markdown file.

    path:pathlib.Path
        - The path to the file where the lines were gathered from.
        - It can be a relative path or absolute.

    # Return

    A list containing markdown links to sections within the document.

    """

    # remove dashes from file names

    if path:
        file_name = path.stem.replace("-", " ").replace("_", " ").title()
        toc = [f"- [{file_name}]({path})" + "{.toc-file}"]

    else:
        toc = []

    ignore_block = MDFence()

    for line in lines:

        if ignore_block.in_block(line):
            continue

        result = find_atx_header(line)

        if result:
            level, text = result

            anchor = section_to_anchor(text)

            # remove attributes from the text, if any
            if md_attribute_syntax_rule.match(text):
                for r in md_attribute_syntax_rule.extract_data(text):
                    text = text.replace(r["full"], "")

                text = text.strip()

            # remove markdown links, replacing them with text
            if md_link_rule.match(text):
                for r in md_link_rule.extract_data(text):
                    text = text.replace(r["full"], r["text"])

                text = text.strip()

            indent = "  " * (level)  # indent two spaces for every level we find.

            if path:
                link = (
                    f"{indent}- [{text}]({path}#{anchor})" + "{.toc-file-section}"
                )  # can't have whitespace between the link and the attribute

            else:
                link = f"{indent}- [{text}](#{anchor})" + "{.toc-file-section}"

            toc.append(link)

    return toc


# def create_toc(files=None, root=None, **kwargs):
#     """
#     Given a list of markdown files generate a list of strings that can be
#     written to a markdown file creating a table of contents. It will iterate
#     through each file searching for ATX headers. It will then determine

#     # Parameters

#     files:list(pathlib.Path)
#         - The list of markdown files to copy and adjust to a temporary folder.

#     root:pathlib.Path
#         - The common root of the files. It is assumed they will be under a common root
#         folder and we can use it to derive relative paths for intra-document links.

#     # Return

#     A list of strings containing a markdown link pointing to the document and section.
#     It will be a bulleted list indented by the column header count.

#     # Note

#     - The table of contents will be ordered by the list containing the files.

#     - The bullet needs to be indented by 2 spaces to be detected as nested lists.

#     """

#     toc = []

#     for md in files:

#         with md.open("r", encoding="utf-8") as fin:

#             file_toc = create_file_toc(lines=fin.readlines(),
#                                        path=md.relative_to(root))

#             if file_toc:
#                 toc.extend(file_toc)

#     return toc


def construct_md_list(
    start_lst=None,
    list_file_contents=None,
    combined=None,
):
    """
    Takes a .lst file and constructs a list of .md files that are associated with it.
    It works recursively on nested .lst files contained within it.

    # Parameters
    start_lst:str
        - The dictionary key for the list file that we want to construct

    list_file_contents:dict[str:pathlib.Path]
        - a dictionary containing .lst files and their contents. start_lst should
        be a member of the dictionary

    combined:list[pathlib.Path]
        - A list of md file paths stored in the .lst files and nested .lst files.

    # Returns

    A list of md file paths stored in the .lst files and nested .lst files.

    """

    if not combined:
        combined = []

    for f in list_file_contents[str(start_lst)]:

        if f.suffix == ".md":
            combined.append(f)

        if f.suffix == ".lst":
            combined.extend(
                construct_md_list(
                    start_lst=f,
                    lst_files=lst_files,
                    combined=combined,
                )
            )

    return combined


def create_file_cache(root=None, extensions=(".md", ".lst")):
    """

    Recursively search from root folder for all files that match the extensions.
    It will return a tuple of dictionaries (matching the order of the extensions tuple).
    The dictionaries will be keyed by the file name and path (relative to the root folder)
    and the values associated with the key will be a list of strings representing the contents
    of the file.

    The idea is to use the caches instead of reading the file multiple times during the processing.

    root:pathlib.Path
        - The path to the root of the document folder. All paths well be made relative to
        this path.

    extensions:tuple(str)
        - The extensions we are looking to create a cache for.
        - default: ('.md', '.lst')

    # Return

    A dictionary containing dictionaries representing the files that match the extension. The
    key will be the extension from the extensions tuple.

    # NOTE

    All keys, i.e. file links are relative to the root folder.

    """

    caches = {}

    for f in root.rglob("*.*"):

        if f.suffix in extensions:

            key = f.relative_to(root)

            with f.open("r", encoding="utf-8") as fin:
                contents = fin.readlines()

            caches.setdefault(f.suffix, {})[str(key)] = contents

    return caches


def create_caches(root=None):
    """
    Recursively search the root folder for all .lst and .md files. It will
    construct two caches. One cache will hold the .lst files
    and their contents. The other will hold the .md file and their contents.

    The idea is to use the caches instead of reading the file multiple times
    during the processing.

    # Parameters

    root:pathlib.Path
        - The path to the root of the document folder. All paths well be made relative to
        this path.

    # Return

    a tuple containing the lst file contents and the md file contents.
    """

    list_file_contents = {}
    md_file_contents = {}

    for f in root.rglob("*.*"):

        if f.suffix == ".md":

            key = f.relative_to(root)

            with f.open("r", encoding="utf-8") as fin:
                contents = fin.readlines()

            md_file_contents[str(key)] = contents

        elif f.suffix == ".lst":
            key = f.relative_to(root)
            content = read_lst(f)

            list_file_contents[str(key)] = [p.relative_to(root) for p in content]

    return list_file_contents, md_file_contents


def extract_markdown_links(line, **kwargs):
    """

    Given a line, return all of the markdown links. The markdown
    image links will be of the form:

    (Description)[URL]

    (This is a link)[../file.md#section_title]

    This method will return a list of link dictionaries for each link
    found in the line.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    Assume that the markdown link looks like this in the text:
    - (Description)[URL]
    - (This is a link)[../file.md#section_title]
    - [text](link)

    This method will return a list of dictionaries keyed as follows:

    A list containing dictionaries representing each match. The dictionary
    contains the following keys:

    full - The full regex match - [text](link)
    text - The text portion of the markdown link
    link - The URL portion of the markdown link

    # Note

    The line classifier rules perform memoization and should be instantiated above
    the loop that calls this method. I don't expect many duplicate lines so this
    optimization is not necessary. Mostly it is about the match and the extract
    data

    """

    link_rule = MarkdownLinkRule()

    matches = []

    if link_rule.match(line.strip()):

        matches = link_rule.extract_data(line.strip())

    return matches


def extract_relative_markdown_links(line, **kwargs):
    """

    Given a line, check to see if it contains a relative markdown link.
    The relative markdown link will look like `../file.md#section_title`

    This method will return a list of link dictionaries for each link
    found in the line.


    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list containing dictionaries representing each match. The dictionary
    contains the following keys:

    - md -           The string representing the link.
    - section -      The string representing the section anchor, if any.
    - md_span -      A tuple(start, end) Containing the starting and ending position of the markdown link match in the string
    - section_span - A tuple(start, end) Containing the starting and ending position of the section anchor match in the string

    # Note

    The line classifier rules perform memoization and should be instantiated above
    the loop that calls this method. I don't expect many duplicate lines so this
    optimization is not necessary. Mostly it is about the match and the extract
    data

    """

    matches = []

    relative_rule = RelativeMarkdownURLRule()

    for r in extract_markdown_links(line):

        url = r["link"]

        if relative_rule.match(url):
            matches.append(relative_rule.extract_data(url))

    return matches


def extract_markdown_image_links(line, **kwargs):
    """

    Given a line, return all of the markdown image links. The markdown
    image links will be of the form:

    ![image caption](URL).

    Returns a list of dictionaries representing the image links.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list of dictionaries keyed by:

    caption - The image caption portion of the link -> ![image caption](URL)
    image - The url to the image

    """

    image_rule = MarkdownImageRule()

    matches = []

    # Contains a valid markdown link?
    if image_rule.match(line.strip()):

        matches = image_rule.extract_data(line.strip())

    return matches


def extract_relative_markdown_image_links(line, **kwargs):
    """

    Given a line, return all of the markdown image links that are relative
    links. The markdown image links will be of the form:

    ![image caption](URL).

    Returns a list of dictionaries representing the relative image links.

    # Parameters

    line:str
        - The text string to analyze for markdown links

    # Return

    A list of dictionaries keyed by:

    caption - The image caption portion of the link -> ![image caption](URL)
    image - The url to the image

    """

    relative_rule = RelativeMarkdownURLRule()

    matches = []

    for m in extract_markdown_image_links(line):

        if relative_rule.match(m["image"]):

            result = relative_rule.extract_data(m["image"])

            matches.append(result | m)

    return matches


def adjust_markdown_links(line, md_file, **kwargs):
    """

    Given the line, find all markdown links that are relative links.

    If a markdown link is detected within the line, we can do a couple
    of things to it. It will check for intra document links (relative
    links) and:

    1. Remove them, leaving a link to a section anchor
    2. Rename the .md file to .html leaving the links intact

    A markdown link is of the form: [text](url)

    1. Does the line contain a markdown link?
    2. Is the url portion absolute (http://www.iring.ca)?
    3. Is the url relative (../file.md#section_title)?

    - If it is not a markdown link the line is returned unaltered.
    - If the url is absolute, the line is returned unaltered.

    Option 1:

    - If the url is relative, the markdown file is removed
    - if the url is relative and doesn't contain a section id an exception is raised.
        - The user obviously wants to link to the beginning of the document.
        This should be allowed for the cases where the individual markdown will
        be compiled to standalone html. However, since this is a
        compressed/merged format this doesn't make sense. We could read the
        document and figure it out, but we don't want to. It should be explicit
        if we are compressing/merging the document into one compressed format.

    Option 2:

    - If the url is relative, the markdown file is renamed to .html.


    # Parameters

    line:str
        - The text string to analyze for markdown links

    md_file:pathlib.Path
        - The full path to the markdown file that the line is from.
        - This is used for exceptions so we know the file and line number
        the exception occurred on.

    # Parameters (kwargs)

    remove_relative_md_link:bool
        - For each relative markdown link discovered, it will remove
        the relative path keeping a link to the section anchor
        - Default - False

    replace_md_extension:bool
        - For each relative markdown link discovered, it will change the
        markdown extension to html
        - Default - False

    # Return

    The line object with modifications to any markdown links as required.

    # Note

    The line classifier rules perform memoization and should be instantiated above
    the loop that calls this method. I don't expect many duplicate lines so this
    optimization is not necessary. Mostly it is about the match and the extract
    data

    """

    remove_relative_md_link = (
        kwargs["remove_relative_md_link"]
        if "remove_relative_md_link" in kwargs
        else False
    )
    replace_md_extension = (
        kwargs["replace_md_extension"] if "replace_md_extension" in kwargs else False
    )

    if not remove_relative_md_link and not replace_md_extension:
        log.warning(
            f"remove_relative_md_link = {remove_relative_md_link} and replace_md_extension = {replace_md_extension} - skipping link check (At least one needs to be set)."
        )
        return line

    matches = extract_relative_markdown_links(line)

    for relative_link in matches:

        if relative_link["md"]:
            # we have a relative path to the markdown file

            if remove_relative_md_link:

                # if there is no section name, this is a problem. They will have to specify the section to link too
                if relative_link["section"] is None:
                    raise ValueError(
                        f'ERROR - Missing Section Link - {md_file.name} - "{line}" <- contains a relative link to a markdown file without a section reference "#section_name". A section id needs to be present!'
                    )

                log.debug(f'Removing relative file name from: "{line}"  ')
                line = line.replace(relative_link["md"], "")

            if replace_md_extension:

                log.debug(f'Replacing .md extension with .html: "{line}"  ')
                line = line.replace(".md", ".html")

    return line


def adjust_image_links(line, md_file, assets=None, output=None, **kwargs):
    """
    Given a line check to see if it contains a markdown image links. We
    need to see if it points to the common 'assets' folder.

    WE ASSUME THAT THE LINKS WE ARE INTERESTED IN ARE iN the 'assets'
    FOLDER (see assumptions).

    ![image caption](URL)

    # Parameters

    line:str
        - The text string to analyze for markdown links

    md_file:pathlib.Path
        - The full path to the markdown file that the line is from. It will be
        used to determine the relative path so that we can adapt the link properly.

    assets:pathlib.Path
        - The full path to the assets folder. The common folder where we are storing
        the images.

    output:pathlib.Path
        - The path to the output folder.

    # Assumptions

    We assume that all images that we use in the markdown files will be stored in the
    assets folder (a folder called 'assets'). This is hard-coded. We can modify it later if
    we need to but I want to keep this simple. We can have nested folders underneath the assets
    folder.

    We are under the assumption that the merged markdown document will be stored in a folder
    that is at the same level as the assets folder i.e.:

    - assets
    - documents/merged.md

    This means that all we have to do is modify the path to point to it i.e. ../../../assets/designer/image.png
    becomes ./assets/designer/image.png

    We are only interested in images that are stored in the 'assets' path and exist locally. Anything else will not touched.

    # Return

    If the line contains image links that are pointing to files in the assets folder a line string will
    be return that contains modifications to the path to the assets folder.
    """

    if assets is None:
        log.debug("assets = None - skipping image link check")

        return line

    if output is None:
        log.debug("output = None - skipping image link check")

        return line

    for r in extract_relative_markdown_image_links(line):

        if r["caption"] is None:
            log.warning(f"Warning - Image Missing Caption -> {md_file.name} -> {line}")

        # we need to determine if it is the path to the assets folder
        im_path = md_file.parent.joinpath(r["image"]).resolve()

        if im_path.exists():

            log.debug(f"md file: {md_file}")
            log.debug(f'Image Path: {r["image"]}')
            log.debug(f"Image Location: {im_path}")
            log.debug(f"Asset Path: {assets}")
            log.debug(f"Output Path: {output}")

            # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
            if assets in im_path.parents:

                # basically flatten the path.
                new_path = Path("./assets").joinpath(im_path.name)
                log.debug(f"New image path -> ./{new_path}")

                line = line.replace(r["image"], f"./{new_path}")

        else:
            # What happens if the image doesn't exist, but is an asset
            log.warning(
                f"WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}"
            )

    return line


def adjust_html_image_links(line, md_file, assets=None, output=None, **kwargs):
    """
    Given a line check to see if it contains an HTML image links. We
    need to see if it points to the common 'assets' folder.

    WE ASSUME THAT THE LINKS WE ARE INTERESTED IN ARE IN the 'assets'
    FOLDER (see assumptions).

    <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>

    # Parameters

    line:str
        - The text string to analyze for markdown links

    md_file:pathlib.Path
        - The full path to the markdown file that the line is from. It will be
        used to determine the relative path so that we can adapt the link properly.

    assets:pathlib.Path
        - The full path to the assets folder. The common folder where we are storing
        the images.

    output:pathlib.Path
        - The path to the output folder.

    # Assumptions

    We assume that all images that we use in the markdown files will be stored in the
    assets folder (a folder called 'assets'). This is hard-coded. We can modify it later if
    we need to but I want to keep this simple. We can have nested folders underneath the assets
    folder.

    We are under the assumption that the merged markdown document will be stored in a folder
    that is at the same level as the assets folder i.e.:

    - assets
    - documents/merged.md

    This means that all we have to do is modify the path to point to it i.e. ../../../assets/designer/image.png
    becomes ./assets/designer/image.png

    We are only interested in images that are stored in the 'assets' path and exist locally. Anything else will not touched.

    # Return

    If the line contains image links that are pointing to files in the assets folder a string will
    be returned that contains modifications to the path to the assets folder.
    """

    if assets is None:
        log.debug("assets = None - skipping image link check")

        return line

    if output is None:
        log.debug("output = None - skipping image link check")

        return line

    rule = HTMLImageRule()

    # Contains a valid HTML img link?
    if rule.match(line.strip()):

        results = rule.extract_data(line.strip())

        for r in results:

            if r["src"] is None:
                log.warning(
                    f"Warning - HTML Image Missing SRC -> {md_file.name} -> {line}"
                )

            # we need to determine if it is the path to the assets folder
            im_path = md_file.parent.joinpath(r["src"]).resolve()

            if im_path.exists():

                log.debug(f"md file: {md_file}")
                log.debug(f'Image Path: {r["src"]}')
                log.debug(f"Image Location: {im_path}")
                log.debug(f"Asset Path: {assets}")
                log.debug(f"Output Path: {output}")

                # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
                if assets in im_path.parents:

                    # basically flatten the path.
                    new_path = Path("./assets").joinpath(im_path.name)
                    log.debug(f"New HTML image path -> ./{new_path}")

                    line = line.replace(r["src"], f"./{new_path}")
            else:
                # What happens if the image doesn't exist, but is an asset
                log.warning(
                    f"WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}"
                )

    return line


def clean_atx_header_text(text):
    """

    The text of the ATX header can contain links and attributes that
    should be removed before display the text.

    # Parameters

    text:str
        - the text associated with the ATX header.

    # Return

    The cleaned text

    """

    md_link_rule = MarkdownLinkRule()
    md_attribute_syntax_rule = MarkdownAttributeSyntax()

    # Remove attributes from the text, if any
    if md_attribute_syntax_rule.match(text):

        for r in md_attribute_syntax_rule.extract_data(text):

            text = text.replace(r["full"], "")

        text = text.strip()

    # remove markdown links, replacing them with text
    if md_link_rule.match(text):

        for r in md_link_rule.extract_data(text):

            text = text.replace(r["full"], r["text"])

        text = text.strip()

    return text


def create_table_of_contents(
    lst,
    lst_links,
    md_file_contents,
    document_root=None,
    include_sections=False,
    **kwargs,
):
    """

    Given a LST file, construct a table of contents using markdown. Determine all
    of the markdown files linked in the lst file. Construct a list of markdown links
    pointing to these files. The list will contain strings that can be written to a
    markdown file.

    ```
    - [test](./test.md)
        - [header 1](./test.md#header-1)
            - [header 2](./test.md#header-2)
            - [Natural Numbers](./test.md#natural-numbers)
    ```

    # Parameters

    lst:Path
        - The list file we want to construct a table of contents for
        - The path should be relative to the document root folder i.e. document_root.joinpath(lst) should
        resolve to a valid file in the system

    lst_links:dict
        - A dictionary keyed by lst file. It contains all of the links within the lst file, both markdown and lst
        - the links are MDLink named tuple ->("line", "link", "section", "full")

    md_file_contents:dict
        - A dictionary keyed by the markdown file path (relative) containing the contents of the file

    document_root:Path
        - The path of the document root, used to create the relative links for the table of contents

    include_sections:bool
        - include markdown document sections as part of the table of contents
        - default - False

    # Parameters (kwargs)

    depth:int
        - How many headers to display, a number from 0 to 6. 0 would be a link to the markdown file, 1 to 6 would
        refer to the ATX headers within that file.
        - Default - 6 - include all headers

    # Return

    A list of strings representing the markdown table of contents

    # NOTE

    All links passed into the method should be relative to the document root

    """

    depth = kwargs['depth'] if 'depth' in kwargs else 6

    if depth < 0:
        raise ValueError('depth has to be in the range 0 to 6...')

    toc = []

    # We need the full path to the list file in order to correctly resolve the relative links
    lst_full_path = document_root.joinpath(lst).resolve()

    # Recursively resolve all markdown links within the LST file
    # NOTE: The links within the LST should be relative to the LST file

    lst_md_links = find_lst_links(lst, lst_links)

    for md in lst_md_links:

        md_full = document_root.joinpath(md.link).resolve()

        md_relative = relative_path(lst_full_path.parent, md_full.parent)
        url = Path(md_relative).joinpath(md_full.name)

        sanitized_file_name = (
            url.stem.replace("-", " ").replace("_", " ").title().strip()
        )
        toc.append(f"- [{sanitized_file_name}]({url})" + "{.toc-file}")

        if not include_sections:
            continue

        key = str(md.link)

        if key in md_file_contents:

            headers = find_all_atx_headers(md_file_contents[key])

            for level, text in headers:

                if level > depth:
                    continue

                anchor = section_to_anchor(text)

                text = clean_atx_header_text(text).title()

                # if the first header matches the file name, we'll skip it
                if text == sanitized_file_name:
                    continue

                # indent two spaces for every level we find.
                indent = "  " * (level)

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


def create_blog_toc(lst=None, lst_links=None, md_file_contents=None):
    """
    Take the files and generate a blog table of contents. It creates a list
    with the article date and article title:

    ```
    - yyyy-mm-dd - [article title](article_title.md)
    ```

    # Parameters

    lst:str
        - The dictionary key for the list file that we want to construct

    lst_links:dict[str:pathlib.Path]
        - a dictionary containing the links within the LST files

    md_file_contents:dict(str:list(str))
        - A dictionary keyed by the path string of the file. It contains the
        contents of each md file in the system. The idea is to look up the
        contents of each file in md_files in this dictionary.

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

    # https://pandoc.org/MANUAL.html#divs-and-spans Creates a div without resorting to native html
    contents = ['::: {.index-file-lst}\n']

    for md in [l.link for l in find_lst_links(lst, lst_links)]:

        if str(md) in md_file_contents:

            yb = extract_yaml(md_file_contents[str(md)])

            if yb and 'date' in yb and 'title' in yb:
                contents.append(f"- [{yb['date']}]{{.index-file-date}} - [{yb['title']}]({str(md)}){{.index-file-link}}\n")

    contents.append(':::\n')

    return contents


def adjust_markdown_contents(md_file=None, contents=None):
    """
    Examine the *.md file contents for inter-document links pointing
    to other .md files. It will rename the .md to .html. Pandoc will
    not alter the links during the transformation. If we want them to
    point to the correct location, we have to alter them.

    # Parameters

     md_files:list(pathlib.Path)
        - The list of files that we are interested in generated a table
        of contents for

    contents:list(str)
        - The list of strings representing the contents of the .md file.

    # Returns

    A list of strings representing the adjusted .md contents.

    """

    adjusted_contents = []

    for line in contents:
        adjusted_contents.append(
            adjust_markdown_links(line, md_file, replace_md_extension=True)
        )

    return adjusted_contents
