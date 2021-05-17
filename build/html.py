#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 0b854b5e-b4bf-11eb-833e-df61029d6284
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-14
# -----------

"""
This module handles the conversion of the markdown files to HTML.
"""

# ------------
# System Modules - Included with Python

import sys
import shutil
import tempfile
import logging

from zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

from multiprocessing import Pool

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules

from md_docs.common import (
    run_cmd,
    path_to_root,
    create_md_link_lookup,
    create_lst_link_lookup,
    find_lst_links,
)

from md_docs.markdown import (
    create_file_cache,
    create_table_of_contents,
    create_blog_toc,
    adjust_markdown_contents,
)

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------

def construct_pandoc_command(
    input_file=None,
    output_file=None,
    config=None,
):
    """
    Construct the required switches to run PANDOC.

    # Parameters

    config:dict
    - A dictionary containing the key paths of the system.

    # Return

    A list of CLI elements that will be used by subprocess.
    """

    # --------
    # Basic Commands

    pandoc = [
        "pandoc",
    ]

    # ---------
    # Relative Offset Calculation

    relative_offset = path_to_root(config["output.path"], output_file)

    # --------
    # Add YAML Data

    # Add the file containing the YAML data, defaults, metadata, etc. It
    # contains the majority of settings needed by pandoc for the transformation.

    config['templates.path'] = config['root'].joinpath(config["templates"]['path'])

    for p in config["templates"]['pandoc_config']:

        pandoc.extend(
            (
             "--defaults",
             str(config['templates.path'].joinpath(p).resolve()),
            )
        )

    # ----------
    # Variables

    pandoc.append(f"--variable=RELATIVE:{str(relative_offset)}")
    pandoc.append(
        f'--variable=build_date:{datetime.now().replace(tzinfo=ZoneInfo(config["default.tz"])).strftime("%Y-%m-%dT%H%M%z")}'
    )

    # NOTE: Can add other things here like Aegis Version Number and Release Date. These could be added to the html footer template.

    # --------
    # Add Metadata

    # pandoc.extend(('--metadata', f"title={input_file.stem.title()}")) # use the name of the file as the title of the document
    # pandoc.extend(('--metadata', 'keywords=test, other, things'))

    # --------
    # Add Filters

    # this filter will promote the first header in the text file to the title of the html

    # pandoc.extend(('--lua-filter', str(config['root'].joinpath("./scripts/promote-headers.lua").resolve())))

    # --------
    # Add Syntax Highlighting

    # if config['syntax-highlight.themes']:
    #     pandoc.append(f"--highlight-style={str(config['syntax-highlight.themes']['breezedark.theme'])}")

    # --------
    # Add CSS

    # The css files will be at the root of the folder. Adjust the relative path to the correct location.

    if 'css_files' in config['css'] and config['css']['css_files']:
        pandoc.extend(
            [f"--css={path_to_root(config['output.path'], output_file).joinpath(p)}" for p in config['css']["css_files"]]
        )

    for key, switch in [
        ('include_in_header', '--include-in-header'),
        ('include_before_body', '--include-before-body'),
        ('include_after_body', '--include-after-body'),
    ]:
        if key in config['templates'] and config['templates'][key]:
            pandoc.extend(
            [f"{switch}={str(config['templates.path'].joinpath(f))}" for f in config['templates'][key]]
        )

    # --------
    # HTML Template Option

    # https://pandoc.org/MANUAL.html#option--template

    if 'html_template' in config['templates']:
        pandoc.append(f"--template={str(config['templates.path'].joinpath(config['templates']['html_template']))}")

    # --------
    # Add Transformation Options

    pandoc.extend(("-o", output_file))  # Output file path
    pandoc.append(input_file)  # Input File path

    return pandoc


def proces_pandoc(job):
    """
    A simple method for the multiprocessing module to work with.
    """

    msg, cmd = job

    log.info(msg)

    run_cmd(cmd)


@click.command('html')
@click.option('--single',
              is_flag=True,
              help='Generate a single HTML file by combining all the markdown files.')
