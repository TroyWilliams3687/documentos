#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = e0965926-2f49-11eb-a7cb-60f262a5770a
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-11-25
# -----------

"""

This module will house the components to take a list of markdown files and merge them
into one. This script is not intended to be used as a standalone script. The intention
is for the methods to be imported into other scripts and used from there to accomplish
document creation tasks.

It should start with a single .lst file.

The main operation of these methods is via a *.lst file. The .lst file contains
references to the markdown files in the order to be merged. It can contain comments and
relative paths to files. Think of a .lst file like the table of contents describing how
the various bits of information are ordered to form a coherent document. It can also include
other .lst files. Ideally these methods should work from one, and only one .lst file at the
top of the hierarchy.

Here is an example .lst file:

```
# This is a comment and will be ignored
# each line is the path to markdown file
# The path is relative to the location of the .lst file
# Each file will be merged, in order, forming one large file
# You can add other .lst files and they will be read
# .lst files can be located anywhere in the document structure

# NOTE: The path is relative to the location of the .lst file
./documents/index.md
./documents/ch0_0_preamble.md
./documents/ch0_1_images.md
./documents/ch0_2_equations.md

# You can include other .lst files within the list
./documents/test.lst
```

The methods in this module are designed to work with the standard python logging system.
Some information is relegated to debug, but most is set for the info level.

"""

# System Modules
import re
import logging
from pathlib import Path

# Custom Modules
from .markdown_classifiers import (
    MarkdownLinkRule,
    AbsoluteURLRule,
    RelativeMarkdownURLRule,
    MarkdownImageRule,
    HTMLImageRule,
)
from .markdown import adjust_markdown_links, adjust_image_links, adjust_html_image_links
from .common import read_lst

# Module level logging
log = logging.getLogger(__name__)

# def adjust_markdown_links(line, md_file, **kwargs):
#     """

#     Given a line, check to see if it contains a markdown link. If it contains
#     a markdown link we need to check for intra document links and remove them.

#     A markdown link is of the form: [text](url)

#     1. Does the line contain a markdown link?
#     2. Is the url portion absolute (http://www.iring.ca)?
#     3. Is the url relative (../file.md#section_title)?

#     - If it is not a markdown link the line is returned unaltered.
#     - If the url is absolute, the line is returned unaltered.
#     - If the url is relative, the markdown file is removed
#     - if the url is relative and doesn't contain a section id an exception is raised.
#         - The user obviously wants to link to the beginning of the document.
#         This should be allowed for the cases where the individual markdown will
#         be compiled to standalone html. However, since this is a
#         compressed/merged format this doesn't make sense. We could read the
#         document and figure it out, but we don't want to. It should be explicit
#         if we are compressing/merging the document into one compressed format.

#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     md_file:pathlib.Path
#         - The full path to the markdown file that the line is from.

#     # Return

#     The line object with modifications to any markdown links as required.

#     # Note

#     The line classifier rules perform memoization and should be instantiated above
#     the loop that calls this method. I don't expect many duplicate lines so this
#     optimization is not necessary. Mostly it is about the match and the extract
#     data

#     """

#     # log.debug(f'adjust_markdown_links({line}, {md_file})')

#     md_link_rule = MarkdownLinkRule()

#      # Contains a valid markdown link?
#     if md_link_rule.match(line.strip()):

#         absolute_url_rule = AbsoluteURLRule()
#         relative_md_url_rule = RelativeMarkdownURLRule()

#         results = md_link_rule.extract_data(line.strip())

#         # can be multiple links in the line...
#         for r in results:

#             url = r['link']

#             # Is absolute url?
#             if absolute_url_rule.match(url):
#                 pass # we can ignore this

#             # Is relative reference to a markdown file?
#             elif relative_md_url_rule.match(url):
#                 results = relative_md_url_rule.extract_data(url)

#                 if results['md']:
#                     # we have a relative path to the markdown file, we need to remove it from the line.

#                     if results['section'] is None:
#                         # if there is no section name, this is a problem. They will have to specify the section to link too
#                         raise ValueError(f'ERROR - Missing Section Link - {md_file.name} - "{line}" <- contains a relative link to a markdown file without a section reference "#section_name". A section id needs to be present!')

