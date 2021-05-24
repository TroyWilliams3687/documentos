#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) <year> <copyright holders>

uuid       =
author     = Troy Williams
email      = troy.williams@bluebill.net
date       =
-----------


"""

import pytest

from pathlib import Path

from md_docs.common import relative_path

# ---------
# relative_path

data = []

data.append(
    {
        "left": Path("documents/file/test/test1"),
        "right": Path("documents/file1/yeet/leet/code"),
        "result": Path("../../../file1/yeet/leet/code"),
    }
)


data.append(
    {
        "left": Path("documents/file/test/test1"),
        "right": Path("documents/file/test/test1/leet/code"),
        "result": Path("./leet/code"),
    }
)


data.append(
    {
        "left": Path("/home/user/test/folder/folder1"),
        "right": Path("/home/user/bruges/numpy"),
        "result": Path("../../../bruges/numpy"),
    }
)

data.append(
    {
        "left": Path("assets/designer/main_ui"),
        "right": Path("assets/designer/main_ui/help/documents"),
        "result": Path("./help/documents"),
    }
)

data.append(
    {
        "left": Path("main/documents/test/test"),
        "right": Path("usr/var/log"),
        "result": Path("../../../../usr/var/log"),
    }
)


data.append(
    {
        "left": Path("/home/troy/repositories/documentation/aegis.documentation/en/documents/designer"),
        "right": Path("/home/troy/repositories/documentation/aegis.documentation/en/documents/designer"),
        "result": Path("./"),
    }
)



@pytest.mark.parametrize("data", data)
def test_find_atx_header(data):

    result = relative_path(data["left"], data["right"])

    assert data["result"] == result
