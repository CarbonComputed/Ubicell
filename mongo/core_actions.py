#!/usr/bin/env python

from time import time
import MySQLdb

from constants import *

from tornado import database


import user_actions

def post_status(db,mc,user,message):
	userid = user['UserID']
	try:
		post = {}
		db.user.update({'_id' : ObjectId(userid)},)
		db.execute("Insert into UserStatus Values(0,%s,%s,%s)",userid,message,t)
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return RespSuccess.DEFAULT_SUCCESS

def post_wall(db,mc,user,friendid,message):
	userid = user['UserID']
	post = {'_id', ObjectId(friendid), 'Message' : message, 'Time' : 'Date()'}
	if userid == friendid:
		fid = -1
	else:
		fid = friendid
	try:
		db.user.update({'_id' : userid},{{'$push' : { 'Wall' : post}})
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return RespSuccess.DEFAULT_SUCCESS



def get_posts(user,orderBy = None, numResults=20, startNum = 1):
	userid = user['UserID']
	rows = None
	try:
		rows = db.query("select * from UserWall where UserID = %s order by Time desc limit %s,%s;",userid,startNum,numResults);
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return rows
	

if __name__ == "__main__":
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="root")
	user = {'UserID' : 5, 'UserName' : "jillian"}
	print get_posts(user)
	#print post_wall(db,None,user,5,'hey how are you?')