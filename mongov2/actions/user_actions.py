#!/usr/bin/env python

import gridfs
import pymongo
import json
from constants import *


import auth_actions

from bson.objectid import ObjectId

from mongokit import Document, Connection


from models.User import *

from models.Notification import *

import core_actions

import logging
logger = logging.getLogger(__name__)

def get_my_data(_id):
	user= User.objects(id=_id).exclude("Password").first()
	if user != None:
		del user['Password']
	return user



def get_friend_data(username):
	#db.user.find_one({'UserName' : username},{'_id' : 1, 'UserName' : 1 ,'FirstName' : 1, 'LastName' : 1})
	user = User.objects(UserName=username).exclude("FriendsRequesting","FriendsRequested").first()
	return user

def get_simple_data(userid):
	user = User.objects(id=userid).exclude("Wall","Friends","FriendsRequested","FriendsRequesting","Password").first()
	return user

def send_friend_request(userid,friendid):

	friend = User.objects(id=friendid).first()
	user = User.objects(id=userid).first()

	if friend in user.Friends or friend in user.FriendsRequested or friend in user.FriendsRequesting:
		print 'test'
		return
	if user in friend.Friends or user in friend.FriendsRequested or user in friend.FriendsRequesting:
		print 'test'
		return


	friend.FriendsRequesting.append(user.id)
	user.FriendsRequested.append(friend.id)
	# #TODO : Check if user already in array
	# friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	# user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })

	friend.save()
	user.save()


	n = FriendRequestNot(Message=(user.FirstName.capitalize() + " " + user.LastName.capitalize() +" sent a friend request"),Friend=userid)

	core_actions.push_notification(friendid,n)
	# print friend
	# print user

	# print userid

	# db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'FriendsRequested' :friend}},upsert = True)
	# db.user.update({'_id' : ObjectId(friendid)},{'$push' : { 'FriendsRequesting' :user}},upsert = True)


	# req = RespSuccess.DEFAULT_SUCCESS
	return 200

def accept_friend_request(userid,friendid):

	#TODO : Check if user already in Friends, Check if users are already requested/ing
	req = RespSuccess.DEFAULT_SUCCESS
	print userid,friendid
	friend = User.objects(id=friendid).first()
	user = User.objects(id=userid).first()

	if friend in user.Friends :
		return
	if user in friend.Friends:
		return

	
	user.FriendsRequesting.remove(ObjectId(friend.id))
	friend.FriendsRequested.remove(ObjectId(user.id))

	friend.Friends.append(ObjectId(user.id))
	user.Friends.append(ObjectId(friend.id))


	friend.save()
	user.save()

	n = FriendRequestNot(Message=(user.FirstName.capitalize()  + " " + user.LastName.capitalize() +" accepted friend request"),Friend=userid)

	core_actions.push_notification(friendid,n)
	# friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	# user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })

	# db.user.update({ '_id' : ObjectId(friendid)},{'$pull' : {'FriendsRequested' : { '_id' : ObjectId(userid)}} ,  '$push' : { 'Friends' :user}},upsert = True)

	# db.user.update({ '_id' : ObjectId(userid)},{'$pull' : {'FriendsRequesting' : { '_id' :ObjectId(friendid)}} ,  '$push' : { 'Friends' :friend}},upsert = True)



	return 200


def get_friend_requests(userid):
	req = None
	print db.user.find_one({'_id' : ObjectId(userid)})
	return req

def get_friends(userid):
	#friends = db.user.find({'Friends._id' : userid}, {'Password' : 0})
	user = User.objects(id=userid).first()

	return user.Friends


def is_friends_with_byid(userid,fid):
#	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1})

	user = User.objects(id=userid).first()
	check = ObjectId(fid) in user.Friends
	return check

def is_friends_with(userid,f_username):
	#_id = db.user.find_one({'UserName' : f_username},{})
	#try:
	#	check = db.user.find_one({'UserName' : f_username,"Friends._id" : ObjectId(userid)},{'Friends' : 1})
	#except:
	#	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.Friends
	return check

def is_friend_requested(userid,f_username):
	# try:
	# 	check = db.user.find_one({'UserName' : f_username,"FriendsRequesting._id" : ObjectId(userid)},{'FriendsRequesting' : 1})
	# except:
	# 	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.FriendsRequesting
	return check


def is_friend_requesting(userid,f_username):
	# _id = db.user.find_one({'UserName' : f_username},{})
	# try:
	# 	check = db.user.find_one({'UserName' : f_username, "FriendsRequested._id" : ObjectId(userid)},{'FriendsRequested' : 1})
	# except:
	# 	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.FriendsRequested
	return check

# def is_friends_with_byid(db,userid,fid):
# 	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[fid])

# 	return check

def is_friend_requested_byid(userid,fid):
	# check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequested' : 1}[fid])
	user = User.objects(id=userid).first()
	check = ObjectId(userid) in user.FriendsRequested
	return check

def is_friend_requesting_byid(userid,fid):
	user = User.objects(id=userid).first()
	check = ObjectId(userid) in user.FriendsRequesting
	return check


def get_user_photos(db,fs,f_username):
	friend = get_friend_data(db,None,f_username)
	photos = {}
	for photo in friend['Photos']:
		pid = photo['_id']
		photos[pid] = fs.get(ObjectId(pid))
	return photos

def validPost(db,postowner,postid):
	check = db.user.find({'_id' : ObjectId(postowner),'Wall._id' : ObjectId(postid)})
	return check != None

def main():
	#print "Testing User Data"
	db = pymongo.MongoClient().uplace
	fs = gridfs.GridFS(db)
	print get_user_photos(db,fs,'kmcarbone').itervalues().next().read()

	#db.close()

if __name__ == "__main__":
	main()
		