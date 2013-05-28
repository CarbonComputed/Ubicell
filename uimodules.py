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
import config

import logging

class PostModule(tornado.web.UIModule):
    def render(self,me, post,uniname,detailed=False):
        return self.render_string("uimodules/post.mod",post=post,detailed=detailed,me=me,uniname=uniname)

class NotModule(tornado.web.UIModule):
    def render(self, n):
        return self.render_string("uimodules/not.mod",n=n)

class NavModule(tornado.web.UIModule):
    # @tornado.web.authenticated
    # @tornado.web.asynchronous
    # @gen.coroutine

    def render(self,uid,nots=None):
        # uid = self.get_current_user()['_id']['$oid']
        #nots= yield gen.Task(core_actions.get_notifications,uid)
        if nots == None:
            nots = core_actions.get_notifications(uid)

        return self.render_string("uimodules/top-nav.mod",nots=nots)
        #return 
        

class NewClubModule(tornado.web.UIModule):
    def render(self):
        return self.render_string("uimodules/newclub-form.mod")

class LeftSideModule(tornado.web.UIModule):
    def render(self,uid,clubs=None):
        if clubs == None:
            clubs = User.objects(id=uid).first().Clubs
        return self.render_string("uimodules/left-side.mod",clubs=clubs)