import tweepy #https://github.com/tweepy/tweepy
import time
import collections
import networkx as nx
from networkx.readwrite import json_graph
import sys
import os

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


def buildTwitterTree(G, root, waitlist, f_l_count, count):
    total = 10000

    f_l_count += 1
    if f_l_count > 15:
        print "15 friend lists reached."
        print "waiting 15 minutes...."
        time.sleep(900)
        f_l_count = 1

    #try and get users friends list
    try:
        friendList = api.friends_ids(root)
    #exception when aunauthorized tweets enabled
    except tweepy.TweepError as e:
        print(e)
        print("Failed to run the command on that user, Skipping...")
        print "waiting 15 minutes...."
        time.sleep(900)
        #pop first node from waitlist: friends found and added to tree
        waitlist.pop(0)
        #recursively call function
        buildTwitterTree(G, waitlist[0], waitlist, f_l_count, count)
        return

    friend_num = 0
    #iterate through friends list, add to children of node
    for friend in friendList:
        friend_num += 1
        count += 1

        if count % 100 == 0:
            print(count)

        if friend_num > 50:
            break

        if count >= total:
            return

        waitlist.append(friend)
        G.add_node(friend)

        G.add_edge(root, friend)

    if count >= total:
        return

    #pop first node from waitlist: friends found and added to tree
    # Maybe should use queue instead
    waitlist.pop(0)

    #recursively call function
    buildTwitterTree(G, waitlist[0], waitlist, f_l_count, count)

#Twitter API credentials - ADD HERE
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

#Create waitlist of userid's
waitlist = []

#make root
root = api.get_user(sys.argv[1]).id
#First add root to waitlist
waitlist.append(root)

#debug
#print "Waitlist.length: %d" % len(waitlist)

counter = 0
G = nx.DiGraph()
G.add_node(root)
buildTwitterTree(G, root, waitlist, 1, 1)
print("done")


# Export graph
nx.write_yaml(G, os.getcwd() + "/" + sys.argv[2])
