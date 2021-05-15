#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = 2fc2598a-341d-11eb-bf3c-ab85e03a1801
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-12-01
# -----------

"""

"""

import pytest
import datetime

from md_docs.pandoc import extract_yaml

# -----------
# Test extract_yaml

data = [(
         [
         'more stuff\n',
         '\n',
         '---\n',
         'title: About\n',
         'author: Troy Williams\n',
         'date: 2016-03-06\n',
         '...\n',
         '\n',
         'Test Data and more Test data\n',
         '\n',
         '---\n',
         'title2: Another Title\n',
         'author2: Troy Williams\n',
         'date2: 2020-12-29\n',
         '---\n',
         '\n',
         'Some more data in there....\n',
         ]
        ,
         {
         'title':'About',
         'author':'Troy Williams',
         'date': datetime.date(2016, 3, 6),
         'title2':'Another Title',
         'author2':'Troy Williams',
         'date2':datetime.date(2020, 12, 29),
         }
        )
       ]


@pytest.mark.parametrize('data', data)
def test_extract_yaml(data):

    tv, tr = data

    result = extract_yaml(tv)

    assert result == tr


# # -----------
# # Test find_atx_header

# data = []
# data.append(('# Header Level 1', 'Header Level 1'))
# data.append(('## Header Level 2', 'Header Level 2'))
# data.append(('### Header Level 3', 'Header Level 3'))
# data.append(('#### Header Level 4', 'Header Level 4'))
# data.append(('##### Header Level 5', 'Header Level 5'))
# data.append(('###### Header Level 6', 'Header Level 6'))

# data.append(('# # Header Level 2', '# Header Level 2'))
# data.append(('## # Header Level 3', '# Header Level 3'))
# data.append(('### # Header Level 4', '# Header Level 4'))
# data.append(('#### # Header Level 5', '# Header Level 5'))
# data.append(('##### # Header Level 6', '# Header Level 6'))

# data.append((' # Header Level 1', 'Header Level 1'))
# data.append(('  ## Header Level 2', 'Header Level 2'))
# data.append(('   ### Header Level 3', 'Header Level 3'))

# data.append(('Not a header', None))
# data.append(('$# Not a header', None))
# data.append(('     #### Header Level 4 - Too many leading spaces', None))

# @pytest.mark.parametrize('data', data)
# def test_find_atx_header(data):

#     tv, tr = data

#     result = find_atx_header(tv)

#     if result:
#         level, text = result
#         assert text == tr

#     else:
#         assert result == tr


# # -----------
# # Test section_to_anchor

# data = []

# data.append(('[Equations](./ch0_2_equations.html#sec:ch0_2_equations-1)', 'equations'))
# data.append(('[Images](./ch0_1_images.html#sec:ch0_1_images-1)', 'images'))
# data.append(('[pandoc-eqnos](https://github.com/tomduck/pandoc-eqnos) Usage', 'pandoc-eqnos-usage'))
# data.append(('[pandoc-fignos](https://github.com/tomduck/pandoc-fignos) Usage', 'pandoc-fignos-usage'))
# data.append(('[pandoc-xnos](https://github.com/tomduck/pandoc-xnos)', 'pandoc-xnos'))
# data.append(('[Sections](./ch0_4_sections.html#sec:ch0_4_sections-1)', 'sections'))
# data.append(('[Tables](./ch0_3_tables.html#sec:ch0_3_tables-1)', 'tables'))

# data.append(('Clever References', 'clever-references'))
# data.append(('Disabling Links', 'disabling-links'))
# data.append(('Tagged Figures', 'tagged-figures'))
# data.append(('Nested Documents', 'nested-documents'))
# data.append(('Examples', 'examples'))
# data.append(('Markdown Preprocessor', 'markdown-preprocessor'))

# data.append(('Equations {#sec:ch0_2_equations-1}', 'sec:ch0_2_equations-1'))
# data.append(('Images {#sec:ch0_1_images-1}', 'sec:ch0_1_images-1'))
# data.append(('Preamble {#sec:ch0_0_preamble-1}', 'sec:ch0_0_preamble-1'))

# data.append(('Explosive Detonation Pressure, $P_{id}$', 'explosive-detonation-pressure-p_id'))
# data.append(('Borehole Pressure, $P_{dbp}$', 'borehole-pressure-p_dbp'))
# data.append(('Internal Energy, $E_{i}$', 'internal-energy-e_i'))

# @pytest.mark.parametrize('data', data)
# def test_section_to_anchor(data):

#     value, result = data

#     assert section_to_anchor(value) == result


# # ------------
# # Test create_file_toc


# lines = []

