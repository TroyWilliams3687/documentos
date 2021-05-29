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

# The location to the python installation to use - we have an environment
# variable set with the correct path
PYPATH = ${python}

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
	@$(PYPATH)/virtualenv $(VENV)

	# --------------------
	# Install Requirements

	@$(BIN)/python -m pip install --upgrade -r requirements.txt

	# -----------------------
	# Install Custom Packages

	# we need to install this package for things to work
	@$(BIN)/python -m pip install --editable .

	# -------------
	# Pretty Errors
	#(https://github.com/onelivesleft/PrettyErrors/)

	# install the pretty errors module and set it up to format errors globally for the virtual environment

	@$(BIN)/python -m pip install pretty_errors
	@$(BIN)/python -m pretty_errors -s

	@# `python -m pretty_errors -s` -s to install to the default system location, in this case .venv
	@# https://github.com/onelivesleft/PrettyErrors/blob/master/pretty_errors/__main__.py

	@# NOTE: Running python -m will call the __main__.py module and can do some wonderful things
	@# In addition, it ensures the properly paired binaries are called like pip

	@touch $(VENV)

# ------------------
# Build Dependencies

# NOTE: The order you call the --config switches is important. The last one in the list will override
# values in the previous ones

output/en/html: $(VENV) en/config.html.yaml
	@$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.html.yaml \
	html

output/en/html_single: $(VENV) en/config.html.single.yaml
	@$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.html.yaml \
	--config=en/config.html.single.yaml \
	html --single

output/en/pdf: $(VENV) en/config.pdf.yaml
	@$(BIN)/build \
	--config=en/config.common.yaml \
	--config=en/config.pdf.yaml \
	pdf

# ----------
# Build HTML

.Phony: html
html: output/en/html
	@echo "Building HTML..."

# -------------------
# Build HTML (Single)

.Phony: single
single: output/en/html_single
	@echo "Building HTML (Single File)..."

# ---------
# Build PDF

.Phony: pdf
pdf: output/en/pdf
	@echo "Building PDF..."

#-----
# Test

.Phone: test
test: $(VENV)
	@echo "Running Tests..."
	@$(BIN)/pytest

# -----
# Black

.PHONY: black
black:
	@echo "Applying Black Code Formatting..."
	@$(BIN)/black src/

# -----
# Clean

# Remove any created documents from the build process

.PHONY: clean
clean:
	@echo "Cleaning Build Output..."
	@rm -rf output

# ------
# Remove

# Remove the Virtual Environment and clean the cached files

.PHONY: remove
remove: clean
	@echo "Removing ${VENV} and Cached Files..."
	@rm -rf $(VENV)
	@find . -type f -name *.pyc -delete
	@find . -type d -name '*.egg-info' -exec rm -r {} +
	@find . -type d -name __pycache__ -exec rm -r {} +
	@find . -type d -name .pytest_cache -exec rm -r {} +

