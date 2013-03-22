import functools
import tornado.web

import user_actions


def auth_friend(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        userid = self.get_current_user()['_id']
        me = self.get_current_user()['UserName']
        friend_username = args[0]
        if me == friend_username:
            return method(self, *args, **kwargs)
        #db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
        db = self.db
        if user_actions.is_friends_with(db,userid,friend_username) is None:
          raise tornado.web.HTTPError(403)
        else:
          return method(self, *args, **kwargs)
    return wrapper

def authenticated_post(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        userid = self.get_current_user()['_id']
        fid = self.get_argument('commenter',default=None,strip = True)
        print fid
        postowner = self.get_argument('ownerid',default=None,strip = True)
        if fid is None:
            return method(self, *args, **kwargs)
        #db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
        db = self.db
        if user_actions.valid_post(db,postowner,postid) is False:
            raise tornado.web.HTTPError(403)

        if user_actions.is_friends_with_byid(db,userid,friend_username) is None:
          raise tornado.web.HTTPError(403)
        
        return method(self, *args, **kwargs)
    return wrapper

def authenticated_get(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        userid = self.get_current_user()['_id']
        postowner = self.get_argument('owner_id',default=None,strip = True)
        postid = self.get_argument('post_id',default=None,strip = True)
        #db = database.Connection("localhost", "ProjectTakeOver",user="root",password="")
        db = self.db
        if user_actions.valid_post(db,postowner,postid) is False:
            raise tornado.web.HTTPError(403)

        if user_actions.is_friends_with_byid(db,userid,postowner) is None:
          raise tornado.web.HTTPError(403)
        
        return method(self, *args, **kwargs)
    return wrapper

def notify_dec(method):
    @functools.wraps(method)
    def wrapper(self,*args, **kwargs):
        pass