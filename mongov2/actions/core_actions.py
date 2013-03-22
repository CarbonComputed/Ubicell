#!/usr/bin/env python


from bson.objectid import ObjectId

from constants import *

from tornado import database
import datetime
from collections import defaultdict
import user_actions

from util import *
import pymongo

from multiprocessing import Process, Lock, Condition

import re

from models.School import *
from models.University import *
from models.Post import *
from models.ProfileImage import * 
from models.Reply import *
from models.User import *
import logging
from util import *

logger = logging.getLogger(__name__)

def tree(): return defaultdict(tree)
def dicts(t): return {k: dicts(t[k]) for k in t}

lock_table = {}

lockTableLock = Lock()
postLock = Condition()
# def post_wall(db,mc,userid,friendid,message):

# 	post = { '_id' : ObjectId(), 'FriendId' : ObjectId(friendid), 'Message' : message, 'Time' : datetime.datetime.now()}

# 	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

# 	return RespSuccess.DEFAULT_SUCCESS

def post_replyWall(db,mc,userid,commenter,message):
	post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter), 'Message' : message, 'Time' : datetime.datetime.now()}

	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

	return RespSuccess.DEFAULT_SUCCESS

def post_wall(userid,message,commenter=None, postid=None,replyid = None,depth=1):
	#TODO : leave link(id) to parent
	if postid is None:
		hotness = ranking.hot(1,0,datetime.datetime.now())

		fid = userid #default writing on own wall
		if commenter != None:
			fid = commenter #someone writing on my wall

		post = Post(id=ObjectId(),FriendId=fid,UserId=userid,Message=message,Time=datetime.datetime.now(),
			Hotness=hotness,Upvotes=1,Downvotes=0,Upvoters=[fid],Downvoters=[])
		user = User.objects(id=userid).first()
		#print userid,user.to_mongo()
		user.Wall.append(post)
		user.save()
		# post = {'_id' : ObjectId(),'FriendId' : fid, 'UserId' : ObjectId(userid), 'Message' : message, 'Time' : datetime.datetime.now(),
		# 'Hotness' : hotness,  'Upvotes' : 1, 'Downvotes' : 0,'Upvoters' : [fid],'Downvoters' : []}
		# db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})
	else:
		if commenter is None:
			return RespError.DEFAULT_ERROR
		confidence = ranking.confidence(1,0)
		if replyid is None:
			replyid = postid  #first set of comments 
		push_rstr = 'Wall' + ('.$.Reply' )
		reply = Reply(id=ObjectId(),ParentId=replyid,UserId=commenter,Message=message,Time=datetime.datetime.now(),
			Hotness=confidence,Upvotes=1,Downvotes=0,Upvoters=[commenter],Downvoters=[])
		user = User.objects(id=userid).first()
		print user.Wall
		post = funcs.find(user.Wall,'id',ObjectId(postid))
		post.Reply.append(reply)
		
		user.save()

		#post = {'_id' : ObjectId(), 'UserId' : ObjectId(commenter), 'ParentId' : ObjectId(replyid),'Message' : message, 'Time' : datetime.datetime.now(), 'Depth' : 1,'Hotness' : confidence, 'Upvotes' : 1, 'Downvotes' : 0,'Upvoters' : [ObjectId(commenter)],'Downvoters' : []}
		#print db.user.update({'Wall._id' : ObjectId(postid),'_id' : ObjectId(userid)},{'$push' : { push_rstr : post}})

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


def upvote_post(ownerid,userid,postid):
	user = User.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = user.Wall
	post = funcs.find(userwall,'id',ObjectId(postid))
	
	upvotes = post.Upvotes
	downvotes = post.Downvotes
	upvoters = post.Upvoters
	downvoters = post.Downvoters
	if ObjectId(userid) in upvoters:
		return UpvoteResp.VOTED_ALREADY
	user.Wall.remove(post)
	upvotes += 1
	if ObjectId(userid) not in downvoters:
		upvoters.append(ObjectId(userid))
	try:
		downvoters.remove(ObjectId(userid))
	except ValueError:
		pass
	hotness = ranking.hot(upvotes,downvotes,datetime.datetime.now())
	post.Upvoters = upvoters
	post.Downvoters = downvoters
	post.Upvotes = upvotes
	post.Downvotes = downvotes
	post.Hotness = hotness

	
	user.Wall.append(post)
	user.save()
	#post = User.objects(id=userid['$oid'],Wall__id=ObjectId(postid)).first()
	
	return 200
# def upvote_post(userid,postid):
# 	coll = User._get_collection()
# 	postLock.acquire()
# 	try:
# 		while lock_table.get(postid,False) is True:
# 			postLock.wait(500)

# 		lock_table[postid] = True
# 	finally:
# 		postLock.release()
# 	check = coll.find_one({ 'Wall._id' : ObjectId(postid)},{'Wall.$' : 1})
	
# 	if check is None:
# 		postLock.acquire()

# 		try:

# 			lock_table[postid] = False
# 			postLock.notify()
# 		finally:
# 			postLock.release()

