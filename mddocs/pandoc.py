#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = a6ad2d22-4a02-11eb-8faf-030b971fcc99
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-12-29
# -----------

"""
This module contains code specific to pandoc markdown.
"""


# ------------
# 3rd Party Modules

import yaml

# ------------


def extract_yaml(md_lines=None, **kwargs):
    """
    Given the [pandoc](https://pandoc.org) formatted markdown file extract
    the YAML block(s), if any.

    The YAML block starts with 3 dashes (---) and ends with 3 dashes or
    3 dots (...). The block markers should be the only things on a line (other
    than leading or trailing spaces perhaps).

    A YAML block may occur anywhere within the document. If the YAML block is
    not at the begging of the file it must be proceeded by an blank line.

    A document may contain multiple YAML blocks. If two blocks attempt to
    set the same field, the field from the second block will be used.

    # Parameters
    md_lines:list(str)
        - A list containing all of the lines in the markdown document.

    # Parameters (kwargs)

    include_block_locations:bool
        - Return a list of tuples indicating the starting and ending
        lines of the YAML blocks

    # Return

    A list of YAML blocks in the order they were discovered. Each block is
    simply a list of strings contained within the block markers.

    # Reference

    - https://pandoc.org/MANUAL.html#extension-yaml_metadata_block

    """

    include_block_locations = (
        kwargs["include_block_locations"]
        if "include_block_locations" in kwargs
        else False
    )

    block_locations = []
    block_start_index = -1

    in_block = False
    start_block = "---"
    end_block = ["---", "..."]

    blocks = []  # store all the blocks discovered in the markdown file
    current_block = None

    for i, line in enumerate(md_lines):

        if in_block:

            if line.strip() in end_block:
                in_block = False
                block_locations.append((block_start_index, i))
                continue

            current_block.append(line)

        else:

            if line.strip() == start_block:
                in_block = True
                current_block = []
                blocks.append(current_block)
                block_start_index = i
                continue

    # merge all the YAML blocks into one dictionary. NOTE: the values in the last block,
    # if duplicated in other blocks will overwrite previous values

    yaml_block = {}

    for b in blocks:
        yaml_block.update(yaml.safe_load("".join(b)))

    if include_block_locations:

        return yaml_block, block_locations

    else:

        return yaml_block
