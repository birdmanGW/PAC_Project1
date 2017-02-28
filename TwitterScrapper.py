import tweepy #https://github.com/tweepy/tweepy
import time
import collections

class Node:
#Class to create and form nodes: storing user_id, screen_name, and user_name
	def __init__(self, user_id, screen_name, user_name, parent):
		self.user_id = user_id
		self.screen_name = screen_name
		self.user_name = user_name
		self.parent = parent
		self.children = []

	def add_child(self, child):
		self.children.append(child)

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
	user_name = str(getuser.name)
	#create node in tree
	node = Node(user_id, screen_name, user_name, None)
	#return node
	'''
	print "The user's name is:  ", user_name
	print "The screenname(username) is:  ", screen_name    
	print "The userID is:  ", user_id
	print "The user's friend list is:  ", friendList
	'''
	return node



#id/user_id/screen_name
def buildTwitterTree(node):
	#try and get users friends list
	try:
		friendList = api.friends_ids(node.user_id)
	#exception when aunauthorized tweets enabled
	except tweepy.TweepError:
		print("Failed to run the command on that user, Skipping...")
		#pop first node from waitlist: friends found and added to tree
		waitlist.pop(1)
		#recursively call function
		buildTwitterTree(waitlist[1])

	#iterate through friends list, add to children of node
	for friendID in friendList:
		#wait counter to circumvent tweepy user rate limit
		#every 3 values in waitlist, wait 15 minutes
		if len(waitlist) % 3 == 0:
			print "waiting 10 minutes ZZzz...."
			time.sleep(600)
		#make friend node
		friend = makeNode(friendID)
		#add friend as child
		node.add_child(friend)
		#make node friends parent
		friend.parent = node
		#Add friend to waitlist
		waitlist.append(friend)
		#debug
		print "Waitlist.length: %d" % len(waitlist)

	#if waitlist.length over 1000 values
	if waitlist.length > 2000:
		return node.findRoot(node)

	#pop first node from waitlist: friends found and added to tree
	waitlist.pop(1)

	#recursively call function
	buildTwitterTree(waitlist[1])


def breadth_first_search(graph, root): 
	visited, queue = set(), collections.deque([root])
	while queue: 
		vertex = queue.popleft()
		for neighbour in graph[vertex]: 
			if neighbour not in visited: 
				visited.add(neighbour) 
				queue.append(neighbour)

#Twitter API credentials
consumer_key = "qktHTVzU7eswKWL4YCEbPjIsE"
consumer_secret = "qYvvQI6gvyzpRfjg8drQyZ6hn92IX8bhTjRSw0Q9tCiYZE14KP"
access_key = "1379713122-zCUb2JK1VHEftSBpj0HP8zNN5TdWRms3Z3s0Nsz"
access_secret = "giPm8QyuKGCN05jztsXHWVeNEM9aMuAvNaDfaMgX8fUxv"

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

#Create waitlist of userid's
waitlist = []

#define root user_id
root_id = 2831170162
#make root
root = makeNode(root_id)
#First add root to waitlist
waitlist.append(root);

#debug
print "Waitlist.length: %d" % len(waitlist)

#start recursivly building tree
Tree = buildTwitterTree(root);

#Tree is root of node at the end of constructing tree

