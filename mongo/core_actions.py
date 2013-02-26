#!/usr/bin/env python


from bson.objectid import ObjectId

from constants import *

from tornado import database
import datetime
from collections import defaultdict
import user_actions

import pymongo


def tree(): return defaultdict(tree)
def dicts(t): return {k: dicts(t[k]) for k in t}
# def post_wall(db,mc,userid,friendid,message):

# 	post = { '_id' : ObjectId(), 'FriendId' : ObjectId(friendid), 'Message' : message, 'Time' : datetime.datetime.now()}

# 	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

# 	return RespSuccess.DEFAULT_SUCCESS

def post_replyWall(db,mc,userid,commenter,message):
	post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter), 'Message' : message, 'Time' : datetime.datetime.now()}

	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

	return RespSuccess.DEFAULT_SUCCESS

def post_wall(db,mc,userid,message,commenter=None, postid=None,replyid = None,depth=1):
	#TODO : leave link(id) to parent
	if postid is None:
		fid = -1
		if commenter != None:
			fid = ObjectId(commenter)
		post = {'_id' : ObjectId(),'FriendId' : fid, 'UserId' : ObjectId(userid), 'Message' : message, 'Time' : datetime.datetime.now()}
		db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})
	else:
		if replyid is None:
			replyid = postid
		push_rstr = 'Wall' + ('.$.Reply' )
		post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter), 'ParentId' : ObjectId(replyid),'Message' : message, 'Time' : datetime.datetime.now(), 'Depth' : 1}
		print db.user.update({'Wall._id' : ObjectId(postid),'_id' : ObjectId(userid)},{'$push' : { push_rstr : post}})

	# else:
	# 	push_rstr = 'Wall' + ('.$.Reply' )
	# 	print push_rstr
	# 	post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter),'ParentId' : ObjectId(replyid), 'Message' : message, 'Time' : datetime.datetime.now(),'Depth' : depth}
	# 	print db.user.update({'Wall._id' : ObjectId(postid),'_id' : ObjectId(userid)},{'$push' : { push_rstr : post}})
		# find_rstr = 'Wall' + ('.Reply' * (depth-1)) + '._id'
		# push_rstr = 'Wall' + ('.$.Reply' * (depth-1)) + '.$.Reply'
		# print find_rstr
		# print push_rstr
		# post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter),'ParentId' : ObjectId(replyid), 'Message' : message, 'Time' : datetime.datetime.now(),'Depth' : depth}
		# q = {'Wall._id' : ObjectId(postid),find_rstr : ObjectId(replyid),'_id' : ObjectId(userid)},{'$push' : { push_rstr : post}}
		# print q
		# print db.user.update({'Wall._id' : ObjectId(postid),find_rstr : ObjectId(replyid),'_id' : ObjectId(userid)},{'$push' : { push_rstr : post}})

	return RespSuccess.DEFAULT_SUCCESS


def get_replies(db,userid,postid,orderBy = None):
	reps = db.user.find({'_id' : userid, 'Wall._id' : postid},{'Wall.Reply' : 1})['Wall']['Reply']

def build_tree(lst,parentid,tree = {}):
	for node in lst:
		pid = node['ParentId']
		lst = tree.get(pid, [])
		lst.append(node)
		tree[pid] = lst
	return tree

def print_graph(graph,parentid,depth = 0):
	lst = graph.get(parentid)
	if lst != None:
		for node in lst :
			indent = ('   ' * depth)
			print indent + str(node)
			print_graph(graph,node['_id'],depth+1)



def get_posts(db,userid,orderBy = None, numResults=20, startNum = 1):
	
	try:
		wall = db.user.find_one({'_id' : ObjectId(userid)}, {'Wall' : 1, '_id' : 0})['Wall']

	except Exception, e:
		print e
	
	return wall
	

if __name__ == "__main__":
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="root")
	#user = {'UserID' : 5, 'UserName' : "jillian"}
	db = pymongo.MongoClient().uplace
	#post_wall(db,None,'511747a18f24a0069b7ed655','511747a18f24a0069b7ed655','hey how are you? testing replies 2')

	#post_wall(db,None,'5119cf32decedf8257ef6acf','This post sucks test!','511747a18f24a0069b7ed655','512a48518f24a04b77946888','512a49548f24a04b9b74ad6b',2)

	node1 = {'_id' : 2, 'ParentId' : 1}
	node2 = {'_id' : 3, 'ParentId' : 1}
	node3 = {'_id' : 4, 'ParentId' : 1}
	node4 = {'_id' : 5, 'ParentId' : 1}
	node5 = {'_id' : 6, 'ParentId' : 2}
	node6 = {'_id' : 7, 'ParentId' : 2}
	node7 = {'_id' : 8, 'ParentId' : 7}
	node8 = {'_id' : 9, 'ParentId' : 4}
	nodes = [node1,node2,node3,node4,node5,node6,node7,node8]
	t = build_tree(nodes,1)
	print t
	print_graph(t,1)


#	post_replyReply(db,None,'511747a18f24a0069b7ed655','5119cf32decedf8257ef6acf','512863be8f24a049f1935578',,'testing10')
	#post_reply
	#print get_posts(db,"511747a18f24a0069b7ed655")
	#print post_wall(db,None,user,5,'hey how are you?')