#                     log.debug(f'Removing relative file name from: "{line}"  ')
#                     line = line.replace(results['md'], '')

#             else:

#                 log.debug(f'Warning - Unrecognized link -> {md_file.name} - "{line}"')

#     return line


# def adjust_image_links(line, md_file, assets=None, output=None, **kwargs):
#     """
#     Given a line check to see if it contains a markdown image links. We
#     need to see if it points to the common 'assets' folder.

#     WE ASSUME THAT THE LINKS WE ARE INTERESTED IN ARE iN the 'assets'
#     FOLDER (see assumptions).

#     ![image caption](URL)

#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     md_file:pathlib.Path
#         - The full path to the markdown file that the line is from. It will be
#         used to determine the relative path so that we can adapt the link properly.

#     assets:pathlib.Path
#         - The full path to the assets folder. The common folder where we are storing
#         the images.

#     output:pathlib.Path
#         - The path to the output folder.

#     # Assumptions

#     We assume that all images that we use in the markdown files will be stored in the
#     assets folder (a folder called 'assets'). This is hard-coded. We can modify it later if
#     we need to but I want to keep this simple. We can have nested folders underneath the assets
#     folder.

#     We are under the assumption that the merged markdown document will be stored in a folder
#     that is at the same level as the assets folder i.e.:

#     - assets
#     - documents/merged.md

#     This means that all we have to do is modify the path to point to it i.e. ../../../assets/designer/image.png
#     becomes ./assets/designer/image.png

#     We are only interested in images that are stored in the 'assets' path and exist locally. Anything else will not touched.

#     # Return

#     If the line contains image links that are pointing to files in the assets folder a line string will
#     be return that contains modifications to the path to the assets folder.
#     """

#     # log.debug(f'adjust_image_links({line}, {md_file}, {assets}, {output}')

#     if assets is None:
#         log.debug('assets = None - skipping image link check')

#         return line

#     if output is None:
#         log.debug('output = None - skipping image link check')

#         return line

#     rule = MarkdownImageRule()

#     # Contains a valid markdown link?
#     if rule.match(line.strip()):

#         results = rule.extract_data(line.strip())

#         for r in results:

#             if r['caption'] is None:
#                 log.warning(f'Warning - Image Missing Caption -> {md_file.name} -> {line}')

#             # we need to determine if it is the path to the assets folder
#             im_path = md_file.parent.joinpath(r['image']).resolve()

#             if im_path.exists():

#                 log.debug(f'md file: {md_file}')
#                 log.debug(f'Image Path: {r["image"]}')
#                 log.debug(f'Image Location: {im_path}')
#                 log.debug(f'Asset Path: {assets}')
#                 log.debug(f'Output Path: {output}')

#                 # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
#                 if assets in im_path.parents:

#                     # basically flatten the path.
#                     new_path = Path('./assets').joinpath(im_path.name)
#                     log.debug(f'New image path -> ./{new_path}')

#                     line = line.replace(r["image"], f'./{new_path}')

#             else:
#                 # What happens if the image doesn't exist, but is an asset
#                 log.warning(f'WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}')

#     return line


# def adjust_html_image_links(line, md_file, assets=None, output=None, **kwargs):
#     """
#     Given a line check to see if it contains an HTML image links. We
#     need to see if it points to the common 'assets' folder.

#     WE ASSUME THAT THE LINKS WE ARE INTERESTED IN ARE IN the 'assets'
#     FOLDER (see assumptions).

#     <img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>

#     # Parameters

#     line:str
#         - The text string to analyze for markdown links

#     md_file:pathlib.Path
#         - The full path to the markdown file that the line is from. It will be
#         used to determine the relative path so that we can adapt the link properly.

#     assets:pathlib.Path
#         - The full path to the assets folder. The common folder where we are storing
#         the images.

#     output:pathlib.Path
#         - The path to the output folder.

#     # Assumptions

