#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : 82933fe2-ba34-11eb-b71c-5daaafeb5856
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-21
# -----------

"""
The `yaml` command examines all of the Markdown files in the system and
reports on the ones missing YAML metadata blocks.
"""

# ------------
# System Modules - Included with Python

import logging

from datetime import datetime
from multiprocessing import Pool

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules

from ..md_docs.document import search

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


def yaml_check(md):
    """
    Perform bask checks on the YAML metadata block return a data
    structure indicating the problem, if any.

    # Return

    A dictionary
    - block:bool - A boolean indicating if the YAML block is present
        - True if the block is present, False if it is not
    - UUID:bool - A boolean indicating that the YAML block has a UUID keyword
        - True if the UUID keyword exists and the contents has a length greater than 0, False otherwise.
    - md:MarkdownDocument - The MarkdownDocument object

    # NOTE

    This might seem redundant, but the MarkdownDocument object does lazy
    loading. That is, it will only load the contents of the Markdown
    document and process the items within it when it needs too.

    """

    results = {}

    results["block"] = True if md.yaml_block else False
    results["UUID"] = (
        True if "UUID" in md.yaml_block and len(md.yaml_block["UUID"]) > 0 else False
    )
    results["md"] = md

    return results


@click.command("yaml")
@click.pass_context
def yaml_blocks(*args, **kwargs):
    """

    Examine all of the Markdown files for YAML blocks. List the files
    that do not have YAML blocks defined.

    # Usage

    $ docs --config=./en/config.common.yaml yaml

    """

    config = args[0].obj["cfg"]

    build_start_time = datetime.now()

    log.info("")
    log.info("Searching for Markdown with YAML Block Problems...")
    log.info("")

    # -----------
    # Multi-Processing

    with Pool(processes=None) as p:
        checks = p.map(
            yaml_check,
            search(root=config["documents.path"]),
        )

    missing_yaml_blocks = [check["md"] for check in checks if not check["block"]]
    missing_uuid = [
        check["md"] for check in checks if check["block"] and not check["UUID"]
    ]

    if missing_yaml_blocks:

        for md in missing_yaml_blocks:
            log.info(f"MISSING YAML BLOCK - {md.filename}")

        log.info("")

    if missing_uuid:

        for md in missing_uuid:
            log.info(f"MISSING YAML UUID - {md.filename}")

    # --------------
    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Files Examined:      {len(checks):>4}")
    log.info(f"Missing YAML Blocks: {len(missing_yaml_blocks):>4}")
    log.info(f"Missing YAML UUID:   {len(missing_uuid):>4}")
    log.info("-----")
    log.info(f"Started:   {build_start_time}")
    log.info(f"Finished:  {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")
