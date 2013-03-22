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

from mongoengine import *
import gridfs
#import pylibmc

from actions import *
from decorators import *
from models.ProfileImage import *
from models.User import *
import config

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
		connect(config.DB_NAME)



class BaseHandler(tornado.web.RequestHandler):


	def get_current_user(self):
		user_json = self.get_secure_cookie("userdata")
		if not user_json: return None
		return tornado.escape.json_decode(loads(user_json))


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		user = self.get_current_user()
		
		print user['_id']['$oid']

		feed = core_actions.get_feed(user['_id']['$oid'])['result']
		#print feed
		self.render("base.html",userdata=user,feed = feed)



	def post(self):
		pass

class AuthLoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):

        self.render("login.html")

    def post(self):
    	username = self.get_argument("UserName",strip = True)
    	password = self.get_argument("Password",strip = True)
    	user = auth_actions.login(username,password)
    	if not user:
            self.redirect("/auth/login")
            return

        #user = user_actions.get_my_data(self.db,user['_id'])
        
        self.set_secure_cookie("userdata", tornado.escape.json_encode(dumps(user.to_mongo())))
        self.redirect("/")



class AuthLogoutHandler(BaseHandler):
	@tornado.web.asynchronous
	def get(self):
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
		resp = auth_actions.register(user,self.request)
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
		uid = user['_id']['$oid']
		user2 = user_actions.get_friend_data(UserName).to_mongo()
		#print user2.to_mongo()
		friend = user_actions.is_friends_with(uid,UserName)
		friend_requested = user_actions.is_friend_requested(uid,UserName)
		friend_requesting = user_actions.is_friend_requesting(uid,UserName)
		feed = core_actions.get_user_feed(user2['_id'])['result']
		print 'friend',friend
		print 'friend_requesting',friend_requesting
		print 'friend_requested',friend_requested
		if user2 is None:
			raise tornado.web.HTTPError(404)
		user2['UserStatus'] = UserStatus.USER_FRI
		print user2['UserStatus']
		if UserName == user['UserName']:
			user2 = user
			user2['UserStatus'] = UserStatus.USER_ME
			#print user2['ProfileImg']['$oid']
			feed = core_actions.get_user_feed(uid)['result']

			self.render("me.html",userdata=user2,feed=feed)
			return
		elif friend is False and friend_requested is False and friend_requesting is False:
			user2['UserStatus'] = UserStatus.USER_NEI
		elif friend_requesting != False:

			user2['UserStatus'] = UserStatus.USER_ACC
		elif friend_requested != False:
			user2['UserStatus'] = UserStatus.USER_REQ

			#raise tornado.web.HTTPError(403)
		#get user data
		#render page
		#print user2['ProfileImg']
		feed = core_actions.get_user_feed(user2['_id'])['result']
		print user2['UserStatus']
		self.render("user.html",userdata=user2,feed=feed)
	def post(self,UserName):
		userid = self.get_current_user()['_id']['$oid']
		message = self.get_argument('message',strip=True)
		posttype = int(self.get_argument('posttype',strip=True))

		friend = user_actions.is_friends_with(userid,UserName)
		friendid = User.objects(UserName=UserName).first().id
		if posttype is PostType.WALL_POST:
			return core_actions.post_wall(friendid,message,userid)
		elif posttype is PostType.REPLY_POST:
			postid = self.get_argument('postid',strip=True)
			replyid = self.get_argument('replyid',default = None,strip=True)
			return core_actions.post_wall(userid,message)
		else:
			print 'huh?'
			return 500;

class UserFriendHandler(UserHandler):
	@tornado.web.authenticated
	#@custom_dec.auth_friend
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
	#@custom_dec.auth_friend
	def post(self,UserName):
		user = self.get_current_user()
		msg = self.get_argument("Message",strip = True)
		fid = user_actions.get_friend_data(self.db,self.mc,UserName)['_id']
		return core_actions.post_wall(self.db,self.mc,user['_id'],fid,msg)

class UserPhotoHandler(BaseHandler):
	@tornado.web.authenticated
	#@custom_dec.auth_friend

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
			resp = user_actions.send_friend_request(me['_id']['$oid'],fid)
		elif ustat == UserStatus.USER_REQ:
			pass
		elif ustat == UserStatus.USER_ACC:
			resp = user_actions.accept_friend_request(me['_id']['$oid'],fid)
		else:
			raise tornado.web.HTTPError(500)
		if resp != RespSuccess.DEFAULT_SUCCESS:
			print 'Default',resp
			raise tornado.web.HTTPError(500)

class PostHandler(BaseHandler):
	@tornado.web.authenticated
	#@custom_dec.authenticated_post

	def get(self):
		userid = self.get_current_user()['_id']['$oid']
		print userid
		feed = core_actions.get_feed(userid)
		print feed
		self.finish(dumps(feed))

	def post(self):
		userid = self.get_current_user()['_id']['$oid']
		message = self.get_argument('message',strip=True)
		posttype = int(self.get_argument('posttype',strip=True))
		if posttype is PostType.WALL_POST:
			return core_actions.post_wall(userid,message)
		elif posttype is PostType.REPLY_POST:
			postid = self.get_argument('postid',strip=True)
			replyid = self.get_argument('replyid',default = None,strip=True)
			ownerid = self.get_argument('ownerid',default = None,strip=True)
			return core_actions.post_wall(ownerid,message,commenter = userid,postid=postid,replyid = replyid)
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
		print picid
		profilepic = ProfileImage.objects(id =picid).first()
		
		self.set_header('Content-Type', 'image/jpg')
		self.finish(profilepic.Image.read())

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
		uid = self.get_current_user()['_id']['$oid']
		#if user_actions.validPost(self.db,powner,postid) is False  or user_actions.is_friends_with_byid(self.db,uid,powner) is False:
		#	reply = 500;
		if vote == 'up':
			reply = core_actions.upvote_post(powner,uid,postid)
		else:
			reply = core_actions.downvote_post(powner,uid,postid)
		print reply
		return reply

class SearchHandler(BaseHandler):
	@tornado.web.authenticated

	def get(self):
		userid = self.get_current_user()['_id']
		uniid = self.get_current_user()['School']['University']['$oid']
		query = self.get_argument('query',strip = True)
		results = core_actions.search(userid,uniid,query)
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
		replies = core_actions.get_replies(userid,powner,postid)
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


