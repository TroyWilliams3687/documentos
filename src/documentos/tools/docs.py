#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : 094f1c94-b8ba-11eb-96c0-41de2ca30456
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-19
# -----------


"""
Methods defining the `docs` command.
"""

# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# 3rd Party

import click
import toml

from appdirs import AppDirs

from rich.traceback import install
install(show_locals=False)

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from ..documentos.common import find_folder_on_path

from .stats import stats
from .graph import graph
from .validate import validate

from .repair import repair

# -------------

# required to consistently use the AppDirs object and get the correct
# information related to this application

__appname__ = "docs"
__company__ = "bluebill.net"


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

    config["documents.path"] = config["root"].joinpath(config["documents"]["path"])

    dirs = AppDirs()

    config["cache_folder"] = (
        Path(dirs.user_cache_dir).joinpath(__company__).joinpath(__appname__)
    )

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
    The `docs` command provides access to various tools to validate and
    alter the system.

    # Parameters

    --config:Path
        - The path to the configuration file to use
        - Can specify multiple configuration files to promote
          de-duplication and sharing across build systems (i.e. HTML
          and PDF)

    # Usage

    $ docs --config=./en/config.common.toml validate markdown

    $ docs --config=./en/config.common.toml validate lst

    $ docs --config=./en/config.common.toml graph ./en/documents/all.lst

    $ docs --config=./en/config.common.toml stats

    $ docs --config=./en/config.common.toml repair --dry-run links

    $ docs --config=./en/config.common.toml repair links

    $ docs --config=./en/config.common.toml repair --dry-run images

    $ docs --config=./en/config.common.toml repair images

    $ docs --config=./en/config.common.toml repair --dry-run headers

    $ docs --config=./en/config.common.toml repair --dry-run headers --list

    $ docs --config=./en/config.common.toml repair headers --list

    $ docs --config=./en/config.common.toml repair headers
    """

    # Initialize the shared context object to a dictionary and configure
    # it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    if len(kwargs["config"]) == 0:

        console.print("[red]At least one configuration file is required![/red]")
        console.print("[red]$ docs --config=cfg.toml html[/red]")

        raise click.Abort()

    ctx.obj["cfg"] = setup([Path(p) for p in kwargs["config"]])


# --------
# Commands

main.add_command(stats)
main.add_command(graph)
main.add_command(validate)
# main.add_command(yaml_blocks)
main.add_command(repair)
