#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 63ee7a34-bb3d-11eb-8e16-a1c71b5bec55
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-22
# -----------

"""
Just a hold for methods and functions I made at an other time.

I used Vulture on the code base to identify methods that were dead. I
pruned quite a few, but there are some that I am not 100% sure - they
live here
"""

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


    # def find_highlight_themes(path):
#     """
#     Takes a path to a folder containing syntax highlighting themes (json
#     files named .theme that pandoc understands).

#     # Parameters

#     path:pathlib.Path
#         - The path of the folder to search for themes.

#     # Return

#     A dictionary keyed by file name i.e. 'pygements.theme'

#     """

#     themes = {}

#     for theme in path.glob("**/*.theme"):
#         themes[theme.name.lower()] = theme

#     return themes

# def create_md_link_lookup(md_file_contents, document_root):
#     """

#     Takes the contents of the markdown files, extracts the relative links
#     and constructs a dictionary of the markdown file and the relative links
#     it contains.

#     # Parameters

#     md_file_contents:dict
#         - A dictionary keyed by the markdown file containing a list of strings
#         representing the contents of the markdown file
#         - The paths to the markdown files are relative of the root of the document
#         folder i.e. document_root

#     document_root:Path
#         - The path to the root of the document folder.

#     # Return

#     A dictionary keyed by the relative markdown url linked to list of MDLinks objects.

#     """

#     links = {}

#     for k, contents in md_file_contents.items():

#         relative_links = extract_relative_links(contents)

#         if relative_links:

#             for rl in relative_links:

#                 line, url, section, full = rl

#                 links.setdefault(k, []).append(MDLink(line, url, section, full))

#         else:

#             # the document contains no links, add an empty list so that it can be accessed.

#             links[k] = []

#     return links

# def create_lst_link_lookup(lst_file_contents, document_root):
#     """

#     Takes the contents of the lst files, extracts the relative links
#     and constructs a dictionary showing what files the lst links too.

#     It resolves the lst files to links so that the only thing stored are
#     links to markdown files, that are relative to the list file

#     # Parameters

#     lst_file_contents:dict
#         - A dictionary keyed by the lst file containing a list of strings
#         representing the contents of the contents of the file
#         - The paths to the lst files are relative of the root of the document
#         folder i.e. document_root

#     document_root:Path
#         - The path to the root of the document folder.

#     # Return

#     A dictionary keyed by the link and pointing to a list MDlink.

#     # NOTE

#     The LST is a very simple format, it contains comments, empty lines and links
#     on single lines. Ignore empty lines and comments.

#     """

#     links = {}

#     for k, contents in lst_file_contents.items():

#         document_links = []

#         for i, line in enumerate(contents):

#             row = line.strip().partition("#")

#             # Is the line commented or empty?
#             if len(row[0]) == 0:
#                 continue

#             # Build the url fully resolved to a file
#             url = (
#                 document_root.joinpath(k)
#                 .parent.joinpath(row[0])
#                 .resolve()
#                 .relative_to(document_root)
#             )

#             mdl = MDLink(i, url, None, url)

#             links.setdefault(k, []).append(mdl)

#     return links


# def create_md_reverse_link_lookup(md_file_contents, document_root):
#     """

#     Takes the contents of the markdown files, extracts the relative links
#     and constructs a reverse dictionary showing what files contain the same
#     relative link to an existing markdown file.

#     # Parameters

#     md_file_contents:dict
#         - A dictionary keyed by the markdown file containing a list of strings
#         representing the contents of the markdown file
#         - The paths to the markdown files are relative of the root of the document
#         folder i.e. document_root

#     document_root:Path
#         - The path to the root of the document folder.

#     # Return

#     A dictionary keyed by the relative markdown link url linked to a dictionary.

#     The value portion is a dictionary containing keys:
#     - 'original file' - This is the path to the markdown file that contained the link
#     - 'link' - A namedtuple containing information about the link, values are:
#         - line - The line number in the markdown file where it was found
#         - link - The url portion of the link
#         - section - The section portion of the link
#         - full - The full markdown formatted link