#     We assume that all images that we use in the markdown files will be stored in the
#     assets folder (a folder called 'assets'). This is hard-coded. We can modify it later if
#     we need to but I want to keep this simple. We can have nested folders underneath the assets
#     folder.

#     We are under the assumption that the merged markdown document will be stored in a folder
#     that is at the same level as the assets folder i.e.:

#     - assets
#     - documents/merged.md

#     This means that all we have to do is modify the path to point to it i.e. ../../../assets/designer/image.png
#     becomes ./assets/designer/image.png

#     We are only interested in images that are stored in the 'assets' path and exist locally. Anything else will not touched.

#     # Return

#     If the line contains image links that are pointing to files in the assets folder a string will
#     be returned that contains modifications to the path to the assets folder.
#     """

#     if assets is None:
#         log.debug('assets = None - skipping image link check')

#         return line

#     if output is None:
#         log.debug('output = None - skipping image link check')

#         return line

#     rule = HTMLImageRule()

#     # Contains a valid HTML img link?
#     if rule.match(line.strip()):

#         results = rule.extract_data(line.strip())

#         for r in results:

#             if r['src'] is None:
#                 log.warning(f'Warning - HTML Image Missing SRC -> {md_file.name} -> {line}')

#             # we need to determine if it is the path to the assets folder
#             im_path = md_file.parent.joinpath(r['src']).resolve()

#             if im_path.exists():

#                 log.debug(f'md file: {md_file}')
#                 log.debug(f'Image Path: {r["src"]}')
#                 log.debug(f'Image Location: {im_path}')
#                 log.debug(f'Asset Path: {assets}')
#                 log.debug(f'Output Path: {output}')

#                 # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
#                 if assets in im_path.parents:

#                     # basically flatten the path.
#                     new_path = Path('./assets').joinpath(im_path.name)
#                     log.debug(f'New HTML image path -> ./{new_path}')

#                     line = line.replace(r["src"], f'./{new_path}')
#             else:
#                 # What happens if the image doesn't exist, but is an asset
#                 log.warning(f'WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}')

#     return line


def merge_documents(start=None, output_md=None, **kwargs):
    """
    This method will take the starting *.lst file and search for all of the documents (markdown *.md)
    it contains and finally merge them together in one large markdown file.

    # Parameters

    start:pathlib.Path
        - The .lst file used to describe the documents to merge together

    output_md:pathlib.Path
        - The output file to write the merged document too

    # Exceptions

    """

    # log.debug(f'merge_documents({start}, {output_md})')

    files = read_lst(start)

    with output_md.open("w", encoding="utf-8") as fo:

        # md_link_rule = MarkdownLinkRule()
        # absolute_url_rule = AbsoluteURLRule()
        # relative_md_url_rule = RelativeMarkdownURLRule()

        for md in files:

            log.info(f"Merging {md.name}...")

            with md.open("r", encoding="utf-8") as f:

                lines = f.readlines()

                for line in lines:

                    line = adjust_markdown_links(
                        line, md, remove_relative_md_link=False, **kwargs
                    )
                    line = adjust_image_links(line, md, **kwargs)
                    line = adjust_html_image_links(line, md, **kwargs)

                    fo.write(line)

                # Add two lines as separators between sections - if there are two many adjust the documents to remove trailing lines
                fo.write("\n\n")

            log.debug(f"Closed {md.name}...")


# def test():
#     """
#     A simple test routine that demonstrates the usage of this module
#     """

#     root = Path(globals().get("__file__", "./_")).absolute().parent

#     assets = root.joinpath('../assets').resolve() # should already exists - NOTE: Can be a different name, just adjust here.

#     output = root.joinpath(Path("../output")).resolve()
#     output.mkdir(parents=True, exist_ok=True)

#     start = root.joinpath(Path("../single_html.lst")).resolve()

#     output_md = output.joinpath(Path("single_html.md")).resolve()

#     print("Merging Documents...")
#     merge_documents(start=start, output_md=output_md, assets=assets, output=output)

#     print("Completed....")


# if __name__ == "__main__":
#     # script was run from the cli, call the entry point
#     test()
