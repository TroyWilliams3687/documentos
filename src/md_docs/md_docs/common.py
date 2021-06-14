#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 91995646-2f49-11eb-8e0d-60f262a5770a
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2020-11-25
-----------

Common methods shared amoung the rest of the code base.

"""

# ------------
# System Modules

import subprocess

from pathlib import Path
from itertools import zip_longest

# ------------
# Custom Modules


def run_cmd(cmd, **kwargs):
    """
    Takes the list of arguments, cmd, and executes them via subprocess.
    It captures STDOUT to a list which can be printed to terminal later.

    # Parameters

    cmd: list(str)
        - The commands to pass to subprocess.

    # Parameters (kwargs)

    cwd:pathlib.Path
        - The path to change the current working directory to
        - Default - None

    # NOTE

    Reference: <https://docs.python.org/3/library/subprocess.html>

    You can use the shlex module to figure out what to pass as the list.
    It helps with complex command lines.

    >>> import shlex, subprocess
    >>> command_line = input()
    /bin/vikings -input eggs.txt -output "spam spam.txt" -cmd "echo '$MONEY'"
    >>> args = shlex.split(command_line)
    >>> print(args)
    ['/bin/vikings',
     '-input',
     'eggs.txt',
     '-output',
     'spam spam.txt',
     '-cmd',
     "echo '$MONEY'"]
    >>> p = subprocess.Popen(args) # Success!

    Using shlex and pasting the command into repl can make this process
    much easier to work with.

    """

    cwd = kwargs["cwd"] if "cwd" in kwargs else None

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd,
    )

    # Gather the results of the operation from STDOUT
    return [line.strip() for line in p.stdout]


def find_folder_on_path(path, target='.git', **kwargs):
    """

    Given a path, find the repo root. The root is considered the top-level
    folder containing the '.git' folder. This method will traverse up the
    tree, searching each level.

    If not `.git` folder is found, None is returned. Otherwise the parent
    folder path of the `.git` folder is returned.

    # Parameters

    path:pathlib.Path
        - the path to search for the repo root.

    target:str
        - The name of the folder to search for. The parent of this
          folder is considered the root folder. parent folder to be the
          root folder
        - Default - '.git' - We'll use the .git folder to identify the
          parent folder.

    # Return

    If the 'target'  is found, the parent of 'target'  is
    returned. Otherwise None is returned.

    """

    # construct the search list, we want to search the path and its
    # parents.
    search = [path] + list(path.parents)

    for p in search:

        if p.joinpath(target).exists():
            return p

    return None


def path_to_root(root, target):
    """
    Given a root path and a target path that exists under the root
    folder somewhere, return the number of relative directory up
    commands (i.e. '../my.file') to use to get to the root folder.


    # Parameters

    root:pathlib.Path
        - the root folder we want to change directories too.

    target:pathlib.Path
        - The target folder/file that we want to see how many steps to get to root from here.
        - It must be a sub-path of root otherwise an exception is raised.

    # Return

    A Path object representing the relative number of directory changes
    to get to the root folder from the target folder.

    # Example

    root = /folder1/folder2/folder3

    target = /folder1/folder2/folder3/1/2/3/file.md

    result = ../../../

    """

    count = len(target.relative_to(root).parents) - 1

    if count == 0:
        return Path(".")

    else:
        return Path("/".join([".."] * count) + "/")


def relative_path(left, right):
    """
    Given two paths, the left and the right, determine a path that can traverse
    from the left path to the right path using `..` and `.`.

    This method works by determining the longest common path shared between the
    left and right path.

    # Parameters

    left:Path
        - A path in a file system. This is the starting point and we
        want to navigate from here to the right using `..` and `.` notation

    right:Path
        - A path in a file system. This is the destination point. We want
        to navigate here from the left path.

    # Return

    A path representing how to move from the left path to the right path
    using a relative path notation.


    # Note

    - It is assumed that left and right are folders, not files or a
    mixture of files and folders.
    - It is assumed that the left and right path are rooted in the same
    file system.
    - If no root path is found (i.e. /), it is assumed that the paths are
    relative to a common shared file system containing both of this paths.

    `left  = documents/assets/designer`
    `right = help/assets/designer`

    It will be assumed that they paths look like this:
    `left  = /documents/assets/designer`
    `right = /help/assets/designer`

    in this case, it returns `../../../help/assets/designer`

    # Reference

    - https://stackoverflow.com/questions/29055511/how-to-find-relative-path-given-two-absolute-paths
    - https://stackoverflow.com/questions/28952366/resolving-a-relative-path-without-referencing-the-current-directory-on-windows/28953905#28953905

    """

    ls = left.parts
    rs = right.parts

    common_prefix = []

    for l, r in zip_longest(ls, rs):

        if l == r:
            common_prefix.append(l)

        else:
            break

    cp_length = len(common_prefix)

    ls = list(ls[cp_length:])
    rs = list(rs[cp_length:])

    cwd = [".."] * len(ls) if len(ls) > 0 else ["."]

    return Path("/".join(cwd + rs))


def search(root=None, extensions=None, recursive=True, **kwargs):
    """

    A generator method that will search the for all files matching any
    extension within the `extensions` lists recursively starting at
    `root`.

    # Parameters

    root:pathlib.Path
        - The root folder to search recursively

    extension:str
        - The file extension to search for
        - Default - .md
        - Note: it has to be dotted i.e. .md and not md

    recursive:bool
        - Search all nested folders from root recursively for the target
          files.
        - Default - True

    # Return

    Each file as it is found.

    # NOTE

    - This is a generator.
    - Extensions is an iterable.
    - Extensions have to be dotted and lower case i.e. ['.md', '.lst'].

    # Example

    return [f for f in search(
                           root=Path("~/documents",
                           extensions=['.md'],
                       )
    ]

    """

    pattern = root.rglob if recursive else root.glob

    for f in pattern("*.*"):

        if extensions is None or f.suffix.lower() in extensions:
            yield f
