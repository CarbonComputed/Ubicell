#!/usr/bin/env python


from bson.objectid import ObjectId

from constants import *

from tornado import database
import datetime

import user_actions

import pymongo



def post_wall(db,mc,user,friendid,message):
	userid = user['_id']

	post = {'_id' : ObjectId(friendid), 'Message' : message, 'Time' : datetime.datetime.now()}

	db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})

	return RespSuccess.DEFAULT_SUCCESS



def get_posts(db,userid,orderBy = None, numResults=20, startNum = 1):
	
	try:
		wall = db.user.find_one({'_id' : ObjectId(userid)}, {'Wall' : 1, '_id' : 0})['Wall']

	except Exception, e:
		print e
	
	return wall
	

if __name__ == "__main__":
	#db = database.Connection("localhost", "ProjectTakeOver",user="root",password="root")
	#user = {'UserID' : 5, 'UserName' : "jillian"}
	db = pymongo.MongoClient().uplace

	print get_posts(db,"511747a18f24a0069b7ed655")
	#print post_wall(db,None,user,5,'hey how are you?')