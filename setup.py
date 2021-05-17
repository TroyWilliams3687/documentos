#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid       = ff3c11de-b5b3-11eb-9fb7-a3fe2da49343
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2021-05-15
# -----------

"""
This module contains information for properly setting up a package that can
represent mddocs.
"""

from setuptools import setup, find_packages

setup(
    name="mddocs",
    version="0.1",
    author="Troy Williams",
    author_email="troy.williams@bluebill.net",
    description="Build tools and Common Utilities for Markdown/Pandoc document system.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=[
        "requests",
        "click",
        "tzdata",
        "pyyaml",
        "pandoc-fignos",
        "pandoc-eqnos",
        "pandoc-tablenos",
        "pandoc-secnos",
    ],
    entry_points="""
        [console_scripts]
        build=build.build:main
    """,
    python_requires=">=3.9",
)