# 		return RespError.DEFAULT_ERROR
# 	if ObjectId(userid) in check['Wall'][0]['Upvoters']:
# 		postLock.acquire()

# 		try:

# 			lock_table[postid] = False
# 			postLock.notify()
# 		finally:
# 			postLock.release()

# 		return UpvoteResp.VOTED_ALREADY
# 	post = check['Wall'][0]
# 	upvotes = post['Upvotes']
# 	downvotes = post['Downvotes']
# 	upvotes = upvotes + 1
# 	upvoters = post['Upvoters']
# 	if ObjectId(userid) not in check['Wall'][0]['Downvoters']:
# 		upvoters.append(ObjectId(userid))
# 	downvoters = post['Downvoters']
# 	try:
# 		downvoters.remove(ObjectId(userid))
# 	except ValueError:
# 		pass
# 	hotness = ranking.hot(upvotes,downvotes,datetime.datetime.now())
# 	coll.update({ 'Wall._id' : ObjectId(postid)},{'$set' : {'Wall.$.Hotness' : hotness,  'Wall.$.Upvotes' : upvotes, 'Wall.$.Downvotes' : downvotes,'Wall.$.Upvoters' : upvoters,'Wall.$.Downvoters' : downvoters}})
# 	postLock.acquire()
# 	try:

# 		lock_table[postid] = False
# 		postLock.notify()
# 	finally:
# 		postLock.release()


# 	return RespSuccess.DEFAULT_SUCCESS

def downvote_post(ownerid,userid,postid):
	user = User.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = user.Wall
	post = funcs.find(userwall,'id',ObjectId(postid))
	
	upvotes = post.Upvotes
	downvotes = post.Downvotes
	upvoters = post.Upvoters
	downvoters = post.Downvoters
	if ObjectId(userid) in downvoters:
		return UpvoteResp.VOTED_ALREADY
	user.Wall.remove(post)
	downvotes += 1
	if ObjectId(userid) not in upvoters:
		downvoters.append(ObjectId(userid))
	try:
		upvoters.remove(ObjectId(userid))
	except ValueError:
		pass
	hotness = ranking.hot(upvotes,downvotes,datetime.datetime.now())
	post.Upvoters = upvoters
	post.Downvoters = downvoters
	post.Upvotes = upvotes
	post.Downvotes = downvotes
	post.Hotness = hotness

	
	user.Wall.append(post)
	user.save()
	#post = User.objects(id=userid['$oid'],Wall__id=ObjectId(postid)).first()
	
	return 200

def upvote_comment(db,userid,postid,replyid):
	pass

# def downvote_post(userid,postid):
# 	coll = User._get_collection()
# 	print 'test'
# 	postLock.acquire()
# 	try:
# 		while lock_table.get(postid,False) is True:
# 			postLock.wait(500)

# 		lock_table[postid] = True
# 	finally:
# 		postLock.release()
# 	check = coll.find_one({ 'Wall._id' : ObjectId(postid)},{'Wall.$' : 1})
	
# 	if check is None:
# 		postLock.acquire()
# 		try:

# 			lock_table[postid] = False
# 			postLock.notify()
# 		finally:
# 			postLock.release()		
# 		return RespError.DEFAULT_ERROR
# 	if ObjectId(userid) in check['Wall'][0]['Downvoters']:
# 		postLock.acquire()
# 		try:

# 			lock_table[postid] = False
# 			postLock.notify()
# 		finally:
# 			postLock.release()
# 		return UpvoteResp.VOTED_ALREADY
# 	post = check['Wall'][0]
# 	upvotes = post['Upvotes']
# 	downvotes = post['Downvotes']
# 	downvotes = downvotes + 1
# 	downvoters = post['Downvoters']
# 	if ObjectId(userid) not in check['Wall'][0]['Upvoters']:
# 		downvoters.append(ObjectId(userid))
# 	upvoters = post['Upvoters']
# 	try:
# 		upvoters.remove(ObjectId(userid))
# 	except ValueError:
# 		pass
# 	hotness = ranking.hot(upvotes,downvotes,datetime.datetime.now())

# 	coll.update({ 'Wall._id' : ObjectId(postid)},{'$set' : {'Wall.$.Hotness' : hotness,  'Wall.$.Upvotes' : upvotes, 'Wall.$.Downvotes' : downvotes,'Wall.$.Downvoters' : downvoters,'Wall.$.Upvoters' : upvoters}})
# 	postLock.acquire()
# 	try:

# 		lock_table[postid] = False
# 		postLock.notify()
# 	finally:
# 		postLock.release()


# 	return RespSuccess.DEFAULT_SUCCESS

def downvote_comment(db,userid,postid,replyid):
	pass


def get_replies(userid,powner, postid,orderBy = None):
	logger.info("Retrieving Replies")
	coll = User._get_collection()
	reps = coll.find({ '_id'  : ObjectId(powner),'Wall._id' : ObjectId(postid)},{'Wall.$.Reply' : 1})[0]['Wall'][0]['Reply']
	return reps

