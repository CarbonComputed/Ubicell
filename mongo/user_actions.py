#!/usr/bin/env python

import gridfs
import pymongo
import json
from constants import *


import auth_actions

from bson.objectid import ObjectId

def get_my_data(db,_id):
	user= db.user.find_one({'_id' : ObjectId(_id)})
	if user != None:
		del user['Password']
	return user



def get_friend_data(db,mc,username):
	#db.user.find_one({'UserName' : username},{'_id' : 1, 'UserName' : 1 ,'FirstName' : 1, 'LastName' : 1})
	row = db.user.find_one({'UserName' : username})
	if row != None:
		del row['Password']
		try:
			del row['FriendRequests']
		except:
			pass
	return row

def get_simple_data(db,userid):
	user = db.user.find_one({'_id' : ObjectId(userid)},{'Wall' : 0, 'Friends' : 0 ,'FriendsRequested' : 0,'FriendsRequesting' : 0,'Password' : 0})
	return user

def send_friend_request(db,userid,friendid):

	#TODO : Check if user already in array
	friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })


	print friend
	print user

	print userid

	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'FriendsRequested' :friend}},upsert = True)
	db.user.update({'_id' : ObjectId(friendid)},{'$push' : { 'FriendsRequesting' :user}},upsert = True)


	req = RespSuccess.DEFAULT_SUCCESS
	return req

def accept_friend_request(db,userid,friendid):

	#TODO : Check if user already in Friends, Check if users are already requested/ing
	req = RespSuccess.DEFAULT_SUCCESS
	print userid,friendid


	friend = db.user.find_one({'_id' : ObjectId(friendid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })
	user = db.user.find_one({'_id' : ObjectId(userid)},{'_id' : 1, 'UserName' : 1, 'FirstName' : 1 , 'LastName' : 1 })

	db.user.update({ '_id' : ObjectId(friendid)},{'$pull' : {'FriendsRequested' : { '_id' : ObjectId(userid)}} ,  '$push' : { 'Friends' :user}},upsert = True)

	db.user.update({ '_id' : ObjectId(userid)},{'$pull' : {'FriendsRequesting' : { '_id' :ObjectId(friendid)}} ,  '$push' : { 'Friends' :friend}},upsert = True)



	return req


def get_friend_requests(db,userid):
	req = None
	print db.user.find_one({'_id' : ObjectId(userid)})
	return req

def get_friends(db,userid):
	friends = db.user.find({'Friends._id' : userid}, {'Password' : 0})
	return friends


def is_friends_with_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1})

	return check

def is_friends_with(db,userid,f_username):
	#_id = db.user.find_one({'UserName' : f_username},{})
	try:
		check = db.user.find_one({'UserName' : f_username,"Friends._id" : ObjectId(userid)},{'Friends' : 1})
	except:
		check = None
	return check

def is_friend_requested(db,userid,f_username):
	try:
		check = db.user.find_one({'UserName' : f_username,"FriendsRequesting._id" : ObjectId(userid)},{'FriendsRequesting' : 1})
	except:
		check = None

	return check


def is_friend_requesting(db,userid,f_username):
	_id = db.user.find_one({'UserName' : f_username},{})
	try:
		check = db.user.find_one({'UserName' : f_username, "FriendsRequested._id" : ObjectId(userid)},{'FriendsRequested' : 1})
	except:
		check = None
	return check

# def is_friends_with_byid(db,userid,fid):
# 	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[fid])

# 	return check

def is_friend_requested_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequested' : 1}[fid])
	return req

def is_friend_requesting_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequesting' : 1}[fid])
	return req


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
		