@click.pass_context
def html(*args, **kwargs):
    """

    Build HTML from the supplied markdown files

    # Usage

    $ build ./cfg/config.en.yaml html

    $ build ./english/config.yaml html

    """

    # Extract the configuration file from the click context
    config = args[0].obj['cfg']

    build_start_time = datetime.now().replace(tzinfo=ZoneInfo(config["default.tz"]))

    # ----------------
    # Find all of the markdown files and lst files

    log.info("Searching for markdown and LST files...")

    config['documents.path'] = config['root'].joinpath(config["documents"]['path'])

    caches = create_file_cache(root=config['documents.path'])

    config["lst_file_contents"] = caches[".lst"]
    config["md_file_contents"] = caches[".md"]

    # extract the relative links from the file contents

    log.info("Extracting relative links...")

    config["md_links"] = create_md_link_lookup(config["md_file_contents"], config["documents.path"])
    config["lst_links"] = create_lst_link_lookup(config["lst_file_contents"], config["documents.path"])

    # look at the lst file contents and resolve all lst files it contains recursively
    md_files = [l.link for l in find_lst_links(config["documents"]['lst'], config["lst_links"])]

    # ----------
    # Table of Contents (TOC)

    if 'tocs' in config["documents"] and config["documents"]['tocs']:

        for item in config["documents"]['tocs']:

            idx = item['lst']
            output_md = item['index']
            depth = item['depth']
            use_blog = item['blog'] if 'blog' in item else False

            # idx = models/models.lst
            p = Path(idx)

            log.info(f'Creating index for {p}')

            if not use_blog:

                contents = create_table_of_contents(
                    p,
                    config["lst_links"],
                    config["md_file_contents"],
                    document_root=config["documents.path"],
                    include_sections=True,
                    depth=depth,
                )

            else:

                contents = create_blog_toc(
                    lst=p,
                    lst_links=config["lst_links"],
                    md_file_contents=config["md_file_contents"],
                )

            # The output path for the TOC files is relative to the repo root
            # p = config["documents.path"].joinpath(output_md)
            p = Path(output_md)

            md_files.insert(0, p) # put them at the front so they are built first

            key = str(p)

            if key in config["md_file_contents"]:
                config["md_file_contents"][key].extend(contents)

            else:

                config["md_file_contents"][key] = contents

    # ----------
    # Adjust .md Links

    # Adjust the markdown links by changing any intra-document links from *.md to *.html.
    # We do this because Pandoc will not alter links.

    log.info(f"Adjusting markdown links...")
    for md in md_files:

        mds = str(md)

        if mds in config["md_file_contents"]:

            adjusted_contents = adjust_markdown_contents(
                md_file=md,
                contents=config["md_file_contents"][mds],
            )

            config["md_file_contents"][mds] = adjusted_contents

    # ----------
    # Merge

    if 'single' in kwargs and kwargs['single']:

        # we will end up with md_files containing one item and the
        # config["md_file_contents"] only having one entry. We do this
        # so nothing downstream in this method changes...

        single_md = 'single.md'
        single_contents = []

        for md in md_files:

            mds = str(md)

            if mds in config["md_file_contents"]:

                single_contents.extend(config["md_file_contents"][mds])

        md_files = [Path(single_md)]

        config["md_file_contents"] = {single_md:single_contents}

    # ----------
    # Copy Files to TMP

    with tempfile.TemporaryDirectory(dir=config["root"]) as tmp:

        config["tmp"] = Path(tmp)

        for md in md_files:

            mds = str(md)

            if mds in config["md_file_contents"]:

                tmp_md = config["tmp"].joinpath(md)
                tmp_md.parent.mkdir(parents=True, exist_ok=True)

                log.debug(f"Writing {tmp_md.name}...")

                with tmp_md.open("w", encoding="utf-8") as fo:

                    for line in config["md_file_contents"][mds]:
                        fo.write(line)

        # ----------
        # Transform Markdown to HTML

        config['output.path'] = config['root'].joinpath(config["output"])

        pandoc_cmds = []

        for md in md_files:

            of = config["output.path"].joinpath(md.parent).joinpath(f"{md.stem}.html")
            of.parent.mkdir(parents=True, exist_ok=True)

            msg = f"Pandoc - Transform {md} to {of.relative_to(config['output.path'])}"

            pandoc = construct_pandoc_command(
                input_file=config["tmp"].joinpath(md),
                output_file=of,
                config=config,
            )

            pandoc_cmds.append((msg, pandoc))

        # -----------
        # Multi-Processing

        # https://docs.python.org/3/library/multiprocessing.html

        # Use max cores - default
        with Pool(processes=None) as p:
            p.map(proces_pandoc, pandoc_cmds)

        log.info('Transformation to HTML complete...')

    # -------------
    # Copy CSS

    # Copy the selected css files to the root of the output folder. All files
    # that require it should have a relative path set to find it there.

    config['css.path'] = config['root'].joinpath(config['css']['path'])

    for css in config['css']["css_files"]:

        cssp = config['css.path'].joinpath(css)

        log.info(f"Copying {cssp.name}...")

        shutil.copy(cssp, config["output.path"].joinpath(cssp.name))

    # ----------
    # Copy Assets

    # Copy the assets folder recursively to the output folder maintaining the relative
    # structure.

    if 'assets' in config['documents'] and config['documents']['assets']:

        config['assets.path'] = config['documents.path'].joinpath(config['documents']['assets'])

        log.info(f"Copying {config['assets.path']}...")

        shutil.copytree(
            config["assets.path"],
            config["output.path"].joinpath(config["assets.path"].name),
            dirs_exist_ok=True,
        )

    build_end_time = datetime.now().replace(tzinfo=ZoneInfo(config['default.tz']))

    log.info('')
    log.info(f'Started  - {build_start_time}')
    log.info(f'Finished - {build_end_time}')
    log.info(f'Elapsed:   {build_end_time - build_start_time}')
