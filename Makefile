# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = 7a2d4c04-b65f-11eb-bfb8-e9fe53ef9e90
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-16
# -----------

# ----------
# Variables

# The location to the python installation to use
PYPATH = ~/opt/python_3.9.1/bin

# The name of the virtual environment to use
VENV = .venv

# The path to the bin folder in the virtual environment. We define this
# so we can use the correct binaries
BIN=$(VENV)/bin

# Set the search path so the venv is searched first
export PATH := $(BIN):$(PATH)

# ---
# all

# What do we execute if `$ make` is called?
# We'll simple build the virtual environment if it doesn't exist. You could modify this
# to build the html or pdf -> `all: $(VENV) html`

all: $(VENV)

# -------------------
# Virtual Environment

$(VENV): requirements.txt
	$(PYPATH)/virtualenv $(VENV)

	# --------------------
	# Install Requirements

	$(BIN)/pip install --upgrade -r requirements.txt

	# -----------------------
	# Install Custom Packages

	# we need to install this package for things to work
	$(BIN)/pip install --editable .

	# -------------
	# Pretty Errors
	#(https://github.com/onelivesleft/PrettyErrors/)

	# install the pretty errors module and set it up to format errors globally for the virtual environment

	$(BIN)/pip install pretty_errors
	$(BIN)/python -m pretty_errors

	touch $(VENV)

# ------------------
# Build Dependencies

# NOTE: The order you call the --config switches is important. The last one in the list will override
# values in the previous ones

output/en/html: $(VENV) en/config.html.yaml
	$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.html.yaml \
	html

output/en/html_single: $(VENV) en/config.html.single.yaml
	$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.html.yaml \
	--config=en/config.html.single.yaml \
	html --single

output/en/pdf: $(VENV) en/config.pdf.yaml
	$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.pdf.yaml \
	pdf

# ----------
# Build HTML

.Phony: html
html: output/en/html

# -------------------
# Build HTML (Single)

.Phony: single
single: output/en/html_single

# ---------
# Build PDF

.Phony: pdf
pdf: output/en/pdf

#-----
# Test

.Phone: test
test: $(VENV)
	$(BIN)/pytest

# -----
# Clean

# Remove any created documents from the build process

.PHONY: clean
clean: output
	@echo "Cleaning build output..."
	@rm -rf output

# ------
# Remove

# Remove the Virtual Environment and clean the cached files

.PHONY: remove
remove: clean
	@echo "Removing ${VENV} and cached files..."
	@rm -rf $(VENV)
	@rm -rf .pytest_cache
	@rm -rf md_docs.egg-info
	@find . -type f -name *.pyc -delete
	@find . -type d -name __pycache__ -delete