# lines.append('# Preamble {#sec:ch0_0_preamble-1}')
# lines.append('')
# lines.append('The purpose of this set of files is to test out the [pandoc](https://pandoc.org) tool chain and see how it works at document creation. The idea is to try and write up some test documents that cover:')
# lines.append('')
# lines.append('- nested documents')
# lines.append('- images')
# lines.append('- equations')
# lines.append('- tables')
# lines.append('- internal links')
# lines.append('- external links')
# lines.append('- intra-document links')
# lines.append('- numbering (figure, equation, table) and references')
# lines.append('')
# lines.append('Since we will be using pandoc, we will adopt some of its notations and conventions for markdown. Namely around referencing and numbering.')
# lines.append('')
# lines.append('## Pandoc')
# lines.append('')
# lines.append('### [pandoc-xnos](https://github.com/tomduck/pandoc-xnos)')
# lines.append('')
# lines.append('The pandoc-xnos filter suite provides facilities for cross-referencing in markdown documents processed by pandoc. Individual filters are maintained in separate projects. They are:')
# lines.append('')
# lines.append('- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.')
# lines.append('- [pandoc-eqnos](https://github.com/tomduck/pandoc-eqnos): Numbers equations and equation references.')
# lines.append('- [pandoc-tablenos](https://github.com/tomduck/pandoc-tablenos): Numbers tables and table references.')
# lines.append('- [pandoc-secnos](https://github.com/tomduck/pandoc-secnos): Numbers section references (sections are numbered by pandoc itself).')
# lines.append('')
# lines.append('')
# lines.append('Click on the above links to access documentation for each filter. LaTeX/pdf, html, and epub output have native support. Native support for docx output is a work in progress.')
# lines.append('')
# lines.append("We'll make use of the xnos suite of tools for testing.")
# lines.append('')
# lines.append('## Nested Documents')
# lines.append('')
# lines.append("The idea is to have store some of the documents (.md) files grouped logically in separate folders. We should be able to construct output document formats based on these structures. HTML should be simple. I don't think we want to construct one giant single file, but a nested hierarchy. So conversion to HTML should be pretty straight forward, it will simply mirror the folder structure. For single file documents like pdf, docx, etc., the documents should be merged into a single markdown file before processing. They should be merged in a logical sequential order.")
# lines.append('')
# lines.append('It should be possible to construct sub-documents by selecting specific documents from the specific folder. For HTML, this will be tricky, do we maintain the structure or merge to a single file. We should be able to do both. If we merge to a single file the numbering must be consistent. With single documents, it is easy the numbering is consistent within the file. When the files are merged, the numbering must be rest and start from the beginning of the document.')
# lines.append('')
# lines.append('## [Images](./ch0_1_images.md#sec:ch0_1_images-1)')
# lines.append('')
# lines.append('The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.')
# lines.append('')
# lines.append('## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)')
# lines.append('')
# lines.append('The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)')
# lines.append('')
# lines.append('')
# lines.append('## [Tables](./ch0_3_tables.md#sec:ch0_3_tables-1)')
# lines.append('')
# lines.append('Tables are not used often but can be vital for organizing and displaying a large amount of data in a compact form. See the stress profile results in the [Table](./ch0_3_tables.md#tbl:ch0_3_tables-5).')
# lines.append('')
# lines.append('## [Sections](./ch0_4_sections.md#sec:ch0_4_sections-1)')
# lines.append('')
# lines.append('Sections are a vital way to organize documents. By default pandoc automatically creates identifiers. pandoc-secnos extends the formatting and makes it easy to assign a unique id across the document. That way if the document is spread across a number of files, it can be handled in a consistent manor.')
# lines.append('')
# lines.append('# Markdown Preprocessor')
# lines.append('')
# lines.append('We are also going to be testing the markdown preprocessor ([MarkdownPP](https://github.com/jreese/markdown-pp)). This will help to handle large documentation projects in a way that is logical and reproducible.')
# lines.append('')
# lines.append('Here is a code block test:')
# lines.append('')
# lines.append('```python')
# lines.append('# A comment - not a section')
# lines.append('   for l in lines:')
# lines.append('       print(l)')
# lines.append('# more comments')
# lines.append('##### other stuff that looks like a section')
# lines.append('```')
# lines.append('# Section After Block')
# lines.append('')


# results = []
# results.append('- [Preamble](#sec:ch0_0_preamble-1)')
# results.append('  - [Pandoc](#pandoc)')
# results.append('    - [pandoc-xnos](#pandoc-xnos)')
# results.append('  - [Nested Documents](#nested-documents)')
# results.append('  - [Images](#images)')
# results.append('  - [Equations](#equations)')
# results.append('  - [Tables](#tables)')
# results.append('  - [Sections](#sections)')
# results.append('- [Markdown Preprocessor](#markdown-preprocessor)')
# results.append('- [Section After Block](#section-after-block)')

# data = [(lines, results)]

# @pytest.mark.parametrize('data', data)
# def test_create_file_toc(data):

#     lines, result = data

#     toc = create_file_toc(lines=lines)

#     assert len(toc) == len(result)

#     for toc_line, result_line in zip(toc, result):
#         assert toc_line == result_line