def build_tree(lst):
	tree = {}
	for node in lst:
		pid = node['ParentId']
		print pid
		lst2 = tree.get(pid, [])
		lst2.append(node)
		tree[pid] = lst2
	return tree

def print_graph(graph,parentid,depth = 0):
	lst = graph.get(parentid)
	#sort lst by confidence
	if lst != None:
		for node in lst :
			indent = ('   ' * depth)
			print indent + str(node['Message'])
			print_graph(graph,node['_id'],depth+1)


def get_feed(userid,includeMe=True,orderBy=None,numResults=60,startNum =1):

	logger.info("Retrieving main feed")
	coll = User._get_collection()
	feed = coll.aggregate([

		{'$match' :{ '$or': [ {"_id": ObjectId(userid) }, {"Friends": ObjectId(userid) } ] } },
		{'$unwind' : "$Wall" },
		{'$sort' :  { "Wall.Hotness" : -1 }},
		{'$limit' : numResults }] )
	for field in feed['result']:
		if field != None:
			del field['Password']
	return feed

def get_user_feed(userid,orderBy=None,numResults=20,startNum =1):
	logger.info("Retrieving user feed")
	coll = User._get_collection()
	feed = coll.aggregate([

		{'$match' : {"_id": ObjectId(userid) } },
		{'$unwind' : "$Wall" },
		{'$sort' :  { "Wall.Hotness" : -1 }},
		{'$limit' : numResults }] )
	for field in feed['result']:
		if field != None:
			del field['Password']
	return feed

def get_posts(userid,orderBy = None, numResults=20, startNum = 1):
	
	try:
	#	wall = db.user.find_one({'_id' : ObjectId(userid)}, {'Wall' : 1, '_id' : 0})['Wall']
		wall = User.objects(_id=userid).only("Wall")
	except Exception, e:
		print e
	
	return wall
	

def search(userid,universityid,query,query_type = None):
	coll = User._get_collection()

	query = query.strip()
	queries = query.split()
	print queries
	if len(queries) <= 1:
		query = '^'+query.lower();
		results = coll.find({'School.University' :  ObjectId(universityid), '$or' : [ {'FirstName' : {'$regex' : query}},{'LastName' : {'$regex' : query}},{'UserName' : {'$regex' : query}}]})
	else:
		firstname = queries[0]
		lastname =  queries[1]
		fquery = '^'+firstname.lower();
		lquery = '^'+lastname.lower();

		results = coll.find({'School.University' :  ObjectId(universityid), '$or' : [ {'FirstName' : {'$regex' : fquery}},{'LastName' : {'$regex' : lquery}},{'UserName' : {'$regex' : query}}]})
	return results


if __name__ == "__main__":
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="root")
	#user = {'UserID' : 5, 'UserName' : "jillian"}
	db = pymongo.MongoClient().uplace

	post_wall(db,None,"513deb988f24a02f86542aaa","i like this reply","513deb988f24a02f86542aaa", "513f4aac407450377d9dc435","513f86a68f24a038a58d6bed")
	#res = search(db,"51379ac240745012adf2209a","51379ac240745012adf22099",'Mart')
	#print res[0]
	# #post_wall(db,None,'511747a18f24a0069b7ed655','511747a18f24a0069b7ed655','hey how are you? testing replies 2')
	# #post_wall(db,None,'5119cf32decedf8257ef6acf','This post sucks test!','511747a18f24a0069b7ed655','512a48518f24a04b77946888','512a49548f24a04b9b74ad6b',2)
	# feed =  get_feed(db,"512d83848f24a00badf60d48",numResults=2)
	# for f in feed['result']:
	# 	print f['Wall']['Message']
	
	#print get_user_feed(db,'512d3d978f24a008bc6865b9')
	#upvote_post(db,"512d83848f24a00badf60d48","513022338f24a01fb0b6c392")
	# node1 = {'_id' : 2, 'ParentId' : 1}
	# node2 = {'_id' : 3, 'ParentId' : 1}
	# node3 = {'_id' : 4, 'ParentId' : 1}
	# node4 = {'_id' : 5, 'ParentId' : 1}
	# node5 = {'_id' : 6, 'ParentId' : 2}
	# node6 = {'_id' : 7, 'ParentId' : 2}
	# node7 = {'_id' : 8, 'ParentId' : 7}
	# node8 = {'_id' : 9, 'ParentId' : 4}
	# nodes = [node1,node2,node3,node4,node5,node6,node7,node8]
	# replies = get_replies(db,"513deb988f24a02f86542aaa","513deb988f24a02f86542aaa","513f4aac407450377d9dc435")
	# t = build_tree(replies)
	# print_graph(t,ObjectId('513f4aac407450377d9dc435'))


#	post_replyReply(db,None,'511747a18f24a0069b7ed655','5119cf32decedf8257ef6acf','512863be8f24a049f1935578',,'testing10')
	#post_reply
	#print get_posts(db,"511747a18f24a0069b7ed655")
	#print post_wall(db,None,user,5,'hey how are you?')
