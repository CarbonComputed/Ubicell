#!/usr/bin/env python

from tornado import database
import MySQLdb
from constants import *

import hashlib
import random

from bson import json_util
import pymongo
import models


import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def get_user_id(db,username):
	_id = db.user.find_one({'UserName' : username},{})
	return _id



def do_login(db,username,password):
	m = hashlib.md5()
	m.update(password)
	hashed = m.hexdigest()
	login = db.user.find_one({'UserName' : username, 'Password' : hashed})
	if login is not None:
		del login['Password']
		login['_id'] = str(login['_id'])

	print 'Login',login
	return login


def validate_email(email):
	if len(email) <= 0:
		return False;
	if not EMAIL_REGEX.match(email):
		return False
	
	per = email.rfind('.') 
	if per >= 0:
		suf = email[per+1:]
		if suf != 'edu':
			return False
	return True



def check_exists(db,field,item):
	item = db.user.find_one({field : item},{})
	return item != None

def do_register(db,user):
	# TODO : Insert User into corresponding school collection/ register request
	# A user should be added to the register request collection:
	#When a user verifies email, then they are inserted into user/university collection
	print user
	password = user["Password"][0].strip()
	m = hashlib.md5()
	m.update(password)
	password = m.hexdigest()
	username = user['UserName'][0].strip()
	if check_exists(db,'UserName',username):
		return RegError.USERNAME_INUSE
	firstname = user['FullName'][0].split()[0].strip()
	lastname = user['FullName'][0].split()[1].strip()
	email = user['Email'][0].strip()
	if validate_email(email) == False or check_exists(db,'Email',email):
		return RegError.INVALID_EMAIL
	gender = user['gender'][0].strip()
	if gender != 'Male' and gender != 'Female':
		return RegError.DEFAULT_ERROR
	university = user['university'][0].strip()
	if university not in UNIVERSITY_LIST:
		return RegError.DEFAULT_ERROR
	major = user['major'][0]
	gradyear = int(user['yearpicker'][0].strip())
	aboutme = user['about'][0].strip()
	if len(aboutme) >  400:
		return RegError.DEFAULT_ERROR


	user  = {'UserName' : username, 'Password' : password,'FirstName' : firstname, 'LastName' : lastname, 'Email' : email ,
			 'Gender' : gender , 'About' : aboutme, 'School' : { 
			 													'University' : university,
			 													'Major' : major,
			 													'GradYear' : gradyear

			 								}
			 }
	return db.user.update({'UserName' : username},user,upsert=True)




def main():
	print "Testing Database Connection"
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
	#print db is not None
	#print "Testing Login"
	#cookie = do_login(db,"kmcarbone","kmcarbone")
	#print cookie
	db = pymongo.MongoClient().uplace

	# user_reg = {'UserName' : "kmcarbone",'Password' : "kmcarbone",'UID' : 1,'FirstName' : "Kevind",'LastName' : "Carbone", 'Email' : "kmcarbone16@gmail.com"}
	# user_reg2 = {'UserName' : "jillian",'Password' : "jillian",'UID' : 1,'FirstName' : "jillian",'LastName' : "Carbone", 'Email' : "jpcarbone@gmail.com"}


	# #print "Testing Registration"
	# userid = do_register(db,user_reg)

	# print userid
	print validate_email('kmc8206@blah.rit.edu')
	print check_exists(db,'Email','kmc8206@rit.edu')
	#print do_login(db,'njcbone2','blah')
	#print "Testing is_register_requested"
	#resp = is_register_requested(db,cookie)
	#print resp
	#db.close()


if __name__ == "__main__":
	main()