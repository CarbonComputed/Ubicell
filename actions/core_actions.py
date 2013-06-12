#!/usr/bin/env python


from bson.objectid import ObjectId

from constants import *

import datetime
from collections import defaultdict
from . import user_actions

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
from models.Club import *
import logging
from util import *
import threading


logger = logging.getLogger(__name__)


def tree(): return defaultdict(tree)
def dicts(t): return {k: dicts(t[k]) for k in t}

lock_table = {}

lockTableLock = threading.Lock()
postCV = threading.Condition()
# def post_wall(db,mc,userid,friendid,message):

# 	post = { '_id' : ObjectId(), 'FriendId' : ObjectId(friendid), 'Message' : message, 'Time' : datetime.datetime.now()}

# 	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

# 	return RespSuccess.DEFAULT_SUCCESS


# @funcs.run_async

class SearchQuery():
	Users = None
	Clubs = None

def post_wall(userid,message,commenter=None,networkid=None,depth=1,callback=None):
	#TODO : leave link(id) to parent
	hotness = ranking.hot(1,0,datetime.datetime.now())

	fid = userid #default writing on own wall
	if commenter != None:
		fid = commenter #someone writing on my wall

	post = Post(FriendId=fid,UserId=userid,Message=message,Time=datetime.datetime.now(),
		Hotness=hotness,Upvotes=1,Downvotes=0,NetworkId=networkid)
	user = User.objects(id=fid).first()
	post.save()
	logger.debug('Postid = '+str(post.id))
	user.Votes[str(post.id).lower()] = 1
	user.save()
	logger.debug(user)
	if callback != None:
		return callback(RespSuccess.DEFAULT_SUCCESS)
	return RespSuccess.DEFAULT_SUCCESS

def post_reply(userid,message,postid,replyid=None,callback=None):
	confidence = ranking.confidence(1,0)
	if replyid is None:
		replyid = postid  #first set of comments 
	
	reply = Reply(id=ObjectId(),ParentId=replyid,UserId=userid,Message=message,Time=datetime.datetime.now(),
		Hotness=confidence,Upvotes=1,Downvotes=0)
	user = User.objects(id=userid).first()
	reply.id = str(reply.id).lower()
	user.Votes[reply.id] = 1
	post = Post.objects(id=postid).first()
	post.Reply.append(reply)
	
	post.save()
	user.save()
	if callback != None:
		return callback(RespSuccess.DEFAULT_SUCCESS)
	return RespSuccess.DEFAULT_SUCCESS

def upvote_post(userid,postid,callback = None):
	postid = str(postid).lower()

	user = User.objects(id=userid).first()
	vote = user.Votes.get(postid,None)
	print vote
	print postid
	print user.Votes
	# return
	post = Post.objects(id=postid).first()
	if vote == None:
		user.Votes[postid] = 1
		Post.objects(id=postid).update(inc__Upvotes=1)
	elif vote == 0:
		user.Votes[postid] = 1
		Post.objects(id=postid).update(inc__Upvotes=1)
	elif vote == -1:
		user.Votes[postid] = 0
		Post.objects(id=postid).update(inc__Downvotes=-1)
	elif vote == 1:
		logger.debug('Already voted')
		if callback != None:
			return callback(500)
		return 500
	hotness = ranking.hot(post.Upvotes,post.Downvotes,post.Time)
	Post.objects(id=postid).update(set__Hotness=hotness)
	# post.save()
	user.save()
	if callback != None:
		return callback(500)
	return 500

def downvote_post(userid,postid,callback = None):
	postid = str(postid).lower()
	user = User.objects(id=userid).first()
	vote = user.Votes.get(postid,None)
	post = Post.objects(id=postid).first()
	if vote == None:
		user.Votes[postid] = -1
		Post.objects(id=postid).update(inc__Downvotes=1)

	elif vote == 0:
		user.Votes[postid] = -1
		Post.objects(id=postid).update(inc__Downvotes=1)

	elif vote == 1:
		user.Votes[postid] = 0
		Post.objects(id=postid).update(inc__Upvotes=-1)

	elif vote == -1:
		logger.debug('Already voted')
		if callback != None:
			return callback(500)
		return 500
	hotness = ranking.hot(post.Upvotes,post.Downvotes,post.Time)
	Post.objects(id=postid).update(set__Hotness=hotness)

	user.save()
	if callback != None:
		return callback(200)
	return 200

