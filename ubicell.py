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
from tornado.httpclient import HTTPError
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
from models.Club import *
from util.funcs import *
from util import scraper
from util.libsolvemedia import *
import config

import logging
logger = logging.getLogger(__name__)

CAPTCHA = SolveMedia(config.CKEY, config.VKEY, config.HKEY)

define("port", default=8000, help="run on the given port", type=int)
define("debug",default=False,help="Run in debug mode",type=bool)


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
                (r'/actions/get_uni_feed',UniversityFeedHandler),
                (r'/actions/new_club',NewClubHandler),
                (r'/actions/thumbnail',LinkPreviewHandler),
                (r'/club',ClubHandler),
                (r'/club/members',ClubMemberHandler),
                (r'/verify',EmailConfirmHandler)                
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
                # print uid
                friends = yield gen.Task(user_actions.get_friends,uid)
                # print friends[0]
                #print self.request
                clubs = User.objects(id=uid).first().Clubs
                if not is_uni:
                        self.render("base.html",userdata=user,feed = feed,nots=nots,uniname=uniname,friends=friends,clubs=clubs,is_club=False)
                else:
                        uniid = user['School']['University']['$oid']

                        feed = yield gen.Task(school_actions.get_feed,uniid)
                        self.render("UniFeed.html",userdata=user,feed = feed,nots=nots,uniname=uniname,friends=friends,code=200,clubs=clubs,is_club=False)



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

        # print("test")
        username = self.get_argument("UserName",strip = True)
        password = self.get_argument("Password",strip = True)

        user = yield gen.Task(auth_actions.login,username,password)
        if not user:
            self.redirect("/auth/login")
            return
        if not user.Active:
            self.render("message.html",message="You haven't activated your account yet. Verify your email first.")
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
                self.render("register.html",captcha=CAPTCHA)

        @tornado.web.asynchronous
        @gen.engine
        def post(self):
                self.clear_cookie('user')
                self.clear_cookie("userdata")
                rip = self.request.remote_ip
                if rip == '127.0.0.1':
                    rip = config.LOCAL_IP
                
                # try:
                capansw = self.get_argument('adcopy_response',strip=True)
                chall = self.get_argument('adcopy_challenge',strip=True)
                capcheck = yield gen.Task(CAPTCHA.check_answer,rip,chall,capansw)
                if not capcheck['is_valid']:
                    logger.debug("Incorrect CAPTCHA")
                    self.set_status(501)
                    self.write({'error' : True,'msg':"Invalid captcha"})
                    # self.send_error(status_code=501,msg='Invalid captcha')
                    self.finish()
                    return
                user = self.request.arguments
                resp = 200
                resp = yield gen.Task(auth_actions.register,user,self.request)
                if resp == 200:
                    self.write({'error' : False,'msg' : 'Success'})
                    self.finish()
                    # self.redirect("/")
                    return
                else:
                    self.write({'error' : True,'msg' : str(resp)})
                    self.finish()
                    return
                # except BaseException as e:
                #     print e
                #     self.write({'error' : True})
                #     self.finish()


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

                friends = yield gen.Task(user_actions.get_friends,uid)
                if UserName == user['UserName']:
                        user2 = user
                        user2['UserStatus'] = UserStatus.USER_ME
                        # print user2
                        # print user2['ProfileImg']['$oid']
                        feed = yield gen.Task(core_actions.get_user_feed,uid)
                        feed = feed['result']

                        self.render("me.html",userdata=user2,feed=feed,nots=nots,uniname=uniname,friends=friends,is_club=False)
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

                self.render("user.html",userdata=user2,feed=feed,nots=nots,uniname=uniname,friends=friends,is_club=False)

        @tornado.web.asynchronous
        @gen.coroutine
        def post(self,UserName):
                userid = self.get_current_user()['_id']['$oid']
                message = self.get_argument('message',strip=True)
                posttype = int(self.get_argument('posttype',strip=True))

                friend = yield gen.Task(user_actions.is_friends_with,userid,UserName)
                friendid = User.objects(UserName=UserName).first().id
                resp = {'error' : False}
                if posttype is PostType.WALL_POST:
                        p = yield gen.Task(core_actions.post_wall,friendid,message,userid)
                        self.write(resp)
                elif posttype is PostType.REPLY_POST:
                        postid = self.get_argument('postid',strip=True)
                        replyid = self.get_argument('replyid',default = None,strip=True)
                        p = yield gen.Task(core_actions.post_wall,userid,message)
                        self.write(resp)
                else:
                        # print 'huh?'
                        self.write({'error' : True})
                self.finish()

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
                        if resp==RespSuccess.DEFAULT_SUCCESS:
                            self.write({'error':False})
                elif ustat == UserStatus.USER_REQ:
                        self.write({'error':True})
                elif ustat == UserStatus.USER_ACC:
                        resp = yield gen.Task(user_actions.accept_friend_request,me['_id']['$oid'],fid)
                        self.write({'error':False})
                else:
                        self.write({'error':True})
                if resp != RespSuccess.DEFAULT_SUCCESS:
                        # print 'Default',resp
                        self.write({'error':True})
                self.finish()

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
                isuni = str2bool(self.get_argument('is_uni',strip=True,default='f'))
                isclub = str2bool(self.get_argument('is_club',strip=True,default='f'))

                post_resp = {'error' : False}
                if not isuni and not isclub:
                        logger.debug('not isuni')
                        if posttype is PostType.WALL_POST:
                                yield gen.Task(core_actions.post_wall,userid,message)
                                self.write(post_resp)

                        elif posttype is PostType.REPLY_POST:
                                postid = self.get_argument('postid',strip=True)
                                replyid = self.get_argument('replyid',default = None,strip=True)
                                # print 'replyid',replyid
                                ownerid = self.get_argument('ownerid',default = None,strip=True)
                                p = yield gen.Task(core_actions.post_wall,ownerid,message,commenter = userid,postid=postid,replyid = replyid)
                                self.write(post_resp)

                        else:
                                self.write({'error': True})
                                
                elif isuni:
                        logger.debug('isuni')
                        uniid = User.objects(id=userid).first().School.University
                        if posttype is PostType.WALL_POST:
                                yield gen.Task(school_actions.post_wall,userid,message,groupid=uniid)
                                self.write(post_resp)

                        elif posttype is PostType.REPLY_POST:
                                postid = self.get_argument('postid',strip=True)
                                replyid = self.get_argument('replyid',default = None,strip=True)
                                # print 'replyid',replyid
                                ownerid = self.get_argument('ownerid',default = None,strip=True)
                                p = yield gen.Task(school_actions.post_wall,ownerid,message,groupid=uniid,commenter = userid,postid=postid,replyid = replyid)
                                self.write(post_resp)

                        else:
                            self.write({'error': True})
                elif isclub:
                        logger.debug('isclub' )
                        clubid = self.get_argument('clubid',strip=True)
                        if posttype is PostType.WALL_POST:
                                yield gen.Task(club_actions.post_wall,userid,message,groupid=clubid)
                                self.write(post_resp)

                        elif posttype is PostType.REPLY_POST:
                                postid = self.get_argument('postid',strip=True)
                                replyid = self.get_argument('replyid',default = None,strip=True)
                                # print 'replyid',replyid
                                ownerid = self.get_argument('ownerid',default = None,strip=True)
                                p = yield gen.Task(club_actions.post_wall,ownerid,message,groupid=clubid,commenter = userid,postid=postid,replyid = replyid)
                                self.write(post_resp)

                        else:
                            self.write({'error': True})
                    
                self.finish()


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
                isuni = str2bool(self.get_argument('is_uni',strip=True,default='f'))
                isclub = str2bool(self.get_argument('is_club',strip=True,default='f'))
                #if user_actions.validPost(self.db,powner,postid) is False  or user_actions.is_friends_with_byid(self.db,uid,powner) is False:
                #       reply = 500;
                # print isuni
                uniid = User.objects(id=powner).first().School.University
                # print 'isrepl',isreply
                if not isuni and not isclub:
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
                        
                elif isuni:
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
                elif isclub:
                        clubid = self.get_argument('clubid',strip=True)
                        if isreply == "true":
                                replyid = self.get_argument('reply_id',strip=True)
                                if vote == 'up':
                                        reply = yield gen.Task(club_actions.upvote_comment,clubid,uid,postid,replyid)
                                else:
                                        reply = yield gen.Task(club_actions.downvote_comment,clubid,uid,postid,replyid)

                        else:
                                if vote == 'up':
                                        reply = yield gen.Task(club_actions.upvote_post,clubid,uid,postid)
                                else:
                                        reply = yield gen.Task(club_actions.downvote_post,clubid,uid,postid)

                        # print reply
                logger.debug("Vote Posted Successfully")
                self.write({
                'error': False, 
                'msg': 'Voted'
                })
                self.finish()  

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
                friends = yield gen.Task(user_actions.get_friends,userid['$oid'])
                self.render('search.html',userdata= self.get_current_user(),results = results,nots=nots,uniname=uniname,friends=friends)
                

