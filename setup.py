#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid  : ff3c11de-b5b3-11eb-9fb7-a3fe2da49343
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2021-05-15
# -----------

"""
This module contains information for properly setting up a package that
can represent md_docs.
"""

from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).parent.joinpath("README.md").read_text()

setup(
    name="mddocs",  # The name of the package
    version="0.0.1",
    description="Build tools and Common Utilities for Markdown/Pandoc document system.",
    author="Troy Williams",
    author_email="troy.williams@bluebill.net",
    url="https://github.com/TroyWilliams3687/md_docs",
    long_description=README,
    long_description_content_type="text/markdown",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    packages=find_packages(where="src"),  # Search for packages in src/
    package_dir={
        "": "src", # Remap the structure so it understands that src/ is the root
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "build=md_docs.tools.build:main",
            "docs=md_docs.tools.docs:main",
        ],
    },
    install_requires=[
        "requests",
        "click",
        "tzdata",
        "toml",
        "pyyaml",        # Required to extract the YAML block from Markdown files.
        "pandoc-fignos",
        "pandoc-eqnos",
        "pandoc-tablenos",
        "pandoc-secnos",
        "appdirs",
        "networkx",
        "matplotlib",
    ],
)
