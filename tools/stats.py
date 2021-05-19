#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 1614098e-b8ca-11eb-96c0-41de2ca30456
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-19
# -----------

"""
"""

# ------------
# System Modules - Included with Python

import sys
import logging

from pathlib import Path
from datetime import datetime

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules

from md_docs.common import run_cmd

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------

# This is the pandoc filter will will write out to a temporary location

lua_filter = {
    'name':'wordcount.lua',
    'contents': [
        "-- counts words in a document",
        "",
        "words = 0",
        "",
        "wordcount = {",
        "  Str = function(el)",
        "    -- we don't count a word if it's entirely punctuation:",
        '    if el.text:match("%P") then',
        "        words = words + 1",
        "    end",
        "  end,",
        "",
        "  Code = function(el)",
        '    _,n = el.text:gsub("%S+","")',
        "    words = words + n",
        "  end,",
        "",
        "  CodeBlock = function(el)",
        '    _,n = el.text:gsub("%S+","")',
        "    words = words + n",
        "  end",
        "}",
        "",
        "function Pandoc(el)",
        "    -- skip metadata, just count body:",
        "    pandoc.walk_block(pandoc.Div(el.blocks), wordcount)",
        '    print(words .. " words in body")',
        "    os.exit(0)",
        "end",
    ]
}

def construct_pandoc_command(
    input_file=None,
    lua_filter=None,
):
    """
    Construct the Pandoc command.

    # Parameters

    input_file:pathlib.Path
        - The file that we want to apply the lua filter too.

    lua_filter:pathlib.Path
        - The path to the lua filter to use for the word counts.

    # Return

    A list of CLI elements that will be used by subprocess.
    """

    # --------
    # Basic Commands

    pandoc = [
        "pandoc",
        "--lua-filter",
        lua_filter,
        input_file,
    ]

    return pandoc

@click.command("stats")
@click.argument('search', type=click.Path(exists=True))
@click.pass_context
def stats(*args, **kwargs):
    """

    Given the `search` path, recursively find all the Markdown files and
    perform a word count return the stats.

    ```
    Started  - 2021-05-19 13:57:30.698969
    Finished - 2021-05-19 13:57:49.755689
    Elapsed:   0:00:19.056720

    Total Documents:      735
    Total Words:      182,584
    Estimated Pages:    365.2
    ```

    # Usage

    $ docs stats ./en/documents

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    # construct the lua script

    config['cache_folder'].mkdir(parents=True, exist_ok=True)

    lua_script = config['cache_folder'].joinpath(lua_filter['name'])

    lua_script.write_text("\n".join(lua_filter['contents']))

    build_start_time = datetime.now()

    word_counts = []

    for f in Path(kwargs['search']).rglob("*.md"):

        pandoc = construct_pandoc_command(
            input_file=f,
            lua_filter=lua_script,
        )

        stdout = run_cmd(pandoc)

        if len(stdout) == 1:

            # The string will be of the form 'xxx words in body'.
            # We need to strip the text and process the count
            count = int(stdout[0].replace(" words in body", ""))
            word_counts.append(count)

            log.info(f"Counted {f.name} -> {count} words...")

        else:
            # something is wrong
            raise ValueError(
                f"Unexpected Return from Pandoc. Expected 1 line, got {len(stdout)}..."
            )

    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")

    log.info("")

    total_words = sum(word_counts)
    words_per_page = total_words / 500  # https://howardcc.libanswers.com/faq/69833

    log.info(f"Total Documents: {len(word_counts):>8,}")
    log.info(f"Total Words:     {total_words:>8,}")
    log.info(f"Estimated Pages: {words_per_page:>8,.1f}")
