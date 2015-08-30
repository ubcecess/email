from urllib import urlencode
import webbrowser

import click

from ecessprivate.forwarders import forwarders
from ecessemail.existing_forwarders import  get_existing_forwarders


@click.group()
def cli():
    pass


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
def draw_graph(dataset, root):
    """Draw a directed graph of forwarding"""
    import networkx as nx
    import matplotlib.pyplot as plt

    def edges_to_adj_map(edges):
        from collections import defaultdict
        map = defaultdict(list)
        for vertex, neighbour in edges:
            map[vertex].append(neighbour)
        return dict(map)

    def visit_children(G, adj_map, root):
        stack = [root]
        while stack:
            node = stack.pop()
            neighbours = adj_map.get(node, [])
            stack.extend(neighbours)
            for neighbour in neighbours:
                G.add_edge(node, neighbour)

    G = nx.DiGraph()
    if dataset == "desired":
        for vertex, neighbours in forwarders.items():
            for neighbour in neighbours:
                if root is None or vertex == root:
                    G.add_edge(vertex, neighbour)
    elif dataset == "current":
        if root is None:
            for vertex, neighbour in existing_forwarders:
                G.add_edge(vertex, neighbour)
        else:
            adj_map = edges_to_adj_map(existing_forwarders)
            visit_children(G, adj_map, root)

    pos = nx.spring_layout(G, k=0.2)  # positions for all nodes
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=1)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    plt.axis('off')
    plt.show()


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
def existing_fwd():
    """Print existing forwarders as per forwarders.html"""
    for fwd in existing_forwarders:
        print(fwd)


@cli.command()
def diff_forwarders():
    """Print list of extra forwarders in current that should be removed
    as per desired
    """
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
    cli()