def upvote_comment(userid,postid,replyid,callback = None):
	user = User.objects(id=userid).first()
	postid = str(postid).lower()
	replyid = str(replyid).lower()

	vote = user.Votes.get(replyid,None)
	coll = Post._get_collection()
	reply = coll.find({'_id' : ObjectId(postid),'Reply.id' : ObjectId(replyid)},{'_id' : 0,'Reply.$' : 1})
	if reply == None:
		if callback != None:
			return callback(500)
		return 500
	upvotes = reply[0]['Reply'][0]['Upvotes']
	downvotes = reply[0]['Reply'][0]['Downvotes']
	#print reply.Upvotes
	if vote == None:
		user.Votes[replyid] = 1
		# post.Upvotes += 1
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Upvotes=1)
	elif vote == 0:
		user.Votes[replyid] = 1
		# post.Upvotes += 1
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Upvotes=1)

	elif vote == -1:
		user.Votes[replyid] = 0
		# post.Downvotes -= 1
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Downvotes=-1)

	elif vote == 1:
		logger.debug('Already voted')
		if callback != None:
			return callback(500)
		return 500
	hotness = ranking.confidence(upvotes,downvotes)
	Post.objects(id=postid,Reply__id=replyid).update(set__Reply__S__Hotness=hotness)
	user.save()
	if callback != None:
		return callback(200)
	return 200

def downvote_comment(userid,postid,replyid,callback = None):
	postid = str(postid).lower()
	replyid = str(replyid).lower()
	user = User.objects(id=userid).first()
	vote = user.Votes.get(replyid,None)
	coll = Post._get_collection()
	reply = coll.find({'_id' : ObjectId(postid),'Reply.id' : ObjectId(replyid)},{'_id' : 0,'Reply.$' : 1})
	if reply == None:
		if callback != None:
			return callback(500)
		return 500
	upvotes = reply[0]['Reply'][0]['Upvotes']
	downvotes = reply[0]['Reply'][0]['Downvotes']
	if vote == None:
		user.Votes[replyid] = -1
		# reply.Downvotes += 1
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Downvotes=1)

	elif vote == 0:
		user.Votes[replyid] = -1
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Downvotes=1)

	elif vote == 1:
		user.Votes[replyid] = 0
		Post.objects(id=postid,Reply__id=replyid).update(inc__Reply__S__Upvotes=-1)

	elif vote == -1:
		logger.debug('Already voted')
		if callback != None:
			return callback(500)
		return 500
	hotness = ranking.confidence(upvotes,downvotes)
	Post.objects(id=postid,Reply__id=replyid).update(set__Reply__S__Hotness=hotness)
	user.save()
	if callback != None:
		return callback(200)
	return 200



@funcs.run_async
def get_replies(userid,postid,orderBy = None,callback=None):
	logger.info("Retrieving Replies")
	#coll = User._get_collection()
	#reps = coll.find({ '_id'  : ObjectId(powner),'Wall._id' : ObjectId(postid)},{'Wall.$.Reply' : 1})[0]['Wall'][0]['Reply']
	# print 'post',postid
	# print 'postowner',powner
	post = Post.objects(id=postid).first()
	# print post.Reply
	if callback != None:
		return callback(post.Reply)
	return post.Reply


def build_tree(lst):
	tree = {}
	for node in lst:
		pid = node['ParentId']
		# print pid
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
			print((indent + str(node['Message'])))
			print_graph(graph,node['id'],depth+1)


# @funcs.run_async
def get_feed(userid,networkid=None,includeMe=True,orderBy='-Hotness',numResults=5,startNum =0,callback=None):
	# gctr += 1
	if networkid == None:
		if includeMe:
			logger.info("Retrieving main feed")
			friends = User.objects(id=userid).first().Friends
			feed = Post.objects(Q(UserId__in=friends) | Q(UserId = userid)).order_by(orderBy).limit(numResults).skip(startNum)
		else:
			logger.info("Retrieving user feed")
			feed = Post.objects(UserId = userid).order_by(orderBy)	
	else:
		feed = Post.objects(NetworkId=networkid).order_by(orderBy).limit(numResults).skip(startNum)


	if callback != None:
		return callback(feed)
	return feed

def count_posts(userid,networkid=None,includeMe=True,orderBy='-Hotness',callback=None):
		if networkid == None:
			if includeMe:
				logger.info("Retrieving main feed count")
				friends = User.objects(id=userid).first().Friends
				count = Post.objects(Q(UserId__in=friends) | Q(UserId = userid)).order_by(orderBy).count()
			else:
				logger.info("Retrieving user feed")
				count = Post.objects(UserId = userid).order_by(orderBy).count()
		else:
			count = Post.objects(NetworkId=networkid).order_by(orderBy).count()


		if callback != None:
			return callback(count)
		return count

