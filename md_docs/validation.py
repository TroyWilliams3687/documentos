#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 91995646-2f49-11eb-8e0d-60f262a5770a
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2020-11-25
-----------

A module for common things I'll need to process documents

"""

# System Modules
import logging
from collections import namedtuple

# 3rd Party Modules
import requests

# Custom Modules
from .markdown_classifiers import (
    MarkdownLinkRule,
    AbsoluteURLRule,
    RelativeMarkdownURLRule,
    MarkdownImageRule,
    CodeFenceClassifier,
)

from .common import read_lst

# Module level logging
log = logging.getLogger(__name__)

ValidationStatus = namedtuple(
    "ValidationStatus",
    [
        "file",  # The path to the file
        "error",  # The Error Type
        "line",  # line number the error was detected on (0 based)
        "message",  # The message associated with the error
    ],
)


def validate_absolute_url(url):
    """
    Given an absolute URL, check to see if it is valid and reachable. They
    should be of the form:

    - https://stackoverflow.com/questions/16778435/python-check-if-website-exists
    - https://en.wikipedia.org/wiki/List_of_HTTP_status_codes


    # Parameters

    url:str
        - the url to test

    # Return

    None if there are no problems otherwise a string indicating what the
    problem is.

    """

    absolute_url_rule = AbsoluteURLRule()

    # Is absolute url?
    if absolute_url_rule.match(url):

        # https://stackoverflow.com/questions/16778435/python-check-if-website-exists
        # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

        log.debug(f"Requesting {url}")

        request = requests.head(url)
        rc = request.status_code

        log.debug(f"Return code - {rc} -> {url}")

        if rc >= 400:

            return f"roken - Absolute URL - Status {rc}"

    else:

        return "Not a valid URL!"

    return None


def validate_relative_url(url, document=None):
    """
    Given a relative URL, check to see if it is valid They should be of
    the form:

    - ../../documents/help.md
    - ../assets/excel.csv

    # Parameters

    url:str
        - the url to test

    document:pathlib.Path
        - The path to the document containing the URL.

    # Return

    None if there are no problems otherwise a string indicating what the
    problem is.
    """

    relative_url_rule = RelativeMarkdownURLRule()

    if relative_url_rule.match(url):

        results = relative_url_rule.extract_data(url)

        if results["md"] is None and results["section"] is None:

            return "Empty - Relative Link"

        elif results["md"]:
            file = document.parent.joinpath(results["md"]).resolve()

            if not file.exists():

                return "Broken - Relative Link"

    else:

        return "Not Relative URL"

    return None


def validate_image_url(url, document=None, **kwargs):
    """

    Takes a line form the markdown file and examines it for markdown links. If
    there are markdown links, they are analyzed to ensure they are not broken.

    # Parameters

    url:str
        - the url to test

    document:pathlib.Path
        - The path to the document containing the URL.

    # Return

    None if there are no problems otherwise a string indicating what the
    problem is.

    """

    absolute_url_rule = AbsoluteURLRule()

    if absolute_url_rule.match(url):

        log.debug(f"Requesting {url}")

        request = requests.head(url)
        rc = request.status_code

        log.debug(f"Return code - {rc} -> {url}")

        if rc >= 400:

            return f"Broken - Absolute Image URL - Status {rc}"

    else:

        file = document.parent.joinpath(url).resolve()

        if not file.exists():

            return "Broken - Relative Image Link"

    return None


def validate_markdown_links(
    md_file,
    line_number,
    line,
    **kwargs,
):
    """
    Takes a line form the markdown file and examines it for markdown links. If
    there are markdown links, they are analyzed to ensure they are not broken.

    # Parameters

    md_file:pathlib.Path
        - The path to the file to examine

    line_number:int
        - The current line number we are analyzing in the markdown file.

    line:str
        - The current line we are analyzing from the markdown file.

    # Parameters (kwargs)

    ignore_missing_md_section:bool
        - Ignore the warning that the relative link to the markdown file
        doesn't have a section specified. This is relevant when combining
        the markdown files into one file.
        - Default - False

     # Return

    A list of ValidationStatus named tuple objects containing the problems encountered.

    # Exceptions

    None

    # NOTE

    This method is not designed to be run as part of a processing routine to convert the
    markdown to a different document format. It is  meant to be run as part of a
    dedicated validation routine.

    """

    ignore_missing_md_section = (
        kwargs["ignore_missing_md_section"]
        if "ignore_missing_md_section" in kwargs
        else False
    )

    md_link_rule = MarkdownLinkRule()
    absolute_url_rule = AbsoluteURLRule()
    relative_url_rule = RelativeMarkdownURLRule()

    problems = []

    # Contains a valid markdown link?
    if md_link_rule.match(line.strip()):

        results = md_link_rule.extract_data(line.strip())

        # can be multiple links in the line...
        for r in results:

            url = r["url"]

            # Is absolute url?
            if absolute_url_rule.match(url):

                # https://stackoverflow.com/questions/16778435/python-check-if-website-exists
                # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

                log.debug(f"Requesting {url}")

                request = requests.head(url)
                rc = request.status_code

                log.debug(f"Return code - {rc}")

                if rc >= 400:

                    vd = ValidationStatus(
                        md_file, "Broken - Absolute Link", line_number, r
                    )
                    problems.append(vd)

            # Is relative URL?
            elif relative_url_rule.match(url):

                results = relative_url_rule.extract_data(url)

                if results["md"] is None and results["section"] is None:

                    vd = ValidationStatus(
                        md_file, "Empty - Relative Link", line_number, r
                    )
                    problems.append(vd)

                elif results["md"]:
                    document = md_file.parent.joinpath(results["md"]).resolve()

                    if not document.exists():

                        vd = ValidationStatus(
                            md_file, "Broken - Relative Link", line_number, r
                        )
                        problems.append(vd)

                if not ignore_missing_md_section:
                    if results["section"] is None and results["md"].lower().endswith(
                        ".md"
                    ):

                        vd = ValidationStatus(
                            md_file, "Missing Section - Relative Link", line_number, r
                        )
                        problems.append(vd)

            else:

                vd = ValidationStatus(
                    md_file, "Warning - Unrecognized link", line_number, r
                )
                problems.append(vd)

    return problems


def validate_markdown_images(
    md_file,
    line_number,
    line,
    **kwargs,
):
    """

    Takes a line form the markdown file and examines it for markdown links. If
    there are markdown links, they are analyzed to ensure they are not broken.

    # Parameters

    md_file:pathlib.Path
        - The path to the file to examine

    line_number:int
        - The current line number we are analyzing in the markdown file.

    line:str
        - The current line we are analyzing from the markdown file.

    # Return

    A list of ValidationStatus named tuple objects containing the problems encountered.

    # Exceptions

    None

    # NOTE

    This method is not designed to be run as part of a processing routine to convert the
    markdown to a different document format. It is  meant to be run as part of a
    dedicated validation routine.

    """

    rule = MarkdownImageRule()
    absolute_url_rule = AbsoluteURLRule()

    problems = []

    # Contains a valid markdown link?
    if rule.match(line.strip()):

        results = rule.extract_data(line.strip())

        for r in results:

            if r["caption"] is None:
                vd = ValidationStatus(
                    md_file, "Warning - Image Missing Caption", line_number, r
                )
                problems.append(vd)

            if absolute_url_rule.match(r["url"]):
                url = r["url"]

                log.debug(f"Requesting {url}")

                request = requests.head(url)
                rc = request.status_code

                log.debug(f"Return code - {rc}")

                if rc >= 400:
                    vd = ValidationStatus(
                        md_file, "Broken - Absolute Image Link", line_number, r
                    )
                    problems.append(vd)

            else:

                im_path = md_file.parent.joinpath(r["url"]).resolve()

                if not im_path.exists():

                    vd = ValidationStatus(
                        md_file, "Broken - Relative Image Link", line_number, r
                    )
                    problems.append(vd)

    return problems


def validate_markdown(md_file, contents, **kwargs):
    """

    Examines the markdown file line by line for various features. It will:

    - Look for markdown links and test to make sure the urls are valid
        - relative - file exists - If the link is a relative link, check to make sure the file exists.
        - absolute - requests - If the link is an absolute url, then use requests to see if the link is valid
    - Look for markdown image links and test to make sure the images are valid
        - relative - file exists
        - absolute - requests

    It will print a message to stdout indicating the problem it found.

    # Parameters

    md_file:Path
        - The path to the md_file we are examining

    contents:list(str)
        - The list of strings representing the contents of the markdown file

    # Parameters (kwargs)

    ignore_missing_md_section:bool
        - Ignore the warning that the relative link to the markdown file
        doesn't have a section specified. This is relevant when combining
        the markdown files into one file.
        - Default - False

    # Return

    A list of ValidationStatus named tuple objects containing the problems encountered.The count of the number of problems.

    # Exceptions

    None

    # NOTE

    This method is not designed to be run as part of a processing routine to convert the
    markdown to a different document format. It is  meant to be run as part of a
    dedicated validation routine.

    """

    # NOTE: Should have a check for YAML blocks here. See Pandoc.extract_yaml

    code_fence_rule = CodeFenceClassifier()
    in_code_fence = False

    problems = []

    for line_number, line in enumerate(contents, 1):

        # need to put in the check for a code fence
        if code_fence_rule.match(line):
            in_code_fence = not in_code_fence

        if in_code_fence:
            continue

        problems.extend(validate_markdown_links(md_file, line_number, line, **kwargs))
        problems.extend(validate_markdown_images(md_file, line_number, line, **kwargs))

    return problems


def validate(file, **kwargs):
    """

    Take the .lst file and validate all of the markdown files it contains.

    # Parameters

    file:pathlib.Path
        - The .lst file used to describe the documents that we want to validate

    # Return

    None

    """

    files = read_lst(file)

    for md in files:

        log.debug(f"Validating {md.name}...")

        if md.exists():

            with md.open("r", encoding="utf-8") as f:

                lines = f.readlines()

                defects = validate_markdown(md, lines, **kwargs)

                if defects:
                    for vd in defects:
                        log.info(
                            "{} Line: {} - {} -> {}".format(
                                vd.file.name, vd.line, vd.error, vd.message
                            )
                        )

                    log.info("")
        else:

            log.info(f"The file {md} does not exist in {file}!")

    log.info("")
    log.info(f"Files Processed: {len(files)}")

    if defects:
        log.info(f"Problems Detected: {len(defects)}")
