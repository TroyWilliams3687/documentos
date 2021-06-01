---
ID: 5104edbe-c2e9-11eb-9b1d-dbcf63dc8c1c

title: YAML Configuration Options
language: en

version_created:
  date: 2021-06-01
...

# YAML Configuration Options

The build system makes extensive use of YAML based configuration files. This allows the user to make changes to the build system without making code changes. The YAML files are very flexible and configurable. The configuration file can be placed anywhere within the git repository holding your documentation. This system is designed to handle localized documentation, it is best to store the YAML files grouped with your documentation under a language identifier:

- en
    - documents
    - templates
    - css
    - config.yaml

- es
    - documents
    - templates
    - css
    - config.yaml

>NOTE: The YAML file is case sensitive.
>NOTE: The YAML file is sensitive to indenting. 

Here is a sample YAML configuration file:

```yaml
# ----------
# Sample Configuration File

# 2021-06-01

# This file is used by the build system to direct and control how the files are
# processed. It is possible to split the contents of this configuration file
# into multiple YAML files. This allows you to reuse common parts without
# having to duplicate settings and introduce potential errors.


# NOTE: All paths should be relative to the repo root, i.e. the folder containing
# the .git folder.

# NOTE: You can use the `null` option for some of these variables.

# NOTE: Indentation and formatting is import. This document is case sensitive.

# ----------
# Documents

documents:
  path: "en/documents"
  assets: "assets"
  lst: "sites.lst"
  plugin_path: "plugins"
  tocs:
    - lst: sites.lst
      index: index.md
      depth: 6
      plugin: "TOC"
    - lst: f1/f2/m1.md
      index: f1/fd/index.md
      depth: 0
    - lst: t1/test.md
      index: t1/toc.md
      depth: 6
  ignore_toc:
    - 'f1/f2/m1.md'
    - 'f1/f2/m2.md'

# ----------
# Templates

templates:
  path: "en/templates"
  pandoc_config:
    - "common.pandoc.yaml"
    - "html.pandoc.yaml"
  html_template: "html.template.html"
  include_in_header:
    - "includes.partial.html"
  include_before_body:
    - "header.partial.html"
  include_after_body:
    - footer.partial.html

# ----------
# CSS

css:
  path: "en/css"
  css_files:
    - "tbw.css"
    - "tbw.syntax-highlight.css"

# ----------
# Output

output: "output/en/html"

# ----------
# Misc

# default timezone name to use for time calculations
default.tz: "America/Toronto"

```

>NOTE: You can also look at the md_docs repository sample folder.

>NOTE: Optional variables can be left out of the configuration file are set to `null`.

## Documents - Section

The `documents` section is a mandatory section within the configuration file. It describes various configuration options to allow the build process to operate correctly. It contains the following keywords

- `path`
    - MANDATORY
    - The path to the root folder where the documents are located.
    - It is relative to the root of the repository, that is, where the `.git` folder is located.

- `assets`
    - MANDATORY
    - The path to the assets (images, videos, etc.) folder.
    - The system assumes it is located underneath the documents folder i.e. `en/documents/assets`.

- `lst`
    - MANDATORY
    - The file used to define what Markdown content will be part of the final document(s).

- `plugin_path`
    - OPTIONAL
    - The path to the plugins folder where the user can add custom code for different areas of the build.
    - This field is not required and doesn't need to be present in the configuration file (or commented out). The system will assume that there are no custom plugins. 
    - You can also specify the value of this field as `null`.

## Tocs - Section

The `tocs` section, is an OPTIONAL section containing a list of files that we want to create table of content pages from. The toc consists of a list of dictionaries representing LST files that we want to create table of contents from. The files in the toc are defined by the following mandatory key words (they are mandatory only if the toc keyword is defined).

- `lst`
    - MANDATORY
    - The name and path of the LST file to use in the TOC process.
    - This is a relative path within the documents folder i.e. relative to the document path, the `path` keyword.

- `index`
    - MANDATORY
    - The name and path of the output file to produce that will contain the table of contents listing.
    - This is a relative path within the documents folder i.e. relative to the document path, the `path` keyword
    - Generally, it will be in the same folder as the LST file (`lst` keyword), but that isn't mandatory.

- `depth`
    - OPTIONAL
    - The depth of ATX headers to include in the TOC. It is a number from 0 to 6.
    - NOTE: depth = 0 means only include the file name.

- `plugin`
    - OPTIONAL
    - The name of the plugin to use to create the table of contents. A different plugin can be used for each LST file defined in the toc section.
    - Defaults to `TOC` which is a basic table of contents.

- `ignore_toc`
    - OPTIONAL
    - A list of files in the documents folder to ignore when creating a table of contents.
    - The path of each file should be relative to the documents folder, the `path` keyword.


## Templates - Section

The `templates` section is an OPTIONAL section that defines the various template options available for the system regarding template usage and configuration. If this section isn't defined within the YAML configuration file, the system will use Pandoc defaults.


- `path`
    - MANDATORY
    - The path to the root folder where the templates are located.
    - It is relative to the root of the repository, that is, where the `.git` folder is located.
    - Typically it should be located in the same parent folder as the documents as the templates will generally be in the same language as the documents.

- `pandoc_config`
    - MANDATORY
    - A list of YAML files to use to configure Pandoc.
    - The configuration will be passed directly to Pandoc.
    - Generally the configuration files are located within the templates folder. They can be nested in sub-folders.
    - NOTE: The order matters, variables will be replaced by files further on down in the list.
    - NOTE: The YAML files for the Pandoc configuration are the standard YAML files that Pandoc uses - nothing fancy.

- `html_template`
    - OPTIONAL
    - The path to the HTML template that can be used by Pandoc when transforming Markdown to HTML

- `include_in_header`
    - OPTIONAL
    - The path to the HTML template stub that can be used by Pandoc when transforming Markdown to HTML. It simply includes the items in the header of the HTML file. Anything that would go in the header can go in this file.
    - NOTE: If using the `html_template` option, it might be best to include any header content in the template directly.

- `include_before_body`
    - OPTIONAL
    - The path to the HTML template stub that can be used by Pandoc when transforming Markdown to HTML. It will insert the HTML stub directly after the body open tag.

- `include_after_body`
    - OPTIONAL
    - The path to the HTML template stub that can be used by Pandoc when transforming Markdown to HTML. It will insert the HTML stub directly before the body close tag.

## CSS - Section

The OPTIONAL `css` section is used to configure css related settings.

- `path`
    - MANDATORY
    - The path to the root folder where the css files are located.
    - It is relative to the root of the repository, that is, where the `.git` folder is located.
    - Typically it should be located in the same parent folder as the documents as the css may have elements in the same language as the documents. If there are no localizable elements within the css they may be located in another
    folder.

- `css_files`
    - OPTIONAL
    - A list of css files to include in the HTML output.


## Output - Section

The `output` value is a MANDATORY value and configures the output folder.

- `output`
    - MANDATORY
    - The path to the output folder where the transformed documents will be placed.
    - It is relative to the root of the repository, that is, where the `.git` folder is located.
    - NOTE: This path will be created automatically.
    - NOTE: It isn't mandatory to include a language in the path. That is meant for documentation that will be localized into a number of different languages.

## Misc - Section

The `default.tz` value is a MANDATORY value allowing you to control the timezone used for any date/time output.

- `default.tz`
    - MANDATORY
    - The timezone name that will be applied to various date/time calculations during the build process.
    - Any valid IANA timezone name is valid.
    - <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>