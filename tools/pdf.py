#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = c5dd9cda-b4ed-11eb-833e-df61029d6284
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-14
# -----------

"""
This module handles the conversion of the markdown files to PDF.
"""

# ------------
# System Modules - Included with Python

import sys
import shutil
import tempfile
import logging

from zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

from multiprocessing import Pool

# ------------
# 3rd Party Modules

import click

# ------------
# Custom Modules

from md_docs.common import (
    run_cmd,
    path_to_root,
    create_md_link_lookup,
    create_lst_link_lookup,
    find_lst_links,
)

from md_docs.markdown import (
    create_file_cache,
    create_table_of_contents,
    adjust_markdown_contents,
)

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


def construct_pandoc_command(
    input_file=None,
    output_file=None,
    config=None,
    **kwargs,
):
    """
    Construct the required switches to run PANDOC.

    # Parameters

    config:dict
    - A dictionary containing the key paths of the system.

    # Return

    A list of CLI elements that will be used by subprocess.

    """

    # --------
    # Basic Commands

    pandoc = [
        "pandoc",
    ]

    # ---------
    # Relative Offset Calculation

    relative_offset = path_to_root(config["output.path"], output_file)

    # --------
    # Add YAML Data

    # Add the file containing the YAML data, defaults, metadata, etc. It
    # contains the majority of settings needed by pandoc for the transformation.

    config["templates.path"] = config["root"].joinpath(config["templates"]["path"])

    for p in config["templates"]["pandoc_config"]:

        pandoc.extend(
            (
                "--defaults",
                str(config["templates.path"].joinpath(p).resolve()),
            )
        )

    # ----------
    # Variables

    pandoc.append(f"--variable=RELATIVE:{str(relative_offset)}")
    pandoc.append(
        f'--variable=build_date:{datetime.now().replace(tzinfo=ZoneInfo(config["default.tz"])).strftime("%Y-%m-%dT%H%M%z")}'
    )

    # NOTE: variables can be added to the main YAML configuration file stored in the templates. They
    # won't be as flexible as adding them here, but could prove useful in some circumstances.

    # --------
    # Add Metadata

    # NOTE: Metadata can be added to the main YAML configuration file stored in the templates

    if "title" in kwargs:
        pandoc.extend(
            ("--metadata", f"title={kwargs['title']}")
        )  # use the name of the file as the title of the document

    if "keywords" in kwargs:
        pandoc.extend(("--metadata", f'keywords={kwargs["keywords"]}'))

    # --------
    # Add Syntax Highlighting

    # NOTE: This is taken care of by the YAML configuration files stored in the templates folder.

    # if config['syntax-highlight.themes']:
    #     pandoc.append(f"--highlight-style={str(config['syntax-highlight.themes']['breezedark.theme'])}")

    # --------
    # Add Transformation Options

    if "latex" in kwargs and kwargs["latex"]:

        pandoc.extend(("--to", "latex"))

    else:

        pandoc.extend(("--to", "pdf"))
        pandoc.append(
            "--pdf-engine=xelatex"
        )  # use xelatex to support Unicode characters in markdown.

    pandoc.extend(("-o", output_file))  # Output file path
    pandoc.append(input_file)  # Input File path

    return pandoc


@click.command("pdf")
@click.option(
    "--latex", is_flag=True, help="Generate a latex output suitable for debugging."
)
@click.pass_context
def pdf(*args, **kwargs):
    """

    Build PDF from the supplied markdown files.

    # Usage

    $ build ./english/config.pdf.yaml pdf

    $ build ./english/config.pdf.yaml pdf --latex

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now().replace(tzinfo=ZoneInfo(config["default.tz"]))

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for markdown and LST files...")

    config["documents.path"] = config["root"].joinpath(config["documents"]["path"])

    caches = create_file_cache(root=config["documents.path"])

    config["lst_file_contents"] = caches[".lst"]
    config["md_file_contents"] = caches[".md"]

    # extract the relative links from the file contents

    log.info("Extracting relative links...")

    config["md_links"] = create_md_link_lookup(
        config["md_file_contents"], config["documents.path"]
    )
    config["lst_links"] = create_lst_link_lookup(
        config["lst_file_contents"], config["documents.path"]
    )

    # look at the lst file contents and resolve all lst files it contains recursively
    md_files = [
        l.link for l in find_lst_links(config["documents"]["lst"], config["lst_links"])
    ]

    # ----------
    # Adjust .md Links

    # Adjust the markdown links by changing any intra-document links from *.md to *.html.
    # We do this because Pandoc will not alter links.

    log.info(f"Adjusting markdown links...")
    for md in md_files:

        mds = str(md)

        if mds in config["md_file_contents"]:

            adjusted_contents = adjust_markdown_contents(
                md_file=md,
                contents=config["md_file_contents"][mds],
            )

            config["md_file_contents"][mds] = adjusted_contents

    # ----------
    # Merge

    single_md = Path("single.md")
    single_contents = []

    for md in md_files:

        mds = str(md)

        if mds in config["md_file_contents"]:
            single_contents.extend(config["md_file_contents"][mds])

    # ----------
    # Copy Files to tmp

    with tempfile.TemporaryDirectory(dir=config["root"]) as tmp:

        config["tmp"] = Path(tmp)

        tmp_md = config["tmp"].joinpath(single_md)
        tmp_md.parent.mkdir(parents=True, exist_ok=True)

        log.debug(f"Writing {tmp_md.name}...")

        with tmp_md.open("w", encoding="utf-8") as fo:
            for line in single_contents:
                fo.write(line)

        # ----------
        # Transform Markdown to PDF

        # Add PANDOC transformation jobs to the queue.

        config["output.path"] = config["root"].joinpath(config["output"])

        of = (
            config["output.path"]
            .joinpath(single_md.parent)
            .joinpath(f"{single_md.stem}.pdf")
        )

        if kwargs["latex"]:
            of = (
                config["output.path"]
                .joinpath(single_md.parent)
                .joinpath(f"{single_md.stem}.tex")
            )

        of.parent.mkdir(parents=True, exist_ok=True)

        msg = (
            f"Pandoc - Transform {single_md} to {of.relative_to(config['output.path'])}"
        )

        pandoc = construct_pandoc_command(
            input_file=config["tmp"].joinpath(single_md),
            output_file=of,
            config=config,
            title=single_md,
            # keywords="",
            **kwargs,
        )

        log.info(msg)

        run_cmd(pandoc)

        log.info("Transformation to PDF complete...")

    build_end_time = datetime.now().replace(tzinfo=ZoneInfo(config["default.tz"]))

    log.info("")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")
