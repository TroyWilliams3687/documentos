# def create_toc(files=None, root=None, **kwargs):
#     """
#     Given a list of markdown files generate a list of strings that can be
#     written to a markdown file creating a table of contents. It will iterate
#     through each file searching for ATX headers. It will then determine

#     # Parameters

#     files:list(pathlib.Path)
#         - The list of markdown files to copy and adjust to a temporary folder.

#     root:pathlib.Path
#         - The common root of the files. It is assumed they will be under a common root
#         folder and we can use it to derive relative paths for intra-document links.

#     # Return

#     A list of strings containing a markdown link pointing to the document and section.
#     It will be a bulleted list indented by the column header count.

#     # Note

#     - The table of contents will be ordered by the list containing the files.

#     - The bullet needs to be indented by 2 spaces to be detected as nested lists.

#     """

#     toc = []

#     for md in files:

#         with md.open("r", encoding="utf-8") as fin:

#             file_toc = create_file_toc(lines=fin.readlines(),
#                                        path=md.relative_to(root))

#             if file_toc:
#                 toc.extend(file_toc)

#     return toc


# def construct_md_list(
#     start_lst=None,
#     list_file_contents=None,
#     combined=None,
# ):
#     """
#     Takes a .lst file and constructs a list of .md files that are associated with it.
#     It works recursively on nested .lst files contained within it.

#     # Parameters
#     start_lst:str
#         - The dictionary key for the list file that we want to construct

#     list_file_contents:dict[str:pathlib.Path]
#         - a dictionary containing .lst files and their contents. start_lst should
#         be a member of the dictionary

#     combined:list[pathlib.Path]
#         - A list of md file paths stored in the .lst files and nested .lst files.

#     # Returns

#     A list of md file paths stored in the .lst files and nested .lst files.

#     """

#     if not combined:
#         combined = []

#     for f in list_file_contents[str(start_lst)]:

#         if f.suffix == ".md":
#             combined.append(f)

#         if f.suffix == ".lst":
#             combined.extend(
#                 construct_md_list(
#                     start_lst=f,
#                     lst_files=lst_files,
#                     combined=combined,
#                 )
#             )

#     return combined


# def create_file_cache(root=None, extensions=(".md", ".lst")):
#     """

#     Recursively search from root folder for all files that match the extensions.
#     It will return a tuple of dictionaries (matching the order of the extensions tuple).
#     The dictionaries will be keyed by the file name and path (relative to the root folder)
#     and the values associated with the key will be a list of strings representing the contents
#     of the file.

#     The idea is to use the caches instead of reading the file multiple times during the processing.

#     root:pathlib.Path
#         - The path to the root of the document folder. All paths well be made relative to
#         this path.

#     extensions:tuple(str)
#         - The extensions we are looking to create a cache for.
#         - default: ('.md', '.lst')

#     # Return

#     A dictionary containing dictionaries representing the files that match the extension. The
#     key will be the extension from the extensions tuple.

#     # NOTE

#     All keys, i.e. file links are relative to the root folder.

#     """

#     caches = {}

#     for f in root.rglob("*.*"):

#         if f.suffix in extensions:

#             key = f.relative_to(root)

#             with f.open("r", encoding="utf-8") as fin:
#                 contents = fin.readlines()

#             caches.setdefault(f.suffix, {})[str(key)] = contents

#     return caches


# def create_caches(root=None):
#     """
#     Recursively search the root folder for all .lst and .md files. It will
#     construct two caches. One cache will hold the .lst files
#     and their contents. The other will hold the .md file and their contents.

#     The idea is to use the caches instead of reading the file multiple times
#     during the processing.

#     # Parameters

#     root:pathlib.Path
#         - The path to the root of the document folder. All paths well be made relative to
#         this path.

#     # Return

#     a tuple containing the lst file contents and the md file contents.
#     """

#     list_file_contents = {}
#     md_file_contents = {}

