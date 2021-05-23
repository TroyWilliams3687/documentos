#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2021 Troy Williams

uuid       = 633f2088-bbe3-11eb-b9c2-33be0bb8451e
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2021-05-23
-----------

This module will hold code to repair various problems that could occur.

- bad-links
    - relative links that don't point to the correct file

- section attributes
    - ATX headers that are missing links

--dry-run

"""

# ------------
# System Modules - Included with Python

import logging

from pathlib import Path
from datetime import datetime
from multiprocessing import Pool
from functools import partial

from difflib import get_close_matches

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules


from md_docs.document import (
    MarkdownDocument,
    search,
    document_lookup,
)

from md_docs.document_validation import (
    validate_urls,
    validate_images,
)

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------

# $ docs repair --dry-run links <- relative markdown links - runs the validate mechanism first and uses those files
# $ docs repair --dry-run headers <- attributes - i.e. anchor tags
# $ docs repair --dry-run images <- relative images

def find_broken_urls(md):
    """
    Examine the relative links for the MarkdownDocument object and return
    a list contain links that don't have matches on the file system.

    # Parameters

    md:MarkdownDocument
        - the document to examine

    # Return

    a list of tuples that contains the problem link and line number.

    item:
    - line number (0 based)
    - dict
        - 'full' - The full regex match - [text](link)
        - 'text' - The text portion of the markdown link
        - 'link' - The URL portion of the markdown link
        - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
        - "md": result.group("md"),
        - "section_span": result.span("section"),
        - "section": section attribute i.e ../file.md#id <- the id portion,

    """

    problems = []

    for rurl in md.relative_links():

        file = md.filename.parent.joinpath(rurl[1]["md"]).resolve()

        if not file.exists():
            problems.append(rurl)

    return problems

def sort_broken_urls(
    lookup=None,
    broken_urls=None,
):
    """

    Using the lookup dictionary and the list of broken urls, sort the
    broken urls for further processing. Sort them into

    - `no match` - There is no match on the file system for the URLs
    - `file match` - There are matching file names on the system
    - `suggestions` - There are no-matching file names, but some of the
                      file names are close


    # Parameters

    lookup:dict
        - A dictionary keyed by the file name mapped to a list of MarkdownDocument
        objects that have the same name but different paths.

    broken_urls:list
        - a list of tuples that contains the problem link and line number.

        - item:
            - line number (0 based)
            - dict
                - 'full' - The full regex match - [text](link)
                - 'text' - The text portion of the markdown link
                - 'link' - The URL portion of the markdown link
                - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
                - "md": result.group("md"),
                - "section_span": result.span("section"),
                - "section": section attribute i.e ../file.md#id <- the id portion,

    # Return

    A dictionary sorting the broken urls into:

    - no_matches - no matches were found, this is a list of the broken urls
    - file_matches - Direct matches in the file system were found, this is a tuple of the broken url and a list of MarkdownDocument objects
        - The name of the file has an exact match in the system, or a number of matches
    - suggestions - Closes matches found in the file system, this is a tuple of the broken url and a list of MarkdownDocument objects
        - This may not be an ideal case or even correct.
    """

    results={
        'no_matches':[],
        'file_matches':[],
        'suggestions':[],
    }

    for problem in broken_urls:

        line, url = problem

        key = Path(url['md']).name

        if key in lookup:

            results['file_matches'].append((problem, [match for match in lookup[key]]))

        else:

            # https://docs.python.org/3/library/difflib.html#difflib.get_close_matches

            # Can we suggest anything?
            suggestions = get_close_matches(key, lookup.keys(), cutoff=0.8)

            if suggestions:

                results['suggestions'].append((problem, [match  for pk in suggestions for match in lookup[pk]]))

            else:

                # We don't have a file match or any suggestions - a dead end :(
                results['no_matches'].append(problem)

    return results


@click.group("repair")
@click.option(
    "--dry-run",
    is_flag=True,
    help="List the changes that would be made without actually making any.",
)
@click.pass_context
def repair(*args, **kwargs):
    """

    Repair certain things within the Markdown documents. This will
    provide tools to deal with validation issues.

    # Usage

    $ docs --config=./en/config.common.yaml repair --dry-run links


    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    config['dry_run'] = kwargs['dry_run'] if 'dry_run' in kwargs else False

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for Markdown files...")

    config["md_files"] = search(root=config["documents.path"])

    log.info(f'{len(config["md_files"])} Markdown files were found...')
    log.info("")

    args[0].obj["cfg"] = config


@repair.command("links")
@click.pass_context
def links(*args, **kwargs):
    """

    Examine all of the Markdown documents in the configuration folder.
    Determine if there are relative lines that have a problem and attempt
    to fix them.

    - Only looks at Markdown Links of the form `[text](url)`
    - Only examines relative links
    - If it finds the correct file, and there is only one it can correct
    the link. If the link could be pointing to multiple files, it will
    not correct, but offer the suggestion of potential matches

    # Usage

    $ docs --config=./en/config.common.yaml repair --dry-run links

    """
    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now()

    # ------
    # Validate Markdown Files

    log.info("Processing Markdown File Links...")
    log.info("")

    lookup = document_lookup(config["md_files"])

    for md in config["md_files"]:

        md_relative = md.filename.relative_to(config["documents.path"])

        broken_urls = find_broken_urls(md)

        results = sort_broken_urls(
            lookup=lookup,
            broken_urls=broken_urls,
        )

        if results['no_matches']:
            log.info('------')

            for problem in results['no_matches']:
                line, url = problem
                log.info(f'{md_relative} - line {line} - UNRESOLVED URL -> {url["full"]}')

            log.info('')

        if results['file_matches']:
            log.info('------')

            for problem, matches in results['file_matches']:
                line, url = problem
                log.info(f'{md_relative} - line {line} - UNRESOLVED URL -> {url["full"]}')

                for match in matches:
                    log.info(f'\t FILE MATCH -> {match.filename.relative_to(config["documents.path"])}')

            log.info('')

        if results['suggestions']:
            log.info('------')

            for problem, matches in results['suggestions']:
                line, url = problem
                log.info(f'{md_relative} - line {line} - UNRESOLVED URL -> {url["full"]}')

                for match in matches:
                    log.info(f'\t POTENTIAL MATCH -> {match.filename.relative_to(config["documents.path"])}')

            log.info('')

        # implement file writing
        #   - update the contents of the markdown file by replacing the url link on the individual lines
        #   - only use file matches that have exactly 1 match
        #   - implement the --dry-run and updating the files based on len(file_matches) == 1
        #   - it should say:
        #   `{file} - line: {line} - {url["full"]} -> {new_url}

        # Clean up this method

    # --------------

    build_end_time = datetime.now()

    log.info("")
    log.info("-----")
    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")





