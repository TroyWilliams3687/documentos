#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 8077014c-b978-11eb-aa40-875c86851247
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-05-20
-----------
"""

# ------------
# System Modules - Included with Python

import logging

from datetime import datetime
from multiprocessing import Pool
from functools import partial

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules


from md_docs.document import (
    LSTDocument,
    search,
)

from md_docs.document_validation import (
    validate_urls,
    validate_images,
)

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


@click.group("validate")
@click.pass_context
def validate(*args, **kwargs):
    """
    Perform validation checks for Markdown files and LST files.

    # Usage

    $ docs --config=./en/config.common.yaml validate markdown

    $ docs --config=./en/config.common.yaml validate lst

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for markdown and LST files...")

    config["md_file_contents"] = search(root=config["documents.path"])
    config["lst_file_contents"] = search(
        root=config["documents.path"],
        extension=".lst",
        document=LSTDocument,
    )

    log.info(f'{len(config["md_file_contents"])} Markdown files were found...')
    log.info(f'{len(config["lst_file_contents"])} LSR files were found...')
    log.info("")

    args[0].obj["cfg"] = config


def multiprocessing_wrapper(root, md):
    """
    Simple wrapper to make multiprocessing easier.

    Returns a tuple containing the file name/key and the defects or
    it returns None.

    NOTE: This methods arguments are defined this way to make use of
    functools.partial

    """

    url_messages = validate_urls(md, root=root)
    image_messages = validate_images(md, root=root)

    if url_messages or image_messages:

        p = md.filename.relative_to(root)
        log.info(f"Issues in `{p}`:")

        if url_messages:
            log.info("URL Issues")

            for msg in url_messages:
                log.info(msg)

        if image_messages:
            log.info("Image Issues")

            for msg in image_messages:
                log.info(msg)

        log.info("")
        log.info("-----")


@validate.command("markdown")
@click.pass_context
def markdown(*args, **kwargs):
    """

    # Usage

    $ docs --config=./en/config.common.yaml validate markdown

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now()

    # ------
    # Validate Markdown Files

    # - absolute URL check
    # - relative URL check
    # - image URL check

    log.info("Validating Markdown Files...")
    log.info("")

    # -----------
    # Multi-Processing

    # Pre-fill the bits that don't change during iteration so we can use
    # the multiprocessing pool effectively

    fp = partial(multiprocessing_wrapper, config["documents.path"])

    with Pool(processes=None) as p:
        p.map(fp, config["md_file_contents"])

    # --------------

    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")


@validate.command("lst")
@click.pass_context
def lst(*args, **kwargs):
    """

    # Usage

    $ docs --config=./en/config.common.yaml validate lst

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    # ------
    # Validate LST Files

    # check for duplicate entries

    log.info("Validating LST Files...")
    log.info("")

    for lst in config["lst_file_contents"]:

        key = lst.filename.relative_to(config["documents.path"])

        log.info(f"{key}")

        for f in lst.links:

            if not f.exists():
                log.info(f"{f} does not exist in: {key}")

    # ------
    # Display any files that are not included in any of the lst files

    lst_files = {str(f) for lst in config["lst_file_contents"] for f in lst.links}
    md_files = {str(f.filename) for f in config["md_file_contents"]}

    log.info("Check - Are all markdown files accounted for in the LST files....")

    log.info(f"MD Files (lst): {len(lst_files)}")
    log.info(f"MD files (file system): {len(md_files)}")

    # Subtracting the sets will give use the difference, that is what files are
    # not listed in the LST file. We have to check both was because of the way the set
    # differences work. a - b will list all the elements in a that are not in b.

    if lst_files >= md_files:

        delta = lst_files - md_files
        msg = "Files that are in the LST but not in the set of MD files:"

    else:

        delta = md_files - lst_files
        msg = "Files that are in the FILE SYSTEM but not in the set of LST files:"

    if delta:

        log.info("")
        log.info(msg)

        for d in delta:
            log.info(f"\t{d}")

        log.info("")
        log.info(f"Count: {len(delta)}")
