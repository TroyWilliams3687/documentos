---
# YAML Metadata Block

# Variables that will populate the values in the template when constructing the document.
# A lot of variables will be common for the documents, and will be set in the 
# `templates/html.yaml` or `templates/pdf.yaml` file in the templates folder.

# These variables are document specific and will override more general variables that are
# set in the configuration file. They can be pretty much anything but should be kept to a minimum.
# It seems that a UUID can be quite useful, particularly for localization.

# Basic Variables
# ---------------

# title - The title of the document. In the majority of cases it will be the same as the 
# first markdown header. It can be anything that makes sense.
# date - The date the document was created. If required we can add date_modified or some 
# other variable to track those changes.
# version - comes in two flavors, a number for users and the regular number. In a general document system
# this isn't required, a date, date last modified and a UUID should be sufficient.

# Note
# ----

# It is possible to have other variables here that can override the global variables. An example could
# be the compile_date (the date the files were complied). If the document was updated later on (a correction)
# that compile_date can be set differently, on a per-file basis.

# This is also a sample block, the other document YAML blocks do not need this comment


# Variables
# ---------

UUID: 337942f8-b5bb-11eb-9fb7-a3fe2da49343

title: md_doc System
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
#  machine: 7.007.012.036

# version_modified:
#   date: 
#   user: 
#   machine: 
...

# md_doc System

