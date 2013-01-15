#!/usr/bin/env python

from time import time


def post_status(db,user,message):
	userid = user['UserID']
	t = int(time.time())
	try:
		db.execute("Insert into UserStatus Values(0,%s,%s,%s)",userid,message,t)
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	return RespSucess.DEFAULT_SUCCESS


def get_status(user,orderBy = None):
	pass