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

define("port", default=8000, help="run on the given port", type=int)

db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
		(r"/", MainHandler),
		(r"/auth/login", AuthLoginHandler),
		(r"/auth/logout", AuthLogoutHandler),
		(r"/auth/register",RegisterHandler),
		]
		settings = dict(
			cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
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
		user_json = self.get_secure_cookie("user")
		if not user_json: return None
		return tornado.escape.json_decode(user_json)


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.render("index.html")

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
        user = user_actions.get_user_data(db,user_cookie)
        #self.user_cache[user_cookie] = user
        self.redirect("/")



class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.write("You are now logged out")

class RegisterHandler(BaseHandler):
	def get(self):
		pass




def main():
    tornado.options.parse_command_line()
    db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
    print "Established Database Connection"
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


