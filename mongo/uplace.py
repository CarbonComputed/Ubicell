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
from bson.objectid import ObjectId

from constants import *


import pymongo
import gridfs
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
		# (r'/auth/login/google',GoogleHandler),
		# (r'/auth/login/facebook',FacebookHandler),
		(r'/user/([A-Za-z\d.]{5,})/?',UserHandler),
		(r'/user/([A-Za-z\d.]{5,})/friends',UserFriendHandler),
		(r'/user/([A-Za-z\d.]{5,})/status',StatusHandler),
		(r'/user/([A-Za-z\d.]{5,})/wall',WallHandler),
		(r'/user/me',MeHandler),
		(r'/actions/respond_friend',FriendActionHandler),
		(r'/actions/post',PostHandler),
		(r'/actions/friend_vote',FriendVoteHandler),
		(r'/images',ImageHandler),
		(r'/search',SearchHandler),
		(r'/actions/get_replies',ReplyLoader)
		
		]
		settings = dict(
			cookie_secret="p5q5askPJeOhs5mXb3QZ9CrNZUlxRWha6CPXif8G",
			login_url="/auth/login",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies=False,
			autoescape="xhtml_escape",
			facebook_api_key='124864341026931',
			facebook_secret='29c22c3ca0963581b47f1604adbe48ce',
			)
		tornado.web.Application.__init__(self, handlers, **settings)
		self.db = pymongo.MongoClient().uplace
		self.mc = None
		self.fs = gridfs.GridFS(self.db)
		#self.mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True,"ketama": True})



class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	@property
	def mc(self):
		return self.application.mc

	@property
	def fs(self):
		return self.application.fs

	def get_current_user(self):
		user_json = self.get_secure_cookie("userdata")
		if not user_json: return None
		return tornado.escape.json_decode(loads(user_json))


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		user = self.get_current_user()
		feed = core_actions.get_feed(self.db,user['_id'])['result']
		self.render("base.html",userdata=user,db = self.db,feed = feed)



	def post(self):
		pass

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
		self.clear_cookie('user')
		self.clear_cookie("userdata")

		user = self.request.arguments
		resp = auth_actions.do_register(self.db,self.fs,user,self.request)
		if resp == 200:
			self.redirect("/")
		else:
			self.redirect("/auth/register")


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
		feed = core_actions.get_user_feed(self.db,user2['_id'])['result']
		if user2 is None:
			raise tornado.web.HTTPError(404)
		user2['UserStatus'] = UserStatus.USER_FRI
		if UserName == user['UserName']:
			user2 = user
			user2['UserStatus'] = UserStatus.USER_ME
			print user2['ProfileImg']['$oid']
			feed = core_actions.get_user_feed(self.db,user['_id'])['result']

			self.render("me.html",userdata=user2,feed=feed)
			return
		elif friend is None and friend_requested is None and friend_requesting is None:

			user2['UserStatus'] = UserStatus.USER_NEI

		elif friend_requesting != None:

			user2['UserStatus'] = UserStatus.USER_ACC
		elif friend_requested != None:
			user2['UserStatus'] = UserStatus.USER_REQ


			#raise tornado.web.HTTPError(403)
		#get user data
		#render page
		print user2['ProfileImg']
		feed = core_actions.get_user_feed(self.db,user2['_id'])['result']

		self.render("user.html",userdata=user2,feed=feed,db=self.db)
	def post(self,UserName):
		userid = self.get_current_user()['_id']
		message = self.get_argument('message',strip=True)
		posttype = int(self.get_argument('posttype',strip=True))

		friend = user_actions.is_friends_with(self.db,userid,UserName)
		friendid = friend['_id']
		if posttype is PostType.WALL_POST:
			return core_actions.post_wall(self.db,None,friendid,message,userid)
		elif posttype is PostType.REPLY_POST:
			postid = self.get_argument('postid',strip=True)
			replyid = self.get_argument('replyid',default = None,strip=True)
			return core_actions.post_wall(self.db,None,userid,message)
		else:
			print 'huh?'
			return 500;

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

		return core_actions.post_wall(self.db,self.mc,user['_id'],fid,msg)

