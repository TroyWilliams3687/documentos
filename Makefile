# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 2021-06-06
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-06-06
# -----------

# -----------
# Information

# This is the prototype for the main Makefile in Python code repositories. It
# will make use of the `Makefile.python` to deal with the majority of python
# functionality that the repos will require. It will also help to make the main
# Makefile clean and contain only specific things that are required for the
# individual repository.


# -----------
# Makefile.env

# Makefile.env - should not be included with your repo. There is a
# Makefile.env.sample that exists with the variables that these makefiles
# require. Please make of copy of that, rename it and update the variables. Also
# add it to the .gitignore file.

include ./mf_support/Makefile.env

include ./mf_support/Makefile.python
include ./mf_support/Makefile.python.build


# ------------------
# Build Dependencies

# NOTE: The order you call the --config switches is important. The last one in the list will override
# values in the previous ones

output/en/html: $(VENV) en/config.html.toml
	@$(BIN)/build \
	--config=en/config.common.toml \
	--config=en/config.html.toml \
	html

output/en/html_single: $(VENV) en/config.html.single.toml
	@$(BIN)/build \
	--config=en/config.common.toml \
	--config=en/config.html.toml \
	--config=en/config.html.single.toml \
	html --single

output/en/pdf: $(VENV) en/config.pdf.toml
	@$(BIN)/build \
	--config=en/config.common.toml \
	--config=en/config.pdf.toml \
	pdf

# ----------
# make html

## make html - Transform the Markdown to HTML.
.Phony: html
html: output/en/html
	@echo "Building HTML..."

# -------------------
# Build HTML (Single)

## make single - Transform the Markdown to a single HTML file.
.Phony: single
single: output/en/html_single
	@echo "Building HTML (Single File)..."

# ---------
# Build PDF

## make pdf - Transform the Markdown to a PDF file.
.Phony: pdf
pdf: output/en/pdf
	@echo "Building PDF..."

# -----
# make clean

# Remove any created documents from the build process

## make clean - Remove the build components
.PHONY: clean
clean:
	@echo "Cleaning PyPI build folder..."
	@rm -rf build
	@echo "Cleaning PyPI dist folder..."
	@rm -rf dist
	@echo "Cleaning Build Output..."
	@rm -rf output

# ------
# make remove

# Remove the Virtual Environment and clean the cached files

## make remove - Remove the virtual environment and all cache files.
.PHONY: remove
remove: remove-venv
	@echo "Removing ${VENV} and Cached Files..."
