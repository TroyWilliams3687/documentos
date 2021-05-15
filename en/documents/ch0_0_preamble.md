---
ID: 063d2ab0-b5c1-11eb-9fb7-a3fe2da49343

title: Preamble
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...

# Preamble {#sec:ch0_0_preamble-1}

The purpose of this set of files is to test out the [pandoc](https://pandoc.org) tool chain and see how it works at document creation. The idea is to try and write up some test documents that cover:

- nested documents
- images
- equations
- tables
- internal links
- external links
- intra-document links
- numbering (figure, equation, table) and references

Since we will be using pandoc, we will adopt some of its notations and conventions for markdown. Namely around referencing and numbering.

## Pandoc

### [pandoc-xnos](https://github.com/tomduck/pandoc-xnos)

The pandoc-xnos filter suite provides facilities for cross-referencing in markdown documents processed by pandoc. Individual filters are maintained in separate projects. They are:

- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.
- [pandoc-eqnos](https://github.com/tomduck/pandoc-eqnos): Numbers equations and equation references.
- [pandoc-tablenos](https://github.com/tomduck/pandoc-tablenos): Numbers tables and table references.
- [pandoc-secnos](https://github.com/tomduck/pandoc-secnos): Numbers section references (sections are numbered by pandoc itself).


Click on the above links to access documentation for each filter. LaTeX/pdf, html, and epub output have native support. Native support for docx output is a work in progress.

We'll make use of the xnos suite of tools for testing.

## Nested Documents

The idea is to have store some of the documents (.md) files grouped logically in separate folders. We should be able to construct output document formats based on these structures. HTML should be simple. I don't think we want to construct one giant single file, but a nested hierarchy. So conversion to HTML should be pretty straight forward, it will simply mirror the folder structure. For single file documents like pdf, docx, etc., the documents should be merged into a single markdown file before processing. They should be merged in a logical sequential order.

It should be possible to construct sub-documents by selecting specific documents from the specific folder. For HTML, this will be tricky, do we maintain the structure or merge to a single file. We should be able to do both. If we merge to a single file the numbering must be consistent. With single documents, it is easy the numbering is consistent within the file. When the files are merged, the numbering must be rest and start from the beginning of the document.

## [Images](./ch0_1_images.md#sec:ch0_1_images-1)

The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.

## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)

The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)


## [Tables](./ch0_3_tables.md#sec:ch0_3_tables-1)

Tables are not used often but can be vital for organizing and displaying a large amount of data in a compact form. See the stress profile results in the [Table](./ch0_3_tables.md#tbl:ch0_3_tables-5).

## [Sections](./ch0_4_sections.md#sec:ch0_4_sections-1)

Sections are a vital way to organize documents. By default pandoc automatically creates identifiers. pandoc-secnos extends the formatting and makes it easy to assign a unique id across the document. That way if the document is spread across a number of files, it can be handled in a consistent manor.
