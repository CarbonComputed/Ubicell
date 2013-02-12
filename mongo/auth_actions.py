#!/usr/bin/env python

from tornado import database
import MySQLdb
from constants import *

import hashlib
import random

import pymongo
import models



def get_user_id(db,username):
	_id = db.user.find_one({'UserName' : username},{})
	return _id



def do_login(db,username,password):
	m = hashlib.md5()
	m.update(password)
	hashed = m.hexdigest()
	login = db.user.find_one({'UserName' : username, 'Password' : hashed})
	del login['Password']
	return login




def do_register(db,user):
	password = user["Password"]
	m = hashlib.md5()
	m.update(password)
	password = m.hexdigest()
	user["Password"] = password
	username = user['UserName']
	return db.user.update({'UserName' : username},user,upsert=True)



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
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	#print db is not None
	#print "Testing Login"
	#cookie = do_login(db,"kmcarbone","kmcarbone")
	#print cookie
	db = pymongo.MongoClient().uplace

	user_reg = {'UserName' : "kmcarbone",'Password' : "kmcarbone",'UID' : 1,'FirstName' : "Kevind",'LastName' : "Carbone", 'Email' : "kmcarbone16@gmail.com"}
	user_reg2 = {'UserName' : "jillian",'Password' : "jillian",'UID' : 1,'FirstName' : "jillian",'LastName' : "Carbone", 'Email' : "jpcarbone@gmail.com"}


	#print "Testing Registration"
	userid = do_register(db,user_reg)

	print userid
	#print do_login(db,'njcbone2','blah')
	#print "Testing is_register_requested"
	#resp = is_register_requested(db,cookie)
	#print resp
	#db.close()


if __name__ == "__main__":
	main()