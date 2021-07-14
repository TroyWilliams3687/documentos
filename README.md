# md_doc

The md_doc system is a way to take a series of [Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) files that can be nested or not and transforms them to HTML or PDF documents. The goal of the system is to provide a tool that can take a set of documentation along with its localizations (translations to other languages) and provide a seamless method to transform to other formats in a consistent and reproducible manor.

It provides a common way to implement documentation in a text based format while retaining the power to transform the documentation to other formats. It makes use of [TOML](https://toml.io/en/) configuration files, and [Pandoc](https://pandoc.org/) and [Python](https://www.python.org) to transform Markdown formatted documents into any of the other formats provided by Pandoc. This system has a heavy focus on HTML transformations.

The goal is to provide a plain text mechanism with a very light markup for software documentation. The idea is to make the documentation so that it can live along side the source code in the repository. Changes in the source code that prompt documentation revisions can live side-by-side in the repository. In fact, it is entirely possible to institute a code-review process for documentation revisions and updates.

This tool includes a [sample](en/documents) documents folder that can help you understand how the system works. Simply [clone](#installation) the repo and issue the [`make html`](en/documents/md_doc_system.md#make) in the repo if you are using Linux.

```bash
$ make html
```

## Installation

Clone the git repo:

```bash
$ git clone git@github.com:TroyWilliams3687/md_docs.git
```

For full details, see the [Documentation Repository](en/documents/repo_setup.md) note. It will walk you through the entire process.


# Create the Virtual Environment

```bash
$ make
```

## Activating the Virtual Environment

### Windows

Activate the virtual environment that you want to install it too.

On Windows, using powershell:

```bash
$ .\.venv\Scripts\activate.ps1
```

### Linux

On Linux, for most causes you can simple using the `Makefile` to build the system. If you need to activate the virtual environment:


```bash
$ . .venv/bin/activate
```

## PIP install

Use [pip](https://pip.pypa.io/en/stable/) to add the repository manually to the virtual environment where you want to use the tools.

```bash
$ pip install -e ~/path/to/repo/
```

## Usage

You can use the code in the md_docs, by importing it into your module:


```python
import md_docs
```

## System Commands

For system commands see [commands](en/documents/commands.md).

## Documentation

The documentation can be found [here](en/documents/). Interesting information:

- [System Information](en/documents/md_doc_system.md)
- [Pandoc](en/documents/pandoc.md)
- [Python](en/documents/python.md)
- [Repo Setup](en/documents/repot_setup.md)
- [TOML](en/documents/toml_configuration.md)


## License

[MIT](https://choosealicense.com/licenses/mit/)

# NOTE

In GitHub, the Markdown files may not render properly because of the YAML meta-blocks.