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

import click

# ------------
# Custom Modules

from md_docs.markdown_classifiers import (
    MarkdownLinkRule,
    RelativeMarkdownURLRule,
    CodeFenceClassifier,
)

from md_docs.common import find_repo_root


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


# def find_images(img_path, root):
#     """

#     Find all images stored in the `img_path` folder. The images it searches
#     for are:

#     - *.png
#     - *.jpg/*.jpeg
#     - *.gif

#     # Parameters

#     img_path:pathlib.Path
#         - The path to the folder where the images are stored. The images can be stored in
#         sub-folders underneath this path.

#     root:pathlib.Path
#         - The Root folder used to transform the absolute paths of the images to relative paths

#     # Return

#     A dictionary keyed by image name with a list of relative image paths containing that same file name.

#     # Note

#     During the search it ignores the case of the extension. .jpg is treated the same as .JPG

#     """

#     images = search(path=img_path, extensions=(".png", ".gif", ".jpg", ".jpeg"))

#     if root:

#         # make the images relative to the root folder
#         for k in images:

#             relative = []
#             for img in images[k]:
#                 relative.append(img.relative_to(root))

#             images[k] = relative

#     return images

    # ---------
    # extensions = (".png", ".gif", ".jpg", ".jpeg")

    # images = {}
    # for f in img_path.rglob("*.*"):
    #     if f.suffix.lower() in extensions:
    #         images.setdefault(f.name, []).append(f.relative_to(root))

    # return images


class Formatter(logging.Formatter):
    """

    https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3

    """

    # colors = {
    #     'error': dict(fg='red', bg='white'),
    #     'exception': dict(fg='red', bg='yellow'),
    #     'critical': dict(fg='red', bg='yellow'),
    #     'debug': dict(fg='blue', bg='yellow'),
    #     'warning': dict(fg='yellow')
    # }

    colors = {
        logging.ERROR: dict(
            fg="red",
            # bg='black',
            blink=False,
            bold=False,
            reverse=False,
            underline=False,
        ),
        logging.CRITICAL: dict(fg="red", bg="yellow"),
        logging.DEBUG: dict(fg="black", bg="yellow"),
        logging.WARNING: dict(fg="yellow"),
    }

    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = "%(message)s"

        else:
            msg = "%(levelname)s: %(msg)s"

            # use click to colorize the text
            # https://click.palletsprojects.com/en/7.x/api/
            # level = record.levelname.lower()
            if record.levelno in self.colors:
                msg = click.style(msg, **self.colors[record.levelno])

            self._style._fmt = msg

        return super().format(record)


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
    """

    # logging.basicConfig()
    logger = logging.getLogger()

    # Note that nothing is passed to getLogger
    # By passing nothing, logger is set to the "root" logger
    # If we instead set logger to logging.getLogger(__name__) other
    # modules will not inherit the settings from this module

    # in other modules call:
    # ```
    # logging.basicConfig()
    # log = logging.getLogger(__name__)
    # ```

    logger.setLevel(level)  # change logging level here...

    console = logging.StreamHandler()
    console.setFormatter(Formatter())

    logger.addHandler(console)

    return logger
