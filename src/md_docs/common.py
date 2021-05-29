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

A module for common things I'll need to process documents

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
    Takes the list of arguments, cmd, and executes them via subprocess. It prints
    stdout to the terminal to report on progress or issues.

    # Parameters

    cmd: list[str]
        - The command and list of switches to execute

    # Parameters (kwargs)

    cwd:pathlib.Path
        - The path to change the current working directory too
        - Default - None

    # NOTE

    Reference: https://docs.python.org/3/library/subprocess.html

    >>> import shlex, subprocess
    >>> command_line = input()
    /bin/vikings -input eggs.txt -output "spam spam.txt" -cmd "echo '$MONEY'"
    >>> args = shlex.split(command_line)
    >>> print(args)
    ['/bin/vikings', '-input', 'eggs.txt', '-output', 'spam spam.txt', '-cmd', "echo '$MONEY'"]
    >>> p = subprocess.Popen(args) # Success!

    Using shlex and pasting the command into repl can make this process much easier to work with.

    """

    cwd = kwargs["cwd"] if "cwd" in kwargs else None

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd,
    )

    # Gather the output to stdout to a list
    output = [line.strip() for line in p.stdout]

    # return the output for processing
    return output


def read_lst(lst=None):
    """

    Read the contents of the lst file. If there are references to other
    lst files, they will be read recursively.

    # Parameters

    lst:pathlib.Path
        - The path to the lst file to extract the file paths from

    # Return

    A list of Path objects, in the order they are read, to the markdown documents to merge.

    """

    files = []
    with lst.open("r", encoding="utf-8") as f:
        for line in f.readlines():

            # handle comments - in-line or whole line
            line = line.partition("#")[0].strip()

            if line:
                # We have a file path
                p = lst.parent.joinpath(Path(line)).resolve()

                # Do we have a .lst?
                if p.suffix.lower() == ".lst":

                    if p == lst:
                        raise ValueError(
                            f"Recursive link to self found! {lst} contains a reference to itself."
                        )

                    results = read_lst(p)
                    files.extend(results)

                else:
                    files.append(p)

    return files


def find_repo_root(path, **kwargs):
    """
    Given a path, find the repo root. The root is considered to contain
    the `.git` folder in it. It will traverse up the tree and search each
    level. None is returned.

    """

    # construct the search list
    search = [path] + list(path.parents)

    root = None
    for p in search:
        git = p.joinpath(".git")
        if git.exists():
            root = p
            break

    return root


def path_to_root(root, target):
    """
    Given a root path and a target path that exists under the root
    folder somewhere, return the number of relative directory up
    commands (i.e. '../my.file') to use to get to the root folder.

    Example:
    root = /folder1/folder2/folder3

    target = /folder1/folder2/folder3/1/2/3/file.md

    result = ../../../

    # Parameters

    root:pathlib.Path
        - the root folder we want to change directories too.

    target:pathlib.Path
        - The target folder/file that we want to see how many steps to get to root from here.
        - It must be a sub-path of root otherwise an exception is raised.

    # Return

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

    - It is assumed that the left and right path are rooted in the same
    file system.
    - If no root path is found (i.e. /), it is assumed that the paths are
    relative to a common shared file system containing both of this paths

    `left  = documents/assets/designer`
    `right = help/assets/designer`

    It will be assumed that they paths look like this:
    `left  = /documents/assets/designer`
    `right = /help/assets/designer`

    in this case, it return `../../../help/assets/designer`

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


def find_lst_links(lst, lst_file_contents):
    """
    Recursively find all links in the given lst file.

    # Parameters

    lst:Path
        - A relative path to the lst file that we are interested in.

    lst_file_contents:dict
        - A dictionary keyed by the lst file containing a list of strings
        representing the contents of the contents of the file
        - The paths to the lst files are relative of the root of the document
        folder i.e. document_root

    # Return

    A list of MDLink objects representing all of the links contained within
    the lst file and the recursive lst files...
    """

    all_links = []

    for link in lst_file_contents[str(lst)]:

        if link.link.suffix == ".md":
            all_links.append(link)

        elif link.link.suffix == ".lst":

            discovered_links = find_lst_links(link.link, lst_file_contents)

            all_links.extend(discovered_links)

        else:

            raise ValueError(
                f"{link.link} - Unknown file extension ({link.link.suffix})!"
            )

    return all_links


def search(root=None, extensions=None):
    """
    Search for all of the files starting from the root folder that
    match the one of the file extensions.


    # Parameters

    root:pathlib.Path
        - The root folder to search recursively

    extension:str
        - The file extension to search for
        - Default - .md
        - Note: it has to be dotted i.e. .md and not md

    # Return

    Each file as it is found.

    # NOTE

    - This is a generator
    - extensions is an iterable
    - extensions have to be dotted and lower case i.e. ['.md', '.lst']

    # Example

    return [f for f in search(
                           root=Path("~/documents",
                           extensions=['.md'],
                       )
    ]

    """

    files = []

    for f in root.rglob("*.*"):

        if extensions is None or f.suffix.lower() in extensions:
            yield f
