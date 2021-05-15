---
ID: 3b5e1a2c-b5be-11eb-9fb7-a3fe2da49343

title: Pandoc
language: en

version_created:
  date: 2021-05-15
  user: 2021.1

pandoc_version: 2.12
...

# Pandoc

[Pandoc](https://pandoc.org) is the swiss army knife of document conversion tools. This tool was chosen to perform the transformation from markdown to HTML. The reason - it works and it supports a plethora of other options as well, including: PDF, Word, PowerPoint, etc...

This tool is relatively easy to use. However, this documentation build system is orchestrated by [Python](https://www.python.org/) code. So using the tool directly is not a required to build the Aegis documentation.

>NOTE: This document is focused towards windows users. Installation will be more or less similar. There are [instructions](https://pandoc.org/installing.html#linux) for linux. They are straightforward. Windows tends to have a lot more moving pieces.

## Current Version (*v2.12*)

This document was written with Pandoc `v2.12`. 

>NOTE: If you need or want to use a different version of Pandoc, feel free. Make sure that all other documentation repository users are at the same version. I don't think this has to be a strict requirement, but Pandoc might do things differently from version to version - there are no guarantees. If different versions are used, it might mean slightly different output results that may not be detected. This may or may not be a problem - you are warned!

### Installers

The current version of the installer can be found here:

- Installers page: <https://github.com/jgm/pandoc/releases/tag/2.12>
- v2.12 windows installer: <https://github.com/jgm/pandoc/releases/download/2.12/pandoc-2.12-windows-x86_64.msi>

## References

- Main Website - <https://pandoc.org>
- Installation - <https://pandoc.org/installing.html>
- Windows Installation - <https://pandoc.org/installing.html#windows>
- Getting Started - <https://pandoc.org/getting-started.html>
- Manual - <https://pandoc.org/MANUAL.html>
    - There is a PDF version of the manual available

## Installation

Download the correct version of the installer (see the [Installers](#installers) section) and execute the MSI. It can be installed using the defaults. There is nothing out of the ordinary or special about the installation.

Once the installation process is completed you can verify success by open a command prompt or PoowerShell terminal and issue the command `pandoc --version`:

```
$ pandoc --version
pandoc.exe 2.12
Compiled with pandoc-types 1.22, texmath 0.12.1.1, skylighting 0.10.4,
citeproc 0.3.0.8, ipynb 0.1.0.1
User data directory: C:\Users\troy.williams\AppData\Roaming\pandoc
Copyright (C) 2006-2021 John MacFarlane. Web:  https://pandoc.org
This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
```

### Linux

Reference: <https://pandoc.org/installing.html#linux>

Download load the DEB - <https://github.com/jgm/pandoc/releases/tag/2.12>. Install it:

```
$ sudo apt install ./pandoc-2.12-1-amd64.deb
```

>NOTE: To install newer versions, it is probably a good idea to `sudo apt remote pandoc` before installing the newer version.


## PDF Requirements

Windows does not come supplied with any proper tools to build PDF files. If this is requirement, you will have to install a Latex package called MikTex.

- <https://miktex.org>
- <https://miktex.org/download>

Download the latest version of MikTex and install it. It doesn't seem to matter what version of MikTex that you select, so choose the latest version.

To verify the installation run `pdflatex --version` from a terminal:

```
$ pdflatex --version
MiKTeX-pdfTeX 4.1 (MiKTeX 20.12)
© 1982 D. E. Knuth, © 1996-2020 Hàn Thế Thành
TeX is a trademark of the American Mathematical Society.
using bzip2 version 1.0.8, 13-Jul-2019
compiled with curl version 7.72.0; using libcurl/7.72.0 Schannel
compiled with expat version 2.2.10; using expat_2.2.10
compiled with jpeg version 9.4
compiled with liblzma version 50020052; using 50020052
compiled with libpng version 1.6.37; using 1.6.37
compiled with libressl version LibreSSL 3.1.4; using LibreSSL 3.1.4
compiled with MiKTeX Application Framework version 4.0; using 4.0
compiled with MiKTeX Core version 4.3; using 4.3
compiled with MiKTeX Archive Extractor version 4.0; using 4.0
compiled with MiKTeX Package Manager version 4.1; using 4.1
compiled with uriparser version 0.9.4
compiled with xpdf version 4.02
compiled with zlib version 1.2.11; using 1.2.11
```

> NOTE: It doesn't seem to matter what version we use as long as it is a recent version. It is probably a good idea to make sure everyone is using the same version to avoid difficulties.

### Linux

For linux, we'll need to install TeX Live:

```
$ sudo apt install texlive
```