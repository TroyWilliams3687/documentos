#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 82933fe2-ba34-11eb-b71c-5daaafeb5856
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-05-21
-----------
"""

# ------------
# System Modules - Included with Python

import logging

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules

# from md_docs.markdown import create_file_cache
# from md_docs.pandoc import extract_yaml

from md_docs.document import search

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


def find_missing_yaml_blocks(md_file_contents, verbose=False):
    """

    # Parameters

    md_file_contents:dict
        - The dictionary is keyed by file and contains a list of strings representing
        the contents of the file.

    # Return

    A list of files (keys) that do not contain a YAML block

    """

    missing_blocks = []

    for k, contents in md_file_contents.items():

        if verbose:
            log.info(f"Searching {k}...")

        yaml_block = extract_yaml(md_lines=contents)

        if not yaml_block:

            if verbose:
                log.info(f"No YAML block detected in {k}...")

            missing_blocks.append(k)

    return missing_blocks


@click.group("yaml")
@click.pass_context
def yaml_blocks(*args, **kwargs):
    """

    # Usage


    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for markdown files...")

    md_files = search(root=config["documents.path"])

    config["md_file_contents"] = md_files

    args[0].obj["cfg"] = config

    log.info(f'{len(config["md_file_contents"])} markdown files were found...')
    log.info("")


# @validate.command("markdown")
# @click.pass_context
# def markdown(*args, **kwargs):
#     """

#     # Usage

#     $ docs --config=./en/config.common.yaml validate markdown

#     """

#     # Extract the configuration file from the click context
#     config = args[0].obj["cfg"]


# @validate.command("lst")
# @click.pass_context
# def lst(*args, **kwargs):
#     """

#     # Usage

#     $ docs --config=./en/config.common.yaml validate lst

#     """

#     # Extract the configuration file from the click context
#     config = args[0].obj["cfg"]
