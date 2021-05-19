#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 075b9352-5bec-11eb-9b85-8181a5d9cc8c
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-01-21
# -----------

"""
Shared methods
"""

# ------------
# System Modules - Included with Python

import logging

from pathlib import Path
from collections import namedtuple

# ------------
# 3rd Party

# ------------
# Custom Modules

from md_docs.markdown_classifiers import (
    MarkdownLinkRule,
    RelativeMarkdownURLRule,
    CodeFenceClassifier,
)

from md_docs.common import find_repo_root


def find_images(img_path, root):
    """

    Find all images stored in the `img_path` folder. The images it searches
    for are:

    - *.png
    - *.jpg/*.jpeg
    - *.gif

    # Parameters

    img_path:pathlib.Path
        - The path to the folder where the images are stored. The images can be stored in
        sub-folders underneath this path.

    root:pathlib.Path
        - The Root folder used to transform the absolute paths of the images to relative paths

    # Return

    A dictionary keyed by image name with a list of relative image paths containing that same file name.

    # Note

    During the search it ignores the case of the extension. .jpg is treated the same as .JPG

    """

    extensions = (".png", ".gif", ".jpg", ".jpeg")

    images = {}
    for f in img_path.rglob("*.*"):
        if f.suffix.lower() in extensions:
            images.setdefault(f.name, []).append(f.relative_to(root))

    return images


def get_basic_logger(logger_name, level=logging.INFO):
    """

    Configure a basic logger that logs to the console. It defaults to the INFO
    level of logging.

    Logging Levels:
        - CRITICAL
        - ERROR
        - WARNING
        - INFO
        - DEBUG
        - NOTSET

    # Reference

        - <http://nathanielobrown.com/blog/posts/quick_and_dirty_python_logging_lesson.html>
    """

    logger = logging.getLogger()
    logger.setLevel(level)  # change logging level here...

    console = logging.StreamHandler()

    logger.addHandler(console)

    return logging.getLogger(logger_name)
