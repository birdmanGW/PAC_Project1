try:
    import networkx as nx
except ImportError:
    print 'Fail to import networkx! Programing terminates'
    print 'Please install by: pip install networkx'
    sys.exit()

import copy


def __find_k_cliques(G, k):
    rcl = nx.find_cliques_recursive(G)
    k_cliques_list = []
    while True:
        edge_list = []
        try:
            clique_list = next(rcl)
            if len(clique_list) != k:
                continue

            else:
                for i in range(len(clique_list)):
                    for j in range(i+1, len(clique_list)):
                        edge_list.append(G.has_edge(clique_list[i], clique_list[j]))
                        edge_list.append(G.has_edge(clique_list[j], clique_list[i]))

                if all( has_edge is True for has_edge in edge_list):
                    k_cliques_list.append(clique_list)

        except StopIteration:
            break

    if len(k_cliques_list) == 0:
        return None

    else:
        return k_cliques_list

def __calc_node_cnc(G_undirected, target_node, k_clique):
    sum_cnc = 0

    for node in k_clique:
        if target_node != node:
           sum_cnc += len(sorted(nx.common_neighbors(G_undirected, target_node, node))) - len(k_clique) + 2

    return float(sum_cnc)



def find_k_clique_seed(lgraph, rgraph, k, e):

    """Compute the k-clique seed selection

    This function is implemented based on NetworkX, please install it first!!!

    Args:
        lgraph is the left graph generated using NetworkX
        rgraph is the right graph generated using NetworkX

        k is the number of k-clique

        e is the threshold (epsilon)

    Returns:
        The list of mappings of seeds
    """

    lgraph_k_clqs = __find_k_cliques(lgraph, k)
    rgraph_k_clqs = __find_k_cliques(rgraph, k)

    lgraph_undirected = lgraph.to_undirected()
    rgraph_undirected = rgraph.to_undirected()

    ## mapping from lgraph to rgraph
    seed_mapping = dict()
    seed_mappings = []

    if lgraph_k_clqs is not None and rgraph_k_clqs is not None:
        for lgraph_k_clq in lgraph_k_clqs:
            for rgraph_k_clq in rgraph_k_clqs:
                for lnode in lgraph_k_clq:
                    for rnode in rgraph_k_clq:
                        lnode_cnc = __calc_node_cnc(lgraph_undirected, lnode, lgraph_k_clq)
                        rnode_cnc = __calc_node_cnc(rgraph_undirected, rnode, rgraph_k_clq)
                        lnode_degree = float(G.degree(lnode))
                        rnode_degree = float(G.degree(rnode))

                        if (1-e <= (lnode_cnc/rnode_cnc) <= 1+e) and \
                            (1-e <= (lnode_degree/rnode_degree) <= 1+e):
                            seed_mapping[lnode] = rnode

                if len(seed_mapping) == k:
                    seed_mappings.append(copy.copy(seed_mapping))
                    seed_mapping.clear()
                    rgraph_k_clqs.remove(rgraph_k_clq)
                    lgraph_k_clqs.remove(lgraph_k_clq)
                    break

        return seed_mappings

    else:
        print 'No k-cliques have been found'



'''An Example of how to use the function'''
if __name__ == '__main__':
    G = nx.DiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_node(6)

    G.add_edge(1, 2)
    G.add_edge(2, 1)
    G.add_edge(1, 3)
    G.add_edge(3, 1)
    G.add_edge(2, 3)
    G.add_edge(3, 2)

    G.add_edge(2, 4)
    G.add_edge(3, 4)
    G.add_edge(2, 5)
    G.add_edge(3, 5)

    G.add_edge(1, 6)
    G.add_edge(3, 6)

    print find_k_clique_seed(lgraph=G, rgraph=G, k=3, e=0.1)
