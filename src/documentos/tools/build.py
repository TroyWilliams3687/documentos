#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : fb7b0232-b4bc-11eb-833e-df61029d6284
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-14
# -----------

"""
This module is the main entry point into the build app. This will build
a series of documents by transforming markdown files stored in nested
folders into HTML or PDF using Pandoc and some light custom markup
files (LST).

See the `en` folder at the root for sample documents to transform and
instructions on the system usage.
"""

# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# 3rd Party

import click
import toml

from rich.traceback import install
install(show_locals=False)

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from ..documentos.common import find_folder_on_path

from .html import html
from .pdf import pdf

from .plugins import load_module

# -------------


def setup(cfg):
    """

    Load the configuration settings and and return a dictionary.
    Basically, this looks for the root of the repository (i.e. the .git
    folder). Every thing will be relative to that folder.

    # Parameters

    cfg:list(pathlib.Path)
        - A list of TOML configuration files that will be merged to
          drive the process.

    # Return

    A dictionary containing the configurations to use for the process.

    """

    repo_root = find_folder_on_path(Path.cwd().resolve())

    if repo_root is None:
        raise FileNotFoundError(
            "Could not find repo root! The root should contain `.git` folder."
        )

    try:

        config = toml.load(
            cfg
        )  # this will load all the files in the list automatically

    except toml.decoder.TomlDecodeError as e:
        # print("Error when parsing the TOML file!")
        # print(f"The error is on line {e.lineno} at column {e.colno}.")
        raise

    config["root"] = repo_root

    # Make sure we have ignore_toc as an empty set at a minimum.
    # Otherwise transform it to a set because there is no YAML for it

    if "ignore_toc" in config:

        config["ignore_toc"] = {
            config["root"] / config["documents"]["path"] / p
            for p in config["ignore_toc"]
        }

        # config["ignore_toc"] = set(config["ignore_toc"])

    else:

        config["ignore_toc"] = set()

    return config


@click.group()
@click.version_option(package_name="documentos")
@click.option(
    "--config",
    "-c",
    multiple=True,
    type=click.Path(exists=True),
    help="Pass in the configuration file to control the process. You can pass in multiple files by calling the switch multiple times. The order you pass the files in matters. Any duplicate values will be overwritten by the last file.",
)
@click.pass_context
def main(*args, **kwargs):
    """
    \b
    Transform the markdown files into another form suitable for
    publication.

    # Parameters

    build_cfg:str
        - The path to the TOML configuration file to use to drive the
          process.

    # Usage

    $ build \
        --config=en/config.common.toml \
        --config=en/config.ignore.toml \
        --config=en/config.html.toml \
        html

    $ build \
        --config=en/config.common.toml \
        --config=en/config.ignore.toml \
        --config=en/config.html.toml \
        html --single

    $ build \
        --config=en/config.common.toml \
        --config=en/config.pdf.toml \
        pdf

    $ build \
        --config=en/config.common.toml \
        --config=en/config.pdf.toml \
        pdf --latex

    """

    # Initialize the shared context object to a dictionary and configure
    # it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    if len(kwargs["config"]) == 0:

        console.print("[red]At least one configuration file is required![/red]")
        console.print("[red]$ build --config=cfg.toml html[/red]")

        raise click.Abort()

    config = setup([Path(p) for p in kwargs["config"]])

    # Do we have any plugins that we need to load?
    if "plugin_path" in config:

        plugin_path = config["root"].joinpath(config["plugin_path"])

        if plugin_path.exists() and plugin_path.is_dir():
            console.print(f"Searching for plugins ({plugin_path})...")

            for f in plugin_path.glob("*.py"):
                console.print(f"Found {f}, attempting to import...")
                load_module(f.stem, str(f))

    # Add the configuration to the context object that will be made
    # available to all the commands
    ctx.obj["cfg"] = config

# --------
# Commands

main.add_command(html)
main.add_command(pdf)
