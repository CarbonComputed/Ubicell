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
import logging
from util import *

logger = logging.getLogger(__name__)


def post_wall(userid,message,groupid,commenter=None, postid=None,replyid = None,depth=1,callback=None):
	#TODO : leave link(id) to parent
	if postid is None:
		hotness = ranking.hot(1,0,datetime.datetime.now())

		fid = userid #default writing on own wall
		if commenter != None:
			fid = commenter #someone writing on my wall

		post = Post(id=ObjectId(),FriendId=fid,UserId=userid,Message=message,Time=datetime.datetime.now(),
			Hotness=hotness,Upvotes=1,Downvotes=0,Upvoters=[fid],Downvoters=[])
		school = University.objects(id=groupid).first()
		#print userid,user.to_mongo()
		school.Wall.append(post)
		school.save()

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
		school = University.objects(id=groupid).first()
		print(school.Wall)
		post = funcs.find(school.Wall,'id',ObjectId(postid))
		post.Reply.append(reply)
		
		school.save()
	if callback != None:
		return callback(200)
	return 200

def get_feed(groupid,includeMe=True,orderBy=None,numResults=60,startNum =1,callback=None):

	logger.info("Retrieving university feed")
	uni = University.objects(id=groupid)
	if callback != None:
		return callback(uni.first().Wall)
	return uni.first().Wall


def upvote_post(ownerid,userid,postid,callback=None):
	school = University.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = school.Wall
	index = funcs.index(userwall,'id',ObjectId(postid))
	post = school.Wall[index]
	
	upvotes = post.Upvotes
	downvotes = post.Downvotes
	upvoters = post.Upvoters
	downvoters = post.Downvoters
	if ObjectId(userid) in upvoters:
		return UpvoteResp.VOTED_ALREADY
	# user.Wall.remove(post)
	if ObjectId(userid) not in downvoters:
		upvotes += 1
		upvoters.append(ObjectId(userid))
	try:
		downvotes -= 1
		downvoters.remove(ObjectId(userid))
	except ValueError:
		downvotes += 1

	hotness = ranking.hot(upvotes,downvotes,post.Time)
	post.Upvoters = upvoters
	post.Downvoters = downvoters
	post.Upvotes = upvotes
	post.Downvotes = downvotes
	post.Hotness = hotness

	
	school.Wall[index] = post
	school.save()
	if callback != None:
		return callback(200)
	return 200

def downvote_post(ownerid,userid,postid,callback=None):
	school = University.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = school.Wall
	index = funcs.index(userwall,'id',ObjectId(postid))
	post = school.Wall[index]
	

	upvotes = post.Upvotes
	downvotes = post.Downvotes
	upvoters = post.Upvoters
	downvoters = post.Downvoters
	if ObjectId(userid) in downvoters:
		return UpvoteResp.VOTED_ALREADY
	# user.Wall.remove(post)
	
	if ObjectId(userid) not in upvoters:
		downvotes += 1
		downvoters.append(ObjectId(userid))
	try:
		upvotes -= 1
		upvoters.remove(ObjectId(userid))
	except ValueError:
		upvotes += 1
	hotness = ranking.hot(upvotes,downvotes,post.Time)
	post.Upvoters = upvoters
	post.Downvoters = downvoters
	post.Upvotes = upvotes
	post.Downvotes = downvotes
	post.Hotness = hotness
	#print post==user.Wall[index]
	#print post is user.Wall[index]
	
	school.Wall[index] = post
	school.save()
	#post = User.objects(id=userid['$oid'],Wall__id=ObjectId(postid)).first()
	
	if callback != None:
		return callback(200)
	return 200


def upvote_comment(ownerid,userid,postid,replyid,callback=None):
	school = University.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = school.Wall
	post_index = funcs.index(userwall,'id',ObjectId(postid))
	reply_index = funcs.index(school.Wall[post_index].Reply,'id',ObjectId(replyid))
	reply = school.Wall[post_index].Reply[reply_index]
	upvotes = reply.Upvotes
	downvotes = reply.Downvotes
	upvoters = reply.Upvoters
	downvoters = reply.Downvoters

	if ObjectId(userid) in upvoters:
		return UpvoteResp.VOTED_ALREADY
	# user.Wall.remove(post)
	if ObjectId(userid) not in downvoters:
		upvotes += 1
		upvoters.append(ObjectId(userid))
	try:
		downvotes -= 1
		downvoters.remove(ObjectId(userid))
	except ValueError:
		downvotes += 1

	hotness = ranking.confidence(upvotes,downvotes)
	reply.Upvoters = upvoters
	reply.Downvoters = downvoters
	reply.Upvotes = upvotes
	reply.Downvotes = downvotes
	reply.Hotness = hotness
	school.Wall[post_index].Reply[reply_index] = reply
	school.save()
	if callback != None:
		return callback(200)
	return 200

def downvote_comment(ownerid,userid,postid,replyid,callback=None):
	school = University.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
	userwall = school.Wall
	post_index = funcs.index(userwall,'id',ObjectId(postid))
	reply_index = funcs.index(school.Wall[post_index].Reply,'id',ObjectId(replyid))
	reply = school.Wall[post_index].Reply[reply_index]
	upvotes = reply.Upvotes
	downvotes = reply.Downvotes
	upvoters = reply.Upvoters
	downvoters = reply.Downvoters

	if ObjectId(userid) in downvoters:
		return UpvoteResp.VOTED_ALREADY
	# user.Wall.remove(post)
	
	if ObjectId(userid) not in upvoters:
		downvotes += 1
		downvoters.append(ObjectId(userid))
	try:
		upvotes -= 1
		upvoters.remove(ObjectId(userid))
	except ValueError:
		upvotes += 1

	hotness = ranking.confidence(upvotes,downvotes)
	reply.Upvoters = upvoters
	reply.Downvoters = downvoters
	reply.Upvotes = upvotes
	reply.Downvotes = downvotes
	reply.Hotness = hotness
	school.Wall[post_index].Reply[reply_index] = reply
	school.save()
	if callback != None:
		return callback(200)
	return 200

def get_replies(userid,powner, postid,orderBy = None,callback=None):
	logger.info("Retrieving Replies")
	#coll = User._get_collection()
	#reps = coll.find({ '_id'  : ObjectId(powner),'Wall._id' : ObjectId(postid)},{'Wall.$.Reply' : 1})[0]['Wall'][0]['Reply']
	print('post',postid)
	print('postowner',powner)
	user = University.objects(id=userid,Wall__id=ObjectId(postid)).first()
	userwall = user.Wall
	post = funcs.find(userwall,'id',ObjectId(postid))
	print(post.Reply)
	return post.Reply
	if callback != None:
		return callback(post.Reply)
	return post.Reply
