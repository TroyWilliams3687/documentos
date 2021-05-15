# MD Docs

This is my repository for code that is common to my Markdown/Pandoc document creation process.

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

Activate the virtual environment that you want to install it too.

On Windows, using powershell:

```
$ .\.venv\Scripts\activate.ps1
```

On Linux, using bash:

```bash
$ . .venv/bin/activate
```

## Pip install

Use [pip](https://pip.pypa.io/en/stable/)


```
$ pip install -e ~/path/to/repo/
```

## Usage

```python

import md_docs

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