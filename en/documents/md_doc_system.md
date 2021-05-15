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

ID: 337942f8-b5bb-11eb-9fb7-a3fe2da49343

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

The md_doc system is a way to take a series of [Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) files that can be nested or not and transforms them to HTML or PDF documents. The goal of the system is to provide a tool that can take a set of documentation along with its localizations (translations to other languages) and provide a seamless method to transform to other formats in a consistent and reproducible manor.


