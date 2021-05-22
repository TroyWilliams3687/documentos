#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) <year> <copyright holders>

# uuid       =
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       =
# -----------

"""
"""

# ------------
# System Modules - Included with Python

import logging

from pathlib import Path

# ------------
# 3rd Party - From pip

import click
import networkx as nx
import matplotlib.pyplot as plt

# ------------
# Custom Modules

from md_docs.document import (
    MarkdownDocument,
    LSTDocument,
    reverse_relative_links,
    search,
)

# -------------
# Logging

log = logging.getLogger(__name__)

# -------------


def create_sub_graph(G, incoming_limit=1, outgoing_limit=0):
    """
    Given the DAG, return a sub-graph where the nodes have the incoming and outgoing
    connections.

    """

    sub_graph = nx.DiGraph()

    # find the nodes that only have one incoming edge and 0 outgoing
    for n in G.nodes:

        incoming = G.in_edges(nbunch=n)
        outgoing = G.out_edges(nbunch=n)

        # is_referenced = len(G.in_edges(nbunch=n))

        if len(incoming) == incoming_limit and len(outgoing) == outgoing_limit:
            log.debug(
                f"node: {n} -> Incoming = {len(incoming)}; Outgoing = {len(outgoing)}"
            )

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

    Given the LST file, find all the Markdown files associated
    with it and display the network graph showing links.

    # Usage

    $ docs --config=./en/config.common.yaml graph ./en/documents/all.lst

    """

    # Extract the configuration file from the click context
    config = args[0].obj["cfg"]

    # the LST file could be passed in as a relative path. We resolve it
    # to an absolute path.

    # lst = Path(kwargs['lst']).resolve()
    lst = LSTDocument(Path(kwargs["lst"]).resolve())

    log.info("Searching for Markdown files...")

    md_files = search(root=config["documents.path"])

    log.info(f"{len(md_files)} markdown files were found...")

    # Gather all Markdown files from the LST
    lst_contents = []

    for f in lst.links:
        lst_contents.append(MarkdownDocument(f))

    lst_contents = list(set(lst_contents))  # remove duplicates

    log.info(f"{len(lst_contents)} markdown files were in {lst.filename}...")

    # To construct the graph, we only need the relative paths to the Markdown files
    # stored in an efficient structure

    md_links = reverse_relative_links(lst_contents, root=config["documents.path"])

    edges = construct_edges(lst_contents, md_links, root=config["documents.path"])

    # At this point we have edges, we can construct the graph
    log.info("Constructing DAG...")

    # construct the DAG
    G = nx.DiGraph()

    G.add_edges_from(edges)

    # print(f'Total Nodes: {len(G)}')
    # print(f'Degree: {len(G.degree)}')
    # print(f'Degree (in): {len(G.in_degree)}')
    # print(f'Degree (out): {len(G.out_degree)}')

    sub_graph = create_sub_graph(G, incoming_limit=1, outgoing_limit=0)

    # -----
    # Plot the Graph

    log.info("Plotting Graph...")

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_axes((0, 0, 1, 1))

    g_plot = sub_graph

    # https://networkx.org/documentation/stable//reference/drawing.html#module-networkx.drawing.layout
    nx.draw_networkx(
        g_plot,
        ax=ax,
        # pos=nx.kamada_kawai_layout(g_plot), # this works well
        # pos=nx.shell_layout(G),
        pos=nx.spring_layout(g_plot),
        # pos=nx.circular_layout(g_plot),
        # pos=nx.planar_layout(g_plot),
        # pos=nx.spiral_layout(g_plot),
        with_labels=True,
        font_size=10,
        font_weight="bold",
    )

    plt.show()
