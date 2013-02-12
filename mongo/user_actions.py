#!/usr/bin/env python

from tornado import database
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

def get_user_data(db,username):
	user_json = db.user.find_one("Select * from User where UserName = %s",username)
	if user_json != None:
		del user_json['Password']
	return user_json

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


def send_friend_request(db,userid,friendid):

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
	rows = db.query("Select * from Friend inner join User on User.UserID = Friend.UserID and Friend.UserID = %s",userid)
	nrows = []
	for row in rows:
		del row['Password']
		del row['Email']
		nrows.append(row)
	return nrows


def is_friends_with_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[fid])

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

def is_friends_with_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[fid])

	return check

def is_friend_requested_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequested' : 1}[fid])
	return req

def is_friend_requesting_byid(db,userid,fid):
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequesting' : 1}[fid])
	return req


def main():
	print "Testing User Data"
	db = pymongo.MongoClient().uplace
	print accept_friend_request(db,"511a607420e5d26cec26302e","511a8b3944913104fc950d84")

	day = {'hi' : 1}
	try:
		print day['hello']
	except KeyError:
		print None
	#get_friend_requests(db,"511a679820e5d26cec26302f")

	#db.close()

if __name__ == "__main__":
	main()
		