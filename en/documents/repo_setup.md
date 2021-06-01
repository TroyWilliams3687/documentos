---
UUID: bbabbd80-b5bc-11eb-9fb7-a3fe2da49343

title: Documentation Repository
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...


# Documentation Repository

You need to create a documentation repository and ensure that this package is properly installed and configured with the virtual environment. The repository will use [Markdown](https://daringfireball.net/projects/markdown/syntax), actually a variation based on [Pandoc](https://pandoc.org/MANUAL.html#pandocs-markdown). It also uses [Python](https://www.python.org) to script the automation processes and orchestrate the transformation of the markdown documents to HTML using [Pandoc](https://pandoc.org).

The documentation will be stored in a [git](https://git-scm.com/) repository under version control. The build process will be managed by the python `build` application that this package maintains or by the use of a `makefile`.

## About

This document will guide you through the process of configuring your machine to build the documentation. This set of documents will also supplement and provide additional examples of the markdown syntax that can be used and how to setup a brand new system. At the end of the installation process you should have documentation repository similar to:

```bash
├── .git
├── .venv
├── en
│   ├── config.common.yaml
│   ├── config.html.yaml
│   ├── css
│   ├── documents
│   │   └── assets
│   └── templates
├── plugins
├── Makefile
└── README.md
```

# Assumptions

- [git](https://git-scm.com/) is installed and running on your system
- You will create a folder called `~/repos/doc`. It can be named anything or located anywhere on your system. This will be the folder where the documentation will be written.

# Repositories

To use the system, you will use pip to install md_docs from github like this:

```bash

$ python -m pip install   git+https://github.com/TroyWilliams3687/md_docs@master

```

However, you can also clone the repository if you like. You should clone the git repo to your local machine, in a folder that is accessible and usable. The repositories can be cloned anywhere on your system. I would recommend creating a specific folder to house the required repositories.

>NOTE: It is assumed you already have an up to date, working copy of git installed on your system.

There is only one repository required to create an effective documentation build process. You can install it:

```
$ mkdir -p ~/repos/docs/md_docs

$ cd ~/repos/docs/md_docs

$ git clone git@github.com:TroyWilliams3687/md_docs.git
```

>NOTE: You should clone the repository to a common folder so it is easier to work with and you keep your system close together. This document will assume you use a common folder called `~/repos/docs` for all the documentation projects.

# Configure Build System

The next steps are:

1. [Install Pandoc](pandoc.md)
1. [Install Python](python.md)
1. [Configure the Virtual Environment](python.md#virtual_env)


# Final Steps

Once you have completed the steps from the previous section, you can finish up. You can create a git repo:

```bash
$ cd `~/repos/docs/custom_docs`

$ git init .
```

Add a copy of the [makefile](https://github.com/TroyWilliams3687/md_docs/blob/master/Makefile) and the [.gitignore](https://github.com/TroyWilliams3687/md_docs/blob/master/.gitignore) files to the repo. It is possible to install `make` on windows, but at the very least you can examine the `Makefile` for details on the various commands that you can use. It also indicates when can be cleaned up in the repository from time-to-time. You may also want to look at the [sample configuration files and plugins](https://github.com/TroyWilliams3687/md_docs/tree/master/samples) and add them to your document repository. Check out the `md_docs` [documentation](https://github.com/TroyWilliams3687/md_docs/tree/master/en) for instructions and hints on how to structure and use the system.
