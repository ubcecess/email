#!/usr/bin/env python

from urllib import urlencode
import webbrowser

import click

from ecessprivate.forwarders import forwarders
from ecessemail.existing_forwarders import  get_existing_forwarders


FORWARDERS_HTML = "forwarders_html"


@click.group()
@click.option("-f", "--forwarders-html")
@click.pass_context
def cli(ctx, forwarders_html):
    if forwarders_html is not None:
        ctx.obj[FORWARDERS_HTML] = forwarders_html


@cli.command()
@click.argument("dest", type=click.STRING)
def recipients(dest):
    """Prints final recipients for a mail that gets sent to a forwarder"""
    leaves = set()
    stack = [dest]
    while stack:
        node = stack.pop()
        children = forwarders.get(node)
        if children is None:
            leaves.add(node)
        else:
            stack.extend(children)

    for leaf in sorted(leaves):
        print(leaf)


@cli.command()
@click.option('-d', "--dataset", required=True,
              type=click.Choice(["desired", "current"]))
@click.option('-r', '--root', required=False, type=click.STRING)
@click.option('-g', '--gp', help='Graphing package to use',
              default="gv", type=click.Choice(["gv", "nx"]))
@click.pass_context
def draw_graph(ctx, dataset, root, gp):
    """Draw a directed graph of forwarding"""
    import networkx as nx
    import matplotlib.pyplot as plt
    from graphviz import Digraph

    def edges_to_adj_map(edges):
        from collections import defaultdict
        map = defaultdict(list)
        for vertex, neighbour in edges:
            map[vertex].append(neighbour)
        return dict(map)

    def visit_children(G, adj_map, root, add_edge):
        stack = [root]
        while stack:
            node = stack.pop()
            neighbours = adj_map.get(node, [])
            stack.extend(neighbours)
            for neighbour in neighbours:
                add_edge(G, node, neighbour)

    if gp == "nx":
        G = nx.DiGraph()
        add_edge = lambda G, a, b: G.add_edge(a, b)
    elif gp == "gv":
        G = Digraph()
        add_edge = lambda G, a, b: G.edge(a, b)
    else:
        raise Exception

    if dataset == "desired":
        for vertex, neighbours in forwarders.items():
            for neighbour in neighbours:
                if root is None or vertex == root:
                    add_edge(G, vertex, neighbour)
    elif dataset == "current":
        existing_forwarders = get_existing_forwarders(ctx.obj[FORWARDERS_HTML])
        if root is None:
            for vertex, neighbour in existing_forwarders:
                add_edge(G, vertex, neighbour)
        else:
            adj_map = edges_to_adj_map(existing_forwarders)
            visit_children(G, adj_map, root, add_edge)

    if gp == "nx":
        # pos = nx.spring_layout(G, k=0.2)  # positions for all nodes
        pos = nx.graphviz_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=200)
        nx.draw_networkx_edges(G, pos, width=0.5, alpha=1)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

        plt.axis('off')
        plt.show()
    elif gp == "gv":
        G.render("graph.gv", view=True)


@cli.command()
@click.argument("filename", type=click.Path())
def write_csv(filename):
    """Write CSV of desired entries"""
    forwarder_entries = [
        (f, t) for f, ts in forwarders.items() for t in ts
    ]
    import csv
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(forwarder_entries)


@cli.command()
@click.pass_context
def existing_fwd(ctx):
    """Print existing forwarders as per forwarders.html"""
    existing_forwarders = get_existing_forwarders(ctx.obj[FORWARDERS_HTML])

    for fwd in existing_forwarders:
        print(fwd)


@cli.command()
@click.pass_context
def diff_forwarders(ctx):
    """Print list of extra forwarders in current that should be removed
    as per desired
    """
    existing_forwarders = get_existing_forwarders(ctx.obj[FORWARDERS_HTML])

    forwarder_entries = {
        (f, t) for f, ts in forwarders.items() for t in ts
    }
    header = "Forwarders to Remove"
    print("{}\n{}".format(header, len(header)*"-"))
    for e in sorted(set(existing_forwarders) - forwarder_entries):
        print(e)
    header = "Forwarders to Add"
    print("{}\n{}".format(header, len(header)*"-"))
    for e in sorted(forwarder_entries - set(existing_forwarders)):
        print(e)


def _delete_forwarder(f, t, cpsess, confirm=True):
    URL = "https://secure152.sgcpanel.com:2083/{}/frontend/" \
          "Crystal/mail/dodelfwd{}.html".format(
        cpsess,
        "confirm" if confirm else ""
    )
    params = {
        "email": f,
        "emaildest": t
    }
    url = "{}?{}".format(URL, urlencode(params))
    webbrowser.open(url)


if __name__ == '__main__':
    cli(obj={})
