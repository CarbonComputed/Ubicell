#!/usr/bin/env python

from tornado import database
import MySQLdb
import json
from constants import *


import auth_actions

def get_my_data(db,cookie):
	user_json = db.get("Select * from User inner join Cookie on Cookie.UserID = User.UserID and Cookie.CookieVal = %s",cookie)
	if user_json != None:
		del user_json['Password']
	return user_json

def get_user_data(db,username):
	user_json = db.get("Select * from User where UserName = %s",username)
	if user_json != None:
		del user_json['Password']
	return user_json

def get_friend_data(db,mc,user):
	rows = db.query("Select UserID,UserName,FirstName,LastName from Friend inner join User on User.UserID = Friend.UserID and Friend.UserID = %s",userid)
	nrows = []
	for row in rows:
		del row['Password']
		del row['Email']
		nrows.append(row)
	return nrows


def send_friend_request(db,userid,friendid):
	req = RespSuccess.DEFAULT_SUCCESS
	try:
		db.execute("Insert into FriendRequests Values(%s,%s)",userid,friendid)
	except MySQLdb.IntegrityError:
		req = RespError.DUPLICATE_ERROR
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

def accept_friend_request(db,userid,friendid):
	req = RespSuccess.DEFAULT_SUCCESS
	print userid,friendid
	try:
		db.execute("Delete from FriendRequests where UserID = %s and FriendID = %s",friendid,userid)
	except:
		req = RespError.DEFAULT_ERROR
		return req
	try:
		db.execute("Insert into Friend Values(%s,%s)",userid,friendid)
		db.execute("Insert into Friend Values(%s,%s)",friendid,userid)
	except:
		req = RespError.DEFAULT_ERROR
	return req

def is_friends_with(db,userid,userid2):
	req = db.get("Select 1 from Friend where UserID = %s and FriendID = %s",userid,userid2)
	if req is None:
		return False
	return True

def is_friends_with(db,userid,f_username):
	req = db.get("Select u.UserID,u.UserName,u.FirstName,u.LastName from Friend f join User u on f.FriendID = u.UserID and u.UserName = %s \
					where f.UserID = %s;",f_username,userid)
	return req

def is_friend_requested(db,userid,f_username):
	req = db.get("Select u.UserID,u.UserName,u.FirstName,u.LastName from FriendRequests f join User u on f.FriendID = u.UserID and u.UserName = %s \
					where f.UserID = %s;",f_username,userid)
	return req

def is_friend_requesting(db,userid,my_username):
	req = db.get("Select 1 from FriendRequests f join User u on f.UserID = u.UserID and u.UserName = %s \
					where f.FriendID = %s;",my_username,userid)
	return req

def auth_currentid(user_data,uid):
	return user_data['UID'] is uid


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
		