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
from tornado import database


import auth_actions
import user_actions
import core_actions
import custom_dec

define("port", default=8000, help="run on the given port", type=int)

db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")



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


class BaseHandler(tornado.web.RequestHandler):
	#user_cache = {}

	def get_current_user(self):
		user_json = self.get_secure_cookie("userdata")
		if not user_json: return None
		return tornado.escape.json_decode(user_json)


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
    	user_cookie = auth_actions.do_login(db,username,password)
    	if not user_cookie:
            self.redirect("/auth/login")
            return
        self.set_secure_cookie("user", tornado.escape.json_encode(user_cookie))
        user = user_actions.get_my_data(db,user_cookie)
        self.set_secure_cookie("userdata", tornado.escape.json_encode(user))
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
		resp = auth_actions.do_register(db,user)
		print resp


class UserHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.web.addslash

	def get(self,UserName):
		#check if user can view profile
		user = self.get_current_user()
		user2 = user_actions.get_user_data(db,UserName)
		friend = user_actions.is_friends_with(db,user['UserID'],UserName)
		if user2 is None:
			raise tornado.web.HTTPError(404)
		user2['FriendFlag'] = True
		if friend is None:
			print friend
			user2['FriendFlag'] = False

			#raise tornado.web.HTTPError(403)
		#get user data
		#render page
		self.render("user.html",userdata=user2)

class UserFriendHandler(BaseHandler):
	@custom_dec.auth_friend
	def get(self,UserName):
		self.write(UserName + "hi!")

class StatusHandler(BaseHandler):

	def post(self):
		user = self.get_current_user()
		msg = self.get_argument("Message",strip = True)
		return core_actions.post_status(db,user,msg)


def main():
    tornado.options.parse_command_line()
    db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
    print "Established Database Connection"
    print 'http://127.0.0.1:'+str(options.port)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


