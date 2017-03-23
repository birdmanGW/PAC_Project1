import tweepy #https://github.com/tweepy/tweepy
import time
import collections
import networkx as nx
from networkx.readwrite import json_graph
import json
import sys

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


def makeNode(userID):
    #get user basic profile
    getuser = api.get_user(userID)
    #get user id
    user_id = getuser.id
    #get user screen name(username)
    screen_name = getuser.screen_name
    #get name
    user_name = (getuser.name).encode("ascii", "replace")
    #create node in tree
    node = Node(user_id, screen_name, user_name)
    #return node

    print user_name
    #print "The user's name is:  ", user_name
    # print "The screenname(username) is:  ", screen_name
    # print "The userID is:  ", user_id
    # print "The user's friend list is:  ", friendList

    return node

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



#id/user_id/screen_name
def buildTwitterTree(G, root):
    global counter
    global waitlist
    counter += 1
    if counter > 15:
        print "15 friend lists reached."
        print "waiting 15 minutes...."
        time.sleep(900)
        counter = 1

    #try and get users friends list
    try:
        friendList = api.friends_ids(root.user_id)
    #exception when aunauthorized tweets enabled
    except tweepy.TweepError:
        print("Failed to run the command on that user, Skipping...")
        print "waiting 15 minutes...."
        time.sleep(900)
        #pop first node from waitlist: friends found and added to tree
        waitlist.pop(0)
        #recursively call function
        buildTwitterTree(G, waitlist[0])

    friend_num = 0
    #iterate through friends list, add to children of node
    for friendID in friendList:
        friend_num += 1
        if friend_num > 50:
            break

        #wait counter to circumvent tweepy user rate limit
        #every n values in waitlist, wait 15 minutes
        if len(waitlist) >= 2000:
            return

        #if len(waitlist) % 700 == 0:

        #    print "waiting 15 minutes...."
        #    time.sleep(900)
        #make friend node
        friend = makeNode(friendID)
        #add friend as child
        #node.add_child(friend)
        #make node friends parent
        #friend.parent = node
        #Add friend to waitlist
        waitlist.append(friend)
        G.add_node(friend)
        G.add_edge(root, friend)
        #debug
        # print "Waitlist.length: %d" % len(waitlist)

    #if waitlist length over 1000 values
    if len(waitlist) >= 2000:
        return

    #pop first node from waitlist: friends found and added to tree
    # Maybe should use queue instead
    waitlist.pop(0)

    #recursively call function
    buildTwitterTree(G, waitlist[0])


def breadth_first_search(graph, root):
    visited, queue = set(), collections.deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

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

#define root user_id
root_id = ""
#make root
root = makeNode(root_id)
#First add root to waitlist
waitlist.append(root)

#debug
print "Waitlist.length: %d" % len(waitlist)

counter = 0
G = nx.DiGraph()
G.add_node(root)
buildTwitterTree(G, root)
print("done")
#start recursivly building tree
#Tree = buildTwitterTree(root);

#Tree is root of node at the end of constructing tree

# Export graph
nx.write_yaml(G, "")
