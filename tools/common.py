#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 075b9352-5bec-11eb-9b85-8181a5d9cc8c
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-01-21
-----------

Shared methods
"""

# ------------
# System Modules - Included with Python

import logging

# ------------
# 3rd Party

# ------------
# Custom Modules


def search(
    path=None,
    extensions=None,
):
    """

    # Parameters

    path:pathlib.Path
        - The folder to search

    extensions:list(str)
        - The list of extensions to search for
        - Default - None
        - Note: it has to be dotted i.e. .md and not md

    # Return

    A dictionary keyed by extension containing a list of Path objects
    discovered.

    """

    files = {}

    for f in path.rglob("*.*"):

        if f.suffix.lower() in extensions:
            files.setdefault(f.name, []).append(f)

    return files


def get_basic_logger(level=logging.INFO):
    """

    Configure a basic logger that logs to the console. It defaults to the INFO
    level of logging.

    The idea is that this logger can be called in the main entry point. Other
    modules should simple call `log = logging.getLogger(__name__)`

    Logging Levels:
        - CRITICAL
        - ERROR
        - WARNING
        - INFO
        - DEBUG
        - NOTSET

    # Reference

        - <http://nathanielobrown.com/blog/posts/quick_and_dirty_python_logging_lesson.html>

    # NOTE

    This method should only be called by the main entry point into the application.

    Note that nothing is passed to getLogger By passing nothing, logger is set
    to the "root" logger If we instead set logger to logging.getLogger
    (__name__) other modules will not inherit the settings from this module

    In other modules simply call:

    ```
    log = logging.getLogger(__name__)
    ```
    """

    logger = logging.getLogger()

    logger.setLevel(level)

    console = logging.StreamHandler()

    logger.addHandler(console)

    return logger