class WallHandler(BaseHandler):
	@tornado.web.authenticated
	@custom_dec.auth_friend
	def post(self,UserName):
		user = self.get_current_user()
		msg = self.get_argument("Message",strip = True)
		fid = user_actions.get_friend_data(self.db,self.mc,UserName)['_id']
		return core_actions.post_wall(self.db,self.mc,user['_id'],fid,msg)

class UserPhotoHandler(BaseHandler):
	@tornado.web.authenticated
	@custom_dec.auth_friend

	def get(self,UserName):
		pass

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

class PostHandler(BaseHandler):
	@tornado.web.authenticated
	@custom_dec.authenticated_post

	def get(self):
		userid = self.get_current_user()['_id']
		print userid
		feed = core_actions.get_feed(self.db,userid)
		print feed
		self.finish(dumps(feed))

	def post(self):
		userid = self.get_current_user()['_id']
		message = self.get_argument('message',strip=True)
		posttype = int(self.get_argument('posttype',strip=True))
		if posttype is PostType.WALL_POST:
			return core_actions.post_wall(self.db,None,userid,message)
		elif posttype is PostType.REPLY_POST:
			postid = self.get_argument('postid',strip=True)
			replyid = self.get_argument('replyid',default = None,strip=True)
			ownerid = self.get_argument('ownerid',default = None,strip=True)
			return core_actions.post_wall(self.db,None,ownerid,message,commenter = userid,postid=postid,replyid = replyid)
		else:
			print 'huh?'
			return 500;


class GoogleHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        self.write(user)
        self.finish()

class FacebookHandler(tornado.web.RequestHandler,
                      tornado.auth.FacebookMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("session", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")
        self.write(user)
        self.finish()
        # Save the user using, e.g., set_secure_cookie()
        # Save the user with, e.g., set_secure_cookie()

class ImageHandler(BaseHandler):
	@tornado.web.authenticated

	def get(self):
		picid = self.get_argument('picid')
		profilepic = self.fs.get(ObjectId(picid))
		if profilepic.metadata['Profile'] !=True:
			raise tornado.web.HTTPError(400,'Forbidden')
		self.set_header('Content-Type', 'image/jpg')
		self.finish(profilepic.read())

class MeHandler(BaseHandler):
	@tornado.web.authenticated

	def get(self):
		self.redirect("/user/"+self.get_current_user()['UserName'])


class FriendVoteHandler(BaseHandler):
	@tornado.web.authenticated
	#Check if post is owned by friend

	def post(self):
		powner = self.get_argument('post_owner',strip=True)
		postid = self.get_argument('post_id',strip=True)
		vote = self.get_argument('vote_type',strip=True)
		uid = self.get_current_user()['_id']
		if user_actions.validPost(self.db,powner,postid) is False  or user_actions.is_friends_with_byid(self.db,uid,powner) is False:
			reply = 500;
		if vote == 'up':
			reply = core_actions.upvote_post(self.db,uid,postid)
		else:
			reply = core_actions.downvote_post(self.db,uid,postid)
		print reply
		return reply

class SearchHandler(BaseHandler):
	@tornado.web.authenticated

	def get(self):
		userid = self.get_current_user()['_id']
		uniid = self.get_current_user()['School']['University']['$oid']
		query = self.get_argument('query',strip = True)
		results = core_actions.search(self.db,userid,uniid,query)
		self.render('search.html',userdata= self.get_current_user(),results = results)
			

class ReplyLoader(BaseHandler):
	@tornado.web.authenticated
	#@custom_dec.authenticated_get


	def get(self):
		#Check if friends
		userid = self.get_current_user()['_id']
		postid = self.get_argument('post_id',strip = True)
		powner = self.get_argument('owner_id',strip = True)
		print 'userid',userid
		print 'powner',powner
		print 'pid',postid
		replies = core_actions.get_replies(self.db,userid,powner,postid)
		t = core_actions.build_tree(replies)
		print 'out',t.get(postid)
		self.render('reply.html',replies=t,depth = 0, 
            render_replies=self.render_replies,parentid=ObjectId(postid))

	def render_replies(self, replies,parentid,depth=0): 
		return self.render_string('reply.html', 
            replies=replies,parentid=parentid,depth = depth, 
            render_replies=self.render_replies)


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


