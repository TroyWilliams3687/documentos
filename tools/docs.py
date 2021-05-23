#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 094f1c94-b8ba-11eb-96c0-41de2ca30456
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-05-19
-----------

"""
# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# 3rd Party

import click
import yaml

from appdirs import AppDirs

# ------------
# Custom Modules

from md_docs.common import find_repo_root

from .common import get_basic_logger

from .stats import stats
from .graph import graph
from .validate import validate

# -------------
# Logging

log = get_basic_logger()
# -------------

__appname__ = "docs"
__company__ = "bluebill.net"


def setup(cfg):
    """

    Load the configuration settings and and return a dictionary. Basically,
    this looks for the root of the repository (i.e. the .git folder). Every
    thing will be relative to that folder.

    # Parameters

    cfg:list(pathlib.Path)
        - A list of YAML configuration files that will be merged to drive the process.


    # Return

    A dictionary containing the configurations to use for the process.

    """

    repo_root = find_repo_root(Path.cwd().resolve())

    if repo_root is None:
        raise FileNotFoundError(
            "Could not find repo root! The root should contain `.git` folder."
        )

    config = {}

    for c in [yaml.load(c.read_text(), Loader=yaml.FullLoader) for c in cfg]:
        config |= c

    config["root"] = repo_root

    config["documents.path"] = config["root"].joinpath(config["documents"]["path"])

    dirs = AppDirs()

    config["config_folder"] = (
        Path(dirs.user_config_dir).joinpath(__company__).joinpath(__appname__)
    )
    config["cache_folder"] = (
        Path(dirs.user_cache_dir).joinpath(__company__).joinpath(__appname__)
    )

    return config


@click.group()
@click.version_option(package_name="md_docs")
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

    # Parameters

    # Usage


    """

    # Initialize the shared context object to a dictionary and configure it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    if len(kwargs["config"]) == 0:

        log.error("At least one configuration file is required!")
        log.error("$ build --config=cfg.yaml html")

        raise click.Abort()

    ctx.obj["cfg"] = setup([Path(p) for p in kwargs["config"]])


# -----------
# Add the child menu options

main.add_command(stats)
main.add_command(graph)
main.add_command(validate)
