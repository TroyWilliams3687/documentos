#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : c5dd9cda-b4ed-11eb-833e-df61029d6284
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-14
# -----------

"""
The build process transforming the Markdown files to PDF.
"""

# ------------
# System Modules - Included with Python

import tempfile
import logging

from zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

# ------------
# 3rd Party Modules

import click

# ------------
# Custom Modules

from ..md_docs.common import (
    run_cmd,
    path_to_root,
)

from ..md_docs.document import (
    MarkdownDocument,
    LSTDocument,
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
    # contains the majority of settings needed by PANDOC for the
    # transformation.

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
        f'--variable=build_date:{datetime.now().replace(tzinfo=ZoneInfo(config["default_timezone"])).strftime("%Y-%m-%dT%H%M%z")}'
    )

    # NOTE: variables can be added to the main YAML configuration file
    # stored in the templates. They won't be as flexible as adding them
    # here, but could prove useful in some circumstances.

    # --------
    # Add Metadata

    # NOTE: Metadata can be added to the main YAML configuration file
    # stored in the templates

    if "title" in kwargs:
        pandoc.extend(
            ("--metadata", f"title={kwargs['title']}")
        )  # use the name of the file as the title of the document

    if "keywords" in kwargs:
        pandoc.extend(("--metadata", f'keywords={kwargs["keywords"]}'))

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
    \b
    Build PDF from the supplied markdown files.

    # Usage

    $ build \
        --config=en/config.common.yaml \
        --config=en/config.pdf.yaml \
        pdf

    $ build \
        --config=en/config.common.yaml \
        --config=en/config.pdf.yaml \
        pdf --latex

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now().replace(
        tzinfo=ZoneInfo(config["default_timezone"])
    )

    config["documents.path"] = config["root"].joinpath(config["documents"]["path"])

    log.info(f'Extracting files from {config["documents"]["lst"]}...')

    lst = LSTDocument(
        config["documents.path"].joinpath(config["documents"]["lst"]).resolve()
    )

    # Gather all Markdown files from the LST and de-duplicate the list
    lst_contents = list({[MarkdownDocument(f) for f in lst.links]})

    # ----------
    # Adjust .MD Links

    # Adjust the markdown links by changing any intra-document links
    # from *.md to *.html. We do this because Pandoc will not alter
    # links.

    # NOTE: We are not applying any checks or validation at this point.
    # You need to run validation methods for this.

    log.info("Adjusting markdown links...")
    for md in lst_contents:

        # remove duplicate line numbers as string replace will deal with
        # them
        for line in {item[0] for item in md.relative_links()}:
            md.contents[line] = md.contents[line].replace(".md", ".html")

    # ----------
    # Merge

    # we will end up with md_files containing one item and the config
    # ["md_file_contents"] only having one entry. We do this so nothing
    # downstream in this method changes...

    single_md = MarkdownDocument(
        config["documents.path"].joinpath("single.md").resolve(),
    )

    single_md.contents = []

    for md in lst_contents:
        single_md.contents.extend(md.contents)

    # ----------
    # Copy Files to TMP

    with tempfile.TemporaryDirectory(dir=config["root"]) as tmp:

        tmp_path = Path(tmp)

        relative_path = single_md.filename.relative_to(config["documents.path"])

        tmp_md = tmp_path.joinpath(relative_path)
        tmp_md.parent.mkdir(parents=True, exist_ok=True)

        log.debug(f"Writing {tmp_md.name}...")

        with tmp_md.open("w", encoding="utf-8") as fo:

            for line in single_md.contents:
                fo.write(line)

        # ----------
        # Transform Markdown to PDF

        # Add PANDOC transformation jobs to the queue.

        config["output.path"] = config["root"].joinpath(config["output"])

        of = (
            config["output.path"]
            .joinpath(relative_path.parent)
            .joinpath(f"{relative_path.stem}.pdf")
        )

        if kwargs["latex"]:
            of = (
                config["output.path"]
                .joinpath(relative_path.parent)
                .joinpath(f"{relative_path.stem}.tex")
            )

        of.parent.mkdir(parents=True, exist_ok=True)

        msg = f"Pandoc - Transform {single_md.filename} to {of.relative_to(config['output.path'])}"

        pandoc = construct_pandoc_command(
            input_file=tmp_path.joinpath(relative_path),
            output_file=of,
            config=config,
            title=single_md.filename.name,
            **kwargs,
        )

        log.info(msg)

        run_cmd(pandoc)

        log.info("Transformation to PDF complete...")

    build_end_time = datetime.now().replace(tzinfo=ZoneInfo(config["default_timezone"]))

    log.info("")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")