#     for f in root.rglob("*.*"):

#         if f.suffix == ".md":

#             key = f.relative_to(root)

#             with f.open("r", encoding="utf-8") as fin:
#                 contents = fin.readlines()

#             md_file_contents[str(key)] = contents

#         elif f.suffix == ".lst":
#             key = f.relative_to(root)
#             content = read_lst(f)

#             list_file_contents[str(key)] = [p.relative_to(root) for p in content]

#     return list_file_contents, md_file_contents


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

#     if assets is None:
#         log.debug("assets = None - skipping image link check")

#         return line

#     if output is None:
#         log.debug("output = None - skipping image link check")

#         return line

#     for r in extract_relative_markdown_image_links(line):

#         if r["caption"] is None:
#             log.warning(f"Warning - Image Missing Caption -> {md_file.name} -> {line}")

#         # we need to determine if it is the path to the assets folder
#         im_path = md_file.parent.joinpath(r["image"]).resolve()

#         if im_path.exists():

#             log.debug(f"md file: {md_file}")
#             log.debug(f'Image Path: {r["image"]}')
#             log.debug(f"Image Location: {im_path}")
#             log.debug(f"Asset Path: {assets}")
#             log.debug(f"Output Path: {output}")

#             # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
#             if assets in im_path.parents:

#                 # basically flatten the path.
#                 new_path = Path("./assets").joinpath(im_path.name)
#                 log.debug(f"New image path -> ./{new_path}")

#                 line = line.replace(r["image"], f"./{new_path}")

#         else:
#             # What happens if the image doesn't exist, but is an asset
#             log.warning(
#                 f"WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}"
#             )

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
#         log.debug("assets = None - skipping image link check")

#         return line

#     if output is None:
#         log.debug("output = None - skipping image link check")

#         return line

#     rule = HTMLImageRule()

#     # Contains a valid HTML img link?
#     if rule.match(line.strip()):

#         results = rule.extract_data(line.strip())

#         for r in results:

#             if r["src"] is None:
#                 log.warning(
#                     f"Warning - HTML Image Missing SRC -> {md_file.name} -> {line}"
#                 )

#             # we need to determine if it is the path to the assets folder
#             im_path = md_file.parent.joinpath(r["src"]).resolve()

#             if im_path.exists():

#                 log.debug(f"md file: {md_file}")
#                 log.debug(f'Image Path: {r["src"]}')
#                 log.debug(f"Image Location: {im_path}")
#                 log.debug(f"Asset Path: {assets}")
#                 log.debug(f"Output Path: {output}")

#                 # the file exists locally, is it in the asset folder? https://stackoverflow.com/a/34236245
#                 if assets in im_path.parents:

#                     # basically flatten the path.
#                     new_path = Path("./assets").joinpath(im_path.name)
#                     log.debug(f"New HTML image path -> ./{new_path}")

#                     line = line.replace(r["src"], f"./{new_path}")
#             else:
#                 # What happens if the image doesn't exist, but is an asset
#                 log.warning(
#                     f"WARNING - Image does not exist: {im_path} -> {md_file.name} -> {line}"
#                 )

#     return line


# def adjust_markdown_contents(md_file=None, contents=None):
#     """
#     Examine the *.md file contents for inter-document links pointing
#     to other .md files. It will rename the .md to .html. Pandoc will
#     not alter the links during the transformation. If we want them to
#     point to the correct location, we have to alter them.

#     # Parameters

#      md_files:list(pathlib.Path)
#         - The list of files that we are interested in generated a table
#         of contents for

#     contents:list(str)
#         - The list of strings representing the contents of the .md file.

#     # Returns

#     A list of strings representing the adjusted .md contents.

#     """

#     adjusted_contents = []

#     for line in contents:
#         adjusted_contents.append(
#             adjust_markdown_links(line, md_file, replace_md_extension=True)
#         )

#     return adjusted_contents
