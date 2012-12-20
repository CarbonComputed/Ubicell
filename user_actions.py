#!/usr/bin/env python

from tornado import database
import MySQLdb
from constants import *

import auth_actions

def get_user_data(db,cookie):
	user_json = db.get("Select * from User inner join Cookie on Cookie.UserID = User.UserID and Cookie.CookieVal = %s",cookie)
	if user_json != None:
		del user_json['Password']
	return user_json

def send_friend_request(db,userid,friendid):
	req = RespSuccess.DEFAULT_SUCCESS
	try:
		req = db.execute("Insert into FriendRequests Values(%s,%s)",userid,friendid)
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

def get_friends(self,userid):
	req = db.get("Select * from Friend inner join User on User.UserID = Friend.UserID and Friend.UserID = %s",userid)
	del req['Password']
	return req

def accept_friend_request(db,userid,friendid):
	req = RespSuccess.DEFAULT_SUCCESS
	try:
		req = db.get("Insert into Friends Values(%s,%s)",userid,friendid)
		req = db.get("Insert into Friends Values(%s,%s)",friendid,userid)
	except:
		req = RespError.DEFAULT_ERROR
	return req

def is_friends_with(db,userid,userid2):
	req = db.get("Select 1 from Friend where UserID = %s and FriendID = %s",userid,userid2)
	if req is None:
		return False
	return True




def main():
	print "Testing User Data"
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	cookie = auth_actions.do_login(db,"kmcarbone","kmcarbone")
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


if __name__ == "__main__":
	main()
		