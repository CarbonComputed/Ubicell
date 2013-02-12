import functools
import tornado.web

import user_actions

from tornado import database

def auth_friend(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        userid = self.get_current_user()['UserID']
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