#!/usr/bin/env python

import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid

from tornado.options import define, options

from bson.json_util import dumps,loads

from constants import *

import pymongo
#import pylibmc

import auth_actions
import user_actions
import core_actions
import custom_dec

define("port", default=8000, help="run on the given port", type=int)


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
		(r"/", MainHandler),
		(r"/auth/login", AuthLoginHandler),
		(r"/auth/logout", AuthLogoutHandler),
		(r"/auth/register",RegisterHandler),
		(r'/user/([a-z\d.]{5,})/?',UserHandler),
		(r'/user/([a-z\d.]{5,})/friends',UserFriendHandler),
		(r'/user/([a-z\d.]{5,})/status',StatusHandler),
		(r'/user/([a-z\d.]{5,})/wall',WallHandler),
		(r'/actions/respond_friend',FriendActionHandler),
		]
		settings = dict(
			cookie_secret="p5q5askPJeOhs5mXb3QZ9CrNZUlxRWha6CPXif8G",
			login_url="/auth/login",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies=False,
			autoescape="xhtml_escape",
			)
		tornado.web.Application.__init__(self, handlers, **settings)
		self.db = pymongo.MongoClient().uplace
		self.mc = None
		#self.mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True,"ketama": True})

class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	@property
	def mc(self):
		return self.application.mc

	def get_current_user(self):
		user_json = self.get_secure_cookie("userdata")
		if not user_json: return None
		return tornado.escape.json_decode(loads(user_json))


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		user = self.get_current_user()
		self.render("index.html",userdata=user)

class AuthLoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):

        self.render("login.html")

    def post(self):
    	username = self.get_argument("UserName",strip = True)
    	password = self.get_argument("Password",strip = True)
    	user = auth_actions.do_login(self.db,username,password)
    	if not user:
            self.redirect("/auth/login")
            return

        #user = user_actions.get_my_data(self.db,user['_id'])
        print dumps(user)
        self.set_secure_cookie("userdata", tornado.escape.json_encode(dumps(user)))
        self.redirect("/")



class AuthLogoutHandler(BaseHandler):
	@tornado.web.asynchronous
	def get(self):
		self.clear_cookie("user")
		self.clear_cookie("userdata")
		self.redirect("/")
        #self.write("You are now logged out")

class RegisterHandler(BaseHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("register.html")
	def post(self):
		user = self.request.arguments
		resp = auth_actions.do_register(self.db,user)
		print resp


class UserHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.web.addslash

	def get(self,UserName):
		#check if user can view profile

		user = self.get_current_user()
		user2 = user_actions.get_friend_data(self.db,None,UserName)
		friend = user_actions.is_friends_with(self.db,user['_id'],UserName)
		friend_requested = user_actions.is_friend_requested(self.db,user['_id'],UserName)
		friend_requesting = user_actions.is_friend_requesting(self.db,user['_id'],UserName)
		if user2 is None:
			raise tornado.web.HTTPError(404)
		user2['UserStatus'] = UserStatus.USER_FRI
		if UserName == user['UserName']:
			user2 = user
			user2['UserStatus'] = UserStatus.USER_ME
		elif friend is None and friend_requested is None and friend_requesting is None:

			user2['UserStatus'] = UserStatus.USER_NEI
		elif friend_requesting != None:

			user2['UserStatus'] = UserStatus.USER_ACC
		elif friend_requested != None:
			user2['UserStatus'] = UserStatus.USER_REQ


			#raise tornado.web.HTTPError(403)
		#get user data
		#render page
		self.render("user.html",userdata=user2)

class UserFriendHandler(UserHandler):
	@tornado.web.authenticated
	@custom_dec.auth_friend
	def get(self,UserName):
		self.write(UserName + "hi!")

class StatusHandler(BaseHandler):
	@tornado.web.authenticated
	def post(self,UserName):
		user = self.get_current_user()
		msg = self.get_argument("Message",strip = True)
		fid = user_actions.get_friend_data(self.db,self.mc,UserName)['_id']

		return core_actions.post_wall(self.db,self.mc,user,fid,msg)

class WallHandler(BaseHandler):
	@tornado.web.authenticated
	@custom_dec.auth_friend
	def post(self,UserName):
		user = self.get_current_user()
		msg = self.get_argument("Message",strip = True)
		fid = user_actions.get_friend_data(self.db,self.mc,UserName)['_id']
		return core_actions.post_wall(self.db,self.mc,user,fid,msg)

class FriendActionHandler(BaseHandler):
	@tornado.web.authenticated

	def post(self):
		me = self.get_current_user()
		act = int(self.get_argument("Action",strip = True))
		fid = self.get_argument("_id",strip = True)
		ustat = int(self.get_argument("UserStatus",strip = True))
		print ustat
		resp = RespSuccess.DEFAULT_SUCCESS
		if int(ustat) == UserStatus.USER_NEI:
			resp = user_actions.send_friend_request(self.db,me['_id'],fid)
		elif ustat == UserStatus.USER_REQ:
			pass
		elif ustat == UserStatus.USER_ACC:
			resp = user_actions.accept_friend_request(self.db,me['_id'],fid)
		else:
			raise tornado.web.HTTPError(500)
		if resp != RespSuccess.DEFAULT_SUCCESS:
			print 'Default',resp
			raise tornado.web.HTTPError(500)


def main():
    tornado.options.parse_command_line()
    #self.db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
    print "Established Database Connection"
    print 'http://127.0.0.1:'+str(options.port)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