#     """

#     # The links dictionary is keyed by the relative url found in the document. The relative url is transformed so it
#     # is relative to the document root so we can link all documents that point to the same link (even if it is
#     # of different forms))
#     links = {}

#     for k, contents in md_file_contents.items():

#         relative_links = extract_relative_links(contents)

#         for rl in relative_links:

#             line, url, section, full = rl

#             mdl = MDLink(line, url, section, full)

#             # Rebuild the url so it is relative to the document folder. This will allow use to know if multiple
#             # documents point to the same file, even if the relative path is different. This also allows us to
#             # handle files with the same name but different paths

#             url = (
#                 document_root.joinpath(k)
#                 .parent.joinpath(url)
#                 .resolve()
#                 .relative_to(document_root)
#             )

#             # Store the original document path and the relative link information
#             links.setdefault(url, []).append({"original file": k, "link": mdl})

#     return links


# def create_lst_reverse_link_lookup(lst_file_contents, document_root):
#     """

#     Takes the contents of the lst files, extracts the relative links
#     and constructs a reverse dictionary showing what files contain the same
#     relative link to an existing markdown file.

#     # Parameters

#     lst_file_contents:dict
#         - A dictionary keyed by the lst file containing a list of strings
#         representing the contents of the contents of the file
#         - The paths to the lst files are relative of the root of the document
#         folder i.e. document_root

#     document_root:Path
#         - The path to the root of the document folder.

#     # Return

#     A dictionary keyed by the link and pointing to a list of dictionaries that contain the link.

#     # NOTE

#     The LST is a very simple format, it contains comments, empty lines and links
#     on single lines. Ignore empty lines and comments.

#     """

#     links = {}

#     for k, contents in lst_file_contents.items():

#         document_links = []

#         for i, line in enumerate(contents):

#             row = line.strip().partition("#")

#             # Is the line commented or empty?
#             if len(row[0]) == 0:
#                 continue

#             # construct the url so that it is relative to the root of the document folder
#             url = (
#                 document_root.joinpath(k)
#                 .parent.joinpath(row[0])
#                 .resolve()
#                 .relative_to(document_root)
#             )

#             mdl = MDLink(i, row[0], None, row[0])

#             links.setdefault(url, []).append({"original file": k, "link": mdl})

#     return links

# # A simple data structure to hold the link information
# MDLink = namedtuple(
#     "MDLink",
#     [
#         "line",  # line number in the md file the link is located on
#         "link",  # The relative markdown link
#         "section",  # Section anchor if any
#         "full",
#     ],
# )

def extract_relative_links(md_contents):
#     """
#     Read the contents of the markdown file and find all of the links.

#     # Parameters

#     md_contents:list(str)
#         - The contents of the markdown file

#     # Return

#     a list containing tuples. The tuple contains the line number, the relative link and the full match

#     """

#     links = []

#     md_link_rule = MarkdownLinkRule()
#     relative_url_rule = RelativeMarkdownURLRule()

#     code_fence_rule = CodeFenceClassifier()
#     in_code_fence = False

#     for i, line in enumerate(md_contents):

#         # Do we have the start or end of a code fence block?
#         if code_fence_rule.match(line):
#             in_code_fence = not in_code_fence

#         # Are we in a code fence?
#         if in_code_fence:
#             continue

#         # Contains a valid markdown link?
#         if md_link_rule.match(line.strip()):

#             results = md_link_rule.extract_data(line.strip())

#             # links.update(r['link'] for r in results)

#             # can be multiple links in the line...
#             for r in results:

#                 url = r[
#                     "link"
#                 ]  # full, text and link are the variables in the results dictionary...

#                 # Is relative URL?
#                 if relative_url_rule.match(url):

#                     results = relative_url_rule.extract_data(
#                         url
#                     )  # `md` and `section` are the keys we are interested in

#                     links.append((i, results["md"], results["section"], r["full"]))

#     return links




