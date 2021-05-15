#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = 91995646-2f49-11eb-8e0d-60f262a5770a
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-11-25
# -----------

"""
A module for common things I'll need to process documents

"""

# ------------
# System Modules

import subprocess
import logging

from pathlib import Path
from itertools import zip_longest
from collections import namedtuple

# ------------
# Custom Modules

from .markdown_classifiers import (
    MarkdownLinkRule,
    RelativeMarkdownURLRule,
    CodeFenceClassifier,
)


# Module level logging
log = logging.getLogger(__name__)


# A simple data structure to hold the link information
MDLink = namedtuple(
    "MDLink",
    [
        "line",  # line number in the md file the link is located on
        "link",  # The relative markdown link
        "section",  # Section anchor if any
        "full",
    ],
)

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

    cwd = kwargs['cwd'] if 'cwd' in kwargs else None

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, cwd=cwd)

    # Gather the output to stdout to a list
    output = [l.strip() for l in p.stdout]

    # Send the output to the logger
    for l in output:
        log.info(l)

    # for l in p.stdout:
    #     log.info(l)

    # return the output for procesing
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
                        raise ValueError(f'Recursive link to self found! {lst} contains a reference to itself.')

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
        git = p.joinpath('.git')
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
        return Path('.')

    else:
        return Path('/'.join(['..']*count) + '/')

def find_highlight_themes(path):
    """
    Takes a path to a folder containing syntax highlighting themes (json
    files named .theme that pandoc understands).

    # Parameters

    path:pathlib.Path
        - The path of the folder to search for themes.

    # Return

    A dictionary keyed by file name i.e. 'pygements.theme'

    """

    themes = {}

    for theme in path.glob('**/*.theme'):
        themes[theme.name.lower()] = theme

    return themes


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

    cwd = ['..']*len(ls) if len(ls) > 0 else ['.']

    return Path('/'.join(cwd + rs))


def extract_relative_links(md_contents):
    """
    Read the contents of the markdown file and find all of the links.

    # Parameters

    md_contents:list(str)
        - The contents of the markdown file

    # Return

    a list containing tuples. The tuple contains the line number, the relative link and the full match

    """

    links = []

    md_link_rule = MarkdownLinkRule()
    relative_url_rule = RelativeMarkdownURLRule()

    code_fence_rule = CodeFenceClassifier()
    in_code_fence = False

    for i, line in enumerate(md_contents):

        # Do we have the start or end of a code fence block?
        if code_fence_rule.match(line):
            in_code_fence = not in_code_fence

        # Are we in a code fence?
        if in_code_fence:
            continue

        # Contains a valid markdown link?
        if md_link_rule.match(line.strip()):

            results = md_link_rule.extract_data(line.strip())

            # links.update(r['link'] for r in results)

            # can be multiple links in the line...
            for r in results:

                url = r[
                    "link"
                ]  # full, text and link are the variables in the results dictionary...

                # Is relative URL?
                if relative_url_rule.match(url):

                    results = relative_url_rule.extract_data(
                        url
                    )  # `md` and `section` are the keys we are interested in

                    links.append((i, results["md"], results["section"], r["full"]))

    return links

def create_md_link_lookup(md_file_contents, document_root):
    """

    Takes the contents of the markdown files, extracts the relative links
    and constructs a dictionary of the markdown file and the relative links
    it contains.

    # Parameters

    md_file_contents:dict
        - A dictionary keyed by the markdown file containing a list of strings
        representing the contents of the markdown file
        - The paths to the markdown files are relative of the root of the document
        folder i.e. document_root

    document_root:Path
        - The path to the root of the document folder.

    # Return

    A dictionary keyed by the relative markdown url linked to list of MDLinks objects.

    """

    links = {}

    for k, contents in md_file_contents.items():

        relative_links = extract_relative_links(contents)

        if relative_links:

            for rl in relative_links:

                line, url, section, full = rl

                links.setdefault(k, []).append(MDLink(line, url, section, full))

        else:

            # the document contains no links, add an empty list so that it can be accessed.

            links[k] = []

    return links

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

        if link.link.suffix == '.md':
            all_links.append(link)

        elif link.link.suffix == '.lst':

            discovered_links = find_lst_links(link.link, lst_file_contents)

            all_links.extend(discovered_links)

        else:

            raise ValueError(f'{link.link} - Unknown file extension ({link.link.suffix})!')

    return all_links


