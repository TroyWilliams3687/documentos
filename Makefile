# 2021-05-15
# Reference: https://venthur.de/2021-03-31-python-makefiles.html


# ----------
# Variables

PYPATH = ~/opt/python_3.9.1/bin
VENV = .venv
BIN=$(VENV)/bin

# Attache the venv path so it is searched first for binaries
export PATH := $(BIN):$(PATH)

# ----------
# all

# What do we execute if `$ make` is called?

all: $(VENV)

# How to construct the virtual environment
$(VENV): requirements.txt
	$(PYPATH)/virtualenv $(VENV)

	# ----------
	# Install Requirements

	$(BIN)/pip install --upgrade -r requirements.txt

	# ----------
	# Install Custom Packages

	$(BIN)/pip install --editable .

	# ----------
	# Pretty Errors (https://github.com/onelivesleft/PrettyErrors/)

	# install the pretty errors module and set it up to format errors globally for the virtual environment

	$(BIN)/pip install pretty_errors
	$(BIN)/python -m pretty_errors

	touch $(VENV)

# ----------
# remove

# Remove the Virtual Environment

.PHONY: remove
remove: $(VENV)
	rm -rf $(VENV)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

