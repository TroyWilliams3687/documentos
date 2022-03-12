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

import importlib.util

from abc import ABC, abstractmethod

# ------------
# 3rd Party - From pip

from rich.console import Console
console = Console()

# ------------
# Custom Modules


# -------------


# The registered plugins with the system. It is a dict of dicts. We add
# a new dictionary for each different type of plugin we have
registered_pluggins = {
    "table of contents": {},  # Create a table of contents given an LSTDocument
    "navigation": {},         # A set of plugins that generate navigation type documents for HTML output (i.e. sitemaps)
    "json document": {},      # Set of json plugs that are registered with the system
}


class JSONDocumentPlugin(ABC):
    """
    A plugin to construct a JSON document containing key fields for all
    of the Markdown documents in the system. The resulting JSON file
    will be useful for various offline/client side search scripts, for
    example elasticlunr.js or lunr.js. The JSON file will be feed into
    those to construct the index they use for searching.

    ```
    @register(name='elasticlunar.js')
    class JSONIndex(JSONDocumentPlugin):
        def __call__(self, documents=None, root=None, ignore=None):
            # A bunch of stuff is done here....
    ```

    """

    @property
    @abstractmethod
    def filename(self):
        """
        The name of the file to use to store the JSON string to, for
        example: `documents.json`.

        """

        pass


    @abstractmethod
    def __call__(self, documents=None, root=None, ignore=None):
        """
        Generate a JSON document suitable for use as the input for a
        JavaScript, client side search engine.


        # Parameters

        documents:list(MarkdownDocuments)
            - The list file we want to construct the JSON document from.

        root:Path
            - The path to the root folder of the documents.

        ignore:set(Path)
            - A set of file Path objects that we do not want to add to
              the JSON document.
            - Full path to the file to ignore.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - None

        # Return

        A valid JSON string is returned.

        """

        pass



class TOCPlugin(ABC):
    """
    A Table of Contents (TOC) plugin must implement this interface to be
    usable by our system.

    The idea is that this plugin will create a table of contents
    (TOC) from the give LSTDocument object. The TOC will be a list of
    Markdown formatted strings that will be converted by the Pandoc
    process.

    ```
    @register(name='TOC')
    class ReplaceTags(TOCPlugin):
        def __call__(self, lst=None, depth=6, ignore=None):
            # A bunch of stuff is done here....
    ```

    """

    @abstractmethod
    def __call__(self, lst, depth, ignore):
        """

        Generate a list of Markdown formatted strings representing a TOC
        for the provided LSTDocument object.

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

        ignore:set(Path)
            - A set of file Path objects that we do not want to add to
              the TOC.
            - Full path to the file to ignore.
            - Should be a set for efficient membership testing, but
              could be a list or tuple.
            - Default - None

        # Return

        The method will return a list of strings formatted using
        Markdown syntax.

        The system will construct a file from the list and place it in
        the same folder as the LST file.

        """

        pass


class NavigationPlugin(ABC):
    """

    This plugin is designed to work with HTML output.

    The plugin allows for the creation of different styles of navigation
    documents to be placed at the root of the output folder. This could
    be a traditional `sitemap.xml` or something more exotic and custom
    to your documentation needs.

    ```
    @register(name='sitemap')
    class SiteMapXML(HTMLNavigationPlugin):
        def __call__(self, root=None, documents=None):
            # A bunch of stuff is done here....
    ```

    This plugin will be given the root document folder and the list of
    MarkdownDocument objects. From these it should be able to construct
    the navigation file.

    # Assumptions

    Since this plugin is focused on HTML output, we can make some
    assumptions based on the build system. These assumptions will help
    us understand what we can and cannot do with this plugin.

    - The build system will transform the Markdown files to HTML in an
      output folder.
    - The HTML files will have the `.html` extension
    - The HTML file names will match the Markdown file names (less the
      file extension)
    - The relative path from the root of the document folder will be
      identical for the HTML and Markdown files
    - The generated navigation file contents will be written to a file
      at the root of the output folder

    """

    @abstractmethod
    def __call__(
        self,
        document_root=None,
        output=None,
        documents=None,
        **kwargs,
    ):
        """

        Given the root path and a list of MarkdownDocument objects,
        construct a suitable navigation document.

        # Parameters

        document_root:Path
            - The valid path to the root of the MarkdownDocument folder
            - It can be used to create relative paths from full paths

        output:Path
            - The valid path to the location that file should be written.
            - This is the folder where the plugin will write the navigation file too

        documents:iterable(MarkdownDocument)
            - The list of MarkdownDocument objects that will be used to
              construct the navigation document.

        # Return

        None - The file will be written by the plugin to the root
        folder.

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
    @register(name="replace_tags")
    class ReplaceTags(Plugin):
    ```

    Essentially it works like this:

    ```
    wrapper_register_plugin = register(name='replace_tags')
    ReplaceTags = wrapper_register(ReplaceTags)
    ```

    """

    def wrapper_register(cls):

        if issubclass(cls, TOCPlugin):
            key = "table of contents"

        elif issubclass(cls, NavigationPlugin):
            key = "navigation"

        elif issubclass(cls, JSONDocumentPlugin):
            key = "json document"

        else:
            raise TypeError(
                f"Cannot register class as a Plugin! Wrong type {type(cls)}..."
            )

        if name in registered_pluggins[key]:
            raise KeyError(
                f"Duplicate plugin name: `{name}`. Plugin names must be unique!"
            )

        registered_pluggins[key][name] = cls()

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

    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(mod)
