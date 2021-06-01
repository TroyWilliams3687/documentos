#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   30355578-c23b-11eb-aa62-1beaed170423
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date    2021-05-31
# -----------

"""
Define all the items we need to use, manage and maintain plugins.
"""

# ------------
# System Modules - Included with Python

import logging
import importlib.util

from abc import ABC, abstractmethod

# ------------
# 3rd Party - From pip

# ------------
# Custom Modules


# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


# the registered plugins with the system. It is a dict of dicts
registered_pluggins = {
    "table of contents": {},  # Add a new dictionary for each different type of plugin we have
}


class TOCPlugin(ABC):
    """
    A Table of Contents (TOC) plugin must implement this interface to be
    usable by our system.


    ```
    @register_plugin(name='TOC')
    class ReplaceTags(TOCPlugin):
        def __call__(self, lst=None, depth=6, ignore=None):
            # A bunch of stuff is done here....
    ```

    """

    @abstractmethod
    def __call__(self, lst, depth, ignore):
        """

        Generate a list of strings representing a TOC for the provided
        LSTDocument object.

        # Parameters

        lst:LSTDocument
            - The list file we want to construct a table of contents
              for

        depth:int
            - How many headers to display, a number from 0 to 6. 0 would
              be a link to the markdown file, 1 to 6 would refer to the
              ATX headers within that file.
            - Default - 6 - include all headers
            - NOTE - We could use this set to 0 to replace the ignore
              variable

        ignore:set(str)
            - a set of files that we do not want to add to the TOC.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - None
        """
        pass


def register(name):
    """

    A decorator that will register the plugin with the system. It is
    smart enough to properly classify the plugin and add it the correct
    register.


    # Parameters

    name:str
        - The dictionary key for the plugin name - a friendly name that
        can be used to retrieve the plugin at a later time

    # Usage

    This is a decorator that takes parameters to preset the wrapper. It
    should be called like this:

    ```
    @register_plugin(name='replace_tags')
    class ReplaceTags(Plugin):
    ```

    Essentially it works like this:

    ```
    wrapper_register_plugin = register_plugin(name='replace_tags')
    ReplaceTags = wrapper_register_plugin(ReplaceTags)
    ```

    """

    def wrapper_register(cls):

        if issubclass(cls, TOCPlugin):

            if name in registered_pluggins["table of contents"]:
                raise KeyError(
                    f"Duplicate plugin name: `{name}`. TOC plugin names must be unique!"
                )

            registered_pluggins["table of contents"][name] = cls()

        else:
            raise TypeError(
                f"Cannot register a class as a Plugin: wrong type {type(cls)}"
            )

    return wrapper_register


def load_module(module_name=None, path=None):
    """
    Load the module into the current space. Typically this will be used
    to load a python module that contains plugin definitions.

    # Parameters

    module_name:str
        - the name of the module to import. It is the name of the .py
          file. `fancy_things.py` would have  module name of
          `fancy_things`. path:str

    path:str
        - The full path to the python file (`~/plugins/fancy_things.py`)

    # Return

    None

    # Reference

    - <https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3>

    # Requirements

    import importlib.util

    # NOTE

    This module must be called at some point before attempting to
    execute the plugins. This ensures that the register_plugin
    decorators are called.

    # NOTE

    If the plugins are already part of a package that will be loaded
    with the application, this call isn't necessary.

    """

    log.debug(f"Importing {path}")

    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(mod)

    log.debug(f"Plugins: {registered_pluggins}")
