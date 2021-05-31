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

from md_docs.document import search

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


def missing_yaml_filter(md):
    """
    Simple multiprocessing wrapper

    Basically does a simple test to see if the md file is missing the
    markdown block.

    NOTE: This might seem redundant, but the MarkdownDocument object
    does lazy loading. That is, it will only load the contents of the
    Markdown document and process the items within it when it needs
    too.

    """

    if not md.yaml_block:
        log.info(f"MISSING YAML BLOCK - {md.filename}")

        return md


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

    log.info("Searching for markdown files missing YAML blocks...")
    log.info("")

    # -----------
    # Multi-Processing

    with Pool(processes=None) as p:
        md_files = p.map(
            missing_yaml_filter,
            search(root=config["documents.path"]),
        )

    # --------------
    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Files Examined:      {len(md_files)}")
    log.info(f"Missing YAML Blocks: {len([f for f in md_files if f is not None])}")
    log.info("-----")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")
