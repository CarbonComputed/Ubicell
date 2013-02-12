#!/usr/bin/env python

from tornado import database
import MySQLdb
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
		del row['FriendRequests']
	return row


def send_friend_request(db,userid,friendid):

	friend = db.user.find_one({'_id' : ObjectId(friendid)},{_id : 1, UserName : 1, FirstName : 1 , LastName : 1 })
	user = db.user.find_one({'_id' : ObjectId(userid)},{_id : 1, UserName : 1, FirstName : 1 , LastName : 1 })
	db.user.update({'_id' : ObjectId(user)},{'$push' : { 'FriendsRequested' :friend},upsert = True)
	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'FriendsRequesting' :user},upsert = True)


	req = RespSuccess.DEFAULT_SUCCESS
	return req

def accept_friend_request(db,userid,friendid):
	req = RespSuccess.DEFAULT_SUCCESS
	print userid,friendid
	try:

		
		db.execute("Delete from FriendRequests where UserID = %s and FriendID = %s",friendid,userid)

		db.execute("Insert into Friend Values(%s,%s)",userid,friendid)
		db.execute("Insert into Friend Values(%s,%s)",friendid,userid)
	except:
		req = RespError.DEFAULT_ERROR
	return req


def get_friend_requests(db,userid):
	req = db.get("Select * from FriendRequests inner join User on User.UserID = FriendRequests.UserID and FriendRequests.UserID = %s",userid)
	if req != None:
		del req['Password']
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
	_id = db.user.find_one({'UserName' : f_username},{})
	check = db.user.find_one({'_id' : ObjectId(userid)},{'Friends' : 1}[_id])

	return check

def is_friend_requested(db,userid,f_username):
	_id = db.user.find_one({'UserName' : f_username},{})
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequested' : 1}[_id])
	return req


def is_friend_requesting(db,userid,f_username):
	_id = db.user.find_one({'UserName' : f_username},{})
	check = db.user.find_one({'_id' : ObjectId(userid)},{'FriendsRequesting' : 1}[_id])
	return req

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
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	cookie = auth_actions.do_login(db,"kevin","test")
	json = get_user_data(db,cookie)
	print json
	print "Testing Friend Request"
	resp = send_friend_request(db,2,1)
	print resp
	print "Testing Friend Check"
	resp = is_friends_with(db,3,2)
	print resp
	print "Testing Get All Friend Requests"
	print get_friend_requests(db,1)
	db.close()

def friend_test():
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	print json.dumps(get_friends(db,1))
def is_friends_test():
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	return is_friends_with(db,1,'jillian')

if __name__ == "__main__":
	print is_friends_test()
		