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
from tornado import gen

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
from models.University import *
from util.funcs import *
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
                (r'/actions/get_replies',ReplyLoader),
                (r'/actions/edit_profile',EditProfileHandler),
                (r'/actions/get_nots',NotificationHandler),
                (r'/actions/get_uni_feed',UniversityFeedHandler)
                
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
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        def get(self):
                user = self.get_current_user()
                is_uni = str2bool(self.get_argument('University',strip=True,default="f"))
                # print user['_id']['$oid']
                

                uid = user['_id']['$oid']
                feed = yield gen.Task(core_actions.get_feed,uid)
                feed = feed['result']
                # print feed
                nots= yield gen.Task(core_actions.get_notifications,uid)
                nots.reverse()

                uniname = University.objects(id=user['School']['University']['$oid']).first().Name
                # print 'is_uni',is_uni
                if not is_uni:
                        self.render("base.html",userdata=user,feed = feed,nots=nots,uniname=uniname)
                else:
                        uniid = user['School']['University']['$oid']

                        feed = yield gen.Task(school_actions.get_feed,uniid)
                        self.render("UniFeed.html",userdata=user,feed = feed,nots=nots,uniname=uniname)



        def post(self):
                pass

class AuthLoginHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):

        self.render("login.html")

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):

        print("test")
        username = self.get_argument("UserName",strip = True)
        password = self.get_argument("Password",strip = True)

        user = yield gen.Task(auth_actions.login,username,password)
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

        @tornado.web.asynchronous
        @gen.engine
        def post(self):
                self.clear_cookie('user')
                self.clear_cookie("userdata")

                user = self.request.arguments
                resp = yield gen.Task(auth_actions.register,user,self.request)
                if resp == 200:
                        self.redirect("/")
                else:
                        self.redirect("/auth/register")


class UserHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        @tornado.web.addslash

        def get(self,UserName):
                #check if user can view profile

                user = self.get_current_user()
                uid = user['_id']['$oid']
                user2 = user_actions.get_friend_data(UserName).to_mongo()
                # print user2.to_mongo()
                friend = yield gen.Task(user_actions.is_friends_with,uid,UserName)
                friend_requested = yield gen.Task(user_actions.is_friend_requested,uid,UserName)
                friend_requesting = yield gen.Task(user_actions.is_friend_requesting,uid,UserName)
                feed = yield gen.Task(core_actions.get_user_feed,user2['_id'])
                feed = feed['result']
                # print 'friend',friend
                # print 'friend_requesting',friend_requesting
                # print 'friend_requested',friend_requested
                if user2 is None:
                        raise tornado.web.HTTPError(404)
                user2['UserStatus'] = UserStatus.USER_FRI
                nots= yield gen.Task(core_actions.get_notifications,uid)
                nots.reverse()
                uniname = University.objects(id=user['School']['University']['$oid']).first().Name
                # print user2['UserStatus']
                if UserName == user['UserName']:
                        user2 = user
                        user2['UserStatus'] = UserStatus.USER_ME
                        print user2
                        # print user2['ProfileImg']['$oid']
                        feed = yield gen.Task(core_actions.get_user_feed,uid)
                        feed = feed['result']

                        self.render("me.html",userdata=user2,feed=feed,nots=nots,uniname=uniname)
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
                # print user2['ProfileImg']
                feed = yield gen.Task(core_actions.get_user_feed,user2['_id'])
                feed = feed['result']
                # print user2['UserStatus']

                self.render("user.html",userdata=user2,feed=feed,nots=nots,uniname=uniname)

        @tornado.web.asynchronous
        @gen.coroutine
        def post(self,UserName):
                userid = self.get_current_user()['_id']['$oid']
                message = self.get_argument('message',strip=True)
                posttype = int(self.get_argument('posttype',strip=True))

                friend = yield gen.Task(user_actions.is_friends_with,userid,UserName)
                friendid = User.objects(UserName=UserName).first().id
                if posttype is PostType.WALL_POST:
                        p = yield gen.Task(core_actions.post_wall,friendid,message,userid)
                        return
                elif posttype is PostType.REPLY_POST:
                        postid = self.get_argument('postid',strip=True)
                        replyid = self.get_argument('replyid',default = None,strip=True)
                        p = yield gen.Task(core_actions.post_wall,userid,message)
                        return
                else:
                        # print 'huh?'
                        return

