#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = fb7b0232-b4bc-11eb-833e-df61029d6284
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-14
# -----------

"""
This module is the main entry point into the build app. This will build a series of documents
by transforming markdown files stored in nested folders into HTML or PDF using Pandoc and
some light custom markup files (LST).

See the `en` folder at the root for sample documents to transform and instructions on the
system usage.
"""

# ------------
# System Modules - Included with Python

import sys
import logging

from pathlib import Path

# ------------
# 3rd Party

import click
import yaml

# ------------
# Custom Modules

from md_docs.common import find_repo_root

from .common import get_basic_logger

from .html import html
from .pdf import pdf

# -------------
# Logging

log = get_basic_logger(__name__)
# -------------

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

    # config = yaml.load(cfg.read_text(), Loader=yaml.FullLoader)

    config['root'] = repo_root

    # make sure we have ignore_toc as an empty set at a minimum. Otherwise
    # transform it to a set because there is no YAML for it
    if 'ignore_toc' in config:

        config['ignore_toc'] = set(config['ignore_toc'])

    else:

        config['ignore_toc'] = set()

    return config


@click.group()
@click.version_option(package_name="md_docs")
@click.option('--config', '-c',
              multiple=True,
              type=click.Path(exists=True),
              help="Pass in the configuration file to control the process. You can pass in multiple files by calling the switch multiple times. The order you pass the files in matters. Any duplicate values will be overwritten by the last file.")
@click.pass_context
def main(*args, **kwargs):
    """

    Transform the markdown files into another form suitable for publication.

    # Parameters

    build_cfg:str
        - The path to the YAML configuration file to use to drive the process.

    # Usage

    $ build ./en/config.hmtl.yaml html

    $ build ./en/config.html.yaml html --single

    $ build ./en/config.pdf.yaml pdf

    $ build ./en/config.pdf.yaml pdf --latex

    """

    # Initialize the shared context object to a dictionary and configure it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    if len(kwargs['config']) == 0:

        log.error('At least one configuration file is required!')
        log.error('$ build --config=cfg.yaml html')

        raise click.Abort()

    ctx.obj['cfg'] = setup([Path(p) for p in kwargs['config']])


# -----------
# Add the child menu options

main.add_command(html)
main.add_command(pdf)

