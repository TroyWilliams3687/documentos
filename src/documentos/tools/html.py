#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : 0b854b5e-b4bf-11eb-833e-df61029d6284
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-14
# -----------

"""
The build process transforming the Markdown files to HTML.
"""

# ------------
# System Modules - Included with Python

import shutil
import tempfile

from zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

from multiprocessing import Pool

# ------------
# 3rd Party - From pip

import click

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from ..documentos.common import (
    run_cmd,
    path_to_root,
)

from ..documentos.document import (
    MarkdownDocument,
    LSTDocument,
)

from .plugins import registered_pluggins

# -------------



def construct_pandoc_command(
    input_file=None,
    output_file=None,
    config=None,
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

    # NOTE: Can add other things here like software version numbers and
    # release dates. These could be added to the HTML footer template.

    # --------
    # Add CSS

    # The CSS files will be at the root of the folder. Adjust the
    # relative path to the correct location.

    if "css_files" in config["css"] and config["css"]["css_files"]:
        pandoc.extend(
            [
                f"--css={path_to_root(config['output.path'], output_file).joinpath(p)}"
                for p in config["css"]["css_files"]
            ]
        )

    for key, switch in [
        ("include_in_header", "--include-in-header"),
        ("include_before_body", "--include-before-body"),
        ("include_after_body", "--include-after-body"),
    ]:
        if key in config["templates"] and config["templates"][key]:
            pandoc.extend(
                [
                    f"{switch}={str(config['templates.path'].joinpath(f))}"
                    for f in config["templates"][key]
                ]
            )

    # --------
    # HTML Template Option

    # https://pandoc.org/MANUAL.html#option--template

    if "html_template" in config["templates"]:
        pandoc.append(
            f"--template={str(config['templates.path'].joinpath(config['templates']['html_template']))}"
        )

    # --------
    # Add Transformation Options

    pandoc.extend(("-o", output_file))  # Output file path
    pandoc.append(input_file)  # Input File path

    return pandoc


def process_pandoc(job):
    """
    A simple method for the multiprocessing module to work with.
    """

    msg, cmd = job

    console.print(msg)

    run_cmd(cmd)


@click.command("html")
@click.option(
    "--single",
    is_flag=True,
    help="Generate a single HTML file by combining all the markdown files.",
)
@click.pass_context
def html(*args, **kwargs):
    """
    \b
    Build HTML from the supplied markdown files

    # Usage

    $ build \
        --config=en/config.common.yaml \
        --config=en/config.ignore.yaml \
        --config=en/config.html.yaml \
        html

    $ build \
        --config=en/config.common.yaml \
        --config=en/config.ignore.yaml \
        --config=en/config.html.yaml \
        html --single

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now().replace(
        tzinfo=ZoneInfo(config["default_timezone"])
    )

    config["documents.path"] = config["root"].joinpath(config["documents"]["path"])

    console.print(f'Extracting files from {config["documents"]["lst"]}...')

    lst = LSTDocument(
        config["documents.path"].joinpath(config["documents"]["lst"]).resolve()
    )

    # Gather all Markdown files from the LST and de-duplicate the list
    lst_contents = list(set([MarkdownDocument(f) for f in lst.links]))

    console.print(f"Found {len(lst_contents)} markdown files...")

    # ----------
    # Table of Contents (TOC) - Plugin

    # https://docs.python.org/3/library/stdtypes.html#dict.get
    tocs_items = config['documents'].get('tocs')

    if tocs_items:

        for item in tocs_items:

            idx = LSTDocument(config["documents.path"].joinpath(item["lst"]).resolve())

            # Which TOC creator?
            plugin = item["toc_plugin"] if "toc_plugin" in item else "TOC"
            console.print(f"Creating index for {idx.filename}. Using plugin: `{plugin}`.")

            if plugin in registered_pluggins["table of contents"]:
                toc_creator = registered_pluggins["table of contents"][plugin]

            else:
                log.warning(f"{plugin} does not exist as a plugin! Using default.")
                toc_creator = registered_pluggins["table of contents"]["TOC"]

            # Generate the TOC
            contents = toc_creator(
                lst=idx,
                depth=item["depth"] if "depth" in item else 6,
                ignore=config["ignore_toc"],
            )

            new_path = config["documents.path"].joinpath(item["index"]).resolve()

            # It is possible to have a markdown file already in the
            # system with the same name. This means we should append
            # the content to the existing file. It will automatically
            # add a space before appending the contents.

            does_file_exist = False
            for f in lst_contents:
                if f.filename == new_path:
                    f.contents.extend([''] + contents)
                    does_file_exist = True
                    break

            # NOTE: We could create some sort of lookup index if this
            # becomes slow, a dictionary?

            if not does_file_exist:
                # Create a new file

                new_md = MarkdownDocument(
                    config["documents.path"].joinpath(item["index"]).resolve(),
                )

                new_md.contents = contents
                lst_contents.insert(0, new_md)

    # ----------
    # Adjust .MD Links

    # Adjust the markdown links by changing any intra-document links
    # from *.md to *.html. We do this because Pandoc will not alter
    # links.

    # NOTE: We are not applying any checks or validation at this point.
    # You need to run validation methods for this.

    console.print("Adjusting markdown links...")
    for md in lst_contents:

        # remove duplicate line numbers as string replace will deal with
        # them
        for line in {item[0] for item in md.relative_links()}:
            md.contents[line] = md.contents[line].replace(".md", ".html")

    # ----------
    # Merge

    if "single" in kwargs and kwargs["single"]:

        # we will end up with md_files containing one item and the
        # config["md_file_contents"] only having one entry. We do this
        # so nothing downstream in this method changes...

        single_md = MarkdownDocument(
            config["documents.path"].joinpath("single.md").resolve(),
        )

        single_md.contents = []

        for md in lst_contents:
            single_md.contents.extend(md.contents)

        lst_contents = [single_md]

    # ----------
    # Copy Files to TMP

    with tempfile.TemporaryDirectory(dir=config["root"]) as tmp:

        tmp_path = Path(tmp)

        for md in lst_contents:

            relative_path = md.filename.relative_to(config["documents.path"])

            tmp_md = tmp_path.joinpath(relative_path)
            tmp_md.parent.mkdir(parents=True, exist_ok=True)


            with tmp_md.open("w", encoding="utf-8") as fo:

                for line in md.contents:
                    fo.write(line)

        # ----------
        # Transform Markdown to HTML

        config["output.path"] = config["root"].joinpath(config["output"])

        pandoc_cmds = []

        for md in lst_contents:

            relative_path = md.filename.relative_to(config["documents.path"])

            of = (
                config["output.path"]
                .joinpath(relative_path.parent)
                .joinpath(f"{relative_path.stem}.html")
            )
            of.parent.mkdir(parents=True, exist_ok=True)

            msg = f"Pandoc - Transform `{relative_path}` to `{of.relative_to(config['output.path'])}`"

            pandoc = construct_pandoc_command(
                input_file=tmp_path.joinpath(relative_path),
                output_file=of,
                config=config,
            )

            pandoc_cmds.append((msg, pandoc))

        # -----------
        # Multi-Processing

        # https://docs.python.org/3/library/multiprocessing.html

        # Use max cores - default
        with Pool(processes=None) as p:
            p.map(process_pandoc, pandoc_cmds)

        console.print("Transformation to HTML complete...")

    # -------
    # JSON Document

    json_plugin = config.get("json_document_plugin")

    if json_plugin:
        json_document_method = registered_pluggins["json document"].get(json_plugin)

        if json_document_method:
            console.print(f"Creating JSON document using plugin: `{json_plugin}`.")

            document = json_document_method(
                documents=lst_contents,
                root=config["documents.path"],
                ignore=config["ignore_toc"],
            )

            json_output = config["output.path"] / json_document_method.filename

            json_output.write_text(document)

    else:
        console.print(f"[red]{json_plugin} does not exist as a plugin! Skipping.[/red]")

    # -------------
    # Copy CSS

    # Copy the selected CSS files to the root of the output folder. All
    # files that require it should have a relative path set to find it
    # there.

    config["css.path"] = config["root"].joinpath(config["css"]["path"])

    for css in config["css"]["css_files"]:

        cssp = config["css.path"].joinpath(css)

        console.print(f"Copying {cssp.name}...")

        shutil.copy(cssp, config["output.path"].joinpath(cssp.name))

    # ----------
    # Copy Assets

    # Copy the assets folder recursively to the output folder
    # maintaining the relative structure.

    if "assets" in config["documents"] and config["documents"]["assets"]:

        config["assets.path"] = config["documents.path"].joinpath(
            config["documents"]["assets"]
        )

        console.print(f"Copying {config['assets.path']}...")

        shutil.copytree(
            config["assets.path"],
            config["output.path"].joinpath(config["assets.path"].name),
            dirs_exist_ok=True,
        )

    # -----
    # Navigation Map - Plugin

    nav_plugin = config.get("navigation_map_plugin")

    if nav_plugin:

        nav_method = registered_pluggins["navigation"].get(nav_plugin)

        if nav_method:
            console.print(f"Creating navigation map for {lst.filename}. Using plugin: `{nav_plugin}`.")

            nav_method(
                document_root=config["documents.path"],
                output=config["output.path"],
                documents=lst_contents,
                **kwargs,
            )

        else:
            console.print(f"[red]{nav_plugin} does not exist as a plugin! Skipping.[/red]")

    build_end_time = datetime.now().replace(tzinfo=ZoneInfo(config["default_timezone"]))

    console.print("")
    console.print(f"Started  - {build_start_time}")
    console.print(f"Finished - {build_end_time}")
    console.print(f"Elapsed:   {build_end_time - build_start_time}")
