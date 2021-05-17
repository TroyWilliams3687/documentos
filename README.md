# md_doc

The md_doc system is a way to take a series of [Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) files that can be nested or not and transforms them to HTML or PDF documents. The goal of the system is to provide a tool that can take a set of documentation along with its localizations (translations to other languages) and provide a seamless method to transform to other formats in a consistent and reproducible manor.

It provides a common way to implement documentation in a text based format while retaining the power to transform the documentation to other formats. It makes use of YAML configuration files, and [Pandoc](https://pandoc.org/) and [Python](https://www.python.org) to transform Markdown formatted documents into any of the other formats provided by Pandoc. This system has a heavy focus on HTML transformations.

The goal is to provide a plain text mechanism with a very light markup for software documentation. The idea is to make the documentation so that it can live along side the source code in the repository. Changes in the source code that prompt documentation revisions can live side-by-side in the repository. In fact, it is entirely possible to institute a code-review process for documentation revisions and updates.

This tool includes a [sample](en/documents) documents folder that can help you understand how the system works. Simply [clone](#installation) the repo and issue the [`make html`](en/documents/md_doc_system.md#make) in the repo if you are using Linux.

```
$ make html
```

## Installation

Clone the git repo:

```
$ git clone git@github.com:TroyWilliams3687/md_docs.git
```

# Create the Virtual Environment

```
$ make
```

## Activating the Virtual Environment

### Windows

Activate the virtual environment that you want to install it too.

On Windows, using powershell:

```
$ .\.venv\Scripts\activate.ps1
```

### Linux

On Linux, for most causes you can simple using the `Makefile` to build the system. If you need to activate the virtual environment:


```bash
$ . .venv/bin/activate
```

## Pip install

Use [pip](https://pip.pypa.io/en/stable/) to add the repository manually to the virtual environment where you want to use the tools.

```
$ pip install -e ~/path/to/repo/
```

## Usage


```python

import mddocs

```

# Build

MD Docs also comes with a build script that can transform the markdown documents to other forms.

You can use it like:

```

$ build ./sample/config.yaml html

```

Please see the sample folder for further details.


## License

[MIT](https://choosealicense.com/licenses/mit/)