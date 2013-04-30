#!/usr/bin/env python


from constants import *
from bson.objectid import ObjectId

import hashlib
import random
import re
import logging

from models.School import *
from models.University import *
from models.Post import *
from models.ProfileImage import * 

from models.User import *

from util.funcs import *
from config import *
import smtplib

from email.mime.text import MIMEText


logger = logging.getLogger(__name__)

smtp = smtplib.SMTP('localhost')

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


@run_async
def login(username,password,callback=None):
	# print 'here!!'

	logger.info("Initiating login")
	
	m = hashlib.md5()
	# password = password.encode('utf-8')
	m.update(password)
	hashed = m.hexdigest()
	login = User.objects(UserName=username.lower(),Password=hashed).exclude("Password","Wall","FriendsRequested","Friends","FriendsRequesting")
	if login.first() is None:
		login = User.objects(Email=username.lower(),Password=hashed).exclude("Password","Wall","FriendsRequested","Friends","FriendsRequesting")
		if login.first() is None:
			if callback != None:
				return callback(None)
			return None
	logger.info(username + " has logged in")
	if callback != None:
		logger.info("Using login callback")
		return callback(login.first())
		

	return login.first()



@run_async
def register(user,request,callback=None):
	# TODO : Insert User into corresponding school collection/ register request
	# A user should be added to the register request collection:
	#When a user verifies email, then they are inserted into user/university collection
	# print user
	password = user["Password"][0].strip()
	m = hashlib.md5()
	m.update(password)
	password = m.hexdigest()
	username = user['UserName'][0].strip().lower()
	names = user['FullName'][0].split()
	if len(names) > 1:
		firstname = user['FullName'][0].split()[0].strip().lower()
		lastname = user['FullName'][0].split()[1].strip().lower()
	else:
		firstname = user['FullName'][0].strip().lower()
		lastname = ''
	email = user['Email'][0].strip().lower()
	gender = user['gender'][0].strip()
	university = user['university'][0].strip()
	major = user['major'][0].strip()
	gradyear = int(user['yearpicker'][0].strip())
	aboutme = user['about'][0].strip()

	regid=ObjectId()
	#print request.files
	fileinfo = request.files['pic'][0]
	uni = University.objects(Name=university).first()
	if uni is None:
		uni = University(Name=university)
		uni.save()
	school = School(University=uni.id,Major=major,GradYear=gradyear)
	#Check length

	usermodel = User(UserName=username,FirstName=firstname,LastName=lastname,Password=password,Email=email,Gender=gender,School=school,About=aboutme,RegId=regid) 
	usermodel.save()

	profimg = ProfileImage(Owner=usermodel.id)
	profimg.Image.put(fileinfo['body'],content_type = 'image/jpeg',Owner=usermodel.id)
	profimg.save()

	

	usermodel.ProfileImg = profimg.id
	usermodel.save()

	uni.Students.append(usermodel.id)
	uni.save()
	logger.info(username + " has registered")
	send_confirmation(email,regid)
	if callback != None:
		return callback(200)
	return 200


def send_confirmation(email,uniqueid):
    msg = MIMEText("""
Welcome to Ubicell!  Your online registration is almost complete. To validate your account please click: 
        http://www.ubicell.com/verify?regid=%s
Thank you for signing up.

Sincerely,
-- 
Kevin Carbone

    """ % uniqueid)
    msg['Subject'] = 'Ubicell Conirmation'
    msg['From'] = 'nobody@ubicell.com'
    msg['To'] = email
    print 'test2'
    smtp = smtplib.SMTP('localhost',timeout=7)
    # smtp.ehlo()
    # smtp.starttls()
    # smtp.ehlo
    # print 'test1'
    smtp.sendmail('nobody@ubicell.com', [email], msg.as_string())
    # print 'test'
    smtp.quit()



def main():

	# print "Testing Database Connection"
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
	# print validate_email('kmc8206@blah.rit.edu')
	# print check_exists(db,'Email','kmc8206@rit.edu')
	#print do_login(db,'njcbone2','blah')
	#print "Testing is_register_requested"
	#resp = is_register_requested(db,cookie)
	#print resp
	#db.close()


if __name__ == "__main__":
	main()