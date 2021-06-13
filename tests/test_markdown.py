#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
-----------
SPDX-License-Identifier: MIT
Copyright (c) 2020 Troy Williams

uuid       = 2fc2598a-341d-11eb-bf3c-ab85e03a1801
author     = Troy Williams
email      = troy.williams@bluebill.net
date       = 2020-12-01
-----------


"""

import pytest

from md_docs.md_docs.markdown import section_to_anchor, find_atx_header

from md_docs.md_docs.markdown import (
    extract_markdown_links,
    extract_relative_markdown_links,
    extract_markdown_image_links,
    extract_relative_markdown_image_links,
)

# -----------
# Test find_atx_header

data = []
data.append(("# Header Level 1", "Header Level 1"))
data.append(("## Header Level 2", "Header Level 2"))
data.append(("### Header Level 3", "Header Level 3"))
data.append(("#### Header Level 4", "Header Level 4"))
data.append(("##### Header Level 5", "Header Level 5"))
data.append(("###### Header Level 6", "Header Level 6"))

data.append(("# # Header Level 2", "# Header Level 2"))
data.append(("## # Header Level 3", "# Header Level 3"))
data.append(("### # Header Level 4", "# Header Level 4"))
data.append(("#### # Header Level 5", "# Header Level 5"))
data.append(("##### # Header Level 6", "# Header Level 6"))

data.append((" # Header Level 1", "Header Level 1"))
data.append(("  ## Header Level 2", "Header Level 2"))
data.append(("   ### Header Level 3", "Header Level 3"))

data.append(("Not a header", None))
data.append(("$# Not a header", None))
data.append(("     #### Header Level 4 - Too many leading spaces", None))


@pytest.mark.parametrize("data", data)
def test_find_atx_header(data):

    tv, tr = data

    result = find_atx_header(tv)

    if result:
        level, text = result
        assert text == tr

    else:
        assert result == tr


# -----------
# Test section_to_anchor

data = []

data.append(("[Equations](./ch0_2_equations.html#sec:ch0_2_equations-1)", "equations"))
data.append(("[Images](./ch0_1_images.html#sec:ch0_1_images-1)", "images"))
data.append(
    (
        "[pandoc-eqnos](https://github.com/tomduck/pandoc-eqnos) Usage",
        "pandoc-eqnos-usage",
    )
)
data.append(
    (
        "[pandoc-fignos](https://github.com/tomduck/pandoc-fignos) Usage",
        "pandoc-fignos-usage",
    )
)
data.append(("[pandoc-xnos](https://github.com/tomduck/pandoc-xnos)", "pandoc-xnos"))
data.append(("[Sections](./ch0_4_sections.html#sec:ch0_4_sections-1)", "sections"))
data.append(("[Tables](./ch0_3_tables.html#sec:ch0_3_tables-1)", "tables"))

data.append(("Clever References", "clever-references"))
data.append(("Disabling Links", "disabling-links"))
data.append(("Tagged Figures", "tagged-figures"))
data.append(("Nested Documents", "nested-documents"))
data.append(("Examples", "examples"))
data.append(("Markdown Preprocessor", "markdown-preprocessor"))

data.append(("Equations {#sec:ch0_2_equations-1}", "sec:ch0_2_equations-1"))
data.append(("Images {#sec:ch0_1_images-1}", "sec:ch0_1_images-1"))
data.append(("Preamble {#sec:ch0_0_preamble-1}", "sec:ch0_0_preamble-1"))

data.append(
    ("Explosive Detonation Pressure, $P_{id}$", "explosive-detonation-pressure-p_id")
)
data.append(("Borehole Pressure, $P_{dbp}$", "borehole-pressure-p_dbp"))
data.append(("Internal Energy, $E_{i}$", "internal-energy-e_i"))


@pytest.mark.parametrize("data", data)
def test_section_to_anchor(data):

    value, result = data

    assert section_to_anchor(value) == result


# ----------
# extract_markdown_links


lines = []
results = []
lines.append(
    "This is a link [test](https://www.google.ca) and another [link](./local/file.text)"
)

results.append(
    [
        {
            "full": "[test](https://www.google.ca)",
            "text": "test",
            "url": "https://www.google.ca",
        },
        {
            "full": "[link](./local/file.text)",
            "text": "link",
            "url": "./local/file.text",
        },
    ]
)

lines.append(
    "Here is a test link: [Equations](http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1) and another one:  [Images](./ch0_1_images.html#sec:ch0_1_images-1)!"
)

results.append(
    [
        {
            "full": "[Equations](http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1)",
            "text": "Equations",
            "url": "http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1",
        },
        {
            "full": "[Images](./ch0_1_images.html#sec:ch0_1_images-1)",
            "text": "Images",
            "url": "./ch0_1_images.html#sec:ch0_1_images-1",
        },
    ]
)


lines.append("[Sections](./ch0_4_sections.html#sec:ch0_4_sections-1)")

results.append(
    [
        {
            "full": "[Sections](./ch0_4_sections.html#sec:ch0_4_sections-1)",
            "text": "Sections",
            "url": "./ch0_4_sections.html#sec:ch0_4_sections-1",
        }
    ]
)

lines.append("This line contains no links!")
results.append([])

data = [(l, r) for l, r in zip(lines, results)]


@pytest.mark.parametrize("data", data)
def test_extract_markdown_links(data):
    line, compare = data

    results = extract_markdown_links(line)

    assert len(results) == len(compare)

    for r, o in zip(compare, results):
        assert r["url"] == o["url"]
        assert r["text"] == o["text"]


# ----------
# extract_relative_markdown_links

lines = []
results = []
lines.append(
    "This is a link [test](https://www.google.ca) and another [link](./local/file.text)"
)

results.append(
    [
        {
            "md": "./local/file.text",
            "section": None,
        }
    ]
)

lines.append(
    "Here is a test link: [Equations](http://test.org/ch0_2_equations.html#sec:ch0_2_equations-1) and another one:  [Images](./ch0_1_images.html#sec:ch0_1_images-1)!"
)

results.append(
    [
        {
            "md": "./ch0_1_images.html",
            "section": "#sec:ch0_1_images-1",
        }
    ]
)


lines.append("[Sections](./ch0_4_sections.html#sec:ch0_4_sections-1)")

results.append(
    [
        {
            "md": "./ch0_4_sections.html",
            "section": "#sec:ch0_4_sections-1",
        }
    ]
)

lines.append("This line contains no links!")
results.append([])

lines.append(
    "- [2016-03-12]{.index-file-date} - [Convert MTS (AVCHD) Files to mkv](archive/Convert MTS (AVCHD) Files to mkv.md){.index-file-link}"
)

results.append(
    [
        {
            "md": "archive/Convert MTS (AVCHD",  # this is what it will capture based on the regex in MarkdownLinkRule. If we change it then it gets confused about markdown links in the same line. So best to not have brackets in files names.
            "section": None,
        }
    ]
)

data = [(l, r) for l, r in zip(lines, results)]


@pytest.mark.parametrize("data", data)
def test_extract_relative_markdown_links(data):
    line, compare = data

    results = extract_relative_markdown_links(line)

    assert len(results) == len(compare)

    for r, o in zip(compare, results):
        assert r["md"] == o["md"]
        assert r["section"] == o["section"]


# def test_extract_relative_markdown_links_direct():

#     line = '- [2016-03-12]{.index-file-date} - [Convert MTS (AVCHD) Files to mkv](archive/Convert MTS (AVCHD) Files to mkv.md){.index-file-link}'
#     results = extract_relative_markdown_links(line)

#     assert len(results) == 1

#     r = results[0]

#     assert r['full'] == '[Convert MTS (AVCHD) Files to mkv](archive/Convert MTS (AVCHD) Files to mkv.md)'
#     assert r['text'] == 'Convert MTS (AVCHD) Files to mkv'
#     assert r['link'] == 'archive/Convert MTS (AVCHD) Files to mkv.md'


# ----------
# extract_markdown_image_links

lines = []
results = []
lines.append(
    "Here is an image link: ![Image Caption](http://www.url.test/image.png) and another one ![](./assets/image.png)"
)

results.append(
    [
        {
            "full": "![Image Caption](http://www.url.test/image.png)",
            "caption": "Image Caption",
            "url": "http://www.url.test/image.png",
        },
        {
            "full": "![](./assets/image.png)",
            "caption": "",
            "url": "./assets/image.png",
        },
    ]
)


lines.append(
    "![Test One](./picture.jpg) and ![Test 2](https://www.google.com/image.png) and ![test Three](./assets/test/test.png)"
)

results.append(
    [
        {
            "full": "![Test One](./picture.jpg)",
            "caption": "Test One",
            "url": "./picture.jpg",
        },
        {
            "full": "![Test 2](https://www.google.com/image.png)",
            "caption": "Test 2",
            "url": "https://www.google.com/image.png",
        },
        {
            "full": "![test Three](./assets/test/test.png)",
            "caption": "test Three",
            "url": "./assets/test/test.png",
        },
    ]
)

lines.append("![A beautiful Sunset on the Mayan Rivera](./sunset.jpg).")

results.append(
    [
        {
            "full": "![A beautiful Sunset on the Mayan Rivera](./sunset.jpg)",
            "caption": "A beautiful Sunset on the Mayan Rivera",
            "url": "./sunset.jpg",
        },
    ]
)

lines.append("This line contains no images links @#$1!.")
results.append([])

data = [(l, r) for l, r in zip(lines, results)]

# test no links present to see what happens


@pytest.mark.parametrize("data", data)
def test_extract_markdown_image_links(data):
    line, result = data

    for r, o in zip(result, extract_markdown_image_links(line)):
        assert r["full"] == o["full"]
        assert r["caption"] == o["caption"]
        assert r["url"] == o["url"]

    # assert result == extract_markdown_image_links(line)


# ----------
# extract_relative_markdown_image_links

results = []

results.append(
    [
        {
            "full": "![](./assets/image.png)",
            "caption": "",
            "url": "./assets/image.png",
        },
    ]
)


results.append(
    [
        {
            "full": "![Test One](./picture.jpg)",
            "caption": "Test One",
            "url": "./picture.jpg",
        },
        {
            "full": "![test Three](./assets/test/test.png)",
            "caption": "test Three",
            "url": "./assets/test/test.png",
        },
    ]
)

results.append(
    [
        {
            "full": "![A beautiful Sunset on the Mayan Rivera](./sunset.jpg)",
            "caption": "A beautiful Sunset on the Mayan Rivera",
            "url": "./sunset.jpg",
        },
    ]
)

results.append([])

data = [(l, r) for l, r in zip(lines, results)]


@pytest.mark.parametrize("data", data)
def test_extract_relative_markdown_image_links(data):
    line, result = data

    for r, o in zip(result, extract_relative_markdown_image_links(line)):
        assert r["full"] == o["full"]
        assert r["caption"] == o["caption"]
        assert r["url"] == o["url"]