def create_lst_link_lookup(lst_file_contents, document_root):
    """

    Takes the contents of the lst files, extracts the relative links
    and constructs a dictionary showing what files the lst links too.

    It resolves the lst files to links so that the only thing stored are
    links to markdown files, that are relative to the list file

    # Parameters

    lst_file_contents:dict
        - A dictionary keyed by the lst file containing a list of strings
        representing the contents of the contents of the file
        - The paths to the lst files are relative of the root of the document
        folder i.e. document_root

    document_root:Path
        - The path to the root of the document folder.

    # Return

    A dictionary keyed by the link and pointing to a list MDlink.

    # NOTE

    The LST is a very simple format, it contains comments, empty lines and links
    on single lines. Ignore empty lines and comments.

    """

    links = {}

    for k, contents in lst_file_contents.items():

        document_links = []

        for i, line in enumerate(contents):

            row = line.strip().partition("#")

            # Is the line commented or empty?
            if len(row[0]) == 0:
                continue

            # Build the url fully resolved to a file
            url = document_root.joinpath(k).parent.joinpath(row[0]).resolve().relative_to(document_root)

            mdl = MDLink(i, url, None, url)

            links.setdefault(k, []).append(mdl)

    return links

def create_md_reverse_link_lookup(md_file_contents, document_root):
    """

    Takes the contents of the markdown files, extracts the relative links
    and constructs a reverse dictionary showing what files contain the same
    relative link to an existing markdown file.

    # Parameters

    md_file_contents:dict
        - A dictionary keyed by the markdown file containing a list of strings
        representing the contents of the markdown file
        - The paths to the markdown files are relative of the root of the document
        folder i.e. document_root

    document_root:Path
        - The path to the root of the document folder.

    # Return

    A dictionary keyed by the relative markdown link url linked to a dictionary.

    The value portion is a dictionary containing keys:
    - 'original file' - This is the path to the markdown file that contained the link
    - 'link' - A namedtuple containing information about the link, values are:
        - line - The line number in the markdown file where it was found
        - link - The url portion of the link
        - section - The section portion of the link
        - full - The full markdown formatted link

    """

    # The links dictionary is keyed by the relative url found in the document. The relative url is transformed so it
    # is relative to the document root so we can link all documents that point to the same link (even if it is
    # of different forms))
    links = {}

    for k, contents in md_file_contents.items():

        relative_links = extract_relative_links(contents)

        for rl in relative_links:

            line, url, section, full = rl

            mdl = MDLink(line, url, section, full)

            # Rebuild the url so it is relative to the document folder. This will allow use to know if multiple
            # documents point to the same file, even if the relative path is different. This also allows us to
            # handle files with the same name but different paths

            url = document_root.joinpath(k).parent.joinpath(url).resolve().relative_to(document_root)

            # Store the original document path and the relative link information
            links.setdefault(url, []).append({'original file':k, 'link':mdl})

    return links

def create_lst_reverse_link_lookup(lst_file_contents, document_root):
    """

    Takes the contents of the lst files, extracts the relative links
    and constructs a reverse dictionary showing what files contain the same
    relative link to an existing markdown file.

    # Parameters

    lst_file_contents:dict
        - A dictionary keyed by the lst file containing a list of strings
        representing the contents of the contents of the file
        - The paths to the lst files are relative of the root of the document
        folder i.e. document_root

    document_root:Path
        - The path to the root of the document folder.

    # Return

    A dictionary keyed by the link and pointing to a list of dictionaries that contain the link.

    # NOTE

    The LST is a very simple format, it contains comments, empty lines and links
    on single lines. Ignore empty lines and comments.

    """

    links = {}

    for k, contents in lst_file_contents.items():

        document_links = []

        for i, line in enumerate(contents):

            row = line.strip().partition("#")

            # Is the line commented or empty?
            if len(row[0]) == 0:
                continue

            # construct the url so that it is relative to the root of the document folder
            url = document_root.joinpath(k).parent.joinpath(row[0]).resolve().relative_to(document_root)

            mdl = MDLink(i, row[0], None, row[0])

            links.setdefault(url, []).append({'original file':k, 'link':mdl})

    return links
