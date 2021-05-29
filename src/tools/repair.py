#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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
import hashlib

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

from md_docs.common import (
    relative_path,
    search,
)

from md_docs.document import (
    MarkdownDocument,
    search as md_search,
    document_lookup,
)

from md_docs.document_validation import (
    validate_urls,
    validate_images,
)

from md_docs.markdown_classifiers import MarkdownAttributeSyntax

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------

# $ docs repair --dry-run links <- relative markdown links - runs the validate mechanism first and uses those files
# $ docs repair --dry-run images <- relative images
# $ docs repair --dry-run headers <- attributes - i.e. anchor tags


def find_broken_urls(
    parent=None,
    links=None,
):
    """
    Examine the relative links for the MarkdownDocument object and return
    a list contain links that don't have matches on the file system.

    Can work for images or relative links pointing to markdown files.

    # Parameters

    parent:Path
        - The path of the parent folder to resolve links

    links:list(tuple)
        - A list of tuples containing:
            - line number (0 based)
            - dict
                - 'url' - The URL portion of the markdown link
                - The `url` key is the required and is the URL of the
                relative link

    # Return

    a list of tuples that contains the problem link and line number.

    item:
    - line number (0 based)
    - dict
        - 'url' - The URL portion of the markdown link

    """

    problems = []

    for rurl in links:

        # we only want the URL, not any section anchors
        left, _, _ = rurl[1]["url"].partition("#")

        file = parent.joinpath(left).resolve()

        if not file.exists():
            problems.append(rurl)

    return problems