First and foremost, the [md_doc](https://github.com/TroyWilliams3687/md_docs) library is a system of tools to help manage user documentation. Typically the documentation will be for software projects, but it can be for any type of documentation project. The other goal of this system is to handle language localizations efficiently. The idea is to provide a set of English (or other language, it doesn't matter) Markdown based files for translations. The translated Markdown files would be stored in a separate folder from the English files. When it comes time to build the system of documents it would be as simple as issuing the `build` command. The goal of the system is to provide a tool that can take a set of documentation along with its localizations (translations to other languages) and provide a seamless method to transform to other formats in a consistent and reproducible manor.

The system also makes use of [Pandoc](https://pandoc.org) to transform the Markdown files into HTML or PDF. Currently the system is target for those output formats. However, in the future it should be possible to target any of the output formats that Pandoc can provide.

On a Linux based system, after everything is installed you issue the following command to build the HTML files:

```bash
$ make html
```

To understand how to configure the Markdown documents folder you can take a look at the `en` folder in the [md_docs repository](https://github.com/TroyWilliams3687/md_docs/tree/master/en). It is a good starting point.

## Commands

For system commands see [commands](commands.md). 


## YAML Configuration files

This system makes use of YAMl configuration files to drive the process and make things simple. Samples can be found [here](./en/). The YAML files can be split up so that common parts can be shared among the different configurations. The configuration files are passed to the system in such a way that the most common is passed in first while the most specific is passed in last. Based on the configuration in the sample system ([`/en` in the repo](https://github.com/TroyWilliams3687/md_docs/tree/master/en)), we can see some examples:

```
$ build \
    --config=en/config.common.yaml \
    --config=en/config.html.yaml \
    html
```

```
$ build \
    --config=en/config.common.yaml \
    --config=en/config.html.yaml \
    --config=en/config.html.single.yaml \
    html --single
```

```
$ build \
    --config=en/config.common.yaml \
    --config=en/config.pdf.yaml \
    pdf
```

All of the above commands will transform the documentation to different forms. Yet they all share the same common base configuration. Why is this important? It means you don't have to make copies of the configuration file to accommodate a different build, particularly when it is very similar to an already existing build. This will come in very handy when building different localizations (languages) of your documentation.

>NOTE see [YAML Configuration file definitions](yaml_configuration.md) for more details on the configuration file format.

## Markdown

This system uses [Markdown](https://daringfireball.net/projects/markdown/), specifically [Pandoc Flavour](https://pandoc.org/MANUAL.html#pandocs-markdown). The Pandoc flavor of Markdown extends the syntax and adds some nice features that Pandoc itself can handle properly. In addition to Pandoc, the system can make use of Pandoc filters, specifically , [pandoc-xnos](https://github.com/tomduck/pandoc-xnos) filters. This is optional and you can setup your own filters as you see fit. 

>NOTE: You can use other filters as you see fit. Modify the [Pandoc YAML configuration files](en/templates) and include the correct syntax within your Markdown. 

At the most basic an individual Markdown will will contain a [YAML metadata block](https://pandoc.org/MANUAL.html#extension-yaml_metadata_block) and the actual Markdown syntax. Typically, we should have an `UUID` field which is a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) and ensures that the same piece of information can be found despite many different localizations.

### YAML Metadata Block

Variables that will populate the values in the template when constructing the document. A lot of variables will be common for the documents, and will be set in the `templates/html.yaml` or `templates/pdf.yaml` file in the templates folder.

These variables are document specific and will override more general variables that are set in the configuration file. They can be pretty much anything but should be kept to a minimum. It seems that a UUID can be quite useful, particularly for localization.

#### Basic Variables

The YAML block is not mandatory and therefore optional. Not including one will use the default defined in the Pandoc configuration file that is provided to the Pandoc command during the build process. I would suggest the most basic information such as:

- ID - UUID unique to each document in the system.
- title - The title of the document. Very often this is identical to the first section header in the Markdown.
- language - The ISO 2 digit language identifier for the document. This is used when transforming to HTML.

- version_created - This section contains the date that the document was created
    - date - The date the document was created
    - user - A specific user friendly version number, for example 2021.1. 

>NOTE: It is possible to have other variables here that can override the global variables. An example could be the compile_date (the date the files were complied). If the document was updated later on (a correction) that compile_date can be set differently, on a per-file basis. 

>NOTE: It is possible to add any sort of variable you want to the metadata block. Make sure it is valid [YAML](https://yaml.org/). The variables do not have to relate to Pandoc but can be recognized by other scripts that do some post-processing.


YAML Metadata Block:

```

UUID: 337942f8-b5bb-11eb-9fb7-a3fe2da49343

title: md_doc System
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
  machine: 7.007.012.036

# version_modified:
#   date: 
#   user: 
#   machine: 
...

```

## LST files

A key piece to a documentation system is grouping documents together forming logical sets. This is accomplished by the `LST` files. These are simple text files that describes the Markdown files and the order they should appear. 

A build process can only have a reference to one `LST` file for any particular process. That in no way should mean that you can have only one `LST` file in the system. In fact, you should have many files at different nested depths to simply things. 

When the `LST` file is loaded for processing, if any `LST` files are specified in the list, they are input, recursively, and their Markdown files are added.

Basic `LST` file, `site.lst`:

```
# This is a comment and will be ignored
# each line is the path to markdown file
# The path is relative to the location of this .lst file
# Each file will be merged, in order, forming one large file
# You can add other .lst files and they will be read
# .lst files can be located anywhere in the document structure

# NOTE: The path is relative to the location of this .lst file

# Simply add the Markdown file names to this document. They should be relative
# to the repository root.

repo_setup.md
python.md
pandoc.md
ch0_0_preamble.md
ch0_1_images.md
ch0_2_equations.md
ch0_3_tables.md
ch0_4_sections.md

# It is possible to have nested documents. You are free to add the links to the
# Markdown files directly or have reference nested LST files like:

# mining/mining.lst
# models/models.lst
# geometry/geometry.lst

# Using nested LST files will simplify things quite a lot and allow you to choose what
# sections of your documentation to build.

```

>NOTE: The paths within an `LST` file are relative to the location of the `LST` file.

>NOTE: If you have a highly nested folder structure it is best to create `LST` files at the root of the folders and use those to group the Markdown documents in to logical sets. The logical sets can be combined into more complex document structures.

>NOTE: It is possible to build partial document transformations by selecting nested `LST` files. This means that if you have part of a document called "Instructions", it is possible to build the full document as a PDF and build an other document called "Instructions" containing only the sub-set of documents that make up the instructions.


## Document Structure

The Markdown document structure can be as simple or complex as is requred. At its most basic, the documents, assets (images, videos, data files, etc.), templates, css and configuration files should be stored within a language folder (I typically use a 2-digit ISO code).

Basic English structure:

- en
- en/css
- en/templates
- en/documents/
- en/documents/assets

Basic Spanish structure:

- es
- es/css
- es/templates
- es/documents/
- es/documents/assets


>NOTE: When handling different localizations, it is best of the folder structure of all the languages be identical.

