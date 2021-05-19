#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 094f1c94-b8ba-11eb-96c0-41de2ca30456
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

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules


# -------------
# Logging

# configure logging for this module - it is a bit different here because
# it is intended to be executed by the user <http://nathanielobrown.com/blog/posts/quick_and_dirty_python_logging_lesson.html>

# Logging Levels:
# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET

# get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO) # change logging level here...

# make a console logger
console = logging.StreamHandler()

# add the console logger to the root logger
logger.addHandler(console)

# Assign the variable
log = logging.getLogger(__name__)
# -------------

# ------------
# System Modules - Included with Python

import sys
import logging

from pathlib import Path

# ------------
# 3rd Party

import click
from appdirs import AppDirs

# ------------
# Custom Modules

from md_docs.common import find_repo_root

from .common import get_basic_logger

from .stats import stats

# -------------
# Logging

log = get_basic_logger(__name__)
# -------------

__appname__ = "docs"
__company__ = "bluebill.net"

def setup():
    """

    Load the configuration settings and and return a dictionary. Basically,
    this looks for the root of the repository (i.e. the .git folder). Every
    thing will be relative to that folder.

    # Parameters


    # Return

    A dictionary containing the configurations to use for the process.

    """

    repo_root = find_repo_root(Path.cwd().resolve())

    if repo_root is None:
        raise FileNotFoundError(
            "Could not find repo root! The root should contain `.git` folder."
        )

    config = {}

    config["root"] = repo_root

    dirs = AppDirs()

    config['config_folder'] = Path(dirs.user_config_dir).joinpath(__company__).joinpath(__appname__)
    config['cache_folder'] = Path(dirs.user_cache_dir).joinpath(__company__).joinpath(__appname__)

    # paths['config_folder'].mkdir(parents=True, exist_ok=True)
    # paths['cache_folder'].mkdir(parents=True, exist_ok=True)

    return config


@click.group()
@click.version_option(package_name="md_docs")
@click.pass_context
def main(*args, **kwargs):
    """

    # Parameters

    # Usage


    """

    # Initialize the shared context object to a dictionary and configure it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    ctx.obj["cfg"] = setup()



# -----------
# Add the child menu options

main.add_command(stats)