def classify_broken_urls(
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
                - 'url' - The URL portion of the markdown link
                - "md_span": result.span("md"),  # tuple(start, end) <- start and end position of the match
                - "md": result.group("md"),
                - "section_span": result.span("section"),
                - "section": section attribute i.e ../file.md#id <- the id portion,

    # Return

    A dictionary keyed by:

    - no_matches - no matches were found, this is a list of the broken urls
    - exact_matches - Direct matches in the file system were found, this is a tuple of the broken url and a list of MarkdownDocument objects
        - The name of the file has an exact match in the system, or a number of matches
        - multiple exact matches fount
    - exact_match - Only one exact match found
    - suggestions - Closes matches found in the file system, this is a tuple of the broken url and a list of MarkdownDocument objects
        - This may not be an ideal case or even correct.

    Each key will contain a list of tuples: (dict, list)
    - dict - this is the same dict that was in the broken_urls list
    - list - the list of Path objects that match or are similar

    """

    results = {
        "no_matches": [],
        "suggestions": [],
        "exact_match": [],
        "exact_matches": [],
    }

    for problem in broken_urls:
        line, url = problem

        # we only want the URL, not any section anchors
        left, _, _ = url["url"].partition("#")

        key = Path(left).name
        # key = Path(url["md"]).name

        if key in lookup:

            matches = [match for match in lookup[key]]

            if len(matches) == 1:
                results["exact_match"].append((problem, matches))

            else:
                results["exact_matches"].append((problem, matches))

        else:
            # https://docs.python.org/3/library/difflib.html#difflib.get_close_matches

            # Can we suggest anything?
            suggestions = get_close_matches(key, lookup.keys(), cutoff=0.8)

            if suggestions:
                results["suggestions"].append(
                    (problem, [match for pk in suggestions for match in lookup[pk]])
                )

            else:
                # We don't have a file match or any suggestions - a dead end :(
                results["no_matches"].append((problem, []))

    return results


def display_classified_url(results, root=None):
    """

    # Parameters

    results:list
        - A list containing a reference to a MarkdownDocument and a list of tuples
        containing line, url (dict) and the list of matches (MarkdownDocument)

    root:Path
        - The path to the root of the document folder

    """

    for item in results:
        md, problems = item
        md_relative = md.filename.relative_to(root)

        for defect, matches in problems:
            line, url = defect

            log.info(f"File: {md_relative}")
            log.info(f'Line: {line} -> `{url["full"]}`')

            for i, match in enumerate(matches, start=1):
                log.info(f"{i}. -> {match.filename.relative_to(root)}")

        log.info("")


def write_corrected_url(
    md=None,
    problems=None,
    root=None,
    dry_run=False,
):
    """

    # Parameters

    md:MarkdownDocument
        - The document we need to correct the URLs

    problems:list(dict, list)
        - dict - this is the same dict that was in the broken_urls list
        - list - the list of Path objects that match or are similar

    root:Path
        - The path to the root of the document folder

    """

    log.info(f"File: {md.filename.relative_to(root)}")

    for defect, matches in problems:
        line, url = defect

        match = (
            matches[0].filename
            if isinstance(matches[0], MarkdownDocument)
            else matches[0]
        )  # assume pathlib.Path

        new_url = relative_path(
            md.filename.parent,
            match.parent,
        ).joinpath(match.name)

        left, _, _ = url["url"].partition("#")
        new_line = md.contents[line].replace(left, str(new_url))

        log.info(f"Line: {line} - Replacing `{left}` -> `{new_url}`")

        md.contents[line] = new_line

    if dry_run:
        log.info("------DRY-RUN------")

    else:
        with md.filename.open("w", encoding="utf-8") as fo:

            for line in md.contents:
                fo.write(line)

            log.info("Changes written...")


def display_and_fix_issues(results, root=None, dry_run=False):
    """ """

    messages = {
        "no_matches": [
            "NO MATCHES",
            "The following files had no matches or any close matches within the system.",
        ],
        "suggestions": [
            "SUGGESTIONS",
            "The following files did not have any exact matches within the system but they had some close matches.",
        ],
        "exact_matches": [
            "EXACT MATCHES",
            "The following files have multiple exact matches within the system.",
        ],
        "exact_match": [
            "EXACT MATCHES",
            "The following files have a single, exact match within the system.",
        ],
    }

    # Display the files that had problems we can't repair automatically
    for key in (k for k in messages.keys() if k != "exact_match"):

        if results[key]:

            log.info("-" * 6)
            for msg in messages[key]:
                log.info(msg)
            log.info("")

            display_classified_url(results[key], root=root)

    # Display and repair the files we can fix
    key = "exact_match"
    if results[key]:

        log.info("-" * 6)

        for msg in messages[key]:
            log.info(msg)

        log.info("")

        for item in results[key]:
            md, problems = item

            write_corrected_url(
                md,
                problems,
                root=root,
                dry_run=dry_run,
            )

            log.info("")

        if dry_run:

            log.info(f"Exact Matches - {len(results[key])} files corrected!")
            log.info("-" * 6)


def find_missing_header_attributes(
    files=None,
    root=None,
    display_problems=False,
):
    """

    # Parameters

    files:list(MarkdownDocument)
        - The list of MarkdownDocument objects to search for missing header attributes

    root:Path
        - The path to the root of the document folder

    display_problems:bool
        - If true, it will display the problems as it finds them
        - Default - False

    # Return

    A dictionary keyed with the MarkdownDocument object that has missing attributes mapped
    to the list of missing attributes which are a tuple (line number, line text)

    """

    md_attribute_syntax_rule = MarkdownAttributeSyntax()

    problems = {}

    for md in files:

        # md.headers()
        # A dictionary keyed by header depth (1 to 6) with
        # a list of tuples containing line numbers containing the ATX header at that depth and
        # the text of the header
        # (23, "[hello World](./en.md) ")

        missing_attributes = []

        for _, headers in md.headers.items():

            for h in headers:

                number, text = h
                if not md_attribute_syntax_rule.match(text):
                    missing_attributes.append(h)

                    if display_problems:
                        log.info(
                            f"MISSING ATTRIBUTE: `{md.filename.relative_to(root)}` - Line: {number} - `{text}`"
                        )

        if missing_attributes:
            problems[md] = missing_attributes

    return problems


def repair_header_issues(
    issues,
    root=None,
    dry_run=False,
):
    """
    # Parameters

    issues:dict
        - A dictionary keyed by the MarkdownDocument object with header issues. It is mapped
        to a list of tuples (line number, header text)

    root:Path
        - The path to the root of the document folder

    dry_run:bool
        - If true, it will not write changes
        - Default - False
    """

    for md, problems in issues.items():

        log.info(f"File: {md.filename.relative_to(root)}")

        # we'll hash the file name and path using SHA256 and use the first 10 hex characters.
        # we just need something to make the section header anchors unique if the document is
        # merged into a pdf - it honestly doesn't matter
        # - https://gnugat.github.io/2018/06/15/short-identifier.html
        # - https://preshing.com/20110504/hash-collision-probabilities/
        # - https://en.wikipedia.org/wiki/Birthday_attack#Mathematics

        # Using 10 characters, i.e. 10 hex numbers yields about 40 bits of the 256 bits
        # using the Birthday paradox approximation we can determine how many hashes we can
        # generate before there is a 50% chance of a collision:
        # 10 hex numbers is 10*4bits = 40bits
        # H = 2^40
        # p(n) = 50% = 0.5 = 1/2
        # n = sqrt(2 * 2^40 * 1/2) = sqrt(2^40) = 1,048,576
        # Essentially we would need to generate at least a million hashes before we expect
        # a collision with about a 50% probability.

        file_hash = (
            hashlib.sha256(str(md.filename).encode("utf-8")).hexdigest()[:10].lower()
        )

        # split the hash up into something easier to understand - `xxx-xxx-xxxx`
        file_id = f"{file_hash[:3]}-{file_hash[3:6]}-{file_hash[6:]}"

        for i, item in enumerate(problems):

            line, _ = item

            section_attribute = f"{{#sec:{file_id}_{i}}}"
            md.contents[line] = md.contents[line].rstrip() + " " + section_attribute

            log.info(f"Line: {line} - Added Section Attribute: `{md.contents[line]}`")

        log.info("")

    if dry_run:
        log.info("------DRY-RUN------")

    else:
        with md.filename.open("w", encoding="utf-8") as fo:

            for line in md.contents:
                fo.write(line)

            log.info("Changes written...")


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
    $ docs --config=./en/config.common.yaml repair links

    $ docs --config=./en/config.common.yaml repair --dry-run images
    $ docs --config=./en/config.common.yaml repair images

    $ docs --config=./en/config.common.yaml repair --dry-run headers --list
    $ docs --config=./en/config.common.yaml repair --dry-run headers
    $ docs --config=./en/config.common.yaml repair headers

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    config["dry_run"] = kwargs["dry_run"] if "dry_run" in kwargs else False

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for Markdown files...")

    config["md_files"] = md_search(root=config["documents.path"])

    log.info(f'{len(config["md_files"])} Markdown files were found...')
    log.info("")

    args[0].obj["cfg"] = config


@repair.command("links")
@click.pass_context
def links(*args, **kwargs):
    """

    Examine all of the Markdown documents in the configuration folder.
    Determine if there are relative links that have a problem and attempt
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

    results = {
        "no_matches": [],
        "suggestions": [],
        "exact_match": [],
        "exact_matches": [],
    }

    for md in config["md_files"]:
        sorted_broken_urls = classify_broken_urls(
            lookup=lookup,
            broken_urls=find_broken_urls(
                md.filename.parent,
                md.relative_links(),
            ),
        )

        for key in results:
            if sorted_broken_urls[key]:
                results[key].append((md, sorted_broken_urls[key]))

    display_and_fix_issues(
        results, root=config["documents.path"], dry_run=config["dry_run"]
    )

    log.info("")
    log.info("-" * 6)

    build_end_time = datetime.now()

    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")


@repair.command("images")
@click.pass_context
def images(*args, **kwargs):
    """

    Examine the MarkdownDocument objects for broken relative image links
    and attempt to repair them.

    # Usage

    $ docs --config=./en/config.common.yaml repair --dry-run images
    $ docs --config=./en/config.common.yaml repair images

    """
    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now()

    # --------
    # Find the images

    images = list(
        search(
            root=config["documents.path"],
            extensions=(".png", ".gif", ".jpg", ".jpeg"),
        )
    )

    log.info(f"{len(images)} images were found...")
    log.info("")

    # 1. create a reverse look for the image names to their file paths

    reverse_image_lookup = {}

    for img in images:
        reverse_image_lookup.setdefault(img.name, []).append(img)

    results = {
        "no_matches": [],
        "suggestions": [],
        "exact_match": [],
        "exact_matches": [],
    }

    for md in config["md_files"]:
        sorted_broken_urls = classify_broken_urls(
            lookup=reverse_image_lookup,
            broken_urls=find_broken_urls(
                md.filename.parent,
                md.image_links(),
            ),
        )

        for key in results:
            if sorted_broken_urls[key]:
                results[key].append((md, sorted_broken_urls[key]))

    display_and_fix_issues(
        results, root=config["documents.path"], dry_run=config["dry_run"]
    )

    # ----------
    log.info("")
    log.info("-" * 6)

    build_end_time = datetime.now()

    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")


@repair.command("headers")
@click.option(
    "--list",
    is_flag=True,
    help="List the problem files as they are encountered.",
)
@click.pass_context
def headers(*args, **kwargs):
    """

    Examine all the MarkdownDocument objects for ATX headers that do not
    have a proper section attribute set. It can automatically add a
    section attribute.

    # Usage

    $ docs --config=./en/config.common.yaml repair --dry-run headers --list
    $ docs --config=./en/config.common.yaml repair headers


    """
    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    build_start_time = datetime.now()
    # ----------

    log.info("Searching for missing header attributes...")
    log.info("")

    problems = find_missing_header_attributes(
        files=config["md_files"],
        root=config["documents.path"],
        display_problems=kwargs["list"],
    )

    if len(problems) > 0:
        log.info("-" * 6)
        log.info(
            f'{len(problems)}/{len(config["md_files"])} files have missing attributes.'
        )

    # -----------
    # Add missing header section attributes

    repair_header_issues(
        problems, root=config["documents.path"], dry_run=config["dry_run"]
    )

    # ----------
    log.info("")
    log.info("-" * 6)

    build_end_time = datetime.now()

    log.info(f"Started  - {build_start_time}")
    log.info(f"Finished - {build_end_time}")
    log.info(f"Elapsed:   {build_end_time - build_start_time}")
