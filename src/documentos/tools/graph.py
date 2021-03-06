#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Troy Williams

# uuid  : 87ea09ea-810c-11ec-8d80-cf6657f7e811
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2022-01-29
# -----------

"""
The graph command will display a plot, a DAG, showing the inter-connections
between all of the documents in the system.
"""

# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# 3rd Party - From pip

import click
import networkx as nx
import matplotlib.pyplot as plt

from rich.console import Console
console = Console()

# ------------
# Custom Modules

from ..documentos.document import (
    MarkdownDocument,
    LSTDocument,
    reverse_relative_links,
    search,
)

# -------------


def create_sub_graph(G, incoming_limit=1, outgoing_limit=0):
    """
    Given the DAG, return a sub-graph where the nodes have the incoming
    and outgoing connections.
    """

    sub_graph = nx.DiGraph()

    # find the nodes that only have one incoming edge and 0 outgoing
    for n in G.nodes:

        incoming = G.in_edges(nbunch=n)
        outgoing = G.out_edges(nbunch=n)

        if len(incoming) == incoming_limit and len(outgoing) == outgoing_limit:
            sub_graph.add_edges_from(G.in_edges(nbunch=n))

    return sub_graph


def construct_edges(lst_contents, md_links, root=None):
    """
    Given the list of Markdown files referenced by the LST file, find
    all links between them.
    """

    edges = []

    for md in lst_contents:

        key = md.filename

        if root:
            key = key.relative_to(root)

        if key in md_links:

            for rl in md_links[key]:
                edges.append((key, str(rl)))

    return edges


@click.command("graph")
@click.argument("lst", type=click.Path(exists=True))
@click.pass_context
def graph(*args, **kwargs):
    """
    \b
    Given the LST file, find all the Markdown files associated with it
    and display the network graph showing links.

    # Usage

    $ docs --config=./en/config.common.yaml graph ./en/documents/all.lst

    """

    config = args[0].obj["cfg"]

    # the LST file could be passed in as a relative path. We resolve it
    # to an absolute path.

    lst = LSTDocument(Path(kwargs["lst"]).resolve())

    console.print("Searching for Markdown files...")

    md_files = search(root=config["documents.path"])

    console.print(f"{len(md_files)} markdown files were found...")

    # Gather all Markdown files from the LST and de-duplicate the list
    lst_contents = list({[MarkdownDocument(f) for f in lst.links]})

    console.print(f"{len(lst_contents)} markdown files were in {lst.filename}...")

    # To construct the graph, we only need the relative paths to the
    # Markdown files stored in an efficient structure

    md_links = reverse_relative_links(lst_contents, root=config["documents.path"])

    edges = construct_edges(lst_contents, md_links, root=config["documents.path"])

    # At this point we have edges, we can construct the graph
    console.print("Constructing DAG...")

    # construct the DAG
    G = nx.DiGraph()

    G.add_edges_from(edges)

    console.print(f"Total Nodes:  {len(G)}")
    console.print(f"Degree:       {len(G.degree)}")
    console.print(f"Degree (in):  {len(G.in_degree)}")
    console.print(f"Degree (out): {len(G.out_degree)}")

    sub_graph = create_sub_graph(G, incoming_limit=1, outgoing_limit=0)

    # -----
    # Plot the Graph

    console.print("Plotting Graph...")

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_axes((0, 0, 1, 1))

    g_plot = sub_graph

    # https://networkx.org/documentation/stable//reference/drawing.html#module-networkx.drawing.layout
    # Other graph options
    # kamada_kawai_layout, # this works well <- requires scipy to be installed
    # shell_layout
    # circular_layout
    # planar_layout
    # spiral_layout
    # spring_layout

    nx.draw_networkx(
        g_plot,
        ax=ax,
        pos=nx.spring_layout(g_plot),
        with_labels=True,
        font_size=10,
        font_weight="bold",
    )

    plt.show()
