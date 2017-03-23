import networkx as nx
import networkx.drawing as drawing
import matplotlib.pyplot as plt
import numpy

from find_k_clique_seed import find_k_clique_seed

class Node:
#Class to create and form nodes: storing user_id, screen_name, and user_name
    def __init__(self, user_id, screen_name, user_name):
        self.user_id = user_id
        self.screen_name = screen_name
        self.user_name = user_name
        #self.parent = parent
        #self.children = []

    #def add_child(self, child):
        #self.children.append(child)

    def isLeaf(self):
        return len(self.children) == 0

    def findRoot(node):
        p = node
        while p.parent != None:
            p = p.parent
        return p


def invert_mapping(mapping):
    return {v: k for k, v in mapping.iteritems()}


def propagation_step(lgraph, rgraph, mapping, theta=0.1):
    scores = {}

    for lnode in lgraph.nodes():
        scores[lnode] = match_scores(lgraph, rgraph, mapping, lnode)

        if eccentricity(scores[lnode]) < theta:
            continue

        rnode = next(
            x for x in rgraph.nodes() if
            scores[lnode][x] == max(scores[lnode]))

        scores[rnode] = match_scores(
            rgraph, lgraph, invert_mapping(mapping), rnode)

        if eccentricity(scores[rnode]) < theta:
            continue

        reverse_match = next(
            x for x in lgraph.nodes() if
            scores[rnode][x] == max(scores[rnode]))

        if reverse_match != lnode:
            continue

    mapping[lnode] = rnode


def match_scores(lgraph, rgraph, mapping, lnode):
    scores = {}

    for rnode in rgraph:
        scores[rnode] = 0

    for (lnbr, lnode) in lgraph.edges():
        if lnbr not in mapping:
            continue
        rnbr = mapping[lnbr]

        for (r, rnode) in rgraph.edges():
            if r == rnbr or rnode in mapping:
                continue
            scores[rnode] += 1 / rgraph.in_degree(rnode) ^ 0.5

    for (lnode, lnbr) in lgraph.edges():
        if lnbr not in mapping:
            continue
        rnbr = mapping[lnbr]

        for (rnode, r) in rgraph.edges():
            if r == rnbr or rnode in mapping:
                continue
            scores[rnode] += 1 / rgraph.out_degree(rnode) ^ 0.5

    return scores


def eccentricity(items):
    max_value = max(items.iterkeys(), key=(lambda key: items[key]))

    without_max = dict(items)
    del without_max[0]

    return (
        (max(items) - max(items.remove(max(items)))) /
        numpy.std(items, ddof=1))


if __name__ == "__main__":
    G = nx.read_yaml("")

    mapping = find_k_clique_seed(G, G, 3, e=0.1)
    print(mapping)
    # drawing.draw(G)
    # plt.show()

    for i in range(100):
        propagation_step(G, G, mapping)