@funcs.run_async
def get_user_feed(userid,orderBy="-Hotness",numResults=5,startNum =0,callback=None):
	logger.info("Retrieving user feed here")
	feed = Post.objects(UserId = userid ).order_by(orderBy).limit(numResults).skip(startNum)
	# feed = Post.objects(Q(UserId__in=friends) | Q(UserId = userid))
	# coll = User._get_collection()
	# feed = coll.aggregate([

	# 	{'$match' : {"_id": ObjectId(userid) } },
	# 	{'$unwind' : "$Wall" },
	# 	{'$sort' :  { "Wall.Hotness" : -1 }},
	# 	{'$limit' : numResults }] )
	# for field in feed['result']:
	# 	if field != None:
	# 		try:
	# 			del field['Password']
	# 			del field['FriendsRequesting']
	# 			del field['FriendsRequested']
	# 			del field['Nots']
	# 			del field['Clubs']
	# 		except BaseException as e:
	# 			logger.debug(e)
	# 		field['Upvoted'] = False
	# 		field['Downvoted'] = False
	# 		if ObjectId(userid) in field['Wall']['Upvoters']:
	# 			del field['Wall']['Upvoters']
	# 			field['Upvoted'] = True
	# 		if ObjectId(userid) in field['Wall']['Downvoters']:
	# 			del field['Wall']['Downvoters']
	# 			field['Downvoted'] = True
	if callback != None:
		return callback(feed)
	return feed

@funcs.run_async
def get_posts(userid,orderBy = None, numResults=20, startNum = 1,callback=None):
	
	try:
	#	wall = db.user.find_one({'_id' : ObjectId(userid)}, {'Wall' : 1, '_id' : 0})['Wall']
		wall = User.objects(_id=userid).only("Wall")
	except Exception as e:
		logger.error (e)
	
	if callback != None:
		return callback(wall)
	return wall
	
@funcs.run_async
def search(userid,universityid,query,query_type = None,numResults=20,startNum =1,callback=None):
	coll = User._get_collection()

	query = query.strip()
	queries = query.split()
	logger.debug (queries)
	if len(queries) <= 1:
		squery = '^'+query.lower();
		results = coll.find({'School.University' :  ObjectId(universityid), '$or' : [ {'FirstName' : {'$regex' : squery}},{'LastName' : {'$regex' : squery}},{'UserName' : {'$regex' : squery}}]})
	else:
		firstname = queries[0]
		lastname =  queries[1]
		fquery = '^'+firstname.lower();
		lquery = '^'+lastname.lower();

		results = coll.find({'School.University' :  ObjectId(universityid), '$or' : [ {'FirstName' : {'$regex' : fquery}},{'LastName' : {'$regex' : lquery}},{'UserName' : {'$regex' : fquery}}]})
	
	search = SearchQuery()
	search.Users = results
	club_coll = Club._get_collection()
	cquery = '^'+query.lower();
	cquery = re.compile(cquery, re.IGNORECASE)

	# cquery = query + '/i'
	# cquery = query + '.+'
	# logger.debug(cquery)

	results = club_coll.find({'University' :  ObjectId(universityid),'Private' : False, 'Name' : {'$regex' : cquery}})
	search.Clubs = results
	# print results[0]


	if callback != None:
		return callback(search)
	return search


def push_notification(userid,notification):
	user = User.objects(id=userid).first()
	user.Nots.append(notification)
	user.save()


def read_notifications(userid,callback=None):
	user = User.objects(id=userid).first()
	for Not in user.Nots:
		Not.Read = True
	user.save()
	if callback != None:
		return callback(200)
	return 200

def get_notifications(userid,callback=None):
	user = User.objects(id=userid).first()
	user.Nots.reverse()
	if callback != None:
		return callback(user.Nots)
	return user.Nots

def get_unread_notifications(userid,callback=None):
	user = User.objects(id=userid).first()
	nots = []
	for n in user.Nots:
		if n.Read == False:
			nots.append(n)
	if callback != None:
		return callback(nots)
	return nots

def clear_notification(userid,notid):
	pass

def main():
	connect("uplace")

	userid = "51637F518F24A0CCB5D94B1C"
	user = User.objects(id=userid).first()
	friendid = "5149CB8B8F24A067B266A305"
	n = FriendRequestNot(Message=(user.FirstName.capitalize() + " " + user.LastName.capitalize() +" sent a friend request"),Friend=userid)

	core_actions.push_notification(friendid,n)
if __name__ == "__main__":
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="root")
	#user = {'UserID' : 5, 'UserName' : "jillian"}
	connect("uplace")

	userid = "51637F518F24A0CCB5D94B1C"
	user = User.objects(id=userid).first()
	friendid = "5149CB8B8F24A067B266A305"
	n = FriendRequestNot(Message=(user.FirstName.capitalize() + " " + user.LastName.capitalize() +" sent a friend request"),Friend=userid)

	core_actions.push_notification(friendid,n)
	# post_wall("5149CB8B8F24A067B266A305","i like this reply","5149CB8B8F24A067B266A305", "514B65D24074506C927D6DB8","514CD7EC407450737085D361")
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
