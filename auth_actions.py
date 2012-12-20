#!/usr/bin/env python

from tornado import database
import MySQLdb
from constants import *

import hashlib
import random

class User(object):
	def __init__(self,user):
		self.user = user


def get_user_id(db,username):
	user = db.get("Select UserID from User where UserName = %s",username)
	userid = user["UserID"]
	return userid


def do_login(db,username,password,cookie=None):
	m = hashlib.md5()
	m.update(password)
	hashed = m.hexdigest()
	login = db.get("select 1 from User where UserName = %s and Password = %s",username,hashed)
	if login == None:
		return None
	m.update(username)
	m.update(str(random.random()))
	cookie = m.hexdigest()
	db.execute("Update Cookie inner join User on User.UserID = Cookie.UserID and User.UserName = %s set CookieVal=%s",username,cookie)
	#db.execute("Update Cookie set CookieVal=%s where UserID = (select UserID from User where UserName = %s)",cookie,username)
	return cookie


def do_register(db,user):
	username = user["UserName"]
	password = user["Password"]
	email = user["Email"]
	uid = user["UID"]
	firstname = user["FirstName"]
	lastname = user["LastName"]
	m = hashlib.md5()
	m.update(password)
	password = m.hexdigest()
	try:
		db.execute("Insert into User Values(0,%s,%s,%s,%s,%s)",username,password,firstname,lastname,email)
	except MySQLdb.IntegrityError:
		return RespError.DUPLICATE_ERROR
	except:
		return RespError.DEFAULT_ERROR
	userid = get_user_id(db,username)
	try:
		db.execute("Insert into RegisterRequests Values(%s)",userid)
	except MySQLdb.IntegrityError:
		db.execute("Delete from User where UserID = %s",userid)
		return RespError.DUPLICATE_ERROR
	except:
		db.execute("Delete from User where UserID = %s",userid)
		return RespError.DEFAULT_ERROR
	return userid


def is_registered(db,cookie):
	req = db.get("select 1 from RegisterRequests where UserID = (select User.UserID from User inner join Cookie on User.UserID = Cookie.UserID and Cookie.CookieVal = %s)",cookie)
	if req is None:
		return True
	return False

def is_register_requested(db,cookie):
	req = db.get("select User.UserID from User inner join Cookie on User.UserID = Cookie.UserID and Cookie.CookieVal = %s",cookie)
	if req is None:
		return False
	userid = req["UserID"]
	req = db.get("select 1 from RegisterRequests where UserID = %s",userid)
	if req is None:
		return False
	return True


def main():
	print "Testing Database Connection"
	db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	print db is not None
	print "Testing Login"
	cookie = do_login(db,"kmcarbone","kmcarbone")
	print cookie
	user_reg = {'UserName' : "njcbone2",'Password' : "blah",'UID' : 1,'FirstName' : "Nick",'LastName' : "Carbone", 'Email' : "njcbone@gmail.com"}
	print "Testing Registration"
	userid = do_register(db,user_reg)
	print userid
	print "Testing is_register_requested"
	resp = is_register_requested(db,cookie)
	print resp
	db.close()


if __name__ == "__main__":
	main()