---
ID: bbabbd80-b5bc-11eb-9fb7-a3fe2da49343

title: Documentation Repository
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...


# Documentation Repository

You would need to create a documentation repository and ensure that this package was properly configured with the virtual environment. The repository will use [Markdown](https://daringfireball.net/projects/markdown/syntax), actually a variation based on [Pandoc](https://pandoc.org/MANUAL.html#pandocs-markdown). It also uses [Python](https://www.python.org) to script the automation processes and orchestrate the transformation of the markdown documents to HTML using [Pandoc](https://pandoc.org).

The documentation will be stored in a [git](https://git-scm.com/) repository under version control. The build process will be managed by the python `build` application that this package maintains.

## About

This document will guide you through the process of configuring your machine to build the documentation. This set of documents will also supplement and provide additional examples of the markdown syntax that can be used and how to setup a brand new system.

# Assumptions

- [git](https://git-scm.com/) is installed and running on your system
- You will create a folder called `support_repos` or something similar to store the required repositories.

# Repositories

You need to clone the git repo to your local machine, in a folder that is accessible and usable. The repositories can be cloned anywhere on your system. I would recommend creating a specific folder to house the required repositories.

>NOTE: It is assumed you already have an up to date, working copy of git installed on your system.

There is only one repository required to create an effective documentation build process. You can install it:

```
$ cd ~/repositories/documentation

$ mkdir md_docs

$ cd ~/repositories/documentation/md_docs

$ git clone git@github.com:TroyWilliams3687/md_docs.git
```

>NOTE: You should clone the repository to a common folder so it is easier to work with and you keep your system close together. This document will assume you use a common folder called `~/repositories/documentation` for all the documentation projects.

# Configure Build System

Once the repositories are cloned, the next steps are:

1. [Install Pandoc](pandoc.md)
1. [Install Python](python.md)
1. [Configure the Virtual Environment](python.md#virtual_env)