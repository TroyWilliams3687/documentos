#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 8077014c-b978-11eb-aa40-875c86851247
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-20
# -----------

"""
"""
# ------------
# System Modules - Included with Python

import sys
import logging

from pathlib import Path
from datetime import datetime
from multiprocessing import Pool
from functools import partial

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules

from md_docs.common import create_lst_reverse_link_lookup
from md_docs.validation import validate_markdown
from md_docs.markdown import create_file_cache

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

    caches = create_file_cache(root=config["documents.path"])

    config["lst_file_contents"] = caches[".lst"]
    config["md_file_contents"] = caches[".md"]

    log.info(f'{len(config["md_file_contents"])} markdown files were found...')
    log.info(f'{len(config["lst_file_contents"])} LST files were found...')
    log.info("")

    args[0].obj["cfg"] = config


def multiprocessing_wrapper(root, k, contents):
    """
    Simple wrapper to make multiprocessing easier.

    Returns a tuple containing the file name/key and the defects or
    it returns None.

    NOTE: This methods arguments are defined this way to make use of
    functools.partial

    """

    defects = validate_markdown(
        root.joinpath(k).resolve(),
        contents,
        ignore_missing_md_section=True,
    )

    if defects:

        return (k, defects)

    else:

        return None


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
        total_defects = p.starmap(fp, config["md_file_contents"].items())

    # Remove empty items
    total_defects = [d for d in total_defects if d is not None]

    for item in total_defects:

        k, defects = item

        log.info("")
        log.info("--------")
        log.info(f"Defects found in {k}:")

        for vd in defects:
            log.info("\tLine: {} - {} -> {}".format(vd.line, vd.error, vd.message))

    # --------------

    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")

    log.info("")
    log.info("--------")
    log.info(f"Files with defects: {len(total_defects)}")


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

    log.info("Constructing reverse LST lookup dictionary...")
    reverse_lst_links = create_lst_reverse_link_lookup(
        config["lst_file_contents"], config["documents.path"]
    )

    for url, lst_files in reverse_lst_links.items():

        p = config["documents.path"].joinpath(url).resolve()

        if not p.exists():
            log.info(f"{url} does not exist in: {lst_files}")

    # ------
    # Display any files that are not included in any of the lst files

    lst_files = set([str(k) for k in reverse_lst_links if k.suffix != ".lst"])
    md_files = set(config["md_file_contents"])

    log.info("Check - Are all markdown files accounted for in the LST files....")

    log.info(f"MD Files (lst): {len(lst_files)}")
    log.info(f"MD files (file system): {len(md_files)}")

    # Subtracting the sets will give use the difference, that is what files are
    # not listed in the LST file. We have to check both was because of the way the set
    # differences work. a - b will list all the elements in a that are not in b.

    if lst_files >= md_files:

        delta = lst_files - md_files

    else:

        delta = md_files - lst_files

    if delta:

        log.info("")
        log.info("Files that are in the LST but not in the set of MD files:")

        for d in delta:
            log.info(f"\t{d}")

        log.info(f"Count: {len(delta)}")
