#!/usr/bin/env python

from time import time
import MySQLdb

from constants import *

import user_actions

def post_status(db,mc,user,message):
	userid = user['UserID']
	t = long(time())
	try:
		db.execute("Insert into UserStatus Values(0,%s,%s,%s)",userid,message,t)
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return RespSuccess.DEFAULT_SUCCESS

def post_wall(db,mc,user,friend,message):
	userid = user['UserID']
	t = long(time())
	print user['UserName'],friend
	if user['UserName'] == friend:
		fid = -1
	else:
		friend = get_friend_data(db,mc,user)
		fid = friend['UserID']
	try:
		db.execute("Insert into UserWall Values(0,%s,%s,%s,%s)",userid,fid,message,t)
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return RespSuccess.DEFAULT_SUCCESS



def get_posts(user,orderBy = None, numResults=20, startNum = 1):
	pass