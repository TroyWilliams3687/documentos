#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   5a047f1c-bb0d-11eb-8e16-a1c71b5bec55
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-05-22
# -----------

"""
Validation methods specifically for documents.
"""

# ------------
# System Modules - Included with Python

# ------------
# Custom Modules

from .validation import (
    validate_absolute_url,
    validate_relative_url,
    validate_image_url,
)


def validate_urls(document, root=None):
    """

    Validate the urls that are contained within the markdown file.
    Returns a list of issues.

    # Parameters

    document:MDDocument
        - the document we want to validate

    root:pathlib.Path
        - Optional root folder so that we can display a shorter path
          name for the document.

    # Return

    A list of strings containing the issues and line numbers. If there
    are no issues, the list will be empty.

    """

    path = document.filename

    if root:
        path = path.relative_to(root)

    messages = []

    for aurl in document.absolute_links():
        line, url = aurl

        msg = validate_absolute_url(url["url"])

        if msg:
            messages.append(f'{msg} - {path} - line {line} - `{url["full"]}`')

    for rurl in document.relative_links():
        line, url = rurl

        msg = validate_relative_url(url["url"], document=document.filename)

        if msg:
            messages.append(f'{msg} - {path} - line {line} - `{url["full"]}`')

    return messages


def validate_images(document, root=None):
    """

    Validate the image URLs that are contained within the markdown file.
    Returns a list of issues.

    # Parameters

    document:MDDocument
        - the document we want to validate

    root:pathlib.Path
        - Root folder so that we can display a shorter path name for the
          document.
        - Default - None - Optional

    # Return

    A list of strings containing the issues and line numbers. If there
    are no issues, the list will be empty.

    """

    path = document.filename

    if root:
        path = path.relative_to(root)

    messages = []

    for image_url in document.image_links():
        line, url = image_url

        msg = validate_image_url(url["url"], document=document.filename)

        if msg:
            messages.append(f'{msg} - {path} - line {line}- `{url["full"]}`.')

    return messages