class UserFriendHandler(UserHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        #@custom_dec.auth_friend
        def get(self,UserName):
            user= yield gen.Task(user_actions.get_friend_data,UserName)
            userid = user.id
            # uniid = self.get_current_user()['School']['University']['$oid']
            # query = self.get_argument('query',strip = True)
            friends = yield gen.Task(user_actions.get_friends,userid)
            nots= yield gen.Task(core_actions.get_notifications,userid)
            nots.reverse()
            uniname = University.objects(id=self.get_current_user()['School']['University']['$oid']).first().Name
            self.render('friends.html',userdata= self.get_current_user(),friends = friends,nots=nots,uniname=uniname)

class StatusHandler(BaseHandler):
    #unused
        @tornado.web.authenticated
        def post(self,UserName):
                user = self.get_current_user()
                msg = self.get_argument("Message",strip = True)
                fid = user_actions.get_friend_data(self.db,self.mc,UserName)['_id']

                return core_actions.post_wall(self.db,self.mc,user['_id'],fid,msg)

class WallHandler(BaseHandler):
    #unused
        @tornado.web.authenticated
        #@custom_dec.auth_friend

        @tornado.web.asynchronous
        @gen.coroutine
        def post(self,UserName):
                user = self.get_current_user()
                msg = self.get_argument("Message",strip = True)
                fid = yield gen.Task(user_actions.get_friend_data,self.db,self.mc,UserName)
                fid = fid['_id']
                yield gen.Task(core_actions.post_wall,self.db,self.mc,user['_id'],fid,msg)
                return

class UserPhotoHandler(BaseHandler):
        @tornado.web.authenticated
        #@custom_dec.auth_friend

        def get(self,UserName):
                pass

class FriendActionHandler(BaseHandler):
        @tornado.web.authenticated

        @tornado.web.asynchronous
        @gen.coroutine
        def post(self):
                me = self.get_current_user()
                act = int(self.get_argument("Action",strip = True))
                fid = self.get_argument("_id",strip = True)
                ustat = int(self.get_argument("UserStatus",strip = True))
                if act == Action.UNFRIEND:
                    user_actions.unfriend(me['_id']['$oid'],fid)
                # print ustat
                resp = RespSuccess.DEFAULT_SUCCESS
                if int(ustat) == UserStatus.USER_NEI:
                        resp = yield gen.Task(user_actions.send_friend_request,me['_id']['$oid'],fid)
                elif ustat == UserStatus.USER_REQ:
                        pass
                elif ustat == UserStatus.USER_ACC:
                        resp = yield gen.Task(user_actions.accept_friend_request,me['_id']['$oid'],fid)
                else:
                        raise tornado.web.HTTPError(500)
                if resp != RespSuccess.DEFAULT_SUCCESS:
                        # print 'Default',resp
                        raise tornado.web.HTTPError(500)

class PostHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        #@custom_dec.authenticated_post

        def get(self):
                userid = self.get_current_user()['_id']['$oid']
                # print userid
                feed = yield gen.Task(core_actions.get_feed,userid)
                # print feed
                self.finish(dumps(feed))

        @tornado.web.asynchronous
        @gen.coroutine
        def post(self):
                userid = self.get_current_user()['_id']['$oid']
                message = self.get_argument('message',strip=True)
                posttype = int(self.get_argument('posttype',strip=True))
                isuni = str2bool(self.get_argument('is_uni',strip=True,default=False))
                if not isuni:
                        if posttype is PostType.WALL_POST:
                                yield gen.Task(core_actions.post_wall,userid,message)
                                return
                        elif posttype is PostType.REPLY_POST:
                                postid = self.get_argument('postid',strip=True)
                                replyid = self.get_argument('replyid',default = None,strip=True)
                                # print 'replyid',replyid
                                ownerid = self.get_argument('ownerid',default = None,strip=True)
                                p = yield gen.Task(core_actions.post_wall,ownerid,message,commenter = userid,postid=postid,replyid = replyid)
                                return
                        else:
                                # print 'huh?'
                                return
                else:
                        uniid = User.objects(id=userid).first().School.University
                        if posttype is PostType.WALL_POST:
                                yield gen.Task(school_actions.post_wall,userid,message,groupid=uniid)
                        elif posttype is PostType.REPLY_POST:
                                postid = self.get_argument('postid',strip=True)
                                replyid = self.get_argument('replyid',default = None,strip=True)
                                # print 'replyid',replyid
                                ownerid = self.get_argument('ownerid',default = None,strip=True)
                                p = yield gen.Task(school_actions.post_wall,ownerid,message,groupid=uniid,commenter = userid,postid=postid,replyid = replyid)
                                return
                        else:
                                # print 'huh?'
                                return


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
                # print picid
                profilepic = ProfileImage.objects(id =picid).first()
                
                self.set_header('Content-Type', 'image/jpg')
                self.finish(profilepic.Image.read())

class MeHandler(BaseHandler):
        @tornado.web.authenticated

        def get(self):
                self.redirect("/user/"+self.get_current_user()['UserName'])


class FriendVoteHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        #Check if post is owned by friend

        def post(self):
                powner = self.get_argument('post_owner',strip=True)
                postid = self.get_argument('post_id',strip=True)
                vote = self.get_argument('vote_type',strip=True)
                uid = self.get_current_user()['_id']['$oid']
                isreply = self.get_argument('is_reply',strip=True)
                isuni = str2bool(self.get_argument('is_uni',strip=True,default=False))
                #if user_actions.validPost(self.db,powner,postid) is False  or user_actions.is_friends_with_byid(self.db,uid,powner) is False:
                #       reply = 500;
                # print isuni
                uniid = User.objects(id=powner).first().School.University

                # print 'isrepl',isreply
                if not isuni:
                        if isreply == "true":
                                replyid = self.get_argument('reply_id',strip=True)
                                if vote == 'up':
                                        reply = yield gen.Task(core_actions.upvote_comment,powner,uid,postid,replyid)
                                else:
                                        reply = yield gen.Task(core_actions.downvote_comment,powner,uid,postid,replyid)

                        else:
                                if vote == 'up':
                                        reply = yield gen.Task(core_actions.upvote_post,powner,uid,postid)
                                else:
                                        reply = yield gen.Task(core_actions.downvote_post,powner,uid,postid)

                        # print reply
                        return
                else:
                        if isreply == "true":
                                replyid = self.get_argument('reply_id',strip=True)
                                if vote == 'up':
                                        reply = yield gen.Task(school_actions.upvote_comment,uniid,uid,postid,replyid)
                                else:
                                        reply = yield gen.Task(school_actions.downvote_comment,uniid,uid,postid,replyid)

                        else:
                                if vote == 'up':
                                        reply = yield gen.Task(school_actions.upvote_post,uniid,uid,postid)
                                else:
                                        reply = yield gen.Task(school_actions.downvote_post,uniid,uid,postid)

                        # print reply
                        return  

class SearchHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated

        def get(self):
                userid = self.get_current_user()['_id']
                uniid = self.get_current_user()['School']['University']['$oid']
                query = self.get_argument('query',strip = True)
                results = yield gen.Task(core_actions.search,userid,uniid,query)
                nots= yield gen.Task(core_actions.get_notifications,userid['$oid'])
                nots.reverse()
                uniname = University.objects(id=self.get_current_user()['School']['University']['$oid']).first().Name
                self.render('search.html',userdata= self.get_current_user(),results = results,nots=nots,uniname=uniname)
                

class EditProfileHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated

        def get(self):
                userid = self.get_current_user()['_id']['$oid']
                nots= yield gen.Task(core_actions.get_notifications,userid)
                nots.reverse()
                uniname = University.objects(id=self.get_current_user()['School']['University']['$oid']).first().Name
                self.render('editprofile.html',user=self.get_current_user(),nots=nots,uniname=uniname)

        def post(self):
                userid = self.get_current_user()['_id']['$oid']
                user = User.objects(id=userid).first()
                name = self.get_argument('FullName',default=(user.FirstName + " "+user.LastName),strip=True)
                gender = self.get_argument('gender',default=user.Gender,strip=True)
                major = self.get_argument('major',default=user.School.Major,strip=True)
                gradyear = int(self.get_argument('yearpicker',default=user.School.GradYear,strip=True))
                about = self.get_argument('about',default=user.About,strip=True)
                print gender
                # if password != user.Password:
                #         m = hashlib.md5()
                #         m.update(password)
                #         password = m.hexdigest()

                # user.Password =  password
                if len(name) < 2:
                    user.FirstName = name[0]
                
                else:
                    user.FirstName = name.split()[0]
                    user.LastName = name.split()[1]
                
                user.Gender = gender
                user.School.Major = major
                user.School.GradYear = gradyear
                user.About = about
                # print self.request.files
                if len(self.request.files) > 0:
                    fileinfo = self.request.files['pic'][0]
                    profimg = ProfileImage(Owner=user.id)
                    profimg.Image.put(fileinfo['body'],content_type = 'image/jpeg',Owner=user.id)
                    profimg.save()
                    user.ProfileImg = profimg.id

                user.save()
                user =  User.objects(id=user.id).exclude("Password","Wall","FriendsRequested","Friends","FriendsRequesting").first()
                self.set_secure_cookie("userdata", tornado.escape.json_encode(dumps(user.to_mongo())))
                # self.write("<script>alert(\"success!\") </script>");
                # self.redirect("/")




class ReplyLoader(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated
        #@custom_dec.authenticated_get


        def get(self):
                #Check if friends
                userid = self.get_current_user()['_id']
                postid = self.get_argument('post_id',strip = True)
                powner = self.get_argument('owner_id',strip = True)
                is_uni = str2bool(self.get_argument('is_uni',strip=True,default="false"))

                # print 'userid',userid
                # print 'powner',powner
                # print 'pid',postid
                if not is_uni:
                        replies = yield gen.Task(core_actions.get_replies,userid,powner,postid)
                else:
                        uniid = self.get_current_user()['School']['University']['$oid']
                        replies = yield gen.Task(school_actions.get_replies,uniid,powner,postid)
                t = core_actions.build_tree(replies)
                # core_actions.print_graph(t,ObjectId(postid))
                # print 'out',t.get(postid)
                self.render('reply.html',replies=t,depth = 0, 
            render_replies=self.render_replies,parentid=ObjectId(postid))

        def render_replies(self, replies,parentid,depth=0): 
                return self.render_string('reply.html', 
            replies=replies,parentid=parentid,depth = depth, 
            render_replies=self.render_replies)


class NotificationHandler(BaseHandler):
        @tornado.web.authenticated

        def post(self):
                userid = self.get_current_user()['_id']['$oid']
                core_actions.read_notifications(userid)

        def get(self):
                userid = self.get_current_user()['_id']['$oid']
                nots = core_actions.get_notifications(userid)
                # print nots
                self.finish(tornado.escape.json_encode(nots))

class UniversityFeedHandler(BaseHandler):
        @tornado.web.authenticated

        def get(self):
                user = self.get_current_user()
                uid = user['_id']['$oid']
                schoolid = user['School']['University']['$oid']
                feed = school_actions.get_feed(schoolid)
                # print feed
                nots=core_actions.get_notifications(uid)
                nots.reverse()
                uniname = University.objects(id=user['School']['University']['$oid']).first().Name
                self.render("UniFeed.html",userdata=user,feed = feed,nots=nots,uniname=uniname)


def NewClubHandler(BaseHandler):
    @tornado.web.authenticated
    
    def post(self):
        pass   

def ClubHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        pass

def main():
    tornado.options.parse_command_line()
    #self.db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
    print ("Established Database Connection")
    print ('http://127.0.0.1:'+str(options.port))
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