class EditProfileHandler(BaseHandler):
        @tornado.web.asynchronous
        @gen.coroutine
        @tornado.web.authenticated

        def get(self):
                userid = self.get_current_user()['_id']['$oid']
                nots= yield gen.Task(core_actions.get_notifications,userid)
                nots.reverse()
                uniname = University.objects(id=self.get_current_user()['School']['University']['$oid']).first().Name
                friends = yield gen.Task(user_actions.get_friends,userid)
                self.render('editprofile.html',user=self.get_current_user(),nots=nots,uniname=uniname,friends=friends,is_club=False)

        def post(self):
                userid = self.get_current_user()['_id']['$oid']
                user = User.objects(id=userid).first()
                name = self.get_argument('FullName',default=(user.FirstName + " "+user.LastName),strip=True)
                gender = self.get_argument('gender',default=user.Gender,strip=True)
                major = self.get_argument('major',default=user.School.Major,strip=True)
                gradyear = int(self.get_argument('yearpicker',default=user.School.GradYear,strip=True))
                about = self.get_argument('about',default=user.About,strip=True)
                #print gender
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
                is_club = str2bool(self.get_argument('is_club',strip=True,default="false"))

                # print 'userid',userid
                # print 'powner',powner
                # print 'pid',postid
                if not is_uni and not is_club:
                        replies = yield gen.Task(core_actions.get_replies,userid,powner,postid)
                elif is_uni:
                        uniid = self.get_current_user()['School']['University']['$oid']
                        replies = yield gen.Task(school_actions.get_replies,uniid,powner,postid)
                elif is_club:
                        clubid = self.get_argument('clubid',strip=True)
                        replies = yield gen.Task(club_actions.get_replies,clubid,powner,postid)
                t = core_actions.build_tree(replies)
                # print t
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
        @tornado.web.asynchronous
        @gen.coroutine    

        def get(self):
                user = self.get_current_user()
                uid = user['_id']['$oid']
                schoolid = user['School']['University']['$oid']
                feed = yield gen.Task(school_actions.get_feed,schoolid)
                # print feed
                nots = yield gen.Task(core_actions.get_notifications,uid)
                nots.reverse()
                uniname = University.objects(id=user['School']['University']['$oid']).first().Name
                self.render("UniFeed.html",userdata=user,feed = feed,nots=nots,uniname=uniname,is_club=False)


class NewClubHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine    

    def post(self):
        name = self.get_argument("name",strip=True)
        about = self.get_argument("about",strip=True,default="")
        print about
        members = self.get_argument("members")
        admins = self.get_argument("admins",default=[])
        private = str2bool(self.get_argument("private",strip=True))
        uid = self.get_current_user()['_id']['$oid']
        uniid = self.get_current_user()['School']['University']['$oid']
        members = members.split(",")
        admins = admins.split(",")
        del members[-1]
        del admins[-1]
        resp = yield gen.Task(club_actions.make_club,ownerid=uid,name=name,university=uniid,about=about,members=members,admins=admins)
        if resp != 200:
            self.write({'error' : True,'msg':'Invalid Club'})
        else:
            self.write({'error' : False,'msg':'Success'})
        self.finish()

class ClubHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine    

    def get(self):
        user = self.get_current_user()
        uid = user['_id']['$oid']
        nots= yield gen.Task(core_actions.get_notifications,uid)
        nots.reverse()
        friends = yield gen.Task(user_actions.get_friends,uid)
        try:
            clubid = self.get_argument('clubid',strip=True)
            club = yield gen.Task(club_actions.get_club,clubid)
        except:
            self.redirect("/")
            return
        logger.debug(club.Name)
        is_member = uid in club.Members
        is_member_reg = uid in club.MemberRequests
        is_admin = uid in club.Admins

        self.render('club.html',nots=nots,friends=friends,uniname=None,is_member=is_member,is_admin=is_admin,club = club,is_club=True,is_member_reg=is_member_reg)
    


    @tornado.web.asynchronous
    @gen.coroutine   
    def post(self):
        user = self.get_current_user()
        uid = user['_id']['$oid']
        clubid = self.get_argument('club_id',strip=True)

class ClubMemberHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine

    def post(self):
        action = int(self.get_argument('action'))
        clubid = self.get_argument('clubid',strip=True)
        userid = self.get_argument('userid',strip=True)
        uid = self.get_current_user()['_id']['$oid']
        resp = 500
        if action == MemberAction.CONFIRM:
            resp = yield gen.Task(club_actions.confirm_member,uid,clubid,userid)
        elif action == MemberAction.ADD:
            resp = yield gen.Task(club_actions.add_member,clubid,userid)
        if resp != 200:
            self.write({'error' : True,'msg' : 'Add Member Failure'})
        else:
            self.write({'error' : False,'msg' : 'Add Member Success'})
        self.finish()

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        clubid = self.get_argument('clubid',strip=True)
        club = Club.objects(id=clubid).first()
        uid = self.get_current_user()['_id']['$oid']
        is_admin = uid in club.Admins
        Members = club_actions.get_member_data(clubid)
        MemberRequests = club_actions.get_member_req_data(clubid)
        print Members
        nots= yield gen.Task(core_actions.get_notifications,self.get_current_user()['_id']['$oid'])
        nots.reverse()
        friends = yield gen.Task(user_actions.get_friends,self.get_current_user()['_id']['$oid'])
        self.render('members.html',Members=Members,MemberRequests=MemberRequests,nots=nots,friends=friends,is_club=True,uniname=None,club=club,is_admin=is_admin)


class LinkPreviewHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine
    
    def get(self):
        url = self.get_argument("url",strip=True)
        height = self.get_argument("height",strip=True,default="250")
        width = self.get_argument("width",strip=True,default="480")
        if len(url) == 0:
            self.finish()
            return
        embed = self.get_argument("embed",strip=True,default=False)
        link = yield gen.Task(scraper.get_link,url)

        if embed:
            if link.embed != None:
                link.embed = re.sub(r'width="\d+"', 'width='+width, link.embed)
                link.embed = re.sub(r'height="\d+"', 'height='+height, link.embed)
                self.write(link.embed)
        else:
            if link.image != None:
                self.write(link.image)
        self.finish()

class EmailConfirmHandler(BaseHandler):
    # @tornado.web.asynchronous
    # @gen.coroutine

    def get(self):
        try:
            uniqueid = self.get_argument('regid',strip=True)
            user = User.objects(RegId=uniqueid).first()
            if user != None:
                if user.Active == True:
                    self.write("Already Confirmed")
                    self.finish()
                user.Active = True
                user.save()
                self.render('message.html',message="Thanks for registering %s" % user.UserName)
                return
            self.write("Thats not right")
            self.finish()
            return
        except:
            self.render('message.html',message='Thats not right')
            
               

def main():
    tornado.options.parse_command_line()
    if options.debug:
        logger.info("Running with debug output")
        logging.getLogger().setLevel(logging.DEBUG)
    #self.db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
    logger.info ("Established Database Connection")
    logger.info ('http://127.0.0.1:'+str(options.port))
    app = Application()
    app.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


