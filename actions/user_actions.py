#!/usr/bin/env python

import gridfs
import pymongo
import json
from constants import *


from . import auth_actions

from bson.objectid import ObjectId

# from mongokit import Document, Connection


from models.User import *

from models.Notification import *

import actions.core_actions
from util import *

import logging
logger = logging.getLogger(__name__)

def get_my_data(_id,callback=None):
	user= User.objects(id=_id).exclude("Password").first()
	if user != None:
		del user['Password']
	return callback(user)



def get_friend_data(username,callback=None):
	#db.user.find_one({'UserName' : username},{'_id' : 1, 'UserName' : 1 ,'FirstName' : 1, 'LastName' : 1})
	user = User.objects(UserName=username).exclude("FriendsRequesting","FriendsRequested").first()
	if callback != None:
		return callback(user)
	return user


def get_simple_data(userid,callback=None):
	user = User.objects(id=userid).exclude("Wall","Friends","FriendsRequested","FriendsRequesting","Password").first()
	if callback != None:
		return callback(user)
	return user

def send_friend_request(userid,friendid,callback=None):

	friend = User.objects(id=friendid).first()
	user = User.objects(id=userid).first()

	if friend in user.Friends or friend in user.FriendsRequested or friend in user.FriendsRequesting:
		return
	if user in friend.Friends or user in friend.FriendsRequested or user in friend.FriendsRequesting:
		return


	friend.FriendsRequesting.append(user.id)
	user.FriendsRequested.append(friend.id)
	# #TODO : Check if user already in array
	# friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	# user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })

	friend.save()
	user.save()


	n = FriendRequestNot(Message=(user.FirstName.capitalize() + " " + user.LastName.capitalize() +" sent a friend request"),Friend=userid)

	actions.core_actions.push_notification(friendid,n)
	# print friend
	# print user

	# print userid

	# db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'FriendsRequested' :friend}},upsert = True)
	# db.user.update({'_id' : ObjectId(friendid)},{'$push' : { 'FriendsRequesting' :user}},upsert = True)


	# req = RespSuccess.DEFAULT_SUCCESS
	if callback != None:
		return callback(200)
	return 200

def accept_friend_request(userid,friendid,callback=None):

	#TODO : Check if user already in Friends, Check if users are already requested/ing
	req = RespSuccess.DEFAULT_SUCCESS
	print(userid,friendid)
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

	actions.core_actions.push_notification(friendid,n)
	# friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	# user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })

	# db.user.update({ '_id' : ObjectId(friendid)},{'$pull' : {'FriendsRequested' : { '_id' : ObjectId(userid)}} ,  '$push' : { 'Friends' :user}},upsert = True)

	# db.user.update({ '_id' : ObjectId(userid)},{'$pull' : {'FriendsRequesting' : { '_id' :ObjectId(friendid)}} ,  '$push' : { 'Friends' :friend}},upsert = True)



	if callback != None:
		return callback(200)
	return 200


def get_friend_requests(userid):
	req = None
	print(db.user.find_one({'_id' : ObjectId(userid)}))
	return req

# def get_friends(userid,callback=None):
# 	#friends = db.user.find({'Friends._id' : userid}, {'Password' : 0})
# 	user = User.objects(id=userid).first()
# 	if callback != None:
# 		return callback(user.Friends)
# 	return user.Friends


def is_friends_with_byid(userid,fid,callback=None):
#	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1})

	user = User.objects(id=userid).first()
	check = ObjectId(fid) in user.Friends
	if callback != None:
		return callback(check)
	return check

def is_friends_with(userid,f_username,callback=None):
	#_id = db.user.find_one({'UserName' : f_username},{})
	#try:
	#	check = db.user.find_one({'UserName' : f_username,"Friends._id" : ObjectId(userid)},{'Friends' : 1})
	#except:
	#	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.Friends
	if callback != None:
		return callback(check)
	return check

def is_friend_requested(userid,f_username,callback=None):
	# try:
	# 	check = db.user.find_one({'UserName' : f_username,"FriendsRequesting._id" : ObjectId(userid)},{'FriendsRequesting' : 1})
	# except:
	# 	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.FriendsRequesting
	if callback != None:
		return callback(check)
	return check

def is_friend_requesting(userid,f_username,callback=None):
	# _id = db.user.find_one({'UserName' : f_username},{})
	# try:
	# 	check = db.user.find_one({'UserName' : f_username, "FriendsRequested._id" : ObjectId(userid)},{'FriendsRequested' : 1})
	# except:
	# 	check = None
	user = User.objects(UserName=f_username).first()
	check = ObjectId(userid) in user.FriendsRequested
	if callback != None:
		return callback(check)
	return check

# def is_friends_with_byid(db,userid,fid):
# 	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[fid])

# 	return check

def is_friend_requested_byid(userid,fid,callback=None):
	# check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequested' : 1}[fid])
	user = User.objects(id=userid).first()
	check = ObjectId(userid) in user.FriendsRequested
	if callback != None:
		return callback(check)
	return check

def is_friend_requesting_byid(userid,fid,callback=None):
	user = User.objects(id=userid).first()
	check = ObjectId(userid) in user.FriendsRequesting
	if callback != None:
		return callback(check)
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

@funcs.run_async
def get_friends(userid,includeMe=True,orderBy=None,numResults=60,startNum =1,callback=None):
	# gctr += 1

	logger.info("Retrieving main feed")
	coll = User._get_collection()
	friends = coll.find({'Friends' : userid})
	if callback != None:
		return callback(friends)
	return friends

def main():
	connect("uplace")

	userid = "51637F518F24A0CCB5D94B1C"
	user = User.objects(id=userid).first()
	friendid = "5149CB8B8F24A067B266A305"
	n = FriendRequestNot(Message=(user.FirstName.capitalize() + " " + user.LastName.capitalize() +" sent a friend request"),Friend=userid)

	actions.core_actions.push_notification(friendid,n)

if __name__ == "__main__":
	main()
		