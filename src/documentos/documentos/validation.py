#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid:   91995646-2f49-11eb-8e0d-60f262a5770a
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date :  2020-11-25
# -----------

"""
This module contains common validation routines.
"""

# ------------
# System Modules - Included with Python

from collections import namedtuple


# ------------
# 3rd Party - From pip

import requests
import urllib3.exceptions

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from .markdown_classifiers import (
    AbsoluteURLRule,
    RelativeMarkdownURLRule,
)

# -------------


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
    Given an absolute URL, check to see if it is valid and reachable.
    They should be of the form:

    - https://stackoverflow.com/questions/16778435/python-check-if-website-exists
    - https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

    # Parameters

    url:str
        - the url to test

    # Return

    if there are problems with the URL, a string indicating the problem
    is returned. Otherwise, None is returned

    """

    absolute_url_rule = AbsoluteURLRule()

    # Is URL Absolute?
    if absolute_url_rule.match(url):
        console.print(f"Requesting {url}")

        try:

            request = requests.head(url, allow_redirects=True)

        except (urllib3.exceptions.MaxRetryError,requests.exceptions.ConnectionError) as ex:

            return "Not a valid absolute URL (max retries exceed)!"

        else:

            console.print(f"Return code - {request.status_code} -> {url}")

            sc = request.status_code

            if 200 <= sc < 300:

                return None

            elif 300 <= sc < 400:

                return f"Redirect - Absolute URL - Status {sc}"

            elif sc >= 400:

                return f"Broken - Absolute URL - Status {sc}"

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

    If there is a problem, a string indicating the problem is returned.
    Otherwise, None is returned.
    """

    relative_url_rule = RelativeMarkdownURLRule()

    if relative_url_rule.match(url):

        results = relative_url_rule.extract_data(url)

        if results["md"] is None and results["section"] is None:
            return "Empty - Relative Link"

        elif results["md"]:
            file = document.parent.joinpath(results["md"]).resolve()

            if not file.exists():
                return "Broken - Relative Link!"

    else:
        return "Not a valid relative URL!"

    return None


def validate_image_url(url, document=None, **kwargs):
    """

    Takes a URL and checks to see if is is a valid absolute URL or
    relative URL.

    # Parameters

    url:str
        - the url to test

    document:pathlib.Path
        - The path to the document containing the URL.

    # Return

    If there is a problem a string describing the problem is returned.
    Otherwise None is returned.

    """

    absolute_url_rule = AbsoluteURLRule()

    if absolute_url_rule.match(url):

        console.print(f"Requesting {url}")

        request = requests.head(url)
        rc = request.status_code

        console.print(f"Return code - {rc} -> {url}")

        if rc >= 400:

            return f"Broken - Absolute Image URL - Status {rc}!"

    else:

        file = document.parent.joinpath(url).resolve()

        if not file.exists():

            return "Broken - Relative Image Link!"

    return None
