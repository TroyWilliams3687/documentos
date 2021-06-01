---
UUID: 277f8c5a-b5c0-11eb-9fb7-a3fe2da49343

title: Python
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...

# Python

[Python](https://www.python.org) is the programming language used to orchestrate the documentation transformation from markdown to HTML. It is used to provide handy tools for bulk document management in addition to the build script.

## Current Version

As of this date, the current version of python we are using:

```
$ python --version
Python 3.9.5
```

>NOTE: All people working with the document repository that will build the documents (i.e. transform the Markdown to HTML) should be on the same version of Python. I don't think this has to be a strict requirement, but Python might do things differently from version to version. If different versions are in use, it might mean slightly different output results that may not be caught. Unexpected errors may occur as well. At a minimum, all repository users should be on the same major version of Python.

>NOTE: In reality, it should be fine to use any of the v3.9 series for example and not have problems. However, if there is a specific language feature that is not available in older versions that would break the build for others.

### Installers

- Current Version of Python: <https://www.python.org/downloads/release/python-395/>
- All installers for windows: <https://www.python.org/downloads/windows/>

## Installation (Recommended)

>NOTE: We will focus on windows users as Python is very trivial to install on Linux.

References:

- <https://realpython.com/installing-python/#how-to-install-from-the-full-installer>

Download the current version of the python installer (v3.9.5 as of this writing) and install it. Choose the `Install Now` option and make sure the option to `Add Python 3.9 to PATH` is selected.

### Custom Installation

If you want more control, you can choose the custom installation. The only advantage this would have is to allow you to control the installation location of the files. This is handy if you want to maintain multiple versions of Python on your system.

- Set the option `Add Python to the PATH`
    - This is important otherwise python will not be visible to the terminals when you type python and windows will try to get you to install python from the windows store - **DO NOT INSTALL PYTHON FROM THE WINDOWS STORE!**
- Use the Customize Install option and make sure the following items are selected:
    - `Documentation`
    - `pip`
    - `tcl/tk and IDLE`
    - `Python Test Suite`
    - `pylauncher`
    - `precompile standard library`
    - Choose a different install location

## Installation Verification

Open a terminal and issue the command `python --version`:

```
$ python --version
Python 3.9.5
```

If you see the correct version, things have installed properly.

# Install Virtual Environment {#virtual_env}

A key concept in python is the use of virtual environments to help different versions of python and different package configurations. We will use a virtual environment in the Aegis documentation repository.

Make sure you are in the correct folder before proceeding with creating the virtual environment. You want to be in the document repository:

```
$ cd ~/repos/docs/custom_docs
```

## Installation

Reference:

- <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>

virtualenv is used to manage Python packages for different projects. Using virtualenv allows you to avoid installing Python packages globally which could break system tools or other projects. You can install virtualenv using pip.

```
$ python -m pip install virtualenv
```

## Virtual Environment - Create {#virtual_env_create}

It is easy to setup a virtual environment from the terminal. Issue the command `virtualenv .venv` when you are inside the folder you want to create a virtual environment in (the `~/repos/docs/custom_docs`):

```
$ virtualenv .venv
```

The `.venv` is the folder that will contain the contents of the virtual environment. Essentially, it will contain copies of all the python binaries (symlinked on systems that properly support it). The name of the folder is already a part of the `.gitignore` so it will not be picked up as part of the repo. The name of the folder is pretty standard as well.

To delete the virtual environment, simply delete the `.venv` folder. Sometimes this is easier to do than figuring out how to rebuild or change components.

>NOTE: You will have to delete the virtual environments if you update Python to a newer version. The virtual environment will maintain a link to the older version of Python independent of the new version installed. This can be nice, but can be annoying if you forget about it.

## Virtual Environment - Configure {#virtual_env_configure}

Once you have a virtual environment created, the next step is to configure it with the required software modules. It already has a reference to the base Python installation as part of the creation process. There are standard Python packages that are easily configured and added. There is a bit of a wrinkle on windows when it comes to installing the `md_docs` repository so it can be used.

### Activate the Virtual Environment

By itself, the virtual environment does nothing. It needs to be activated. Once it is activated, it will stay activated for the remainder of the session in the terminal.

For PowerShell:

```
$ .\.venv\Scripts\activate.ps1
```

For windows command prompt:

```
$ .\.venv\Scripts\activate.bat
```

>NOTE: I recommend using PowerShell.

Once the virtual environment is activated, the prompt will change to something like this:

```
(.venv) $
```

It will display the name of the currently active virtual environment.

### Install Required Modules

The next step is to install the `md_docs` repository. From the command line:

```bash
$ python -m pip install   git+https://github.com/TroyWilliams3687/md_docs@master
```

This will install the `md_docs` package into your virtual environment from the github repo.

#### Alternative - Local Repository Installation

If you want to install `md_docs` from a local repo, issue the following command:

```bash
$ python -m pip install --editable ~/repo/docs/md_docs/.
```

That will install the contents of the `md_docs` repository into the active virtual environment in an editable format. That means that if changes are made to `md_docs` (pull new changes, manual changes, etc.) they will be immediately reflected in the virtual environment without having to rebuild it. If the `-e` flag is not specified you would have to delete and rebuild the virtual environment every time you had a change in `md_docs`.

